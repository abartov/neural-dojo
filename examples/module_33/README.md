# Module 33: Diffusion Models & Image Generation

This directory contains examples and a toolkit for understanding diffusion models.

## Contents

- `deliverable_diffusion_lab.py` - Interactive diffusion model toolkit
- `DELIVERABLE_README.md` - Detailed documentation for the deliverable

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python deliverable_diffusion_lab.py demo1  # Forward diffusion
python deliverable_diffusion_lab.py demo2  # Noise schedules
python deliverable_diffusion_lab.py demo3  # Train model
python deliverable_diffusion_lab.py demo4  # DDPM vs DDIM
python deliverable_diffusion_lab.py demo5  # Generate report
```

## Key Concepts

### How Diffusion Works

1. **Forward Process**: Gradually add noise until data becomes pure noise
2. **Reverse Process**: Train neural network to predict and remove noise
3. **Generation**: Start from noise, iteratively denoise to create new data

### The Core Equations

```
Forward:  x_t = √ᾱ_t · x_0 + √(1 - ᾱ_t) · ε
Loss:     L = ||ε - ε_θ(x_t, t)||²
```

### Stable Diffusion Architecture

```
Text → CLIP Encoder → Text Embeddings
                          ↓
Noise → U-Net (with cross-attention) → Denoised Latent → VAE Decoder → Image
```

## Theory

See `docs/curriculum/notes/module_33_diffusion_models.md` for complete theory.

## Requirements

- Python 3.10+
- numpy (required)
- torch (optional, for training demos)
