import { normalizeObservation } from './protocol.js';
import { signPayload } from './signing.js';

export class SenlayClient {
  constructor({ endpoint, providerId, signingSecret, fetchImpl = globalThis.fetch }) {
    if (!endpoint) throw new TypeError('endpoint is required');
    if (!providerId) throw new TypeError('providerId is required');
    if (typeof fetchImpl !== 'function') throw new TypeError('fetch implementation is required');
    this.endpoint = endpoint;
    this.providerId = providerId;
    this.signingSecret = signingSecret;
    this.fetch = fetchImpl;
  }

  async publish(observation) {
    const normalized = normalizeObservation(observation, { providerId: this.providerId });
    const body = JSON.stringify(normalized);
    const headers = {
      'content-type': 'application/json',
      'user-agent': '@senlay/open-network',
      'x-senlay-station-id': normalized.stationId
    };
    if (this.signingSecret) {
      const signed = signPayload(body, this.signingSecret);
      headers['x-senlay-timestamp'] = signed.timestamp;
      headers['x-senlay-signature'] = signed.signature;
    }
    const response = await this.fetch(this.endpoint, { method: 'POST', headers, body });
    const responseBody = await response.text();
    if (!response.ok) throw new Error(`Senlay ingestion failed (${response.status}): ${responseBody}`);
    try { return JSON.parse(responseBody); } catch { return { accepted: true, response: responseBody }; }
  }
}
