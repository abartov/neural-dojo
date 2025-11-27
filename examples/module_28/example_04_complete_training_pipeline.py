"""
Module 28, Example 04: Complete Production Training Pipeline

A full training pipeline with all best practices:
- Proper initialization
- Normalization (BatchNorm/LayerNorm)
- Dropout regularization
- Learning rate scheduling with warmup
- Gradient clipping
- Early stopping
- Model checkpointing

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.utils as nn_utils
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
import os
import json
import math
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TrainingConfig:
    """Configuration for training."""
    batch_size: int = 64
    learning_rate: float = 0.001
    weight_decay: float = 0.01
    max_epochs: int = 50
    patience: int = 10
    max_grad_norm: float = 1.0
    warmup_epochs: int = 3
    dropout_rate: float = 0.3
    val_split: float = 0.1
    checkpoint_dir: str = "checkpoints"


class ProductionCNN(nn.Module):
    """
    Production-ready CNN with all best practices.
    """

    def __init__(self, dropout_rate: float = 0.3):
        super().__init__()

        # Feature extractor with BatchNorm
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate / 2),

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate / 2),

            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),  # Global average pooling
        )

        # Classifier with LayerNorm (works well for small batches)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, 10)
        )

        # Apply He initialization for ReLU
        self.apply(self._init_weights)

    def _init_weights(self, m):
        """He initialization for Conv and Linear layers."""
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Linear):
            nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.ones_(m.weight)
            nn.init.zeros_(m.bias)

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


class EarlyStopping:
    """Stop training when validation loss stops improving."""

    def __init__(self, patience: int = 7, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
        self.best_model_state = None
        self.should_stop = False

    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.best_model_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True

        return self.should_stop

    def restore_best(self, model: nn.Module):
        """Restore best model weights."""
        if self.best_model_state:
            model.load_state_dict(self.best_model_state)


class ProductionTrainer:
    """Production-ready trainer with all best practices."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: TrainingConfig,
        device: str = None
    ):
        self.config = config
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader

        # Loss function with label smoothing
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

        # Optimizer with weight decay
        self.optimizer = optim.AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )

        # Learning rate scheduler with warmup
        total_steps = config.max_epochs * len(train_loader)
        warmup_steps = config.warmup_epochs * len(train_loader)

        def lr_lambda(step):
            if step < warmup_steps:
                return step / warmup_steps
            progress = (step - warmup_steps) / (total_steps - warmup_steps)
            return 0.5 * (1 + math.cos(math.pi * progress))

        self.scheduler = LambdaLR(self.optimizer, lr_lambda)

        # Early stopping
        self.early_stopping = EarlyStopping(patience=config.patience)

        # Checkpointing
        os.makedirs(config.checkpoint_dir, exist_ok=True)

        # History
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
            'learning_rates': []
        }

    def train_epoch(self) -> Tuple[float, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0

        for batch_idx, (inputs, targets) in enumerate(self.train_loader):
            inputs, targets = inputs.to(self.device), targets.to(self.device)

            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)

            # Backward pass
            loss.backward()

            # Gradient clipping
            grad_norm = nn_utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.max_grad_norm
            )

            # Optimizer step
            self.optimizer.step()
            self.scheduler.step()

            # Track metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        return total_loss / len(self.train_loader), 100. * correct / total

    @torch.no_grad()
    def validate(self) -> Tuple[float, float]:
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0

        for inputs, targets in self.val_loader:
            inputs, targets = inputs.to(self.device), targets.to(self.device)

            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        return total_loss / len(self.val_loader), 100. * correct / total

    def save_checkpoint(self, epoch: int, is_best: bool = False):
        """Save training checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'history': self.history,
            'config': asdict(self.config)
        }

        path = os.path.join(self.config.checkpoint_dir, f'checkpoint_epoch_{epoch}.pt')
        torch.save(checkpoint, path)

        if is_best:
            best_path = os.path.join(self.config.checkpoint_dir, 'best_model.pt')
            torch.save(checkpoint, best_path)

    def train(self) -> Dict:
        """Complete training loop."""
        print("="*60)
        print("Production Training Pipeline")
        print("="*60)
        print(f"Device: {self.device}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        print(f"Config: {self.config}")
        print("="*60 + "\n")

        best_val_acc = 0

        for epoch in range(self.config.max_epochs):
            start_time = datetime.now()

            # Train
            train_loss, train_acc = self.train_epoch()

            # Validate
            val_loss, val_acc = self.validate()

            # Track
            current_lr = self.optimizer.param_groups[0]['lr']
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            self.history['learning_rates'].append(current_lr)

            # Check for best model
            is_best = val_acc > best_val_acc
            if is_best:
                best_val_acc = val_acc
                print(f"  ★ New best model!")

            # Save checkpoint every 5 epochs and best model
            if epoch % 5 == 0 or is_best:
                self.save_checkpoint(epoch, is_best)

            # Logging
            elapsed = datetime.now() - start_time
            print(f"Epoch {epoch+1:3d}/{self.config.max_epochs} | "
                  f"Train: {train_loss:.4f} ({train_acc:.1f}%) | "
                  f"Val: {val_loss:.4f} ({val_acc:.1f}%) | "
                  f"LR: {current_lr:.6f} | "
                  f"Time: {elapsed.total_seconds():.1f}s")

            # Early stopping
            if self.early_stopping(val_loss, self.model):
                print(f"\n⚡ Early stopping at epoch {epoch+1}")
                self.early_stopping.restore_best(self.model)
                break

        # Final save
        self.save_checkpoint(epoch, is_best=False)

        # Save history as JSON
        history_path = os.path.join(self.config.checkpoint_dir, 'history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)

        print("\n" + "="*60)
        print(f"✓ Training complete!")
        print(f"  Best validation accuracy: {best_val_acc:.1f}%")
        print(f"  Checkpoints saved to: {self.config.checkpoint_dir}/")
        print("="*60)

        return self.history


def main():
    """Run complete training pipeline."""
    print("\n" + "="*60)
    print("Module 28: Complete Production Training Pipeline")
    print("="*60 + "\n")

    # Configuration
    config = TrainingConfig(
        batch_size=64,
        learning_rate=0.001,
        max_epochs=30,
        patience=7,
        dropout_rate=0.3
    )

    # Data
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    full_train = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)

    # Split training into train/val
    val_size = int(len(full_train) * config.val_split)
    train_size = len(full_train) - val_size
    train_dataset, val_dataset = random_split(
        full_train, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Test samples: {len(test_dataset)}")

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, num_workers=0)

    # Create model
    model = ProductionCNN(dropout_rate=config.dropout_rate)

    # Train
    trainer = ProductionTrainer(model, train_loader, val_loader, config)
    history = trainer.train()

    # Final test evaluation
    print("\n" + "="*60)
    print("Final Test Evaluation")
    print("="*60)

    model.eval()
    device = trainer.device
    test_correct = 0
    test_total = 0

    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            test_total += targets.size(0)
            test_correct += predicted.eq(targets).sum().item()

    test_acc = 100. * test_correct / test_total
    print(f"✓ Test Accuracy: {test_acc:.2f}%")

    print("\nTraining techniques used:")
    print("  ✓ He (Kaiming) initialization")
    print("  ✓ BatchNorm + LayerNorm")
    print("  ✓ Dropout regularization")
    print("  ✓ AdamW optimizer with weight decay")
    print("  ✓ Warmup + Cosine annealing LR schedule")
    print("  ✓ Gradient clipping")
    print("  ✓ Early stopping")
    print("  ✓ Model checkpointing")
    print("  ✓ Label smoothing")


if __name__ == "__main__":
    main()
