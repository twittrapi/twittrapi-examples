// Small, defensive helpers for reading X's raw GraphQL JSON.
//
// TwittrAPI returns X's responses unchanged. The response shapes come from X, are not documented
// and may change at any time, so these helpers walk the whole response looking for the objects
// they need instead of following one fixed path. If a field moves you get an empty value, not a
// crash. Check a real response before relying on a field.

/** Yields every plain object inside `node`, depth first. */
export function* walk(node) {
  const stack = [node];
  while (stack.length) {
    const n = stack.pop();
    if (Array.isArray(n)) {
      for (let i = n.length - 1; i >= 0; i--) stack.push(n[i]);
    } else if (n && typeof n === "object") {
      yield n;
      const values = Object.values(n);
      for (let i = values.length - 1; i >= 0; i--) stack.push(values[i]);
    }
  }
}

const num = (v) => (v === undefined || v === null || v === "" || Number.isNaN(Number(v)) ? null : Number(v));

/** Flattens a `user_results.result` object. */
export function flatUser(u) {
  const legacy = u.legacy ?? {};
  const core = u.core ?? {}; // X moved name/screen_name from legacy to core in 2025
  return {
    id: u.rest_id,
    username: core.screen_name ?? legacy.screen_name ?? "",
    name: core.name ?? legacy.name ?? "",
    followers: num(legacy.followers_count),
    following: num(legacy.friends_count),
    tweets: num(legacy.statuses_count),
    verified: Boolean(u.is_blue_verified ?? legacy.verified),
    createdAt: core.created_at ?? legacy.created_at ?? "",
    location: (typeof u.location === "object" ? u.location?.location : null) ?? legacy.location ?? "",
    bio: legacy.description ?? u.profile_bio?.description ?? "",
  };
}

/** Every user in a response, flattened and de-duplicated by ID, in response order. */
export function extractUsers(data) {
  const users = new Map();
  for (const obj of walk(data)) {
    const u = obj.user_results?.result;
    if (u?.rest_id && !users.has(u.rest_id)) users.set(u.rest_id, flatUser(u));
  }
  return [...users.values()];
}

/** The profile in a user lookup response (`data.user.result`), flattened, or null. */
export function extractProfile(data) {
  for (const obj of walk(data)) {
    if (obj.rest_id && (obj.legacy || obj.core) && (obj.__typename ?? "User") === "User") return flatUser(obj);
  }
  return null;
}

/** Every tweet in a response, flattened and de-duplicated by ID, newest first. */
export function extractTweets(data) {
  const tweets = new Map();
  for (const obj of walk(data)) {
    let t = obj.tweet_results?.result;
    if (t?.__typename === "TweetWithVisibilityResults") t = t.tweet;
    if (!t?.legacy || !t.rest_id || tweets.has(t.rest_id)) continue;
    const author = t.core?.user_results?.result;
    const username = author?.core?.screen_name ?? author?.legacy?.screen_name ?? "";
    tweets.set(t.rest_id, {
      id: t.rest_id,
      createdAt: t.legacy.created_at ?? "",
      author: username,
      text: t.note_tweet?.note_tweet_results?.result?.text ?? t.legacy.full_text ?? "",
      likes: num(t.legacy.favorite_count) ?? 0,
      retweets: num(t.legacy.retweet_count) ?? 0,
      replies: num(t.legacy.reply_count) ?? 0,
      views: num(t.views?.count),
      lang: t.legacy.lang ?? "",
      url: `https://x.com/${username || "i"}/status/${t.rest_id}`,
    });
  }
  // Tweet IDs grow over time, so sorting by ID sorts by time.
  return [...tweets.values()].sort((a, b) => (BigInt(b.id) > BigInt(a.id) ? 1 : -1));
}

/** Converts rows of flat objects to CSV text. */
export function toCsv(rows, fields = Object.keys(rows[0] ?? {})) {
  const cell = (v) => {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [fields.join(","), ...rows.map((r) => fields.map((f) => cell(r[f])).join(","))].join("\n") + "\n";
}

/** Communities in a community search response: `{ id, name, members }`. */
export function extractCommunities(data) {
  const found = new Map();
  for (const obj of walk(data)) {
    const id = obj.rest_id ?? obj.id_str;
    if (id && typeof obj.name === "string" && (obj.__typename === "Community" || "member_count" in obj)) {
      if (!found.has(id)) found.set(id, { id, name: obj.name, members: num(obj.member_count) });
    }
  }
  return [...found.values()];
}
