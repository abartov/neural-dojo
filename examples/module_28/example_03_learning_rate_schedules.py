"""
Module 28, Example 03: Learning Rate Schedule Comparison

Compare different learning rate schedules:
- Constant LR
- Step decay
- Cosine annealing
- 1cycle policy

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR, OneCycleLR, LambdaLR
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
import math


class SimpleCNN(nn.Module):
    """Simple CNN for MNIST."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


def warmup_cosine_schedule(epoch: int, warmup_epochs: int, total_epochs: int) -> float:
    """Linear warmup then cosine decay."""
    if epoch < warmup_epochs:
        return epoch / warmup_epochs
    else:
        progress = (epoch - warmup_epochs) / (total_epochs - warmup_epochs)
        return 0.5 * (1 + math.cos(math.pi * progress))


def train_with_schedule(
    schedule_name: str,
    train_loader: DataLoader,
    test_loader: DataLoader,
    num_epochs: int = 20,
    base_lr: float = 0.1,
    device: str = "cpu"
) -> Dict:
    """Train with a specific learning rate schedule."""
    print(f"\n{'='*50}")
    print(f"Training with {schedule_name} schedule")
    print(f"{'='*50}")

    model = SimpleCNN().to(device)
    optimizer = optim.SGD(model.parameters(), lr=base_lr, momentum=0.9, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    # Create scheduler based on name
    if schedule_name == "Constant":
        scheduler = None
    elif schedule_name == "Step Decay":
        scheduler = StepLR(optimizer, step_size=7, gamma=0.1)
    elif schedule_name == "Cosine":
        scheduler = CosineAnnealingLR(optimizer, T_max=num_epochs)
    elif schedule_name == "Warmup+Cosine":
        scheduler = LambdaLR(
            optimizer,
            lr_lambda=lambda e: warmup_cosine_schedule(e, warmup_epochs=3, total_epochs=num_epochs)
        )
    elif schedule_name == "1cycle":
        total_steps = num_epochs * len(train_loader)
        scheduler = OneCycleLR(
            optimizer,
            max_lr=base_lr,
            total_steps=total_steps,
            pct_start=0.3,
            anneal_strategy='cos'
        )
    else:
        scheduler = None

    history = {
        'train_loss': [],
        'train_acc': [],
        'test_acc': [],
        'learning_rates': []
    }

    # For 1cycle, we need to track LR per step
    is_per_step = schedule_name == "1cycle"

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            # 1cycle updates per step
            if is_per_step and scheduler:
                scheduler.step()

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        train_loss = total_loss / len(train_loader)
        train_acc = 100. * correct / total

        # Per-epoch scheduler update
        if scheduler and not is_per_step:
            scheduler.step()

        current_lr = optimizer.param_groups[0]['lr']

        # Evaluate
        model.eval()
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

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_acc'].append(test_acc)
        history['learning_rates'].append(current_lr)

        print(f"Epoch {epoch+1:2d}: "
              f"Loss={train_loss:.4f}, Train={train_acc:.1f}%, Test={test_acc:.1f}% | "
              f"LR={current_lr:.6f}")

    return history


def plot_lr_comparison(results: Dict[str, Dict], save_path: str = None):
    """Plot learning rate curves and performance."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    colors = {
        'Constant': 'gray',
        'Step Decay': 'red',
        'Cosine': 'blue',
        'Warmup+Cosine': 'green',
        '1cycle': 'purple'
    }

    # Plot 1: Learning Rate
    ax = axes[0]
    for name, hist in results.items():
        ax.plot(hist['learning_rates'], label=name, color=colors.get(name, 'black'))
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Learning Rate')
    ax.set_title('Learning Rate Schedule')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Training Loss
    ax = axes[1]
    for name, hist in results.items():
        ax.plot(hist['train_loss'], label=name, color=colors.get(name, 'black'))
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Training Loss')
    ax.set_title('Training Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Test Accuracy
    ax = axes[2]
    for name, hist in results.items():
        ax.plot(hist['test_acc'], label=name, color=colors.get(name, 'black'))
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Test Accuracy (%)')
    ax.set_title('Test Accuracy')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"\n📊 Plot saved to {save_path}")
    else:
        plt.show()


def main():
    """Run learning rate schedule comparison."""
    print("="*60)
    print("Module 28: Learning Rate Schedule Comparison")
    print("="*60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nUsing device: {device}")

    # Data
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)

    # Use subset for faster demo
    train_dataset = torch.utils.data.Subset(train_dataset, range(10000))
    test_dataset = torch.utils.data.Subset(test_dataset, range(2000))

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64)

    # Schedules to compare
    schedules = ["Constant", "Step Decay", "Cosine", "Warmup+Cosine", "1cycle"]

    results = {}
    for schedule_name in schedules:
        results[schedule_name] = train_with_schedule(
            schedule_name,
            train_loader,
            test_loader,
            num_epochs=20,
            base_lr=0.1,
            device=device
        )

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Schedule':<20} {'Final Test Acc':>15} {'Best Test Acc':>15}")
    print("-"*50)

    for name, hist in results.items():
        final_acc = hist['test_acc'][-1]
        best_acc = max(hist['test_acc'])
        print(f"{name:<20} {final_acc:>14.1f}% {best_acc:>14.1f}%")

    print("\n✓ Experiment complete!")
    print("\nKey observations:")
    print("1. Constant LR often plateaus early")
    print("2. Step decay helps but can be jerky")
    print("3. Cosine annealing is smooth and effective")
    print("4. Warmup helps prevent early divergence")
    print("5. 1cycle often achieves best results fastest")

    # Optionally plot
    try:
        plot_lr_comparison(results, save_path='lr_schedule_comparison.png')
    except Exception as e:
        print(f"\n(Could not create plot: {e})")


if __name__ == "__main__":
    main()
