#!/usr/bin/env python3
"""
Module 25 Example 1: NumPy Fundamentals

Demonstrates core NumPy operations with performance benchmarks
comparing NumPy to pure Python implementations.

This is the foundation for all machine learning in Python.
"""

import numpy as np
import time
from typing import Callable, List, Tuple


def benchmark(func: Callable, *args, n_runs: int = 5, **kwargs) -> Tuple[float, any]:
    """
    Benchmark a function and return average execution time.

    Args:
        func: Function to benchmark
        *args: Arguments to pass to function
        n_runs: Number of runs to average
        **kwargs: Keyword arguments to pass to function

    Returns:
        Tuple of (average_time_ms, result)
    """
    times = []
    result = None

    for _ in range(n_runs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds

    return np.mean(times), result


# =============================================================================
# Part 1: Array Creation and Basic Operations
# =============================================================================

def demo_array_creation():
    """Demonstrate various ways to create NumPy arrays."""
    print("\n" + "="*60)
    print("Part 1: Array Creation")
    print("="*60)

    # From Python lists
    arr_1d = np.array([1, 2, 3, 4, 5])
    arr_2d = np.array([[1, 2, 3], [4, 5, 6]])

    print(f"\n1D Array from list: {arr_1d}")
    print(f"   Shape: {arr_1d.shape}, Dtype: {arr_1d.dtype}")

    print(f"\n2D Array from nested list:")
    print(arr_2d)
    print(f"   Shape: {arr_2d.shape}, Dtype: {arr_2d.dtype}")

    # Common initializations
    print("\n--- Common Initializations ---")

    zeros = np.zeros((3, 4))
    print(f"\nZeros (3x4):\n{zeros}")

    ones = np.ones((2, 3))
    print(f"\nOnes (2x3):\n{ones}")

    identity = np.eye(4)
    print(f"\nIdentity (4x4):\n{identity}")

    # Range-based
    print("\n--- Range-based Arrays ---")

    arange = np.arange(0, 10, 2)
    print(f"\narange(0, 10, 2): {arange}")

    linspace = np.linspace(0, 1, 5)
    print(f"linspace(0, 1, 5): {linspace}")

    # Random arrays
    print("\n--- Random Arrays ---")
    np.random.seed(42)  # For reproducibility

    uniform = np.random.rand(3, 3)
    print(f"\nUniform [0,1) (3x3):\n{uniform.round(3)}")

    normal = np.random.randn(3, 3)
    print(f"\nStandard Normal (3x3):\n{normal.round(3)}")

    randint = np.random.randint(0, 10, (3, 3))
    print(f"\nRandom Integers [0,10) (3x3):\n{randint}")


# =============================================================================
# Part 2: Indexing and Slicing
# =============================================================================

def demo_indexing():
    """Demonstrate NumPy indexing and slicing capabilities."""
    print("\n" + "="*60)
    print("Part 2: Indexing and Slicing")
    print("="*60)

    arr = np.array([[1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9, 10, 11, 12]])

    print(f"\nOriginal Array:\n{arr}")

    # Basic indexing
    print("\n--- Basic Indexing ---")
    print(f"arr[0, 0] = {arr[0, 0]}")       # First element
    print(f"arr[1, 2] = {arr[1, 2]}")       # Row 1, Col 2
    print(f"arr[-1, -1] = {arr[-1, -1]}")   # Last element

    # Slicing
    print("\n--- Slicing ---")
    print(f"First row arr[0, :]: {arr[0, :]}")
    print(f"First column arr[:, 0]: {arr[:, 0]}")
    print(f"Submatrix arr[0:2, 1:3]:\n{arr[0:2, 1:3]}")
    print(f"Every other row arr[::2, :]:\n{arr[::2, :]}")

    # Boolean indexing
    print("\n--- Boolean Indexing (Very Powerful!) ---")
    print(f"Elements > 5: {arr[arr > 5]}")
    print(f"Even elements: {arr[arr % 2 == 0]}")

    # Fancy indexing
    print("\n--- Fancy Indexing ---")
    print(f"Rows 0 and 2:\n{arr[[0, 2], :]}")
    print(f"Columns 0 and 3:\n{arr[:, [0, 3]]}")


# =============================================================================
# Part 3: Broadcasting
# =============================================================================

def demo_broadcasting():
    """Demonstrate NumPy's powerful broadcasting feature."""
    print("\n" + "="*60)
    print("Part 3: Broadcasting")
    print("="*60)

    matrix = np.array([[1, 2, 3],
                       [4, 5, 6],
                       [7, 8, 9]])

    print(f"\nOriginal Matrix:\n{matrix}")

    # Scalar broadcast
    print("\n--- Scalar Broadcasting ---")
    result = matrix + 10
    print(f"matrix + 10:\n{result}")

    # Row broadcast
    print("\n--- Row Broadcasting ---")
    row = np.array([100, 200, 300])
    print(f"Row vector: {row}")
    result = matrix + row
    print(f"matrix + row:\n{result}")

    # Column broadcast
    print("\n--- Column Broadcasting ---")
    col = np.array([[1000], [2000], [3000]])
    print(f"Column vector:\n{col}")
    result = matrix + col
    print(f"matrix + col:\n{result}")

    # Broadcasting visualization
    print("\n--- Broadcasting Rules ---")
    print("""
    Shape (3, 4) + Shape (4,)   → Works! (4,) becomes (1, 4), broadcasts to (3, 4)
    Shape (3, 4) + Shape (3,)   → Error! Can't broadcast (3,) to (3, 4)
    Shape (3, 4) + Shape (3, 1) → Works! (3, 1) broadcasts to (3, 4)
    """)


# =============================================================================
# Part 4: Vectorized Operations
# =============================================================================

def demo_vectorized_ops():
    """Demonstrate vectorized operations and universal functions."""
    print("\n" + "="*60)
    print("Part 4: Vectorized Operations")
    print("="*60)

    arr = np.array([1, 4, 9, 16, 25])
    print(f"\nOriginal: {arr}")

    # Universal functions
    print("\n--- Universal Functions (ufuncs) ---")
    print(f"np.sqrt(arr): {np.sqrt(arr)}")
    print(f"np.square(arr): {np.square(arr)}")
    print(f"np.log(arr): {np.log(arr).round(3)}")
    print(f"np.exp(arr/10): {np.exp(arr/10).round(3)}")

    # Trigonometric
    angles = np.array([0, np.pi/4, np.pi/2, np.pi])
    print(f"\nAngles: {angles.round(3)}")
    print(f"np.sin(angles): {np.sin(angles).round(3)}")
    print(f"np.cos(angles): {np.cos(angles).round(3)}")

    # Aggregations
    print("\n--- Aggregations ---")
    data = np.random.randn(1000)
    print(f"1000 random values:")
    print(f"  Sum: {data.sum():.3f}")
    print(f"  Mean: {data.mean():.3f}")
    print(f"  Std: {data.std():.3f}")
    print(f"  Min: {data.min():.3f}")
    print(f"  Max: {data.max():.3f}")
    print(f"  Median: {np.median(data):.3f}")

    # Axis operations
    print("\n--- Axis Operations ---")
    matrix = np.array([[1, 2, 3],
                       [4, 5, 6]])
    print(f"Matrix:\n{matrix}")
    print(f"Sum all: {matrix.sum()}")
    print(f"Sum axis=0 (columns): {matrix.sum(axis=0)}")
    print(f"Sum axis=1 (rows): {matrix.sum(axis=1)}")


# =============================================================================
# Part 5: Linear Algebra
# =============================================================================

def demo_linear_algebra():
    """Demonstrate linear algebra operations essential for ML."""
    print("\n" + "="*60)
    print("Part 5: Linear Algebra")
    print("="*60)

    A = np.array([[1, 2],
                  [3, 4]])
    B = np.array([[5, 6],
                  [7, 8]])

    print(f"\nMatrix A:\n{A}")
    print(f"\nMatrix B:\n{B}")

    # Matrix operations
    print("\n--- Matrix Operations ---")
    print(f"A @ B (matrix multiplication):\n{A @ B}")
    print(f"A.T (transpose):\n{A.T}")
    print(f"np.linalg.det(A) (determinant): {np.linalg.det(A):.3f}")

    # Inverse
    print("\n--- Matrix Inverse ---")
    A_inv = np.linalg.inv(A)
    print(f"A inverse:\n{A_inv}")
    print(f"A @ A_inv (should be identity):\n{(A @ A_inv).round(10)}")

    # Eigenvalues
    print("\n--- Eigenvalues and Eigenvectors ---")
    eigenvalues, eigenvectors = np.linalg.eig(A)
    print(f"Eigenvalues: {eigenvalues}")
    print(f"Eigenvectors:\n{eigenvectors}")

    # Solving linear systems
    print("\n--- Solving Linear Systems (Ax = b) ---")
    b = np.array([1, 2])
    x = np.linalg.solve(A, b)
    print(f"A:\n{A}")
    print(f"b: {b}")
    print(f"Solution x: {x}")
    print(f"Verify A @ x = {A @ x}")

    # SVD (crucial for dimensionality reduction)
    print("\n--- Singular Value Decomposition (SVD) ---")
    U, S, Vt = np.linalg.svd(A)
    print(f"U:\n{U.round(3)}")
    print(f"Singular values: {S.round(3)}")
    print(f"Vt:\n{Vt.round(3)}")


# =============================================================================
# Part 6: Performance Benchmarks - NumPy vs Pure Python
# =============================================================================

def python_dot_product(a: List[float], b: List[float]) -> float:
    """Pure Python dot product."""
    return sum(x * y for x, y in zip(a, b))


def python_matrix_multiply(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """Pure Python matrix multiplication."""
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])

    result = [[0 for _ in range(cols_B)] for _ in range(rows_A)]

    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]

    return result


def python_element_wise_add(a: List[float], b: List[float]) -> List[float]:
    """Pure Python element-wise addition."""
    return [x + y for x, y in zip(a, b)]


def demo_performance_benchmarks():
    """Compare NumPy vs pure Python performance."""
    print("\n" + "="*60)
    print("Part 6: Performance Benchmarks")
    print("="*60)
    print("\nComparing NumPy (optimized C) vs Pure Python (interpreted)")

    sizes = [100, 1000, 10000, 100000]

    print("\n--- Vector Operations ---")
    print(f"{'Size':<10} {'Python (ms)':<15} {'NumPy (ms)':<15} {'Speedup':<10}")
    print("-" * 50)

    for size in sizes:
        # Create data
        py_a = list(range(size))
        py_b = list(range(size))
        np_a = np.arange(size)
        np_b = np.arange(size)

        # Benchmark element-wise addition
        py_time, _ = benchmark(python_element_wise_add, py_a, py_b)
        np_time, _ = benchmark(lambda: np_a + np_b)

        speedup = py_time / np_time if np_time > 0 else float('inf')
        print(f"{size:<10} {py_time:<15.3f} {np_time:<15.3f} {speedup:<10.1f}x")

    # Matrix multiplication benchmark
    print("\n--- Matrix Multiplication ---")
    print(f"{'Size':<10} {'Python (ms)':<15} {'NumPy (ms)':<15} {'Speedup':<10}")
    print("-" * 50)

    matrix_sizes = [10, 50, 100, 200]

    for size in matrix_sizes:
        # Create data
        py_A = [[float(i + j) for j in range(size)] for i in range(size)]
        py_B = [[float(i * j) for j in range(size)] for i in range(size)]
        np_A = np.array(py_A)
        np_B = np.array(py_B)

        # Only benchmark Python for smaller sizes (it's very slow!)
        if size <= 100:
            py_time, _ = benchmark(python_matrix_multiply, py_A, py_B, n_runs=1)
        else:
            py_time = float('inf')

        np_time, _ = benchmark(lambda: np_A @ np_B)

        if py_time < float('inf'):
            speedup = py_time / np_time
            print(f"{size}x{size:<6} {py_time:<15.3f} {np_time:<15.3f} {speedup:<10.1f}x")
        else:
            print(f"{size}x{size:<6} {'(too slow)':<15} {np_time:<15.3f} {'>>1000':<10}x")

    # Dot product benchmark
    print("\n--- Dot Product ---")
    size = 100000
    py_a = list(range(size))
    py_b = list(range(size))
    np_a = np.arange(size, dtype=np.float64)
    np_b = np.arange(size, dtype=np.float64)

    py_time, py_result = benchmark(python_dot_product, py_a, py_b)
    np_time, np_result = benchmark(lambda: np.dot(np_a, np_b))

    print(f"Size: {size:,}")
    print(f"Python: {py_time:.3f}ms (result: {py_result:,.0f})")
    print(f"NumPy:  {np_time:.3f}ms (result: {np_result:,.0f})")
    print(f"Speedup: {py_time/np_time:.1f}x")

    # Memory comparison
    print("\n--- Memory Usage ---")
    size = 1_000_000

    # Python list of integers
    py_list = list(range(size))
    py_mem = py_list.__sizeof__() + sum(x.__sizeof__() for x in py_list[:1000]) * (size // 1000)

    # NumPy array
    np_arr = np.arange(size, dtype=np.int64)
    np_mem = np_arr.nbytes

    print(f"Storing {size:,} integers:")
    print(f"Python list: ~{py_mem / 1e6:.1f} MB")
    print(f"NumPy array: {np_mem / 1e6:.1f} MB")
    print(f"Memory savings: {py_mem / np_mem:.1f}x")


# =============================================================================
# Part 7: Real-World ML Operations
# =============================================================================

def demo_ml_operations():
    """Demonstrate NumPy operations commonly used in ML."""
    print("\n" + "="*60)
    print("Part 7: Real-World ML Operations")
    print("="*60)

    np.random.seed(42)

    # Normalization (StandardScaler equivalent)
    print("\n--- Feature Normalization ---")
    data = np.random.randn(100, 4) * np.array([10, 100, 1000, 1]) + np.array([5, 50, 500, 0])
    print(f"Original stats:")
    print(f"  Means: {data.mean(axis=0).round(2)}")
    print(f"  Stds:  {data.std(axis=0).round(2)}")

    # Standardize: (x - mean) / std
    normalized = (data - data.mean(axis=0)) / data.std(axis=0)
    print(f"\nNormalized stats:")
    print(f"  Means: {normalized.mean(axis=0).round(2)}")
    print(f"  Stds:  {normalized.std(axis=0).round(2)}")

    # One-hot encoding
    print("\n--- One-Hot Encoding ---")
    labels = np.array([0, 1, 2, 0, 1])
    n_classes = 3
    one_hot = np.eye(n_classes)[labels]
    print(f"Labels: {labels}")
    print(f"One-hot encoded:\n{one_hot.astype(int)}")

    # Softmax (for neural network outputs)
    print("\n--- Softmax Function ---")
    logits = np.array([2.0, 1.0, 0.1])
    exp_logits = np.exp(logits - logits.max())  # Subtract max for numerical stability
    softmax = exp_logits / exp_logits.sum()
    print(f"Logits: {logits}")
    print(f"Softmax probabilities: {softmax.round(3)}")
    print(f"Sum: {softmax.sum():.3f}")

    # Cross-entropy loss
    print("\n--- Cross-Entropy Loss ---")
    predictions = np.array([0.7, 0.2, 0.1])
    true_label = 0  # Class 0 is correct
    loss = -np.log(predictions[true_label])
    print(f"Predictions: {predictions}")
    print(f"True label: {true_label}")
    print(f"Cross-entropy loss: {loss:.3f}")

    # Batch operations
    print("\n--- Batch Matrix Operations ---")
    batch_size = 32
    input_dim = 10
    output_dim = 5

    # Simulating a neural network layer: Y = XW + b
    X = np.random.randn(batch_size, input_dim)  # Input batch
    W = np.random.randn(input_dim, output_dim)  # Weights
    b = np.random.randn(output_dim)             # Bias

    Y = X @ W + b  # Broadcasting handles bias addition!

    print(f"Input X: {X.shape}")
    print(f"Weights W: {W.shape}")
    print(f"Bias b: {b.shape}")
    print(f"Output Y: {Y.shape}")

    # Gradient computation (simplified)
    print("\n--- Gradient Computation (Simplified) ---")
    # For Y = XW + b, gradient of loss w.r.t. W is X^T @ dL/dY
    dL_dY = np.random.randn(batch_size, output_dim)  # Upstream gradient
    dL_dW = X.T @ dL_dY  # Weight gradient
    dL_db = dL_dY.sum(axis=0)  # Bias gradient

    print(f"Weight gradient shape: {dL_dW.shape}")
    print(f"Bias gradient shape: {dL_db.shape}")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Module 25: NumPy Fundamentals")
    print("The Foundation of Machine Learning in Python")
    print("="*60)

    # Run all demonstrations
    demo_array_creation()
    demo_indexing()
    demo_broadcasting()
    demo_vectorized_ops()
    demo_linear_algebra()
    demo_performance_benchmarks()
    demo_ml_operations()

    print("\n" + "="*60)
    print("NumPy Fundamentals Complete!")
    print("="*60)
    print("""
Key Takeaways:
1. NumPy arrays are 10-1000x faster than Python lists
2. Broadcasting enables elegant, efficient operations
3. Linear algebra operations are essential for ML
4. Vectorize everything - avoid Python loops!

Next: example_02_pandas_essentials.py
    """)
