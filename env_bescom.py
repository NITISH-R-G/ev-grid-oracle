import gymnasium as gym
from gymnasium import spaces
import numpy as np

class BESCOM_EV_Env(gym.Env):
    """
    Custom Environment for the BESCOM EV Grid Oracle.
    Adapted from the OpenEnv specification.
    """
    def __init__(self):
        super(BESCOM_EV_Env, self).__init__()
        
        # Define Action Space: Based on OpenEnv yaml
        # 0: inspect_grid_load
        # 1: prioritize_ev_queue
        # 2: summarize_demand
        # 3: set_charging_schedule
        # 4: submit_grid_report
        self.action_space = spaces.Discrete(5)
        
        # Define Observation Space: Text-based (using strings for simplicity in this hackathon setup)
        # In a real setup, this might be a Dict or a Box
        self.observation_space = spaces.Text(max_length=1000)
        
        self.state = {
            "transformer_load": 0.75,
            "ev_queue_length": 10,
            "peak_hours": False,
            "tokens_used": 0,
            "budget": 5000
        }
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = {
            "transformer_load": np.random.uniform(0.5, 0.9),
            "ev_queue_length": np.random.randint(5, 20),
            "peak_hours": np.random.choice([True, False]),
            "tokens_used": 0,
            "budget": 5000
        }
        return self._get_obs(), {}

    def _get_obs(self):
        return f"Grid Status: Load={self.state['transformer_load']:.2f}, Queue={self.state['ev_queue_length']}, Peak={self.state['peak_hours']}"

    def step(self, action):
        # Basic state transition logic
        reward = 0.0
        terminated = False
        truncated = False
        
        if action == 3: # set_charging_schedule
            reward = 0.5
            self.state["transformer_load"] += 0.1
        elif action == 4: # submit_grid_report
            reward = 1.0
            terminated = True
            
        # Constraint check
        if self.state["transformer_load"] > 0.95:
            reward -= 2.0 # Penalty for grid overload
            terminated = True
            
        return self._get_obs(), reward, terminated, truncated, {}
