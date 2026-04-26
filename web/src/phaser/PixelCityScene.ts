import Phaser from "phaser";
import type { DemoMode, DemoStepResponse, StationNode } from "../evgrid/api";
import { demoStep } from "../evgrid/api";
import { computeBBox, makeProjector } from "../evgrid/project";
import { staticAssetUrl } from "../paths";

/** One fetch + parse for all Phaser maps (baseline + oracle) — avoids duplicate work on “New”. */
let roadsGeojsonPromise: Promise<any> | null = null;

async function withTimeout<T>(p: Promise<T>, ms: number): Promise<T> {
  let timeoutId: number | null = null;
  try {
    return await Promise.race([
      p,
      new Promise<T>((_, reject) => {
        timeoutId = window.setTimeout(() => reject(new Error(`timeout after ${ms}ms`)), ms);
      }),
    ]);
  } finally {
    if (timeoutId != null) window.clearTimeout(timeoutId);
  }
}

function fetchJsonWithTimeout(url: string, ms: number): Promise<any> {
  const ctl = new AbortController();
  const t = window.setTimeout(() => ctl.abort(), ms);
  return fetch(url, { signal: ctl.signal })
    .then(async (r) => {
      if (!r.ok) throw new Error(`fetch failed: ${r.status}`);
      return await r.json();
    })
    .finally(() => window.clearTimeout(t));
}

function loadRoadsGeojsonOnce(): Promise<any> {
  if (!roadsGeojsonPromise) {
    roadsGeojsonPromise = (async () => {
      const url = staticAssetUrl("maps/bangalore_roads_demo.geojson");
      // On HF Spaces cold-start, static assets can be slow. Never let this hang forever.
      return await fetchJsonWithTimeout(url, 12_000);
    })();

    // If it fails, clear the cached promise so a later retry can succeed.
    roadsGeojsonPromise = roadsGeojsonPromise.catch((e) => {
      roadsGeojsonPromise = null;
      throw e;
    });
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

  private stationUi = new Map<string, { root: Phaser.GameObjects.Container; label: Phaser.GameObjects.Text }>();
  private hoverCard: Phaser.GameObjects.Container | null = null;
  private hoverBg: Phaser.GameObjects.Rectangle | null = null;
  private hoverText: Phaser.GameObjects.Text | null = null;

  private ev!: Phaser.GameObjects.Sprite;
  private evShadow!: Phaser.GameObjects.Ellipse;

  private camMain!: Phaser.Cameras.Scene2D.Camera;
  private camMini!: Phaser.Cameras.Scene2D.Camera;

  private side: "baseline" | "oracle" = "oracle";
  private flickerRect: Phaser.GameObjects.Rectangle | null = null;
  private energyDots: Phaser.GameObjects.Image[] = [];
  private reactor: Phaser.GameObjects.Container | null = null;
  private roadsFallbackEdges: Array<{ a: { x: number; y: number }; b: { x: number; y: number } }> = [];

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

    // Pixel station sprite
    {
      const s = this.make.graphics({ x: 0, y: 0 });
      s.clear();
      s.fillStyle(0x0b0d14, 1);
      s.fillRect(0, 0, 16, 16);
      s.fillStyle(0x1b243a, 1);
      s.fillRect(2, 2, 12, 12);
      s.fillStyle(0x35ffb8, 1);
      s.fillRect(6, 3, 4, 3);
      s.fillStyle(0xe8ecff, 1);
      s.fillRect(5, 7, 6, 6);
      s.fillStyle(0x0b0d14, 1);
      s.fillRect(6, 8, 4, 4);
      s.generateTexture("station", 16, 16);
      s.destroy();
    }

    // Energy dot sprite
    {
      const e = this.make.graphics({ x: 0, y: 0 });
      e.clear();
      e.fillStyle(0x000000, 0);
      e.fillRect(0, 0, 8, 8);
      e.fillStyle(0x61ffb1, 1);
      e.fillRect(3, 0, 2, 8);
      e.fillStyle(0x61ffb1, 1);
      e.fillRect(0, 3, 8, 2);
      e.generateTexture("energyDot", 8, 8);
      e.destroy();
    }
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

    // Hover card (micro-interaction)
    this.hoverBg = this.add.rectangle(0, 0, 10, 10, 0x070911, 0.82).setOrigin(0, 0);
    this.hoverBg.setStrokeStyle(1, 0x5a78ff, 0.35);
    this.hoverText = this.add.text(0, 0, "", {
      fontFamily: "monospace",
      fontSize: "12px",
      color: "#e8ecff",
    });
    this.hoverText.setShadow(0, 0, "#000", 6);
    this.hoverCard = this.add.container(0, 0, [this.hoverBg, this.hoverText]);
    this.hoverCard.setDepth(9999);
    this.hoverCard.setVisible(false);

    // Idle “alive” motion on load even before sessions
    this.time.addEvent({
      loop: true,
      delay: 900,
      callback: () => {
        if (!this.reactor) return;
        // Soft heartbeat on the Bangalore hub
        const core = this.reactor.getByName("reactorCore") as Phaser.GameObjects.Arc | null;
        if (!core) return;
        this.tweens.add({
          targets: core,
          scale: { from: 1.0, to: 1.08 },
          yoyo: true,
          duration: 420,
          ease: "Sine.easeInOut",
        });
      },
    });
  }

  setSide(side: "baseline" | "oracle") {
    this.side = side;
  }

  async bindSession(sessionId: string, station_nodes: StationNode[]) {
    this.sessionId = sessionId;
    this.nodes = station_nodes;
    const bbox = computeBBox(this.nodes);
    this.projector = makeProjector(bbox, this.scale.width, this.scale.height, 70);
    this.drawStations();
    this.snapCameraToCity();
    this.ensureReactorHub();
    this.startAmbientEnergy();

    // Roads are optional; do not block session readiness on them.
    void (async () => {
      try {
        await withTimeout(this.loadAndDrawRoads(), 15_000);
        // Re-draw stations on top once roads are present.
        this.drawStations();
      } catch {
        // Fallback roads layer is already handled by drawStations(); ignore.
      }
    })();
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
    this.stationUi.clear();
    this.roadsFallbackEdges = [];
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
          this.roadsFallbackEdges.push({ a: { x: pa.x, y: pa.y }, b: { x: pb.x, y: pb.y } });
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
      const spr = this.add.sprite(p.x, p.y, "station");
      spr.setScale(1.6);
      spr.setDepth(2);
      spr.setInteractive({ useHandCursor: true });

      const label = this.add.text(p.x + 14, p.y - 10, n.station_id, {
        fontFamily: "monospace",
        fontSize: "10px",
        color: "#b7c6ff",
      });
      label.setAlpha(0.85);
      label.setShadow(0, 0, "#000", 4);

      // Subtle idle pulse per station (makes map “alive” immediately)
      this.tweens.add({
        targets: [glow, ring],
        alpha: { from: 0.05, to: 0.12 },
        duration: 1400 + Math.random() * 900,
        yoyo: true,
        repeat: -1,
        ease: "Sine.easeInOut",
      });

      spr.on("pointerover", () => {
        spr.setScale(1.9);
        const stype = String((n as any).station_type || "charger");
        this.showHover(`Station: ${n.station_id}\nSlots: ${n.total_slots}\nType: ${stype}`, p.x, p.y);
      });
      spr.on("pointerout", () => {
        spr.setScale(1.6);
        this.hideHover();
      });
      spr.on("pointerdown", () => {
        // Satisfying click feedback
        this.spawnBurst(p.x, p.y, this.side === "oracle" ? 0xb85cff : 0x35ffb8);
      });

      const root = this.add.container(0, 0, [glow, ring, base, spr, label]);
      this.stationsLayer.add(root);
      this.stationMarks.set(n.station_id, { glow, ring, base });
      this.stationUi.set(n.station_id, { root, label });
    }
  }

  private ensureReactorHub() {
    if (!this.projector || this.nodes.length === 0) return;
    // center of bbox in screen space
    const xs = this.nodes.map((n) => this.projector!(n.lat, n.lng).x);
    const ys = this.nodes.map((n) => this.projector!(n.lat, n.lng).y);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
    const cy = (Math.min(...ys) + Math.max(...ys)) / 2;

    this.reactor?.destroy(true);
    const outer = this.add.circle(cx, cy, 34, 0x5a78ff, 0.06);
    const mid = this.add.circle(cx, cy, 22, 0xb85cff, 0.10);
    const core = this.add.circle(cx, cy, 12, 0x35ffb8, 0.35);
    core.setName("reactorCore");
    const label = this.add.text(cx, cy + 42, "BANGALORE HUB", {
      fontFamily: "monospace",
      fontSize: "12px",
      color: "#e8ecff",
    });
    label.setOrigin(0.5, 0);
    label.setAlpha(0.9);
    label.setShadow(0, 0, "#000", 6);

    this.reactor = this.add.container(0, 0, [outer, mid, core, label]);
    this.reactor.setDepth(1);
    this.fxLayer.add(this.reactor);

    // Continuous reactor breathing glow (immediate focal point)
    this.tweens.add({
      targets: [outer, mid],
      alpha: { from: 0.06, to: 0.18 },
      duration: 1200,
      yoyo: true,
      repeat: -1,
      ease: "Sine.easeInOut",
    });
  }

  private startAmbientEnergy() {
    // Clear old dots
    for (const d of this.energyDots) d.destroy();
    this.energyDots = [];
    if (this.roadsFallbackEdges.length === 0) return;

    // Spawn a few “energy dots” that flow along edges (directional motion)
    const count = 10;
    for (let i = 0; i < count; i++) {
      const e = this.roadsFallbackEdges[Math.floor(Math.random() * this.roadsFallbackEdges.length)];
      const dot = this.add.image(e.a.x, e.a.y, "energyDot");
      dot.setScale(1.2);
      dot.setDepth(3);
      dot.setAlpha(0.8);
      this.fxLayer.add(dot);
      this.energyDots.push(dot);
      this.loopDot(dot, e);
    }
  }

  private loopDot(dot: Phaser.GameObjects.Image, edge: { a: { x: number; y: number }; b: { x: number; y: number } }) {
    const from = Math.random() < 0.5 ? edge.a : edge.b;
    const to = from === edge.a ? edge.b : edge.a;
    dot.setPosition(from.x, from.y);
    this.tweens.add({
      targets: dot,
      x: to.x,
      y: to.y,
      duration: 1400 + Math.random() * 1100,
      ease: "Sine.easeInOut",
      onComplete: () => {
        // pick a new edge to keep it feeling alive
        const e = this.roadsFallbackEdges[Math.floor(Math.random() * this.roadsFallbackEdges.length)];
        this.loopDot(dot, e);
      },
    });
  }

  private showHover(text: string, x: number, y: number) {
    if (!this.hoverCard || !this.hoverBg || !this.hoverText) return;
    this.hoverText.setText(text);
    const pad = 10;
    const w = Math.min(320, this.hoverText.width + pad * 2);
    const h = this.hoverText.height + pad * 2;
    this.hoverBg.setSize(w, h);
    this.hoverText.setPosition(pad, pad);

    const px = Phaser.Math.Clamp(x + 14, 10, this.scale.width - w - 10);
    const py = Phaser.Math.Clamp(y - h - 12, 10, this.scale.height - h - 10);
    this.hoverCard.setPosition(px, py);
    this.hoverCard.setVisible(true);
    this.hoverCard.setAlpha(0);
    this.tweens.add({ targets: this.hoverCard, alpha: 1, duration: 120, ease: "Sine.easeOut" });
  }

  private hideHover() {
    if (!this.hoverCard) return;
    this.hoverCard.setVisible(false);
  }

  private spawnBurst(x: number, y: number, color: number) {
    const g = this.add.graphics();
    g.setDepth(50);
    this.fxLayer.add(g);
    const rays = 8;
    const r1 = 6;
    const r2 = 20;
    g.lineStyle(3, color, 0.8);
    for (let i = 0; i < rays; i++) {
      const a = (Math.PI * 2 * i) / rays;
      g.beginPath();
      g.moveTo(x + Math.cos(a) * r1, y + Math.sin(a) * r1);
      g.lineTo(x + Math.cos(a) * r2, y + Math.sin(a) * r2);
      g.strokePath();
    }
    this.tweens.add({
      targets: g,
      alpha: { from: 1, to: 0 },
      duration: 360,
      ease: "Sine.easeOut",
      onComplete: () => g.destroy(),
    });
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
      if (danger && Math.random() < 0.07) {
        // “event burst” micro-magic when stress spikes
        this.spawnBurst(m.glow.x, m.glow.y, 0xff5a8a);
      }
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

