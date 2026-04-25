# Examples — outputs this skill should generate

## Example: KPI comparison table (README-ready)
```text
Metric                     | Baseline (no AI) | Oracle Agent
---------------------------|------------------|------------
Avg queue wait (min)        | 44               | 14
Grid stress events/episode  | 18               | 3
Peak load exceeded count    | 23               | 2
Renewable utilized (%)      | 31               | 58
Critical EVs stranded       | 7                | 0
Invalid actions (%)         | 0.0              | < 1.0
```

## Example: 2-minute demo screenplay (judge flow)
```text
0:00–0:20 Problem: Bangalore peak + EV surge → queues/grid overload (show baseline sim)
0:20–0:45 Environment: 25 stations, real neighborhoods, BESCOM feeder constraint, renewable curve (show prompt + action)
0:45–1:05 Training evidence: reward curves + component breakdown; highlight before/after
1:05–1:40 Oracle in action: same scenario; routing spread; peak stays <80%; critical EVs prioritized
1:40–2:00 KPI split-screen + links (HF Space, repo, Colab)
```

## Example: dual-submission framing (copy blocks)
### OpenEnv Hackathon framing
```text
We built EVGridEnv, an OpenEnv-compliant RL environment modeling a city-scale EV charging network with procedural demand, multi-term rewards, and explicit reward-hacking defenses. Using GRPO to train a small LLM policy, we reduce queueing and grid-stress events while improving renewable-aligned charging behavior.
```

### AI for Bharat / BESCOM Theme 9 framing
```text
EV Grid Oracle is a demand-response routing system for India’s DISCOM constraints: it flattens feeder peak load, prioritizes critical vehicles, and shifts flexible charging into renewable-heavy windows—without requiring hardware changes. The same architecture generalizes from Bangalore (BESCOM) to any Indian DISCOM with station + feeder telemetry.
```

## Example: “what the agent sees” (prompt snippet)
Use a structured, stable prompt with an explicit response contract and a single pending request (or a clearly delimited batch section).

