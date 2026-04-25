# EV Grid Oracle — “City Ops Replay” (OpenOfficeRL patterns) Design Spec

Date: 2026-04-26  
Status: Approved (chat)  
Owner: EV_Grid_Oracle

## Goal

Make `EV_Grid_Oracle` feel **award-winning and unforgettable** by “copying” 10 high-leverage patterns from `OpenOfficeRL` (multi-agent tension, adversarial scenarios, composite reward breakdown + anti-cheat, hot-swappable modes, replayable seeds) and expressing them as a **Phaser-first City Ops replay experience**.

Primary demo style: **A — City Ops Replay** (Phaser map + timeline scrubber + dramatic scenario events).

Non-goals:
- Build a full multi-policy multi-agent training system in this iteration.
- Overhaul the simulator physics/graph; changes should layer on existing `EVGridCore`.

## Current baseline (as of now)

- FastAPI server already provides a demo API:
  - `POST /demo/new` returns `session_id`, `obs`, `station_nodes`
  - `POST /demo/step` steps `baseline` or `oracle` and returns `obs`, `event`, `reward_breakdown`, oracle text, etc.
- Web UI already has a dual-view Phaser “command center”:
  - baseline vs oracle side-by-side maps
  - “New / Step / Run” controls

## “Copy these 10 things” — concrete adaptations

### 1) Multi-role incentive tension (even if single-actor policy at first)

Introduce a **role model** as first-class state/logging:
- Roles: `discom`, `cpo`, `fleet`, `driver`
- Each role gets:
  - role KPIs per tick (grid safety, utilization, on-time service, user delay)
  - role reward components per tick (credit assignment surface)

Implementation note: In v1, the acting policy remains the dispatcher/oracle, but the environment emits role-scoped metrics and reward components so “multi-agent” is visible, and later can become true multi-agent policies.

### 2) Asymmetric observations (role-scoped views)

Add a “role observation” view generator:
- `observation_for(role)` returns a filtered summary of the state:
  - `discom`: feeder headroom, overload risk, peak risk
  - `cpo`: station queues, slot occupancy, outages
  - `fleet`: pending EV urgency, estimated detours, service level
  - `driver`: nearest stations, expected wait, price proxy

UI uses this as explainability panels, not necessarily as multiple policies yet.

### 3) Composite reward with explicit breakdown columns (+ shaping)

Standardize on a 6(+1) component reward:
- `wait`
- `grid_stress`
- `peak`
- `renewable`
- `urgency`
- `anti_hack`
- `valid_action_shaping` (small +ε when action is valid and constraint-respecting)

Guarantee: every tick logs **each component** and `total`.

### 4) Named anti-reward-hacking checks (visible + logged)

Add deterministic “anti-cheat” flags that trigger penalties and UI callouts:
- `teleportation`: SOC infeasible / unreachable station
- `phantom_capacity`: selecting unavailable station/slot state
- `time_window_violation`: ignores travel time / defer window rules
- `queue_piling`: repeatedly routing into an already failing queue
- `grid_limit_violation`: exceeds feeder/transformer safety caps

API returns `anti_cheat_flags: string[]` per tick.

### 5) Adversarial scenarios with scheduled events (reproducible stress tests)

Create scenario suite with deterministic event schedules:
- `baseline`
- `heatwave_peak`
- `festival_surge`
- `transformer_derate`
- `station_outage`
- `tariff_shock`

Each scenario has fixed tick events (and optional low-prob random events). API returns `scenario_events: []` per tick and the UI renders them.

### 6) Memory + reflection + planning loop (lightweight, demo-visible)

Add a lightweight “ops memory” stream (not full agent cognition yet):
- store recent events + top reward deltas (bounded buffer)
- periodically emit “reflection” text like:
  - “Peak risk rising in region X; prefer load shifting 18–21”

This shows long-horizon behavior and improves storytelling.

### 7) Token/prompt budgeting (priority pruning)

For the oracle prompt builder, introduce priority sections (P0–P8) and deterministic pruning so the model always sees constraints first:
- P0: action schema + constraints + current grid headroom
- P1: pending EVs + urgency
- P2: station queues/occupancy/outages
- P3: renewable window + price proxy
- P4+: history/memory

### 8) Hot-swappable modes + A/B comparison (foundation vs trained vs baseline)

UI can toggle:
- baseline heuristic
- oracle (LLM)
- oracle (LoRA) when available

Server already supports this; UI will add better visibility (badges + “LLM active”).

### 9) Replayable seeds + timeline scrubber (the core “wow”)

Record every tick into a compact `Frame`:
- state snapshot needed for rendering
- action + event
- reward breakdown + anti-cheat flags
- scenario events

UI adds:
- timeline slider (scrub)
- play/pause/step
- “bookmark event” quick jumps (e.g., first overload, first outage)

### 10) Explainability-first HUD overlays

In the Phaser map:
- feeder/region stress overlay (glow/heat)
- station outage icon + queue halo
- per-tick callout: “why reward changed” (top 2 components + flags)

## Backend/API changes

Extend `POST /demo/new` to accept:
- `seed`
- `scenario`

Extend `POST /demo/step` response with:
- `frame_id` (tick index)
- `anti_cheat_flags: string[]`
- `scenario_events: Array<{type, tick, meta}>`
- `role_kpis: Record<role, {...}>`
- `role_reward_breakdown: Record<role, Record<string, number>>`

Maintain backwards compatibility where possible, but the web UI will be updated in lockstep.

## Frontend changes (web Phaser)

Add a Replay layer on top of `PixelCityScene`:
- `ReplayStore` (frames, current tick, playing)
- timeline UI + controls
- events list / jump-to

Make scenario selection + seed entry first-class.

## Success criteria (what “mindblowing” means)

- Demo starts with one click and looks alive within 2 seconds.
- You can replay the same seed + scenario and see identical stress events.
- UI clearly shows *why* baseline fails and oracle improves:
  - lower queue halo counts
  - fewer overload callouts
  - reward breakdown bars improve over time

## Risks / mitigations

- Risk: scope creep into “true multi-agent policies”.
  - Mitigation: keep acting policy single-actor; add role surfaces for later.
- Risk: heavy snapshots bloat responses.
  - Mitigation: store minimal render state; keep frames bounded (e.g., last 300).

