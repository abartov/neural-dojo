# Module 26: Neural Networks from Scratch

Build neural networks using only NumPy - no PyTorch, no TensorFlow, just pure mathematics.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: The Perceptron
**File**: `example_01_perceptron.py`

The simplest neural network - a single neuron:
- Learn AND, OR, NAND, NOR gates
- Demonstrate XOR failure (not linearly separable)
- Visualize decision boundaries
- Compare activation functions
- Gradient descent visualization

```bash
python example_01_perceptron.py
```

### Example 2: Multilayer Network
**File**: `example_02_multilayer_network.py`

Build a full neural network from scratch:
- Forward propagation implementation
- Backpropagation derivation and code
- Solve the XOR problem
- Non-linear classification (circles, spirals)
- Hyperparameter exploration

```bash
python example_02_multilayer_network.py
```

### Example 3: MNIST Classifier
**File**: `example_03_mnist_classifier.py`

The "Hello World" of deep learning:
- Download and preprocess MNIST
- Build 784 -> 128 -> 64 -> 10 network
- Train on 60,000 handwritten digits
- Achieve >95% accuracy
- Visualize learned features

```bash
python example_03_mnist_classifier.py
```

## Main Deliverable: Neural Network Toolkit

**File**: `deliverable_neural_network_from_scratch.py`

A complete, production-quality neural network implementation:

### Features
- Configurable architecture (any number of layers)
- Multiple activation functions (ReLU, Sigmoid, Tanh, Leaky ReLU)
- Multiple optimizers (SGD, Momentum, Adam)
- Mini-batch training
- Model save/load functionality
- Training visualization

### Quick Start

```bash
# XOR problem
python deliverable_neural_network_from_scratch.py demo1

# Spiral classification
python deliverable_neural_network_from_scratch.py demo2

# MNIST training
python deliverable_neural_network_from_scratch.py demo3

# Activation comparison
python deliverable_neural_network_from_scratch.py demo4

# Optimizer comparison
python deliverable_neural_network_from_scratch.py demo5
```

### Usage in Code

```python
from deliverable_neural_network_from_scratch import (
    NeuralNetwork, NetworkArchitecture, TrainingConfig
)

# Define architecture
arch = NetworkArchitecture(
    layer_dims=[784, 128, 64, 10],
    activation='relu',
    output_activation='softmax'
)

# Create network
nn = NeuralNetwork(arch)

# Configure training
config = TrainingConfig(
    learning_rate=0.01,
    epochs=100,
    batch_size=64,
    optimizer='adam'
)

# Train
history = nn.train(X_train, Y_train, X_val, Y_val, config=config)

# Predict
predictions = nn.predict(X_test)

# Save/Load
nn.save('model.json')
nn = NeuralNetwork.load('model.json')
```

## Key Concepts

### Forward Propagation
```
Input -> [Linear] -> [Activation] -> ... -> Output

Z[l] = W[l] @ A[l-1] + b[l]
A[l] = activation(Z[l])
```

### Backpropagation
```
Output Gradient -> [Activation Derivative] -> [Weight Gradient] -> ... -> Input

dZ[L] = A[L] - Y  (for softmax + cross-entropy)
dW[l] = (1/m) * dZ[l] @ A[l-1].T
db[l] = (1/m) * sum(dZ[l])
dA[l-1] = W[l].T @ dZ[l]
```

### Gradient Descent
```
θ_new = θ_old - learning_rate * gradient
```

## Generated Outputs

```
.neural_network/
├── models/
│   └── mnist_model.json
└── plots/
    ├── spiral_classification.png
    ├── mnist_training.png
    ├── activation_comparison.png
    └── optimizer_comparison.png
```

## Performance Benchmarks

| Dataset | Architecture | Accuracy | Training Time |
|---------|--------------|----------|---------------|
| XOR | 2-8-1 | 100% | <1s |
| Spiral (3 class) | 2-100-50-3 | ~95% | ~5s |
| MNIST (10k) | 784-128-64-10 | ~95% | ~30s |

## Further Reading

- [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/) - Michael Nielsen
- [Deep Learning Book](https://www.deeplearningbook.org/) - Goodfellow et al.
- [3Blue1Brown Neural Networks](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi)
