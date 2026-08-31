# Documentation for `ev_grid_oracle/bescom_feed.py`

## Class: `BESCOMFeedAPI`

Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.

## Function: `snapshot`

## Function: `_stable_seed`

## Function: `_zone_for_station`

