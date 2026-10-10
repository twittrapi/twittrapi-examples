// Command get-replies-to-a-tweet prints a tweet and its replies, and can save them as JSON.
//
//	export TWITTRAPI_API_KEY=...   # or RAPIDAPI_KEY=...
//	go run ./get-replies-to-a-tweet https://x.com/jack/status/20
//	go run ./get-replies-to-a-tweet -sort Likes -pages 3 -o replies.json 20
//
// -sort is Relevance (default), Recency or Likes. Each page is one request.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"

	twittrapi "github.com/twittrapi/twittrapi-go"

	"github.com/twittrapi/examples/go/internal/extract"
)

var idPattern = regexp.MustCompile(`\d+`)

func main() {
	sortMode := flag.String("sort", "Relevance", "Relevance, Recency or Likes")
	pages := flag.Int("pages", 1, "pages of replies to fetch")
	out := flag.String("o", "", "write replies to this JSON file")
	flag.Parse()

	// Accept a bare ID or a tweet URL; the status ID is the last number in the URL.
	ids := idPattern.FindAllString(flag.Arg(0), -1)
	if len(ids) == 0 {
		fmt.Fprintln(os.Stderr, "usage: get-replies-to-a-tweet [-sort Likes] [-pages 2] [-o file.json] <tweet id or URL>")
		os.Exit(2)
	}
	tweetID := ids[len(ids)-1]

	client, err := twittrapi.NewClient()
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	var root *extract.Tweet
	replies := map[string]extract.Tweet{}
	var order []string

	// Tweets.Get returns the tweet plus a page of its conversation. Follow the cursor by hand.
	params := twittrapi.TweetParams{TweetID: tweetID, RankingMode: twittrapi.RankingMode(*sortMode)}
	for page := 0; page < *pages; page++ {
		raw, err := client.Tweets.Get(ctx, params)
		if err != nil {
			log.Fatal(err)
		}
		for _, t := range extract.Tweets(raw) {
			t := t
			switch {
			case t.ID == tweetID:
				root = &t
			case t.ReplyTo == tweetID:
				if _, dup := replies[t.ID]; !dup {
					replies[t.ID] = t
					order = append(order, t.ID)
				}
			}
		}
		next := twittrapi.ExtractBottomCursor(raw)
		if next == "" || next == params.Cursor {
			break
		}
		params.Cursor = next
	}

	if root != nil {
		fmt.Printf("@%s: %s\n%d replies · %d likes\n\n", root.Author, oneLine(root.Text), root.Replies, root.Likes)
	}
	list := make([]extract.Tweet, 0, len(order))
	for _, id := range order {
		t := replies[id]
		list = append(list, t)
		fmt.Printf("  @%s (%d likes): %s\n", t.Author, t.Likes, oneLine(t.Text))
	}
	fmt.Printf("\n%d direct replies fetched\n", len(list))

	if *out != "" {
		b, _ := json.MarshalIndent(list, "", "  ")
		if err := os.WriteFile(*out, b, 0o644); err != nil {
			log.Fatal(err)
		}
		fmt.Println("Saved to", *out)
	}
}

func oneLine(s string) string { return strings.Join(strings.Fields(s), " ") }
