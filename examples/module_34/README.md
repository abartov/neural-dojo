# Module 34 Examples: Code Generation Models

This directory contains working code examples for Module 34: Code Generation Models.

## Overview

Learn how AI coding assistants like GitHub Copilot, Cursor, and Claude Code work under the hood.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Main Deliverable

### Code Generation Toolkit

**File**: `deliverable_codegen_toolkit.py`

A comprehensive toolkit for understanding code generation:

```bash
# FIM transformation demo
python deliverable_codegen_toolkit.py demo1

# Completion strategy comparison
python deliverable_codegen_toolkit.py demo2

# Pass@k evaluation
python deliverable_codegen_toolkit.py demo3

# Code search index
python deliverable_codegen_toolkit.py demo4

# Generate analysis report
python deliverable_codegen_toolkit.py demo5
```

## Key Concepts Covered

### 1. Fill-in-the-Middle (FIM)

How models learn to insert code, not just continue:
- PSM format (Prefix-Suffix-Middle)
- SPM format (Suffix-Prefix-Middle)
- Different model conventions

### 2. Code Completion Strategies

Different approaches to generating code:
- Greedy decoding (temperature=0)
- Sampling with temperature
- Beam search
- Best-of-n selection

### 3. Pass@k Evaluation

The key metric for code generation benchmarks:
- HumanEval problems
- MBPP dataset
- SWE-bench for real-world tasks

### 4. Code Search

Building repository-aware completion:
- AST-based code chunking
- Keyword indexing
- Semantic search with embeddings
- Hybrid search strategies

## Expected Output

```
$ python deliverable_codegen_toolkit.py demo1
======================================================================
Demo 1: Fill-in-the-Middle (FIM) Transformation
======================================================================

Original Code:
----------------------------------------
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0
    total = sum(numbers)
    count = len(numbers)
    return total / count

FIM Transformation (Line Strategy):
----------------------------------------
Prefix:
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""

[CURSOR - Model generates here]

Middle (what model should generate):
    if not numbers:

Suffix:
        return 0.0
    total = sum(numbers)
...
```

## Storage

Results are saved to `.codegen_toolkit/`:
- `code_index.json` - Saved code search index
- `codegen_report.md` - Analysis report

## Further Reading

- [Codex Paper](https://arxiv.org/abs/2107.03374)
- [StarCoder](https://arxiv.org/abs/2305.06161)
- [DeepSeek Coder](https://arxiv.org/abs/2401.14196)
- [FIM Paper](https://arxiv.org/abs/2207.14255)
