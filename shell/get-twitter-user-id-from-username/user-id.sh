#!/usr/bin/env bash
# Get the numeric Twitter/X user ID for one or more usernames, with curl and jq.
#
#   export TWITTRAPI_API_KEY=...      # or RAPIDAPI_KEY=...
#   ./user-id.sh jack nasa @github
#
# Prints "username<TAB>id" per line. One request per username.
set -euo pipefail
source "$(dirname "$0")/../_shared/twittrapi.sh"

if [ $# -eq 0 ]; then
  echo "usage: $0 <username> [username...]" >&2
  exit 2
fi

for name in "$@"; do
  name="${name#@}"
  if body=$(twittrapi_get "/username/to/id/${name}"); then
    id=$(jq -r "$JQ_USER_ID" <<<"$body")
    printf '%s\t%s\n' "$name" "${id:-not found}"
  else
    printf '%s\t%s\n' "$name" "error" >&2
  fi
done
