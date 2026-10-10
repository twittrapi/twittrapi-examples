# Twitter/X API examples in Go

Go programs using the official [`github.com/twittrapi/twittrapi-go`](https://github.com/twittrapi/twittrapi-go) module (Go 1.21+). All examples share one module, so run them from this folder:

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

```bash
cd go
export TWITTRAPI_API_KEY=your_key         # or: export RAPIDAPI_KEY=your_rapidapi_key
go run ./get-trending-topics-by-country DE
```

[`internal/extract`](internal/extract) holds the small parser for X's raw JSON. To use an example in your own project, copy its `main.go` and the `extract` package and run `go get github.com/twittrapi/twittrapi-go`.

More examples in other languages: [README](../README.md)
