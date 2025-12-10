# Module 33: Diffusion Models & Image Generation
# Or: How AI Learned to Dream in Pixels

**Last Updated**: 2025-11-27
**Status**: Complete
**Reading Time**: 7-8 hours
**Prerequisites**: Module 32

---

## Learning Objectives

By the end of this module, you will:
- Understand how diffusion models generate images from noise
- Master the forward and reverse diffusion processes
- Learn the U-Net architecture for denoising
- Understand text conditioning with CLIP
- Implement classifier-free guidance
- Know how Stable Diffusion works end-to-end
- Apply LoRA to customize image generation

---

## The Image That Shook the Art World

**London. August 30, 2022. 2:30 PM.**

Jason Allen was nervous. He had just won first place in the digital art category at the Colorado State Fair—beating human artists who had spent months on their entries. His piece, "Théâtre D'opéra Spatial," depicted an elaborate operatic scene with ethereal lighting and impossible architecture.

The problem? Jason had created it with Midjourney, an AI image generator, in about 80 hours of prompt refinement.

When the news broke, artists were furious. "This is the death of artistry," one competitor declared. "We're watching the decay of legitimate artistic work." Twitter erupted. News outlets covered it for weeks. A debate about creativity, authenticity, and the future of art consumed the internet.

What most people didn't know: Midjourney was powered by diffusion models—the same technology driving Stable Diffusion, DALL-E 2, and a revolution in how images are created. And this was just the beginning.

> "I'm not going to apologize for it. I won. I didn't break any rules."
> — Jason Allen, 2022

Within two years, diffusion models would be generating billions of images daily, disrupting stock photography, transforming advertising, and forcing every creative industry to reckon with AI-generated content.

This module teaches you how diffusion models work—from pure noise to photorealistic images, one denoising step at a time.

---

## The Big Picture: Teaching AI to Dream

Imagine you're watching a time-lapse of a photograph slowly dissolving into static noise on an old TV. Frame by frame, the image becomes less recognizable until it's pure random fuzz.

Now imagine playing that video in reverse — starting from static and watching a photograph emerge from nothing.

That's diffusion. We train a neural network to reverse the corruption process, to look at noisy images and predict what they looked like before the noise was added. Do this enough times, starting from pure noise, and you can generate entirely new images.

It's like teaching someone to restore damaged photographs — but so well that they can "restore" photographs that never existed.

### Why Diffusion Won

Before diffusion models, we had:
- **GANs** (2014): Two networks fighting — often unstable, mode collapse
- **VAEs** (2013): Encode-decode with latent space — often blurry
- **Autoregressive** (2016): Generate pixel by pixel — slow, loses global coherence

Diffusion models combined the best properties:
- **Stable training** (no adversarial games)
- **High quality** (sharp, coherent images)
- **Flexible** (easy to condition on text, class, etc.)
- **Theoretically grounded** (solid probabilistic foundation)

> **Did You Know?** Diffusion models were largely ignored for years after being introduced. The original paper by Sohl-Dickstein et al. (2015) "Deep Unsupervised Learning using Nonequilibrium Thermodynamics" drew from statistical physics. It took until 2020 when Jonathan Ho's DDPM paper showed they could match GANs in image quality, and 2022 when Stable Diffusion went viral, for the world to pay attention.

---

## The Forward Process: Destroying Images Scientifically

The forward process is simple: gradually add Gaussian noise to an image until it becomes pure noise.

### The Math

At each timestep t, we add a small amount of noise:

```
x_t = √(1 - β_t) · x_{t-1} + √(β_t) · ε

Where:
- x_t is the noisy image at timestep t
- x_{t-1} is the image at the previous timestep
- β_t is the noise schedule (small value, e.g., 0.0001 to 0.02)
- ε ~ N(0, I) is random Gaussian noise
```

**Worked Example:**

Let's trace a single pixel value through 4 timesteps:

```
Original pixel value: x_0 = 0.8
Noise schedule: β = [0.1, 0.2, 0.3, 0.4]

Step 1: β_1 = 0.1
  x_1 = √0.9 · 0.8 + √0.1 · (-0.5)  [random noise = -0.5]
  x_1 = 0.949 · 0.8 + 0.316 · (-0.5)
  x_1 = 0.759 - 0.158 = 0.601

Step 2: β_2 = 0.2
  x_2 = √0.8 · 0.601 + √0.2 · (0.3)  [random noise = 0.3]
  x_2 = 0.894 · 0.601 + 0.447 · 0.3
  x_2 = 0.537 + 0.134 = 0.671

Step 3: β_3 = 0.3
  x_3 = √0.7 · 0.671 + √0.3 · (-0.8)  [random noise = -0.8]
  x_3 = 0.837 · 0.671 + 0.548 · (-0.8)
  x_3 = 0.561 - 0.438 = 0.123

Step 4: β_4 = 0.4
  x_4 = √0.6 · 0.123 + √0.4 · (0.9)  [random noise = 0.9]
  x_4 = 0.775 · 0.123 + 0.632 · 0.9
  x_4 = 0.095 + 0.569 = 0.664
```

Notice how the pixel value drifts randomly as noise accumulates. After enough steps (~1000), the original value is completely lost.

### The Reparameterization Trick

We can skip directly to any timestep using cumulative products:

```
α_t = 1 - β_t
ᾱ_t = α_1 · α_2 · ... · α_t  (cumulative product)

x_t = √ᾱ_t · x_0 + √(1 - ᾱ_t) · ε
```

This lets us sample any noisy version directly without iterating through all steps!

```python
def forward_diffusion(x_0, t, noise_schedule):
    """Add noise to image at timestep t."""
    alpha_bar = torch.cumprod(1 - noise_schedule, dim=0)
    alpha_bar_t = alpha_bar[t]

    noise = torch.randn_like(x_0)

    # Direct formula: x_t = √ᾱ_t · x_0 + √(1-ᾱ_t) · ε
    x_t = torch.sqrt(alpha_bar_t) * x_0 + torch.sqrt(1 - alpha_bar_t) * noise

    return x_t, noise
```

Notice how we return both the noisy image AND the noise we added — the model will learn to predict this noise.

---

## The Reverse Process: Learning to Denoise

The reverse process is where the magic happens. We train a neural network to predict the noise that was added, then subtract it.

### The Training Objective

The loss is surprisingly simple:

```
L = E[||ε - ε_θ(x_t, t)||²]

Where:
- ε is the actual noise we added
- ε_θ(x_t, t) is the model's prediction of that noise
- x_t is the noisy image
- t is the timestep (tells model how noisy the image is)
```

It's just MSE between the true noise and predicted noise!

Think of it like this: We show the model a corrupted image and ask "What noise was added?" The model learns to recognize the noise pattern and predict it. Once we know the noise, we can subtract it to get a cleaner image.

### Training Loop

```python
def train_step(model, x_0, noise_schedule):
    """Single training step for diffusion model."""
    batch_size = x_0.shape[0]

    # 1. Sample random timesteps
    t = torch.randint(0, len(noise_schedule), (batch_size,))

    # 2. Add noise (forward process)
    x_t, noise = forward_diffusion(x_0, t, noise_schedule)

    # 3. Predict the noise
    noise_pred = model(x_t, t)

    # 4. Compute loss (simple MSE!)
    loss = F.mse_loss(noise_pred, noise)

    return loss
```

Notice how each training step samples a random timestep — the model learns to denoise at ALL noise levels, not just one.

> **Did You Know?** The idea of predicting noise instead of the clean image was a key insight from Ho et al.'s DDPM paper. Earlier work tried to predict the clean image directly, which is much harder. Predicting noise is easier because the noise has a known distribution (Gaussian), while images have complex, varied distributions.

---

## The U-Net: Architecture for Denoising

The workhorse of diffusion models is the **U-Net** — a convolutional architecture shaped like the letter U.

### Why U-Net?

Denoising requires understanding both:
- **Global structure**: Is this a face? A landscape? Where should the eyes be?
- **Local details**: Exact pixel values, textures, edges

U-Net achieves this through:
1. **Encoder** (downsampling): Captures global context
2. **Decoder** (upsampling): Reconstructs details
3. **Skip connections**: Preserve fine-grained information

```
Input (noisy image)
    │
    ▼
┌─────────┐
│  Conv   │─────────────────────────────┐ (skip connection)
│ 64→128  │                             │
└────┬────┘                             │
     │ downsample                       │
     ▼                                  │
┌─────────┐                             │
│  Conv   │──────────────────┐          │
│128→256  │                  │          │
└────┬────┘                  │          │
     │ downsample            │          │
     ▼                       │          │
┌─────────┐                  │          │
│ Bottleneck                 │          │
│256→256  │                  │          │
└────┬────┘                  │          │
     │ upsample              │          │
     ▼                       ▼          │
┌─────────┐            ┌─────────┐      │
│  Conv   │◄───concat──│  skip   │      │
│256→128  │            └─────────┘      │
└────┬────┘                             │
     │ upsample                         │
     ▼                                  ▼
┌─────────┐                       ┌─────────┐
│  Conv   │◄──────────concat──────│  skip   │
│128→64   │                       └─────────┘
└────┬────┘
     │
     ▼
Output (predicted noise)
```

### Time Embedding

The model needs to know the timestep (noise level). We encode this as a sinusoidal embedding (like positional encoding in transformers):

```python
def timestep_embedding(t, dim):
    """Create sinusoidal timestep embedding."""
    half_dim = dim // 2
    emb = math.log(10000) / (half_dim - 1)
    emb = torch.exp(torch.arange(half_dim) * -emb)
    emb = t[:, None] * emb[None, :]
    emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=-1)
    return emb
```

This embedding is added to each layer of the U-Net, telling it how noisy the input is.

### Attention in U-Net

Modern U-Nets include self-attention layers (especially at lower resolutions) to capture long-range dependencies:

```python
class AttentionBlock(nn.Module):
    """Self-attention for spatial features."""

    def __init__(self, channels):
        super().__init__()
        self.norm = nn.GroupNorm(8, channels)
        self.qkv = nn.Conv1d(channels, channels * 3, 1)
        self.proj = nn.Conv1d(channels, channels, 1)

    def forward(self, x):
        b, c, h, w = x.shape
        x_flat = x.view(b, c, h * w)

        qkv = self.qkv(self.norm(x_flat))
        q, k, v = qkv.chunk(3, dim=1)

        # Scaled dot-product attention
        attn = torch.softmax(q.transpose(-1, -2) @ k / math.sqrt(c), dim=-1)
        out = (v @ attn.transpose(-1, -2)).view(b, c, h, w)

        return x + self.proj(out.view(b, c, -1)).view(b, c, h, w)
```

Notice how attention lets distant pixels communicate — crucial for maintaining global coherence in generated images.

> **Did You Know?** The U-Net architecture was originally invented by Olaf Ronneberger in 2015 for biomedical image segmentation (detecting cell boundaries in microscopy images). It became the standard for diffusion models because its skip connections perfectly preserve the fine details needed for high-quality image generation.

---

## DDPM vs DDIM: Speed vs Quality

### DDPM (Denoising Diffusion Probabilistic Models)

The original formulation requires many steps (~1000) because each step only removes a tiny bit of noise.

**Sampling:**
```python
def ddpm_sample(model, shape, noise_schedule, num_steps=1000):
    """Sample using DDPM (slow but high quality)."""
    x = torch.randn(shape)  # Start from pure noise

    for t in reversed(range(num_steps)):
        # Predict noise
        noise_pred = model(x, t)

        # Compute coefficients
        alpha = 1 - noise_schedule[t]
        alpha_bar = torch.cumprod(1 - noise_schedule[:t+1], dim=0)[-1]
        beta = noise_schedule[t]

        # Denoise one step
        mean = (1 / torch.sqrt(alpha)) * (
            x - (beta / torch.sqrt(1 - alpha_bar)) * noise_pred
        )

        # Add noise (except at t=0)
        if t > 0:
            noise = torch.randn_like(x)
            x = mean + torch.sqrt(beta) * noise
        else:
            x = mean

    return x
```

**Problem**: 1000 forward passes through a huge U-Net = slow!

### DDIM (Denoising Diffusion Implicit Models)

Song et al. (2020) discovered you can skip steps by making the process deterministic:

```python
def ddim_sample(model, shape, noise_schedule, num_steps=50):
    """Sample using DDIM (fast, deterministic)."""
    x = torch.randn(shape)

    # Use only a subset of timesteps
    timesteps = torch.linspace(999, 0, num_steps).long()

    for i, t in enumerate(timesteps):
        noise_pred = model(x, t)

        alpha_bar_t = get_alpha_bar(t, noise_schedule)

        if i < len(timesteps) - 1:
            alpha_bar_prev = get_alpha_bar(timesteps[i+1], noise_schedule)
        else:
            alpha_bar_prev = 1.0

        # DDIM update (no random noise!)
        pred_x0 = (x - torch.sqrt(1 - alpha_bar_t) * noise_pred) / torch.sqrt(alpha_bar_t)
        dir_xt = torch.sqrt(1 - alpha_bar_prev) * noise_pred
        x = torch.sqrt(alpha_bar_prev) * pred_x0 + dir_xt

    return x
```

**DDIM advantages:**
- 20-50 steps instead of 1000 (20-50x faster!)
- Deterministic (same noise → same image)
- Allows interpolation in latent space

Notice how DDIM removes the random noise term — the process becomes deterministic, which is why the same starting noise always produces the same image.

---

## Text Conditioning: From Words to Images

How do we go from "a cat wearing a top hat" to an actual image?

### CLIP: Connecting Text and Images

CLIP (Contrastive Language-Image Pre-training) by OpenAI learns to align text and image representations:

```
"a photo of a cat"  ──► Text Encoder  ──► [0.2, -0.5, 0.8, ...]
                                              │
                                              │ should be similar!
                                              │
[actual cat photo]  ──► Image Encoder ──► [0.3, -0.4, 0.7, ...]
```

CLIP was trained on 400 million image-text pairs from the internet. It learns that "cat" and images of cats should have similar embeddings.

### Cross-Attention for Conditioning

We inject text information into the U-Net using cross-attention:

```python
class CrossAttention(nn.Module):
    """Attend to text embeddings."""

    def __init__(self, query_dim, context_dim):
        super().__init__()
        self.to_q = nn.Linear(query_dim, query_dim)
        self.to_k = nn.Linear(context_dim, query_dim)
        self.to_v = nn.Linear(context_dim, query_dim)
        self.to_out = nn.Linear(query_dim, query_dim)

    def forward(self, x, context):
        """
        x: image features [batch, seq, dim]
        context: text embeddings [batch, text_len, context_dim]
        """
        q = self.to_q(x)
        k = self.to_k(context)
        v = self.to_v(context)

        # Attention: image queries attend to text keys/values
        attn = torch.softmax(q @ k.transpose(-1, -2) / math.sqrt(q.shape[-1]), dim=-1)
        out = attn @ v

        return self.to_out(out)
```

Notice how cross-attention lets every spatial location in the image "look at" the text tokens. When generating the cat's location, those pixels attend strongly to the "cat" token.

> **Did You Know?** CLIP was trained with a simple contrastive loss: given a batch of image-text pairs, maximize similarity between matching pairs and minimize similarity between non-matching pairs. This seemingly simple objective created representations so powerful they enabled zero-shot image classification, revolutionized image search, and became the backbone of text-to-image generation.

---

## Classifier-Free Guidance: Steering Generation

One of the most important techniques for high-quality generation is **classifier-free guidance** (CFG).

### The Problem

Text conditioning alone often produces images that vaguely match the prompt but lack detail or accuracy. We want stronger adherence to the prompt.

### The Solution

Train the model with **conditional dropout** — sometimes give it the text, sometimes don't:

```python
def train_with_cfg(model, x_0, text_embedding, noise_schedule, drop_prob=0.1):
    """Training with classifier-free guidance preparation."""
    t = torch.randint(0, len(noise_schedule), (x_0.shape[0],))
    x_t, noise = forward_diffusion(x_0, t, noise_schedule)

    # Randomly drop text conditioning
    if random.random() < drop_prob:
        text_embedding = torch.zeros_like(text_embedding)  # Unconditional

    noise_pred = model(x_t, t, text_embedding)
    loss = F.mse_loss(noise_pred, noise)

    return loss
```

At inference, run the model twice and blend:

```python
def cfg_sample(model, x_t, t, text_embedding, guidance_scale=7.5):
    """Sample with classifier-free guidance."""
    # Unconditional prediction (no text)
    noise_uncond = model(x_t, t, torch.zeros_like(text_embedding))

    # Conditional prediction (with text)
    noise_cond = model(x_t, t, text_embedding)

    # Blend: move AWAY from unconditional, TOWARD conditional
    noise_pred = noise_uncond + guidance_scale * (noise_cond - noise_uncond)

    return noise_pred
```

**Guidance scale effects:**
- `guidance_scale = 1.0`: Pure conditional (often blurry)
- `guidance_scale = 7-8`: Good balance (typical default)
- `guidance_scale > 15`: Over-saturated, artifacts

Think of it like this: unconditional output is "generic image," conditional is "image matching your prompt." We extrapolate beyond conditional to get MORE of what makes it match the prompt.

---

## Stable Diffusion: The Full Architecture

Stable Diffusion combines everything into a complete text-to-image system:

```
┌─────────────────────────────────────────────────────────────┐
│                    STABLE DIFFUSION                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "a cat wearing       ┌──────────┐                          │
│   a top hat"    ───►  │   CLIP   │ ───► text embeddings     │
│                       │  Text    │     [77, 768]            │
│                       │ Encoder  │                          │
│                       └──────────┘          │               │
│                                             │               │
│                                             ▼               │
│  Random noise    ┌─────────────────────────────────┐        │
│  [4, 64, 64] ───►│         U-Net                   │        │
│                  │   (with cross-attention)        │        │
│                  │                                 │        │
│  timestep ──────►│   Predicts noise in latent     │        │
│                  │   space (not pixel space!)      │        │
│                  └─────────────────────────────────┘        │
│                                    │                        │
│                                    ▼                        │
│                           denoised latent                   │
│                              [4, 64, 64]                    │
│                                    │                        │
│                                    ▼                        │
│                            ┌──────────┐                     │
│                            │   VAE    │                     │
│                            │ Decoder  │                     │
│                            └──────────┘                     │
│                                    │                        │
│                                    ▼                        │
│                             Final Image                     │
│                            [3, 512, 512]                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Innovation: Latent Diffusion

Instead of running diffusion on full 512×512×3 images (786K values), Stable Diffusion runs in a compressed **latent space** (64×64×4 = 16K values).

The VAE (Variational Autoencoder) compresses and decompresses:
- **Encoder**: 512×512×3 → 64×64×4 (48× compression!)
- **Decoder**: 64×64×4 → 512×512×3

This makes training and inference dramatically faster.

```python
def stable_diffusion_inference(prompt, num_steps=50, guidance_scale=7.5):
    """Complete Stable Diffusion inference."""
    # 1. Encode text
    text_embeddings = clip_encoder(prompt)

    # 2. Start from random latent noise
    latents = torch.randn(1, 4, 64, 64)

    # 3. Denoise in latent space
    for t in tqdm(scheduler.timesteps):
        # Expand latents for CFG (unconditional + conditional)
        latent_input = torch.cat([latents] * 2)

        # Predict noise
        noise_pred = unet(latent_input, t, text_embeddings)

        # Apply CFG
        noise_uncond, noise_cond = noise_pred.chunk(2)
        noise_pred = noise_uncond + guidance_scale * (noise_cond - noise_uncond)

        # Scheduler step (DDIM, etc.)
        latents = scheduler.step(noise_pred, t, latents)

    # 4. Decode latents to image
    image = vae.decode(latents)

    return image
```

Notice how the entire diffusion process happens in latent space — we only touch pixel space once at the very end.

> **Did You Know?** Stable Diffusion was created by Stability AI in collaboration with researchers from LMU Munich and Runway. The key innovation of latent diffusion came from Robin Rombach's PhD work. By open-sourcing the model weights, Stability AI sparked an explosion of creativity — thousands of fine-tuned models, LoRAs, and applications emerged within months.

---

## LoRA for Stable Diffusion

Just like with LLMs, we can fine-tune Stable Diffusion with LoRA to create custom styles or characters.

### What to Fine-tune

Stable Diffusion's U-Net has ~860M parameters. With LoRA, we typically target:
- **Cross-attention layers**: Keys and values (text → image mapping)
- **Self-attention layers**: Image coherence
- **Linear layers**: General adaptation

```python
from peft import LoraConfig, get_peft_model

# LoRA config for Stable Diffusion
lora_config = LoraConfig(
    r=4,                          # Low rank works well for SD
    lora_alpha=4,
    target_modules=[
        "to_k", "to_q", "to_v",   # Cross-attention
        "to_out.0",               # Output projection
        "proj_in", "proj_out",    # Convolutions
    ],
    lora_dropout=0.0,
)

# Apply to U-Net
unet = get_peft_model(unet, lora_config)
```

### Training Data

For LoRA fine-tuning, you typically need:
- **Style transfer**: 10-50 images of the target style
- **Character/concept**: 5-20 images of the subject
- **Captions**: Descriptions of each image

### Dreambooth vs LoRA

| Aspect | Dreambooth | LoRA |
|--------|------------|------|
| Parameters | Full fine-tune | 0.1% of parameters |
| Data needed | 3-10 images | 5-50 images |
| Training time | 15-30 min | 10-20 min |
| Model size | Full copy (~5GB) | Adapter only (~10-100MB) |
| Combinability | Hard | Easy (stack multiple) |

LoRA's killer feature: you can combine multiple LoRAs at inference time!

```python
# Load and combine multiple LoRAs
base_model = load_stable_diffusion()
art_style_lora = load_lora("impressionist_style.safetensors")
character_lora = load_lora("my_character.safetensors")

# Apply both with different strengths
model = apply_lora(base_model, art_style_lora, strength=0.8)
model = apply_lora(model, character_lora, strength=0.6)

# Generate: character in impressionist style!
image = model("portrait of [character], impressionist painting")
```

---

## Common Pitfalls and Solutions

### 1. Blurry or Low-Quality Images

**Causes:**
- Guidance scale too low
- Too few denoising steps
- Poor prompt engineering

**Solutions:**
- Increase guidance scale (try 7-12)
- Use at least 30-50 steps
- Be specific in prompts

### 2. Prompt Not Followed

**Causes:**
- Conflicting prompt elements
- Weak words not emphasized
- Model bias toward common concepts

**Solutions:**
- Use parentheses for emphasis: `(detailed hands:1.3)`
- Negative prompts: exclude unwanted elements
- Reorder prompt (earlier = more important)

### 3. Artifacts and Distortions

**Causes:**
- Guidance scale too high
- Incompatible model/LoRA combinations
- Poor training data (for custom models)

**Solutions:**
- Lower guidance scale
- Check LoRA compatibility
- Curate training data carefully

### 4. Inconsistent Characters

**Causes:**
- No character consistency mechanism
- Varied poses/angles in training data

**Solutions:**
- Use reference images (IP-Adapter)
- Train dedicated character LoRA
- Use consistent seed for similar outputs

### 5. Slow Generation

**Causes:**
- Too many steps
- Not using optimizations

**Solutions:**
- Use DDIM or DPM++ schedulers (20-30 steps)
- Enable xformers memory-efficient attention
- Use FP16/BF16 precision
- Consider LCM-LoRA for 4-8 step generation

> **Did You Know?** The "hands problem" that plagued early diffusion models (generating extra fingers, distorted hands) happens because hands are underrepresented in training data compared to faces, and they have complex, variable geometry. Newer models like SDXL and SD 3.0 have improved significantly through better training data curation and architectural improvements.

---

## The Diffusion Family Tree

```
2015: Diffusion Models (Sohl-Dickstein)
        └── Theoretical foundation from thermodynamics

2020: DDPM (Ho et al.)
        └── Practical implementation, matched GAN quality
        └── 1000 steps, slow but stable

2020: DDIM (Song et al.)
        └── Deterministic sampling
        └── 50 steps, much faster

2021: Guided Diffusion (Dhariwal & Nichol)
        └── Classifier guidance
        └── Beat GANs on ImageNet

2021: GLIDE (OpenAI)
        └── Text-to-image with CLIP
        └── Classifier-free guidance

2022: DALL-E 2 (OpenAI)
        └── Diffusion + CLIP prior
        └── High-quality text-to-image

2022: Stable Diffusion (Stability AI)
        └── Latent diffusion (efficient!)
        └── Open source revolution

2023: SDXL (Stability AI)
        └── 1024px, better prompts
        └── Two U-Nets (base + refiner)

2024: SD 3.0 / Flux
        └── Transformer-based (DiT)
        └── Better text rendering
```

---

## Quiz: Test Your Understanding

**Q1**: Why does Stable Diffusion run diffusion in latent space instead of pixel space?

<details>
<summary>Answer</summary>

Running in latent space is **48× more efficient**:
- Pixel space: 512×512×3 = 786,432 values
- Latent space: 64×64×4 = 16,384 values

This makes training and inference dramatically faster while maintaining quality because:
1. The VAE learns to compress to perceptually important features
2. The U-Net can focus on semantic content, not pixel details
3. Less memory, faster forward passes

</details>

**Q2**: What is classifier-free guidance and why does it improve image quality?

<details>
<summary>Answer</summary>

Classifier-free guidance (CFG) combines unconditional and conditional predictions:

```
noise_pred = noise_uncond + scale × (noise_cond - noise_uncond)
```

It improves quality by:
1. **Amplifying** features that distinguish "this prompt" from "generic image"
2. **Suppressing** generic features not specific to the prompt
3. Creating a **trade-off**: higher scale = more prompt adherence but more artifacts

Typical scales: 7-8 for balance, higher for artistic effect.

</details>

**Q3**: A diffusion model is trained for 1000 timesteps. During inference, you want to generate an image in 50 steps. What technique allows this?

<details>
<summary>Answer</summary>

**DDIM (Denoising Diffusion Implicit Models)** allows skipping steps by:

1. Making the sampling process **deterministic** (no random noise added)
2. Using a **non-Markovian** process that can "skip" timesteps
3. Interpolating directly between any two noise levels

DDPM requires sequential steps because each step adds random noise. DDIM removes this randomness, allowing larger jumps.

</details>

**Q4**: You're training a LoRA on Stable Diffusion to create a specific art style. You have 30 training images. What modules should you target and why?

<details>
<summary>Answer</summary>

For **style transfer**, target:

1. **Cross-attention K/V** (`to_k`, `to_v`): How text maps to image features
2. **Self-attention** (`to_q`, `to_k`, `to_v` in self-attn): Image coherence and style
3. **Output projections** (`to_out`): Final feature transformation

**Why**: Style is primarily about HOW features are rendered, which is controlled by attention patterns. Cross-attention controls text→image mapping (so "painting" triggers your style), while self-attention controls overall image coherence.

Low rank (r=4-8) is usually sufficient for style.

</details>

**Q5**: Explain why the forward diffusion process uses the formula `x_t = √ᾱ_t · x_0 + √(1 - ᾱ_t) · ε` instead of just `x_t = x_0 + ε`.

<details>
<summary>Answer</summary>

The formula maintains **unit variance** throughout the diffusion process:

```
Var(x_t) = (√ᾱ_t)² · Var(x_0) + (√(1-ᾱ_t))² · Var(ε)
         = ᾱ_t · 1 + (1-ᾱ_t) · 1
         = 1
```

If we just added noise (`x_t = x_0 + ε`), variance would grow unbounded, making training unstable.

The coefficients ensure:
1. **Signal preservation**: `√ᾱ_t` controls how much original signal remains
2. **Noise calibration**: `√(1-ᾱ_t)` controls noise magnitude
3. **Smooth transition**: From pure signal (t=0) to pure noise (t=T)

This is also known as a **variance-preserving** diffusion process.

</details>

---

## Summary

You've learned:

1. **Diffusion = noise and denoise**: Forward adds noise, reverse removes it
2. **U-Net architecture**: Encoder-decoder with skip connections for denoising
3. **DDPM vs DDIM**: 1000 steps vs 50 steps, quality vs speed trade-off
4. **Text conditioning**: CLIP embeddings + cross-attention
5. **Classifier-free guidance**: Amplify prompt adherence by comparing conditional vs unconditional
6. **Stable Diffusion**: Latent diffusion (VAE + U-Net + CLIP) for efficiency
7. **LoRA**: Efficient fine-tuning for custom styles/characters

The key insight: Diffusion models learn to **reverse corruption**. Train on "what noise was added?" and you get a model that can generate images from pure noise.

---

## Further Reading

### Essential Papers

1. **DDPM**: "Denoising Diffusion Probabilistic Models" (Ho et al., 2020)
   - https://arxiv.org/abs/2006.11239

2. **DDIM**: "Denoising Diffusion Implicit Models" (Song et al., 2020)
   - https://arxiv.org/abs/2010.02502

3. **Latent Diffusion**: "High-Resolution Image Synthesis with Latent Diffusion Models" (Rombach et al., 2022)
   - https://arxiv.org/abs/2112.10752

4. **Classifier-Free Guidance**: (Ho & Salimans, 2022)
   - https://arxiv.org/abs/2207.12598

### Tutorials and Code

1. **Hugging Face Diffusers**: Official library
   - https://huggingface.co/docs/diffusers

2. **The Annotated Diffusion Model**: Step-by-step implementation
   - https://huggingface.co/blog/annotated-diffusion

3. **Stable Diffusion Deep Dive**: Comprehensive guide
   - https://stability.ai/research

---

## Next Steps

Move on to **Module 34: Code Generation Models** where you'll learn:
- How Codex, Copilot, and Code Llama work
- Specialized training for code
- Fill-in-the-middle and infilling
- Evaluating code generation

Or explore the deliverable to:
- Visualize the diffusion process step by step
- Experiment with different schedulers
- Generate images with Stable Diffusion
- Create custom LoRAs

---

_Last updated: 2025-11-27_
_Status: Complete_
