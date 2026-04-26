#!/usr/bin/env python3
"""
Export loss + reward (or closest TRL scalar tags) from a TensorBoard run dir into PNGs.

Hackathon requirement: committed plots from a *real* GRPO run. After `trainer.train()` in
`training/train_grpo.ipynb`, copy `ev_oracle_grpo_road/` from Colab (or run locally), then:

  pip install tensorboard matplotlib
  python tools/export_grpo_tensorboard_plots.py --logdir ev_oracle_grpo_road --out-dir artifacts

Writes e.g. artifacts/grpo_loss.png and artifacts/grpo_reward.png (filenames depend on tags found).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def _pick_tags(scalar_tags: list[str]) -> tuple[str | None, str | None]:
    loss_tag = None
    reward_tag = None
    lower = {t: t.lower() for t in scalar_tags}
    for t in scalar_tags:
        tl = lower[t]
        if loss_tag is None and re.search(r"(^|/)loss$|train/loss|loss/", tl):
            loss_tag = t
        if reward_tag is None and "reward" in tl:
            reward_tag = t
    if loss_tag is None:
        for t in scalar_tags:
            if "loss" in lower[t]:
                loss_tag = t
                break
    if reward_tag is None:
        for t in scalar_tags:
            if "reward" in lower[t] or "return" in lower[t]:
                reward_tag = t
                break
    return loss_tag, reward_tag


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--logdir",
        type=Path,
        default=Path("ev_oracle_grpo_road"),
        help="Directory containing events.out.tfevents.* (GRPO output_dir)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts"),
        help="Where to write PNGs",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from tensorboard.backend.event_processing.event_accumulator import (
            EventAccumulator,
        )
    except ImportError as e:
        raise SystemExit(
            "Missing dependency. Run: pip install tensorboard matplotlib"
        ) from e

    logdir = args.logdir
    if not logdir.is_dir():
        raise SystemExit(f"Logdir not found: {logdir.resolve()}")

    acc = EventAccumulator(str(logdir), size_guidance={"scalars": 0})
    acc.Reload()
    tags = sorted(acc.Tags().get("scalars", []))
    if not tags:
        raise SystemExit(
            f"No scalar tags under {logdir}. Train first or check output_dir."
        )

    loss_tag, reward_tag = _pick_tags(tags)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    def plot_tag(tag: str, out_name: str) -> None:
        events = acc.Scalars(tag)
        steps = [e.step for e in events]
        vals = [e.value for e in events]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(steps, vals, linewidth=1.2)
        ax.set_xlabel("step")
        ax.set_ylabel(tag)
        ax.set_title(tag)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        path = out_dir / out_name
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"Wrote {path}")

    print("Scalar tags found:", ", ".join(tags))
    if loss_tag:
        safe = "grpo_loss.png"
        plot_tag(loss_tag, safe)
    else:
        print("WARN: no loss-like tag; skip loss PNG")

    if reward_tag:
        plot_tag(reward_tag, "grpo_reward.png")
    else:
        print("WARN: no reward-like tag; skip reward PNG")

    if not loss_tag and not reward_tag:
        raise SystemExit("Could not infer loss/reward tags; inspect list above.")


if __name__ == "__main__":
    main()
