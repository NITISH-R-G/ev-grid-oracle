from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from ev_grid_oracle.models import EVGridAction, GridState
from ev_grid_oracle.parsing import parse_action, parse_simulation
from ev_grid_oracle.policies import baseline_policy


_CACHE = {}
_CACHE_LOCK = None


class OracleRuntime:
    """
    Singleton-style loader that prefers CUDA when available.

    This keeps T4 Spaces fast and makes oracle behavior undeniable.
    """

    _lock = None
    _loaded: dict[tuple[str, str, str], tuple[object, object]] = {}

    @classmethod
    def load(cls, *, base_model_id: str, lora_repo_id: str, device: str) -> tuple[object, object] | None:
        if not lora_repo_id:
            return None
        if cls._lock is None:
            import threading

            cls._lock = threading.Lock()
        key = (base_model_id, lora_repo_id, device)
        with cls._lock:
            if key in cls._loaded:
                return cls._loaded[key]

        try:
            import torch
            from peft import PeftModel
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except Exception:
            return None

        dtype = torch.float16 if device.startswith("cuda") else torch.float32
        tok = AutoTokenizer.from_pretrained(base_model_id, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            device_map=device if device != "cuda" else "auto",
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
        )
        model = PeftModel.from_pretrained(model, lora_repo_id)
        model.eval()

        with cls._lock:
            cls._loaded[key] = (tok, model)
        return tok, model


@dataclass
class OracleAgent:
    """
    Oracle agent wrapper.

    Default: baseline fallback (always available).
    Optional: load a trained LoRA adapter when `lora_repo_id` provided.
    """

    lora_repo_id: Optional[str] = None
    base_model_id: str = "unsloth/Qwen2.5-3B-Instruct"
    max_new_tokens: int = 140

    _loaded: bool = False
    _tokenizer = None
    _model = None

    def _ensure_loaded(self):
        global _CACHE_LOCK
        if _CACHE_LOCK is None:
            import threading

            _CACHE_LOCK = threading.Lock()

        if self._loaded:
            return
        self._loaded = True

        if not self.lora_repo_id:
            return

        # Lazy import to keep Space CPU demo alive even without ML deps.
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
        except Exception:
            # No deps -> baseline fallback
            self.lora_repo_id = None
            return

        cache_key = (self.base_model_id, self.lora_repo_id)
        with _CACHE_LOCK:
            cached = _CACHE.get(cache_key)
            if cached is not None:
                self._tokenizer, self._model = cached
                return

        # Prefer CUDA when available (T4 Space).
        device = "cuda" if torch.cuda.is_available() else "cpu"
        loaded = OracleRuntime.load(base_model_id=self.base_model_id, lora_repo_id=self.lora_repo_id, device=device)
        if loaded is None:
            self.lora_repo_id = None
            return
        tok, model = loaded

        self._tokenizer = tok
        self._model = model
        with _CACHE_LOCK:
            _CACHE[cache_key] = (tok, model)

    def act(self, state: GridState, prompt: str, graph) -> EVGridAction:
        action, _txt = self.act_with_text(state, prompt, graph)
        return action

    def act_with_text(self, state: GridState, prompt: str, graph) -> Tuple[EVGridAction, str]:
        # choose target ev_id (matches env prompt builder v0)
        ev_id = state.pending_evs[0].ev_id if state.pending_evs else "EV-000"

        self._ensure_loaded()
        if self.lora_repo_id and self._model is not None and self._tokenizer is not None:
            txt = self._generate(prompt)
            action = parse_action(txt, ev_id=ev_id)
            if action is not None:
                return action, txt

        return baseline_policy(state, graph), ""

    @property
    def is_active(self) -> bool:
        return bool(self.lora_repo_id) and self._model is not None and self._tokenizer is not None

    def _generate(self, prompt: str) -> str:
        tok = self._tokenizer
        model = self._model
        if tok is None or model is None:
            return ""
        import torch

        inputs = tok(prompt, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )
        return tok.decode(out[0], skip_special_tokens=True)

