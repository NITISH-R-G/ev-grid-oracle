# API Reference for `./ev_grid_oracle/oracle_agent.py`

## Class: `OracleRuntime`

Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

## Class: `OracleAgent`

Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

## Function: `load`

No docstring available.

## Function: `_ensure_loaded`

No docstring available.

## Function: `act`

No docstring available.

## Function: `act_with_text`

No docstring available.

## Function: `is_active`

No docstring available.

## Function: `_generate`

No docstring available.
