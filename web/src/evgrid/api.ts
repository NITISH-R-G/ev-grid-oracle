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
  action?: any;
  forced_action?: boolean;
};

export async function demoNew(seed: number, scenario: string = "baseline"): Promise<DemoNewResponse> {
  const r = await fetch("/demo/new", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ seed, scenario }),
  });
  if (!r.ok) throw new Error(`demoNew failed: ${r.status}`);
  return (await r.json()) as DemoNewResponse;
}

export async function demoStep(args: {
  session_id: string;
  mode: DemoMode;
  oracle_lora_repo: string;
  forced_action?: any;
}): Promise<DemoStepResponse> {
  const r = await fetch("/demo/step", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(args),
  });
  if (!r.ok) throw new Error(`demoStep failed: ${r.status}`);
  return (await r.json()) as DemoStepResponse;
}

