"""Download tweets to a JSON file, from a search query or a user's timeline.

    export TWITTRAPI_API_KEY=...        # or RAPIDAPI_KEY=...
    python download_tweets.py --search "python lang:en" -o tweets.json
    python download_tweets.py --user jack -o jack.json --max-pages 5
    python download_tweets.py --user jack --raw -o jack-raw.json   # X's raw pages, unparsed
"""

import argparse
import json
import sys
from pathlib import Path

from twittrapi import TwittrAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
import extract  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download tweets to JSON.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--search", metavar="QUERY", help="X search query (operators like from:, lang: work)")
    source.add_argument("--user", metavar="USERNAME", help="download a user's timeline")
    parser.add_argument("-o", "--output", default="tweets.json")
    parser.add_argument("--max-pages", type=int, default=3, help="each page is one request")
    parser.add_argument("--raw", action="store_true", help="save X's raw JSON pages instead of flat tweets")
    args = parser.parse_args()

    with TwittrAPI() as client:
        if args.search:
            pages = client.paginate(client.search.tweets, args.search, category="Latest", count=20, max_pages=args.max_pages)
        else:
            pages = client.paginate(client.users.tweets, username=args.user, count=20, max_pages=args.max_pages)
        raw_pages = list(pages)

    if args.raw:
        result = raw_pages
        summary = f"{len(raw_pages)} raw pages"
    else:
        merged = {}
        for page in raw_pages:
            for tweet in extract.tweets(page):
                merged.setdefault(tweet["id"], tweet)
        result = sorted(merged.values(), key=lambda t: int(t["id"]), reverse=True)
        summary = f"{len(result)} tweets"

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"Saved {summary} to {args.output}")


if __name__ == "__main__":
    main()
