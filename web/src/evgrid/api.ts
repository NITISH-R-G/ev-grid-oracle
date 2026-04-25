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
};

export type DemoStepResponse = {
  obs: any;
  event: any;
  mode?: "baseline" | "oracle";
  oracle_lora_repo?: string;
  oracle_llm_active?: boolean;
  action?: any;
};

export async function demoNew(seed: number): Promise<DemoNewResponse> {
  const r = await fetch("/demo/new", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ seed }),
  });
  if (!r.ok) throw new Error(`demoNew failed: ${r.status}`);
  return (await r.json()) as DemoNewResponse;
}

export async function demoStep(args: {
  session_id: string;
  mode: DemoMode;
  oracle_lora_repo: string;
}): Promise<DemoStepResponse> {
  const r = await fetch("/demo/step", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(args),
  });
  if (!r.ok) throw new Error(`demoStep failed: ${r.status}`);
  return (await r.json()) as DemoStepResponse;
}

