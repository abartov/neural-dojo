#!/usr/bin/env python3
"""
Module 32 Deliverable: Fine-tuning Toolkit

A comprehensive toolkit for fine-tuning LLMs with LoRA and QLoRA.
Demonstrates configuration, dataset preparation, cost estimation,
and evaluation - all the key concepts for practical fine-tuning.

Features:
- LoRA configuration builder with parameter analysis
- Dataset validator and formatter
- Memory and cost estimator
- Training configuration generator
- Simulated fine-tuning demonstration
- Evaluation pipeline

Usage:
    python deliverable_finetuning_toolkit.py demo1  # LoRA configuration analysis
    python deliverable_finetuning_toolkit.py demo2  # Dataset preparation
    python deliverable_finetuning_toolkit.py demo3  # Cost and memory estimation
    python deliverable_finetuning_toolkit.py demo4  # Simulated fine-tuning
    python deliverable_finetuning_toolkit.py demo5  # Generate report

Author: Neural Dojo
Date: 2025-11-27
"""

import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


# =============================================================================
# Configuration Classes
# =============================================================================

class QuantizationType(Enum):
    """Supported quantization types."""
    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    NF4 = "nf4"  # QLoRA's NormalFloat4


class TaskType(Enum):
    """Fine-tuning task types."""
    CAUSAL_LM = "causal_lm"
    SEQ2SEQ = "seq2seq"
    CLASSIFICATION = "classification"


@dataclass
class ModelConfig:
    """Configuration for a base model."""
    name: str
    parameters_billions: float
    hidden_size: int
    num_layers: int
    num_attention_heads: int
    vocab_size: int
    context_length: int
    license: str = "Open"

    @property
    def total_parameters(self) -> int:
        """Total parameters as integer."""
        return int(self.parameters_billions * 1e9)

    def memory_footprint(self, dtype_bytes: int = 2) -> float:
        """Memory in GB for given dtype (2=FP16, 4=FP32)."""
        return (self.total_parameters * dtype_bytes) / (1024**3)


@dataclass
class LoRAConfig:
    """LoRA adapter configuration."""
    r: int = 16                      # Rank
    lora_alpha: int = 32             # Scaling factor
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "v_proj", "k_proj", "o_proj"
    ])
    bias: str = "none"
    task_type: TaskType = TaskType.CAUSAL_LM

    def calculate_trainable_params(self, model: ModelConfig) -> int:
        """Calculate number of trainable parameters."""
        # Each target module gets two LoRA matrices: A (r x d) and B (d x r)
        d = model.hidden_size
        params_per_module = 2 * self.r * d
        num_modules = len(self.target_modules) * model.num_layers
        return params_per_module * num_modules

    def compression_ratio(self, model: ModelConfig) -> float:
        """How much we compress vs full fine-tuning."""
        return model.total_parameters / self.calculate_trainable_params(model)


@dataclass
class QLoRAConfig(LoRAConfig):
    """QLoRA configuration extending LoRA with quantization."""
    quantization: QuantizationType = QuantizationType.NF4
    double_quantization: bool = True
    compute_dtype: str = "bfloat16"


@dataclass
class TrainingConfig:
    """Training hyperparameters."""
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    lr_scheduler: str = "cosine"
    warmup_ratio: float = 0.03
    max_grad_norm: float = 0.3
    weight_decay: float = 0.01
    max_seq_length: int = 512
    fp16: bool = True
    gradient_checkpointing: bool = True

    @property
    def effective_batch_size(self) -> int:
        """Effective batch size including gradient accumulation."""
        return self.batch_size * self.gradient_accumulation_steps


@dataclass
class DatasetStats:
    """Statistics about a training dataset."""
    total_examples: int
    avg_input_length: float
    avg_output_length: float
    max_length: int
    quality_score: float  # 0-100
    issues: List[str] = field(default_factory=list)


# =============================================================================
# Predefined Models
# =============================================================================

MODELS = {
    "llama-3.1-8b": ModelConfig(
        name="Llama 3.1 8B",
        parameters_billions=8.0,
        hidden_size=4096,
        num_layers=32,
        num_attention_heads=32,
        vocab_size=128256,
        context_length=128000,
        license="Llama 3.1 License"
    ),
    "mistral-7b": ModelConfig(
        name="Mistral 7B",
        parameters_billions=7.3,
        hidden_size=4096,
        num_layers=32,
        num_attention_heads=32,
        vocab_size=32000,
        context_length=32768,
        license="Apache 2.0"
    ),
    "phi-3-mini": ModelConfig(
        name="Phi-3 Mini 3.8B",
        parameters_billions=3.8,
        hidden_size=3072,
        num_layers=32,
        num_attention_heads=32,
        vocab_size=32064,
        context_length=128000,
        license="MIT"
    ),
    "qwen2-7b": ModelConfig(
        name="Qwen2 7B",
        parameters_billions=7.6,
        hidden_size=3584,
        num_layers=28,
        num_attention_heads=28,
        vocab_size=151936,
        context_length=131072,
        license="Apache 2.0"
    ),
    "gemma-2-9b": ModelConfig(
        name="Gemma 2 9B",
        parameters_billions=9.2,
        hidden_size=3584,
        num_layers=42,
        num_attention_heads=16,
        vocab_size=256000,
        context_length=8192,
        license="Gemma License"
    ),
}


# =============================================================================
# GPU Configurations
# =============================================================================

@dataclass
class GPUConfig:
    """GPU specification."""
    name: str
    vram_gb: int
    cost_per_hour: float
    provider: str = "AWS/GCP"


GPUS = {
    "t4": GPUConfig("NVIDIA T4", 16, 0.50),
    "a10g": GPUConfig("NVIDIA A10G", 24, 1.00),
    "l4": GPUConfig("NVIDIA L4", 24, 0.80),
    "a100-40": GPUConfig("NVIDIA A100 40GB", 40, 4.00),
    "a100-80": GPUConfig("NVIDIA A100 80GB", 80, 8.00),
    "h100": GPUConfig("NVIDIA H100", 80, 12.00),
    "rtx-4090": GPUConfig("RTX 4090 (local)", 24, 0.00, "Local"),
    "rtx-3090": GPUConfig("RTX 3090 (local)", 24, 0.00, "Local"),
}


# =============================================================================
# Core Analysis Functions
# =============================================================================

def analyze_lora_config(
    model: ModelConfig,
    lora: LoRAConfig,
    quantization: QuantizationType = QuantizationType.NONE
) -> Dict[str, Any]:
    """
    Analyze LoRA configuration for a given model.

    Returns detailed breakdown of parameters, memory, and efficiency.
    """
    trainable = lora.calculate_trainable_params(model)
    compression = lora.compression_ratio(model)

    # Memory estimation
    dtype_bytes = {
        QuantizationType.NONE: 2,  # FP16
        QuantizationType.INT8: 1,
        QuantizationType.INT4: 0.5,
        QuantizationType.NF4: 0.5,
    }[quantization]

    base_memory = model.memory_footprint(dtype_bytes)

    # LoRA adapters in FP16
    lora_memory = (trainable * 2) / (1024**3)

    # Optimizer states (Adam: 2x for momentum and variance)
    optimizer_memory = (trainable * 2 * 2) / (1024**3)

    # Activations (rough estimate based on batch size and sequence length)
    activation_memory = 2.0  # Approximate GB

    total_training_memory = base_memory + lora_memory + optimizer_memory + activation_memory

    return {
        "model_name": model.name,
        "model_parameters": f"{model.parameters_billions:.1f}B",
        "lora_rank": lora.r,
        "target_modules": lora.target_modules,
        "trainable_parameters": trainable,
        "trainable_percentage": f"{100 * trainable / model.total_parameters:.4f}%",
        "compression_ratio": f"{compression:.0f}x",
        "quantization": quantization.value,
        "memory_breakdown": {
            "base_model_gb": f"{base_memory:.2f}",
            "lora_adapters_gb": f"{lora_memory:.4f}",
            "optimizer_states_gb": f"{optimizer_memory:.4f}",
            "activations_gb": f"{activation_memory:.2f}",
            "total_training_gb": f"{total_training_memory:.2f}",
        },
        "recommended_gpu": recommend_gpu(total_training_memory),
    }


def recommend_gpu(required_memory_gb: float) -> str:
    """Recommend smallest GPU that can handle the workload."""
    for gpu_id, gpu in sorted(GPUS.items(), key=lambda x: x[1].vram_gb):
        # Leave 20% headroom
        if gpu.vram_gb * 0.8 >= required_memory_gb:
            return f"{gpu.name} ({gpu.vram_gb}GB) - ${gpu.cost_per_hour:.2f}/hr"
    return "Multiple GPUs required (A100 80GB x2+)"


def estimate_training_cost(
    model: ModelConfig,
    dataset_size: int,
    training: TrainingConfig,
    gpu: GPUConfig
) -> Dict[str, Any]:
    """
    Estimate training time and cost.
    """
    # Rough tokens per second estimation (varies widely)
    tokens_per_second = {
        "NVIDIA T4": 500,
        "NVIDIA A10G": 800,
        "NVIDIA L4": 900,
        "NVIDIA A100 40GB": 2000,
        "NVIDIA A100 80GB": 2500,
        "NVIDIA H100": 4000,
        "RTX 4090 (local)": 1500,
        "RTX 3090 (local)": 1000,
    }.get(gpu.name, 1000)

    # Total tokens to process
    avg_tokens = training.max_seq_length * 0.6  # Assume 60% fill rate
    total_tokens = dataset_size * avg_tokens * training.num_epochs

    # Time estimation
    training_seconds = total_tokens / tokens_per_second
    training_hours = training_seconds / 3600

    # Cost
    total_cost = training_hours * gpu.cost_per_hour

    # Steps
    total_steps = (dataset_size * training.num_epochs) / training.effective_batch_size

    return {
        "dataset_size": dataset_size,
        "epochs": training.num_epochs,
        "effective_batch_size": training.effective_batch_size,
        "total_steps": int(total_steps),
        "estimated_tokens": int(total_tokens),
        "gpu": gpu.name,
        "tokens_per_second": tokens_per_second,
        "estimated_hours": f"{training_hours:.2f}",
        "cost_per_hour": f"${gpu.cost_per_hour:.2f}",
        "total_cost": f"${total_cost:.2f}",
    }


# =============================================================================
# Dataset Processing
# =============================================================================

def validate_dataset(examples: List[Dict]) -> DatasetStats:
    """
    Validate and analyze a training dataset.
    """
    issues = []
    input_lengths = []
    output_lengths = []

    valid_count = 0
    for i, ex in enumerate(examples):
        # Check required fields
        if "instruction" not in ex and "messages" not in ex:
            issues.append(f"Example {i}: Missing instruction/messages field")
            continue

        if "output" not in ex and "messages" not in ex:
            issues.append(f"Example {i}: Missing output field")
            continue

        # Get text lengths
        if "messages" in ex:
            # Conversation format
            user_text = " ".join(
                m["content"] for m in ex["messages"]
                if m["role"] == "user"
            )
            assistant_text = " ".join(
                m["content"] for m in ex["messages"]
                if m["role"] == "assistant"
            )
        else:
            # Instruction format
            user_text = ex.get("instruction", "") + ex.get("input", "")
            assistant_text = ex.get("output", "")

        input_lengths.append(len(user_text))
        output_lengths.append(len(assistant_text))

        # Quality checks
        if len(assistant_text) < 20:
            issues.append(f"Example {i}: Very short output ({len(assistant_text)} chars)")

        if len(user_text) < 5:
            issues.append(f"Example {i}: Very short input ({len(user_text)} chars)")

        valid_count += 1

    # Calculate quality score
    quality_score = 100
    quality_score -= min(30, len(issues) * 2)  # Deduct for issues
    if valid_count < 100:
        quality_score -= 20  # Deduct for small dataset
    if len(set(str(e) for e in examples)) < len(examples) * 0.9:
        quality_score -= 15  # Deduct for duplicates
        issues.append("Dataset may contain duplicates")

    return DatasetStats(
        total_examples=len(examples),
        avg_input_length=sum(input_lengths) / len(input_lengths) if input_lengths else 0,
        avg_output_length=sum(output_lengths) / len(output_lengths) if output_lengths else 0,
        max_length=max(input_lengths + output_lengths) if input_lengths else 0,
        quality_score=max(0, quality_score),
        issues=issues[:10],  # Limit to 10 issues
    )


def format_for_training(
    examples: List[Dict],
    chat_template: str = "chatml"
) -> List[str]:
    """
    Format examples using specified chat template.
    """
    templates = {
        "chatml": """<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
{assistant}<|im_end|>""",

        "llama": """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{assistant}<|eot_id|>""",

        "alpaca": """### Instruction:
{user}

### Response:
{assistant}""",
    }

    template = templates.get(chat_template, templates["chatml"])
    formatted = []

    for ex in examples:
        if "messages" in ex:
            system = ""
            user = ""
            assistant = ""
            for msg in ex["messages"]:
                if msg["role"] == "system":
                    system = msg["content"]
                elif msg["role"] == "user":
                    user = msg["content"]
                elif msg["role"] == "assistant":
                    assistant = msg["content"]
        else:
            system = "You are a helpful assistant."
            user = ex.get("instruction", "")
            if ex.get("input"):
                user += "\n\n" + ex["input"]
            assistant = ex.get("output", "")

        text = template.format(system=system, user=user, assistant=assistant)
        formatted.append(text)

    return formatted


def generate_synthetic_dataset(
    task: str,
    num_examples: int = 100
) -> List[Dict]:
    """
    Generate synthetic training data for demonstration.
    """
    random.seed(42)

    if task == "customer_service":
        templates = [
            ("How do I reset my password?", "To reset your password, visit our login page and click 'Forgot Password'. Enter your email and follow the instructions sent to your inbox."),
            ("What are your business hours?", "Our customer service team is available Monday through Friday, 9 AM to 6 PM EST. For urgent matters, use our 24/7 chat support."),
            ("Can I get a refund?", "Yes, we offer a 30-day money-back guarantee. To request a refund, go to your order history and click 'Request Refund'."),
            ("My order hasn't arrived", "I apologize for the delay. Let me look up your order. Please provide your order number and I'll check the shipping status immediately."),
            ("How do I cancel my subscription?", "You can cancel your subscription at any time from your account settings. Go to Settings > Subscription > Cancel. Your access will continue until the end of the billing period."),
        ]
    elif task == "code_review":
        templates = [
            ("Review this function for bugs", "I noticed several issues: 1) No input validation - add type checks. 2) Missing error handling for edge cases. 3) Consider using early returns for readability."),
            ("Is this code efficient?", "The current complexity is O(n²) due to nested loops. Consider using a hash map to achieve O(n) time complexity."),
            ("How can I improve this?", "Good structure, but I suggest: 1) Add docstrings for clarity. 2) Use more descriptive variable names. 3) Extract the logic into smaller functions."),
        ]
    else:  # general
        templates = [
            ("Explain this concept", "Let me break this down step by step. The core idea is that..."),
            ("Summarize the main points", "The key takeaways are: 1) First point... 2) Second point... 3) Third point..."),
            ("What should I do?", "Based on your situation, I recommend the following approach..."),
        ]

    examples = []
    for i in range(num_examples):
        instruction, output = random.choice(templates)
        # Add variation
        instruction = instruction + f" [variant {i}]"
        output = output + f" [Example #{i}]"
        examples.append({
            "instruction": instruction,
            "output": output
        })

    return examples


# =============================================================================
# Report Generation
# =============================================================================

def generate_report(
    model_key: str,
    lora: LoRAConfig,
    training: TrainingConfig,
    dataset_size: int,
    output_dir: Path
) -> str:
    """Generate a comprehensive fine-tuning analysis report."""
    model = MODELS[model_key]
    quantization = QuantizationType.NF4  # Default to QLoRA

    analysis = analyze_lora_config(model, lora, quantization)

    # Find best GPU
    required_memory = float(analysis["memory_breakdown"]["total_training_gb"])
    best_gpu = None
    for gpu in sorted(GPUS.values(), key=lambda x: x.vram_gb):
        if gpu.vram_gb * 0.8 >= required_memory:
            best_gpu = gpu
            break
    if not best_gpu:
        best_gpu = GPUS["a100-80"]

    cost_analysis = estimate_training_cost(model, dataset_size, training, best_gpu)

    report = f"""# Fine-tuning Analysis Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Model Configuration

| Property | Value |
|----------|-------|
| Base Model | {model.name} |
| Parameters | {model.parameters_billions:.1f}B |
| Hidden Size | {model.hidden_size} |
| Layers | {model.num_layers} |
| Context Length | {model.context_length:,} |
| License | {model.license} |

## LoRA Configuration

| Property | Value |
|----------|-------|
| Rank (r) | {lora.r} |
| Alpha | {lora.lora_alpha} |
| Dropout | {lora.lora_dropout} |
| Target Modules | {", ".join(lora.target_modules)} |
| Quantization | {quantization.value} |

## Parameter Analysis

| Metric | Value |
|--------|-------|
| Base Model Parameters | {model.total_parameters:,} |
| Trainable Parameters | {analysis["trainable_parameters"]:,} |
| Trainable Percentage | {analysis["trainable_percentage"]} |
| Compression Ratio | {analysis["compression_ratio"]} |

## Memory Requirements

| Component | Memory (GB) |
|-----------|-------------|
| Base Model ({quantization.value}) | {analysis["memory_breakdown"]["base_model_gb"]} |
| LoRA Adapters | {analysis["memory_breakdown"]["lora_adapters_gb"]} |
| Optimizer States | {analysis["memory_breakdown"]["optimizer_states_gb"]} |
| Activations (est.) | {analysis["memory_breakdown"]["activations_gb"]} |
| **Total Training** | **{analysis["memory_breakdown"]["total_training_gb"]}** |

**Recommended GPU**: {analysis["recommended_gpu"]}

## Training Configuration

| Property | Value |
|----------|-------|
| Epochs | {training.num_epochs} |
| Batch Size | {training.batch_size} |
| Gradient Accumulation | {training.gradient_accumulation_steps} |
| Effective Batch Size | {training.effective_batch_size} |
| Learning Rate | {training.learning_rate} |
| Max Sequence Length | {training.max_seq_length} |
| Gradient Checkpointing | {training.gradient_checkpointing} |

## Cost Estimation

| Metric | Value |
|--------|-------|
| Dataset Size | {cost_analysis["dataset_size"]:,} examples |
| Total Steps | {cost_analysis["total_steps"]:,} |
| Estimated Tokens | {cost_analysis["estimated_tokens"]:,} |
| GPU | {cost_analysis["gpu"]} |
| Processing Speed | {cost_analysis["tokens_per_second"]:,} tokens/sec |
| **Estimated Time** | **{cost_analysis["estimated_hours"]} hours** |
| **Estimated Cost** | **{cost_analysis["total_cost"]}** |

## Cost Comparison

| Approach | Setup Cost | Monthly Cost (10K queries) |
|----------|------------|---------------------------|
| Fine-tuned + Self-hosted | {cost_analysis["total_cost"]} | ~$20 (hosting) |
| RAG + API (GPT-4) | $0 | ~$300-500 |
| Few-shot API | $0 | ~$500-1000 |

## Recommendations

1. **Dataset**: Aim for at least 1,000 high-quality examples
2. **LoRA Rank**: Start with r=16, increase if underfitting
3. **Epochs**: 3-5 epochs, monitor validation loss
4. **Learning Rate**: 2e-4 for LoRA, lower for full fine-tuning
5. **Evaluation**: Always compare against base model + few-shot

---

*Generated by Neural Dojo Fine-tuning Toolkit*
"""

    return report


# =============================================================================
# Demo Functions
# =============================================================================

def demo1_lora_analysis():
    """Demo 1: Analyze LoRA configurations across different models and ranks."""
    print("\n" + "=" * 70)
    print("DEMO 1: LoRA Configuration Analysis")
    print("=" * 70)

    print("\n📊 Comparing LoRA ranks across different models...")
    print("-" * 70)

    # Test different ranks
    ranks = [4, 8, 16, 32, 64]

    for model_key in ["phi-3-mini", "mistral-7b", "llama-3.1-8b"]:
        model = MODELS[model_key]
        print(f"\n🤖 {model.name} ({model.parameters_billions}B parameters)")
        print("-" * 50)

        print(f"{'Rank':>6} | {'Trainable':>12} | {'%':>8} | {'Compression':>12} | {'Memory':>10}")
        print("-" * 60)

        for r in ranks:
            lora = LoRAConfig(r=r)
            analysis = analyze_lora_config(model, lora, QuantizationType.NF4)

            trainable = analysis["trainable_parameters"]
            pct = analysis["trainable_percentage"]
            compression = analysis["compression_ratio"]
            memory = analysis["memory_breakdown"]["total_training_gb"]

            print(f"{r:>6} | {trainable:>12,} | {pct:>8} | {compression:>12} | {memory:>10} GB")

    print("\n✅ Key Insights:")
    print("   - Higher rank = more parameters = more expressiveness")
    print("   - r=16 is a good default (0.08% trainable, 128x compression)")
    print("   - QLoRA (NF4) reduces base model memory by 75%")
    print("   - Even r=64 trains only ~0.3% of parameters")


def demo2_dataset_preparation():
    """Demo 2: Dataset validation and preparation."""
    print("\n" + "=" * 70)
    print("DEMO 2: Dataset Preparation and Validation")
    print("=" * 70)

    # Generate synthetic datasets
    tasks = ["customer_service", "code_review", "general"]

    for task in tasks:
        print(f"\n📂 Generating synthetic '{task}' dataset...")

        dataset = generate_synthetic_dataset(task, num_examples=100)

        # Validate
        stats = validate_dataset(dataset)

        print(f"\n   Dataset Statistics:")
        print(f"   ├── Total examples: {stats.total_examples}")
        print(f"   ├── Avg input length: {stats.avg_input_length:.0f} chars")
        print(f"   ├── Avg output length: {stats.avg_output_length:.0f} chars")
        print(f"   ├── Max length: {stats.max_length} chars")
        print(f"   └── Quality score: {stats.quality_score}/100")

        if stats.issues:
            print(f"\n   ⚠️ Issues found ({len(stats.issues)}):")
            for issue in stats.issues[:3]:
                print(f"      - {issue}")

    # Demonstrate formatting
    print("\n📝 Chat Template Formatting Examples:")
    print("-" * 50)

    sample = [{"instruction": "What is machine learning?",
               "output": "Machine learning is a subset of AI..."}]

    for template in ["chatml", "llama", "alpaca"]:
        formatted = format_for_training(sample, template)[0]
        print(f"\n{template.upper()} format:")
        print("-" * 30)
        # Show truncated version
        lines = formatted.split('\n')
        for line in lines[:8]:
            print(f"  {line[:60]}...")
        if len(lines) > 8:
            print(f"  ... ({len(lines) - 8} more lines)")

    print("\n✅ Key Insights:")
    print("   - Always validate dataset before training")
    print("   - Match chat template to base model")
    print("   - Quality > Quantity for fine-tuning data")


def demo3_cost_estimation():
    """Demo 3: Estimate training costs across different configurations."""
    print("\n" + "=" * 70)
    print("DEMO 3: Cost and Memory Estimation")
    print("=" * 70)

    training = TrainingConfig()

    print("\n💰 Cost Comparison Matrix:")
    print("-" * 70)

    dataset_sizes = [1000, 5000, 10000, 50000]
    models = ["phi-3-mini", "mistral-7b", "llama-3.1-8b"]

    print(f"\n{'Model':<20} | {'Dataset':>10} | {'GPU':>15} | {'Time':>10} | {'Cost':>10}")
    print("-" * 75)

    for model_key in models:
        model = MODELS[model_key]
        lora = LoRAConfig(r=16)
        analysis = analyze_lora_config(model, lora, QuantizationType.NF4)
        required_memory = float(analysis["memory_breakdown"]["total_training_gb"])

        # Find suitable GPU
        best_gpu = None
        for gpu in sorted(GPUS.values(), key=lambda x: x.vram_gb):
            if gpu.vram_gb * 0.8 >= required_memory:
                best_gpu = gpu
                break
        if not best_gpu:
            best_gpu = GPUS["a100-80"]

        for ds_size in dataset_sizes:
            estimate = estimate_training_cost(model, ds_size, training, best_gpu)
            print(f"{model.name:<20} | {ds_size:>10,} | {best_gpu.name:>15} | "
                  f"{estimate['estimated_hours']:>10} | {estimate['total_cost']:>10}")

    print("\n📊 GPU Options and Pricing:")
    print("-" * 50)

    for gpu_id, gpu in sorted(GPUS.items(), key=lambda x: x[1].cost_per_hour):
        print(f"  {gpu.name:<25} | {gpu.vram_gb:>3}GB | ${gpu.cost_per_hour:.2f}/hr | {gpu.provider}")

    print("\n✅ Key Insights:")
    print("   - Smaller models = cheaper training")
    print("   - Local GPUs (RTX 4090) = best value for regular use")
    print("   - A100 80GB needed for models >30B")
    print("   - Fine-tuning 7B model: $5-50 typical")


def demo4_simulated_training():
    """Demo 4: Simulate a fine-tuning run with progress tracking."""
    print("\n" + "=" * 70)
    print("DEMO 4: Simulated Fine-tuning Run")
    print("=" * 70)

    model = MODELS["mistral-7b"]
    lora = QLoRAConfig(r=16)
    training = TrainingConfig(num_epochs=3)

    print("\n🚀 Starting simulated fine-tuning...")
    print("-" * 50)

    print(f"\n   Model: {model.name}")
    print(f"   LoRA Rank: {lora.r}")
    print(f"   Quantization: {lora.quantization.value}")
    print(f"   Epochs: {training.num_epochs}")
    print(f"   Batch Size: {training.effective_batch_size}")

    # Simulate training
    num_steps = 100
    print(f"\n📈 Training Progress ({num_steps} simulated steps):")
    print("-" * 50)

    losses = []
    random.seed(42)

    # Simulate realistic loss curve
    for step in range(1, num_steps + 1):
        # Loss decreases with noise
        base_loss = 2.5 * math.exp(-step / 30) + 0.3
        noise = random.gauss(0, 0.05)
        loss = max(0.1, base_loss + noise)
        losses.append(loss)

        if step % 20 == 0 or step == 1:
            lr = training.learning_rate * (1 - step / num_steps)  # Linear decay simulation
            print(f"   Step {step:>3}/{num_steps} | Loss: {loss:.4f} | LR: {lr:.2e}")

    # Epoch markers
    print("\n📊 Epoch Summary:")
    epoch_size = num_steps // training.num_epochs
    for epoch in range(training.num_epochs):
        start_idx = epoch * epoch_size
        end_idx = (epoch + 1) * epoch_size
        epoch_losses = losses[start_idx:end_idx]
        avg_loss = sum(epoch_losses) / len(epoch_losses)
        print(f"   Epoch {epoch + 1}: Avg Loss = {avg_loss:.4f}")

    # Final stats
    print(f"\n✅ Training Complete!")
    print(f"   Final Loss: {losses[-1]:.4f}")
    print(f"   Best Loss: {min(losses):.4f}")
    print(f"   Improvement: {(losses[0] - losses[-1]) / losses[0] * 100:.1f}%")

    print("\n🔧 Next Steps:")
    print("   1. Evaluate on held-out test set")
    print("   2. Compare with base model")
    print("   3. Test with domain-specific prompts")
    print("   4. Merge adapters if satisfied")


def demo5_generate_report():
    """Demo 5: Generate comprehensive analysis report."""
    print("\n" + "=" * 70)
    print("DEMO 5: Generate Analysis Report")
    print("=" * 70)

    # Create output directory
    output_dir = Path(".finetuning_toolkit")
    output_dir.mkdir(exist_ok=True)

    # Configuration
    model_key = "llama-3.1-8b"
    lora = LoRAConfig(r=16, lora_alpha=32)
    training = TrainingConfig()
    dataset_size = 5000

    print(f"\n📝 Generating report for {MODELS[model_key].name}...")

    report = generate_report(model_key, lora, training, dataset_size, output_dir)

    # Save report
    report_path = output_dir / "finetuning_report.md"
    report_path.write_text(report)

    print(f"\n✅ Report saved to: {report_path}")

    # Print preview
    print("\n📄 Report Preview:")
    print("-" * 50)
    lines = report.split('\n')
    for line in lines[:40]:
        print(line)
    print("\n... (see full report in file)")

    # Save configurations
    config_path = output_dir / "config.json"
    config = {
        "model": model_key,
        "lora": {
            "r": lora.r,
            "alpha": lora.lora_alpha,
            "dropout": lora.lora_dropout,
            "target_modules": lora.target_modules,
        },
        "training": {
            "epochs": training.num_epochs,
            "batch_size": training.batch_size,
            "learning_rate": training.learning_rate,
            "max_seq_length": training.max_seq_length,
        },
        "dataset_size": dataset_size,
        "generated_at": datetime.now().isoformat(),
    }
    config_path.write_text(json.dumps(config, indent=2))
    print(f"✅ Configuration saved to: {config_path}")


# =============================================================================
# Main Entry Point
# =============================================================================

def print_usage():
    """Print usage information."""
    print("""
Fine-tuning Toolkit - Module 32 Deliverable
============================================

Usage: python deliverable_finetuning_toolkit.py <command>

Commands:
  demo1   - LoRA configuration analysis (compare ranks and models)
  demo2   - Dataset preparation and validation
  demo3   - Cost and memory estimation
  demo4   - Simulated fine-tuning run
  demo5   - Generate comprehensive report
  all     - Run all demos

Examples:
  python deliverable_finetuning_toolkit.py demo1
  python deliverable_finetuning_toolkit.py all

Learn more: docs/curriculum/notes/module_32_finetuning_llms.md
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo1_lora_analysis,
        "demo2": demo2_dataset_preparation,
        "demo3": demo3_cost_estimation,
        "demo4": demo4_simulated_training,
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
