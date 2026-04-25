from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean
from typing import Any

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction
from ev_grid_oracle.oracle_agent import OracleAgent
from ev_grid_oracle.policies import baseline_policy
from ev_grid_oracle.scenarios import ScenarioName


@dataclass(frozen=True, slots=True)
class EpisodeMetrics:
    avg_wait: float
    grid_stress_events: int
    peak_violations: int
    renewable_mean: float
    critical_deferred: int
    anti_cheat_steps: int
    reward_breakdown_mean: dict[str, float] = field(default_factory=dict)


def _episode_metrics_to_json(m: EpisodeMetrics) -> dict[str, Any]:
    return {
        "avg_wait": m.avg_wait,
        "grid_stress_events": m.grid_stress_events,
        "peak_violations": m.peak_violations,
        "renewable_mean": m.renewable_mean,
        "critical_deferred": m.critical_deferred,
        "anti_cheat_steps": m.anti_cheat_steps,
        "reward_breakdown_mean": dict(m.reward_breakdown_mean),
    }


def run_episode(
    env: EVGridCore,
    *,
    policy: str,
    seed: int,
    scenario: ScenarioName = "baseline",
    oracle_repo: str | None = None,
) -> EpisodeMetrics:
    obs = env.reset(seed=seed, scenario=scenario)
    graph = env.city_graph
    oracle = None
    if policy == "oracle":
        if os.getenv("ORACLE_SKIP_LLM", "").strip() not in ("", "0", "false", "False"):
            oracle = OracleAgent(lora_repo_id=None)
        else:
            oracle = OracleAgent(lora_repo_id=(oracle_repo or "").strip() or None)

    waits = []
    grid_stress = 0
    peak_violations = 0
    renewable = []
    critical_deferred = 0
    anti_cheat_steps = 0

    rb_sums: dict[str, float] = defaultdict(float)
    rb_steps = 0

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
                action = oracle.act(state, obs.prompt, graph) if oracle else baseline_policy(state, graph)

            if action.action_type == ActionType.defer and state.pending_evs[0].battery_pct_0_100 < 15.0:
                critical_deferred += 1

        obs = env.step(action)
        if obs.anti_cheat_flags:
            anti_cheat_steps += 1
        rb = obs.reward_breakdown
        for k, v in rb.items():
            ks = str(k)
            if ks == "total" or ks.startswith("_"):
                continue
            rb_sums[ks] += float(v)
        rb_steps += 1
        if obs.done:
            break

    rb_mean: dict[str, float] = {}
    if rb_steps > 0:
        rb_mean = {k: rb_sums[k] / rb_steps for k in sorted(rb_sums.keys())}

    return EpisodeMetrics(
        avg_wait=float(mean(waits)) if waits else 0.0,
        grid_stress_events=int(grid_stress),
        peak_violations=int(peak_violations),
        renewable_mean=float(mean(renewable)) if renewable else 0.0,
        critical_deferred=int(critical_deferred),
        anti_cheat_steps=int(anti_cheat_steps),
        reward_breakdown_mean=rb_mean,
    )


def summarize(metrics: list[EpisodeMetrics]) -> dict[str, float]:
    return {
        "avg_wait_minutes": mean([m.avg_wait for m in metrics]),
        "grid_stress_events": mean([m.grid_stress_events for m in metrics]),
        "peak_violations": mean([m.peak_violations for m in metrics]),
        "renewable_mean": mean([m.renewable_mean for m in metrics]),
        "critical_deferred": mean([m.critical_deferred for m in metrics]),
        "anti_cheat_steps": mean([m.anti_cheat_steps for m in metrics]),
    }


def summarize_reward_breakdown(metrics: list[EpisodeMetrics]) -> dict[str, float]:
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for m in metrics:
        for k, v in m.reward_breakdown_mean.items():
            sums[k] += float(v)
            counts[k] += 1
    return {k: sums[k] / counts[k] for k in sorted(sums.keys()) if counts[k]}


SCENARIO_CHOICES: tuple[str, ...] = (
    "baseline",
    "heatwave_peak",
    "festival_surge",
    "transformer_derate",
    "station_outage",
    "tariff_shock",
)


def main():
    ap = argparse.ArgumentParser(description="Paired baseline vs oracle rollouts (same seed + scenario per episode).")
    ap.add_argument("--episodes", type=int, default=50)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument(
        "--scenario",
        type=str,
        default="baseline",
        choices=SCENARIO_CHOICES,
        help="Deterministic scenario schedule (see ev_grid_oracle/scenarios.py).",
    )
    ap.add_argument("--out", type=str, default="training/eval_results.json")
    args = ap.parse_args()

    scenario: ScenarioName = args.scenario  # type: ignore[assignment]

    graph = build_city_graph()
    env = EVGridCore(city_graph=graph)

    oracle_repo = os.getenv("ORACLE_LORA_REPO", "").strip() or None

    baseline_runs: list[EpisodeMetrics] = []
    oracle_runs: list[EpisodeMetrics] = []
    per_episode: list[dict[str, Any]] = []

    for i in range(args.episodes):
        episode_seed = args.seed + i
        b = run_episode(env, policy="baseline", seed=episode_seed, scenario=scenario, oracle_repo=oracle_repo)
        o = run_episode(env, policy="oracle", seed=episode_seed, scenario=scenario, oracle_repo=oracle_repo)
        baseline_runs.append(b)
        oracle_runs.append(o)

        per_episode.append(
            {
                "episode_index": i,
                "episode_seed": episode_seed,
                "scenario": scenario,
                "baseline": _episode_metrics_to_json(b),
                "oracle": _episode_metrics_to_json(o),
                "binary": {
                    "baseline_any_peak_violation": b.peak_violations > 0,
                    "oracle_any_peak_violation": o.peak_violations > 0,
                    "baseline_any_anti_cheat": b.anti_cheat_steps > 0,
                    "oracle_any_anti_cheat": o.anti_cheat_steps > 0,
                    "baseline_any_critical_defer": b.critical_deferred > 0,
                    "oracle_any_critical_defer": o.critical_deferred > 0,
                    "baseline_high_stress": b.grid_stress_events > int(env.max_steps * 0.25),
                    "oracle_high_stress": o.grid_stress_events > int(env.max_steps * 0.25),
                },
            }
        )

    out = {
        "episodes": args.episodes,
        "seed": args.seed,
        "scenario": scenario,
        "paired_same_world": True,
        "baseline": summarize(baseline_runs),
        "oracle": summarize(oracle_runs),
        "baseline_reward_breakdown_mean": summarize_reward_breakdown(baseline_runs),
        "oracle_reward_breakdown_mean": summarize_reward_breakdown(oracle_runs),
        "per_episode": per_episode,
        "note": "Per-episode: identical episode_seed for baseline and oracle. Oracle uses ORACLE_LORA_REPO if set; "
        "ORACLE_SKIP_LLM forces baseline policy inside oracle path.",
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
