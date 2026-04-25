from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Optional

import pygame

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore, _build_prompt
from ev_grid_oracle.models import ActionType, EVGridAction, GridState
from ev_grid_oracle.oracle_agent import OracleAgent
from ev_grid_oracle.policies import baseline_policy
from viz.city_map import CityMapRenderer, RenderConfig


PolicyFn = Callable[[GridState, object], EVGridAction]


def _step_action(env: EVGridCore, policy: PolicyFn) -> EVGridAction:
    st = env._grid_state
    if st is None or not st.pending_evs:
        return EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
    return policy(st, env.city_graph)


def record_phase(
    *,
    env: EVGridCore,
    renderer: CityMapRenderer,
    surface: pygame.Surface,
    out_dir: Path,
    phase_label: str,
    steps: int,
    tick_every_frames: int,
    frame_start: int,
    policy: PolicyFn,
) -> int:
    last_action: Optional[EVGridAction] = None
    frame = frame_start
    for _ in range(steps):
        last_action = _step_action(env, policy)
        env.step(last_action)
        for _ in range(tick_every_frames):
            renderer.render(surface, last_action=last_action, mode_label=phase_label)
            pygame.image.save(surface, str(out_dir / f"frame_{frame:06d}.png"))
            frame += 1
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--baseline-steps", type=int, default=24)
    ap.add_argument("--oracle-steps", type=int, default=24)
    ap.add_argument("--out", type=str, default="artifacts/frames_2min")
    ap.add_argument("--oracle-lora", type=str, default="", help="HF LoRA repo id (optional)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--tick-every-frames", type=int, default=15)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    pygame.init()
    cfg = RenderConfig(fps=args.fps)
    surf = pygame.Surface((cfg.width, cfg.height))

    env = EVGridCore(city_graph=build_city_graph())
    env.reset(seed=args.seed)
    renderer = CityMapRenderer(env, cfg)
    oracle = OracleAgent(lora_repo_id=args.oracle_lora or None)

    frame = 0
    frame = record_phase(
        env=env,
        renderer=renderer,
        surface=surf,
        out_dir=out_dir,
        phase_label="BASELINE",
        steps=args.baseline_steps,
        tick_every_frames=args.tick_every_frames,
        frame_start=frame,
        policy=baseline_policy,
    )

    # TODO: swap to real oracle policy once LoRA is ready.
    frame = record_phase(
        env=env,
        renderer=renderer,
        surface=surf,
        out_dir=out_dir,
        phase_label="ORACLE",
        steps=args.oracle_steps,
        tick_every_frames=args.tick_every_frames,
        frame_start=frame,
        policy=lambda s, g: oracle.act(s, _build_prompt(s), g),
    )

    pygame.quit()
    print(f"Wrote frames to {out_dir}")
    print("Make video:")
    print("  ffmpeg -framerate 30 -i frame_%06d.png -c:v libx264 -pix_fmt yuv420p out.mp4")


if __name__ == "__main__":
    main()

