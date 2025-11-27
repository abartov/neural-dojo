# Module 30 Deliverable: Transformer Lab

**A comprehensive lab for understanding and building transformer architectures from scratch.**

**This is a HEUREKA MOMENT module - understand why "Attention Is All You Need"!**

## Features

- **Self-Attention Visualization**: See how attention works on sequences
- **Multi-Head Attention**: Multiple attention heads learning different patterns
- **Mini Language Model**: Train a character-level transformer
- **Attention Analysis**: Analyze patterns across layers and heads
- **Report Generator**: Generate comprehensive markdown reports

## Quick Start

```bash
python deliverable_transformer_lab.py demo1  # Visualize attention patterns
python deliverable_transformer_lab.py demo2  # Train mini language model
python deliverable_transformer_lab.py demo3  # Analyze attention patterns
python deliverable_transformer_lab.py demo4  # Generate report
```

## Demo Details

### Demo 1: Self-Attention Visualization

Visualizes how multi-head attention processes a sequence, showing attention patterns for each head.

```
Head 0:
     The  cat  sat   on  the  mat
The   ##   ++   .    .    ++   .
cat   ++   ##   ++   .    .    .
sat   .    ++   ##   ++   .    .
...

Legend: ## = high attention, ++ = medium, . = low
```

### Demo 2: Train Mini Language Model

Trains a small transformer on sample text, demonstrating:
- Character-level tokenization
- Causal (decoder) attention masking
- Autoregressive generation

```
Creating Mini Language Model...
  d_model: 128
  num_heads: 4
  num_layers: 3
  Total parameters: 1,234,567

Training...
  Epoch  1: Loss = 3.2145
  Epoch  2: Loss = 2.4523
  ...

Generated: 'The transformer architecture has...'
```

### Demo 3: Attention Pattern Analysis

Analyzes attention patterns across all layers and heads:

```
Layer 0:
  Head 0: Local/positional attention
    Entropy: 1.23 | Sparsity: 0.45 | Diagonal: 0.67
  Head 1: Key-focused attention
    Entropy: 0.89 | Sparsity: 0.78 | Diagonal: 0.12
...
```

### Demo 4: Report Generator

Generates a comprehensive markdown report summarizing all experiments.

## Key Concepts

### Self-Attention Formula

```
Attention(Q, K, V) = softmax(Q @ K.T / sqrt(d_k)) @ V
```

- **Q (Query)**: What each position is looking for
- **K (Key)**: What each position can be found by
- **V (Value)**: What information each position contains

### Multi-Head Attention

Multiple attention heads run in parallel, each learning different patterns:
- Syntactic relationships (subject-verb)
- Semantic similarity
- Positional patterns

### Positional Encoding

Sinusoidal encoding adds position information:
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

## Architecture Summary

```
Input Tokens
    |
Token Embedding + Positional Encoding
    |
[Transformer Block] x N
    |  - Multi-Head Self-Attention
    |  - Layer Norm + Residual
    |  - Feed-Forward Network
    |  - Layer Norm + Residual
    |
Output Embeddings
```

## Storage

Results are saved to `.transformer_lab/`:
- `mini_lm_result.json` - Language model training results
- `attention_analysis.json` - Attention pattern analysis
- `transformer_report.md` - Generated report

## Expected Results

| Metric | Expected Value |
|--------|---------------|
| Mini LM Final Loss | 1.5-2.5 |
| Training Time (10 epochs) | 10-30s |
| Attention Heads Specialized | Yes |
| Different Patterns per Layer | Yes |

## Requirements

```
torch>=2.0.0
numpy>=1.21.0
matplotlib>=3.5.0
tqdm>=4.62.0
```

## The Heureka Moment

After completing this lab, you'll understand:

1. **Why attention beats recurrence**: Parallel processing, no vanishing gradients
2. **How Q, K, V work**: Soft database lookup with learned projections
3. **Why multiple heads**: Different heads capture different relationships
4. **Why position encoding**: Attention is permutation invariant without it
5. **Why transformers scale**: More parameters + more data = predictable improvement

This is the architecture powering GPT-4, Claude, Gemini, and virtually all modern AI!

---

**Time**: ~4 hours | **Lines**: 750+ | **Author**: Neural Dojo
