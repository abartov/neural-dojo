# Module 27 Deliverable: PyTorch Lab

**A comprehensive PyTorch learning toolkit for mastering deep learning fundamentals.**

## Features

- **Tensor Benchmarks**: Compare PyTorch vs NumPy performance
- **Autograd Visualizer**: Understand automatic differentiation
- **Architecture Builder**: Design and analyze neural networks
- **Training Lab**: Experiment with hyperparameters
- **GPU Support**: Automatic detection and benchmarking

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demos
python deliverable_pytorch_lab.py demo1  # Tensor benchmarks
python deliverable_pytorch_lab.py demo2  # Autograd visualization
python deliverable_pytorch_lab.py demo3  # Architecture comparison
python deliverable_pytorch_lab.py demo4  # Training experiments
python deliverable_pytorch_lab.py demo5  # Full comprehensive demo
```

## Demo Descriptions

### Demo 1: Tensor Benchmarks
Compares PyTorch tensor operations with NumPy:
- Element-wise operations
- Matrix multiplication
- Reductions (sum, mean)
- Mathematical functions
- GPU vs CPU performance (if CUDA available)

### Demo 2: Autograd Visualizer
Demonstrates automatic differentiation:
- Simple gradients (x^2, x^3, sin, exp, log)
- Chain rule in action
- Neural network gradient flow
- Understanding computational graphs

### Demo 3: Architecture Builder
Compare neural network architectures:
- Different depths (shallow vs deep)
- Different widths (narrow vs wide)
- Parameter counting
- Layer analysis

### Demo 4: Training Lab
Run hyperparameter experiments:
- Learning rate comparison
- Optimizer comparison (SGD vs Adam)
- Architecture comparison
- Dropout effects

### Demo 5: Full Experiment
Comprehensive demonstration combining all features.

## Key Concepts

### Tensors
```python
# Create tensor
x = torch.randn(3, 4)

# Operations
y = x @ x.T  # Matrix multiply
z = torch.relu(x)  # Activation
```

### Autograd
```python
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2
y.backward()
print(x.grad)  # tensor([4.0])
```

### Neural Networks
```python
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)
```

### Training Loop
```python
for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model(data)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
```

## Benchmark Results (Typical)

| Operation | PyTorch vs NumPy |
|-----------|------------------|
| Matrix multiply | ~1.5x faster |
| Element-wise | ~1.2x faster |
| Reductions | ~1.3x faster |
| GPU vs CPU | 10-100x faster |

## Training Results (Typical)

| Config | Accuracy |
|--------|----------|
| Small network | ~85% |
| Medium network | ~90% |
| With dropout | ~92% |
| With AdamW | ~93% |

## Files Generated

Results are saved to `.pytorch_lab/`:
- `benchmark_results.json` - Tensor benchmarks
- `autograd_results.json` - Gradient computations
- `training_results.json` - Training experiments
- `full_experiment.json` - Comprehensive results

## Why PyTorch?

1. **Dynamic Graphs**: Define-by-run makes debugging easy
2. **Pythonic**: Feels like regular Python code
3. **Research Standard**: 80%+ of ML papers use PyTorch
4. **Autograd**: No manual gradient calculation
5. **GPU Support**: Seamless CPU/GPU switching

---

**Time**: ~4-6 hours | **Lines**: 700+ | **Author**: Neural Dojo
