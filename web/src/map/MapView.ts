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
  private raf: number | null = null;
  private lastTs: number | null = null;
  private routeCumM: number[] = [];
  private routeTotalM = 0;
  private routeProgM = 0;
  private staticLayers: any[] = [];

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
      if (this.raf != null) cancelAnimationFrame(this.raf);
      this.map.remove();
    } catch {
      // ignore
    }
  }

  setSide(side: "baseline" | "oracle") {
    this.side = side;
    this.renderStatic();
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
    const roadsUrl = staticAssetUrl("maps/bangalore_roads_full.geojson");
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
    this.renderStatic();
  }

  async playExternalEvent(event: any) {
    if (!event || event.type !== "route" || !Array.isArray(event.polyline)) return;
    const poly = ensureLngLat(event.polyline);
    if (poly.length < 2) return;
    this.activeRoute = poly;
    this.vehiclePos = poly[0];

    // Precompute cumulative meters for time-based interpolation
    this.routeCumM = [0];
    let acc = 0;
    for (let i = 1; i < poly.length; i++) {
      const a = poly[i - 1];
      const b = poly[i];
      acc += this.haversineM(a[1], a[0], b[1], b[0]); // lat,lng
      this.routeCumM.push(acc);
    }
    this.routeTotalM = acc;
    this.routeProgM = 0;

    // Rebuild static layers (roads/stations/route) once; vehicle anim updates icon only.
    this.renderStatic();
    this.kickAnim();
  }

  private kickAnim() {
    if (this.raf != null) cancelAnimationFrame(this.raf);
    this.lastTs = null;
    const tick = (ts: number) => {
      if (this.lastTs == null) this.lastTs = ts;
      const dt = Math.max(0, Math.min(0.05, (ts - this.lastTs) / 1000));
      this.lastTs = ts;

      // Simple speed model (can be upgraded to per-road-type later).
      const speedMps = this.side === "oracle" ? 14.5 : 10.5; // ~52km/h vs ~38km/h
      this.routeProgM = Math.min(this.routeTotalM, this.routeProgM + speedMps * dt);

      const p = this.pointAt(this.routeProgM);
      if (p) {
        this.vehiclePos = p.pos;
        this.vehicleHeadingDeg = p.headingDeg;
        this.renderVehicleOnly();
        if (this.follow && this.vehiclePos) this.map.easeTo({ center: this.vehiclePos, duration: 120 });
      }

      if (this.routeProgM < this.routeTotalM) {
        this.raf = requestAnimationFrame(tick);
      } else {
        this.raf = null;
      }
    };
    this.raf = requestAnimationFrame(tick);
  }

  private pointAt(m: number): { pos: [number, number]; headingDeg: number } | null {
    if (!this.activeRoute.length || this.routeCumM.length !== this.activeRoute.length) return null;
    if (m <= 0) {
      const a = this.activeRoute[0];
      const b = this.activeRoute[1];
      return { pos: a, headingDeg: this.headingDeg(a, b) };
    }
    if (m >= this.routeTotalM) {
      const n = this.activeRoute.length;
      const a = this.activeRoute[n - 2];
      const b = this.activeRoute[n - 1];
      return { pos: b, headingDeg: this.headingDeg(a, b) };
    }
    // Find segment
    let i = 1;
    while (i < this.routeCumM.length && this.routeCumM[i] < m) i++;
    const i0 = Math.max(1, i);
    const a = this.activeRoute[i0 - 1];
    const b = this.activeRoute[i0];
    const m0 = this.routeCumM[i0 - 1];
    const m1 = this.routeCumM[i0];
    const t = m1 <= m0 ? 0 : (m - m0) / (m1 - m0);
    const lng = a[0] + (b[0] - a[0]) * t;
    const lat = a[1] + (b[1] - a[1]) * t;
    return { pos: [lng, lat], headingDeg: this.headingDeg(a, b) };
  }

  private headingDeg(a: [number, number], b: [number, number]) {
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    return (Math.atan2(dy, dx) * 180) / Math.PI;
  }

  private haversineM(lat1: number, lng1: number, lat2: number, lng2: number) {
    const R = 6371000;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    const sLat1 = (lat1 * Math.PI) / 180;
    const sLat2 = (lat2 * Math.PI) / 180;
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(sLat1) * Math.cos(sLat2) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  private renderVehicleOnly() {
    const vehicleLayer = this.makeVehicleLayer();
    this.overlay.setProps({ layers: [...this.staticLayers, vehicleLayer] });
  }

  private renderStatic() {
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
        // placeholder; replaced on every tick by renderVehicleOnly
        id: `vehicle-placeholder-${this.side}`,
        data: [],
        iconAtlas: CAR_ICON_ATLAS,
        iconMapping: { car: { x: 0, y: 0, width: 64, height: 64, mask: false, anchorY: 52 } },
        getIcon: () => "car",
        sizeUnits: "pixels",
        getSize: 34,
        getPosition: (d: any) => (d as any).pos,
        getAngle: (d: any) => (d as any).angle,
        billboard: false,
        pickable: false,
        parameters: { depthTest: false },
      }),
    ];
    this.staticLayers = layers.slice(0, layers.length - 1);
    this.overlay.setProps({ layers: [...this.staticLayers, this.makeVehicleLayer()] });
  }

  private makeVehicleLayer() {
    return new IconLayer({
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
    });
  }
}

