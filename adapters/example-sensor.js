import { SenlayClient } from '../src/index.js';

const client = new SenlayClient({
  endpoint: process.env.SENLAY_GATEWAY_URL || 'http://127.0.0.1:8787/v1/observations',
  providerId: process.env.SENLAY_PROVIDER_ID || 'community.example',
  signingSecret: process.env.SENLAY_SIGNING_SECRET
});

const result = await client.publish({
  stationId: process.env.SENLAY_STATION_ID || 'example-weather-001',
  observedAt: new Date().toISOString(),
  location: { lat: 15.8801, lon: 108.3380 },
  measurements: [
    { phenomenon: 'wind.speed', value: 7.4, unit: 'm/s', quality: 'checked' },
    { phenomenon: 'wind.direction', value: 62, unit: 'deg', quality: 'checked' }
  ],
  metadata: { adapter: 'example-sensor', firmware: '0.1.0' }
});

console.log(JSON.stringify(result, null, 2));
