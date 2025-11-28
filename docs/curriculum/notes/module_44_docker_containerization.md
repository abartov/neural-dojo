# Module 44: Docker & Containerization for ML

**Last Updated**: 2025-11-28
**Status**: 🟢 Complete
**Duration**: 6-7 hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why containers are essential for ML reproducibility
- Master Docker fundamentals (images, containers, layers)
- Build optimized ML Docker images with multi-stage builds
- Handle large ML artifacts (models, data) in containers
- Configure GPU containers with NVIDIA Docker
- Create Docker Compose stacks for ML development
- Apply production best practices for containerized ML

---

## 📖 Why Containers for ML?

### The Reproducibility Crisis

Machine learning has a reproducibility problem. A model that works perfectly on your laptop fails mysteriously in production. Why?

```
THE "IT WORKS ON MY MACHINE" PROBLEM
=====================================

Developer's Machine          Production Server
------------------          -----------------
Python 3.10.4               Python 3.10.1
PyTorch 2.0.1               PyTorch 2.0.0
CUDA 11.8                   CUDA 11.7
cuDNN 8.6.0                 cuDNN 8.5.0
Ubuntu 22.04                Ubuntu 20.04
libc 2.35                   libc 2.31

Result: "RuntimeError: CUDA error: no kernel image is available"
```

**Did You Know?** A 2019 study attempted to reproduce 255 ML papers and found that only 14% could be reproduced with the original code. The main culprits? Missing dependencies, version mismatches, and undocumented environment requirements. Docker doesn't solve all reproducibility issues (random seeds, hardware differences), but it eliminates the environment variable.

### What Containers Solve

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTAINER BENEFITS FOR ML                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. REPRODUCIBILITY                                                 │
│     Same environment everywhere: dev, CI, staging, production       │
│     "If it runs in the container, it runs anywhere"                 │
│                                                                     │
│  2. DEPENDENCY ISOLATION                                            │
│     PyTorch 1.x and PyTorch 2.x can coexist on same machine        │
│     No more "pip install broke my other project"                    │
│                                                                     │
│  3. PORTABILITY                                                     │
│     Move from laptop → cloud → on-prem seamlessly                  │
│     Same Dockerfile works on AWS, GCP, Azure, bare metal            │
│                                                                     │
│  4. SCALABILITY                                                     │
│     Kubernetes orchestrates containers                              │
│     Scale from 1 to 1000 instances with same image                  │
│                                                                     │
│  5. VERSION CONTROL                                                 │
│     Tag images: model-v1.0, model-v1.1, model-v2.0                 │
│     Rollback instantly if deployment fails                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Containers vs Virtual Machines

```
VIRTUAL MACHINE                    CONTAINER
===============                    =========

┌─────────────────┐               ┌─────────────────┐
│   Application   │               │   Application   │
├─────────────────┤               ├─────────────────┤
│   Guest OS      │               │   Container     │
│   (Full Linux)  │               │   Runtime       │
├─────────────────┤               ├─────────────────┤
│   Hypervisor    │               │   Host OS       │
├─────────────────┤               │                 │
│   Host OS       │               │                 │
└─────────────────┘               └─────────────────┘

Size: 1-10+ GB                    Size: 100MB-2GB
Boot: 30-60 seconds               Boot: <1 second
Overhead: High (full OS)          Overhead: Minimal
Isolation: Strong                 Isolation: Process-level
```

**Did You Know?** Solomon Hykes created Docker in 2013 while working at dotCloud (a PaaS company). The key insight was combining Linux cgroups (resource isolation) with union filesystems (layered images) into a simple, developer-friendly tool. Docker didn't invent containers—Linux had LXC since 2008—but it made them accessible.

---

## 🐳 Docker Fundamentals

### Core Concepts

```
DOCKER ARCHITECTURE
===================

┌─────────────────────────────────────────────────────────────────┐
│                         DOCKER HOST                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │Container │    │Container │    │Container │                  │
│  │  (App 1) │    │  (App 2) │    │  (App 3) │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
│       │               │               │                         │
│       └───────────────┼───────────────┘                         │
│                       │                                         │
│              ┌────────┴────────┐                                │
│              │  Docker Engine  │                                │
│              └────────┬────────┘                                │
│                       │                                         │
│              ┌────────┴────────┐                                │
│              │    Host OS      │                                │
│              │  (Linux Kernel) │                                │
│              └─────────────────┘                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

IMAGE → Blueprint (read-only template)
CONTAINER → Running instance of an image
REGISTRY → Storage for images (Docker Hub, ECR, GCR)
VOLUME → Persistent storage outside container
NETWORK → Communication between containers
```

### Image Layers

Docker images are built in layers. Each instruction in a Dockerfile creates a new layer:

```
LAYER ARCHITECTURE
==================

┌─────────────────────────────────────────┐
│  Layer 5: COPY . /app                   │  ← Your code (changes often)
├─────────────────────────────────────────┤
│  Layer 4: RUN pip install -r req.txt    │  ← Dependencies
├─────────────────────────────────────────┤
│  Layer 3: COPY requirements.txt .       │  ← Requirements file
├─────────────────────────────────────────┤
│  Layer 2: RUN apt-get install python3   │  ← System packages
├─────────────────────────────────────────┤
│  Layer 1: FROM ubuntu:22.04             │  ← Base image
└─────────────────────────────────────────┘

CACHE BEHAVIOR:
- If a layer changes, all layers ABOVE it are rebuilt
- Order matters! Put rarely-changing layers first
- This is why we COPY requirements.txt before COPY . /app
```

**Did You Know?** Docker's layer caching can save enormous build times. A well-structured Dockerfile for an ML project might take 10 minutes to build from scratch but only 30 seconds for code changes (since the heavy PyTorch/TensorFlow layers are cached). This is why layer ordering is critical.

### Essential Docker Commands

```bash
# IMAGE COMMANDS
docker build -t myapp:v1 .           # Build image from Dockerfile
docker images                         # List local images
docker pull pytorch/pytorch:2.0.0     # Download image
docker push myrepo/myapp:v1           # Upload image to registry
docker rmi myapp:v1                   # Remove image

# CONTAINER COMMANDS
docker run myapp:v1                   # Create and start container
docker run -it myapp:v1 bash          # Interactive shell
docker run -d myapp:v1                # Detached (background)
docker run -p 8000:8000 myapp:v1      # Port mapping
docker run -v /data:/app/data myapp   # Volume mount
docker ps                             # List running containers
docker ps -a                          # List all containers
docker stop <container_id>            # Stop container
docker rm <container_id>              # Remove container
docker logs <container_id>            # View logs
docker exec -it <id> bash             # Shell into running container

# CLEANUP COMMANDS
docker system prune                   # Remove unused data
docker image prune                    # Remove dangling images
docker container prune                # Remove stopped containers
```

---

## 🔧 Writing Dockerfiles for ML

### Basic ML Dockerfile

```dockerfile
# Basic ML Dockerfile - NOT OPTIMIZED
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Default command
CMD ["python", "train.py"]
```

**Problems with this approach:**
1. Large image size (Python base + all code)
2. No layer caching optimization
3. Runs as root (security risk)
4. No GPU support
5. Development tools included in production

### Optimized ML Dockerfile

```dockerfile
# Optimized ML Dockerfile
# Stage 1: Build stage
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.10-slim AS production

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser models/ ./models/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "src.serve"]
```

### Multi-Stage Build Benefits

```
SINGLE-STAGE VS MULTI-STAGE
============================

Single-Stage:
┌─────────────────────────────────┐
│  Base Image     (100 MB)        │
│  Build Tools    (500 MB)        │  ← Not needed at runtime!
│  Dependencies   (2 GB)          │
│  Source Code    (10 MB)         │
├─────────────────────────────────┤
│  TOTAL: ~2.6 GB                 │
└─────────────────────────────────┘

Multi-Stage:
┌─────────────────────────────────┐
│  Slim Base      (50 MB)         │
│  Dependencies   (2 GB)          │  ← Only runtime deps
│  Source Code    (10 MB)         │
├─────────────────────────────────┤
│  TOTAL: ~2.06 GB                │  ← 20% smaller, more secure
└─────────────────────────────────┘

Build tools (gcc, make, etc.) stay in builder stage!
```

---

## 🎮 GPU Containers with NVIDIA Docker

### The GPU Challenge

GPUs require kernel-level drivers. How do containers access them?

```
GPU CONTAINER ARCHITECTURE
==========================

┌─────────────────────────────────────────────────────────────────┐
│                         CONTAINER                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Your ML Application                                      │   │
│  │  (PyTorch, TensorFlow, etc.)                             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  CUDA Toolkit (nvcc, cuBLAS, cuDNN)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ NVIDIA Container  │
                    │    Toolkit        │  ← Bridges container to GPU
                    └─────────┬─────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                         HOST                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  NVIDIA Driver                                            │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Linux Kernel                                             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  GPU Hardware (RTX 4090, A100, etc.)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

KEY INSIGHT: Driver on HOST, CUDA toolkit in CONTAINER
```

**Did You Know?** NVIDIA Container Toolkit (formerly nvidia-docker) was released in 2016. It uses a custom runtime hook that mounts the GPU device files and driver libraries into the container at launch time. This means you can have containers with different CUDA versions all using the same host driver.

### GPU Dockerfile

```dockerfile
# GPU-enabled ML Dockerfile
FROM nvidia/cuda:11.8-cudnn8-runtime-ubuntu22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-venv \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR /app

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir \
    torch==2.0.1+cu118 \
    torchvision==0.15.2+cu118 \
    --extra-index-url https://download.pytorch.org/whl/cu118

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY models/ ./models/

# Environment variables
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

CMD ["python", "-m", "src.train"]
```

### Running GPU Containers

```bash
# Run with GPU access (Docker 19.03+)
docker run --gpus all myapp:gpu

# Run with specific GPUs
docker run --gpus '"device=0,1"' myapp:gpu

# Run with GPU memory limit
docker run --gpus all --memory=16g myapp:gpu

# Check GPU inside container
docker run --gpus all nvidia/cuda:11.8-base nvidia-smi
```

### CUDA Version Compatibility

```
CUDA COMPATIBILITY MATRIX
=========================

Host Driver    | Supported CUDA Versions in Container
---------------|-------------------------------------
535.x          | CUDA 12.2 and earlier
525.x          | CUDA 12.0 and earlier
515.x          | CUDA 11.7 and earlier
470.x          | CUDA 11.4 and earlier

RULE: Host driver must be >= container CUDA version
      (Forward compatible, not backward)

Example:
- Host has Driver 525.85 (supports up to CUDA 12.0)
- Container with CUDA 11.8 ✅ Works
- Container with CUDA 12.1 ❌ Fails
```

---

## 📦 Handling Large ML Artifacts

### The Model Size Problem

ML models can be huge:
- BERT-base: 440 MB
- GPT-2: 1.5 GB
- Stable Diffusion: 4 GB
- LLaMA-7B: 13 GB
- LLaMA-70B: 140 GB

Baking these into Docker images is problematic:
1. Images become huge (slow to pull)
2. Every model update requires new image
3. Registry storage costs increase
4. Build times explode

### Strategy 1: Download at Runtime

```dockerfile
# Download model at container start
FROM python:3.10-slim

COPY download_model.py .
COPY src/ ./src/

# Don't include model in image
# Download when container starts
CMD ["sh", "-c", "python download_model.py && python -m src.serve"]
```

```python
# download_model.py
import os
from huggingface_hub import snapshot_download

MODEL_ID = os.environ.get("MODEL_ID", "bert-base-uncased")
CACHE_DIR = os.environ.get("MODEL_CACHE", "/models")

if not os.path.exists(f"{CACHE_DIR}/{MODEL_ID}"):
    print(f"Downloading {MODEL_ID}...")
    snapshot_download(MODEL_ID, cache_dir=CACHE_DIR)
else:
    print(f"Model {MODEL_ID} already cached")
```

### Strategy 2: Volume Mounts

```bash
# Mount model directory from host
docker run -v /host/models:/app/models myapp:v1

# Or use named volume (persists across container restarts)
docker volume create ml-models
docker run -v ml-models:/app/models myapp:v1
```

### Strategy 3: Model Registry

```dockerfile
# Pull from model registry at runtime
FROM python:3.10-slim

ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000
ENV MODEL_NAME=production-classifier
ENV MODEL_VERSION=3

COPY src/ ./src/

CMD ["python", "-m", "src.serve"]
```

```python
# src/serve.py
import mlflow
import os

model_uri = f"models:/{os.environ['MODEL_NAME']}/{os.environ['MODEL_VERSION']}"
model = mlflow.pyfunc.load_model(model_uri)
```

### Strategy 4: Separate Model Image

```dockerfile
# Base inference image (small, reusable)
FROM python:3.10-slim AS inference-base
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/

# Model-specific image (extends base)
FROM inference-base AS model-v1
COPY models/v1/ ./models/
ENV MODEL_PATH=/app/models

# Different model, same base
FROM inference-base AS model-v2
COPY models/v2/ ./models/
ENV MODEL_PATH=/app/models
```

---

## 🐙 Docker Compose for ML Development

### Why Docker Compose?

ML systems rarely run alone. A typical setup:

```
ML DEVELOPMENT STACK
====================

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Model   │  │   API    │  │  Vector  │  │  Redis   │       │
│  │ Training │  │  Server  │  │    DB    │  │  Cache   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │             │             │             │               │
│       └─────────────┴─────────────┴─────────────┘               │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │   Docker    │                              │
│                    │   Network   │                              │
│                    └─────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Basic docker-compose.yml

```yaml
# docker-compose.yml for ML development
version: '3.8'

services:
  # ML API Server
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src        # Hot reload for development
      - model-cache:/app/models
    environment:
      - MODEL_PATH=/app/models
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

  # Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant-data:/qdrant/storage

  # Cache Layer
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  # Experiment Tracking
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.0
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    command: mlflow server --host 0.0.0.0 --backend-store-uri sqlite:///mlflow/mlflow.db

  # Jupyter for Development
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
      - JUPYTER_TOKEN=dev-token
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  model-cache:
  qdrant-data:
  redis-data:
  mlflow-data:
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up api

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (careful!)
docker-compose down -v

# Scale service (if stateless)
docker-compose up --scale api=3
```

### Development vs Production Compose

```yaml
# docker-compose.yml (base)
version: '3.8'
services:
  api:
    build: .
    environment:
      - MODEL_PATH=/app/models

# docker-compose.override.yml (development - auto-loaded)
version: '3.8'
services:
  api:
    volumes:
      - ./src:/app/src          # Hot reload
    environment:
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    ports:
      - "8000:8000"

# docker-compose.prod.yml (production - explicit)
version: '3.8'
services:
  api:
    image: myregistry/api:v1.0.0  # Use pre-built image
    environment:
      - LOG_LEVEL=WARNING
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
```

```bash
# Development (uses override automatically)
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## 🏭 Production Best Practices

### Security Hardening

```dockerfile
# Security-hardened Dockerfile
FROM python:3.10-slim

# 1. Don't run as root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 2. Remove unnecessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# 3. Set restrictive permissions
WORKDIR /app
RUN chown -R appuser:appgroup /app

# 4. Copy only what's needed
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup src/ ./src/

# 5. Switch to non-root user
USER appuser

# 6. Use specific versions, not 'latest'
# 7. Scan for vulnerabilities: docker scan myimage

# 8. Read-only filesystem (enable in run command)
# docker run --read-only myimage

CMD ["python", "-m", "src.serve"]
```

### Image Size Optimization

```
SIZE REDUCTION TECHNIQUES
=========================

1. Use slim/alpine base images
   python:3.10      → 1 GB
   python:3.10-slim → 150 MB
   python:3.10-alpine → 50 MB (may have compatibility issues)

2. Multi-stage builds
   Keep build tools out of final image

3. Minimize layers
   Combine RUN commands with &&

4. Clean up in same layer
   RUN apt-get update && apt-get install -y pkg \
       && rm -rf /var/lib/apt/lists/*

5. Use .dockerignore
   Exclude: .git, __pycache__, *.pyc, .env, tests/, docs/

6. Don't install dev dependencies in production
   pip install --no-dev or poetry install --no-dev
```

### .dockerignore Example

```
# .dockerignore for ML projects
.git
.gitignore
.env
.env.*
*.md
docs/
tests/
notebooks/
*.ipynb
__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
data/raw/
data/interim/
*.h5
*.pkl
*.joblib
wandb/
mlruns/
.vscode/
.idea/
Dockerfile*
docker-compose*
Makefile
```

### Health Checks

```dockerfile
# Health check in Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

```python
# Health endpoint in FastAPI
from fastapi import FastAPI
import torch

app = FastAPI()

@app.get("/health")
async def health():
    """Health check endpoint."""
    checks = {
        "status": "healthy",
        "model_loaded": model is not None,
        "gpu_available": torch.cuda.is_available(),
    }
    if not all([checks["model_loaded"]]):
        return {"status": "unhealthy", **checks}, 503
    return checks

@app.get("/ready")
async def ready():
    """Readiness check - is the service ready to accept traffic?"""
    if model is None:
        return {"ready": False}, 503
    return {"ready": True}
```

---

## 📊 Common ML Docker Patterns

### Pattern 1: Training Container

```dockerfile
# Training container with experiment tracking
FROM nvidia/cuda:11.8-cudnn8-runtime-ubuntu22.04

# ... Python setup ...

# Mount points for data and output
VOLUME ["/data", "/output", "/checkpoints"]

# Environment for experiment tracking
ENV WANDB_API_KEY=""
ENV MLFLOW_TRACKING_URI=""

COPY train.py .
COPY src/ ./src/

ENTRYPOINT ["python", "train.py"]
# Arguments passed at runtime: docker run myapp:train --epochs 100 --lr 0.001
```

### Pattern 2: Inference Server

```dockerfile
# FastAPI inference server
FROM python:3.10-slim

# ... setup ...

COPY src/ ./src/
COPY models/ ./models/

EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
```

### Pattern 3: Batch Processing

```dockerfile
# Batch inference container
FROM python:3.10-slim

COPY src/ ./src/
COPY models/ ./models/

# No exposed ports - runs to completion
ENTRYPOINT ["python", "-m", "src.batch_predict"]
# docker run -v /data/input:/input -v /data/output:/output myapp:batch
```

### Pattern 4: Development Environment

```dockerfile
# Development container with all tools
FROM nvidia/cuda:11.8-cudnn8-devel-ubuntu22.04

# Install development tools
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip \
    git vim curl wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dev tools
RUN pip install \
    ipython \
    jupyter \
    pytest \
    black \
    ruff \
    mypy

# Install ML libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /workspace
VOLUME ["/workspace"]

# Jupyter by default
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
```

---

## 🔍 Debugging Docker Containers

### Common Issues

```
ISSUE: "ModuleNotFoundError: No module named 'xyz'"
CAUSE: Dependencies not installed or wrong Python path
FIX: Check requirements.txt, verify PYTHONPATH

ISSUE: "CUDA out of memory"
CAUSE: GPU memory limit exceeded
FIX: Reduce batch size, use gradient checkpointing, or --shm-size

ISSUE: Container exits immediately
CAUSE: CMD completes or crashes
FIX: Check logs (docker logs <id>), run interactively

ISSUE: "Permission denied"
CAUSE: Running as non-root, file ownership issues
FIX: Check USER directive, use --chown in COPY

ISSUE: Build cache not working
CAUSE: Layer order changed or COPY invalidates cache
FIX: Order layers by change frequency, use .dockerignore
```

### Debugging Commands

```bash
# Run shell in existing image
docker run -it myapp:v1 bash

# Shell into running container
docker exec -it <container_id> bash

# View container logs
docker logs <container_id>
docker logs -f <container_id>  # Follow

# Inspect container details
docker inspect <container_id>

# Check resource usage
docker stats <container_id>

# Copy files from container
docker cp <container_id>:/app/logs ./logs

# Build with verbose output
docker build --progress=plain -t myapp:v1 .
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Basic ML Dockerfile

Create a Dockerfile for a simple ML inference service:
- Use Python 3.10 slim base
- Install scikit-learn
- Copy a trained model
- Expose port 8000
- Run a FastAPI server

### Exercise 2: Multi-Stage Build

Convert your Dockerfile to multi-stage:
- Builder stage with build tools
- Production stage with only runtime
- Compare image sizes

### Exercise 3: GPU Container

Create a GPU-enabled training container:
- Use NVIDIA CUDA base image
- Install PyTorch with CUDA
- Mount volumes for data and checkpoints
- Run with --gpus all

### Exercise 4: Docker Compose Stack

Create a docker-compose.yml with:
- ML API service
- Redis for caching
- Qdrant for vector search
- Shared network and volumes

---

## 📚 Further Reading

### Official Documentation
- [Docker Documentation](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)

### Best Practices
- [Docker Best Practices for Python](https://testdriven.io/blog/docker-best-practices/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [NVIDIA Deep Learning Containers](https://catalog.ngc.nvidia.com/containers)

### ML-Specific
- [ML Containers with Docker](https://neptune.ai/blog/how-to-build-and-manage-docker-containers-for-machine-learning)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)

---

## ✅ Knowledge Check

1. **Why are containers important for ML reproducibility?**

2. **What's the difference between an image and a container?**

3. **Why should you use multi-stage builds for ML?**

4. **How do GPU containers access the host GPU?**

5. **What are three strategies for handling large model files?**

6. **Why is layer ordering important in Dockerfiles?**

---

## ⏭️ Next Steps

You now understand Docker for ML! This is foundational for:
- CI/CD pipelines (Module 45)
- Kubernetes deployments (Module 46)
- Model serving at scale (Module 48)

**Up Next**: Module 45 - CI/CD for AI/ML Development

---

_Module 44 Complete! You now understand containerization for ML!_
_"The best code is code that runs the same everywhere."_
