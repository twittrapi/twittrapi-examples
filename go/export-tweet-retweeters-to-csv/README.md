# Export who retweeted a tweet to CSV (Go)

See who retweeted a tweet and export the accounts to CSV: ID, username, name, follower counts, verified flag and bio. With `-quotes`, export the quote tweets instead.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd go      # from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
go run ./export-tweet-retweeters-to-csv -o retweeters.csv https://x.com/jack/status/20
go run ./export-tweet-retweeters-to-csv -quotes -o quotes.csv 20
```

## Sample output

```text
Wrote 412 rows to retweeters.csv

$ head -2 retweeters.csv
id,username,name,followers,following,verified,bio
1580000000000000001,example_dev,Example Dev,1204,311,true,Building things on the internet
```

_Output values are illustrative._

## Notes

Uses `twittrapi.Paginate` over `client.Tweets.Retweeters` (or `client.Tweets.Quotes`).

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
