# Real-time tweet alerts to Telegram, Discord or Slack (Python)

Get a message in Telegram, Discord or Slack within seconds of an X account posting. TwittrAPI account monitoring sends every new tweet of the accounts you watch to your webhook; this small relay checks the signature and forwards the tweet.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · Monitoring has a free plan for one account; paid plans watch more accounts, up to every second.

## Run it

```bash
cd python/tweet-alerts-to-telegram-discord
pip install -r requirements.txt
export TWITTRAPI_WEBHOOK_SECRET=whsec_...        # returned by PUT /monitors/webhook
export TELEGRAM_BOT_TOKEN=123456:abc TELEGRAM_CHAT_ID=-1001234567890
# or: export DISCORD_WEBHOOK_URL=...   or: export SLACK_WEBHOOK_URL=...
python relay.py                                   # listens on :8080, path /hooks/twittrapi
```

The relay must be reachable over **https** from the internet (a small VPS, Fly.io, Railway or a tunnel such as Cloudflare Tunnel).

## Connect it to TwittrAPI

In the dashboard under **Monitors**: book a plan (or start the free one), add the accounts, set the webhook to `https://your-relay.example.com/hooks/twittrapi` and click **Send test event**. Or with the API:

```bash
curl -X POST https://api.twittrapi.com/monitors/accounts -H "X-API-KEY: $TWITTRAPI_API_KEY" \
  -H "Content-Type: application/json" -d '{"usernames": ["NASA"]}'
curl -X PUT https://api.twittrapi.com/monitors/webhook -H "X-API-KEY: $TWITTRAPI_API_KEY" \
  -H "Content-Type: application/json" -d '{"url": "https://your-relay.example.com/hooks/twittrapi"}'
curl -X POST https://api.twittrapi.com/monitors/webhook/test -H "X-API-KEY: $TWITTRAPI_API_KEY"
```

## Sample message

```text
@NASA: Launch day! Coverage starts at 10am ET.
https://x.com/NASA/status/1976400000000000001
```

_Output values are illustrative._

## Notes

- The signature header is `X-TwittrAPI-Signature: t=<unix seconds>,v1=<HMAC-SHA256 of "<t>.<raw body>">`; the relay rejects other bodies and timestamps older than 5 minutes.
- TwittrAPI retries failed deliveries for up to 24 hours with the same `X-TwittrAPI-Delivery` ID; the relay forwards each ID once.
- Answer within 5 seconds: the forwarding runs in a background thread.
- To filter, check `tweet["replyTo"]`, `tweet["retweetOf"]` or the text before forwarding.
- Tests: `python -m unittest test_relay.py`.

Guides: [Account monitoring docs](https://www.twittrapi.com/docs/monitoring) · [Tweet alerts in Discord, Telegram or Slack](https://www.twittrapi.com/blog/tweet-alerts-discord-telegram-slack)

More examples: [TwittrAPI examples](../../README.md) · Not affiliated with X Corp.
