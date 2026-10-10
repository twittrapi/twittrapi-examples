#!/usr/bin/env bash
# Get Twitter/X trending topics with curl, by WOEID (1 = worldwide, 23424977 = United States).
#
#   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
#   ./trends.sh                 # worldwide
#   ./trends.sh 23424829        # Germany
#   ./trends.sh --locations     # list every location and its WOEID
#
# Prints "name<TAB>volume" per trend. One request.
set -euo pipefail
source "$(dirname "$0")/../_shared/twittrapi.sh"

if [ "${1:-}" = "--locations" ]; then
  twittrapi_get /misc/locations | jq -r "$JQ_LOCATIONS"
  exit 0
fi

woeid="${1:-1}"
case "$woeid" in *[!0-9]*) echo "WOEID must be a number (try --locations)" >&2; exit 2 ;; esac
twittrapi_get "/trends/${woeid}" | jq -r "$JQ_TRENDS"
