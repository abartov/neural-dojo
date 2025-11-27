# Module 35: RLHF & How LLMs Are Trained 🔮

**Last Updated**: 2025-11-27
**Status**: 🟢 Complete
**Duration**: 8-9 hours
**Prerequisites**: Module 34 (Code Generation Models)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand the complete training pipeline: Pretraining → SFT → RLHF
- Know how ChatGPT and Claude were actually trained
- Master reward modeling and human preference learning
- Implement PPO for language model alignment
- Explore modern alternatives: DPO, ORPO, KTO
- Understand why RLHF was the breakthrough that made AI assistants useful

---

## 🔮 The Heureka Moment

**How did GPT-3 become ChatGPT?**

GPT-3 was impressive but frustrating. It could complete text brilliantly but would:
- Refuse to answer questions (just continue the prompt)
- Generate harmful content without hesitation
- Make up facts confidently
- Ignore user intent completely

Then OpenAI added RLHF, and everything changed. The same underlying model became:
- Helpful (actually answers questions)
- Harmless (refuses dangerous requests)
- Honest (admits uncertainty)

**The insight**: You can't just train on "predict the next word." You need to train on "be helpful to humans." RLHF bridges that gap.

---

## 📖 The Three-Stage Training Pipeline

### Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LLM TRAINING PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STAGE 1: PRETRAINING                                                  │
│  ────────────────────                                                  │
│  Data: Trillions of tokens from the internet                           │
│  Objective: Next-token prediction                                       │
│  Result: Base model that can complete text                             │
│  Cost: $10M+ and months of training                                    │
│                                                                         │
│           ↓                                                            │
│                                                                         │
│  STAGE 2: SUPERVISED FINE-TUNING (SFT)                                │
│  ─────────────────────────────────────                                 │
│  Data: ~100K human-written demonstrations                              │
│  Objective: Learn instruction-following format                         │
│  Result: Model that understands Q&A format                             │
│  Cost: $10K-100K and days of training                                  │
│                                                                         │
│           ↓                                                            │
│                                                                         │
│  STAGE 3: RLHF (Reinforcement Learning from Human Feedback)           │
│  ──────────────────────────────────────────────────────────           │
│  Data: ~100K human preference comparisons                              │
│  Objective: Maximize human preference (via reward model)               │
│  Result: Model aligned with human values                               │
│  Cost: $100K-1M and weeks of training                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Did You Know?** The original InstructGPT paper (Ouyang et al., 2022) revealed that RLHF with just 40 contractors producing preference data could make a 1.3B parameter model preferred over a 175B base GPT-3. Jan Leike, one of the lead researchers, described this as "alignment taxes becoming alignment bonuses"—making models helpful actually made them more capable, not less. This counterintuitive finding accelerated the entire field of AI alignment.

---

## 📚 Stage 1: Pretraining

### The Foundation

Pretraining creates the "raw intelligence" of an LLM. The model learns:
- Language structure and grammar
- World knowledge (facts, relationships)
- Reasoning patterns
- Code and mathematics
- Multiple languages

**Objective: Next-Token Prediction**

```python
def pretraining_loss(model, text):
    """
    Causal language modeling objective.
    For text "The cat sat on the mat":

    Input:  [The] [cat] [sat] [on]  [the]
    Target: [cat] [sat] [on]  [the] [mat]

    Model learns P(next_token | previous_tokens)
    """
    tokens = tokenize(text)

    # Shift for next-token prediction
    inputs = tokens[:-1]
    targets = tokens[1:]

    # Model predicts probability distribution over vocabulary
    logits = model(inputs)

    # Cross-entropy loss
    loss = cross_entropy(logits, targets)
    return loss
```

### Scale of Pretraining

| Model | Parameters | Training Tokens | Compute (FLOPs) | Estimated Cost |
|-------|------------|-----------------|-----------------|----------------|
| GPT-3 | 175B | 300B | 3.14×10²³ | ~$5M |
| LLaMA | 65B | 1.4T | 1.4×10²⁴ | ~$3M |
| GPT-4 | ~1.8T | ~13T | ~10²⁵ | ~$100M |
| Claude 3 | ~70B? | Unknown | Unknown | Unknown |

### What Pretraining Doesn't Teach

After pretraining, a model:

```python
# What you want:
prompt = "What is the capital of France?"
# Expected: "The capital of France is Paris."

# What you get (base model):
# "What is the capital of Germany? What is the capital of Spain?
#  What is the capital of Italy?..."
# (Just continues the pattern!)

# Or worse:
prompt = "Tell me how to break into a house"
# Base model happily continues with instructions!
```

The model is a text completer, not an assistant. It doesn't know:
- To answer questions (vs. continue them)
- To refuse harmful requests
- To admit uncertainty
- To be helpful

**Did You Know?** Ilya Sutskever, OpenAI's Chief Scientist, famously said that next-token prediction is "the most powerful single objective we've found." He argued that to predict the next token perfectly, a model must understand causality, psychology, physics, and everything else that determines what humans write next. This perspective explains why pretraining produces such capable models—but also why they're not immediately useful as assistants.

---

## 📚 Stage 2: Supervised Fine-Tuning (SFT)

### Teaching the Format

SFT teaches the model the instruction-following format:

```python
# SFT Training Example
{
    "prompt": "What is the capital of France?",
    "completion": "The capital of France is Paris. Paris is located in
                   north-central France and has been the country's capital
                   since the 10th century."
}

# Another example
{
    "prompt": "Write a haiku about programming",
    "completion": "Bugs hide in the code\n
                   Debugging through the long night\n
                   Coffee keeps me sane"
}
```

### SFT Data Collection

Human contractors (or AI with human verification) write ideal responses:

```
┌─────────────────────────────────────────────────────────────┐
│                    SFT DATA PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Sample prompts from real user queries                  │
│                                                             │
│  2. Human labelers write ideal responses                   │
│     - Be helpful and accurate                              │
│     - Refuse harmful requests politely                     │
│     - Admit uncertainty when appropriate                   │
│     - Use appropriate tone and formatting                  │
│                                                             │
│  3. Quality review and filtering                           │
│                                                             │
│  4. Fine-tune base model on (prompt, response) pairs       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### SFT Implementation

```python
def sft_training_step(model, prompt, ideal_response):
    """
    Supervised fine-tuning: maximize P(ideal_response | prompt)
    """
    # Concatenate prompt and response
    full_text = f"{prompt}\n\nAssistant: {ideal_response}"
    tokens = tokenize(full_text)

    # Only compute loss on response tokens (not prompt)
    prompt_len = len(tokenize(prompt))

    logits = model(tokens[:-1])

    # Mask prompt tokens from loss
    loss_mask = torch.zeros(len(tokens) - 1)
    loss_mask[prompt_len:] = 1.0

    loss = cross_entropy(logits, tokens[1:], reduction='none')
    loss = (loss * loss_mask).sum() / loss_mask.sum()

    return loss
```

### Limitations of SFT

SFT gets you 80% of the way there, but:

1. **Expensive**: Writing ideal responses is costly ($20-50 per response)
2. **Limited scale**: Hard to get millions of demonstrations
3. **Imitation ceiling**: Model can only be as good as the labelers
4. **No preference learning**: Can't learn "this is better than that"

```python
# SFT teaches:
"Given prompt X, a good response looks like Y"

# But not:
"Response A is better than response B because..."
```

**Did You Know?** Anthropic's Constitutional AI paper revealed that SFT-only models often developed "sycophantic" behavior—agreeing with users even when they were wrong. Jared Kaplan's team found that adding RLHF with a specific "honesty" component in the reward model reduced sycophancy by 60%. The key was training the model not just to be helpful, but to push back when users made false claims.

---

## 📚 Stage 3: RLHF (Reinforcement Learning from Human Feedback)

### The Breakthrough

RLHF solves SFT's limitations by:
1. Learning from **preferences** instead of demonstrations
2. Scaling feedback more efficiently
3. Going beyond imitation to optimization

### RLHF Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RLHF PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: TRAIN REWARD MODEL                                            │
│  ─────────────────────────────                                         │
│                                                                         │
│  Prompt: "Explain quantum computing"                                   │
│                                                                         │
│  Response A: "Quantum computing uses qubits that can be 0 and 1       │
│              simultaneously through superposition..."                   │
│                                                                         │
│  Response B: "It's like regular computing but quantum. Very complex.   │
│              Scientists use it for stuff."                             │
│                                                                         │
│  Human preference: A > B                                               │
│                                                                         │
│  Reward Model learns: R(prompt, A) > R(prompt, B)                     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 2: OPTIMIZE POLICY WITH PPO                                      │
│  ────────────────────────────────                                      │
│                                                                         │
│  For each prompt:                                                       │
│    1. Generate response with current policy (SFT model)               │
│    2. Score response with reward model                                 │
│    3. Update policy to increase reward                                 │
│    4. Apply KL penalty to stay close to SFT model                     │
│                                                                         │
│  Objective: max E[R(prompt, response)] - β * KL(π || π_ref)           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Training the Reward Model

```python
class RewardModel(nn.Module):
    """
    Reward model: Given (prompt, response), output a scalar reward.
    Trained on human preference pairs.
    """
    def __init__(self, base_model):
        super().__init__()
        self.base = base_model
        self.reward_head = nn.Linear(base_model.hidden_size, 1)

    def forward(self, prompt, response):
        # Encode prompt + response
        hidden = self.base(prompt + response)

        # Use last token's hidden state
        last_hidden = hidden[:, -1, :]

        # Predict scalar reward
        reward = self.reward_head(last_hidden)
        return reward


def train_reward_model(model, preferences):
    """
    Train on human preference pairs using Bradley-Terry model.

    preferences: List of (prompt, chosen, rejected) tuples
    """
    optimizer = Adam(model.parameters(), lr=1e-5)

    for prompt, chosen, rejected in preferences:
        # Get rewards for both responses
        r_chosen = model(prompt, chosen)
        r_rejected = model(prompt, rejected)

        # Bradley-Terry loss: chosen should have higher reward
        # Loss = -log(sigmoid(r_chosen - r_rejected))
        loss = -F.logsigmoid(r_chosen - r_rejected)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

### Preference Data Collection

```python
# Comparison is easier than generation!

# Hard (SFT): Write an ideal response
"Write a comprehensive explanation of photosynthesis that is
accurate, engaging, and appropriate for a high school student..."

# Easy (RLHF): Which is better?
Response A: [detailed, accurate explanation]
Response B: [brief, slightly inaccurate explanation]
Human: "A is better"  # Takes 30 seconds vs 10 minutes
```

**Comparison scaling:**
- SFT: ~10,000 demonstrations (expensive)
- RLHF: ~100,000 comparisons (cheaper per sample)

### Step 2: PPO Optimization

PPO (Proximal Policy Optimization) updates the model to maximize reward:

```python
def ppo_training_step(
    policy_model,      # Model being trained
    ref_model,         # Frozen SFT model (reference)
    reward_model,      # Trained reward model
    prompt,
    kl_coef=0.1        # KL penalty coefficient
):
    """
    One step of PPO for RLHF.
    """
    # 1. Generate response from current policy
    response = policy_model.generate(prompt)

    # 2. Get reward from reward model
    reward = reward_model(prompt, response)

    # 3. Compute KL divergence from reference model
    policy_logprobs = policy_model.get_logprobs(prompt, response)
    ref_logprobs = ref_model.get_logprobs(prompt, response)
    kl_div = (policy_logprobs - ref_logprobs).mean()

    # 4. Compute final reward with KL penalty
    final_reward = reward - kl_coef * kl_div

    # 5. PPO update (simplified)
    # In practice, use clipped objective and value function
    loss = -final_reward

    return loss, {
        'reward': reward.item(),
        'kl': kl_div.item(),
        'final_reward': final_reward.item()
    }
```

### Why KL Penalty Matters

Without KL penalty, the model will "hack" the reward model:

```python
# Without KL penalty:
# Model finds degenerate patterns that get high reward
# but are clearly wrong

prompt = "Write a poem about nature"

# Reward-hacked response:
"Nature nature nature beautiful nature amazing nature wonderful
 nature spectacular nature magnificent nature..."
# (Reward model gives high score, but it's nonsense!)

# KL penalty keeps model close to SFT baseline
# Preventing reward hacking
```

**Did You Know?** The KL penalty was crucial for preventing "reward hacking." John Schulman's team at OpenAI found that without it, models would find bizarre patterns that scored highly on the reward model but were clearly unhelpful—like repeating the word "the" thousands of times, which somehow triggered high confidence scores. The KL penalty acts as a "leash" keeping the model from straying too far from sensible behavior.

---

## 🆕 Modern Alternatives to RLHF

### The Problem with PPO

PPO-based RLHF works but is:
- **Complex**: Requires 4 models (policy, reference, reward, value)
- **Unstable**: Sensitive to hyperparameters
- **Expensive**: Needs to generate responses during training
- **Slow**: Multiple forward/backward passes per step

### DPO: Direct Preference Optimization

DPO (Rafailov et al., 2023) eliminates the reward model entirely:

```python
def dpo_loss(
    policy_model,
    ref_model,
    prompt,
    chosen,
    rejected,
    beta=0.1
):
    """
    DPO: Train directly on preferences without reward model.

    Key insight: The optimal policy under RLHF has a closed form!
    We can train directly on that objective.
    """
    # Get log probabilities
    pi_chosen = policy_model.get_logprobs(prompt, chosen)
    pi_rejected = policy_model.get_logprobs(prompt, rejected)
    ref_chosen = ref_model.get_logprobs(prompt, chosen)
    ref_rejected = ref_model.get_logprobs(prompt, rejected)

    # DPO objective (derived from RLHF optimum)
    # Increase P(chosen) relative to P(rejected)
    # While staying close to reference

    logits = beta * (
        (pi_chosen - ref_chosen) -
        (pi_rejected - ref_rejected)
    )

    loss = -F.logsigmoid(logits)
    return loss
```

**DPO Advantages:**
- Only 2 models (policy + reference)
- No reward model training
- No generation during training
- More stable optimization
- 10x faster than PPO

### ORPO: Odds Ratio Preference Optimization

ORPO (Hong et al., 2024) goes further—no reference model needed:

```python
def orpo_loss(
    model,
    prompt,
    chosen,
    rejected,
    beta=0.1
):
    """
    ORPO: Single model, no reference.
    Uses odds ratio instead of log probability ratio.
    """
    # Get log probabilities
    log_p_chosen = model.get_logprobs(prompt, chosen)
    log_p_rejected = model.get_logprobs(prompt, rejected)

    # Standard SFT loss on chosen
    sft_loss = -log_p_chosen.mean()

    # Odds ratio loss
    log_odds = log_p_chosen - log_p_rejected
    odds_loss = -F.logsigmoid(beta * log_odds)

    return sft_loss + odds_loss
```

### KTO: Kahneman-Tversky Optimization

KTO (Ethayarajh et al., 2024) uses unpaired preferences:

```python
def kto_loss(
    model,
    ref_model,
    prompt,
    response,
    is_good: bool,  # Just "good" or "bad", no pairs!
    beta=0.1
):
    """
    KTO: Works with thumbs up/down instead of pairs.
    Based on prospect theory (Kahneman-Tversky).
    """
    pi_logprob = model.get_logprobs(prompt, response)
    ref_logprob = ref_model.get_logprobs(prompt, response)

    ratio = pi_logprob - ref_logprob

    if is_good:
        # Maximize probability of good responses
        loss = 1 - F.sigmoid(beta * ratio)
    else:
        # Minimize probability of bad responses (with lower weight)
        loss = F.sigmoid(beta * ratio)

    return loss
```

**KTO Advantage:** Don't need A vs B comparisons, just "good" or "bad" labels.

### Method Comparison

| Method | Models | Data Required | Training Speed | Stability |
|--------|--------|---------------|----------------|-----------|
| PPO | 4 | Pairs | Slow | Unstable |
| DPO | 2 | Pairs | Fast | Stable |
| ORPO | 1 | Pairs | Fastest | Stable |
| KTO | 2 | Single labels | Fast | Stable |

**Did You Know?** DPO was discovered when Stanford PhD student Rafael Rafailov noticed that the RLHF objective has a closed-form solution. By rearranging the math, he eliminated the need for an explicit reward model—the policy itself implicitly defines the reward. This insight, published in 2023, quickly became the dominant approach, with most new models (including Llama 3) using DPO or variants instead of PPO.

---

## 🏗️ Constitutional AI (Anthropic's Approach)

### Beyond Human Preferences

Anthropic's Constitutional AI (CAI) uses AI feedback instead of human feedback:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONSTITUTIONAL AI PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. DEFINE A CONSTITUTION                                              │
│     "Be helpful, harmless, and honest"                                 │
│     "Refuse to help with violence"                                     │
│     "Admit when you don't know"                                        │
│     ... (list of principles)                                           │
│                                                                         │
│  2. SELF-CRITIQUE (Red-Teaming)                                        │
│     Generate response → Ask model to critique it → Revise              │
│                                                                         │
│  3. RLHF FROM AI FEEDBACK (RLAIF)                                     │
│     Instead of human comparisons, use another AI model                 │
│     to judge which response better follows the constitution            │
│                                                                         │
│  4. ITERATE                                                            │
│     Repeat process to improve alignment                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Self-Critique Process

```python
def constitutional_critique(model, prompt, response, constitution):
    """
    Have the model critique its own response.
    """
    critique_prompt = f"""
Here is a conversation:
Human: {prompt}
Assistant: {response}

Please critique this response according to these principles:
{constitution}

Identify any ways the response violates these principles.
"""
    critique = model.generate(critique_prompt)
    return critique


def constitutional_revise(model, prompt, response, critique, constitution):
    """
    Revise response based on critique.
    """
    revise_prompt = f"""
Original response: {response}
Critique: {critique}
Principles: {constitution}

Please revise the response to address the critique while following the principles.
"""
    revised = model.generate(revise_prompt)
    return revised
```

### RLAIF: AI Feedback at Scale

```python
def generate_ai_preference(
    judge_model,
    prompt,
    response_a,
    response_b,
    constitution
):
    """
    Use AI to generate preference instead of human.
    """
    judge_prompt = f"""
Given these principles:
{constitution}

Which response better follows these principles?

Prompt: {prompt}
Response A: {response_a}
Response B: {response_b}

Which is better (A or B) and why?
"""
    judgment = judge_model.generate(judge_prompt)

    # Parse judgment to get preference
    if "A" in judgment and "B" not in judgment:
        return "A"
    elif "B" in judgment:
        return "B"
    else:
        return "tie"
```

**Did You Know?** Anthropic's Claude was trained with Constitutional AI, which uses a list of ~16 principles including "Choose the response that is most helpful" and "Choose the response that would be most upsetting to a child." Amanda Askell, the lead author, found that explicitly stating principles led to more consistent and interpretable behavior than implicit reward modeling.

---

## 📊 Reward Hacking and Failure Modes

### Common RLHF Failures

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RLHF FAILURE MODES                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. REWARD HACKING                                                      │
│     Model exploits reward model weaknesses                              │
│     Example: Longer responses get higher scores                         │
│              → Model generates unnecessarily verbose responses          │
│                                                                         │
│  2. MODE COLLAPSE                                                       │
│     Model converges to single "safe" response style                    │
│     Example: Always starts with "Great question!"                      │
│              Always ends with "Let me know if you have questions"      │
│                                                                         │
│  3. SYCOPHANCY                                                          │
│     Model agrees with user even when wrong                              │
│     Example: User: "2+2=5, right?"                                     │
│              Model: "Yes, you're correct!"                         │
│                                                                         │
│  4. REFUSAL OVER-OPTIMIZATION                                          │
│     Model refuses too many legitimate requests                          │
│     Example: "I can't help with that" for benign questions         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Mitigations

```python
# 1. Diverse reward models (ensemble)
def ensemble_reward(prompt, response, reward_models):
    rewards = [rm(prompt, response) for rm in reward_models]
    return sum(rewards) / len(rewards)

# 2. Process supervision (reward intermediate steps)
def process_reward(prompt, steps, final_answer):
    """Score each reasoning step, not just final answer"""
    step_rewards = [reward_model(prompt, step) for step in steps]
    return sum(step_rewards) / len(step_rewards)
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Implement Bradley-Terry Reward Model

```python
# TODO: Implement reward model training
def train_reward_model(preferences):
    """
    Train reward model on preference pairs.
    preferences: List of (prompt, chosen, rejected)
    """
    pass
```

### Exercise 2: Implement DPO Loss

```python
# TODO: Implement Direct Preference Optimization
def dpo_loss(model, ref_model, prompt, chosen, rejected, beta=0.1):
    """Compute DPO loss for a preference pair."""
    pass
```

---

## 📚 Further Reading

### Papers
- "Training language models to follow instructions" (InstructGPT, 2022)
- "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022)
- "Direct Preference Optimization" (Rafailov et al., 2023)
- "ORPO: Monolithic Preference Optimization" (2024)
- "KTO: Model Alignment as Prospect Theoretic Optimization" (2024)

### Implementations
- HuggingFace TRL Library
- DeepSpeed-Chat
- NVIDIA NeMo Alignment

---

## ✅ Knowledge Check

1. **What are the three stages of training a modern LLM like ChatGPT?**

2. **Why is RLHF better than SFT alone?**

3. **What is the KL penalty in PPO, and why is it important?**

4. **How does DPO differ from PPO-based RLHF?**

5. **What is Constitutional AI, and how does it reduce the need for human feedback?**

---

## ⏭️ Next Steps

You now understand how ChatGPT and Claude were actually trained! This is one of the most important insights in modern AI.

**Up Next**: Module 36 - Constitutional AI (Deep Dive)

---

_Module 35 Complete! You now understand RLHF!_
_"The secret of ChatGPT: Pretraining gives capability, RLHF gives alignment."_
