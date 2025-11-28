# Module 43: DevOps Fundamentals for ML Engineers

**Last Updated**: 2025-11-28
**Status**: Complete
**Duration**: 5-6 hours
**Prerequisites**: Phase 9 complete

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master Git workflows specifically designed for ML projects
- Implement version control for code, data, and models
- Build comprehensive testing strategies for ML code
- Set up pre-commit hooks for ML code quality
- Understand the unique challenges of DevOps in ML contexts

---

## 📖 Why ML DevOps is Different

### The ML DevOps Challenge

Traditional software development has well-established DevOps practices. ML introduces unique challenges:

```
TRADITIONAL SOFTWARE vs ML SOFTWARE
====================================

Traditional:                    ML:
├── Code changes               ├── Code changes
├── Config changes             ├── Config changes
└── Dependencies               ├── Dependencies
                               ├── DATA changes (huge!)
                               ├── MODEL changes (huge!)
                               ├── Hyperparameters
                               ├── Training environment
                               └── Random seeds

Result: ML has MORE things that can change and break your system!
```

**Did You Know?** A 2022 survey by Algorithmia found that 55% of companies have not deployed a single ML model to production. The #1 reason cited? Lack of MLOps practices and infrastructure. DevOps fundamentals are the first step.

### The Three Pillars of ML Version Control

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ML VERSION CONTROL PILLARS                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. CODE VERSIONING (Git)                                              │
│     ├── Training scripts                                                │
│     ├── Inference code                                                  │
│     ├── Data preprocessing                                              │
│     └── Configuration files                                             │
│                                                                         │
│  2. DATA VERSIONING (DVC, Delta Lake, etc.)                            │
│     ├── Training datasets                                               │
│     ├── Validation datasets                                             │
│     ├── Feature stores                                                  │
│     └── Data transformations                                            │
│                                                                         │
│  3. MODEL VERSIONING (MLflow, W&B, etc.)                               │
│     ├── Model weights                                                   │
│     ├── Hyperparameters                                                 │
│     ├── Metrics                                                         │
│     └── Artifacts                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔀 Git Workflows for ML Projects

### The ML-Adapted Git Flow

Standard Git Flow doesn't quite work for ML. Here's an adapted version:

```
ML GIT WORKFLOW
===============

main ─────────────────●─────────────────●────────────────────→
                      │                 │
                      │                 │ (merge after validation)
                      │                 │
staging ──────●───────┼────●────────────┼─────────────────────→
              │       │    │            │
              │       │    │ (model validated)
              │       │    │
experiment/   │       │    │
  exp-001 ────┴───────┘    │
                           │
experiment/                │
  exp-002 ─────────────────┘

Key differences from standard Git Flow:
1. "experiment" branches for ML experiments
2. Staging branch for model validation
3. Longer validation before merging to main
```

### Branch Naming Conventions

```python
# ML-specific branch naming
BRANCH_PATTERNS = {
    # Feature development
    "feature/": "New functionality (feature/add-preprocessing)",

    # Bug fixes
    "fix/": "Bug fixes (fix/data-leak-validation)",

    # ML experiments
    "experiment/": "ML experiments (experiment/bert-large-v2)",
    "exp/": "Short form (exp/learning-rate-sweep)",

    # Model versions
    "model/": "Model iterations (model/v2-transformer)",

    # Data changes
    "data/": "Dataset changes (data/add-2024-samples)",

    # Hotfixes
    "hotfix/": "Production fixes (hotfix/inference-timeout)",
}

# Good examples
GOOD_BRANCH_NAMES = [
    "experiment/gpt4-fine-tune-customer-support",
    "feature/add-streaming-inference",
    "fix/memory-leak-batch-processing",
    "data/incorporate-q4-feedback",
    "model/v3-improved-embeddings",
]

# Bad examples
BAD_BRANCH_NAMES = [
    "test",           # Too vague
    "my-changes",     # Not descriptive
    "experiment1",    # No description
    "final",          # Never final in ML!
    "final-v2",       # Proof that "final" is never final
]
```

### Commit Message Conventions for ML

```python
# Conventional Commits adapted for ML

COMMIT_TYPES = {
    "feat": "New feature",
    "fix": "Bug fix",
    "exp": "Experiment (ML-specific)",
    "data": "Data changes (ML-specific)",
    "model": "Model changes (ML-specific)",
    "perf": "Performance improvement",
    "refactor": "Code refactoring",
    "test": "Adding/updating tests",
    "docs": "Documentation",
    "chore": "Maintenance",
}

# Examples
GOOD_COMMITS = [
    "feat: add streaming support for inference API",
    "exp: test BERT-large with learning rate 2e-5",
    "data: add 10k labeled examples from Q4 feedback",
    "model: improve accuracy from 0.85 to 0.89 with attention fix",
    "fix: resolve memory leak in batch processing",
    "perf: reduce inference latency by 40% with model quantization",
]

# Include metrics in experiment commits!
EXPERIMENT_COMMIT_FORMAT = """
exp: {short_description}

Experiment: {experiment_name}
Hypothesis: {what_you_tested}
Result: {outcome}

Metrics:
- Accuracy: {accuracy}
- F1: {f1_score}
- Latency: {latency_ms}ms

Config changes:
- learning_rate: {lr}
- batch_size: {batch_size}
- epochs: {epochs}
"""
```

**Did You Know?** Google's ML teams require experiment commits to include a "hypothesis" field. This practice, borrowed from scientific research, helps teams understand not just what changed but why it was expected to help. It's been credited with reducing duplicate experiments by 30%.

---

## 📊 Data Version Control (DVC)

### Why Git Alone Isn't Enough

```
THE PROBLEM WITH LARGE FILES IN GIT
===================================

Git stores EVERY version of EVERY file.

Your ML project:
├── training_data.csv (500 MB)
├── model_v1.pkl (200 MB)
├── model_v2.pkl (200 MB)
└── embeddings.npy (1 GB)

After 10 commits with model changes:
Repository size: 500 MB + (200 MB × 10) + 1 GB = 3.5 GB 😱

And you can't even push to GitHub (100 MB limit)!
```

### DVC: Git for Data

```bash
# Install DVC
pip install dvc

# Initialize DVC in a Git repo
dvc init

# Track a large file
dvc add data/training_data.csv

# This creates:
# - data/training_data.csv.dvc (small pointer file, tracked by Git)
# - data/.gitignore (ignores the actual data file)

# The actual data goes to remote storage
dvc remote add -d myremote s3://my-bucket/dvc-storage
dvc push
```

### DVC Workflow

```python
"""
DVC + Git Workflow for ML
"""

# 1. Make data changes
# (add new training samples, fix labels, etc.)

# 2. Track changes with DVC
"""
dvc add data/training_data.csv
dvc add models/best_model.pkl
"""

# 3. Commit the .dvc files with Git
"""
git add data/training_data.csv.dvc models/best_model.pkl.dvc
git commit -m "data: add 5000 new labeled samples"
"""

# 4. Push both
"""
dvc push  # Pushes data to remote storage
git push  # Pushes code + DVC pointers to Git
"""

# 5. Collaborator pulls
"""
git pull
dvc pull  # Downloads actual data files
"""

# DVC enables TIME TRAVEL for data!
"""
git checkout exp/bert-large
dvc checkout  # Gets the data from THAT experiment!
"""
```

### DVC Pipelines

```yaml
# dvc.yaml - Define reproducible ML pipelines

stages:
  prepare:
    cmd: python src/prepare_data.py
    deps:
      - src/prepare_data.py
      - data/raw/
    outs:
      - data/processed/

  train:
    cmd: python src/train.py --config configs/train.yaml
    deps:
      - src/train.py
      - data/processed/
      - configs/train.yaml
    outs:
      - models/model.pkl
    metrics:
      - metrics/train_metrics.json:
          cache: false
    plots:
      - metrics/loss_curve.csv:
          x: epoch
          y: loss

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/test/
    metrics:
      - metrics/eval_metrics.json:
          cache: false
```

```bash
# Run the full pipeline
dvc repro

# Compare metrics across experiments
dvc metrics diff

# Visualize pipeline
dvc dag
```

**Did You Know?** Iterative (the company behind DVC) found that teams using DVC reduced "data drift" bugs by 60%. Data drift - when training data changes unexpectedly - is one of the most common causes of ML system failures in production.

---

## 🧪 Testing Strategies for ML Code

### The ML Testing Pyramid

```
                    △
                   /│\
                  / │ \      End-to-End Tests
                 /  │  \     (Full pipeline, real data)
                /───┼───\
               /    │    \   Integration Tests
              /     │     \  (Components together)
             /──────┼──────\
            /       │       \ Unit Tests
           /        │        \(Individual functions)
          ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

ML Addition:

            △
           /│\
          / │ \         Model Quality Tests
         /──┼──\        (Accuracy, fairness)
        /   │   \       Data Quality Tests
       /────┼────\      (Schema, distributions)
      ▔▔▔▔▔▔▔▔▔▔▔▔
```

### Unit Tests for ML

```python
import pytest
import numpy as np
from src.preprocessing import normalize, tokenize, extract_features

class TestPreprocessing:
    """Unit tests for preprocessing functions."""

    def test_normalize_scales_to_unit_range(self):
        """Normalization should scale values to [0, 1]."""
        data = np.array([0, 50, 100])
        result = normalize(data)

        assert result.min() >= 0
        assert result.max() <= 1
        assert np.isclose(result[0], 0)
        assert np.isclose(result[2], 1)

    def test_normalize_handles_constant_values(self):
        """Normalization shouldn't crash on constant input."""
        data = np.array([5, 5, 5])
        result = normalize(data)

        # Should return zeros or handle gracefully
        assert not np.any(np.isnan(result))

    def test_tokenize_handles_empty_string(self):
        """Tokenizer should handle empty input."""
        result = tokenize("")
        assert result == [] or result == [""]

    def test_tokenize_preserves_important_tokens(self):
        """Tokenizer shouldn't drop important tokens."""
        text = "machine learning is amazing"
        tokens = tokenize(text)

        # Important words should be preserved
        assert "machine" in tokens or "machin" in tokens  # Allow stemming
        assert "learning" in tokens or "learn" in tokens

    def test_extract_features_output_shape(self):
        """Feature extraction should produce expected dimensions."""
        text = "sample input text"
        features = extract_features(text)

        assert features.shape == (768,)  # Expected embedding dim
        assert features.dtype == np.float32


class TestModelInference:
    """Unit tests for model inference."""

    def test_model_output_shape(self, model):
        """Model output should have correct shape."""
        input_data = np.random.randn(1, 768)
        output = model.predict(input_data)

        assert output.shape == (1, 10)  # 10 classes

    def test_model_output_is_probability(self, model):
        """Model output should be valid probabilities."""
        input_data = np.random.randn(1, 768)
        output = model.predict(input_data)

        assert np.all(output >= 0)
        assert np.all(output <= 1)
        assert np.isclose(output.sum(), 1.0)

    def test_model_deterministic(self, model):
        """Model should produce same output for same input."""
        input_data = np.random.randn(1, 768)

        output1 = model.predict(input_data)
        output2 = model.predict(input_data)

        np.testing.assert_array_equal(output1, output2)
```

### Data Quality Tests

```python
import pytest
import pandas as pd
import great_expectations as ge

class TestDataQuality:
    """Tests for data quality and schema validation."""

    @pytest.fixture
    def training_data(self):
        return pd.read_csv("data/training_data.csv")

    def test_no_missing_labels(self, training_data):
        """All samples should have labels."""
        assert training_data["label"].notna().all()

    def test_label_distribution_balanced(self, training_data):
        """Labels should be reasonably balanced."""
        label_counts = training_data["label"].value_counts()
        ratio = label_counts.max() / label_counts.min()

        # Allow up to 3:1 imbalance
        assert ratio < 3, f"Label imbalance too high: {ratio}"

    def test_no_data_leakage(self, training_data):
        """Training data shouldn't contain test identifiers."""
        test_ids = pd.read_csv("data/test_ids.csv")["id"]

        overlap = set(training_data["id"]) & set(test_ids)
        assert len(overlap) == 0, f"Data leakage! IDs in both: {overlap}"

    def test_feature_ranges(self, training_data):
        """Features should be within expected ranges."""
        # Using Great Expectations for complex validations
        ge_df = ge.from_pandas(training_data)

        # Age should be reasonable
        result = ge_df.expect_column_values_to_be_between(
            "age", min_value=0, max_value=120
        )
        assert result.success

        # Price should be positive
        result = ge_df.expect_column_values_to_be_between(
            "price", min_value=0
        )
        assert result.success

    def test_no_duplicate_samples(self, training_data):
        """No duplicate samples in training data."""
        duplicates = training_data.duplicated(subset=["text", "label"])
        assert not duplicates.any(), f"Found {duplicates.sum()} duplicates"


class TestDataDrift:
    """Tests for data drift between training and production."""

    def test_feature_distribution_similar(self):
        """Production features should match training distribution."""
        train_stats = load_training_statistics()
        prod_sample = get_production_sample(n=1000)

        for feature in ["age", "income", "score"]:
            train_mean = train_stats[feature]["mean"]
            train_std = train_stats[feature]["std"]
            prod_mean = prod_sample[feature].mean()

            # Z-score of production mean
            z_score = abs(prod_mean - train_mean) / train_std

            # Alert if mean shifted by more than 2 std
            assert z_score < 2, f"Feature {feature} drifted: z={z_score:.2f}"
```

### Model Quality Tests

```python
import pytest
from sklearn.metrics import accuracy_score, f1_score
from fairlearn.metrics import demographic_parity_difference

class TestModelQuality:
    """Tests for model quality and fairness."""

    @pytest.fixture
    def model_and_data(self):
        model = load_model("models/production_model.pkl")
        X_test, y_test = load_test_data()
        return model, X_test, y_test

    def test_accuracy_above_threshold(self, model_and_data):
        """Model accuracy should meet minimum threshold."""
        model, X_test, y_test = model_and_data
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)

        assert accuracy >= 0.85, f"Accuracy {accuracy:.2%} below threshold"

    def test_f1_score_per_class(self, model_and_data):
        """F1 score should be acceptable for all classes."""
        model, X_test, y_test = model_and_data
        y_pred = model.predict(X_test)

        f1_per_class = f1_score(y_test, y_pred, average=None)

        # No class should have F1 below 0.7
        for i, f1 in enumerate(f1_per_class):
            assert f1 >= 0.7, f"Class {i} F1 too low: {f1:.2f}"

    def test_no_performance_regression(self, model_and_data):
        """New model should not be worse than production."""
        model, X_test, y_test = model_and_data

        # Load production model metrics
        prod_metrics = load_production_metrics()

        # Calculate new model metrics
        y_pred = model.predict(X_test)
        new_accuracy = accuracy_score(y_test, y_pred)

        # Allow 1% degradation for statistical noise
        threshold = prod_metrics["accuracy"] - 0.01
        assert new_accuracy >= threshold, \
            f"Regression: {new_accuracy:.2%} < {threshold:.2%}"

    def test_fairness_demographic_parity(self, model_and_data):
        """Model should have similar performance across groups."""
        model, X_test, y_test = model_and_data
        sensitive_features = X_test["gender"]

        y_pred = model.predict(X_test)

        dpd = demographic_parity_difference(
            y_test, y_pred,
            sensitive_features=sensitive_features
        )

        # Demographic parity difference should be small
        assert abs(dpd) < 0.1, f"Fairness violation: DPD = {dpd:.3f}"


class TestModelRobustness:
    """Tests for model robustness and edge cases."""

    def test_handles_missing_values(self, model):
        """Model should handle missing values gracefully."""
        input_with_nan = pd.DataFrame({
            "feature1": [1.0, np.nan, 3.0],
            "feature2": [np.nan, 2.0, 3.0],
        })

        # Should not raise exception
        try:
            predictions = model.predict(input_with_nan)
            assert len(predictions) == 3
        except Exception as e:
            pytest.fail(f"Model crashed on missing values: {e}")

    def test_handles_extreme_values(self, model):
        """Model should handle extreme inputs."""
        extreme_input = pd.DataFrame({
            "feature1": [1e10, -1e10, 0],
            "feature2": [0, 0, 1e-10],
        })

        predictions = model.predict(extreme_input)

        # Predictions should be valid
        assert not np.any(np.isnan(predictions))
        assert not np.any(np.isinf(predictions))
```

**Did You Know?** Netflix runs over 500 automated tests on every model before deployment. These include not just accuracy tests but fairness tests across demographic groups, latency tests, and "chaos tests" that simulate production failures. This comprehensive testing reduced their model rollback rate by 70%.

---

## 🔧 Pre-commit Hooks for ML

### Setting Up Pre-commit

```bash
# Install pre-commit
pip install pre-commit

# Create configuration
touch .pre-commit-config.yaml

# Install hooks
pre-commit install
```

### ML-Specific Pre-commit Configuration

```yaml
# .pre-commit-config.yaml

repos:
  # Standard code quality
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']  # Catch accidentally committed models
      - id: detect-private-key
      - id: check-merge-conflict

  # Python formatting
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.10

  # Import sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  # Linting
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, numpy]

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: ["-r", "src/"]
        exclude: tests/

  # Notebook cleaning (ML-specific)
  - repo: https://github.com/kynan/nbstripout
    rev: 0.7.1
    hooks:
      - id: nbstripout  # Remove notebook outputs before commit

  # Custom ML checks (local hooks)
  - repo: local
    hooks:
      - id: check-no-secrets-in-config
        name: Check no secrets in config
        entry: python scripts/check_secrets.py
        language: python
        files: \.(yaml|yml|json|ini|env)$

      - id: validate-model-config
        name: Validate model config
        entry: python scripts/validate_config.py
        language: python
        files: configs/.*\.(yaml|yml)$

      - id: check-data-not-committed
        name: Check data files not committed
        entry: python scripts/check_data_files.py
        language: python
        types: [file]
```

### Custom Pre-commit Scripts

```python
# scripts/check_secrets.py
"""Check that config files don't contain secrets."""

import sys
import re
from pathlib import Path

SECRET_PATTERNS = [
    r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}',
    r'password\s*[:=]\s*["\']?[^"\'\s]+',
    r'secret\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}',
    r'token\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}',
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
    r'AKIA[A-Z0-9]{16}',     # AWS access key pattern
]

def check_file(filepath: str) -> list:
    """Check a file for secrets."""
    issues = []
    content = Path(filepath).read_text()

    for i, line in enumerate(content.split('\n'), 1):
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(f"{filepath}:{i}: Possible secret detected")

    return issues

def main():
    issues = []
    for filepath in sys.argv[1:]:
        issues.extend(check_file(filepath))

    if issues:
        print("❌ Secrets detected in config files:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)

    print("✅ No secrets detected")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

```python
# scripts/validate_config.py
"""Validate ML configuration files."""

import sys
import yaml
from pathlib import Path

REQUIRED_FIELDS = {
    "model": ["name", "version"],
    "training": ["batch_size", "learning_rate", "epochs"],
    "data": ["train_path", "val_path"],
}

def validate_config(filepath: str) -> list:
    """Validate a config file."""
    issues = []

    with open(filepath) as f:
        config = yaml.safe_load(f)

    for section, fields in REQUIRED_FIELDS.items():
        if section not in config:
            issues.append(f"Missing section: {section}")
            continue

        for field in fields:
            if field not in config[section]:
                issues.append(f"Missing field: {section}.{field}")

    # Validate values
    if "training" in config:
        lr = config["training"].get("learning_rate", 0)
        if lr <= 0 or lr > 1:
            issues.append(f"Invalid learning_rate: {lr}")

        batch_size = config["training"].get("batch_size", 0)
        if batch_size <= 0:
            issues.append(f"Invalid batch_size: {batch_size}")

    return issues

def main():
    all_issues = []
    for filepath in sys.argv[1:]:
        issues = validate_config(filepath)
        if issues:
            all_issues.append((filepath, issues))

    if all_issues:
        print("❌ Config validation failed:")
        for filepath, issues in all_issues:
            print(f"\n  {filepath}:")
            for issue in issues:
                print(f"    - {issue}")
        sys.exit(1)

    print("✅ All configs valid")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## 📁 Project Structure for ML

### Recommended ML Project Layout

```
ml-project/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline
│       ├── train.yml           # Training pipeline
│       └── deploy.yml          # Deployment pipeline
├── configs/
│   ├── model/
│   │   ├── base.yaml           # Base model config
│   │   ├── small.yaml          # Small model variant
│   │   └── large.yaml          # Large model variant
│   ├── training/
│   │   ├── default.yaml        # Default training config
│   │   └── fine_tune.yaml      # Fine-tuning config
│   └── inference/
│       └── production.yaml     # Production inference config
├── data/
│   ├── raw/                    # Raw data (DVC tracked)
│   ├── processed/              # Processed data (DVC tracked)
│   ├── features/               # Feature store
│   └── .gitignore              # Ignore actual data files
├── models/
│   ├── checkpoints/            # Training checkpoints (DVC)
│   ├── production/             # Production models (DVC)
│   └── .gitignore
├── notebooks/
│   ├── exploration/            # EDA notebooks
│   ├── experiments/            # Experiment notebooks
│   └── reports/                # Report notebooks
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── load.py             # Data loading
│   │   ├── preprocess.py       # Preprocessing
│   │   └── validate.py         # Data validation
│   ├── features/
│   │   ├── __init__.py
│   │   └── extract.py          # Feature extraction
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py            # Training logic
│   │   ├── evaluate.py         # Evaluation logic
│   │   └── predict.py          # Inference logic
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Config loading
│       └── logging.py          # Logging setup
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_preprocess.py
│   │   └── test_features.py
│   ├── integration/
│   │   └── test_pipeline.py
│   └── data/
│       └── test_data_quality.py
├── scripts/
│   ├── train.py                # Training entry point
│   ├── evaluate.py             # Evaluation entry point
│   └── predict.py              # Inference entry point
├── .dvc/                       # DVC configuration
├── .pre-commit-config.yaml     # Pre-commit hooks
├── dvc.yaml                    # DVC pipeline
├── dvc.lock                    # DVC lock file
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
├── requirements-dev.txt        # Dev dependencies
├── Makefile                    # Common commands
└── README.md                   # Project documentation
```

### Makefile for Common Commands

```makefile
# Makefile

.PHONY: install test lint train evaluate clean

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test types
test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-data:
	pytest tests/data/ -v

# Lint code
lint:
	black src/ tests/
	isort src/ tests/
	flake8 src/ tests/
	mypy src/

# Run full pipeline
train:
	dvc repro

# Evaluate model
evaluate:
	python scripts/evaluate.py --config configs/training/default.yaml

# Clean artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/

# Pull data from remote
data-pull:
	dvc pull

# Push data to remote
data-push:
	dvc push
```

---

## 💡 Did You Know? (Best Practices)

### Reproducibility Checklist

**Did You Know?** A 2019 study found that only 6% of ML papers had fully reproducible results. The main culprits: random seeds, missing hyperparameters, and unreported preprocessing steps. Here's a checklist to avoid this:

```python
# Reproducibility checklist for ML experiments

REPRODUCIBILITY_CHECKLIST = {
    "Random Seeds": {
        "python": "random.seed(42)",
        "numpy": "np.random.seed(42)",
        "torch": "torch.manual_seed(42)",
        "cuda": "torch.cuda.manual_seed_all(42)",
        "deterministic": "torch.backends.cudnn.deterministic = True",
    },
    "Environment": {
        "python_version": "3.10.x",
        "requirements": "requirements.txt with pinned versions",
        "hardware": "Document GPU model, CUDA version",
    },
    "Data": {
        "version": "DVC tracked with hash",
        "preprocessing": "Documented and versioned",
        "splits": "Fixed train/val/test splits",
    },
    "Model": {
        "architecture": "Documented with config",
        "hyperparameters": "All recorded in config",
        "initialization": "Documented (random, pretrained, etc.)",
    },
    "Training": {
        "optimizer": "Type and parameters",
        "scheduler": "Type and parameters",
        "early_stopping": "Criteria documented",
    },
}
```

### The Experiment Tracking Hierarchy

**Did You Know?** Spotify's ML platform team developed a hierarchy for experiment organization that's now used across the industry:

```
EXPERIMENT TRACKING HIERARCHY
==============================

Project (e.g., "Customer Churn Prediction")
└── Experiment Group (e.g., "Feature Engineering v2")
    └── Experiment (e.g., "Add behavioral features")
        └── Run (e.g., "lr=0.001, batch=32")
            └── Artifacts (model, metrics, plots)

Why this matters:
- Projects last months/years
- Experiment groups last weeks
- Experiments last days
- Runs last hours

Organize accordingly!
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Set Up ML Git Workflow

Set up a complete Git workflow for an ML project with proper branch naming, commit conventions, and PR templates.

### Exercise 2: Implement DVC Pipeline

Create a DVC pipeline that tracks data preprocessing, training, and evaluation stages.

### Exercise 3: Write ML Tests

Write a comprehensive test suite covering unit tests, data quality tests, and model quality tests.

---

## 📚 Further Reading

### Tools
- [DVC Documentation](https://dvc.org/doc)
- [Pre-commit](https://pre-commit.com/)
- [Great Expectations](https://greatexpectations.io/)
- [pytest](https://docs.pytest.org/)

### Papers & Articles
- "Hidden Technical Debt in Machine Learning Systems" (Google, 2015)
- "Machine Learning: The High-Interest Credit Card of Technical Debt" (Google, 2014)
- "Continuous Delivery for Machine Learning" (ThoughtWorks)

---

## ✅ Knowledge Check

1. **Why can't you use standard Git for large ML files?**

2. **What are the three pillars of ML version control?**

3. **How does DVC enable "time travel" for data?**

4. **What's the difference between unit tests and model quality tests?**

5. **Why are pre-commit hooks important for ML projects?**

---

## 🎯 Deliverables Checklist

- [ ] ML DevOps Toolkit with Git workflow automation
- [ ] Pre-commit configuration for ML projects
- [ ] Data and model quality test framework
- [ ] Project template with proper structure
- [ ] 5 working demos

---

## ⏭️ Next Steps

With DevOps fundamentals in place, you're ready to containerize your ML applications!

**Up Next**: Module 44 - Docker & Containerization for ML

---

_Module 43 Complete! You now understand ML DevOps fundamentals!_

_"The best ML model is worthless if you can't deploy it reliably."_
