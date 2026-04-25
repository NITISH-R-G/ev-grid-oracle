from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ev_grid_oracle.models import EVGridAction, GridState
from ev_grid_oracle.parsing import parse_action
from ev_grid_oracle.policies import baseline_policy


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

        # CPU-safe default. (For speed, prefer running inference on a GPU Space later.)
        tok = AutoTokenizer.from_pretrained(self.base_model_id, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(
            self.base_model_id,
            device_map="cpu",
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        )
        model = PeftModel.from_pretrained(model, self.lora_repo_id)
        model.eval()

        self._tokenizer = tok
        self._model = model

    def act(self, state: GridState, prompt: str, graph) -> EVGridAction:
        # choose target ev_id (matches env prompt builder v0)
        ev_id = state.pending_evs[0].ev_id if state.pending_evs else "EV-000"

        self._ensure_loaded()
        if self.lora_repo_id and self._model is not None and self._tokenizer is not None:
            txt = self._generate(prompt)
            action = parse_action(txt, ev_id=ev_id)
            if action is not None:
                return action

        return baseline_policy(state, graph)

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

