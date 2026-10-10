# Export Twitter followers to CSV with Python

This script downloads the followers of any public Twitter/X account and writes them to a CSV file: user ID, username, display name, follower and following counts, verified flag, join date and bio. It uses the `twittrapi` Python SDK and follows pagination for you; each page of up to 100 followers is one request.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd python/export-twitter-followers-to-csv
pip install -r requirements.txt
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
python export_followers.py jack followers.csv --max-pages 5
```

## Sample output

```text
page 1: 100 followers
page 2: 100 followers
...
Wrote 500 followers of @jack to followers.csv

$ head -3 followers.csv
id,username,name,followers,following,tweets,verified,created_at,bio
1580000000000000001,example_dev,Example Dev,1204,311,5120,True,Tue Mar 01 09:12:44 +0000 2016,Building things on the internet
1580000000000000002,another_user,Another User,87,140,431,False,Sat Jun 06 17:03:10 +0000 2020,
```

_Output values are illustrative._

## Notes

Use `--count` (max 100) to change the page size and `--max-pages` to cap the number of requests.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
