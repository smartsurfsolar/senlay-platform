import mqtt from 'mqtt';
import { SenlayClient } from '../src/client.js';

const brokerUrl = process.env.SENLAY_MQTT_URL || '';
const topic = process.env.SENLAY_MQTT_TOPIC || 'senlay/observations/#';
const endpoint = process.env.SENLAY_INGEST_URL || 'https://senlay.cloud/api/v1/observations';
const providerId = process.env.SENLAY_PROVIDER_ID || '';
const signingSecret = process.env.SENLAY_SIGNING_SECRET || '';

if (!brokerUrl || !providerId || !signingSecret) {
  console.error('Set SENLAY_MQTT_URL, SENLAY_PROVIDER_ID, and SENLAY_SIGNING_SECRET before starting the MQTT bridge.');
  process.exit(1);
}

const client = new SenlayClient({ endpoint, providerId, signingSecret });
const broker = mqtt.connect(brokerUrl, {
  username: process.env.SENLAY_MQTT_USERNAME || undefined,
  password: process.env.SENLAY_MQTT_PASSWORD || undefined,
  reconnectPeriod: 2000,
  connectTimeout: 10000
});

broker.on('connect', () => {
  broker.subscribe(topic, { qos: 1 }, error => {
    if (error) console.error('MQTT subscription failed:', error.message);
    else console.log(`Senlay MQTT bridge subscribed to ${topic}`);
  });
});

broker.on('message', async (receivedTopic, payload) => {
  try {
    const observation = JSON.parse(payload.toString('utf8'));
    const result = await client.publish(observation);
    console.log(JSON.stringify({ topic: receivedTopic, stationId: observation.stationId, accepted: result.accepted !== false }));
  } catch (error) {
    // Do not echo payloads: they can contain proprietary sensor metadata.
    console.error(`MQTT observation rejected on ${receivedTopic}: ${error.message}`);
  }
});

broker.on('error', error => console.error('MQTT broker error:', error.message));
process.on('SIGINT', () => broker.end(true, () => process.exit(0)));
process.on('SIGTERM', () => broker.end(true, () => process.exit(0)));
