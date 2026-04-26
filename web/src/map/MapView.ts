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

/** Uniform resample cap: huge OSM polylines slow Deck; keep shape + endpoints. */
function simplifyPathLngLat(path: [number, number][], maxPts: number): [number, number][] {
  if (path.length <= 2 || path.length <= maxPts) return path;
  const out: [number, number][] = [];
  const last = path.length - 1;
  const step = last / (maxPts - 1);
  for (let k = 0; k < maxPts - 1; k++) {
    const idx = Math.min(last, Math.round(k * step));
    out.push([path[idx][0], path[idx][1]]);
  }
  out.push([path[last][0], path[last][1]]);
  return out;
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
    // Exact emoji only (requested): no outline/glow/fallback styling.
    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "34px \"Segoe UI Emoji\", \"Apple Color Emoji\", \"Noto Color Emoji\", system-ui";
    ctx.globalAlpha = 1;
    ctx.fillText("🚗", ox + 32, 34);
    ctx.restore();
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
  arrivedTs?: number | null;
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
  private heroVehicleId: string | null = null;
  private raf: number | null = null;
  private lastTs: number | null = null;
  private staticLayers: any[] = [];
  private vehicles: Map<string, Vehicle> = new Map();

  private heroRemainingPath(): [number, number][] {
    if (!this.heroVehicleId) return this.activeRoute;
    const v = this.vehicles.get(this.heroVehicleId);
    if (!v || v.route.length < 2 || v.cumM.length !== v.route.length) return this.activeRoute;
    return this.splitRouteAtProgress(v.route, v.cumM, v.totalM, v.progM).remaining;
  }

  private nearestProgMOnRoute(pos: [number, number], route: [number, number][], cumM: number[]) {
    if (!route.length || cumM.length !== route.length) return 0;
    let bestI = 0;
    let bestD = 1e18;
    for (let i = 0; i < route.length; i++) {
      const p = route[i];
      const d = this.haversineM(pos[1], pos[0], p[1], p[0]);
      if (d < bestD) {
        bestD = d;
        bestI = i;
      }
    }
    return Number(cumM[bestI] || 0);
  }

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
    this.heroVehicleId = id;
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

    // If we already have this vehicle, update its route but keep its current position/progress
    // so the animation feels continuous (no teleport to the start of the new polyline).
    const prev = this.vehicles.get(id);
    if (prev) {
      prev.kind = kind;
      prev.color = color;
      prev.route = poly;
      prev.cumM = cumM;
      prev.totalM = acc;
      prev.segMq = segMq;
      prev.lastSeenTs = now;
      // Anchor progress to the closest point on the new route.
      const anchored = this.nearestProgMOnRoute(prev.pos, poly, cumM);
      prev.progM = Math.max(0, Math.min(acc, anchored));
      // Update heading based on the next point (if any).
      const p = this.pointAtOn(prev.route, prev.cumM, prev.totalM, prev.progM);
      if (p) {
        prev.pos = p.pos;
        prev.headingDeg = p.headingDeg;
      }
    } else {
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
    }

    // Keep the map clean: cap number of vehicles (oldest removed).
    const maxVehicles = 90;
    if (this.vehicles.size > maxVehicles) {
      const oldest = [...this.vehicles.values()].sort((a, b) => a.lastSeenTs - b.lastSeenTs)[0];
      if (oldest) this.vehicles.delete(oldest.id);
    }

    this.renderStatic();
    const fitPoly = this.side === "baseline" ? this.heroRemainingPath() : poly;
    this.fitViewToRoute(fitPoly);
    this.kickAnim();
  }

  /** Tight camera frame around the active route so Step feels like Ola/Uber navigation, not a whole-city mess. */
  private fitViewToRoute(poly: [number, number][]) {
    if (!poly.length) return;
    let minLng = poly[0][0];
    let maxLng = poly[0][0];
    let minLat = poly[0][1];
    let maxLat = poly[0][1];
    for (const [lng, lat] of poly) {
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
    }
    const padLng = Math.max(0.002, (maxLng - minLng) * 0.12);
    const padLat = Math.max(0.002, (maxLat - minLat) * 0.12);
    const sw: [number, number] = [minLng - padLng, minLat - padLat];
    const ne: [number, number] = [maxLng + padLng, maxLat + padLat];
    const isBaseline = this.side === "baseline";
    try {
      this.map.fitBounds([sw, ne] as any, {
        padding: isBaseline ? { top: 36, bottom: 36, left: 36, right: 36 } : { top: 56, bottom: 56, left: 56, right: 56 },
        duration: isBaseline ? 520 : 700,
        maxZoom: isBaseline ? 16.6 : 15.2,
        minZoom: isBaseline ? 13.2 : 11.2,
      });
    } catch {
      // ignore map timing errors
    }
  }

  private kickAnim() {
    if (this.raf != null) cancelAnimationFrame(this.raf);
    this.lastTs = null;
    const tick = (ts: number) => {
      if (this.lastTs == null) this.lastTs = ts;
      const dt = Math.max(0, Math.min(0.05, (ts - this.lastTs) / 1000));
      this.lastTs = ts;

      // Simple speed model (can be upgraded to per-road-type later).
      const baseSpeedMps = this.side === "oracle" ? 34.0 : 30.0; // faster demo motion

      const now = performance.now();
      // TTL: fade out old vehicles so the map doesn't become messy.
      const ttlMs = 120_000;
      const lingerAfterArriveMs = 25_000;
      for (const [id, v] of this.vehicles) {
        if (v.arrivedTs != null) {
          if (now - v.arrivedTs > lingerAfterArriveMs) {
            this.vehicles.delete(id);
            continue;
          }
        } else if (now - v.lastSeenTs > ttlMs) {
          this.vehicles.delete(id);
          continue;
        }
        const base = v.kind === "bike" ? baseSpeedMps * 0.92 : baseSpeedMps;
        const m = this.multAt(v);
        const targetSpeed = base / Math.max(0.35, Math.min(1.15, m));
        v.speedMps = v.speedMps == null ? targetSpeed : v.speedMps * 0.84 + targetSpeed * 0.16;
        const nextProg = Math.min(v.totalM, v.progM + (v.speedMps || targetSpeed) * dt);
        v.progM = nextProg;
        // Keep active trips alive; don't delete mid-route just because they were spawned earlier.
        if (v.progM < v.totalM - 1e-3) {
          v.lastSeenTs = now;
        } else if (v.arrivedTs == null) {
          v.arrivedTs = now;
        }
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

  private nearLngLat(a: [number, number], b: [number, number]) {
    return Math.abs(a[0] - b[0]) < 1e-9 && Math.abs(a[1] - b[1]) < 1e-9;
  }

  /** Split active polyline at hero progress for Uber-style “done vs ahead” styling. */
  private splitRouteAtProgress(
    route: [number, number][],
    cumM: number[],
    totalM: number,
    progM: number
  ): { traveled: [number, number][]; remaining: [number, number][] } {
    if (route.length < 2) return { traveled: [...route], remaining: [...route] };
    const m = Math.max(0, Math.min(progM, totalM));
    const cut = this.pointAtOn(route, cumM, totalM, m);
    if (!cut) return { traveled: [[route[0][0], route[0][1]]], remaining: [...route] };
    const pos = cut.pos;
    let i = 1;
    while (i < cumM.length && cumM[i] < m) i++;

    const traveled: [number, number][] = [];
    for (let j = 0; j < i; j++) traveled.push([route[j][0], route[j][1]]);
    const lastT = traveled[traveled.length - 1];
    if (!lastT || !this.nearLngLat(lastT, pos)) traveled.push([pos[0], pos[1]]);

    const remaining: [number, number][] = [];
    if (!this.nearLngLat(pos, route[i - 1])) remaining.push([pos[0], pos[1]]);
    for (let j = i; j < route.length; j++) {
      if (j === i && this.nearLngLat(pos, route[j])) continue;
      remaining.push([route[j][0], route[j][1]]);
    }
    if (remaining.length < 2) {
      const end = route[route.length - 1];
      remaining.push([end[0], end[1]]);
    }
    return {
      traveled: simplifyPathLngLat(traveled, 220),
      remaining: simplifyPathLngLat(remaining, 360),
    };
  }

  /** Route is updated every animation frame; roads stay in `staticLayers`. */
  private makeRouteProgressLayers(): PathLayer[] {
    if (!this.activeRoute.length) return [];
    const hero = this.heroVehicleId ? this.vehicles.get(this.heroVehicleId) : undefined;
    let traveled: [number, number][] = [];
    let remaining: [number, number][] = [];
    if (hero && hero.route.length >= 2 && hero.cumM.length === hero.route.length && hero.totalM > 1e-6) {
      const sp = this.splitRouteAtProgress(hero.route, hero.cumM, hero.totalM, hero.progM);
      traveled = sp.traveled;
      remaining = sp.remaining;
    } else {
      remaining = simplifyPathLngLat(this.activeRoute, 360);
    }

    const traveledCore: [number, number, number, number] =
      this.side === "oracle" ? [60, 160, 175, 170] : [200, 200, 220, 150];
    const routeCore = this.side === "oracle" ? [55, 240, 255, 255] : [240, 244, 255, 250];
    const routeCasing = [8, 10, 18, 235];
    const routeHalo = this.side === "oracle" ? [35, 200, 230, 55] : [200, 210, 245, 45];

    const layers: PathLayer[] = [];
    if (traveled.length >= 2) {
      layers.push(
        new PathLayer({
          id: `route-traveled-${this.side}`,
          data: [{ path: traveled }],
          getPath: (d: any) => d.path,
          getColor: traveledCore as any,
          getWidth: 2.2,
          widthUnits: "pixels",
          capRounded: true,
          jointRounded: true,
          pickable: false,
          parameters: { depthTest: false },
        })
      );
    }
    if (remaining.length >= 2) {
      layers.push(
        new PathLayer({
          id: `route-halo-${this.side}`,
          data: [{ path: remaining }],
          getPath: (d: any) => d.path,
          getColor: routeHalo as any,
          getWidth: 7,
          widthUnits: "pixels",
          capRounded: false,
          jointRounded: false,
          pickable: false,
          parameters: { depthTest: false },
        }),
        new PathLayer({
          id: `route-casing-${this.side}`,
          data: [{ path: remaining }],
          getPath: (d: any) => d.path,
          getColor: routeCasing as any,
          getWidth: 5,
          widthUnits: "pixels",
          capRounded: false,
          jointRounded: false,
          pickable: false,
          parameters: { depthTest: false },
        }),
        new PathLayer({
          id: `route-core-${this.side}`,
          data: [{ path: remaining }],
          getPath: (d: any) => d.path,
          getColor: routeCore as any,
          getWidth: 2.75,
          widthUnits: "pixels",
          capRounded: true,
          jointRounded: true,
          pickable: false,
          parameters: { depthTest: false },
        })
      );
    }
    return layers;
  }

  private renderVehicleOnly() {
    const vehicleDotLayer = this.makeVehicleDotLayer();
    const stationLayer = this.makeStationIconLayer();
    const routeLayers = this.makeRouteProgressLayers();
    this.overlay.setProps({
      layers: [...this.staticLayers, ...routeLayers, stationLayer, vehicleDotLayer],
    });
  }

  private renderStatic() {
    const roads: { path: [number, number][]; highway: string }[] = (this as any)._roads || [];
    const roadColor = (hw: string) => {
      if (hw === "motorway" || hw === "trunk" || hw === "primary") return [230, 235, 255, 55] as any;
      if (hw === "secondary") return [200, 210, 245, 28] as any;
      return [160, 170, 210, 16] as any;
    };
    const roadWidth = (hw: string) => (hw === "primary" ? 2.4 : hw === "secondary" ? 1.8 : 1.2);

    const roadLayer = new PathLayer({
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
    });
    this.staticLayers = [roadLayer];
    this.renderVehicleOnly();
  }

  private makeVehicleDotLayer() {
    return new ScatterplotLayer({
      id: `vehicle-dots-${this.side}`,
      data: [...this.vehicles.values()],
      getPosition: (d: any) => d.pos,
      radiusUnits: "pixels",
      getRadius: (d: any) => (d.kind === "bike" ? 6.5 : 8.0),
      getFillColor: (d: any) => d.color,
      getLineColor: [0, 0, 0, 190] as any,
      lineWidthUnits: "pixels",
      lineWidthMinPixels: 2,
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

