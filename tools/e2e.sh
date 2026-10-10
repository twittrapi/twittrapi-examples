#!/usr/bin/env bash
# Runs examples end to end against the local mock server (tools/mock_server.py), offline.
# Run tools/setup-local-sdks.sh first. Uses a fake key; nothing leaves 127.0.0.1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8787}"
OUT="$(mktemp -d)"
trap 'kill $MOCK_PID 2>/dev/null; wait $MOCK_PID 2>/dev/null || true; rm -rf "$OUT"' EXIT

"$ROOT/.venv/bin/python" "$ROOT/tools/mock_server.py" --port "$PORT" 2>"$OUT/mock.log" &
MOCK_PID=$!
for _ in $(seq 1 50); do curl -s "http://127.0.0.1:$PORT/" >/dev/null 2>&1 && break; sleep 0.1; done

export TWITTRAPI_API_KEY=test-key TWITTRAPI_BASE_URL="http://127.0.0.1:$PORT"
unset RAPIDAPI_KEY
PY="$ROOT/.venv/bin/python -W ignore"
pass=0
run() { echo; echo "\$ $*"; "$@"; pass=$((pass + 1)); }
expect() { grep -q "$1" "$2" || { echo "FAIL: expected '$1' in $2"; cat "$2"; exit 1; }; }

cd "$OUT"
echo "== Python"
run $PY "$ROOT/python/export-twitter-followers-to-csv/export_followers.py" jack followers.csv
expect "user_7" followers.csv; head -3 followers.csv
run $PY "$ROOT/python/get-tweets-from-user/get_user_tweets.py" jack --limit 3
run $PY "$ROOT/python/download-tweets-to-json/download_tweets.py" --search "python" -o tweets.json
expect '"author": "user_0"' tweets.json
run $PY "$ROOT/python/twitter-followers-count-tracker/track_followers.py" jack nasa --csv history.csv
run $PY "$ROOT/python/twitter-followers-count-tracker/track_followers.py" jack nasa --csv history.csv
expect "NASA" history.csv
run $PY "$ROOT/python/export-twitter-list-members/export_list_members.py" https://x.com/i/lists/84839422 members.csv
expect "user_9" members.csv

echo; echo "== Node"
cd "$ROOT/node"
run node twitter-user-lookup-by-username/lookup.mjs jack @nasa
run node scrape-twitter-search-results/scrape-search.mjs "node.js" --pages 3 --out "$OUT/search.csv"
expect "mock result 7" "$OUT/search.csv"
run node find-tweets-mentioning-a-brand/brand-mentions.mjs --name "Acme" --handle acme --since 2026-10-01
rm -f monitor-twitter-keyword-and-send-to-slack/.seen-*.json
SLACK_WEBHOOK_URL="http://127.0.0.1:$PORT/slack-webhook" run node monitor-twitter-keyword-and-send-to-slack/monitor.mjs "acme" --once --backfill
rm -f monitor-twitter-keyword-and-send-to-slack/.seen-*.json
expect "\[slack\]" "$OUT/mock.log"
echo "(mock Slack received $(grep -c '\[slack\]' "$OUT/mock.log") messages, first one:)"; grep -m1 '\[slack\]' "$OUT/mock.log"
run node export-twitter-community-tweets/export-community.mjs --search "javascript"
run node export-twitter-community-tweets/export-community.mjs 1500000000000000000 --out "$OUT/community.jsonl"
expect "Community post 5" "$OUT/community.jsonl"

echo; echo "== Go"
cd "$ROOT/go"
run go run ./get-trending-topics-by-country DE
run go run ./get-trending-topics-by-country -list
run go run ./get-replies-to-a-tweet -pages 2 -o "$OUT/replies.json" https://x.com/jack/status/20
expect "Reply 7" "$OUT/replies.json"
run go run ./export-tweet-retweeters-to-csv -o "$OUT/retweeters.csv" 20
expect "user_9" "$OUT/retweeters.csv"
run go run ./track-competitor-tweets -state "$OUT/state.json" acme rival
# Pretend the last run saw an older tweet, so the next run reports new ones.
sed -i.bak 's/"acme": "[0-9]*"/"acme": "1900000000000424201"/' "$OUT/state.json"
run go run ./track-competitor-tweets -state "$OUT/state.json" acme rival

echo; echo "== Shell"
run "$ROOT/shell/get-twitter-user-id-from-username/user-id.sh" jack nasa
run "$ROOT/shell/search-tweets-with-curl/search.sh" "curl"
run "$ROOT/shell/get-twitter-trends-with-curl/trends.sh" 23424829

echo; echo "E2E: $pass example runs passed against the mock server."
