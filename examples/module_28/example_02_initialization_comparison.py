"""
Module 28, Example 02: Weight Initialization Comparison

Compare Xavier vs He vs Random initialization.
See how initialization affects training convergence.

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
from typing import Dict, Callable, Tuple
import copy


class DeepMLP(nn.Module):
    """
    A deeper MLP to show initialization effects.

    With 8 layers, bad initialization causes gradient problems.
    """

    def __init__(self, init_fn: Callable = None):
        super().__init__()

        # 8 hidden layers - deep enough to see initialization effects
        self.layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 10)
        )

        if init_fn:
            self.apply(init_fn)

    def forward(self, x):
        return self.layers(x)


def init_random(m):
    """Random uniform initialization (the bad old days)."""
    if isinstance(m, nn.Linear):
        nn.init.uniform_(m.weight, -1, 1)
        if m.bias is not None:
            nn.init.uniform_(m.bias, -1, 1)


def init_xavier(m):
    """Xavier/Glorot initialization (good for tanh/sigmoid)."""
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.zeros_(m.bias)


def init_he(m):
    """He/Kaiming initialization (best for ReLU)."""
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
        if m.bias is not None:
            nn.init.zeros_(m.bias)


def init_small(m):
    """Very small initialization (gradients will vanish)."""
    if isinstance(m, nn.Linear):
        nn.init.normal_(m.weight, mean=0, std=0.01)
        if m.bias is not None:
            nn.init.zeros_(m.bias)


def compute_gradient_stats(model: nn.Module) -> Dict[str, float]:
    """Compute gradient statistics across all layers."""
    grad_norms = []
    grad_means = []

    for name, param in model.named_parameters():
        if param.grad is not None and 'weight' in name:
            grad = param.grad.data
            grad_norms.append(grad.norm().item())
            grad_means.append(grad.abs().mean().item())

    return {
        'mean_grad_norm': sum(grad_norms) / len(grad_norms) if grad_norms else 0,
        'max_grad_norm': max(grad_norms) if grad_norms else 0,
        'min_grad_norm': min(grad_norms) if grad_norms else 0,
        'mean_grad_abs': sum(grad_means) / len(grad_means) if grad_means else 0,
    }


def train_with_init(
    init_name: str,
    init_fn: Callable,
    train_loader: DataLoader,
    test_loader: DataLoader,
    num_epochs: int = 15,
    device: str = "cpu"
) -> Dict:
    """Train a model with given initialization."""
    print(f"\n{'='*50}")
    print(f"Training with {init_name} initialization")
    print(f"{'='*50}")

    model = DeepMLP(init_fn=init_fn).to(device)
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    criterion = nn.CrossEntropyLoss()

    history = {
        'train_loss': [],
        'train_acc': [],
        'test_acc': [],
        'gradient_stats': []
    }

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        grad_stats_epoch = []

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            # Check for NaN (exploding gradients)
            if torch.isnan(loss):
                print(f"  ⚠️ NaN loss at epoch {epoch+1}! Training diverged.")
                return history

            loss.backward()

            # Record gradient stats
            grad_stats_epoch.append(compute_gradient_stats(model))

            optimizer.step()

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        train_loss = total_loss / len(train_loader)
        train_acc = 100. * correct / total

        # Aggregate gradient stats
        avg_grad_stats = {
            'mean_grad_norm': sum(s['mean_grad_norm'] for s in grad_stats_epoch) / len(grad_stats_epoch),
            'max_grad_norm': max(s['max_grad_norm'] for s in grad_stats_epoch),
        }

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
        history['gradient_stats'].append(avg_grad_stats)

        print(f"Epoch {epoch+1:2d}: "
              f"Loss={train_loss:.4f}, Train Acc={train_acc:.1f}%, Test Acc={test_acc:.1f}% | "
              f"Grad Norm: {avg_grad_stats['mean_grad_norm']:.4f}")

    return history


def plot_results(results: Dict[str, Dict], save_path: str = None):
    """Plot training curves for all initializations."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    colors = {
        'Random': 'red',
        'Small': 'orange',
        'Xavier': 'blue',
        'He (Kaiming)': 'green'
    }

    # Plot 1: Training Loss
    ax = axes[0]
    for name, hist in results.items():
        if hist['train_loss']:
            ax.plot(hist['train_loss'], label=name, color=colors.get(name, 'gray'))
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Training Loss')
    ax.set_title('Training Loss by Initialization')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Test Accuracy
    ax = axes[1]
    for name, hist in results.items():
        if hist['test_acc']:
            ax.plot(hist['test_acc'], label=name, color=colors.get(name, 'gray'))
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Test Accuracy (%)')
    ax.set_title('Test Accuracy by Initialization')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Gradient Norms
    ax = axes[2]
    for name, hist in results.items():
        if hist['gradient_stats']:
            grad_norms = [s['mean_grad_norm'] for s in hist['gradient_stats']]
            ax.plot(grad_norms, label=name, color=colors.get(name, 'gray'))
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Mean Gradient Norm')
    ax.set_title('Gradient Magnitude by Initialization')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"\n📊 Plot saved to {save_path}")
    else:
        plt.show()


def main():
    """Run initialization comparison experiments."""
    print("="*60)
    print("Module 28: Weight Initialization Comparison")
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

    # Run experiments
    initializations = {
        'Random': init_random,
        'Small': init_small,
        'Xavier': init_xavier,
        'He (Kaiming)': init_he,
    }

    results = {}
    for name, init_fn in initializations.items():
        results[name] = train_with_init(
            name, init_fn, train_loader, test_loader,
            num_epochs=15, device=device
        )

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Initialization':<20} {'Final Test Acc':>15} {'Converged':>12}")
    print("-"*47)

    for name, hist in results.items():
        if hist['test_acc']:
            final_acc = hist['test_acc'][-1]
            converged = "Yes" if final_acc > 80 else "No"
        else:
            final_acc = 0
            converged = "Diverged"
        print(f"{name:<20} {final_acc:>14.1f}% {converged:>12}")

    print("\n✓ Experiment complete!")
    print("\nKey observations:")
    print("1. He initialization works best for ReLU networks")
    print("2. Random uniform can cause extreme gradients")
    print("3. Too-small initialization causes vanishing gradients")
    print("4. Xavier works but He is better for ReLU")

    # Optionally plot
    try:
        plot_results(results, save_path='initialization_comparison.png')
    except Exception as e:
        print(f"\n(Could not create plot: {e})")


if __name__ == "__main__":
    main()
