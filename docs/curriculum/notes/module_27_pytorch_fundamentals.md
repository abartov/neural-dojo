# Module 27: PyTorch Fundamentals

**Last Updated**: 2025-11-27
**Status**: 🟢 Complete
**Duration**: 6-7 hours
**Prerequisites**: Module 26 (Neural Networks from Scratch)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand PyTorch tensors and their relationship to NumPy arrays
- Master automatic differentiation with autograd
- Build neural networks using `nn.Module`
- Implement training loops with optimizers and loss functions
- Move computations between CPU and GPU
- Appreciate the elegance of PyTorch compared to manual implementations

---

## 📖 Introduction: From Pain to Power

In Module 26, you built neural networks from scratch. You computed gradients by hand using the chain rule. You tracked intermediate values in caches. You debugged NaN explosions at 2am.

**It was educational. It was also painful.**

That pain was the point. You now understand what happens under the hood. But here's the truth: nobody builds production neural networks from scratch. It would be like writing a web application in assembly language - technically possible, intellectually impressive, practically insane.

**PyTorch is the power tool that makes deep learning practical.**

Think of it this way: In Module 26, you learned to chop down a tree with a hand axe. Now you get a chainsaw. The chainsaw doesn't make the hand axe knowledge useless - understanding how to fell a tree helps you use the chainsaw safely and effectively.

---

## 💡 Did You Know? The Birth of PyTorch

### The Framework Wars

In 2015, Google released TensorFlow. It was powerful, backed by Google's resources, and quickly became the dominant deep learning framework. But researchers had a problem: TensorFlow was *painful* to use.

TensorFlow 1.x used something called **static graphs**. You had to:
1. Define your entire computation as a graph
2. Compile the graph
3. Create a "session" to run it
4. Feed data through placeholders

It was like writing a recipe, translating it to assembly language, compiling it, and only then cooking - for every single meal.

```python
# TensorFlow 1.x - The pain was real
import tensorflow as tf

# Step 1: Define placeholders (not real data yet!)
x = tf.placeholder(tf.float32, shape=[None, 784])
y = tf.placeholder(tf.float32, shape=[None, 10])

# Step 2: Build the graph (nothing runs!)
W = tf.Variable(tf.zeros([784, 10]))
logits = tf.matmul(x, W)

# Step 3: Create a session
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())  # Initialize
    result = sess.run(logits, feed_dict={x: data})  # Finally run!
```

Debugging was a nightmare. You couldn't just print a variable - you had to evaluate it in a session. Error messages pointed to the graph construction, not where the actual problem was.

### The Facebook Answer

Enter **Soumith Chintala** at Facebook AI Research. He and his team created PyTorch in 2016 with a radical philosophy: **define-by-run**.

Instead of building a graph and then running it, PyTorch builds the graph *as you run Python code*. You write normal Python. You can use print statements. You can use Python debuggers. If statements, for loops - they all just work.

```python
# PyTorch - The relief was immediate
import torch

x = torch.randn(32, 784)  # This creates actual data!
W = torch.randn(784, 10, requires_grad=True)

logits = x @ W  # This actually computes the result!
print(logits.shape)  # You can just print it!
```

### The Research Takeover

By 2019, PyTorch had conquered academia:
- **NeurIPS 2019**: 75% of papers used PyTorch
- **ICLR 2020**: 80% PyTorch
- **CVPR 2020**: 70% PyTorch

Why? Researchers need to iterate fast. They try crazy ideas. Many don't work. Static graphs meant recompiling for every experiment. Dynamic graphs meant instant feedback.

**TensorFlow noticed.** TensorFlow 2.0 (2019) adopted eager execution by default - essentially admitting PyTorch got it right.

### The Name

Why "PyTorch"? It's the Python version of **Torch**, a scientific computing framework written in Lua that was popular in academia during the early 2010s. The original Torch was named after the Olympic torch - a symbol of passing knowledge forward.

The PyTorch logo is a stylized flame - representing both the torch and the "fire" of GPU-accelerated computing.

---

## Part 1: Tensors - The Universal Container

### What is a Tensor, Really?

You've heard "tensor" thrown around. Let's demystify it.

A **tensor** is just a multi-dimensional array. That's it. No magic. But this simple concept is the foundation of *everything* in deep learning.

Think of tensors like containers of different dimensions:

| Dimensions | Math Name | Real Example | Shape |
|------------|-----------|--------------|-------|
| 0 | Scalar | The temperature right now: 72.5°F | `[]` |
| 1 | Vector | Today's hourly temperatures: [68, 70, 72, 75, 73] | `[5]` |
| 2 | Matrix | A grayscale image with pixel values | `[28, 28]` |
| 3 | 3D Tensor | A color image (RGB channels × height × width) | `[3, 224, 224]` |
| 4 | 4D Tensor | A batch of color images | `[32, 3, 224, 224]` |
| 5 | 5D Tensor | A batch of video clips (batch × frames × channels × H × W) | `[8, 16, 3, 224, 224]` |

**The key insight**: Neural networks don't care about what data means. They just see tensors of numbers. An image, a sentence, a stock price history - all become tensors.

### Why PyTorch Tensors Instead of NumPy Arrays?

You might wonder: we already have NumPy. Why learn another array type?

Three killer features:

**1. Automatic Differentiation**

NumPy can do math on arrays. PyTorch can do math on arrays *and track how to compute gradients*. This is the magic that makes deep learning practical.

```python
# NumPy: Just computation
import numpy as np
x = np.array([2.0, 3.0])
y = x ** 2  # [4, 9]
# Now compute dy/dx manually? Good luck!

# PyTorch: Computation + gradient tracking
import torch
x = torch.tensor([2.0, 3.0], requires_grad=True)
y = (x ** 2).sum()  # 13
y.backward()        # Compute gradients automatically
print(x.grad)       # tensor([4., 6.]) - that's dy/dx = 2x!
```

**2. GPU Acceleration**

Moving computation to a GPU in NumPy requires different libraries and painful code changes. In PyTorch, it's one line:

```python
# CPU tensor
x = torch.randn(1000, 1000)

# GPU tensor - one line!
x_gpu = x.cuda()  # or x.to('cuda')
```

**3. Deep Learning Ecosystem**

PyTorch tensors integrate seamlessly with neural network layers, optimizers, data loaders, and the entire deep learning workflow.

### Creating Tensors

Let's get hands-on. There are many ways to create tensors:

**From Python Data**

The most direct way - convert Python lists:

```python
import torch

# From a simple list
x = torch.tensor([1, 2, 3, 4, 5])
print(x)  # tensor([1, 2, 3, 4, 5])

# From nested lists (creates a matrix)
matrix = torch.tensor([[1, 2, 3],
                       [4, 5, 6]])
print(matrix.shape)  # torch.Size([2, 3])
```

**Common Initializations**

In practice, you rarely type out values. You create tensors filled with specific patterns:

```python
# Zeros and ones - common for initialization
zeros = torch.zeros(3, 4)       # 3×4 matrix of zeros
ones = torch.ones(2, 3, 4)      # 2×3×4 tensor of ones

# Random values - essential for weight initialization
uniform = torch.rand(5, 5)      # Uniform between [0, 1)
normal = torch.randn(5, 5)      # Normal distribution (mean=0, std=1)

# Sequences - useful for indices and positions
sequence = torch.arange(0, 10, 2)    # [0, 2, 4, 6, 8]
linspace = torch.linspace(0, 1, 5)   # [0.0, 0.25, 0.5, 0.75, 1.0]

# Identity matrix - useful in linear algebra
identity = torch.eye(4)  # 4×4 identity matrix
```

**Copying Shape from Another Tensor**

Often you need a tensor the same shape as another:

```python
x = torch.randn(3, 4, 5)

# Create zeros/ones with the same shape, dtype, and device
zeros_like_x = torch.zeros_like(x)
ones_like_x = torch.ones_like(x)
random_like_x = torch.randn_like(x)
```

This is especially useful when you need to create tensors on the same device (CPU or GPU) as your model.

### Tensor Properties

Every tensor has properties you'll check constantly:

```python
t = torch.randn(3, 4, 5)

# Shape: The dimensions of the tensor
print(t.shape)      # torch.Size([3, 4, 5])
print(t.size())     # Same thing, method form

# Data type: What kind of numbers
print(t.dtype)      # torch.float32 (default for randn)

# Device: Where the tensor lives
print(t.device)     # cpu (or cuda:0, cuda:1, etc.)

# Number of dimensions
print(t.ndim)       # 3

# Total number of elements
print(t.numel())    # 60 (3 × 4 × 5)
```

### 💡 Did You Know? Data Types Matter More Than You Think

PyTorch supports many data types, and choosing the right one affects both **correctness** and **performance**.

**For Neural Networks (most common)**:
- `torch.float32` (or `torch.float`) - The default. Good balance of precision and speed.
- `torch.float16` (or `torch.half`) - Half precision. 2× faster on modern GPUs, but less precise.
- `torch.bfloat16` - "Brain float". Better for training than float16 because it has more exponent bits.

**For Indices and Counts**:
- `torch.int64` (or `torch.long`) - Required for indices in PyTorch. Most common integer type.
- `torch.int32` - When you know values fit and want to save memory.

**For Images**:
- `torch.uint8` - Unsigned 8-bit integers (0-255). Raw image format.

```python
# Creating tensors with specific types
weights = torch.randn(100, 100, dtype=torch.float32)
indices = torch.tensor([0, 5, 3, 7], dtype=torch.long)
image = torch.randint(0, 256, (3, 224, 224), dtype=torch.uint8)

# Converting between types
weights_half = weights.half()      # to float16
weights_back = weights_half.float()  # back to float32
```

**The fp16 Training Revolution**

In 2017, researchers discovered you could train neural networks in half precision (float16) with almost no accuracy loss - but 2× faster and using half the memory. This "mixed precision training" is now standard for large models.

```python
# Modern training uses automatic mixed precision
with torch.cuda.amp.autocast():
    output = model(input)  # Automatically uses fp16 where safe
```

### The NumPy Bridge

PyTorch and NumPy are best friends. They can share memory, making conversion instant:

```python
import numpy as np

# NumPy → PyTorch (shared memory!)
numpy_array = np.array([1, 2, 3, 4, 5])
tensor = torch.from_numpy(numpy_array)

# They share memory - changes propagate!
numpy_array[0] = 100
print(tensor)  # tensor([100, 2, 3, 4, 5]) - changed too!

# If you want a copy instead:
tensor_copy = torch.tensor(numpy_array)  # Independent copy

# PyTorch → NumPy
tensor = torch.randn(3, 4)
numpy_array = tensor.numpy()  # Shared memory (if on CPU)

# Safe conversion (handles GPU tensors too)
numpy_array = tensor.detach().cpu().numpy()
```

**Warning**: The shared memory behavior is a feature, not a bug. It's fast and memory-efficient. But it can surprise you if you modify one and expect the other unchanged!

---

## Part 2: Autograd - The Magic Behind Deep Learning

This is where PyTorch becomes truly magical. Remember computing gradients by hand in Module 26? All those partial derivatives, the chain rule applied recursively, the careful tracking of intermediate values?

**PyTorch does all of that automatically.**

### The Computational Graph

When you create a tensor with `requires_grad=True`, PyTorch starts recording every operation. It builds an invisible "computational graph" that tracks how to compute gradients.

Let's see it in action:

```python
# Create a tensor that tracks gradients
x = torch.tensor([2.0, 3.0], requires_grad=True)

# Perform operations - PyTorch records them!
y = x ** 2        # y = [4, 9]
z = y.sum()       # z = 13

# Compute gradients
z.backward()

# Gradients are stored in .grad
print(x.grad)     # tensor([4., 6.])
```

What happened? Let's trace through:
- `z = x[0]² + x[1]²`
- `∂z/∂x[0] = 2·x[0] = 2·2 = 4`
- `∂z/∂x[1] = 2·x[1] = 2·3 = 6`

PyTorch computed exactly the gradients we'd compute by hand - but automatically!

### Why This Matters

In Module 26, you implemented backpropagation manually. For a simple network, it was manageable. But modern networks have:
- Millions of parameters
- Hundreds of layers
- Complex architectures (skip connections, attention, normalization)

Computing gradients by hand for GPT-4? That would be tens of thousands of lines of gradient code. With PyTorch:

```python
loss.backward()  # That's it. Gradients for every parameter.
```

### The Chain Rule in Action

The real power shows with complex computations:

```python
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)

# Complex computation with multiple steps
y = x * 2          # y = [2, 4, 6]
z = y ** 2         # z = [4, 16, 36]
loss = z.mean()    # loss = 56/3 ≈ 18.67

# One backward call - all gradients computed!
loss.backward()

print(x.grad)  # tensor([2.6667, 5.3333, 8.0000])
```

Let's verify: The chain rule says:
- `∂loss/∂x = ∂loss/∂z · ∂z/∂y · ∂y/∂x`
- `∂loss/∂z = 1/3` (derivative of mean)
- `∂z/∂y = 2y = [4, 8, 12]`
- `∂y/∂x = 2`
- Result: `[4·2/3, 8·2/3, 12·2/3] = [8/3, 16/3, 24/3]` ✓

### 💡 Did You Know? The Secret History of Automatic Differentiation

Automatic differentiation isn't a deep learning invention. It was developed in the 1960s and 1970s for computational physics and engineering!

**Reverse-mode automatic differentiation** (what PyTorch uses) was published by Seppo Linnainmaa in 1970 for his master's thesis. Backpropagation in neural networks was rediscovered independently in the 1980s - it's the same algorithm applied to neural network computation graphs.

The key insight: forward-mode AD is efficient when you have few inputs and many outputs. Reverse-mode is efficient when you have many inputs and few outputs. Neural networks have millions of inputs (weights) and one output (loss) - reverse mode wins!

### Critical Gotcha: Gradients Accumulate!

This trips up every PyTorch beginner:

```python
x = torch.tensor([1.0], requires_grad=True)

y = x * 2
y.backward()
print(x.grad)  # tensor([2.])

y = x * 3
y.backward()
print(x.grad)  # tensor([5.]) - Not 3! It's 2 + 3!
```

By default, calling `.backward()` **adds** to existing gradients. This is actually useful for some advanced techniques (like gradient accumulation), but usually you want fresh gradients each time.

**The fix**: Zero gradients before each backward pass:

```python
x.grad.zero_()  # Zero out accumulated gradients
y = x * 4
y.backward()
print(x.grad)  # tensor([4.]) - Fresh gradient
```

In training loops, you'll see `optimizer.zero_grad()` - this zeros all parameter gradients.

### When to Detach from the Graph

Sometimes you want to use a computed value without tracking gradients:

```python
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2

# Detach: Creates a new tensor, no gradient tracking
z = y.detach()
print(z.requires_grad)  # False

# Or use no_grad context
with torch.no_grad():
    z = y * 2
    print(z.requires_grad)  # False
```

**When to use this**:
- Computing metrics (accuracy, etc.) during training
- Using a frozen pretrained model
- Preventing gradients from flowing to certain parts of the network

---

## Part 3: Building Neural Networks with nn.Module

Now we get to build actual neural networks! PyTorch provides `torch.nn`, a module specifically designed for deep learning.

### The nn.Module Class

Every neural network in PyTorch inherits from `nn.Module`. This base class provides:
- Automatic parameter registration
- Easy device movement (CPU ↔ GPU)
- Training/evaluation mode switching
- Model saving and loading

Here's the pattern you'll use hundreds of times:

```python
import torch.nn as nn

class SimpleNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()  # Always call this first!

        # Define layers (registered automatically!)
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        # Define how data flows through the network
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Create the network
model = SimpleNetwork(784, 128, 10)

# Forward pass - just call the model!
x = torch.randn(32, 784)  # Batch of 32 images
output = model(x)         # Calls forward() automatically
print(output.shape)       # torch.Size([32, 10])
```

Compare this to Module 26 where you manually created weight matrices, implemented forward propagation, and tracked everything yourself. The PyTorch version is almost self-documenting!

### 💡 Did You Know? Why super().__init__()?

That `super().__init__()` call isn't just Python formality. It initializes PyTorch's internal machinery that:
- Creates a registry for parameters
- Enables recursive calls like `.to(device)` on all submodules
- Sets up hooks for saving/loading

Forget it, and your model silently breaks in confusing ways. Every PyTorch tutorial includes it, and now you know why!

### Common Layers Explained

PyTorch provides layers for every architecture. Here are the ones you'll use most:

**Linear (Fully Connected) Layers**

These are the basic building blocks - matrix multiplication plus bias:

```python
# Linear: y = xW^T + b
layer = nn.Linear(in_features=784, out_features=128)

# What it creates internally:
# - weight: [128, 784] matrix
# - bias: [128] vector (optional, bias=True by default)
```

**Activation Functions**

Activations introduce non-linearity (without them, a deep network is just one linear transformation):

```python
# As modules (use in __init__)
nn.ReLU()           # max(0, x) - most common
nn.LeakyReLU(0.01)  # Allows small negative values
nn.GELU()           # Used in transformers (smoother than ReLU)
nn.Sigmoid()        # Squashes to [0, 1]
nn.Tanh()           # Squashes to [-1, 1]

# As functions (use in forward)
import torch.nn.functional as F
output = F.relu(x)
output = F.gelu(x)
```

**Normalization Layers**

These stabilize training by normalizing intermediate values:

```python
nn.BatchNorm1d(num_features)  # Normalize across batch
nn.LayerNorm(normalized_shape)  # Normalize across features (transformers)
```

**Dropout**

Randomly zeroes elements during training to prevent overfitting:

```python
nn.Dropout(p=0.5)  # 50% of elements set to zero during training
```

### Sequential: The Quick Way

For simple architectures, you don't need a custom class:

```python
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 10)
)

# Works exactly like a custom nn.Module
output = model(input)
```

Use Sequential for prototypes and simple models. Use custom classes when you need complex control flow (if statements, loops, skip connections).

### Inspecting Your Model

PyTorch makes it easy to see what's inside:

```python
model = SimpleNetwork(784, 128, 10)

# Print model structure
print(model)
# SimpleNetwork(
#   (fc1): Linear(in_features=784, out_features=128, bias=True)
#   (fc2): Linear(in_features=128, out_features=10, bias=True)
#   (relu): ReLU()
# )

# List all parameters with names
for name, param in model.named_parameters():
    print(f"{name}: {param.shape}")
# fc1.weight: torch.Size([128, 784])
# fc1.bias: torch.Size([128])
# fc2.weight: torch.Size([10, 128])
# fc2.bias: torch.Size([10])

# Count total parameters
total = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total:,}")  # 101,770
```

---

## Part 4: Training Neural Networks

Now for the payoff - actually training a network!

### Loss Functions: Measuring Wrongness

A loss function measures how wrong your predictions are. Lower is better.

**For Classification** (choosing between categories):

```python
# Cross-entropy loss - the workhorse of classification
criterion = nn.CrossEntropyLoss()

# It expects:
# - Input: Raw logits (NOT softmaxed!)  Shape: [batch, num_classes]
# - Target: Class indices (NOT one-hot!)  Shape: [batch]

logits = torch.randn(32, 10)          # Raw network output
labels = torch.randint(0, 10, (32,))  # Class labels 0-9
loss = criterion(logits, labels)
```

**Critical**: `CrossEntropyLoss` applies softmax internally. Don't softmax your outputs first - you'll get wrong gradients and worse training!

**For Regression** (predicting numbers):

```python
criterion = nn.MSELoss()   # Mean squared error
criterion = nn.L1Loss()    # Mean absolute error
```

### Optimizers: Updating Weights

Optimizers implement gradient descent algorithms. They take gradients and update parameters:

```python
import torch.optim as optim

# SGD: Simple, but needs tuning
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Adam: Usually works well out of the box
optimizer = optim.Adam(model.parameters(), lr=0.001)

# AdamW: Adam with proper weight decay (recommended for transformers)
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```

### 💡 Did You Know? The Adam Story

Adam (2014) combined ideas from two earlier optimizers:
- **Momentum**: Use exponentially weighted average of past gradients
- **RMSprop**: Adapt learning rate per-parameter based on gradient history

The name "Adam" comes from "adaptive moment estimation". Within a year of publication, it became the default optimizer for most deep learning - it just works in most situations without careful tuning.

But it's not perfect! Researchers later found that Adam's weight decay implementation was subtly wrong. **AdamW** (2017) fixed this, and it's now preferred for large models.

### The Training Loop

Here's the standard PyTorch training pattern you'll use forever:

```python
model = SimpleNetwork(784, 128, 10)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(num_epochs):
    model.train()  # Enable training mode (dropout, batchnorm behave differently)

    for batch_idx, (data, labels) in enumerate(train_loader):
        # 1. Zero gradients from previous batch
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

**The five steps are always the same**:
1. Zero gradients
2. Forward pass
3. Compute loss
4. Backward pass
5. Update weights

This pattern works whether you're training a 2-layer network on MNIST or a billion-parameter language model.

### Evaluation Mode

When evaluating (not training), you need to:
1. Switch to evaluation mode (changes dropout/batchnorm behavior)
2. Disable gradient computation (faster, uses less memory)

```python
model.eval()  # Evaluation mode

correct = 0
total = 0

with torch.no_grad():  # Don't compute gradients
    for data, labels in test_loader:
        outputs = model(data)
        _, predicted = outputs.max(1)  # Get predicted class
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f"Accuracy: {accuracy:.2f}%")
```

---

## Part 5: GPU Computing

GPUs can make training 10-100× faster. PyTorch makes GPU computing almost trivially easy.

### Moving to GPU

```python
# Check if CUDA (GPU) is available
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Count: {torch.cuda.device_count()}")
else:
    print("No GPU available, using CPU")

# The standard pattern: create a device variable
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Move tensors
x = torch.randn(1000, 1000)
x_gpu = x.to(device)

# Move models (moves all parameters)
model = SimpleNetwork(784, 128, 10).to(device)

# Create tensors directly on GPU
y = torch.randn(1000, 1000, device=device)
```

### GPU Training Loop

The only change from CPU training: move data to the GPU each batch.

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

### 💡 Did You Know? GPU Memory Gotchas

GPU memory is precious and limited. Common mistakes:

**Memory Leak #1: Storing Tensors in Python Lists**

```python
# BAD - keeps entire computation graph!
losses = []
for batch in loader:
    loss = criterion(model(batch), labels)
    losses.append(loss)  # Full tensor with gradient graph!

# GOOD - just keep the number
losses = []
for batch in loader:
    loss = criterion(model(batch), labels)
    losses.append(loss.item())  # Just the Python float
```

**Memory Leak #2: Not Using no_grad() During Evaluation**

```python
# BAD - builds computation graph unnecessarily
accuracy = (model(data).argmax(1) == labels).float().mean()

# GOOD - no gradient tracking needed
with torch.no_grad():
    accuracy = (model(data).argmax(1) == labels).float().mean()
```

**Checking Memory**:

```python
print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

---

## Part 6: Data Loading

PyTorch's `DataLoader` handles batching, shuffling, and parallel loading.

### Basic Usage

```python
from torch.utils.data import DataLoader, TensorDataset

# Create a dataset from tensors
X = torch.randn(1000, 784)
y = torch.randint(0, 10, (1000,))
dataset = TensorDataset(X, y)

# Create a data loader
loader = DataLoader(
    dataset,
    batch_size=32,       # Samples per batch
    shuffle=True,        # Shuffle each epoch (for training)
    num_workers=4,       # Parallel data loading processes
    pin_memory=True      # Faster GPU transfer
)

# Iterate
for batch_x, batch_y in loader:
    print(batch_x.shape, batch_y.shape)  # [32, 784], [32]
```

### Built-in Datasets

PyTorch provides standard datasets through `torchvision`:

```python
from torchvision import datasets, transforms

# Define preprocessing
transform = transforms.Compose([
    transforms.ToTensor(),              # PIL Image → Tensor
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST mean/std
])

# Load MNIST
train_data = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_data = datasets.MNIST('./data', train=False, download=True, transform=transform)

# Create loaders
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=1000)
```

---

## Part 7: Saving and Loading Models

Always save your trained models!

### Recommended: Save State Dict

```python
# Save just the weights (recommended)
torch.save(model.state_dict(), 'model_weights.pth')

# Load
model = SimpleNetwork(784, 128, 10)  # Create architecture first
model.load_state_dict(torch.load('model_weights.pth'))
model.eval()  # Set to evaluation mode
```

### Checkpointing for Training

For long training runs, save checkpoints to resume later:

```python
# Save checkpoint
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'checkpoint.pth')

# Load checkpoint
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
start_epoch = checkpoint['epoch']
```

### 💡 Did You Know? The .pth Security Risk

PyTorch model files use Python's pickle format. **Pickle can execute arbitrary code when loading!**

```python
# This could run malicious code!
model = torch.load('untrusted_model.pth')  # Dangerous!
```

Only load models from sources you trust. For sharing models publicly, consider the new `safetensors` format that can't execute code.

---

## Part 8: PyTorch vs From-Scratch Comparison

Let's appreciate how far we've come. Here's Module 26 versus PyTorch:

### Module 26: Manual Backpropagation

```python
# Forward pass - tracking everything manually
def forward(self, X):
    self.cache = {'A0': X}
    A = X
    for l in range(1, len(self.layer_dims)):
        Z = self.params[f'W{l}'] @ A + self.params[f'b{l}']
        A = self.activation_fn(Z)
        self.cache[f'A{l}'] = A
    return A

# Backward pass - chain rule by hand
def backward(self, Y):
    m = Y.shape[1]
    dA = -(Y / self.cache[f'A{L}'])

    for l in reversed(range(1, L + 1)):
        dZ = dA * self.activation_derivative(self.cache[f'A{l}'])
        self.grads[f'dW{l}'] = (1/m) * dZ @ self.cache[f'A{l-1}'].T
        self.grads[f'db{l}'] = (1/m) * np.sum(dZ, axis=1, keepdims=True)
        dA = self.params[f'W{l}'].T @ dZ
```

### PyTorch: Elegance

```python
class Network(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)

# Training - all the complexity hidden
outputs = model(inputs)
loss = criterion(outputs, labels)
loss.backward()  # All gradients computed!
optimizer.step()  # All weights updated!
```

**What PyTorch automates**:
- Gradient computation for any architecture
- Cache management
- Numerical stability
- GPU support
- Optimizers
- Data loading
- Model serialization

---

## 💡 Did You Know? The Future: torch.compile()

PyTorch 2.0 (2022) introduced something remarkable: `torch.compile()`.

```python
model = MyModel()
model = torch.compile(model)  # That's it!
```

One line turns your dynamic, debuggable PyTorch model into an optimized, compiled version that runs 30-200% faster. The dynamic graph philosophy remains - you can still use Python control flow, print statements, debuggers - but get static-graph performance.

This represents PyTorch's philosophy: make the right thing easy. Build your model the simple way, debug it, make sure it works. Then compile for production.

---

## Summary

You've learned PyTorch fundamentals:

| Concept | What You Learned |
|---------|-----------------|
| **Tensors** | Multi-dimensional arrays with GPU support and NumPy integration |
| **Autograd** | Automatic differentiation that makes backpropagation trivial |
| **nn.Module** | Clean abstractions for building neural networks |
| **Training** | The 5-step training loop that works for any model |
| **GPU** | One-line device movement for massive speedups |
| **DataLoader** | Efficient batched, parallel data loading |
| **Saving** | Checkpointing for long training runs |

### The Key Insight

Having built neural networks from scratch in Module 26, you now deeply appreciate what PyTorch gives you:

```python
# Module 26: Dozens of lines of careful gradient computation
# PyTorch:
loss.backward()
```

**PyTorch doesn't replace understanding - it amplifies it.** You know what happens inside that one line. You can debug it when things go wrong. You can extend it when needed.

---

## Next Steps

In Module 28, you'll learn **Training Deep Networks**:
- Why deep networks are hard to train
- Batch normalization
- Dropout and regularization
- Weight initialization strategies
- Learning rate scheduling
- Debugging training failures

The foundation is set. Now let's learn the art of making networks actually converge!

---

## Further Reading

1. **Official PyTorch Tutorials**: https://pytorch.org/tutorials/
2. **Deep Learning with PyTorch** (free book): https://pytorch.org/deep-learning-with-pytorch
3. **Andrej Karpathy's micrograd**: https://github.com/karpathy/micrograd - A tiny autograd engine for educational purposes
4. **PyTorch Internals**: http://blog.ezyang.com/2019/05/pytorch-internals/ - How the magic works

---

_Last updated: 2025-11-27_
_Status: 🟢 Complete_
