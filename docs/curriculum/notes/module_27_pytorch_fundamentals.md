# Module 27: PyTorch Fundamentals

**Last Updated**: 2025-11-27
**Status**: In Progress
**Duration**: 4-6 hours

---

## Learning Objectives

By the end of this module, you will:
- Understand PyTorch tensors and their relationship to NumPy arrays
- Master automatic differentiation with autograd
- Build neural networks using `nn.Module`
- Implement training loops with optimizers and loss functions
- Move computations between CPU and GPU
- Appreciate the elegance of PyTorch compared to manual implementations

---

## Introduction: From Scratch to Framework

In Module 26, you built neural networks from scratch. You implemented:
- Forward propagation with matrix multiplications
- Backpropagation computing gradients by hand
- Gradient descent updating weights manually
- Everything in NumPy with careful numerical handling

**It was educational. It was also painful.**

Now imagine doing that for a 100-layer network. Or a transformer with attention mechanisms. Or a GAN with two competing networks. The manual approach doesn't scale.

**Enter PyTorch** - a framework that automates the tedious parts while giving you complete control over the important parts.

---

## The PyTorch Story

### Did You Know? The Birth of PyTorch

PyTorch emerged from Facebook AI Research (FAIR) in 2016, but its roots go deeper. It's actually the spiritual successor to **Torch**, a scientific computing framework written in Lua that was popular in academia.

**Soumith Chintala**, a researcher at FAIR, led the development of PyTorch. The key insight? Take Torch's dynamic computational graphs and bring them to Python - the language the ML community had already adopted.

The timing was perfect. TensorFlow 1.x (released in 2015) was powerful but painful to use:

```python
# TensorFlow 1.x - Static graph (painful)
import tensorflow as tf

# Define placeholders
x = tf.placeholder(tf.float32, shape=[None, 784])
y = tf.placeholder(tf.float32, shape=[None, 10])

# Build graph (this doesn't run anything!)
W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))
logits = tf.matmul(x, W) + b

# Create session and run
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    result = sess.run(logits, feed_dict={x: data})
```

PyTorch offered something revolutionary - **define-by-run**:

```python
# PyTorch - Dynamic graph (pythonic!)
import torch

x = torch.randn(32, 784)  # This actually creates data!
W = torch.randn(784, 10, requires_grad=True)
b = torch.zeros(10, requires_grad=True)

logits = x @ W + b  # This actually computes!
logits.backward(torch.ones_like(logits))  # Gradients computed!
print(W.grad)  # Gradients available immediately!
```

**The difference**: In TensorFlow 1.x, you built a graph, then ran it. In PyTorch, you just... wrote Python. The graph was built as you executed code.

### Did You Know? The Research Takeover

By 2019, **PyTorch dominated research**. A study of papers at major ML conferences found:
- NeurIPS 2019: 75% of papers used PyTorch
- ICLR 2020: 80% PyTorch
- CVPR 2020: 70% PyTorch

Why? Researchers need to experiment quickly. Static graphs meant recompiling for every change. Dynamic graphs meant instant iteration.

**TensorFlow noticed.** TensorFlow 2.0 (2019) adopted eager execution by default - essentially admitting PyTorch got it right.

### Did You Know? The Name

Why "Torch"? The original Lua framework was named after the Olympic torch - a symbol of passing knowledge forward. PyTorch carries that torch (pun intended) into the Python ecosystem.

The logo is a stylized flame - representing both the torch and the "fire" of GPU-accelerated computing.

---

## Part 1: Tensors - The Foundation

### What is a Tensor?

A tensor is a multi-dimensional array. That's it. But that simple concept is the foundation of ALL deep learning.

| Dimensions | Name | Example |
|------------|------|---------|
| 0 | Scalar | Temperature: 72.5 |
| 1 | Vector | Stock prices: [150.2, 148.7, 151.3] |
| 2 | Matrix | Grayscale image: 28x28 pixels |
| 3 | 3D Tensor | RGB image: 3x224x224 |
| 4 | 4D Tensor | Batch of images: 32x3x224x224 |
| 5 | 5D Tensor | Video batch: 32x10x3x224x224 |

### Creating Tensors

```python
import torch

# From Python data
tensor_from_list = torch.tensor([1, 2, 3, 4, 5])
tensor_from_nested = torch.tensor([[1, 2], [3, 4]])

# Common initializations
zeros = torch.zeros(3, 4)          # 3x4 matrix of zeros
ones = torch.ones(2, 3, 4)         # 2x3x4 tensor of ones
random_uniform = torch.rand(5, 5)  # Uniform [0, 1)
random_normal = torch.randn(5, 5)  # Normal(0, 1)
range_tensor = torch.arange(0, 10, 2)  # [0, 2, 4, 6, 8]
linspace = torch.linspace(0, 1, 5)     # [0.0, 0.25, 0.5, 0.75, 1.0]

# Identity matrix
eye = torch.eye(4)

# Like another tensor (same shape, dtype, device)
like_zeros = torch.zeros_like(random_normal)
like_ones = torch.ones_like(random_normal)
```

### Tensor Properties

```python
t = torch.randn(3, 4, 5)

print(t.shape)    # torch.Size([3, 4, 5])
print(t.dtype)    # torch.float32 (default)
print(t.device)   # cpu (or cuda:0)
print(t.ndim)     # 3
print(t.numel())  # 60 (total elements)
```

### Data Types

PyTorch supports many data types:

```python
# Float types (most common for neural networks)
torch.float32  # or torch.float (default)
torch.float64  # or torch.double
torch.float16  # or torch.half (GPU training)
torch.bfloat16 # Brain float (better for training than float16)

# Integer types
torch.int8, torch.int16, torch.int32, torch.int64
torch.uint8  # Common for images (0-255)

# Boolean
torch.bool

# Creating with specific dtype
x = torch.tensor([1.0, 2.0], dtype=torch.float64)
y = torch.zeros(3, 4, dtype=torch.int32)

# Converting dtype
z = x.to(torch.float32)
z = x.float()  # Shorthand
z = x.int()    # To int32
```

### NumPy Bridge

PyTorch and NumPy are best friends. They can share memory!

```python
import numpy as np

# NumPy to PyTorch
numpy_array = np.array([1, 2, 3, 4, 5])
tensor = torch.from_numpy(numpy_array)  # Shares memory!
tensor = torch.tensor(numpy_array)       # Copies data

# PyTorch to NumPy
tensor = torch.randn(3, 4)
numpy_array = tensor.numpy()  # Shares memory (if on CPU)
numpy_array = tensor.detach().cpu().numpy()  # Safe conversion

# Warning: shared memory means changes propagate!
a = np.array([1, 2, 3])
t = torch.from_numpy(a)
a[0] = 100
print(t)  # tensor([100, 2, 3]) - changed too!
```

### Tensor Operations

```python
# Element-wise operations
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

print(a + b)   # tensor([5., 7., 9.])
print(a - b)   # tensor([-3., -3., -3.])
print(a * b)   # tensor([4., 10., 18.])
print(a / b)   # tensor([0.25, 0.4, 0.5])
print(a ** 2)  # tensor([1., 4., 9.])

# In-place operations (with underscore)
a.add_(b)      # a is now [5., 7., 9.]
a.mul_(2)      # a is now [10., 14., 18.]

# Matrix operations
A = torch.randn(3, 4)
B = torch.randn(4, 5)

# Matrix multiplication (3 equivalent ways)
C = A @ B
C = torch.mm(A, B)
C = torch.matmul(A, B)

# Batch matrix multiplication
batch_A = torch.randn(32, 3, 4)  # 32 matrices of 3x4
batch_B = torch.randn(32, 4, 5)  # 32 matrices of 4x5
batch_C = torch.bmm(batch_A, batch_B)  # 32 matrices of 3x5

# Transpose
A_T = A.T
A_T = A.transpose(0, 1)
A_T = A.permute(1, 0)  # More general
```

### Broadcasting

Like NumPy, PyTorch broadcasts operations:

```python
# Scalar broadcast
a = torch.tensor([1, 2, 3])
b = 10
print(a + b)  # tensor([11, 12, 13])

# Vector to matrix broadcast
matrix = torch.randn(3, 4)
row = torch.randn(4)      # Broadcasts across rows
col = torch.randn(3, 1)   # Broadcasts across columns

print((matrix + row).shape)  # [3, 4]
print((matrix + col).shape)  # [3, 4]

# Broadcasting rules:
# 1. Align shapes from the right
# 2. Dimensions must be equal or one of them must be 1
# 3. Missing dimensions are treated as 1
```

### Reshaping Tensors

```python
x = torch.randn(12)

# Reshape (may copy or view)
y = x.reshape(3, 4)
y = x.reshape(2, 2, 3)
y = x.reshape(-1, 4)  # -1 infers dimension: [3, 4]

# View (always a view, shares memory)
y = x.view(3, 4)

# Flatten
x = torch.randn(2, 3, 4)
flat = x.flatten()           # [24]
flat = x.flatten(start_dim=1)  # [2, 12] - keep batch dim

# Squeeze and unsqueeze
x = torch.randn(1, 3, 1, 4)
print(x.squeeze().shape)      # [3, 4] - remove all 1s
print(x.squeeze(0).shape)     # [3, 1, 4] - remove specific dim
print(x.unsqueeze(0).shape)   # [1, 1, 3, 1, 4] - add dim

# Stack and concatenate
a = torch.randn(3, 4)
b = torch.randn(3, 4)
stacked = torch.stack([a, b])      # [2, 3, 4] - new dimension
concatenated = torch.cat([a, b])   # [6, 4] - along existing dim
concatenated = torch.cat([a, b], dim=1)  # [3, 8]
```

### Indexing and Slicing

```python
x = torch.randn(5, 4, 3)

# Basic indexing (like NumPy)
x[0]          # First element along dim 0
x[0, 1]       # First of dim 0, second of dim 1
x[0, 1, 2]    # Scalar

# Slicing
x[1:3]        # Elements 1 and 2 along dim 0
x[:, :2]      # All of dim 0, first 2 of dim 1
x[..., 0]     # Ellipsis: all dims except last, first of last

# Boolean indexing
mask = x > 0
positives = x[mask]  # Flat tensor of positive values

# Fancy indexing
indices = torch.tensor([0, 2, 4])
x[indices]    # Select specific indices
```

---

## Part 2: Autograd - Automatic Differentiation

This is where PyTorch becomes magical. Remember computing gradients by hand in Module 26? PyTorch does it automatically.

### The Computational Graph

When you perform operations on tensors with `requires_grad=True`, PyTorch builds a computational graph:

```python
# Create tensor that tracks gradients
x = torch.tensor([2.0, 3.0], requires_grad=True)

# Perform operations - PyTorch records them!
y = x ** 2        # y = [4, 9]
z = y.sum()       # z = 13

# Compute gradients
z.backward()

# Gradients are stored in .grad
print(x.grad)     # tensor([4., 6.]) = d(z)/d(x) = 2*x
```

What happened?
1. `z = x[0]**2 + x[1]**2`
2. `dz/dx[0] = 2*x[0] = 2*2 = 4`
3. `dz/dx[1] = 2*x[1] = 2*3 = 6`

PyTorch computed this automatically!

### The Chain Rule in Action

```python
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)

# Complex computation
y = x * 2          # y = [2, 4, 6]
z = y ** 2         # z = [4, 16, 36]
loss = z.mean()    # loss = 56/3 ≈ 18.67

# Backward computes all gradients
loss.backward()

# Chain rule: d(loss)/dx = d(loss)/dz * dz/dy * dy/dx
# d(loss)/dz = 1/3 (mean)
# dz/dy = 2y = [4, 8, 12]
# dy/dx = 2
# Result: [4*2/3, 8*2/3, 12*2/3] = [8/3, 16/3, 24/3]
print(x.grad)  # tensor([2.6667, 5.3333, 8.0000])
```

### Gradient Computation Rules

```python
# Gradients accumulate!
x = torch.tensor([1.0], requires_grad=True)

y = x * 2
y.backward()
print(x.grad)  # tensor([2.])

y = x * 3
y.backward()
print(x.grad)  # tensor([5.]) - accumulated! (2 + 3)

# Always zero gradients before new backward
x.grad.zero_()
y = x * 4
y.backward()
print(x.grad)  # tensor([4.]) - fresh gradient
```

### Detaching from the Graph

Sometimes you want to stop gradient flow:

```python
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2

# Detach - creates a new tensor without gradient tracking
z = y.detach()
print(z.requires_grad)  # False

# Or use torch.no_grad() context
with torch.no_grad():
    z = y * 2
    print(z.requires_grad)  # False

# Common use: computing metrics during training
with torch.no_grad():
    accuracy = (predictions.argmax(1) == labels).float().mean()
```

### Did You Know? Autograd's Secret

PyTorch's autograd uses **reverse-mode automatic differentiation**. This is different from:

1. **Numerical differentiation**: `(f(x+h) - f(x)) / h` - slow, imprecise
2. **Symbolic differentiation**: Like Mathematica - creates expression trees, can explode in size
3. **Forward-mode AD**: Computes derivatives alongside forward pass - efficient when few inputs, many outputs
4. **Reverse-mode AD**: Records forward pass, then computes gradients backward - efficient when many inputs, few outputs

Neural networks have millions of parameters (inputs) but one loss (output). Reverse-mode AD is perfect!

**Fun fact**: The algorithm is essentially the same as backpropagation - they were invented independently in different communities (ML vs. optimization) and later recognized as equivalent.

---

## Part 3: Building Neural Networks with nn.Module

PyTorch provides `torch.nn` module for building neural networks. Let's see how it compares to our from-scratch implementation.

### The nn.Module Class

Every neural network in PyTorch inherits from `nn.Module`:

```python
import torch.nn as nn

class SimpleNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()  # Always call this first!

        # Define layers
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        # Define forward pass
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Create network
model = SimpleNetwork(784, 128, 10)

# Forward pass
x = torch.randn(32, 784)  # Batch of 32 images
output = model(x)         # Calls forward() automatically
print(output.shape)       # [32, 10]
```

### Common Layers

```python
# Linear (fully connected)
nn.Linear(in_features, out_features, bias=True)

# Convolutional
nn.Conv1d(in_channels, out_channels, kernel_size)
nn.Conv2d(in_channels, out_channels, kernel_size)

# Recurrent
nn.RNN(input_size, hidden_size, num_layers)
nn.LSTM(input_size, hidden_size, num_layers)
nn.GRU(input_size, hidden_size, num_layers)

# Normalization
nn.BatchNorm1d(num_features)
nn.BatchNorm2d(num_features)
nn.LayerNorm(normalized_shape)

# Dropout
nn.Dropout(p=0.5)
nn.Dropout2d(p=0.5)

# Pooling
nn.MaxPool2d(kernel_size)
nn.AvgPool2d(kernel_size)
nn.AdaptiveAvgPool2d(output_size)

# Embedding (for NLP)
nn.Embedding(num_embeddings, embedding_dim)
```

### Activation Functions

```python
# As modules (use in __init__)
nn.ReLU()
nn.LeakyReLU(negative_slope=0.01)
nn.Sigmoid()
nn.Tanh()
nn.Softmax(dim=1)
nn.GELU()  # Used in transformers

# As functions (use in forward)
import torch.nn.functional as F

F.relu(x)
F.leaky_relu(x, 0.01)
F.sigmoid(x)
F.tanh(x)
F.softmax(x, dim=1)
F.gelu(x)
```

### Sequential Models

For simple architectures, use `nn.Sequential`:

```python
# Instead of defining a class
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 10)
)

# With named layers
model = nn.Sequential(OrderedDict([
    ('fc1', nn.Linear(784, 256)),
    ('relu1', nn.ReLU()),
    ('fc2', nn.Linear(256, 10))
]))

# Access layers
print(model[0])  # First layer
print(model.fc1)  # By name
```

### Inspecting Models

```python
model = SimpleNetwork(784, 128, 10)

# See all parameters
for name, param in model.named_parameters():
    print(f"{name}: {param.shape}")
# fc1.weight: [128, 784]
# fc1.bias: [128]
# fc2.weight: [10, 128]
# fc2.bias: [10]

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total: {total_params:,}, Trainable: {trainable_params:,}")

# Model summary (like Keras)
print(model)
```

---

## Part 4: Loss Functions and Optimizers

### Loss Functions

```python
import torch.nn as nn

# For classification
criterion = nn.CrossEntropyLoss()  # Softmax + NLLLoss
criterion = nn.NLLLoss()           # Negative log likelihood
criterion = nn.BCELoss()           # Binary cross entropy
criterion = nn.BCEWithLogitsLoss() # BCE + Sigmoid (more stable)

# For regression
criterion = nn.MSELoss()           # Mean squared error
criterion = nn.L1Loss()            # Mean absolute error
criterion = nn.SmoothL1Loss()      # Huber loss

# Usage
outputs = model(inputs)          # [batch_size, num_classes]
loss = criterion(outputs, labels)  # labels: [batch_size]
```

**Important**: `nn.CrossEntropyLoss` expects:
- Input: Raw logits (no softmax!)
- Target: Class indices (not one-hot!)

```python
# Correct usage
logits = torch.randn(32, 10)  # Raw network output
labels = torch.randint(0, 10, (32,))  # Class indices [0-9]
loss = nn.CrossEntropyLoss()(logits, labels)

# NOT this (common mistake)
probs = F.softmax(logits, dim=1)  # Don't do this!
loss = nn.CrossEntropyLoss()(probs, labels)  # Wrong!
```

### Optimizers

```python
import torch.optim as optim

# Basic SGD
optimizer = optim.SGD(model.parameters(), lr=0.01)

# SGD with momentum
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# SGD with weight decay (L2 regularization)
optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)

# Adam (most popular)
optimizer = optim.Adam(model.parameters(), lr=0.001)

# AdamW (Adam with correct weight decay)
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# RMSprop
optimizer = optim.RMSprop(model.parameters(), lr=0.01)

# Different learning rates for different layers
optimizer = optim.Adam([
    {'params': model.fc1.parameters(), 'lr': 0.001},
    {'params': model.fc2.parameters(), 'lr': 0.0001}
])
```

### The Training Loop

Here's the standard PyTorch training loop:

```python
model = SimpleNetwork(784, 128, 10)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(num_epochs):
    model.train()  # Set to training mode

    for batch_idx, (data, labels) in enumerate(train_loader):
        # 1. Zero gradients (critical!)
        optimizer.zero_grad()

        # 2. Forward pass
        outputs = model(data)

        # 3. Compute loss
        loss = criterion(outputs, labels)

        # 4. Backward pass (compute gradients)
        loss.backward()

        # 5. Update weights
        optimizer.step()

        if batch_idx % 100 == 0:
            print(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}")
```

### Evaluation Loop

```python
model.eval()  # Set to evaluation mode (disables dropout, etc.)

correct = 0
total = 0

with torch.no_grad():  # No gradient computation needed
    for data, labels in test_loader:
        outputs = model(data)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f"Accuracy: {accuracy:.2f}%")
```

### Did You Know? Why zero_grad()?

In PyTorch, gradients accumulate by default. This is actually useful sometimes:

```python
# Gradient accumulation for larger effective batch sizes
for i, (data, labels) in enumerate(loader):
    outputs = model(data)
    loss = criterion(outputs, labels) / accumulation_steps
    loss.backward()  # Gradients accumulate

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

This lets you train with a batch size of 64 on a GPU that can only fit 16 samples - just accumulate gradients over 4 batches!

---

## Part 5: GPU Computing

### Moving to GPU

```python
# Check if CUDA is available
print(torch.cuda.is_available())  # True if GPU available
print(torch.cuda.device_count())   # Number of GPUs
print(torch.cuda.get_device_name(0))  # GPU name

# Move tensors to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

x = torch.randn(1000, 1000)
x_gpu = x.to(device)
x_gpu = x.cuda()  # Shorthand (if GPU available)

# Move model to GPU
model = SimpleNetwork(784, 128, 10)
model = model.to(device)

# Create tensors directly on GPU
y = torch.randn(1000, 1000, device=device)
```

### Training on GPU

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = SimpleNetwork(784, 128, 10).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(num_epochs):
    for data, labels in train_loader:
        # Move data to GPU
        data = data.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(data)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
```

### Did You Know? GPU Memory

GPU memory is precious! Common issues:

```python
# BAD: Keeping history in Python list
losses = []
for batch in loader:
    loss = criterion(model(batch), labels)
    losses.append(loss)  # Keeps entire computation graph!

# GOOD: Detach from graph
losses = []
for batch in loader:
    loss = criterion(model(batch), labels)
    losses.append(loss.item())  # Just the number

# Check GPU memory
print(torch.cuda.memory_allocated() / 1e9, "GB")
print(torch.cuda.memory_reserved() / 1e9, "GB")

# Clear cache
torch.cuda.empty_cache()
```

---

## Part 6: Data Loading

### The DataLoader

PyTorch provides efficient data loading with `torch.utils.data`:

```python
from torch.utils.data import Dataset, DataLoader, TensorDataset

# Simple dataset from tensors
X = torch.randn(1000, 784)
y = torch.randint(0, 10, (1000,))
dataset = TensorDataset(X, y)

# Create DataLoader
loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,         # Shuffle every epoch
    num_workers=4,        # Parallel data loading
    pin_memory=True,      # Faster GPU transfer
    drop_last=False       # Keep incomplete final batch
)

# Iterate
for batch_x, batch_y in loader:
    print(batch_x.shape, batch_y.shape)  # [32, 784], [32]
```

### Custom Datasets

```python
class CustomDataset(Dataset):
    def __init__(self, data_path, transform=None):
        self.data = load_data(data_path)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        if self.transform:
            sample = self.transform(sample)
        return sample

# Usage
dataset = CustomDataset("path/to/data")
loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Built-in Datasets

```python
from torchvision import datasets, transforms

# MNIST
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST(
    root='./data',
    train=True,
    download=True,
    transform=transform
)

test_dataset = datasets.MNIST(
    root='./data',
    train=False,
    download=True,
    transform=transform
)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000)
```

---

## Part 7: Saving and Loading Models

### Saving

```python
# Save entire model (not recommended)
torch.save(model, 'model.pth')

# Save state dict (recommended)
torch.save(model.state_dict(), 'model_weights.pth')

# Save checkpoint (for resuming training)
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'checkpoint.pth')
```

### Loading

```python
# Load entire model
model = torch.load('model.pth')

# Load state dict
model = SimpleNetwork(784, 128, 10)
model.load_state_dict(torch.load('model_weights.pth'))

# Load checkpoint
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']
loss = checkpoint['loss']

# Load for inference
model.eval()
```

### Did You Know? The .pth Extension

The `.pth` extension is conventional but not required. PyTorch uses Python's pickle internally, so any extension works. However, `.pth` is standard, and `.pt` is also common.

**Security warning**: Loading pickled files can execute arbitrary code! Only load models from trusted sources.

---

## Part 8: Comparing to From-Scratch

Let's compare our Module 26 implementation to PyTorch:

### From Scratch (Module 26)
```python
# Forward pass (our implementation)
def forward(self, X):
    self.cache = {'A0': X}
    A = X
    for l in range(1, len(self.layer_dims)):
        Z = self.params[f'W{l}'] @ A + self.params[f'b{l}']
        A = self.activation_fn(Z)
        self.cache[f'A{l}'] = A
    return A

# Backward pass (our implementation)
def backward(self, Y):
    m = Y.shape[1]
    dA = -(Y / self.cache[f'A{L}'])

    for l in reversed(range(1, L + 1)):
        dZ = dA * self.activation_derivative(self.cache[f'A{l}'])
        self.grads[f'dW{l}'] = (1/m) * dZ @ self.cache[f'A{l-1}'].T
        self.grads[f'db{l}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)
        dA = self.params[f'W{l}'].T @ dZ
```

### PyTorch
```python
class Network(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Training
outputs = model(inputs)
loss = criterion(outputs, labels)
loss.backward()  # Gradients computed automatically!
optimizer.step()
```

**The difference is dramatic:**
- No manual gradient computation
- No cache management
- No numerical stability worries
- Automatic GPU support
- Built-in optimizers
- Easy model serialization

---

## Common Patterns and Best Practices

### 1. Device Agnostic Code

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create tensors on correct device
x = torch.randn(100, device=device)

# Move model once
model = Model().to(device)

# Move data in training loop
for data, labels in loader:
    data, labels = data.to(device), labels.to(device)
```

### 2. Reproducibility

```python
def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(42)
```

### 3. Gradient Clipping

```python
# Clip by norm (most common)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Clip by value
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=0.5)

# In training loop
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
optimizer.step()
```

### 4. Learning Rate Scheduling

```python
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau, CosineAnnealingLR

# Step decay
scheduler = StepLR(optimizer, step_size=10, gamma=0.1)

# Reduce on plateau
scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=5)

# Cosine annealing
scheduler = CosineAnnealingLR(optimizer, T_max=100)

# In training loop
for epoch in range(epochs):
    train(...)
    val_loss = validate(...)
    scheduler.step()  # For most schedulers
    scheduler.step(val_loss)  # For ReduceLROnPlateau
```

---

## Summary

You've learned PyTorch fundamentals:

| Concept | What You Learned |
|---------|-----------------|
| **Tensors** | Multi-dimensional arrays, NumPy bridge, operations |
| **Autograd** | Automatic differentiation, computational graphs |
| **nn.Module** | Building networks, layers, activations |
| **Training** | Loss functions, optimizers, training loops |
| **GPU** | Moving tensors and models to CUDA |
| **Data Loading** | DataLoader, custom datasets |
| **Saving/Loading** | Model checkpoints, state dicts |

### Key Insight

**PyTorch is Python with superpowers.**

Unlike older frameworks that required you to think in terms of graphs and sessions, PyTorch lets you write natural Python code. The framework handles the complex parts (gradient computation, GPU acceleration) while you focus on the model architecture.

Having built neural networks from scratch in Module 26, you now deeply appreciate what PyTorch automates:

```python
# What you did manually in Module 26:
# - Computed forward activations for each layer
# - Implemented backpropagation with chain rule
# - Tracked caches for gradient computation
# - Handled numerical stability (clipping, NaN)
# - Implemented multiple optimizers
# - Managed mini-batch iteration

# What PyTorch does for you:
loss.backward()  # All of the above, automatically
```

---

## Further Reading

1. **Official PyTorch Tutorials**: https://pytorch.org/tutorials/
2. **Deep Learning with PyTorch** (free book): https://pytorch.org/deep-learning-with-pytorch
3. **PyTorch Documentation**: https://pytorch.org/docs/stable/
4. **Andrej Karpathy's micrograd**: https://github.com/karpathy/micrograd

---

## Did You Know? The Future of PyTorch

In 2022, PyTorch 2.0 introduced `torch.compile()` - a way to make PyTorch code run even faster:

```python
model = Model()
model = torch.compile(model)  # That's it!
```

This uses Python's new compiler infrastructure to optimize the entire model, achieving 30-200% speedups with no code changes. The dynamic graph philosophy continues, but now with static-graph-level performance.

PyTorch's philosophy of "research-first, then optimize" has proven powerful. Build in eager mode, debug easily, then compile for production.

---

## Next Steps

In Module 28, you'll learn about **Training Deep Networks**:
- Batch normalization
- Dropout and regularization
- Weight initialization strategies
- Learning rate scheduling
- Debugging training

The foundation is set. Now let's learn to train networks that actually work!

---

_Last updated: 2025-11-27_
_Status: Complete_
