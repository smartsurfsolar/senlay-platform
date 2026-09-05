# Senlay — Verified Physical Context for Systems That Act Outside

This is the Senlay Open Network: the open protocol, JavaScript SDK, and edge-gateway starter for connecting independently operated sensors to verified physical context.

[senlay.cloud](https://senlay.cloud) · [API documentation](https://senlay.cloud/docs)

## Connect an AI agent with MCP — no install

Add the public stateless Streamable HTTP endpoint to an MCP-capable client. Anonymous trial access requires no signup or OAuth:

```json
{
  "mcpServers": {
    "senlay": {
      "url": "https://senlay.cloud/mcp"
    }
  }
}
```

The MCP `2026-07-28` server exposes exactly `sense_location`, `check_operability`, and `list_domains`. It preserves Senlay evidence provenance and explicitly reports unavailable inputs instead of inventing values. To use an account tier, add `Authorization: Bearer sl_live_...` to the server headers. Operability results are decision support; humans remain the final authority.

## What is open here

- vendor-neutral observation envelope and JSON Schema
- deterministic validation and normalization
- HMAC request signing for provider-to-gateway transport
- JavaScript client for any compatible ingestion endpoint
- small edge gateway that validates before forwarding
- adapter example and automated tests

The production aggregation engine, global registry, authentication, billing, provider credentials, historical place-memory corpus, risk models, and commercial connectors remain in the private `senlay-platform-core` repository.

## Status

This is the first `0.x` protocol release. Self-service station registration and signed observation ingestion are available at `senlay.cloud` for authenticated Senlay accounts. The server retains only a non-recoverable hash of every station secret; save each secret when it is returned.

## Connect a station to the live network

First create a normal account at [senlay.cloud/register.html](https://senlay.cloud/register.html), then create or retrieve an API key in the dashboard. Use that account key only for provider and station management; use the station secret only to sign observations.

```bash
# Create a provider with your account API key.
curl -sS -X POST https://senlay.cloud/api/v1/providers/register \
  -H "Authorization: Bearer $API_KEY" -H 'content-type: application/json' \
  --data '{"name":"My community network","slug":"my-community-network"}'

# Substitute the returned prv_... ID. Save the returned station secret now.
curl -sS -X POST https://senlay.cloud/api/v1/stations/register \
  -H "Authorization: Bearer $API_KEY" -H 'content-type: application/json' \
  --data '{"providerId":"prv_REPLACE_ME","name":"Beach wind station","sensorType":"weather_station","location":{"lat":15.8801,"lng":108.3380}}'
```

Before publishing live data, use the dashboard's `Send signed test` action to verify the station secret and payload shape without storing a fake observation. Then publish to `https://senlay.cloud/api/v1/observations` using the returned `stationId` plus the `X-Senlay-*` signature headers described in [the network protocol](docs/NETWORK_PROTOCOL.md).

Nearby accepted observations appear in later authenticated `/api/v1/sense` and `/api/v1/pwm` responses as explicitly labelled direct station evidence. Checked station measurements also contribute to Senlay local memory baselines for the same place and season; those baselines are historical context, not current evidence.

## Five-minute Python station

The Python connector uses only the standard library, so a Raspberry Pi or ordinary computer needs no package installation. Copy the `stationId` and one-time station secret returned by the dashboard, then preview a simulated observation locally:

```bash
git clone https://github.com/smartsurfsolar/senlay-platform.git
cd senlay-platform
export SENLAY_STATION_ID='stn_REPLACE_ME'
export SENLAY_STATION_SECRET='sl_station_REPLACE_ME'
python3 python/simulator.py --seed 1
```

Preview mode does not contact Senlay. To verify the signature and payload without storing a reading, add the account API key and use the commissioning endpoint:

```bash
export SENLAY_ACCOUNT_API_KEY='sl_live_REPLACE_ME'
python3 python/simulator.py --dry-run --seed 1
```

To exercise live ingestion with generated data, use `--publish`. Simulator readings are always marked `estimated`, carry `simulated: true`, and never enter the checked-reading place-memory baseline.

```bash
python3 python/simulator.py --publish --count 3 --interval 10 --seed 1
```

For a real wind sensor, pass its readings to the publisher. The default quality is `raw`; use `--quality checked` only when your adapter and sensor calibration justify that claim.

```bash
python3 python/publish_reading.py \
  --lat 15.8801 --lng 108.3380 \
  --wind-speed 7.4 --wind-direction 62
```

Import `SenlayClient` and `observation` from [`python/senlay_client.py`](python/senlay_client.py) to connect another sensor process directly.

## Try the live API — no install

```bash
CREDS="$(curl -sS -X POST https://senlay.cloud/api/v1/agent-register -H 'content-type: application/json' --data '{"ownerEmail":"you@example.com","agentName":"my-first-agent"}')"; printf '%s\n' "$CREDS"
API_KEY="$(printf '%s' "$CREDS" | sed -n 's/.*"apiKey":"\([^"]*\)".*/\1/p')"
curl -sS -H "Authorization: Bearer $API_KEY" "https://senlay.cloud/api/v1/sense?lat=15.8801&lng=108.3380&field=kitesurfing"
```

Save both the `apiKey` and `recoveryToken` shown by the first command; each is returned only once. Replace `you@example.com` and `my-first-agent` with your own identity.

## Local SDK and gateway

```bash
npm install
npm test
cp .env.example .env
npm run gateway
```

Send the example observation to the local gateway:

```bash
npm run example
```

The gateway validates observations locally. Set `SENLAY_INGEST_URL` to forward them to an authorized compatible ingestion endpoint.

## MQTT bridge (optional)

For hardware that publishes JSON observations to an MQTT broker, configure the MQTT variables in `.env` and run:

```bash
npm run mqtt-bridge
```

The bridge subscribes to `SENLAY_MQTT_TOPIC`, validates every message through the SDK, signs it with the station secret, and forwards it to the HTTPS ingestion endpoint. Use one bridge credential per station; do not share a station secret among devices.

## Branches

- `main`: stable public releases
- `develop`: active public development

Changes move from a feature branch to `develop`, then reach `main` after review and tests. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Minimal SDK example

```js
import { SenlayClient } from '@senlay/open-network';

const client = new SenlayClient({
  endpoint: 'https://senlay.cloud/api/v1/observations',
  providerId: 'prv_REPLACE_ME',
  signingSecret: process.env.SENLAY_STATION_SECRET
});

await client.publish({
  stationId: 'stn_REPLACE_ME',
  observedAt: new Date().toISOString(),
  location: { lat: 15.8801, lon: 108.3380 },
  measurements: [{ phenomenon: 'wind.speed', value: 7.4, unit: 'm/s' }]
});
```

## License

Apache-2.0. Contributions are welcome under the same license.
