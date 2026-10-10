# Get Twitter trends with curl

Get the current Twitter/X trending topics for any location with `curl` and `jq`. Use `--locations` to find the WOEID for a country or city.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd shell/get-twitter-trends-with-curl
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
./trends.sh                  # worldwide
./trends.sh 23424829         # Germany
./trends.sh --locations | grep -i germany

# the raw request:
curl -s -H "X-API-KEY: $TWITTRAPI_API_KEY" https://api.twittrapi.com/trends/1
```

## Sample output

```text
#Bundesliga	125000
Formula 1	48200
Open Source	
```

_Output values are illustrative._

## Notes

Needs `curl` and `jq`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
