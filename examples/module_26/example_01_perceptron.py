#!/usr/bin/env python3
"""
Module 26 Example 1: The Perceptron

The simplest neural network - a single neuron that can learn
linear decision boundaries.

This example demonstrates:
1. How a single neuron works
2. The perceptron learning algorithm
3. Why perceptrons can learn AND/OR but NOT XOR
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List


class Perceptron:
    """
    A single-layer perceptron (single neuron).

    The perceptron is the simplest neural network:
    - Takes inputs x₁, x₂, ..., xₙ
    - Computes weighted sum: z = w·x + b
    - Applies step function: y = 1 if z > 0 else 0
    """

    def __init__(self, n_inputs: int, learning_rate: float = 0.1):
        """
        Initialize perceptron with random weights.

        Args:
            n_inputs: Number of input features
            learning_rate: Step size for weight updates
        """
        self.weights = np.random.randn(n_inputs) * 0.01
        self.bias = 0.0
        self.learning_rate = learning_rate
        self.history: List[float] = []

    def activation(self, z: float) -> int:
        """Step activation function."""
        return 1 if z > 0 else 0

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions for input data.

        Args:
            X: Input data (n_samples, n_features)

        Returns:
            Predictions (n_samples,)
        """
        z = X @ self.weights + self.bias
        return np.array([self.activation(zi) for zi in z])

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100) -> List[float]:
        """
        Train the perceptron using the perceptron learning rule.

        The perceptron learning rule:
        - If prediction is correct: do nothing
        - If prediction is 0 but should be 1: add input to weights
        - If prediction is 1 but should be 0: subtract input from weights

        Args:
            X: Training data (n_samples, n_features)
            y: Labels (n_samples,)
            epochs: Number of training iterations

        Returns:
            List of accuracy values per epoch
        """
        self.history = []

        for epoch in range(epochs):
            errors = 0

            for xi, yi in zip(X, y):
                # Forward pass
                z = np.dot(xi, self.weights) + self.bias
                prediction = self.activation(z)

                # Update if wrong
                if prediction != yi:
                    errors += 1
                    # Perceptron learning rule
                    update = self.learning_rate * (yi - prediction)
                    self.weights += update * xi
                    self.bias += update

            accuracy = 1 - errors / len(y)
            self.history.append(accuracy)

            if errors == 0:
                print(f"  Converged at epoch {epoch + 1}")
                break

        return self.history


def create_logic_gate_data(gate: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create training data for logic gates.

    Args:
        gate: One of 'AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR'

    Returns:
        X: Input data (4, 2)
        y: Labels (4,)
    """
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])

    gates = {
        'AND':  np.array([0, 0, 0, 1]),
        'OR':   np.array([0, 1, 1, 1]),
        'NAND': np.array([1, 1, 1, 0]),
        'NOR':  np.array([1, 0, 0, 0]),
        'XOR':  np.array([0, 1, 1, 0]),
        'XNOR': np.array([1, 0, 0, 1]),
    }

    return X, gates[gate]


def plot_decision_boundary(perceptron: Perceptron, X: np.ndarray, y: np.ndarray,
                           title: str, ax: plt.Axes):
    """Plot the decision boundary learned by the perceptron."""
    # Create mesh grid
    x_min, x_max = -0.5, 1.5
    y_min, y_max = -0.5, 1.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                         np.linspace(y_min, y_max, 100))

    # Predict on mesh
    mesh_points = np.c_[xx.ravel(), yy.ravel()]
    Z = perceptron.predict(mesh_points)
    Z = Z.reshape(xx.shape)

    # Plot decision boundary
    ax.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
    ax.contour(xx, yy, Z, colors='black', linewidths=0.5)

    # Plot data points
    colors = ['red' if yi == 0 else 'blue' for yi in y]
    ax.scatter(X[:, 0], X[:, 1], c=colors, s=200, edgecolors='black', zorder=5)

    # Add labels
    for i, (xi, yi) in enumerate(zip(X, y)):
        ax.annotate(f'{int(yi)}', xy=(xi[0], xi[1]), ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white')

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('x₁')
    ax.set_ylabel('x₂')
    ax.set_title(title)
    ax.set_aspect('equal')


def demo_logic_gates():
    """Demonstrate perceptron learning on logic gates."""
    print("="*60)
    print("Part 1: Perceptron Learning Logic Gates")
    print("="*60)

    # Gates that ARE linearly separable
    learnable_gates = ['AND', 'OR', 'NAND', 'NOR']

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes = axes.flatten()

    for idx, gate in enumerate(learnable_gates):
        print(f"\n--- Learning {gate} Gate ---")
        X, y = create_logic_gate_data(gate)

        print(f"  Truth table:")
        for xi, yi in zip(X, y):
            print(f"    {xi[0]} {gate} {xi[1]} = {yi}")

        # Train perceptron
        perceptron = Perceptron(n_inputs=2, learning_rate=0.1)
        history = perceptron.train(X, y, epochs=100)

        # Test
        predictions = perceptron.predict(X)
        accuracy = np.mean(predictions == y)
        print(f"  Final accuracy: {accuracy * 100:.0f}%")
        print(f"  Learned weights: w = {perceptron.weights.round(3)}, b = {perceptron.bias:.3f}")

        # Plot
        plot_decision_boundary(perceptron, X, y, f'{gate} Gate', axes[idx])

    plt.suptitle('Perceptron Learning Linearly Separable Functions', fontsize=14)
    plt.tight_layout()
    plt.savefig('perceptron_learnable_gates.png', dpi=150)
    plt.close()
    print(f"\n  Saved: perceptron_learnable_gates.png")


def demo_xor_failure():
    """Demonstrate why perceptron fails on XOR."""
    print("\n" + "="*60)
    print("Part 2: The XOR Problem - Why Perceptrons Fail")
    print("="*60)

    X, y = create_logic_gate_data('XOR')

    print("\n  XOR Truth Table:")
    for xi, yi in zip(X, y):
        print(f"    {xi[0]} XOR {xi[1]} = {yi}")

    print("\n  Training perceptron on XOR...")
    perceptron = Perceptron(n_inputs=2, learning_rate=0.1)
    history = perceptron.train(X, y, epochs=1000)

    predictions = perceptron.predict(X)
    accuracy = np.mean(predictions == y)
    print(f"  Final accuracy: {accuracy * 100:.0f}%")

    # Visualize the failure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Decision boundary attempt
    plot_decision_boundary(perceptron, X, y, 'XOR: Perceptron Cannot Learn', axes[0])

    # Right: Why it's impossible
    axes[1].scatter([0, 1], [1, 0], c='blue', s=200, label='Class 1', edgecolors='black')
    axes[1].scatter([0, 1], [0, 1], c='red', s=200, label='Class 0', edgecolors='black')

    # Add annotations
    axes[1].annotate('(0,0)→0', (0, 0), textcoords="offset points", xytext=(10, 10))
    axes[1].annotate('(0,1)→1', (0, 1), textcoords="offset points", xytext=(10, 10))
    axes[1].annotate('(1,0)→1', (1, 0), textcoords="offset points", xytext=(10, 10))
    axes[1].annotate('(1,1)→0', (1, 1), textcoords="offset points", xytext=(10, 10))

    # Show impossible lines
    for angle in np.linspace(0, np.pi, 8):
        x_line = np.linspace(-0.5, 1.5, 100)
        y_line = 0.5 + np.tan(angle) * (x_line - 0.5)
        mask = (y_line > -0.5) & (y_line < 1.5)
        axes[1].plot(x_line[mask], y_line[mask], 'gray', alpha=0.3, linewidth=1)

    axes[1].set_xlim(-0.5, 1.5)
    axes[1].set_ylim(-0.5, 1.5)
    axes[1].set_xlabel('x₁')
    axes[1].set_ylabel('x₂')
    axes[1].set_title('XOR: No Single Line Can Separate the Classes')
    axes[1].legend()
    axes[1].set_aspect('equal')

    plt.suptitle('The XOR Problem: Why Single Neurons Are Not Enough', fontsize=14)
    plt.tight_layout()
    plt.savefig('perceptron_xor_failure.png', dpi=150)
    plt.close()
    print(f"  Saved: perceptron_xor_failure.png")

    print("""
  Key Insight:
  -----------
  XOR is NOT linearly separable!

  No single straight line can separate the 1s from the 0s.
  This was proven by Minsky & Papert in 1969 and nearly
  killed neural network research for decades.

  The solution? Multiple layers of neurons!
  A 2-layer network CAN learn XOR (next example).
    """)


def demo_sigmoid_neuron():
    """Demonstrate a neuron with sigmoid activation."""
    print("\n" + "="*60)
    print("Part 3: Sigmoid Neuron (Smooth Activation)")
    print("="*60)

    def sigmoid(z):
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    # Visualize activation functions
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    z = np.linspace(-10, 10, 100)

    # Step function
    step = np.where(z > 0, 1, 0)
    axes[0].plot(z, step, 'b-', linewidth=2)
    axes[0].set_title('Step Function (Perceptron)')
    axes[0].set_xlabel('z')
    axes[0].set_ylabel('f(z)')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    axes[0].axvline(x=0, color='gray', linestyle='--', alpha=0.5)

    # Sigmoid
    sig = sigmoid(z)
    axes[1].plot(z, sig, 'b-', linewidth=2)
    axes[1].set_title('Sigmoid Function')
    axes[1].set_xlabel('z')
    axes[1].set_ylabel('σ(z)')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    axes[1].axvline(x=0, color='gray', linestyle='--', alpha=0.5)

    # ReLU
    relu = np.maximum(0, z)
    axes[2].plot(z, relu, 'b-', linewidth=2)
    axes[2].set_title('ReLU Function')
    axes[2].set_xlabel('z')
    axes[2].set_ylabel('ReLU(z)')
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[2].axvline(x=0, color='gray', linestyle='--', alpha=0.5)

    plt.suptitle('Activation Functions in Neural Networks', fontsize=14)
    plt.tight_layout()
    plt.savefig('activation_functions.png', dpi=150)
    plt.close()
    print(f"  Saved: activation_functions.png")

    print("""
  Why Sigmoid over Step?
  ----------------------
  1. Smooth: Has a gradient everywhere (needed for backpropagation)
  2. Probabilistic: Output between 0 and 1 (like a probability)
  3. Differentiable: σ'(z) = σ(z) * (1 - σ(z))

  Why ReLU over Sigmoid?
  ----------------------
  1. No vanishing gradient for positive values
  2. Computationally efficient (just max(0, z))
  3. Sparse activation (many neurons output 0)
  4. Works better for deep networks
    """)


def demo_gradient_descent():
    """Visualize gradient descent on a simple function."""
    print("\n" + "="*60)
    print("Part 4: Gradient Descent Visualization")
    print("="*60)

    # Simple 1D function: f(x) = x^2
    def f(x):
        return x ** 2

    def df(x):
        return 2 * x

    # Gradient descent
    x = 4.0  # Starting point
    learning_rate = 0.2
    history = [(x, f(x))]

    for i in range(15):
        gradient = df(x)
        x = x - learning_rate * gradient
        history.append((x, f(x)))

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Function and path
    x_range = np.linspace(-5, 5, 100)
    axes[0].plot(x_range, f(x_range), 'b-', linewidth=2, label='f(x) = x²')

    xs, ys = zip(*history)
    axes[0].plot(xs, ys, 'ro-', markersize=8, label='Gradient descent path')
    axes[0].annotate('Start', xy=(xs[0], ys[0]), xytext=(xs[0]+0.5, ys[0]+2),
                    arrowprops=dict(arrowstyle='->', color='red'))
    axes[0].annotate('End', xy=(xs[-1], ys[-1]), xytext=(xs[-1]+1, ys[-1]+2),
                    arrowprops=dict(arrowstyle='->', color='green'))

    axes[0].set_xlabel('x (parameter)')
    axes[0].set_ylabel('f(x) (loss)')
    axes[0].set_title('Gradient Descent: Finding the Minimum')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Right: Convergence
    axes[1].plot(range(len(history)), [y for _, y in history], 'b-o')
    axes[1].set_xlabel('Iteration')
    axes[1].set_ylabel('Loss f(x)')
    axes[1].set_title('Loss Decreasing Over Iterations')
    axes[1].grid(True, alpha=0.3)

    plt.suptitle('Gradient Descent: The Learning Algorithm', fontsize=14)
    plt.tight_layout()
    plt.savefig('gradient_descent.png', dpi=150)
    plt.close()
    print(f"  Saved: gradient_descent.png")

    print(f"""
  Gradient Descent in Action:
  ---------------------------
  Starting point: x = 4.0, f(x) = 16.0
  After 15 iterations: x = {xs[-1]:.4f}, f(x) = {ys[-1]:.6f}

  Each step: x_new = x_old - learning_rate * gradient
           = x_old - 0.2 * 2x_old
           = 0.6 * x_old

  The loss decreases exponentially toward the minimum!
    """)


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Module 26: The Perceptron")
    print("The Simplest Neural Network")
    print("="*60)

    demo_logic_gates()
    demo_xor_failure()
    demo_sigmoid_neuron()
    demo_gradient_descent()

    print("\n" + "="*60)
    print("Perceptron Examples Complete!")
    print("="*60)
    print("""
Key Takeaways:
1. A perceptron is just: y = step(w·x + b)
2. It can learn linearly separable functions (AND, OR)
3. It CANNOT learn XOR (not linearly separable)
4. This limitation led to the "AI Winter" of the 1970s
5. The solution: Multiple layers (next example!)

Generated plots:
- perceptron_learnable_gates.png
- perceptron_xor_failure.png
- activation_functions.png
- gradient_descent.png

Next: example_02_multilayer_network.py (solving XOR!)
    """)
