from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Literal

import gradio as gr
from PIL import Image, ImageDraw, ImageFont

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction
from ev_grid_oracle.policies import baseline_policy
from training.evaluate import run_episode, summarize


Mode = Literal["Untrained Baseline", "Oracle Agent"]


def _norm(v: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    x = (v - lo) / (hi - lo)
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _station_color(load_pct: float) -> tuple[int, int, int]:
    if load_pct < 0.40:
        return (46, 213, 115)
    if load_pct < 0.60:
        return (255, 200, 0)
    if load_pct < 0.80:
        return (255, 130, 0)
    if load_pct < 0.95:
        return (255, 50, 50)
    return (180, 0, 0)


def render_map(env: EVGridCore, *, w: int = 900, h: int = 600) -> Image.Image:
    state = env._grid_state
    img = Image.new("RGB", (w, h), (10, 12, 20))
    draw = ImageDraw.Draw(img)

    if state is None:
        draw.text((20, 20), "No state", fill=(255, 255, 255))
        return img

    lats = [s.lat for s in state.stations]
    lngs = [s.lng for s in state.stations]
    lat_lo, lat_hi = min(lats), max(lats)
    lng_lo, lng_hi = min(lngs), max(lngs)

    def xy(lat: float, lng: float) -> tuple[int, int]:
        x = int(40 + _norm(lng, lng_lo, lng_hi) * (w - 80))
        y = int(40 + (1.0 - _norm(lat, lat_lo, lat_hi)) * (h - 120))
        return x, y

    # edges (graph-ish feel)
    # (we don't draw real edges yet; keep light)
    for s in state.stations:
        x, y = xy(s.lat, s.lng)
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(60, 80, 120))

    # stations
    for s in state.stations:
        x, y = xy(s.lat, s.lng)
        load = s.occupied_slots / max(1, s.total_slots)
        c = _station_color(load)
        r = 10 + int(_norm(s.total_slots, 4, 16) * 10)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=c, outline=(0, 0, 0), width=2)
        # queue dots
        for i in range(min(5, s.queue_length)):
            draw.ellipse((x - 3, y - r - 8 - i * 6, x + 3, y - r - 2 - i * 6), fill=(245, 245, 245))
        draw.text((x + r + 4, y - 8), s.station_id, fill=(220, 220, 220))

    # HUD
    draw.rectangle((w - 260, 20, w - 20, 160), fill=(18, 20, 32), outline=(80, 90, 120))
    draw.text((w - 245, 30), f"Time: {state.hour:02d}:00  {state.day_type.value}", fill=(240, 240, 240))
    draw.text((w - 245, 55), f"Grid load: {state.grid_load_pct*100:.1f}%", fill=(240, 240, 240))
    draw.text((w - 245, 80), f"Renewable: {state.renewable_pct*100:.1f}%", fill=(240, 240, 240))
    draw.text((w - 245, 105), f"Peak risk: {state.peak_risk.value}", fill=(240, 240, 240))
    avg_wait = sum(s.avg_wait_minutes for s in state.stations) / max(1, len(state.stations))
    draw.text((w - 245, 130), f"Avg wait: {avg_wait:.1f} min", fill=(240, 240, 240))

    return img


@dataclass
class Session:
    env: EVGridCore
    last_action_text: str = ""
    seed: int = 0


def new_session(seed: int) -> Session:
    env = EVGridCore(city_graph=build_city_graph())
    env.reset(seed=seed)
    return Session(env=env, seed=seed)


def step_once(sess: Session, mode: Mode) -> tuple[Image.Image, str, str]:
    state = sess.env._grid_state
    if state is None or not state.pending_evs:
        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        sess.last_action_text = "ACTION: load_shift (no pending EVs)"
    else:
        ev = state.pending_evs[0]
        if mode == "Untrained Baseline":
            action = baseline_policy(state, sess.env.city_graph)
            sess.last_action_text = f"Baseline picked {action.action_type.value} -> {action.station_id or 'NONE'}"
        else:
            # Placeholder until model wiring: use baseline but label it.
            action = baseline_policy(state, sess.env.city_graph)
            sess.last_action_text = f"Oracle (stub) picked {action.action_type.value} -> {action.station_id or 'NONE'}"

    obs = sess.env.step(action)
    img = render_map(sess.env)
    kpi = f"reward_total={obs.reward_breakdown.get('total', 0.0):.2f} | pending={len(obs.state.pending_evs)}"
    return img, sess.last_action_text, kpi


def compute_kpis(seed: int, episodes: int = 10) -> str:
    graph = build_city_graph()
    env = EVGridCore(city_graph=graph)
    baseline = [run_episode(env, policy="baseline", seed=seed + i) for i in range(episodes)]
    oracle = [run_episode(env, policy="oracle", seed=seed + 10_000 + i) for i in range(episodes)]
    out = {
        "episodes": episodes,
        "baseline": summarize(baseline),
        "oracle": summarize(oracle),
        "note": "oracle currently uses baseline policy (LLM wiring pending).",
    }
    # Human-readable
    b = out["baseline"]
    o = out["oracle"]
    return (
        f"Episodes={episodes}\n"
        f"Baseline avg_wait={b['avg_wait_minutes']:.2f}m | stress={b['grid_stress_events']:.1f} | peak_viol={b['peak_violations']:.1f}\n"
        f"Oracle   avg_wait={o['avg_wait_minutes']:.2f}m | stress={o['grid_stress_events']:.1f} | peak_viol={o['peak_violations']:.1f}\n"
        f"Renewable mean: baseline={b['renewable_mean']:.2f} oracle={o['renewable_mean']:.2f}\n"
        f"Critical deferred: baseline={b['critical_deferred']:.2f} oracle={o['critical_deferred']:.2f}\n"
        f"{out['note']}"
    )


with gr.Blocks(title="EV Grid Oracle") as demo:
    gr.Markdown("## EV Grid Oracle — Bangalore EV charging dispatch (baseline vs oracle)")

    with gr.Row():
        mode = gr.Radio(["Untrained Baseline", "Oracle Agent"], value="Untrained Baseline", label="Mode")
        seed = gr.Slider(0, 10_000, value=123, step=1, label="Scenario seed")

    start = gr.Button("Start / Reset")
    step = gr.Button("Step 1 tick (5 min)")
    kpis_btn = gr.Button("Compute KPI summary (10 episodes)")

    img = gr.Image(type="pil", label="Bangalore map (sim)")
    thought = gr.Textbox(label="Agent decision", lines=2)
    kpi = gr.Textbox(label="KPIs", lines=1)
    kpi_summary = gr.Textbox(label="Baseline vs Oracle (batch KPIs)", lines=6)

    state = gr.State()

    def _start(seed_val: int):
        sess = new_session(seed_val)
        return sess, render_map(sess.env), "", "", ""

    start.click(_start, inputs=[seed], outputs=[state, img, thought, kpi, kpi_summary])

    def _step(sess: Session, mode_val: Mode):
        if sess is None:
            sess = new_session(123)
        im, t, k = step_once(sess, mode_val)
        return sess, im, t, k

    step.click(_step, inputs=[state, mode], outputs=[state, img, thought, kpi])

    def _kpis(seed_val: int):
        return compute_kpis(seed_val, episodes=10)

    kpis_btn.click(_kpis, inputs=[seed], outputs=[kpi_summary])


if __name__ == "__main__":
    demo.launch()

