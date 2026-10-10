// Package extract has small, defensive helpers for reading X's raw GraphQL JSON.
//
// TwittrAPI returns X's responses unchanged. The response shapes come from X, are not
// documented and may change at any time, so these helpers walk the whole response looking for
// the objects they need instead of following one fixed path. If a field moves you get a zero
// value, not a panic. Check a real response before relying on a field.
package extract

import (
	"encoding/json"
	"sort"
	"strconv"
)

// User is a flattened user profile.
type User struct {
	ID        string `json:"id"`
	Username  string `json:"username"`
	Name      string `json:"name"`
	Followers int64  `json:"followers"`
	Following int64  `json:"following"`
	Verified  bool   `json:"verified"`
	Bio       string `json:"bio"`
}

// Tweet is a flattened tweet.
type Tweet struct {
	ID        string `json:"id"`
	CreatedAt string `json:"createdAt"`
	Author    string `json:"author"`
	Text      string `json:"text"`
	Likes     int64  `json:"likes"`
	Retweets  int64  `json:"retweets"`
	Replies   int64  `json:"replies"`
	Views     int64  `json:"views"`
	ReplyTo   string `json:"replyTo,omitempty"`   // ID of the tweet this one replies to
	RetweetOf string `json:"retweetOf,omitempty"` // for a retweet: username of the original author
}

// URL is the tweet's link on x.com.
func (t Tweet) URL() string {
	user := t.Author
	if user == "" {
		user = "i"
	}
	return "https://x.com/" + user + "/status/" + t.ID
}

// Trend is one trending topic. Volume is 0 when X does not report it.
type Trend struct {
	Name   string `json:"name"`
	Volume int64  `json:"volume"`
}

// Location is a place that has trends.
type Location struct {
	WOEID       int64  `json:"woeid"`
	Name        string `json:"name"`
	Country     string `json:"country"`
	CountryCode string `json:"countryCode"`
	Type        string `json:"type"` // "Country", "Town", "Supername", ...
}

// walk calls fn for every JSON object in v. Object keys are visited in random order.
func walk(v any, fn func(map[string]any)) {
	switch t := v.(type) {
	case map[string]any:
		fn(t)
		for _, child := range t {
			walk(child, fn)
		}
	case []any:
		for _, child := range t {
			walk(child, fn)
		}
	}
}

func decode(raw []byte) any {
	var v any
	_ = json.Unmarshal(raw, &v) // on error v stays nil and the helpers return nothing
	return v
}

func obj(m map[string]any, keys ...string) map[string]any {
	for _, k := range keys {
		next, ok := m[k].(map[string]any)
		if !ok {
			return map[string]any{}
		}
		m = next
	}
	return m
}

func str(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}

func num(m map[string]any, key string) int64 {
	switch v := m[key].(type) {
	case float64:
		return int64(v)
	case string:
		n, _ := strconv.ParseInt(v, 10, 64)
		return n
	}
	return 0
}

func first(values ...string) string {
	for _, v := range values {
		if v != "" {
			return v
		}
	}
	return ""
}

func flatUser(u map[string]any) User {
	legacy, core := obj(u, "legacy"), obj(u, "core") // X moved screen_name/name to core in 2025
	verified, _ := u["is_blue_verified"].(bool)
	return User{
		ID:        str(u, "rest_id"),
		Username:  first(str(core, "screen_name"), str(legacy, "screen_name")),
		Name:      first(str(core, "name"), str(legacy, "name")),
		Followers: num(legacy, "followers_count"),
		Following: num(legacy, "friends_count"),
		Verified:  verified,
		Bio:       first(str(legacy, "description"), str(obj(u, "profile_bio"), "description")),
	}
}

// Users returns the users in a response (user_results.result in timelines, plus plain
// {"result": {"__typename": "User"}} items as in users-by-IDs and community members),
// de-duplicated by ID and sorted by follower count, highest first (Go map order is random, so
// this keeps output stable).
func Users(raw []byte) []User {
	seen := map[string]bool{}
	var out []User
	walk(decode(raw), func(m map[string]any) {
		u := obj(m, "user_results", "result")
		if r := obj(m, "result"); str(u, "rest_id") == "" && str(r, "__typename") == "User" {
			u = r
		}
		id := str(u, "rest_id")
		if id == "" || seen[id] {
			return
		}
		seen[id] = true
		out = append(out, flatUser(u))
	})
	sort.SliceStable(out, func(i, j int) bool { return out[i].Followers > out[j].Followers })
	return out
}

// unwrapTweet returns the tweet inside a TweetWithVisibilityResults wrapper, or t itself.
func unwrapTweet(t map[string]any) map[string]any {
	if str(t, "__typename") == "TweetWithVisibilityResults" {
		return obj(t, "tweet")
	}
	return t
}

// tweetText is the long-form note_tweet text when present, else legacy.full_text.
func tweetText(t map[string]any) string {
	return first(str(obj(t, "note_tweet", "note_tweet_results", "result"), "text"), str(obj(t, "legacy"), "full_text"))
}

// screenName is the tweet author's handle (core.screen_name since 2025, legacy before).
func screenName(t map[string]any) string {
	author := obj(t, "core", "user_results", "result")
	return first(str(obj(author, "core"), "screen_name"), str(obj(author, "legacy"), "screen_name"))
}

// Tweets returns the tweets (tweet_results.result) in a response, de-duplicated by ID,
// newest first.
func Tweets(raw []byte) []Tweet {
	seen := map[string]bool{}
	var out []Tweet
	walk(decode(raw), func(m map[string]any) {
		t := unwrapTweet(obj(m, "tweet_results", "result")) // {} for deleted tweets: skipped
		legacy, ok := t["legacy"].(map[string]any)
		id := str(t, "rest_id")
		if !ok || id == "" || seen[id] {
			return
		}
		seen[id] = true
		text := tweetText(t)
		retweetOf := ""
		// A retweet's own full_text is "RT @user: " plus a truncated copy; use the original.
		if orig := unwrapTweet(obj(legacy, "retweeted_status_result", "result")); orig["legacy"] != nil {
			retweetOf = screenName(orig)
			text = "RT @" + retweetOf + ": " + tweetText(orig)
		}
		out = append(out, Tweet{
			ID:        id,
			CreatedAt: str(legacy, "created_at"),
			Author:    screenName(t),
			Text:      text,
			Likes:     num(legacy, "favorite_count"),
			Retweets:  num(legacy, "retweet_count"),
			Replies:   num(legacy, "reply_count"),
			Views:     num(obj(t, "views"), "count"),
			ReplyTo:   str(legacy, "in_reply_to_status_id_str"),
			RetweetOf: retweetOf,
		})
	})
	// Tweet IDs grow over time, so sorting by ID sorts by time.
	sort.Slice(out, func(i, j int) bool {
		a, b := out[i].ID, out[j].ID
		if len(a) != len(b) {
			return len(a) > len(b)
		}
		return a > b
	})
	return out
}

// Trends returns objects that look like trends ({"name", "tweet_volume" | "query" | "url"}).
func Trends(raw []byte) []Trend {
	seen := map[string]bool{}
	var out []Trend
	walk(decode(raw), func(m map[string]any) {
		name := str(m, "name")
		_, hasWOEID := m["woeid"]
		_, hasVolume := m["tweet_volume"]
		_, hasQuery := m["query"]
		if name == "" || hasWOEID || seen[name] || !(hasVolume || hasQuery || m["url"] != nil) {
			return
		}
		seen[name] = true
		out = append(out, Trend{Name: name, Volume: num(m, "tweet_volume")})
	})
	return out
}

// Locations returns trend locations (objects with "woeid" and "name").
func Locations(raw []byte) []Location {
	var out []Location
	walk(decode(raw), func(m map[string]any) {
		if _, ok := m["woeid"]; !ok || str(m, "name") == "" {
			return
		}
		typ := str(obj(m, "placeType"), "name")
		if typ == "" {
			typ = str(m, "placeType")
		}
		out = append(out, Location{
			WOEID:       num(m, "woeid"),
			Name:        str(m, "name"),
			Country:     str(m, "country"),
			CountryCode: str(m, "countryCode"),
			Type:        typ,
		})
	})
	return out
}
