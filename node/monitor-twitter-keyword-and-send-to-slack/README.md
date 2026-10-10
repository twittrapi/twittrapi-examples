# Monitor a Twitter keyword and send new tweets to Slack (Node.js)

Watch Twitter/X for a keyword, hashtag or brand name and post every new matching tweet to a Slack channel through an incoming webhook. It polls search on an interval (or once, for cron), remembers which tweets it already posted, and works without Slack too: with no webhook set it prints to the terminal.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd node && npm install    # once, from the repository root
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T000/B000/XXXX
node monitor-twitter-keyword-and-send-to-slack/monitor.mjs "acme OR @acme -filter:retweets" --interval 120

# or one check per cron run:
node monitor-twitter-keyword-and-send-to-slack/monitor.mjs "acme" --once
```

## Sample output

```text
Watching "acme OR @acme -filter:retweets". Skipped 20 existing tweets.
2026-10-10T08:02:00.112Z 0 new tweet(s)
2026-10-10T08:04:00.540Z 2 new tweet(s)

Slack message:
  *@example_dev* mentioned "acme OR @acme -filter:retweets":
  > Just switched our team to Acme, setup took 5 minutes
  Open on X · 12 likes
```

_Output values are illustrative._

## Notes

Create the webhook in Slack under *Apps → Incoming Webhooks*. The first run only records existing tweets so the channel is not flooded; add `--backfill` to post them too. Each check is one request.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
