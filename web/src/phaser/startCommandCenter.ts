import { demoNew, demoStep, maAutoStep, maNew } from "../evgrid/api";
import type { StationNode } from "../evgrid/api";
import { MapView } from "../map/MapView";

type Args = {
  baselineMountId: string;
  oracleMountId: string;
  btnNew: HTMLButtonElement;
  btnStep: HTMLButtonElement;
  btnRun: HTMLButtonElement;
  btnJudge: HTMLButtonElement;
  scenarioEl: HTMLSelectElement;
  seedEl: HTMLInputElement;
  tickEl: HTMLInputElement;
  tickLabelEl: HTMLSpanElement;
  btnPlay: HTMLButtonElement;
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

  const seedRand = () => Math.floor(Math.random() * 10_000);

  const appendEvent = (line: string) => {
    const prev = args.eventsEl.textContent || "";
    args.eventsEl.textContent = prev ? `${prev}\n${line}` : line;
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

    const seed = Number(args.seedEl.value || "0") || seedRand();
    const scenario = args.scenarioEl.value || "baseline";
    pill(args.baselineBadge, "warn", "waking server…");
    pill(args.oracleBadge, "warn", "waking server…");
    args.eventsEl.textContent = "(creating sessions — HF Space cold-start may take ~10–30s)";
    try {
      const [b, o] = await withDeadline(
        Promise.all([
          judgeMode ? maNew(seed, scenario) : demoNew(seed, scenario),
          judgeMode ? maNew(seed, scenario) : demoNew(seed, scenario),
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
    if (!baselineSid || !oracleSid) throw new Error("Click New first.");

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
      setReplayUi();
    }

    // animate
    const [bView, oView] = await withDeadline(Promise.all([baseline.ready, oracle.ready]), 10_000, "mapReady");
    bView.setFollowVehicle(args.followEl.checked);
    oView.setFollowVehicle(args.followEl.checked);
    await bView.playExternalEvent(bRes.event);
    await oView.playExternalEvent(oRes.event);

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

  const replayToTick = async (frameIdx: number) => {
    if (replayBusy) return;
    replayBusy = true;
    isReplaying = true;
    try {
      if (!baselineSid || !oracleSid) return;
      const seed = Number(args.seedEl.value || "0") || 123;
      const scenario = args.scenarioEl.value || "baseline";

      stopPlay();

      const [b, o] = await Promise.all([demoNew(seed, scenario), demoNew(seed, scenario)]);
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
    void initSessions();
  }, 200);

  args.btnJudge.onclick = async () => {
    judgeMode = true;
    args.eventsEl.textContent = "(Judge Mode enabled — multi-agent protocol)";
    await initSessions();
  };
}

