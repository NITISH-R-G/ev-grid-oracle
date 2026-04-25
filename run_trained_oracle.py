import torch
from unsloth import FastLanguageModel
from env_bescom import BESCOM_EV_Env
import re
import time

# ==========================================
# 1. LOAD TRAINED ORACLE
# ==========================================
model_path = "trained_ev_oracle"
max_seq_length = 512

print(f"Initializing Trained BESCOM EV Grid Oracle from {model_path}...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_path,
    max_seq_length = max_seq_length,
    load_in_4bit = False, # Load the merged 16-bit weights
)
FastLanguageModel.for_inference(model)

# ==========================================
# 2. INFERENCE LOOP
# ==========================================
def run_trained_oracle_demo(num_steps=50):
    env = BESCOM_EV_Env()
    obs, _ = env.reset()
    
    print("\nOracle Active. Monitoring Grid State...")
    
    for step in range(num_steps):
        # Format the current observation for the LLM
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
        # Generate Action via LLM
        inputs = tokenizer([prompt], return_tensors = "pt").to("cuda")
        outputs = model.generate(**inputs, max_new_tokens = 128, use_cache = True)
        response = tokenizer.batch_decode(outputs)[0][len(prompt):]
        
        # Extract Action from XML tags
        match = re.search(r"<action>(.*?)</action>", response, re.DOTALL)
        action_str = match.group(1).strip().lower() if match else "inspect"
        
        # Map string to Gymnasium action ID
        action_map = {
            "inspect": 0, "prioritize": 1, "summarize": 2, "schedule": 3, "report": 4
        }
        action_id = action_map.get(action_str, 0)
        
        # Step the Environment
        obs, reward, terminated, truncated, _ = env.step(action_id)
        
        print(f"Step {step+1}: Oracle chose {action_str.upper()} | Reward: {reward:.2f}")
        
        if terminated and reward > 0:
            print("✅ Shift successful. Grid remains within safety thresholds.")
            env.reset()
        elif terminated and reward < 0:
            print("❌ Critical System Failure. (Unexpected)")
            env.reset()
            
        time.sleep(0.5) # For smooth visualization update

if __name__ == "__main__":
    if torch.cuda.is_available():
        run_trained_oracle_demo()
    else:
        print("Error: CUDA not found. Inference must run on a GPU instance.")
