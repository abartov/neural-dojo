"""
Module 28, Example 01: Normalization Comparison

Compare BatchNorm vs LayerNorm vs no normalization on MNIST.
See how each behaves with different batch sizes.

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time
from typing import Dict, List, Tuple


def create_network(norm_type: str = "batch") -> nn.Module:
    """
    Create a simple MLP with specified normalization.

    Args:
        norm_type: "batch", "layer", or "none"

    Returns:
        PyTorch model
    """
    if norm_type == "batch":
        return nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
    elif norm_type == "layer":
        return nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
    else:  # no normalization
        return nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: str
) -> Tuple[float, float]:
    """Train for one epoch, return loss and accuracy."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    return total_loss / len(loader), 100. * correct / total


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: str
) -> Tuple[float, float]:
    """Evaluate model, return loss and accuracy."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)

        outputs = model(inputs)
        loss = criterion(outputs, targets)

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    return total_loss / len(loader), 100. * correct / total


def run_experiment(
    norm_type: str,
    batch_size: int,
    num_epochs: int = 10,
    device: str = "cpu"
) -> Dict:
    """
    Run a single experiment with given normalization and batch size.

    Returns dict with training history.
    """
    print(f"\n{'='*50}")
    print(f"Experiment: {norm_type} normalization, batch_size={batch_size}")
    print(f"{'='*50}")

    # Data loaders
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)

    # Use smaller subset for faster demo
    train_dataset = torch.utils.data.Subset(train_dataset, range(10000))
    test_dataset = torch.utils.data.Subset(test_dataset, range(2000))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Create model
    model = create_network(norm_type).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    # Training history
    history = {
        'train_loss': [],
        'train_acc': [],
        'test_loss': [],
        'test_acc': [],
        'epoch_times': []
    }

    # Train
    for epoch in range(num_epochs):
        start_time = time.time()

        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)

        epoch_time = time.time() - start_time

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_loss'].append(test_loss)
        history['test_acc'].append(test_acc)
        history['epoch_times'].append(epoch_time)

        print(f"Epoch {epoch+1:2d}: "
              f"Train Loss={train_loss:.4f}, Acc={train_acc:.1f}% | "
              f"Test Loss={test_loss:.4f}, Acc={test_acc:.1f}% | "
              f"Time={epoch_time:.2f}s")

    return history


def main():
    """Run comparison experiments."""
    print("="*60)
    print("Module 28: Normalization Comparison (BatchNorm vs LayerNorm)")
    print("="*60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nUsing device: {device}")

    # Experiments to run
    experiments = [
        ("none", 64),
        ("batch", 64),
        ("layer", 64),
        ("batch", 8),   # Small batch - BatchNorm struggles
        ("layer", 8),   # Small batch - LayerNorm handles it
    ]

    results = {}

    for norm_type, batch_size in experiments:
        key = f"{norm_type}_bs{batch_size}"
        results[key] = run_experiment(
            norm_type=norm_type,
            batch_size=batch_size,
            num_epochs=10,
            device=device
        )

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Experiment':<20} {'Final Test Acc':>15} {'Avg Epoch Time':>15}")
    print("-"*50)

    for key, hist in results.items():
        final_acc = hist['test_acc'][-1]
        avg_time = sum(hist['epoch_times']) / len(hist['epoch_times'])
        print(f"{key:<20} {final_acc:>14.1f}% {avg_time:>14.2f}s")

    print("\n✓ Experiment complete!")
    print("\nKey observations:")
    print("1. BatchNorm typically trains faster with large batches")
    print("2. LayerNorm is more stable with small batches")
    print("3. No normalization struggles with deeper networks")


if __name__ == "__main__":
    main()
