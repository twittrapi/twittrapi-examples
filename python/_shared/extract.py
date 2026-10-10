"""Small, defensive helpers for reading X's raw GraphQL JSON.

TwittrAPI returns X's responses unchanged. The response shapes come from X, are not documented
and may change at any time, so these helpers walk the whole response looking for the objects
they need instead of following one fixed path. If a field moves, you get an empty value rather
than a crash. Check a real response before relying on a field.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional


def walk(data: Any) -> Iterator[Dict[str, Any]]:
    """Yields every JSON object (dict) inside ``data``, depth first."""
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            yield node
            stack.extend(reversed(list(node.values())))
        elif isinstance(node, list):
            stack.extend(reversed(node))


def _int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def flat_user(user: Dict[str, Any]) -> Dict[str, Any]:
    """Turns a ``user_results.result`` object into a flat dict."""
    legacy = user.get("legacy") or {}
    core = user.get("core") or {}  # X moved name/screen_name from legacy to core in 2025
    return {
        "id": user.get("rest_id"),
        "username": core.get("screen_name") or legacy.get("screen_name") or "",
        "name": core.get("name") or legacy.get("name") or "",
        "followers": _int(legacy.get("followers_count")),
        "following": _int(legacy.get("friends_count")),
        "tweets": _int(legacy.get("statuses_count")),
        "verified": bool(user.get("is_blue_verified") or legacy.get("verified")),
        "created_at": core.get("created_at") or legacy.get("created_at") or "",
        "bio": legacy.get("description") or (user.get("profile_bio") or {}).get("description") or "",
    }


def users(data: Any) -> List[Dict[str, Any]]:
    """Every user in a response, flattened and de-duplicated by ID, in response order.

    Finds ``user_results.result`` (timelines, followers, list members, retweeters) and plain
    ``{"result": {"__typename": "User"}}`` items (users by IDs, community members).
    """
    out: Dict[str, Dict[str, Any]] = {}
    for obj in walk(data):
        holder = obj.get("user_results")
        user = holder.get("result") if isinstance(holder, dict) else None
        if not (isinstance(user, dict) and user.get("rest_id")):
            result = obj.get("result")
            user = result if isinstance(result, dict) and result.get("__typename") == "User" else None
        if isinstance(user, dict) and user.get("rest_id") and user["rest_id"] not in out:
            out[user["rest_id"]] = flat_user(user)
    return list(out.values())


def first_user(data: Any) -> Optional[Dict[str, Any]]:
    """The first user object in a profile response (``data.user.result``), flattened."""
    for obj in walk(data):
        if obj.get("rest_id") and (obj.get("legacy") or obj.get("core")) and obj.get("__typename", "User") == "User":
            return flat_user(obj)
    return None


def _unwrap_tweet(tweet: Any) -> Any:
    """The tweet inside a ``TweetWithVisibilityResults`` wrapper, or ``tweet`` itself."""
    if isinstance(tweet, dict) and tweet.get("__typename") == "TweetWithVisibilityResults":
        return tweet.get("tweet")
    return tweet


def _tweet_text(tweet: Dict[str, Any]) -> str:
    """Long-form ``note_tweet`` text when present, else ``legacy.full_text``."""
    note = (((tweet.get("note_tweet") or {}).get("note_tweet_results") or {}).get("result") or {})
    return note.get("text") or (tweet.get("legacy") or {}).get("full_text") or ""


def _screen_name(tweet: Dict[str, Any]) -> str:
    """The author's handle (``core.screen_name`` since 2025, ``legacy.screen_name`` before)."""
    author = ((tweet.get("core") or {}).get("user_results") or {}).get("result") or {}
    return (author.get("core") or {}).get("screen_name") or (author.get("legacy") or {}).get("screen_name") or ""


def tweets(data: Any) -> List[Dict[str, Any]]:
    """Every tweet in a response, flattened and de-duplicated by ID, newest first.

    Entries with an empty ``tweet_results`` (deleted tweets or articles) are skipped. For a
    retweet, ``text`` is ``"RT @user: "`` plus the original's full text and ``retweet_of`` is
    the original author.
    """
    out: Dict[str, Dict[str, Any]] = {}
    for obj in walk(data):
        holder = obj.get("tweet_results")
        tweet = _unwrap_tweet(holder.get("result") if isinstance(holder, dict) else None)
        if not isinstance(tweet, dict) or not isinstance(tweet.get("legacy"), dict):
            continue
        tid = tweet.get("rest_id")
        if not tid or tid in out:
            continue
        legacy = tweet["legacy"]
        username = _screen_name(tweet)
        text = _tweet_text(tweet)
        retweet_of = ""
        # A retweet's own full_text is "RT @user: " plus a truncated copy; use the original.
        original = _unwrap_tweet(((legacy.get("retweeted_status_result") or {}).get("result")))
        if isinstance(original, dict) and isinstance(original.get("legacy"), dict):
            retweet_of = _screen_name(original)
            text = f"RT @{retweet_of}: {_tweet_text(original)}"
        out[tid] = {
            "id": tid,
            "created_at": legacy.get("created_at", ""),
            "author": username,
            "text": text,
            "likes": _int(legacy.get("favorite_count")) or 0,
            "retweets": _int(legacy.get("retweet_count")) or 0,
            "replies": _int(legacy.get("reply_count")) or 0,
            "views": _int((tweet.get("views") or {}).get("count")),
            "retweet_of": retweet_of,
            "url": f"https://x.com/{username or 'i'}/status/{tid}",
        }
    # Tweet IDs grow over time, so sorting by ID sorts by time.
    return sorted(out.values(), key=lambda t: int(t["id"]), reverse=True)


def trends(data: Any) -> List[Dict[str, Any]]:
    """Trend objects (``{"name": ..., "tweet_volume": ...}``) found anywhere in a response."""
    seen = set()
    out = []
    for obj in walk(data):
        name = obj.get("name")
        if isinstance(name, str) and "woeid" not in obj and ("tweet_volume" in obj or "query" in obj or "url" in obj):
            if name not in seen:
                seen.add(name)
                out.append({"name": name, "tweet_volume": _int(obj.get("tweet_volume"))})
    return out


def locations(data: Any) -> List[Dict[str, Any]]:
    """Trend locations (objects with ``woeid`` and ``name``) found anywhere in a response."""
    out = []
    for obj in walk(data):
        if "woeid" in obj and isinstance(obj.get("name"), str) and _int(obj["woeid"]) is not None:
            place = obj.get("placeType")
            out.append({
                "woeid": _int(obj["woeid"]),
                "name": obj["name"],
                "country": obj.get("country") or "",
                "country_code": obj.get("countryCode") or "",
                "type": place.get("name") if isinstance(place, dict) else (place or ""),
            })
    return out
