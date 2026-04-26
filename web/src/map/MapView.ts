import maplibregl, { type LngLatLike, type Map as MapLibreMap } from "maplibre-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PathLayer, IconLayer, ScatterplotLayer } from "@deck.gl/layers";
import type { PickingInfo } from "@deck.gl/core";
import { staticAssetUrl } from "../paths";
import { cartoDarkStyle } from "./basemap";

type Station = { station_id: string; lat: number; lng: number; total_slots: number };

function ensureLngLat(poly: any[]): [number, number][] {
  // Server returns [lat,lng]. Deck expects [lng,lat].
  // Heuristic: if abs(first) > abs(second) and within lng range, assume [lng,lat]
  if (poly.length === 0) return [];
  const [a, b] = poly[0] as any;
  const looksLikeLngLat = Math.abs(a) <= 180 && Math.abs(b) <= 90;
  return looksLikeLngLat ? (poly as any) : (poly as any).map(([lat, lng]: any) => [lng, lat]);
}

const CAR_ICON_ATLAS =
  "data:image/svg+xml," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">
      <defs>
        <filter id="g" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="b"/>
          <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      <rect x="18" y="18" width="28" height="28" rx="7" fill="#0b0d14" opacity="0.85"/>
      <path filter="url(#g)" d="M22 36c0-7 3-13 10-13s10 6 10 13" fill="#23e7ff"/>
      <circle cx="26" cy="39" r="3" fill="#e8ecff"/>
      <circle cx="38" cy="39" r="3" fill="#e8ecff"/>
    </svg>`
  );

export class MapView {
  private map: MapLibreMap;
  private overlay: MapboxOverlay;
  private side: "baseline" | "oracle" = "oracle";
  private stations: Station[] = [];
  private activeRoute: [number, number][] = [];
  private vehiclePos: [number, number] | null = null; // [lng,lat]
  private vehicleHeadingDeg = 0;
  private follow = false;

  constructor(mount: HTMLElement) {
    // MapLibre requires a real element size; ensure mount is empty.
    mount.innerHTML = "";
    mount.style.position = "relative";

    const mapEl = document.createElement("div");
    mapEl.style.position = "absolute";
    mapEl.style.inset = "0";
    mount.appendChild(mapEl);

    this.map = new maplibregl.Map({
      container: mapEl,
      style: cartoDarkStyle(),
      center: [77.60, 12.97] as LngLatLike,
      zoom: 11.5,
      pitch: 45,
      bearing: -18,
      attributionControl: { compact: true },
      cooperativeGestures: true,
    });

    this.map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");

    this.overlay = new MapboxOverlay({ interleaved: true, layers: [] });
    this.map.addControl(this.overlay as any);

    // Make sure assets are CORS-safe for WebGL
    (this.map as any).getCanvas().setAttribute("crossorigin", "anonymous");
  }

  destroy() {
    try {
      this.map.remove();
    } catch {
      // ignore
    }
  }

  setSide(side: "baseline" | "oracle") {
    this.side = side;
    this.render();
  }

  setFollowVehicle(on: boolean) {
    this.follow = on;
  }

  async bindSession(_sessionId: string, station_nodes: Station[]) {
    this.stations = station_nodes;

    // Fit to stations bbox (area-wise, not whole city)
    const lngs = station_nodes.map((s) => s.lng);
    const lats = station_nodes.map((s) => s.lat);
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lngs), Math.min(...lats)],
      [Math.max(...lngs), Math.max(...lats)],
    ];
    this.map.fitBounds(bounds as any, { padding: 60, duration: 600, maxZoom: 13.8 });

    // Load roads GeoJSON as a deck PathLayer (thin background mesh)
    const roadsUrl = staticAssetUrl("maps/bangalore_roads_demo.geojson");
    const gj = await fetch(roadsUrl).then((r) => r.json());
    const feats = Array.isArray(gj?.features) ? gj.features : [];
    const paths: { path: [number, number][]; highway: string }[] = [];
    for (const f of feats) {
      if (f?.geometry?.type !== "LineString") continue;
      const hw = String(f?.properties?.highway || "");
      const coords = f?.geometry?.coordinates;
      if (!Array.isArray(coords) || coords.length < 2) continue;
      // geojson is [lng,lat] already
      paths.push({ path: coords as [number, number][], highway: hw });
    }

    (this as any)._roads = paths;
    this.render();
  }

  async playExternalEvent(event: any) {
    if (!event || event.type !== "route" || !Array.isArray(event.polyline)) return;
    const poly = ensureLngLat(event.polyline);
    if (poly.length < 2) return;
    this.activeRoute = poly;
    this.vehiclePos = poly[0];

    // approximate heading from first segment
    const [a, b] = [poly[0], poly[1]];
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    this.vehicleHeadingDeg = (Math.atan2(dy, dx) * 180) / Math.PI;

    this.render();
  }

  private render() {
    const roads: { path: [number, number][]; highway: string }[] = (this as any)._roads || [];
    const roadColor = (hw: string) => {
      if (hw === "motorway" || hw === "trunk" || hw === "primary") return [230, 235, 255, 55] as any;
      if (hw === "secondary") return [200, 210, 245, 28] as any;
      return [160, 170, 210, 16] as any;
    };
    const roadWidth = (hw: string) => (hw === "primary" ? 2.4 : hw === "secondary" ? 1.8 : 1.2);

    const routeCore = this.side === "oracle" ? [35, 231, 255, 220] : [188, 198, 229, 190];
    const routeCasing = [0, 0, 0, 160];

    const layers = [
      new PathLayer({
        id: `roads-${this.side}`,
        data: roads,
        getPath: (d: any) => d.path,
        getColor: (d: any) => roadColor(d.highway),
        getWidth: (d: any) => roadWidth(d.highway),
        widthUnits: "pixels",
        rounded: true,
        capRounded: true,
        jointRounded: true,
        pickable: false,
        parameters: { depthTest: false },
      }),
      new PathLayer({
        id: `route-casing-${this.side}`,
        data: this.activeRoute.length ? [{ path: this.activeRoute }] : [],
        getPath: (d: any) => d.path,
        getColor: routeCasing as any,
        getWidth: 10,
        widthUnits: "pixels",
        rounded: true,
        capRounded: true,
        jointRounded: true,
        pickable: false,
        parameters: { depthTest: false },
      }),
      new PathLayer({
        id: `route-core-${this.side}`,
        data: this.activeRoute.length ? [{ path: this.activeRoute }] : [],
        getPath: (d: any) => d.path,
        getColor: routeCore as any,
        getWidth: 6,
        widthUnits: "pixels",
        rounded: true,
        capRounded: true,
        jointRounded: true,
        pickable: false,
        parameters: { depthTest: false },
      }),
      new ScatterplotLayer({
        id: `stations-${this.side}`,
        data: this.stations,
        getPosition: (d: Station) => [d.lng, d.lat],
        getRadius: 26,
        radiusUnits: "meters",
        getFillColor: this.side === "oracle" ? ([35, 231, 255, 160] as any) : ([255, 90, 138, 120] as any),
        getLineColor: [232, 236, 255, 90] as any,
        lineWidthUnits: "pixels",
        lineWidthMinPixels: 1,
        stroked: true,
        filled: true,
        pickable: true,
        autoHighlight: true,
        onClick: (info: PickingInfo) => {
          if (!info?.object) return;
          const s = info.object as any;
          // focus a bit (micro-interaction)
          this.map.easeTo({ center: [s.lng, s.lat], zoom: Math.max(this.map.getZoom(), 13.2), duration: 420 });
        },
        parameters: { depthTest: false },
      }),
      new IconLayer({
        id: `vehicle-${this.side}`,
        data: this.vehiclePos ? [{ pos: this.vehiclePos, angle: this.vehicleHeadingDeg }] : [],
        iconAtlas: CAR_ICON_ATLAS,
        iconMapping: { car: { x: 0, y: 0, width: 64, height: 64, mask: false, anchorY: 52 } },
        getIcon: () => "car",
        sizeUnits: "pixels",
        getSize: 34,
        getPosition: (d: any) => d.pos,
        getAngle: (d: any) => d.angle,
        billboard: false,
        pickable: false,
        parameters: { depthTest: false },
      }),
    ];

    this.overlay.setProps({ layers });

    if (this.follow && this.vehiclePos) {
      this.map.easeTo({ center: this.vehiclePos, duration: 250 });
    }
  }
}

