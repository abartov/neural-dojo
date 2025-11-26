# Module 27: PyTorch Fundamentals

This directory contains code examples for learning PyTorch from the ground up.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 01: Tensor Basics
**File**: `example_01_tensors_basics.py`
**Description**: Learn PyTorch tensors - creation, properties, operations, NumPy bridge
**Run**: `python example_01_tensors_basics.py`

### Example 02: Autograd
**File**: `example_02_autograd.py`
**Description**: Automatic differentiation - the magic behind deep learning
**Run**: `python example_02_autograd.py`

### Example 03: Neural Networks
**File**: `example_03_neural_network.py`
**Description**: Building and training neural networks with nn.Module
**Run**: `python example_03_neural_network.py`

## Deliverable

### PyTorch Lab
**File**: `deliverable_pytorch_lab.py`
**Description**: Comprehensive PyTorch learning toolkit with benchmarks, autograd visualization, architecture builder, and training experiments

**Commands**:
```bash
python deliverable_pytorch_lab.py demo1  # Tensor benchmarks
python deliverable_pytorch_lab.py demo2  # Autograd visualizer
python deliverable_pytorch_lab.py demo3  # Architecture builder
python deliverable_pytorch_lab.py demo4  # Training lab
python deliverable_pytorch_lab.py demo5  # Full experiment
```

## Expected Output

### Example 01 (Tensors)
```
TENSOR CREATION
===============
From list: tensor([1, 2, 3, 4, 5])
zeros(3, 4): 3x4 matrix of zeros
...
```

### Example 02 (Autograd)
```
BASIC GRADIENT COMPUTATION
==========================
x = 2.0
y = x^2 = 4.0
dy/dx = 2x = 4.0
```

### Example 03 (Neural Networks)
```
Training for 20 epochs...
Epoch 5: Train Acc=85.0%, Test Acc=82.0%
...
Final Test Accuracy: 95%+
```

## Key Concepts

1. **Tensors**: Multi-dimensional arrays (like NumPy but with GPU support)
2. **Autograd**: Automatic gradient computation via computational graphs
3. **nn.Module**: Base class for all neural networks
4. **Optimizers**: SGD, Adam, AdamW for weight updates
5. **DataLoaders**: Efficient batching and shuffling

## Notes

- GPU support is automatic if CUDA is available
- PyTorch uses define-by-run (dynamic graphs)
- Always call `optimizer.zero_grad()` before backward pass
- Use `model.train()` and `model.eval()` to toggle modes
