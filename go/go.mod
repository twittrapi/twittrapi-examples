module github.com/twittrapi/examples/go

go 1.21

// go.sum is added by running `go mod tidy` here once twittrapi-go v0.1.0 is tagged.
// For local development against an unpublished SDK checkout, tools/setup-local-sdks.sh
// writes a gitignored go.work instead of a replace directive.
require github.com/twittrapi/twittrapi-go v0.1.0
