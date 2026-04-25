#!/bin/bash
# setup_colab.sh - Script to prepare Google Colab for GRPO Training

echo "Installing Unsloth and RLHF dependencies..."
pip install --no-deps "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "trl<0.9.0" peft accelerate bitsandbytes
pip install gymnasium wandb datasets

echo "Configuration complete. You can now run: python train_grpo.py"
