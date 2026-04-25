# BESCOM EV Grid Oracle: RLHF Training Pipeline

## 🏆 Meta x Hugging Face Hackathon Submission

### Overview
The **BESCOM EV Grid Oracle** is a dual-reasoning LLM system designed to manage smart grid loads in response to the surging demand of Electric Vehicles (EVs). Using **Group Relative Policy Optimization (GRPO)**, we have trained a `Gemma-1.1-2b-it` model to act as a real-time decision-maker for transformer load balancing.

### 🛠️ Technical Stack
*   **Base Model**: `unsloth/gemma-1.1-2b-it-bnb-4bit`
*   **Training Method**: GRPO (Group Relative Policy Optimization)
*   **Frameworks**: Unsloth, TRL (Hugging Face), Gymnasium
*   **Hardware**: Optimized for NVIDIA T4 (16GB VRAM)

### 🧠 The Reasoning Engine (GRPO)
Unlike standard SFT (Supervised Fine-Tuning), this project uses **GRPO** to refine the model's internal "Chain of Thought" (`<thought>` tags). 
The model is rewarded for:
1.  **Format Adherence**: Strictly following XML-based output.
2.  **Safety Compliance**: Never suggesting a charging schedule when the grid is above 90% load.
3.  **Logical Depth**: Longer, more analytical thought processes before taking an action.

### 📁 Repository Structure
*   `train_grpo.py`: Core RLHF training script.
*   `env_bescom.py`: Custom Gymnasium environment simulating grid load dynamics.
*   `test_oracle.py`: Inference script to validate the trained oracle.
*   `train_ev_oracle.ipynb`: Jupyter Notebook for quick Colab deployment.
*   `setup_colab.sh`: One-click environment setup script.

### 🚀 Getting Started
1. Open `train_ev_oracle.ipynb` in Google Colab.
2. Ensure you have an NVIDIA T4 GPU runtime selected.
3. Run the setup and training cells.
4. The final merged 16-bit model will be saved to `/trained_ev_oracle`.

---
*Built for the Meta x Hugging Face Hackathon - April 2026*
