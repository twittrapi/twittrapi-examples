# Shared helpers for the curl examples. Source it, don't run it.
#
#   twittrapi_get /path [extra curl args...]   -> prints the JSON body, exits non-zero on HTTP errors
#
# Auth: TWITTRAPI_API_KEY (direct API, X-API-KEY header) or RAPIDAPI_KEY (RapidAPI headers).
# RAPIDAPI_HOST sets the RapidAPI listing's host (default twitter-aio.p.rapidapi.com).
# TWITTRAPI_BASE_URL overrides the direct API base URL (e.g. for a local mock server).
#
# The jq filters below read X's raw GraphQL JSON. The response shapes come from X and may change,
# so they search the whole response with `..` instead of following one fixed path.

twittrapi_get() {
  local path="$1"; shift
  local base auth_args host
  if [ -n "${TWITTRAPI_API_KEY:-}" ]; then
    base="${TWITTRAPI_BASE_URL:-https://api.twittrapi.com}"
    auth_args=(-H "X-API-KEY: ${TWITTRAPI_API_KEY}")
  elif [ -n "${RAPIDAPI_KEY:-}" ]; then
    host="${RAPIDAPI_HOST:-twitter-aio.p.rapidapi.com}"
    host="${host#https://}"; host="${host%/}"
    base="https://${host}"
    auth_args=(-H "x-rapidapi-key: ${RAPIDAPI_KEY}" -H "x-rapidapi-host: ${host}")
  else
    echo "Set TWITTRAPI_API_KEY (https://twittrapi.com/start) or RAPIDAPI_KEY first." >&2
    return 1
  fi
  curl --silent --show-error --fail-with-body --get \
    -H "Accept: application/json" "${auth_args[@]}" "$@" "${base%/}${path}"
}

# Every tweet in a response as one compact JSON object per line: id, author, created_at, likes, text.
JQ_TWEETS='
  [ .. | objects | .tweet_results?.result? | objects
    | if .__typename == "TweetWithVisibilityResults" then .tweet else . end
    | select(.legacy? and .rest_id?) ]
  | unique_by(.rest_id) | sort_by([(.rest_id | length), .rest_id]) | reverse | .[]
  | {
      id: .rest_id,
      author: (.core.user_results.result | (.core.screen_name? // .legacy.screen_name? // "")),
      created_at: .legacy.created_at,
      likes: (.legacy.favorite_count // 0),
      text: ((.note_tweet.note_tweet_results.result.text? // .legacy.full_text // "") | gsub("\\s+"; " "))
    }'

# Trend names (and volume when present), one per line.
JQ_TRENDS='
  [ .. | objects | select((.name? | type) == "string" and (has("woeid") | not)
                          and (has("tweet_volume") or has("query") or has("url"))) ]
  | reduce .[] as $t ([]; if any(.[]; .name == $t.name) then . else . + [$t] end) | .[]
  | "\(.name)\t\(.tweet_volume // "")"'

# Numeric user ID from a username-to-ID or profile response.
JQ_USER_ID='
  [ .. | objects | (.rest_id?, .id_str?, .user_id?, (.id? | select(type == "string")))
    | strings | select(test("^[0-9]+$")) ] | first // empty'

# Trend locations: "woeid<TAB>name<TAB>country code", one per line.
JQ_LOCATIONS='
  [ .. | objects | select(has("woeid") and (.name? | type) == "string") ][]
  | "\(.woeid)\t\(.name)\t\(.countryCode // "")"'
