---
title: "EV Grid Oracle - verifiable GRPO on a Bangalore EV dispatch world"
emoji: ⚡
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

<div align="center">

# EV Grid Oracle

### Verifiable GRPO dispatch oracle for Bangalore's EV charging grid

[![OpenEnv](https://img.shields.io/badge/OpenEnv-openenv--core%200.2.3-0ea5e9)](https://pypi.org/project/openenv-core/)
[![Space](https://img.shields.io/badge/HF%20Space-ev--grid--oracle-f97316)](https://huggingface.co/spaces/NITISHRG15102007/ev-grid-oracle)
[![Colab](https://img.shields.io/badge/Colab-train_grpo.ipynb-facc15)](https://colab.research.google.com/github/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb)
[![Repo](https://img.shields.io/badge/GitHub-ev--grid--oracle-22c55e)](https://github.com/NITISH-R-G/ev-grid-oracle)

</div>

---

**EV Grid Oracle** is an **OpenEnv** environment + verifier suite where a small LLM learns to output **tool-like dispatch actions** that can be **executed, checked, and scored** (not just explained).

### Team Codestreak

- **Nitish R.G.** - Team Leader · [LinkedIn](https://www.linkedin.com/in/nitish-r-g-15-10-2007-rgn/)  
- **Padmanabhan Suresh Babu**  
- **Prithic**

---

## The 3-second hook (what makes this different)

- **Verifiable world, not vibes:** every action is parsed -> validated -> stepped in a simulator -> scored with a **reward breakdown**.  
- **Replayable evidence:** baseline vs oracle is evaluated on the **same seeds** (paired, deterministic).  
- **Engineer-grade outputs:** plots + stats are committed as PNG/JSON artifacts so judges can audit without rerunning everything.

If you only read one thing, read the repo's **"Judges - non-negotiables"** table in [`README.md`](https://github.com/NITISH-R-G/ev-grid-oracle/blob/main/README.md) (Space + Colab + plots + writeup in one place).

---

## Live environment (discoverable, runnable)

- **HF Space (environment):** see `README.md` -> Quick links (Space card + live host).  
- **OpenEnv descriptor:** [`openenv.yaml`](../openenv.yaml)  
- **Server entrypoint:** `server/app.py` (FastAPI, OpenEnv-style endpoints)  

**Core API shape (judge-friendly):**

- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /schema`
- `GET /health`

---

## Problem statement (why it matters)

Grid operators (and fleet dispatchers) are constantly making routing decisions under:

- **Queues / wait times**
- **Feeder stress / peak violations**
- **Renewable windows (shift load when it’s clean)**
- **Safety constraints + "no cheating" constraints**

We want an LLM that produces **structured, executable actions** under these constraints, then **improves** by reinforcement learning against a verifier.

---

## What the agent can do (action schemas)

This project uses **strict action schemas** so verification is deterministic.

### A) Station routing / load shifting (EVGridAction)

```text
ACTION: route|defer|load_shift
STATION: BLR-01..BLR-25 or NONE
CHARGE_RATE: slow|fast|ultra_fast
DEFER_MINUTES: integer
REASON: max 20 words
CONFIDENCE: 0.0-1.0
```

### B) Road-graph routing (connected-edge only)

```text
CURRENT_NODE: <int>
NEXT_NODE: <int>
REASON: max 20 words
CONFIDENCE: 0.0-1.0
```

The key constraint: **no teleporting** - the agent must pick a **neighbor edge** in the Bangalore road graph.

---

## Environment design (OpenEnv-first)

### Observations (what the model sees)

High-level: a text prompt containing the current grid snapshot (queues, stress, renewables, and the next decision point), plus a JSON-like `state` structure that is included in the OpenEnv response object.

### World dynamics (what changes after actions)

Each step advances a simulator tick:

- queue dynamics (arrivals / services)
- stress events (load crossing thresholds)
- renewable windows (time-varying clean score)
- anti-cheat flags if the action violates constraints

### Episode structure (long-horizon)

This is not a single-shot task. Policies are scored over many steps, and early mistakes can compound (or be recovered from).

---

## Reward design (verifiable, multi-component, anti-hack)

Reward is **not** "LLM-as-judge only." It's computed by the environment/verifier, with **independent components** (logged as columns).

High-level components include:

- **wait** (penalize long queues / delays)
- **grid_stress** (penalize overload)
- **peak** (penalize peak violations)
- **renewable** (reward clean windows)
- **urgency** (don’t defer critical EVs)
- **format + validity shaping**
- **anti-hack** (punish impossible/cheaty steps)

This is where most hackathon projects win or lose: **if reward is crisp and hard to game, RL works.**

---

## Training (Colab + TRL GRPO + Unsloth)

**Public training notebook:**

- **Colab:** `https://colab.research.google.com/github/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb`  
- **GitHub:** `https://github.com/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb`

The notebook:

- clones this repo
- installs `openenv-core`
- trains with **TRL GRPO** (verifier reward function)
- uses a **small model** + **QLoRA**-style adapter saving for iteration speed

### Winning tip (practical)

Small models + many short runs beat "one heroic huge run." Iterate on:

- reward components
- anti-hack flags
- scenario curriculum
- throughput (rollout speed dominates RL runtime)

---

## Evidence: results + plots (auditable, committed)

Everything below is generated by:

- `training/evaluate.py` → `training/eval_results.json`  
- `training/fair_eval.py` → `artifacts/fair_eval_results.json` + `artifacts/fair_eval_chart.png`  
- `training/make_plots.py` → the figure pack in `artifacts/`

### Current snapshot (paired evaluation)

From `training/eval_results.json` (paired_same_world=true, episodes=72):

- **avg_wait_minutes:** 0.2939  
- **grid_stress_events:** 10.3194  
- **peak_violations:** 5.6528  
- **renewable_mean:** 0.3625  
- **critical_deferred:** 0  
- **anti_cheat_steps:** 2.6389  

From `artifacts/fair_eval_results.json` (n_episodes=25): Wilson + McNemar summaries are committed for binary outcomes.

> Note: If oracle is configured to fall back to baseline (e.g. `ORACLE_SKIP_LLM=1` or no LoRA loaded), baseline and oracle curves may coincide. That’s expected and actually useful: it validates the **paired harness** before you spend GPU time.

---

## Training logs (non‑negotiable requirement)

After a real GPU GRPO run, TensorBoard event files land in `ev_oracle_grpo_road/`.

Export judge-ready plots (PNG) with labeled axes:

```bash
python tools/export_grpo_tensorboard_plots.py --logdir ev_oracle_grpo_road --out-dir artifacts
```

This writes:

- `artifacts/grpo_loss.png`
- `artifacts/grpo_reward.png`

These two files are the simplest "we actually trained" evidence judges look for.

---

## Visualization gallery (what judges can scan fast)

### One-page dashboard

![Six-panel evaluation dashboard](../artifacts/eval_dashboard_summary.png)

### Aggregate KPI comparison

![Baseline vs Oracle - mean KPIs](../artifacts/kpi_comparison.png)

### Per-episode trajectories (paired seeds)

![Wait, peak ticks, stress ticks vs episode index](../artifacts/eval_episode_trajectories.png)

### Paired deltas (oracle − baseline)

![Per-episode delta histograms](../artifacts/eval_delta_histograms.png)

### Reward breakdown (mean components)

![Reward breakdown bars](../artifacts/eval_reward_breakdown_bars.png)

### Distribution over episodes

![Boxplots by policy](../artifacts/eval_boxplots_by_policy.png)

### Head-to-head win rates

![Oracle win rates](../artifacts/eval_oracle_win_rates.png)

### Paired scatter: wait

![Paired scatter wait](../artifacts/eval_paired_scatter_wait.png)

### Binary timeline (baseline difficulty map)

![Binary timeline baseline](../artifacts/eval_binary_timeline_baseline.png)

### Wilson intervals (binary rates)

![Binary rates with Wilson intervals](../artifacts/eval_fair_binary_rates.png)

### McNemar p-values (paired test)

![McNemar p-values](../artifacts/eval_mcnemar_pvalues.png)

### Fair-eval chart

![Wilson chart](../artifacts/fair_eval_chart.png)

---

## Submission bundle (the "don't miss anything" checklist)

If you want **env + scripts + logs** in one place:

- [`docs/submission/training-artifacts-and-logs.md`](submission/training-artifacts-and-logs.md)
- Under-2 minute video shot list: [`docs/submission/youtube-under-2min-outline.md`](submission/youtube-under-2min-outline.md)

---

## LoRA / QLoRA warning (verbatim, keep this intact)

> If you're using LoRA/QLoRA, don't naively upcast a 4-bit base to 16-bit and "merge" at the end without the correct path - it can badly degrade quality. Save adapters cleanly and test post-training inference immediately.

---

## Official hackathon materials

See [`docs/hackathon-official-resources.md`](hackathon-official-resources.md) for OpenEnv + HF resources and the official video series.

---

## Shareable blog markdown URL (for submission forms)

Use the public GitHub URL of this markdown file:

`https://github.com/NITISH-R-G/ev-grid-oracle/blob/main/docs/hf-mini-blog-ev-grid-oracle.md`

If you mirror it to the **HF Space repository**, use the equivalent HF repo file URL (same path/name).
