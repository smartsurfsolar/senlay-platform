import http from 'node:http';
import { normalizeObservation } from '../src/protocol.js';
import { signPayload, verifyPayload } from '../src/signing.js';

const host = process.env.SENLAY_GATEWAY_HOST || '127.0.0.1';
const port = Number(process.env.SENLAY_GATEWAY_PORT || 8787);
const upstream = process.env.SENLAY_INGEST_URL || '';
const providerId = process.env.SENLAY_PROVIDER_ID || 'community.local';
const signingSecret = process.env.SENLAY_SIGNING_SECRET || '';
const maxBytes = 256 * 1024;

function reply(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > maxBytes) throw Object.assign(new Error('payload too large'), { status: 413 });
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8');
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'GET' && req.url === '/health') return reply(res, 200, { status: 'ok', mode: upstream ? 'forward' : 'validate-only' });
  if (req.method !== 'POST' || req.url !== '/v1/observations') return reply(res, 404, { error: 'not_found' });
  try {
    const body = await readBody(req);
    if (signingSecret && !verifyPayload(body, signingSecret, req.headers['x-senlay-timestamp'], req.headers['x-senlay-signature'])) {
      return reply(res, 401, { error: 'invalid_signature' });
    }
    const observation = normalizeObservation(JSON.parse(body), { providerId });
    if (!upstream) return reply(res, 202, { accepted: true, forwarded: false, observationId: observation.id });
    const upstreamBody = JSON.stringify(observation);
    const headers = { 'content-type': 'application/json', 'x-senlay-station-id': observation.stationId };
    if (signingSecret) {
      const signed = signPayload(upstreamBody, signingSecret);
      headers['x-senlay-timestamp'] = signed.timestamp;
      headers['x-senlay-signature'] = signed.signature;
    }
    const response = await fetch(upstream, { method: 'POST', headers, body: upstreamBody });
    const responseText = await response.text();
    if (!response.ok) return reply(res, 502, { error: 'upstream_rejected', upstreamStatus: response.status, detail: responseText.slice(0, 500) });
    return reply(res, 202, { accepted: true, forwarded: true, observationId: observation.id });
  } catch (error) {
    return reply(res, error.status || 400, { error: 'invalid_observation', detail: error.message });
  }
});

server.listen(port, host, () => {
  console.log(`Senlay edge gateway listening at http://${host}:${port}`);
});
