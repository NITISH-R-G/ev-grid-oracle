from __future__ import annotations

try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:  # pragma: no cover
    raise ImportError("openenv-core required. Install deps from pyproject.") from e

from typing import Any, Literal
from uuid import uuid4

from pathlib import Path
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
from ev_grid_oracle.world_model_verifier import rollout_deterministic_5ticks, score_prediction
from server.ev_grid_environment import EVGridEnvironment


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

_demo_sessions: dict[str, EVGridCore] = {}
_demo_graph = build_city_graph()


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
def demo_new(payload: "DemoNewRequest" = Body(...)) -> dict[str, Any]:
    session_id = str(uuid4())
    core = EVGridCore(city_graph=_demo_graph)
    obs = core.reset(seed=payload.seed, scenario=payload.scenario)
    _demo_sessions[session_id] = core
    return {
        "session_id": session_id,
        "obs": _obs_to_jsonable(obs),
        "station_nodes": _station_nodes(core),
        "scenario": core.scenario,
        "seed": payload.seed,
    }


class DemoNewRequest(BaseModel):
    seed: int = Field(123, ge=0, le=1_000_000)
    scenario: str = Field("baseline")


@app.get("/demo/state")
def demo_state(session_id: str = Query(...)) -> dict[str, Any]:
    core = _demo_sessions.get(session_id)
    if core is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")
    st = core._grid_state
    if st is None:
        obs = core.reset(seed=123)
    else:
        obs = EVGridObservation(prompt=_build_prompt(st), state=st, done=False, reward_breakdown={})
    return {"session_id": session_id, "obs": _obs_to_jsonable(obs), "station_nodes": _station_nodes(core)}


@app.post("/demo/step")
def demo_step(
    session_id: str = Body(...),
    mode: Literal["baseline", "oracle"] = Body("baseline"),
    oracle_lora_repo: str = Body("", embed=True),
) -> dict[str, Any]:
    core = _demo_sessions.get(session_id)
    if core is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")

    st = core._grid_state
    oracle_llm_active = False
    oracle_text = ""
    dream_score = None
    dream_breakdown: dict[str, float] = {}
    dream_pred = None
    dream_true = None
    if st is None or not st.pending_evs:
        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        event: dict[str, Any] = {"type": "idle"}
    else:
        if mode == "baseline":
            action = baseline_policy(st, core.city_graph)
        else:
            agent = OracleAgent(lora_repo_id=(oracle_lora_repo or "").strip() or None)
            action, oracle_text = agent.act_with_text(st, _build_prompt(st), core.city_graph)
            oracle_llm_active = bool(agent.is_active)

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

    # scenario events that fired at this tick
    from ev_grid_oracle.scenarios import scenario_schedule

    sched = scenario_schedule(core.scenario)
    fired = [e for e in sched if int(e.get("tick", -1)) == int(core.step_count + 1)]

    obs = core.step(action)
    return {
        "obs": _obs_to_jsonable(obs),
        "event": event,
        "scenario": core.scenario,
        "scenario_events": fired,
        "tick": core.step_count,
        "mode": mode,
        "oracle_lora_repo": (oracle_lora_repo or "").strip(),
        "oracle_llm_active": oracle_llm_active,
        "action": action.model_dump(),
        "oracle_text": oracle_text,
        "dream_score": dream_score,
        "dream_breakdown": dream_breakdown,
        "dream_pred": dream_pred,
        "dream_true": dream_true,
    }


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

