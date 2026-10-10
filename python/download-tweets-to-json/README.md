# Download tweets to JSON with Python

Download tweets from an X search query or from a user's timeline and save them as a JSON file. By default each tweet is flattened to `id`, `created_at`, `author`, `text`, `likes`, `retweets`, `replies`, `views` and `url`; pass `--raw` to keep X's original response pages.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd python/download-tweets-to-json
pip install -r requirements.txt
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
python download_tweets.py --search "python lang:en -filter:replies" -o tweets.json
python download_tweets.py --user jack -o jack.json --max-pages 5
```

## Sample output

```text
Saved 58 tweets to tweets.json

$ head -13 tweets.json
[
  {
    "id": "1976512345678901234",
    "created_at": "Fri Oct 09 18:42:00 +0000 2026",
    "author": "example_dev",
    "text": "Finally moved our ETL jobs to Python 3.13 ...",
    "likes": 42,
    "retweets": 6,
    "replies": 3,
    "views": 3120,
    "retweet_of": "",
    "url": "https://x.com/example_dev/status/1976512345678901234"
  },
```

_Output values are illustrative._

## Notes

Search supports X operators such as `from:`, `to:`, `lang:`, `since:`, `until:`, `min_faves:` and `-filter:replies`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
