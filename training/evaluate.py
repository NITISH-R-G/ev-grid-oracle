from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from statistics import mean
from typing import Optional

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction, GridState
from ev_grid_oracle.policies import baseline_policy


@dataclass(frozen=True, slots=True)
class EpisodeMetrics:
    avg_wait: float
    grid_stress_events: int
    peak_violations: int
    renewable_mean: float
    critical_deferred: int


def _first_ev_id(state: GridState) -> Optional[str]:
    return state.pending_evs[0].ev_id if state.pending_evs else None


def run_episode(env: EVGridCore, *, policy: str, seed: int) -> EpisodeMetrics:
    obs = env.reset(seed=seed)
    graph = env.city_graph

    waits = []
    grid_stress = 0
    peak_violations = 0
    renewable = []
    critical_deferred = 0

    for _ in range(env.max_steps):
        state = obs.state
        waits.append(mean([s.avg_wait_minutes for s in state.stations]))
        grid_stress += sum(1 for s in state.stations if (s.occupied_slots / max(1, s.total_slots)) > 0.85)
        peak_violations += 1 if state.grid_load_pct > 0.80 else 0
        renewable.append(state.renewable_pct)

        if not state.pending_evs:
            action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        else:
            if policy == "baseline":
                action = baseline_policy(state, graph)
            else:
                # placeholder: oracle policy will be wired to LLM later.
                action = baseline_policy(state, graph)

            if action.action_type == ActionType.defer and state.pending_evs[0].battery_pct_0_100 < 15.0:
                critical_deferred += 1

        obs = env.step(action)
        if obs.done:
            break

    return EpisodeMetrics(
        avg_wait=float(mean(waits)) if waits else 0.0,
        grid_stress_events=int(grid_stress),
        peak_violations=int(peak_violations),
        renewable_mean=float(mean(renewable)) if renewable else 0.0,
        critical_deferred=int(critical_deferred),
    )


def summarize(metrics: list[EpisodeMetrics]) -> dict:
    return {
        "avg_wait_minutes": mean([m.avg_wait for m in metrics]),
        "grid_stress_events": mean([m.grid_stress_events for m in metrics]),
        "peak_violations": mean([m.peak_violations for m in metrics]),
        "renewable_mean": mean([m.renewable_mean for m in metrics]),
        "critical_deferred": mean([m.critical_deferred for m in metrics]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=50)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--out", type=str, default="training/eval_results.json")
    args = ap.parse_args()

    graph = build_city_graph()
    env = EVGridCore(city_graph=graph)

    baseline = [run_episode(env, policy="baseline", seed=args.seed + i) for i in range(args.episodes)]
    oracle = [run_episode(env, policy="oracle", seed=args.seed + 10_000 + i) for i in range(args.episodes)]

    out = {
        "episodes": args.episodes,
        "baseline": summarize(baseline),
        "oracle": summarize(oracle),
        "note": "oracle currently uses baseline policy (LLM wiring pending).",
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

