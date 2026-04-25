# EV Grid Oracle — “Credit_Assessment-style” Judge Kit Map (Repo-Specific)

This document maps the patterns that make [Nijin-P-S/Credit_Assessment_Env](https://github.com/Nijin-P-S/Credit_Assessment_Env) feel “submission-grade” to **your exact EV_Grid_Oracle codebase**, with **brutally practical** next steps.

Legend:
- **✅ shipped / already exists** in repo today
- **⚠️ partial / exists but not yet judge-bulletproof**
- **❌ missing (high ROI for elite showcases)**

---

## 1) One-glance “exhibit table” (Space + adapters + Colab + video + audit trail)

| Artifact (what judges expect) | EV_Grid_Oracle location today | Status | What to do next (specific) |
|---|---|---:|---|
| Live HF Space | Linked from `README.md` (verify URLs match your canonical Space) | ⚠️ | Add a **single “Evidence”** section in `README.md` mirroring Credit_Assessment’s table: Space, Colab, LoRA, dataset run folder, “headline chart” link. |
| Colab training | `training/train_grpo.ipynb` | ✅ | Add a **1-page “Run order”** at top of notebook: minimum T4 run, expected outputs, where logs land. |
| Adapter weights | Linked from `README.md` / env vars in `training/evaluate.py` | ⚠️ | Publish **date-stamped** adapter repos for ablations (baseline-oracle vs curriculum vs adversarial) like they do—avoid overwrite risk stories. |
| Versioned logs/plots dataset | `artifacts/` + `training/eval_results.json` | ⚠️ | Create a HF Dataset folder per run (like their `run-…`) and commit **only small** JSON/PNGs; link large artifacts. |
| `<2 min` video / blog | `README.md` TODO | ❌ | Minimum: **HF mini-blog** + embed 1 “headline” plot (`artifacts/kpi_comparison.png`). |

---

## 2) “Headline result” packaging (fair eval + statistical hygiene)

Credit_Assessment’s killer move is **head-to-head on identical applicants** + explicit **Wilson CIs** + “which chart is headline vs internal ablation”.

### Where EV eval lives now
- **Episode rollouts + summaries**: `training/evaluate.py`
- **Plots**: `training/make_plots.py` → `artifacts/kpi_comparison.png`

### Status vs judge bar
| Requirement | Current implementation | Status | Next commit |
|---|---|---:|---|
| Same seed pool for both policies | `training/evaluate.py` uses **paired** `episode_seed = seed + i` for baseline and oracle; `per_episode` in JSON | ✅ | Optional: McNemar / bootstrap on paired deltas for significance. |
| Scenario-aware eval | `evaluate.py` CLI `--scenario` (names from `ev_grid_oracle/scenarios.py`) | ✅ | Next: small sweep script or matrix in CI over 2–3 scenarios. |
| Uncertainty / significance | `training/fair_eval.py` → Wilson CIs on `per_episode` binaries + `artifacts/fair_eval_chart.png` | ✅ | Extend with paired tests (McNemar) if reviewers ask. |
| Reward breakdown evidence | `ev_grid_oracle/reward.py` + `EVGridObservation.reward_breakdown` | ✅ | Extend eval to log **mean/std** of each breakdown component per policy (not only KPI aggregates). |

---

## 3) Trap library + adversarial curriculum (their `ADVERSARIAL_STRATEGIES`)

### Where EV “traps/scenarios” live now
- **Deterministic scenario schedules**: `ev_grid_oracle/scenarios.py`
- **Scenario application + sticky modifiers**: `ev_grid_oracle/env.py`
- **Anti-cheat flags**: `ev_grid_oracle/reward.py` + `EVGridObservation.anti_cheat_*` in `ev_grid_oracle/models.py`
- **Demo surfacing**: `server/app.py` (`scenario_schedule`, `scenario_events_at_tick`, `anti_cheat_*`, `role_*`)

### Status
| Pattern | EV analog | Status | Next commit |
|---|---|---:|---|
| Named trap IDs | scenario types + anti-cheat flags | ⚠️ | Add `docs/judge-kit/trap-catalog.md` listing **10–15** traps with: trigger condition, expected oracle behavior, reward components touched, example seed. |
| Trap-weighted training | not wired into `training/train_grpo.ipynb` yet | ❌ | Export a `trap_id` field into training logs; add “worst trap histogram” → reweight sampling (their `AdversarialTracker` idea). |
| “Can’t collapse strategy” argument | asymmetric costs exist (`reward.py`) | ⚠️ | Add **empirical collapse tests**: always-defer / always-load-shift / always-route-nearest policies as extra baselines in eval. |

---

## 4) Demo UX that feels “product”, not “debug UI”

### Where EV demo lives
- **Phaser command center**: `web/src/main.ts`, `web/src/phaser/startCommandCenter.ts`, `web/src/phaser/PixelCityScene.ts`, `web/src/style.css`
- **Demo API**: `server/app.py` (`/demo/new`, `/demo/step`, optional forced replay path)
- **Client API typings**: `web/src/evgrid/api.ts`

### Status
| UX element | EV status | Notes / next |
|---|---:|---|
| Split-screen A/B | ✅ | Keep; it’s a differentiator vs text-only finance demos. |
| Deterministic replay | ✅ (client records actions + replays) | Next: add **server-side frame store** if you want cross-device replay + judge auditing without localStorage assumptions. |
| “Why penalty” overlays | ⚠️ | Add a compact HUD chip: top 2 `reward_breakdown` deltas + `anti_cheat_flags` (strings already returned). |
| Accessibility | ❌ | Keyboard controls for scrubber; reduce CRT intensity toggle. |

---

## 5) Engineering hygiene table (what elite repos show off)

Credit_Assessment advertises tests, validator output, client/server separation.

### EV map
| Hygiene item | EV location | Status | Next |
|---|---|---:|---|
| Unit tests | `tests/` (`test_reward.py`, `test_demo_api.py`, …) | ✅ | Add tests for **scenario schedule determinism** + paired eval seeds once `evaluate.py` changes. |
| “validate submission” script | not present | ❌ | Add `validate-submission.sh` (docker build + pytest + `openenv` validate if applicable). |
| Training vs demo API drift | `server/app.py` vs `server/ev_grid_environment.py` vs `EVGridCore` | ⚠️ | Document “source of truth”: OpenEnv `/step` vs demo `/demo/step`—judges hate ambiguity. |

---

## 6) Highest ROI “next 10 commits” (ordered)

1. ~~**Fix paired evaluation seeds** in `training/evaluate.py`~~ (done: `paired_same_world` + `per_episode`).
2. ~~Add `training/fair_eval.py` + **Wilson CIs**~~ (done: `artifacts/fair_eval_results.json` + `fair_eval_chart.png`).
3. Add `docs/judge-kit/trap-catalog.md` + link from `README.md` “Evidence”.
4. Extend eval to **scenario sweep** (`--scenario`) aligned with `ev_grid_oracle/scenarios.py`.
5. Log **reward breakdown means** in eval JSON (not just KPI averages).
6. Add `validate-submission.sh` + `assets/validation_output.txt` pattern.
7. Add “collapse baselines” policies to `ev_grid_oracle/policies.py` + eval them.
8. Notebook top: “minimum run + expected artifacts” in `training/train_grpo.ipynb`.
9. HF Dataset publish script (small) under `tools/publish_eval_bundle.py` (optional but huge judge UX).
10. Record **15–30s vertical clip** showing scenario + scrub replay + anti-cheat callout.

---

## Brutal honesty: your current edge vs Credit_Assessment

**You can beat them on “spatial world + operator replay + grid stress drama.”**  
They win on **statistical packaging + trap library narrative + audit trail habit**.

Do (1)+(2)+(3) above and you’re competing in the same “judge trust” league—while keeping the EV demo advantage they can’t trivially clone.
