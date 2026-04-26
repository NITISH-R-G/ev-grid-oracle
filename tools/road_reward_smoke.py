from __future__ import annotations

import re

from ev_grid_oracle.road_env import RoadCore
from ev_grid_oracle.road_models import RoadAction, RoadState


def main() -> int:
    core = RoadCore(g=None, nodes=[])  # type: ignore[arg-type]
    obs = core.reset(seed=0)
    st = obs.state
    nb = list(core.g.neighbors(st.node))[0]

    ok = f"CURRENT_NODE: {st.node}\nNEXT_NODE: {int(nb)}\nREASON: go\nCONFIDENCE: 0.7\n"
    bad = f"CURRENT_NODE: {st.node + 999}\nNEXT_NODE: {int(nb)}\nREASON: hack\nCONFIDENCE: 0.7\n"

    r = re.compile(r"CURRENT_NODE:\s*(\d+)\s*\nNEXT_NODE:\s*(\d+)\s*\n", re.I)

    def parse(t: str) -> RoadAction | None:
        m = r.search(t.strip())
        if not m:
            return None
        return RoadAction(current_node=int(m.group(1)), next_node=int(m.group(2)))

    def reward(comp: str) -> float:
        st2 = RoadState.model_validate(st.model_dump(mode="json"))
        a = parse(comp)
        if a is None or int(a.current_node) != int(st2.node):
            return -1.0
        local = RoadCore(g=core.g, nodes=core.nodes)
        local.node = int(st2.node)
        local.battery_pct = float(st2.battery_pct_0_100)
        local.target_station_id = str(st2.target_station_id)
        local.steps_remaining = int(st2.steps_remaining)
        ob = local.step(a)
        base = float(ob.reward_breakdown.get("total", 0.0))
        cheat = -1.0 if ob.anti_cheat_flags else 0.0
        return base + cheat

    print("ok", reward(ok))
    print("bad", reward(bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

