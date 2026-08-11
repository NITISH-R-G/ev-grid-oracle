# Documentation for `./ev_grid_oracle/oracle_agent.py`

## Classes

### OracleRuntime
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

**Methods:**
- `load`

### OracleAgent
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

**Methods:**
- `_ensure_loaded`
- `act`
- `act_with_text`
- `is_active`
- `_generate`
