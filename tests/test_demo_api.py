from fastapi.testclient import TestClient


def test_demo_new_and_step_roundtrip():
    # Import inside test so module import errors surface as test failures.
    from server.app import app

    c = TestClient(app)

    r = c.post("/demo/new", json={"seed": 123})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data and isinstance(data["session_id"], str) and data["session_id"]
    assert "obs" in data and isinstance(data["obs"], dict)
    assert "station_nodes" in data and isinstance(data["station_nodes"], list)
    assert data.get("scenario") == "baseline"
    assert isinstance(data.get("sim_version"), str) and data["sim_version"]
    assert isinstance(data.get("scenario_schedule"), list)

    sid = data["session_id"]
    r2 = c.post("/demo/step", json={"session_id": sid, "mode": "baseline", "oracle_lora_repo": ""})
    assert r2.status_code == 200
    data2 = r2.json()
    assert "obs" in data2 and isinstance(data2["obs"], dict)
    assert "event" in data2 and isinstance(data2["event"], dict)
    assert data2.get("mode") == "baseline"
    assert "action" in data2 and isinstance(data2["action"], dict)
    assert "oracle_llm_active" in data2
    assert isinstance(data2.get("tick"), int)
    assert isinstance(data2.get("scenario_events_at_tick"), list)
    assert isinstance(data2.get("anti_cheat_flags"), list)
    assert isinstance(data2.get("anti_cheat_details"), dict)
    assert isinstance(data2.get("sim_version"), str) and data2["sim_version"]

