"""Tests for extract.py against trimmed real TwittrAPI responses in ../../testdata/live.

Run from the repo root (standard library only):  python -m unittest discover -s python/_shared
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402

LIVE = Path(__file__).resolve().parents[2] / "testdata" / "live"


def fixture(name):
    return json.loads((LIVE / f"{name}.json").read_text(encoding="utf-8"))


class UsersTest(unittest.TestCase):
    def test_users_from_live_fixtures(self):
        cases = {
            "user-userid-followers": "example_user_1,example_user_2",  # legacy.screen_name
            "lists-members": "TwitterAble,TwitterThailand",  # core.screen_name
            "tweet-tweetid-retweets": "example_user_1,example_user_2",
            "communities-communityid-members": "example_user_1,example_user_2",  # items_results[].result
            "user-users-by-ids": "XDevelopers,jack",  # data.users[].result
            "user-userid-likes": "",
        }
        for name, want in cases.items():
            users = extract.users(fixture(name))
            self.assertEqual(",".join(sorted(u["username"] for u in users)), want, name)
            self.assertTrue(all(u["id"] for u in users), name)


class TweetsTest(unittest.TestCase):
    def test_tweets_from_live_fixtures(self):
        cases = {
            "user-userid-tweets": ["2019881223666233717:XDevelopers"],
            "tweet-tweetid": ["2019881223666233717:XDevelopers", "2000000000000000001:example_user_1"],
            "search": ["2000000000000000001:example_user_1"],
            "user-userid-articles": ["2041295840325636551:XDevelopers"],
            "tweet-tweetid-retweets": [],
            "user-userid-likes": [],
        }
        for name, want in cases.items():
            got = [f"{t['id']}:{t['author']}" for t in extract.tweets(fixture(name))]
            self.assertEqual(got, want, name)

    def test_note_tweet_long_text(self):
        (tweet,) = extract.tweets(fixture("user-userid-media"))
        self.assertTrue(tweet["text"].endswith("Explore it now: https://t.co/XorO5ldGTN"), tweet["text"])

    def test_visibility_retweet_and_empty_results(self):
        orig = next(
            o["tweet_results"]["result"]
            for o in extract.walk(fixture("user-userid-tweets"))
            if (o.get("tweet_results") or {}).get("result", {}).get("rest_id") == "2019881223666233717"
        )
        retweet = {
            "__typename": "Tweet",
            "rest_id": "2100000000000000001",
            "core": {"user_results": {"result": {"__typename": "User", "rest_id": "1000000000000000001",
                                                 "core": {"screen_name": "example_user_1"}}}},
            "legacy": {
                "full_text": "RT @XDevelopers: Officially launching X API Pay…",
                "retweeted_status_result": {"result": {"__typename": "TweetWithVisibilityResults", "tweet": orig}},
            },
        }
        body = {"entries": [
            {"entryId": "tweet-1", "content": {"itemContent": {"tweet_results": {}}}},
            {"entryId": "tweet-2", "content": {"itemContent": {"tweet_results": {"result": retweet}}}},
            {"entryId": "tweet-3", "content": {"itemContent": {"tweet_results": {
                "result": {"__typename": "TweetWithVisibilityResults", "tweet": orig}}}}},
            {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "x"}},
        ]}
        tweets = extract.tweets(body)
        self.assertEqual(len(tweets), 2)
        rt, plain = tweets
        self.assertEqual((rt["author"], rt["retweet_of"]), ("example_user_1", "XDevelopers"))
        self.assertEqual(rt["text"], f"RT @XDevelopers: {plain['text']}")
        self.assertEqual((plain["id"], plain["author"], plain["retweet_of"]), ("2019881223666233717", "XDevelopers", ""))


if __name__ == "__main__":
    unittest.main()
