# Module 17: Chain-of-Thought & Reasoning 🔮

This module teaches you how to make LLMs "think out loud" for dramatically improved reasoning.

## 🔮 The Heureka Moment

**Making AI "think out loud" dramatically improves its reasoning ability.**

Adding "Let's think step by step" can improve accuracy by 2-3x on reasoning tasks!

## Learning Objectives

- Master Chain-of-Thought (CoT) prompting
- Implement the ReAct pattern (Reason + Act)
- Build multi-step reasoning systems
- Apply self-consistency for reliable answers
- Understand reasoning limitations

## Examples

### Example 1: Chain-of-Thought (`01_chain_of_thought.py`)
Demonstrates the power of CoT prompting:
- Direct vs CoT comparison
- Zero-shot CoT ("Let's think step by step")
- Few-shot CoT with examples
- Different trigger phrases

```bash
export GOOGLE_API_KEY="your-key"
python 01_chain_of_thought.py
```

### Example 2: ReAct Pattern (`02_react_pattern.py`)
Combines reasoning with tool use:
- The ReAct prompt format
- Manual ReAct loop implementation
- Tools: calculate, search, convert
- Comparison to pure reasoning

```bash
python 02_react_pattern.py
```

### Example 3: Self-Consistency (`03_self_consistency.py`)
Advanced reasoning techniques:
- Multiple reasoning paths voting
- Least-to-most decomposition
- Program-Aided Language Models (PAL)
- Technique comparison

```bash
python 03_self_consistency.py
```

## Deliverable: Reasoning Engine

A comprehensive system combining all techniques.

```bash
python deliverable_reasoning_engine.py demo1  # Techniques
python deliverable_reasoning_engine.py demo2  # ReAct
python deliverable_reasoning_engine.py demo3  # Benchmark
python deliverable_reasoning_engine.py solve "Your question"
```

See [DELIVERABLE_README.md](DELIVERABLE_README.md) for full documentation.

## Key Concepts

### 1. Zero-Shot CoT
Just add "Let's think step by step" to your prompt.

### 2. Few-Shot CoT
Provide 2-3 examples of step-by-step reasoning.

### 3. ReAct Pattern
```
Thought → Action → Observation → Repeat → Final Answer
```

### 4. Self-Consistency
Generate multiple reasoning paths, vote on the answer.

### 5. PAL (Program-Aided)
Generate code for calculations instead of natural language.

## When to Use Each Technique

| Technique | Best For |
|-----------|----------|
| Zero-Shot CoT | General reasoning, logic |
| Few-Shot CoT | Domain-specific problems |
| Self-Consistency | High-stakes decisions |
| ReAct | Questions needing external info |
| PAL | Math and calculations |

## Prerequisites

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="your-key"  # or ANTHROPIC_API_KEY
```

## Next Module

**Module 18: LangGraph for Stateful Workflows** - Build sophisticated agents with persistent state, cycles, and complex control flow.
