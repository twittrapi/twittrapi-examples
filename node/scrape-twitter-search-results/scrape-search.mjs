// Scrape Twitter/X search results to CSV or JSON with Node.js.
//
//   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
//   node scrape-search.mjs "node.js lang:en min_faves:10" --pages 3 --out results.csv
//   node scrape-search.mjs "from:nodejs" --tab Top --out results.json
//
// --tab is one of Top, Latest (default), Photos, Videos. Each page is one request (~20 tweets).
import { writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { TwittrAPI } from "twittrapi";
import { extractTweets, toCsv } from "../_shared/extract.mjs";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    pages: { type: "string", default: "3" },
    tab: { type: "string", default: "Latest" },
    out: { type: "string", default: "results.csv" },
  },
});
const query = positionals[0];
if (!query) {
  console.error('Usage: node scrape-search.mjs "<search query>" [--pages 3] [--tab Latest] [--out results.csv]');
  process.exit(1);
}

const client = new TwittrAPI();
const tweets = new Map();

for await (const page of client.paginate(
  client.search.tweets,
  // The SDK checks the tab name and throws a ValidationError for anything else.
  { query, category: /** @type {import("twittrapi").SearchCategory} */ (values.tab), count: 20 },
  { maxPages: Number(values.pages) },
)) {
  const found = extractTweets(page.data);
  for (const t of found) if (!tweets.has(t.id)) tweets.set(t.id, t);
  console.error(`page ${page.pageNumber}: ${found.length} tweets`);
}

const rows = [...tweets.values()];
const output = values.out.endsWith(".json") ? JSON.stringify(rows, null, 2) : toCsv(rows);
writeFileSync(values.out, output);
console.log(`Saved ${rows.length} tweets for "${query}" to ${values.out}`);
