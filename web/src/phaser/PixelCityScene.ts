import Phaser from "phaser";
import type { DemoMode, DemoStepResponse, StationNode } from "../evgrid/api";
import { demoStep } from "../evgrid/api";
import { computeBBox, makeProjector } from "../evgrid/project";

/** One fetch + parse for all Phaser maps (baseline + oracle) — avoids duplicate work on “New”. */
let roadsGeojsonPromise: Promise<any> | null = null;
function loadRoadsGeojsonOnce(): Promise<any> {
  if (!roadsGeojsonPromise) {
    roadsGeojsonPromise = (async () => {
      const r = await fetch("/maps/bangalore_roads_demo.geojson");
      if (!r.ok) throw new Error(`roads fetch failed: ${r.status}`);
      return await r.json();
    })();
  }
  return roadsGeojsonPromise;
}

type UIRefs = {
  statusEl: HTMLPreElement;
  eventEl: HTMLPreElement;
  modeEl: HTMLSelectElement;
  followEl: HTMLInputElement;
  loraEl: HTMLInputElement;
};

export class PixelCityScene extends Phaser.Scene {
  private ui!: UIRefs;
  private sessionId: string | null = null;
  private nodes: StationNode[] = [];
  private projector: ((lat: number, lng: number) => { x: number; y: number }) | null = null;

  private stationsLayer!: Phaser.GameObjects.Container;
  private fxLayer!: Phaser.GameObjects.Container;
  private roadsLayer!: Phaser.GameObjects.Container;
  private roadsGraphics: Phaser.GameObjects.Graphics | null = null;
  private roadsRtMajor: Phaser.GameObjects.RenderTexture | null = null;
  private roadsRtMinor: Phaser.GameObjects.RenderTexture | null = null;

  private stationMarks = new Map<
    string,
    { glow: Phaser.GameObjects.Arc; ring: Phaser.GameObjects.Arc; base: Phaser.GameObjects.Arc }
  >();

  private ev!: Phaser.GameObjects.Sprite;
  private evShadow!: Phaser.GameObjects.Ellipse;

  private camMain!: Phaser.Cameras.Scene2D.Camera;
  private camMini!: Phaser.Cameras.Scene2D.Camera;

  private side: "baseline" | "oracle" = "oracle";
  private flickerRect: Phaser.GameObjects.Rectangle | null = null;

  constructor() {
    super("PixelCityScene");
  }

  init(data: { ui: UIRefs }) {
    this.ui = data.ui;
  }

  preload() {
    // Create a tiny pixel EV sprite procedurally (so repo has no binary assets yet).
    const g = this.make.graphics({ x: 0, y: 0 });
    g.clear();
    g.fillStyle(0x1b1f2e, 1);
    g.fillRect(0, 0, 16, 16);
    g.fillStyle(0x61ffb1, 1);
    g.fillRect(3, 4, 10, 8);
    g.fillStyle(0x0b0d14, 1);
    g.fillRect(4, 6, 3, 2);
    g.fillRect(9, 6, 3, 2);
    g.fillStyle(0xffffff, 1);
    g.fillRect(12, 5, 1, 2);
    g.generateTexture("ev", 16, 16);
    g.destroy();
  }

  create() {
    this.camMain = this.cameras.main;

    const w = this.scale.width;
    const h = this.scale.height;
    this.camMini = this.cameras.add(w - 240, 18, 220, 160);
    this.camMini.setBackgroundColor(0x0b0d14);
    this.camMini.setZoom(0.35);

    // Containers so minimap can render everything too.
    this.roadsLayer = this.add.container(0, 0);
    this.stationsLayer = this.add.container(0, 0);
    this.fxLayer = this.add.container(0, 0);

    // Pixel ground (simple tiled vibe)
    const bg = this.add.graphics();
    bg.fillStyle(0x070911, 1);
    bg.fillRect(0, 0, w, h);
    // subtle grid “tile” pattern
    bg.lineStyle(1, 0x131a33, 0.25);
    for (let x = 0; x <= w; x += 24) bg.lineBetween(x, 0, x, h);
    for (let y = 0; y <= h; y += 24) bg.lineBetween(0, y, w, y);
    bg.setDepth(-10);

    // Subtle vignette (readability): darken edges/top/bottom without noisy gradients.
    const vig = this.add.graphics();
    vig.fillStyle(0x000000, 0.22);
    vig.fillRect(0, 0, w, 70);
    vig.fillRect(0, h - 70, w, 70);
    vig.fillStyle(0x000000, 0.18);
    vig.fillRect(0, 0, 70, h);
    vig.fillRect(w - 70, 0, 70, h);
    vig.setDepth(-9);

    // EV sprite
    this.evShadow = this.add.ellipse(w / 2, h / 2 + 10, 18, 7, 0x000000, 0.35);
    this.evShadow.setDepth(10);
    this.ev = this.add.sprite(w / 2, h / 2, "ev");
    this.ev.setScale(2.0);
    this.ev.setDepth(11);
    this.ev.setOrigin(0.5, 0.5);

    this.camMain.setRoundPixels(true);
    this.camMini.setRoundPixels(true);

    // Baseline gets CRT flicker + micro-shake (to sell chaos vs control).
    this.flickerRect = this.add.rectangle(w / 2, h / 2, w, h, 0x000000, 0.0);
    this.flickerRect.setDepth(999);

    this.time.addEvent({
      loop: true,
      delay: 80,
      callback: () => {
        if (this.side !== "baseline" || !this.flickerRect) return;
        const a = 0.02 + Math.random() * 0.08;
        this.flickerRect.setAlpha(a);
        if (Math.random() < 0.20) {
          this.camMain.shake(40, 0.002);
        }
      },
    });

    this.ui.statusEl.textContent = "Click New to start.";
  }

  setSide(side: "baseline" | "oracle") {
    this.side = side;
  }

  async bindSession(sessionId: string, station_nodes: StationNode[]) {
    this.sessionId = sessionId;
    this.nodes = station_nodes;
    const bbox = computeBBox(this.nodes);
    this.projector = makeProjector(bbox, this.scale.width, this.scale.height, 70);
    await this.loadAndDrawRoads();
    this.drawStations();
    this.snapCameraToCity();
  }

  private async loadAndDrawRoads() {
    this.roadsLayer.removeAll(true);
    this.roadsGraphics?.destroy();
    this.roadsGraphics = null;
    this.roadsRtMajor?.destroy();
    this.roadsRtMajor = null;
    this.roadsRtMinor?.destroy();
    this.roadsRtMinor = null;
    if (!this.projector) return;

    try {
      // IMPORTANT: do not load the full-city raw dump in the browser.
      // Use a pruned demo GeoJSON (station-bounded + simplified) generated by:
      //   python tools/prune_osm_geojson.py
      const gj = await loadRoadsGeojsonOnce();
      const feats = Array.isArray(gj?.features) ? gj.features : [];

      // Game-studio readability pattern:
      // - Draw roads into an offscreen buffer at higher res, then downscale (cheap “AA” + pixel cohesion)
      // - Separate passes: wide dark underlay → mid outline → bright core (Google-ish hierarchy)
      const w = this.scale.width;
      const h = this.scale.height;
      const scale = 2; // internal supersample factor
      const rw = Math.max(1, Math.floor(w * scale));
      const rh = Math.max(1, Math.floor(h * scale));

      const buildRt = (subset: any[]) => {
        const rt = this.add.renderTexture(0, 0, rw, rh);
        rt.setOrigin(0, 0);
        rt.setDepth(-1);
        rt.clear();

        const g = this.make.graphics({ x: 0, y: 0 });
        g.setScale(scale, scale);

        const stroke = (coords: any, color: number, width: number, alpha: number) => {
          if (!Array.isArray(coords) || coords.length < 2) return;
          const pts = coords
            .map((c: [number, number]) => this.projector!(c[1], c[0])) // geojson is [lon,lat]
            .map((p: any) => new Phaser.Math.Vector2(p.x, p.y));
          if (pts.length < 2) return;
          g.lineStyle(width, color, alpha);
          g.beginPath();
          g.moveTo(pts[0].x, pts[0].y);
          for (let i = 1; i < pts.length; i++) g.lineTo(pts[i].x, pts[i].y);
          g.strokePath();
        };

        const drawWayStyled = (coords: any, hw: string) => {
          if (hw === "motorway" || hw === "trunk" || hw === "primary") {
            stroke(coords, 0x000000, 14, 0.22);
            stroke(coords, 0x0b1022, 10, 0.55);
            stroke(coords, 0xf3f5ff, 6, 0.55);
          } else if (hw === "secondary") {
            stroke(coords, 0x000000, 12, 0.18);
            stroke(coords, 0x0b1022, 8, 0.45);
            stroke(coords, 0xe6ebfb, 4, 0.38);
          } else if (hw === "tertiary") {
            stroke(coords, 0x000000, 9, 0.12);
            stroke(coords, 0x0b1022, 6, 0.30);
            stroke(coords, 0xd6def5, 3, 0.22);
          } else {
            stroke(coords, 0x000000, 7, 0.10);
            stroke(coords, 0x0b1022, 5, 0.22);
            stroke(coords, 0xc7d0ea, 2, 0.14);
          }
        };

        // Painter’s algorithm inside subset: minor-ish first, arterials last.
        const minor: any[] = [];
        const major: any[] = [];
        for (const f of subset) {
          const hw = String(f?.properties?.highway || "");
          if (f?.geometry?.type !== "LineString") continue;
          if (hw === "motorway" || hw === "trunk" || hw === "primary") major.push(f);
          else minor.push(f);
        }
        for (const f of minor) drawWayStyled(f.geometry.coordinates, String(f?.properties?.highway || ""));
        for (const f of major) drawWayStyled(f.geometry.coordinates, String(f?.properties?.highway || ""));

        rt.draw(g, 0, 0, 1);
        g.destroy();

        rt.setPosition(0, 0);
        rt.setScale(1 / scale, 1 / scale);
        rt.setDisplaySize(w, h);
        return rt;
      };

      // Zoom-style LOD: keep arterials always crisp; fade “secondary mesh” until follow/zoom.
      const majorFeats: any[] = [];
      const minorFeats: any[] = [];
      for (const f of feats) {
        const hw = String(f?.properties?.highway || "");
        if (f?.geometry?.type !== "LineString") continue;
        if (hw === "motorway" || hw === "trunk" || hw === "primary") majorFeats.push(f);
        else minorFeats.push(f);
      }

      this.roadsRtMinor = buildRt(minorFeats);
      this.roadsRtMajor = buildRt(majorFeats);
      this.roadsRtMajor.setAlpha(0.96);
      this.updateRoadLod();

      this.roadsLayer.add(this.roadsRtMinor);
      this.roadsLayer.add(this.roadsRtMajor);
      this.roadsGraphics = null;
    } catch {
      // If GeoJSON isn’t present yet, we’ll keep the v0 station-graph “roads” in drawStations().
    }
  }

  private updateRoadLod() {
    const follow = this.ui.followEl.checked;
    const zoom = this.camMain.zoom;
    // City view: keep secondary roads subtle. Follow view: reveal more detail.
    const minorAlpha = Phaser.Math.Clamp(0.22 + (follow ? 0.35 : 0) + (zoom > 1.2 ? 0.25 : 0), 0.12, 0.85);
    this.roadsRtMinor?.setAlpha(minorAlpha);
  }

  private drawStations() {
    this.stationsLayer.removeAll(true);
    this.stationMarks.clear();
    if (!this.projector) return;

    // Roads fallback (v0) only if OSM layer didn’t load
    if (!this.roadsGraphics) {
      const road = this.add.graphics();
      road.lineStyle(6, 0x0d1326, 0.9);
      for (let i = 0; i < this.nodes.length; i++) {
        const a = this.nodes[i];
        const pa = this.projector(a.lat, a.lng);
        for (let j = i + 1; j < Math.min(this.nodes.length, i + 4); j++) {
          const b = this.nodes[j];
          const pb = this.projector(b.lat, b.lng);
          road.lineBetween(pa.x, pa.y, pb.x, pb.y);
        }
      }
      road.lineStyle(3, 0xbcc6e5, 0.10);
      for (let i = 0; i < this.nodes.length; i++) {
        const a = this.nodes[i];
        const pa = this.projector(a.lat, a.lng);
        for (let j = i + 1; j < Math.min(this.nodes.length, i + 4); j++) {
          const b = this.nodes[j];
          const pb = this.projector(b.lat, b.lng);
          road.lineBetween(pa.x, pa.y, pb.x, pb.y);
        }
      }
      road.setDepth(0);
      this.stationsLayer.add(road);
    }

    for (const n of this.nodes) {
      const p = this.projector(n.lat, n.lng);
      const base = this.add.circle(p.x, p.y, 10, 0x1b243a, 1);
      const glow = this.add.circle(p.x, p.y, 18, 0x3cff9a, 0.08);
      const ring = this.add.circle(p.x, p.y, 14, 0x5a78ff, 0.08);
      const label = this.add.text(p.x + 14, p.y - 10, n.station_id, {
        fontFamily: "monospace",
        fontSize: "10px",
        color: "#b7c6ff",
      });
      label.setAlpha(0.85);
      label.setShadow(0, 0, "#000", 4);

      this.stationsLayer.add([glow, ring, base, label]);
      this.stationMarks.set(n.station_id, { glow, ring, base });
    }
  }

  private snapCameraToCity() {
    // Frame all stations (simple: center on bbox in screen space).
    if (!this.projector) return;
    const xs: number[] = [];
    const ys: number[] = [];
    for (const n of this.nodes) {
      const p = this.projector(n.lat, n.lng);
      xs.push(p.x);
      ys.push(p.y);
    }
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
    const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    this.camMain.centerOn(cx, cy);
    this.camMain.setZoom(1.0);

    this.camMini.centerOn(cx, cy);
    this.camMini.setZoom(0.45);
    this.updateRoadLod();
  }

  async stepOnce() {
    if (!this.sessionId) throw new Error("No session. Click New first.");

    const mode = this.ui.modeEl.value as DemoMode;
    const oracle_lora_repo = this.ui.loraEl.value || "";

    const res: DemoStepResponse = await demoStep({ session_id: this.sessionId, mode, oracle_lora_repo });
    this.applyStationStress(res.obs?.state);
    await this.playEvent(res.event);
  }

  private applyStationStress(st: any) {
    if (!st?.stations) return;
    for (const s of st.stations as any[]) {
      const m = this.stationMarks.get(String(s.station_id));
      if (!m) continue;
      const load = s.occupied_slots / Math.max(1, s.total_slots);
      const qn = Math.min(5, Number(s.queue_length || 0)) / 5;
      const stress = Phaser.Math.Clamp(0.55 * load + 0.45 * qn, 0, 1);
      m.glow.setAlpha(0.05 + stress * 0.55);
      m.ring.setAlpha(0.05 + stress * 0.45);
      const danger = stress > 0.72;
      // Arc doesn't support tint the same way sprites do; adjust fill color directly.
      m.glow.setFillStyle(danger ? 0xff5a8a : 0x3cff9a, m.glow.alpha);
    }
  }

  private async playEvent(event: any) {
    if (!this.projector) return;
    if (!event || event.type !== "route" || !Array.isArray(event.polyline)) {
      // Idle bob animation
      this.tweens.add({
        targets: [this.ev, this.evShadow],
        y: "-=2",
        duration: 180,
        yoyo: true,
        ease: "Sine.easeInOut",
      });
      return;
    }

    const pts = event.polyline
      .map((ll: [number, number]) => this.projector!(ll[0], ll[1]))
      .map((p: any) => new Phaser.Math.Vector2(p.x, p.y));
    if (pts.length < 2) return;

    // GHOST PATH (Oracle only): dashed purple dream path appears first.
    const ghost = this.add.graphics();
    ghost.setDepth(4);
    this.fxLayer.add(ghost);
    if (this.side === "oracle") {
      ghost.lineStyle(4, 0xb85cff, 0.45);
      this._strokeDashed(ghost, pts, 16, 12);
      this.time.delayedCall(900, () => ghost.destroy());
    } else {
      ghost.destroy();
    }

    // ACTUAL PATH: solid glow (oracle brighter, baseline dimmer)
    const g = this.add.graphics();
    const core = this.side === "oracle" ? 0x35ffb8 : 0x6d7aa6;
    const alpha = this.side === "oracle" ? 0.26 : 0.12;
    g.lineStyle(6, core, alpha);
    g.beginPath();
    g.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) g.lineTo(pts[i].x, pts[i].y);
    g.strokePath();
    g.setDepth(5);
    this.fxLayer.add(g);
    this.time.delayedCall(1100, () => g.destroy());

    // Start at first point
    this.ev.setPosition(pts[0].x, pts[0].y);
    this.evShadow.setPosition(pts[0].x, pts[0].y + 14);

    // Follow-cam toggle
    if (this.ui.followEl.checked) {
      this.camMain.startFollow(this.ev, true, 0.12, 0.12);
      this.camMain.setZoom(1.8);
    } else {
      this.camMain.stopFollow();
      this.snapCameraToCity();
    }
    this.updateRoadLod();

    // Animate along polyline (segment tweens)
    const segDur = 900 / (pts.length - 1);
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1];
      const b = pts[i];
      const ang = Phaser.Math.RadToDeg(Phaser.Math.Angle.Between(a.x, a.y, b.x, b.y));
      this.ev.setRotation(Phaser.Math.DegToRad(ang));

      await this.tweenTo(b.x, b.y, segDur);
    }
  }

  private tweenTo(x: number, y: number, duration: number) {
    return new Promise<void>((resolve) => {
      this.tweens.add({
        targets: this.ev,
        x,
        y,
        duration,
        ease: "Sine.easeInOut",
        onUpdate: () => {
          this.evShadow.setPosition(this.ev.x, this.ev.y + 14);
        },
        onComplete: () => resolve(),
      });
    });
  }

  private _strokeDashed(g: Phaser.GameObjects.Graphics, pts: Phaser.Math.Vector2[], dash: number, gap: number) {
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1];
      const b = pts[i];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len = Math.hypot(dx, dy);
      if (len < 1) continue;
      const ux = dx / len;
      const uy = dy / len;
      let t = 0;
      while (t < len) {
        const t2 = Math.min(len, t + dash);
        g.beginPath();
        g.moveTo(a.x + ux * t, a.y + uy * t);
        g.lineTo(a.x + ux * t2, a.y + uy * t2);
        g.strokePath();
        t += dash + gap;
      }
    }
  }

  // For the split-screen command center: drive animation externally.
  async playExternalEvent(event: any) {
    await this.playEvent(event);
  }
}

