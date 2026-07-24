# Documentation for `./ev_grid_oracle/bescom_feed.py`

## Classes

### `BESCOMFeedAPI`
Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.

## Functions

### `snapshot`
*No docstring available.*

### `_stable_seed`
*No docstring available.*

### `_zone_for_station`
*No docstring available.*
