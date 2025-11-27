# Module 35 Examples: RLHF & How LLMs Are Trained 🔮

This directory contains working code examples for Module 35: RLHF.

## Overview

Learn how ChatGPT and Claude were actually trained! This is THE module
that explains the secret sauce behind modern AI assistants.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Main Deliverable

### RLHF Training Toolkit

**File**: `deliverable_rlhf_toolkit.py`

A comprehensive toolkit for understanding RLHF:

```bash
# Reward model training
python deliverable_rlhf_toolkit.py demo1

# DPO vs PPO comparison
python deliverable_rlhf_toolkit.py demo2

# KTO with unpaired feedback
python deliverable_rlhf_toolkit.py demo3

# Full RLHF pipeline
python deliverable_rlhf_toolkit.py demo4

# Generate analysis report
python deliverable_rlhf_toolkit.py demo5
```

## Key Concepts

### The Three Stages

1. **Pretraining**: Next-token prediction on internet text
2. **SFT**: Train on human demonstrations
3. **RLHF**: Optimize for human preferences

### Why RLHF Matters

GPT-3 → GPT-3.5 → ChatGPT

The difference? RLHF taught the model to:
- Answer questions (not just continue them)
- Refuse harmful requests
- Admit uncertainty

### Modern Methods

- **PPO**: Original, 4 models, slow, unstable
- **DPO**: 2 models, 10x faster, stable
- **KTO**: Works with thumbs up/down
- **ORPO**: Single model, fastest

## Expected Output

```
$ python deliverable_rlhf_toolkit.py demo1
======================================================================
Demo 1: Bradley-Terry Reward Model Training
======================================================================

What is a Reward Model?
----------------------------------------
A reward model predicts human preferences:
  Input: (prompt, response)
  Output: Scalar reward (higher = better)

Training: Learn to predict which response humans prefer
  Given: Response A vs Response B
  Loss: -log(sigmoid(R(A) - R(B))) when A is preferred

Generating preference pairs...
  Generated 50 preference pairs

Training Reward Model:
----------------------------------------
  Epoch 1/3: Loss = 0.6931
  Epoch 2/3: Loss = 0.5234
  Epoch 3/3: Loss = 0.4521
...
```

## Further Reading

- [InstructGPT Paper](https://arxiv.org/abs/2203.02155)
- [DPO Paper](https://arxiv.org/abs/2305.18290)
- [Constitutional AI](https://arxiv.org/abs/2212.08073)
- [HuggingFace TRL Library](https://github.com/huggingface/trl)
