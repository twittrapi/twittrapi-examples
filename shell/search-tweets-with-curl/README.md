# Search tweets with curl

Search Twitter/X from the command line with `curl` and turn the result into one compact JSON object per tweet with `jq`. Pipe it into other tools or append it to a `.jsonl` file.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd shell/search-tweets-with-curl
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
./search.sh "openai lang:en -filter:replies"
./search.sh "from:nasa" Top > nasa.jsonl

# the raw request:
curl -s -G -H "X-API-KEY: $TWITTRAPI_API_KEY" https://api.twittrapi.com/search \
  --data-urlencode "searchItem=from:nasa" --data-urlencode "category=Latest"
```

## Sample output

```text
{"id":"1976512345678901234","author":"example_dev","created_at":"Fri Oct 09 18:42:00 +0000 2026","likes":42,"text":"..."}
{"id":"1976498765432109876","author":"another_user","created_at":"Fri Oct 09 17:10:00 +0000 2026","likes":7,"text":"..."}
```

_Output values are illustrative._

## Notes

Needs `curl` and `jq`. Category is `Top`, `Latest` (default), `Photos` or `Videos`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
