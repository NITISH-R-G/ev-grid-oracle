# Documentation for ev_grid_oracle/oracle_agent.py

### Class: `OracleRuntime`
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

#### Method: `load`

### Class: `OracleAgent`
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

#### Method: `_ensure_loaded`

#### Method: `act`

#### Method: `act_with_text`

#### Method: `is_active`

#### Method: `_generate`
