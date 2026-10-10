# Scrape Twitter search results with Node.js

Get Twitter/X search results into a CSV or JSON file from Node.js, without a browser or headless scraper. Any X search query works, including operators like `from:`, `lang:`, `since:` and `min_faves:`, and the script follows pagination for you.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd node && npm install    # once, from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
node scrape-twitter-search-results/scrape-search.mjs "node.js lang:en min_faves:10" --pages 3 --out results.csv
node scrape-twitter-search-results/scrape-search.mjs "from:nodejs" --tab Top --out results.json
```

## Sample output

```text
page 1: 20 tweets
page 2: 19 tweets
page 3: 20 tweets
Saved 59 tweets for "node.js lang:en min_faves:10" to results.csv
```

_Output values are illustrative._

## Notes

Each page is one request of about 20 tweets. `--tab` is `Top`, `Latest` (default), `Photos` or `Videos`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
