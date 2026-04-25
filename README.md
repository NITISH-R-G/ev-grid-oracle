# ⚡ BESCOM EV Grid Oracle 🔮

### Meta x Hugging Face OpenEnv Hackathon Submission
**A Zero-Latency AI Dispatcher for Bengaluru's Smart Grid**

---

## 📍 Section 1: AI for Bharat Impact (BESCOM Theme 9)

Bengaluru is the EV capital of India, but its power infrastructure—managed by **BESCOM**—faces a looming crisis. Traditional grid expansion is slow and capital-intensive. The **BESCOM EV Grid Oracle** offers a software-defined solution: an LLM-based dispatcher that manages EV load dynamically using real-time reasoning.

By acting as a **Zero-Latency Dispatcher**, this AI prioritizes charging at stations with high renewable availability and transformer headroom (e.g., Whitefield during solar peaks) while deferring load in high-stress areas like Silk Board. This shifts the focus from building physical grid capacity to **optimizing existing infrastructure with hybrid intelligence.**

---

## 🧠 Section 2: OpenEnv RL Architecture

### The "Cheat Architecture"
We abstracted the physical complexity of the Bangalore grid into a **Discrete Topological Graph** with 10 critical nodes. This allows our LLM to reason about the grid as a spatial network rather than just numbers.

### GRPO: Reinforcement Learning from Reasoning
We used **Group Relative Policy Optimization (GRPO)** to train the model's internal "Chain of Thought" (`<thought>` tags). This ensures the Oracle doesn't just guess; it analyzes the grid state before taking an action.

### The 3 Verifiable Reward Functions:
To prevent "reward hacking" (where the model finds shortcuts that don't solve the problem), we implemented three independent verifiers:
1.  **Format Reward**: Validates strict XML output for seamless integration with the control systems.
2.  **Constraint Reward**: Heavily penalizes any action that ignores high-load warnings (Load > 90%).
3.  **Objective Reward**: Incentivizes deep, long-horizon reasoning about grid stability and demand fulfillment.

---

## 🛠️ Section 3: How to Run

### Installation
```bash
!bash setup_colab.sh
```

### The "Before" Demo (Baseline Chaos)
Run this to see the grid fail under random, uncoordinated EV charging:
```bash
python record_baseline.py
```

### The "After" Demo (Oracle in Control)
Run this to launch the trained AI Oracle and watch it maintain grid stability across all nodes:
```bash
python run_trained_oracle.py
```

---
*Built for the Meta x Hugging Face Hackathon - April 2026*
