#!/usr/bin/env bash
# Search Twitter/X with curl and print matching tweets (or save them as JSON Lines).
#
#   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
#   ./search.sh "openai lang:en -filter:replies"
#   ./search.sh "from:nasa" Top > nasa.jsonl     # category: Top | Latest (default) | Photos | Videos
#
# Output: one JSON object per tweet (pipe through `jq -r .text` for just the text). One request.
set -euo pipefail
source "$(dirname "$0")/../_shared/twittrapi.sh"

query="${1:?usage: $0 \"<search query>\" [Top|Latest|Photos|Videos]}"
category="${2:-Latest}"

twittrapi_get /search \
  --data-urlencode "searchItem=${query}" \
  --data-urlencode "category=${category}" \
  --data-urlencode "count=20" |
  jq -c "$JQ_TWEETS"
