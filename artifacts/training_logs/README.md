# Training logs (place exports here)

Commit **small** artifacts judges can open without cloning multi‑GB checkpoints:

- `colab_console_tail.txt` — last lines of Colab output (step, loss, reward)  
- Optional: `trainer_state.json` from a short run (strip paths if sensitive)  
- Prefer **`artifacts/grpo_loss.png`** and **`artifacts/grpo_reward.png`** from `tools/export_grpo_tensorboard_plots.py` (or TensorBoard screenshots) so judges see **real** GRPO scalars  

See **[`docs/submission/training-artifacts-and-logs.md`](../../docs/submission/training-artifacts-and-logs.md)** for the full checklist.
