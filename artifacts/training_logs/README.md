# Training logs (place exports here)

Commit **small** artifacts judges can open without cloning multi‑GB checkpoints:

- `colab_console_tail.txt` — last lines of Colab output (step, loss, reward)  
- Optional: `trainer_state.json` from a short run (strip paths if sensitive)  
- Prefer **PNG screenshots** of TensorBoard (**reward**, **loss**) at repo root `artifacts/grpo_*.png` so they appear in the README gallery  

See **[`docs/submission/training-artifacts-and-logs.md`](../../docs/submission/training-artifacts-and-logs.md)** for the full checklist.
