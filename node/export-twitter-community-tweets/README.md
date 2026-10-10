# Export Twitter Community tweets (Node.js)

Export the tweets posted in an X (Twitter) Community to a JSON Lines or CSV file. If you don't know the community ID, search for communities by keyword first.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd node && npm install    # once, from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
node export-twitter-community-tweets/export-community.mjs --search "javascript"
node export-twitter-community-tweets/export-community.mjs 1500000000000000000 --pages 5 --out community.jsonl
```

## Sample output

```text
1500000000000000000  JavaScript  (48210 members)
1500000000000000001  JavaScript Jobs  (5120 members)

Exported 97 tweets from community 1500000000000000000 to community.jsonl
```

_Output values are illustrative._

## Notes

The community ID is the number in the community URL: `x.com/i/communities/<id>`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
