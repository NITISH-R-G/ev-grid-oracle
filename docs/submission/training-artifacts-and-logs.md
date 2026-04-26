# Training artifacts, logs, and what judges should open

This page is the **single checklist** for “we shared the env, training scripts, and training logs” before you freeze the submission.

---

## 1) Environment (shared, runnable)

| Artifact | URL / path |
|----------|------------|
| **HF Space (OpenEnv server)** | See root [`README.md`](../../README.md) → *Quick links* → OpenEnv Space + live host |
| **OpenEnv descriptor** | [`openenv.yaml`](../../openenv.yaml) |
| **Server entry** | `server/app.py` (FastAPI) |
| **Core env + rewards** | `ev_grid_oracle/` (`reward.py`, `road_env.py`, scenarios, etc.) |

Judges should be able to open the Space, hit `/health`, and use `/reset` + `/step` (and `/road/*` if you demo graph routing).

---

## 2) Training scripts (required)

| Script | Role |
|--------|------|
| **[`training/train_grpo.ipynb`](../../training/train_grpo.ipynb)** | **Primary:** Colab-ready GRPO + Unsloth + verifier `reward_fn` stepping `RoadCore` |
| [`training/evaluate.py`](../../training/evaluate.py) | Paired baseline vs oracle → `training/eval_results.json` |
| [`training/fair_eval.py`](../../training/fair_eval.py) | Wilson + McNemar on paired episodes → `artifacts/fair_eval_results.json` + chart |
| [`training/make_plots.py`](../../training/make_plots.py) | Figure pack under `artifacts/` |

**Colab (opens same notebook as GitHub):** linked from [`README.md`](../../README.md) → *Quick links*.

---

## 3) Training logs (what “logs” means here)

Hackathon reviewers usually want **evidence the trainer ran**, not only final weights.

### A) GRPO / TRL run directory (`output_dir`)

In [`training/train_grpo.ipynb`](../../training/train_grpo.ipynb), `GRPOConfig` sets `output_dir` (default: `ev_oracle_grpo_road`). After a real GPU run you should have:

- **`trainer_state.json`** — step, epoch, RNG state snapshot  
- **`events.out.tfevents.*`** — TensorBoard scalars (reward, loss, LR, etc.) if `report_to` includes `"tensorboard"`  
- **`checkpoint-*`** folders — optional; often **too large** to commit; keep on Drive / Hub run artifact instead  

**What to commit for judges (pick one or more):**

1. **TensorBoard PNGs** — open TensorBoard on the run folder, screenshot *reward* and *loss* curves with **labeled axes**, save as e.g. `artifacts/grpo_reward_mean.png`, `artifacts/grpo_loss.png`, and commit.  
2. **Short text log** — paste the last ~50 lines of Colab output (step, reported reward) into `artifacts/training_logs/colab_console_tail.txt` (create the folder).  
3. **Hub / W&B / Trackio** — if you log to a hosted run, add the **run URL** to [`README.md`](../../README.md) *Quick links*.

### B) Eval / verification “logs” (already repo-friendly)

These are JSON + PNG and are strong evidence even without GRPO TensorBoard:

- `training/eval_results.json` (from `evaluate.py`)  
- `artifacts/fair_eval_results.json` + `artifacts/fair_eval_chart.png`  
- Full gallery from `make_plots.py` under `artifacts/` (see README)

---

## 4) Last push before packaging (order)

1. **Space green** — `/health`, UI `/ui/`, one scripted `reset`/`step` smoke test.  
2. **One real Colab GRPO run** — enable TensorBoard (`report_to`), save adapters, **test inference** immediately after save.  
3. **Export curves or console tail** → commit under `artifacts/` or `artifacts/training_logs/` (small text only if no PNG yet).  
4. **Refresh eval JSON + plots** — same seeds, baseline vs oracle, commit deltas judges can read.  
5. **Links** — README *Quick links*: Space, Colab, LoRA repo, blog, **video URL** (when ready).  
6. **Video or blog** — use [`youtube-under-2min-outline.md`](youtube-under-2min-outline.md); HF mini-blog source is [`docs/hf-mini-blog-ev-grid-oracle.md`](../hf-mini-blog-ev-grid-oracle.md).

---

## 5) LoRA / QLoRA (verbatim)

> If you’re using LoRA/QLoRA, don’t naively upcast a 4-bit base to 16-bit and “merge” at the end without the correct path — it can badly degrade quality. Save adapters cleanly and test post-training inference immediately.

---

## 6) Do not commit

- Huge checkpoints, full `node_modules`, raw multi-GB OSM extracts (see root `.gitignore`).  
- Secrets (Hub tokens, `.env`). Use Space **Secrets** for runtime keys only.
