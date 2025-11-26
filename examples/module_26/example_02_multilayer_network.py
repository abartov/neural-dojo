#!/usr/bin/env python3
"""
Module 26 Example 2: Multilayer Neural Network

Building a neural network from scratch with:
- Forward propagation
- Backpropagation
- Gradient descent

This network CAN learn XOR (unlike the perceptron)!
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple


# =============================================================================
# Activation Functions
# =============================================================================

def sigmoid(z: np.ndarray) -> np.ndarray:
    """Sigmoid activation function."""
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


def sigmoid_derivative(z: np.ndarray) -> np.ndarray:
    """Derivative of sigmoid: σ'(z) = σ(z) * (1 - σ(z))."""
    s = sigmoid(z)
    return s * (1 - s)


def relu(z: np.ndarray) -> np.ndarray:
    """ReLU activation function."""
    return np.maximum(0, z)


def relu_derivative(z: np.ndarray) -> np.ndarray:
    """Derivative of ReLU: 1 if z > 0 else 0."""
    return (z > 0).astype(float)


def tanh(z: np.ndarray) -> np.ndarray:
    """Tanh activation function."""
    return np.tanh(z)


def tanh_derivative(z: np.ndarray) -> np.ndarray:
    """Derivative of tanh: 1 - tanh²(z)."""
    return 1 - np.tanh(z) ** 2


# =============================================================================
# Neural Network Class
# =============================================================================

class NeuralNetwork:
    """
    A fully-connected neural network built from scratch.

    Supports arbitrary architecture and multiple activation functions.
    """

    def __init__(self, layer_dims: List[int], activation: str = 'relu'):
        """
        Initialize the neural network.

        Args:
            layer_dims: List of layer sizes [n_input, n_hidden1, ..., n_output]
            activation: Activation function for hidden layers ('relu', 'sigmoid', 'tanh')
        """
        self.layer_dims = layer_dims
        self.L = len(layer_dims) - 1  # Number of layers (excluding input)
        self.activation = activation
        self.parameters: Dict[str, np.ndarray] = {}
        self.costs: List[float] = []

        # Set activation function
        if activation == 'relu':
            self.act_fn = relu
            self.act_derivative = relu_derivative
        elif activation == 'sigmoid':
            self.act_fn = sigmoid
            self.act_derivative = sigmoid_derivative
        elif activation == 'tanh':
            self.act_fn = tanh
            self.act_derivative = tanh_derivative
        else:
            raise ValueError(f"Unknown activation: {activation}")

        # Initialize weights
        self._initialize_parameters()

    def _initialize_parameters(self):
        """
        Initialize weights using He initialization.

        He initialization: W ~ N(0, sqrt(2/n_in))
        Helps prevent vanishing/exploding gradients.
        """
        np.random.seed(42)

        for l in range(1, self.L + 1):
            n_in = self.layer_dims[l - 1]
            n_out = self.layer_dims[l]

            # He initialization
            self.parameters[f'W{l}'] = np.random.randn(n_out, n_in) * np.sqrt(2 / n_in)
            self.parameters[f'b{l}'] = np.zeros((n_out, 1))

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Forward propagation through the network.

        Args:
            X: Input data (n_features, n_samples)

        Returns:
            AL: Output of the network
            caches: Dictionary of intermediate values for backprop
        """
        caches = {}
        A = X

        # Hidden layers with chosen activation
        for l in range(1, self.L):
            A_prev = A
            W = self.parameters[f'W{l}']
            b = self.parameters[f'b{l}']

            Z = W @ A_prev + b
            A = self.act_fn(Z)

            caches[f'A{l-1}'] = A_prev
            caches[f'Z{l}'] = Z
            caches[f'A{l}'] = A

        # Output layer with sigmoid (for binary classification)
        W = self.parameters[f'W{self.L}']
        b = self.parameters[f'b{self.L}']
        Z = W @ A + b
        AL = sigmoid(Z)

        caches[f'A{self.L-1}'] = A
        caches[f'Z{self.L}'] = Z

        return AL, caches

    def compute_cost(self, AL: np.ndarray, Y: np.ndarray) -> float:
        """
        Compute binary cross-entropy loss.

        L = -1/m * Σ[y*log(ŷ) + (1-y)*log(1-ŷ)]
        """
        m = Y.shape[1]
        epsilon = 1e-15
        AL = np.clip(AL, epsilon, 1 - epsilon)

        cost = -np.mean(Y * np.log(AL) + (1 - Y) * np.log(1 - AL))
        return float(cost)

    def backward(self, AL: np.ndarray, Y: np.ndarray, caches: Dict) -> Dict:
        """
        Backward propagation to compute gradients.

        Args:
            AL: Output from forward propagation
            Y: True labels
            caches: Intermediate values from forward propagation

        Returns:
            gradients: Dictionary with dW and db for each layer
        """
        gradients = {}
        m = Y.shape[1]

        # Output layer gradient (sigmoid + cross-entropy simplifies to AL - Y)
        dZ = AL - Y

        gradients[f'dW{self.L}'] = (1/m) * dZ @ caches[f'A{self.L-1}'].T
        gradients[f'db{self.L}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)

        dA_prev = self.parameters[f'W{self.L}'].T @ dZ

        # Hidden layers
        for l in reversed(range(1, self.L)):
            dZ = dA_prev * self.act_derivative(caches[f'Z{l}'])

            A_prev = caches[f'A{l-1}'] if l > 1 else caches.get('X', caches['A0'])

            gradients[f'dW{l}'] = (1/m) * dZ @ A_prev.T
            gradients[f'db{l}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)

            if l > 1:
                dA_prev = self.parameters[f'W{l}'].T @ dZ

        return gradients

    def update_parameters(self, gradients: Dict, learning_rate: float):
        """Update parameters using gradient descent."""
        for l in range(1, self.L + 1):
            self.parameters[f'W{l}'] -= learning_rate * gradients[f'dW{l}']
            self.parameters[f'b{l}'] -= learning_rate * gradients[f'db{l}']

    def train(self, X: np.ndarray, Y: np.ndarray, learning_rate: float = 0.1,
              iterations: int = 10000, print_cost: bool = True) -> List[float]:
        """
        Train the neural network.

        Args:
            X: Training data (n_features, n_samples)
            Y: Labels (1, n_samples)
            learning_rate: Step size for gradient descent
            iterations: Number of training iterations
            print_cost: Whether to print cost during training

        Returns:
            List of costs during training
        """
        self.costs = []

        for i in range(iterations):
            # Forward propagation
            AL, caches = self.forward(X)

            # Store input in cache for backprop
            caches['A0'] = X

            # Compute cost
            cost = self.compute_cost(AL, Y)
            self.costs.append(cost)

            # Backward propagation
            gradients = self.backward(AL, Y, caches)

            # Update parameters
            self.update_parameters(gradients, learning_rate)

            # Print progress
            if print_cost and i % 1000 == 0:
                print(f"  Iteration {i:5d}: cost = {cost:.6f}")

        return self.costs

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions (returns 0 or 1)."""
        AL, _ = self.forward(X)
        return (AL > 0.5).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return probability predictions."""
        AL, _ = self.forward(X)
        return AL


# =============================================================================
# Demo Functions
# =============================================================================

def demo_xor():
    """Solve XOR with a 2-layer network."""
    print("="*60)
    print("Part 1: Solving XOR with a 2-Layer Network")
    print("="*60)

    # XOR data
    X = np.array([[0, 0, 1, 1],
                  [0, 1, 0, 1]])
    Y = np.array([[0, 1, 1, 0]])

    print("\n  XOR Truth Table:")
    print("  x₁  x₂  |  y")
    print("  --------+----")
    for i in range(4):
        print(f"   {X[0,i]}   {X[1,i]}  |  {Y[0,i]}")

    # Create network: 2 inputs -> 4 hidden -> 1 output
    print("\n  Network Architecture: 2 -> 4 -> 1")
    nn = NeuralNetwork([2, 4, 1], activation='tanh')

    # Train
    print("\n  Training...")
    costs = nn.train(X, Y, learning_rate=0.5, iterations=10000, print_cost=True)

    # Test
    predictions = nn.predict(X)
    accuracy = np.mean(predictions == Y)
    print(f"\n  Final Accuracy: {accuracy * 100:.0f}%")

    print("\n  Predictions:")
    probs = nn.predict_proba(X)
    for i in range(4):
        print(f"    [{X[0,i]}, {X[1,i]}] -> {probs[0,i]:.4f} (rounded: {predictions[0,i]})")

    # Visualize
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Plot 1: Cost curve
    axes[0].plot(costs)
    axes[0].set_xlabel('Iteration')
    axes[0].set_ylabel('Cost')
    axes[0].set_title('Training Loss')
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Decision boundary
    x_min, x_max = -0.5, 1.5
    y_min, y_max = -0.5, 1.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                         np.linspace(y_min, y_max, 100))
    mesh_input = np.array([xx.ravel(), yy.ravel()])
    Z = nn.predict_proba(mesh_input).reshape(xx.shape)

    axes[1].contourf(xx, yy, Z, levels=20, cmap='RdYlBu_r', alpha=0.8)
    axes[1].colorbar = plt.colorbar(axes[1].contourf(xx, yy, Z, levels=20, cmap='RdYlBu_r'),
                                     ax=axes[1], label='P(y=1)')

    colors = ['red' if y == 0 else 'blue' for y in Y[0]]
    axes[1].scatter(X[0], X[1], c=colors, s=200, edgecolors='black', zorder=5)
    for i in range(4):
        axes[1].annotate(f'{Y[0,i]}', xy=(X[0,i], X[1,i]), ha='center', va='center',
                        fontsize=12, fontweight='bold', color='white')

    axes[1].set_xlabel('x₁')
    axes[1].set_ylabel('x₂')
    axes[1].set_title('Learned Decision Boundary (XOR)')
    axes[1].set_xlim(x_min, x_max)
    axes[1].set_ylim(y_min, y_max)

    # Plot 3: Network architecture
    axes[2].axis('off')

    # Draw neurons
    layer_sizes = [2, 4, 1]
    layer_names = ['Input', 'Hidden', 'Output']
    layer_x = [0.2, 0.5, 0.8]

    for l, (size, name, x) in enumerate(zip(layer_sizes, layer_names, layer_x)):
        y_positions = np.linspace(0.2, 0.8, size)

        for i, y in enumerate(y_positions):
            circle = plt.Circle((x, y), 0.05, fill=True, color='steelblue',
                               ec='black', linewidth=2)
            axes[2].add_patch(circle)

            # Add labels
            if l == 0:
                axes[2].text(x - 0.1, y, f'x{i+1}', ha='center', va='center', fontsize=10)
            elif l == len(layer_sizes) - 1:
                axes[2].text(x + 0.1, y, 'ŷ', ha='center', va='center', fontsize=10)

        axes[2].text(x, 0.05, name, ha='center', fontsize=12)

    # Draw connections
    for l in range(len(layer_sizes) - 1):
        x1, x2 = layer_x[l], layer_x[l + 1]
        y1_positions = np.linspace(0.2, 0.8, layer_sizes[l])
        y2_positions = np.linspace(0.2, 0.8, layer_sizes[l + 1])

        for y1 in y1_positions:
            for y2 in y2_positions:
                axes[2].plot([x1 + 0.05, x2 - 0.05], [y1, y2], 'gray', alpha=0.3, linewidth=0.5)

    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)
    axes[2].set_title('Network Architecture')

    plt.suptitle('XOR Problem Solved!', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('xor_solved.png', dpi=150)
    plt.close()
    print(f"\n  Saved: xor_solved.png")


def demo_nonlinear_classification():
    """Demonstrate classification on non-linearly separable data."""
    print("\n" + "="*60)
    print("Part 2: Non-Linear Classification (Circles)")
    print("="*60)

    # Generate circular data
    np.random.seed(42)
    n_samples = 200

    # Inner circle (class 0)
    r1 = np.random.uniform(0, 1, n_samples // 2)
    theta1 = np.random.uniform(0, 2 * np.pi, n_samples // 2)
    X1 = np.array([r1 * np.cos(theta1), r1 * np.sin(theta1)])
    Y1 = np.zeros((1, n_samples // 2))

    # Outer ring (class 1)
    r2 = np.random.uniform(1.5, 2.5, n_samples // 2)
    theta2 = np.random.uniform(0, 2 * np.pi, n_samples // 2)
    X2 = np.array([r2 * np.cos(theta2), r2 * np.sin(theta2)])
    Y2 = np.ones((1, n_samples // 2))

    X = np.hstack([X1, X2])
    Y = np.hstack([Y1, Y2])

    print(f"\n  Generated {n_samples} samples (circles dataset)")

    # Create and train network
    print("\n  Network Architecture: 2 -> 16 -> 8 -> 1")
    nn = NeuralNetwork([2, 16, 8, 1], activation='relu')

    print("\n  Training...")
    costs = nn.train(X, Y, learning_rate=0.1, iterations=5000, print_cost=True)

    # Test
    predictions = nn.predict(X)
    accuracy = np.mean(predictions == Y)
    print(f"\n  Final Accuracy: {accuracy * 100:.1f}%")

    # Visualize
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Plot 1: Training data
    axes[0].scatter(X[0, Y[0] == 0], X[1, Y[0] == 0], c='red', label='Class 0', alpha=0.6)
    axes[0].scatter(X[0, Y[0] == 1], X[1, Y[0] == 1], c='blue', label='Class 1', alpha=0.6)
    axes[0].set_xlabel('x₁')
    axes[0].set_ylabel('x₂')
    axes[0].set_title('Training Data (Circles)')
    axes[0].legend()
    axes[0].set_aspect('equal')

    # Plot 2: Decision boundary
    x_min, x_max = X[0].min() - 0.5, X[0].max() + 0.5
    y_min, y_max = X[1].min() - 0.5, X[1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                         np.linspace(y_min, y_max, 100))
    mesh_input = np.array([xx.ravel(), yy.ravel()])
    Z = nn.predict_proba(mesh_input).reshape(xx.shape)

    axes[1].contourf(xx, yy, Z, levels=20, cmap='RdYlBu_r', alpha=0.8)
    axes[1].scatter(X[0, Y[0] == 0], X[1, Y[0] == 0], c='red', edgecolors='black', alpha=0.8)
    axes[1].scatter(X[0, Y[0] == 1], X[1, Y[0] == 1], c='blue', edgecolors='black', alpha=0.8)
    axes[1].set_xlabel('x₁')
    axes[1].set_ylabel('x₂')
    axes[1].set_title('Learned Decision Boundary')
    axes[1].set_aspect('equal')

    # Plot 3: Cost curve
    axes[2].plot(costs)
    axes[2].set_xlabel('Iteration')
    axes[2].set_ylabel('Cost')
    axes[2].set_title('Training Loss')
    axes[2].grid(True, alpha=0.3)

    plt.suptitle('Non-Linear Classification with Neural Network', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('nonlinear_classification.png', dpi=150)
    plt.close()
    print(f"  Saved: nonlinear_classification.png")


def demo_backprop_visualization():
    """Visualize what happens during backpropagation."""
    print("\n" + "="*60)
    print("Part 3: Visualizing Backpropagation")
    print("="*60)

    # Simple network for visualization
    X = np.array([[0, 0, 1, 1],
                  [0, 1, 0, 1]])
    Y = np.array([[0, 1, 1, 0]])

    nn = NeuralNetwork([2, 3, 1], activation='sigmoid')

    # Collect gradient magnitudes during training
    gradient_history = []

    # Manual training loop to capture gradients
    for i in range(1000):
        AL, caches = nn.forward(X)
        caches['A0'] = X
        gradients = nn.backward(AL, Y, caches)

        # Store gradient magnitudes
        grad_mags = {
            'dW1': np.mean(np.abs(gradients['dW1'])),
            'dW2': np.mean(np.abs(gradients['dW2'])),
        }
        gradient_history.append(grad_mags)

        nn.update_parameters(gradients, learning_rate=0.5)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Gradient magnitudes over time
    iterations = range(len(gradient_history))
    dW1_mags = [g['dW1'] for g in gradient_history]
    dW2_mags = [g['dW2'] for g in gradient_history]

    axes[0].plot(iterations, dW1_mags, label='Layer 1 gradients')
    axes[0].plot(iterations, dW2_mags, label='Layer 2 gradients')
    axes[0].set_xlabel('Iteration')
    axes[0].set_ylabel('Average |gradient|')
    axes[0].set_title('Gradient Magnitudes During Training')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')

    # Weight distribution
    W1 = nn.parameters['W1'].flatten()
    W2 = nn.parameters['W2'].flatten()

    axes[1].hist(W1, bins=20, alpha=0.6, label='Layer 1 weights')
    axes[1].hist(W2, bins=20, alpha=0.6, label='Layer 2 weights')
    axes[1].set_xlabel('Weight value')
    axes[1].set_ylabel('Count')
    axes[1].set_title('Final Weight Distribution')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle('Backpropagation Internals', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('backprop_visualization.png', dpi=150)
    plt.close()
    print(f"  Saved: backprop_visualization.png")

    print("""
  Key Observations:
  -----------------
  1. Gradients are largest at the start (steep learning curve)
  2. Gradients decrease as we approach the minimum
  3. Output layer gradients are typically larger than hidden layer
  4. This is why deep networks can suffer from "vanishing gradients"
    """)


def demo_hyperparameters():
    """Demonstrate the effect of hyperparameters."""
    print("\n" + "="*60)
    print("Part 4: Effect of Hyperparameters")
    print("="*60)

    # XOR data
    X = np.array([[0, 0, 1, 1], [0, 1, 0, 1]])
    Y = np.array([[0, 1, 1, 0]])

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Learning rate comparison
    print("\n  Testing learning rates...")
    learning_rates = [0.01, 0.1, 0.5, 2.0]

    for lr in learning_rates:
        nn = NeuralNetwork([2, 4, 1], activation='tanh')
        costs = nn.train(X, Y, learning_rate=lr, iterations=3000, print_cost=False)
        axes[0, 0].plot(costs, label=f'lr={lr}')

    axes[0, 0].set_xlabel('Iteration')
    axes[0, 0].set_ylabel('Cost')
    axes[0, 0].set_title('Effect of Learning Rate')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Network depth comparison
    print("  Testing network depths...")
    architectures = [
        [2, 2, 1],
        [2, 4, 1],
        [2, 8, 1],
        [2, 4, 4, 1],
    ]

    for arch in architectures:
        nn = NeuralNetwork(arch, activation='tanh')
        costs = nn.train(X, Y, learning_rate=0.5, iterations=3000, print_cost=False)
        axes[0, 1].plot(costs, label=f'{arch}')

    axes[0, 1].set_xlabel('Iteration')
    axes[0, 1].set_ylabel('Cost')
    axes[0, 1].set_title('Effect of Network Architecture')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Activation function comparison
    print("  Testing activation functions...")
    activations = ['sigmoid', 'tanh', 'relu']

    for act in activations:
        nn = NeuralNetwork([2, 8, 1], activation=act)
        costs = nn.train(X, Y, learning_rate=0.5, iterations=3000, print_cost=False)
        axes[1, 0].plot(costs, label=act)

    axes[1, 0].set_xlabel('Iteration')
    axes[1, 0].set_ylabel('Cost')
    axes[1, 0].set_title('Effect of Activation Function')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Final comparison table
    axes[1, 1].axis('off')

    table_data = [
        ['Hyperparameter', 'Good Values', 'Bad Signs'],
        ['Learning Rate', '0.001 - 1.0', 'Loss oscillating or stuck'],
        ['Hidden Neurons', '16 - 256', 'Underfitting or overfitting'],
        ['Num Layers', '2 - 5', 'Vanishing gradients'],
        ['Activation', 'ReLU (hidden)', 'Dead neurons (ReLU)'],
    ]

    table = axes[1, 1].table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    # Color header
    for i in range(3):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', fontweight='bold')

    axes[1, 1].set_title('Hyperparameter Guidelines', fontsize=12, pad=20)

    plt.suptitle('Hyperparameter Effects on Training', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('hyperparameter_effects.png', dpi=150)
    plt.close()
    print(f"  Saved: hyperparameter_effects.png")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Module 26: Multilayer Neural Network from Scratch")
    print("="*60)

    demo_xor()
    demo_nonlinear_classification()
    demo_backprop_visualization()
    demo_hyperparameters()

    print("\n" + "="*60)
    print("Multilayer Network Examples Complete!")
    print("="*60)
    print("""
Key Takeaways:
1. Multiple layers allow learning non-linear boundaries
2. Forward prop: compute outputs layer by layer
3. Backprop: compute gradients layer by layer (in reverse)
4. Gradient descent: update weights in direction of steepest descent
5. Hyperparameters matter: learning rate, architecture, activation

Generated plots:
- xor_solved.png
- nonlinear_classification.png
- backprop_visualization.png
- hyperparameter_effects.png

Next: example_03_mnist_classifier.py (real-world application!)
    """)
