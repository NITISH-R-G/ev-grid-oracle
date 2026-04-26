export type DemoMode = "baseline" | "oracle";

export type StationNode = {
  station_id: string;
  name: string;
  slug: string;
  lat: number;
  lng: number;
  total_slots: number;
};

export type DemoNewResponse = {
  session_id: string;
  obs: any;
  station_nodes: StationNode[];
  scenario?: string;
  seed?: number;
  sim_version?: string;
  scenario_schedule?: any[];
};

export type DemoStepResponse = {
  obs: any;
  event: any;
  scenario?: string;
  scenario_events_at_tick?: any[];
  tick?: number;
  sim_version?: string;
  anti_cheat_flags?: string[];
  anti_cheat_details?: Record<string, string>;
  role_kpis?: Record<string, Record<string, number>>;
  role_reward_breakdown?: Record<string, Record<string, number>>;
  mode?: "baseline" | "oracle";
  oracle_lora_repo?: string;
  oracle_llm_active?: boolean;
  oracle_timed_out?: boolean;
  oracle_skipped_env?: boolean;
  action?: any;
  forced_action?: boolean;
};

export type DemoSpawnVehicleResponse = {
  request_id?: string;
  session_id: string;
  spawned_ev?: any;
  assignment?: any;
  event?: any;
  ms?: number;
};

export type MANewResponse = {
  session_id: string;
  obs: any;
  station_nodes: StationNode[];
  scenario?: string;
  seed?: number;
  sim_version?: string;
  messages?: any[];
  grid_directive?: any;
};

export type MAStepResponse = {
  session_id: string;
  obs: any;
  tick?: number;
  scenario?: string;
  grid_directive?: any;
  fleet_action?: any;
  resolved_action?: any;
  violations?: string[];
  messages?: any[];
  role_rewards?: any;
};

async function sleep(ms: number) {
  await new Promise((r) => setTimeout(r, ms));
}

export async function demoNew(seed: number, scenario: string = "baseline", fleet_mode: string = "mixed"): Promise<DemoNewResponse> {
  const maxAttempts = 3;
  let lastErr: unknown = null;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const ctl = new AbortController();
    const timeoutMs = 90_000;
    const t = window.setTimeout(() => ctl.abort(), timeoutMs);
    try {
      const r = await fetch("/demo/new", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ seed, scenario, fleet_mode }),
        signal: ctl.signal,
      });
      if (!r.ok) {
        let detail = "";
        try {
          const j = await r.json();
          detail = j?.detail ? ` — ${String(j.detail)}` : ` — ${JSON.stringify(j).slice(0, 500)}`;
        } catch {
          try {
            const txt = await r.text();
            detail = txt ? ` — ${txt.slice(0, 500)}` : "";
          } catch {
            detail = "";
          }
        }
        throw new Error(`demoNew failed: ${r.status}${detail}`);
      }
      return (await r.json()) as DemoNewResponse;
    } catch (e: any) {
      lastErr = e;
      const isAbort = e?.name === "AbortError";
      if (attempt >= maxAttempts) {
        if (isAbort) {
          throw new Error(
            "demoNew timed out (90s). The Space may be cold-starting. Wait ~30s and refresh, or try again."
          );
        }
        throw e;
      }
      // Brief backoff for HF Spaces cold-start / transient network.
      await sleep(isAbort ? 1_250 : 650);
    } finally {
      window.clearTimeout(t);
    }
  }
  throw lastErr instanceof Error ? lastErr : new Error("demoNew failed.");
}

export async function demoStep(args: {
  session_id: string;
  mode: DemoMode;
  oracle_lora_repo: string;
  forced_action?: any;
}): Promise<DemoStepResponse> {
  const ctl = new AbortController();
  const t = window.setTimeout(() => ctl.abort(), 240_000);
  try {
    const r = await fetch("/demo/step", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(args),
      signal: ctl.signal,
    });
    if (!r.ok) {
      let detail = "";
      try {
        const j = await r.json();
        detail = j?.detail ? ` — ${String(j.detail)}` : ` — ${JSON.stringify(j).slice(0, 500)}`;
      } catch {
        try {
          const txt = await r.text();
          detail = txt ? ` — ${txt.slice(0, 500)}` : "";
        } catch {
          detail = "";
        }
      }
      throw new Error(`demoStep failed: ${r.status}${detail}`);
    }
    return (await r.json()) as DemoStepResponse;
  } catch (e: any) {
    if (e?.name === "AbortError") {
      throw new Error("demoStep timed out after 4m — server may be loading Qwen+LoRA on CPU; try ORACLE_SKIP_LLM=1 on Space or fix LoRA repo id.");
    }
    throw e;
  } finally {
    window.clearTimeout(t);
  }
}

export async function demoSpawnVehicle(args: {
  session_id: string;
  min_station_dist_m?: number;
  battery_threshold_pct?: number;
}): Promise<DemoSpawnVehicleResponse> {
  const r = await fetch("/demo/spawn_vehicle", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(args),
  });
  if (!r.ok) {
    let detail = "";
    try {
      const j = await r.json();
      detail = j?.detail ? ` — ${String(j.detail)}` : ` — ${JSON.stringify(j).slice(0, 500)}`;
    } catch {
      try {
        const txt = await r.text();
        detail = txt ? ` — ${txt.slice(0, 500)}` : "";
      } catch {
        detail = "";
      }
    }
    throw new Error(`demoSpawnVehicle failed: ${r.status}${detail}`);
  }
  return (await r.json()) as DemoSpawnVehicleResponse;
}

export async function maNew(seed: number, scenario: string = "baseline", fleet_mode: string = "mixed"): Promise<MANewResponse> {
  const r = await fetch("/ma/new", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ seed, scenario, fleet_mode }),
  });
  if (!r.ok) throw new Error(`maNew failed: ${r.status}`);
  return (await r.json()) as MANewResponse;
}

export async function maAutoStep(args: {
  session_id: string;
  fleet_policy: "baseline" | "oracle";
  oracle_lora_repo?: string;
}): Promise<MAStepResponse> {
  const r = await fetch("/ma/auto_step", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(args),
  });
  if (!r.ok) throw new Error(`maAutoStep failed: ${r.status}`);
  return (await r.json()) as MAStepResponse;
}

