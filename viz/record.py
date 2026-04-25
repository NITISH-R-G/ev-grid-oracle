from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pygame

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction
from ev_grid_oracle.policies import baseline_policy
from viz.city_map import CityMapRenderer, RenderConfig


def record(
    *,
    seed: int,
    steps: int,
    out_dir: Path,
    label: str,
    fps: int = 30,
    tick_every_frames: int = 15,
):
    """
    Record frames as PNGs.

    - `tick_every_frames`: how many frames to show per env.step() (slows animation, looks smoother).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pygame.init()

    cfg = RenderConfig(fps=fps)
    surf = pygame.Surface((cfg.width, cfg.height))

    env = EVGridCore(city_graph=build_city_graph())
    env.reset(seed=seed)
    renderer = CityMapRenderer(env, cfg)

    last_action: Optional[EVGridAction] = None
    frame = 0
    for step in range(steps):
        st = env._grid_state
        if st is None or not st.pending_evs:
            action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        else:
            action = baseline_policy(st, env.city_graph)
        last_action = action
        env.step(action)

        for _ in range(tick_every_frames):
            renderer.render(surf, last_action=last_action, mode_label=label)
            pygame.image.save(surf, str(out_dir / f"frame_{frame:06d}.png"))
            frame += 1

    pygame.quit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--steps", type=int, default=48)
    ap.add_argument("--out", type=str, default="artifacts/frames_baseline")
    ap.add_argument("--label", type=str, default="baseline")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--tick-every-frames", type=int, default=15)
    args = ap.parse_args()

    record(
        seed=args.seed,
        steps=args.steps,
        out_dir=Path(args.out),
        label=args.label,
        fps=args.fps,
        tick_every_frames=args.tick_every_frames,
    )
    print(f"Wrote frames to {args.out}")
    print("To make a video (example):")
    print("  ffmpeg -framerate 30 -i frame_%06d.png -c:v libx264 -pix_fmt yuv420p out.mp4")


if __name__ == "__main__":
    main()

