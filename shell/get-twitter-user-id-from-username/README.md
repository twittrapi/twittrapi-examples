# Get a Twitter user ID from a username with curl

Convert one or more Twitter/X usernames to their numeric user IDs with a single `curl` call each and `jq`. Handy for scripts and for tools that need IDs instead of handles.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd shell/get-twitter-user-id-from-username
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
./user-id.sh jack nasa @github

# the raw request:
curl -s -H "X-API-KEY: $TWITTRAPI_API_KEY" https://api.twittrapi.com/username/to/id/jack
```

## Sample output

```text
jack	12
nasa	11348282
github	13334762
```

_Output values are illustrative._

## Notes

Needs `curl` and `jq`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
