import time
import random
from env_bescom import BESCOM_EV_Env

def record_baseline_chaos():
    """
    Runs a 50-step simulation with a random agent to demonstrate grid failure.
    """
    print("Starting Baseline Chaos Recording...")
    env = BESCOM_EV_Env()
    obs, _ = env.reset()
    
    total_reward = 0
    failures = 0
    
    for step in range(50):
        # Pick a random action (0-4)
        # Action 3 (schedule) increases load, random agent will likely trigger overload
        action = env.action_space.sample()
        
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        # Check if the grid is failing
        if "0.9" in obs or "1.00" in obs:
            print(f"Step {step}: GRID STRESS DETECTED!")
        
        if terminated and reward < 0:
            print(f"Step {step}: TOTAL GRID COLLAPSE! (Outage occurred)")
            failures += 1
            env.reset() # Keep recording even if it fails
            
        time.sleep(0.5) # Slow down for smooth screen recording
        
    print(f"\n✅ Recording Complete.")
    print(f"Total Steps: 50 | Outages: {failures} | Avg Reward: {total_reward/50:.2f}")

if __name__ == "__main__":
    record_baseline_chaos()
