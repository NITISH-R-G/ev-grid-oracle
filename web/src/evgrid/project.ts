export type BBox = { latLo: number; latHi: number; lngLo: number; lngHi: number };

export function computeBBox(nodes: { lat: number; lng: number }[]): BBox {
  const lats = nodes.map((n) => n.lat);
  const lngs = nodes.map((n) => n.lng);
  return {
    latLo: Math.min(...lats),
    latHi: Math.max(...lats),
    lngLo: Math.min(...lngs),
    lngHi: Math.max(...lngs),
  };
}

export function makeProjector(bbox: BBox, w: number, h: number, pad = 40) {
  const { latLo, latHi, lngLo, lngHi } = bbox;
  const latSpan = Math.max(1e-9, latHi - latLo);
  const lngSpan = Math.max(1e-9, lngHi - lngLo);
  return (lat: number, lng: number) => {
    const nx = (lng - lngLo) / lngSpan;
    const ny = 1 - (lat - latLo) / latSpan;
    const x = pad + nx * (w - pad * 2);
    const y = pad + ny * (h - pad * 2);
    return { x, y };
  };
}

