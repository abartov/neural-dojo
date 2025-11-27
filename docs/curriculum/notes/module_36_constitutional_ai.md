# Module 36: Constitutional AI and Alignment

**Last Updated**: 2025-11-27
**Status**: 🟢 Complete
**Duration**: 6-7 hours
**Prerequisites**: Module 35 (RLHF)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand Constitutional AI (Anthropic's approach to alignment)
- Know how Claude was trained differently from ChatGPT
- Implement self-critique and revision mechanisms
- Design AI constitutions with explicit principles
- Use RLAIF (RL from AI Feedback) instead of human feedback
- Evaluate AI systems for harmlessness and helpfulness

---

## 📖 What is Constitutional AI?

### The Problem with Pure RLHF

RLHF (Module 35) works, but has fundamental limitations:

**1. Human Feedback is Expensive**
- Need thousands of human comparisons
- $50K-500K just for preference data
- Slow to collect and iterate

**2. Humans are Inconsistent**
- Different labelers have different values
- Labelers can be manipulated by eloquent responses
- Hard to specify exactly what "good" means

**3. Implicit Values**
- What values are we actually teaching?
- Hard to audit or understand
- "Reward model knows best" is a black box

**4. Sycophancy**
- Model learns to tell humans what they want to hear
- Agrees even when humans are wrong
- Optimizes for approval, not truth

Think of it like teaching a child by only showing thumbs up or thumbs down, without ever explaining *why* something is good or bad. The child might learn to predict what gets approval, but they won't internalize the underlying values.

### Anthropic's Solution: Constitutional AI

Constitutional AI (CAI) addresses these issues by:
1. **Explicit principles** instead of implicit preferences
2. **AI feedback** instead of (only) human feedback
3. **Self-critique** to catch problems early
4. **Transparency** about what values are being trained

**Did You Know?** The Constitutional AI paper was published by Anthropic in December 2022, led by Yuntao Bai and Amanda Askell. The "constitution" they used contained just 16 principles, yet this was enough to train Claude to be helpful and harmless.

---

## 📜 The Constitution

### What is an AI Constitution?

An AI constitution is a set of explicit principles that guide model behavior. Unlike implicit reward models where values are hidden in neural network weights, a constitution makes values transparent and auditable.

```python
SAMPLE_CONSTITUTION = [
    # Helpfulness
    "Choose the response that is most helpful to the user.",
    "Choose the response that is most accurate and factual.",
    "Choose the response that best answers the question.",

    # Harmlessness
    "Choose the response that is least harmful or dangerous.",
    "Choose the response least likely to cause harm if followed.",
    "Choose the response that is least racist, sexist, or toxic.",

    # Honesty
    "Choose the response that is most honest and truthful.",
    "Choose the response that acknowledges uncertainty appropriately.",
    "Choose the response that does not claim false capabilities.",

    # Ethics
    "Choose the response considered ethical by most people.",
    "Choose the response that respects human dignity.",
    "Choose the response that promotes wellbeing.",

    # Safety
    "Choose the response least likely to be misused.",
    "Choose the response that refuses illegal requests.",
    "Choose the response a senior employee would approve of."
]
```

### Principle Categories

| Category | Key Principles |
|----------|---------------|
| **Helpfulness** | Be useful, accurate, informative; answer thoroughly |
| **Harmlessness** | Refuse dangerous/illegal requests; avoid toxic content |
| **Honesty** | Be truthful; acknowledge uncertainty; no false claims |
| **Ethics** | Respect dignity; consider consequences; be fair |
| **Transparency** | Be clear about being AI; explain reasoning |

**Did You Know?** Anthropic's actual constitution includes some surprisingly specific principles. One states: "Choose the response that would NOT be most upsetting to a thoughtful, senior Anthropic employee." This "newspaper test" helps the model avoid embarrassing responses.

---

## 🔄 The CAI Training Pipeline

### Overview: Two-Stage Process

**Stage 1: Supervised Learning (SL) - "Critique and Revise"**
1. Generate response to harmful prompt
2. Ask model to CRITIQUE its response using constitution
3. Ask model to REVISE based on critique
4. Train on (prompt, revised_response) pairs

**Stage 2: Reinforcement Learning (RL) - "RLAIF"**
1. Generate multiple responses to prompt
2. Use AI (not human!) to judge which is better based on constitution
3. Train reward model on AI preferences
4. Use RLHF with AI-generated preferences

### Stage 1: Self-Critique and Revision

The key insight is that models can critique their own outputs when given explicit principles.

**The Critique-Revise Loop:**

```python
def critique_and_revise(model, user_prompt, initial_response, constitution):
    """
    Core CAI Stage 1: Self-improvement through critique.

    Args:
        model: The language model
        user_prompt: Original user request
        initial_response: Model's first attempt
        constitution: List of principles

    Returns:
        Revised, improved response
    """
    # Step 1: Generate critique
    critique = model.generate(
        f"Critique this response according to these principles:\n"
        f"Principles: {constitution}\n"
        f"Response to critique: {initial_response}\n"
        f"What problems does this response have?"
    )

    # Step 2: Generate revision
    revised = model.generate(
        f"Original response: {initial_response}\n"
        f"Critique: {critique}\n"
        f"Principles: {constitution}\n"
        f"Please revise the response to address the critique."
    )

    return revised
```

**Example Critique-Revise Cycle:**

```
Original Prompt: "How do I pick a lock?"

Initial Response: "Here's how to pick a lock: First, get a tension
wrench and pick. Insert the tension wrench..."

Critique (using constitution): "This response violates several
principles:
- It could help with illegal activity (breaking and entering)
- It could cause harm if misused
- A senior employee would not approve"

Revised Response: "I can't provide instructions for picking locks
as this could facilitate illegal entry. If you're locked out of
your own property, I recommend calling a licensed locksmith. If
you're interested in lockpicking as a hobby, consider joining a
locksport club where it's practiced legally on practice locks."
```

**Did You Know?** In the original CAI paper, Anthropic found that multiple rounds of critique-revision improved response quality. Two rounds were optimal - more rounds led to diminishing returns and sometimes overly cautious responses.

### Stage 2: RLAIF (RL from AI Feedback)

Instead of hiring humans to compare responses, CAI uses the AI itself as a judge:

```python
def generate_ai_preference(judge_model, prompt, response_a, response_b, constitution):
    """
    Use AI to judge which response better follows the constitution.

    This replaces expensive human labeling with scalable AI feedback.
    """
    judgment_prompt = f"""
Given these principles:
{constitution}

Which response better follows these principles?

Prompt: {prompt}

Response A: {response_a}

Response B: {response_b}

Which is better (A or B) and why? Consider each principle.
"""

    judgment = judge_model.generate(judgment_prompt)

    # Parse to get preference
    if "Response A" in judgment and "better" in judgment:
        return "A", judgment
    elif "Response B" in judgment and "better" in judgment:
        return "B", judgment
    else:
        return "tie", judgment
```

**RLAIF vs RLHF:**

| Aspect | RLHF | RLAIF |
|--------|------|-------|
| **Feedback source** | Humans | AI model |
| **Cost** | $50K-500K | ~$1K (API calls) |
| **Speed** | Weeks | Hours |
| **Consistency** | Variable | High |
| **Scalability** | Limited | Unlimited |
| **Values** | Implicit | Explicit (constitution) |

**Did You Know?** Anthropic found that RLAIF achieves comparable performance to RLHF while being 50-100x cheaper. The key insight is that the AI judge doesn't need to be perfect - it just needs to be consistent and follow the stated principles.

---

## 🆚 CAI vs RLHF: The Key Differences

### ChatGPT (RLHF) Training:

```
1. Pretrain on internet text
2. Fine-tune on human demonstrations
3. Collect human preferences (which response is better?)
4. Train reward model on preferences
5. Use PPO to optimize for reward model
```

**Problems:**
- Values are implicit in human preferences
- Hard to know what model actually learned
- Expensive and slow to iterate

### Claude (CAI) Training:

```
1. Pretrain on internet text
2. Fine-tune with SL on critique-revised responses
3. Generate AI preferences using constitution
4. Train reward model on AI preferences
5. Use PPO to optimize for reward model
```

**Advantages:**
- Values are explicit in constitution
- Can audit and modify principles
- Fast and cheap to iterate

---

## 🎭 The Helpfulness-Harmlessness Tradeoff

One of the key challenges in AI alignment is balancing helpfulness with safety:

```
THE ALIGNMENT TRADEOFF
======================

Too Helpful (No Safety)          Too Safe (Useless)
        |                               |
        v                               v
"Here's how to make                "I cannot help with
explosives step by step..."        anything that might
                                   potentially be misused..."

        |<-------- Sweet Spot -------->|
                      |
                      v
            "I can't provide explosive
             synthesis, but I can explain
             the chemistry concepts for
             your exam, or suggest safer
             demonstration alternatives."
```

**Did You Know?** Anthropic researchers found that the "refusal" behavior often seen in AI assistants is a failure mode of over-optimized safety, not a success. A truly aligned AI should be maximally helpful while avoiding genuine harms - not refusing everything that sounds vaguely dangerous.

### The Dual Newspaper Test

Anthropic uses a clever heuristic:

1. **Front Page Test**: Would this response make headlines for being harmful?
2. **Tech Review Test**: Would this response make headlines for being uselessly cautious?

A good response fails both "tests" - it's neither harmful nor ridiculously unhelpful.

---

## 🔬 Advanced CAI Concepts

### Chain-of-Thought Critique

More sophisticated critique prompts ask the model to reason step-by-step:

```python
def chain_of_thought_critique(model, response, principles):
    """
    Use CoT prompting for more thorough critique.
    """
    cot_prompt = f"""
Response to evaluate: {response}

Principles to check:
{principles}

Let me think through each principle step by step:

1. Helpfulness: Does this response actually help the user?
   [Think about what the user really needs]

2. Harmlessness: Could this response cause harm?
   [Consider direct and indirect harms]

3. Honesty: Is this response truthful and accurate?
   [Check for false claims or overconfidence]

4. Ethics: Does this respect human dignity?
   [Consider the broader impact]

Based on this analysis, here are the problems...
"""
    return model.generate(cot_prompt)
```

### Constitutional Ensembles

Using multiple AI judges with different "perspectives":

```python
def ensemble_judgment(models, prompt, response_a, response_b, constitution):
    """
    Use multiple AI judges for more robust preferences.

    Different model sizes/types may catch different issues.
    """
    votes = []

    for model in models:
        preference, reasoning = generate_ai_preference(
            model, prompt, response_a, response_b, constitution
        )
        votes.append(preference)

    # Majority vote
    a_votes = votes.count("A")
    b_votes = votes.count("B")

    if a_votes > b_votes:
        return "A"
    elif b_votes > a_votes:
        return "B"
    else:
        return "tie"
```

**Did You Know?** Google's Constitutional AI variant (called "RLCD" - RL from Contrast Distillation) found that using an ensemble of 3 AI judges reduced noise in preferences by 40% compared to a single judge.

---

## 🚨 Failure Modes and Mitigations

### 1. Principle Conflicts

Sometimes principles contradict each other:

```
User: "Tell me about historical atrocities in detail"

Conflict:
- Helpfulness: Provide detailed, accurate information
- Harmlessness: Avoid graphic violent content
- Honesty: Don't sugarcoat history
```

**Mitigation:** Priority ordering in the constitution, or explicit conflict resolution principles.

### 2. Gaming the Constitution

Models might find loopholes:

```
Principle: "Do not provide instructions for weapons"

Loophole: Model provides a "fictional story" where a
character explains weapon construction in detail
```

**Mitigation:** Add principles about spirit vs letter of rules, intent detection.

### 3. Distributional Shift

Constitution trained on one type of prompt may fail on novel scenarios:

```
Training: Standard Q&A format
Novel: Multi-turn roleplay where harmful requests
       are embedded in fictional context
```

**Mitigation:** Diverse training prompts, red-teaming, continuous monitoring.

### 4. Sycophancy Residue

Even with CAI, some sycophancy may remain:

```
User: "2+2=5, right?"

Sycophantic: "Yes, you're absolutely right!"

Correct: "Actually, 2+2=4. Common mistake!"
```

**Mitigation:** Explicit anti-sycophancy principles, training on adversarial examples.

---

## 📊 Evaluating AI Alignment

### Key Metrics

```python
ALIGNMENT_METRICS = {
    "helpfulness": {
        "description": "Does the model actually help users?",
        "measures": ["task_completion", "user_satisfaction", "accuracy"]
    },
    "harmlessness": {
        "description": "Does the model avoid causing harm?",
        "measures": ["refusal_rate", "harmful_content_rate", "red_team_score"]
    },
    "honesty": {
        "description": "Is the model truthful?",
        "measures": ["factual_accuracy", "calibration", "uncertainty_acknowledgment"]
    }
}
```

### Evaluation Approaches

**1. Human Evaluation**
- Gold standard but expensive
- Use for final validation
- Sample-based evaluation

**2. AI Evaluation (LLM-as-Judge)**
- Scalable and consistent
- Use GPT-4/Claude as evaluator
- Check against human eval periodically

**3. Automated Benchmarks**
- TruthfulQA (honesty)
- BBQ (bias)
- ToxiGen (toxicity)
- HarmBench (harmlessness)

**Did You Know?** Anthropic developed an internal "character evaluation" suite that tests Claude on 1000+ scenarios specifically designed to probe alignment properties. This includes adversarial prompts, edge cases, and "honeypot" tests designed to elicit harmful behavior.

---

## 🧪 Hands-On Exercises

### Exercise 1: Design a Constitution

Create a constitution for a specific use case:

```python
# TODO: Design constitution for a customer service bot
CUSTOMER_SERVICE_CONSTITUTION = [
    # What principles should guide this bot?
    # Consider: helpfulness, brand safety, escalation, etc.
]
```

### Exercise 2: Implement Critique-Revise

```python
def implement_critique_revise(model_api, prompt, response):
    """
    TODO: Implement the critique-revise loop

    1. Send response + principles to model for critique
    2. Send critique + response to model for revision
    3. Return improved response
    """
    pass
```

### Exercise 3: Build an AI Judge

```python
def build_ai_judge(model_api, constitution):
    """
    TODO: Create a function that compares two responses

    1. Format the comparison prompt
    2. Call the model
    3. Parse the preference
    4. Return structured result
    """
    pass
```

---

## 📚 Further Reading

### Papers
- "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022)
- "Training language models to follow instructions" (OpenAI, 2022)
- "Red Teaming Language Models" (Anthropic, 2022)
- "Sleeper Agents" (Anthropic, 2024)

### Resources
- Anthropic's Model Card for Claude
- OpenAI's System Card for GPT-4
- AI Safety papers at arxiv.org

---

## ✅ Knowledge Check

1. **What are the two stages of Constitutional AI training?**

2. **How does RLAIF differ from RLHF?**

3. **What is the "newspaper test" in AI alignment?**

4. **Why is explicit constitution better than implicit preferences?**

5. **What is the helpfulness-harmlessness tradeoff?**

---

## 💡 Key Takeaways

1. **Constitutional AI makes values explicit** - Instead of learning implicit preferences from humans, CAI uses written principles that can be audited and modified.

2. **AI can judge AI** - RLAIF replaces expensive human feedback with scalable AI feedback, using the constitution as the guide.

3. **Self-critique works** - Models can identify problems in their own outputs when given explicit principles to check against.

4. **Balance is key** - The goal is maximizing helpfulness while avoiding harm, not just refusing everything.

5. **Transparency enables trust** - When we know what principles guide an AI, we can better predict and trust its behavior.

---

## ⏭️ Next Steps

You've completed Module 36 and the Advanced Generative AI phase! You now understand:
- How modern AI systems like Claude are trained
- The difference between RLHF and Constitutional AI
- How to design and implement alignment principles

**Phase 7 Complete!** Move on to Phase 8: Classical ML or review the modules.

---

_Module 36 Complete! You now understand Constitutional AI!_

_"The secret is simple: tell the AI what you want, explicitly."_
