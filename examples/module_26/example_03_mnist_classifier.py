#!/usr/bin/env python3
"""
Module 26 Example 3: MNIST Classifier

The "Hello World" of deep learning - classifying handwritten digits.

This example:
1. Loads and preprocesses MNIST data
2. Builds a neural network from scratch
3. Trains on 60,000 images
4. Achieves >95% accuracy on test set
5. Visualizes results and learned features
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from pathlib import Path
import gzip
import urllib.request
import os


# =============================================================================
# Data Loading (MNIST)
# =============================================================================

def download_mnist(data_dir: str = './mnist_data'):
    """
    Download MNIST dataset if not already present.

    MNIST files:
    - train-images-idx3-ubyte.gz: Training images
    - train-labels-idx1-ubyte.gz: Training labels
    - t10k-images-idx3-ubyte.gz: Test images
    - t10k-labels-idx1-ubyte.gz: Test labels
    """
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
            print(f"  Downloading {filename}...")
            urllib.request.urlretrieve(base_url + filename, filepath)

    print("  MNIST data ready!")


def load_mnist(data_dir: str = './mnist_data') -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load MNIST dataset.

    Returns:
        X_train: Training images (60000, 784)
        y_train: Training labels (60000,)
        X_test: Test images (10000, 784)
        y_test: Test labels (10000,)
    """
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

    return X_train, y_train, X_test, y_test


def one_hot_encode(y: np.ndarray, num_classes: int = 10) -> np.ndarray:
    """Convert labels to one-hot encoding."""
    one_hot = np.zeros((num_classes, len(y)))
    one_hot[y, np.arange(len(y))] = 1
    return one_hot


# =============================================================================
# Activation Functions
# =============================================================================

def relu(z: np.ndarray) -> np.ndarray:
    """ReLU activation."""
    return np.maximum(0, z)


def relu_derivative(z: np.ndarray) -> np.ndarray:
    """Derivative of ReLU."""
    return (z > 0).astype(float)


def softmax(z: np.ndarray) -> np.ndarray:
    """
    Softmax activation for multi-class classification.
    Converts logits to probabilities that sum to 1.
    """
    exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
    return exp_z / np.sum(exp_z, axis=0, keepdims=True)


# =============================================================================
# Neural Network for MNIST
# =============================================================================

class MNISTClassifier:
    """
    A neural network for MNIST digit classification.

    Architecture: 784 -> hidden -> ... -> 10 (softmax)
    """

    def __init__(self, layer_dims: List[int]):
        """
        Initialize the network.

        Args:
            layer_dims: Layer sizes, e.g., [784, 128, 64, 10]
        """
        self.layer_dims = layer_dims
        self.L = len(layer_dims) - 1
        self.parameters: Dict[str, np.ndarray] = {}
        self.costs: List[float] = []

        self._initialize_parameters()

    def _initialize_parameters(self):
        """He initialization for weights."""
        np.random.seed(42)

        for l in range(1, self.L + 1):
            n_in = self.layer_dims[l - 1]
            n_out = self.layer_dims[l]

            self.parameters[f'W{l}'] = np.random.randn(n_out, n_in) * np.sqrt(2 / n_in)
            self.parameters[f'b{l}'] = np.zeros((n_out, 1))

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Forward propagation.

        Hidden layers use ReLU, output layer uses softmax.
        """
        caches = {'A0': X}
        A = X

        # Hidden layers with ReLU
        for l in range(1, self.L):
            W = self.parameters[f'W{l}']
            b = self.parameters[f'b{l}']

            Z = W @ A + b
            A = relu(Z)

            caches[f'Z{l}'] = Z
            caches[f'A{l}'] = A

        # Output layer with softmax
        W = self.parameters[f'W{self.L}']
        b = self.parameters[f'b{self.L}']
        Z = W @ A + b
        AL = softmax(Z)

        caches[f'Z{self.L}'] = Z

        return AL, caches

    def compute_cost(self, AL: np.ndarray, Y: np.ndarray) -> float:
        """
        Categorical cross-entropy loss.

        L = -1/m * Σ Σ y_ij * log(ŷ_ij)
        """
        m = Y.shape[1]
        epsilon = 1e-15
        AL = np.clip(AL, epsilon, 1 - epsilon)

        cost = -np.mean(np.sum(Y * np.log(AL), axis=0))
        return float(cost)

    def backward(self, AL: np.ndarray, Y: np.ndarray, caches: Dict) -> Dict:
        """
        Backward propagation.

        For softmax + cross-entropy, the gradient simplifies to: dZ = AL - Y
        """
        gradients = {}
        m = Y.shape[1]

        # Output layer (softmax + cross-entropy)
        dZ = AL - Y

        A_prev = caches[f'A{self.L - 1}']
        gradients[f'dW{self.L}'] = (1/m) * dZ @ A_prev.T
        gradients[f'db{self.L}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)

        dA_prev = self.parameters[f'W{self.L}'].T @ dZ

        # Hidden layers (ReLU)
        for l in reversed(range(1, self.L)):
            Z = caches[f'Z{l}']
            dZ = dA_prev * relu_derivative(Z)

            A_prev = caches[f'A{l - 1}']
            gradients[f'dW{l}'] = (1/m) * dZ @ A_prev.T
            gradients[f'db{l}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)

            if l > 1:
                dA_prev = self.parameters[f'W{l}'].T @ dZ

        return gradients

    def update_parameters(self, gradients: Dict, learning_rate: float):
        """Gradient descent update."""
        for l in range(1, self.L + 1):
            self.parameters[f'W{l}'] -= learning_rate * gradients[f'dW{l}']
            self.parameters[f'b{l}'] -= learning_rate * gradients[f'db{l}']

    def train(self, X_train: np.ndarray, Y_train: np.ndarray,
              X_val: np.ndarray = None, Y_val: np.ndarray = None,
              learning_rate: float = 0.1, epochs: int = 100,
              batch_size: int = 64, print_every: int = 10) -> Dict:
        """
        Train the network using mini-batch gradient descent.

        Args:
            X_train: Training data (n_features, n_samples)
            Y_train: One-hot labels (n_classes, n_samples)
            X_val: Validation data (optional)
            Y_val: Validation labels (optional)
            learning_rate: Step size
            epochs: Number of passes through data
            batch_size: Samples per gradient update
            print_every: Print frequency

        Returns:
            Training history
        """
        m = X_train.shape[1]
        history = {'train_cost': [], 'train_acc': [], 'val_acc': []}

        for epoch in range(epochs):
            # Shuffle data
            permutation = np.random.permutation(m)
            X_shuffled = X_train[:, permutation]
            Y_shuffled = Y_train[:, permutation]

            epoch_cost = 0

            # Mini-batch training
            for i in range(0, m, batch_size):
                X_batch = X_shuffled[:, i:i + batch_size]
                Y_batch = Y_shuffled[:, i:i + batch_size]

                # Forward
                AL, caches = self.forward(X_batch)

                # Cost
                batch_cost = self.compute_cost(AL, Y_batch)
                epoch_cost += batch_cost * X_batch.shape[1]

                # Backward
                gradients = self.backward(AL, Y_batch, caches)

                # Update
                self.update_parameters(gradients, learning_rate)

            epoch_cost /= m
            history['train_cost'].append(epoch_cost)

            # Training accuracy
            train_pred = self.predict(X_train)
            train_acc = np.mean(train_pred == np.argmax(Y_train, axis=0))
            history['train_acc'].append(train_acc)

            # Validation accuracy
            if X_val is not None:
                val_pred = self.predict(X_val)
                val_acc = np.mean(val_pred == np.argmax(Y_val, axis=0))
                history['val_acc'].append(val_acc)
            else:
                val_acc = None

            # Print progress
            if (epoch + 1) % print_every == 0:
                val_str = f", val_acc: {val_acc:.4f}" if val_acc else ""
                print(f"  Epoch {epoch + 1:3d}: cost = {epoch_cost:.4f}, "
                      f"train_acc = {train_acc:.4f}{val_str}")

        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        AL, _ = self.forward(X)
        return np.argmax(AL, axis=0)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return probability predictions."""
        AL, _ = self.forward(X)
        return AL


# =============================================================================
# Visualization Functions
# =============================================================================

def plot_samples(X: np.ndarray, y: np.ndarray, n_samples: int = 25):
    """Plot sample MNIST images."""
    fig, axes = plt.subplots(5, 5, figsize=(8, 8))

    for i, ax in enumerate(axes.flatten()):
        if i < n_samples:
            ax.imshow(X[i].reshape(28, 28), cmap='gray')
            ax.set_title(f'Label: {y[i]}')
        ax.axis('off')

    plt.suptitle('Sample MNIST Images', fontsize=14)
    plt.tight_layout()
    plt.savefig('mnist_samples.png', dpi=150)
    plt.close()


def plot_training_history(history: Dict):
    """Plot training curves."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Cost
    axes[0].plot(history['train_cost'])
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Cost')
    axes[0].set_title('Training Loss')
    axes[0].grid(True, alpha=0.3)

    # Accuracy
    axes[1].plot(history['train_acc'], label='Training')
    if history['val_acc']:
        axes[1].plot(history['val_acc'], label='Validation')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle('Training History', fontsize=14)
    plt.tight_layout()
    plt.savefig('mnist_training.png', dpi=150)
    plt.close()


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray):
    """Plot confusion matrix."""
    # Compute confusion matrix
    n_classes = 10
    cm = np.zeros((n_classes, n_classes), dtype=int)

    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap='Blues')

    # Add labels
    ax.set_xticks(range(10))
    ax.set_yticks(range(10))
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_title('Confusion Matrix')

    # Add text annotations
    for i in range(10):
        for j in range(10):
            color = 'white' if cm[i, j] > cm.max() / 2 else 'black'
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', color=color)

    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig('mnist_confusion.png', dpi=150)
    plt.close()


def plot_misclassified(X: np.ndarray, y_true: np.ndarray, y_pred: np.ndarray, n_samples: int = 16):
    """Plot misclassified examples."""
    misclassified_idx = np.where(y_true != y_pred)[0]

    if len(misclassified_idx) == 0:
        print("  No misclassified samples!")
        return

    n_samples = min(n_samples, len(misclassified_idx))
    sample_idx = np.random.choice(misclassified_idx, n_samples, replace=False)

    fig, axes = plt.subplots(4, 4, figsize=(10, 10))

    for i, ax in enumerate(axes.flatten()):
        if i < n_samples:
            idx = sample_idx[i]
            ax.imshow(X[idx].reshape(28, 28), cmap='gray')
            ax.set_title(f'True: {y_true[idx]}, Pred: {y_pred[idx]}', color='red')
        ax.axis('off')

    plt.suptitle('Misclassified Examples', fontsize=14)
    plt.tight_layout()
    plt.savefig('mnist_misclassified.png', dpi=150)
    plt.close()


def plot_learned_features(W: np.ndarray, n_features: int = 64):
    """Visualize first-layer weights as learned features."""
    n_show = min(n_features, W.shape[0])
    n_cols = 8
    n_rows = (n_show + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, n_rows * 1.5))

    for i, ax in enumerate(axes.flatten()):
        if i < n_show:
            feature = W[i].reshape(28, 28)
            ax.imshow(feature, cmap='RdBu_r', vmin=-np.abs(feature).max(),
                     vmax=np.abs(feature).max())
        ax.axis('off')

    plt.suptitle('Learned First-Layer Features (Weights)', fontsize=14)
    plt.tight_layout()
    plt.savefig('mnist_features.png', dpi=150)
    plt.close()


# =============================================================================
# Main Training Script
# =============================================================================

def main():
    """Train and evaluate MNIST classifier."""
    print("="*60)
    print("Module 26: MNIST Classifier from Scratch")
    print("="*60)

    # Download and load data
    print("\n1. Loading MNIST dataset...")
    download_mnist()
    X_train, y_train, X_test, y_test = load_mnist()

    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    print(f"  Image size: 28x28 = {X_train.shape[1]} features")
    print(f"  Classes: 0-9 (10 digits)")

    # Plot samples
    print("\n2. Visualizing samples...")
    plot_samples(X_train, y_train)
    print("  Saved: mnist_samples.png")

    # Preprocess
    print("\n3. Preprocessing...")
    # Transpose to (features, samples) for our network
    X_train_T = X_train.T
    X_test_T = X_test.T

    # One-hot encode labels
    Y_train = one_hot_encode(y_train)
    Y_test = one_hot_encode(y_test)

    # Use subset for faster training (optional - comment out for full training)
    n_train = 10000  # Use 10k samples for faster demo
    X_train_T = X_train_T[:, :n_train]
    Y_train = Y_train[:, :n_train]
    y_train_subset = y_train[:n_train]

    print(f"  Using {n_train} training samples")
    print(f"  X shape: {X_train_T.shape}")
    print(f"  Y shape: {Y_train.shape}")

    # Create network
    print("\n4. Creating neural network...")
    architecture = [784, 128, 64, 10]
    print(f"  Architecture: {architecture}")

    nn = MNISTClassifier(architecture)

    # Train
    print("\n5. Training (this may take a few minutes)...")
    history = nn.train(
        X_train_T, Y_train,
        X_val=X_test_T, Y_val=Y_test,
        learning_rate=0.1,
        epochs=30,
        batch_size=64,
        print_every=5
    )

    # Plot training history
    print("\n6. Plotting training history...")
    plot_training_history(history)
    print("  Saved: mnist_training.png")

    # Evaluate on test set
    print("\n7. Evaluating on test set...")
    y_pred = nn.predict(X_test_T)
    accuracy = np.mean(y_pred == y_test)
    print(f"  Test Accuracy: {accuracy * 100:.2f}%")

    # Confusion matrix
    print("\n8. Generating confusion matrix...")
    plot_confusion_matrix(y_test, y_pred)
    print("  Saved: mnist_confusion.png")

    # Misclassified examples
    print("\n9. Finding misclassified examples...")
    plot_misclassified(X_test, y_test, y_pred)
    print("  Saved: mnist_misclassified.png")

    # Learned features
    print("\n10. Visualizing learned features...")
    W1 = nn.parameters['W1']
    plot_learned_features(W1)
    print("  Saved: mnist_features.png")

    # Summary
    print("\n" + "="*60)
    print("MNIST Classification Complete!")
    print("="*60)
    print(f"""
Results:
--------
- Architecture: {architecture}
- Training samples: {n_train}
- Test Accuracy: {accuracy * 100:.2f}%
- Parameters: {sum(nn.parameters[f'W{l}'].size + nn.parameters[f'b{l}'].size for l in range(1, nn.L + 1)):,}

Generated plots:
- mnist_samples.png      : Sample training images
- mnist_training.png     : Training loss and accuracy curves
- mnist_confusion.png    : Confusion matrix
- mnist_misclassified.png: Examples the network got wrong
- mnist_features.png     : First-layer weights (learned patterns)

Key Insight:
-----------
The network learned to recognize handwritten digits without being
explicitly programmed! It discovered features (edges, curves, strokes)
through gradient descent alone.

This is the essence of deep learning: learning representations
from data.
    """)


if __name__ == "__main__":
    main()
