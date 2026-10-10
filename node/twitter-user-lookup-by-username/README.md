# Twitter user lookup by username (Node.js)

Look up Twitter/X profiles by username from Node.js: numeric user ID, display name, follower, following and tweet counts, verified flag, join date, location and bio. Prints a readable summary, flat JSON (`--json`) or X's raw response (`--raw`).

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd node && npm install    # once, from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
node twitter-user-lookup-by-username/lookup.mjs jack nasa @github
node twitter-user-lookup-by-username/lookup.mjs jack --json
```

## Sample output

```text
@jack (jack) [verified]
  id:        12
  followers: 6,400,000   following: 4,500   tweets: 29,000
  joined:    Tue Mar 21 20:50:14 +0000 2006
  bio:       no state is the best state
```


## Notes

One request per username (`client.users.getByUsername`). Values above are illustrative.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
