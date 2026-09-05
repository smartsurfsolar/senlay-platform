import { createHmac, timingSafeEqual } from 'node:crypto';

export function signPayload(payload, secret, timestamp = Math.floor(Date.now() / 1000)) {
  if (!secret) throw new TypeError('signing secret is required');
  const body = typeof payload === 'string' ? payload : JSON.stringify(payload);
  const signature = createHmac('sha256', secret).update(`${timestamp}.${body}`).digest('hex');
  return { timestamp: String(timestamp), signature: `sha256=${signature}` };
}

export function verifyPayload(payload, secret, timestamp, signature, maxAgeSeconds = 300) {
  const numericTimestamp = Number(timestamp);
  if (!Number.isFinite(numericTimestamp) || Math.abs(Date.now() / 1000 - numericTimestamp) > maxAgeSeconds) return false;
  const expected = signPayload(payload, secret, numericTimestamp).signature;
  const supplied = String(signature || '');
  return expected.length === supplied.length && timingSafeEqual(Buffer.from(expected), Buffer.from(supplied));
}
