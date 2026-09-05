"""Dependency-free Python client for the Senlay Open Network."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone


SUPPORTED_UNITS = {"m/s", "km/h", "kt", "deg", "C", "hPa", "%", "mm", "m", "ug/m3"}
SUPPORTED_QUALITY = {"raw", "checked", "estimated"}


class SenlayError(RuntimeError):
    """Raised when a payload is invalid or Senlay rejects a request."""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sign_payload(body, station_secret, timestamp=None):
    if not station_secret:
        raise SenlayError("station secret is required")
    timestamp = int(time.time()) if timestamp is None else int(timestamp)
    derived_key = hashlib.sha256(station_secret.encode("utf-8")).hexdigest().encode("ascii")
    message = f"{timestamp}.{body}".encode("utf-8")
    digest = hmac.new(derived_key, message, hashlib.sha256).hexdigest()
    return str(timestamp), f"sha256={digest}"


def validate_observation(observation):
    if not isinstance(observation, dict):
        raise SenlayError("observation must be an object")
    station_id = str(observation.get("stationId", ""))
    if not station_id.startswith("stn_") or len(station_id) != 36:
        raise SenlayError("stationId must be the stn_... value returned by Senlay")
    try:
        datetime.fromisoformat(str(observation["observedAt"]).replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError) as error:
        raise SenlayError("observedAt must be an ISO-8601 timestamp") from error
    location = observation.get("location") or {}
    lat = location.get("lat")
    lng = location.get("lng", location.get("lon"))
    if not isinstance(lat, (int, float)) or isinstance(lat, bool) or not math.isfinite(lat) or not -90 <= lat <= 90:
        raise SenlayError("location.lat must be between -90 and 90")
    if not isinstance(lng, (int, float)) or isinstance(lng, bool) or not math.isfinite(lng) or not -180 <= lng <= 180:
        raise SenlayError("location.lng must be between -180 and 180")
    measurements = observation.get("measurements")
    if not isinstance(measurements, list) or not 1 <= len(measurements) <= 128:
        raise SenlayError("measurements must contain 1-128 values")
    for index, measurement in enumerate(measurements):
        if not isinstance(measurement, dict) or "." not in str(measurement.get("phenomenon", "")):
            raise SenlayError(f"measurements[{index}].phenomenon is invalid")
        value = measurement.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise SenlayError(f"measurements[{index}].value must be finite")
        if measurement.get("unit") not in SUPPORTED_UNITS:
            raise SenlayError(f"measurements[{index}].unit is unsupported")
        if measurement.get("quality", "raw") not in SUPPORTED_QUALITY:
            raise SenlayError(f"measurements[{index}].quality is unsupported")
    return observation


def observation(station_id, lat, lng, measurements, *, altitude_m=None, metadata=None, observation_id=None, observed_at=None):
    payload = {
        "id": observation_id or f"sensor-{uuid.uuid4()}",
        "stationId": station_id,
        "observedAt": observed_at or utc_now(),
        "location": {"lat": float(lat), "lng": float(lng)},
        "measurements": measurements,
    }
    if altitude_m is not None:
        payload["location"]["altitudeM"] = float(altitude_m)
    if metadata:
        payload["metadata"] = metadata
    return validate_observation(payload)


class SenlayClient:
    def __init__(self, station_id, station_secret, endpoint="https://senlay.cloud/api/v1/observations", timeout=15):
        self.station_id = station_id
        self.station_secret = station_secret
        self.endpoint = endpoint
        self.timeout = timeout
        parsed = urllib.parse.urlparse(endpoint)
        if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise SenlayError("endpoint must use HTTPS, except for a local test server")

    def prepare(self, payload):
        validate_observation(payload)
        if payload["stationId"] != self.station_id:
            raise SenlayError("payload stationId does not match this client")
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        timestamp, signature = sign_payload(body, self.station_secret)
        return body, {
            "Content-Type": "application/json",
            "User-Agent": "senlay-python/0.1",
            "X-Senlay-Station-Id": self.station_id,
            "X-Senlay-Timestamp": timestamp,
            "X-Senlay-Signature": signature,
        }

    def publish(self, payload):
        body, headers = self.prepare(payload)
        return self._post(self.endpoint, body, headers)

    def dry_run(self, payload, account_api_key):
        if not account_api_key:
            raise SenlayError("account API key is required for a commissioning dry run")
        body, headers = self.prepare(payload)
        parsed = urllib.parse.urlsplit(self.endpoint)
        path = f"/api/v1/stations/{urllib.parse.quote(self.station_id)}/test-signature"
        dry_run_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
        headers["Authorization"] = f"Bearer {account_api_key}"
        return self._post(dry_run_url, body, headers)

    def _post(self, url, body, headers):
        request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body) if response_body else {"accepted": True}
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            raise SenlayError(f"Senlay rejected the observation ({error.code}): {detail}") from error
        except urllib.error.URLError as error:
            raise SenlayError(f"Unable to reach Senlay: {error.reason}") from error
