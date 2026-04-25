from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-json", type=str, default="training/eval_results.json")
    ap.add_argument("--out-dir", type=str, default="artifacts")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(Path(args.eval_json).read_text(encoding="utf-8"))
    b = data.get("baseline", {})
    o = data.get("oracle", {})

    metrics = [
        "avg_wait_minutes",
        "grid_stress_events",
        "peak_violations",
        "renewable_mean",
        "critical_deferred",
        "anti_cheat_steps",
    ]
    labels = [
        "Avg wait (min)",
        "Stress events",
        "Peak violations",
        "Renewable mean",
        "Critical deferred",
        "Anti-cheat steps",
    ]

    bvals = [float(b.get(m, 0.0)) for m in metrics]
    ovals = [float(o.get(m, 0.0)) for m in metrics]

    fig = plt.figure(figsize=(10, 4))
    ax = fig.add_subplot(111)

    x = list(range(len(metrics)))
    w = 0.38
    ax.bar([i - w / 2 for i in x], bvals, width=w, label="Baseline")
    ax.bar([i + w / 2 for i in x], ovals, width=w, label="Oracle")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_title("EV Grid Oracle — Baseline vs Oracle KPIs")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()

    fig.tight_layout()
    out = out_dir / "kpi_comparison.png"
    fig.savefig(out, dpi=180)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

