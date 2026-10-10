"""Get the latest tweets from a Twitter/X user and print them.

    export TWITTRAPI_API_KEY=...        # or RAPIDAPI_KEY=...
    python get_user_tweets.py jack --limit 20
    python get_user_tweets.py jack --replies     # include replies
"""

import argparse
import sys
from pathlib import Path

from twittrapi import NotFoundError, TwittrAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
import extract  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a user's latest tweets.")
    parser.add_argument("username", help="handle, with or without @")
    parser.add_argument("--limit", type=int, default=20, help="how many tweets to print")
    parser.add_argument("--replies", action="store_true", help="include replies")
    parser.add_argument("--max-pages", type=int, default=3)
    args = parser.parse_args()

    collected = {}
    with TwittrAPI() as client:
        method = client.users.tweets_and_replies if args.replies else client.users.tweets
        try:
            for page in client.paginate(method, username=args.username, count=20, max_pages=args.max_pages):
                for tweet in extract.tweets(page):
                    collected.setdefault(tweet["id"], tweet)
                if len(collected) >= args.limit:
                    break
        except NotFoundError:
            sys.exit(f"User @{args.username.lstrip('@')} not found")

    # User timelines can include pinned tweets and retweets, so sort by ID (time) again.
    for tweet in sorted(collected.values(), key=lambda t: int(t["id"]), reverse=True)[: args.limit]:
        text = " ".join(tweet["text"].split())
        print(f"{tweet['created_at']}  likes={tweet['likes']}  rts={tweet['retweets']}")
        print(f"  @{tweet['author']}: {text}")
        print(f"  {tweet['url']}\n")


if __name__ == "__main__":
    main()
