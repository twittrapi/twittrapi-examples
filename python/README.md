# Twitter/X API examples in Python

Python scripts that use the official [`twittrapi`](https://pypi.org/project/twittrapi/) package (Python 3.9+).

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

```bash
pip install twittrapi                     # gspread too for tweets-to-google-sheets; flask for tweet-alerts-to-telegram-discord
export TWITTRAPI_API_KEY=your_key         # or: export RAPIDAPI_KEY=your_rapidapi_key
python export-twitter-followers-to-csv/export_followers.py jack followers.csv
```

Each folder has its own README and `requirements.txt`. [`_shared/extract.py`](_shared/extract.py) holds the small parser that turns X's raw JSON into flat users and tweets; the scripts import it with a relative path, so keep the folder layout when you copy an example (or copy `extract.py` next to the script).

More examples in other languages: [README](../README.md)
