"""Export the members of a Twitter/X list to CSV.

    export TWITTRAPI_API_KEY=...        # or RAPIDAPI_KEY=...
    python export_list_members.py 84839422 members.csv

The list ID is the number in the list URL: https://x.com/i/lists/<list_id>
(84839422 is X's public "Official Twitter Accounts" list.)
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from twittrapi import NotFoundError, TwittrAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
import extract  # noqa: E402

FIELDS = ["id", "username", "name", "followers", "following", "tweets", "verified", "bio"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export list members to CSV.")
    parser.add_argument("list", help="list ID or list URL")
    parser.add_argument("output", nargs="?", default="list_members.csv")
    parser.add_argument("--max-pages", type=int, default=10)
    args = parser.parse_args()

    match = re.search(r"(\d{5,})", args.list)
    if not match:
        sys.exit("Could not find a numeric list ID in the argument")
    list_id = match.group(1)

    seen = set()
    with TwittrAPI() as client, open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        try:
            for page in client.paginate(client.lists.members, list_id, count=100, max_pages=args.max_pages):
                for user in extract.users(page):
                    if user["id"] not in seen:
                        seen.add(user["id"])
                        writer.writerow(user)
        except NotFoundError:
            sys.exit(f"List {list_id} not found (private lists are not available)")

    print(f"Wrote {len(seen)} members of list {list_id} to {args.output}")


if __name__ == "__main__":
    main()
