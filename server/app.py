from __future__ import annotations

import concurrent.futures
import os
from pathlib import Path
import time
from collections import OrderedDict
import logging

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
from ev_grid_oracle.models import (
    ActionType,
    EVGridAction,
    EVGridObservation,
    GridDirective,
    MultiAgentStepRequest,
    NegotiationMessage,
)
from ev_grid_oracle.oracle_agent import OracleAgent
from ev_grid_oracle.policies import baseline_policy
from ev_grid_oracle.parsing import parse_simulation
from ev_grid_oracle.scenarios import ScenarioName
from ev_grid_oracle.world_model_verifier import rollout_deterministic_5ticks, score_prediction
from ev_grid_oracle.multi_agent import MultiAgentSession
from server.ev_grid_environment import EVGridEnvironment
from server.role_metrics import compute_role_kpis, compute_role_reward_breakdown, summarize_action

log = logging.getLogger("ev-grid-oracle")
if not log.handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


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


# -----------------------------
# Multi-agent demo API (Theme #1)
# -----------------------------

_MA_SESSION_TTL_SEC = int(os.getenv("MA_SESSION_TTL_SEC", "3600"))
_MA_MAX_SESSIONS = int(os.getenv("MA_MAX_SESSIONS", "64"))
_ma_sessions: "OrderedDict[str, tuple[float, MultiAgentSession]]" = OrderedDict()


def _ma_gc(now: float | None = None) -> None:
    t = float(now if now is not None else time.time())
    expired: list[str] = []
    for sid, (ts, _sess) in _ma_sessions.items():
        if t - float(ts) > float(_MA_SESSION_TTL_SEC):
            expired.append(sid)
    for sid in expired:
        _ma_sessions.pop(sid, None)
    while len(_ma_sessions) > int(_MA_MAX_SESSIONS):
        _ma_sessions.popitem(last=False)


def _ma_get(session_id: str) -> MultiAgentSession | None:
    _ma_gc()
    row = _ma_sessions.get(session_id)
    if row is None:
        return None
    _ts, sess = row
    _ma_sessions.move_to_end(session_id, last=True)
    _ma_sessions[session_id] = (time.time(), sess)
    return sess


class MANewRequest(BaseModel):
    seed: int = Field(123, ge=0, le=1_000_000)
    scenario: ScenarioName = Field("baseline")


@app.post("/ma/new")
def ma_new(payload: MANewRequest = Body(...)) -> dict[str, Any]:
    t0 = time.time()
    _ma_gc()
    sid = str(uuid4())
    core = EVGridCore(city_graph=_demo_graph)
    obs = core.reset(seed=payload.seed, scenario=cast(ScenarioName, payload.scenario))
    sess = MultiAgentSession(core=core)
    _ma_sessions[sid] = (time.time(), sess)
    log.info("ma_new", extra={"sid": sid, "seed": payload.seed, "scenario": str(core.scenario), "ms": int((time.time() - t0) * 1000)})
    return {
        "session_id": sid,
        "obs": _obs_to_jsonable(obs),
        "station_nodes": _station_nodes(core),
        "scenario": core.scenario,
        "seed": payload.seed,
        "sim_version": _SIM_VERSION,
        "messages": [],
        "grid_directive": GridDirective().model_dump(mode="json"),
    }


@app.get("/ma/state")
def ma_state(session_id: str = Query(...)) -> dict[str, Any]:
    t0 = time.time()
    sess = _ma_get(session_id)
    if sess is None:
        log.info("ma_state_miss", extra={"sid": session_id, "ms": int((time.time() - t0) * 1000)})
        raise HTTPException(status_code=404, detail="Unknown session_id")
    core = sess.core
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
    return {
        "session_id": session_id,
        "obs": _obs_to_jsonable(obs),
        "station_nodes": _station_nodes(core),
        "scenario": core.scenario,
        "tick": core.step_count,
        "messages": [m.model_dump(mode="json") for m in sess.messages[-50:]],
        "grid_directive": sess.last_directive.model_dump(mode="json"),
        "violations": list(sess.last_violations),
        "resolved_action": sess.last_resolved_action.model_dump(mode="json") if sess.last_resolved_action else None,
    }


@app.post("/ma/step")
def ma_step(payload: MultiAgentStepRequest = Body(...)) -> dict[str, Any]:
    t0 = time.time()
    sess = _ma_get(payload.session_id)
    if sess is None:
        log.info("ma_step_miss", extra={"sid": payload.session_id, "ms": int((time.time() - t0) * 1000)})
        raise HTTPException(status_code=404, detail="Unknown session_id")

    gm = payload.grid_message
    fm = payload.fleet_message
    if gm is not None and gm.role != "grid":
        raise HTTPException(status_code=400, detail="grid_message.role must be 'grid'")
    if fm is not None and fm.role != "fleet":
        raise HTTPException(status_code=400, detail="fleet_message.role must be 'fleet'")

    resolved = sess.step(
        grid_directive=payload.grid_directive,
        fleet_action=payload.fleet_action,
        grid_message=gm,
        fleet_message=fm,
    )
    obs = sess.core._grid_state
    out_obs = (
        {}
        if obs is None
        else EVGridObservation(
            prompt=_build_prompt(obs),
            state=obs,
            done=sess.core.step_count >= sess.core.max_steps,
            reward_breakdown={},
            anti_cheat_flags=[],
            anti_cheat_details={},
        ).model_dump(mode="json")
    )
    log.info(
        "ma_step",
        extra={
            "sid": payload.session_id,
            "tick": int(sess.core.step_count),
            "viol": ",".join(sess.last_violations),
            "ms": int((time.time() - t0) * 1000),
        },
    )
    return {
        "session_id": payload.session_id,
        "obs": out_obs,
        "tick": sess.core.step_count,
        "scenario": sess.core.scenario,
        "grid_directive": payload.grid_directive.model_dump(mode="json"),
        "fleet_action": payload.fleet_action.model_dump(mode="json"),
        "resolved_action": resolved.model_dump(mode="json"),
        "violations": list(sess.last_violations),
        "messages": [m.model_dump(mode="json") for m in sess.messages[-50:]],
    }


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
    t0 = time.time()
    _demo_session_gc()
    session_id = str(uuid4())
    core = EVGridCore(city_graph=_demo_graph)
    obs = core.reset(seed=payload.seed, scenario=cast(ScenarioName, payload.scenario))
    _demo_sessions[session_id] = (time.time(), core)
    from ev_grid_oracle.scenarios import scenario_schedule

    log.info("demo_new", extra={"sid": session_id, "seed": payload.seed, "scenario": str(obs.state and core.scenario), "ms": int((time.time()-t0)*1000)})
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
    t0 = time.time()
    core = _demo_session_get(session_id)
    if core is None:
        log.info("demo_state_miss", extra={"sid": session_id, "ms": int((time.time()-t0)*1000)})
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

    log.info("demo_state", extra={"sid": session_id, "tick": int(core.step_count), "ms": int((time.time()-t0)*1000)})
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
    t0 = time.time()
    core = _demo_session_get(session_id)
    if core is None:
        log.info("demo_step_miss", extra={"sid": session_id, "ms": int((time.time()-t0)*1000)})
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
    out = {
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
    log.info(
        "demo_step",
        extra={
            "sid": session_id,
            "mode": mode,
            "tick": int(core.step_count),
            "oracle_active": bool(oracle_llm_active),
            "oracle_timeout": bool(oracle_timed_out),
            "oracle_skipped": bool(oracle_skipped_env),
            "forced": bool(forced_action is not None),
            "ms": int((time.time() - t0) * 1000),
        },
    )
    return out


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

