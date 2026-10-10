// Command track-competitor-tweets checks several Twitter/X accounts and reports tweets that
// are new since the last run, with engagement numbers.
//
//	export TWITTRAPI_API_KEY=...   # or RAPIDAPI_KEY=...
//	go run ./track-competitor-tweets -state competitors.json linear notionhq figma
//
// Run it on a schedule (cron, GitHub Actions). The first run records the current tweets
// without reporting them. One request per account per run.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	twittrapi "github.com/twittrapi/twittrapi-go"

	"github.com/twittrapi/examples/go/internal/extract"
)

// state maps a lowercase username to the newest tweet ID seen for it.
type state map[string]string

func load(path string) state {
	s := state{}
	if b, err := os.ReadFile(path); err == nil {
		_ = json.Unmarshal(b, &s)
	}
	return s
}

// newer reports whether tweet ID a is newer than b (IDs are numeric strings that grow).
func newer(a, b string) bool {
	if len(a) != len(b) {
		return len(a) > len(b)
	}
	return a > b
}

func main() {
	statePath := flag.String("state", "competitors.json", "file that remembers the last seen tweet per account")
	jsonOut := flag.Bool("json", false, "print new tweets as JSON lines")
	flag.Parse()
	if flag.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "usage: track-competitor-tweets [-state file] [-json] username [username...]")
		os.Exit(2)
	}

	client, err := twittrapi.NewClient()
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()
	seen := load(*statePath)
	total := 0

	for _, arg := range flag.Args() {
		name := strings.ToLower(strings.TrimPrefix(arg, "@"))
		raw, err := client.Users.Tweets(ctx, twittrapi.UserTimelineParams{Username: name, Count: 20})
		var notFound *twittrapi.NotFoundError
		if errors.As(err, &notFound) {
			fmt.Fprintf(os.Stderr, "@%s: not found\n", name)
			continue
		} else if err != nil {
			log.Fatalf("@%s: %v", name, err)
		}

		last, known := seen[name]
		newest := last
		var fresh []extract.Tweet
		for _, t := range extract.Tweets(raw) {
			// Skip retweets and tweets by other accounts; keep the account's own tweets.
			if t.RetweetOf != "" || (t.Author != "" && !strings.EqualFold(t.Author, name)) {
				continue
			}
			if newer(t.ID, newest) {
				newest = t.ID
			}
			if known && newer(t.ID, last) {
				fresh = append(fresh, t)
			}
		}
		seen[name] = newest

		if !known {
			fmt.Printf("@%s: now tracking (latest tweet %s)\n", name, newest)
			continue
		}
		for i := len(fresh) - 1; i >= 0; i-- { // oldest first
			t := fresh[i]
			total++
			if *jsonOut {
				b, _ := json.Marshal(t)
				fmt.Println(string(b))
				continue
			}
			fmt.Printf("@%s  %s\n  %s\n  %d likes · %d reposts · %d replies · %d views\n  %s\n\n",
				name, t.CreatedAt, strings.Join(strings.Fields(t.Text), " "), t.Likes, t.Retweets, t.Replies, t.Views, t.URL())
		}
	}

	b, _ := json.MarshalIndent(seen, "", "  ")
	if err := os.WriteFile(*statePath, b, 0o644); err != nil {
		log.Fatal(err)
	}
	if !*jsonOut {
		fmt.Printf("%d new tweet(s) across %d account(s)\n", total, flag.NArg())
	}
}
