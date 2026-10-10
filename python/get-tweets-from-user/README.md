# Get tweets from a Twitter user with Python

Fetch the most recent tweets from any public Twitter/X account in a few lines of Python. The script prints each tweet with its date, likes, retweets and link, and can include replies with `--replies`.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd python/get-tweets-from-user
pip install -r requirements.txt
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
python get_user_tweets.py nasa --limit 3
```

## Sample output

```text
Fri Oct 09 18:42:00 +0000 2026  likes=1840  rts=312
  @NASA: Our latest image shows a star-forming region 7,500 light-years away.
  https://x.com/NASA/status/1976500000000000002

Fri Oct 09 15:10:00 +0000 2026  likes=2210  rts=401
  @NASA: Launch day! Coverage starts at 10am ET.
  https://x.com/NASA/status/1976400000000000001
...
```

_Output values are illustrative._

## Notes

The core call is `client.users.tweets(username="nasa", count=20)`. Pass `user_id=` instead of `username=` if you already have the ID; it is slightly faster.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
