"""A tiny local stand-in for the TwittrAPI HTTP API, for testing the examples offline.

    python3 tools/mock_server.py --port 8787
    export TWITTRAPI_API_KEY=test-key TWITTRAPI_BASE_URL=http://127.0.0.1:8787

It serves small, made-up fixture responses in the same general shape X's GraphQL uses
(timelines with entries, user_results / tweet_results, bottom cursors). The data is fake and
the shapes are simplified; real responses carry many more fields. Paginated routes return
two pages with results and a third page with only cursor entries, so the SDK paginators stop.

POST /slack-webhook accepts Slack-style webhook payloads and logs them to stderr, so the
Slack example can be tested without Slack.

Standard library only. Not for production use.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, unquote, urlparse

CREATED = ["Fri Oct 09 18:{:02d}:00 +0000 2026".format(m) for m in range(60)]

# Fixture data -----------------------------------------------------------------------------

def user(uid: int, handle: str, name: str, followers: int, bio: str = "") -> Dict[str, Any]:
    return {
        "__typename": "User",
        "rest_id": str(uid),
        "is_blue_verified": uid % 2 == 0,
        "core": {"screen_name": handle, "name": name, "created_at": "Tue Mar 21 20:50:14 +0000 2006"},
        "location": {"location": "Internet"},
        "legacy": {
            "description": bio or f"Bio of {name}",
            "followers_count": followers,
            "friends_count": followers // 10,
            "statuses_count": followers // 3,
        },
    }


USERS = [user(1000 + i, f"user_{i}", f"Test User {i}", 5000 - i * 250) for i in range(12)]
PROFILES = {
    "jack": user(12, "jack", "jack", 6_400_000, "no state is the best state"),
    "nasa": user(11348282, "NASA", "NASA", 89_000_000, "Explore the universe and discover our home planet."),
    "acme": user(4242, "acme", "Acme Corp", 15_300, "We make everything."),
    "rival": user(4343, "rival", "Rival Inc", 9_800, "We also make everything."),
}


def tweet(tid: int, author: Dict[str, Any], text: str, likes: int, reply_to: Optional[str] = None) -> Dict[str, Any]:
    legacy = {
        "created_at": CREATED[tid % 60],
        "full_text": text,
        "favorite_count": likes,
        "retweet_count": likes // 5,
        "reply_count": likes // 10,
        "lang": "en",
    }
    if reply_to:
        legacy["in_reply_to_status_id_str"] = reply_to
    return {
        "__typename": "Tweet",
        "rest_id": str(tid),
        "core": {"user_results": {"result": author}},
        "legacy": legacy,
        "views": {"count": str(likes * 40), "state": "EnabledWithCount"},
    }


def user_entry(u: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "entryId": f"user-{u['rest_id']}",
        "content": {
            "entryType": "TimelineTimelineItem",
            "itemContent": {"itemType": "TimelineUser", "user_results": {"result": u}},
        },
    }


def tweet_entry(t: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "entryId": f"tweet-{t['rest_id']}",
        "content": {
            "entryType": "TimelineTimelineItem",
            "itemContent": {"itemType": "TimelineTweet", "tweet_results": {"result": t}},
        },
    }


def cursor_entries(next_cursor: str) -> List[Dict[str, Any]]:
    return [
        {"entryId": "cursor-top-0", "content": {"entryType": "TimelineTimelineCursor", "value": "top", "cursorType": "Top"}},
        {"entryId": f"cursor-bottom-{next_cursor}", "content": {"entryType": "TimelineTimelineCursor", "value": next_cursor, "cursorType": "Bottom"}},
    ]


def timeline(entries: List[Dict[str, Any]], wrapper: str) -> Dict[str, Any]:
    body = {"timeline": {"instructions": [{"type": "TimelineAddEntries", "entries": entries}]}}
    if wrapper == "search":
        return {"data": {"search_by_raw_query": {"search_timeline": body}}}
    if wrapper == "list":
        return {"data": {"list": {"members_timeline": body}}}
    if wrapper == "community":
        return {"data": {"communityResults": {"result": {"ranked_community_timeline": body}}}}
    if wrapper == "tweet":
        return {"data": {"threaded_conversation_with_injections_v2": body["timeline"]}}
    return {"data": {"user": {"result": {"timeline": body}}}}


def paged(items: List[Dict[str, Any]], cursor: Optional[str], make_entry, wrapper: str) -> Dict[str, Any]:
    """Page 1 (no cursor) and page 2 (cursor "p2") have items; page 3 has only cursors."""
    half = (len(items) + 1) // 2
    if not cursor:
        chunk, nxt = items[:half], "p2"
    elif cursor == "p2":
        chunk, nxt = items[half:], "p3"
    else:
        chunk, nxt = [], "p4"
    return timeline([make_entry(i) for i in chunk] + cursor_entries(nxt), wrapper)


def tweets_for(author: Dict[str, Any], base: int, topic: str, n: int = 6) -> List[Dict[str, Any]]:
    handle = author["core"]["screen_name"]
    return [tweet(base + i, author, f"{topic} update #{i} from @{handle}. Shipping things today.", 100 - i * 7) for i in range(n)]


TRENDS = [
    {"name": "#MockTrend", "url": "https://x.com/search?q=%23MockTrend", "query": "%23MockTrend", "tweet_volume": 125000},
    {"name": "Formula 1", "url": "https://x.com/search?q=Formula+1", "query": "Formula+1", "tweet_volume": 48200},
    {"name": "Open Source", "url": "https://x.com/search?q=Open+Source", "query": "Open+Source", "tweet_volume": None},
]
LOCATIONS = [
    {"name": "Worldwide", "woeid": 1, "country": "", "countryCode": None, "placeType": {"code": 19, "name": "Supername"}},
    {"name": "Germany", "woeid": 23424829, "country": "Germany", "countryCode": "DE", "placeType": {"code": 12, "name": "Country"}},
    {"name": "Berlin", "woeid": 638242, "country": "Germany", "countryCode": "DE", "placeType": {"code": 7, "name": "Town"}},
    {"name": "United States", "woeid": 23424977, "country": "United States", "countryCode": "US", "placeType": {"code": 12, "name": "Country"}},
]

# Routing ----------------------------------------------------------------------------------

Response = Tuple[int, Any]


def not_found(what: str) -> Response:
    return 404, {"error": f"{what} not found"}


def lookup_profile(handle: str) -> Optional[Dict[str, Any]]:
    return PROFILES.get(handle.lower().lstrip("@"))


def route(path: str, q: Dict[str, str]) -> Response:
    cursor = q.get("cursor")
    m = re.fullmatch(r"/user/by/username/([^/]+)", path)
    if m:
        u = lookup_profile(unquote(m.group(1)))
        return (200, {"data": {"user": {"result": u}}}) if u else not_found("User")

    m = re.fullmatch(r"/username/to/id/([^/]+)", path)
    if m:
        u = lookup_profile(unquote(m.group(1)))
        return (200, {"data": {"user": {"result": {"rest_id": u["rest_id"]}}}}) if u else not_found("User")

    m = re.fullmatch(r"/user/(-1|\d+)/(\w+)", path)
    if m:
        uid, kind = m.groups()
        author = lookup_profile(q.get("username", "")) if uid == "-1" else next(
            (p for p in PROFILES.values() if p["rest_id"] == uid), USERS[0])
        if author is None:
            return not_found("User")
        if kind in ("followers", "followings", "verifiedFollowers"):
            return 200, paged(USERS[:8], cursor, user_entry, "user")
        if kind in ("tweets", "tweetsAndReplies", "media"):
            base = 1_900_000_000_000_000_000 + int(author["rest_id"]) * 100
            return 200, paged(tweets_for(author, base, "Product"), cursor, tweet_entry, "user")
        return not_found("Route")

    m = re.fullmatch(r"/user/(\d+)", path)
    if m:
        u = next((p for p in PROFILES.values() if p["rest_id"] == m.group(1)), None)
        return (200, {"data": {"user": {"result": u}}}) if u else not_found("User")

    if path == "/search":
        term = q.get("searchItem", "")
        if q.get("category") == "People":
            return 200, paged(USERS[:6], cursor, user_entry, "search")
        items = [tweet(1_950_000_000_000_000_000 + i, USERS[i], f"Talking about {term} (mock result {i})", 80 - i * 5) for i in range(8)]
        return 200, paged(items, cursor, tweet_entry, "search")

    if path == "/lists/members":
        return 200, paged(USERS[2:10], cursor, user_entry, "list")
    if path == "/lists/tweets":
        items = [tweet(1_960_000_000_000_000_000 + i, USERS[i], f"List tweet {i}", 30 + i) for i in range(6)]
        return 200, paged(items, cursor, tweet_entry, "list")

    m = re.fullmatch(r"/communities/(\d+)/tweets", path)
    if m:
        items = [tweet(1_970_000_000_000_000_000 + i, USERS[i], f"Community post {i}: has anyone tried this?", 12 + i) for i in range(6)]
        return 200, paged(items, cursor, tweet_entry, "community")
    m = re.fullmatch(r"/communities/search/([^/]+)", path)
    if m:
        name = unquote(m.group(1))
        communities = [{"__typename": "Community", "rest_id": str(1_500_000_000_000_000_000 + i), "name": f"{name.title()} Community {i}", "member_count": 1200 * (i + 1)} for i in range(2)]
        return 200, {"data": {"communities_search_slice": {"items_results": [{"result": c} for c in communities]}}}

    m = re.fullmatch(r"/tweet/(\d+)", path)
    if m:
        tid = m.group(1)
        root = tweet(int(tid), PROFILES["jack"], "just setting up my twttr", 250_000)
        replies = [tweet(int(tid) + 1000 + i, USERS[i], f"Reply {i} to the tweet", 50 - i * 3, reply_to=tid) for i in range(8)]
        if not cursor:
            entries = [tweet_entry(root)] + [tweet_entry(r) for r in replies[:5]] + cursor_entries("r2")
        elif cursor == "r2":
            entries = [tweet_entry(r) for r in replies[5:]] + cursor_entries("r3")
        else:
            entries = cursor_entries("r4")
        return 200, timeline(entries, "tweet")
    m = re.fullmatch(r"/tweet/(\d+)/(retweets|favorites)", path)
    if m:
        return 200, paged(USERS[:10], cursor, user_entry, "tweet")
    m = re.fullmatch(r"/tweet/(\d+)/quotes", path)
    if m:
        items = [tweet(1_980_000_000_000_000_000 + i, USERS[i], f"Quote tweet {i}", 9 + i) for i in range(4)]
        return 200, paged(items, cursor, tweet_entry, "search")

    m = re.fullmatch(r"/trends/(\d+)", path)
    if m:
        woeid = int(m.group(1))
        loc = next((l for l in LOCATIONS if l["woeid"] == woeid), {"name": "Unknown", "woeid": woeid})
        return 200, [{"trends": TRENDS, "as_of": "2026-10-09T18:00:00Z", "locations": [{"name": loc["name"], "woeid": woeid}]}]
    if path == "/misc/locations":
        return 200, LOCATIONS

    return not_found("Route")


class Handler(BaseHTTPRequestHandler):
    server_version = "TwittrAPIMock/1.0"

    def _send(self, status: int, body: Any) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if not (self.headers.get("X-API-KEY") or self.headers.get("x-rapidapi-key")):
            self._send(401, {"error": "Missing API key"})
            return
        url = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        status, body = route(url.path, query)
        self._send(status, body)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        payload = self.rfile.read(length).decode("utf-8", "replace")
        if self.path == "/slack-webhook":
            print(f"[slack] {payload}", file=sys.stderr, flush=True)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self._send(404, {"error": "Route not found"})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[mock] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}", file=sys.stderr, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local mock of the TwittrAPI HTTP API.")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Mock TwittrAPI on http://127.0.0.1:{args.port}", file=sys.stderr, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
