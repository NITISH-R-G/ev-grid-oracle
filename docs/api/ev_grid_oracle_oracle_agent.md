# Documentation for `ev_grid_oracle/oracle_agent.py`

## Classes

### Class `OracleRuntime`

Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

### Class `OracleAgent`

Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

## Functions

### Function `load`

No documentation provided.

### Function `_ensure_loaded`

No documentation provided.

### Function `act`

No documentation provided.

### Function `act_with_text`

No documentation provided.

### Function `is_active`

No documentation provided.

### Function `_generate`

No documentation provided.
