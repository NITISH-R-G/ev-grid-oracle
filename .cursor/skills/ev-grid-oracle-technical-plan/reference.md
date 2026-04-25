# Reference — EV Grid Oracle templates

Use these templates when generating the plan, scaffolding a repo, or writing “starter code” quickly and consistently.

## Repo tree (suggested)
```text
ev-grid-oracle/
├── openenv.yaml
├── pyproject.toml
├── README.md
├── ev_grid_oracle/
│   ├── __init__.py
│   ├── env.py
│   ├── models.py
│   ├── city_graph.py
│   ├── demand_sim.py
│   ├── grid_sim.py
│   ├── reward.py
│   └── prompt_builder.py
├── server/
│   └── app.py
├── client/
│   └── client.py
├── viz/
│   ├── city_map.py
│   └── gradio_demo.py
└── training/
    ├── train_grpo.ipynb
    └── evaluate.py
```

## `openenv.yaml` (outline)
Keep this aligned to the OpenEnv version in use; the plan should explicitly say “validate against latest schema”.

```yaml
name: ev-grid-oracle
version: 0.1.0
description: OpenEnv environment simulating Bangalore EV charging grid routing with grid constraints and renewable-aware rewards.
entrypoint: server.app:app
python:
  version: "3.10"
```

## Prompt format (strict, parseable)
Principles:
- Use a **fixed header**, stable separators, and bounded free-text
- Prefer **tables** for station info and a **single EV request** block (or explicit multi-EV batch section)
- Require responses in **one strict schema** (lines or JSON), and validate hard

Example response contract (line-based):
```text
ACTION: route|defer|load_shift
EV_ID: <ev_id>
STATION: <station_id|NONE>
CHARGE_RATE: slow|fast|ultra_fast|NONE
DEFER_MINUTES: <int>
REASON: <max 20 words>
CONFIDENCE: <0.0-1.0>
```

## Action parsing + validation (policy)
Default handling rules:
- If parse fails → action = INVALID, reward = 0, info includes `errors`
- If station_id unknown → INVALID
- If routing to full station → apply hard penalty component (e.g. `impossible = -8`)
- If deferring a critical EV (urgency > 0.8) → strong penalty component

## Reward breakdown keys (recommended)
Make the plan insist on stable keys to support plotting:
- `wait`
- `grid_stress`
- `peak`
- `renewable`
- `urgency`
- `impossible`
- `queue_routing`

## Minimal baseline policies (for demo)
- **Random**: choose any station with capacity, else defer 5
- **Greedy ETA**: choose min(avg_wait + travel_time) subject to capacity and urgency
- **Price-aware**: avoid peak price unless urgency high

## GRPO training (plan-level outline)
The plan should specify:
- model: `unsloth/Qwen2.5-3B-Instruct`
- QLoRA 4-bit on Colab T4
- TRL `GRPOTrainer`
- reward function calls env’s local `compute_reward` via deterministic sim step
- monitoring: reward components + action distribution + invalid action rate

