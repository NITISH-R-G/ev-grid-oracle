---
title: "EV Grid Oracle — verifiable GRPO on a Bangalore EV dispatch world"
emoji: ⚡
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

# EV Grid Oracle — verifiable GRPO on a Bangalore EV dispatch world

**TL;DR:** We built an **OpenEnv**-style environment that simulates EV charging stress on a city graph, exposed it on **Hugging Face Spaces**, and trained a small **Qwen2.5‑3B** policy with **TRL GRPO** using **verifier-style rewards** (strict action schema + reward breakdown + anti-cheat flags). Judges can replay **paired** baseline vs oracle episodes on the **same seeds** and read **Wilson + McNemar** summaries from `training/fair_eval.py`.

---

## The problem

Operators route EVs to stations under **queues**, **feeder stress**, and **renewable variability**. A language model should output **structured actions** that the simulator can check—not hand-wavy prose.

---

## What we shipped

| Piece | Where |
|--------|--------|
| Environment + FastAPI Space | Repo `server/`, Space linked from `README.md` |
| Deterministic stress scenarios | `ev_grid_oracle/scenarios.py` |
| Verifier rewards + anti-cheat | `ev_grid_oracle/reward.py`, flags on `EVGridObservation` |
| Phaser “City Ops” demo + replay | `web/` |
| Paired eval + Wilson + McNemar | `training/evaluate.py`, `training/fair_eval.py` |
| Trap catalog (for judges) | `docs/judge-kit/trap-catalog.md` |

---

## Training (Colab + TRL + Unsloth)

- **Runnable notebook:** open from GitHub or Colab:  
  [training/train_grpo.ipynb](https://github.com/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb)  
  [Open in Colab](https://colab.research.google.com/github/NITISH-R-G/ev-grid-oracle/blob/main/training/train_grpo.ipynb)

The first notebook cell **clones this repository** and runs `pip install -e .` so `import ev_grid_oracle` works on a clean Colab VM. Use **GPU runtime (T4+)** before running Unsloth / GRPO cells.

---

## Evidence judges can trust

1. Run `python training/evaluate.py` → JSON includes **`paired_same_world`** and **`per_episode`** rows.  
2. Run `python training/fair_eval.py` → **`artifacts/fair_eval_results.json`** includes **`binary_rates_wilson`** and **`paired_mcnemar`**.  
3. Plots: `python training/make_plots.py` → `artifacts/kpi_comparison.png`.

---

## LoRA / QLoRA warning (verbatim)

> If you're using LoRA/QLoRA, don't naively upcast a 4-bit base to 16-bit and "merge" at the end without the correct path — it can badly degrade quality. Save adapters cleanly and test post-training inference immediately.

---

## Links (canonical)

- **GitHub:** `https://github.com/NITISH-R-G/ev-grid-oracle`  
- **Space / live URL:** see root `README.md` → Quick links (keep in sync with your HF account).

---

*This file lives in the environment repository so you can **copy it into a Hugging Face Space blog post**, **link the raw GitHub file** from your model card, or **mirror** it on `huggingface.co/blog` with minimal edits.*
