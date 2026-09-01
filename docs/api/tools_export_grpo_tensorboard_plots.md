# API Documentation for `tools/export_grpo_tensorboard_plots.py`

## Module Description
Export loss + reward (or closest TRL scalar tags) from a TensorBoard run dir into PNGs.

Hackathon requirement: committed plots from a *real* GRPO run. After `trainer.train()` in
`training/train_grpo.ipynb`, copy `ev_oracle_grpo_road/` from Colab (or run locally), then:

  pip install tensorboard matplotlib
  python tools/export_grpo_tensorboard_plots.py --logdir ev_oracle_grpo_road --out-dir artifacts

Writes e.g. artifacts/grpo_loss.png and artifacts/grpo_reward.png (filenames depend on tags found).

## Function `_pick_tags`

## Function `main`
