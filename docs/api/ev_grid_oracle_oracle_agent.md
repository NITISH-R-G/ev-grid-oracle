# Documentation for `./ev_grid_oracle/oracle_agent.py`

## Classes

### `OracleRuntime`
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

### `OracleAgent`
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

## Functions

### `load`
*No docstring available.*

### `_ensure_loaded`
*No docstring available.*

### `act`
*No docstring available.*

### `act_with_text`
*No docstring available.*

### `is_active`
*No docstring available.*

### `_generate`
*No docstring available.*
