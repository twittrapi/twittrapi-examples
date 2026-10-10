# Track competitor tweets (Go)

Keep an eye on what competitors post on Twitter/X. Each run checks the accounts you pass, prints tweets that are new since the last run with likes, reposts, replies and views, and stores the last seen tweet per account in a small JSON file. Run it from cron or a GitHub Action.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd go      # from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
go run ./track-competitor-tweets -state competitors.json linear notionhq figma
go run ./track-competitor-tweets -json linear notionhq figma >> new-tweets.jsonl
```

## Sample output

```text
@linear  Fri Oct 09 16:01:00 +0000 2026
  Introducing triage rules for every team.
  812 likes · 64 reposts · 41 replies · 120330 views
  https://x.com/linear/status/1976400000000000001

1 new tweet(s) across 3 account(s)
```

_Output values are illustrative._

## Notes

The first run only records the current state. One request per account per run.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
