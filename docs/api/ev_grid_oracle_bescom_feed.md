# Module: `./ev_grid_oracle/bescom_feed.py`

**Description:**
*No module docstring provided.*

## Class: `BESCOMFeedAPI`
Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.

### Method: `BESCOMFeedAPI.snapshot`
*No method docstring provided.*

### Method: `BESCOMFeedAPI._stable_seed`
*No method docstring provided.*

### Method: `BESCOMFeedAPI._zone_for_station`
*No method docstring provided.*

