# Twitter followers count tracker in Python

Track how follower counts change over time. Each run looks up the accounts you list, appends one row per account to a CSV history file and prints the change since the last run. Schedule it with cron or GitHub Actions to build a daily follower chart.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd python/twitter-followers-count-tracker
pip install -r requirements.txt
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
python track_followers.py nasa spacex esa --csv follower_history.csv

# daily at 08:00 with cron:
# 0 8 * * * cd /path/to/twitter-followers-count-tracker && python track_followers.py nasa spacex esa
```

## Sample output

```text
@NASA: 89,012,455 followers (+12,310)
@SpaceX: 41,220,901 followers (+8,774)
@esa: 6,804,112 followers (+1,020)

$ tail -3 follower_history.csv
2026-10-10T08:00:02Z,NASA,11348282,89012455,180,72310
2026-10-10T08:00:02Z,SpaceX,34743251,41220901,120,9120
2026-10-10T08:00:03Z,esa,15193981,6804112,410,24410
```

_Output values are illustrative._

## Notes

One request per account per run (`client.users.get_by_username`).

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
