#!/usr/bin/env python3
"""
Module 27 Deliverable: PyTorch Lab
==================================

A comprehensive PyTorch learning toolkit that demonstrates:
- Tensor operations and performance benchmarks
- Autograd visualization
- Network architecture builder
- Training experiments with different hyperparameters
- GPU vs CPU comparison

Usage:
    python deliverable_pytorch_lab.py demo1  # Tensor benchmarks
    python deliverable_pytorch_lab.py demo2  # Autograd visualizer
    python deliverable_pytorch_lab.py demo3  # Architecture builder
    python deliverable_pytorch_lab.py demo4  # Training lab
    python deliverable_pytorch_lab.py demo5  # Full experiment

Author: Neural Dojo
"""

import json
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import warnings

warnings.filterwarnings('ignore')

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

# Storage directory
STORAGE_DIR = Path(".pytorch_lab")
STORAGE_DIR.mkdir(exist_ok=True)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BenchmarkResult:
    """Result of a tensor benchmark."""
    operation: str
    pytorch_time_ms: float
    numpy_time_ms: float
    speedup: float
    shape: str


@dataclass
class GradientInfo:
    """Information about gradient computation."""
    variable: str
    value: float
    gradient: float
    formula: str


@dataclass
class LayerSpec:
    """Specification for a network layer."""
    layer_type: str
    in_features: int
    out_features: int
    activation: Optional[str] = None
    dropout: float = 0.0


@dataclass
class TrainingConfig:
    """Configuration for training experiment."""
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 20
    optimizer: str = "adam"
    hidden_sizes: List[int] = field(default_factory=lambda: [128, 64])
    dropout_rate: float = 0.2
    weight_decay: float = 0.0


@dataclass
class TrainingResult:
    """Result of a training experiment."""
    config: Dict[str, Any]
    train_losses: List[float]
    train_accs: List[float]
    test_losses: List[float]
    test_accs: List[float]
    final_accuracy: float
    training_time: float
    total_params: int


@dataclass
class ExperimentLog:
    """Log of all experiments."""
    experiments: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# TENSOR BENCHMARKER
# =============================================================================

class TensorBenchmarker:
    """Benchmark PyTorch tensor operations."""

    def __init__(self, sizes: List[Tuple[int, ...]] = None):
        self.sizes = sizes or [(100, 100), (1000, 1000), (5000, 5000)]
        self.results: List[BenchmarkResult] = []

    def benchmark_operation(self, name: str, pytorch_fn, numpy_fn,
                           shape: Tuple[int, ...], n_runs: int = 10) -> BenchmarkResult:
        """Benchmark a single operation."""
        # PyTorch
        torch_times = []
        for _ in range(n_runs):
            t = torch.randn(*shape)
            start = time.perf_counter()
            pytorch_fn(t)
            torch_times.append(time.perf_counter() - start)
        pytorch_time = np.median(torch_times) * 1000  # ms

        # NumPy
        numpy_times = []
        for _ in range(n_runs):
            a = np.random.randn(*shape).astype(np.float32)
            start = time.perf_counter()
            numpy_fn(a)
            numpy_times.append(time.perf_counter() - start)
        numpy_time = np.median(numpy_times) * 1000  # ms

        speedup = numpy_time / pytorch_time if pytorch_time > 0 else 0

        return BenchmarkResult(
            operation=name,
            pytorch_time_ms=round(pytorch_time, 4),
            numpy_time_ms=round(numpy_time, 4),
            speedup=round(speedup, 2),
            shape=str(shape)
        )

    def run_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        print("\n" + "=" * 70)
        print("  PYTORCH TENSOR BENCHMARKS")
        print("=" * 70)

        operations = [
            ("Element-wise multiply", lambda t: t * t, lambda a: a * a),
            ("Matrix multiply", lambda t: t @ t.T, lambda a: a @ a.T),
            ("Sum reduction", lambda t: t.sum(), lambda a: a.sum()),
            ("Mean", lambda t: t.mean(), lambda a: a.mean()),
            ("Sqrt", lambda t: torch.sqrt(torch.abs(t)), lambda a: np.sqrt(np.abs(a))),
            ("Exp", lambda t: torch.exp(t), lambda a: np.exp(a)),
            ("Transpose", lambda t: t.T.contiguous(), lambda a: a.T.copy()),
        ]

        self.results = []

        for size in self.sizes:
            print(f"\n  Shape: {size}")
            print("-" * 70)
            print(f"  {'Operation':<25} {'PyTorch (ms)':<15} {'NumPy (ms)':<15} {'Speedup':<10}")
            print("-" * 70)

            for name, pytorch_fn, numpy_fn in operations:
                result = self.benchmark_operation(name, pytorch_fn, numpy_fn, size)
                self.results.append(result)

                speedup_str = f"{result.speedup:.2f}x"
                if result.speedup > 1:
                    speedup_str = f"{speedup_str} faster"
                else:
                    speedup_str = f"{1/result.speedup:.2f}x slower"

                print(f"  {name:<25} {result.pytorch_time_ms:<15.4f} {result.numpy_time_ms:<15.4f} {speedup_str}")

        return self.results

    def check_gpu(self) -> Dict[str, Any]:
        """Check GPU availability and performance."""
        print("\n" + "=" * 70)
        print("  GPU CHECK")
        print("=" * 70)

        info = {
            "cuda_available": torch.cuda.is_available(),
            "device_count": 0,
            "device_name": None,
            "gpu_speedup": None
        }

        print(f"\n  CUDA available: {info['cuda_available']}")

        if info['cuda_available']:
            info['device_count'] = torch.cuda.device_count()
            info['device_name'] = torch.cuda.get_device_name(0)
            print(f"  Device count: {info['device_count']}")
            print(f"  Device name: {info['device_name']}")

            # Benchmark GPU vs CPU
            print("\n  GPU vs CPU benchmark (5000x5000 matrix multiply):")

            size = (5000, 5000)

            # CPU
            a_cpu = torch.randn(*size)
            start = time.perf_counter()
            _ = a_cpu @ a_cpu.T
            cpu_time = time.perf_counter() - start

            # GPU
            a_gpu = torch.randn(*size, device='cuda')
            torch.cuda.synchronize()
            start = time.perf_counter()
            _ = a_gpu @ a_gpu.T
            torch.cuda.synchronize()
            gpu_time = time.perf_counter() - start

            info['gpu_speedup'] = round(cpu_time / gpu_time, 2)

            print(f"  CPU time: {cpu_time*1000:.2f} ms")
            print(f"  GPU time: {gpu_time*1000:.2f} ms")
            print(f"  GPU speedup: {info['gpu_speedup']:.2f}x")
        else:
            print("  No GPU available. Running on CPU.")

        return info


# =============================================================================
# AUTOGRAD VISUALIZER
# =============================================================================

class AutogradVisualizer:
    """Visualize autograd computations."""

    def __init__(self):
        self.gradients: List[GradientInfo] = []

    def visualize_simple(self, x_val: float = 3.0) -> List[GradientInfo]:
        """Visualize simple gradient computation."""
        print("\n" + "=" * 70)
        print("  AUTOGRAD VISUALIZATION: Simple Gradients")
        print("=" * 70)

        self.gradients = []

        print("\n  Computing gradients for various functions at x =", x_val)
        print("-" * 70)

        functions = [
            ("y = x^2", lambda x: x ** 2, "2x"),
            ("y = x^3", lambda x: x ** 3, "3x^2"),
            ("y = sin(x)", lambda x: torch.sin(x), "cos(x)"),
            ("y = exp(x)", lambda x: torch.exp(x), "exp(x)"),
            ("y = log(x)", lambda x: torch.log(x), "1/x"),
            ("y = 1/x", lambda x: 1 / x, "-1/x^2"),
            ("y = sqrt(x)", lambda x: torch.sqrt(x), "1/(2*sqrt(x))"),
        ]

        print(f"\n  {'Function':<20} {'f(x)':<15} {'df/dx':<15} {'Formula':<15}")
        print("-" * 70)

        for name, fn, formula in functions:
            x = torch.tensor([x_val], requires_grad=True)
            y = fn(x)
            y.backward()

            grad_info = GradientInfo(
                variable=name,
                value=round(y.item(), 4),
                gradient=round(x.grad.item(), 4),
                formula=formula
            )
            self.gradients.append(grad_info)

            print(f"  {name:<20} {y.item():<15.4f} {x.grad.item():<15.4f} {formula}")

        return self.gradients

    def visualize_chain_rule(self) -> List[GradientInfo]:
        """Visualize chain rule in action."""
        print("\n" + "=" * 70)
        print("  AUTOGRAD VISUALIZATION: Chain Rule")
        print("=" * 70)

        print("\n  Computing f(x) = sin(x^2) at x = 2.0")
        print("  Using chain rule: df/dx = cos(x^2) * 2x")

        x = torch.tensor([2.0], requires_grad=True)
        u = x ** 2
        f = torch.sin(u)
        f.backward()

        print(f"\n  x = {x.item()}")
        print(f"  u = x^2 = {u.item()}")
        print(f"  f = sin(u) = {f.item():.4f}")
        print(f"  df/dx = {x.grad.item():.4f}")

        # Manual verification
        manual_grad = torch.cos(torch.tensor([4.0])) * 2 * 2
        print(f"  Manual: cos(4) * 4 = {manual_grad.item():.4f}")

        return self.gradients

    def visualize_neural_network_gradients(self):
        """Visualize gradients through a neural network."""
        print("\n" + "=" * 70)
        print("  AUTOGRAD VISUALIZATION: Neural Network Gradients")
        print("=" * 70)

        torch.manual_seed(42)

        # Simple network
        x = torch.randn(1, 4)
        target = torch.tensor([[1.0]])

        W1 = torch.randn(4, 3, requires_grad=True)
        b1 = torch.zeros(3, requires_grad=True)
        W2 = torch.randn(3, 1, requires_grad=True)
        b2 = torch.zeros(1, requires_grad=True)

        print("\n  Network: Input(4) -> Hidden(3) -> Output(1)")
        print(f"  Input: {x}")

        # Forward pass
        h = torch.relu(x @ W1 + b1)
        y = h @ W2 + b2
        loss = F.mse_loss(y, target)

        print(f"  Hidden: {h}")
        print(f"  Output: {y.item():.4f}")
        print(f"  Target: {target.item()}")
        print(f"  Loss (MSE): {loss.item():.4f}")

        # Backward pass
        loss.backward()

        print("\n  Gradients after backward():")
        print(f"  W2.grad norm: {W2.grad.norm().item():.4f}")
        print(f"  b2.grad: {b2.grad}")
        print(f"  W1.grad norm: {W1.grad.norm().item():.4f}")
        print(f"  b1.grad: {b1.grad}")

        print("\n  Observation: Gradients flow from output layer back to input layer")


# =============================================================================
# ARCHITECTURE BUILDER
# =============================================================================

class ArchitectureBuilder:
    """Build and analyze neural network architectures."""

    def __init__(self):
        self.architectures: Dict[str, nn.Module] = {}

    def build_mlp(self, name: str, input_size: int, hidden_sizes: List[int],
                  output_size: int, activation: str = "relu",
                  dropout: float = 0.0) -> nn.Module:
        """Build a multi-layer perceptron."""
        layers = []
        prev_size = input_size

        for i, hidden_size in enumerate(hidden_sizes):
            layers.append(nn.Linear(prev_size, hidden_size))

            if activation == "relu":
                layers.append(nn.ReLU())
            elif activation == "tanh":
                layers.append(nn.Tanh())
            elif activation == "leaky_relu":
                layers.append(nn.LeakyReLU(0.1))
            elif activation == "gelu":
                layers.append(nn.GELU())

            if dropout > 0:
                layers.append(nn.Dropout(dropout))

            prev_size = hidden_size

        layers.append(nn.Linear(prev_size, output_size))

        model = nn.Sequential(*layers)
        self.architectures[name] = model

        return model

    def analyze_architecture(self, model: nn.Module) -> Dict[str, Any]:
        """Analyze a model architecture."""
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        layer_info = []
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                layer_info.append({
                    "name": name,
                    "type": "Linear",
                    "in_features": module.in_features,
                    "out_features": module.out_features,
                    "params": module.weight.numel() + (module.bias.numel() if module.bias is not None else 0)
                })
            elif isinstance(module, (nn.ReLU, nn.Tanh, nn.GELU)):
                layer_info.append({
                    "name": name,
                    "type": type(module).__name__,
                    "params": 0
                })
            elif isinstance(module, nn.Dropout):
                layer_info.append({
                    "name": name,
                    "type": "Dropout",
                    "p": module.p,
                    "params": 0
                })

        return {
            "total_params": total_params,
            "trainable_params": trainable_params,
            "layers": layer_info,
            "depth": len([l for l in layer_info if l.get("type") == "Linear"])
        }

    def compare_architectures(self, configs: List[Dict[str, Any]]) -> None:
        """Compare different architectures."""
        print("\n" + "=" * 70)
        print("  ARCHITECTURE COMPARISON")
        print("=" * 70)

        results = []

        for config in configs:
            model = self.build_mlp(**config)
            analysis = self.analyze_architecture(model)
            results.append({
                "name": config["name"],
                "hidden": config["hidden_sizes"],
                "params": analysis["total_params"],
                "depth": analysis["depth"]
            })

        print(f"\n  {'Name':<20} {'Hidden Layers':<25} {'Parameters':<15} {'Depth':<10}")
        print("-" * 70)

        for r in results:
            print(f"  {r['name']:<20} {str(r['hidden']):<25} {r['params']:<15,} {r['depth']:<10}")


# =============================================================================
# TRAINING LAB
# =============================================================================

class TrainingLab:
    """Laboratory for training experiments."""

    def __init__(self):
        self.results: List[TrainingResult] = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def create_dataset(self, n_samples: int = 2000, n_features: int = 20,
                       n_classes: int = 10) -> Tuple[DataLoader, DataLoader]:
        """Create synthetic classification dataset."""
        torch.manual_seed(42)
        np.random.seed(42)

        X = torch.randn(n_samples, n_features)

        # Create class patterns
        true_W = torch.randn(n_features, n_classes)
        logits = X @ true_W
        y = logits.argmax(dim=1)

        # Add noise
        X += torch.randn_like(X) * 0.5

        # Split
        train_size = int(0.8 * n_samples)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        train_loader = DataLoader(
            TensorDataset(X_train, y_train),
            batch_size=32, shuffle=True
        )
        test_loader = DataLoader(
            TensorDataset(X_test, y_test),
            batch_size=200
        )

        return train_loader, test_loader, n_features, n_classes

    def build_model(self, input_size: int, hidden_sizes: List[int],
                    output_size: int, dropout: float = 0.2) -> nn.Module:
        """Build a model for training."""
        layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev_size = hidden_size

        layers.append(nn.Linear(prev_size, output_size))

        return nn.Sequential(*layers)

    def train_model(self, config: TrainingConfig,
                    train_loader: DataLoader, test_loader: DataLoader,
                    input_size: int, output_size: int,
                    verbose: bool = True) -> TrainingResult:
        """Train a model with given configuration."""
        # Build model
        model = self.build_model(
            input_size, config.hidden_sizes, output_size, config.dropout_rate
        ).to(self.device)

        total_params = sum(p.numel() for p in model.parameters())

        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()

        if config.optimizer == "adam":
            optimizer = optim.Adam(model.parameters(), lr=config.learning_rate,
                                  weight_decay=config.weight_decay)
        elif config.optimizer == "sgd":
            optimizer = optim.SGD(model.parameters(), lr=config.learning_rate,
                                 momentum=0.9, weight_decay=config.weight_decay)
        elif config.optimizer == "adamw":
            optimizer = optim.AdamW(model.parameters(), lr=config.learning_rate,
                                   weight_decay=config.weight_decay)
        else:
            optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)

        # Training loop
        train_losses, train_accs = [], []
        test_losses, test_accs = [], []

        start_time = time.time()

        for epoch in range(config.epochs):
            # Training
            model.train()
            epoch_loss = 0.0
            correct = 0
            total = 0

            for batch_x, batch_y in train_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)

                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                _, predicted = outputs.max(1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()

            train_losses.append(epoch_loss / len(train_loader))
            train_accs.append(100 * correct / total)

            # Testing
            model.eval()
            test_loss = 0.0
            correct = 0
            total = 0

            with torch.no_grad():
                for batch_x, batch_y in test_loader:
                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)

                    outputs = model(batch_x)
                    loss = criterion(outputs, batch_y)

                    test_loss += loss.item()
                    _, predicted = outputs.max(1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()

            test_losses.append(test_loss / len(test_loader))
            test_accs.append(100 * correct / total)

            if verbose and (epoch + 1) % 5 == 0:
                print(f"    Epoch {epoch+1:3d}: Train Loss={train_losses[-1]:.4f}, "
                      f"Train Acc={train_accs[-1]:.1f}%, Test Acc={test_accs[-1]:.1f}%")

        training_time = time.time() - start_time

        result = TrainingResult(
            config=asdict(config),
            train_losses=train_losses,
            train_accs=train_accs,
            test_losses=test_losses,
            test_accs=test_accs,
            final_accuracy=test_accs[-1],
            training_time=round(training_time, 2),
            total_params=total_params
        )

        self.results.append(result)
        return result

    def run_experiment_grid(self, experiments: List[TrainingConfig]) -> List[TrainingResult]:
        """Run multiple experiments."""
        print("\n" + "=" * 70)
        print("  TRAINING EXPERIMENT GRID")
        print("=" * 70)

        # Create dataset
        train_loader, test_loader, n_features, n_classes = self.create_dataset()

        results = []

        for i, config in enumerate(experiments):
            print(f"\n  Experiment {i+1}/{len(experiments)}")
            print(f"  Config: lr={config.learning_rate}, hidden={config.hidden_sizes}, "
                  f"opt={config.optimizer}, dropout={config.dropout_rate}")
            print("-" * 70)

            result = self.train_model(
                config, train_loader, test_loader, n_features, n_classes
            )
            results.append(result)

            print(f"  Final Accuracy: {result.final_accuracy:.1f}% "
                  f"({result.training_time:.1f}s, {result.total_params:,} params)")

        # Summary
        print("\n" + "=" * 70)
        print("  EXPERIMENT SUMMARY")
        print("=" * 70)
        print(f"\n  {'#':<5} {'LR':<10} {'Hidden':<20} {'Optimizer':<10} {'Acc':<10} {'Time':<10}")
        print("-" * 70)

        for i, result in enumerate(results):
            cfg = result.config
            print(f"  {i+1:<5} {cfg['learning_rate']:<10} {str(cfg['hidden_sizes']):<20} "
                  f"{cfg['optimizer']:<10} {result.final_accuracy:<10.1f} {result.training_time:<10.1f}s")

        # Best result
        best = max(results, key=lambda r: r.final_accuracy)
        print(f"\n  Best: {best.final_accuracy:.1f}% accuracy")

        return results


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo1_tensor_benchmarks():
    """Demo 1: Tensor operation benchmarks."""
    print("\n" + "=" * 70)
    print("  DEMO 1: TENSOR BENCHMARKS")
    print("=" * 70)

    benchmarker = TensorBenchmarker(sizes=[(100, 100), (1000, 1000), (3000, 3000)])
    results = benchmarker.run_benchmarks()
    gpu_info = benchmarker.check_gpu()

    # Save results
    data = {
        "benchmarks": [asdict(r) for r in results],
        "gpu_info": gpu_info
    }

    with open(STORAGE_DIR / "benchmark_results.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n  Results saved to {STORAGE_DIR / 'benchmark_results.json'}")

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    large_results = [r for r in results if "3000" in r.shape]
    avg_speedup = np.mean([r.speedup for r in large_results])
    print(f"\n  Average PyTorch speedup (3000x3000): {avg_speedup:.2f}x")

    if gpu_info['cuda_available']:
        print(f"  GPU speedup: {gpu_info['gpu_speedup']:.2f}x")
    print("\n  PyTorch tensors are optimized for numerical computing!")


def demo2_autograd_visualizer():
    """Demo 2: Autograd visualization."""
    print("\n" + "=" * 70)
    print("  DEMO 2: AUTOGRAD VISUALIZER")
    print("=" * 70)

    visualizer = AutogradVisualizer()

    # Simple gradients
    gradients = visualizer.visualize_simple(x_val=2.0)

    # Chain rule
    visualizer.visualize_chain_rule()

    # Neural network gradients
    visualizer.visualize_neural_network_gradients()

    # Save results
    data = {
        "gradients": [asdict(g) for g in gradients]
    }

    with open(STORAGE_DIR / "autograd_results.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n  Results saved to {STORAGE_DIR / 'autograd_results.json'}")

    print("\n" + "=" * 70)
    print("  KEY INSIGHT")
    print("=" * 70)
    print("""
  PyTorch autograd computes gradients automatically!

  You define: y = f(x)
  PyTorch computes: dy/dx

  This is the magic that makes deep learning tractable.
  No manual derivative calculation needed!
    """)


def demo3_architecture_builder():
    """Demo 3: Architecture builder."""
    print("\n" + "=" * 70)
    print("  DEMO 3: ARCHITECTURE BUILDER")
    print("=" * 70)

    builder = ArchitectureBuilder()

    # Define architectures to compare
    configs = [
        {"name": "small", "input_size": 784, "hidden_sizes": [64], "output_size": 10},
        {"name": "medium", "input_size": 784, "hidden_sizes": [256, 128], "output_size": 10},
        {"name": "large", "input_size": 784, "hidden_sizes": [512, 256, 128], "output_size": 10},
        {"name": "wide", "input_size": 784, "hidden_sizes": [1024], "output_size": 10},
        {"name": "deep", "input_size": 784, "hidden_sizes": [128, 128, 128, 128], "output_size": 10},
    ]

    builder.compare_architectures(configs)

    # Detailed analysis of one
    print("\n  Detailed analysis of 'large' architecture:")
    print("-" * 70)

    model = builder.build_mlp(
        name="large_detailed",
        input_size=784,
        hidden_sizes=[512, 256, 128],
        output_size=10,
        activation="relu",
        dropout=0.2
    )

    analysis = builder.analyze_architecture(model)

    print(f"\n  Total parameters: {analysis['total_params']:,}")
    print(f"  Network depth: {analysis['depth']} linear layers")
    print("\n  Layer breakdown:")

    for layer in analysis['layers']:
        if layer['type'] == 'Linear':
            print(f"    {layer['name']}: {layer['type']} "
                  f"({layer['in_features']} -> {layer['out_features']}) "
                  f"[{layer['params']:,} params]")
        elif layer['type'] == 'Dropout':
            print(f"    {layer['name']}: {layer['type']} (p={layer['p']})")
        else:
            print(f"    {layer['name']}: {layer['type']}")

    print("\n" + "=" * 70)
    print("  ARCHITECTURE INSIGHTS")
    print("=" * 70)
    print("""
  - Wide networks (more neurons per layer) can be faster to train
  - Deep networks (more layers) can learn more complex functions
  - Dropout helps prevent overfitting
  - Parameter count affects memory and computation
  - Rule of thumb: Start small, scale up if needed
    """)


def demo4_training_lab():
    """Demo 4: Training experiments."""
    print("\n" + "=" * 70)
    print("  DEMO 4: TRAINING LAB")
    print("=" * 70)

    lab = TrainingLab()

    # Define experiments
    experiments = [
        TrainingConfig(learning_rate=0.001, hidden_sizes=[64], epochs=20, optimizer="adam"),
        TrainingConfig(learning_rate=0.001, hidden_sizes=[128, 64], epochs=20, optimizer="adam"),
        TrainingConfig(learning_rate=0.01, hidden_sizes=[128, 64], epochs=20, optimizer="sgd"),
        TrainingConfig(learning_rate=0.001, hidden_sizes=[256, 128, 64], epochs=20, optimizer="adam"),
    ]

    results = lab.run_experiment_grid(experiments)

    # Save results
    data = {
        "experiments": [
            {
                "config": r.config,
                "final_accuracy": r.final_accuracy,
                "training_time": r.training_time,
                "total_params": r.total_params
            }
            for r in results
        ]
    }

    with open(STORAGE_DIR / "training_results.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n  Results saved to {STORAGE_DIR / 'training_results.json'}")

    print("\n" + "=" * 70)
    print("  TRAINING INSIGHTS")
    print("=" * 70)
    print("""
  - Learning rate is the most important hyperparameter
  - Adam optimizer is a good default choice
  - Deeper networks don't always perform better
  - Start with a simple model, add complexity as needed
  - Watch for overfitting (train acc >> test acc)
    """)


def demo5_full_experiment():
    """Demo 5: Full comprehensive experiment."""
    print("\n" + "=" * 70)
    print("  DEMO 5: FULL PYTORCH EXPERIMENT")
    print("=" * 70)

    # 1. Benchmarks
    print("\n  [1/4] Running tensor benchmarks...")
    benchmarker = TensorBenchmarker(sizes=[(500, 500), (2000, 2000)])
    bench_results = benchmarker.run_benchmarks()

    # 2. Autograd
    print("\n  [2/4] Visualizing autograd...")
    visualizer = AutogradVisualizer()
    visualizer.visualize_simple(x_val=3.0)

    # 3. Architecture comparison
    print("\n  [3/4] Comparing architectures...")
    builder = ArchitectureBuilder()
    arch_configs = [
        {"name": "tiny", "input_size": 20, "hidden_sizes": [32], "output_size": 10},
        {"name": "small", "input_size": 20, "hidden_sizes": [64, 32], "output_size": 10},
        {"name": "medium", "input_size": 20, "hidden_sizes": [128, 64, 32], "output_size": 10},
    ]
    builder.compare_architectures(arch_configs)

    # 4. Training comparison
    print("\n  [4/4] Running training experiments...")
    lab = TrainingLab()

    experiments = [
        TrainingConfig(learning_rate=0.001, hidden_sizes=[64, 32], epochs=25,
                      optimizer="adam", dropout_rate=0.0),
        TrainingConfig(learning_rate=0.001, hidden_sizes=[64, 32], epochs=25,
                      optimizer="adam", dropout_rate=0.3),
        TrainingConfig(learning_rate=0.001, hidden_sizes=[128, 64], epochs=25,
                      optimizer="adamw", dropout_rate=0.2, weight_decay=0.01),
    ]

    results = lab.run_experiment_grid(experiments)

    # Final summary
    print("\n" + "=" * 70)
    print("  FULL EXPERIMENT SUMMARY")
    print("=" * 70)

    best_result = max(results, key=lambda r: r.final_accuracy)

    print(f"""
  Tensor Operations:
    - PyTorch provides optimized tensor operations
    - GPU can provide significant speedups (if available)

  Autograd:
    - Automatic differentiation is PyTorch's superpower
    - No manual gradient calculation needed

  Architecture:
    - Different architectures have different trade-offs
    - More parameters != better performance

  Training:
    - Best accuracy: {best_result.final_accuracy:.1f}%
    - Config: {best_result.config['hidden_sizes']}, {best_result.config['optimizer']}
    - Dropout and weight decay help regularization

  PyTorch makes deep learning accessible and efficient!
    """)

    # Save comprehensive results
    all_results = {
        "benchmarks": [asdict(r) for r in bench_results],
        "training": [
            {
                "config": r.config,
                "final_accuracy": r.final_accuracy,
                "training_time": r.training_time
            }
            for r in results
        ]
    }

    with open(STORAGE_DIR / "full_experiment.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"  All results saved to {STORAGE_DIR / 'full_experiment.json'}")


def print_help():
    """Print usage information."""
    print("""
PyTorch Lab - Module 27 Deliverable
===================================

A comprehensive PyTorch learning toolkit.

Usage:
    python deliverable_pytorch_lab.py <command>

Commands:
    demo1    Tensor operation benchmarks (PyTorch vs NumPy)
    demo2    Autograd visualization (gradient computation)
    demo3    Architecture builder (compare network designs)
    demo4    Training lab (hyperparameter experiments)
    demo5    Full experiment (comprehensive demo)
    help     Show this help message

Examples:
    python deliverable_pytorch_lab.py demo1
    python deliverable_pytorch_lab.py demo4
    python deliverable_pytorch_lab.py demo5

Results are saved to .pytorch_lab/ directory.
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo1_tensor_benchmarks()
    elif command == "demo2":
        demo2_autograd_visualizer()
    elif command == "demo3":
        demo3_architecture_builder()
    elif command == "demo4":
        demo4_training_lab()
    elif command == "demo5":
        demo5_full_experiment()
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
