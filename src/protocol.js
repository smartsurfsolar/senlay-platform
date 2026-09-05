const UNITS = new Set(['m/s', 'km/h', 'kt', 'deg', 'C', 'hPa', '%', 'mm', 'm', 'ug/m3']);

export function validateObservation(input) {
  const errors = [];
  if (!input || typeof input !== 'object' || Array.isArray(input)) return ['observation must be an object'];
  if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{1,127}$/.test(input.stationId || '')) errors.push('stationId is invalid');
  if (!input.observedAt || Number.isNaN(Date.parse(input.observedAt))) errors.push('observedAt must be an ISO-8601 date-time');
  const lat = input.location?.lat;
  const lon = input.location?.lon;
  if (!Number.isFinite(lat) || lat < -90 || lat > 90) errors.push('location.lat must be between -90 and 90');
  if (!Number.isFinite(lon) || lon < -180 || lon > 180) errors.push('location.lon must be between -180 and 180');
  if (!Array.isArray(input.measurements) || input.measurements.length === 0) {
    errors.push('measurements must contain at least one item');
  } else {
    input.measurements.forEach((item, index) => {
      if (!/^[a-z][a-z0-9]*(\.[a-z0-9]+)+$/.test(item?.phenomenon || '')) errors.push(`measurements[${index}].phenomenon is invalid`);
      if (!Number.isFinite(item?.value)) errors.push(`measurements[${index}].value must be finite`);
      if (!UNITS.has(item?.unit)) errors.push(`measurements[${index}].unit is unsupported`);
    });
  }
  return errors;
}

export function normalizeObservation(input, { providerId } = {}) {
  const errors = validateObservation(input);
  if (errors.length) throw new TypeError(errors.join('; '));
  return {
    schema: 'https://senlay.cloud/protocol/observation/v0.1',
    id: input.id || crypto.randomUUID(),
    providerId: input.providerId || providerId,
    stationId: input.stationId,
    observedAt: new Date(input.observedAt).toISOString(),
    receivedAt: new Date().toISOString(),
    location: { lat: input.location.lat, lon: input.location.lon, ...(Number.isFinite(input.location.altitudeM) ? { altitudeM: input.location.altitudeM } : {}) },
    measurements: input.measurements.map(item => ({ phenomenon: item.phenomenon, value: item.value, unit: item.unit, ...(item.quality ? { quality: item.quality } : {}) })),
    ...(input.metadata ? { metadata: input.metadata } : {})
  };
}
