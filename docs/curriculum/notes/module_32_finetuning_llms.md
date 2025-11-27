# Module 32: Fine-tuning Large Language Models
# Or: Teaching Old Models New Tricks (Without Breaking the Bank)

**Last Updated**: 2025-11-27
**Status**: Complete
**Reading Time**: 7-8 hours
**Prerequisites**: Module 31

---

## Learning Objectives

By the end of this module, you will:
- Understand when to fine-tune vs use RAG vs prompt engineering
- Master LoRA and QLoRA for efficient fine-tuning
- Fine-tune open-source models (Llama, Mistral) on custom datasets
- Prepare high-quality training datasets
- Evaluate fine-tuned models properly
- Deploy fine-tuned models to production
- Calculate and optimize fine-tuning costs

---

## The Big Picture: Why Fine-tune?

Imagine you've hired a brilliant new employee — they graduated top of their class, speak eloquently, and have read millions of books. But they know nothing about *your* company. They don't know your products, your jargon, or how you like things done.

You have three options:
1. **Give them a manual to consult** (RAG) — they look things up as needed
2. **Coach them with examples** (prompt engineering) — show them what you want each time
3. **Train them on the job** (fine-tuning) — they internalize your company's way

Fine-tuning is option 3. It modifies the model's weights so the knowledge becomes *part* of the model, not something it retrieves or is reminded of each time.

### When to Fine-tune

| Use Case | Best Approach |
|----------|---------------|
| Custom knowledge (docs, FAQs) | RAG |
| New tasks with few examples | Few-shot prompting |
| Consistent style/format | Fine-tuning |
| Domain-specific language | Fine-tuning |
| New behaviors/capabilities | Fine-tuning |
| Cost optimization (repeated tasks) | Fine-tuning |
| Speed optimization | Fine-tuning |

**The key insight**: Fine-tuning changes *how* the model behaves, not *what* it knows. For adding knowledge, use RAG. For changing behavior, use fine-tuning.

> **Did You Know?** OpenAI's ChatGPT wasn't just a larger GPT-3. The magic came from fine-tuning: first on human demonstrations (SFT), then on human preferences (RLHF). The base GPT-3 couldn't hold a conversation — fine-tuning taught it to be helpful, harmless, and honest. This insight spawned an entire field of "alignment" research.

---

## The Fine-tuning Spectrum

Not all fine-tuning is created equal. There's a spectrum from full fine-tuning to minimal adaptation:

```
Full Fine-tuning ←────────────────────────→ No Fine-tuning
    │                                            │
    │   LoRA    QLoRA    Prompt     Few-shot    │
    │    │        │      Tuning      Learning   │
    │    ▼        ▼        ▼           ▼        │
 [All params] [4-bit] [Soft prompts] [In-context]
```

### Full Fine-tuning

Update ALL model parameters. For a 7B model:
- 7 billion parameters × 4 bytes = **28 GB** just for the model
- Plus optimizer states (Adam needs 2x): **84 GB** total
- Plus activations, gradients: **~100+ GB**

You need multiple A100s ($10-30/hour on cloud).

### Parameter-Efficient Fine-tuning (PEFT)

The insight: We don't need to update all parameters! We can:
1. **Freeze** most of the model
2. **Add** small trainable components
3. **Train** only these new components

This reduces memory from 100GB to 10-15GB — fitting on consumer GPUs!

Think of it like this: Instead of rebuilding the entire house to add a room, you're just adding an extension. The foundation (original weights) stays intact.

---

## LoRA: The Game-Changer

**LoRA** (Low-Rank Adaptation) is the most important fine-tuning technique to understand. Published by Microsoft in 2021, it revolutionized how we customize LLMs.

### The Core Idea

Neural network weight matrices are typically huge. For a 7B model, a single layer's attention weights might be 4096×4096 = 16.7 million parameters.

LoRA's insight: **The update to these weights during fine-tuning is low-rank**. We don't need a full 4096×4096 update matrix — a much smaller decomposition works just as well.

Think of it like **compression**. Just as a high-resolution image can often be compressed to 10% of its size without visible quality loss, the fine-tuning update can be compressed dramatically.

### The Math

Instead of updating weight W directly:

```
W_new = W + ΔW
```

LoRA decomposes the update into two smaller matrices:

```
W_new = W + B × A

Where:
- W is frozen (original weights): d × d
- A is trainable: r × d  (r << d)
- B is trainable: d × r
- ΔW = B × A: d × d (reconstructed)
```

**Worked Example:**

Original layer: 4096 × 4096 = 16,777,216 parameters (17M)

With LoRA (rank r = 16):
- A: 16 × 4096 = 65,536 parameters
- B: 4096 × 16 = 65,536 parameters
- Total: 131,072 parameters (131K)

**Compression ratio**: 17M / 131K = **128×** fewer trainable parameters!

### Visual Representation

```
Original:               With LoRA:

┌─────────┐            ┌─────────┐
│         │            │    W    │ (frozen)
│    W    │            │         │
│  d × d  │     →      └────┬────┘
│         │                 │
└─────────┘            ┌────┴────┐
                       │    +    │
                       └────┬────┘
                            │
                       ┌────┴────┐
                       │  B × A  │
                       │(d×r×r×d)│ (trainable)
                       └─────────┘
```

### Why Low-Rank Works

During fine-tuning, the model doesn't need to learn entirely new representations — it just needs to *adapt* existing ones to the new task. This adaptation lies in a low-dimensional subspace.

The original paper showed that with r=8 (just 8 dimensions!), LoRA could match full fine-tuning performance on many tasks. This is remarkable: 8 dimensions capturing the essence of a task-specific adaptation!

> **Did You Know?** Edward Hu, the lead author of the LoRA paper, was a PhD student at Microsoft Research when he developed the technique. The paper was initially rejected from NeurIPS 2021 but went on to become one of the most cited and influential papers in LLM adaptation. It's now the standard for fine-tuning open-source models, used by millions.

---

## QLoRA: Fine-tuning for Everyone

QLoRA combines LoRA with **quantization** to make fine-tuning accessible on consumer GPUs.

### What is Quantization?

Models are typically stored in FP32 (32-bit floating point) or FP16 (16-bit). Quantization reduces this to INT8 (8-bit) or even INT4 (4-bit):

```
FP32: 3.14159265... (full precision)
FP16: 3.1416      (half precision)
INT8: 3           (8-bit integer + scale)
INT4: ~3          (4-bit, extreme compression)
```

**Memory savings:**
- FP32: 4 bytes per parameter
- FP16: 2 bytes per parameter
- INT8: 1 byte per parameter
- INT4: 0.5 bytes per parameter

For a 7B model:
- FP32: 28 GB
- FP16: 14 GB
- INT4: 3.5 GB ← Fits on consumer GPU!

### QLoRA's Innovation

QLoRA (Tim Dettmers et al., 2023) introduced:

1. **4-bit NormalFloat (NF4)**: A new 4-bit data type optimized for normally distributed weights
2. **Double Quantization**: Quantize the quantization constants too
3. **Paged Optimizers**: Use CPU RAM when GPU memory fills up

The result: Fine-tune a 65B model on a single 48GB GPU!

### The Catch

Quantization introduces some precision loss. But QLoRA showed that 4-bit base model + LoRA adapters can match 16-bit full fine-tuning on most tasks. The LoRA adapters (trained in full precision) compensate for quantization error.

```python
# QLoRA configuration
from peft import LoraConfig
from transformers import BitsAndBytesConfig

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # NormalFloat4
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,       # Double quantization
)

# LoRA config
lora_config = LoraConfig(
    r=16,                    # Rank
    lora_alpha=32,           # Scaling factor
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    bias="none",
    task_type="CAUSAL_LM",
)
```

Notice how the configuration specifies which modules to apply LoRA to. For transformers, the attention projections (Q, K, V, O) are the most impactful targets.

> **Did You Know?** Tim Dettmers, the creator of QLoRA, is known for his work on making deep learning more accessible. He maintains bitsandbytes, the library that powers QLoRA's quantization. His blog posts on GPU memory optimization are required reading for anyone training large models on limited hardware.

---

## Practical Fine-tuning: Step by Step

Let's walk through fine-tuning a model from start to finish.

### Step 1: Choose Your Base Model

For most use cases, start with these open-source models:

| Model | Size | Good For |
|-------|------|----------|
| **Llama 3.1 8B** | 8B | General tasks, instruction following |
| **Mistral 7B** | 7B | Fast inference, general tasks |
| **Phi-3** | 3.8B | Limited resources, mobile |
| **Qwen 2** | 7B | Multilingual, coding |
| **Gemma 2** | 9B | Google ecosystem |

**Rule of thumb**: Start with the smallest model that might work. Fine-tuning amplifies a model's existing capabilities — it can't add capabilities that aren't there.

### Step 2: Prepare Your Dataset

The quality of your fine-tuning depends entirely on your dataset quality. Garbage in, garbage out.

**Dataset Format:**

Most fine-tuning uses instruction format:

```json
{
  "instruction": "Summarize the following article",
  "input": "The article text here...",
  "output": "The summary here..."
}
```

Or conversation format:

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"},
    {"role": "assistant", "content": "Machine learning is..."}
  ]
}
```

**Dataset Size Guidelines:**

| Task Type | Minimum Samples | Recommended |
|-----------|-----------------|-------------|
| Style transfer | 100-500 | 1,000+ |
| Domain adaptation | 1,000 | 5,000+ |
| New task learning | 5,000 | 10,000+ |
| Behavior modification | 500-2,000 | 5,000+ |

**Quality > Quantity**: 1,000 high-quality examples beat 100,000 noisy ones.

### Step 3: Configure Training

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",

    # Core training settings
    num_train_epochs=3,               # 3-5 epochs typically
    per_device_train_batch_size=4,    # Depends on GPU memory
    gradient_accumulation_steps=4,    # Effective batch = 4 * 4 = 16

    # Learning rate
    learning_rate=2e-4,               # LoRA can use higher LR
    lr_scheduler_type="cosine",       # Gradual decay
    warmup_ratio=0.03,                # Warm up for 3% of steps

    # Optimization
    optim="paged_adamw_8bit",         # Memory-efficient optimizer
    max_grad_norm=0.3,                # Gradient clipping

    # Logging
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="epoch",

    # Memory optimization
    fp16=True,                        # Mixed precision
    gradient_checkpointing=True,       # Trade compute for memory
)
```

Notice how gradient_checkpointing is enabled — this recomputes activations during backward pass instead of storing them, trading ~30% more compute for ~50% less memory.

### Step 4: Fine-tune

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
tokenizer.pad_token = tokenizer.eos_token

# Load model with quantization
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Print trainable parameters
def print_trainable_parameters(model):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable: {trainable:,} ({100 * trainable / total:.2f}%)")

print_trainable_parameters(model)
# Trainable: 6,553,600 (0.08%) <- Only 0.08% of parameters!

# Train
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=512,
)

trainer.train()
```

Notice how only 0.08% of parameters are trainable! This is the power of LoRA.

### Step 5: Save and Merge

After training, you have two options:

**Option A: Keep adapters separate (recommended for testing)**
```python
# Save just the LoRA adapters (small, ~50MB)
model.save_pretrained("./lora-adapters")
```

**Option B: Merge into base model (for deployment)**
```python
# Merge LoRA weights into base model
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./merged-model")
```

---

## Dataset Preparation: The Most Important Step

Your fine-tuning is only as good as your data. Here's how to prepare high-quality datasets.

### Principles of Good Training Data

1. **Diverse but focused**: Cover the range of tasks, but stay on-topic
2. **High quality**: Every example should be something you'd want the model to output
3. **Consistent format**: Use the same structure throughout
4. **Balanced**: Don't over-represent any single pattern
5. **No leakage**: Ensure train/eval split is truly separate

### Data Cleaning Pipeline

```python
import json
from typing import List, Dict

def clean_dataset(examples: List[Dict]) -> List[Dict]:
    """Clean and validate training examples."""
    cleaned = []

    for ex in examples:
        # Skip empty examples
        if not ex.get("instruction") or not ex.get("output"):
            continue

        # Skip very short outputs (likely low quality)
        if len(ex["output"]) < 50:
            continue

        # Skip duplicates (check instruction similarity)
        if is_duplicate(ex, cleaned):
            continue

        # Normalize whitespace
        ex["instruction"] = " ".join(ex["instruction"].split())
        ex["output"] = " ".join(ex["output"].split())

        cleaned.append(ex)

    return cleaned


def format_for_training(example: Dict) -> str:
    """Format example as chat template."""
    return f"""<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
{example['instruction']}<|im_end|>
<|im_start|>assistant
{example['output']}<|im_end|>"""
```

Notice how formatting uses special tokens (`<|im_start|>`, `<|im_end|>`). These must match your base model's chat template — check the tokenizer documentation.

### Common Dataset Sources

1. **Curate from production logs**: Real user queries are gold
2. **Generate with stronger models**: Use GPT-4 to create examples
3. **Public datasets**: Hugging Face Hub has thousands
4. **Manual creation**: Expensive but highest quality

> **Did You Know?** The Alpaca dataset, which kickstarted open-source instruction tuning, was generated by prompting GPT-3 to create 52,000 instruction-following examples. It cost only $500 to generate and enabled fine-tuning Llama 7B to follow instructions. This technique — using a stronger model to generate training data for a weaker one — is called "distillation" and is now standard practice.

---

## Evaluation: How Do You Know It Worked?

Fine-tuning without evaluation is flying blind. Here's how to know if your fine-tuning worked.

### Quantitative Metrics

**Perplexity (PPL)**: How surprised is the model by the test data?
```python
import math

def compute_perplexity(model, eval_dataset, tokenizer):
    model.eval()
    total_loss = 0
    total_tokens = 0

    for batch in eval_dataset:
        with torch.no_grad():
            outputs = model(**batch)
            total_loss += outputs.loss.item() * batch["input_ids"].numel()
            total_tokens += batch["input_ids"].numel()

    perplexity = math.exp(total_loss / total_tokens)
    return perplexity
```

**Task-specific metrics**:
- Classification: Accuracy, F1
- Generation: BLEU, ROUGE
- Code: Pass@k

### Qualitative Evaluation

Run the model on representative prompts and check:
1. Does it follow instructions?
2. Is the style correct?
3. Does it hallucinate less/more?
4. Is it safe?

```python
test_prompts = [
    "Explain quantum computing to a 5-year-old",
    "Write a formal email declining a meeting",
    "Debug this Python code: [code here]",
    # Add domain-specific prompts
]

for prompt in test_prompts:
    response = generate(model, prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print("-" * 50)
```

### The Comparison Test

Always compare:
1. **Base model** (no fine-tuning)
2. **Fine-tuned model**
3. **Base model with few-shot examples**

If #3 beats #2, your fine-tuning didn't help — just use few-shot prompting!

---

## Common Pitfalls and Solutions

### 1. Catastrophic Forgetting

**Problem**: Model forgets general knowledge after fine-tuning.

**Solution**:
- Use LoRA instead of full fine-tuning
- Mix in general data (10-20%) with your task data
- Use lower learning rate

### 2. Overfitting

**Problem**: Model memorizes training data, doesn't generalize.

**Signs**:
- Training loss drops but eval loss increases
- Model outputs training examples verbatim

**Solution**:
- More diverse training data
- Higher LoRA dropout (0.1-0.2)
- Fewer epochs
- Regularization (weight decay)

### 3. Training Instability

**Problem**: Loss spikes or goes NaN.

**Solution**:
- Lower learning rate
- Gradient clipping (max_grad_norm=0.3)
- Warmup period
- Check for data issues (NaN, very long sequences)

### 4. Wrong Chat Template

**Problem**: Model outputs garbage or doesn't follow instructions.

**Solution**:
- Use the correct chat template for your base model
- Check tokenizer's `chat_template` attribute
- Ensure consistent formatting between train and inference

```python
# Check the model's expected format
print(tokenizer.chat_template)

# Apply it correctly
formatted = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
```

### 5. Insufficient Data

**Problem**: Model doesn't learn the task.

**Solution**:
- More epochs (but watch for overfitting)
- Data augmentation (paraphrase, back-translate)
- Start with a model closer to your domain
- Consider RAG instead

> **Did You Know?** The phenomenon of catastrophic forgetting has plagued neural networks since the 1980s. It's why continual learning (learning new tasks without forgetting old ones) remains an open research problem. LoRA's genius is that by keeping most weights frozen, it naturally prevents catastrophic forgetting — the base model's knowledge stays intact.

---

## Cost Analysis

Let's do the math on fine-tuning costs.

### Cloud GPU Costs

| GPU | VRAM | Cost/hour | Can Train |
|-----|------|-----------|-----------|
| T4 | 16GB | $0.50 | 7B with QLoRA |
| A10G | 24GB | $1.00 | 7B with QLoRA |
| A100 40GB | 40GB | $4.00 | 13B with QLoRA |
| A100 80GB | 80GB | $8.00 | 70B with QLoRA |

### Time Estimates

For fine-tuning Llama 3.1 8B on 10,000 examples:

| Setup | Time | Cost |
|-------|------|------|
| 1x A10G | ~4 hours | $4 |
| 1x A100 | ~1.5 hours | $6 |
| 4x A100 | ~25 min | $13 |

**Key insight**: More GPUs = faster but not cheaper. Optimize for your constraints.

### Comparison: Fine-tuning vs RAG vs API

For 10,000 queries/month:

| Approach | Setup Cost | Per-Query Cost | Monthly Cost |
|----------|------------|----------------|--------------|
| **Fine-tuned local** | $5-50 | ~$0 | ~$20 (hosting) |
| **RAG with API** | $0 | $0.01-0.05 | $100-500 |
| **API few-shot** | $0 | $0.02-0.10 | $200-1000 |

Fine-tuning wins when you have high volume and stable requirements.

---

## Deployment Options

### Option 1: Hugging Face Inference Endpoints

Easiest deployment — just upload your model:

```python
# Push to Hub
model.push_to_hub("your-username/my-finetuned-model")

# Deploy as endpoint (click in HF UI or use API)
```

Cost: $0.60-4.00/hour depending on GPU

### Option 2: Self-hosted with vLLM

For cost optimization at scale:

```bash
# Install vLLM
pip install vllm

# Run server
python -m vllm.entrypoints.openai.api_server \
    --model your-model-path \
    --tensor-parallel-size 1
```

vLLM optimizations:
- **PagedAttention**: 24x throughput improvement
- **Continuous batching**: Efficient request handling
- **OpenAI-compatible API**: Drop-in replacement

### Option 3: Ollama for Local Deployment

For personal/team use:

```bash
# Create Modelfile
cat > Modelfile << 'EOF'
FROM ./merged-model
PARAMETER temperature 0.7
SYSTEM "You are a helpful assistant fine-tuned for..."
EOF

# Create and run
ollama create my-model -f Modelfile
ollama run my-model
```

---

## Quiz: Test Your Understanding

**Q1**: When should you use fine-tuning instead of RAG?

<details>
<summary>Answer</summary>

Use fine-tuning when you need to change the model's **behavior** or **style**, not its knowledge:
- Consistent output format
- Domain-specific language/jargon
- New task types
- Speed optimization (no retrieval latency)
- Cost optimization at high volume

Use RAG when you need to add **knowledge** that changes frequently or is very large.

</details>

**Q2**: Why does LoRA work with such low rank (r=8 or r=16)?

<details>
<summary>Answer</summary>

The weight updates during fine-tuning lie in a low-dimensional subspace. The model doesn't need to learn entirely new representations — it just needs to **adapt** existing ones. This adaptation is intrinsically low-rank because:

1. The base model already has rich representations
2. Fine-tuning tasks share structure with pretraining
3. The manifold of "useful adaptations" is low-dimensional

Empirically, r=8-16 captures 99%+ of the fine-tuning benefit for most tasks.

</details>

**Q3**: A 7B model has parameters stored in FP16. You apply QLoRA with 4-bit quantization. How much memory is saved?

<details>
<summary>Answer</summary>

**Original (FP16)**: 7B × 2 bytes = 14 GB

**QLoRA (4-bit)**: 7B × 0.5 bytes = 3.5 GB (for base model)
Plus LoRA adapters in FP16: ~50-100 MB

**Total**: ~3.6 GB vs 14 GB

**Savings**: 14 - 3.6 = **10.4 GB (~75% reduction)**

This is what makes QLoRA trainable on consumer GPUs!

</details>

**Q4**: Your fine-tuned model achieves low training loss but outputs training examples verbatim during inference. What's happening and how do you fix it?

<details>
<summary>Answer</summary>

This is **overfitting** — the model memorized training data instead of learning the underlying patterns.

Fixes:
1. **More diverse training data**: Add variations, paraphrases
2. **Fewer epochs**: Stop earlier (use validation loss)
3. **Higher dropout**: Increase `lora_dropout` to 0.15-0.2
4. **Weight decay**: Add `weight_decay=0.01` to training args
5. **Early stopping**: Stop when eval loss starts increasing
6. **Regularization**: Consider adding KL divergence from base model

</details>

**Q5**: You're fine-tuning for a customer service chatbot. The model keeps forgetting general knowledge (like basic math). What went wrong?

<details>
<summary>Answer</summary>

This is **catastrophic forgetting** — the model lost general capabilities while learning the new task.

Solutions:
1. **Use LoRA instead of full fine-tuning**: Keeps base weights frozen
2. **Mix in general data**: Add 10-20% general instruction data to your training set
3. **Lower learning rate**: Reduces how much weights change
4. **Fewer epochs**: Less time to forget
5. **Larger model**: Bigger models are more resistant to forgetting

LoRA naturally prevents most forgetting since only the small adapter weights are modified.

</details>

---

## Summary

You've learned:

1. **When to fine-tune** vs RAG vs prompting — behavior change needs fine-tuning
2. **LoRA** decomposes weight updates into low-rank matrices (128× parameter reduction)
3. **QLoRA** adds 4-bit quantization (75% memory reduction)
4. **Data quality** is everything — clean, diverse, properly formatted
5. **Evaluation** must compare fine-tuned vs base vs few-shot
6. **Common pitfalls**: forgetting, overfitting, wrong templates
7. **Deployment** options: HF endpoints, vLLM, Ollama

The key insight: Fine-tuning is now accessible to everyone. With QLoRA, you can fine-tune a 7B model on a single gaming GPU in a few hours for a few dollars.

---

## Further Reading

### Essential Resources

1. **LoRA Paper**: "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., 2021)
   - https://arxiv.org/abs/2106.09685

2. **QLoRA Paper**: "QLoRA: Efficient Finetuning of Quantized LLMs" (Dettmers et al., 2023)
   - https://arxiv.org/abs/2305.14314

3. **Hugging Face PEFT**: Official documentation
   - https://huggingface.co/docs/peft

4. **TRL Library**: For SFT, RLHF, DPO
   - https://huggingface.co/docs/trl

### Advanced Topics

1. **DoRA**: Weight-Decomposed Low-Rank Adaptation (2024)
2. **LongLoRA**: Efficient fine-tuning for long contexts
3. **NEFTune**: Noisy embedding fine-tuning
4. **ORPO**: Odds Ratio Preference Optimization

---

## Next Steps

Move on to **Module 33: Diffusion Models & Image Generation** where you'll learn:
- How Stable Diffusion works
- DDPM and DDIM schedulers
- LoRA for image models
- Text-to-image from scratch

Or explore the deliverable to:
- Fine-tune Llama 3.1 on a custom dataset
- Compare LoRA ranks and configurations
- Evaluate fine-tuned models
- Calculate cost/benefit

---

_Last updated: 2025-11-27_
_Status: Complete_
