# Get replies to a tweet (Go)

Get the replies to any tweet from its ID or URL in Go. Replies can be sorted by relevance, recency or likes, paged through, and saved to a JSON file.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd go      # from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
go run ./get-replies-to-a-tweet https://x.com/jack/status/20
go run ./get-replies-to-a-tweet -sort Likes -pages 3 -o replies.json 20
```

## Sample output

```text
@jack: just setting up my twttr
25000 replies · 250000 likes

  @example_dev (50 likes): Where it all started
  @another_user (47 likes): Happy anniversary!
...

8 direct replies fetched
```

_Output values are illustrative._

## Notes

Uses `client.Tweets.Get` with a ranking mode and follows the bottom cursor by hand with `twittrapi.ExtractBottomCursor`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
