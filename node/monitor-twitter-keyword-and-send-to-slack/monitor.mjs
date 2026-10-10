// Monitor Twitter/X for a keyword and post new tweets to a Slack channel.
//
//   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
//   export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
//   node monitor.mjs "your keyword -filter:retweets" --interval 120
//   node monitor.mjs "your keyword" --once      # one check, e.g. from cron
//   node monitor.mjs "your keyword" --backfill  # also post tweets found on the first run
//
// Without SLACK_WEBHOOK_URL the tweets are printed instead of posted.
// Each check is one request. Seen tweet IDs are kept in .seen-<hash>.json next to this script.
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { RateLimitError, TwittrAPI } from "twittrapi";
import { extractTweets } from "../_shared/extract.mjs";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    interval: { type: "string", default: "120" },
    once: { type: "boolean", default: false },
    backfill: { type: "boolean", default: false },
  },
});
const query = positionals[0];
if (!query) {
  console.error('Usage: node monitor.mjs "<search query>" [--interval seconds] [--once] [--backfill]');
  process.exit(1);
}

const webhook = process.env.SLACK_WEBHOOK_URL;
const stateFile = new URL(`.seen-${createHash("sha1").update(query).digest("hex").slice(0, 8)}.json`, import.meta.url);
const seen = new Set(existsSync(stateFile) ? JSON.parse(readFileSync(stateFile, "utf8")) : []);
let skipExisting = seen.size === 0 && !values.backfill;
const client = new TwittrAPI();

async function notify(tweet) {
  const text = `*@${tweet.author}* mentioned "${query}":\n>${tweet.text.replace(/\n/g, "\n>")}\n<${tweet.url}|Open on X> · ${tweet.likes} likes`;
  if (!webhook) {
    console.log(`[new] @${tweet.author}: ${tweet.text.replace(/\s+/g, " ")}\n      ${tweet.url}`);
    return;
  }
  const res = await fetch(webhook, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text, unfurl_links: false }),
  });
  if (!res.ok) console.error(`Slack returned ${res.status}: ${await res.text()}`);
}

async function check() {
  const data = await client.search.tweets({ query, category: "Latest", count: 20 });
  const fresh = extractTweets(data).filter((t) => !seen.has(t.id)).reverse(); // oldest first
  for (const t of fresh) seen.add(t.id);
  // On the very first run, remember existing tweets without flooding the channel.
  if (skipExisting) {
    console.log(`Watching "${query}". Skipped ${fresh.length} existing tweets.`);
    skipExisting = false;
  } else {
    for (const t of fresh) await notify(t);
    console.log(`${new Date().toISOString()} ${fresh.length} new tweet(s)`);
  }
  writeFileSync(stateFile, JSON.stringify([...seen].slice(-2000)));
}

while (true) {
  try {
    await check();
  } catch (err) {
    if (err instanceof RateLimitError) console.error(`Rate limited, retrying next round: ${err.message}`);
    else throw err;
  }
  if (values.once) break;
  await new Promise((r) => setTimeout(r, Number(values.interval) * 1000));
}
