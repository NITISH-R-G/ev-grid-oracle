from __future__ import annotations

try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:  # pragma: no cover
    raise ImportError("openenv-core required. Install deps from pyproject.") from e

from typing import Any, Literal
from uuid import uuid4

from fastapi import Body, HTTPException, Query

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore, _build_prompt
from ev_grid_oracle.models import ActionType, EVGridAction, EVGridObservation
from ev_grid_oracle.oracle_agent import OracleAgent
from ev_grid_oracle.policies import baseline_policy
from server.ev_grid_environment import EVGridEnvironment


app = create_app(EVGridEnvironment, EVGridAction, EVGridObservation, env_name="ev-grid-oracle", max_concurrent_envs=1)


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
def demo_new(seed: int = Body(123, embed=True)) -> dict[str, Any]:
    session_id = str(uuid4())
    core = EVGridCore(city_graph=_demo_graph)
    obs = core.reset(seed=seed)
    _demo_sessions[session_id] = core
    return {"session_id": session_id, "obs": _obs_to_jsonable(obs), "station_nodes": _station_nodes(core)}


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
    if st is None or not st.pending_evs:
        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        event: dict[str, Any] = {"type": "idle"}
    else:
        if mode == "baseline":
            action = baseline_policy(st, core.city_graph)
        else:
            agent = OracleAgent(lora_repo_id=(oracle_lora_repo or "").strip() or None)
            action = agent.act(st, _build_prompt(st), core.city_graph)
            oracle_llm_active = bool(agent.is_active)

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
    return {
        "obs": _obs_to_jsonable(obs),
        "event": event,
        "mode": mode,
        "oracle_lora_repo": (oracle_lora_repo or "").strip(),
        "oracle_llm_active": oracle_llm_active,
        "action": action.model_dump(),
    }


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

