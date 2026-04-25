---
name: openenv-hackathon-env-designer
description: Design OpenEnv-compliant training environments for the OpenEnv Hackathon (India) aligned to themes like multi-agent interactions, long-horizon planning, world modeling, and self-improvement. Use when the user mentions OpenEnv hackathon themes, building an OpenEnv environment, reward design/rubrics, HF Spaces hosting, TRL/Unsloth training scripts, or needs a concrete environment spec + scaffold checklist.
---

# OpenEnv Hackathon Environment Designer

## Quick start (default workflow)

When the user gives theme text (multi-agent / long-horizon / world-modeling / self-improvement / wildcard), produce **one concrete environment** with:

- **Capability target**: what the model should learn (1 sentence)
- **Core loop**: observation → action → transition (3–7 bullets)
- **Partial observability**: what’s hidden, how it’s revealed
- **Actions**: allowed tool/API calls + natural language outputs
- **Rewards**: rubric-style, dense enough to learn, hard to game
- **Eval**: baseline vs trained comparison + plots
- **Packaging**: OpenEnv manifest + HF Spaces plan
- **Training**: minimal TRL/Unsloth script/notebook plan that actually runs

If the request is ambiguous, choose the **most “trainable”** variant (dense signals, short episodes at first, curriculum knobs).

Additional templates:
- See [THEME_TEMPLATES.md](THEME_TEMPLATES.md) for idea patterns per theme.
- See [OPENENV_SUBMISSION_CHECKLIST.md](OPENENV_SUBMISSION_CHECKLIST.md) for “minimum requirements” + packaging.

## Output format (what to write back)

Use this template (headings required; keep it to 1–2 pages):

```markdown
## Environment: <name>

### Why this matters (capability gap)
- ...

### World + episode loop
- **Episode length**: ...
- **Hidden state**: ...
- **Observation**: ...
- **Actions**: ...
- **Transitions**: ...

### Reward (rubric)
- **R_total** = ...
- **Rubric items**:
  - <item>: <signal> (range, frequency), anti-gaming note

### Difficulty & curriculum knobs
- ...

### Evaluation (show improvement)
- **Baselines**: ...
- **Metrics**: ...
- **Plots**: ...

### OpenEnv + HF Spaces packaging plan
- Repo tree:
  - ...
- Demo UX:
  - ...

### Minimal training script plan (TRL/Unsloth)
- ...
```

## Design rules (judging-aligned defaults)

- **Default to “trainability”**: prefer rewards that produce learning curves within hours, not days.
- **Dense feedback, sparse objective**: combine shaping rewards with a terminal objective reward.
- **Anti-gaming**: for every reward component, name a plausible exploit and block it (caps, normalization, counter-metrics, consistency checks).
- **Partial observability is real**: hide key variables; provide noisy/limited probes and logs.
- **Tool use must be necessary**: the environment should require interaction (APIs, simulated tools, dynamic state), not just “answer from prior knowledge”.
- **Evidence beats polish**: make sure the environment can run + train + plot, even if UI is minimal.

## Theme-to-environment mapping heuristics

### Theme 1: Multi-agent interactions
Pick one:
- **Negotiation** (buyer/seller/arbiter) with private values
- **Coalitions** (3–6 agents) with shifting incentives
- **Mixed coop/comp** (shared constraint + individual payoff)

Must-have:
- Private info per agent
- Communication channel(s) with bounded budget
- Mechanism constraints (deadlines, compute budget, limited offers)

### Theme 2: (Super) long-horizon planning & instruction following
Default pattern:
- Break a 200–300 step goal into **checkpoints** and **memory constraints** (e.g., short context windows, periodic “amnesia”, external scratchpad with cost).
- Introduce **recoverability**: allow re-plans but with penalties.

Must-have:
- Delayed rewards + intermediate rubric scores
- State that persists across sessions/episodes (project-style)
- Evaluation that tests “did it finish?” and “did it recover?”

### Theme 3: World modeling (professional / personal)
Default pattern:
- A dynamic system with **latent variables** that drift (queues, deadlines, trust, inventory, hidden constraints).
- Tools produce partial, sometimes inconsistent evidence (logs, emails, tickets).

Must-have:
- Causal interventions (actions change world)
- Observation updates based on outcomes (belief update)
- Consistency scoring (no contradictions across time)

### Theme 4: Self-improvement
Default pattern:
- The agent proposes new tasks/cases; the environment validates and scores them; difficulty auto-scales.

Must-have:
- Curriculum knobs + automatic difficulty adjustment
- “Task quality” rubric (novelty, solvability, non-triviality)
- Overfitting checks (holdout task families)

### Theme 5: Wild card
Rule:
- Keep the environment **runnable + trainable**; novelty is only valuable if you can show improvement.

## What to implement first (tracer bullet)

When asked to “build it”, do this in order:

1. **Single-episode minimal env** with deterministic transitions and a simple rubric.
2. **One exploit test**: show a dumb policy that tries to game the reward; patch it.
3. **Training loop** that runs 50–200 episodes and logs reward.
4. **Curriculum**: add 1–2 knobs and show curves improve.
5. **HF Spaces demo** with a small interactive episode runner + plots.

