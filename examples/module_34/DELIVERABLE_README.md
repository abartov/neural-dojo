# Module 34 Deliverable: Code Generation Toolkit

**Understand how AI coding assistants work under the hood!**

## Features

- **FIM Transformation**: See how Fill-in-the-Middle training works
- **Completion Strategies**: Compare greedy, sampling, and beam search
- **Pass@k Evaluation**: Understand the key code generation metric
- **Code Search**: Build semantic code search indexes
- **Model Comparison**: Compare current code generation models

## Quick Start

```bash
# Navigate to module directory
cd examples/module_34

# Run demos
python deliverable_codegen_toolkit.py demo1  # FIM transformation
python deliverable_codegen_toolkit.py demo2  # Completion strategies
python deliverable_codegen_toolkit.py demo3  # Pass@k evaluation
python deliverable_codegen_toolkit.py demo4  # Code search index
python deliverable_codegen_toolkit.py demo5  # Generate full report
```

## Demo Descriptions

### Demo 1: Fill-in-the-Middle (FIM)

Shows how code is transformed for FIM training:

```
Original:    def add(a, b): return a + b
             ↓
FIM Format:  <fim_prefix>def add(a, b): <fim_suffix>
             <fim_middle>return a + b
```

**Key insight**: FIM enables insertion, not just continuation!

### Demo 2: Completion Strategies

Compares different code completion approaches:

| Strategy | Temperature | Best For |
|----------|-------------|----------|
| Greedy | 0.0 | Single best completion |
| Low Sampling | 0.3 | Code completion |
| High Sampling | 1.0 | Exploration |
| Beam Search | - | Quality-critical |

### Demo 3: Pass@k Evaluation

Demonstrates the key metric for code generation:

```
Accuracy: 20%
Pass@1:   20%
Pass@10:  89%   ← Much higher!
Pass@100: 99%

Key insight: Multiple samples dramatically improve success!
```

### Demo 4: Code Search Index

Builds a semantic code search system:
- Parses Python files into chunks
- Indexes by name, keywords, embeddings
- Supports keyword, semantic, and hybrid search

### Demo 5: Analysis Report

Generates a comprehensive report covering:
- FIM statistics
- Completion strategy comparison
- Pass@k analysis
- Code index stats
- Recommendations

## Key Concepts

### Fill-in-the-Middle (FIM)

Traditional models: Generate left-to-right only
FIM models: Can insert code anywhere (prefix + suffix → middle)

```
# Without FIM:
def greet(name):
    |← cursor, model can only continue

# With FIM:
def greet(name):
    |← cursor (prefix above, suffix below)
    return message  ← model sees this too!
```

### Pass@k Metric

```python
def estimate_pass_at_k(n: int, c: int, k: int) -> float:
    """
    n = total samples
    c = correct samples
    k = number of attempts allowed
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))
```

### Model Landscape

| Model | HumanEval | Open | Best For |
|-------|-----------|------|----------|
| GPT-4 | 67% | No | Best quality |
| Claude 3.5 | 64% | No | Long context |
| DeepSeek 33B | 56% | Yes | Best open model |
| StarCoder2 | 46% | Yes | Fully open |

## Output Files

```
.codegen_toolkit/
├── code_index.json       # Saved code search index
└── codegen_report.md     # Generated analysis report
```

## No API Keys Required

All demos work without external APIs:
- FIM transformation is local
- Completion strategies are simulated
- Pass@k uses mathematical formulas
- Code search uses simple embeddings

## Dependencies

- numpy (for statistics and embeddings)
- Standard library only (ast, re, json, etc.)

**Time**: ~5 hours | **Lines**: 900+ | **Author**: Neural Dojo
