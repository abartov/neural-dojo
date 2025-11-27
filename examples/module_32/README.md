# Module 32: Fine-tuning Large Language Models

This directory contains examples and a toolkit for fine-tuning LLMs with LoRA and QLoRA.

## Contents

- `deliverable_finetuning_toolkit.py` - Comprehensive fine-tuning analysis toolkit
- `DELIVERABLE_README.md` - Detailed documentation for the deliverable

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python deliverable_finetuning_toolkit.py demo1  # LoRA analysis
python deliverable_finetuning_toolkit.py demo2  # Dataset prep
python deliverable_finetuning_toolkit.py demo3  # Cost estimation
python deliverable_finetuning_toolkit.py demo4  # Simulated training
python deliverable_finetuning_toolkit.py demo5  # Generate report
```

## Key Concepts

### LoRA (Low-Rank Adaptation)

LoRA decomposes weight updates into low-rank matrices:
- Original: W_new = W + ΔW (full rank)
- LoRA: W_new = W + BA (low rank)

This reduces trainable parameters by 100-500x!

### QLoRA

Combines LoRA with 4-bit quantization:
- Base model in 4-bit (NF4)
- LoRA adapters in FP16
- Result: Train 7B models on 8GB VRAM

### When to Fine-tune

- **DO**: Style/format, domain language, new behaviors
- **DON'T**: Adding knowledge (use RAG instead)

## Theory

See `docs/curriculum/notes/module_32_finetuning_llms.md` for complete theory.

## Requirements

- Python 3.10+
- No GPU required for toolkit demos
- For actual fine-tuning: See requirements.txt

## Dependencies

The toolkit has minimal dependencies (just Python stdlib).

For actual fine-tuning, you'd need:
- transformers
- peft
- bitsandbytes
- trl
- accelerate
