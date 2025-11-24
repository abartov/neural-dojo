# Module 13 Examples: RAG vs Fine-tuning Trade-offs

This directory contains working code examples for Module 13: RAG vs Fine-tuning Trade-offs.

## Overview

These examples help you make data-driven decisions about when to use RAG, fine-tuning, or a hybrid approach for your AI projects.

## Prerequisites

```bash
# No additional dependencies required!
# These examples use only Python standard library
python --version  # Python 3.10+
```

## Examples

### Example 1: Decision Framework (`01_decision_framework.py`)

**What it does**: Interactive framework to analyze your use case and recommend an approach.

**Run**:
```bash
python 01_decision_framework.py

# Interactive mode for custom analysis
python 01_decision_framework.py --interactive
```

**You'll learn**:
- How to evaluate knowledge frequency
- When citations matter
- Style vs knowledge requirements
- Training data considerations
- Latency impact on approach selection

**Key Decision Factors**:
| Factor | RAG Favors | Fine-tuning Favors |
|--------|------------|-------------------|
| Knowledge updates | Frequent | Rare |
| Citations needed | Yes | No |
| Style requirements | Low | High |
| Training data | Limited | Abundant |
| Latency | Flexible | Strict |

**Example output**:
```
RECOMMENDATION: Hybrid (RAG + LoRA)
Confidence: 78%

REASONING:
1. Knowledge changes weekly - RAG provides dynamic updates
2. Citations required - RAG provides natural source attribution
3. Critical style requirements - fine-tuning ensures consistency
4. 200 examples sufficient for LoRA

Estimated Monthly Cost: $2,850
```

---

### Example 2: Cost Analysis (`02_cost_analysis.py`)

**What it does**: Detailed cost calculations for RAG, fine-tuning, and hybrid approaches.

**Run**:
```bash
python 02_cost_analysis.py           # All scenarios
python 02_cost_analysis.py startup   # 10K queries/month
python 02_cost_analysis.py growth    # 100K queries/month
python 02_cost_analysis.py scale     # 1M queries/month
python 02_cost_analysis.py enterprise # 10M queries/month
```

**You'll learn**:
- Real pricing for different approaches
- Break-even analysis
- Cost optimization strategies
- Scale-dependent recommendations

**2025 Pricing Used**:
| Component | Cost |
|-----------|------|
| GPT-4o Input | $2.50/1M tokens |
| GPT-4o Output | $10.00/1M tokens |
| Fine-tuned Input | $3.75/1M tokens |
| Fine-tuned Output | $15.00/1M tokens |
| Embeddings | $0.02/1M tokens |
| Vector DB | $0-300/month |

**Example output**:
```
GROWTH SCENARIO
100,000 queries/month | 500 training examples

Approach                   Monthly      One-time     Year 1 Total
------------------------------------------------------------------
RAG                       $2,572.00       $0.00      $30,864.00
Fine-tuning               $5,437.50     $125.00      $65,375.00
Hybrid (RAG + LoRA)       $2,572.00     $100.00      $30,964.00

Winner (Year 1): RAG
Potential Savings: $34,411.00/year
```

---

## Quick Start

```bash
# Run decision framework with example scenarios
python 01_decision_framework.py

# Compare costs at different scales
python 02_cost_analysis.py all

# Interactive analysis for your specific use case
python 01_decision_framework.py --interactive
```

---

## Key Takeaways

### The Fundamental Distinction

```
RAG = Dynamic Knowledge
- Facts that change
- External data sources
- Citations required

Fine-tuning = Behavior Modification
- Style and tone
- Reasoning patterns
- Domain expertise
```

### When to Use What

**RAG**:
- Knowledge changes frequently (weekly or faster)
- Citations/attribution required
- Large document corpus
- Limited training data

**Fine-tuning**:
- Specific style is critical
- Knowledge is stable
- Strict latency requirements (<100ms)
- Abundant high-quality training data

**Hybrid**:
- Need both dynamic knowledge AND specific behavior
- Building production systems
- Want best quality at reasonable cost

### Cost Insights

1. **Fine-tuned models cost 1.5x per token** (GPT-4o pricing)
2. **RAG adds minimal overhead** (~$70-300/month for vector DB)
3. **LoRA training is cheap** ($50-200 one-time)
4. **Hybrid often wins** on both cost AND quality
5. **At scale**, negotiate enterprise pricing (40-60% discounts)

---

## Practical Exercises

After running the examples:

1. **Analyze your project**:
   - Run `--interactive` mode with your actual requirements
   - Document the recommendation and reasoning

2. **Calculate ROI**:
   - Compare your current approach to the recommendation
   - Calculate potential savings

3. **Design a hybrid architecture**:
   - Identify what should be RAG (knowledge)
   - Identify what should be fine-tuned (behavior)
   - Plan the integration

---

## Common Gotchas

1. **Don't fine-tune for knowledge** - Use RAG for facts, fine-tune for style
2. **Don't ignore latency** - RAG adds 100-500ms overhead
3. **Don't underestimate training data needs** - <50 examples rarely work
4. **Don't forget retraining costs** - Knowledge changes mean RAG updates
5. **Don't skip cost analysis** - Fine-tuned inference is expensive at scale

---

## Further Reading

- Module 13 Theory: `docs/curriculum/notes/module_13_rag_vs_finetuning.md`
- LoRA Paper: "LoRA: Low-Rank Adaptation of Large Language Models"
- QLoRA Paper: "QLoRA: Efficient Finetuning of Quantized LLMs"
- RAG Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"

---

## Next Steps

After mastering these trade-offs:
- **Module 14**: LangChain Fundamentals - Build sophisticated RAG systems
- **Module 26**: Fine-tuning Large Language Models - Hands-on LoRA/QLoRA

---

**Neural Dojo - Make data-driven AI decisions! **

---

_Last updated: 2025-11-24_
