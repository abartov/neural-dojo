# Module 31 Deliverable: Autograd Engine

**A complete automatic differentiation engine built from scratch — understand how neural networks really learn.**

**This module completes Phase 6 - Deep Learning Foundations!**

## Features

- **Scalar Autograd**: Value class with full operation support
- **Neural Network**: MLP built entirely with custom autograd
- **Gradient Checking**: Verify correctness with numerical gradients
- **Visualization**: See the computation graph
- **Training Demo**: Train XOR classifier from scratch

## Quick Start

```bash
python deliverable_autograd_engine.py demo1  # Scalar autograd basics
python deliverable_autograd_engine.py demo2  # Train neural network
python deliverable_autograd_engine.py demo3  # Gradient checking
python deliverable_autograd_engine.py demo4  # Generate report
```

## Demo Details

### Demo 1: Scalar Autograd Basics

Shows how the chain rule works at the scalar level:

```
Example: L = (x * w + b)²

Forward pass:
  x = 2.0, w = 3.0, b = 1.0
  z = x*w + b = 7.0
  L = z² = 49.0

Backward pass (gradients):
  dL/dL = 1.0
  dL/dz = 2z = 14.0
  dL/dw = dL/dz * dz/dw = 14 * 2 = 28.0
  dL/dx = dL/dz * dz/dx = 14 * 3 = 42.0
```

### Demo 2: Train Neural Network

Trains an MLP on the XOR problem using our custom autograd:

```
Dataset: XOR (not linearly separable!)
  [0, 0] -> 0
  [0, 1] -> 1
  [1, 0] -> 1
  [1, 1] -> 0

Architecture: 2 -> 8 -> 8 -> 1
Parameters: ~100
Training: 100 epochs with SGD

Final predictions:
  [0, 0] -> 0.02 ✓
  [0, 1] -> 0.97 ✓
  [1, 0] -> 0.96 ✓
  [1, 1] -> 0.04 ✓
```

### Demo 3: Gradient Checking

Verifies autograd correctness by comparing with numerical gradients:

```
Test: L = tanh(x*w + b)²

  x: analytical=0.2851, numerical=0.2851, error=1.23e-10 ✓ PASS
  w: analytical=0.2851, numerical=0.2851, error=1.23e-10 ✓ PASS
  b: analytical=0.2851, numerical=0.2851, error=1.23e-10 ✓ PASS

SUMMARY: 12/12 gradient checks passed
All gradients verified! Autograd implementation is correct.
```

### Demo 4: Report Generator

Generates a comprehensive markdown report summarizing all tests.

## How It Works

### The Value Class

Every operation records how to compute its gradient:

```python
def __mul__(self, other):
    out = Value(self.data * other.data, (self, other), '*')

    def _backward():
        # d(a * b)/da = b, d(a * b)/db = a
        self.grad += other.data * out.grad
        other.grad += self.data * out.grad
    out._backward = _backward

    return out
```

### Backward Pass

Topological sort ensures correct order:

```python
def backward(self):
    # Build topological order
    topo = []
    visited = set()
    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._prev:
                build_topo(child)
            topo.append(v)
    build_topo(self)

    # Backpropagate
    self.grad = 1.0
    for v in reversed(topo):
        v._backward()
```

## Key Concepts

### Chain Rule

The foundation of backpropagation:

```
If y = f(g(x)), then dy/dx = dy/dg * dg/dx
```

### Reverse-Mode Autodiff

Compute all gradients in one backward pass:
- O(1) backward passes regardless of parameter count
- Why neural networks use backprop, not forward-mode

### Gradient Checking

Verify with numerical approximation:

```
numerical_grad ≈ [f(x+ε) - f(x-ε)] / (2ε)
```

## Storage

Results are saved to `.autograd_engine/`:
- `training_log.json` - Neural network training results
- `gradient_check_results.json` - Gradient verification
- `autograd_report.md` - Generated report

## Expected Results

| Metric | Expected Value |
|--------|----------------|
| XOR Final Loss | < 0.01 |
| Gradient Check Pass Rate | 100% |
| Training Time (100 epochs) | < 1s |

## Requirements

```
# No external dependencies!
# Pure Python implementation
```

## The Heureka Moment

After completing this module, you understand:

1. **Backprop is just chain rule**: No magic, just calculus
2. **Computational graphs**: Every operation builds the graph
3. **Reverse-mode autodiff**: One backward pass for all gradients
4. **Why it works**: The algorithm that powers all of deep learning

This is exactly how PyTorch's autograd works internally!

---

**Time**: ~6 hours | **Lines**: 600+ | **Author**: Neural Dojo

**Congratulations! You've completed Phase 6: Deep Learning Foundations!**
