// Command get-trending-topics-by-country prints the current Twitter/X trends for a country.
//
//	export TWITTRAPI_API_KEY=...   # or RAPIDAPI_KEY=...
//	go run ./get-trending-topics-by-country DE
//	go run ./get-trending-topics-by-country "United Kingdom"
//	go run ./get-trending-topics-by-country world
//	go run ./get-trending-topics-by-country -list      # every location with trends
//
// The argument is a two-letter country code, a country or city name, or "world".
// Two requests: one to look up the WOEID, one for the trends.
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	twittrapi "github.com/twittrapi/twittrapi-go"

	"github.com/twittrapi/examples/go/internal/extract"
)

func main() {
	list := flag.Bool("list", false, "print every location that has trends")
	limit := flag.Int("n", 20, "how many trends to print")
	flag.Parse()
	place := strings.TrimSpace(strings.Join(flag.Args(), " "))
	if place == "" {
		place = "US"
	}

	client, err := twittrapi.NewClient() // reads TWITTRAPI_API_KEY or RAPIDAPI_KEY
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	woeid, label := int64(twittrapi.WOEIDWorldwide), "Worldwide"
	if *list || !strings.EqualFold(place, "world") {
		raw, err := client.Trends.Locations(ctx)
		if err != nil {
			log.Fatal(err)
		}
		locations := extract.Locations(raw)
		if *list {
			for _, l := range locations {
				fmt.Printf("%10d  %-25s %-8s %s\n", l.WOEID, l.Name, l.CountryCode, l.Type)
			}
			return
		}
		loc, ok := findLocation(locations, place)
		if !ok {
			fmt.Fprintf(os.Stderr, "No trend location matches %q. Try -list.\n", place)
			os.Exit(1)
		}
		woeid, label = loc.WOEID, loc.Name
	}

	raw, err := client.Trends.Get(ctx, woeid)
	if err != nil {
		log.Fatal(err)
	}
	trends := extract.Trends(raw)
	if len(trends) == 0 {
		fmt.Println(string(raw)) // unknown shape: show the raw JSON
		return
	}
	fmt.Printf("Trending in %s (WOEID %d)\n", label, woeid)
	for i, t := range trends {
		if i == *limit {
			break
		}
		volume := ""
		if t.Volume > 0 {
			volume = fmt.Sprintf("  (%d posts)", t.Volume)
		}
		fmt.Printf("%3d. %s%s\n", i+1, t.Name, volume)
	}
}

// findLocation matches a country code (country-level entry) or a place name.
func findLocation(locations []extract.Location, place string) (extract.Location, bool) {
	if len(place) == 2 {
		for _, l := range locations {
			if strings.EqualFold(l.CountryCode, place) && l.Type == "Country" {
				return l, true
			}
		}
	}
	for _, l := range locations {
		if strings.EqualFold(l.Name, place) {
			return l, true
		}
	}
	return extract.Location{}, false
}
