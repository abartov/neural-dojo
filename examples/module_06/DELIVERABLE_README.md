# Module 06 Deliverable: Model Comparison Benchmark Suite

**Deep model performance analysis tool**

## Features
- Compare 4 models: Claude Sonnet/Opus, GPT-4o/3.5
- 5 standardized tasks: simple code, complex algorithms, explanation, debugging, optimization
- Metrics: quality score, latency, cost, tokens
- Automated report generation

## Quick Start
```bash
python deliverable_model_benchmark.py demo1  # List models
python deliverable_model_benchmark.py demo2  # Run benchmark
python deliverable_model_benchmark.py demo3  # Generate report
```

## Models Supported
- Claude Sonnet 4.5 ($3/M in, $15/M out)
- Claude Opus 4 ($15/M in, $75/M out)
- GPT-4o ($5/M in, $15/M out)
- GPT-3.5 Turbo ($0.50/M in, $1.50/M out)

## Output
- Quality scores (0-100 based on keyword detection)
- Latency measurements (seconds)
- Cost calculations (USD)
- Markdown comparison reports

**Time**: ~3 hours | **Lines**: 450+ | **Author**: Neural Dojo
