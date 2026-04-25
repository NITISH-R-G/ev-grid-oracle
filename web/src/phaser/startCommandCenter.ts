import Phaser from "phaser";
import { demoNew, demoStep } from "../evgrid/api";
import { PixelCityScene } from "./PixelCityScene";

type Args = {
  baselineMountId: string;
  oracleMountId: string;
  btnNew: HTMLButtonElement;
  btnStep: HTMLButtonElement;
  btnRun: HTMLButtonElement;
  followEl: HTMLInputElement;
  loraEl: HTMLInputElement;

  baselineBadge: HTMLDivElement;
  oracleBadge: HTMLDivElement;

  kpiWait: HTMLDivElement;
  kpiPeak: HTMLDivElement;
  kpiStress: HTMLDivElement;
  kpiRen: HTMLDivElement;
  kpiDream: HTMLDivElement;

  dreamEl: HTMLPreElement;
  oracleEl: HTMLPreElement;
  eventsEl: HTMLPreElement;
};

function fmtDelta(v: number, goodWhenNegative = true) {
  const cls = v === 0 ? "" : goodWhenNegative ? (v < 0 ? "deltaPos" : "deltaNeg") : v > 0 ? "deltaPos" : "deltaNeg";
  const sign = v > 0 ? "+" : "";
  return { text: `${sign}${v.toFixed(2)}`, cls };
}

function pill(el: HTMLElement, kind: "good" | "warn" | "bad", text: string) {
  el.className = `pill ${kind}`;
  el.textContent = text;
}

export function startCommandCenter(args: Args) {
  const mountBaseline = document.getElementById(args.baselineMountId);
  const mountOracle = document.getElementById(args.oracleMountId);
  if (!mountBaseline || !mountOracle) throw new Error("Mount nodes missing");

  const mkGame = (mount: HTMLElement) => {
    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      parent: mount,
      width: 1280,
      height: 720,
      backgroundColor: "#070911",
      pixelArt: true,
      antialias: false,
      physics: { default: "arcade" },
      scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
      scene: [PixelCityScene],
    };
    const game = new Phaser.Game(config);
    game.scene.start("PixelCityScene", {
      ui: {
        // PixelCityScene expects ui refs; we only use follow/lora via its updateRoadLod hook.
        statusEl: document.createElement("pre"),
        eventEl: document.createElement("pre"),
        modeEl: document.createElement("select"),
        followEl: args.followEl,
        loraEl: args.loraEl,
      },
    });
    const scene = () => game.scene.getScene("PixelCityScene") as PixelCityScene;
    return { game, scene };
  };

  const baseline = mkGame(mountBaseline);
  const oracle = mkGame(mountOracle);

  // Side-specific vibe (baseline = jittery, oracle = smooth)
  baseline.scene().setSide("baseline");
  oracle.scene().setSide("oracle");

  let baselineSid: string | null = null;
  let oracleSid: string | null = null;

  const seedRand = () => Math.floor(Math.random() * 10_000);

  const appendEvent = (line: string) => {
    const prev = args.eventsEl.textContent || "";
    args.eventsEl.textContent = prev ? `${prev}\n${line}` : line;
  };

  const applyKpis = (b: any, o: any, dreamScore: number | null) => {
    const bw = Number(b?.baseline?.avg_wait_minutes ?? 0);
    const ow = Number(o?.oracle?.avg_wait_minutes ?? 0);
    const wait = fmtDelta(ow - bw, true);
    args.kpiWait.textContent = wait.text;
    args.kpiWait.className = `kpiVal ${wait.cls}`;

    const bp = Number(b?.baseline?.peak_violations ?? 0);
    const op = Number(o?.oracle?.peak_violations ?? 0);
    const peak = fmtDelta(op - bp, true);
    args.kpiPeak.textContent = peak.text;
    args.kpiPeak.className = `kpiVal ${peak.cls}`;

    const bs = Number(b?.baseline?.grid_stress_events ?? 0);
    const os = Number(o?.oracle?.grid_stress_events ?? 0);
    const stress = fmtDelta(os - bs, true);
    args.kpiStress.textContent = stress.text;
    args.kpiStress.className = `kpiVal ${stress.cls}`;

    const br = Number(b?.baseline?.renewable_mean ?? 0);
    const or = Number(o?.oracle?.renewable_mean ?? 0);
    const ren = fmtDelta(or - br, false);
    args.kpiRen.textContent = ren.text;
    args.kpiRen.className = `kpiVal ${ren.cls}`;

    args.kpiDream.textContent = dreamScore == null ? "—" : `${(dreamScore * 100).toFixed(1)}%`;
    args.kpiDream.className = "kpiVal";
  };

  const initSessions = async () => {
    const seed = seedRand();
    pill(args.oracleBadge, "warn", "loading…");
    args.eventsEl.textContent = "(creating sessions)";
    try {
      const [b, o] = await Promise.all([demoNew(seed), demoNew(seed)]);
      baselineSid = b.session_id;
      oracleSid = o.session_id;
      await baseline.scene().bindSession(b.session_id, b.station_nodes);
      await oracle.scene().bindSession(o.session_id, o.station_nodes);
      pill(args.baselineBadge, "warn", "heuristic");
      pill(args.oracleBadge, "good", "ready");
      args.eventsEl.textContent = `seed=${seed}\nbaseline=${baselineSid}\noracle=${oracleSid}`;
      // Optional: take 1 automatic step so the UI shows life immediately.
      appendEvent("(auto-step 1)");
      await stepOne();
    } catch (e: any) {
      pill(args.oracleBadge, "bad", "API ERROR");
      pill(args.baselineBadge, "bad", "API ERROR");
      args.dreamEl.textContent = "ERROR: failed to create sessions.";
      args.oracleEl.textContent = "ERROR: failed to create sessions.";
      args.eventsEl.textContent = `ERROR creating sessions:\n${String(e?.message || e)}`;
    }
  };

  const stepOne = async () => {
    if (!baselineSid || !oracleSid) throw new Error("Click New first.");

    const oracleRepo = args.loraEl.value || "";
    const bRes = await demoStep({ session_id: baselineSid, mode: "baseline", oracle_lora_repo: "" });
    const oRes = await demoStep({ session_id: oracleSid, mode: "oracle", oracle_lora_repo: oracleRepo });

    // animate
    await baseline.scene().playExternalEvent(bRes.event);
    await oracle.scene().playExternalEvent(oRes.event);

    // badges
    pill(args.baselineBadge, "warn", "heuristic");
    pill(
      args.oracleBadge,
      oRes.oracle_llm_active ? "good" : "warn",
      oRes.oracle_llm_active ? "LLM ACTIVE" : "FALLBACK"
    );

    // right rail: dream panel + oracle panel
    const dreamScore = typeof (oRes as any).dream_score === "number" ? (oRes as any).dream_score : null;
    const dreamBreak = (oRes as any).dream_breakdown || {};
    const dreamPred = (oRes as any).dream_pred || null;
    const dreamTrue = (oRes as any).dream_true || null;
    args.dreamEl.textContent =
      dreamScore == null
        ? "Dream score: N/A (no <SIMULATE> from Oracle yet)\n\nTip: run Oracle with LoRA trained on dream reward."
        : `DREAM SCORE: ${(dreamScore * 100).toFixed(1)}%\n\nPRED:\n${JSON.stringify(dreamPred, null, 2)}\n\nTRUE:\n${JSON.stringify(dreamTrue, null, 2)}\n\nBREAKDOWN:\n${JSON.stringify(dreamBreak, null, 2)}`;

    const rb = (oRes.obs?.reward_breakdown || {}) as Record<string, number>;
    const top = Object.entries(rb)
      .filter(([k]) => k !== "total")
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .slice(0, 8)
      .map(([k, v]) => `${k}=${v.toFixed(3)}`)
      .join(" | ");
    const st = oRes.obs?.state;
    args.oracleEl.textContent =
      `ACTION: ${String(oRes.action?.action_type || "")} station=${String(oRes.action?.station_id || "NONE")}\n` +
      `GRID: load=${((st?.grid_load_pct ?? 0) * 100).toFixed(1)}% renew=${((st?.renewable_pct ?? 0) * 100).toFixed(
        1
      )}% peak=${String(st?.peak_risk || "")}\n` +
      `REWARD: total=${Number(rb.total ?? 0).toFixed(3)}\n` +
      `BREAKDOWN: ${top || "(empty)"}`;

    // event stream
    args.eventsEl.textContent = JSON.stringify(
      { baseline: { event: bRes.event, action: bRes.action }, oracle: { event: oRes.event, action: oRes.action } },
      null,
      2
    );

    // KPI delta: use evaluate-style summary approximations from obs (lightweight)
    const bKpi = {
      baseline: {
        avg_wait_minutes: Number(bRes.obs?.state?.stations?.reduce((a: number, s: any) => a + s.avg_wait_minutes, 0) ?? 0) /
          Math.max(1, bRes.obs?.state?.stations?.length ?? 1),
        peak_violations: Number(bRes.obs?.state?.grid_load_pct ?? 0) > 0.8 ? 1 : 0,
        grid_stress_events: Number(
          (bRes.obs?.state?.stations ?? []).filter(
            (s: any) => s.occupied_slots / Math.max(1, s.total_slots) > 0.85
          ).length
        ),
        renewable_mean: Number(bRes.obs?.state?.renewable_pct ?? 0),
      },
    };
    const oKpi = {
      oracle: {
        avg_wait_minutes: Number(oRes.obs?.state?.stations?.reduce((a: number, s: any) => a + s.avg_wait_minutes, 0) ?? 0) /
          Math.max(1, oRes.obs?.state?.stations?.length ?? 1),
        peak_violations: Number(oRes.obs?.state?.grid_load_pct ?? 0) > 0.8 ? 1 : 0,
        grid_stress_events: Number(
          (oRes.obs?.state?.stations ?? []).filter(
            (s: any) => s.occupied_slots / Math.max(1, s.total_slots) > 0.85
          ).length
        ),
        renewable_mean: Number(oRes.obs?.state?.renewable_pct ?? 0),
      },
    };
    applyKpis(bKpi, oKpi, dreamScore);
  };

  args.btnNew.onclick = async () => {
    await initSessions();
  };

  args.btnStep.onclick = async () => {
    await stepOne();
  };

  args.btnRun.onclick = async () => {
    for (let i = 0; i < 60; i++) {
      // eslint-disable-next-line no-await-in-loop
      await stepOne();
      // eslint-disable-next-line no-await-in-loop
      await new Promise((r) => setTimeout(r, 90));
    }
  };

  // initial badges
  pill(args.baselineBadge, "warn", "heuristic");
  pill(args.oracleBadge, "warn", "ready");

  // Auto-start for Spaces (no need to click New)
  window.setTimeout(() => {
    void initSessions();
  }, 200);
}

