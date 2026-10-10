// Export tweets from a Twitter/X Community to JSON Lines or CSV.
//
//   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
//   node export-community.mjs 1500000000000000000 --pages 5 --out community.jsonl
//   node export-community.mjs --search "javascript"        # find community IDs first
//
// The community ID is the number in the URL: https://x.com/i/communities/<id>
import { writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { TwittrAPI } from "twittrapi";
import { extractCommunities, extractTweets, toCsv } from "../_shared/extract.mjs";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    search: { type: "string" },
    pages: { type: "string", default: "3" },
    out: { type: "string", default: "community.jsonl" },
  },
});

const client = new TwittrAPI();

if (values.search) {
  const found = extractCommunities(await client.communities.search({ query: values.search }));
  for (const c of found) console.log(`${c.id}  ${c.name}  (${c.members ?? "?"} members)`);
  if (found.length === 0) console.log("No communities found");
  process.exit(0);
}

const communityId = positionals[0]?.match(/\d{5,}/)?.[0];
if (!communityId) {
  console.error("Usage: node export-community.mjs <community id or URL> [--pages 3] [--out file.jsonl|file.csv]");
  process.exit(1);
}

const tweets = new Map();
for await (const page of client.paginate(client.communities.tweets, { communityId, count: 20 }, { maxPages: Number(values.pages) })) {
  for (const t of extractTweets(page.data)) if (!tweets.has(t.id)) tweets.set(t.id, t);
}

const rows = [...tweets.values()];
const body = values.out.endsWith(".csv") ? toCsv(rows) : rows.map((r) => JSON.stringify(r)).join("\n") + "\n";
writeFileSync(values.out, body);
console.log(`Exported ${rows.length} tweets from community ${communityId} to ${values.out}`);
