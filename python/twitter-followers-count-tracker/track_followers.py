"""Track Twitter/X follower counts over time in a CSV file.

    export TWITTRAPI_API_KEY=...        # or RAPIDAPI_KEY=...
    python track_followers.py jack nasa github --csv follower_history.csv

Run it once a day (cron, GitHub Actions, ...). Each run appends one row per account and
prints the change since the previous run. One request per account.
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from twittrapi import NotFoundError, TwittrAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
import extract  # noqa: E402

FIELDS = ["checked_at", "username", "id", "followers", "following", "tweets"]


def last_counts(path: str) -> Dict[str, int]:
    """Most recent follower count per username from an existing history file."""
    counts: Dict[str, int] = {}
    if not os.path.exists(path):
        return counts
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("followers", "").isdigit():
                counts[row["username"].lower()] = int(row["followers"])
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Append follower counts to a CSV history.")
    parser.add_argument("usernames", nargs="+")
    parser.add_argument("--csv", default="follower_history.csv")
    args = parser.parse_args()

    previous = last_counts(args.csv)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_file = not os.path.exists(args.csv)

    with TwittrAPI() as client, open(args.csv, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        for name in args.usernames:
            name = name.lstrip("@")
            try:
                user = extract.first_user(client.users.get_by_username(name))
            except NotFoundError:
                print(f"@{name}: not found", file=sys.stderr)
                continue
            if not user or user["followers"] is None:
                print(f"@{name}: no follower count in response", file=sys.stderr)
                continue
            writer.writerow({"checked_at": now, **user, "username": user["username"] or name})
            before = previous.get((user["username"] or name).lower())
            change = "" if before is None else f" ({user['followers'] - before:+,})"
            print(f"@{user['username'] or name}: {user['followers']:,} followers{change}")


if __name__ == "__main__":
    main()
