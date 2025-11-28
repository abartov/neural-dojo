# Module 43 Deliverable: ML DevOps Toolkit

**Comprehensive toolkit for ML DevOps including Git workflows, testing frameworks, and project templates.**

## Features

- **Git Workflow Helper**: ML-specific branch naming and commit conventions
- **Pre-commit Generator**: Generate configurations for ML projects
- **Data Quality Testing**: Test for missing values, imbalance, leakage
- **Model Quality Testing**: Test accuracy, latency, regression
- **Project Template**: Generate complete ML project structure

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Git workflow helper
python deliverable_ml_devops_toolkit.py demo1

# Pre-commit configuration
python deliverable_ml_devops_toolkit.py demo2

# Data quality tests
python deliverable_ml_devops_toolkit.py demo3

# Model quality tests
python deliverable_ml_devops_toolkit.py demo4

# Project template generator
python deliverable_ml_devops_toolkit.py demo5
```

## Git Workflow Conventions

### Branch Naming
```
feature/add-preprocessing     # New features
fix/memory-leak-batch        # Bug fixes
exp/bert-large-v2            # ML experiments
model/improved-embeddings    # Model iterations
data/incorporate-q4-feedback # Data changes
```

### Commit Message Format
```
type(scope): description

Types: feat, fix, exp, data, model, perf, refactor, test, docs, chore

Example:
exp: BERT-large with attention fix

Experiment Details:
- Hypothesis: Fixing attention dropout will improve accuracy
- Result: Accuracy improved from 0.85 to 0.89

Metrics:
- accuracy: 0.89
- f1: 0.87
```

## Data Quality Tests

| Test | Description |
|------|-------------|
| No Missing Values | Critical columns are complete |
| Label Distribution | Classes are reasonably balanced |
| No Duplicates | No duplicate rows in dataset |
| Value Ranges | Values within expected bounds |
| No Data Leakage | Train/test sets don't overlap |

## Model Quality Tests

| Test | Description |
|------|-------------|
| Accuracy Threshold | Meets minimum accuracy |
| No Class Collapse | Predicts multiple classes |
| Prediction Variance | Outputs aren't constant |
| Latency P99 | Inference speed acceptable |
| No Regression | Not worse than baseline |

## Generated Project Structure

```
my_ml_project/
├── .github/workflows/     # CI/CD pipelines
├── configs/               # Model & training configs
├── data/                  # Data directories (DVC tracked)
├── models/                # Model checkpoints
├── notebooks/             # Jupyter notebooks
├── src/                   # Source code
├── tests/                 # Test suite
├── scripts/               # Entry points
├── .pre-commit-config.yaml
├── Makefile
└── pyproject.toml
```

**Time**: ~4 hours | **Lines**: 1,400+ | **Author**: Neural Dojo
