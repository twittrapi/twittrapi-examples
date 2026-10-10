"""Export a Twitter/X user's followers to a CSV file.

    export TWITTRAPI_API_KEY=...        # or RAPIDAPI_KEY=...
    python export_followers.py jack followers.csv --max-pages 5

Each page is one billed request (up to 100 followers per page with --count 100).
"""

import argparse
import csv
import sys
from pathlib import Path

from twittrapi import NotFoundError, TwittrAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
import extract  # noqa: E402

FIELDS = ["id", "username", "name", "followers", "following", "tweets", "verified", "created_at", "bio"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a user's followers to CSV.")
    parser.add_argument("username", help="handle, with or without @")
    parser.add_argument("output", nargs="?", default="followers.csv", help="CSV file to write")
    parser.add_argument("--max-pages", type=int, default=5, help="pages to fetch (each is one request)")
    parser.add_argument("--count", type=int, default=100, help="followers per page, max 100")
    args = parser.parse_args()

    seen = set()
    with TwittrAPI() as client, open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        try:
            pages = client.paginate(
                client.users.followers, username=args.username, count=args.count, max_pages=args.max_pages
            )
            for n, page in enumerate(pages, 1):
                new = [u for u in extract.users(page) if u["id"] not in seen]
                for user in new:
                    seen.add(user["id"])
                    writer.writerow(user)
                print(f"page {n}: {len(new)} followers", file=sys.stderr)
        except NotFoundError:
            sys.exit(f"User @{args.username.lstrip('@')} not found")

    print(f"Wrote {len(seen)} followers of @{args.username.lstrip('@')} to {args.output}")


if __name__ == "__main__":
    main()
