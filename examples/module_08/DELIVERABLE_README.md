# Module 08 Deliverable: Sampling Strategy Tuner

**Optimize AI model sampling parameters for different tasks**

## Features
- Test different temperature settings
- Experiment with top_p values
- Compare sampling strategies
- Find optimal parameters for tasks
- Generate tuning reports

## Quick Start
```bash
python deliverable_sampling_tuner.py demo1  # List presets
python deliverable_sampling_tuner.py demo2  # Test a preset
python deliverable_sampling_tuner.py demo3  # Compare presets
```

## Preset Configurations
- **Creative** (temp=0.9, top_p=0.95) - For creative writing, brainstorming
- **Balanced** (temp=0.7, top_p=0.9) - General-purpose tasks
- **Precise** (temp=0.3, top_p=0.85) - Code generation, translation
- **Deterministic** (temp=0.0, top_p=1.0) - Factual Q&A, consistency

## Task Types
- Creative Writing (optimal: temp=0.8, top_p=0.95)
- Code Generation (optimal: temp=0.2, top_p=0.85)
- Factual Q&A (optimal: temp=0.1, top_p=0.9)
- Brainstorming (optimal: temp=0.9, top_p=0.95)
- Translation (optimal: temp=0.3, top_p=0.9)

## Scoring Metrics
- **Diversity Score**: Unique word ratio (0-100)
- **Quality Score**: Heuristic-based completeness check (0-100)
- **Consistency Score**: Variance across multiple runs (placeholder)

**Time**: ~2 hours | **Lines**: 400+ | **Author**: Neural Dojo
