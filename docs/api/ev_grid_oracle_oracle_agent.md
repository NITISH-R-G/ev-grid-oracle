# Module: `./ev_grid_oracle/oracle_agent.py`

**Description:**
*No module docstring provided.*

## Class: `OracleRuntime`
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

### Method: `OracleRuntime.load`
*No method docstring provided.*

## Class: `OracleAgent`
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

### Method: `OracleAgent._ensure_loaded`
*No method docstring provided.*

### Method: `OracleAgent.act`
*No method docstring provided.*

### Method: `OracleAgent.act_with_text`
*No method docstring provided.*

### Method: `OracleAgent.is_active`
*No method docstring provided.*

### Method: `OracleAgent._generate`
*No method docstring provided.*

