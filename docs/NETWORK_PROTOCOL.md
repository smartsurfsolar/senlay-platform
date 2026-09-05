# Network protocol v0.1

Each message represents one station observation at one time and location. Measurements use explicit canonical units; adapters are responsible for converting vendor payloads before publishing.

Transport uses JSON over HTTPS. A station authenticates messages with `X-Senlay-Station-Id`, `X-Senlay-Timestamp`, and `X-Senlay-Signature`. The signature is `sha256=` followed by the hex HMAC-SHA256 of `<unix_timestamp>.<exact_request_body>`, using `SHA-256(station_secret)` as the HMAC key. This lets Senlay verify requests while retaining only a non-recoverable hash of the station secret.

Gateways should reject timestamps outside a short replay window, invalid coordinates, unsupported units, oversized payloads, and station identifiers outside the documented pattern. Production providers additionally require authorization, provenance, rate limits, licensing metadata, and quality monitoring.

See [`protocol/observation.schema.json`](../protocol/observation.schema.json) for the machine-readable envelope.
