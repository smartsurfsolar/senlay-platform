# Network protocol v0.1

Each message represents one station observation at one time and location. Measurements use explicit canonical units; adapters are responsible for converting vendor payloads before publishing.

Transport uses JSON over HTTPS. A station authenticates messages with `X-Senlay-Station-Id`, `X-Senlay-Timestamp`, and `X-Senlay-Signature`. The signature is `sha256=` followed by the hex HMAC-SHA256 of `<unix_timestamp>.<exact_request_body>`, using `SHA-256(station_secret)` as the HMAC key. This lets Senlay verify requests while retaining only a non-recoverable hash of the station secret.

Gateways should reject timestamps outside a short replay window, invalid coordinates, unsupported units, oversized payloads, and station identifiers outside the documented pattern. Production providers additionally require authorization, provenance, rate limits, licensing metadata, and quality monitoring.

## Commissioning

Production Senlay exposes a dry-run signature endpoint for station owners:

`POST /api/v1/stations/{stationId}/test-signature`

Send the same observation body and the same `X-Senlay-*` signature headers that would be used for `/api/v1/observations`, plus the owner's account bearer token. Senlay verifies ownership, station signature, payload shape, timestamp freshness, plausible ranges, and registered-station location drift, then returns `dryRun: true` without storing the observation.

## Health and local memory

Accepted observations are scored with a station-health signal. Fresh, repeated, non-frozen submissions can rise from `awaiting_data` to `unproven`, `observed`, and `consistent`; disabled stations stop accepting signatures. Treat this as source trust, not a guarantee that the physical reading is correct.

Only `checked` measurements are eligible for learned local memory. Senlay stores baselines by small local grid cell, month, phenomenon, and unit, then compares matching current signed readings against those baselines in context responses. Local memory is historical context and must be compared with current sensors and live models.

See [`protocol/observation.schema.json`](../protocol/observation.schema.json) for the machine-readable envelope.
