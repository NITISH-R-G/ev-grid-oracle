from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def _boxplot_compat(ax: Any, data: list[list[float]], names: list[str]) -> None:
    try:
        ax.boxplot(data, tick_labels=names)
    except TypeError:
        ax.boxplot(data, labels=names)  # type: ignore[call-arg]


def _per_episode_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("per_episode")
    return rows if isinstance(rows, list) else []


def plot_kpi_bars(data: dict[str, Any], out_dir: Path) -> Path:
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

    fig, ax = plt.subplots(figsize=(11, 4.2))
    x = list(range(len(metrics)))
    w = 0.38
    ax.bar([i - w / 2 for i in x], bvals, width=w, label="Baseline", color="#2563eb", edgecolor="white", linewidth=0.5)
    ax.bar([i + w / 2 for i in x], ovals, width=w, label="Oracle", color="#16a34a", edgecolor="white", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=22, ha="right")
    ax.set_ylabel("Mean over paired episodes")
    ax.set_title(
        "Baseline vs Oracle — aggregate KPIs (same seed per episode)\n"
        f"scenario={data.get('scenario', '?')}, n={data.get('episodes', '?')}, seed_base={data.get('seed', '?')}"
    )
    ax.grid(axis="y", alpha=0.28)
    ax.legend(loc="upper right")
    fig.tight_layout()
    out = out_dir / "kpi_comparison.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_episode_trajectories(rows: list[dict[str, Any]], data: dict[str, Any], out_dir: Path) -> Path | None:
    if not rows:
        return None
    idx = [r["episode_index"] for r in rows]
    b_wait = [float(r["baseline"]["avg_wait"]) for r in rows]
    o_wait = [float(r["oracle"]["avg_wait"]) for r in rows]
    b_peak = [float(r["baseline"]["peak_violations"]) for r in rows]
    o_peak = [float(r["oracle"]["peak_violations"]) for r in rows]
    b_stress = [float(r["baseline"]["grid_stress_events"]) for r in rows]
    o_stress = [float(r["oracle"]["grid_stress_events"]) for r in rows]

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    titles = [
        ("Avg station wait (min)", b_wait, o_wait),
        ("Peak-violation ticks (grid >80%)", b_peak, o_peak),
        ("High-stress station-ticks (>85% full)", b_stress, o_stress),
    ]
    for ax, (title, bv, ov) in zip(axes, titles):
        ax.plot(idx, bv, label="Baseline", color="#2563eb", alpha=0.85, linewidth=1.4)
        ax.plot(idx, ov, label="Oracle", color="#16a34a", alpha=0.85, linewidth=1.4)
        ax.set_ylabel(title.split("(")[0].strip())
        ax.grid(alpha=0.25)
        ax.legend(loc="upper right", fontsize=9)
    axes[0].set_title("Per-episode trajectories (paired worlds — lines should diverge when LoRA is active)")
    axes[-1].set_xlabel("Episode index")
    fig.tight_layout()
    out = out_dir / "eval_episode_trajectories.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_delta_histograms(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    if not rows:
        return None
    d_wait = [float(r["oracle"]["avg_wait"]) - float(r["baseline"]["avg_wait"]) for r in rows]
    d_peak = [float(r["oracle"]["peak_violations"]) - float(r["baseline"]["peak_violations"]) for r in rows]
    d_stress = [float(r["oracle"]["grid_stress_events"]) - float(r["baseline"]["grid_stress_events"]) for r in rows]

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, vals, title in zip(
        axes,
        [d_wait, d_peak, d_stress],
        ["Δ Avg wait (oracle − baseline)", "Δ Peak ticks", "Δ Stress ticks"],
    ):
        ax.hist(vals, bins=min(20, max(5, len(rows) // 3)), color="#7c3aed", edgecolor="white", alpha=0.88)
        ax.axvline(0.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.set_ylabel("Episodes")
    fig.suptitle("Paired deltas per episode — mass left of 0 means oracle is better (lower wait / fewer violations)")
    fig.tight_layout()
    out = out_dir / "eval_delta_histograms.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_reward_breakdown(data: dict[str, Any], out_dir: Path) -> Path | None:
    bb = data.get("baseline_reward_breakdown_mean") or {}
    ob = data.get("oracle_reward_breakdown_mean") or {}
    if not bb or not ob:
        return None
    keys = sorted(set(bb.keys()) & set(ob.keys()))
    keys = [k for k in keys if k not in ("no_pending",) and not str(k).startswith("_")]
    if not keys:
        return None
    y = list(range(len(keys)))
    bv = [float(bb[k]) for k in keys]
    ov = [float(ob[k]) for k in keys]

    fig, ax = plt.subplots(figsize=(10, max(4.0, 0.35 * len(keys))))
    h = 0.35
    ax.barh([i - h / 2 for i in y], bv, height=h, label="Baseline", color="#2563eb")
    ax.barh([i + h / 2 for i in y], ov, height=h, label="Oracle", color="#16a34a")
    ax.set_yticks(y)
    ax.set_yticklabels(keys)
    ax.set_xlabel("Mean per-step reward component (episode average, then mean over episodes)")
    ax.set_title("Reward breakdown — verifier components (paired eval)")
    ax.axvline(0.0, color="black", linewidth=0.6, alpha=0.5)
    ax.legend()
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    out = out_dir / "eval_reward_breakdown_bars.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_boxplots(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    if not rows:
        return None
    series = [
        ("Avg wait (min)", "avg_wait", False),
        ("Peak ticks", "peak_violations", False),
        ("Stress ticks", "grid_stress_events", False),
        ("Renewable mean", "renewable_mean", True),
        ("Anti-cheat steps", "anti_cheat_steps", False),
    ]
    fig, axes = plt.subplots(1, len(series), figsize=(14, 3.8))
    for ax, (label, key, higher_better) in zip(axes, series):
        b = [float(r["baseline"][key]) for r in rows]
        o = [float(r["oracle"][key]) for r in rows]
        _boxplot_compat(ax, [b, o], ["Baseline", "Oracle"])
        ax.set_title(label + ("\n(higher better)" if higher_better else "\n(lower better)"))
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Distribution over episodes — spread shows world variance; separation shows learning")
    fig.tight_layout()
    out = out_dir / "eval_boxplots_by_policy.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_oracle_win_rates(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    if not rows:
        return None
    n = len(rows)

    def rate(lower_is_win: bool, bf: str, of: str) -> float:
        wins = 0
        for r in rows:
            b, o = float(r["baseline"][bf]), float(r["oracle"][of])
            if lower_is_win and o < b - 1e-9:
                wins += 1
            if not lower_is_win and o > b + 1e-9:
                wins += 1
        return 100.0 * wins / n

    items = [
        ("Oracle lower wait", rate(True, "avg_wait", "avg_wait")),
        ("Oracle fewer peak ticks", rate(True, "peak_violations", "peak_violations")),
        ("Oracle fewer stress ticks", rate(True, "grid_stress_events", "grid_stress_events")),
        ("Oracle higher renewable", rate(False, "renewable_mean", "renewable_mean")),
        ("Oracle fewer anti-cheat steps", rate(True, "anti_cheat_steps", "anti_cheat_steps")),
    ]
    labels, vals = zip(*items)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    colors = ["#16a34a" if v > 50 else "#ca8a04" if v > 0 else "#64748b" for v in vals]
    ax.barh(labels, vals, color=colors, edgecolor="white")
    ax.set_xlabel("% of paired episodes where oracle wins outright")
    ax.set_xlim(0, 100)
    ax.axvline(50, color="black", linestyle=":", alpha=0.4)
    ax.set_title("Head-to-head win rate on paired episodes (same seed)")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    out = out_dir / "eval_oracle_win_rates.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_paired_scatter(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    if not rows:
        return None
    b = [float(r["baseline"]["avg_wait"]) for r in rows]
    o = [float(r["oracle"]["avg_wait"]) for r in rows]
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.scatter(b, o, alpha=0.65, c="#7c3aed", edgecolors="white", linewidths=0.4)
    lim = max(max(b + o, default=1.0), 1e-6) * 1.05
    ax.plot([0, lim], [0, lim], "k--", linewidth=1, label="y = x (no change)")
    ax.set_xlabel("Baseline avg wait (min)")
    ax.set_ylabel("Oracle avg wait (min)")
    ax.set_title("Paired scatter — points below diagonal = oracle faster")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out = out_dir / "eval_paired_scatter_wait.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_binary_timeline(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    if not rows:
        return None
    keys = [
        ("Peak viol.", "baseline_any_peak_violation"),
        ("Anti-cheat", "baseline_any_anti_cheat"),
        ("Crit. defer", "baseline_any_critical_defer"),
    ]
    n = len(rows)
    mat = []
    for _, k in keys:
        row_vals = []
        for r in rows:
            row_vals.append(1.0 if (r.get("binary") or {}).get(k) else 0.0)
        mat.append(row_vals)
    fig, ax = plt.subplots(figsize=(12, 2.8))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1, interpolation="nearest")
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([k[0] for k in keys])
    ax.set_xlabel("Episode index")
    ax.set_title("Baseline binary stress flags over paired episodes (dark = event occurred)")
    fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02, label="1 = occurred")
    fig.tight_layout()
    out = out_dir / "eval_binary_timeline_baseline.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_fair_eval_rates(fair_path: Path, out_dir: Path) -> Path | None:
    if not fair_path.is_file():
        return None
    fe = json.loads(fair_path.read_text(encoding="utf-8"))
    br = fe.get("binary_rates_wilson") or {}
    pairs = [
        ("baseline_any_peak_violation", "oracle_any_peak_violation", "Any peak violation"),
        ("baseline_any_anti_cheat", "oracle_any_anti_cheat", "Any anti-cheat"),
        ("baseline_any_critical_defer", "oracle_any_critical_defer", "Any critical defer"),
        ("baseline_high_stress", "oracle_high_stress", "High stress episode"),
    ]
    labels_m: list[str] = []
    pb, po = [], []
    eb_lo, eb_hi = [], []
    eo_lo, eo_hi = [], []
    for bk, ok, title in pairs:
        if bk not in br or ok not in br:
            continue
        labels_m.append(title)
        pb.append(float(br[bk]["p_hat"]))
        po.append(float(br[ok]["p_hat"]))
        eb_lo.append(float(br[bk]["p_hat"]) - float(br[bk]["wilson_low"]))
        eb_hi.append(float(br[bk]["wilson_high"]) - float(br[bk]["p_hat"]))
        eo_lo.append(float(br[ok]["p_hat"]) - float(br[ok]["wilson_low"]))
        eo_hi.append(float(br[ok]["wilson_high"]) - float(br[ok]["p_hat"]))
    if not labels_m:
        return None

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = list(range(len(labels_m)))
    w = 0.36
    ax.bar(
        [i - w / 2 for i in x],
        pb,
        width=w,
        yerr=[eb_lo, eb_hi],
        capsize=4,
        label="Baseline",
        color="#2563eb",
    )
    ax.bar(
        [i + w / 2 for i in x],
        po,
        width=w,
        yerr=[eo_lo, eo_hi],
        capsize=4,
        label="Oracle",
        color="#16a34a",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels_m, rotation=15, ha="right")
    ax.set_ylabel("Rate (point + Wilson 95% CI)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Binary episode rates (from fair_eval_results.json)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out = out_dir / "eval_fair_binary_rates.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_mcnemar_summary(fair_path: Path, out_dir: Path) -> Path | None:
    if not fair_path.is_file():
        return None
    fe = json.loads(fair_path.read_text(encoding="utf-8"))
    mc = fe.get("paired_mcnemar") or {}
    if not mc:
        return None
    labels = []
    pvals = []
    for k, block in mc.items():
        if not isinstance(block, dict):
            continue
        p = block.get("p_value_two_sided_exact")
        if p is None or (isinstance(p, float) and math.isnan(p)):
            continue
        labels.append(k.replace("_", " "))
        pvals.append(float(p))

    if not labels:
        return None
    fig, ax = plt.subplots(figsize=(9, 4))
    colors = ["#16a34a" if p < 0.05 else "#64748b" for p in pvals]
    ax.barh(labels, pvals, color=colors, edgecolor="white")
    ax.axvline(0.05, color="red", linestyle="--", linewidth=1, label="p = 0.05")
    ax.set_xlabel("McNemar exact two-sided p (discordant pairs)")
    ax.set_title("Paired significance — low p means baseline vs oracle differ on binary outcomes")
    ax.legend()
    ax.set_xlim(0, 1)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    out = out_dir / "eval_mcnemar_pvalues.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def plot_dashboard_grid(rows: list[dict[str, Any]], data: dict[str, Any], out_dir: Path) -> Path | None:
    if not rows:
        return None
    idx = [r["episode_index"] for r in rows]
    b_wait = [float(r["baseline"]["avg_wait"]) for r in rows]
    o_wait = [float(r["oracle"]["avg_wait"]) for r in rows]
    d_peak = [float(r["oracle"]["peak_violations"]) - float(r["baseline"]["peak_violations"]) for r in rows]

    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.28)

    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(idx, b_wait, label="Baseline wait", color="#2563eb")
    ax1.plot(idx, o_wait, label="Oracle wait", color="#16a34a")
    ax1.set_title("1) Wait trajectory (paired)")
    ax1.legend()
    ax1.grid(alpha=0.25)

    ax2 = fig.add_subplot(gs[1, 0])
    ax2.hist(d_peak, bins=12, color="#7c3aed", edgecolor="white")
    ax2.axvline(0, color="black", linestyle="--")
    ax2.set_title("2) Δ Peak ticks")
    ax2.set_xlabel("oracle − baseline")

    ax3 = fig.add_subplot(gs[1, 1])
    b = [float(r["baseline"]["avg_wait"]) for r in rows]
    o = [float(r["oracle"]["avg_wait"]) for r in rows]
    ax3.scatter(b, o, alpha=0.5, c="#0d9488")
    m = max(max(b + o, default=0.1), 0.05) * 1.1
    ax3.plot([0, m], [0, m], "k--", linewidth=1)
    ax3.set_title("3) Wait scatter")
    ax3.set_xlabel("baseline")
    ax3.set_ylabel("oracle")

    ax4 = fig.add_subplot(gs[2, 0])
    _boxplot_compat(
        ax4,
        [
            [float(r["baseline"]["grid_stress_events"]) for r in rows],
            [float(r["oracle"]["grid_stress_events"]) for r in rows],
        ],
        ["B", "O"],
    )
    ax4.set_title("4) Stress ticks box")

    ax5 = fig.add_subplot(gs[2, 1])
    wins = sum(1 for r in rows if float(r["oracle"]["avg_wait"]) < float(r["baseline"]["avg_wait"]) - 1e-9)
    ax5.bar(["Oracle wins\n(lower wait)"], [100 * wins / len(rows)], color="#16a34a", width=0.45)
    ax5.set_ylim(0, 100)
    ax5.set_title("5) Win rate (wait)")
    ax5.grid(axis="y", alpha=0.25)

    fig.suptitle(
        f"EV Grid Oracle — evaluation dashboard | scenario={data.get('scenario')} | n={len(rows)}",
        fontsize=12,
        fontweight="bold",
    )
    out = out_dir / "eval_dashboard_summary.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate KPI + paired-eval visualization suite for README / judges.")
    ap.add_argument("--eval-json", type=str, default="training/eval_results.json")
    ap.add_argument("--fair-json", type=str, default="artifacts/fair_eval_results.json")
    ap.add_argument("--out-dir", type=str, default="artifacts")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    eval_path = Path(args.eval_json)
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    rows = _per_episode_rows(data)
    fair_path = Path(args.fair_json)

    written: list[str] = []
    for fn in (
        lambda: plot_kpi_bars(data, out_dir),
        lambda: plot_episode_trajectories(rows, data, out_dir),
        lambda: plot_delta_histograms(rows, out_dir),
        lambda: plot_reward_breakdown(data, out_dir),
        lambda: plot_boxplots(rows, out_dir),
        lambda: plot_oracle_win_rates(rows, out_dir),
        lambda: plot_paired_scatter(rows, out_dir),
        lambda: plot_binary_timeline(rows, out_dir),
        lambda: plot_dashboard_grid(rows, data, out_dir),
        lambda: plot_fair_eval_rates(fair_path, out_dir),
        lambda: plot_mcnemar_summary(fair_path, out_dir),
    ):
        path = fn()
        if path is not None:
            written.append(str(path))

    for w in written:
        print(f"Wrote {w}")
    if not written:
        print("No figures written (missing per_episode in eval JSON?).")


if __name__ == "__main__":
    main()
