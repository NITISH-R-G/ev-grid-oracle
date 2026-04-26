# Under–2 minute video outline (EV Grid Oracle)

Use this as a **shot list** so recording stays under the hackathon cap. Link the final URL only in [`README.md`](../../README.md) (do not commit large video files to the Space repo).

---

## 0:00–0:15 — Problem (why judges care)

- **VO:** Bangalore-style EV dispatch: queues, feeder stress, renewables.  
- **Visual:** Space UI `/ui/` — map + station heat or queue dots (static frame OK).  
- **One line:** “We need policies that pass a **simulator + verifier**, not slide decks.”

## 0:15–0:35 — Environment + verification

- **VO:** OpenEnv-style API: `reset` / `step`, strict action text (`CURRENT_NODE` / `NEXT_NODE` …).  
- **Visual:** README action schema snippet **or** browser DevTools showing `POST /road/step` JSON.  
- **VO:** Reward is **decomposed** (wait, stress, anti-cheat flags) — point to `ev_grid_oracle/reward.py` in GitHub tab if screen-recording IDE.

## 0:35–0:55 — Training + evidence

- **VO:** Colab + TRL **GRPO** + Unsloth; notebook clones repo and installs package.  
- **Visual:** Colab file list showing `train_grpo.ipynb` **or** TensorBoard reward curve PNG from `artifacts/`.  
- **VO:** Paired eval: same seed, baseline vs oracle; Wilson / McNemar in `fair_eval_results.json`.

## 0:55–1:15 — Demo punchline

- **Visual:** Space: toggle baseline vs oracle **or** “Run N ticks” / Judge Mode if MA is your story.  
- **VO:** One metric that moved (e.g. mean wait, stress ticks) — **numbers on screen**.

## 1:15–1:45 — Trust + ship

- **VO:** Anti-hack flags, timeouts, LoRA saved as adapters + inference tested.  
- **Visual:** Quick links slide or README: **Space · Colab · GitHub · LoRA repo**.  
- **Optional:** 5s QR or URL paste for judges.

## 1:45–2:00 — Close

- **VO:** “EV Grid Oracle — verifiable RL on a grid ops world.”  
- **Visual:** Logo or repo name + hackathon tagline.

---

## Production tips

- **Record at 1080p**, export **1080p or 720p** MP4; upload to **YouTube (unlisted)** or HF dataset/post.  
- **Captions:** YouTube auto-captions + fix “GRPO”, “OpenEnv”, “BESCOM”.  
- **Audio:** quiet room; if no mic, use captions + on-screen text only (still acceptable for many judges).  
- **Alt:** Turn [`docs/hf-mini-blog-ev-grid-oracle.md`](../hf-mini-blog-ev-grid-oracle.md) into a **HF Space discussion / blog post** and link that instead of video if you run out of time.
