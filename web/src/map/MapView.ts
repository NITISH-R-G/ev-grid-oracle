import maplibregl, { type LngLatLike, type Map as MapLibreMap } from "maplibre-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PathLayer, IconLayer, ScatterplotLayer } from "@deck.gl/layers";
import { staticAssetUrl } from "../paths";
import { cartoDarkStyle } from "./basemap";

type Station = { station_id: string; lat: number; lng: number; total_slots: number };

function ensureLngLat(poly: any[]): [number, number][] {
  // Server returns [lat,lng]. Deck expects [lng,lat].
  // Do NOT use heuristics here: Bangalore values (12.xx, 77.xx) can look valid in both orders.
  return Array.isArray(poly) ? (poly as any).map(([lat, lng]: any) => [lng, lat]) : [];
}

// Canvas atlas containing: car | bike | station
// (data-URL SVG atlases can fail to load in some deck.gl environments)
function buildIconAtlas(): HTMLCanvasElement {
  const c = document.createElement("canvas");
  c.width = 192;
  c.height = 64;
  const ctx = c.getContext("2d")!;
  ctx.clearRect(0, 0, c.width, c.height);

  const drawGlow = (x: number, y: number, w: number, h: number) => {
    ctx.save();
    ctx.globalAlpha = 0.28;
    ctx.fillStyle = "#23e7ff";
    ctx.shadowColor = "#23e7ff";
    ctx.shadowBlur = 10;
    ctx.fillRect(x, y, w, h);
    ctx.restore();
  };

  const drawCar = (ox: number) => {
    drawGlow(ox + 18, 18, 28, 28);
    ctx.fillStyle = "#ffffff";
    ctx.globalAlpha = 0.96;
    roundRect(ctx, ox + 18, 18, 28, 28, 8);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#0b0d14";
    ctx.beginPath();
    ctx.arc(ox + 26, 39, 3.2, 0, Math.PI * 2);
    ctx.arc(ox + 38, 39, 3.2, 0, Math.PI * 2);
    ctx.fill();
  };

  const drawBike = (ox: number) => {
    ctx.save();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(ox + 22, 40, 7, 0, Math.PI * 2);
    ctx.arc(ox + 42, 40, 7, 0, Math.PI * 2);
    ctx.stroke();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(ox + 26, 40);
    ctx.lineTo(ox + 33, 26);
    ctx.lineTo(ox + 40, 40);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(ox + 33, 26);
    ctx.lineTo(ox + 28, 26);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(ox + 33, 26);
    ctx.lineTo(ox + 38, 22);
    ctx.stroke();
    ctx.restore();
  };

  const drawStation = (ox: number) => {
    drawGlow(ox + 24, 14, 18, 28);
    ctx.fillStyle = "#ffffff";
    roundRect(ctx, ox + 24, 14, 18, 28, 4);
    ctx.fill();
    ctx.fillStyle = "#0b0d14";
    roundRect(ctx, ox + 28, 18, 10, 8, 2);
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(ox + 42, 24);
    ctx.bezierCurveTo(50 + ox, 28, 50 + ox, 38, ox + 42, 42);
    ctx.stroke();
    ctx.strokeStyle = "#0b0d14";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(ox + 32, 28);
    ctx.lineTo(ox + 28, 36);
    ctx.lineTo(ox + 34, 36);
    ctx.lineTo(ox + 30, 44);
    ctx.stroke();
  };

  const roundRect = (cx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => {
    const rr = Math.min(r, w / 2, h / 2);
    cx.beginPath();
    cx.moveTo(x + rr, y);
    cx.arcTo(x + w, y, x + w, y + h, rr);
    cx.arcTo(x + w, y + h, x, y + h, rr);
    cx.arcTo(x, y + h, x, y, rr);
    cx.arcTo(x, y, x + w, y, rr);
    cx.closePath();
  };

  drawCar(0);
  drawBike(64);
  drawStation(128);
  return c;
}

const ICON_ATLAS = buildIconAtlas() as any;

const ICON_MAPPING = {
  car: { x: 0, y: 0, width: 64, height: 64, mask: true, anchorY: 52 },
  bike: { x: 64, y: 0, width: 64, height: 64, mask: true, anchorY: 52 },
  station: { x: 128, y: 0, width: 64, height: 64, mask: true, anchorY: 52 },
} as const;

type VehicleKind = "car" | "bike";
type Vehicle = {
  id: string;
  kind: VehicleKind;
  color: [number, number, number, number];
  route: [number, number][]; // [lng,lat]
  cumM: number[];
  totalM: number;
  progM: number;
  pos: [number, number];
  headingDeg: number;
  lastSeenTs: number;
  segMq?: number[] | null; // traffic multiplier per segment (q=1000 => 1.0)
  speedMps?: number; // smoothed instantaneous speed
};

export class MapView {
  private map: MapLibreMap;
  private overlay: MapboxOverlay;
  private side: "baseline" | "oracle" = "oracle";
  private stations: Station[] = [];
  private activeRoute: [number, number][] = [];
  private follow = false;
  private raf: number | null = null;
  private lastTs: number | null = null;
  private staticLayers: any[] = [];
  private vehicles: Map<string, Vehicle> = new Map();

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

    // Load simplified render paths (much smaller than GeoJSON).
    // Fallback to GeoJSON only if render file is missing.
    const paths: { path: [number, number][]; highway: string }[] = [];
    try {
      const renderUrl = staticAssetUrl("maps/bangalore_roads_render.json");
      const rows = (await fetch(renderUrl).then((r) => r.json())) as any[];
      if (Array.isArray(rows)) {
        for (const row of rows) {
          const hw = String(row?.highway || "");
          const coords = row?.path;
          if (!Array.isArray(coords) || coords.length < 2) continue;
          paths.push({ path: coords as [number, number][], highway: hw });
        }
      }
    } catch {
      const roadsUrl = staticAssetUrl("maps/bangalore_roads_full.geojson");
      const gj = await fetch(roadsUrl).then((r) => r.json());
      const feats = Array.isArray(gj?.features) ? gj.features : [];
      for (const f of feats) {
        if (f?.geometry?.type !== "LineString") continue;
        const hw = String(f?.properties?.highway || "");
        const coords = f?.geometry?.coordinates;
        if (!Array.isArray(coords) || coords.length < 2) continue;
        paths.push({ path: coords as [number, number][], highway: hw });
      }
    }

    (this as any)._roads = paths;
    this.renderStatic();
  }

  async playExternalEvent(event: any) {
    if (!event || event.type !== "route" || !Array.isArray(event.polyline)) return;
    const poly = ensureLngLat(event.polyline);
    if (poly.length < 2) return;
    this.activeRoute = poly;
    const segMq = Array.isArray(event?.traffic_seg_m_q) ? (event.traffic_seg_m_q as number[]) : null;

    // Decide vehicle type from persona if present (taxi/corp/private/emergency -> car; delivery -> bike).
    const persona = String(event?.persona || "");
    const kind: VehicleKind = /Delivery/i.test(persona) ? "bike" : "car";

    const id = String(event?.ev_id || `ev-${Math.random().toString(16).slice(2)}`);
    const now = performance.now();
    const baseColor: [number, number, number, number] =
      this.side === "oracle" ? ([35, 231, 255, 210] as any) : ([255, 90, 138, 190] as any);
    const color: [number, number, number, number] =
      /Emergency/i.test(persona) ? ([255, 72, 72, 220] as any) : baseColor;

    const cumM = [0];
    let acc = 0;
    for (let i = 1; i < poly.length; i++) {
      const a = poly[i - 1];
      const b = poly[i];
      acc += this.haversineM(a[1], a[0], b[1], b[0]); // lat,lng
      cumM.push(acc);
    }

    const v: Vehicle = {
      id,
      kind,
      color,
      route: poly,
      cumM,
      totalM: acc,
      progM: 0,
      pos: poly[0],
      headingDeg: this.headingDeg(poly[0], poly[1]),
      lastSeenTs: now,
      segMq,
      speedMps: undefined,
    };
    this.vehicles.set(id, v);

    // Keep the map clean: cap number of vehicles (oldest removed).
    const maxVehicles = 90;
    if (this.vehicles.size > maxVehicles) {
      const oldest = [...this.vehicles.values()].sort((a, b) => a.lastSeenTs - b.lastSeenTs)[0];
      if (oldest) this.vehicles.delete(oldest.id);
    }

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
      const baseSpeedMps = this.side === "oracle" ? 14.5 : 10.5; // ~52km/h vs ~38km/h

      const now = performance.now();
      // TTL: fade out old vehicles so the map doesn't become messy.
      const ttlMs = 22_000;
      for (const [id, v] of this.vehicles) {
        if (now - v.lastSeenTs > ttlMs) {
          this.vehicles.delete(id);
          continue;
        }
        const base = v.kind === "bike" ? baseSpeedMps * 0.78 : baseSpeedMps;
        const m = this.multAt(v);
        const targetSpeed = base / Math.max(0.35, Math.min(1.15, m));
        v.speedMps = v.speedMps == null ? targetSpeed : v.speedMps * 0.84 + targetSpeed * 0.16;
        v.progM = Math.min(v.totalM, v.progM + (v.speedMps || targetSpeed) * dt);
        const p = this.pointAtOn(v.route, v.cumM, v.totalM, v.progM);
        if (p) {
          v.pos = p.pos;
          v.headingDeg = p.headingDeg;
        }
      }

      // Follow the most recently updated vehicle (if enabled)
      if (this.follow) {
        const latest = [...this.vehicles.values()].sort((a, b) => b.lastSeenTs - a.lastSeenTs)[0];
        if (latest?.pos) this.map.easeTo({ center: latest.pos, duration: 120 });
      }

      this.renderVehicleOnly();

      if (this.vehicles.size > 0) {
        this.raf = requestAnimationFrame(tick);
      } else {
        this.raf = null;
      }
    };
    this.raf = requestAnimationFrame(tick);
  }

  private pointAtOn(
    route: [number, number][],
    cumM: number[],
    totalM: number,
    m: number
  ): { pos: [number, number]; headingDeg: number } | null {
    if (!route.length || cumM.length !== route.length) return null;
    if (m <= 0) {
      const a = route[0];
      const b = route[1];
      return { pos: a, headingDeg: this.headingDeg(a, b) };
    }
    if (m >= totalM) {
      const n = route.length;
      const a = route[n - 2];
      const b = route[n - 1];
      return { pos: b, headingDeg: this.headingDeg(a, b) };
    }
    let i = 1;
    while (i < cumM.length && cumM[i] < m) i++;
    const i0 = Math.max(1, i);
    const a = route[i0 - 1];
    const b = route[i0];
    const m0 = cumM[i0 - 1];
    const m1 = cumM[i0];
    const t = m1 <= m0 ? 0 : (m - m0) / (m1 - m0);
    const lng = a[0] + (b[0] - a[0]) * t;
    const lat = a[1] + (b[1] - a[1]) * t;
    return { pos: [lng, lat], headingDeg: this.headingDeg(a, b) };
  }

  private multAt(v: Vehicle): number {
    const segMq = v.segMq;
    if (!segMq || segMq.length < 1) return 1.0;
    let i = 1;
    while (i < v.cumM.length && v.cumM[i] < v.progM) i++;
    const segIdx = Math.max(0, Math.min(segMq.length - 1, i - 1));
    const q = Number(segMq[segIdx] || 1000);
    return q / 1000.0;
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
    const vehicleDotLayer = this.makeVehicleDotLayer();
    const stationLayer = this.makeStationIconLayer();
    this.overlay.setProps({ layers: [...this.staticLayers, stationLayer, vehicleDotLayer, vehicleLayer] });
  }

  private renderStatic() {
    const roads: { path: [number, number][]; highway: string }[] = (this as any)._roads || [];
    const roadColor = (hw: string) => {
      if (hw === "motorway" || hw === "trunk" || hw === "primary") return [230, 235, 255, 55] as any;
      if (hw === "secondary") return [200, 210, 245, 28] as any;
      return [160, 170, 210, 16] as any;
    };
    const roadWidth = (hw: string) => (hw === "primary" ? 2.4 : hw === "secondary" ? 1.8 : 1.2);

    const routeCore = this.side === "oracle" ? [35, 231, 255, 235] : [232, 236, 255, 220];
    const routeCasing = [0, 0, 0, 190];

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
        getWidth: 12,
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
        getWidth: 7,
        widthUnits: "pixels",
        rounded: true,
        capRounded: true,
        jointRounded: true,
        pickable: false,
        parameters: { depthTest: false },
      }),
      // stations + vehicles are appended by renderVehicleOnly() for smooth updates
    ];
    this.staticLayers = layers;
    this.overlay.setProps({
      layers: [...this.staticLayers, this.makeStationIconLayer(), this.makeVehicleDotLayer(), this.makeVehicleLayer()],
    });
  }

  private makeVehicleLayer() {
    return new IconLayer({
      id: `vehicle-${this.side}`,
      data: [...this.vehicles.values()],
      iconAtlas: ICON_ATLAS as any,
      iconMapping: ICON_MAPPING as any,
      getIcon: (d: any) => d.kind,
      sizeUnits: "pixels",
      getSize: (d: any) => (d.kind === "bike" ? 28 : 32),
      getPosition: (d: any) => d.pos,
      getAngle: (d: any) => d.headingDeg,
      getColor: (d: any) => d.color,
      billboard: false,
      pickable: false,
      parameters: { depthTest: false },
    });
  }

  private makeVehicleDotLayer() {
    return new ScatterplotLayer({
      id: `vehicle-dots-${this.side}`,
      data: [...this.vehicles.values()],
      getPosition: (d: any) => d.pos,
      radiusUnits: "pixels",
      getRadius: (d: any) => (d.kind === "bike" ? 4.5 : 5.5),
      getFillColor: (d: any) => d.color,
      getLineColor: [0, 0, 0, 140] as any,
      lineWidthUnits: "pixels",
      lineWidthMinPixels: 1,
      stroked: true,
      filled: true,
      pickable: false,
      parameters: { depthTest: false },
    });
  }

  private makeStationIconLayer() {
    return new IconLayer({
      id: `station-icons-${this.side}`,
      data: this.stations,
      iconAtlas: ICON_ATLAS as any,
      iconMapping: ICON_MAPPING as any,
      getIcon: () => "station",
      sizeUnits: "pixels",
      getSize: 24,
      getPosition: (d: Station) => [d.lng, d.lat],
      getColor: this.side === "oracle" ? ([35, 231, 255, 170] as any) : ([232, 236, 255, 120] as any),
      billboard: true,
      pickable: false,
      parameters: { depthTest: false },
    });
  }
}

