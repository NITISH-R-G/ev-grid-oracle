from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction, SimTopStation, SimulationPrediction
from ev_grid_oracle.policies import baseline_policy
from ev_grid_oracle.world_model_verifier import rollout_deterministic_5ticks, score_prediction


def test_rollout_deterministic_is_stable():
    g = build_city_graph()
    core = EVGridCore(city_graph=g)
    obs = core.reset(seed=123)
    st = obs.state
    if not st.pending_evs:
        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
    else:
        action = baseline_policy(st, g)

    a = rollout_deterministic_5ticks(st, action)
    b = rollout_deterministic_5ticks(st, action)
    assert a.model_dump() == b.model_dump()


def test_prediction_score_higher_when_close():
    g = build_city_graph()
    core = EVGridCore(city_graph=g)
    obs = core.reset(seed=123)
    st = obs.state
    if not st.pending_evs:
        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
    else:
        action = baseline_policy(st, g)

    true5 = rollout_deterministic_5ticks(st, action)
    top = sorted(
        [
            (s.station_id, s.occupied_slots / max(1, s.total_slots), s.queue_length)
            for s in true5.stations
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    pred_good = SimulationPrediction(
        t5_grid_load_pct=true5.grid_load_pct,
        t5_renewable_pct=true5.renewable_pct,
        t5_top_stations=[SimTopStation(station_id=sid, load_pct=float(load), queue=int(q)) for sid, load, q in top],
    )
    pred_bad = SimulationPrediction(
        t5_grid_load_pct=0.0,
        t5_renewable_pct=1.0,
        t5_top_stations=[SimTopStation(station_id="BLR-01", load_pct=0.0, queue=0)],
    )

    s_good = score_prediction(st, action, pred_good)
    s_bad = score_prediction(st, action, pred_bad)
    assert s_good.score_0_1 > s_bad.score_0_1

