import os
import torch
from unsloth import FastLanguageModel, PatchFastRL
from trl import GRPOConfig, GRPOTrainer
from datasets import Dataset
import gymnasium as gym
import wandb

# Patch Unsloth for RLHF trainers
PatchFastRL()

# ==========================================
# 1. HARDWARE & LOGGING CONFIGURATION
# ==========================================
# Optimized for Google Colab T4 (16GB VRAM)
max_seq_length = 512 # Keep this small for T4 to avoid OOM
load_in_4bit = True
model_name = "unsloth/gemma-1.1-2b-it-bnb-4bit"

# Initialize Weights & Biases for Hackathon tracking
wandb.init(
    project="meta-hf-hackathon-ev-oracle",
    name="grpo-bescom-ev-v1",
    config={
        "model": model_name,
        "method": "GRPO",
        "batch_size": 1,
        "grad_accum": 4,
    }
)

# ==========================================
# 2. LOAD MODEL & TOKENIZER (UNSLOTH)
# ==========================================
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = load_in_4bit,
    fast_inference = True, # Optimization for GRPO completions
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Rank
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth", # Crucial for T4 VRAM
    random_state = 3407,
)

import re

# ==========================================
# 3. PRODUCTION REWARD FUNCTIONS
# ==========================================

def extract_xml_answer(text, tag):
    """Helper to extract content between XML tags."""
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else None

def format_reward_func(completions, **kwargs) -> list[float]:
    """
    Elite format reward: Validates XML structure for <thought> and <action>.
    """
    rewards = []
    for content in completions:
        score = 0.0
        if "<thought>" in content and "</thought>" in content:
            score += 0.5
        if "<action>" in content and "</action>" in content:
            # Action must be one of the valid Gymnasium actions
            action_text = extract_xml_answer(content, "action")
            valid_actions = ["inspect", "prioritize", "summarize", "schedule", "report"]
            if action_text and any(a in action_text.lower() for a in valid_actions):
                score += 0.5
        rewards.append(score)
    return rewards

def constraint_reward_func(completions, prompts, **kwargs) -> list[float]:
    """
    Grid constraint reward: Penalizes reasoning that ignores high load warnings.
    Works with 10-node multi-load observations.
    """
    rewards = []
    for content, prompt in zip(completions, prompts):
        score = 1.0
        # If any node in the prompt shows a load >= 0.9 and action is 'schedule'
        # We look for decimals like 0.9x or 1.00
        if re.search(r"0\.9\d|1\.00", prompt) and "schedule" in content.lower():
            score = -2.0 # Increased penalty for multi-node risk
        rewards.append(score)
    return rewards

def objective_reward_func(completions, **kwargs) -> list[float]:
    """
    Reasoning quality reward: Rewards longer, detailed thought processes.
    """
    rewards = []
    for content in completions:
        thought = extract_xml_answer(content, "thought")
        if thought and len(thought) > 100: # Reward deep thinking
            rewards.append(1.0)
        else:
            rewards.append(0.0)
    return rewards

from env_bescom import BESCOM_EV_Env

# ==========================================
# 4. ENVIRONMENT HOOK & DATA PREPARATION
# ==========================================
def format_observation_to_prompt(obs):
    """
    Converts BESCOM_EV_Env observation into a prompt for the model.
    The model is instructed to use <thought> and <action> tags.
    """
    prompt = f"""### Instruction:
You are the BESCOM EV Grid Oracle. Based on the current grid state, decide the next optimal charging schedule.
Your goal is to balance EV demand without exceeding transformer capacity.

Provide your response strictly in the following format:
<thought>
[Your reasoning about the grid state and constraints]
</thought>
<action>
[One of: inspect, prioritize, summarize, schedule, report]
</action>

### Current Observation:
{obs}

### Response:
"""
    return prompt

# Real environment-based dataset generation
def get_training_dataset(num_samples=100):
    env = BESCOM_EV_Env()
    prompts = []
    
    for _ in range(num_samples):
        obs, _ = env.reset()
        # We can also simulate some steps to get diverse observations
        for _ in range(np.random.randint(0, 3)):
            obs, _, _, _, _ = env.step(env.action_space.sample())
        
        prompts.append(format_observation_to_prompt(obs))
    
    return Dataset.from_dict({"prompt": prompts})

import numpy as np # Needed for sampling
train_dataset = get_training_dataset()

# ==========================================
# 5. GRPO CONFIGURATION & TRAINING
# ==========================================
training_args = GRPOConfig(
    output_dir = "trained_ev_oracle_checkpoints",
    per_device_train_batch_size = 1,
    gradient_accumulation_steps = 4,
    learning_rate = 5e-5,
    max_prompt_length = 256,
    max_completion_length = 128,
    num_generations = 2, # Number of completions to sample per prompt for GRPO
    max_steps = 100, # Adjust for hackathon duration
    logging_steps = 1,
    report_to = "wandb",
)

trainer = GRPOTrainer(
    model = model,
    reward_funcs = [
        format_reward_func,
        constraint_reward_func,
        objective_reward_func,
    ],
    args = training_args,
    train_dataset = train_dataset,
    # tokenizer = tokenizer, # Often needed for sequence length checks
)

print("Starting GRPO Training...")
trainer.train()

# ==========================================
# 6. SAVE THE MODEL (THE SAVE TRAP)
# ==========================================
print("Training complete. Merging and saving model...")

# CRITICAL: Use Unsloth's specific save function to avoid 4-bit/16-bit merge issues
model.save_pretrained_merged(
    "trained_ev_oracle", 
    tokenizer, 
    save_method = "merged_16bit"
)

print("Model successfully saved to 'trained_ev_oracle' in 16-bit format.")
wandb.finish()
