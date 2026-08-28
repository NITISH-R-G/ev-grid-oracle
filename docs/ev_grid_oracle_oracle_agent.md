# Documentation for ev_grid_oracle/oracle_agent.py

## Classes

### OracleRuntime
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

### OracleAgent
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

## Functions

### load
No docstring provided.

### _ensure_loaded
No docstring provided.

### act
No docstring provided.

### act_with_text
No docstring provided.

### is_active
No docstring provided.

### _generate
No docstring provided.
