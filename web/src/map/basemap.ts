import type { StyleSpecification } from "maplibre-gl";

/**
 * MapLibre style using CARTO raster tiles (no API key).
 * Looks close to “mobility product dark mode”.
 */
export function cartoDarkStyle(): StyleSpecification {
  return {
    version: 8,
    sources: {
      carto: {
        type: "raster",
        tiles: ["https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors © CARTO",
      },
    },
    layers: [
      {
        id: "carto",
        type: "raster",
        source: "carto",
      },
    ],
  };
}

