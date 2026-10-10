"""Append tweets matching a search to a Google Sheet.

    export TWITTRAPI_API_KEY=...                         # or RAPIDAPI_KEY=...
    export GOOGLE_APPLICATION_CREDENTIALS=service-account.json
    python tweets_to_sheets.py "your brand -filter:retweets" --sheet-id 1AbC...xyz

Share the sheet with the service account's e-mail address first. Tweets already in the
sheet (by ID in column A) are skipped, so you can run this on a schedule.
"""

import argparse
import os
import sys
from pathlib import Path

import gspread
from twittrapi import TwittrAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
import extract  # noqa: E402

HEADER = ["id", "created_at", "author", "text", "likes", "retweets", "replies", "views", "url"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Append search results to a Google Sheet.")
    parser.add_argument("query", help="X search query")
    parser.add_argument("--sheet-id", default=os.environ.get("SHEET_ID"), help="spreadsheet ID from its URL")
    parser.add_argument("--worksheet", default="tweets")
    parser.add_argument("--max-pages", type=int, default=2)
    args = parser.parse_args()
    if not args.sheet_id:
        sys.exit("Pass --sheet-id or set SHEET_ID")

    gc = gspread.service_account(filename=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json"))
    spreadsheet = gc.open_by_key(args.sheet_id)
    try:
        ws = spreadsheet.worksheet(args.worksheet)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(args.worksheet, rows=1000, cols=len(HEADER))
        ws.append_row(HEADER)
    existing = set(ws.col_values(1))

    rows = []
    with TwittrAPI() as client:
        for page in client.paginate(client.search.tweets, args.query, category="Latest", count=20, max_pages=args.max_pages):
            for t in extract.tweets(page):
                if t["id"] not in existing:
                    existing.add(t["id"])
                    rows.append(["" if t[k] is None else t[k] for k in HEADER])

    if rows:
        # Oldest first, so the sheet reads top to bottom in time order.
        ws.append_rows(list(reversed(rows)), value_input_option="RAW")
    print(f"Added {len(rows)} new tweets to '{args.worksheet}'")


if __name__ == "__main__":
    main()
