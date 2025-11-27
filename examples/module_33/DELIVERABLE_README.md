# Module 33 Deliverable: Diffusion Lab

**Understand diffusion models from first principles with interactive demos.**

## Features

- **Forward Diffusion Visualization**: Watch data dissolve into noise
- **Noise Schedule Comparison**: Linear, cosine, quadratic schedules
- **Minimal Diffusion Model**: Train on 2D data (spirals, moons)
- **DDPM vs DDIM**: Compare sampling speed and quality
- **Analysis Reports**: Comprehensive markdown reports

## Quick Start

```bash
# Forward diffusion process
python deliverable_diffusion_lab.py demo1

# Noise schedules comparison
python deliverable_diffusion_lab.py demo2

# Train minimal diffusion model (requires PyTorch)
python deliverable_diffusion_lab.py demo3

# DDPM vs DDIM sampling
python deliverable_diffusion_lab.py demo4

# Generate analysis report
python deliverable_diffusion_lab.py demo5

# Run all demos
python deliverable_diffusion_lab.py all
```

## Key Concepts Demonstrated

### Forward Diffusion

```
x_t = √ᾱ_t · x_0 + √(1 - ᾱ_t) · ε

Signal preserved: √ᾱ_t (decreases with t)
Noise added: √(1 - ᾱ_t) (increases with t)
```

### Noise Schedules

| Schedule | Characteristic | Best For |
|----------|----------------|----------|
| Linear | Uniform noise addition | Simple cases |
| Cosine | Slower at start/end | Image generation |
| Quadratic | Very slow start | Fine details |

### DDPM vs DDIM

| Method | Steps | Speed | Quality |
|--------|-------|-------|---------|
| DDPM | 1000 | Slow | Highest |
| DDIM | 50 | 20x faster | ~Same |
| DDIM | 20 | 50x faster | Good |

## Output Files

Generated in `.diffusion_lab/`:

```
.diffusion_lab/
├── diffusion_report.md     # Comprehensive analysis
└── schedule_analysis.json  # Schedule data
```

## Requirements

- **Required**: numpy
- **Optional**: PyTorch (for training demos)

Without PyTorch, demos 1, 2, and 5 still work!

## Key Insights

1. **Forward process is easy**: Just add noise according to schedule
2. **Reverse process is learned**: Neural network predicts the noise
3. **Loss is simple**: MSE between true and predicted noise
4. **DDIM enables fast sampling**: 50 steps ≈ 1000 DDPM steps
5. **Schedule matters**: Cosine preserves details longer

---

**Time**: ~4 hours | **Lines**: 600+ | **Author**: Neural Dojo
