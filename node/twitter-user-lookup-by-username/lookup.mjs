// Look up Twitter/X users by username: ID, name, follower counts, bio and join date.
//
//   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
//   node lookup.mjs jack nasa @github
//   node lookup.mjs jack --json        # flat JSON instead of a table
//   node lookup.mjs jack --raw         # X's raw response for the first user
//
// One request per username.
import { parseArgs } from "node:util";
import { NotFoundError, TwittrAPI } from "twittrapi";
import { extractProfile } from "../_shared/extract.mjs";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: { json: { type: "boolean", default: false }, raw: { type: "boolean", default: false } },
});
if (positionals.length === 0) {
  console.error("Usage: node lookup.mjs <username> [more usernames] [--json | --raw]");
  process.exit(1);
}

const client = new TwittrAPI();

if (values.raw) {
  console.log(JSON.stringify(await client.users.getByUsername(positionals[0]), null, 2));
  process.exit(0);
}

const profiles = [];
for (const username of positionals) {
  try {
    const profile = extractProfile(await client.users.getByUsername(username));
    if (profile) profiles.push(profile);
    else console.error(`@${username}: unexpected response shape, try --raw`);
  } catch (err) {
    if (err instanceof NotFoundError) console.error(`@${username.replace(/^@/, "")}: not found or suspended`);
    else throw err;
  }
}

if (values.json) {
  console.log(JSON.stringify(profiles, null, 2));
} else {
  for (const p of profiles) {
    console.log(`@${p.username} (${p.name})${p.verified ? " [verified]" : ""}`);
    console.log(`  id:        ${p.id}`);
    console.log(`  followers: ${p.followers?.toLocaleString("en-US") ?? "?"}   following: ${p.following?.toLocaleString("en-US") ?? "?"}   tweets: ${p.tweets?.toLocaleString("en-US") ?? "?"}`);
    if (p.createdAt) console.log(`  joined:    ${p.createdAt}`);
    if (p.location) console.log(`  location:  ${p.location}`);
    if (p.bio) console.log(`  bio:       ${p.bio.replace(/\s+/g, " ")}`);
    console.log("");
  }
}
