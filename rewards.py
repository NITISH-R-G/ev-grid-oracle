import re

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
