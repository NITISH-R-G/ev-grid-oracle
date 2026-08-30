# Fix ruff C414 in city_graph
sed -i 's/comps = \[sorted(list(c)) for c in nx.connected_components(g)\]/comps = [sorted(c) for c in nx.connected_components(g)]/g' ev_grid_oracle/city_graph.py
# Fix env.py RUF046
sed -i 's/arrivals = int(round(arrivals \* float(self._scenario_mods.arrivals_mult)))/arrivals = round(arrivals * float(self._scenario_mods.arrivals_mult))/g' ev_grid_oracle/env.py

# Fix B008 DemandParams
sed -i 's/params: DemandParams = DemandParams()/params: DemandParams | None = None/g' ev_grid_oracle/demand_sim.py
# We can't multiline sed easily so just modify the body directly if needed, but actually since we added type None the body needs fixing too
sed -i '/def expected_arrivals_per_step(/a\    if params is None:\n        params = DemandParams()' ev_grid_oracle/demand_sim.py
sed -i '/def sample_arrivals_per_step(/a\    if params is None:\n        params = DemandParams()' ev_grid_oracle/demand_sim.py

# Fix B008 GridParams
sed -i 's/params: GridParams = GridParams()/params: GridParams | None = None/g' ev_grid_oracle/grid_sim.py
sed -i '/def baseline_grid_load(/a\    if params is None:\n        params = GridParams()' ev_grid_oracle/grid_sim.py
sed -i '/def renewable_pct(hour: int/a\    if params is None:\n        params = GridParams()' ev_grid_oracle/grid_sim.py
sed -i '/def evaluate_action(/a\    if params is None:\n        params = GridParams()' ev_grid_oracle/grid_sim.py

# Replace zip with pairwise in reward
sed -i 's/zip(path, path\[1:\])/itertools.pairwise(path)/g' ev_grid_oracle/reward.py
# Need to import itertools in reward
sed -i '1i import itertools' ev_grid_oracle/reward.py

# Fix mutable default in oracle_agent.py
sed -i 's/_loaded: dict\[tuple\[str, str, str\], tuple\[object, object\]\] = {}/_loaded: typing.ClassVar[dict[tuple[str, str, str], tuple[object, object]]] = {}/g' ev_grid_oracle/oracle_agent.py
sed -i '1i import typing' ev_grid_oracle/oracle_agent.py

# Fix build_road_graph
sed -i 's/ilat = int(round(float(lat) \* factor))/ilat = round(float(lat) * factor)/g' tools/build_road_graph.py
sed -i 's/ilng = int(round(float(lng) \* factor))/ilng = round(float(lng) * factor)/g' tools/build_road_graph.py
sed -i 's/zip(snapped, snapped\[1:\])/itertools.pairwise(snapped)/g' tools/build_road_graph.py
sed -i 's/zip(seg_geom, seg_geom\[1:\])/itertools.pairwise(seg_geom)/g' tools/build_road_graph.py
sed -i '1i import itertools' tools/build_road_graph.py
sed -i 's/keep_nodes_set = set(int(x) for x in keep_nodes)/keep_nodes_set = {int(x) for x in keep_nodes}/g' tools/build_road_graph.py

# Unused loop vars in build_road_graph
sed -i 's/v_kmh = speed_kmh(highway)/v_kmh = speed_kmh(str(highway))/g' tools/build_road_graph.py
sed -i 's/"highway": highway,/"highway": str(highway),/g' tools/build_road_graph.py
sed -i 's/"name": name,/"name": str(name),/g' tools/build_road_graph.py

# road_reward_smoke.py
sed -i 's/nb = list(core.g.neighbors(st.node))\[0\]/nb = next(iter(core.g.neighbors(st.node)))/g' tools/road_reward_smoke.py

# viz/city_map.py B008
sed -i 's/cfg: RenderConfig = RenderConfig()/cfg: RenderConfig | None = None/g' viz/city_map.py
sed -i '/def __init__(self, env: EVGridCore, cfg: RenderConfig | None = None):/a\        if cfg is None:\n            cfg = RenderConfig()' viz/city_map.py

# PLC0206 server/role_metrics.py
sed -i 's/for r in out:/for r, out_r in out.items():/g' server/role_metrics.py
sed -i 's/out\[r\]\[k\] = /out_r[k] = /g' server/role_metrics.py
