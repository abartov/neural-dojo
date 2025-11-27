#!/usr/bin/env python3
"""
Module 28 Deliverable: Neural Network Training Toolkit

A comprehensive toolkit for training deep neural networks with best practices.
Includes learning rate finder, initialization analysis, and production training.

Features:
- Learning rate range test (find optimal LR)
- Weight initialization comparison
- Normalization strategy comparison
- Complete training pipeline with all best practices
- JSON result persistence
- Visualization support

Usage:
    python deliverable_training_toolkit.py demo1  # Learning rate finder
    python deliverable_training_toolkit.py demo2  # Initialization comparison
    python deliverable_training_toolkit.py demo3  # Full training with best practices
    python deliverable_training_toolkit.py demo4  # Training report generator

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.utils as nn_utils
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import datasets, transforms
import os
import sys
import json
import math
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Callable, Any


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TrainingConfig:
    """Configuration for model training."""
    batch_size: int = 64
    learning_rate: float = 0.001
    weight_decay: float = 0.01
    max_epochs: int = 30
    patience: int = 7
    max_grad_norm: float = 1.0
    warmup_epochs: int = 3
    dropout_rate: float = 0.3
    val_split: float = 0.1


@dataclass
class LRFinderResult:
    """Results from learning rate range test."""
    learning_rates: List[float]
    losses: List[float]
    suggested_lr: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class InitComparisonResult:
    """Results from initialization comparison."""
    init_name: str
    final_accuracy: float
    final_loss: float
    epochs_to_converge: int
    gradient_stats: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TrainingResult:
    """Results from a training run."""
    config: Dict[str, Any]
    train_losses: List[float]
    val_losses: List[float]
    train_accuracies: List[float]
    val_accuracies: List[float]
    learning_rates: List[float]
    best_val_accuracy: float
    total_epochs: int
    early_stopped: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# NEURAL NETWORK MODELS
# ============================================================================

class FlexibleCNN(nn.Module):
    """
    Configurable CNN for experimentation.
    Supports different normalization strategies.
    """

    def __init__(
        self,
        norm_type: str = "batch",
        dropout_rate: float = 0.3,
        num_classes: int = 10
    ):
        super().__init__()
        self.norm_type = norm_type

        # Feature extractor
        self.features = self._make_features(norm_type, dropout_rate)

        # Classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            self._get_norm_layer(norm_type, 64, is_conv=False),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )

    def _get_norm_layer(
        self,
        norm_type: str,
        num_features: int,
        is_conv: bool = True
    ) -> nn.Module:
        """Get appropriate normalization layer."""
        if norm_type == "batch":
            return nn.BatchNorm2d(num_features) if is_conv else nn.BatchNorm1d(num_features)
        elif norm_type == "layer":
            return nn.LayerNorm(num_features)
        else:
            return nn.Identity()

    def _make_features(self, norm_type: str, dropout_rate: float) -> nn.Sequential:
        """Create feature extraction layers."""
        layers = []

        # Block 1: 1 -> 32
        layers.extend([
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            self._get_norm_layer(norm_type, 32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate / 2),
        ])

        # Block 2: 32 -> 64
        layers.extend([
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            self._get_norm_layer(norm_type, 64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate / 2),
        ])

        # Block 3: 64 -> 128 with global pooling
        layers.extend([
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            self._get_norm_layer(norm_type, 128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        ])

        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)


class DeepMLP(nn.Module):
    """
    Deep MLP for initialization testing.
    8 hidden layers to show gradient effects.
    """

    def __init__(self, init_fn: Optional[Callable] = None):
        super().__init__()

        self.layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, 10)
        )

        if init_fn:
            self.apply(init_fn)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================

def init_random(m: nn.Module) -> None:
    """Random uniform initialization."""
    if isinstance(m, nn.Linear):
        nn.init.uniform_(m.weight, -1, 1)
        if m.bias is not None:
            nn.init.uniform_(m.bias, -1, 1)


def init_xavier(m: nn.Module) -> None:
    """Xavier/Glorot initialization."""
    if isinstance(m, (nn.Linear, nn.Conv2d)):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.zeros_(m.bias)


def init_he(m: nn.Module) -> None:
    """He/Kaiming initialization for ReLU."""
    if isinstance(m, (nn.Linear, nn.Conv2d)):
        nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
        if m.bias is not None:
            nn.init.zeros_(m.bias)


INITIALIZATIONS = {
    "random": init_random,
    "xavier": init_xavier,
    "he": init_he,
}


# ============================================================================
# TRAINING UTILITIES
# ============================================================================

class EarlyStopping:
    """Early stopping to prevent overfitting."""

    def __init__(self, patience: int = 7, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
        self.best_state = None
        self.should_stop = False

    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop

    def restore_best(self, model: nn.Module) -> None:
        """Restore best weights."""
        if self.best_state:
            model.load_state_dict(self.best_state)


def get_warmup_cosine_scheduler(
    optimizer: optim.Optimizer,
    warmup_epochs: int,
    total_epochs: int,
    steps_per_epoch: int
) -> torch.optim.lr_scheduler.LambdaLR:
    """Create warmup + cosine annealing scheduler."""
    total_steps = total_epochs * steps_per_epoch
    warmup_steps = warmup_epochs * steps_per_epoch

    def lr_lambda(step: int) -> float:
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)


# ============================================================================
# TOOLKIT CLASS
# ============================================================================

class TrainingToolkit:
    """
    Comprehensive toolkit for training neural networks.
    """

    STORAGE_DIR = ".training_toolkit"

    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        os.makedirs(self.STORAGE_DIR, exist_ok=True)

        # Load MNIST data
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

        print(f"🔧 Training Toolkit initialized")
        print(f"   Device: {self.device}")
        print(f"   Storage: {self.STORAGE_DIR}/")

    def _get_data_loaders(
        self,
        batch_size: int = 64,
        subset_size: Optional[int] = None,
        val_split: float = 0.1
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Get train, validation, and test data loaders."""
        train_dataset = datasets.MNIST(
            './data', train=True, download=True, transform=self.transform
        )
        test_dataset = datasets.MNIST(
            './data', train=False, download=True, transform=self.transform
        )

        # Use subset for faster experimentation
        if subset_size:
            train_dataset = Subset(train_dataset, range(min(subset_size, len(train_dataset))))
            test_dataset = Subset(test_dataset, range(min(subset_size // 5, len(test_dataset))))

        # Split train into train/val
        val_size = int(len(train_dataset) * val_split)
        train_size = len(train_dataset) - val_size
        train_set, val_set = random_split(
            train_dataset, [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )

        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_set, batch_size=batch_size)
        test_loader = DataLoader(test_dataset, batch_size=batch_size)

        return train_loader, val_loader, test_loader

    def find_learning_rate(
        self,
        start_lr: float = 1e-7,
        end_lr: float = 10.0,
        num_iterations: int = 100
    ) -> LRFinderResult:
        """
        Find optimal learning rate using the LR range test.

        Trains with exponentially increasing LR and records loss.
        Suggested LR is where loss decreases fastest.
        """
        print("\n" + "="*60)
        print("📈 Learning Rate Range Test")
        print("="*60)

        # Get data
        train_loader, _, _ = self._get_data_loaders(batch_size=64, subset_size=5000)

        # Fresh model
        model = FlexibleCNN(norm_type="batch", dropout_rate=0.0).to(self.device)
        model.apply(init_he)
        initial_state = model.state_dict()

        optimizer = optim.SGD(model.parameters(), lr=start_lr, momentum=0.9)
        criterion = nn.CrossEntropyLoss()

        # LR finder
        lrs = []
        losses = []
        lr = start_lr
        lr_mult = (end_lr / start_lr) ** (1 / num_iterations)

        model.train()
        iterator = iter(train_loader)
        best_loss = float('inf')
        smoothed_loss = 0

        for i in range(num_iterations):
            # Get batch (cycle if needed)
            try:
                inputs, targets = next(iterator)
            except StopIteration:
                iterator = iter(train_loader)
                inputs, targets = next(iterator)

            inputs, targets = inputs.to(self.device), targets.to(self.device)

            # Set LR
            optimizer.param_groups[0]['lr'] = lr

            # Forward/backward
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            # Smoothed loss
            if i == 0:
                smoothed_loss = loss.item()
            else:
                smoothed_loss = 0.98 * smoothed_loss + 0.02 * loss.item()

            # Stop if loss explodes
            if i > 10 and smoothed_loss > 4 * best_loss:
                print(f"   Stopping early - loss exploded at LR={lr:.2e}")
                break

            if smoothed_loss < best_loss:
                best_loss = smoothed_loss

            lrs.append(lr)
            losses.append(smoothed_loss)

            loss.backward()
            optimizer.step()

            lr *= lr_mult

            if i % 20 == 0:
                print(f"   Iteration {i:3d}: LR={lr:.2e}, Loss={smoothed_loss:.4f}")

        # Find suggested LR (steepest descent)
        suggested_lr = self._find_steepest_gradient(lrs, losses)

        result = LRFinderResult(
            learning_rates=lrs,
            losses=losses,
            suggested_lr=suggested_lr
        )

        # Save result
        self._save_result("lr_finder", asdict(result))

        print(f"\n✅ Suggested learning rate: {suggested_lr:.2e}")
        print("   (Choose LR about 10x smaller than the minimum loss point)")

        return result

    def _find_steepest_gradient(
        self,
        lrs: List[float],
        losses: List[float]
    ) -> float:
        """Find LR with steepest negative gradient."""
        if len(lrs) < 10:
            return lrs[0]

        # Compute gradients
        gradients = []
        for i in range(5, len(losses) - 5):
            grad = (losses[i + 5] - losses[i - 5]) / (math.log(lrs[i + 5]) - math.log(lrs[i - 5]))
            gradients.append((lrs[i], grad))

        # Find most negative gradient
        min_grad_lr = min(gradients, key=lambda x: x[1])[0]

        # Return LR 10x smaller for stability
        return min_grad_lr / 10

    def compare_initializations(
        self,
        num_epochs: int = 15
    ) -> Dict[str, InitComparisonResult]:
        """
        Compare different weight initialization strategies.
        """
        print("\n" + "="*60)
        print("⚖️ Initialization Comparison")
        print("="*60)

        train_loader, val_loader, _ = self._get_data_loaders(batch_size=64, subset_size=8000)
        results = {}

        for name, init_fn in INITIALIZATIONS.items():
            print(f"\n--- Testing {name.upper()} initialization ---")

            model = DeepMLP(init_fn=init_fn).to(self.device)
            optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
            criterion = nn.CrossEntropyLoss()

            train_accs = []
            grad_norms = []

            for epoch in range(num_epochs):
                model.train()
                correct = 0
                total = 0
                epoch_grad_norms = []

                for inputs, targets in train_loader:
                    inputs, targets = inputs.to(self.device), targets.to(self.device)

                    optimizer.zero_grad()
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)

                    if torch.isnan(loss):
                        print(f"   ⚠️ NaN at epoch {epoch+1}, training diverged!")
                        break

                    loss.backward()

                    # Track gradient norm
                    total_norm = 0
                    for p in model.parameters():
                        if p.grad is not None:
                            total_norm += p.grad.data.norm(2).item() ** 2
                    epoch_grad_norms.append(total_norm ** 0.5)

                    optimizer.step()

                    _, predicted = outputs.max(1)
                    total += targets.size(0)
                    correct += predicted.eq(targets).sum().item()

                if torch.isnan(loss):
                    break

                acc = 100.0 * correct / total
                train_accs.append(acc)
                grad_norms.append(sum(epoch_grad_norms) / len(epoch_grad_norms))

                print(f"   Epoch {epoch+1:2d}: Acc={acc:.1f}%, Grad Norm={grad_norms[-1]:.4f}")

            # Evaluate final
            model.eval()
            val_correct = 0
            val_total = 0
            val_loss = 0
            with torch.no_grad():
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)
                    val_loss += loss.item()
                    _, predicted = outputs.max(1)
                    val_total += targets.size(0)
                    val_correct += predicted.eq(targets).sum().item()

            final_acc = 100.0 * val_correct / val_total if val_total > 0 else 0
            final_loss = val_loss / len(val_loader) if len(val_loader) > 0 else float('inf')

            # Find convergence epoch (>90% accuracy)
            epochs_to_converge = num_epochs
            for i, acc in enumerate(train_accs):
                if acc >= 90:
                    epochs_to_converge = i + 1
                    break

            results[name] = InitComparisonResult(
                init_name=name,
                final_accuracy=final_acc,
                final_loss=final_loss,
                epochs_to_converge=epochs_to_converge,
                gradient_stats={
                    "mean_grad_norm": sum(grad_norms) / len(grad_norms) if grad_norms else 0,
                    "max_grad_norm": max(grad_norms) if grad_norms else 0,
                    "min_grad_norm": min(grad_norms) if grad_norms else 0,
                }
            )

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"{'Init':<12} {'Final Acc':>12} {'Converge':>12} {'Grad Norm':>12}")
        print("-"*48)
        for name, res in results.items():
            print(f"{name:<12} {res.final_accuracy:>11.1f}% "
                  f"{res.epochs_to_converge:>12} "
                  f"{res.gradient_stats['mean_grad_norm']:>12.4f}")

        # Save
        self._save_result("init_comparison", {k: asdict(v) for k, v in results.items()})

        return results

    def train_with_best_practices(
        self,
        config: Optional[TrainingConfig] = None
    ) -> TrainingResult:
        """
        Train a model with all best practices.
        """
        config = config or TrainingConfig()

        print("\n" + "="*60)
        print("🚀 Production Training with Best Practices")
        print("="*60)
        print(f"Config: batch_size={config.batch_size}, lr={config.learning_rate}")
        print(f"        max_epochs={config.max_epochs}, patience={config.patience}")

        # Data
        train_loader, val_loader, test_loader = self._get_data_loaders(
            batch_size=config.batch_size,
            subset_size=None,  # Use full dataset
            val_split=config.val_split
        )

        print(f"\nData: {len(train_loader.dataset)} train, "
              f"{len(val_loader.dataset)} val, {len(test_loader.dataset)} test")

        # Model with best practices
        model = FlexibleCNN(
            norm_type="batch",
            dropout_rate=config.dropout_rate
        ).to(self.device)
        model.apply(init_he)

        # Optimizer
        optimizer = optim.AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )

        # Scheduler with warmup
        scheduler = get_warmup_cosine_scheduler(
            optimizer,
            config.warmup_epochs,
            config.max_epochs,
            len(train_loader)
        )

        criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        early_stopping = EarlyStopping(patience=config.patience)

        # Training loop
        history = {
            'train_loss': [], 'val_loss': [],
            'train_acc': [], 'val_acc': [],
            'lr': []
        }
        best_val_acc = 0

        print("\nTraining...")
        for epoch in range(config.max_epochs):
            # Train
            model.train()
            train_loss = 0
            train_correct = 0
            train_total = 0

            for inputs, targets in train_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()

                nn_utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)

                optimizer.step()
                scheduler.step()

                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += targets.size(0)
                train_correct += predicted.eq(targets).sum().item()

            train_loss /= len(train_loader)
            train_acc = 100.0 * train_correct / train_total

            # Validate
            model.eval()
            val_loss = 0
            val_correct = 0
            val_total = 0

            with torch.no_grad():
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)
                    val_loss += loss.item()
                    _, predicted = outputs.max(1)
                    val_total += targets.size(0)
                    val_correct += predicted.eq(targets).sum().item()

            val_loss /= len(val_loader)
            val_acc = 100.0 * val_correct / val_total

            # Track
            current_lr = optimizer.param_groups[0]['lr']
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_acc'].append(train_acc)
            history['val_acc'].append(val_acc)
            history['lr'].append(current_lr)

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                marker = " ★"
            else:
                marker = ""

            print(f"Epoch {epoch+1:3d}: "
                  f"Train {train_loss:.4f} ({train_acc:.1f}%) | "
                  f"Val {val_loss:.4f} ({val_acc:.1f}%) | "
                  f"LR {current_lr:.6f}{marker}")

            # Early stopping
            if early_stopping(val_loss, model):
                print(f"\n⚡ Early stopping at epoch {epoch+1}")
                early_stopping.restore_best(model)
                break

        # Final test
        model.eval()
        test_correct = 0
        test_total = 0
        with torch.no_grad():
            for inputs, targets in test_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                test_total += targets.size(0)
                test_correct += predicted.eq(targets).sum().item()

        test_acc = 100.0 * test_correct / test_total

        print(f"\n✅ Training complete!")
        print(f"   Best validation accuracy: {best_val_acc:.1f}%")
        print(f"   Test accuracy: {test_acc:.1f}%")

        result = TrainingResult(
            config=asdict(config),
            train_losses=history['train_loss'],
            val_losses=history['val_loss'],
            train_accuracies=history['train_acc'],
            val_accuracies=history['val_acc'],
            learning_rates=history['lr'],
            best_val_accuracy=best_val_acc,
            total_epochs=epoch + 1,
            early_stopped=early_stopping.should_stop
        )

        self._save_result("training", asdict(result))

        return result

    def generate_report(self) -> str:
        """Generate a comprehensive training report from saved results."""
        print("\n" + "="*60)
        print("📋 Training Report Generator")
        print("="*60)

        report_lines = [
            "# Neural Network Training Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
        ]

        # Load saved results
        lr_result = self._load_result("lr_finder")
        init_result = self._load_result("init_comparison")
        train_result = self._load_result("training")

        if lr_result:
            report_lines.extend([
                "## Learning Rate Finder",
                f"- Suggested LR: {lr_result['suggested_lr']:.2e}",
                f"- Tested range: {lr_result['learning_rates'][0]:.2e} to {lr_result['learning_rates'][-1]:.2e}",
                "",
            ])

        if init_result:
            report_lines.extend([
                "## Initialization Comparison",
                "| Method | Final Acc | Epochs to 90% |",
                "|--------|-----------|---------------|",
            ])
            for name, data in init_result.items():
                report_lines.append(
                    f"| {name} | {data['final_accuracy']:.1f}% | {data['epochs_to_converge']} |"
                )
            report_lines.append("")

        if train_result:
            report_lines.extend([
                "## Training Results",
                f"- Best Validation Accuracy: {train_result['best_val_accuracy']:.1f}%",
                f"- Total Epochs: {train_result['total_epochs']}",
                f"- Early Stopped: {train_result['early_stopped']}",
                "",
                "### Configuration",
            ])
            for key, value in train_result['config'].items():
                report_lines.append(f"- {key}: {value}")
            report_lines.append("")

        report_lines.extend([
            "## Best Practices Applied",
            "- ✅ He (Kaiming) initialization for ReLU",
            "- ✅ Batch normalization",
            "- ✅ Dropout regularization",
            "- ✅ AdamW with weight decay",
            "- ✅ Warmup + Cosine LR schedule",
            "- ✅ Gradient clipping",
            "- ✅ Early stopping",
            "- ✅ Label smoothing",
        ])

        report = "\n".join(report_lines)

        # Save report
        report_path = os.path.join(self.STORAGE_DIR, "training_report.md")
        with open(report_path, 'w') as f:
            f.write(report)

        print(report)
        print(f"\n📁 Report saved to: {report_path}")

        return report

    def _save_result(self, name: str, data: Dict) -> None:
        """Save result to JSON."""
        path = os.path.join(self.STORAGE_DIR, f"{name}_result.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 Saved {name} results to {path}")

    def _load_result(self, name: str) -> Optional[Dict]:
        """Load result from JSON."""
        path = os.path.join(self.STORAGE_DIR, f"{name}_result.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_1_lr_finder():
    """Demo 1: Learning Rate Range Test"""
    print("\n" + "="*70)
    print("DEMO 1: Learning Rate Range Test")
    print("="*70)
    print("\nFinding the optimal learning rate for training...")
    print("This helps you avoid guessing - the test reveals the best LR.\n")

    toolkit = TrainingToolkit()
    result = toolkit.find_learning_rate(
        start_lr=1e-7,
        end_lr=1.0,
        num_iterations=100
    )

    print("\n" + "-"*50)
    print("KEY INSIGHT: The suggested LR is where loss decreases fastest.")
    print("Use a LR about 10x smaller than the minimum for stability.")


def demo_2_init_comparison():
    """Demo 2: Initialization Comparison"""
    print("\n" + "="*70)
    print("DEMO 2: Weight Initialization Comparison")
    print("="*70)
    print("\nComparing Random vs Xavier vs He initialization...")
    print("For ReLU networks, He initialization should win.\n")

    toolkit = TrainingToolkit()
    results = toolkit.compare_initializations(num_epochs=15)

    print("\n" + "-"*50)
    print("KEY INSIGHT: He initialization is designed for ReLU activations.")
    print("Xavier works for tanh/sigmoid, but can struggle with ReLU.")


def demo_3_full_training():
    """Demo 3: Full Training with Best Practices"""
    print("\n" + "="*70)
    print("DEMO 3: Production Training Pipeline")
    print("="*70)
    print("\nTraining with ALL best practices combined:")
    print("  • He initialization")
    print("  • BatchNorm + Dropout")
    print("  • AdamW optimizer")
    print("  • Warmup + Cosine LR schedule")
    print("  • Gradient clipping")
    print("  • Early stopping")
    print()

    toolkit = TrainingToolkit()

    config = TrainingConfig(
        batch_size=64,
        learning_rate=0.001,
        max_epochs=30,
        patience=7,
        dropout_rate=0.3
    )

    result = toolkit.train_with_best_practices(config)

    print("\n" + "-"*50)
    print("KEY INSIGHT: Combining these techniques usually gets >99% on MNIST!")


def demo_4_report():
    """Demo 4: Generate Training Report"""
    print("\n" + "="*70)
    print("DEMO 4: Training Report Generator")
    print("="*70)
    print("\nGenerating a comprehensive report from all experiments...\n")

    toolkit = TrainingToolkit()
    report = toolkit.generate_report()


def print_usage():
    """Print usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           Module 28 Deliverable: Neural Network Training Toolkit     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  A comprehensive toolkit for training deep neural networks with      ║
║  best practices including LR finding, initialization comparison,     ║
║  and production-ready training pipelines.                            ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  USAGE:                                                              ║
║                                                                      ║
║    python deliverable_training_toolkit.py demo1                      ║
║        → Learning Rate Range Test (find optimal LR)                  ║
║                                                                      ║
║    python deliverable_training_toolkit.py demo2                      ║
║        → Initialization Comparison (Random vs Xavier vs He)          ║
║                                                                      ║
║    python deliverable_training_toolkit.py demo3                      ║
║        → Full Training with All Best Practices                       ║
║                                                                      ║
║    python deliverable_training_toolkit.py demo4                      ║
║        → Generate Comprehensive Training Report                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  BEST PRACTICES INCLUDED:                                            ║
║                                                                      ║
║    ✓ He (Kaiming) initialization for ReLU                            ║
║    ✓ BatchNorm and LayerNorm                                         ║
║    ✓ Dropout regularization                                          ║
║    ✓ AdamW optimizer with weight decay                               ║
║    ✓ Warmup + Cosine annealing LR schedule                           ║
║    ✓ Gradient clipping                                               ║
║    ✓ Early stopping with patience                                    ║
║    ✓ Label smoothing                                                 ║
║    ✓ JSON result persistence                                         ║
║                                                                       ║
╚══════════════════════════════════════════════════════════════════════╝
""")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_lr_finder()
    elif command == "demo2":
        demo_2_init_comparison()
    elif command == "demo3":
        demo_3_full_training()
    elif command == "demo4":
        demo_4_report()
    elif command in ["help", "-h", "--help"]:
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)
