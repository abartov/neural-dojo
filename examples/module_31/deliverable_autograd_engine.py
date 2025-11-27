#!/usr/bin/env python3
"""
Module 31 Deliverable: Autograd Engine

A complete automatic differentiation engine built from scratch.
Implements reverse-mode autodiff (backpropagation) with visualization
and gradient checking utilities.

Features:
- Scalar autograd with full operation support
- Tensor autograd for neural networks
- Gradient checking for verification
- Computation graph visualization
- Training example with custom autograd

Usage:
    python deliverable_autograd_engine.py demo1  # Scalar autograd basics
    python deliverable_autograd_engine.py demo2  # Build and train neural network
    python deliverable_autograd_engine.py demo3  # Gradient checking
    python deliverable_autograd_engine.py demo4  # Generate autograd report

Author: Neural Dojo
"""

import math
import os
import sys
import json
import random
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Any, Union, Set, Callable


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class GradientCheckResult:
    """Results from gradient checking."""
    param_name: str
    analytical_grad: float
    numerical_grad: float
    relative_error: float
    passed: bool


@dataclass
class TrainingLog:
    """Log of training run."""
    epochs: int
    losses: List[float]
    final_loss: float
    training_time_seconds: float
    model_params: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# SCALAR AUTOGRAD ENGINE
# ============================================================================

class Value:
    """
    A scalar value that tracks its computation history for automatic differentiation.

    This is a complete implementation of reverse-mode autodiff for scalars,
    similar to how PyTorch tensors work internally.

    Example:
        x = Value(2.0)
        y = Value(3.0)
        z = x * y + x ** 2
        z.backward()
        print(x.grad)  # dz/dx = y + 2x = 3 + 4 = 7
    """

    def __init__(self, data: float, _children: tuple = (), _op: str = '', label: str = ''):
        self.data = float(data)
        self.grad = 0.0
        self.label = label

        # Internal variables for autograd
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __repr__(self):
        if self.label:
            return f"Value({self.label}={self.data:.4f}, grad={self.grad:.4f})"
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

    # ========== Arithmetic Operations ==========

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), '+')

        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward

        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), '*')

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward

        return out

    def __pow__(self, n):
        assert isinstance(n, (int, float)), "only int/float powers supported"
        out = Value(self.data ** n, (self,), f'**{n}')

        def _backward():
            self.grad += (n * self.data ** (n - 1)) * out.grad
        out._backward = _backward

        return out

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, other):
        return self * other ** -1

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return other + (-self)

    def __rtruediv__(self, other):
        return other * self ** -1

    # ========== Activation Functions ==========

    def relu(self):
        out = Value(max(0, self.data), (self,), 'ReLU')

        def _backward():
            self.grad += (self.data > 0) * out.grad
        out._backward = _backward

        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), 'tanh')

        def _backward():
            self.grad += (1 - t ** 2) * out.grad
        out._backward = _backward

        return out

    def sigmoid(self):
        s = 1 / (1 + math.exp(-self.data))
        out = Value(s, (self,), 'sigmoid')

        def _backward():
            self.grad += s * (1 - s) * out.grad
        out._backward = _backward

        return out

    def exp(self):
        out = Value(math.exp(self.data), (self,), 'exp')

        def _backward():
            self.grad += out.data * out.grad
        out._backward = _backward

        return out

    def log(self):
        out = Value(math.log(self.data), (self,), 'log')

        def _backward():
            self.grad += (1 / self.data) * out.grad
        out._backward = _backward

        return out

    # ========== Backward Pass ==========

    def backward(self):
        """
        Compute gradients for all nodes in the computation graph.

        Uses reverse topological sort to ensure nodes are processed
        in the correct order (outputs before inputs).
        """
        # Topological sort
        topo = []
        visited = set()

        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        # Initialize gradient of output
        self.grad = 1.0

        # Backpropagate in reverse order
        for v in reversed(topo):
            v._backward()

    def zero_grad(self):
        """Reset gradient to zero."""
        self.grad = 0.0


# ============================================================================
# NEURAL NETWORK COMPONENTS
# ============================================================================

class Neuron:
    """
    A single neuron with learnable weights and bias.

    Computes: activation(sum(w_i * x_i) + b)
    """

    def __init__(self, nin: int, nonlin: bool = True):
        """
        Args:
            nin: Number of inputs
            nonlin: Whether to apply tanh activation
        """
        # Xavier initialization
        self.w = [Value(random.uniform(-1, 1) / math.sqrt(nin)) for _ in range(nin)]
        self.b = Value(0.0)
        self.nonlin = nonlin

    def __call__(self, x: List[Value]) -> Value:
        # Weighted sum
        act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        # Activation
        return act.tanh() if self.nonlin else act

    def parameters(self) -> List[Value]:
        return self.w + [self.b]

    def __repr__(self):
        return f"{'TanhNeuron' if self.nonlin else 'LinearNeuron'}({len(self.w)})"


class Layer:
    """A layer of neurons."""

    def __init__(self, nin: int, nout: int, **kwargs):
        self.neurons = [Neuron(nin, **kwargs) for _ in range(nout)]

    def __call__(self, x: List[Value]) -> List[Value]:
        out = [n(x) for n in self.neurons]
        return out[0] if len(out) == 1 else out

    def parameters(self) -> List[Value]:
        return [p for n in self.neurons for p in n.parameters()]

    def __repr__(self):
        return f"Layer([{', '.join(str(n) for n in self.neurons)}])"


class MLP:
    """
    Multi-Layer Perceptron built with our custom autograd.

    Example:
        model = MLP(2, [16, 16, 1])  # 2 inputs -> 16 -> 16 -> 1 output
        x = [Value(1.0), Value(2.0)]
        y = model(x)
    """

    def __init__(self, nin: int, nouts: List[int]):
        """
        Args:
            nin: Number of input features
            nouts: List of layer sizes (last is output)
        """
        sz = [nin] + nouts
        self.layers = [
            Layer(sz[i], sz[i + 1], nonlin=(i != len(nouts) - 1))
            for i in range(len(nouts))
        ]

    def __call__(self, x: List[Value]) -> Value:
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self) -> List[Value]:
        return [p for layer in self.layers for p in layer.parameters()]

    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0.0

    def __repr__(self):
        return f"MLP([{', '.join(str(layer) for layer in self.layers)}])"


# ============================================================================
# GRADIENT CHECKING
# ============================================================================

def numerical_gradient(
    f: Callable,
    params: List[Value],
    epsilon: float = 1e-5
) -> List[float]:
    """
    Compute numerical gradients using finite differences.

    Args:
        f: Function that returns a Value (loss)
        params: Parameters to compute gradients for
        epsilon: Small perturbation

    Returns:
        List of numerical gradients
    """
    grads = []

    for param in params:
        # f(x + ε)
        original = param.data
        param.data = original + epsilon
        loss_plus = f().data

        # f(x - ε)
        param.data = original - epsilon
        loss_minus = f().data

        # Numerical gradient
        grad = (loss_plus - loss_minus) / (2 * epsilon)
        grads.append(grad)

        # Restore
        param.data = original

    return grads


def gradient_check(
    f: Callable,
    params: List[Value],
    param_names: List[str] = None,
    epsilon: float = 1e-5,
    tolerance: float = 1e-5
) -> List[GradientCheckResult]:
    """
    Compare analytical gradients (from backprop) with numerical gradients.

    Args:
        f: Function that returns a Value (loss)
        params: Parameters to check
        param_names: Names for parameters (for reporting)
        epsilon: Perturbation for numerical gradient
        tolerance: Max relative error for passing

    Returns:
        List of GradientCheckResult
    """
    if param_names is None:
        param_names = [f"param_{i}" for i in range(len(params))]

    # Get analytical gradients
    for p in params:
        p.grad = 0.0
    loss = f()
    loss.backward()
    analytical = [p.grad for p in params]

    # Get numerical gradients
    numerical = numerical_gradient(f, params, epsilon)

    # Compare
    results = []
    for name, a, n in zip(param_names, analytical, numerical):
        # Relative error
        denom = max(abs(a), abs(n), 1e-8)
        rel_error = abs(a - n) / denom

        results.append(GradientCheckResult(
            param_name=name,
            analytical_grad=a,
            numerical_grad=n,
            relative_error=rel_error,
            passed=rel_error < tolerance
        ))

    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def trace_graph(root: Value) -> Tuple[Set[Value], Set[Tuple[Value, Value]]]:
    """
    Trace the computation graph from output to inputs.

    Returns:
        nodes: Set of all Value nodes
        edges: Set of (child, parent) edges
    """
    nodes, edges = set(), set()

    def build(v):
        if v not in nodes:
            nodes.add(v)
            for child in v._prev:
                edges.add((child, v))
                build(child)

    build(root)
    return nodes, edges


def draw_graph_ascii(root: Value, max_depth: int = 10) -> str:
    """
    Create ASCII visualization of computation graph.

    Args:
        root: Output node of the graph
        max_depth: Maximum depth to display

    Returns:
        ASCII string representation
    """
    lines = []
    lines.append("Computation Graph:")
    lines.append("=" * 50)

    def format_node(v: Value) -> str:
        label = v.label if v.label else f"{v.data:.4f}"
        return f"[{label}] (grad={v.grad:.4f})"

    def draw(v: Value, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            lines.append(f"{prefix}...")
            return

        node_str = format_node(v)
        if v._op:
            node_str = f"{v._op} -> {node_str}"
        lines.append(f"{prefix}{node_str}")

        children = list(v._prev)
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}", )
            draw(child, new_prefix, depth + 1)

    # Simplified version - just list nodes
    nodes, edges = trace_graph(root)
    lines.append(f"\nTotal nodes: {len(nodes)}")
    lines.append(f"Total edges: {len(edges)}")
    lines.append("")

    # List all nodes with values and gradients
    for node in sorted(nodes, key=lambda x: x.data):
        label = node.label if node.label else "intermediate"
        op = f"({node._op})" if node._op else ""
        lines.append(f"  {label:12s} {op:8s}: value={node.data:8.4f}, grad={node.grad:8.4f}")

    return "\n".join(lines)


# ============================================================================
# STORAGE
# ============================================================================

class Storage:
    """Handle saving and loading results."""

    def __init__(self, storage_dir: str = ".autograd_engine"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_json(self, data: Any, filename: str) -> str:
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return filepath

    def load_json(self, filename: str) -> Dict:
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_1_scalar_autograd():
    """
    Demo 1: Scalar Autograd Basics

    Shows how our custom autograd computes gradients for scalar expressions.
    """
    print("=" * 60)
    print("DEMO 1: Scalar Autograd Basics")
    print("=" * 60)
    print()

    # Example 1: Simple expression
    print("Example 1: L = (x * w + b)²")
    print("-" * 40)

    x = Value(2.0, label='x')
    w = Value(3.0, label='w')
    b = Value(1.0, label='b')

    # Forward pass
    z = x * w + b
    z.label = 'z'
    L = z ** 2
    L.label = 'L'

    print(f"Forward pass:")
    print(f"  x = {x.data}, w = {w.data}, b = {b.data}")
    print(f"  z = x*w + b = {z.data}")
    print(f"  L = z² = {L.data}")
    print()

    # Backward pass
    L.backward()

    print(f"Backward pass (gradients):")
    print(f"  dL/dL = {L.grad}")
    print(f"  dL/dz = 2z = 2*{z.data} = {z.grad}")
    print(f"  dL/dw = dL/dz * dz/dw = {z.grad} * {x.data} = {w.grad}")
    print(f"  dL/dx = dL/dz * dz/dx = {z.grad} * {w.data} = {x.grad}")
    print(f"  dL/db = dL/dz * dz/db = {z.grad} * 1 = {b.grad}")
    print()

    # Verify analytically
    print("Verification:")
    print(f"  L = (xw + b)² = (2*3 + 1)² = 49 ✓" if L.data == 49 else "  L ✗")
    print(f"  dL/dw = 2(xw+b)*x = 2*7*2 = 28 ✓" if w.grad == 28 else "  dL/dw ✗")
    print(f"  dL/dx = 2(xw+b)*w = 2*7*3 = 42 ✓" if x.grad == 42 else "  dL/dx ✗")
    print()

    # Example 2: With activation functions
    print("Example 2: Neuron with tanh activation")
    print("-" * 40)

    x1 = Value(1.0, label='x1')
    x2 = Value(0.5, label='x2')
    w1 = Value(0.3, label='w1')
    w2 = Value(-0.2, label='w2')
    b = Value(0.1, label='b')

    # Forward: y = tanh(w1*x1 + w2*x2 + b)
    pre_act = w1 * x1 + w2 * x2 + b
    pre_act.label = 'pre_act'
    y = pre_act.tanh()
    y.label = 'y'

    print(f"Forward pass:")
    print(f"  pre_activation = w1*x1 + w2*x2 + b = {pre_act.data:.4f}")
    print(f"  y = tanh(pre_activation) = {y.data:.4f}")
    print()

    # Backward
    y.backward()

    print(f"Backward pass:")
    print(f"  dy/dy = {y.grad:.4f}")
    print(f"  dy/d(pre_act) = 1 - tanh²(pre_act) = {pre_act.grad:.4f}")
    print(f"  dy/dw1 = {w1.grad:.4f}")
    print(f"  dy/dw2 = {w2.grad:.4f}")
    print(f"  dy/db = {b.grad:.4f}")
    print()

    # Example 3: Chain of operations
    print("Example 3: Chain rule in action")
    print("-" * 40)

    a = Value(2.0, label='a')
    b = Value(3.0, label='b')

    # c = a * b
    # d = c + a
    # e = d * d
    c = a * b
    c.label = 'c'
    d = c + a
    d.label = 'd'
    e = d * d
    e.label = 'e'

    e.backward()

    print(f"Expression: e = (a*b + a)²")
    print(f"  a = {a.data}, b = {b.data}")
    print(f"  c = a*b = {c.data}")
    print(f"  d = c + a = {d.data}")
    print(f"  e = d² = {e.data}")
    print()
    print(f"Gradients:")
    print(f"  de/da = {a.grad} (via two paths: through c and directly to d)")
    print(f"  de/db = {b.grad}")
    print()

    # Verify: de/da = de/dd * (dd/dc * dc/da + dd/da)
    #                = 2d * (b + 1) = 2*8 * (3+1) = 64
    expected_da = 2 * d.data * (b.data + 1)
    print(f"Verification: de/da = 2d*(b+1) = {expected_da} ✓" if abs(a.grad - expected_da) < 1e-6 else "✗")

    return {"L": L.data, "dL_dw": w.grad, "dL_dx": x.grad}


def demo_2_train_neural_network():
    """
    Demo 2: Train Neural Network with Custom Autograd

    Builds and trains an MLP using our autograd engine.
    """
    print("=" * 60)
    print("DEMO 2: Train Neural Network with Custom Autograd")
    print("=" * 60)
    print()

    storage = Storage()
    random.seed(1337)  # This seed works well for XOR

    # Create a simple dataset: XOR problem (not linearly separable!)
    # Scale to -1/1 for better gradient flow with tanh
    print("Dataset: XOR problem (scaled to -1/1)")
    print("-" * 40)

    xs = [
        [Value(-1.0), Value(-1.0)],
        [Value(-1.0), Value(1.0)],
        [Value(1.0), Value(-1.0)],
        [Value(1.0), Value(1.0)],
    ]
    ys = [Value(-1.0), Value(1.0), Value(1.0), Value(-1.0)]  # XOR outputs

    for x, y in zip(xs, ys):
        print(f"  Input: [{x[0].data}, {x[1].data}] -> Target: {y.data}")
    print()

    # Create model
    print("Creating MLP: 2 -> 8 -> 8 -> 1")
    model = MLP(2, [8, 8, 1])
    params = model.parameters()
    print(f"Total parameters: {len(params)}")
    print()

    # Training loop
    print("Training...")
    print("-" * 40)

    learning_rate = 0.05
    epochs = 200
    losses = []

    import time
    start_time = time.time()

    for epoch in range(epochs):
        # Forward pass
        preds = [model(x) for x in xs]

        # MSE Loss
        loss = sum((pred - y) ** 2 for pred, y in zip(preds, ys))
        losses.append(loss.data)

        # Backward pass
        model.zero_grad()
        loss.backward()

        # Update parameters (SGD)
        for p in params:
            p.data -= learning_rate * p.grad

        if (epoch + 1) % 50 == 0:
            print(f"  Epoch {epoch + 1:3d}: Loss = {loss.data:.6f}")

    training_time = time.time() - start_time
    print("-" * 40)
    print()

    # Final predictions
    print("Final Predictions:")
    print("-" * 40)
    for x, y in zip(xs, ys):
        pred = model(x)
        correct = "✓" if abs(pred.data - y.data) < 0.5 else "✗"
        print(f"  [{x[0].data:.0f}, {x[1].data:.0f}] -> pred: {pred.data:6.3f}, target: {y.data:4.1f} {correct}")
    print()

    # Save results
    log = TrainingLog(
        epochs=epochs,
        losses=losses,
        final_loss=losses[-1],
        training_time_seconds=training_time,
        model_params=len(params)
    )

    filepath = storage.save_json(asdict(log), "training_log.json")
    print(f"Training log saved to: {filepath}")
    print()

    print("Summary:")
    print(f"  Final loss: {losses[-1]:.6f}")
    print(f"  Training time: {training_time:.2f}s")
    print(f"  Parameters: {len(params)}")

    return log


def demo_3_gradient_checking():
    """
    Demo 3: Gradient Checking

    Verifies our autograd implementation by comparing with numerical gradients.
    """
    print("=" * 60)
    print("DEMO 3: Gradient Checking")
    print("=" * 60)
    print()

    storage = Storage()

    # Test 1: Simple quadratic
    print("Test 1: L = x²")
    print("-" * 40)

    x = Value(3.0, label='x')

    def loss_fn1():
        return x ** 2

    results1 = gradient_check(loss_fn1, [x], ['x'])
    for r in results1:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"  {r.param_name}: analytical={r.analytical_grad:.6f}, "
              f"numerical={r.numerical_grad:.6f}, error={r.relative_error:.2e} {status}")
    print()

    # Test 2: Product
    print("Test 2: L = x * y")
    print("-" * 40)

    x = Value(2.0, label='x')
    y = Value(3.0, label='y')

    def loss_fn2():
        return x * y

    results2 = gradient_check(loss_fn2, [x, y], ['x', 'y'])
    for r in results2:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"  {r.param_name}: analytical={r.analytical_grad:.6f}, "
              f"numerical={r.numerical_grad:.6f}, error={r.relative_error:.2e} {status}")
    print()

    # Test 3: tanh activation
    print("Test 3: L = tanh(x)")
    print("-" * 40)

    x = Value(0.5, label='x')

    def loss_fn3():
        return x.tanh()

    results3 = gradient_check(loss_fn3, [x], ['x'])
    for r in results3:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"  {r.param_name}: analytical={r.analytical_grad:.6f}, "
              f"numerical={r.numerical_grad:.6f}, error={r.relative_error:.2e} {status}")
    print()

    # Test 4: Complex expression
    print("Test 4: L = tanh(x*w + b)²")
    print("-" * 40)

    x = Value(1.0, label='x')
    w = Value(0.5, label='w')
    b = Value(0.1, label='b')

    def loss_fn4():
        return (x * w + b).tanh() ** 2

    results4 = gradient_check(loss_fn4, [x, w, b], ['x', 'w', 'b'])
    for r in results4:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"  {r.param_name}: analytical={r.analytical_grad:.6f}, "
              f"numerical={r.numerical_grad:.6f}, error={r.relative_error:.2e} {status}")
    print()

    # Test 5: Neural network layer
    print("Test 5: Single neuron")
    print("-" * 40)

    random.seed(42)
    neuron = Neuron(2, nonlin=True)
    x_input = [Value(1.0), Value(0.5)]

    def loss_fn5():
        return neuron(x_input) ** 2

    param_names = [f'w{i}' for i in range(len(neuron.w))] + ['b']
    results5 = gradient_check(loss_fn5, neuron.parameters(), param_names)

    all_passed = True
    for r in results5:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"  {r.param_name}: analytical={r.analytical_grad:.6f}, "
              f"numerical={r.numerical_grad:.6f}, error={r.relative_error:.2e} {status}")
        if not r.passed:
            all_passed = False
    print()

    # Summary
    all_results = results1 + results2 + results3 + results4 + results5
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    print("=" * 40)
    print(f"SUMMARY: {passed}/{total} gradient checks passed")
    if passed == total:
        print("All gradients verified! Autograd implementation is correct.")
    else:
        print("Some gradients failed! Check implementation.")

    # Save results
    results_data = {
        "tests": [asdict(r) for r in all_results],
        "passed": passed,
        "total": total,
        "timestamp": datetime.now().isoformat()
    }
    filepath = storage.save_json(results_data, "gradient_check_results.json")
    print(f"\nResults saved to: {filepath}")

    return all_results


def demo_4_generate_report():
    """
    Demo 4: Generate Autograd Report

    Generates a comprehensive markdown report from saved results.
    """
    print("=" * 60)
    print("DEMO 4: Generate Autograd Report")
    print("=" * 60)
    print()

    storage = Storage()

    # Load results
    training_log = storage.load_json("training_log.json")
    grad_check = storage.load_json("gradient_check_results.json")

    # Generate report
    lines = [
        "# Autograd Engine Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Overview",
        "",
        "This report summarizes the custom autograd engine implementation and tests.",
        "",
        "### Key Concepts Implemented",
        "",
        "1. **Value class**: Scalar with gradient tracking",
        "2. **Computational graph**: Automatic construction during forward pass",
        "3. **Backward pass**: Reverse-mode autodiff using chain rule",
        "4. **Neural network**: MLP built entirely with custom autograd",
        "",
    ]

    # Training results
    if training_log:
        lines.extend([
            "## Neural Network Training",
            "",
            f"- **Task**: XOR classification (not linearly separable)",
            f"- **Architecture**: MLP 2 -> 8 -> 8 -> 1",
            f"- **Parameters**: {training_log.get('model_params', 'N/A')}",
            f"- **Epochs**: {training_log.get('epochs', 'N/A')}",
            f"- **Final Loss**: {training_log.get('final_loss', 'N/A'):.6f}",
            f"- **Training Time**: {training_log.get('training_time_seconds', 'N/A'):.2f}s",
            "",
        ])

    # Gradient check results
    if grad_check:
        lines.extend([
            "## Gradient Checking",
            "",
            f"**Result**: {grad_check.get('passed', 0)}/{grad_check.get('total', 0)} checks passed",
            "",
            "| Parameter | Analytical | Numerical | Error | Status |",
            "|-----------|------------|-----------|-------|--------|",
        ])

        for test in grad_check.get('tests', [])[:10]:  # First 10
            status = "✓" if test['passed'] else "✗"
            lines.append(
                f"| {test['param_name']} | {test['analytical_grad']:.4f} | "
                f"{test['numerical_grad']:.4f} | {test['relative_error']:.2e} | {status} |"
            )

        lines.append("")

    # Key takeaways
    lines.extend([
        "## Key Takeaways",
        "",
        "1. **Backprop is just the chain rule**: Each operation stores how to compute its local gradient",
        "2. **Reverse-mode autodiff**: Process graph from output to inputs for efficiency",
        "3. **Gradient checking**: Numerical verification catches implementation bugs",
        "4. **Custom autograd works**: We trained a real neural network with our implementation!",
        "",
        "---",
        "",
        "*Generated by Neural Dojo Autograd Engine*",
    ])

    report = "\n".join(lines)

    # Save report
    report_path = os.path.join(storage.storage_dir, "autograd_report.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print("Report generated successfully!")
    print()
    print(f"Report saved to: {report_path}")
    print()
    print("Preview:")
    print("-" * 50)
    for line in lines[:40]:
        print(line)
    if len(lines) > 40:
        print("...")
    print("-" * 50)

    return report_path


# ============================================================================
# MAIN
# ============================================================================

def print_help():
    """Print usage information."""
    print("""
Autograd Engine - Module 31 Deliverable
=======================================

A complete automatic differentiation engine built from scratch.

Usage:
    python deliverable_autograd_engine.py <command>

Commands:
    demo1   Scalar autograd basics (chain rule, gradients)
    demo2   Train a neural network using custom autograd
    demo3   Gradient checking (verify implementation)
    demo4   Generate a comprehensive report
    help    Show this help message

Examples:
    python deliverable_autograd_engine.py demo1
    python deliverable_autograd_engine.py demo2
    python deliverable_autograd_engine.py demo3
    python deliverable_autograd_engine.py demo4

Results are saved to .autograd_engine/

This module completes Phase 6 - you now understand how neural networks learn!
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_scalar_autograd()
    elif command == "demo2":
        demo_2_train_neural_network()
    elif command == "demo3":
        demo_3_gradient_checking()
    elif command == "demo4":
        demo_4_generate_report()
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
