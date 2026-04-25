---
name: hackathon-self-serve-guide
description: Self-serve guide for OpenEnv hackathon teams to pick a verifiable RL project, build an OpenEnv environment (reset/step/state), design verifier-based rewards, train with TRL (GRPO/RLVR) + Unsloth, and ship a Hugging Face Spaces demo. Use when the user mentions OpenEnv hackathon themes or asks how to go from environment → rewards → RL training → deployment.
---

# Hackathon Self-Serve Guide: Build an RL Environment, Train an LLM, Ship a Demo

## Quick start (default workflow)

When invoked, produce a **single, practical guide** that helps a team go from zero → demo:

- Pick a project idea that is **step-based**, **programmatically verifiable**, and **non-zero success probability**
- Specify the **minimum RL loop** (prompt → action → env/verifier → reward → update)
- Decide **SFT vs RL** (and when to do “light SFT then RL”)
- Design the environment **before** the trainer (obs/actions/termination/reward/anti-cheat)
- Implement the environment using **OpenEnv** (reset/step/state + server wrapper)
- Design **2–4 independent reward functions** + explicit anti-hacking defenses
- Train with **TRL (GRPO/RLVR)** + **Unsloth** (keep inference fast, start tiny)
- Deploy the environment early (Spaces) and ship a demo with **before/after evidence**

If the user references “[External] Apr ‘26 OpenEnv Hackathon Themes” but doesn’t provide the text, ask them to paste the theme bullets they’re targeting, then tailor the “project idea” section to those constraints.

## Output format (what to write back)

Use these headings, in order:

1. **What you are building (stack + artifacts)**
2. **Pick the right project idea (3 properties + examples)**
3. **Minimum RL loop (mental model)**
4. **SFT vs RL decision rule (hackathon default)**
5. **Environment spec (observation/actions/termination/state)**
6. **Reward & verifier design (multiple signals + anti-hack)**
7. **Training stack (TRL GRPO/RLVR + Unsloth)**
8. **Deployment plan (OpenEnv → Spaces)**
9. **1-day execution plan (roles + phases)**
10. **What judges find compelling (evidence checklist)**
11. **Common mistakes to avoid**
12. **Learning resources (links)**

## Content rules (don’t violate)

- **Bias for verifiability**: prefer crisp checks (tests, regex, executors, simulators) over “looks good”.
- **Non-zero success**: if the environment is too hard, add curriculum knobs until early success happens.
- **Multiple rewards**: use at least 2–4 independent reward components (format, correctness, constraints, timeouts).
- **Anti-reward-hacking defaults**:
  - deterministic parsing/validation of actions
  - timeouts and step caps
  - prohibit or detect hidden state mutation / caching / globals (where applicable)
  - log reward breakdown columns and inspect generations regularly
- **Demo requires evidence**: baseline vs trained behavior, measurable metrics, and an explanation of safeguards.

## Recommended “project idea” examples (copy/paste menu)

Offer 3–6 idea patterns; pick the most trainable one unless the user overrides:

- **Code-with-tests**: model writes a function; verifier runs unit tests + style/timeout checks.
- **Grid/route planning**: model proposes a route/dispatch; verifier simulates + checks constraints.
- **Scheduling**: model assigns jobs to resources; verifier checks feasibility + objective value.
- **Game-like puzzles**: step-by-step actions with a simulator and a win condition (short horizon first).

For each pattern, include:
- **Observation** (what the agent sees)
- **Action format** (strict schema)
- **Verifier** (what is checked)
- **Curriculum knobs** (what makes it easier/harder)
- **Primary failure mode** (reward hacking angle + defense)

## Reward design template (use in the guide)

Use this rubric structure:

```text
R_total = w1*R_correct + w2*R_format + w3*R_constraints + w4*R_efficiency + w5*R_safety - w6*R_timeout

R_correct: objective success (tests pass / constraints satisfied / terminal goal)
R_format: strict parseable schema compliance
R_constraints: feasibility (no illegal actions)
R_efficiency: resource/time/steps used (caps + diminishing returns)
R_safety: forbidden operations avoided (sandbox/allowlist)
R_timeout: penalty on timeouts / infinite loops / step cap hits
```

Always add 1–2 explicit anti-cheat checks that are specific to the chosen domain (e.g., “no globals”, “no cached answers”, “no mutation of protected state”).

## Training guidance defaults (hackathon-safe)

- Start with a capable instruct base model; **RL improves behavior**, it doesn’t conjure it from nothing.
- If success rate is ~0, **simplify tasks** or add curriculum until rewards are non-zero.
- Keep rollouts cheap: **inference often dominates runtime**.
- Prefer **verifier-based RL (GRPO/RLVR style)** when you can score outputs programmatically.
- During training, track:
  - overall reward and **each reward column**
  - success rate / timeout rate
  - sampled generations to detect exploitation

## Saving/export warning (must include)

Include this warning verbatim:

> If you’re using LoRA/QLoRA, don’t naively upcast a 4-bit base to 16-bit and “merge” at the end without the correct path — it can badly degrade quality. Save adapters cleanly and test post-training inference immediately.

## Learning resources (links to include)

Include these links (with brief notes):

- Workshop Module 1 (Why OpenEnv?): `https://www.youtube.com/watch?v=1jU05MlENOI&t=482s`
- Workshop Module 2 (Using existing envs): `https://www.youtube.com/watch?v=1jU05MlENOI&t=2133s`
- Workshop Module 3 (Deploying envs): `https://www.youtube.com/watch?v=1jU05MlENOI&t=2585s`
- Workshop Module 4 (Building your own): `https://www.youtube.com/watch?v=1jU05MlENOI&t=2625s`
- Mega Lecture Module 5 (Training + TRL / Wordle GRPO): `https://www.youtube.com/watch?v=Jew4lhAiqnw&t=6800s`

