# Senlay Open Network

Open protocol, JavaScript SDK, and edge-gateway starter for connecting independently operated sensors to Senlay.

[senlay.cloud](https://senlay.cloud) · [API documentation](https://senlay.cloud/docs.html)

## What is open here

- vendor-neutral observation envelope and JSON Schema
- deterministic validation and normalization
- HMAC request signing for provider-to-gateway transport
- JavaScript client for any compatible ingestion endpoint
- small edge gateway that validates before forwarding
- adapter example and automated tests

The production aggregation engine, global registry, authentication, billing, provider credentials, historical place-memory corpus, risk models, and commercial connectors remain in the private `senlay-platform-core` repository.

## Status

This is the first `0.x` protocol release. The SDK and gateway work locally and against a configurable compatible endpoint. Public self-service sensor ingestion on `senlay.cloud` is not claimed as generally available until its production endpoint and provider onboarding process are announced.

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

## Branches

- `main`: stable public releases
- `develop`: active public development

Changes move from a feature branch to `develop`, then reach `main` after review and tests. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Minimal SDK example

```js
import { SenlayClient } from '@senlay/open-network';

const client = new SenlayClient({
  endpoint: 'http://127.0.0.1:8787/v1/observations',
  providerId: 'community.example',
  signingSecret: process.env.SENLAY_SIGNING_SECRET
});

await client.publish({
  stationId: 'station-001',
  observedAt: new Date().toISOString(),
  location: { lat: 15.8801, lon: 108.3380 },
  measurements: [{ phenomenon: 'wind.speed', value: 7.4, unit: 'm/s' }]
});
```

## License

Apache-2.0. Contributions are welcome under the same license.
