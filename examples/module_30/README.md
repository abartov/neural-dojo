# Module 30 Examples: Transformers & Attention Mechanisms

This directory contains working code examples for Module 30 - Transformers & Attention.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Self-Attention Visualizer
**File**: `example_01_attention_visualizer.py`
**Description**: Visualize how self-attention works on simple sequences.
**Run**: `python example_01_attention_visualizer.py`

### Example 2: Multi-Head Attention
**File**: `example_02_multihead_attention.py`
**Description**: Build and test multi-head attention from scratch.
**Run**: `python example_02_multihead_attention.py`

### Example 3: Positional Encoding
**File**: `example_03_positional_encoding.py`
**Description**: Visualize sinusoidal and learned positional encodings.
**Run**: `python example_03_positional_encoding.py`

### Example 4: Complete Transformer
**File**: `example_04_transformer_encoder.py`
**Description**: Build a complete transformer encoder.
**Run**: `python example_04_transformer_encoder.py`

## Deliverable

### Transformer Lab
**File**: `deliverable_transformer_lab.py`
**Description**: A comprehensive lab for building, training, and analyzing transformers.
**Documentation**: See `DELIVERABLE_README.md`

```bash
python deliverable_transformer_lab.py demo1  # Self-attention visualization
python deliverable_transformer_lab.py demo2  # Train mini language model
python deliverable_transformer_lab.py demo3  # Attention pattern analysis
python deliverable_transformer_lab.py demo4  # Generate transformer report
```

## Key Concepts

### Self-Attention
- Query, Key, Value projections
- Scaled dot-product attention
- Softmax normalization

### Multi-Head Attention
- Multiple attention heads in parallel
- Each head learns different patterns
- Concatenation and projection

### Positional Encoding
- Sinusoidal encoding (original)
- Learned positional embeddings
- Relative position representations

### Full Transformer
- Encoder blocks (attention + feed-forward)
- Layer normalization
- Residual connections

## Related Module

See `docs/curriculum/notes/module_30_transformers.md` for the full theory.

This is a **Heureka Moment** module - you'll understand why "Attention Is All You Need"!
