#!/usr/bin/env python3
"""
Module 26 Deliverable: Neural Network from Scratch

A complete neural network implementation using only NumPy.
No PyTorch, no TensorFlow - just pure mathematics.

Features:
- Configurable architecture (any number of layers)
- Multiple activation functions (ReLU, Sigmoid, Tanh, Leaky ReLU)
- Multiple optimizers (SGD, Momentum, Adam)
- Mini-batch training
- Model save/load functionality
- Training visualization
- MNIST benchmark

Usage:
    python deliverable_neural_network_from_scratch.py demo1    # XOR problem
    python deliverable_neural_network_from_scratch.py demo2    # Spiral classification
    python deliverable_neural_network_from_scratch.py demo3    # MNIST training
    python deliverable_neural_network_from_scratch.py demo4    # Activation comparison
    python deliverable_neural_network_from_scratch.py demo5    # Optimizer comparison
    python deliverable_neural_network_from_scratch.py help     # Show help
"""

import json
import sys
import time
import gzip
import os
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
np.seterr(all='ignore')  # Suppress numpy warnings for cleaner output
import matplotlib.pyplot as plt

# Storage directory
STORAGE_DIR = Path(__file__).parent / ".neural_network"
STORAGE_DIR.mkdir(exist_ok=True)
MODELS_DIR = STORAGE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
PLOTS_DIR = STORAGE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TrainingConfig:
    """Configuration for neural network training."""
    learning_rate: float = 0.01
    epochs: int = 100
    batch_size: int = 32
    optimizer: str = 'sgd'  # sgd, momentum, adam
    momentum: float = 0.9
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    weight_decay: float = 0.0
    early_stopping: bool = False
    patience: int = 10


@dataclass
class TrainingHistory:
    """Training history and metrics."""
    train_losses: List[float] = field(default_factory=list)
    train_accuracies: List[float] = field(default_factory=list)
    val_losses: List[float] = field(default_factory=list)
    val_accuracies: List[float] = field(default_factory=list)
    training_time: float = 0.0
    epochs_trained: int = 0
    final_train_accuracy: float = 0.0
    final_val_accuracy: float = 0.0


@dataclass
class NetworkArchitecture:
    """Neural network architecture specification."""
    layer_dims: List[int]
    activation: str = 'relu'
    output_activation: str = 'softmax'
    weight_init: str = 'he'


# =============================================================================
# Activation Functions
# =============================================================================

class Activations:
    """Collection of activation functions and their derivatives."""

    @staticmethod
    def relu(z: np.ndarray) -> np.ndarray:
        return np.maximum(0, z)

    @staticmethod
    def relu_derivative(z: np.ndarray) -> np.ndarray:
        return (z > 0).astype(float)

    @staticmethod
    def leaky_relu(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
        return np.where(z > 0, z, alpha * z)

    @staticmethod
    def leaky_relu_derivative(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
        return np.where(z > 0, 1, alpha)

    @staticmethod
    def sigmoid(z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))

    @staticmethod
    def sigmoid_derivative(z: np.ndarray) -> np.ndarray:
        s = Activations.sigmoid(z)
        return s * (1 - s)

    @staticmethod
    def tanh(z: np.ndarray) -> np.ndarray:
        return np.tanh(z)

    @staticmethod
    def tanh_derivative(z: np.ndarray) -> np.ndarray:
        return 1 - np.tanh(z) ** 2

    @staticmethod
    def softmax(z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -500, 500)  # Prevent overflow
        exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
        result = exp_z / (np.sum(exp_z, axis=0, keepdims=True) + 1e-15)
        return np.nan_to_num(result, nan=1.0/z.shape[0])

    @staticmethod
    def linear(z: np.ndarray) -> np.ndarray:
        return z

    @staticmethod
    def linear_derivative(z: np.ndarray) -> np.ndarray:
        return np.ones_like(z)

    @classmethod
    def get_activation(cls, name: str) -> Tuple[Callable, Callable]:
        """Get activation function and its derivative by name."""
        activations = {
            'relu': (cls.relu, cls.relu_derivative),
            'leaky_relu': (cls.leaky_relu, cls.leaky_relu_derivative),
            'sigmoid': (cls.sigmoid, cls.sigmoid_derivative),
            'tanh': (cls.tanh, cls.tanh_derivative),
            'softmax': (cls.softmax, None),
            'linear': (cls.linear, cls.linear_derivative),
        }
        if name not in activations:
            raise ValueError(f"Unknown activation: {name}")
        return activations[name]


# =============================================================================
# Loss Functions
# =============================================================================

class Losses:
    """Collection of loss functions."""

    @staticmethod
    def cross_entropy(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """Categorical cross-entropy loss."""
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        return -np.mean(np.sum(y_true * np.log(y_pred), axis=0))

    @staticmethod
    def binary_cross_entropy(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """Binary cross-entropy loss."""
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

    @staticmethod
    def mse(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """Mean squared error loss."""
        return np.mean((y_pred - y_true) ** 2)


# =============================================================================
# Neural Network Implementation
# =============================================================================

class NeuralNetwork:
    """
    A fully-connected neural network built from scratch.

    This implementation supports:
    - Arbitrary architecture
    - Multiple activation functions
    - Multiple optimizers (SGD, Momentum, Adam)
    - Mini-batch training
    - Model persistence
    """

    def __init__(self, architecture: NetworkArchitecture):
        """
        Initialize the neural network.

        Args:
            architecture: Network architecture specification
        """
        self.architecture = architecture
        self.layer_dims = architecture.layer_dims
        self.L = len(self.layer_dims) - 1
        self.parameters: Dict[str, np.ndarray] = {}
        self.velocity: Dict[str, np.ndarray] = {}  # For momentum
        self.cache_m: Dict[str, np.ndarray] = {}   # For Adam
        self.cache_v: Dict[str, np.ndarray] = {}   # For Adam
        self.t = 0  # Time step for Adam

        # Get activation functions
        self.act_fn, self.act_derivative = Activations.get_activation(architecture.activation)
        self.output_act_fn, _ = Activations.get_activation(architecture.output_activation)

        # Initialize weights
        self._initialize_parameters(architecture.weight_init)

    def _initialize_parameters(self, method: str = 'he'):
        """
        Initialize network parameters.

        Args:
            method: 'he', 'xavier', or 'random'
        """
        np.random.seed(42)

        for l in range(1, self.L + 1):
            n_in = self.layer_dims[l - 1]
            n_out = self.layer_dims[l]

            if method == 'he':
                scale = np.sqrt(2 / n_in)
            elif method == 'xavier':
                scale = np.sqrt(1 / n_in)
            else:
                scale = 0.01

            self.parameters[f'W{l}'] = np.random.randn(n_out, n_in) * scale
            self.parameters[f'b{l}'] = np.zeros((n_out, 1))

            # Initialize optimizer caches
            self.velocity[f'W{l}'] = np.zeros_like(self.parameters[f'W{l}'])
            self.velocity[f'b{l}'] = np.zeros_like(self.parameters[f'b{l}'])
            self.cache_m[f'W{l}'] = np.zeros_like(self.parameters[f'W{l}'])
            self.cache_m[f'b{l}'] = np.zeros_like(self.parameters[f'b{l}'])
            self.cache_v[f'W{l}'] = np.zeros_like(self.parameters[f'W{l}'])
            self.cache_v[f'b{l}'] = np.zeros_like(self.parameters[f'b{l}'])

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Forward propagation."""
        caches = {'A0': X}
        A = X

        # Hidden layers
        for l in range(1, self.L):
            W = self.parameters[f'W{l}']
            b = self.parameters[f'b{l}']

            Z = W @ A + b
            Z = np.nan_to_num(Z, nan=0.0, posinf=500, neginf=-500)
            A = self.act_fn(Z)
            A = np.nan_to_num(A, nan=0.0)

            caches[f'Z{l}'] = Z
            caches[f'A{l}'] = A

        # Output layer
        W = self.parameters[f'W{self.L}']
        b = self.parameters[f'b{self.L}']
        Z = W @ A + b
        Z = np.nan_to_num(Z, nan=0.0, posinf=500, neginf=-500)
        AL = self.output_act_fn(Z)

        caches[f'Z{self.L}'] = Z

        return AL, caches

    def backward(self, AL: np.ndarray, Y: np.ndarray, caches: Dict) -> Dict:
        """Backward propagation."""
        gradients = {}
        m = Y.shape[1]

        # Output layer
        if self.architecture.output_activation == 'softmax':
            dZ = AL - Y
        else:
            dZ = AL - Y  # Simplified for sigmoid/softmax + cross-entropy

        A_prev = caches[f'A{self.L - 1}']
        gradients[f'dW{self.L}'] = (1/m) * dZ @ A_prev.T
        gradients[f'db{self.L}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)
        dA_prev = self.parameters[f'W{self.L}'].T @ dZ

        # Hidden layers
        for l in reversed(range(1, self.L)):
            Z = caches[f'Z{l}']
            dZ = dA_prev * self.act_derivative(Z)

            A_prev = caches[f'A{l - 1}']
            gradients[f'dW{l}'] = (1/m) * dZ @ A_prev.T
            gradients[f'db{l}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)

            if l > 1:
                dA_prev = self.parameters[f'W{l}'].T @ dZ

        return gradients

    def update_parameters(self, gradients: Dict, config: TrainingConfig):
        """Update parameters using specified optimizer."""
        if config.optimizer == 'sgd':
            self._sgd_update(gradients, config.learning_rate, config.weight_decay)
        elif config.optimizer == 'momentum':
            self._momentum_update(gradients, config.learning_rate, config.momentum, config.weight_decay)
        elif config.optimizer == 'adam':
            self._adam_update(gradients, config)

    def _sgd_update(self, gradients: Dict, lr: float, weight_decay: float):
        """Vanilla SGD update."""
        for l in range(1, self.L + 1):
            self.parameters[f'W{l}'] -= lr * (gradients[f'dW{l}'] + weight_decay * self.parameters[f'W{l}'])
            self.parameters[f'b{l}'] -= lr * gradients[f'db{l}']

    def _momentum_update(self, gradients: Dict, lr: float, momentum: float, weight_decay: float):
        """SGD with momentum update."""
        for l in range(1, self.L + 1):
            self.velocity[f'W{l}'] = momentum * self.velocity[f'W{l}'] - lr * gradients[f'dW{l}']
            self.velocity[f'b{l}'] = momentum * self.velocity[f'b{l}'] - lr * gradients[f'db{l}']

            self.parameters[f'W{l}'] += self.velocity[f'W{l}'] - lr * weight_decay * self.parameters[f'W{l}']
            self.parameters[f'b{l}'] += self.velocity[f'b{l}']

    def _adam_update(self, gradients: Dict, config: TrainingConfig):
        """Adam optimizer update."""
        self.t += 1

        for l in range(1, self.L + 1):
            for param in ['W', 'b']:
                key = f'{param}{l}'
                g = gradients[f'd{key}']

                # Update biased first moment
                self.cache_m[key] = config.beta1 * self.cache_m[key] + (1 - config.beta1) * g
                # Update biased second moment
                self.cache_v[key] = config.beta2 * self.cache_v[key] + (1 - config.beta2) * (g ** 2)

                # Bias correction
                m_corrected = self.cache_m[key] / (1 - config.beta1 ** self.t)
                v_corrected = self.cache_v[key] / (1 - config.beta2 ** self.t)

                # Update parameters
                self.parameters[key] -= config.learning_rate * m_corrected / (np.sqrt(v_corrected) + config.epsilon)

    def compute_loss(self, AL: np.ndarray, Y: np.ndarray) -> float:
        """Compute loss based on output activation."""
        if self.architecture.output_activation in ['softmax']:
            return Losses.cross_entropy(AL, Y)
        else:
            return Losses.binary_cross_entropy(AL, Y)

    def train(self, X_train: np.ndarray, Y_train: np.ndarray,
              X_val: np.ndarray = None, Y_val: np.ndarray = None,
              config: TrainingConfig = None, verbose: bool = True) -> TrainingHistory:
        """
        Train the neural network.

        Args:
            X_train: Training data (n_features, n_samples)
            Y_train: Training labels
            X_val: Validation data (optional)
            Y_val: Validation labels (optional)
            config: Training configuration
            verbose: Print progress

        Returns:
            Training history
        """
        config = config or TrainingConfig()
        history = TrainingHistory()
        m = X_train.shape[1]
        best_val_loss = float('inf')
        patience_counter = 0

        start_time = time.time()

        for epoch in range(config.epochs):
            # Shuffle data
            permutation = np.random.permutation(m)
            X_shuffled = X_train[:, permutation]
            Y_shuffled = Y_train[:, permutation]

            epoch_loss = 0

            # Mini-batch training
            for i in range(0, m, config.batch_size):
                X_batch = X_shuffled[:, i:i + config.batch_size]
                Y_batch = Y_shuffled[:, i:i + config.batch_size]

                # Forward
                AL, caches = self.forward(X_batch)

                # Compute loss
                batch_loss = self.compute_loss(AL, Y_batch)
                epoch_loss += batch_loss * X_batch.shape[1]

                # Backward
                gradients = self.backward(AL, Y_batch, caches)

                # Update
                self.update_parameters(gradients, config)

            epoch_loss /= m
            history.train_losses.append(epoch_loss)

            # Training accuracy
            train_pred = self.predict(X_train)
            train_acc = np.mean(train_pred == np.argmax(Y_train, axis=0))
            history.train_accuracies.append(train_acc)

            # Validation metrics
            if X_val is not None:
                AL_val, _ = self.forward(X_val)
                val_loss = self.compute_loss(AL_val, Y_val)
                val_pred = self.predict(X_val)
                val_acc = np.mean(val_pred == np.argmax(Y_val, axis=0))

                history.val_losses.append(val_loss)
                history.val_accuracies.append(val_acc)

                # Early stopping
                if config.early_stopping:
                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        patience_counter = 0
                    else:
                        patience_counter += 1
                        if patience_counter >= config.patience:
                            if verbose:
                                print(f"  Early stopping at epoch {epoch + 1}")
                            break

            # Print progress
            if verbose and (epoch + 1) % max(1, config.epochs // 10) == 0:
                val_str = f", val_acc: {val_acc:.4f}" if X_val is not None else ""
                print(f"  Epoch {epoch + 1:4d}: loss = {epoch_loss:.4f}, "
                      f"train_acc = {train_acc:.4f}{val_str}")

        history.training_time = time.time() - start_time
        history.epochs_trained = epoch + 1
        history.final_train_accuracy = history.train_accuracies[-1]
        if history.val_accuracies:
            history.final_val_accuracy = history.val_accuracies[-1]

        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        AL, _ = self.forward(X)
        if AL.shape[0] == 1:
            return (AL > 0.5).astype(int).flatten()
        return np.argmax(AL, axis=0)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return probability predictions."""
        AL, _ = self.forward(X)
        return AL

    def save(self, filepath: str):
        """Save model to file."""
        model_data = {
            'architecture': asdict(self.architecture),
            'parameters': {k: v.tolist() for k, v in self.parameters.items()},
        }
        with open(filepath, 'w') as f:
            json.dump(model_data, f)

    @classmethod
    def load(cls, filepath: str) -> 'NeuralNetwork':
        """Load model from file."""
        with open(filepath, 'r') as f:
            model_data = json.load(f)

        arch = NetworkArchitecture(**model_data['architecture'])
        nn = cls(arch)
        nn.parameters = {k: np.array(v) for k, v in model_data['parameters'].items()}
        return nn

    def summary(self) -> str:
        """Return model summary."""
        total_params = sum(
            self.parameters[f'W{l}'].size + self.parameters[f'b{l}'].size
            for l in range(1, self.L + 1)
        )

        lines = [
            "="*50,
            "Neural Network Summary",
            "="*50,
            f"Architecture: {self.layer_dims}",
            f"Hidden activation: {self.architecture.activation}",
            f"Output activation: {self.architecture.output_activation}",
            f"Total parameters: {total_params:,}",
            "-"*50,
        ]

        for l in range(1, self.L + 1):
            W_shape = self.parameters[f'W{l}'].shape
            b_shape = self.parameters[f'b{l}'].shape
            params = W_shape[0] * W_shape[1] + b_shape[0]
            lines.append(f"Layer {l}: {W_shape[1]} -> {W_shape[0]} ({params:,} params)")

        lines.append("="*50)
        return "\n".join(lines)


# =============================================================================
# Data Utilities
# =============================================================================

def download_mnist(data_dir: str = './mnist_data'):
    """Download MNIST dataset."""
    base_url = 'http://yann.lecun.com/exdb/mnist/'
    files = [
        'train-images-idx3-ubyte.gz',
        'train-labels-idx1-ubyte.gz',
        't10k-images-idx3-ubyte.gz',
        't10k-labels-idx1-ubyte.gz'
    ]

    os.makedirs(data_dir, exist_ok=True)

    for filename in files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"    Downloading {filename}...")
            urllib.request.urlretrieve(base_url + filename, filepath)


def load_mnist(data_dir: str = './mnist_data'):
    """Load MNIST dataset."""
    def load_images(filename):
        with gzip.open(filename, 'rb') as f:
            data = np.frombuffer(f.read(), np.uint8, offset=16)
        return data.reshape(-1, 784).astype(np.float32) / 255.0

    def load_labels(filename):
        with gzip.open(filename, 'rb') as f:
            return np.frombuffer(f.read(), np.uint8, offset=8)

    X_train = load_images(os.path.join(data_dir, 'train-images-idx3-ubyte.gz'))
    y_train = load_labels(os.path.join(data_dir, 'train-labels-idx1-ubyte.gz'))
    X_test = load_images(os.path.join(data_dir, 't10k-images-idx3-ubyte.gz'))
    y_test = load_labels(os.path.join(data_dir, 't10k-labels-idx1-ubyte.gz'))

    return X_train.T, y_train, X_test.T, y_test


def one_hot_encode(y: np.ndarray, num_classes: int = 10) -> np.ndarray:
    """Convert labels to one-hot encoding."""
    one_hot = np.zeros((num_classes, len(y)))
    one_hot[y, np.arange(len(y))] = 1
    return one_hot


def generate_spiral_data(n_samples: int = 100, n_classes: int = 3):
    """Generate spiral classification data."""
    np.random.seed(42)
    X = np.zeros((2, n_samples * n_classes))
    y = np.zeros(n_samples * n_classes, dtype=int)

    for j in range(n_classes):
        ix = range(n_samples * j, n_samples * (j + 1))
        r = np.linspace(0.0, 1, n_samples)
        t = np.linspace(j * 4, (j + 1) * 4, n_samples) + np.random.randn(n_samples) * 0.2
        X[0, ix] = r * np.sin(t)
        X[1, ix] = r * np.cos(t)
        y[ix] = j

    return X, one_hot_encode(y, n_classes), y


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_xor():
    """Demo 1: Solve XOR problem."""
    print("\n" + "="*70)
    print(" DEMO 1: XOR PROBLEM")
    print("="*70)

    X = np.array([[0, 0, 1, 1], [0, 1, 0, 1]])
    Y = np.array([[0, 1, 1, 0]])

    print("\n  XOR Truth Table:")
    for i in range(4):
        print(f"    {X[0,i]} XOR {X[1,i]} = {Y[0,i]}")

    arch = NetworkArchitecture([2, 8, 1], activation='tanh', output_activation='sigmoid')
    nn = NeuralNetwork(arch)

    print(f"\n  {nn.summary()}")

    config = TrainingConfig(learning_rate=0.5, epochs=5000, batch_size=4)
    history = nn.train(X, Y, config=config, verbose=True)

    predictions = nn.predict(X)
    probs = nn.predict_proba(X)

    print("\n  Results:")
    for i in range(4):
        print(f"    [{X[0,i]}, {X[1,i]}] -> {probs[0,i]:.4f} (predicted: {predictions[i]})")

    print(f"\n  Accuracy: {np.mean(predictions == Y.flatten()) * 100:.0f}%")


def demo_2_spiral():
    """Demo 2: Spiral classification."""
    print("\n" + "="*70)
    print(" DEMO 2: SPIRAL CLASSIFICATION")
    print("="*70)

    X, Y, y = generate_spiral_data(n_samples=100, n_classes=3)
    print(f"\n  Generated spiral data: {X.shape[1]} samples, 3 classes")

    # Use tanh for better numerical stability in this demo
    arch = NetworkArchitecture([2, 64, 32, 3], activation='tanh', output_activation='softmax')
    nn = NeuralNetwork(arch)

    print(f"\n  {nn.summary()}")

    config = TrainingConfig(
        learning_rate=0.5,
        epochs=200,
        batch_size=32,
        optimizer='sgd'  # SGD is more stable for this small example
    )

    print("\n  Training with SGD optimizer...")
    history = nn.train(X, Y, config=config, verbose=True)

    predictions = nn.predict(X)
    accuracy = np.mean(predictions == y)
    print(f"\n  Final Accuracy: {accuracy * 100:.1f}%")

    # Visualize
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Data and boundary
    x_min, x_max = X[0].min() - 0.5, X[0].max() + 0.5
    y_min, y_max = X[1].min() - 0.5, X[1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
    mesh_input = np.array([xx.ravel(), yy.ravel()])
    Z = nn.predict(mesh_input).reshape(xx.shape)

    axes[0].contourf(xx, yy, Z, alpha=0.3, cmap='Set1')
    axes[0].scatter(X[0], X[1], c=y, cmap='Set1', edgecolors='black', s=40)
    axes[0].set_title('Learned Decision Boundary')

    axes[1].plot(history.train_losses)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].set_title('Training Loss')
    axes[1].grid(True, alpha=0.3)

    plt.suptitle('Spiral Classification', fontsize=14)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'spiral_classification.png', dpi=150)
    plt.close()
    print(f"\n  Saved: {PLOTS_DIR}/spiral_classification.png")


def demo_3_mnist():
    """Demo 3: MNIST classification."""
    print("\n" + "="*70)
    print(" DEMO 3: MNIST CLASSIFICATION")
    print("="*70)

    print("\n  Loading MNIST...")
    download_mnist()
    X_train, y_train, X_test, y_test = load_mnist()

    # Use subset for faster demo
    n_train = 10000
    X_train = X_train[:, :n_train]
    y_train = y_train[:n_train]
    Y_train = one_hot_encode(y_train)
    Y_test = one_hot_encode(y_test)

    print(f"  Training: {X_train.shape[1]} samples")
    print(f"  Test: {X_test.shape[1]} samples")

    arch = NetworkArchitecture([784, 128, 64, 10], activation='relu', output_activation='softmax')
    nn = NeuralNetwork(arch)

    print(f"\n  {nn.summary()}")

    config = TrainingConfig(
        learning_rate=0.01,
        epochs=20,
        batch_size=64,
        optimizer='adam'
    )

    print("\n  Training...")
    history = nn.train(X_train, Y_train, X_test, Y_test, config=config, verbose=True)

    test_pred = nn.predict(X_test)
    test_accuracy = np.mean(test_pred == y_test)
    print(f"\n  Test Accuracy: {test_accuracy * 100:.2f}%")
    print(f"  Training Time: {history.training_time:.1f}s")

    # Save model
    model_path = MODELS_DIR / 'mnist_model.json'
    nn.save(str(model_path))
    print(f"  Model saved: {model_path}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history.train_losses, label='Train')
    axes[0].plot(history.val_losses, label='Validation')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(history.train_accuracies, label='Train')
    axes[1].plot(history.val_accuracies, label='Validation')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle(f'MNIST Training (Test Acc: {test_accuracy*100:.1f}%)', fontsize=14)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'mnist_training.png', dpi=150)
    plt.close()
    print(f"  Saved: {PLOTS_DIR}/mnist_training.png")


def demo_4_activations():
    """Demo 4: Compare activation functions."""
    print("\n" + "="*70)
    print(" DEMO 4: ACTIVATION FUNCTION COMPARISON")
    print("="*70)

    X, Y, y = generate_spiral_data(n_samples=100, n_classes=3)
    activations = ['relu', 'sigmoid', 'tanh', 'leaky_relu']

    results = {}

    for act in activations:
        print(f"\n  Testing {act}...")
        arch = NetworkArchitecture([2, 50, 50, 3], activation=act, output_activation='softmax')
        nn = NeuralNetwork(arch)

        config = TrainingConfig(learning_rate=0.1, epochs=100, batch_size=32, optimizer='adam')
        history = nn.train(X, Y, config=config, verbose=False)

        predictions = nn.predict(X)
        accuracy = np.mean(predictions == y)
        results[act] = {'accuracy': accuracy, 'losses': history.train_losses}
        print(f"    Accuracy: {accuracy * 100:.1f}%")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for act, data in results.items():
        axes[0].plot(data['losses'], label=act)

    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss by Activation')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    accuracies = [data['accuracy'] for data in results.values()]
    bars = axes[1].bar(activations, accuracies)
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Final Accuracy by Activation')
    axes[1].set_ylim(0, 1)

    for bar, acc in zip(bars, accuracies):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{acc:.1%}', ha='center', va='bottom')

    plt.suptitle('Activation Function Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'activation_comparison.png', dpi=150)
    plt.close()
    print(f"\n  Saved: {PLOTS_DIR}/activation_comparison.png")


def demo_5_optimizers():
    """Demo 5: Compare optimizers."""
    print("\n" + "="*70)
    print(" DEMO 5: OPTIMIZER COMPARISON")
    print("="*70)

    X, Y, y = generate_spiral_data(n_samples=100, n_classes=3)
    optimizers = ['sgd', 'momentum', 'adam']

    results = {}

    for opt in optimizers:
        print(f"\n  Testing {opt}...")
        arch = NetworkArchitecture([2, 50, 50, 3], activation='relu', output_activation='softmax')
        nn = NeuralNetwork(arch)

        lr = 0.1 if opt == 'adam' else 0.5
        config = TrainingConfig(learning_rate=lr, epochs=100, batch_size=32, optimizer=opt)
        history = nn.train(X, Y, config=config, verbose=False)

        predictions = nn.predict(X)
        accuracy = np.mean(predictions == y)
        results[opt] = {'accuracy': accuracy, 'losses': history.train_losses}
        print(f"    Accuracy: {accuracy * 100:.1f}%")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for opt, data in results.items():
        axes[0].plot(data['losses'], label=opt)

    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss by Optimizer')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    accuracies = [data['accuracy'] for data in results.values()]
    bars = axes[1].bar(optimizers, accuracies)
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Final Accuracy by Optimizer')
    axes[1].set_ylim(0, 1)

    for bar, acc in zip(bars, accuracies):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{acc:.1%}', ha='center', va='bottom')

    plt.suptitle('Optimizer Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'optimizer_comparison.png', dpi=150)
    plt.close()
    print(f"\n  Saved: {PLOTS_DIR}/optimizer_comparison.png")


def show_help():
    """Show help information."""
    print("""
Neural Network from Scratch - Module 26 Deliverable
====================================================

A complete neural network implementation using only NumPy.

Usage:
    python deliverable_neural_network_from_scratch.py <command>

Commands:
    demo1    - XOR problem (simple binary classification)
    demo2    - Spiral classification (multi-class)
    demo3    - MNIST digit classification
    demo4    - Compare activation functions
    demo5    - Compare optimizers
    help     - Show this help message

Features:
    - Configurable architecture (any number of layers)
    - Activation functions: ReLU, Sigmoid, Tanh, Leaky ReLU
    - Output activations: Softmax, Sigmoid
    - Optimizers: SGD, Momentum, Adam
    - Mini-batch training
    - Model save/load
    - Training visualization

Example Usage in Code:
    from deliverable_neural_network_from_scratch import NeuralNetwork, NetworkArchitecture

    arch = NetworkArchitecture([784, 128, 64, 10], activation='relu')
    nn = NeuralNetwork(arch)

    config = TrainingConfig(learning_rate=0.01, epochs=100, optimizer='adam')
    history = nn.train(X_train, Y_train, X_val, Y_val, config=config)

    predictions = nn.predict(X_test)

Output:
    - Models saved to: .neural_network/models/
    - Plots saved to: .neural_network/plots/
    """)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_xor()
    elif command == "demo2":
        demo_2_spiral()
    elif command == "demo3":
        demo_3_mnist()
    elif command == "demo4":
        demo_4_activations()
    elif command == "demo5":
        demo_5_optimizers()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands.")
        sys.exit(1)

    print("\n" + "="*70)
    print(" DEMO COMPLETE")
    print("="*70)
