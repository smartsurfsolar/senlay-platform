import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeObservation, signPayload, validateObservation, verifyPayload } from '../src/index.js';

const sample = {
  stationId: 'station-001',
  observedAt: '2026-09-05T10:00:00.000Z',
  location: { lat: 15.8801, lon: 108.338 },
  measurements: [{ phenomenon: 'wind.speed', value: 7.4, unit: 'm/s' }]
};

test('validates and normalizes an observation', () => {
  assert.deepEqual(validateObservation(sample), []);
  const value = normalizeObservation(sample, { providerId: 'provider.example' });
  assert.equal(value.providerId, 'provider.example');
  assert.equal(value.measurements[0].value, 7.4);
  assert.match(value.id, /^[0-9a-f-]{36}$/);
});

test('rejects invalid coordinates and units', () => {
  const errors = validateObservation({ ...sample, location: { lat: 100, lon: 0 }, measurements: [{ phenomenon: 'wind.speed', value: 1, unit: 'mph' }] });
  assert.ok(errors.some(error => error.includes('location.lat')));
  assert.ok(errors.some(error => error.includes('unit')));
});

test('signs and verifies an exact payload', () => {
  const body = JSON.stringify(sample);
  const timestamp = Math.floor(Date.now() / 1000);
  const signed = signPayload(body, 'test-secret', timestamp);
  assert.equal(verifyPayload(body, 'test-secret', signed.timestamp, signed.signature), true);
  assert.equal(verifyPayload(`${body}x`, 'test-secret', signed.timestamp, signed.signature), false);
});
