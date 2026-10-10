# Send tweets to Google Sheets with Python

Collect tweets that match a search query in a Google Sheet. The script appends new tweets (ID, date, author, text, likes, retweets, replies, views, link) to a worksheet and skips tweets that are already there, so you can run it every hour.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd python/tweets-to-google-sheets
pip install -r requirements.txt
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
export GOOGLE_APPLICATION_CREDENTIALS=service-account.json   # Google Cloud service account key
python tweets_to_sheets.py "your brand -filter:retweets" --sheet-id 1AbCdEfGh...xyz
```

## Sample output

```text
Added 37 new tweets to 'tweets'
```

_Output values are illustrative._

## Notes

Setup for Google Sheets:

1. In Google Cloud, enable the Google Sheets API and create a service account. Download its JSON key (keep it out of git; `service-account*.json` is in `.gitignore`).
2. Share your spreadsheet with the service account's e-mail address (Editor).
3. The sheet ID is the long string in the sheet URL: `docs.google.com/spreadsheets/d/<sheet-id>/edit`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
