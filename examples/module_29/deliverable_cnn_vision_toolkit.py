#!/usr/bin/env python3
"""
Module 29 Deliverable: CNN Vision Toolkit

A comprehensive toolkit for building, training, and analyzing Convolutional Neural Networks.
Includes custom architecture building, transfer learning, and feature analysis.

Features:
- Custom CNN architecture builder with best practices
- Transfer learning with pretrained ResNet/EfficientNet
- Architecture comparison and analysis
- Training pipeline with all modern techniques
- JSON result persistence
- Comprehensive reporting

Usage:
    python deliverable_cnn_vision_toolkit.py demo1  # Train custom CNN on CIFAR-10
    python deliverable_cnn_vision_toolkit.py demo2  # Transfer learning comparison
    python deliverable_cnn_vision_toolkit.py demo3  # Architecture analysis
    python deliverable_cnn_vision_toolkit.py demo4  # Generate CNN report

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import datasets, transforms, models
import os
import sys
import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Any


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class CNNConfig:
    """Configuration for CNN architecture."""
    num_classes: int = 10
    in_channels: int = 3
    base_channels: int = 32
    num_blocks: int = 3
    dropout_rate: float = 0.5
    use_residual: bool = True
    use_batchnorm: bool = True


@dataclass
class TrainingConfig:
    """Configuration for model training."""
    batch_size: int = 64
    learning_rate: float = 0.001
    weight_decay: float = 0.01
    max_epochs: int = 30
    patience: int = 7
    warmup_epochs: int = 3


@dataclass
class ArchitectureInfo:
    """Information about a CNN architecture."""
    name: str
    total_params: int
    trainable_params: int
    input_size: Tuple[int, int, int]
    output_size: int
    memory_mb: float
    layers_count: int
    conv_layers: int
    fc_layers: int


@dataclass
class TrainingResult:
    """Results from a training run."""
    model_name: str
    config: Dict[str, Any]
    train_losses: List[float]
    val_losses: List[float]
    train_accuracies: List[float]
    val_accuracies: List[float]
    best_val_accuracy: float
    total_epochs: int
    training_time_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ComparisonResult:
    """Results from comparing multiple architectures."""
    architectures: List[ArchitectureInfo]
    training_results: List[TrainingResult]
    best_model: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# CNN ARCHITECTURES
# ============================================================================

class ConvBlock(nn.Module):
    """
    A standard convolutional block: Conv -> BatchNorm -> ReLU.
    Optionally includes residual connection.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        use_residual: bool = False,
        use_batchnorm: bool = True
    ):
        super().__init__()
        self.use_residual = use_residual
        padding = kernel_size // 2

        layers = [
            nn.Conv2d(
                in_channels, out_channels,
                kernel_size=kernel_size,
                stride=stride,
                padding=padding,
                bias=not use_batchnorm
            )
        ]

        if use_batchnorm:
            layers.append(nn.BatchNorm2d(out_channels))

        layers.append(nn.ReLU(inplace=True))
        self.conv = nn.Sequential(*layers)

        # Shortcut for residual connection
        self.shortcut = nn.Identity()
        if use_residual and (in_channels != out_channels or stride != 1):
            shortcut_layers = [
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False)
            ]
            if use_batchnorm:
                shortcut_layers.append(nn.BatchNorm2d(out_channels))
            self.shortcut = nn.Sequential(*shortcut_layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.conv(x)
        if self.use_residual:
            out = out + self.shortcut(x)
        return out


class CustomCNN(nn.Module):
    """
    A modern CNN incorporating best practices:
    - BatchNorm after every conv
    - Residual connections in deeper blocks
    - Global average pooling instead of flattening
    - Dropout for regularization
    """

    def __init__(self, config: CNNConfig):
        super().__init__()
        self.config = config

        # Build feature extractor
        self.features = self._build_features()

        # Classification head
        final_channels = config.base_channels * (2 ** (config.num_blocks - 1))
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(final_channels, config.num_classes)
        )

        self._init_weights()

    def _build_features(self) -> nn.Sequential:
        """Build the feature extraction layers."""
        layers = []
        in_ch = self.config.in_channels

        # Initial stem
        out_ch = self.config.base_channels
        layers.append(ConvBlock(
            in_ch, out_ch,
            use_batchnorm=self.config.use_batchnorm
        ))
        in_ch = out_ch

        # Feature blocks with increasing channels
        for i in range(self.config.num_blocks):
            out_ch = self.config.base_channels * (2 ** i)

            # First conv in block: downsample
            layers.append(ConvBlock(
                in_ch, out_ch,
                stride=2 if i > 0 else 1,
                use_residual=self.config.use_residual,
                use_batchnorm=self.config.use_batchnorm
            ))

            # Second conv in block
            layers.append(ConvBlock(
                out_ch, out_ch,
                use_residual=self.config.use_residual,
                use_batchnorm=self.config.use_batchnorm
            ))

            in_ch = out_ch

        return nn.Sequential(*layers)

    def _init_weights(self):
        """Initialize weights using He initialization."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x


def create_transfer_model(
    num_classes: int,
    backbone: str = "resnet18",
    freeze_backbone: bool = True
) -> nn.Module:
    """
    Create a model using transfer learning.

    Args:
        num_classes: Number of output classes
        backbone: One of 'resnet18', 'resnet34', 'resnet50', 'efficientnet_b0'
        freeze_backbone: Whether to freeze the pretrained weights

    Returns:
        PyTorch model ready for training
    """
    if backbone == "resnet18":
        model = models.resnet18(weights='IMAGENET1K_V1')
        num_features = model.fc.in_features
    elif backbone == "resnet34":
        model = models.resnet34(weights='IMAGENET1K_V1')
        num_features = model.fc.in_features
    elif backbone == "resnet50":
        model = models.resnet50(weights='IMAGENET1K_V1')
        num_features = model.fc.in_features
    elif backbone == "efficientnet_b0":
        model = models.efficientnet_b0(weights='IMAGENET1K_V1')
        num_features = model.classifier[1].in_features
    else:
        raise ValueError(f"Unknown backbone: {backbone}")

    # Freeze backbone if requested
    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace classifier
    if backbone.startswith("resnet"):
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )
    else:  # EfficientNet
        model.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )

    return model


# ============================================================================
# DATA LOADING
# ============================================================================

def get_cifar10_loaders(
    batch_size: int = 64,
    val_split: float = 0.1,
    num_workers: int = 2,
    data_dir: str = "./data"
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Get CIFAR-10 data loaders with standard augmentation.

    Returns:
        train_loader, val_loader, test_loader
    """
    # Training transforms with augmentation
    train_transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(32, padding=4),
        transforms.ToTensor(),
        transforms.Normalize([0.4914, 0.4822, 0.4465], [0.2470, 0.2435, 0.2616])
    ])

    # Validation/Test transforms (no augmentation)
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.4914, 0.4822, 0.4465], [0.2470, 0.2435, 0.2616])
    ])

    # Download datasets
    full_train = datasets.CIFAR10(
        root=data_dir, train=True, download=True, transform=train_transform
    )
    test_dataset = datasets.CIFAR10(
        root=data_dir, train=False, download=True, transform=test_transform
    )

    # Split training into train/val
    train_size = int((1 - val_split) * len(full_train))
    val_size = len(full_train) - train_size
    train_dataset, val_dataset = random_split(
        full_train, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    # Create data loaders
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )

    return train_loader, val_loader, test_loader


def get_small_subset_loaders(
    batch_size: int = 32,
    samples_per_class: int = 100,
    num_workers: int = 2,
    data_dir: str = "./data"
) -> Tuple[DataLoader, DataLoader]:
    """
    Get small subset of CIFAR-10 for quick transfer learning demos.

    Returns:
        train_loader, test_loader (smaller datasets)
    """
    # Use ImageNet-style transforms for transfer learning
    train_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    test_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Download full datasets
    full_train = datasets.CIFAR10(
        root=data_dir, train=True, download=True, transform=train_transform
    )
    full_test = datasets.CIFAR10(
        root=data_dir, train=False, download=True, transform=test_transform
    )

    # Create subset indices (samples_per_class from each class)
    train_indices = []
    class_counts = {i: 0 for i in range(10)}
    for idx, (_, label) in enumerate(full_train):
        if class_counts[label] < samples_per_class:
            train_indices.append(idx)
            class_counts[label] += 1
        if sum(class_counts.values()) >= samples_per_class * 10:
            break

    test_indices = list(range(min(1000, len(full_test))))

    train_subset = Subset(full_train, train_indices)
    test_subset = Subset(full_test, test_indices)

    train_loader = DataLoader(
        train_subset, batch_size=batch_size, shuffle=True, num_workers=num_workers
    )
    test_loader = DataLoader(
        test_subset, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )

    return train_loader, test_loader


# ============================================================================
# TRAINING
# ============================================================================

class Trainer:
    """Handles model training with best practices."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: TrainingConfig,
        device: str = "auto"
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config

        # Set device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model = self.model.to(self.device)

        # Setup optimizer and scheduler
        self.optimizer = optim.AdamW(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )

        total_steps = len(train_loader) * config.max_epochs
        warmup_steps = len(train_loader) * config.warmup_epochs

        self.scheduler = optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=config.learning_rate * 10,
            total_steps=total_steps,
            pct_start=warmup_steps / total_steps
        )

        self.criterion = nn.CrossEntropyLoss()

        # Tracking
        self.train_losses = []
        self.val_losses = []
        self.train_accs = []
        self.val_accs = []
        self.best_val_acc = 0.0
        self.patience_counter = 0

    def train_epoch(self) -> Tuple[float, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for inputs, targets in self.train_loader:
            inputs, targets = inputs.to(self.device), targets.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            total_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        avg_loss = total_loss / total
        accuracy = correct / total
        return avg_loss, accuracy

    def validate(self) -> Tuple[float, float]:
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, targets in self.val_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)

                total_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()

        avg_loss = total_loss / total
        accuracy = correct / total
        return avg_loss, accuracy

    def train(self, verbose: bool = True) -> TrainingResult:
        """
        Full training loop with early stopping.

        Returns:
            TrainingResult with all metrics
        """
        start_time = time.time()

        for epoch in range(self.config.max_epochs):
            train_loss, train_acc = self.train_epoch()
            val_loss, val_acc = self.validate()

            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accs.append(train_acc)
            self.val_accs.append(val_acc)

            # Track best model
            improved = ""
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.patience_counter = 0
                improved = " *"
            else:
                self.patience_counter += 1

            if verbose:
                print(f"  Epoch {epoch+1:3d}: "
                      f"Train {train_loss:.4f} ({train_acc*100:.1f}%) | "
                      f"Val {val_loss:.4f} ({val_acc*100:.1f}%){improved}")

            # Early stopping
            if self.patience_counter >= self.config.patience:
                if verbose:
                    print(f"  Early stopping at epoch {epoch+1}")
                break

        training_time = time.time() - start_time

        return TrainingResult(
            model_name=self.model.__class__.__name__,
            config=asdict(self.config),
            train_losses=self.train_losses,
            val_losses=self.val_losses,
            train_accuracies=self.train_accs,
            val_accuracies=self.val_accs,
            best_val_accuracy=self.best_val_acc,
            total_epochs=len(self.train_losses),
            training_time_seconds=training_time
        )


# ============================================================================
# ARCHITECTURE ANALYSIS
# ============================================================================

def analyze_architecture(
    model: nn.Module,
    input_size: Tuple[int, int, int] = (3, 32, 32),
    name: Optional[str] = None
) -> ArchitectureInfo:
    """
    Analyze a CNN architecture.

    Args:
        model: PyTorch model
        input_size: Input dimensions (C, H, W)
        name: Optional name for the model

    Returns:
        ArchitectureInfo with analysis results
    """
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    # Count layers
    conv_layers = sum(1 for m in model.modules() if isinstance(m, nn.Conv2d))
    fc_layers = sum(1 for m in model.modules() if isinstance(m, nn.Linear))
    total_layers = len(list(model.modules()))

    # Estimate memory (rough)
    param_memory = total_params * 4 / (1024 * 1024)  # MB

    # Get output size
    model.eval()
    with torch.no_grad():
        dummy = torch.randn(1, *input_size)
        try:
            output = model(dummy)
            output_size = output.shape[-1]
        except Exception:
            output_size = -1

    return ArchitectureInfo(
        name=name or model.__class__.__name__,
        total_params=total_params,
        trainable_params=trainable_params,
        input_size=input_size,
        output_size=output_size,
        memory_mb=param_memory,
        layers_count=total_layers,
        conv_layers=conv_layers,
        fc_layers=fc_layers
    )


def compare_architectures(
    models_dict: Dict[str, nn.Module],
    input_size: Tuple[int, int, int] = (3, 32, 32)
) -> List[ArchitectureInfo]:
    """Compare multiple architectures."""
    results = []
    for name, model in models_dict.items():
        info = analyze_architecture(model, input_size, name)
        results.append(info)
    return results


# ============================================================================
# STORAGE
# ============================================================================

class Storage:
    """Handle saving and loading results."""

    def __init__(self, storage_dir: str = ".cnn_toolkit"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_result(self, result: Any, filename: str):
        """Save a dataclass result to JSON."""
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        return filepath

    def load_result(self, filename: str) -> Dict:
        """Load a result from JSON."""
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_1_train_custom_cnn():
    """
    Demo 1: Train a Custom CNN on CIFAR-10

    Demonstrates building and training a CNN from scratch with:
    - Modern architecture (BatchNorm, residual connections)
    - Best training practices (OneCycleLR, early stopping)
    - Full metric tracking
    """
    print("=" * 60)
    print("DEMO 1: Train Custom CNN on CIFAR-10")
    print("=" * 60)
    print()

    storage = Storage()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print()

    # Architecture configuration
    cnn_config = CNNConfig(
        num_classes=10,
        in_channels=3,
        base_channels=32,
        num_blocks=3,
        dropout_rate=0.5,
        use_residual=True,
        use_batchnorm=True
    )

    print("Building Custom CNN...")
    model = CustomCNN(cnn_config)
    info = analyze_architecture(model, (3, 32, 32), "CustomCNN")
    print(f"  Parameters: {info.total_params:,}")
    print(f"  Conv layers: {info.conv_layers}")
    print(f"  Memory: {info.memory_mb:.1f} MB")
    print()

    # Load data
    print("Loading CIFAR-10 dataset...")
    train_loader, val_loader, test_loader = get_cifar10_loaders(
        batch_size=64, val_split=0.1
    )
    print(f"  Train: {len(train_loader.dataset):,} samples")
    print(f"  Val: {len(val_loader.dataset):,} samples")
    print(f"  Test: {len(test_loader.dataset):,} samples")
    print()

    # Training configuration
    train_config = TrainingConfig(
        batch_size=64,
        learning_rate=0.001,
        weight_decay=0.01,
        max_epochs=20,
        patience=5
    )

    print("Training Custom CNN...")
    print("-" * 50)
    trainer = Trainer(model, train_loader, val_loader, train_config, device)
    result = trainer.train(verbose=True)
    print("-" * 50)
    print()

    # Final test evaluation
    print("Evaluating on test set...")
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

    test_acc = correct / total
    print(f"  Test accuracy: {test_acc*100:.2f}%")
    print()

    # Save results
    filepath = storage.save_result(result, "custom_cnn_result.json")
    print(f"Results saved to: {filepath}")
    print()

    print("Summary:")
    print(f"  Best validation accuracy: {result.best_val_accuracy*100:.2f}%")
    print(f"  Test accuracy: {test_acc*100:.2f}%")
    print(f"  Training time: {result.training_time_seconds:.1f}s")
    print(f"  Total epochs: {result.total_epochs}")

    return result


def demo_2_transfer_learning():
    """
    Demo 2: Transfer Learning Comparison

    Compares training from scratch vs transfer learning:
    - Custom CNN from scratch
    - Frozen ResNet-18 backbone
    - Shows the power of pretrained features
    """
    print("=" * 60)
    print("DEMO 2: Transfer Learning Comparison")
    print("=" * 60)
    print()

    storage = Storage()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print()

    # Use small dataset to highlight transfer learning benefit
    print("Loading small CIFAR-10 subset (100 samples/class)...")
    train_loader, test_loader = get_small_subset_loaders(
        batch_size=32, samples_per_class=100
    )
    print(f"  Train: {len(train_loader.dataset):,} samples")
    print(f"  Test: {len(test_loader.dataset):,} samples")
    print()

    results = []

    # Method 1: Transfer Learning (Frozen ResNet-18)
    print("Method 1: Transfer Learning (Frozen ResNet-18)")
    print("-" * 50)
    transfer_model = create_transfer_model(
        num_classes=10, backbone="resnet18", freeze_backbone=True
    )
    info = analyze_architecture(transfer_model, (3, 224, 224), "ResNet18-Frozen")
    print(f"  Total params: {info.total_params:,}")
    print(f"  Trainable params: {info.trainable_params:,}")
    print()

    train_config = TrainingConfig(
        batch_size=32,
        learning_rate=0.01,  # Higher LR for head only
        max_epochs=10,
        patience=5
    )

    trainer = Trainer(transfer_model, train_loader, test_loader, train_config, device)
    transfer_result = trainer.train(verbose=True)
    transfer_result.model_name = "ResNet18-Frozen"
    results.append(transfer_result)
    print()

    # Method 2: Simple CNN from scratch (adjusted for 224x224)
    print("Method 2: Simple CNN from Scratch")
    print("-" * 50)

    # Create a small CNN for 224x224 input
    class SmallCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(3, 32, 3, stride=2, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(),
                nn.Conv2d(32, 64, 3, stride=2, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.Conv2d(64, 128, 3, stride=2, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1)
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Dropout(0.5),
                nn.Linear(128, 10)
            )

        def forward(self, x):
            x = self.features(x)
            return self.classifier(x)

    scratch_model = SmallCNN()
    info = analyze_architecture(scratch_model, (3, 224, 224), "SmallCNN-Scratch")
    print(f"  Total params: {info.total_params:,}")
    print(f"  Trainable params: {info.trainable_params:,}")
    print()

    train_config = TrainingConfig(
        batch_size=32,
        learning_rate=0.001,
        max_epochs=10,
        patience=5
    )

    trainer = Trainer(scratch_model, train_loader, test_loader, train_config, device)
    scratch_result = trainer.train(verbose=True)
    scratch_result.model_name = "SmallCNN-Scratch"
    results.append(scratch_result)
    print()

    # Comparison
    print("=" * 50)
    print("COMPARISON RESULTS")
    print("=" * 50)
    print()
    print(f"{'Model':<20} {'Best Val Acc':>12} {'Time (s)':>10}")
    print("-" * 44)
    for r in results:
        print(f"{r.model_name:<20} {r.best_val_accuracy*100:>11.2f}% {r.training_time_seconds:>10.1f}")
    print()

    # Save comparison
    comparison = ComparisonResult(
        architectures=[],
        training_results=results,
        best_model=max(results, key=lambda r: r.best_val_accuracy).model_name
    )
    filepath = storage.save_result(comparison, "transfer_learning_comparison.json")
    print(f"Results saved to: {filepath}")
    print()

    print("Key Insight:")
    print("  Transfer learning achieves higher accuracy with the same small dataset")
    print("  because it leverages features learned from 1.2M ImageNet images.")

    return comparison


def demo_3_architecture_analysis():
    """
    Demo 3: CNN Architecture Analysis

    Analyzes and compares different CNN architectures:
    - Parameter counts
    - Memory requirements
    - Layer structure
    """
    print("=" * 60)
    print("DEMO 3: CNN Architecture Analysis")
    print("=" * 60)
    print()

    storage = Storage()

    # Create various architectures
    architectures = {}

    # Custom CNN variants
    for base_ch in [16, 32, 64]:
        config = CNNConfig(base_channels=base_ch, num_blocks=3)
        name = f"CustomCNN-{base_ch}"
        architectures[name] = CustomCNN(config)

    # Pretrained models (for comparison)
    architectures["ResNet-18"] = models.resnet18(weights=None)
    architectures["ResNet-34"] = models.resnet34(weights=None)
    architectures["ResNet-50"] = models.resnet50(weights=None)

    # EfficientNet (different input size)
    architectures["EfficientNet-B0"] = models.efficientnet_b0(weights=None)

    # Analyze all
    print("Architecture Comparison")
    print("-" * 70)
    print(f"{'Name':<20} {'Params':>12} {'Conv':>6} {'FC':>6} {'Memory (MB)':>12}")
    print("-" * 70)

    results = []
    for name, model in architectures.items():
        input_size = (3, 224, 224) if "EfficientNet" in name else (3, 32, 32)
        info = analyze_architecture(model, input_size, name)
        results.append(info)

        print(f"{info.name:<20} {info.total_params:>12,} {info.conv_layers:>6} "
              f"{info.fc_layers:>6} {info.memory_mb:>12.2f}")

    print("-" * 70)
    print()

    # Group analysis
    print("Analysis by Category:")
    print()

    custom = [r for r in results if "CustomCNN" in r.name]
    resnets = [r for r in results if "ResNet" in r.name]

    print("Custom CNNs (CIFAR-10 optimized):")
    for r in custom:
        print(f"  {r.name}: {r.total_params:,} params, {r.conv_layers} conv layers")
    print()

    print("ResNet Family (ImageNet scale):")
    for r in resnets:
        print(f"  {r.name}: {r.total_params:,} params, {r.conv_layers} conv layers")
    print()

    # Save results
    # Convert to serializable format
    comparison_data = {
        "architectures": [asdict(r) for r in results],
        "timestamp": datetime.now().isoformat()
    }
    filepath = os.path.join(storage.storage_dir, "architecture_analysis.json")
    with open(filepath, 'w') as f:
        json.dump(comparison_data, f, indent=2)

    print(f"Results saved to: {filepath}")
    print()

    print("Key Insights:")
    print("  - ResNet-50 has ~2x params vs ResNet-34, but only slightly deeper")
    print("  - Custom CNNs are 100-1000x smaller (designed for CIFAR-10)")
    print("  - Memory scales linearly with parameters")

    return results


def demo_4_generate_report():
    """
    Demo 4: Generate CNN Report

    Generates a comprehensive markdown report from saved results.
    """
    print("=" * 60)
    print("DEMO 4: Generate CNN Report")
    print("=" * 60)
    print()

    storage = Storage()

    # Load any available results
    custom_result = storage.load_result("custom_cnn_result.json")
    comparison_result = storage.load_result("transfer_learning_comparison.json")
    arch_result = storage.load_result("architecture_analysis.json")

    # Generate report
    report_lines = [
        "# CNN Vision Toolkit Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
    ]

    # Custom CNN section
    if custom_result:
        report_lines.extend([
            "## Custom CNN Training Results",
            "",
            f"- **Best Validation Accuracy**: {custom_result.get('best_val_accuracy', 0)*100:.2f}%",
            f"- **Total Epochs**: {custom_result.get('total_epochs', 0)}",
            f"- **Training Time**: {custom_result.get('training_time_seconds', 0):.1f}s",
            "",
        ])

    # Transfer learning section
    if comparison_result and comparison_result.get('training_results'):
        report_lines.extend([
            "## Transfer Learning Comparison",
            "",
            "| Model | Best Val Accuracy | Training Time |",
            "|-------|------------------|---------------|",
        ])
        for tr in comparison_result['training_results']:
            report_lines.append(
                f"| {tr.get('model_name', 'Unknown')} | "
                f"{tr.get('best_val_accuracy', 0)*100:.2f}% | "
                f"{tr.get('training_time_seconds', 0):.1f}s |"
            )
        report_lines.append("")

    # Architecture analysis section
    if arch_result and arch_result.get('architectures'):
        report_lines.extend([
            "## Architecture Analysis",
            "",
            "| Architecture | Parameters | Conv Layers | Memory (MB) |",
            "|--------------|-----------|-------------|-------------|",
        ])
        for arch in arch_result['architectures']:
            report_lines.append(
                f"| {arch.get('name', 'Unknown')} | "
                f"{arch.get('total_params', 0):,} | "
                f"{arch.get('conv_layers', 0)} | "
                f"{arch.get('memory_mb', 0):.2f} |"
            )
        report_lines.append("")

    # Key takeaways
    report_lines.extend([
        "## Key Takeaways",
        "",
        "1. **Transfer learning is powerful**: Even with frozen backbones, pretrained models",
        "   often outperform custom architectures trained from scratch on small datasets.",
        "",
        "2. **Architecture matters**: ResNet's skip connections enable deeper networks",
        "   without the vanishing gradient problem.",
        "",
        "3. **Modern best practices**: BatchNorm, proper initialization, and learning rate",
        "   schedules are essential for training deep CNNs effectively.",
        "",
        "---",
        "",
        "*Generated by Neural Dojo CNN Vision Toolkit*",
    ])

    report = "\n".join(report_lines)

    # Save report
    report_path = os.path.join(storage.storage_dir, "cnn_report.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print("Report generated successfully!")
    print()
    print(f"Report saved to: {report_path}")
    print()
    print("Preview:")
    print("-" * 50)
    # Print first 30 lines
    for line in report_lines[:30]:
        print(line)
    if len(report_lines) > 30:
        print("...")
    print("-" * 50)

    return report_path


# ============================================================================
# MAIN
# ============================================================================

def print_help():
    """Print usage information."""
    print("""
CNN Vision Toolkit - Module 29 Deliverable
==========================================

A comprehensive toolkit for building, training, and analyzing CNNs.

Usage:
    python deliverable_cnn_vision_toolkit.py <command>

Commands:
    demo1   Train a custom CNN on CIFAR-10 with best practices
    demo2   Compare transfer learning vs training from scratch
    demo3   Analyze and compare CNN architectures
    demo4   Generate a comprehensive report from saved results
    help    Show this help message

Examples:
    python deliverable_cnn_vision_toolkit.py demo1
    python deliverable_cnn_vision_toolkit.py demo2
    python deliverable_cnn_vision_toolkit.py demo3
    python deliverable_cnn_vision_toolkit.py demo4

Results are saved to .cnn_toolkit/
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_train_custom_cnn()
    elif command == "demo2":
        demo_2_transfer_learning()
    elif command == "demo3":
        demo_3_architecture_analysis()
    elif command == "demo4":
        demo_4_generate_report()
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
