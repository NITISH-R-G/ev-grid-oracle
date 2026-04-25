---
title: EV Grid Oracle (OpenEnv)
emoji: ⚡
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

## EV Grid Oracle — Bangalore’s EV Dispatch “Oracle”

An **OpenEnv RL environment** that simulates Bangalore’s EV charging grid and trains a small LLM (Qwen2.5‑3B) with **verifiable GRPO rewards** to route EVs in real time — **lower queues**, **avoid feeder stress**, **shift load to renewables**.

### OpenEnv Hackathon 2026 — theme fit (pick a primary; justify in pitch)

| Theme | How EV Grid Oracle aligns |
|------|----------------------------|
| **#3 World modeling (primary)** | **Partially observable** grid + queues + **strict tool-like** actions; rewards come from **simulator + verifier** (`ev_grid_oracle/reward.py`), not from the model grading itself. Optional **world-model head** in training (`SimulationPrediction` + verifier in `training/train_grpo.ipynb`). |
| **#2 Long horizon (primary)** | Multi-step episodes (`reset` / `step` over many ticks), **delayed** stress from **scheduled scenarios** (`ev_grid_oracle/scenarios.py`), recovery from early mistakes visible in replay. |
| **#1 Multi-agent (secondary narrative)** | Not a full multi-LLM MARL stack today; the **reward mixes stakeholder tensions** (wait vs peak vs renewables vs urgency). A credible **stretch** is to pitch **coalition / incentives** (fleet, operator, grid) and reserve explicit multi-agent turns for a follow-on. |
| **#4 Self-improvement** | Scenario curriculum + trap catalog (`docs/judge-kit/trap-catalog.md`) are a hook for **adaptive difficulty**; training can reweight scenarios (future work). |
| **#5 Wild card** | Spatial **Bangalore graph** + **City Ops** demo + paired statistical eval are the differentiated story. |

**Dual framing:** OpenEnv Hackathon + AI for Bharat (BESCOM Theme 9).

### How this maps to judging (40 / 30 / 20 / 10)

| Criterion (weight) | What judges ask | Where we answer |
|--------------------|-----------------|-----------------|
| **Environment innovation (40%)** | Novel, hard to game, tests behavior | Graph routing + **anti-cheat flags**, deterministic **stress scenarios**, Phaser command center + replay (`web/`). |
| **Storytelling (30%)** | Problem → env → what changed → why it matters | This README + [`docs/hf-mini-blog-ev-grid-oracle.md`](docs/hf-mini-blog-ev-grid-oracle.md) + Space demo. |
| **Improvement in rewards / behavior (20%)** | Before vs after, same seeds | **Paired** `training/evaluate.py`, plots below, `training/fair_eval.py` (Wilson + McNemar on `per_episode`). |
| **Reward & pipeline (10%)** | Coherent reward, training hooks env | `ev_grid_oracle/reward.py` breakdown + `training/train_grpo.ipynb` (GRPO + `reward_fn` stepping `EVGridCore`). |

### Why judges will care (fast)
- **It’s verifiable**: every action parsed + validated; reward breakdown logged (anti‑hack by design).
- **It’s visual**: live “city map” with station heat, queues, arrows, HUD.
- **It shows learning**: baseline vs oracle KPIs + reward curves + replayable seeds.

---

## What’s in this repo

- **Environment (this Space)**: FastAPI server exposing `EVGridEnvironment` (OpenEnv interface).
- **Demo UI**: `viz/gradio_demo.py` (baseline vs oracle toggle + streaming “Run 60 ticks”).
- **2D recording**: `viz/city_map.py`, `viz/record_two_phase.py` (baseline → oracle 2‑minute frames).
- **Training**: `training/train_grpo.ipynb` (Colab T4 GRPO with verifier rewards).
- **Evidence**: `training/evaluate.py` (paired seeds + `per_episode` JSON) + `training/fair_eval.py` (Wilson CIs + **McNemar** `paired_mcnemar` + `artifacts/fair_eval_chart.png`) + `training/make_plots.py` → `artifacts/kpi_comparison.png`.
- **Judge kit (repo-specific checklist)**: `docs/judge-kit/credit-assessment-pattern-map.md`
- **HF mini-blog (markdown article in repo)**: `docs/hf-mini-blog-ev-grid-oracle.md`
- **Official hackathon links (OpenEnv + HF Hub + tutorials + papers)**: `docs/hackathon-official-resources.md`
- **Trap catalog (scenarios + verifier flags)**: `docs/judge-kit/trap-catalog.md`
- **Local validation**: `./validate-submission.sh` → `assets/validation_output.txt` (gitignored; see `assets/README.md`)

---

## Quick links (fill these in before submission)

- **OpenEnv Space (env)**: `https://huggingface.co/spaces/NITISHRG15102007/ev-grid-oracle`
- **Live host**: `https://nitishrg15102007-ev-grid-oracle.hf.space`
- **GitHub**: `https://github.com/NITISH-R-G/ev-grid-oracle`
- **Colab (opens `main` notebook on a clean VM)**: `https://colab.research.google.com/github/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb`
- **Notebook source (same file as Colab)**: `https://github.com/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb`
- **HF mini-blog / article (markdown in this repo — paste into a Hub post or link raw)**: `https://github.com/NITISH-R-G/ev-grid-oracle/blob/main/docs/hf-mini-blog-ev-grid-oracle.md`
- **2‑minute video**: TODO (YouTube/HF post link)
- **LoRA repo**: `https://huggingface.co/NITISHRG15102007/ev-oracle-lora`

**Submission tips:** Hugging Face accepts long-form writeups as **markdown in your repo** (see `docs/hf-mini-blog-ev-grid-oracle.md`). Keep the **Colab link** and **GitHub `.ipynb` link** both in the README so judges can open Colab directly or review the notebook on GitHub. The training notebook’s **first code cell clones this repo and `pip install -e .`** so Colab runs stay reproducible.

### Official hackathon resources (OpenEnv + HF + tutorials)

Full list with descriptions: [`docs/hackathon-official-resources.md`](docs/hackathon-official-resources.md).

| Resource | Link |
|----------|------|
| OpenEnv Core (GitHub) | https://github.com/meta-pytorch/OpenEnV |
| OpenEnv docs | https://meta-pytorch.org/OpenEnv/ |
| HF OpenEnv environments | https://huggingface.co/openenv |
| HF OpenEnv Spaces | https://huggingface.co/openenv/spaces |
| Tutorials (tree) | https://github.com/meta-pytorch/OpenEnv/tree/main/tutorial |
| Training examples | https://github.com/meta-pytorch/OpenEnv/tree/main/tutorial/examples |
| Environment examples | https://github.com/meta-pytorch/OpenEnv/tree/main/envs |
| Reward papers | https://arxiv.org/abs/2408.10215 · https://arxiv.org/abs/2601.19100 |

**YouTube (RL envs):** [0airz7BhBiA](https://www.youtube.com/watch?v=0airz7BhBiA) · [ap4q4sAK4OY](https://www.youtube.com/watch?v=ap4q4sAK4OY) · [Jew4lhAiqnw](https://www.youtube.com/watch?v=Jew4lhAiqnw) · [kkCNMz0Ptd8 (live)](https://www.youtube.com/live/kkCNMz0Ptd8?si=JJ7og8x5qc7_Gi0e)

---

## The environment (OpenEnv)

This Space hosts the **OpenEnv‑compatible FastAPI server** for `EVGridEnvironment`.

### Endpoints

- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /schema`
- `GET /health`

### Action format (strict)

The agent must respond in this exact schema (parsed by a deterministic regex):

```text
ACTION: route|defer|load_shift
STATION: BLR-01..BLR-25 or NONE
CHARGE_RATE: slow|fast|ultra_fast
DEFER_MINUTES: integer
REASON: max 20 words
CONFIDENCE: 0.0-1.0
```

### Reward (verifiable + anti‑hack)

Total reward is the sum of components (each logged) in `ev_grid_oracle/reward.py`:
- **wait**: penalize average station wait
- **grid_stress**: penalize overloaded stations (>85% capacity)
- **peak**: penalize feeder load > 80%, bonus below it
- **renewable**: reward green windows
- **urgency**: punish deferring critical EVs
- **anti‑hack**: punish impossible routes / queue piling

---

## Demo + Visualization

### Gradio demo (interactive)

Run locally:

```bash
python -m viz.gradio_demo
```

What judges see:
- map heat (green → red), queue dots, live KPIs
- mode toggle: baseline vs oracle
- **Run 60 ticks** streaming button (looks “alive”)

### Pygame cinematic map (for recording)

```bash
python -m viz.city_map
```

Press **SPACE** to advance simulation ticks.

### 2‑minute screen‑record pipeline (baseline → oracle)

```bash
python -m viz.record_two_phase --seed 123 --out artifacts/frames_2min
```

Then:

```bash
ffmpeg -framerate 30 -i frame_%06d.png -c:v libx264 -pix_fmt yuv420p out.mp4
```

---

## Evidence (baseline vs oracle)

**KPI comparison** (lower wait / stress / violations is better; same episode seeds for both bars — see `training/evaluate.py`):

![Baseline vs Oracle KPIs — mean metrics over paired episodes](artifacts/kpi_comparison.png)

**Paired binary outcomes + Wilson 95% intervals** (from `training/fair_eval.py`; baseline vs oracle on the **same** `per_episode` worlds):

![Paired eval — Wilson intervals on binary rates](artifacts/fair_eval_chart.png)

Regenerate (GPU recommended for real oracle weights):

```bash
export ORACLE_LORA_REPO="NITISHRG15102007/ev-oracle-lora"  # optional; omit or set ORACLE_SKIP_LLM=1 for KPI plumbing only
python training/evaluate.py --episodes 50 --seed 123 --out training/eval_results.json
python training/fair_eval.py --eval-json training/eval_results.json
python training/make_plots.py --eval-json training/eval_results.json --out-dir artifacts
```

`artifacts/fair_eval_results.json` holds **`paired_mcnemar`** (discordant-pair exact p-values) alongside Wilson rates.

Note: On CPU-only machines, loading a 3B model can be slow or fail; set `ORACLE_SKIP_LLM=1` for a fast sanity run, but **use Colab GPU** for the final “evidence of learning” artifacts.

---

## Training (Colab T4)

Open:
- `training/train_grpo.ipynb`

Notes:
- start with 1 epoch + small `num_generations`, then scale
- sample rollouts every N steps to detect reward hacking

> If you’re using LoRA/QLoRA, don’t naively upcast a 4-bit base to 16-bit and “merge” at the end without the correct path — it can badly degrade quality. Save adapters cleanly and test post-training inference immediately.

### Local dev

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

---

## Submission checklist (OpenEnv India 2026 — non‑negotiables)

- [ ] **OpenEnv (current stack):** `openenv.yaml` + `openenv-core` per `pyproject.toml`; env runnable from **HF Space URL** (submit this URL).
- [ ] **Training:** Colab **or** repo path — [`training/train_grpo.ipynb`](training/train_grpo.ipynb) + [Open in Colab](https://colab.research.google.com/github/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb) using **Unsloth / TRL**.
- [ ] **Evidence of real training:** committed **readable plots** (axes interpretable) — KPI + fair eval figures above; link Wandb/Trackio **per run** if you use them.
- [ ] **Writeup:** **HF mini-blog** ([`docs/hf-mini-blog-ev-grid-oracle.md`](docs/hf-mini-blog-ev-grid-oracle.md)) **or** an **under 2 minute** video (YouTube/HF) — **link only** (no large video files in the Space repo).
- [ ] **README:** motivates **problem**, explains **env + reward**, shows **results**, says **why it matters**; includes **Space + Colab + blog/video + LoRA** links (see Quick links).
- [ ] **One submission per team:** freeze the Space URL you give judges; avoid post-deadline reliance on unpinned `main` unless rules allow.

---

## Repo structure

```text
ev-grid-oracle/
├── openenv.yaml
├── pyproject.toml
├── ev_grid_oracle/
├── server/
├── training/
├── viz/
└── artifacts/
```

---

## Demo UI

The Gradio demo is in `viz/gradio_demo.py` (separate Space recommended).

