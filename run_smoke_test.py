import os
import sys
import numpy as np
from env_bescom import BESCOM_EV_Env
from rewards import format_reward_func, constraint_reward_func, objective_reward_func

def run_bulletproof_smoke_test():
    print("--- Starting Bulletproof Smoke Test ---")
    
    # 1. Instantiate Environment
    try:
        env = BESCOM_EV_Env()
        print("[PASS] Environment instantiation successful.")
    except Exception as e:
        print(f"[FAIL] Environment instantiation failed: {e}")
        return

    # 2. Run 10-Step Loop
    print("Running 10-step dummy simulation...")
    obs, _ = env.reset()
    
    # Mock completions and prompts for reward testing
    mock_completions = [
        "<thought>Thinking about the high load at Silk Board.</thought><action>inspect</action>",
        "<thought>Load is safe. Scheduling charging for Whitefield node.</thought><action>schedule</action>"
    ]
    mock_prompts = [
        "Grid Status: [Silk Board: 0.95, ...] | Queue=10 | Peak=True",
        "Grid Status: [Silk Board: 0.50, ...] | Queue=5 | Peak=False"
    ]

    for i in range(10):
        # Pick a random valid action
        action = env.action_space.sample()
        
        # Step the environment
        try:
            obs, reward, terminated, truncated, _ = env.step(action)
            # Verify UI update (visually verified by user if running locally, otherwise check for crashes)
            if i == 0:
                print("[PASS] First step successful.")
        except Exception as e:
            print(f"[FAIL] Step {i} failed: {e}")
            return
            
        if terminated:
            env.reset()

    print("[PASS] 10-step simulation completed without crashes.")

    # 3. Verify Reward Functions
    print("Testing reward functions...")
    try:
        r1 = format_reward_func(mock_completions)
        r2 = constraint_reward_func(mock_completions, mock_prompts)
        r3 = objective_reward_func(mock_completions)
        
        if all(isinstance(r, list) for r in [r1, r2, r3]):
            print(f"[PASS] Reward functions returned lists: {len(r1)}, {len(r2)}, {len(r3)}")
        else:
            print("[FAIL] Reward functions did not return lists.")
            return
    except Exception as e:
        print(f"[FAIL] Reward functions crashed: {e}")
        return

    print("\n[SUCCESS] Pipeline is bulletproof. Ready for overnight training.")

if __name__ == "__main__":
    run_bulletproof_smoke_test()
