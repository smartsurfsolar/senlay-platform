import hashlib
import hmac
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from senlay_client import SenlayClient, SenlayError, observation, sign_payload


STATION_ID = "stn_0123456789abcdef0123456789abcdef"


class Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.body).encode()


class SenlayClientTests(unittest.TestCase):
    def test_signature_matches_protocol(self):
        timestamp, signature = sign_payload('{"value":7}', "test-secret", 1770000000)
        key = hashlib.sha256(b"test-secret").hexdigest().encode("ascii")
        expected = hmac.new(key, b'1770000000.{"value":7}', hashlib.sha256).hexdigest()
        self.assertEqual(timestamp, "1770000000")
        self.assertEqual(signature, f"sha256={expected}")

    def test_prepare_signs_exact_body(self):
        payload = observation(STATION_ID, 15.8801, 108.338, [
            {"phenomenon": "wind.speed", "value": 7.4, "unit": "m/s", "quality": "raw"}
        ], observation_id="python-test-0001", observed_at="2026-09-05T10:00:00.000Z")
        client = SenlayClient(STATION_ID, "test-secret")
        body, headers = client.prepare(payload)
        self.assertEqual(json.loads(body), payload)
        self.assertEqual(headers["X-Senlay-Station-Id"], STATION_ID)
        self.assertTrue(headers["X-Senlay-Signature"].startswith("sha256="))

    @mock.patch("urllib.request.urlopen")
    def test_publish_uses_signed_post(self, urlopen):
        urlopen.return_value = Response({"accepted": True, "duplicate": False})
        payload = observation(STATION_ID, 1, 2, [
            {"phenomenon": "weather.temperature", "value": 24.5, "unit": "C", "quality": "checked"}
        ])
        result = SenlayClient(STATION_ID, "test-secret").publish(payload)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("X-senlay-station-id"), STATION_ID)
        self.assertTrue(result["accepted"])

    def test_rejects_non_production_station_id(self):
        with self.assertRaises(SenlayError):
            observation("example-station", 1, 2, [{"phenomenon": "wind.speed", "value": 2, "unit": "m/s"}])


if __name__ == "__main__":
    unittest.main()
