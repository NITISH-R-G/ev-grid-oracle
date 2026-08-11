# Documentation for `./server/ev_grid_road_environment.py`

## Classes

### EVGridRoadEnvironment
Separate OpenEnv environment that forces real-road-graph actions.
Mounted as a sub-app under /road/ so it doesn't break the existing env.

**Methods:**
- `__init__`
- `reset`
- `step`
- `state`
