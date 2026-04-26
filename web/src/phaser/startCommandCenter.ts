import { demoNew, demoSpawnVehicle, demoStep, maAutoStep, maNew } from "../evgrid/api";
import type { StationNode } from "../evgrid/api";
import { MapView } from "../map/MapView";

type Args = {
  baselineMountId: string;
  oracleMountId: string;
  btnNew: HTMLButtonElement;
  btnStep: HTMLButtonElement;
  btnRun: HTMLButtonElement;
  btnSpawn: HTMLButtonElement;
  btnDemo: HTMLButtonElement;
  btnJudge: HTMLButtonElement;
  btnExport: HTMLButtonElement;
  scenarioEl: HTMLSelectElement;
  seedEl: HTMLInputElement;
  tickEl: HTMLInputElement;
  tickLabelEl: HTMLSpanElement;
  btnPlay: HTMLButtonElement;
  followEl: HTMLInputElement;
  loraEl: HTMLInputElement;
  fleetEl?: HTMLSelectElement;

  baselineBadge: HTMLDivElement;
  oracleBadge: HTMLDivElement;

  kpiWait: HTMLDivElement;
  kpiPeak: HTMLDivElement;
  kpiStress: HTMLDivElement;
  kpiRen: HTMLDivElement;
  kpiDream: HTMLDivElement;

  dreamEl: HTMLPreElement;
  oracleEl: HTMLPreElement;
  diffEl: HTMLPreElement;
  eventsEl: HTMLPreElement;
  negoEl: HTMLPreElement;
};

type TurnFrame = {
  tick: number;
  action: any;
  event: any;
  anti_cheat_flags?: string[];
  anti_cheat_details?: Record<string, string>;
  scenario_events_at_tick?: any[];
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

function bump(el: HTMLElement | null, cls: "pulse" | "shake") {
  if (!el) return;
  el.classList.remove(cls);
  // Force reflow so the animation retriggers even with same class.
  void el.offsetWidth;
  el.classList.add(cls);
}

function setText(id: string, v: string) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = v;
}

function setVerdict(kind: "ready" | "win" | "risk", text: string) {
  const el = document.getElementById("heroVerdict");
  if (!el) return;
  el.className = `heroVerdict ${kind}`;
  el.textContent = text;
}

function setBar(id: string, pct: number, good: boolean) {
  const el = document.getElementById(id) as HTMLDivElement | null;
  if (!el) return;
  const p = Math.max(0, Math.min(100, pct));
  el.style.width = `${p.toFixed(0)}%`;
  el.style.background = good
    ? "linear-gradient(90deg, rgba(71,255,154,0.90), rgba(35,231,255,0.70))"
    : "linear-gradient(90deg, rgba(255,90,138,0.92), rgba(255,191,60,0.62))";
}

async function withDeadline<T>(p: Promise<T>, ms: number, label: string): Promise<T> {
  let timeoutId: number | null = null;
  try {
    return await Promise.race([
      p,
      new Promise<T>((_, reject) => {
        timeoutId = window.setTimeout(() => reject(new Error(`${label} timed out after ${ms / 1000}s`)), ms);
      }),
    ]);
  } finally {
    if (timeoutId != null) window.clearTimeout(timeoutId);
  }
}

export function startCommandCenter(args: Args) {
  const mountBaseline = document.getElementById(args.baselineMountId);
  const mountOracle = document.getElementById(args.oracleMountId);
  if (!mountBaseline || !mountOracle) {
    pill(args.baselineBadge, "bad", "UI ERROR");
    pill(args.oracleBadge, "bad", "UI ERROR");
    args.eventsEl.textContent =
      "ERROR: mount nodes missing.\n\n" +
      `baselineMountId=${args.baselineMountId} oracleMountId=${args.oracleMountId}\n` +
      "This is a frontend wiring issue (DOM ids).";
    return;
  }

  // Surface unexpected runtime errors in the UI (HF Spaces users often don't open DevTools).
  const reportFatal = (label: string, detail: unknown) => {
    pill(args.baselineBadge, "bad", label);
    pill(args.oracleBadge, "bad", label);
    const msg = detail instanceof Error ? `${detail.name}: ${detail.message}` : String(detail);
    args.eventsEl.textContent = `${label}\n${msg}`;
    args.oracleEl.textContent = `${label}\n${msg}`;
    args.dreamEl.textContent =
      `${label}\n${msg}\n\n` +
      "Tip: hard refresh (Ctrl+F5) to clear cached JS after a Space rebuild.";
  };
  window.addEventListener("error", (ev) => reportFatal("RUNTIME ERROR", (ev as ErrorEvent).error || (ev as ErrorEvent).message));
  window.addEventListener("unhandledrejection", (ev) => reportFatal("PROMISE REJECTION", (ev as PromiseRejectionEvent).reason));

  const mkMap = (mount: HTMLElement) => {
    const view = new MapView(mount);
    const ready = Promise.resolve(view);
    return { view, ready };
  };

  const baseline = mkMap(mountBaseline);
  const oracle = mkMap(mountOracle);

  void baseline.ready.then((s) => s.setSide("baseline")).catch((e) => reportFatal("MAP ERROR", e));
  void oracle.ready.then((s) => s.setSide("oracle")).catch((e) => reportFatal("MAP ERROR", e));

  let baselineSid: string | null = null;
  let oracleSid: string | null = null;
  let judgeMode = false;

  const baselineFrames: TurnFrame[] = [];
  const oracleFrames: TurnFrame[] = [];
  let isReplaying = false;
  let replayBusy = false;
  let playTimer: number | null = null;
  let playing = false;
  let demoBusy = false;
  let tourBusy = false;
  let lastBaselineState: any | null = null;
  let lastOracleState: any | null = null;
  let lastOracleRb: Record<string, number> | null = null;
  const episodeLog: { tick: number; baseline: TurnFrame; oracle: TurnFrame }[] = [];

  const seedRand = () => Math.floor(Math.random() * 10_000);

  const sleep = async (ms: number) => {
    await new Promise((r) => window.setTimeout(r, ms));
  };

  const appendEvent = (line: string) => {
    const prev = args.eventsEl.textContent || "";
    args.eventsEl.textContent = prev ? `${prev}\n${line}` : line;
  };

  const applyUrlParams = () => {
    const p = new URLSearchParams(window.location.search || "");
    const seedQ = p.get("seed");
    const scenarioQ = p.get("scenario");
    const followQ = p.get("follow");
    const loraQ = p.get("lora");
    const fleetQ = p.get("fleet");
    const judgeQ = p.get("judge");

    if (scenarioQ) args.scenarioEl.value = scenarioQ;
    if (seedQ && !Number.isNaN(Number(seedQ))) args.seedEl.value = String(Number(seedQ));
    if (followQ != null) args.followEl.checked = followQ === "1" || followQ.toLowerCase() === "true";
    if (loraQ) args.loraEl.value = loraQ;
    if (args.fleetEl && fleetQ) args.fleetEl.value = fleetQ;
    if (judgeQ === "1" || judgeQ?.toLowerCase() === "true") judgeMode = true;
  };

  const updateShareLink = () => {
    const seed = Number(args.seedEl.value || "0") || 0;
    const scenario = args.scenarioEl.value || "baseline";
    const fleet = args.fleetEl ? args.fleetEl.value : "mixed";
    const params = new URLSearchParams();
    if (seed) params.set("seed", String(seed));
    if (scenario) params.set("scenario", scenario);
    if (fleet) params.set("fleet", fleet);
    if (args.followEl.checked) params.set("follow", "1");
    if (judgeMode) params.set("judge", "1");
    const lora = args.loraEl.value || "";
    if (lora) params.set("lora", lora);
    const url = `${window.location.pathname}?${params.toString()}`;
    appendEvent(`share: ${url}`);
  };

  const summarizeDiff = (prev: any | null, next: any | null) => {
    if (!next) return "(no state)";
    const pv = prev || {};
    const nv = next || {};
    const d = (a: any, b: any) => (Number(b ?? 0) - Number(a ?? 0));
    const pct = (x: any) => `${(Number(x ?? 0) * 100).toFixed(1)}%`;
    const num = (x: any) => Number(x ?? 0);

    const prevStations = Array.isArray(pv.stations) ? pv.stations : [];
    const nextStations = Array.isArray(nv.stations) ? nv.stations : [];
    const meanWait = (arr: any[]) => arr.reduce((a, s) => a + Number(s?.avg_wait_minutes ?? 0), 0) / Math.max(1, arr.length);
    const stressCount = (arr: any[]) => arr.filter((s) => Number(s?.occupied_slots ?? 0) / Math.max(1, Number(s?.total_slots ?? 1)) > 0.85).length;

    const lines: string[] = [];
    lines.push(`grid_load: ${pct(pv.grid_load_pct)} → ${pct(nv.grid_load_pct)} (Δ ${(d(pv.grid_load_pct, nv.grid_load_pct) * 100).toFixed(1)}pp)`);
    lines.push(`renewable: ${pct(pv.renewable_pct)} → ${pct(nv.renewable_pct)} (Δ ${(d(pv.renewable_pct, nv.renewable_pct) * 100).toFixed(1)}pp)`);
    lines.push(`avg_wait: ${meanWait(prevStations).toFixed(2)} → ${meanWait(nextStations).toFixed(2)} (Δ ${d(meanWait(prevStations), meanWait(nextStations)).toFixed(2)} min)`);
    lines.push(`stress_stations: ${stressCount(prevStations)} → ${stressCount(nextStations)} (Δ ${d(stressCount(prevStations), stressCount(nextStations)).toFixed(0)})`);
    lines.push(`peak_risk: ${String(pv.peak_risk || "—")} → ${String(nv.peak_risk || "—")}`);
    const pPend = Array.isArray(pv.pending_evs) ? pv.pending_evs.length : 0;
    const nPend = Array.isArray(nv.pending_evs) ? nv.pending_evs.length : 0;
    lines.push(`pending_evs: ${pPend} → ${nPend} (Δ ${nPend - pPend})`);
    lines.push(`tick_dt_s: ${num(nv.tick_dt_s).toFixed(1)}`);
    return lines.join("\n");
  };

  const summarizeRewardDelta = (prev: Record<string, number> | null, next: Record<string, number> | null) => {
    if (!next) return "(no reward)";
    const p = prev || {};
    const keys = Array.from(new Set([...Object.keys(p), ...Object.keys(next)])).filter((k) => k !== "total");
    const diffs = keys
      .map((k) => [k, Number(next[k] ?? 0) - Number(p[k] ?? 0)] as const)
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .slice(0, 6)
      .map(([k, dv]) => `${k}: ${dv >= 0 ? "+" : ""}${dv.toFixed(3)}`);
    const total = Number(next.total ?? 0);
    return `reward_total: ${total.toFixed(3)}\nΔ reward terms:\n${diffs.join("\n") || "(none)"}`;
  };

  const setReplayUi = () => {
    const n = Math.max(0, baselineFrames.length - 1);
    args.tickEl.min = "0";
    args.tickEl.max = String(n);
    args.tickEl.disabled = baselineFrames.length === 0;
    args.btnPlay.disabled = baselineFrames.length === 0;
    const t = Math.min(Number(args.tickEl.value || "0"), n);
    args.tickEl.value = String(t);
    args.tickLabelEl.textContent = String(t);
  };

  const stopPlay = () => {
    playing = false;
    args.btnPlay.textContent = "Play";
    if (playTimer != null) {
      window.clearInterval(playTimer);
      playTimer = null;
    }
  };

  const applyKpis = (b: any, o: any, dreamScore: number | null) => {
    const bw = Number(b?.baseline?.avg_wait_minutes ?? 0);
    const ow = Number(o?.oracle?.avg_wait_minutes ?? 0);
    const wait = fmtDelta(ow - bw, true);
    args.kpiWait.textContent = wait.text;
    args.kpiWait.className = `kpiVal ${wait.cls}`;
    setText("heroMain", wait.text);
    setText("heroMainUnit", "avg wait (min)");
    setBar("kpiWaitBar", (Math.min(30, Math.abs(ow - bw)) / 30) * 100, ow - bw <= 0);

    const bp = Number(b?.baseline?.peak_violations ?? 0);
    const op = Number(o?.oracle?.peak_violations ?? 0);
    const peak = fmtDelta(op - bp, true);
    args.kpiPeak.textContent = peak.text;
    args.kpiPeak.className = `kpiVal ${peak.cls}`;
    setText("heroPeak", peak.text);
    setBar("kpiPeakBar", (Math.min(8, Math.abs(op - bp)) / 8) * 100, op - bp <= 0);

    const bs = Number(b?.baseline?.grid_stress_events ?? 0);
    const os = Number(o?.oracle?.grid_stress_events ?? 0);
    const stress = fmtDelta(os - bs, true);
    args.kpiStress.textContent = stress.text;
    args.kpiStress.className = `kpiVal ${stress.cls}`;
    setText("heroStress", stress.text);
    setBar("kpiStressBar", (Math.min(12, Math.abs(os - bs)) / 12) * 100, os - bs <= 0);

    const br = Number(b?.baseline?.renewable_mean ?? 0);
    const or = Number(o?.oracle?.renewable_mean ?? 0);
    const ren = fmtDelta(or - br, false);
    args.kpiRen.textContent = ren.text;
    args.kpiRen.className = `kpiVal ${ren.cls}`;
    setText("heroRen", ren.text);
    setBar("kpiRenBar", (Math.min(0.55, Math.abs(or - br)) / 0.55) * 100, or - br >= 0);

    args.kpiDream.textContent = dreamScore == null ? "—" : `${(dreamScore * 100).toFixed(1)}%`;
    args.kpiDream.className = "kpiVal";
    setText("heroDream", dreamScore == null ? "—" : `${(dreamScore * 100).toFixed(1)}%`);
    setBar("kpiDreamBar", dreamScore == null ? 0 : dreamScore * 100, (dreamScore ?? 0) >= 0.6);

    const wins =
      (ow - bw <= 0 ? 1 : 0) +
      (op - bp <= 0 ? 1 : 0) +
      (os - bs <= 0 ? 1 : 0) +
      (or - br >= 0 ? 1 : 0);
    if (wins >= 3) {
      setVerdict("win", `WIN ${wins}/4`);
      setText("heroSub", "Oracle is outperforming baseline under current conditions.");
      bump(document.getElementById("oraclePanel"), "pulse");
    } else if (wins <= 1) {
      setVerdict("risk", `RISK ${wins}/4`);
      setText("heroSub", "Baseline is holding up — try a stress scenario, then Run 60.");
      bump(document.getElementById("baselinePanel"), "shake");
    } else {
      setVerdict("ready", `LIVE ${wins}/4`);
      setText("heroSub", "Close race — keep stepping and watch the deltas stabilize.");
      bump(document.getElementById("heroStrip"), "pulse");
    }
  };

  const initSessions = async () => {
    stopPlay();
    baselineFrames.length = 0;
    oracleFrames.length = 0;
    episodeLog.length = 0;

    const seed = Number(args.seedEl.value || "0") || seedRand();
    const scenario = args.scenarioEl.value || "baseline";
    const fleet = args.fleetEl ? args.fleetEl.value : "mixed";
    pill(args.baselineBadge, "warn", "waking server…");
    pill(args.oracleBadge, "warn", "waking server…");
    args.eventsEl.textContent = "(creating sessions — HF Space cold-start may take ~10–30s)";
    try {
      const [b, o] = await withDeadline(
        Promise.all([
          judgeMode ? maNew(seed, scenario, fleet) : demoNew(seed, scenario, fleet),
          judgeMode ? maNew(seed, scenario, fleet) : demoNew(seed, scenario, fleet),
        ]),
        75_000,
        judgeMode ? "maNew" : "demoNew"
      );
      baselineSid = b.session_id;
      oracleSid = o.session_id;
      const [bView, oView] = await withDeadline(Promise.all([baseline.ready, oracle.ready]), 10_000, "mapReady");
      await withDeadline(
        Promise.all([
          bView.bindSession(b.session_id, b.station_nodes as StationNode[]),
          oView.bindSession(o.session_id, o.station_nodes as StationNode[]),
        ]),
        25_000,
        "bindSession"
      );
      pill(args.baselineBadge, "warn", "heuristic");
      pill(args.oracleBadge, "good", judgeMode ? "ready (MA)" : "ready");
      setVerdict("ready", judgeMode ? "READY (MA)" : "READY");
      setText("heroSub", "Take 1–2 steps to reveal the delta. Then hit Run 60.");
      args.eventsEl.textContent = `seed=${seed}\nscenario=${scenario}\nbaseline=${baselineSid}\noracle=${oracleSid}`;
      args.dreamEl.textContent =
        "Sessions ready. Click STEP (first oracle step may download Qwen+LoRA on CPU — can take minutes; Space uses a server timeout fallback).\n\nTip: LoRA id must match Hub exactly, e.g. NITISHRG15102007/ev-oracle-lora";
      args.oracleEl.textContent = "(click STEP — no auto-run avoids blocking on model load)";
      appendEvent("(ready — click STEP or RUN 60)");
      if (judgeMode) args.negoEl.textContent = "Judge Mode enabled. STEP runs multi-agent auto policies (grid+fleet).";
      setReplayUi();
    } catch (e: any) {
      pill(args.oracleBadge, "bad", "API ERROR");
      pill(args.baselineBadge, "bad", "API ERROR");
      const msg = String(e?.message || e);
      args.dreamEl.textContent =
        "ERROR: failed to create sessions.\n\n" +
        "- If this is a fresh Space cold-start, wait ~30s and refresh.\n" +
        "- Check `/health` loads.\n" +
        "- If roads are missing, the client should still render stations; this error is likely API reachability.";
      args.oracleEl.textContent = `ERROR: ${msg}`;
      args.eventsEl.textContent = `ERROR creating sessions:\n${msg}`;
      setVerdict("risk", "API ERROR");
    }
  };

  const stepOne = async () => {
    if (!baselineSid || !oracleSid) {
      appendEvent("(auto: creating sessions)");
      await initSessions();
    }
    if (!baselineSid || !oracleSid) throw new Error("Sessions not ready. Click New and wait for the Space to warm up.");

    const oracleRepo = args.loraEl.value || "";
    if (judgeMode) {
      const bRes = await maAutoStep({ session_id: baselineSid, fleet_policy: "baseline", oracle_lora_repo: "" });
      const oRes = await maAutoStep({ session_id: oracleSid, fleet_policy: "oracle", oracle_lora_repo: oracleRepo });

      pill(args.baselineBadge, "warn", "heuristic");
      pill(args.oracleBadge, "good", "MA ACTIVE");

      // No Phaser event animation in MA v0 (server doesn't emit polylines yet).
      const rb = (oRes.obs?.reward_breakdown || {}) as Record<string, number>;
      const top = Object.entries(rb)
        .filter(([k]) => k !== "total")
        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
        .slice(0, 8)
        .map(([k, v]) => `${k}=${v.toFixed(3)}`)
        .join(" | ");
      const st = oRes.obs?.state;
      args.oracleEl.textContent =
        `ACTION: ${String(oRes.resolved_action?.action_type || "")} station=${String(oRes.resolved_action?.station_id || "NONE")}\n` +
        `GRID: load=${((st?.grid_load_pct ?? 0) * 100).toFixed(1)}% renew=${((st?.renewable_pct ?? 0) * 100).toFixed(
          1
        )}% peak=${String(st?.peak_risk || "")}\n` +
        `REWARD: total=${Number(rb.total ?? 0).toFixed(3)}\n` +
        `BREAKDOWN: ${top || "(empty)"}`;

      args.eventsEl.textContent = JSON.stringify(
        {
          baseline: { tick: bRes.tick, violations: bRes.violations, role_rewards: bRes.role_rewards },
          oracle: { tick: oRes.tick, violations: oRes.violations, role_rewards: oRes.role_rewards },
        },
        null,
        2
      );
      const msgs = (oRes.messages || []).slice(-6);
      args.negoEl.textContent = msgs.map((m: any) => `[${m.role}] ${m.text}`).join("\n") || "(no messages)";

      // KPI delta: lightweight approximations from obs
      const bKpi = {
        baseline: {
          avg_wait_minutes:
            Number(bRes.obs?.state?.stations?.reduce((a: number, s: any) => a + s.avg_wait_minutes, 0) ?? 0) /
            Math.max(1, bRes.obs?.state?.stations?.length ?? 1),
          peak_violations: Number(bRes.obs?.state?.grid_load_pct ?? 0) > 0.8 ? 1 : 0,
          grid_stress_events: Number(
            (bRes.obs?.state?.stations ?? []).filter((s: any) => s.occupied_slots / Math.max(1, s.total_slots) > 0.85).length
          ),
          renewable_mean: Number(bRes.obs?.state?.renewable_pct ?? 0),
        },
      };
      const oKpi = {
        oracle: {
          avg_wait_minutes:
            Number(oRes.obs?.state?.stations?.reduce((a: number, s: any) => a + s.avg_wait_minutes, 0) ?? 0) /
            Math.max(1, oRes.obs?.state?.stations?.length ?? 1),
          peak_violations: Number(oRes.obs?.state?.grid_load_pct ?? 0) > 0.8 ? 1 : 0,
          grid_stress_events: Number(
            (oRes.obs?.state?.stations ?? []).filter((s: any) => s.occupied_slots / Math.max(1, s.total_slots) > 0.85).length
          ),
          renewable_mean: Number(oRes.obs?.state?.renewable_pct ?? 0),
        },
      };
      applyKpis(bKpi, oKpi, null);
      return;
    }

    const bRes = await demoStep({ session_id: baselineSid, mode: "baseline", oracle_lora_repo: "" });
    const oRes = await demoStep({ session_id: oracleSid, mode: "oracle", oracle_lora_repo: oracleRepo });

    if (!isReplaying) {
      baselineFrames.push({
        tick: Number(bRes.tick ?? baselineFrames.length),
        action: bRes.action,
        event: bRes.event,
        anti_cheat_flags: bRes.anti_cheat_flags,
        anti_cheat_details: bRes.anti_cheat_details,
        scenario_events_at_tick: bRes.scenario_events_at_tick,
      });
      oracleFrames.push({
        tick: Number(oRes.tick ?? oracleFrames.length),
        action: oRes.action,
        event: oRes.event,
        anti_cheat_flags: oRes.anti_cheat_flags,
        anti_cheat_details: oRes.anti_cheat_details,
        scenario_events_at_tick: oRes.scenario_events_at_tick,
      });
      const bi = baselineFrames.length - 1;
      const oi = oracleFrames.length - 1;
      if (bi >= 0 && oi >= 0) {
        episodeLog.push({
          tick: Number(bRes.tick ?? bi),
          baseline: { ...baselineFrames[bi] },
          oracle: { ...oracleFrames[oi] },
        });
      }
      setReplayUi();
    }

    // animate
    const [bView, oView] = await withDeadline(Promise.all([baseline.ready, oracle.ready]), 10_000, "mapReady");
    bView.setFollowVehicle(args.followEl.checked);
    oView.setFollowVehicle(args.followEl.checked);
    // Enrich route events with persona so MapView can pick car vs bike cleanly.
    const bEvt = { ...(bRes.event || {}), persona: String(bRes.obs?.state?.pending_evs?.[0]?.persona || "") };
    const oEvt = { ...(oRes.event || {}), persona: String(oRes.obs?.state?.pending_evs?.[0]?.persona || "") };
    await bView.playExternalEvent(bEvt);
    await oView.playExternalEvent(oEvt);

    // badges
    pill(args.baselineBadge, "warn", "heuristic");
    if (!judgeMode && (oRes as any).oracle_timed_out) {
      pill(args.oracleBadge, "bad", "TIMEOUT→baseline");
    } else if (!judgeMode && (oRes as any).oracle_skipped_env) {
      pill(args.oracleBadge, "warn", "SKIP LLM env");
    } else {
      pill(
        args.oracleBadge,
        judgeMode ? "good" : (oRes as any).oracle_llm_active ? "good" : "warn",
        judgeMode ? "MA ACTIVE" : (oRes as any).oracle_llm_active ? "LLM ACTIVE" : "FALLBACK"
      );
    }

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

    // diff panel: state + reward deltas (readable, judge-friendly)
    const bState = bRes.obs?.state || null;
    const oState = oRes.obs?.state || null;
    const oRb = (oRes.obs?.reward_breakdown || {}) as Record<string, number>;
    args.diffEl.textContent =
      `BASELINE\n${summarizeDiff(lastBaselineState, bState)}\n\nORACLE\n${summarizeDiff(lastOracleState, oState)}\n\nORACLE REWARD\n${summarizeRewardDelta(lastOracleRb, oRb)}`;
    lastBaselineState = bState;
    lastOracleState = oState;
    lastOracleRb = oRb;

    // event stream + negotiation
    if (!judgeMode) {
      args.eventsEl.textContent = JSON.stringify(
        {
          baseline: { tick: (bRes as any).tick, event: (bRes as any).event, action: (bRes as any).action, anti: (bRes as any).anti_cheat_flags },
          oracle: { tick: (oRes as any).tick, event: (oRes as any).event, action: (oRes as any).action, anti: (oRes as any).anti_cheat_flags },
        },
        null,
        2
      );
    } else {
      args.eventsEl.textContent = JSON.stringify(
        {
          baseline: { tick: (bRes as any).tick, violations: (bRes as any).violations, role_rewards: (bRes as any).role_rewards },
          oracle: { tick: (oRes as any).tick, violations: (oRes as any).violations, role_rewards: (oRes as any).role_rewards },
        },
        null,
        2
      );
      const msgs = ((oRes as any).messages || []).slice(-6);
      args.negoEl.textContent = msgs.map((m: any) => `[${m.role}] ${m.text}`).join("\n") || "(no messages)";
    }

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

  const runJudgeTour = async () => {
    if (tourBusy) return;
    tourBusy = true;
    const prevScenario = args.scenarioEl.value;
    const prevSeed = args.seedEl.value;
    const prevJudge = judgeMode;
    try {
      args.followEl.checked = true;
      judgeMode = false; // tour focuses on crisp route visuals + KPI deltas
      args.scenarioEl.value = args.scenarioEl.value || "festival_surge";
      args.seedEl.value = String(Number(args.seedEl.value || "0") || seedRand());

      setVerdict("ready", "TOUR");
      setText("heroSub", "Judge tour: short scripted sequence (watch neon route + KPI deltas).");

      args.btnDemo.disabled = true;
      args.btnRun.disabled = true;
      args.btnStep.disabled = true;
      args.btnNew.disabled = true;
      args.btnJudge.disabled = true;
      args.btnExport.disabled = true;

      await initSessions();
      updateShareLink();
      await sleep(450);

      const captions: string[] = [
        "Step 1: route appears under current traffic.",
        "Step 2: congestion pressure builds — oracle should adapt.",
        "Step 3: KPI deltas begin separating (avg wait / stress / peak).",
        "Step 4: follow stays tight — no messy whole-city view.",
        "Step 5: 'wow' moment — smooth motion + crisp polyline.",
        "Step 6: wrap-up — hit Run 60 for long-horizon evidence.",
      ];

      for (let i = 0; i < captions.length; i++) {
        setText("heroSub", captions[i]);
        // eslint-disable-next-line no-await-in-loop
        await stepOne();
        // eslint-disable-next-line no-await-in-loop
        await sleep(420);
      }

      setVerdict("win", "TOUR DONE");
      setText("heroSub", "Tour complete. Copy the share link in the log, or press Run 60 for full proof.");
    } catch (e) {
      reportFatal("TOUR ERROR", e);
    } finally {
      args.btnDemo.disabled = false;
      args.btnRun.disabled = false;
      args.btnStep.disabled = false;
      args.btnNew.disabled = false;
      args.btnJudge.disabled = false;
      args.btnExport.disabled = false;
      args.scenarioEl.value = prevScenario;
      args.seedEl.value = prevSeed;
      judgeMode = prevJudge;
      tourBusy = false;
    }
  };

  const replayToTick = async (frameIdx: number) => {
    if (replayBusy) return;
    replayBusy = true;
    isReplaying = true;
    try {
      if (!baselineSid || !oracleSid) return;
      const seed = Number(args.seedEl.value || "0") || 123;
      const scenario = args.scenarioEl.value || "baseline";
      const fleet = args.fleetEl ? args.fleetEl.value : "mixed";

      stopPlay();

      const [b, o] = await Promise.all([demoNew(seed, scenario, fleet), demoNew(seed, scenario, fleet)]);
      baselineSid = b.session_id;
      oracleSid = o.session_id;
      const [bView, oView] = await withDeadline(Promise.all([baseline.ready, oracle.ready]), 10_000, "mapReady");
      await bView.bindSession(b.session_id, b.station_nodes as StationNode[]);
      await oView.bindSession(o.session_id, o.station_nodes as StationNode[]);

      const oracleRepo = args.loraEl.value || "";
      const f = Math.max(0, Math.min(frameIdx, baselineFrames.length - 1, oracleFrames.length - 1));

      let bLast: any = null;
      let oLast: any = null;
      for (let i = 0; i <= f; i++) {
        const bf = baselineFrames[i];
        const of = oracleFrames[i];
        // eslint-disable-next-line no-await-in-loop
        bLast = await demoStep({
          session_id: baselineSid,
          mode: "baseline",
          oracle_lora_repo: "",
          forced_action: bf.action,
        });
        // eslint-disable-next-line no-await-in-loop
        oLast = await demoStep({
          session_id: oracleSid,
          mode: "oracle",
          oracle_lora_repo: oracleRepo,
          forced_action: of.action,
        });
      }

      if (bLast && oLast) {
        const [bView2, oView2] = await withDeadline(Promise.all([baseline.ready, oracle.ready]), 10_000, "mapReady");
        await bView2.playExternalEvent(bLast.event);
        await oView2.playExternalEvent(oLast.event);
      }
    } finally {
      isReplaying = false;
      replayBusy = false;
    }
  };

  args.btnNew.onclick = async () => {
    await initSessions();
    updateShareLink();
  };

  args.btnSpawn.onclick = async () => {
    try {
      args.btnSpawn.disabled = true;
      args.btnStep.disabled = true;
      args.btnRun.disabled = true;
      args.btnNew.disabled = true;
      args.btnExport.disabled = true;
      args.btnSpawn.textContent = "Spawning…";

      if (!baselineSid || !oracleSid) await initSessions();
      if (!baselineSid || !oracleSid) throw new Error("Sessions not ready.");

      const [bRes, oRes] = await Promise.all([
        demoSpawnVehicle({ session_id: baselineSid, min_station_dist_m: 250, battery_threshold_pct: 30 }),
        demoSpawnVehicle({ session_id: oracleSid, min_station_dist_m: 250, battery_threshold_pct: 30 }),
      ]);

      const [bView, oView] = await withDeadline(Promise.all([baseline.ready, oracle.ready]), 10_000, "mapReady");
      bView.setFollowVehicle(true);
      oView.setFollowVehicle(true);
      if (bRes?.event) await bView.playExternalEvent({ ...(bRes.event || {}), persona: String(bRes?.spawned_ev?.persona || "") });
      if (oRes?.event) await oView.playExternalEvent({ ...(oRes.event || {}), persona: String(oRes?.spawned_ev?.persona || "") });

      appendEvent(`spawned: ${String(oRes?.spawned_ev?.ev_id || bRes?.spawned_ev?.ev_id || "")}`);
      updateShareLink();
    } catch (e) {
      reportFatal("SPAWN ERROR", e);
    } finally {
      args.btnSpawn.disabled = false;
      args.btnStep.disabled = false;
      args.btnRun.disabled = false;
      args.btnNew.disabled = false;
      args.btnExport.disabled = false;
      args.btnSpawn.textContent = "New Vehicle";
    }
  };

  args.btnStep.onclick = async () => {
    try {
      args.btnStep.disabled = true;
      args.btnRun.disabled = true;
      args.btnNew.disabled = true;
      args.btnSpawn.disabled = true;
      args.btnStep.textContent = "Stepping…";
      // Default to follow mode so the judge can track the route/vehicle instantly.
      args.followEl.checked = true;
      await stepOne();
      updateShareLink();
    } catch (e) {
      reportFatal("STEP ERROR", e);
    } finally {
      args.btnStep.disabled = false;
      args.btnRun.disabled = false;
      args.btnNew.disabled = false;
      args.btnSpawn.disabled = false;
      args.btnStep.textContent = "Step";
    }
  };

  args.btnRun.onclick = async () => {
    try {
      args.btnStep.disabled = true;
      args.btnRun.disabled = true;
      args.btnNew.disabled = true;
      args.btnSpawn.disabled = true;
      args.btnRun.textContent = "Running…";
      for (let i = 0; i < 60; i++) {
        // eslint-disable-next-line no-await-in-loop
        await stepOne();
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => setTimeout(r, 90));
      }
      updateShareLink();
    } catch (e) {
      reportFatal("RUN ERROR", e);
    } finally {
      args.btnStep.disabled = false;
      args.btnRun.disabled = false;
      args.btnNew.disabled = false;
      args.btnSpawn.disabled = false;
      args.btnRun.textContent = "Run 60";
    }
  };

  args.btnDemo.onclick = async () => {
    if (demoBusy) return;
    demoBusy = true;
    const prevScenario = args.scenarioEl.value;
    const prevSeed = args.seedEl.value;
    try {
      args.followEl.checked = true;
      args.scenarioEl.value = "festival_surge";
      args.seedEl.value = String(seedRand());
      setText("heroSub", "Guided demo: chaos spike → Oracle reroutes → KPI win banner. Watch the neon path + smooth car motion.");
      setVerdict("risk", "DEMO");
      args.btnDemo.disabled = true;
      args.btnRun.disabled = true;
      args.btnStep.disabled = true;
      args.btnNew.disabled = true;
      args.btnExport.disabled = true;

      // New session
      await initSessions();
      updateShareLink();
      await sleep(450);

      // Cinematic: 14 ticks at readable pacing
      for (let i = 0; i < 14; i++) {
        await stepOne();
        if (i === 2) setText("heroSub", "Congestion builds. Baseline keeps pushing straight into it.");
        if (i === 5) setText("heroSub", "Oracle uses road-level routing — follow mode stays glued to the moving EV.");
        if (i === 9) setText("heroSub", "Delta stabilizes. This is your “wow” moment on a projector.");
        await sleep(320);
      }

      setVerdict("win", "WIN");
      setText("heroSub", "Guided demo complete. Now hit Run 60 for the longer replay proof, or scrub the timeline.");
    } catch (e) {
      reportFatal("DEMO ERROR", e);
    } finally {
      args.btnDemo.disabled = false;
      args.btnRun.disabled = false;
      args.btnStep.disabled = false;
      args.btnNew.disabled = false;
      args.btnExport.disabled = false;
      args.scenarioEl.value = prevScenario;
      args.seedEl.value = prevSeed;
      demoBusy = false;
    }
  };

  args.tickEl.addEventListener("input", async () => {
    const t = Number(args.tickEl.value || "0");
    args.tickLabelEl.textContent = String(t);
    if (baselineFrames.length === 0) return;
    await replayToTick(t);
  });

  args.btnPlay.onclick = async () => {
    if (baselineFrames.length === 0) return;
    if (playing) {
      stopPlay();
      return;
    }
    playing = true;
    args.btnPlay.textContent = "Pause";
    let idx = Number(args.tickEl.value || "0");
    playTimer = window.setInterval(() => {
      void (async () => {
        idx = Math.min(idx + 1, baselineFrames.length - 1);
        args.tickEl.value = String(idx);
        args.tickLabelEl.textContent = String(idx);
        try {
          await replayToTick(idx);
        } catch {
          stopPlay();
        }
        if (idx >= baselineFrames.length - 1) stopPlay();
      })();
    }, 320);
  };

  // initial badges
  pill(args.baselineBadge, "warn", "heuristic");
  pill(args.oracleBadge, "warn", "ready");

  // Auto-start for Spaces (no need to click New)
  window.setTimeout(() => {
    applyUrlParams();
    void initSessions();
    const p = new URLSearchParams(window.location.search || "");
    if (p.get("tour") === "1" || p.get("tour")?.toLowerCase() === "true") {
      window.setTimeout(() => void runJudgeTour(), 650);
    }
  }, 200);

  args.btnJudge.onclick = async () => {
    judgeMode = true;
    args.eventsEl.textContent = "(Judge Mode enabled — multi-agent protocol)";
    await initSessions();
    updateShareLink();
  };

  args.btnExport.onclick = () => {
    const seed = Number(args.seedEl.value || "0") || 0;
    const scenario = args.scenarioEl.value || "baseline";
    const fleet = args.fleetEl ? args.fleetEl.value : "mixed";
    const payload = {
      exported_at: new Date().toISOString(),
      seed,
      scenario,
      fleet,
      judge_mode: judgeMode,
      frames: episodeLog,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `ev-grid-oracle-episode-${scenario}-${seed}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    appendEvent("(exported episode JSON — use OS screenshot for map stills)");
  };

  // Power-user keyboard shortcut: Shift+T runs the judge tour.
  window.addEventListener("keydown", (ev) => {
    if (ev.key.toLowerCase() === "t" && ev.shiftKey) void runJudgeTour();
  });
}

