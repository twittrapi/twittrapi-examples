// Find tweets that mention a brand (by name or @handle), excluding the brand's own tweets.
//
//   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
//   node brand-mentions.mjs --name "Notion" --handle NotionHQ --since 2026-10-01
//   node brand-mentions.mjs --name "Linear" --lang en --pages 3 --json mentions.json
//
// Prints the most engaging mentions first, plus a short summary.
import { writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { TwittrAPI } from "twittrapi";
import { extractTweets } from "../_shared/extract.mjs";

const { values } = parseArgs({
  options: {
    name: { type: "string" },
    handle: { type: "string" },
    since: { type: "string" }, // YYYY-MM-DD
    lang: { type: "string" },
    pages: { type: "string", default: "2" },
    json: { type: "string" },
  },
});
if (!values.name && !values.handle) {
  console.error('Usage: node brand-mentions.mjs --name "Brand" [--handle brand] [--since YYYY-MM-DD] [--lang en]');
  process.exit(1);
}

// Build an X search query: ("Brand" OR @brand) -from:brand -filter:retweets
const handle = values.handle?.replace(/^@/, "");
const terms = [values.name && `"${values.name}"`, handle && `@${handle}`].filter(Boolean);
const query = [
  terms.length > 1 ? `(${terms.join(" OR ")})` : terms[0],
  handle && `-from:${handle}`,
  "-filter:retweets",
  values.since && `since:${values.since}`,
  values.lang && `lang:${values.lang}`,
]
  .filter(Boolean)
  .join(" ");

const client = new TwittrAPI();
const mentions = new Map();
for await (const page of client.paginate(client.search.tweets, { query, category: "Latest", count: 20 }, { maxPages: Number(values.pages) })) {
  for (const t of extractTweets(page.data)) if (!mentions.has(t.id)) mentions.set(t.id, t);
}

const ranked = [...mentions.values()].sort((a, b) => b.likes + 2 * b.retweets - (a.likes + 2 * a.retweets));
console.log(`Query: ${query}`);
console.log(`${ranked.length} mentions by ${new Set(ranked.map((t) => t.author)).size} accounts\n`);
for (const t of ranked.slice(0, 15)) {
  console.log(`${String(t.likes).padStart(6)} likes  @${t.author}: ${t.text.replace(/\s+/g, " ").slice(0, 120)}`);
  console.log(`              ${t.url}`);
}
if (values.json) {
  writeFileSync(values.json, JSON.stringify(ranked, null, 2));
  console.log(`\nSaved all mentions to ${values.json}`);
}
