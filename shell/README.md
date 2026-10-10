# Twitter/X API examples with curl

Bash scripts that call the API with `curl` and parse the result with `jq`. No SDK needed.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

```bash
export TWITTRAPI_API_KEY=your_key         # or: export RAPIDAPI_KEY=your_rapidapi_key
./shell/search-tweets-with-curl/search.sh "openai lang:en"
```

[`_shared/twittrapi.sh`](_shared/twittrapi.sh) holds the request function (direct key or RapidAPI key) and the `jq` filters for X's raw JSON.

More examples in other languages: [README](../README.md)
