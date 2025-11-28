# Module 45: CI/CD for AI/ML Development

**Last Updated**: 2025-11-28
**Status**: 🟢 Complete
**Duration**: 7-8 hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why CI/CD for ML is different from traditional software
- Master GitHub Actions for ML workflows
- Build automated testing pipelines for ML code
- Implement continuous training (CT) pipelines
- Create model validation gates
- Use portable CI/CD with Dagger

---

## 📖 Why CI/CD for ML is Different

### The Traditional CI/CD Pipeline

```
TRADITIONAL SOFTWARE CI/CD
===========================

Code Change → Build → Test → Deploy
     │          │       │       │
     │          │       │       └── Ship binary/container
     │          │       └── Unit + Integration tests
     │          └── Compile/bundle
     └── Git push

Simple because:
- Code is the only artifact
- Tests are deterministic
- "Working" is binary (pass/fail)
```

### The ML CI/CD Challenge

```
ML CI/CD COMPLEXITY
===================

┌─────────────────────────────────────────────────────────────────────┐
│                    THREE THINGS CAN CHANGE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. CODE                                                            │
│     Model architecture, feature engineering, inference code         │
│     Traditional CI/CD handles this                                  │
│                                                                     │
│  2. DATA                                                            │
│     Training data, validation data, production data drift           │
│     Need data validation, versioning, quality checks               │
│                                                                     │
│  3. MODEL                                                           │
│     Trained weights, hyperparameters, model version                 │
│     Need model validation, A/B testing, rollback                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Any of these can trigger a pipeline!
```

**Did You Know?** Google's ML platform team coined the term "ML Technical Debt" in a famous 2015 paper. They found that ML systems have a small fraction of actual ML code surrounded by a massive infrastructure for data collection, feature extraction, configuration, and monitoring. This is why CI/CD for ML is so complex—you're not just testing code.

### Continuous X in ML

```
THE CONTINUOUS SPECTRUM
=======================

CI  (Continuous Integration)
    → Code changes trigger tests
    → Unit tests, linting, type checking
    → Same as traditional software

CD  (Continuous Delivery/Deployment)
    → Successful tests trigger deployment
    → Model packaging, container builds
    → Deploy to staging/production

CT  (Continuous Training) ← NEW FOR ML!
    → Data changes trigger retraining
    → Scheduled or event-driven
    → Automatic model updates

CM  (Continuous Monitoring) ← NEW FOR ML!
    → Track model performance in production
    → Detect data drift, model degradation
    → Trigger retraining when needed
```

---

## 🔄 GitHub Actions for ML

### Anatomy of a Workflow

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

# Triggers
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'requirements.txt'
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly retraining
  workflow_dispatch:      # Manual trigger

# Environment variables
env:
  PYTHON_VERSION: '3.10'
  MODEL_REGISTRY: 'models'

# Jobs
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

### ML-Specific Workflow Patterns

```yaml
# Pattern 1: Code Quality + ML Tests
jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: ruff check src/
      - name: Type Check
        run: mypy src/
      - name: Format Check
        run: black --check src/

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest tests/unit/ -v

  data-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate data schema
        run: python -m src.validate_data
      - name: Check data quality
        run: pytest tests/data/ -v

  model-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, data-tests]
    steps:
      - uses: actions/checkout@v4
      - name: Load model
        run: python -m src.load_model
      - name: Run model tests
        run: pytest tests/model/ -v
      - name: Check model metrics
        run: python -m src.validate_metrics
```

### Caching for ML Workflows

```yaml
# Cache dependencies (saves 2-5 minutes)
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

# Cache model artifacts (saves download time)
- uses: actions/cache@v4
  with:
    path: models/
    key: models-${{ hashFiles('models/config.json') }}

# Cache Hugging Face models
- uses: actions/cache@v4
  with:
    path: ~/.cache/huggingface
    key: hf-${{ hashFiles('requirements.txt') }}
```

**Did You Know?** GitHub Actions provides 2,000 free minutes per month for private repos and unlimited minutes for public repos. A typical ML test suite takes 5-15 minutes, so you can run 130-400 pipeline runs per month for free. Self-hosted runners can reduce this further—and give you GPU access.

---

## 🧪 Testing Strategies for ML

### The ML Testing Pyramid

```
                    ▲
                   ╱ ╲
                  ╱   ╲     End-to-End Tests
                 ╱ E2E ╲    (Full pipeline validation)
                ╱───────╲
               ╱         ╲   Model Tests
              ╱  MODEL    ╲  (Accuracy, latency, regression)
             ╱─────────────╲
            ╱               ╲  Data Tests
           ╱     DATA        ╲ (Schema, quality, drift)
          ╱───────────────────╲
         ╱                     ╲ Integration Tests
        ╱    INTEGRATION        ╲(API contracts, services)
       ╱─────────────────────────╲
      ╱                           ╲ Unit Tests
     ╱         UNIT                ╲(Functions, transformations)
    ╱───────────────────────────────╲

    MORE ──────────────────────────► FEWER
    FAST ──────────────────────────► SLOW
    CHEAP ─────────────────────────► EXPENSIVE
```

### Unit Tests for ML Code

```python
# tests/unit/test_preprocessing.py
import pytest
import numpy as np
from src.preprocessing import normalize, tokenize, extract_features

class TestNormalize:
    """Test normalization functions."""

    def test_normalize_zero_mean(self):
        """Output should have zero mean."""
        data = np.array([1, 2, 3, 4, 5])
        result = normalize(data)
        assert np.isclose(result.mean(), 0, atol=1e-7)

    def test_normalize_unit_variance(self):
        """Output should have unit variance."""
        data = np.array([1, 2, 3, 4, 5])
        result = normalize(data)
        assert np.isclose(result.std(), 1, atol=1e-7)

    def test_normalize_handles_constant(self):
        """Should handle constant arrays without division by zero."""
        data = np.array([5, 5, 5, 5, 5])
        result = normalize(data)
        assert not np.any(np.isnan(result))

    def test_normalize_empty_array(self):
        """Should raise on empty input."""
        with pytest.raises(ValueError):
            normalize(np.array([]))


class TestTokenize:
    """Test tokenization functions."""

    def test_tokenize_basic(self):
        """Basic tokenization should split on whitespace."""
        text = "Hello world"
        tokens = tokenize(text)
        assert tokens == ["hello", "world"]

    def test_tokenize_handles_punctuation(self):
        """Should remove punctuation."""
        text = "Hello, world!"
        tokens = tokenize(text)
        assert tokens == ["hello", "world"]

    def test_tokenize_max_length(self):
        """Should respect max_length parameter."""
        text = "one two three four five"
        tokens = tokenize(text, max_length=3)
        assert len(tokens) == 3
```

### Data Quality Tests

```python
# tests/data/test_data_quality.py
import pytest
import pandas as pd
from src.data import load_training_data

@pytest.fixture
def training_data():
    """Load training data for tests."""
    return load_training_data()

class TestDataSchema:
    """Verify data schema expectations."""

    def test_required_columns_exist(self, training_data):
        """All required columns must be present."""
        required = ['text', 'label', 'timestamp', 'source']
        missing = set(required) - set(training_data.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_no_null_in_required_fields(self, training_data):
        """Required fields should not have nulls."""
        required = ['text', 'label']
        for col in required:
            null_count = training_data[col].isnull().sum()
            assert null_count == 0, f"{col} has {null_count} nulls"

    def test_label_values_valid(self, training_data):
        """Labels should be in expected set."""
        valid_labels = {0, 1, 2}  # negative, neutral, positive
        actual_labels = set(training_data['label'].unique())
        invalid = actual_labels - valid_labels
        assert not invalid, f"Invalid labels: {invalid}"


class TestDataQuality:
    """Verify data quality expectations."""

    def test_minimum_samples(self, training_data):
        """Should have minimum number of samples."""
        min_samples = 1000
        assert len(training_data) >= min_samples

    def test_class_balance(self, training_data):
        """Classes should be reasonably balanced."""
        label_counts = training_data['label'].value_counts()
        min_ratio = label_counts.min() / label_counts.max()
        assert min_ratio >= 0.1, f"Class imbalance ratio: {min_ratio}"

    def test_text_length_distribution(self, training_data):
        """Text lengths should be within expected range."""
        lengths = training_data['text'].str.len()
        assert lengths.min() >= 10, "Text too short"
        assert lengths.max() <= 10000, "Text too long"
        assert lengths.median() >= 50, "Median text length too short"

    def test_no_duplicate_texts(self, training_data):
        """Should not have duplicate texts."""
        duplicates = training_data['text'].duplicated().sum()
        duplicate_ratio = duplicates / len(training_data)
        assert duplicate_ratio < 0.01, f"Duplicate ratio: {duplicate_ratio:.2%}"
```

### Model Quality Tests

```python
# tests/model/test_model_quality.py
import pytest
import time
import numpy as np
from src.model import load_model, predict

@pytest.fixture(scope="module")
def model():
    """Load model once for all tests."""
    return load_model("models/production/model.pt")

@pytest.fixture
def test_samples():
    """Sample inputs for testing."""
    return [
        "This product is amazing!",
        "Terrible experience, never again.",
        "It's okay, nothing special.",
    ]

class TestModelAccuracy:
    """Verify model accuracy thresholds."""

    def test_accuracy_above_threshold(self, model):
        """Model accuracy should meet minimum threshold."""
        from src.evaluate import evaluate_on_test_set
        metrics = evaluate_on_test_set(model)
        assert metrics['accuracy'] >= 0.85, f"Accuracy {metrics['accuracy']}"

    def test_f1_score_above_threshold(self, model):
        """F1 score should meet minimum threshold."""
        from src.evaluate import evaluate_on_test_set
        metrics = evaluate_on_test_set(model)
        assert metrics['f1'] >= 0.80, f"F1 {metrics['f1']}"

    def test_no_class_collapse(self, model, test_samples):
        """Model should predict multiple classes."""
        predictions = [predict(model, text) for text in test_samples * 10]
        unique_predictions = set(predictions)
        assert len(unique_predictions) >= 2, "Model collapsed to single class"


class TestModelLatency:
    """Verify model inference performance."""

    def test_single_inference_latency(self, model, test_samples):
        """Single inference should be fast."""
        text = test_samples[0]

        start = time.perf_counter()
        predict(model, text)
        latency_ms = (time.perf_counter() - start) * 1000

        assert latency_ms < 100, f"Latency {latency_ms:.1f}ms exceeds 100ms"

    def test_batch_inference_latency(self, model, test_samples):
        """Batch inference should scale efficiently."""
        batch = test_samples * 100  # 300 samples

        start = time.perf_counter()
        for text in batch:
            predict(model, text)
        total_ms = (time.perf_counter() - start) * 1000

        per_sample_ms = total_ms / len(batch)
        assert per_sample_ms < 50, f"Per-sample latency {per_sample_ms:.1f}ms"


class TestModelRegression:
    """Verify model doesn't regress from baseline."""

    def test_no_accuracy_regression(self, model):
        """New model should not be worse than baseline."""
        from src.evaluate import evaluate_on_test_set, load_baseline_metrics

        current = evaluate_on_test_set(model)
        baseline = load_baseline_metrics()

        # Allow 1% regression tolerance
        min_accuracy = baseline['accuracy'] * 0.99
        assert current['accuracy'] >= min_accuracy, (
            f"Regression: {current['accuracy']:.3f} < {min_accuracy:.3f}"
        )
```

---

## 🔁 Continuous Training (CT)

### CT Architecture

```
CONTINUOUS TRAINING PIPELINE
============================

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   DATA SOURCES           TRIGGERS              PIPELINE             │
│   ============           ========              ========             │
│                                                                     │
│   ┌─────────┐                                                       │
│   │ New Data│ ─────┐                                                │
│   └─────────┘      │     ┌──────────────┐     ┌──────────────┐     │
│                    ├────►│   Trigger    │────►│   Training   │     │
│   ┌─────────┐      │     │   Service    │     │   Pipeline   │     │
│   │Schedule │ ─────┤     └──────────────┘     └──────┬───────┘     │
│   │(Weekly) │      │                                 │              │
│   └─────────┘      │                                 ▼              │
│                    │                          ┌──────────────┐      │
│   ┌─────────┐      │                          │  Validation  │      │
│   │  Drift  │ ─────┘                          │    Gate      │      │
│   │Detected │                                 └──────┬───────┘      │
│   └─────────┘                                        │              │
│                                                      ▼              │
│                                               ┌──────────────┐      │
│                                               │   Deploy?    │      │
│                                               │  (if better) │      │
│                                               └──────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Scheduled Retraining Workflow

```yaml
# .github/workflows/continuous-training.yml
name: Continuous Training

on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 2 AM
  workflow_dispatch:
    inputs:
      force_deploy:
        description: 'Deploy even if metrics are worse'
        required: false
        default: 'false'

jobs:
  fetch-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Fetch latest training data
        run: |
          python -m src.data.fetch \
            --start-date $(date -d '7 days ago' +%Y-%m-%d) \
            --end-date $(date +%Y-%m-%d) \
            --output data/new/

      - name: Upload data artifact
        uses: actions/upload-artifact@v4
        with:
          name: training-data
          path: data/new/

  train:
    needs: fetch-data
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download data
        uses: actions/download-artifact@v4
        with:
          name: training-data
          path: data/new/

      - name: Train model
        run: |
          python -m src.train \
            --data data/new/ \
            --output models/candidate/ \
            --experiment-name "weekly-retrain-${{ github.run_id }}"

      - name: Upload model
        uses: actions/upload-artifact@v4
        with:
          name: candidate-model
          path: models/candidate/

  validate:
    needs: train
    runs-on: ubuntu-latest
    outputs:
      should_deploy: ${{ steps.compare.outputs.should_deploy }}
    steps:
      - uses: actions/checkout@v4

      - name: Download candidate model
        uses: actions/download-artifact@v4
        with:
          name: candidate-model
          path: models/candidate/

      - name: Download production model
        run: |
          aws s3 cp s3://models/production/ models/production/ --recursive

      - name: Compare models
        id: compare
        run: |
          python -m src.evaluate.compare \
            --candidate models/candidate/ \
            --baseline models/production/ \
            --output metrics.json

          # Check if candidate is better
          BETTER=$(python -c "
          import json
          m = json.load(open('metrics.json'))
          print('true' if m['candidate']['accuracy'] > m['baseline']['accuracy'] else 'false')
          ")
          echo "should_deploy=$BETTER" >> $GITHUB_OUTPUT

  deploy:
    needs: validate
    if: needs.validate.outputs.should_deploy == 'true' || github.event.inputs.force_deploy == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download candidate model
        uses: actions/download-artifact@v4
        with:
          name: candidate-model
          path: models/candidate/

      - name: Deploy to production
        run: |
          # Upload to S3
          aws s3 cp models/candidate/ s3://models/production/ --recursive

          # Update Kubernetes deployment
          kubectl set image deployment/model-server \
            model=myregistry/model:${{ github.sha }}

      - name: Notify
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text": "New model deployed! Run: ${{ github.run_id }}"}'
```

**Did You Know?** Uber's Michelangelo platform processes over 1.5 million predictions per second. They implemented continuous training that automatically retrains models when feature drift exceeds thresholds. Their paper "Meet Michelangelo: Uber's Machine Learning Platform" (2017) was foundational for MLOps practices.

---

## 🚦 Model Validation Gates

### Quality Gates Pattern

```
MODEL VALIDATION GATES
======================

Candidate Model
      │
      ▼
┌─────────────────┐
│ Gate 1: Schema  │ → Does model output match expected format?
│   Validation    │   (shapes, types, ranges)
└────────┬────────┘
         │ PASS
         ▼
┌─────────────────┐
│ Gate 2: Metrics │ → Does accuracy meet threshold?
│   Threshold     │   (accuracy >= 0.85, latency < 100ms)
└────────┬────────┘
         │ PASS
         ▼
┌─────────────────┐
│ Gate 3: No      │ → Is it better than current production?
│   Regression    │   (accuracy_new >= accuracy_old * 0.99)
└────────┬────────┘
         │ PASS
         ▼
┌─────────────────┐
│ Gate 4: Shadow  │ → Does it work on real traffic?
│   Testing       │   (A/B test with no user impact)
└────────┬────────┘
         │ PASS
         ▼
    DEPLOY ✅
```

### Implementation

```python
# src/validation/gates.py
from dataclasses import dataclass
from typing import Callable, Optional
from enum import Enum

class GateStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class GateResult:
    gate_name: str
    status: GateStatus
    message: str
    metrics: dict = None

class ValidationGate:
    """Base class for validation gates."""

    def __init__(self, name: str, required: bool = True):
        self.name = name
        self.required = required

    def check(self, model, context: dict) -> GateResult:
        raise NotImplementedError


class MetricsThresholdGate(ValidationGate):
    """Check if model meets minimum metrics thresholds."""

    def __init__(
        self,
        thresholds: dict,
        name: str = "metrics_threshold",
    ):
        super().__init__(name)
        self.thresholds = thresholds

    def check(self, model, context: dict) -> GateResult:
        metrics = context.get('metrics', {})

        failures = []
        for metric, threshold in self.thresholds.items():
            value = metrics.get(metric, 0)
            if value < threshold:
                failures.append(
                    f"{metric}: {value:.3f} < {threshold:.3f}"
                )

        if failures:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAILED,
                message=f"Thresholds not met: {', '.join(failures)}",
                metrics=metrics,
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASSED,
            message="All thresholds met",
            metrics=metrics,
        )


class NoRegressionGate(ValidationGate):
    """Check that new model isn't worse than baseline."""

    def __init__(
        self,
        metric: str = "accuracy",
        tolerance: float = 0.01,
        name: str = "no_regression",
    ):
        super().__init__(name)
        self.metric = metric
        self.tolerance = tolerance

    def check(self, model, context: dict) -> GateResult:
        current = context.get('metrics', {}).get(self.metric, 0)
        baseline = context.get('baseline_metrics', {}).get(self.metric, 0)

        min_allowed = baseline * (1 - self.tolerance)

        if current < min_allowed:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAILED,
                message=f"Regression: {current:.3f} < {min_allowed:.3f}",
                metrics={"current": current, "baseline": baseline},
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASSED,
            message=f"No regression: {current:.3f} >= {min_allowed:.3f}",
            metrics={"current": current, "baseline": baseline},
        )


class ValidationPipeline:
    """Run model through validation gates."""

    def __init__(self, gates: list[ValidationGate]):
        self.gates = gates

    def validate(self, model, context: dict) -> tuple[bool, list[GateResult]]:
        results = []
        all_passed = True

        for gate in self.gates:
            result = gate.check(model, context)
            results.append(result)

            if result.status == GateStatus.FAILED and gate.required:
                all_passed = False
                break  # Stop on first required failure

        return all_passed, results
```

---

## 🐙 Portable CI/CD with Dagger

### Why Dagger?

```
THE CI VENDOR LOCK-IN PROBLEM
=============================

Traditional Approach:
┌─────────────────┐
│ GitHub Actions  │ ← Workflow YAML (vendor-specific)
│ GitLab CI       │ ← .gitlab-ci.yml (different syntax)
│ Jenkins         │ ← Jenkinsfile (Groovy DSL)
│ CircleCI        │ ← config.yml (yet another format)
└─────────────────┘

Problems:
- Can't test locally
- Vendor-specific syntax
- Hard to debug
- "Works on CI" ≠ "Works locally"

Dagger Approach:
┌─────────────────┐
│     Dagger      │ ← Write pipelines in Python/Go/TypeScript
│   (Portable)    │ ← Run anywhere: local, GitHub, GitLab, etc.
└─────────────────┘

Benefits:
- Test locally before pushing
- Same code runs everywhere
- Type-safe, IDE support
- Cacheable, reproducible
```

**Did You Know?** Dagger was created by Solomon Hykes (the creator of Docker) in 2022. His insight was that CI/CD pipelines have the same portability problem that Docker solved for applications. Dagger pipelines run inside containers, making them truly portable across CI platforms.

### Dagger Pipeline Example

```python
# dagger/pipeline.py
import dagger
from dagger import dag, function, object_type

@object_type
class MLPipeline:
    """ML Pipeline with Dagger."""

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Run tests on the ML code."""
        return await (
            dag.container()
            .from_("python:3.10-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec(["pip", "install", "pytest"])
            .with_exec(["pytest", "tests/", "-v"])
            .stdout()
        )

    @function
    async def lint(self, source: dagger.Directory) -> str:
        """Lint the code."""
        return await (
            dag.container()
            .from_("python:3.10-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "ruff", "mypy"])
            .with_exec(["ruff", "check", "src/"])
            .with_exec(["mypy", "src/"])
            .stdout()
        )

    @function
    async def train(
        self,
        source: dagger.Directory,
        data: dagger.Directory,
        epochs: int = 10,
    ) -> dagger.Directory:
        """Train the model."""
        return await (
            dag.container()
            .from_("pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime")
            .with_directory("/app", source)
            .with_directory("/data", data)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec([
                "python", "-m", "src.train",
                "--data", "/data",
                "--output", "/models",
                "--epochs", str(epochs),
            ])
            .directory("/models")
        )

    @function
    async def build_image(
        self,
        source: dagger.Directory,
        model: dagger.Directory,
    ) -> str:
        """Build production Docker image."""
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_directory("/app", source)
            .with_directory("/app/models", model)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_entrypoint(["python", "-m", "src.serve"])
        )

        # Publish to registry
        address = await container.publish(
            f"myregistry/ml-model:latest"
        )
        return address

    @function
    async def full_pipeline(
        self,
        source: dagger.Directory,
        data: dagger.Directory,
    ) -> str:
        """Run the complete ML pipeline."""
        # Run tests and lint in parallel
        test_result = self.test(source)
        lint_result = self.lint(source)

        # Wait for both
        await test_result
        await lint_result

        # Train model
        model = await self.train(source, data)

        # Build and publish image
        image = await self.build_image(source, model)

        return f"Pipeline complete! Image: {image}"
```

### Running Dagger Locally

```bash
# Install Dagger CLI
curl -L https://dl.dagger.io/dagger/install.sh | sh

# Run pipeline locally
dagger call test --source=.

# Run full pipeline
dagger call full-pipeline --source=. --data=./data/

# Call from GitHub Actions
# .github/workflows/dagger.yml
name: Dagger Pipeline
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dagger/dagger-for-github@v5
        with:
          verb: call
          args: full-pipeline --source=. --data=./data/
```

---

## 📊 Workflow Patterns for ML

### Pattern 1: PR Validation

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation

on:
  pull_request:
    branches: [main]

jobs:
  quick-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint & Format
        run: |
          pip install ruff black
          ruff check src/
          black --check src/

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Unit Tests
        run: |
          pip install -r requirements.txt pytest
          pytest tests/unit/ -v --tb=short

  model-smoke-test:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - name: Quick Model Test
        run: |
          pip install -r requirements.txt
          python -m src.test_model --quick
```

### Pattern 2: Release Pipeline

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Full Test Suite
        run: pytest tests/ -v

  build-image:
    needs: build-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker Image
        run: |
          docker build -t myapp:${{ github.ref_name }} .

      - name: Push to Registry
        run: |
          docker push myapp:${{ github.ref_name }}

  deploy-staging:
    needs: build-image
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Staging
        run: |
          kubectl set image deployment/app app=myapp:${{ github.ref_name }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          kubectl set image deployment/app app=myapp:${{ github.ref_name }}
```

### Pattern 3: Matrix Testing

```yaml
# Test across multiple Python versions and OS
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11']
        exclude:
          - os: macos-latest
            python-version: '3.9'

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest tests/
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Basic ML Workflow

Create a GitHub Actions workflow that:
1. Runs on push to main
2. Lints with ruff
3. Runs pytest
4. Reports code coverage

### Exercise 2: Continuous Training

Create a workflow that:
1. Runs weekly on schedule
2. Fetches new data
3. Retrains the model
4. Compares with baseline
5. Deploys if better

### Exercise 3: Validation Gates

Implement validation gates for:
1. Minimum accuracy threshold
2. Maximum latency requirement
3. No regression from baseline
4. Memory usage limit

---

## 📚 Further Reading

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Dagger Documentation](https://docs.dagger.io/)
- [MLflow CI/CD](https://mlflow.org/docs/latest/projects.html)

### Papers & Articles
- "Hidden Technical Debt in ML Systems" (Google, 2015)
- "Continuous Delivery for Machine Learning" (ThoughtWorks)
- "ML Test Score: A Rubric for ML Production Readiness" (Google)

### Tools
- [Great Expectations](https://greatexpectations.io/) - Data validation
- [Evidently](https://evidentlyai.com/) - ML monitoring
- [DVC](https://dvc.org/) - Data version control

---

## ✅ Knowledge Check

1. **What are the three things that can trigger an ML pipeline?**

2. **What is Continuous Training (CT)?**

3. **Why is the ML testing pyramid different from traditional software?**

4. **What problem does Dagger solve for CI/CD?**

5. **What are validation gates and why are they important?**

---

## ⏭️ Next Steps

You now understand CI/CD for ML! Key takeaways:
- ML pipelines are triggered by code, data, AND model changes
- Testing includes data quality and model quality tests
- Continuous Training automates model updates
- Validation gates prevent bad models from deploying

**Up Next**: Module 46 - Kubernetes Fundamentals for ML

---

_Module 45 Complete! You now understand CI/CD for ML!_
_"The best pipeline is the one that catches problems before production."_
