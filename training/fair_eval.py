from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """
    Wilson score interval for a binomial proportion.
    Returns (low, high, p_hat). For n==0 returns (nan, nan, nan).
    """
    if n <= 0:
        return (float("nan"), float("nan"), float("nan"))
    phat = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denom
    rad = z * math.sqrt((phat * (1.0 - phat) + z2 / (4.0 * n)) / n) / denom
    return (center - rad, center + rad, phat)


def _binary_keys(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    b0 = rows[0].get("binary") or {}
    return sorted(b0.keys())


def analyze_per_episode(per_episode: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(per_episode)
    out_rates: dict[str, Any] = {}
    for key in _binary_keys(per_episode):
        # Keys are like "baseline_any_peak_violation" — split prefix
        parts = key.split("_", 1)
        if len(parts) < 2:
            continue
        prefix, rest = parts[0], parts[1]
        if prefix not in ("baseline", "oracle"):
            continue
        successes = sum(1 for row in per_episode if (row.get("binary") or {}).get(key))
        lo, hi, phat = wilson_interval(successes, n)
        out_rates[key] = {
            "successes": successes,
            "n": n,
            "p_hat": phat,
            "wilson_low": lo,
            "wilson_high": hi,
        }
    return {"n_episodes": n, "binary_rates": out_rates}


def _paired_improvement_counts(per_episode: list[dict[str, Any]]) -> dict[str, Any]:
    """Operational 'wins' where oracle strictly improves a binary bad outcome vs baseline."""
    n = len(per_episode)
    if n == 0:
        return {}
    improved_peak = 0
    improved_anti = 0
    improved_defer = 0
    improved_stress = 0
    for row in per_episode:
        b = row.get("binary") or {}
        bp = b.get("baseline_any_peak_violation", False)
        op = b.get("oracle_any_peak_violation", False)
        if bp and not op:
            improved_peak += 1
        ba = b.get("baseline_any_anti_cheat", False)
        oa = b.get("oracle_any_anti_cheat", False)
        if ba and not oa:
            improved_anti += 1
        bd = b.get("baseline_any_critical_defer", False)
        od = b.get("oracle_any_critical_defer", False)
        if bd and not od:
            improved_defer += 1
        bs = b.get("baseline_high_stress", False)
        os_ = b.get("oracle_high_stress", False)
        if bs and not os_:
            improved_stress += 1
    def rate(k: int) -> dict[str, float | int]:
        lo, hi, phat = wilson_interval(k, n)
        return {"successes": k, "n": n, "p_hat": phat, "wilson_low": lo, "wilson_high": hi}

    return {
        "oracle_strictly_better_peak_violation_episodes": rate(improved_peak),
        "oracle_strictly_better_anti_cheat_episodes": rate(improved_anti),
        "oracle_strictly_better_critical_defer_episodes": rate(improved_defer),
        "oracle_strictly_better_high_stress_episodes": rate(improved_stress),
    }


def plot_fair_eval(binary_rates: dict[str, Any], out_path: Path) -> None:
    """Bar chart: select headline baseline vs oracle binary rates with Wilson error bars."""
    pairs = [
        ("baseline_any_peak_violation", "oracle_any_peak_violation", "Any peak violation"),
        ("baseline_any_anti_cheat", "oracle_any_anti_cheat", "Any anti-cheat step"),
        ("baseline_any_critical_defer", "oracle_any_critical_defer", "Any critical defer"),
    ]
    labels: list[str] = []
    lows_b: list[float] = []
    highs_b: list[float] = []
    mids_b: list[float] = []
    lows_o: list[float] = []
    highs_o: list[float] = []
    mids_o: list[float] = []

    for bk, ok, title in pairs:
        rb = binary_rates.get(bk)
        ro = binary_rates.get(ok)
        if not rb or not ro:
            continue
        labels.append(title)
        mids_b.append(float(rb["p_hat"]))
        lows_b.append(float(rb["wilson_low"]))
        highs_b.append(float(rb["wilson_high"]))
        mids_o.append(float(ro["p_hat"]))
        lows_o.append(float(ro["wilson_low"]))
        highs_o.append(float(ro["wilson_high"]))

    if not labels:
        return

    x = list(range(len(labels)))
    w = 0.36
    fig = plt.figure(figsize=(10, 4.5))
    ax = fig.add_subplot(111)

    def errs(mids: list[float], lows: list[float], highs: list[float]) -> list[list[float]]:
        return [[m - lo for m, lo in zip(mids, lows)], [hi - m for m, hi in zip(mids, highs)]]

    eb_b = ax.errorbar(
        [i - w / 2 for i in x],
        mids_b,
        yerr=errs(mids_b, lows_b, highs_b),
        fmt="o",
        capsize=4,
        label="Baseline",
        color="#2563eb",
    )
    eb_o = ax.errorbar(
        [i + w / 2 for i in x],
        mids_o,
        yerr=errs(mids_o, lows_o, highs_o),
        fmt="o",
        capsize=4,
        label="Oracle",
        color="#16a34a",
    )
    _ = eb_b, eb_o
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylim(0, min(1.05, max(highs_b + highs_o, default=1.0) * 1.15))
    ax.set_ylabel("Rate (Wilson 95% CI)")
    ax.set_title("EV Grid Oracle — Paired eval: binary outcomes + Wilson intervals")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Wilson CIs + chart from training/eval_results.json (expects per_episode from evaluate.py)."
    )
    ap.add_argument("--eval-json", type=str, default="training/eval_results.json")
    ap.add_argument("--out-json", type=str, default="artifacts/fair_eval_results.json")
    ap.add_argument("--out-chart", type=str, default="artifacts/fair_eval_chart.png")
    args = ap.parse_args()

    data = json.loads(Path(args.eval_json).read_text(encoding="utf-8"))
    per_episode = data.get("per_episode")
    if not isinstance(per_episode, list) or len(per_episode) == 0:
        raise SystemExit(
            "eval JSON missing non-empty 'per_episode'. Run: python -m training.evaluate (paired output)."
        )

    rates_block = analyze_per_episode(per_episode)
    paired = _paired_improvement_counts(per_episode)
    out = {
        "source_eval": args.eval_json,
        "n_episodes": rates_block["n_episodes"],
        "binary_rates_wilson": rates_block["binary_rates"],
        "paired_oracle_improvements_wilson": paired,
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    out_chart = Path(args.out_chart)
    out_chart.parent.mkdir(parents=True, exist_ok=True)
    plot_fair_eval(rates_block["binary_rates"], out_chart)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_chart}")


if __name__ == "__main__":
    main()
