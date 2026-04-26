from __future__ import annotations

import concurrent.futures
import os
from pathlib import Path
import time
from collections import OrderedDict
import logging
from server.road_router import get_router
from ev_grid_oracle.traffic import TrafficModel
import hashlib

try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:  # pragma: no cover
    raise ImportError("openenv-core required. Install deps from pyproject.") from e

from typing import Any, Literal, cast
from uuid import uuid4
from pydantic import BaseModel, Field

from fastapi import Body, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ev_grid_oracle.city_graph import build_city_graph
import networkx as nx
from ev_grid_oracle.env import EVGridCore, _build_prompt
from ev_grid_oracle.models import (
    ActionType,
    EVRequest,
    EVGridAction,
    EVGridObservation,
    GridDirective,
    MultiAgentStepRequest,
    NegotiationMessage,
)
from ev_grid_oracle.oracle_agent import OracleAgent
from ev_grid_oracle.policies import baseline_policy
from ev_grid_oracle.parsing import parse_simulation
from ev_grid_oracle.reward import split_role_rewards
from ev_grid_oracle.scenarios import ScenarioName
from ev_grid_oracle.world_model_verifier import rollout_deterministic_5ticks, score_prediction
from ev_grid_oracle.multi_agent import MultiAgentSession
from server.ev_grid_environment import EVGridEnvironment
from server.ev_grid_road_environment import EVGridRoadEnvironment
from ev_grid_oracle.road_models import RoadAction, RoadObservation
from server.role_metrics import compute_role_kpis, compute_role_reward_breakdown, summarize_action
from server.road_router import haversine_m

log = logging.getLogger("ev-grid-oracle")
if not log.handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

def _request_id(req: Request) -> str:
    rid = (req.headers.get("x-request-id") or req.headers.get("x-amzn-trace-id") or "").strip()
    return rid or uuid4().hex


def _oracle_skip_llm_env() -> bool:
    return os.getenv("ORACLE_SKIP_LLM", "").strip() not in ("", "0", "false", "False")


_RATE_BUCKET: dict[str, list[float]] = {}


def _rate_limit(req: Request, *, key: str, limit: int, window_sec: int) -> None:
    ip = (req.client.host if req.client else "unknown") + ":" + key
    now = time.time()
    xs = _RATE_BUCKET.get(ip, [])
    xs = [t for t in xs if now - t < window_sec]
    if len(xs) >= limit:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({key}). Please wait and retry.")
    xs.append(now)
    _RATE_BUCKET[ip] = xs

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

# Mount a separate “real road graph” RL environment under /road/.
road_app = create_app(EVGridRoadEnvironment, RoadAction, RoadObservation, env_name="ev-grid-oracle-road", max_concurrent_envs=1)
app.mount("/road", road_app)

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


@app.get("/healthz")
def healthz(req: Request) -> dict[str, Any]:
    """
    HF Spaces / cold-start friendly health endpoint.
    Keep it fast and dependency-safe (no heavy routing work).
    """
    rid = _request_id(req)
    router_ok = True
    try:
        # Lazy import / init; should be cached if already loaded.
        get_router()
    except Exception:
        router_ok = False
    return {
        "ok": True,
        "request_id": rid,
        "sim_version": _SIM_VERSION,
        "web_ui": bool(_WEB_DIST.exists()),
        "demo_sessions": len(_demo_sessions),
        "router_ok": router_ok,
        "schema_version": "traffic-v1",
    }


# -----------------------------
# Demo API (Phaser frontend)
# -----------------------------

_DEMO_SESSION_TTL_SEC = int(os.getenv("DEMO_SESSION_TTL_SEC", "3600"))  # 1h
_DEMO_MAX_SESSIONS = int(os.getenv("DEMO_MAX_SESSIONS", "64"))

# Ordered for deterministic eviction of oldest sessions.
_demo_sessions: "OrderedDict[str, tuple[float, EVGridCore]]" = OrderedDict()
_demo_graph = build_city_graph()
_SIM_VERSION = "2026-04-26.1"


def _osm_route_polyline(
    *,
    src_lat: float,
    src_lng: float,
    dst_lat: float,
    dst_lng: float,
    traffic: TrafficModel | None = None,
    tick: int | None = None,
) -> tuple[list[list[float]], list[int]] | None:
    try:
        return get_router().route_polyline(
            src_lat=src_lat, src_lng=src_lng, dst_lat=dst_lat, dst_lng=dst_lng, traffic=traffic, tick=tick
        )
    except Exception:
        return None


def _graph_route_polyline(core: EVGridCore, *, src_station_id: str, dst_station_id: str) -> list[list[float]]:
    """
    Return a render-friendly polyline (lat/lng pairs) along the station graph.
    v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.
    """
    if src_station_id == dst_station_id:
        n = core.city_graph.nodes[src_station_id]
        return [[float(n["lat"]), float(n["lng"])]]
    try:
        path = cast(list[str], nx.shortest_path(core.city_graph, src_station_id, dst_station_id, weight="weight_minutes"))
    except Exception:
        # Fallback: direct
        a = core.city_graph.nodes[src_station_id]
        b = core.city_graph.nodes[dst_station_id]
        return [[float(a["lat"]), float(a["lng"])], [float(b["lat"]), float(b["lng"])]]
    out: list[list[float]] = []
    for sid in path:
        n = core.city_graph.nodes[sid]
        out.append([float(n["lat"]), float(n["lng"])])
    return out


def _spawn_road_point_away_from_stations(
    *,
    core: EVGridCore,
    min_station_dist_m: float,
    seed_key: str,
    attempts: int = 80,
) -> tuple[float, float]:
    """
    Pick a deterministic road-graph node location (lat,lng) that is not within
    `min_station_dist_m` of any station. Deterministic for a given seed_key.
    """
    router = get_router()
    st = core._grid_state
    if st is None:
        raise ValueError("core not initialized")
    stations = st.stations
    if not stations:
        raise ValueError("no stations")

    h = hashlib.sha1(seed_key.encode("utf-8")).digest()
    base = int.from_bytes(h[:4], "big")
    n = len(router.nodes)
    for k in range(attempts):
        idx = (base + k * 9973) % max(1, n)
        lat, lng = router.nodes[int(idx)]
        ok = True
        for s in stations:
            if haversine_m(float(lat), float(lng), float(s.lat), float(s.lng)) < float(min_station_dist_m):
                ok = False
                break
        if ok:
            return float(lat), float(lng)
    raise ValueError("could_not_find_spawn_point")


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
    fleet_mode: str = Field("mixed", description="Fleet persona mix: mixed|taxi|corporate|delivery|private|emergency")


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
    fleet_mode: str = Field("mixed", description="Fleet persona mix: mixed|taxi|corporate|delivery|private|emergency")


@app.post("/ma/new")
def ma_new(req: Request, payload: MANewRequest = Body(...)) -> dict[str, Any]:
    _rate_limit(req, key="ma_new", limit=30, window_sec=60)
    t0 = time.time()
    rid = _request_id(req)
    try:
        _ma_gc()
        sid = str(uuid4())
        core = EVGridCore(city_graph=_demo_graph)
        obs = core.reset(seed=payload.seed, scenario=cast(ScenarioName, payload.scenario), fleet_mode=cast(Any, payload.fleet_mode))
        sess = MultiAgentSession(core=core)
        _ma_sessions[sid] = (time.time(), sess)
        log.info(
            "ma_new",
            extra={"rid": rid, "sid": sid, "seed": payload.seed, "scenario": str(core.scenario), "ms": int((time.time() - t0) * 1000)},
        )
        return {
            "request_id": rid,
            "session_id": sid,
            "obs": _obs_to_jsonable(obs),
            "station_nodes": _station_nodes(core),
            "scenario": core.scenario,
            "seed": payload.seed,
            "sim_version": _SIM_VERSION,
            "messages": [],
            "grid_directive": GridDirective().model_dump(mode="json"),
        }
    except HTTPException:
        raise
    except Exception as e:
        log.exception("ma_new_error", extra={"rid": rid, "ms": int((time.time() - t0) * 1000)})
        raise HTTPException(status_code=500, detail=f"ma_new_error: {type(e).__name__}: {e}")


def _grid_policy(st) -> tuple[GridDirective, NegotiationMessage]:
    # Deterministic grid-side directive: tighten budget during high/critical risk,
    # and blacklist top-loaded stations to prevent local overload.
    peak = getattr(st, "peak_risk", None)
    max_grid = 0.92
    if peak and str(peak.value) == "high":
        max_grid = 0.88
    if peak and str(peak.value) == "critical":
        max_grid = 0.84
    # blacklist top-2 load stations
    stations = list(getattr(st, "stations", []) or [])
    top = sorted(stations, key=lambda s: (s.occupied_slots / max(1, s.total_slots), s.queue_length), reverse=True)[:2]
    bl = [s.station_id for s in top]
    d = GridDirective(max_grid_load_pct=float(max_grid), station_blacklist=bl, price_mult=1.0)
    msg = NegotiationMessage(role="grid", text=f"Keep grid<= {max_grid:.2f}. Avoid {', '.join(bl) if bl else 'none'}.")
    return d, msg


class MAAutoStepRequest(BaseModel):
    session_id: str
    fleet_policy: Literal["baseline", "oracle"] = "baseline"
    oracle_lora_repo: str = ""


@app.post("/ma/auto_step")
def ma_auto_step(req: Request, payload: MAAutoStepRequest = Body(...)) -> dict[str, Any]:
    _rate_limit(req, key="ma_auto_step", limit=120, window_sec=60)
    """
    Convenience endpoint for the demo UI: server computes both roles' actions/messages
    while still using the explicit multi-agent protocol internally.
    """
    sess = _ma_get(payload.session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")
    st = sess.core._grid_state
    if st is None:
        raise HTTPException(status_code=400, detail="Session not initialized")

    directive, grid_msg = _grid_policy(st)

    if payload.fleet_policy == "baseline":
        fleet_action = baseline_policy(st, sess.core.city_graph)
        fleet_msg = NegotiationMessage(role="fleet", text="Routing using heuristic baseline under grid constraints.")
    else:
        action, _txt, active, timed_out, skipped = _demo_oracle_act_with_guard(st=st, core=sess.core, oracle_lora_repo=payload.oracle_lora_repo)
        fleet_action = action
        tag = "LLM" if active else "fallback"
        fleet_msg = NegotiationMessage(role="fleet", text=f"Routing with oracle ({tag}).")

    obs = sess.step(
        grid_directive=directive,
        fleet_action=fleet_action,
        grid_message=grid_msg,
        fleet_message=fleet_msg,
    )
    directive_ok = len(sess.last_violations) == 0
    meaningful = True
    rr = split_role_rewards(obs.reward_breakdown, grid_directive_ok=directive_ok, has_meaningful_messages=meaningful)

    return {
        "session_id": payload.session_id,
        "obs": obs.model_dump(mode="json"),
        "tick": sess.core.step_count,
        "scenario": sess.core.scenario,
        "grid_directive": directive.model_dump(mode="json"),
        "fleet_action": fleet_action.model_dump(mode="json"),
        "resolved_action": sess.last_resolved_action.model_dump(mode="json") if sess.last_resolved_action else fleet_action.model_dump(mode="json"),
        "violations": list(sess.last_violations),
        "messages": [m.model_dump(mode="json") for m in sess.messages[-50:]],
        "role_rewards": rr,
    }


@app.get("/ma/state")
def ma_state(req: Request, session_id: str = Query(...)) -> dict[str, Any]:
    _rate_limit(req, key="ma_state", limit=120, window_sec=60)
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
def ma_step(req: Request, payload: MultiAgentStepRequest = Body(...)) -> dict[str, Any]:
    _rate_limit(req, key="ma_step", limit=120, window_sec=60)
    t0 = time.time()
    rid = _request_id(req)
    sess = _ma_get(payload.session_id)
    if sess is None:
        log.info("ma_step_miss", extra={"rid": rid, "sid": payload.session_id, "ms": int((time.time() - t0) * 1000)})
        raise HTTPException(status_code=404, detail="Unknown session_id")

    gm = payload.grid_message
    fm = payload.fleet_message
    if gm is not None and gm.role != "grid":
        raise HTTPException(status_code=400, detail="grid_message.role must be 'grid'")
    if fm is not None and fm.role != "fleet":
        raise HTTPException(status_code=400, detail="fleet_message.role must be 'fleet'")

    obs = sess.step(
        grid_directive=payload.grid_directive,
        fleet_action=payload.fleet_action,
        grid_message=gm,
        fleet_message=fm,
    )
    out_obs = obs.model_dump(mode="json")

    directive_ok = len(sess.last_violations) == 0
    meaningful = (gm is not None and gm.text.strip() != "") or (fm is not None and fm.text.strip() != "")
    role_rewards = split_role_rewards(
        out_obs.get("reward_breakdown", {}) if isinstance(out_obs, dict) else {},
        grid_directive_ok=directive_ok,
        has_meaningful_messages=meaningful,
    )
    log.info(
        "ma_step",
        extra={
            "rid": rid,
            "sid": payload.session_id,
            "tick": int(sess.core.step_count),
            "viol": ",".join(sess.last_violations),
            "ms": int((time.time() - t0) * 1000),
        },
    )
    return {
        "request_id": rid,
        "session_id": payload.session_id,
        "obs": out_obs,
        "tick": sess.core.step_count,
        "scenario": sess.core.scenario,
        "grid_directive": payload.grid_directive.model_dump(mode="json"),
        "fleet_action": payload.fleet_action.model_dump(mode="json"),
        "resolved_action": sess.last_resolved_action.model_dump(mode="json") if sess.last_resolved_action else payload.fleet_action.model_dump(mode="json"),
        "violations": list(sess.last_violations),
        "messages": [m.model_dump(mode="json") for m in sess.messages[-50:]],
        "role_rewards": role_rewards,
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
def demo_new(req: Request, payload: DemoNewRequest = Body(...)) -> dict[str, Any]:
    _rate_limit(req, key="demo_new", limit=30, window_sec=60)
    t0 = time.time()
    rid = _request_id(req)
    try:
        _demo_session_gc()
        session_id = str(uuid4())
        core = EVGridCore(city_graph=_demo_graph)
        obs = core.reset(seed=payload.seed, scenario=cast(ScenarioName, payload.scenario), fleet_mode=cast(Any, payload.fleet_mode))
        _demo_sessions[session_id] = (time.time(), core)
        from ev_grid_oracle.scenarios import scenario_schedule

        log.info(
            "demo_new",
            extra={"rid": rid, "sid": session_id, "seed": payload.seed, "scenario": str(obs.state and core.scenario), "ms": int((time.time()-t0)*1000)},
        )
        return {
            "request_id": rid,
            "session_id": session_id,
            "obs": _obs_to_jsonable(obs),
            "station_nodes": _station_nodes(core),
            "scenario": core.scenario,
            "seed": payload.seed,
            "sim_version": _SIM_VERSION,
            "scenario_schedule": scenario_schedule(core.scenario),
        }
    except HTTPException:
        raise
    except Exception as e:
        log.exception("demo_new_error", extra={"rid": rid, "ms": int((time.time() - t0) * 1000)})
        raise HTTPException(status_code=500, detail=f"demo_new_error: {type(e).__name__}: {e}")


@app.get("/demo/state")
def demo_state(req: Request, session_id: str = Query(...)) -> dict[str, Any]:
    _rate_limit(req, key="demo_state", limit=120, window_sec=60)
    t0 = time.time()
    rid = _request_id(req)
    core = _demo_session_get(session_id)
    if core is None:
        log.info("demo_state_miss", extra={"rid": rid, "sid": session_id, "ms": int((time.time()-t0)*1000)})
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

    log.info("demo_state", extra={"rid": rid, "sid": session_id, "tick": int(core.step_count), "ms": int((time.time()-t0)*1000)})
    return {
        "request_id": rid,
        "session_id": session_id,
        "obs": _obs_to_jsonable(obs),
        "station_nodes": _station_nodes(core),
        "scenario": core.scenario,
        "sim_version": _SIM_VERSION,
        "scenario_schedule": scenario_schedule(core.scenario),
    }


class DemoSpawnVehicleRequest(BaseModel):
    session_id: str
    min_station_dist_m: float = Field(250.0, ge=50.0, le=3000.0)
    battery_threshold_pct: float = Field(30.0, ge=1.0, le=80.0)


@app.post("/demo/spawn_vehicle")
def demo_spawn_vehicle(req: Request, payload: DemoSpawnVehicleRequest = Body(...)) -> dict[str, Any]:
    """
    Spawn a new EV at a valid road location (away from stations) and immediately compute
    an assignment + route event for the frontend.
    """
    _rate_limit(req, key="demo_spawn_vehicle", limit=80, window_sec=60)
    t0 = time.time()
    rid = _request_id(req)
    core = _demo_session_get(payload.session_id)
    if core is None:
        log.info("demo_spawn_vehicle_miss", extra={"rid": rid, "sid": payload.session_id, "ms": int((time.time()-t0)*1000)})
        raise HTTPException(status_code=404, detail="Unknown session_id")
    st = core._grid_state
    if st is None:
        raise HTTPException(status_code=400, detail="Session not initialized")

    # deterministic id and spawn point
    ev_id = f"SPAWN-{uuid4().hex[:10]}"
    seed_key = f"{core._seed_for_bescom}|{core.scenario}|{core.step_count}|{len(st.pending_evs)}|{ev_id}"
    try:
        lat, lng = _spawn_road_point_away_from_stations(
            core=core,
            min_station_dist_m=float(payload.min_station_dist_m),
            seed_key=seed_key,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Pick nearest station just to fill neighborhood fields (used by policies + prompt).
    nearest = min(st.stations, key=lambda s: haversine_m(lat, lng, float(s.lat), float(s.lng)))
    # Force low battery so it needs charging.
    battery = min(float(payload.battery_threshold_pct) - 1.0, 25.0)
    if battery < 2.0:
        battery = float(payload.battery_threshold_pct) * 0.5
    battery = max(1.0, battery)

    spawned = EVRequest(
        ev_id=ev_id,
        battery_pct_0_100=round(float(battery), 1),
        urgency=round(0.9 if battery < 15.0 else 0.7, 2),
        persona="PrivateOwner",
        price_sensitivity=0.35,
        neighborhood_slug=str(nearest.neighborhood_slug),
        neighborhood_name=str(nearest.neighborhood_name),
        target_charge_pct_0_100=90.0,
        max_wait_minutes=30,
    )
    st.pending_evs.insert(0, spawned)

    # Assignment: re-use the baseline scoring (distance + wait + stress + price),
    # and require capacity (avoid full stations). If none, respond gracefully.
    candidates = [s for s in st.stations if int(s.occupied_slots) < int(s.total_slots)]
    if not candidates:
        return {
            "request_id": rid,
            "session_id": payload.session_id,
            "spawned_ev": spawned.model_dump(mode="json"),
            "assignment": None,
            "event": {"type": "no_station", "reason": "all_stations_full"},
            "ms": int((time.time() - t0) * 1000),
        }

    try:
        action = baseline_policy(st, core.city_graph)
    except Exception:
        # last-resort: pick nearest non-full station
        best = min(candidates, key=lambda s: haversine_m(lat, lng, float(s.lat), float(s.lng)))
        action = EVGridAction(action_type=ActionType.route, ev_id=ev_id, station_id=str(best.station_id), defer_minutes=0)

    assigned_station_id = getattr(action, "station_id", None)
    dst = next((s for s in st.stations if assigned_station_id and s.station_id == assigned_station_id), None)
    if action.action_type != ActionType.route or dst is None:
        return {
            "request_id": rid,
            "session_id": payload.session_id,
            "spawned_ev": spawned.model_dump(mode="json"),
            "assignment": action.model_dump(mode="json"),
            "event": {"type": "no_station", "reason": "policy_defer_or_invalid"},
            "ms": int((time.time() - t0) * 1000),
        }

    traffic = TrafficModel(seed=int(core._seed_for_bescom), scenario=str(core.scenario))
    routed = _osm_route_polyline(src_lat=lat, src_lng=lng, dst_lat=float(dst.lat), dst_lng=float(dst.lng), traffic=traffic, tick=int(core.step_count))
    poly, seg_m_q = routed if routed is not None else ([], None)
    event = {
        "type": "route",
        "ev_id": ev_id,
        "from": {"station_id": "ROAD", "lat": lat, "lng": lng},
        "to": {"station_id": dst.station_id, "lat": dst.lat, "lng": dst.lng},
        "polyline": (poly or [[lat, lng], [float(dst.lat), float(dst.lng)]]),
        "traffic_seg_m_q": seg_m_q,
        "reroute_reason": "spawn",
    }
    log.info(
        "demo_spawn_vehicle",
        extra={"rid": rid, "sid": payload.session_id, "ev_id": ev_id, "to": str(dst.station_id), "ms": int((time.time() - t0) * 1000)},
    )
    return {
        "request_id": rid,
        "session_id": payload.session_id,
        "spawned_ev": spawned.model_dump(mode="json"),
        "assignment": action.model_dump(mode="json"),
        "event": event,
        "ms": int((time.time() - t0) * 1000),
    }


@app.post("/demo/step")
def demo_step(
    req: Request,
    session_id: str = Body(...),
    mode: Literal["baseline", "oracle"] = Body("baseline"),
    oracle_lora_repo: str = Body("", embed=True),
    forced_action: dict[str, Any] | None = Body(None),
) -> dict[str, Any]:
    _rate_limit(req, key="demo_step", limit=120, window_sec=60)
    t0 = time.time()
    rid = _request_id(req)
    core = _demo_session_get(session_id)
    if core is None:
        log.info("demo_step_miss", extra={"rid": rid, "sid": session_id, "ms": int((time.time()-t0)*1000)})
        raise HTTPException(status_code=404, detail="Unknown session_id")

    try:
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
        forced = forced_action is not None
        if forced_action is not None:
            try:
                action = EVGridAction.model_validate(forced_action)
            except Exception as ve:
                issues = ve.errors() if hasattr(ve, "errors") else [{"msg": str(ve)}]
                # Pydantic v2 can include non-JSON-serializable objects under `ctx` (e.g., ValueError instances).
                for it in issues:
                    if isinstance(it, dict) and "ctx" in it:
                        try:
                            ctx = it.get("ctx") or {}
                            if isinstance(ctx, dict):
                                it["ctx"] = {str(k): str(v) for k, v in ctx.items()}
                            else:
                                it["ctx"] = str(ctx)
                        except Exception:
                            it.pop("ctx", None)
                raise HTTPException(status_code=422, detail={"error": "invalid_forced_action", "issues": issues})
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
                    traffic = TrafficModel(seed=int(core._seed_for_bescom), scenario=str(core.scenario))
                    routed = _osm_route_polyline(
                        src_lat=float(src.lat),
                        src_lng=float(src.lng),
                        dst_lat=float(dst.lat),
                        dst_lng=float(dst.lng),
                        traffic=traffic,
                        tick=int(core.step_count),
                    )
                    poly, seg_m_q = routed if routed is not None else ([], None)
                    event = {
                        "type": "route",
                        "ev_id": ev.ev_id,
                        "from": {"station_id": src.station_id, "lat": src.lat, "lng": src.lng},
                        "to": {"station_id": dst.station_id, "lat": dst.lat, "lng": dst.lng},
                        "polyline": (poly or _graph_route_polyline(core, src_station_id=src.station_id, dst_station_id=dst.station_id)),
                        "traffic_seg_m_q": seg_m_q,
                        "reroute_reason": "periodic" if (int(core.step_count) % 6 == 0) else None,
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

        # Render-friendly event for frontend animation (skip overwriting if replaying forced_action).
        # v0: polyline path is station-to-station graph path (lat/lng pairs).
        if not forced and st is not None and st.pending_evs:
            ev = st.pending_evs[0]
            src = next((x for x in st.stations if x.neighborhood_slug == ev.neighborhood_slug), None)
            dst = next((x for x in st.stations if x.station_id == action.station_id), None)
            if action.action_type == ActionType.route and src is not None and dst is not None:
                traffic = TrafficModel(seed=int(core._seed_for_bescom), scenario=str(core.scenario))
                routed = _osm_route_polyline(
                    src_lat=float(src.lat),
                    src_lng=float(src.lng),
                    dst_lat=float(dst.lat),
                    dst_lng=float(dst.lng),
                    traffic=traffic,
                    tick=int(core.step_count),
                )
                poly, seg_m_q = routed if routed is not None else ([], None)
                event = {
                    "type": "route",
                    "ev_id": ev.ev_id,
                    "from": {"station_id": src.station_id, "lat": src.lat, "lng": src.lng},
                    "to": {"station_id": dst.station_id, "lat": dst.lat, "lng": dst.lng},
                    "polyline": (poly or _graph_route_polyline(core, src_station_id=src.station_id, dst_station_id=dst.station_id)),
                    "traffic_seg_m_q": seg_m_q,
                    "reroute_reason": "periodic" if (int(core.step_count) % 6 == 0) else None,
                }
            else:
                event = {"type": action.action_type.value}

        # Ensure the map always looks alive: if action isn't a route, emit a deterministic
        # ambient trip for UI motion (does not affect env dynamics or rewards).
        if (event.get("type") != "route") and st is not None and len(st.stations) >= 2:
            tick_i = int(core.step_count)
            seed_i = int(core._seed_for_bescom)
            scen = str(core.scenario)
            h = hashlib.sha1(f"{seed_i}|{scen}|{mode}|ambient|{tick_i}".encode("utf-8")).digest()
            a_i = int.from_bytes(h[:2], "big") % len(st.stations)
            b_i = int.from_bytes(h[2:4], "big") % len(st.stations)
            if b_i == a_i:
                b_i = (b_i + 1) % len(st.stations)
            src2 = st.stations[a_i]
            dst2 = st.stations[b_i]
            traffic2 = TrafficModel(seed=seed_i, scenario=scen)
            routed2 = _osm_route_polyline(
                src_lat=float(src2.lat),
                src_lng=float(src2.lng),
                dst_lat=float(dst2.lat),
                dst_lng=float(dst2.lng),
                traffic=traffic2,
                tick=tick_i,
            )
            poly2, seg2 = routed2 if routed2 is not None else ([], None)
            event = {
                "type": "route",
                "ev_id": f"AMBIENT-{mode}-{a_i}-{b_i}",
                "from": {"station_id": src2.station_id, "lat": src2.lat, "lng": src2.lng},
                "to": {"station_id": dst2.station_id, "lat": dst2.lat, "lng": dst2.lng},
                "polyline": (poly2 or _graph_route_polyline(core, src_station_id=src2.station_id, dst_station_id=dst2.station_id)),
                "traffic_seg_m_q": seg2,
                "reroute_reason": "ambient",
            }

        obs = core.step(action)
        anti_flags = obs.anti_cheat_flags
        anti_details = obs.anti_cheat_details
        role_kpis = compute_role_kpis(obs)
        role_reward_breakdown = compute_role_reward_breakdown(obs)
        out = {
            "request_id": rid,
            "obs": _obs_to_jsonable(obs),
            "event": event,
            "scenario": core.scenario,
            "scenario_events_at_tick": core.last_scenario_events,
            "tick": core.step_count,
            "tick_dt_s": float(core.step_minutes) * 60.0,
            "schema_version": "traffic-v1",
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
                "rid": rid,
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
    except HTTPException:
        raise
    except Exception as e:
        log.exception("demo_step_error", extra={"rid": rid, "sid": session_id, "mode": mode, "ms": int((time.time() - t0) * 1000)})
        raise HTTPException(status_code=500, detail=f"demo_step_error: {type(e).__name__}: {e}")


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

