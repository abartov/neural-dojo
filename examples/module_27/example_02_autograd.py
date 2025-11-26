#!/usr/bin/env python3
"""
Example 02: PyTorch Autograd - Automatic Differentiation
========================================================

This example covers:
1. Basic gradient computation
2. The computational graph
3. Chain rule in action
4. Gradient accumulation
5. Detaching from the graph
6. Comparing with manual gradients

Module 27: PyTorch Fundamentals
"""

import torch
import numpy as np


def demo_basic_gradients():
    """Demonstrate basic gradient computation."""
    print("=" * 60)
    print("BASIC GRADIENT COMPUTATION")
    print("=" * 60)

    # Simple gradient
    print("\n1. Simple gradient (y = x^2):")
    x = torch.tensor([2.0], requires_grad=True)
    y = x ** 2
    print(f"   x = {x.item()}")
    print(f"   y = x^2 = {y.item()}")

    y.backward()  # Compute dy/dx
    print(f"   dy/dx = 2x = {x.grad.item()}")
    print(f"   (Expected: 2 * 2 = 4)")

    # Multiple inputs
    print("\n2. Multiple inputs (z = x^2 + y^3):")
    x = torch.tensor([2.0], requires_grad=True)
    y = torch.tensor([3.0], requires_grad=True)
    z = x ** 2 + y ** 3

    print(f"   x = {x.item()}, y = {y.item()}")
    print(f"   z = x^2 + y^3 = {z.item()}")

    z.backward()
    print(f"   dz/dx = 2x = {x.grad.item()}")
    print(f"   dz/dy = 3y^2 = {y.grad.item()}")

    # Vector input, scalar output
    print("\n3. Vector input, scalar output:")
    x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
    y = x.sum() ** 2  # y = (x1 + x2 + x3)^2 = 36

    print(f"   x = {x.data}")
    print(f"   y = sum(x)^2 = {y.item()}")

    y.backward()
    print(f"   dy/dx = 2*sum(x) = {x.grad}")
    print(f"   (Expected: 2 * 6 = [12, 12, 12])")


def demo_chain_rule():
    """Demonstrate chain rule through composed functions."""
    print("\n" + "=" * 60)
    print("CHAIN RULE IN ACTION")
    print("=" * 60)

    print("\n   Computing gradients through composed functions:")
    print("   f(x) = (x^2 + 1)^3")
    print("   Let u = x^2 + 1, then f = u^3")
    print("   df/dx = df/du * du/dx = 3u^2 * 2x = 6x(x^2 + 1)^2")

    x = torch.tensor([2.0], requires_grad=True)

    # Step by step
    u = x ** 2 + 1     # u = 5
    f = u ** 3         # f = 125

    f.backward()

    print(f"\n   x = {x.item()}")
    print(f"   u = x^2 + 1 = {u.item()}")
    print(f"   f = u^3 = {f.item()}")
    print(f"   df/dx = {x.grad.item()}")

    # Manual verification
    manual_grad = 6 * 2 * (2**2 + 1)**2
    print(f"   Manual: 6x(x^2+1)^2 = 6*2*25 = {manual_grad}")


def demo_computational_graph():
    """Demonstrate the computational graph concept."""
    print("\n" + "=" * 60)
    print("COMPUTATIONAL GRAPH")
    print("=" * 60)

    print("""
    When requires_grad=True, PyTorch builds a graph:

         x (leaf)
          |
         [*2]  --> a = 2x
          |
         [**2] --> b = a^2 = 4x^2
          |
         [sum] --> c = sum(b)
          |
      backward()
    """)

    x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)

    # Build the graph
    a = x * 2
    b = a ** 2
    c = b.sum()

    print(f"   x = {x.data}")
    print(f"   a = 2x = {a.data}")
    print(f"   b = a^2 = {b.data}")
    print(f"   c = sum(b) = {c.item()}")

    # Inspect graph
    print(f"\n   Graph information:")
    print(f"   x.requires_grad: {x.requires_grad}")
    print(f"   x.is_leaf: {x.is_leaf}")
    print(f"   a.is_leaf: {a.is_leaf}")
    print(f"   c.grad_fn: {c.grad_fn}")

    # Backward pass
    c.backward()
    print(f"\n   After backward():")
    print(f"   x.grad = {x.grad}")
    print(f"   (Expected: d(sum(4x^2))/dx = 8x = [8, 16, 24])")


def demo_gradient_accumulation():
    """Demonstrate gradient accumulation behavior."""
    print("\n" + "=" * 60)
    print("GRADIENT ACCUMULATION")
    print("=" * 60)

    print("\n   Key insight: Gradients ACCUMULATE by default!")

    x = torch.tensor([1.0], requires_grad=True)

    # First backward
    y1 = x * 2
    y1.backward()
    print(f"\n   After first backward (y = 2x):")
    print(f"   x.grad = {x.grad.item()}")

    # Second backward - gradients accumulate!
    y2 = x * 3
    y2.backward()
    print(f"\n   After second backward (y = 3x), WITHOUT zeroing:")
    print(f"   x.grad = {x.grad.item()} (accumulated: 2 + 3 = 5)")

    # Zero gradients
    x.grad.zero_()
    print(f"\n   After x.grad.zero_():")
    print(f"   x.grad = {x.grad.item()}")

    # Third backward - fresh gradient
    y3 = x * 4
    y3.backward()
    print(f"\n   After third backward (y = 4x):")
    print(f"   x.grad = {x.grad.item()}")

    print("""
    Why accumulation?
    - Useful for gradient accumulation across mini-batches
    - Enables larger effective batch sizes on limited memory
    - But remember: always zero_grad() in training loops!
    """)


def demo_detaching():
    """Demonstrate detaching from computational graph."""
    print("\n" + "=" * 60)
    print("DETACHING FROM GRAPH")
    print("=" * 60)

    print("\n1. Using .detach():")
    x = torch.tensor([2.0], requires_grad=True)
    y = x ** 2
    z = y.detach()  # z is a new tensor, not tracking gradients

    print(f"   x = {x.item()}, requires_grad: {x.requires_grad}")
    print(f"   y = x^2 = {y.item()}, requires_grad: {y.requires_grad}")
    print(f"   z = y.detach() = {z.item()}, requires_grad: {z.requires_grad}")

    print("\n2. Using torch.no_grad():")
    x = torch.tensor([3.0], requires_grad=True)

    with torch.no_grad():
        y = x ** 2
        print(f"   Inside no_grad: y.requires_grad = {y.requires_grad}")

    # Outside the context, new computations track again
    z = x ** 2
    print(f"   Outside no_grad: z.requires_grad = {z.requires_grad}")

    print("""
    Common uses:
    - Inference: with torch.no_grad(): predictions = model(data)
    - Freezing layers: param.requires_grad = False
    - Computing metrics without affecting gradients
    """)


def demo_comparing_manual():
    """Compare autograd with manual gradient computation."""
    print("\n" + "=" * 60)
    print("AUTOGRAD VS MANUAL GRADIENTS")
    print("=" * 60)

    print("\n   Function: Loss = mean((Wx + b - y)^2)")
    print("   This is linear regression!")

    # Setup
    torch.manual_seed(42)
    X = torch.randn(100, 5)
    y_true = torch.randn(100)

    W = torch.randn(5, requires_grad=True)
    b = torch.zeros(1, requires_grad=True)

    # Forward pass
    y_pred = X @ W + b
    loss = ((y_pred - y_true) ** 2).mean()

    print(f"\n   Input shape: {X.shape}")
    print(f"   W shape: {W.shape}")
    print(f"   Loss: {loss.item():.4f}")

    # Autograd
    loss.backward()
    autograd_W = W.grad.clone()
    autograd_b = b.grad.clone()

    print(f"\n   Autograd gradients:")
    print(f"   dL/dW[:3]: {autograd_W[:3]}")
    print(f"   dL/db: {autograd_b.item():.4f}")

    # Manual gradient computation
    # L = mean((Xw + b - y)^2)
    # dL/dW = (2/n) * X.T @ (Xw + b - y)
    # dL/db = (2/n) * sum(Xw + b - y)
    residual = y_pred.detach() - y_true
    manual_W = (2 / len(y_true)) * (X.T @ residual)
    manual_b = (2 / len(y_true)) * residual.sum()

    print(f"\n   Manual gradients:")
    print(f"   dL/dW[:3]: {manual_W[:3]}")
    print(f"   dL/db: {manual_b.item():.4f}")

    # Verify
    diff_W = (autograd_W - manual_W).abs().max().item()
    diff_b = (autograd_b - manual_b).abs().item()

    print(f"\n   Verification (should be ~0):")
    print(f"   Max diff in W: {diff_W:.2e}")
    print(f"   Diff in b: {diff_b:.2e}")


def demo_higher_order():
    """Demonstrate higher-order gradients."""
    print("\n" + "=" * 60)
    print("HIGHER-ORDER GRADIENTS")
    print("=" * 60)

    print("\n   Computing second derivative of f(x) = x^3")
    print("   f'(x) = 3x^2")
    print("   f''(x) = 6x")

    x = torch.tensor([2.0], requires_grad=True)

    # First derivative
    y = x ** 3
    grad1 = torch.autograd.grad(y, x, create_graph=True)[0]
    print(f"\n   x = {x.item()}")
    print(f"   f(x) = x^3 = {y.item()}")
    print(f"   f'(x) = 3x^2 = {grad1.item()} (expected: 12)")

    # Second derivative
    grad2 = torch.autograd.grad(grad1, x)[0]
    print(f"   f''(x) = 6x = {grad2.item()} (expected: 12)")


def demo_gradient_flow():
    """Visualize gradient flow through a small network."""
    print("\n" + "=" * 60)
    print("GRADIENT FLOW VISUALIZATION")
    print("=" * 60)

    print("""
    Simple 2-layer network:
    input (2) -> hidden (3) -> output (1)

        x1 ----
                \\
        x2 ---- W1 --> h1, h2, h3 -- W2 --> y
                /
         bias1
    """)

    torch.manual_seed(42)

    # Input
    x = torch.tensor([[1.0, 2.0]])  # [1, 2]

    # Layer 1: 2 -> 3
    W1 = torch.randn(2, 3, requires_grad=True)
    b1 = torch.zeros(3, requires_grad=True)

    # Layer 2: 3 -> 1
    W2 = torch.randn(3, 1, requires_grad=True)
    b2 = torch.zeros(1, requires_grad=True)

    # Forward pass
    h = torch.relu(x @ W1 + b1)  # Hidden layer with ReLU
    y = h @ W2 + b2               # Output

    # Target and loss
    target = torch.tensor([[1.0]])
    loss = ((y - target) ** 2).mean()

    print(f"   Input: {x}")
    print(f"   Hidden: {h}")
    print(f"   Output: {y.item():.4f}")
    print(f"   Target: {target.item()}")
    print(f"   Loss: {loss.item():.4f}")

    # Backward pass
    loss.backward()

    print(f"\n   Gradients after backward():")
    print(f"   W2.grad:\n{W2.grad}")
    print(f"   W1.grad:\n{W1.grad}")
    print(f"   b2.grad: {b2.grad}")
    print(f"   b1.grad: {b1.grad}")

    print("""
    Notice:
    - Gradients flow from loss back to all parameters
    - W2 (closer to output) typically has larger gradients
    - This is the foundation of neural network training!
    """)


def demo_retain_graph():
    """Demonstrate retain_graph for multiple backward passes."""
    print("\n" + "=" * 60)
    print("RETAIN GRAPH")
    print("=" * 60)

    x = torch.tensor([3.0], requires_grad=True)
    y = x ** 2

    print("   Without retain_graph:")
    print("   y.backward() - works")
    print("   y.backward() again - ERROR (graph freed)")

    print("\n   With retain_graph=True:")

    # First backward with retain
    y = x ** 2  # Recreate
    y.backward(retain_graph=True)
    print(f"   First backward: x.grad = {x.grad.item()}")

    # Second backward (graph still exists)
    x.grad.zero_()
    y.backward(retain_graph=True)
    print(f"   Second backward: x.grad = {x.grad.item()}")

    print("""
    Use cases for retain_graph:
    - Computing gradients for multiple losses
    - GAN training (generator and discriminator)
    - Multi-task learning
    """)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("   MODULE 27: PYTORCH AUTOGRAD")
    print("=" * 60)

    demo_basic_gradients()
    demo_chain_rule()
    demo_computational_graph()
    demo_gradient_accumulation()
    demo_detaching()
    demo_comparing_manual()
    demo_higher_order()
    demo_gradient_flow()
    demo_retain_graph()

    print("\n" + "=" * 60)
    print("   SUMMARY")
    print("=" * 60)
    print("""
    Key Takeaways:

    1. requires_grad=True enables gradient tracking
    2. .backward() computes gradients via backpropagation
    3. Gradients are stored in .grad attribute
    4. Gradients ACCUMULATE - always zero_grad() first
    5. .detach() and no_grad() stop gradient tracking
    6. Chain rule is applied automatically
    7. create_graph=True enables higher-order gradients

    The magic of autograd:
    - You define the forward pass
    - PyTorch computes the backward pass automatically
    - No manual derivative calculation needed!

    This is why PyTorch is so popular for research.
    """)


if __name__ == "__main__":
    main()
