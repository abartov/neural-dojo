# Module 31 Examples: Backpropagation Deep Dive

This directory contains working code examples for Module 31 - Backpropagation.

## Prerequisites

```bash
# No external dependencies! Pure Python implementation.
```

## Deliverable

### Autograd Engine
**File**: `deliverable_autograd_engine.py`
**Description**: A complete automatic differentiation engine built from scratch.
**Documentation**: See `DELIVERABLE_README.md`

```bash
python deliverable_autograd_engine.py demo1  # Scalar autograd basics
python deliverable_autograd_engine.py demo2  # Train neural network
python deliverable_autograd_engine.py demo3  # Gradient checking
python deliverable_autograd_engine.py demo4  # Generate report
```

## Key Concepts

### Chain Rule
- Foundation of backpropagation
- Compose derivatives through operations
- dy/dx = dy/dg * dg/dx

### Computational Graph
- Automatically built during forward pass
- Tracks all operations and dependencies
- Enables automatic gradient computation

### Reverse-Mode Autodiff
- Process graph from output to inputs
- O(1) backward passes for all gradients
- Why neural networks use this approach

### Gradient Checking
- Numerical verification of analytical gradients
- Essential for debugging custom operations
- Compare: [f(x+ε) - f(x-ε)] / 2ε

## Related Module

See `docs/curriculum/notes/module_31_backpropagation.md` for the full theory.

**This completes Phase 6: Deep Learning Foundations!**
