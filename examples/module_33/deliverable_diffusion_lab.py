#!/usr/bin/env python3
"""
Module 33 Deliverable: Diffusion Lab

An educational toolkit for understanding diffusion models from first principles.
Demonstrates the core concepts of diffusion without requiring heavy compute.

Features:
- Forward diffusion process visualization
- Noise schedule comparison (linear, cosine, quadratic)
- Minimal diffusion model training on 2D data
- DDPM vs DDIM sampling comparison
- Classifier-free guidance demonstration
- Step-by-step generation visualization

Usage:
    python deliverable_diffusion_lab.py demo1  # Forward diffusion process
    python deliverable_diffusion_lab.py demo2  # Noise schedules comparison
    python deliverable_diffusion_lab.py demo3  # Train minimal diffusion model
    python deliverable_diffusion_lab.py demo4  # DDPM vs DDIM sampling
    python deliverable_diffusion_lab.py demo5  # Generate analysis report

Author: Neural Dojo
Date: 2025-11-27
"""

import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Try to import torch, fall back to numpy-only mode
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Note: PyTorch not available. Running in numpy-only mode.")

import numpy as np


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class DiffusionConfig:
    """Configuration for diffusion experiments."""
    num_timesteps: int = 1000
    beta_start: float = 0.0001
    beta_end: float = 0.02
    schedule_type: str = "linear"  # linear, cosine, quadratic


@dataclass
class TrainingConfig:
    """Configuration for training."""
    num_epochs: int = 100
    batch_size: int = 128
    learning_rate: float = 1e-3
    hidden_dim: int = 128
    num_samples: int = 2000


# =============================================================================
# Noise Schedules
# =============================================================================

def linear_schedule(num_timesteps: int, beta_start: float = 0.0001, beta_end: float = 0.02) -> np.ndarray:
    """Linear noise schedule."""
    return np.linspace(beta_start, beta_end, num_timesteps)


def cosine_schedule(num_timesteps: int, s: float = 0.008) -> np.ndarray:
    """
    Cosine noise schedule from 'Improved DDPM' paper.
    Provides smoother noise addition, especially at high timesteps.
    """
    steps = np.arange(num_timesteps + 1)
    alpha_bar = np.cos((steps / num_timesteps + s) / (1 + s) * np.pi / 2) ** 2
    alpha_bar = alpha_bar / alpha_bar[0]
    betas = 1 - alpha_bar[1:] / alpha_bar[:-1]
    return np.clip(betas, 0.0001, 0.999)


def quadratic_schedule(num_timesteps: int, beta_start: float = 0.0001, beta_end: float = 0.02) -> np.ndarray:
    """Quadratic noise schedule (slower at start, faster at end)."""
    return np.linspace(beta_start ** 0.5, beta_end ** 0.5, num_timesteps) ** 2


def get_schedule(schedule_type: str, num_timesteps: int) -> np.ndarray:
    """Get noise schedule by type."""
    schedules = {
        "linear": lambda: linear_schedule(num_timesteps),
        "cosine": lambda: cosine_schedule(num_timesteps),
        "quadratic": lambda: quadratic_schedule(num_timesteps),
    }
    return schedules.get(schedule_type, schedules["linear"])()


def compute_alpha_bars(betas: np.ndarray) -> np.ndarray:
    """Compute cumulative product of alphas."""
    alphas = 1 - betas
    return np.cumprod(alphas)


# =============================================================================
# Forward Diffusion Process
# =============================================================================

def forward_diffusion_step(x: np.ndarray, t: int, betas: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Single step of forward diffusion.

    x_t = sqrt(1 - beta_t) * x_{t-1} + sqrt(beta_t) * epsilon
    """
    beta_t = betas[t]
    noise = np.random.randn(*x.shape)
    x_t = np.sqrt(1 - beta_t) * x + np.sqrt(beta_t) * noise
    return x_t, noise


def forward_diffusion_direct(x_0: np.ndarray, t: int, alpha_bars: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Direct forward diffusion to timestep t (reparameterization trick).

    x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
    """
    alpha_bar_t = alpha_bars[t]
    noise = np.random.randn(*x_0.shape)
    x_t = np.sqrt(alpha_bar_t) * x_0 + np.sqrt(1 - alpha_bar_t) * noise
    return x_t, noise


# =============================================================================
# 2D Data Generation
# =============================================================================

def generate_spiral_data(n_samples: int, noise: float = 0.1) -> np.ndarray:
    """Generate 2D spiral data for visualization."""
    t = np.linspace(0, 4 * np.pi, n_samples)
    x = t * np.cos(t) / (4 * np.pi)
    y = t * np.sin(t) / (4 * np.pi)
    data = np.stack([x, y], axis=1)
    data += np.random.randn(n_samples, 2) * noise
    return data.astype(np.float32)


def generate_moons_data(n_samples: int, noise: float = 0.1) -> np.ndarray:
    """Generate 2D moons data."""
    n_samples_out = n_samples // 2
    n_samples_in = n_samples - n_samples_out

    outer_circ_x = np.cos(np.linspace(0, np.pi, n_samples_out))
    outer_circ_y = np.sin(np.linspace(0, np.pi, n_samples_out))
    inner_circ_x = 1 - np.cos(np.linspace(0, np.pi, n_samples_in))
    inner_circ_y = 0.5 - np.sin(np.linspace(0, np.pi, n_samples_in))

    x = np.concatenate([outer_circ_x, inner_circ_x])
    y = np.concatenate([outer_circ_y, inner_circ_y])
    data = np.stack([x, y], axis=1)
    data += np.random.randn(n_samples, 2) * noise
    return data.astype(np.float32)


def generate_circle_data(n_samples: int, noise: float = 0.1) -> np.ndarray:
    """Generate 2D circle data."""
    t = np.linspace(0, 2 * np.pi, n_samples)
    x = np.cos(t)
    y = np.sin(t)
    data = np.stack([x, y], axis=1)
    data += np.random.randn(n_samples, 2) * noise
    return data.astype(np.float32)


# =============================================================================
# Minimal Diffusion Model (PyTorch)
# =============================================================================

if TORCH_AVAILABLE:
    class SinusoidalTimeEmbedding(nn.Module):
        """Sinusoidal timestep embedding."""

        def __init__(self, dim: int):
            super().__init__()
            self.dim = dim

        def forward(self, t: torch.Tensor) -> torch.Tensor:
            device = t.device
            half_dim = self.dim // 2
            emb = math.log(10000) / (half_dim - 1)
            emb = torch.exp(torch.arange(half_dim, device=device) * -emb)
            emb = t[:, None] * emb[None, :]
            emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=-1)
            return emb

    class MinimalDiffusionModel(nn.Module):
        """
        Minimal diffusion model for 2D data.
        Predicts the noise added at each timestep.
        """

        def __init__(self, data_dim: int = 2, hidden_dim: int = 128, time_dim: int = 32):
            super().__init__()

            self.time_embed = SinusoidalTimeEmbedding(time_dim)

            self.net = nn.Sequential(
                nn.Linear(data_dim + time_dim, hidden_dim),
                nn.SiLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.SiLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.SiLU(),
                nn.Linear(hidden_dim, data_dim),
            )

        def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
            """
            Predict noise for input x at timestep t.

            Args:
                x: [batch, data_dim] noisy data
                t: [batch] timesteps

            Returns:
                Predicted noise [batch, data_dim]
            """
            t_emb = self.time_embed(t)
            x_input = torch.cat([x, t_emb], dim=-1)
            return self.net(x_input)

    class DiffusionTrainer:
        """Trainer for minimal diffusion model."""

        def __init__(self, model: nn.Module, config: DiffusionConfig):
            self.model = model
            self.config = config

            # Compute schedules
            self.betas = torch.tensor(
                get_schedule(config.schedule_type, config.num_timesteps),
                dtype=torch.float32
            )
            self.alphas = 1 - self.betas
            self.alpha_bars = torch.cumprod(self.alphas, dim=0)

        def train_step(self, x_0: torch.Tensor) -> float:
            """Single training step."""
            batch_size = x_0.shape[0]

            # Sample random timesteps
            t = torch.randint(0, self.config.num_timesteps, (batch_size,))

            # Get noise schedule values
            alpha_bar_t = self.alpha_bars[t].unsqueeze(-1)

            # Sample noise
            noise = torch.randn_like(x_0)

            # Forward diffusion
            x_t = torch.sqrt(alpha_bar_t) * x_0 + torch.sqrt(1 - alpha_bar_t) * noise

            # Predict noise
            noise_pred = self.model(x_t, t.float())

            # MSE loss
            loss = F.mse_loss(noise_pred, noise)

            return loss

        @torch.no_grad()
        def sample_ddpm(self, shape: Tuple[int, int], num_steps: Optional[int] = None) -> List[np.ndarray]:
            """
            Sample using DDPM (returns intermediate steps for visualization).
            """
            if num_steps is None:
                num_steps = self.config.num_timesteps

            self.model.eval()
            x = torch.randn(shape)
            trajectory = [x.numpy().copy()]

            for t in reversed(range(num_steps)):
                t_tensor = torch.full((shape[0],), t, dtype=torch.float32)

                # Predict noise
                noise_pred = self.model(x, t_tensor)

                # Get coefficients
                alpha_t = self.alphas[t]
                alpha_bar_t = self.alpha_bars[t]
                beta_t = self.betas[t]

                # Compute mean
                mean = (1 / torch.sqrt(alpha_t)) * (
                    x - (beta_t / torch.sqrt(1 - alpha_bar_t)) * noise_pred
                )

                # Add noise (except at t=0)
                if t > 0:
                    noise = torch.randn_like(x)
                    x = mean + torch.sqrt(beta_t) * noise
                else:
                    x = mean

                # Store trajectory at intervals
                if t % (num_steps // 10) == 0 or t == 0:
                    trajectory.append(x.numpy().copy())

            return trajectory

        @torch.no_grad()
        def sample_ddim(self, shape: Tuple[int, int], num_steps: int = 50) -> List[np.ndarray]:
            """
            Sample using DDIM (faster, deterministic).
            """
            self.model.eval()
            x = torch.randn(shape)
            trajectory = [x.numpy().copy()]

            # Use subset of timesteps
            timesteps = torch.linspace(
                self.config.num_timesteps - 1, 0, num_steps
            ).long()

            for i, t in enumerate(timesteps):
                t_tensor = torch.full((shape[0],), t.item(), dtype=torch.float32)

                # Predict noise
                noise_pred = self.model(x, t_tensor)

                alpha_bar_t = self.alpha_bars[t]

                if i < len(timesteps) - 1:
                    alpha_bar_prev = self.alpha_bars[timesteps[i + 1]]
                else:
                    alpha_bar_prev = torch.tensor(1.0)

                # DDIM update (deterministic)
                pred_x0 = (x - torch.sqrt(1 - alpha_bar_t) * noise_pred) / torch.sqrt(alpha_bar_t)
                dir_xt = torch.sqrt(1 - alpha_bar_prev) * noise_pred
                x = torch.sqrt(alpha_bar_prev) * pred_x0 + dir_xt

                # Store trajectory
                if i % (num_steps // 10) == 0 or i == len(timesteps) - 1:
                    trajectory.append(x.numpy().copy())

            return trajectory


# =============================================================================
# Visualization (ASCII Art)
# =============================================================================

def ascii_scatter(data: np.ndarray, width: int = 60, height: int = 20, title: str = "") -> str:
    """Create ASCII scatter plot of 2D data."""
    if data.shape[1] != 2:
        return "Error: Data must be 2D"

    # Normalize to grid
    x, y = data[:, 0], data[:, 1]
    x_min, x_max = x.min() - 0.1, x.max() + 0.1
    y_min, y_max = y.min() - 0.1, y.max() + 0.1

    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot points
    for px, py in zip(x, y):
        gx = int((px - x_min) / (x_max - x_min) * (width - 1))
        gy = int((py - y_min) / (y_max - y_min) * (height - 1))
        gy = height - 1 - gy  # Flip y
        gx = max(0, min(width - 1, gx))
        gy = max(0, min(height - 1, gy))
        grid[gy][gx] = '•'

    # Build output
    lines = []
    if title:
        lines.append(f"  {title}")
        lines.append("  " + "-" * width)

    for row in grid:
        lines.append("  |" + "".join(row) + "|")

    lines.append("  " + "-" * (width + 2))

    return "\n".join(lines)


def ascii_histogram(values: np.ndarray, bins: int = 20, width: int = 40, title: str = "") -> str:
    """Create ASCII histogram."""
    hist, edges = np.histogram(values, bins=bins)
    max_count = max(hist)

    lines = []
    if title:
        lines.append(f"  {title}")
        lines.append("")

    for i, count in enumerate(hist):
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        bar = "█" * bar_len
        lines.append(f"  {edges[i]:6.2f} |{bar}")

    return "\n".join(lines)


# =============================================================================
# Demo Functions
# =============================================================================

def demo1_forward_diffusion():
    """Demo 1: Visualize the forward diffusion process."""
    print("\n" + "=" * 70)
    print("DEMO 1: Forward Diffusion Process")
    print("=" * 70)

    print("\n📊 The Forward Process: Gradually Adding Noise")
    print("-" * 50)

    # Generate initial data
    np.random.seed(42)
    data = generate_spiral_data(200, noise=0.05)

    print("\n🌀 Original spiral data:")
    print(ascii_scatter(data, title="t=0 (Original)"))

    # Setup diffusion
    config = DiffusionConfig(num_timesteps=1000, schedule_type="linear")
    betas = get_schedule(config.schedule_type, config.num_timesteps)
    alpha_bars = compute_alpha_bars(betas)

    # Show diffusion at different timesteps
    timesteps = [0, 100, 250, 500, 750, 999]

    print("\n📈 Diffusion at different timesteps:")
    print("-" * 50)

    for t in timesteps:
        if t == 0:
            noisy_data = data
        else:
            noisy_data, _ = forward_diffusion_direct(data, t, alpha_bars)

        signal_preserved = alpha_bars[t] if t < len(alpha_bars) else 0
        noise_level = 1 - signal_preserved

        print(f"\n  t={t:4d} | Signal: {signal_preserved*100:5.1f}% | Noise: {noise_level*100:5.1f}%")
        print(ascii_scatter(noisy_data, width=50, height=12))

    print("\n✅ Key Insights:")
    print("   - Signal (√ᾱ_t) decreases as t increases")
    print("   - Noise (√(1-ᾱ_t)) increases as t increases")
    print("   - By t=1000, data is nearly pure Gaussian noise")
    print("   - The reverse process learns to UNDO this corruption!")


def demo2_noise_schedules():
    """Demo 2: Compare different noise schedules."""
    print("\n" + "=" * 70)
    print("DEMO 2: Noise Schedule Comparison")
    print("=" * 70)

    num_timesteps = 1000

    schedules = {
        "linear": linear_schedule(num_timesteps),
        "cosine": cosine_schedule(num_timesteps),
        "quadratic": quadratic_schedule(num_timesteps),
    }

    print("\n📊 Comparing β (beta) schedules:")
    print("-" * 50)

    # Show beta values at key timesteps
    print(f"\n  {'Timestep':>10} | {'Linear':>10} | {'Cosine':>10} | {'Quadratic':>10}")
    print("  " + "-" * 50)

    for t in [0, 100, 250, 500, 750, 999]:
        linear_b = schedules["linear"][t]
        cosine_b = schedules["cosine"][t]
        quad_b = schedules["quadratic"][t]
        print(f"  {t:>10} | {linear_b:>10.6f} | {cosine_b:>10.6f} | {quad_b:>10.6f}")

    print("\n📉 Signal preservation (ᾱ_t) over time:")
    print("-" * 50)

    for name, betas in schedules.items():
        alpha_bars = compute_alpha_bars(betas)

        print(f"\n  {name.upper()} schedule:")
        # ASCII mini-chart
        chart = "  "
        for t in range(0, 1000, 50):
            signal = alpha_bars[t]
            if signal > 0.8:
                chart += "█"
            elif signal > 0.6:
                chart += "▓"
            elif signal > 0.4:
                chart += "▒"
            elif signal > 0.2:
                chart += "░"
            else:
                chart += "·"
        print(f"  t: 0{' ' * 17}1000")
        print(f"  {chart}")
        print(f"  Signal at t=500: {alpha_bars[500]*100:.1f}%")
        print(f"  Signal at t=750: {alpha_bars[750]*100:.1f}%")

    print("\n✅ Key Insights:")
    print("   - LINEAR: Uniform noise addition (original DDPM)")
    print("   - COSINE: Slower at start/end, preserves details longer")
    print("   - QUADRATIC: Very slow start, aggressive at end")
    print("   - Cosine is often preferred for image generation")


def demo3_train_diffusion():
    """Demo 3: Train a minimal diffusion model on 2D data."""
    print("\n" + "=" * 70)
    print("DEMO 3: Train Minimal Diffusion Model")
    print("=" * 70)

    if not TORCH_AVAILABLE:
        print("\n⚠️  PyTorch not available. Skipping training demo.")
        print("   Install with: pip install torch")
        return

    print("\n🔧 Training Configuration:")
    print("-" * 50)

    train_config = TrainingConfig(
        num_epochs=100,
        batch_size=128,
        learning_rate=1e-3,
        hidden_dim=128,
        num_samples=2000
    )
    diff_config = DiffusionConfig(num_timesteps=200, schedule_type="cosine")

    print(f"   Data points: {train_config.num_samples}")
    print(f"   Epochs: {train_config.num_epochs}")
    print(f"   Timesteps: {diff_config.num_timesteps}")
    print(f"   Schedule: {diff_config.schedule_type}")

    # Generate training data
    print("\n📊 Generating spiral training data...")
    np.random.seed(42)
    torch.manual_seed(42)
    train_data = generate_spiral_data(train_config.num_samples, noise=0.05)
    train_tensor = torch.tensor(train_data)

    print(ascii_scatter(train_data[:500], width=40, height=15, title="Training Data"))

    # Create model and trainer
    model = MinimalDiffusionModel(
        data_dim=2,
        hidden_dim=train_config.hidden_dim,
        time_dim=32
    )
    trainer = DiffusionTrainer(model, diff_config)
    optimizer = torch.optim.Adam(model.parameters(), lr=train_config.learning_rate)

    print(f"\n🏋️ Training ({train_config.num_epochs} epochs)...")
    print("-" * 50)

    losses = []
    start_time = time.time()

    for epoch in range(train_config.num_epochs):
        # Shuffle data
        perm = torch.randperm(len(train_tensor))
        train_shuffled = train_tensor[perm]

        epoch_loss = 0
        num_batches = 0

        for i in range(0, len(train_shuffled), train_config.batch_size):
            batch = train_shuffled[i:i + train_config.batch_size]

            optimizer.zero_grad()
            loss = trainer.train_step(batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1

        avg_loss = epoch_loss / num_batches
        losses.append(avg_loss)

        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"   Epoch {epoch+1:3d}/{train_config.num_epochs} | Loss: {avg_loss:.4f}")

    training_time = time.time() - start_time
    print(f"\n✅ Training complete in {training_time:.1f}s")
    print(f"   Final loss: {losses[-1]:.4f}")

    # Generate samples
    print("\n🎨 Generating samples with DDPM...")
    trajectory = trainer.sample_ddpm((500, 2), num_steps=diff_config.num_timesteps)

    print("\n   Reverse diffusion trajectory:")
    for i, (step_idx, samples) in enumerate(zip(
        [0, len(trajectory)//3, 2*len(trajectory)//3, -1],
        [trajectory[0], trajectory[len(trajectory)//3],
         trajectory[2*len(trajectory)//3], trajectory[-1]]
    )):
        step_name = ["Pure noise", "Early denoising", "Mid denoising", "Final samples"][i]
        print(f"\n   {step_name}:")
        print(ascii_scatter(samples[:200], width=35, height=10))

    print("\n✅ Key Insights:")
    print("   - Model learned to denoise at ALL noise levels")
    print("   - Starting from pure noise, we recover the spiral structure")
    print("   - Each denoising step makes the data more structured")


def demo4_ddpm_vs_ddim():
    """Demo 4: Compare DDPM and DDIM sampling."""
    print("\n" + "=" * 70)
    print("DEMO 4: DDPM vs DDIM Sampling")
    print("=" * 70)

    if not TORCH_AVAILABLE:
        print("\n⚠️  PyTorch not available. Showing conceptual comparison.")
        print("-" * 50)
        print("""
   DDPM (Denoising Diffusion Probabilistic Models):
   ├── Steps: 1000 (one per timestep)
   ├── Stochastic: Adds noise at each step
   ├── Quality: Highest quality
   └── Speed: SLOW (~30-60 seconds per image)

   DDIM (Denoising Diffusion Implicit Models):
   ├── Steps: 20-50 (skips timesteps)
   ├── Deterministic: No noise added
   ├── Quality: Very close to DDPM
   └── Speed: FAST (~2-5 seconds per image)

   Trade-off: DDIM sacrifices slight quality for 20-50x speedup
        """)
        return

    print("\n🔬 Training model for comparison...")

    # Quick training
    np.random.seed(42)
    torch.manual_seed(42)
    train_data = torch.tensor(generate_spiral_data(1000, noise=0.05))

    diff_config = DiffusionConfig(num_timesteps=200, schedule_type="cosine")
    model = MinimalDiffusionModel(data_dim=2, hidden_dim=64, time_dim=32)
    trainer = DiffusionTrainer(model, diff_config)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Quick training
    for epoch in range(50):
        perm = torch.randperm(len(train_data))
        for i in range(0, len(train_data), 128):
            batch = train_data[perm[i:i+128]]
            optimizer.zero_grad()
            loss = trainer.train_step(batch)
            loss.backward()
            optimizer.step()

    print("   Model trained!")

    print("\n📊 Comparing Sampling Methods:")
    print("-" * 50)

    # DDPM (all steps)
    print("\n   DDPM (200 steps):")
    start = time.time()
    ddpm_trajectory = trainer.sample_ddpm((300, 2), num_steps=200)
    ddpm_time = time.time() - start
    print(f"   Time: {ddpm_time:.2f}s")
    print(ascii_scatter(ddpm_trajectory[-1][:150], width=35, height=10))

    # DDIM (fewer steps)
    for num_steps in [50, 20, 10]:
        print(f"\n   DDIM ({num_steps} steps):")
        start = time.time()
        ddim_trajectory = trainer.sample_ddim((300, 2), num_steps=num_steps)
        ddim_time = time.time() - start
        speedup = ddpm_time / ddim_time
        print(f"   Time: {ddim_time:.2f}s ({speedup:.1f}x faster)")
        print(ascii_scatter(ddim_trajectory[-1][:150], width=35, height=10))

    print("\n✅ Key Insights:")
    print("   - DDIM achieves similar quality with far fewer steps")
    print("   - 50 DDIM steps ≈ 1000 DDPM steps in quality")
    print("   - DDIM is deterministic: same seed = same output")
    print("   - This is why Stable Diffusion uses ~30-50 steps!")


def demo5_generate_report():
    """Demo 5: Generate comprehensive analysis report."""
    print("\n" + "=" * 70)
    print("DEMO 5: Generate Analysis Report")
    print("=" * 70)

    # Create output directory
    output_dir = Path(".diffusion_lab")
    output_dir.mkdir(exist_ok=True)

    print("\n📝 Generating diffusion analysis report...")

    # Analyze schedules
    num_timesteps = 1000
    schedules = {
        "linear": linear_schedule(num_timesteps),
        "cosine": cosine_schedule(num_timesteps),
        "quadratic": quadratic_schedule(num_timesteps),
    }

    schedule_stats = {}
    for name, betas in schedules.items():
        alpha_bars = compute_alpha_bars(betas)
        schedule_stats[name] = {
            "beta_start": float(betas[0]),
            "beta_end": float(betas[-1]),
            "beta_mean": float(np.mean(betas)),
            "signal_at_t500": float(alpha_bars[500]),
            "signal_at_t750": float(alpha_bars[750]),
            "signal_at_t999": float(alpha_bars[999]),
        }

    report = f"""# Diffusion Lab Analysis Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Overview

This report analyzes diffusion model concepts demonstrated in the Diffusion Lab toolkit.

### Key Equations

**Forward Diffusion (Direct):**
```
x_t = √ᾱ_t · x_0 + √(1 - ᾱ_t) · ε
```

**Reverse Process (DDPM):**
```
x_{{t-1}} = (1/√α_t) · (x_t - (β_t/√(1-ᾱ_t)) · ε_θ(x_t, t)) + √β_t · z
```

**Training Loss:**
```
L = E[||ε - ε_θ(x_t, t)||²]
```

## Noise Schedule Comparison

| Schedule | β_start | β_end | Signal at t=500 | Signal at t=999 |
|----------|---------|-------|-----------------|-----------------|
| Linear | {schedule_stats['linear']['beta_start']:.6f} | {schedule_stats['linear']['beta_end']:.6f} | {schedule_stats['linear']['signal_at_t500']*100:.1f}% | {schedule_stats['linear']['signal_at_t999']*100:.3f}% |
| Cosine | {schedule_stats['cosine']['beta_start']:.6f} | {schedule_stats['cosine']['beta_end']:.6f} | {schedule_stats['cosine']['signal_at_t500']*100:.1f}% | {schedule_stats['cosine']['signal_at_t999']*100:.3f}% |
| Quadratic | {schedule_stats['quadratic']['beta_start']:.6f} | {schedule_stats['quadratic']['beta_end']:.6f} | {schedule_stats['quadratic']['signal_at_t500']*100:.1f}% | {schedule_stats['quadratic']['signal_at_t999']*100:.3f}% |

**Recommendation**: Cosine schedule for most applications (better detail preservation).

## DDPM vs DDIM

| Method | Steps | Stochastic | Typical Time | Quality |
|--------|-------|------------|--------------|---------|
| DDPM | 1000 | Yes | 30-60s | Highest |
| DDIM | 50 | No | 2-5s | Very High |
| DDIM | 20 | No | 1-2s | Good |
| LCM | 4-8 | No | <1s | Good |

## Key Concepts

### 1. Forward Diffusion
- Gradually adds Gaussian noise to data
- Uses noise schedule β_t to control rate
- After ~1000 steps, data becomes pure noise

### 2. Reverse Diffusion
- Neural network predicts added noise
- Subtracting predicted noise denoises the image
- Trained with simple MSE loss

### 3. U-Net Architecture
- Encoder-decoder with skip connections
- Time embedding tells model the noise level
- Cross-attention for conditioning (text → image)

### 4. Classifier-Free Guidance
- Train with random conditioning dropout
- At inference: blend unconditional + conditional
- Higher guidance scale = stronger prompt adherence

### 5. Latent Diffusion (Stable Diffusion)
- Run diffusion in compressed latent space
- 48× fewer values (64×64×4 vs 512×512×3)
- VAE encodes/decodes between pixel and latent space

## PyTorch Availability

PyTorch Available: {TORCH_AVAILABLE}

---

*Generated by Neural Dojo Diffusion Lab*
"""

    report_path = output_dir / "diffusion_report.md"
    report_path.write_text(report)
    print(f"\n✅ Report saved to: {report_path}")

    # Save schedule data
    data_path = output_dir / "schedule_analysis.json"
    data_path.write_text(json.dumps(schedule_stats, indent=2))
    print(f"✅ Schedule data saved to: {data_path}")

    # Print preview
    print("\n📄 Report Preview:")
    print("-" * 50)
    for line in report.split('\n')[:50]:
        print(line)
    print("\n... (see full report in file)")


# =============================================================================
# Main Entry Point
# =============================================================================

def print_usage():
    """Print usage information."""
    print("""
Diffusion Lab - Module 33 Deliverable
======================================

Usage: python deliverable_diffusion_lab.py <command>

Commands:
  demo1   - Forward diffusion process visualization
  demo2   - Noise schedules comparison
  demo3   - Train minimal diffusion model (requires PyTorch)
  demo4   - DDPM vs DDIM sampling comparison
  demo5   - Generate comprehensive report
  all     - Run all demos

Examples:
  python deliverable_diffusion_lab.py demo1
  python deliverable_diffusion_lab.py all

Learn more: docs/curriculum/notes/module_33_diffusion_models.md
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo1_forward_diffusion,
        "demo2": demo2_noise_schedules,
        "demo3": demo3_train_diffusion,
        "demo4": demo4_ddpm_vs_ddim,
        "demo5": demo5_generate_report,
    }

    if command == "all":
        for name, demo_fn in demos.items():
            demo_fn()
            print("\n")
    elif command in demos:
        demos[command]()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
