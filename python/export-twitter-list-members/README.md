# Export Twitter list members to CSV with Python

Export all members of a public Twitter/X list to a CSV file with ID, username, name, follower counts and bio. Pass the list ID or the full list URL.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

## Run it

```bash
cd python/export-twitter-list-members
pip install -r requirements.txt
export TWITTRAPI_API_KEY=your_key      # or: export RAPIDAPI_KEY=your_rapidapi_key
python export_list_members.py https://x.com/i/lists/84839422 members.csv
```

## Sample output

```text
Wrote 214 members of list 84839422 to members.csv

$ head -2 members.csv
id,username,name,followers,following,tweets,verified,bio
783214,X,X,68000000,5,15000,True,what's happening?!
```

_Output values are illustrative._

## Notes

The core call is `client.lists.members(list_id, count=100)`, paged with `client.paginate`.

Responses are X's raw JSON; the small parser in [`../_shared`](../_shared) reads the fields used here. X changes its response shapes from time to time, so check a real response before relying on a field.

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
