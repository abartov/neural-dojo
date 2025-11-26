# Module 17 Deliverable: Reasoning Engine

**A comprehensive reasoning system combining Chain-of-Thought, ReAct, self-consistency, and more.**

## Features

- **Automatic Problem Classification**: Detects problem type (arithmetic, logic, multi-step)
- **Adaptive Strategy Selection**: Chooses the best reasoning approach
- **Multiple Reasoning Strategies**: Zero-shot CoT, Few-shot CoT, Self-consistency, PAL, ReAct
- **Confidence Scoring**: Reports reliability of answers
- **Reasoning Trace Logging**: Persists all reasoning for analysis
- **Benchmark Suite**: Evaluate strategy performance

## Quick Start

```bash
python deliverable_reasoning_engine.py demo1  # Compare reasoning techniques
python deliverable_reasoning_engine.py demo2  # ReAct with tools
python deliverable_reasoning_engine.py demo3  # Benchmark evaluation
python deliverable_reasoning_engine.py solve "What is 15 * 7 + 3?"  # Solve any question
```

## Reasoning Strategies

| Strategy | Best For | How It Works |
|----------|----------|--------------|
| Zero-Shot CoT | General reasoning | "Let's think step by step" |
| Self-Consistency | Multi-step problems | Multiple paths, vote on answer |
| PAL | Math calculations | Generate and execute Python code |
| ReAct | Factual questions | Reason + Act with tools |
| Least-to-Most | Complex problems | Decompose into sub-problems |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Reasoning Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────────────────────────────┐ │
│  │   Problem   │    │         Strategy Selector           │ │
│  │ Classifier  │───▶│  arithmetic → PAL                   │ │
│  │             │    │  multi_step → Self-Consistency      │ │
│  └─────────────┘    │  factual    → ReAct                 │ │
│                     │  logic      → Zero-Shot CoT         │ │
│                     └─────────────────────────────────────┘ │
│                                  │                          │
│                                  ▼                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                  Reasoning Executor                     ││
│  │                                                         ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ││
│  │  │Zero-Shot │ │Self-Con  │ │   PAL    │ │  ReAct   │  ││
│  │  │   CoT    │ │sistency  │ │ (Code)   │ │ (Tools)  │  ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│                                  │                          │
│                                  ▼                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Reasoning Trace (question, strategy, answer, conf...)  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Problem Types

The engine automatically classifies problems:

- **Arithmetic**: "Calculate", "compute", "sum" → Uses PAL
- **Multi-step**: Multiple numbers, "then", "after" → Uses Self-Consistency
- **Logic**: "If", "all", "therefore" → Uses Zero-Shot CoT
- **Factual**: "What is", "capital of" → Uses ReAct
- **Trick**: "All but", "except" → Uses Zero-Shot CoT

## Example Usage

```python
from deliverable_reasoning_engine import ReasoningEngine, ReasoningStrategy

engine = ReasoningEngine()

# Auto-select strategy
trace = engine.solve("What is 15 * 7 + 3?")
print(f"Answer: {trace.answer}")
print(f"Confidence: {trace.confidence:.0%}")

# Force specific strategy
trace = engine.solve(
    "A store has 23 apples...",
    strategy=ReasoningStrategy.SELF_CONSISTENCY
)
```

## Data Storage

Reasoning traces are persisted to `.reasoning_engine/`:

- `reasoning_traces.json` - Last 100 reasoning traces
- `benchmarks.json` - Benchmark results

## Benchmark Results

Run benchmarks to compare strategies:

```bash
python deliverable_reasoning_engine.py demo3
```

Sample output:
```
📈 Results:
   Accuracy: 80% (4/5)
   Avg Latency: 1250ms
   Avg Confidence: 75%
```

## Key Concepts Demonstrated

1. **Chain-of-Thought**: Making LLMs "think out loud"
2. **Self-Consistency**: Multiple paths for robust answers
3. **Program-Aided**: Code for accurate calculations
4. **ReAct Pattern**: Reasoning + Acting with tools
5. **Adaptive Selection**: Right strategy for right problem

---

**Time**: ~4 hours | **Lines**: 550+ | **Author**: Neural Dojo Module 17
