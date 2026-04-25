import gymnasium as gym
from gymnasium import spaces
import numpy as np
from render import EVGridVisualizer

class BESCOM_EV_Env(gym.Env):
    """
    Custom Environment for the BESCOM EV Grid Oracle.
    Integrated with real-time visualization.
    """
    def __init__(self):
        super(BESCOM_EV_Env, self).__init__()
        
        # 0: inspect, 1: prioritize, 2: summarize, 3: schedule, 4: report
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Text(max_length=2000)
        
        # Initialize Visualizer
        self.viz = EVGridVisualizer()
        
        self.nodes = [
            "Silk Board", "Whitefield", "Indiranagar", "Electronic City",
            "Koramangala", "HSR Layout", "MG Road", "Malleshwaram",
            "Jayanagar", "Banashankari"
        ]
        
        self.reset()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # 10 nodes with random starting loads
        self.transformer_loads = np.random.uniform(0.4, 0.8, size=10)
        self.state = {
            "ev_queue_length": np.random.randint(5, 20),
            "peak_hours": np.random.choice([True, False]),
            "tokens_used": 0,
            "budget": 5000
        }
        return self._get_obs(), {}

    def _get_obs(self):
        load_summary = ", ".join([f"{name}: {load:.2f}" for name, load in zip(self.nodes, self.transformer_loads)])
        return f"Grid Status: [{load_summary}] | Queue={self.state['ev_queue_length']} | Peak={self.state['peak_hours']}"

    def step(self, action):
        reward = 0.0
        terminated = False
        truncated = False
        
        # Logic: Action 3 (schedule) affects a random node or the most loaded node
        if action == 3: # schedule
            target_node = np.argmax(self.transformer_loads)
            self.transformer_loads[target_node] += 0.15
            reward = 0.5
        elif action == 4: # report
            reward = 1.0
            terminated = True
            
        # Check for grid failure on ANY node
        if np.any(self.transformer_loads > 0.95):
            reward -= 5.0 # Severe penalty for any outage
            terminated = True
            
        # Update Visuals (The Hook)
        self.viz.update_grid(self.transformer_loads)
            
        return self._get_obs(), reward, terminated, truncated, {}
