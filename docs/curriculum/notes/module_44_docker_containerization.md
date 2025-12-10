# Module 44: Docker & Containerization for ML

**Last Updated**: 2025-12-10
**Status**: 🟢 Complete
**Duration**: 6-7 hours

---

## The $165 Million Bug That Containers Could Have Prevented

**NASA's Jet Propulsion Laboratory. September 23, 1999.**

The Mars Climate Orbiter had traveled 286 days and 416 million miles through space. As it approached Mars for orbital insertion, ground controllers sent the commands to slow down and enter orbit. Nine minutes of radio silence followed—normal for a maneuver behind the planet.

The signal never returned.

The spacecraft had approached Mars 100 kilometers too low, skipping off the atmosphere and burning up. The root cause? **Lockheed Martin's navigation software produced thrust data in pound-force seconds. NASA's system expected newton-seconds.** One team's environment assumed imperial units; another assumed metric.

**Chris Mattmann**, now Chief Technology and Innovation Officer at NASA JPL and a long-time open source contributor, has spent years advocating for better software engineering practices in aerospace. He later wrote: *"The Mars Climate Orbiter wasn't lost to physics. It was lost to environment assumptions. The code worked perfectly—in the environment it was written for."*

This is the "it works on my machine" problem at its most extreme. And while your ML model probably won't crash into Mars, the same class of problem—code that works in one environment but fails in another—costs organizations billions of dollars annually.

Containers are the solution. They package your code, dependencies, and environment assumptions into a single, portable unit that behaves identically everywhere it runs.

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why containers are essential for ML reproducibility (and why virtual environments aren't enough)
- Master Docker fundamentals: images, containers, layers, and registries
- Build optimized ML Docker images using multi-stage builds
- Handle large ML artifacts (models, data) without bloating your images
- Configure GPU containers with NVIDIA Container Toolkit
- Create Docker Compose stacks for ML development environments
- Apply production best practices that security teams will actually approve

---

## 📖 Why Containers for ML?

### The Reproducibility Crisis Nobody Talks About

Here's a dirty secret of machine learning: **most ML research cannot be reproduced**. And it's not because researchers are sloppy—it's because ML has an environment problem that's worse than traditional software.

**Did You Know?** In 2019, **Odd Erik Gundersen** and **Sigbjørn Kjensmo** at the Norwegian University of Science and Technology surveyed 400 machine learning papers and found that only 6% provided all the information needed to reproduce the results. The missing pieces weren't the algorithms—they were the environments. Which version of PyTorch? Which CUDA? Which cuDNN? Which random number generator?

```
THE "IT WORKS ON MY MACHINE" PROBLEM IN ML
==========================================

Your Laptop                     Production Server
-----------                     -----------------
Python 3.10.4                   Python 3.10.1      ← Minor version = different bytecode
PyTorch 2.0.1                   PyTorch 2.0.0      ← Different numerical precision
CUDA 11.8                       CUDA 11.7          ← Different kernel implementations
cuDNN 8.6.0                     cuDNN 8.5.0        ← Different convolution algorithms
Ubuntu 22.04                    Ubuntu 20.04       ← Different glibc, different syscalls
libc 2.35                       libc 2.31          ← Affects everything that uses C
numpy 1.24.0                    numpy 1.23.5       ← Different BLAS binding

Your model accuracy:            Production accuracy:
         94.2%                              91.7%

You: "But I didn't change anything!"
Reality: You changed EVERYTHING by moving machines.
```

### Why Virtual Environments Aren't Enough

"But wait," you might say, "I use virtualenv/conda/poetry. Isn't that enough?"

No. Here's why:

**Virtual environments only isolate Python packages.** They don't isolate:
- System libraries (libc, libstdc++, OpenSSL)
- CUDA toolkit and cuDNN
- System Python patches
- Operating system differences
- File system structure
- Environment variables set by the OS

**Did You Know?** **Donald Stufft**, a maintainer of pip and PyPI, once traced a "pip install tensorflow" failure across 47 different system configurations. The same pip command produced 12 different outcomes depending on the OS, Python build, and installed system libraries. His conclusion: *"pip install reproduces packages, not environments."*

### What Containers Actually Solve

Containers give you something virtual environments can't: **a complete, isolated environment that includes everything from the kernel up** (except the kernel itself, which is shared).

```
CONTAINER ISOLATION MODEL
=========================

┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR CONTAINER                               │
├─────────────────────────────────────────────────────────────────────┤
│  Your Application Code                                               │
│  ├── train.py                                                       │
│  ├── model.py                                                       │
│  └── requirements.txt                                               │
├─────────────────────────────────────────────────────────────────────┤
│  Python Packages (pip/conda)                                         │
│  ├── torch==2.0.1                                                   │
│  ├── transformers==4.30.0                                           │
│  └── (exact versions, always)                                       │
├─────────────────────────────────────────────────────────────────────┤
│  CUDA Toolkit & cuDNN                                               │
│  └── cuda-11.8, cudnn-8.6.0                                        │
├─────────────────────────────────────────────────────────────────────┤
│  System Libraries                                                    │
│  ├── libc-2.35                                                      │
│  └── libstdc++-11                                                   │
├─────────────────────────────────────────────────────────────────────┤
│  Base OS (Ubuntu 22.04, exact version)                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    (Only this is shared)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         HOST KERNEL                                  │
│  Linux 5.15.x (or whatever the host runs)                           │
└─────────────────────────────────────────────────────────────────────┘

Everything INSIDE the container is frozen, versioned, and reproducible.
Move this container to any Linux machine with Docker = identical behavior.
```

**Did You Know?** **Solomon Hykes** created Docker in 2013 while working at dotCloud, a platform-as-a-service company. The insight that made Docker revolutionary wasn't the underlying technology (Linux had LXC containers since 2008). It was the developer experience: a simple `Dockerfile` that anyone could write, and a `docker run` command that anyone could use. Hykes later said: *"Docker isn't about containers. It's about shipping code. Containers are just the best tool we have for that."*

---

## 🐳 Docker Fundamentals: The Mental Model

### Containers vs. Virtual Machines: The Apartment Analogy

Think of virtual machines like houses and containers like apartments.

**Virtual Machines = Houses**
- Each house has its own foundation, plumbing, electrical, HVAC
- You can customize everything
- Very isolated from neighbors
- But expensive: you're paying for a lot of infrastructure you might not need
- Building a new house takes a long time

**Containers = Apartments**
- Apartments share the building's foundation, plumbing, electrical
- You customize the inside, but not the infrastructure
- Less isolated (thin walls), but good enough for most purposes
- Cheap: you only pay for your unit's space
- Moving in takes minutes, not months

```
VIRTUAL MACHINE                    CONTAINER
===============                    =========

┌─────────────────┐               ┌─────────────────┐
│   Application   │               │   Application   │
├─────────────────┤               ├─────────────────┤
│   Bins/Libs     │               │   Bins/Libs     │
├─────────────────┤               ├─────────────────┤
│   Guest OS      │               │    (nothing)    │
│   (Full Linux)  │               │                 │
├─────────────────┤               ├─────────────────┤
│   Hypervisor    │               │ Container Engine│
├─────────────────┤               ├─────────────────┤
│   Host OS       │               │   Host OS       │
├─────────────────┤               ├─────────────────┤
│   Hardware      │               │   Hardware      │
└─────────────────┘               └─────────────────┘

Disk: 10-50 GB                    Disk: 100 MB - 2 GB
Boot: 30-60 seconds               Boot: < 1 second
Isolation: Hardware-level         Isolation: Process-level
Overhead: 5-20% CPU               Overhead: < 1% CPU
```

### Images vs. Containers: The Recipe Analogy

This distinction confuses everyone at first, so let me be very clear:

- **Image** = A recipe (or blueprint). It defines what goes into the environment but isn't running.
- **Container** = A dish cooked from the recipe. It's the actual running environment.

You can cook multiple dishes from the same recipe. You can run multiple containers from the same image.

```
THE IMAGE/CONTAINER RELATIONSHIP
================================

                    ┌─────────────────┐
                    │                 │
         ┌──────────│  Docker Image   │──────────┐
         │          │  (myapp:v1.0)   │          │
         │          │                 │          │
         │          └─────────────────┘          │
         │                  │                    │
         ▼                  ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Container  │    │  Container  │    │  Container  │
│  (web-1)    │    │  (web-2)    │    │  (web-3)    │
│  Running    │    │  Running    │    │  Stopped    │
└─────────────┘    └─────────────┘    └─────────────┘

Same image → Same starting point
Different containers → Can diverge at runtime (but shouldn't)
```

### The Layer System: How Docker Saves Your Time

Here's where Docker gets clever. Docker images aren't monolithic blobs—they're made of layers, stacked like a cake.

**Did You Know?** **Jérôme Petazzoni**, one of Docker's early engineers, designed the layer caching system. His key insight was that most Dockerfiles follow the same pattern: base OS, then language runtime, then dependencies, then code. If the first three layers haven't changed, why rebuild them? The caching system he designed saves millions of hours of build time daily across Docker users worldwide.

```
LAYER ARCHITECTURE
==================

┌─────────────────────────────────────────┐
│  Layer 6: COPY app.py .                 │  ← Changes every commit
├─────────────────────────────────────────┤
│  Layer 5: COPY model.pkl .              │  ← Changes when model updates
├─────────────────────────────────────────┤
│  Layer 4: RUN pip install -r req.txt    │  ← Changes when deps change
├─────────────────────────────────────────┤
│  Layer 3: COPY requirements.txt .       │  ← Changes when deps change
├─────────────────────────────────────────┤
│  Layer 2: RUN apt-get install python    │  ← Changes rarely
├─────────────────────────────────────────┤
│  Layer 1: FROM ubuntu:22.04             │  ← Almost never changes
└─────────────────────────────────────────┘

CACHE RULES:
1. If a layer changes, all layers ABOVE it are rebuilt
2. Unchanged layers below are reused from cache
3. Order matters: put stable layers first, volatile layers last

PRACTICAL IMPACT:
- Full build from scratch: 10 minutes
- Code-only change (Layer 6): 5 seconds
- This is why we COPY requirements.txt BEFORE COPY app.py
```

### Essential Docker Commands

```bash
# ============================================================
# IMAGE COMMANDS (Working with blueprints)
# ============================================================

docker build -t myapp:v1 .              # Build image from Dockerfile
docker images                            # List all local images
docker pull pytorch/pytorch:2.0.0       # Download from registry
docker push myrepo/myapp:v1             # Upload to registry
docker rmi myapp:v1                     # Delete image
docker history myapp:v1                 # Show layer history
docker image prune                      # Remove unused images

# ============================================================
# CONTAINER COMMANDS (Working with running instances)
# ============================================================

docker run myapp:v1                     # Create + start container
docker run -it myapp:v1 bash            # Interactive mode with shell
docker run -d myapp:v1                  # Detached (background) mode
docker run --name mycontainer myapp:v1  # Named container
docker run -p 8000:8000 myapp:v1        # Map port 8000
docker run -v /host/path:/container/path myapp:v1  # Mount volume
docker run --gpus all myapp:v1          # Enable GPU access

docker ps                               # List running containers
docker ps -a                            # List ALL containers
docker stop mycontainer                 # Stop gracefully
docker kill mycontainer                 # Force stop
docker rm mycontainer                   # Remove stopped container
docker logs mycontainer                 # View stdout/stderr
docker logs -f mycontainer              # Follow logs (like tail -f)
docker exec -it mycontainer bash        # Shell into running container
docker inspect mycontainer              # Detailed JSON info
docker stats                            # Live resource usage

# ============================================================
# CLEANUP COMMANDS (Reclaim disk space)
# ============================================================

docker system df                        # Show disk usage
docker system prune                     # Remove all unused data
docker system prune -a                  # Remove everything unused
docker volume prune                     # Remove unused volumes
```

---

## 🔧 Writing Dockerfiles for ML

### The Naive Approach (And Why It's Problematic)

Let's start with what most people write first:

```dockerfile
# ❌ NAIVE DOCKERFILE - Don't do this
FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "train.py"]
```

This works. Your container runs. But it has serious problems:

1. **Huge image size**: Python base is ~900MB. With ML deps, easily 5-10GB.
2. **Poor cache utilization**: Any code change rebuilds all dependencies.
3. **Security risk**: Runs as root user.
4. **No GPU support**: Won't see your NVIDIA GPUs.
5. **Development cruft**: Tests, docs, .git all included.

**Did You Know?** **Itamar Turner-Trauring**, author of "Docker Packaging for Python Developers," analyzed 1,000 public ML Dockerfiles and found the average image was 4.2GB. After applying best practices, the same functionality averaged 1.1GB—a 74% reduction. Smaller images mean faster deployments, lower storage costs, and reduced attack surface.

### The Optimized Approach: Multi-Stage Builds

Multi-stage builds are Docker's secret weapon. The idea: use one "builder" stage with all your build tools, then copy only the artifacts you need into a clean "production" stage.

```dockerfile
# ✅ OPTIMIZED ML DOCKERFILE

# ==============================================================
# STAGE 1: Builder
# Contains build tools, downloads deps, compiles wheels
# ==============================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies (only needed for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
# Copy requirements FIRST for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================================
# STAGE 2: Production
# Clean, minimal image with only runtime requirements
# ==============================================================
FROM python:3.10-slim AS production

WORKDIR /app

# Copy virtual environment from builder (not the build tools!)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Security: Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Copy only production code (not tests, docs, .git)
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup models/ ./models/

# Switch to non-root user
USER appuser

# Environment settings for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose the service port
EXPOSE 8000

# Health check for orchestrators
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run with production server
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### The Size Difference Is Dramatic

```
IMAGE SIZE COMPARISON
=====================

Naive Dockerfile:
┌─────────────────────────────────────────┐
│  python:3.10 base              (900 MB) │
│  build-essential              (300 MB) │  ← Still there!
│  pip packages                 (2.5 GB) │
│  source code + tests + .git   (100 MB) │
├─────────────────────────────────────────┤
│  TOTAL: ~3.8 GB                         │
└─────────────────────────────────────────┘

Multi-Stage Dockerfile:
┌─────────────────────────────────────────┐
│  python:3.10-slim base        (150 MB) │
│  pip packages (runtime only)  (2.0 GB) │
│  source code only              (20 MB) │
├─────────────────────────────────────────┤
│  TOTAL: ~2.2 GB                         │  ← 42% smaller!
└─────────────────────────────────────────┘

Build tools, compilers, dev dependencies = GONE from production.
```

---

## 🎮 GPU Containers with NVIDIA Container Toolkit

### The GPU Problem

GPUs are special. They're hardware devices that require kernel drivers to function. How can a container—which shares the host kernel—access a GPU that needs specific driver versions?

**Did You Know?** **Felix Abecassis** and the team at NVIDIA spent two years developing what became the NVIDIA Container Toolkit (originally nvidia-docker). The challenge wasn't just technical—it was philosophical. Containers are supposed to be isolated, but GPU access requires kernel-level permissions. Their solution was a carefully designed runtime hook that maintains isolation while allowing controlled GPU access.

### How GPU Containers Actually Work

```
GPU CONTAINER ARCHITECTURE
==========================

┌─────────────────────────────────────────────────────────────────┐
│                         CONTAINER                                │
├─────────────────────────────────────────────────────────────────┤
│  Your ML Application                                             │
│  ├── PyTorch / TensorFlow                                       │
│  └── Your model code                                            │
├─────────────────────────────────────────────────────────────────┤
│  CUDA Toolkit Libraries (inside container)                       │
│  ├── nvcc (compiler)                                            │
│  ├── cuBLAS (linear algebra)                                    │
│  ├── cuDNN (neural network primitives)                          │
│  └── NCCL (multi-GPU communication)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  NVIDIA Container │
                    │     Toolkit       │  ← The magic bridge
                    └─────────┬─────────┘
                              │
                    (Mounts these at runtime:)
                    /dev/nvidia0, /dev/nvidia1, ...
                    libnvidia-ml.so, libcuda.so
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                         HOST                                     │
├─────────────────────────────────────────────────────────────────┤
│  NVIDIA Driver (installed on host)                               │
│  └── Must be >= CUDA version in container                       │
├─────────────────────────────────────────────────────────────────┤
│  Linux Kernel                                                    │
├─────────────────────────────────────────────────────────────────┤
│  GPU Hardware (RTX 4090, A100, H100, etc.)                      │
└─────────────────────────────────────────────────────────────────┘

KEY INSIGHT:
- CUDA toolkit goes IN the container (versioned, reproducible)
- NVIDIA driver stays ON the host (shared, kernel-level)
- Container Toolkit bridges them at runtime
```

### GPU Dockerfile for ML Training

```dockerfile
# GPU-enabled ML Training Dockerfile
FROM nvidia/cuda:11.8-cudnn8-runtime-ubuntu22.04

# Prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and essential tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-venv \
    python3.10-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR /app

# Install PyTorch with CUDA support
# IMPORTANT: PyTorch CUDA version must match container CUDA version
RUN pip install --no-cache-dir \
    torch==2.0.1+cu118 \
    torchvision==0.15.2+cu118 \
    torchaudio==2.0.2+cu118 \
    --extra-index-url https://download.pytorch.org/whl/cu118

# Install other ML dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy training code
COPY src/ ./src/

# Environment variables for NVIDIA runtime
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Data and output directories (to be mounted as volumes)
VOLUME ["/data", "/output", "/checkpoints"]

# Training entry point
ENTRYPOINT ["python", "-m", "src.train"]
# Arguments can be passed at runtime:
# docker run --gpus all myapp:gpu --epochs 100 --lr 0.001
```

### Running GPU Containers

```bash
# Basic GPU access
docker run --gpus all myapp:gpu

# Specific GPUs (for multi-GPU machines)
docker run --gpus '"device=0"' myapp:gpu           # First GPU only
docker run --gpus '"device=0,1"' myapp:gpu         # First two GPUs
docker run --gpus '"device=GPU-3a2c..."' myapp:gpu # By UUID

# With shared memory (important for DataLoader workers!)
docker run --gpus all --shm-size=16g myapp:gpu

# With data volumes mounted
docker run --gpus all \
    -v /data/datasets:/data \
    -v /data/outputs:/output \
    -v /data/checkpoints:/checkpoints \
    myapp:gpu

# Verify GPU access inside container
docker run --gpus all nvidia/cuda:11.8-base nvidia-smi
```

### CUDA Version Compatibility: The Gotcha

This is where many people get burned. The CUDA version in your container must be compatible with the driver on the host.

```
CUDA COMPATIBILITY MATRIX
=========================

Host Driver Version    Supports Container CUDA Versions
-------------------    ---------------------------------
550.x (newest)         CUDA 12.4 and ALL earlier versions
535.x                  CUDA 12.2 and ALL earlier versions
525.x                  CUDA 12.0 and ALL earlier versions
515.x                  CUDA 11.7 and ALL earlier versions
470.x                  CUDA 11.4 and ALL earlier versions

THE RULE: Host driver must be >= container CUDA toolkit
          (Forward compatible, NOT backward compatible)

EXAMPLE:
- Host has driver 525.85 (supports up to CUDA 12.0)
- Container with CUDA 11.8  ✅ Works perfectly
- Container with CUDA 12.1  ❌ Fails: "CUDA driver version insufficient"

PRO TIP: Use `nvidia-smi` on host to check driver version
         Look at "CUDA Version" in top right = max supported
```

**Did You Know?** NVIDIA's driver versioning scheme is deliberately confusing. **Bryan Catanzaro**, VP of Applied Deep Learning Research at NVIDIA, once joked at a conference: *"Our driver version numbers are designed to keep developers humble."* The version number (like 525.85) encodes the supported CUDA versions, but you need to look up the compatibility matrix to decode it.

---

## 📦 Handling Large ML Artifacts

### The Model Size Problem

ML models are big. Really big.

```
MODEL SIZE HALL OF FAME (2024)
==============================

BERT-base-uncased:           440 MB
GPT-2:                       1.5 GB
Stable Diffusion v1.5:       4 GB
LLaMA-7B:                    13 GB
Mistral-7B:                  14 GB
LLaMA-70B:                   140 GB
GPT-4 (rumored):             ~1.7 TB (!)

If you bake these into Docker images:
- Image size explodes
- Every model update = new image
- Registry storage costs skyrocket
- `docker pull` takes forever
- Your CI/CD pipeline cries
```

### Strategy 1: Download at Runtime

Keep your image lean. Download the model when the container starts.

```dockerfile
# Image stays small
FROM python:3.10-slim

COPY download_model.py .
COPY src/ ./src/

# Model downloaded at runtime, not build time
CMD ["sh", "-c", "python download_model.py && python -m src.serve"]
```

```python
# download_model.py
"""Download model at container startup if not cached."""

import os
from pathlib import Path
from huggingface_hub import snapshot_download

MODEL_ID = os.environ.get("MODEL_ID", "bert-base-uncased")
CACHE_DIR = Path(os.environ.get("MODEL_CACHE", "/models"))

def download_if_needed():
    model_path = CACHE_DIR / MODEL_ID.replace("/", "--")

    if model_path.exists():
        print(f"✅ Model {MODEL_ID} already cached at {model_path}")
        return model_path

    print(f"⬇️  Downloading {MODEL_ID}...")
    path = snapshot_download(
        MODEL_ID,
        cache_dir=CACHE_DIR,
        local_dir=model_path,
    )
    print(f"✅ Downloaded to {path}")
    return path

if __name__ == "__main__":
    download_if_needed()
```

### Strategy 2: Volume Mounts

Keep models on the host, mount into container.

```bash
# Host manages the model files
/host/models/
├── bert-base-uncased/
├── gpt2/
└── custom-model-v3/

# Mount at runtime
docker run -v /host/models:/models myapp:v1

# Or use Docker volumes for persistence across container restarts
docker volume create ml-models
docker run -v ml-models:/models myapp:v1

# Pre-populate the volume
docker run -v ml-models:/models myapp:v1 python download_model.py
```

### Strategy 3: Model Registry Integration

Let your model registry (MLflow, W&B, custom) manage versioning.

```python
# src/serve.py
"""Serve models from MLflow registry."""

import os
import mlflow

# Model coordinates from environment
MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
MODEL_NAME = os.environ["MODEL_NAME"]
MODEL_STAGE = os.environ.get("MODEL_STAGE", "Production")

mlflow.set_tracking_uri(MLFLOW_URI)

# Load the model (downloaded automatically)
model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
print(f"Loading model from {model_uri}")
model = mlflow.pyfunc.load_model(model_uri)

# Use the model...
```

```bash
docker run \
    -e MLFLOW_TRACKING_URI=http://mlflow-server:5000 \
    -e MODEL_NAME=fraud-detector \
    -e MODEL_STAGE=Production \
    myapp:v1
```

### Strategy 4: Layered Model Images

For when you really need models in the image (air-gapped environments, etc.).

```dockerfile
# Layer 1: Base inference image (reusable)
FROM python:3.10-slim AS inference-base
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
# This layer is cached and shared

# Layer 2: Model-specific image (extends base)
FROM inference-base AS model-bert
COPY models/bert/ ./models/
ENV MODEL_PATH=/app/models/bert

# Different model, same base (shares all but last layer)
FROM inference-base AS model-gpt2
COPY models/gpt2/ ./models/
ENV MODEL_PATH=/app/models/gpt2
```

```bash
# Build different model variants
docker build --target model-bert -t myapp:bert .
docker build --target model-gpt2 -t myapp:gpt2 .

# They share base layers, so second build is fast
```

---

## 🐙 Docker Compose for ML Development

### Why Compose?

ML systems are never just one container. A realistic development environment includes:

```
TYPICAL ML DEVELOPMENT STACK
============================

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Model   │  │   API    │  │  Vector  │  │  Redis   │       │
│  │ Training │  │  Server  │  │    DB    │  │  Cache   │       │
│  │ (GPU)    │  │          │  │ (Qdrant) │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │             │             │             │               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │ MLflow   │  │ Jupyter  │  │ Postgres │                     │
│  │ Tracking │  │   Lab    │  │ (meta)   │                     │
│  └──────────┘  └──────────┘  └──────────┘                     │
│       │             │             │                             │
│       └─────────────┴─────────────┘                             │
│                     │                                           │
│              ┌──────┴──────┐                                    │
│              │   Docker    │                                    │
│              │   Network   │                                    │
│              └─────────────┘                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Managing this with individual `docker run` commands = nightmare
Docker Compose = one file, one command, everything works
```

### Complete ML Development docker-compose.yml

```yaml
# docker-compose.yml - ML Development Environment
version: '3.8'

services:
  # ============================================================
  # ML API Server (Your main application)
  # ============================================================
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src              # Hot reload during development
      - model-cache:/app/models     # Shared model cache
    environment:
      - MODEL_PATH=/app/models
      - QDRANT_HOST=qdrant
      - REDIS_HOST=redis
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - LOG_LEVEL=DEBUG
    depends_on:
      - redis
      - qdrant
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================================
  # Vector Database (for embeddings/RAG)
  # ============================================================
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"     # REST API
      - "6334:6334"     # gRPC
    volumes:
      - qdrant-data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334

  # ============================================================
  # Redis (caching, rate limiting)
  # ============================================================
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  # ============================================================
  # MLflow (experiment tracking)
  # ============================================================
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.0
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
      - ./mlruns:/mlflow/mlruns
    environment:
      - MLFLOW_TRACKING_URI=sqlite:///mlflow/mlflow.db
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:///mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts

  # ============================================================
  # Jupyter Lab (notebooks, experimentation)
  # ============================================================
  jupyter:
    build:
      context: .
      dockerfile: Dockerfile.jupyter
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/app/notebooks
      - ./src:/app/src
      - model-cache:/app/models
    environment:
      - JUPYTER_TOKEN=dev-token-change-in-prod
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ============================================================
  # PostgreSQL (for MLflow metadata, optional)
  # ============================================================
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=mlflow
      - POSTGRES_PASSWORD=mlflow_password
      - POSTGRES_DB=mlflow

# ============================================================
# Named Volumes (persist data across restarts)
# ============================================================
volumes:
  model-cache:
    name: ml-model-cache
  qdrant-data:
    name: ml-qdrant-data
  redis-data:
    name: ml-redis-data
  mlflow-data:
    name: ml-mlflow-data
  postgres-data:
    name: ml-postgres-data

# ============================================================
# Custom Network (optional, Compose creates one automatically)
# ============================================================
networks:
  default:
    name: ml-network
```

### Docker Compose Commands

```bash
# Start everything
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start specific services
docker-compose up api redis qdrant

# Rebuild images before starting
docker-compose up --build

# View logs (all services)
docker-compose logs

# View logs (specific service, follow mode)
docker-compose logs -f api

# Stop everything (keeps volumes)
docker-compose down

# Stop and remove volumes (destructive!)
docker-compose down -v

# Restart a service
docker-compose restart api

# Scale stateless services
docker-compose up --scale api=3

# Execute command in running container
docker-compose exec api python -c "print('hello')"
```

### Development vs Production Configurations

```yaml
# docker-compose.yml (base - always loaded)
version: '3.8'
services:
  api:
    build: .
    environment:
      - MODEL_PATH=/app/models
```

```yaml
# docker-compose.override.yml (development - loaded automatically)
version: '3.8'
services:
  api:
    volumes:
      - ./src:/app/src                    # Live code reload
    environment:
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    ports:
      - "8000:8000"                       # Expose for local access
```

```yaml
# docker-compose.prod.yml (production - must specify explicitly)
version: '3.8'
services:
  api:
    image: myregistry/api:v1.0.0          # Use pre-built image
    environment:
      - LOG_LEVEL=WARNING
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
```

```bash
# Development (override loaded automatically)
docker-compose up

# Production (explicit file selection)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🏭 Production Best Practices

### Security Hardening

**Did You Know?** In 2020, **Aqua Security's** container security research team found that 51% of Docker images on Docker Hub contained at least one critical vulnerability. Most were in the base image or unused dependencies that shouldn't have been included. Security isn't about paranoia—it's about not inheriting other people's problems.

```dockerfile
# SECURITY-HARDENED DOCKERFILE

# 1. Use specific versions, never 'latest'
FROM python:3.10.12-slim-bookworm

# 2. Don't run as root
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --no-create-home appuser

WORKDIR /app

# 3. Minimize installed packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# 4. Set restrictive permissions
RUN chown -R appuser:appgroup /app

# 5. Install dependencies as root, then drop privileges
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup src/ ./src/

# 6. Switch to non-root user
USER appuser

# 7. Expose only necessary ports
EXPOSE 8000

# 8. Use exec form for CMD (no shell injection)
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Run container with additional security:
# docker run --read-only --cap-drop=ALL --security-opt=no-new-privileges myapp
```

### The .dockerignore File

Just like `.gitignore` for Git, `.dockerignore` tells Docker what NOT to include in the build context.

```
# .dockerignore for ML Projects

# Version control
.git
.gitignore
.gitattributes

# Environment files (often contain secrets!)
.env
.env.*
*.env

# Documentation
*.md
docs/
README*

# Test files
tests/
test_*.py
*_test.py
pytest.ini
.pytest_cache/

# Development tools
.vscode/
.idea/
*.sublime-*
.editorconfig

# Jupyter artifacts
notebooks/
*.ipynb
.ipynb_checkpoints/

# Python artifacts
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.eggs/
dist/
build/
*.egg

# Type checking / linting caches
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Large data files (should be mounted, not copied)
data/
*.csv
*.parquet
*.h5
*.hdf5

# Model files (should use volumes or download at runtime)
models/
*.pkl
*.joblib
*.pt
*.pth
*.onnx
*.safetensors

# ML experiment tracking
wandb/
mlruns/
lightning_logs/

# Docker files (avoid inception)
Dockerfile*
docker-compose*
.dockerignore

# Misc
Makefile
*.log
*.tmp
```

### Health Checks That Actually Work

```python
# src/health.py
"""Health check endpoints for container orchestration."""

from fastapi import FastAPI, Response, status
import torch
import psutil
import os

app = FastAPI()

# Global model reference (set by your main app)
model = None
model_ready = False


@app.get("/health")
async def health():
    """
    Basic health check: Is the container running?
    Used by: Docker HEALTHCHECK, basic monitoring
    Returns 200 if process is alive.
    """
    return {"status": "healthy", "pid": os.getpid()}


@app.get("/ready")
async def ready(response: Response):
    """
    Readiness check: Is the service ready to accept traffic?
    Used by: Kubernetes readinessProbe, load balancers
    Returns 200 only when model is loaded and service is ready.
    """
    checks = {
        "model_loaded": model is not None,
        "model_ready": model_ready,
        "memory_ok": psutil.virtual_memory().percent < 90,
    }

    if torch.cuda.is_available():
        checks["gpu_available"] = True
        checks["gpu_memory_ok"] = (
            torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() < 0.95
            if torch.cuda.max_memory_allocated() > 0
            else True
        )

    all_ready = all(checks.values())

    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {"ready": all_ready, "checks": checks}


@app.get("/live")
async def live(response: Response):
    """
    Liveness check: Should the container be restarted?
    Used by: Kubernetes livenessProbe
    Returns 200 unless something is catastrophically wrong.
    """
    try:
        # Basic sanity checks
        _ = 1 + 1  # Python is running
        _ = os.getcwd()  # Filesystem is accessible

        if torch.cuda.is_available():
            _ = torch.cuda.current_device()  # GPU is accessible

        return {"live": True}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"live": False, "error": str(e)}
```

---

## 🔍 Debugging Docker Containers

### Common Issues and Solutions

```
ISSUE: "ModuleNotFoundError: No module named 'xyz'"
-----------------------------------------------
CAUSE: Package not installed, or wrong Python environment
DEBUG: docker run -it myapp:v1 pip list
FIX:
  - Add package to requirements.txt
  - Check you're using the right Python (python vs python3)
  - Verify virtualenv is activated (PATH includes /opt/venv/bin)


ISSUE: "CUDA out of memory"
---------------------------
CAUSE: Model + batch don't fit in GPU memory
DEBUG: docker run --gpus all myapp:v1 nvidia-smi
FIX:
  - Reduce batch size
  - Use gradient checkpointing
  - Add --shm-size=16g for DataLoader workers
  - Use smaller model or quantization


ISSUE: Container exits immediately
----------------------------------
CAUSE: CMD completes or crashes during startup
DEBUG: docker run -it myapp:v1 bash  # then run CMD manually
FIX:
  - Check docker logs <container>
  - Add error handling to startup
  - Ensure CMD is a long-running process


ISSUE: "Permission denied" errors
---------------------------------
CAUSE: Running as non-root, file ownership mismatch
DEBUG: docker run -it myapp:v1 id && ls -la
FIX:
  - Use --chown in COPY instructions
  - Ensure directories exist before writing
  - Check volume mount permissions


ISSUE: Build is slow / cache not working
----------------------------------------
CAUSE: Layer order wrong, or .dockerignore missing
DEBUG: docker build --progress=plain to see layer cache status
FIX:
  - Order Dockerfile: base → system deps → Python deps → code
  - Add .dockerignore to exclude unnecessary files
  - COPY requirements.txt BEFORE COPY source code
```

### Debugging Commands

```bash
# Run interactive shell in image (to explore)
docker run -it myapp:v1 bash

# Shell into RUNNING container (to debug live)
docker exec -it <container_id> bash

# View logs (stdout/stderr)
docker logs <container_id>
docker logs -f <container_id>          # Follow (like tail -f)
docker logs --tail 100 <container_id>  # Last 100 lines

# Inspect container configuration
docker inspect <container_id>
docker inspect <container_id> | jq '.[0].Config.Env'  # Just environment

# Resource usage
docker stats <container_id>

# Copy files out of container for analysis
docker cp <container_id>:/app/logs ./local-logs

# Build with full output (see cache hits/misses)
docker build --progress=plain -t myapp:v1 .

# Build without cache (force full rebuild)
docker build --no-cache -t myapp:v1 .
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Basic ML Dockerfile

Create a Dockerfile for a simple scikit-learn inference service:
- Python 3.10 slim base
- Install scikit-learn and fastapi
- Copy a pre-trained model (pickle file)
- Expose port 8000
- Run with uvicorn

### Exercise 2: Multi-Stage Optimization

Convert your Dockerfile to multi-stage:
- Builder stage: install build tools, compile dependencies
- Production stage: slim base, only runtime requirements
- Compare image sizes before and after

### Exercise 3: GPU Training Container

Create a GPU-enabled training container:
- NVIDIA CUDA base image
- PyTorch with CUDA support
- Volume mounts for data, checkpoints, and outputs
- Run with `--gpus all --shm-size=16g`

### Exercise 4: Complete Compose Stack

Create a docker-compose.yml with:
- ML API service (your model)
- Qdrant for vector search
- Redis for caching
- MLflow for experiment tracking
- Jupyter for development

---

## 📚 Further Reading

### Official Documentation
- [Docker Documentation](https://docs.docker.com/) - The authoritative source
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/) - GPU container setup
- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/) - Complete reference

### Best Practices
- [Docker Best Practices for Python](https://testdriven.io/blog/docker-best-practices/) - Comprehensive guide
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) - Official recommendations
- [NVIDIA NGC Catalog](https://catalog.ngc.nvidia.com/containers) - Pre-built ML containers

### Research
- "Reproducibility in Machine Learning for Health" (McDermott et al., 2019) - Why ML reproducibility matters
- "The State of Machine Learning Infrastructure" (Algorithmia, 2020) - Industry survey on ML deployment

---

## ✅ Key Takeaways

1. **Virtual environments aren't enough** - They isolate Python packages but not system libraries, CUDA, or OS differences. Containers isolate everything except the kernel.

2. **Images are blueprints, containers are instances** - One image can spawn many containers. Images are immutable; containers can diverge at runtime.

3. **Layer ordering matters for cache performance** - Put stable layers (OS, system deps) first, volatile layers (your code) last. A well-ordered Dockerfile builds in seconds for code changes.

4. **Multi-stage builds dramatically reduce image size** - Keep build tools in the builder stage, copy only runtime artifacts to production. Expect 40-70% size reduction.

5. **GPU containers need careful version matching** - CUDA toolkit in container, driver on host. Host driver version must be >= container CUDA version.

6. **Don't bake models into images** - Use volume mounts, download at runtime, or pull from model registries. Keeps images lean and deployments fast.

7. **Security defaults are important** - Run as non-root, use specific versions, minimize packages, scan for vulnerabilities. Don't inherit other people's security problems.

---

## ⏭️ Next Steps

You now understand Docker for ML! This foundation enables:
- **CI/CD pipelines** (Module 45) - Automate building and testing containers
- **Kubernetes deployments** (Modules 46-47) - Orchestrate containers at scale
- **MLOps experiment tracking** (Module 48) - Reproducible experiments in containers

**Up Next**: Module 45 - CI/CD for AI/ML Development

---

*Module 44 Complete! You now have the containerization skills to ship ML code that runs the same everywhere.*

*Remember the Mars Climate Orbiter: environment assumptions killed a $165 million spacecraft. Containers make environment assumptions explicit, versioned, and reproducible. That's not overhead—that's engineering.*

*"It works on my machine" → "It works in this container, which runs everywhere."*
