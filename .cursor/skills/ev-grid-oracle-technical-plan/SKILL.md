---
name: ev-grid-oracle-technical-plan
description: Produces a complete, hackathon-ready technical plan (and repo scaffold checklist) for building EVGridEnv (OpenEnv RL environment) and a GRPO-trained “Oracle Agent” (Qwen2.5 3B + Unsloth/QLoRA) for EV charging grid routing (Bangalore/BESCOM). Use when the user mentions EV Grid Oracle, BESCOM Theme 9, OpenEnv hackathon, EV charging routing, demand-response, GRPO/TRL, Unsloth, Qwen 2.5 3B, Hugging Face Spaces, Gradio demo, Pygame viz, openenv.yaml, or wants a dual-submission plan with measurable KPIs.
---
 
# ⚡ EV Grid Oracle — Complete Technical Plan
 
## Quick start (what to do when invoked)
Deliver a single cohesive plan that results in:
- An **OpenEnv-compliant environment** (`EVGridEnv`) with `reset()`, `step()`, `state()`, reward breakdown, and a FastAPI wrapper
- A **trainable Oracle Agent loop** (Qwen 2.5 3B Instruct + GRPO) that reads structured text state and emits a verifiable action
- A **judge-friendly demo** (HF Spaces + Gradio, optional Pygame recording) with before/after KPIs
- A **dual-submission narrative** (OpenEnv + AI for Bharat/BESCOM) without changing code, only framing
 
Default style: practical, measurable, India-specific (Bangalore neighborhoods, rupee pricing, BESCOM feeder constraint).
 
## Output format (use these headings)
Return the plan using exactly these headings, in order:
1. **One-line pitch**
2. **What we’re building (2 layers)**
3. **Architecture diagram (ASCII)**
4. **Environment spec (state/action/reward/episodes)**
5. **Verification & anti-hack rules**
6. **Repo scaffold (tree + key files)**
7. **Training plan (Colab T4)**
8. **Demo plan (HF Spaces + judge screenplay)**
9. **Metrics & evaluation**
10. **Submission checklist**
11. **20-hour build plan (hour-by-hour)**
12. **Risks & mitigations**
 
## Core constraints (don’t violate)
- **OpenEnv compliance**: environment must inherit `openenv.Environment` and expose standard API surface; server/client separation respected.
- **Verifiable actions**: every model output must be parsed + validated; invalid/malicious actions handled deterministically.
- **No reward hacking freebies**: incorporate at least 3 explicit defenses (invalid action, impossible routing, “always defer”).
- **Measurable demo**: baseline vs oracle comparison table required; reward breakdown logging required.
- **HF Spaces deployability**: plan must include a minimal working path that runs on Spaces CPU; training stays in Colab T4.
 
## Environment design defaults (use unless user overrides)
- **City**: Bangalore graph with ~25 charging stations (real neighborhoods + GPS for map viz)
- **Charger types**: slow (7kW), fast (30kW), ultra-fast (150kW); slot counts 4–16
- **Time model**: step = 5 minutes; episode = 48 steps (4 hours)
- **State**: stations + pending EV requests + grid load + renewable % + time-of-day + peak risk
- **Action**: route/defer/load_shift with station_id + charge_rate + defer_minutes
- **Reward**: wait penalty, grid stress penalty, peak penalty, renewable bonus, urgency satisfaction, anti-hack penalties (return breakdown dict)
 
## Recommended implementation workflow (agent instructions)
1. **Pin the deliverable**: confirm the user wants (a) just a plan, or (b) a plan + repo scaffold + code skeleton. If unclear, assume **plan + scaffold**.
2. **Define the contracts first**:
   - `GridState` / `EVRequest` / `StationState` dataclasses
   - `EVGridAction` schema
   - `prompt_builder(state) -> str` format and strict parser for actions
3. **Design for verification**:
   - `parse_action(text) -> (action|INVALID, errors)`
   - `validate_action(state, action) -> (ok, reason)`
   - invalid actions get safe handling + stable reward signal (prefer 0 or small negative; don’t create exploit)
4. **Reward and logging**:
   - implement `compute_reward(prev, action, next) -> (total, breakdown)`
   - log breakdown keys consistently (e.g. `reward/wait`, `reward/peak`)
5. **Demo-first slice**:
   - baseline policy (random/greedy) + env + metrics
   - Gradio UI that runs baseline immediately
   - only then add trained agent toggle
 
## Templates & deeper material
- For `openenv.yaml`, strict prompt/action formats, and repo skeleton templates, use [reference.md](reference.md).
- For judge screenplay + KPI table template, use [examples.md](examples.md).

