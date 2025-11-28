# Module 42 Deliverable: LLM Evaluation Toolkit

**Comprehensive toolkit for evaluating LLM systems with benchmarks, LLM-as-Judge, A/B testing, and custom pipelines.**

## Features

- **Benchmark Evaluation**: 24+ MMLU-style questions across 6 categories
- **LLM-as-Judge**: Compare responses with position bias mitigation
- **A/B Testing**: Statistical framework with confidence intervals and p-values
- **Custom Pipelines**: Build multi-metric evaluation pipelines
- **Report Generation**: Comprehensive evaluation reports

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run benchmark evaluation
python deliverable_llm_evaluation_toolkit.py demo1

# Test LLM-as-Judge
python deliverable_llm_evaluation_toolkit.py demo2

# Run A/B testing
python deliverable_llm_evaluation_toolkit.py demo3

# Custom evaluation pipeline
python deliverable_llm_evaluation_toolkit.py demo4

# Full evaluation report
python deliverable_llm_evaluation_toolkit.py demo5
```

## Benchmark Categories

| Category | Questions | Description |
|----------|-----------|-------------|
| Knowledge | 8 | MMLU-style factual questions |
| Reasoning | 4 | Logic and deduction problems |
| Math | 4 | GSM8K-style word problems |
| Common Sense | 3 | HellaSwag-style completion |
| Truthfulness | 3 | TruthfulQA-style misconceptions |
| Safety | 2 | Helpful vs harmful decisions |

## Evaluation Framework

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  Benchmark   │    │  LLM-as-     │    │   A/B Test   │              │
│  │  Evaluator   │    │  Judge       │    │  Framework   │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                   │                   │                       │
│         ▼                   ▼                   ▼                       │
│  ┌──────────────────────────────────────────────────────┐              │
│  │              REPORT GENERATOR                         │              │
│  └──────────────────────────────────────────────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## LLM-as-Judge Position Debiasing

The toolkit implements position bias mitigation:

```
Standard Judging:          Position-Debiased:
├── Run once               ├── Run with A-first
├── May favor position 1   ├── Run with B-first
└── Single result          ├── Compare results
                           └── Aggregate (or flag disagreement)
```

## Statistical Analysis

A/B Testing provides:
- **Win Rate**: Percentage of comparisons won
- **Confidence Intervals**: Wilson score intervals (95%)
- **P-value**: Binomial test against 50% null hypothesis
- **Sample Size Calculator**: Plan experiments correctly

```
Sample Size Requirements:
├── 55% vs 45% detection: ~392 samples
├── 60% vs 40% detection: ~98 samples
└── 65% vs 35% detection: ~44 samples
```

## Custom Pipeline Example

```python
from deliverable_llm_evaluation_toolkit import (
    EvaluationPipeline, EvalCase,
    exact_match_evaluator, length_evaluator, keyword_evaluator
)

# Create pipeline
pipeline = EvaluationPipeline("My Pipeline")
pipeline.add_evaluator(exact_match_evaluator)
pipeline.add_evaluator(length_evaluator)
pipeline.add_evaluator(keyword_evaluator)

# Define test cases
cases = [
    EvalCase(
        id="q1",
        prompt="What is 2+2?",
        expected="4",
        metadata={"keywords": ["4", "four"]}
    )
]

# Run evaluation
summary = pipeline.run(my_model_fn, cases)
```

## Sample Output

```
======================================================================
LLM EVALUATION REPORT
======================================================================

📋 Model: My LLM v1.0
📅 Date: 2025-11-28

📊 BENCHMARK RESULTS
   Accuracy: 87.5%

   By Category:
   • knowledge: 100.0%
   • reasoning: 75.0%
   • math: 100.0%

⚔️ A/B TEST RESULTS
   Model A Wins: 60
   Model B Wins: 40
   Win Rate: 60.0%
   P-value: 0.0456
   Significant: ✅ YES

======================================================================
```

## File Storage

Results are stored in `.llm_eval_toolkit/`:
- `evaluation_results.json`: Raw evaluation data
- `benchmarks/`: Custom benchmark definitions
- `reports/`: Generated evaluation reports

**Time**: ~4 hours | **Lines**: 1,600+ | **Author**: Neural Dojo
