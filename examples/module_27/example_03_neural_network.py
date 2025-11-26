#!/usr/bin/env python3
"""
Example 03: Building Neural Networks with nn.Module
===================================================

This example covers:
1. Creating networks with nn.Module
2. Using nn.Sequential
3. Training loops
4. Loss functions and optimizers
5. Complete MNIST classification example

Module 27: PyTorch Fundamentals
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import time


class SimpleNetwork(nn.Module):
    """A simple feedforward network."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class DeepNetwork(nn.Module):
    """A deeper network with dropout."""

    def __init__(self, input_size: int, hidden_sizes: list, output_size: int,
                 dropout_rate: float = 0.2):
        super().__init__()

        # Build layers dynamically
        layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            prev_size = hidden_size

        layers.append(nn.Linear(prev_size, output_size))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def demo_basic_module():
    """Demonstrate basic nn.Module usage."""
    print("=" * 60)
    print("BASIC nn.Module")
    print("=" * 60)

    # Create network
    model = SimpleNetwork(input_size=10, hidden_size=20, output_size=5)

    print("\n1. Network structure:")
    print(model)

    print("\n2. Parameters:")
    for name, param in model.named_parameters():
        print(f"   {name}: shape {param.shape}, requires_grad={param.requires_grad}")

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n   Total parameters: {total_params:,}")

    print("\n3. Forward pass:")
    x = torch.randn(32, 10)  # Batch of 32, input size 10
    output = model(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")


def demo_sequential():
    """Demonstrate nn.Sequential."""
    print("\n" + "=" * 60)
    print("nn.Sequential")
    print("=" * 60)

    # Basic sequential
    print("\n1. Basic Sequential:")
    model1 = nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )
    print(model1)

    # Named modules
    print("\n2. Sequential with OrderedDict:")
    from collections import OrderedDict
    model2 = nn.Sequential(OrderedDict([
        ('flatten', nn.Flatten()),
        ('fc1', nn.Linear(784, 256)),
        ('relu1', nn.ReLU()),
        ('fc2', nn.Linear(256, 10))
    ]))
    print(model2)

    # Access layers
    print("\n3. Accessing layers:")
    print(f"   model1[0]: {model1[0]}")
    print(f"   model2.fc1: {model2.fc1}")


def demo_layers_and_activations():
    """Demonstrate common layers and activations."""
    print("\n" + "=" * 60)
    print("COMMON LAYERS AND ACTIVATIONS")
    print("=" * 60)

    # Activation functions
    print("\n1. Activation Functions:")
    x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
    print(f"   Input: {x}")

    print(f"   ReLU: {F.relu(x)}")
    print(f"   Sigmoid: {torch.sigmoid(x)}")
    print(f"   Tanh: {torch.tanh(x)}")
    print(f"   LeakyReLU(0.1): {F.leaky_relu(x, 0.1)}")
    print(f"   Softmax: {F.softmax(x, dim=0)}")

    # Linear layer
    print("\n2. Linear Layer:")
    linear = nn.Linear(5, 3)
    x = torch.randn(2, 5)
    output = linear(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    print(f"   Weight shape: {linear.weight.shape}")
    print(f"   Bias shape: {linear.bias.shape}")

    # Dropout
    print("\n3. Dropout:")
    dropout = nn.Dropout(p=0.5)
    x = torch.ones(10)

    dropout.train()  # Enable dropout
    print(f"   Training mode (50% dropped): {dropout(x)}")

    dropout.eval()  # Disable dropout
    print(f"   Eval mode (no dropout): {dropout(x)}")

    # Batch Normalization
    print("\n4. Batch Normalization:")
    bn = nn.BatchNorm1d(5)
    x = torch.randn(32, 5) * 10 + 5  # Mean ~5, std ~10
    print(f"   Input mean: {x.mean():.2f}, std: {x.std():.2f}")

    bn.train()
    output = bn(x)
    print(f"   After BatchNorm: mean={output.mean():.2f}, std={output.std():.2f}")


def demo_loss_functions():
    """Demonstrate common loss functions."""
    print("\n" + "=" * 60)
    print("LOSS FUNCTIONS")
    print("=" * 60)

    # Classification losses
    print("\n1. CrossEntropyLoss (multi-class classification):")
    criterion = nn.CrossEntropyLoss()

    # Logits (raw network output, before softmax)
    logits = torch.tensor([[2.0, 1.0, 0.1],   # Predicts class 0
                           [0.1, 2.0, 0.1],   # Predicts class 1
                           [0.1, 0.1, 2.0]])  # Predicts class 2
    labels = torch.tensor([0, 1, 2])  # Correct labels

    loss = criterion(logits, labels)
    print(f"   Logits:\n{logits}")
    print(f"   Labels: {labels}")
    print(f"   CrossEntropyLoss: {loss.item():.4f}")

    print("\n   IMPORTANT: CrossEntropyLoss expects RAW LOGITS, not softmax!")

    # Binary cross entropy
    print("\n2. BCEWithLogitsLoss (binary classification):")
    criterion = nn.BCEWithLogitsLoss()

    logits = torch.tensor([2.0, -1.0, 0.5])  # Raw outputs
    labels = torch.tensor([1.0, 0.0, 1.0])  # Binary labels

    loss = criterion(logits, labels)
    print(f"   Logits: {logits}")
    print(f"   Labels: {labels}")
    print(f"   BCEWithLogitsLoss: {loss.item():.4f}")

    # Regression losses
    print("\n3. MSELoss (regression):")
    criterion = nn.MSELoss()

    predictions = torch.tensor([2.5, 3.0, 4.5])
    targets = torch.tensor([2.0, 3.5, 4.0])

    loss = criterion(predictions, targets)
    print(f"   Predictions: {predictions}")
    print(f"   Targets: {targets}")
    print(f"   MSELoss: {loss.item():.4f}")

    # L1 Loss
    criterion = nn.L1Loss()
    loss = criterion(predictions, targets)
    print(f"   L1Loss (MAE): {loss.item():.4f}")


def demo_optimizers():
    """Demonstrate common optimizers."""
    print("\n" + "=" * 60)
    print("OPTIMIZERS")
    print("=" * 60)

    # Create a simple model
    model = nn.Linear(10, 1)

    print("\n1. SGD (Stochastic Gradient Descent):")
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    print(f"   {optimizer}")

    print("\n2. SGD with momentum:")
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    print(f"   {optimizer}")

    print("\n3. Adam (most popular):")
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    print(f"   {optimizer}")

    print("\n4. AdamW (Adam with weight decay):")
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    print(f"   {optimizer}")

    # Demonstrate optimization step
    print("\n5. Optimization step:")
    model = nn.Linear(5, 1)
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    x = torch.randn(10, 5)
    y = torch.randn(10, 1)

    print(f"   Initial weight[0]: {model.weight[0, 0].item():.4f}")

    # Forward pass
    pred = model(x)
    loss = F.mse_loss(pred, y)

    # Backward pass
    optimizer.zero_grad()  # Clear previous gradients
    loss.backward()        # Compute gradients
    optimizer.step()       # Update weights

    print(f"   After step weight[0]: {model.weight[0, 0].item():.4f}")
    print("   Weight changed due to gradient update!")


def demo_training_loop():
    """Demonstrate a complete training loop."""
    print("\n" + "=" * 60)
    print("COMPLETE TRAINING LOOP")
    print("=" * 60)

    # Create synthetic dataset
    print("\n1. Creating synthetic classification dataset...")
    torch.manual_seed(42)
    np.random.seed(42)

    n_samples = 1000
    n_features = 20
    n_classes = 3

    X = torch.randn(n_samples, n_features)
    # Create linearly separable classes
    true_weights = torch.randn(n_features, n_classes)
    logits = X @ true_weights
    y = logits.argmax(dim=1)

    # Split into train/test
    train_size = 800
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    print(f"   Train: {X_train.shape}, Test: {X_test.shape}")

    # Create data loaders
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=100)

    # Create model
    model = nn.Sequential(
        nn.Linear(n_features, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, n_classes)
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    print("\n2. Model:")
    print(model)

    # Training loop
    print("\n3. Training for 20 epochs...")
    epochs = 20

    for epoch in range(epochs):
        model.train()  # Set to training mode
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_x, batch_y in train_loader:
            # 1. Zero gradients
            optimizer.zero_grad()

            # 2. Forward pass
            outputs = model(batch_x)

            # 3. Compute loss
            loss = criterion(outputs, batch_y)

            # 4. Backward pass
            loss.backward()

            # 5. Update weights
            optimizer.step()

            # Track metrics
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += batch_y.size(0)
            train_correct += (predicted == batch_y).sum().item()

        train_acc = 100 * train_correct / train_total

        # Evaluation (every 5 epochs)
        if (epoch + 1) % 5 == 0:
            model.eval()  # Set to evaluation mode
            test_correct = 0
            test_total = 0

            with torch.no_grad():  # No gradient computation
                for batch_x, batch_y in test_loader:
                    outputs = model(batch_x)
                    _, predicted = outputs.max(1)
                    test_total += batch_y.size(0)
                    test_correct += (predicted == batch_y).sum().item()

            test_acc = 100 * test_correct / test_total
            print(f"   Epoch {epoch+1:2d}: Train Loss={train_loss/len(train_loader):.4f}, "
                  f"Train Acc={train_acc:.1f}%, Test Acc={test_acc:.1f}%")

    print("\n4. Training complete!")


def demo_save_load():
    """Demonstrate saving and loading models."""
    print("\n" + "=" * 60)
    print("SAVING AND LOADING MODELS")
    print("=" * 60)

    # Create and "train" a model
    model = SimpleNetwork(10, 20, 5)

    # Method 1: Save state dict (recommended)
    print("\n1. Saving state dict (recommended):")
    state_dict = model.state_dict()
    print(f"   State dict keys: {list(state_dict.keys())}")
    # torch.save(state_dict, 'model_weights.pth')
    print("   Would save with: torch.save(model.state_dict(), 'model_weights.pth')")

    # Method 2: Load state dict
    print("\n2. Loading state dict:")
    new_model = SimpleNetwork(10, 20, 5)  # Same architecture
    new_model.load_state_dict(state_dict)
    print("   new_model.load_state_dict(torch.load('model_weights.pth'))")

    # Verify
    x = torch.randn(1, 10)
    out1 = model(x)
    out2 = new_model(x)
    print(f"   Outputs match: {torch.allclose(out1, out2)}")

    # Method 3: Save checkpoint (for resuming training)
    print("\n3. Saving checkpoint (for resuming training):")
    optimizer = optim.Adam(model.parameters())
    checkpoint = {
        'epoch': 10,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': 0.123,
    }
    # torch.save(checkpoint, 'checkpoint.pth')
    print("   Checkpoint includes: epoch, model_state, optimizer_state, loss")


def demo_device_handling():
    """Demonstrate device handling (CPU/GPU)."""
    print("\n" + "=" * 60)
    print("DEVICE HANDLING")
    print("=" * 60)

    # Check for GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n   Using device: {device}")

    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA version: {torch.version.cuda}")

    # Move model to device
    model = SimpleNetwork(784, 128, 10).to(device)
    print(f"\n   Model moved to: {next(model.parameters()).device}")

    # Move data to device
    x = torch.randn(32, 784).to(device)
    print(f"   Data moved to: {x.device}")

    # Forward pass on device
    output = model(x)
    print(f"   Output on: {output.device}")

    # Best practice: device-agnostic code
    print("\n   Device-agnostic pattern:")
    print("""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Model().to(device)

    for data, labels in dataloader:
        data, labels = data.to(device), labels.to(device)
        outputs = model(data)
        ...
    """)


def demo_mnist_mini():
    """A mini MNIST-like classification example."""
    print("\n" + "=" * 60)
    print("MINI MNIST CLASSIFICATION")
    print("=" * 60)

    print("\n   Creating synthetic 'digit-like' dataset...")
    torch.manual_seed(42)

    # Simulate 8x8 images (64 pixels) with 10 classes
    n_samples = 2000
    n_features = 64  # 8x8 image
    n_classes = 10

    # Create patterns for each digit
    X = torch.randn(n_samples, n_features) * 0.1
    y = torch.randint(0, n_classes, (n_samples,))

    # Add class-specific patterns
    for i in range(n_samples):
        digit = y[i].item()
        # Each digit has a unique pattern
        X[i, digit * 6:(digit + 1) * 6] += 1.0

    # Split
    train_size = 1600
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=64, shuffle=True)
    test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=400)

    # Model
    model = nn.Sequential(
        nn.Linear(64, 128),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(64, 10)
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training
    print("\n   Training for 30 epochs...")
    start_time = time.time()

    for epoch in range(30):
        model.train()
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                correct = 0
                total = 0
                for batch_x, batch_y in test_loader:
                    outputs = model(batch_x)
                    _, predicted = outputs.max(1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
                acc = 100 * correct / total
            print(f"   Epoch {epoch+1}: Test Accuracy = {acc:.1f}%")

    elapsed = time.time() - start_time
    print(f"\n   Training complete in {elapsed:.2f}s")

    # Final evaluation
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        for batch_x, batch_y in test_loader:
            outputs = model(batch_x)
            _, predicted = outputs.max(1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

    print(f"   Final Test Accuracy: {100 * correct / total:.1f}%")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("   MODULE 27: BUILDING NEURAL NETWORKS")
    print("=" * 60)

    demo_basic_module()
    demo_sequential()
    demo_layers_and_activations()
    demo_loss_functions()
    demo_optimizers()
    demo_training_loop()
    demo_save_load()
    demo_device_handling()
    demo_mnist_mini()

    print("\n" + "=" * 60)
    print("   SUMMARY")
    print("=" * 60)
    print("""
    Key Takeaways:

    1. nn.Module is the base class for all neural networks
    2. Define layers in __init__, computation in forward()
    3. nn.Sequential for simple architectures
    4. Common losses: CrossEntropyLoss, MSELoss
    5. Common optimizers: Adam, SGD

    Training Loop Pattern:
    ```python
    for epoch in range(epochs):
        model.train()
        for data, labels in train_loader:
            optimizer.zero_grad()    # 1. Clear gradients
            outputs = model(data)    # 2. Forward pass
            loss = criterion(outputs, labels)  # 3. Compute loss
            loss.backward()          # 4. Backward pass
            optimizer.step()         # 5. Update weights
    ```

    You now have all the tools to build and train neural networks!
    """)


if __name__ == "__main__":
    main()
