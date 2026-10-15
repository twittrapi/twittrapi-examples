"""python -m unittest test_relay.py: signature check, retries, the webhook route."""
import hashlib
import hmac
import json
import os
import sys
import time
import unittest
from typing import Optional
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay  # noqa: E402

SECRET = b"whsec_test"


def sign(body: bytes, t: Optional[int] = None) -> str:
    t = t or int(time.time())
    return f"t={t},v1=" + hmac.new(SECRET, f"{t}.".encode() + body, hashlib.sha256).hexdigest()


class RelayTest(unittest.TestCase):
    def test_verify(self):
        body = b'{"event":"test"}'
        self.assertTrue(relay.verify(SECRET, sign(body), body))
        self.assertFalse(relay.verify(SECRET, sign(body), body + b" "))
        self.assertFalse(relay.verify(SECRET, sign(body, int(time.time()) - 600), body), "too old")
        self.assertFalse(relay.verify(SECRET, "garbage", body))

    def test_route_forwards_each_delivery_once(self):
        tweet = {"author": {"username": "NASA"}, "text": "Launch day!", "url": "https://x.com/NASA/status/1"}
        body = json.dumps({"event": "tweet", "tweet": tweet}).encode()
        client = relay.app.test_client()
        with mock.patch.dict(os.environ, {"TWITTRAPI_WEBHOOK_SECRET": SECRET.decode()}), mock.patch.object(relay, "forward") as fwd, \
                mock.patch.object(relay.threading, "Thread", side_effect=lambda target, args, daemon: mock.Mock(start=lambda: target(*args))):
            headers = {"X-TwittrAPI-Signature": sign(body), "X-TwittrAPI-Delivery": "1849203", "Content-Type": "application/json"}
            self.assertEqual(client.post("/hooks/twittrapi", data=body, headers=headers).status_code, 204)
            self.assertEqual(client.post("/hooks/twittrapi", data=body, headers=headers).status_code, 204)
            fwd.assert_called_once_with(tweet)
            bad = dict(headers, **{"X-TwittrAPI-Signature": "t=1,v1=00"})
            self.assertEqual(client.post("/hooks/twittrapi", data=body, headers=bad).status_code, 401)

    def test_message(self):
        self.assertEqual(relay.message({"author": {"username": "a"}, "text": "hi", "url": "u"}), "@a: hi\nu")


if __name__ == "__main__":
    unittest.main()
