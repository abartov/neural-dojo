# Module 26 Deliverable: Neural Network from Scratch

**Build and train neural networks using only NumPy - no frameworks, just mathematics.**

## Features

- **Configurable Architecture**: Any number of layers, any size
- **Multiple Activations**: ReLU, Sigmoid, Tanh, Leaky ReLU, Softmax
- **Multiple Optimizers**: SGD, Momentum, Adam
- **Mini-batch Training**: Efficient gradient computation
- **Model Persistence**: Save and load trained models
- **Training Visualization**: Loss curves, accuracy plots

## Quick Start

```bash
python deliverable_neural_network_from_scratch.py demo1  # XOR
python deliverable_neural_network_from_scratch.py demo2  # Spiral
python deliverable_neural_network_from_scratch.py demo3  # MNIST
python deliverable_neural_network_from_scratch.py demo4  # Activations
python deliverable_neural_network_from_scratch.py demo5  # Optimizers
```

## Architecture

### NetworkArchitecture
```python
arch = NetworkArchitecture(
    layer_dims=[784, 128, 64, 10],  # Input -> Hidden -> Output
    activation='relu',               # Hidden layer activation
    output_activation='softmax',     # Output activation
    weight_init='he'                 # Weight initialization
)
```

### TrainingConfig
```python
config = TrainingConfig(
    learning_rate=0.01,
    epochs=100,
    batch_size=64,
    optimizer='adam',      # 'sgd', 'momentum', 'adam'
    momentum=0.9,          # For momentum optimizer
    early_stopping=True,   # Stop if validation loss increases
    patience=10            # Epochs to wait before stopping
)
```

## Usage Example

```python
from deliverable_neural_network_from_scratch import (
    NeuralNetwork, NetworkArchitecture, TrainingConfig,
    load_mnist, one_hot_encode
)

# Load data
X_train, y_train, X_test, y_test = load_mnist()
Y_train = one_hot_encode(y_train)
Y_test = one_hot_encode(y_test)

# Create network
arch = NetworkArchitecture([784, 128, 64, 10])
nn = NeuralNetwork(arch)

# Print summary
print(nn.summary())

# Train
config = TrainingConfig(learning_rate=0.01, epochs=50, optimizer='adam')
history = nn.train(X_train, Y_train, X_test, Y_test, config=config)

# Evaluate
predictions = nn.predict(X_test)
accuracy = (predictions == y_test).mean()
print(f"Test Accuracy: {accuracy:.2%}")

# Save model
nn.save('my_model.json')

# Load model
nn_loaded = NeuralNetwork.load('my_model.json')
```

## How It Works

### Forward Propagation
Each layer computes:
1. **Linear**: `Z = W @ A_prev + b`
2. **Activation**: `A = activation(Z)`

### Backpropagation
Gradients flow backward using the chain rule:
1. **Output**: `dZ = A - Y` (for softmax + cross-entropy)
2. **Hidden**: `dZ = dA * activation'(Z)`
3. **Weights**: `dW = (1/m) * dZ @ A_prev.T`
4. **Bias**: `db = (1/m) * sum(dZ)`

### Optimizers

**SGD**:
```
W = W - lr * dW
```

**Momentum**:
```
v = momentum * v - lr * dW
W = W + v
```

**Adam**:
```
m = beta1 * m + (1 - beta1) * dW
v = beta2 * v + (1 - beta2) * dW^2
m_hat = m / (1 - beta1^t)
v_hat = v / (1 - beta2^t)
W = W - lr * m_hat / (sqrt(v_hat) + eps)
```

## Results

### Demo 1: XOR
- Architecture: 2 -> 8 -> 1
- Accuracy: 100%
- Shows that multi-layer networks can learn non-linear functions

### Demo 2: Spiral
- Architecture: 2 -> 100 -> 50 -> 3
- Accuracy: ~95%
- Demonstrates complex decision boundary learning

### Demo 3: MNIST
- Architecture: 784 -> 128 -> 64 -> 10
- Test Accuracy: ~95%
- Real-world digit classification

### Demo 4: Activation Comparison
- Compares ReLU, Sigmoid, Tanh, Leaky ReLU
- ReLU typically performs best for deep networks

### Demo 5: Optimizer Comparison
- Compares SGD, Momentum, Adam
- Adam typically converges fastest

## Output Files

```
.neural_network/
├── models/
│   └── mnist_model.json      # Saved model weights
└── plots/
    ├── spiral_classification.png
    ├── mnist_training.png
    ├── activation_comparison.png
    └── optimizer_comparison.png
```

## Key Insights

1. **Neural networks are just functions**: Parameterized by weights and biases
2. **Backpropagation is just the chain rule**: Applied systematically
3. **Gradient descent finds good parameters**: By following the slope downhill
4. **Non-linearity is essential**: Without it, deep networks collapse to linear
5. **Initialization matters**: He/Xavier initialization prevents vanishing gradients

## Why Build from Scratch?

- **Understanding**: Know what PyTorch/TensorFlow do under the hood
- **Debugging**: Recognize when something goes wrong
- **Appreciation**: See why frameworks are valuable
- **Foundation**: Essential knowledge for advanced topics

**Time**: ~7 hours | **Lines**: 800+ | **Author**: Neural Dojo
