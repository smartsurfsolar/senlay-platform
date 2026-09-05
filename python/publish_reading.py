#!/usr/bin/env python3
"""Publish one real station reading supplied by a sensor process or operator."""

import argparse
import json
import os

from senlay_client import SenlayClient, SenlayError, observation


def main():
    parser = argparse.ArgumentParser(description="Publish one Senlay station reading")
    parser.add_argument("--station-id", default=os.getenv("SENLAY_STATION_ID"), required=False)
    parser.add_argument("--station-secret", default=os.getenv("SENLAY_STATION_SECRET"), required=False)
    parser.add_argument("--endpoint", default=os.getenv("SENLAY_INGEST_URL", "https://senlay.cloud/api/v1/observations"))
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lng", type=float, required=True)
    parser.add_argument("--wind-speed", type=float, required=True, help="wind speed in m/s")
    parser.add_argument("--wind-direction", type=float, help="meteorological direction in degrees")
    parser.add_argument("--quality", choices=("raw", "checked"), default="raw")
    args = parser.parse_args()
    if not args.station_id or not args.station_secret:
        raise SenlayError("set SENLAY_STATION_ID and SENLAY_STATION_SECRET")
    measurements = [{"phenomenon": "wind.speed", "value": args.wind_speed, "unit": "m/s", "quality": args.quality}]
    if args.wind_direction is not None:
        measurements.append({"phenomenon": "wind.direction", "value": args.wind_direction, "unit": "deg", "quality": args.quality})
    payload = observation(args.station_id, args.lat, args.lng, measurements, metadata={"adapter": "senlay-python"})
    result = SenlayClient(args.station_id, args.station_secret, args.endpoint).publish(payload)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SenlayError as error:
        raise SystemExit(str(error))
