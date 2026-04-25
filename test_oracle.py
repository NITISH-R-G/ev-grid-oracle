import torch
from unsloth import FastLanguageModel
from env_bescom import BESCOM_EV_Env
import re

# ==========================================
# 1. LOAD TRAINED MODEL
# ==========================================
model_path = "trained_ev_oracle" # Path to the merged 16bit model
max_seq_length = 512

print(f"Loading trained oracle from {model_path}...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_path,
    max_seq_length = max_seq_length,
    load_in_4bit = False, # Load the merged 16bit weights
)
FastLanguageModel.for_inference(model)

# ==========================================
# 2. INFERENCE LOGIC
# ==========================================
def run_oracle_test(num_episodes=5):
    env = BESCOM_EV_Env()
    successes = 0
    
    for i in range(num_episodes):
        print(f"\n--- Episode {i+1} ---")
        obs, _ = env.reset()
        done = False
        step_count = 0
        
        while not done and step_count < 5:
            # Format prompt
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
            inputs = tokenizer([prompt], return_tensors = "pt").to("cuda")
            outputs = model.generate(**inputs, max_new_tokens = 256, use_cache = True)
            response = tokenizer.batch_decode(outputs)[0]
            
            # Extract Action
            match = re.search(r"<action>(.*?)</action>", response, re.DOTALL)
            action_str = match.group(1).strip().lower() if match else "unknown"
            
            # Map string to Gymnasium action ID
            action_map = {
                "inspect": 0, "prioritize": 1, "summarize": 2, "schedule": 3, "report": 4
            }
            action_id = action_map.get(action_str, 0) # Default to inspect if unknown
            
            print(f"Observation: {obs}")
            print(f"Oracle Action: {action_str.upper()}")
            
            obs, reward, terminated, truncated, _ = env.step(action_id)
            done = terminated or truncated
            step_count += 1
            
            if terminated and reward > 0:
                print("✅ GRID STABLE - REPORT SUBMITTED")
                successes += 1
            elif terminated and reward < 0:
                print("❌ GRID OVERLOADED - FAILURE")

    print(f"\nFinal Success Rate: {successes/num_episodes * 100}%")

if __name__ == "__main__":
    if torch.cuda.is_available():
        run_oracle_test()
    else:
        print("CUDA not available. Please run inference on a GPU instance.")
