// Command export-tweet-retweeters-to-csv saves the accounts that retweeted a tweet to CSV.
//
//	export TWITTRAPI_API_KEY=...   # or RAPIDAPI_KEY=...
//	go run ./export-tweet-retweeters-to-csv -o retweeters.csv https://x.com/jack/status/20
//	go run ./export-tweet-retweeters-to-csv -quotes -o quotes.csv 20   # quote tweets instead
//
// Each page is one request (up to 100 accounts with -count 100).
package main

import (
	"context"
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"regexp"
	"strconv"

	twittrapi "github.com/twittrapi/twittrapi-go"

	"github.com/twittrapi/examples/go/internal/extract"
)

func main() {
	out := flag.String("o", "retweeters.csv", "CSV file to write")
	maxPages := flag.Int("pages", 5, "maximum pages to fetch")
	count := flag.Int("count", 100, "accounts per page, max 100")
	quotes := flag.Bool("quotes", false, "export quote tweets instead of retweeters")
	flag.Parse()

	ids := regexp.MustCompile(`\d+`).FindAllString(flag.Arg(0), -1)
	if len(ids) == 0 {
		fmt.Fprintln(os.Stderr, "usage: export-tweet-retweeters-to-csv [-o file.csv] [-pages 5] [-quotes] <tweet id or URL>")
		os.Exit(2)
	}
	params := twittrapi.TweetPageParams{TweetID: ids[len(ids)-1], Count: *count}

	client, err := twittrapi.NewClient()
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	f, err := os.Create(*out)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()

	method := client.Tweets.Retweeters
	header := []string{"id", "username", "name", "followers", "following", "verified", "bio"}
	if *quotes {
		method = client.Tweets.Quotes
		header = []string{"id", "author", "created_at", "likes", "retweets", "text", "url"}
	}
	_ = w.Write(header)

	seen := map[string]bool{}
	it := twittrapi.Paginate(ctx, method, params, &twittrapi.PaginateOptions{MaxPages: *maxPages})
	for it.Next() {
		page := it.Page()
		if *quotes {
			for _, t := range extract.Tweets(page.Data) {
				if t.ID == params.TweetID || seen[t.ID] {
					continue
				}
				seen[t.ID] = true
				_ = w.Write([]string{t.ID, t.Author, t.CreatedAt, itoa(t.Likes), itoa(t.Retweets), t.Text, t.URL()})
			}
			continue
		}
		for _, u := range extract.Users(page.Data) {
			if seen[u.ID] {
				continue
			}
			seen[u.ID] = true
			_ = w.Write([]string{u.ID, u.Username, u.Name, itoa(u.Followers), itoa(u.Following), strconv.FormatBool(u.Verified), u.Bio})
		}
	}
	if err := it.Err(); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Wrote %d rows to %s\n", len(seen), *out)
}

func itoa(n int64) string { return strconv.FormatInt(n, 10) }
