# Module 28 Examples: Training Deep Networks

This directory contains working code examples for Module 28 - Training Deep Networks.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Normalization Comparison
**File**: `example_01_normalization_comparison.py`
**Description**: Compare BatchNorm vs LayerNorm vs no normalization on MNIST. See how each behaves with different batch sizes.

```bash
python example_01_normalization_comparison.py
```

Key observations:
- BatchNorm works best with large batches (32+)
- LayerNorm is more stable with small batches
- No normalization struggles with deep networks

### Example 2: Initialization Comparison
**File**: `example_02_initialization_comparison.py`
**Description**: Compare Xavier vs He vs Random initialization. See how initialization affects gradient flow and convergence.

```bash
python example_02_initialization_comparison.py
```

Key observations:
- He initialization works best for ReLU networks
- Random uniform can cause extreme gradients
- Too-small initialization causes vanishing gradients

### Example 3: Learning Rate Schedules
**File**: `example_03_learning_rate_schedules.py`
**Description**: Compare different learning rate schedules: Constant, Step decay, Cosine annealing, Warmup+Cosine, and 1cycle.

```bash
python example_03_learning_rate_schedules.py
```

Key observations:
- Constant LR often plateaus early
- Cosine annealing is smooth and effective
- 1cycle often achieves best results fastest
- Warmup prevents early divergence

### Example 4: Complete Training Pipeline
**File**: `example_04_complete_training_pipeline.py`
**Description**: A production-ready training pipeline with ALL best practices combined.

```bash
python example_04_complete_training_pipeline.py
```

Features demonstrated:
- He (Kaiming) initialization
- BatchNorm + LayerNorm
- Dropout regularization
- AdamW optimizer with weight decay
- Warmup + Cosine annealing LR schedule
- Gradient clipping
- Early stopping
- Model checkpointing
- Label smoothing

## Expected Output

Each example will:
1. Train models on MNIST (subset for faster execution)
2. Print progress during training
3. Display a summary comparison at the end
4. Optionally save plots (if matplotlib is available)

## Notes

- Examples use a subset of MNIST for faster execution
- GPU is used if available (CUDA)
- Checkpoints are saved to `./checkpoints/` directory
- Plots are saved to current directory as PNG files

## Common Issues

**CUDA out of memory**: Reduce batch_size in the config
**NaN loss**: Try reducing learning rate or adding gradient clipping
**Slow training**: Ensure you're using GPU if available
