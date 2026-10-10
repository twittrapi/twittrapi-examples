# Find tweets mentioning a brand (Node.js)

Find tweets that mention your brand, product or a competitor, by name or @handle, while excluding the brand's own tweets and retweets. Results are ranked by engagement and can be saved to JSON for reporting.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd node && npm install    # once, from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
node find-tweets-mentioning-a-brand/brand-mentions.mjs --name "Acme" --handle acme --since 2026-10-01 --lang en
node find-tweets-mentioning-a-brand/brand-mentions.mjs --name "Acme" --json mentions.json
```

## Sample output

```text
Query: ("Acme" OR @acme) -from:acme -filter:retweets since:2026-10-01 lang:en
38 mentions by 31 accounts

   412 likes  @example_dev: Acme's new release is the first one that just works out of the box
              https://x.com/example_dev/status/1976512345678901234
    96 likes  @another_user: @acme any plans for an EU data region?
              https://x.com/another_user/status/1976498765432109876
...
```

_Output values are illustrative._

## Notes

The script only builds an X search query and calls `client.search.tweets`; edit the query to add `min_faves:`, `-is:reply` style filters or more names.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
