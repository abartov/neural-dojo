#!/usr/bin/env python3
"""
Example 01: PyTorch Tensors Basics
==================================

This example covers:
1. Creating tensors
2. Tensor properties and operations
3. NumPy bridge
4. Reshaping and indexing
5. Broadcasting

Module 27: PyTorch Fundamentals
"""

import torch
import numpy as np

def demo_tensor_creation():
    """Demonstrate various ways to create tensors."""
    print("=" * 60)
    print("TENSOR CREATION")
    print("=" * 60)

    # From Python data
    print("\n1. From Python data:")
    t1 = torch.tensor([1, 2, 3, 4, 5])
    print(f"   From list: {t1}")

    t2 = torch.tensor([[1, 2, 3], [4, 5, 6]])
    print(f"   From nested list:\n{t2}")

    # Common initializations
    print("\n2. Common initializations:")
    zeros = torch.zeros(3, 4)
    print(f"   zeros(3, 4):\n{zeros}")

    ones = torch.ones(2, 3)
    print(f"   ones(2, 3):\n{ones}")

    random_uniform = torch.rand(3, 3)
    print(f"   rand(3, 3) - Uniform [0, 1):\n{random_uniform}")

    random_normal = torch.randn(3, 3)
    print(f"   randn(3, 3) - Normal(0, 1):\n{random_normal}")

    # Ranges
    print("\n3. Range tensors:")
    range_t = torch.arange(0, 10, 2)
    print(f"   arange(0, 10, 2): {range_t}")

    linspace = torch.linspace(0, 1, 5)
    print(f"   linspace(0, 1, 5): {linspace}")

    # Special matrices
    print("\n4. Special matrices:")
    eye = torch.eye(4)
    print(f"   eye(4) - Identity:\n{eye}")

    # Like existing tensors
    print("\n5. Like existing tensors:")
    base = torch.randn(2, 3)
    zeros_like = torch.zeros_like(base)
    ones_like = torch.ones_like(base)
    rand_like = torch.rand_like(base)
    print(f"   zeros_like(base):\n{zeros_like}")


def demo_tensor_properties():
    """Demonstrate tensor properties."""
    print("\n" + "=" * 60)
    print("TENSOR PROPERTIES")
    print("=" * 60)

    t = torch.randn(3, 4, 5)

    print(f"\n   Tensor shape: (3, 4, 5)")
    print(f"   t.shape: {t.shape}")
    print(f"   t.size(): {t.size()}")
    print(f"   t.dtype: {t.dtype}")
    print(f"   t.device: {t.device}")
    print(f"   t.ndim: {t.ndim}")
    print(f"   t.numel(): {t.numel()} (total elements)")

    # Data types
    print("\n   Data types:")
    int_tensor = torch.tensor([1, 2, 3], dtype=torch.int32)
    print(f"   int32 tensor: {int_tensor}, dtype: {int_tensor.dtype}")

    float64_tensor = torch.tensor([1.0, 2.0], dtype=torch.float64)
    print(f"   float64 tensor: {float64_tensor}, dtype: {float64_tensor.dtype}")

    # Type conversion
    print("\n   Type conversion:")
    original = torch.tensor([1.5, 2.7, 3.9])
    print(f"   Original: {original}")
    print(f"   .int(): {original.int()}")
    print(f"   .long(): {original.long()}")
    print(f"   .double(): {original.double()}")


def demo_tensor_operations():
    """Demonstrate tensor operations."""
    print("\n" + "=" * 60)
    print("TENSOR OPERATIONS")
    print("=" * 60)

    a = torch.tensor([1.0, 2.0, 3.0, 4.0])
    b = torch.tensor([5.0, 6.0, 7.0, 8.0])

    print(f"\n   a = {a}")
    print(f"   b = {b}")

    # Element-wise operations
    print("\n1. Element-wise operations:")
    print(f"   a + b = {a + b}")
    print(f"   a - b = {a - b}")
    print(f"   a * b = {a * b}")
    print(f"   a / b = {a / b}")
    print(f"   a ** 2 = {a ** 2}")
    print(f"   torch.sqrt(a) = {torch.sqrt(a)}")
    print(f"   torch.exp(a) = {torch.exp(a)}")

    # Aggregation operations
    print("\n2. Aggregation operations:")
    print(f"   a.sum() = {a.sum()}")
    print(f"   a.mean() = {a.mean()}")
    print(f"   a.std() = {a.std():.4f}")
    print(f"   a.min() = {a.min()}")
    print(f"   a.max() = {a.max()}")
    print(f"   a.argmax() = {a.argmax()} (index of max)")

    # Matrix operations
    print("\n3. Matrix operations:")
    A = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    B = torch.tensor([[5.0, 6.0], [7.0, 8.0]])

    print(f"   A:\n{A}")
    print(f"   B:\n{B}")
    print(f"   A @ B (matrix multiply):\n{A @ B}")
    print(f"   A.T (transpose):\n{A.T}")

    # In-place operations
    print("\n4. In-place operations (modify tensor):")
    c = torch.tensor([1.0, 2.0, 3.0])
    print(f"   c = {c}")
    c.add_(10)
    print(f"   c.add_(10) -> c = {c}")
    c.mul_(2)
    print(f"   c.mul_(2) -> c = {c}")


def demo_numpy_bridge():
    """Demonstrate NumPy-PyTorch interoperability."""
    print("\n" + "=" * 60)
    print("NUMPY BRIDGE")
    print("=" * 60)

    # NumPy to PyTorch
    print("\n1. NumPy to PyTorch:")
    np_array = np.array([1.0, 2.0, 3.0, 4.0])
    print(f"   NumPy array: {np_array}")

    # Using from_numpy (shares memory!)
    t_shared = torch.from_numpy(np_array)
    print(f"   torch.from_numpy(): {t_shared}")

    # Using tensor (copies data)
    t_copied = torch.tensor(np_array)
    print(f"   torch.tensor(): {t_copied}")

    # Show memory sharing
    print("\n2. Memory sharing with from_numpy:")
    np_array[0] = 999
    print(f"   Modified np_array[0] = 999")
    print(f"   Shared tensor now: {t_shared}")
    print(f"   Copied tensor unchanged: {t_copied}")

    # PyTorch to NumPy
    print("\n3. PyTorch to NumPy:")
    tensor = torch.tensor([10.0, 20.0, 30.0])
    print(f"   PyTorch tensor: {tensor}")

    np_from_tensor = tensor.numpy()
    print(f"   .numpy(): {np_from_tensor}")
    print(f"   Type: {type(np_from_tensor)}")

    # Safe conversion (for GPU tensors)
    print("\n4. Safe conversion pattern:")
    print("   tensor.detach().cpu().numpy()")
    print("   - detach(): Removes from computation graph")
    print("   - cpu(): Moves to CPU (if on GPU)")
    print("   - numpy(): Converts to NumPy")


def demo_reshaping():
    """Demonstrate reshaping operations."""
    print("\n" + "=" * 60)
    print("RESHAPING TENSORS")
    print("=" * 60)

    # Basic reshape
    x = torch.arange(12)
    print(f"\n   Original: {x}")
    print(f"   Shape: {x.shape}")

    print("\n1. Reshape operations:")
    print(f"   x.reshape(3, 4):\n{x.reshape(3, 4)}")
    print(f"   x.reshape(2, 2, 3):\n{x.reshape(2, 2, 3)}")
    print(f"   x.reshape(-1, 4) (-1 infers dim):\n{x.reshape(-1, 4)}")

    # View vs reshape
    print("\n2. View (memory-efficient):")
    y = x.view(3, 4)
    print(f"   x.view(3, 4):\n{y}")
    print("   Note: view() shares memory with original")

    # Flatten
    print("\n3. Flatten:")
    z = torch.randn(2, 3, 4)
    print(f"   Shape: {z.shape}")
    print(f"   z.flatten().shape: {z.flatten().shape}")
    print(f"   z.flatten(start_dim=1).shape: {z.flatten(start_dim=1).shape}")

    # Squeeze and unsqueeze
    print("\n4. Squeeze and Unsqueeze:")
    w = torch.randn(1, 3, 1, 4)
    print(f"   Original shape: {w.shape}")
    print(f"   w.squeeze().shape: {w.squeeze().shape} (removes all 1s)")
    print(f"   w.squeeze(0).shape: {w.squeeze(0).shape} (remove dim 0)")

    single = torch.randn(5)
    print(f"   single.shape: {single.shape}")
    print(f"   single.unsqueeze(0).shape: {single.unsqueeze(0).shape}")
    print(f"   single.unsqueeze(1).shape: {single.unsqueeze(1).shape}")

    # Stack and concatenate
    print("\n5. Stack and Concatenate:")
    a = torch.randn(3, 4)
    b = torch.randn(3, 4)
    print(f"   a.shape: {a.shape}, b.shape: {b.shape}")
    print(f"   torch.stack([a, b]).shape: {torch.stack([a, b]).shape} (new dim)")
    print(f"   torch.cat([a, b]).shape: {torch.cat([a, b]).shape} (concat dim 0)")
    print(f"   torch.cat([a, b], dim=1).shape: {torch.cat([a, b], dim=1).shape} (concat dim 1)")


def demo_indexing():
    """Demonstrate indexing and slicing."""
    print("\n" + "=" * 60)
    print("INDEXING AND SLICING")
    print("=" * 60)

    x = torch.arange(20).reshape(4, 5)
    print(f"\n   Tensor (4x5):\n{x}")

    # Basic indexing
    print("\n1. Basic indexing:")
    print(f"   x[0]: {x[0]}")
    print(f"   x[0, 0]: {x[0, 0]}")
    print(f"   x[-1]: {x[-1]} (last row)")
    print(f"   x[-1, -1]: {x[-1, -1]} (last element)")

    # Slicing
    print("\n2. Slicing:")
    print(f"   x[1:3]:\n{x[1:3]}")
    print(f"   x[:, 2:4]:\n{x[:, 2:4]}")
    print(f"   x[::2] (every 2nd row):\n{x[::2]}")

    # Boolean indexing
    print("\n3. Boolean indexing:")
    mask = x > 10
    print(f"   Mask (x > 10):\n{mask}")
    print(f"   x[x > 10]: {x[x > 10]}")

    # Fancy indexing
    print("\n4. Fancy indexing:")
    indices = torch.tensor([0, 2, 3])
    print(f"   indices = {indices}")
    print(f"   x[indices]:\n{x[indices]}")


def demo_broadcasting():
    """Demonstrate broadcasting rules."""
    print("\n" + "=" * 60)
    print("BROADCASTING")
    print("=" * 60)

    print("\n   Broadcasting rules:")
    print("   1. Align shapes from the right")
    print("   2. Dimensions must be equal or one must be 1")
    print("   3. Missing dimensions are treated as 1")

    # Scalar broadcast
    print("\n1. Scalar broadcast:")
    a = torch.tensor([1, 2, 3, 4])
    print(f"   a = {a}")
    print(f"   a + 10 = {a + 10}")
    print(f"   a * 2 = {a * 2}")

    # Vector to matrix broadcast
    print("\n2. Vector to matrix broadcast:")
    matrix = torch.arange(12).reshape(3, 4).float()
    row = torch.tensor([100.0, 200.0, 300.0, 400.0])
    col = torch.tensor([[1000.0], [2000.0], [3000.0]])

    print(f"   matrix (3x4):\n{matrix}")
    print(f"   row (4,): {row}")
    print(f"   col (3x1):\n{col}")

    print(f"\n   matrix + row (broadcasts across rows):\n{matrix + row}")
    print(f"\n   matrix + col (broadcasts across cols):\n{matrix + col}")

    # Shape alignment
    print("\n3. Shape alignment example:")
    a = torch.randn(5, 3, 4, 1)
    b = torch.randn(3, 1, 6)
    print(f"   a.shape: {a.shape}")
    print(f"   b.shape: {b.shape}")
    result = a + b
    print(f"   (a + b).shape: {result.shape}")
    print("   Alignment: (5,3,4,1) + (3,1,6) -> (5,3,4,6)")


def demo_device_operations():
    """Demonstrate device operations."""
    print("\n" + "=" * 60)
    print("DEVICE OPERATIONS")
    print("=" * 60)

    # Check CUDA availability
    print(f"\n   torch.cuda.is_available(): {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"   torch.cuda.device_count(): {torch.cuda.device_count()}")
        print(f"   torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")

    # Device selection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n   Using device: {device}")

    # Create tensor on device
    x = torch.randn(3, 3, device=device)
    print(f"\n   Tensor created on {x.device}:")
    print(f"{x}")

    # Move tensor between devices
    cpu_tensor = torch.randn(2, 2)
    print(f"\n   CPU tensor device: {cpu_tensor.device}")

    if torch.cuda.is_available():
        gpu_tensor = cpu_tensor.to(device)
        print(f"   GPU tensor device: {gpu_tensor.device}")

        # Move back
        back_to_cpu = gpu_tensor.cpu()
        print(f"   Back to CPU: {back_to_cpu.device}")
    else:
        print("   (GPU operations skipped - no CUDA)")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("   MODULE 27: PYTORCH TENSORS BASICS")
    print("=" * 60)

    demo_tensor_creation()
    demo_tensor_properties()
    demo_tensor_operations()
    demo_numpy_bridge()
    demo_reshaping()
    demo_indexing()
    demo_broadcasting()
    demo_device_operations()

    print("\n" + "=" * 60)
    print("   SUMMARY")
    print("=" * 60)
    print("""
    Key Takeaways:

    1. Tensors are multi-dimensional arrays (like NumPy arrays)
    2. Creation: zeros, ones, rand, randn, arange, linspace
    3. Properties: shape, dtype, device, ndim, numel
    4. Operations: +, -, *, /, @, and torch functions
    5. NumPy bridge: from_numpy (shares), tensor (copies)
    6. Reshaping: reshape, view, flatten, squeeze, unsqueeze
    7. Indexing: same as NumPy, plus boolean/fancy indexing
    8. Broadcasting: automatic shape expansion
    9. Devices: CPU by default, .to(device) for GPU

    PyTorch tensors are the foundation of all deep learning!
    """)


if __name__ == "__main__":
    main()
