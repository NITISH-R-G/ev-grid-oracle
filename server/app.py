from __future__ import annotations

import concurrent.futures
import os
from pathlib import Path
import time
from collections import OrderedDict

try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:  # pragma: no cover
    raise ImportError("openenv-core required. Install deps from pyproject.") from e

from typing import Any, Literal, cast
from uuid import uuid4
from pydantic import BaseModel, Field

from fastapi import Body, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore, _build_prompt
from ev_grid_oracle.models import ActionType, EVGridAction, EVGridObservation
from ev_grid_oracle.oracle_agent import OracleAgent
from ev_grid_oracle.policies import baseline_policy
from ev_grid_oracle.parsing import parse_simulation
from ev_grid_oracle.scenarios import ScenarioName
from ev_grid_oracle.world_model_verifier import rollout_deterministic_5ticks, score_prediction
from server.ev_grid_environment import EVGridEnvironment
from server.role_metrics import compute_role_kpis, compute_role_reward_breakdown, summarize_action


def _oracle_skip_llm_env() -> bool:
    return os.getenv("ORACLE_SKIP_LLM", "").strip() not in ("", "0", "false", "False")


def _demo_oracle_act_with_guard(
    *,
    st: Any,
    core: EVGridCore,
    oracle_lora_repo: str,
) -> tuple[EVGridAction, str, bool, bool, bool]:
    """
    Run oracle policy with CPU-Space-safe guards.

    Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env
    """
    if _oracle_skip_llm_env():
        a, t = OracleAgent(lora_repo_id=None).act_with_text(st, _build_prompt(st), core.city_graph)
        return a, t, False, False, True

    repo = (oracle_lora_repo or "").strip() or None
    if not repo:
        agent = OracleAgent(lora_repo_id=None)
        action, text = agent.act_with_text(st, _build_prompt(st), core.city_graph)
        return action, text, bool(agent.is_active), False, False

    timeout = float(os.getenv("DEMO_ORACLE_INFERENCE_TIMEOUT_SEC", "90"))

    # Reuse a single executor to avoid spawning threads repeatedly.
    # Note: cancellation does not reliably stop model load once started, so we keep the timeout
    # as a *response guard* only. The model cache in OracleAgent prevents repeated cold-loads.
    global _ORACLE_EXEC
    try:
        _ORACLE_EXEC
    except NameError:
        _ORACLE_EXEC = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def run() -> tuple[EVGridAction, str, bool]:
        agent = OracleAgent(lora_repo_id=repo)
        action, text = agent.act_with_text(st, _build_prompt(st), core.city_graph)
        return action, text, bool(agent.is_active)

    fut = _ORACLE_EXEC.submit(run)
    try:
        action, text, active = fut.result(timeout=timeout)
        return action, text, active, False, False
    except concurrent.futures.TimeoutError:
        return baseline_policy(st, core.city_graph), "[timeout] baseline fallback (oracle too slow)", False, True, False


app = create_app(EVGridEnvironment, EVGridAction, EVGridObservation, env_name="ev-grid-oracle", max_concurrent_envs=1)

_WEB_DIST = (Path(__file__).resolve().parents[1] / "web" / "dist").resolve()
if _WEB_DIST.exists():
    # Serve Phaser UI at /ui (built by Docker during Space build)
    app.mount("/ui", StaticFiles(directory=str(_WEB_DIST), html=True), name="ui")


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    # HF Spaces loads / by default; redirect to the Phaser UI if present.
    if _WEB_DIST.exists():
        return """<!doctype html><html><head><meta http-equiv="refresh" content="0; url=/ui/" /></head><body></body></html>"""
    return """\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>EV Grid Oracle (OpenEnv)</title>
    <style>
      body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; background:#0b1022; color:#e8ecff; margin:0; }
      .wrap { max-width: 920px; margin: 0 auto; padding: 28px 18px; }
      .card { background: rgba(255,255,255,0.04); border: 1px solid rgba(120,140,200,0.22); border-radius: 16px; padding: 16px; margin-top: 14px; }
      a { color: #7aa7ff; text-decoration: none; }
      a:hover { text-decoration: underline; }
      code { background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 8px; }
      .k { opacity: 0.85; font-size: 13px; }
      ul { margin: 10px 0 0 18px; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <h2>EV Grid Oracle — OpenEnv Environment</h2>
      <div class="k">This Space hosts the FastAPI server for the OpenEnv environment + a small demo API.</div>

      <div class="card">
        <b>OpenEnv API</b>
        <ul>
          <li><a href="/docs">/docs</a> (FastAPI Swagger)</li>
          <li><a href="/schema">/schema</a></li>
          <li><a href="/health">/health</a></li>
          <li><code>POST</code> /reset · <code>POST</code> /step · <code>GET</code> /state</li>
        </ul>
      </div>

      <div class="card">
        <b>Demo API (for the Phaser pixel-map client)</b>
        <ul>
          <li><code>POST</code> /demo/new</li>
          <li><code>POST</code> /demo/step</li>
          <li><code>GET</code> /demo/state</li>
        </ul>
        <div class="k">If the Phaser UI is built into this Space, it will be available at <a href="/ui/">/ui/</a>.</div>
      </div>
    </div>
  </body>
</html>
"""


# -----------------------------
# Demo API (Phaser frontend)
# -----------------------------

_DEMO_SESSION_TTL_SEC = int(os.getenv("DEMO_SESSION_TTL_SEC", "3600"))  # 1h
_DEMO_MAX_SESSIONS = int(os.getenv("DEMO_MAX_SESSIONS", "64"))

# Ordered for deterministic eviction of oldest sessions.
_demo_sessions: "OrderedDict[str, tuple[float, EVGridCore]]" = OrderedDict()
_demo_graph = build_city_graph()
_SIM_VERSION = "2026-04-26.1"


def _demo_session_gc(now: float | None = None) -> None:
    t = float(now if now is not None else time.time())
    # TTL eviction
    expired: list[str] = []
    for sid, (ts, _core) in _demo_sessions.items():
        if t - float(ts) > float(_DEMO_SESSION_TTL_SEC):
            expired.append(sid)
    for sid in expired:
        _demo_sessions.pop(sid, None)
    # size eviction
    while len(_demo_sessions) > int(_DEMO_MAX_SESSIONS):
        _demo_sessions.popitem(last=False)


def _demo_session_get(session_id: str) -> EVGridCore | None:
    _demo_session_gc()
    row = _demo_sessions.get(session_id)
    if row is None:
        return None
    ts, core = row
    # touch (LRU-ish)
    _demo_sessions.move_to_end(session_id, last=True)
    _demo_sessions[session_id] = (time.time(), core)
    return core


class DemoNewRequest(BaseModel):
    seed: int = Field(123, ge=0, le=1_000_000)
    scenario: ScenarioName = Field("baseline")


def _obs_to_jsonable(obs: EVGridObservation) -> dict[str, Any]:
    # Pydantic v2 BaseModel: use model_dump for JSONable dicts
    return obs.model_dump()


def _station_nodes(core: EVGridCore) -> list[dict[str, Any]]:
    st = core._grid_state
    if st is None:
        return []
    return [
        {
            "station_id": s.station_id,
            "name": s.neighborhood_name,
            "slug": s.neighborhood_slug,
            "lat": s.lat,
            "lng": s.lng,
            "total_slots": s.total_slots,
        }
        for s in st.stations
    ]


@app.post("/demo/new")
def demo_new(payload: DemoNewRequest = Body(...)) -> dict[str, Any]:
    _demo_session_gc()
    session_id = str(uuid4())
    core = EVGridCore(city_graph=_demo_graph)
    obs = core.reset(seed=payload.seed, scenario=cast(ScenarioName, payload.scenario))
    _demo_sessions[session_id] = (time.time(), core)
    from ev_grid_oracle.scenarios import scenario_schedule

    return {
        "session_id": session_id,
        "obs": _obs_to_jsonable(obs),
        "station_nodes": _station_nodes(core),
        "scenario": core.scenario,
        "seed": payload.seed,
        "sim_version": _SIM_VERSION,
        "scenario_schedule": scenario_schedule(core.scenario),
    }


@app.get("/demo/state")
def demo_state(session_id: str = Query(...)) -> dict[str, Any]:
    core = _demo_session_get(session_id)
    if core is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")
    st = core._grid_state
    if st is None:
        obs = core.reset(seed=123, scenario=core.scenario)
    else:
        obs = EVGridObservation(
            prompt=_build_prompt(st),
            state=st,
            done=False,
            reward_breakdown={},
            anti_cheat_flags=[],
            anti_cheat_details={},
        )
    from ev_grid_oracle.scenarios import scenario_schedule

    return {
        "session_id": session_id,
        "obs": _obs_to_jsonable(obs),
        "station_nodes": _station_nodes(core),
        "scenario": core.scenario,
        "sim_version": _SIM_VERSION,
        "scenario_schedule": scenario_schedule(core.scenario),
    }


@app.post("/demo/step")
def demo_step(
    session_id: str = Body(...),
    mode: Literal["baseline", "oracle"] = Body("baseline"),
    oracle_lora_repo: str = Body("", embed=True),
    forced_action: dict[str, Any] | None = Body(None),
) -> dict[str, Any]:
    core = _demo_session_get(session_id)
    if core is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")

    st = core._grid_state
    oracle_llm_active = False
    oracle_text = ""
    oracle_timed_out = False
    oracle_skipped_env = False
    dream_score = None
    dream_breakdown: dict[str, float] = {}
    dream_pred = None
    dream_true = None
    event: dict[str, Any] = {"type": "noop"}
    if forced_action is not None:
        action = EVGridAction.model_validate(forced_action)
        oracle_llm_active = False
        oracle_text = ""
        dream_score = None
        dream_breakdown = {}
        dream_pred = None
        dream_true = None
        # Keep animation useful even when replaying stored actions.
        if st is not None:
            ev = next((e for e in st.pending_evs if e.ev_id == action.ev_id), st.pending_evs[0] if st.pending_evs else None)
            src = next((x for x in st.stations if ev is not None and x.neighborhood_slug == ev.neighborhood_slug), None)
            dst = next((x for x in st.stations if action.station_id and x.station_id == action.station_id), None)
            if action.action_type == ActionType.route and ev is not None and src is not None and dst is not None:
                event = {
                    "type": "route",
                    "ev_id": ev.ev_id,
                    "from": {"station_id": src.station_id, "lat": src.lat, "lng": src.lng},
                    "to": {"station_id": dst.station_id, "lat": dst.lat, "lng": dst.lng},
                    "polyline": [[src.lat, src.lng], [dst.lat, dst.lng]],
                }
            else:
                event = {"type": "forced_action", "action_type": str(action.action_type.value)}
        else:
            event = {"type": "forced_action"}
    elif st is None or not st.pending_evs:
        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        event = {"type": "idle"}
    else:
        if mode == "baseline":
            action = baseline_policy(st, core.city_graph)
        else:
            action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env = _demo_oracle_act_with_guard(
                st=st, core=core, oracle_lora_repo=oracle_lora_repo
            )

            # If oracle produced a <SIMULATE> block, score it against a deterministic T+5 rollout.
            pred = parse_simulation(oracle_text) if oracle_text else None
            if pred is not None:
                ps = score_prediction(st, action, pred)
                dream_score = ps.score_0_1
                dream_breakdown = ps.breakdown
                dream_pred = pred.model_dump(mode="json")
                t5 = rollout_deterministic_5ticks(st, action)
                # summarize true top3
                top3 = sorted(
                    [
                        (
                            s.station_id,
                            s.occupied_slots / max(1, s.total_slots),
                            s.queue_length,
                        )
                        for s in t5.stations
                    ],
                    key=lambda x: x[1],
                    reverse=True,
                )[:3]
                dream_true = {
                    "t5_grid_load_pct": float(t5.grid_load_pct),
                    "t5_renewable_pct": float(t5.renewable_pct),
                    "t5_top_stations": [
                        {"station_id": sid, "load_pct": float(load), "queue": int(q)} for sid, load, q in top3
                    ],
                }

        # Render-friendly event for frontend animation.
        # v0: polyline path is station-to-station graph path (lat/lng pairs).
        ev = st.pending_evs[0]
        src = next((x for x in st.stations if x.neighborhood_slug == ev.neighborhood_slug), None)
        dst = next((x for x in st.stations if x.station_id == action.station_id), None)
        if action.action_type == ActionType.route and src is not None and dst is not None:
            event = {
                "type": "route",
                "ev_id": ev.ev_id,
                "from": {"station_id": src.station_id, "lat": src.lat, "lng": src.lng},
                "to": {"station_id": dst.station_id, "lat": dst.lat, "lng": dst.lng},
                "polyline": [[src.lat, src.lng], [dst.lat, dst.lng]],
            }
        else:
            event = {"type": action.action_type.value}

    obs = core.step(action)
    anti_flags = obs.anti_cheat_flags
    anti_details = obs.anti_cheat_details
    role_kpis = compute_role_kpis(obs)
    role_reward_breakdown = compute_role_reward_breakdown(obs)
    return {
        "obs": _obs_to_jsonable(obs),
        "event": event,
        "scenario": core.scenario,
        "scenario_events_at_tick": core.last_scenario_events,
        "tick": core.step_count,
        "sim_version": _SIM_VERSION,
        "anti_cheat_flags": anti_flags,
        "anti_cheat_details": anti_details,
        "role_kpis": role_kpis,
        "role_reward_breakdown": role_reward_breakdown,
        "mode": mode,
        "oracle_lora_repo": (oracle_lora_repo or "").strip(),
        "oracle_llm_active": oracle_llm_active,
        "oracle_timed_out": oracle_timed_out,
        "oracle_skipped_env": oracle_skipped_env,
        "action": summarize_action(action),
        "oracle_text": oracle_text,
        "dream_score": dream_score,
        "dream_breakdown": dream_breakdown,
        "dream_pred": dream_pred,
        "dream_true": dream_true,
        "forced_action": forced_action is not None,
    }


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

