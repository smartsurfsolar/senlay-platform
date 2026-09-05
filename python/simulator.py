#!/usr/bin/env python3
"""Generate plausible estimated readings without claiming real sensor evidence."""

import argparse
import json
import os
import random
import time

from senlay_client import SenlayClient, SenlayError, observation


def parser():
    value = argparse.ArgumentParser(description="Senlay safe station simulator")
    mode = value.add_mutually_exclusive_group()
    mode.add_argument("--publish", action="store_true", help="publish estimated readings to the live ingestion endpoint")
    mode.add_argument("--dry-run", action="store_true", help="verify one signed payload without storing it")
    value.add_argument("--station-id", default=os.getenv("SENLAY_STATION_ID"))
    value.add_argument("--station-secret", default=os.getenv("SENLAY_STATION_SECRET"))
    value.add_argument("--account-api-key", default=os.getenv("SENLAY_ACCOUNT_API_KEY"))
    value.add_argument("--endpoint", default=os.getenv("SENLAY_INGEST_URL", "https://senlay.cloud/api/v1/observations"))
    value.add_argument("--lat", type=float, default=float(os.getenv("SENLAY_STATION_LAT", "15.8801")))
    value.add_argument("--lng", type=float, default=float(os.getenv("SENLAY_STATION_LNG", "108.3380")))
    value.add_argument("--count", type=int, default=1)
    value.add_argument("--interval", type=float, default=10)
    value.add_argument("--seed", type=int)
    return value


def main():
    args = parser().parse_args()
    if not args.station_id:
        raise SenlayError("set SENLAY_STATION_ID or pass --station-id")
    if not 1 <= args.count <= 1000 or args.interval < 0:
        raise SenlayError("count must be 1-1000 and interval must be non-negative")
    rng = random.Random(args.seed)
    client = None
    if args.publish or args.dry_run:
        if not args.station_secret:
            raise SenlayError("set SENLAY_STATION_SECRET before signing")
        client = SenlayClient(args.station_id, args.station_secret, args.endpoint)
    for index in range(args.count):
        wind_speed = round(max(0, rng.gauss(7.0, 0.8)), 2)
        wind_direction = round((rng.gauss(75, 8) + 360) % 360, 1)
        payload = observation(
            args.station_id, args.lat, args.lng,
            [
                {"phenomenon": "wind.speed", "value": wind_speed, "unit": "m/s", "quality": "estimated"},
                {"phenomenon": "wind.direction", "value": wind_direction, "unit": "deg", "quality": "estimated"},
            ],
            metadata={"adapter": "senlay-python-simulator", "simulated": True},
        )
        if args.dry_run:
            result = client.dry_run(payload, args.account_api_key)
        elif args.publish:
            result = client.publish(payload)
        else:
            result = {"preview": True, "stored": False, "observation": payload}
        print(json.dumps(result, indent=2))
        if index + 1 < args.count:
            time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except (SenlayError, KeyboardInterrupt) as error:
        raise SystemExit(str(error))
