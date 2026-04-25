# OpenEnv Hackathon submission checklist (practical)

## Minimum requirements (non-negotiable)
- Use **OpenEnv** (latest release)
- Provide a **training script/notebook** using **Unsloth** or **Hugging Face TRL** (Colab-friendly)
- Show **real training evidence** (reward curve / loss curve, baseline vs trained)
- Publish a short **mini-blog** (HF post) or **<2 minute video**; link from README
- Host the environment on **Hugging Face Spaces**
- README includes:
  - motivation (capability gap)
  - how env works (obs/actions/reward)
  - results (plots + before/after)
  - links to Space + blog/video + runs

## Engineering table-stakes
- Use OpenEnv’s base classes properly (`Environment` / `MCPEnvironment` as appropriate)
- Respect client/server separation (clients should not import server internals)
- Provide standard loop semantics (`reset`, `step`, `state`)
- Include `openenv.yaml` manifest
- Don’t use reserved tool names (`reset`, `step`, `state`, `close`) for MCP tools

## Trainability checklist (to actually get curves)
- Start with **short episodes** and a **dense rubric**
- Add at least 1 **curriculum knob** (difficulty, noise, budget, episode length)
- Log per-episode metrics in a simple format (CSV/JSONL) + plot to PNG committed to repo
- Include at least one “exploit policy” test to harden reward against gaming

## HF Spaces checklist (demo UX)
- Provide a minimal UI:
  - run 1 episode
  - show observation/action transcript
  - show latest reward breakdown
  - show training curves images (static is fine)
- Keep repo size small; link to videos/runs instead of committing large media

