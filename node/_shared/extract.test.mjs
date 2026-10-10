// Tests for extract.mjs against trimmed real TwittrAPI responses in ../../testdata/live.
// Run: npm test (node --test, no dependencies).
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { extractTweets, extractUsers, walk } from "./extract.mjs";

const fixture = (name) => JSON.parse(readFileSync(new URL(`../../testdata/live/${name}.json`, import.meta.url), "utf8"));
const handles = (users) => users.map((u) => u.username).sort().join(",");

test("users from followers, list members, retweeters, community members, users by IDs", () => {
  const cases = {
    "user-userid-followers": "example_user_1,example_user_2", // legacy.screen_name
    "lists-members": "TwitterAble,TwitterThailand", // core.screen_name
    "tweet-tweetid-retweets": "example_user_1,example_user_2",
    "communities-communityid-members": "example_user_1,example_user_2", // items_results[].result
    "user-users-by-ids": "XDevelopers,jack", // data.users[].result
    "user-userid-likes": "",
  };
  for (const [name, want] of Object.entries(cases)) {
    const users = extractUsers(fixture(name));
    assert.equal(handles(users), want, name);
    for (const u of users) assert.ok(u.id, `${name}: user without id`);
  }
});

test("tweets skip cursor entries and keep authors", () => {
  const cases = {
    "user-userid-tweets": ["2019881223666233717:XDevelopers"],
    "tweet-tweetid": ["2019881223666233717:XDevelopers", "2000000000000000001:example_user_1"],
    search: ["2000000000000000001:example_user_1"],
    "user-userid-articles": ["2041295840325636551:XDevelopers"],
    "tweet-tweetid-retweets": [],
    "user-userid-likes": [],
  };
  for (const [name, want] of Object.entries(cases)) {
    assert.deepEqual(extractTweets(fixture(name)).map((t) => `${t.id}:${t.author}`), want, name);
  }
});

test("note_tweet long text wins over truncated full_text", () => {
  const [tweet] = extractTweets(fixture("user-userid-media"));
  assert.ok(tweet.text.endsWith("Explore it now: https://t.co/XorO5ldGTN"), tweet.text);
});

test("visibility wrapper, retweet and empty tweet_results", () => {
  let orig;
  for (const obj of walk(fixture("user-userid-tweets"))) {
    if (obj.tweet_results?.result?.rest_id === "2019881223666233717") orig = obj.tweet_results.result;
  }
  const retweet = {
    __typename: "Tweet",
    rest_id: "2100000000000000001",
    core: { user_results: { result: { __typename: "User", rest_id: "1000000000000000001", core: { screen_name: "example_user_1" } } } },
    legacy: {
      full_text: "RT @XDevelopers: Officially launching X API Pay…",
      retweeted_status_result: { result: { __typename: "TweetWithVisibilityResults", tweet: orig } },
    },
  };
  const body = {
    entries: [
      { entryId: "tweet-1", content: { itemContent: { tweet_results: {} } } },
      { entryId: "tweet-2", content: { itemContent: { tweet_results: { result: retweet } } } },
      { entryId: "tweet-3", content: { itemContent: { tweet_results: { result: { __typename: "TweetWithVisibilityResults", tweet: orig } } } } },
      { entryId: "cursor-bottom-1", content: { cursorType: "Bottom", value: "x" } },
    ],
  };
  const [rt, plain] = extractTweets(body);
  assert.equal(extractTweets(body).length, 2);
  assert.equal(rt.author, "example_user_1");
  assert.equal(rt.retweetOf, "XDevelopers");
  assert.equal(rt.text, `RT @XDevelopers: ${plain.text}`);
  assert.equal(plain.id, "2019881223666233717");
  assert.equal(plain.author, "XDevelopers");
  assert.equal(plain.retweetOf, "");
});
