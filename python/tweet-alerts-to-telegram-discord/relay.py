"""Forward new tweets from TwittrAPI account monitoring to Discord, Telegram or Slack.

TwittrAPI POSTs every new tweet of the accounts you watch to your webhook, signed with
HMAC-SHA256. This relay checks the signature, answers within the 5-second limit and sends the
tweet on in a background thread.

    export TWITTRAPI_WEBHOOK_SECRET=whsec_...       # from PUT /monitors/webhook
    export DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...   # any of the three
    export TELEGRAM_BOT_TOKEN=123:abc TELEGRAM_CHAT_ID=-100123
    export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
    python relay.py                                  # listens on :8080, path /hooks/twittrapi

Docs: https://www.twittrapi.com/docs/monitoring
"""
import hashlib
import hmac
import os
import threading
import time
from collections import OrderedDict

import requests
from flask import Flask, abort, request

app = Flask(__name__)
_seen: "OrderedDict[str, None]" = OrderedDict()  # recent delivery IDs (retries reuse them)


def verify(secret: bytes, header: str, raw_body: bytes, tolerance: int = 300) -> bool:
    """X-TwittrAPI-Signature is "t=<unix seconds>,v1=<hex HMAC-SHA256 of '<t>.<raw body>'>"."""
    parts = dict(p.strip().split("=", 1) for p in header.split(",") if "=" in p)
    t, sig = parts.get("t", ""), parts.get("v1", "")
    if not t.isdigit() or not sig or abs(time.time() - int(t)) > tolerance:
        return False
    expected = hmac.new(secret, t.encode() + b"." + raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


def first_time(delivery_id: str, keep: int = 1000) -> bool:
    """False for a delivery we already handled (TwittrAPI retries with the same ID)."""
    if not delivery_id:
        return True
    if delivery_id in _seen:
        return False
    _seen[delivery_id] = None
    while len(_seen) > keep:
        _seen.popitem(last=False)
    return True


def message(tweet: dict) -> str:
    return f"@{tweet['author']['username']}: {tweet['text']}\n{tweet['url']}"


def forward(tweet: dict) -> None:
    text = message(tweet)
    if url := os.environ.get("DISCORD_WEBHOOK_URL"):
        requests.post(url, json={"content": text[:2000]}, timeout=10)
    if token := os.environ.get("TELEGRAM_BOT_TOKEN"):
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text[:4096]},
            timeout=10,
        )
    if url := os.environ.get("SLACK_WEBHOOK_URL"):
        requests.post(url, json={"text": text}, timeout=10)


@app.post("/hooks/twittrapi")
def hook():
    secret = os.environ["TWITTRAPI_WEBHOOK_SECRET"].encode()
    if not verify(secret, request.headers.get("X-TwittrAPI-Signature", ""), request.get_data()):
        abort(401)
    event = request.get_json()
    # "test" events (POST /monitors/webhook/test) only check that this endpoint answers
    if event.get("event") == "tweet" and first_time(request.headers.get("X-TwittrAPI-Delivery", "")):
        threading.Thread(target=forward, args=(event["tweet"],), daemon=True).start()
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
