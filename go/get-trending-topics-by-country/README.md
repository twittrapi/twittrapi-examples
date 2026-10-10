# Get Twitter trending topics by country (Go)

Get the current Twitter/X trending topics for any country or city in Go. Pass a two-letter country code, a place name or `world`; the program looks up the WOEID and prints the trends with post volume when X reports it.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd go      # from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
go run ./get-trending-topics-by-country DE
go run ./get-trending-topics-by-country "New York"
go run ./get-trending-topics-by-country -list
```

## Sample output

```text
Trending in Germany (WOEID 23424829)
  1. #Bundesliga  (125000 posts)
  2. Formula 1  (48200 posts)
  3. Open Source
...
```

_Output values are illustrative._

## Notes

Two requests: `client.Trends.Locations` and `client.Trends.Get`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
