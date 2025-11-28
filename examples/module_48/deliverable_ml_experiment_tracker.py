#!/usr/bin/env python3
"""
ML Experiment Tracker Toolkit
=============================

A local experiment tracking system demonstrating MLOps concepts:
- Experiment and run management
- Parameter and metric logging
- Artifact tracking
- Model registry with versioning
- Experiment comparison and analysis

This toolkit simulates MLflow/W&B functionality for learning purposes.

Usage:
    python deliverable_ml_experiment_tracker.py demo1  # Basic experiment tracking
    python deliverable_ml_experiment_tracker.py demo2  # Hyperparameter comparison
    python deliverable_ml_experiment_tracker.py demo3  # Model registry
    python deliverable_ml_experiment_tracker.py demo4  # Experiment analysis
    python deliverable_ml_experiment_tracker.py demo5  # Full MLOps workflow

Author: Neural Dojo
"""

import json
import os
import sys
import random
import hashlib
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import math


# =============================================================================
# CONFIGURATION
# =============================================================================

STORAGE_DIR = Path(".ml_experiment_tracker")
EXPERIMENTS_DIR = STORAGE_DIR / "experiments"
REGISTRY_DIR = STORAGE_DIR / "registry"
ARTIFACTS_DIR = STORAGE_DIR / "artifacts"


class ModelStage(Enum):
    """Model lifecycle stages."""
    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class RunStatus(Enum):
    """Run status."""
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    KILLED = "KILLED"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Metric:
    """A logged metric with optional step."""
    key: str
    value: float
    timestamp: str
    step: Optional[int] = None


@dataclass
class Param:
    """A logged parameter."""
    key: str
    value: str


@dataclass
class Artifact:
    """A logged artifact."""
    path: str
    size_bytes: int
    timestamp: str


@dataclass
class Run:
    """An experiment run."""
    run_id: str
    run_name: str
    experiment_id: str
    status: RunStatus = RunStatus.RUNNING
    start_time: str = ""
    end_time: str = ""
    params: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, List[Metric]] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    artifacts: List[Artifact] = field(default_factory=list)

    def __post_init__(self):
        if not self.start_time:
            self.start_time = datetime.now().isoformat()


@dataclass
class Experiment:
    """An experiment containing multiple runs."""
    experiment_id: str
    name: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    created_time: str = ""
    runs: List[str] = field(default_factory=list)  # Run IDs

    def __post_init__(self):
        if not self.created_time:
            self.created_time = datetime.now().isoformat()


@dataclass
class ModelVersion:
    """A registered model version."""
    name: str
    version: int
    run_id: str
    stage: ModelStage = ModelStage.NONE
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    created_time: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.created_time:
            self.created_time = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = self.created_time


@dataclass
class RegisteredModel:
    """A registered model with versions."""
    name: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    created_time: str = ""
    versions: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_time:
            self.created_time = datetime.now().isoformat()


# =============================================================================
# EXPERIMENT TRACKER
# =============================================================================

class ExperimentTracker:
    """Local experiment tracking system."""

    def __init__(self):
        """Initialize tracker with storage directories."""
        EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

        self.experiments: Dict[str, Experiment] = {}
        self.runs: Dict[str, Run] = {}
        self.registered_models: Dict[str, RegisteredModel] = {}
        self.model_versions: Dict[str, Dict[int, ModelVersion]] = {}

        self._load_state()

    def _generate_id(self, prefix: str = "") -> str:
        """Generate unique ID."""
        timestamp = datetime.now().isoformat()
        random_part = random.randint(1000, 9999)
        hash_input = f"{prefix}{timestamp}{random_part}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _save_state(self):
        """Save tracker state to disk."""
        # Save experiments
        for exp_id, exp in self.experiments.items():
            exp_file = EXPERIMENTS_DIR / f"{exp_id}.json"
            exp_data = asdict(exp)
            exp_file.write_text(json.dumps(exp_data, indent=2, default=str))

        # Save runs
        for run_id, run in self.runs.items():
            run_file = EXPERIMENTS_DIR / f"run_{run_id}.json"
            run_data = asdict(run)
            run_data["status"] = run.status.value
            run_data["metrics"] = {
                k: [asdict(m) for m in v]
                for k, v in run.metrics.items()
            }
            run_file.write_text(json.dumps(run_data, indent=2, default=str))

        # Save registry
        for model_name, model in self.registered_models.items():
            model_file = REGISTRY_DIR / f"{model_name}.json"
            model_data = asdict(model)
            model_file.write_text(json.dumps(model_data, indent=2, default=str))

        # Save model versions
        for model_name, versions in self.model_versions.items():
            for version, mv in versions.items():
                mv_file = REGISTRY_DIR / f"{model_name}_v{version}.json"
                mv_data = asdict(mv)
                mv_data["stage"] = mv.stage.value
                mv_file.write_text(json.dumps(mv_data, indent=2, default=str))

    def _load_state(self):
        """Load tracker state from disk."""
        # Load experiments
        for exp_file in EXPERIMENTS_DIR.glob("*.json"):
            if not exp_file.name.startswith("run_"):
                data = json.loads(exp_file.read_text())
                self.experiments[data["experiment_id"]] = Experiment(**data)

        # Load runs
        for run_file in EXPERIMENTS_DIR.glob("run_*.json"):
            data = json.loads(run_file.read_text())
            data["status"] = RunStatus(data["status"])
            data["metrics"] = {
                k: [Metric(**m) for m in v]
                for k, v in data.get("metrics", {}).items()
            }
            self.runs[data["run_id"]] = Run(**data)

        # Load registered models
        for model_file in REGISTRY_DIR.glob("*.json"):
            if "_v" not in model_file.name:
                data = json.loads(model_file.read_text())
                self.registered_models[data["name"]] = RegisteredModel(**data)

        # Load model versions
        for mv_file in REGISTRY_DIR.glob("*_v*.json"):
            data = json.loads(mv_file.read_text())
            data["stage"] = ModelStage(data["stage"])
            mv = ModelVersion(**data)
            if mv.name not in self.model_versions:
                self.model_versions[mv.name] = {}
            self.model_versions[mv.name][mv.version] = mv

    # Experiment Management
    def create_experiment(self, name: str, description: str = "") -> Experiment:
        """Create a new experiment."""
        exp_id = self._generate_id("exp")
        experiment = Experiment(
            experiment_id=exp_id,
            name=name,
            description=description
        )
        self.experiments[exp_id] = experiment
        self._save_state()
        return experiment

    def get_experiment(self, name: str) -> Optional[Experiment]:
        """Get experiment by name."""
        for exp in self.experiments.values():
            if exp.name == name:
                return exp
        return None

    def get_or_create_experiment(self, name: str, description: str = "") -> Experiment:
        """Get existing experiment or create new one."""
        exp = self.get_experiment(name)
        if exp:
            return exp
        return self.create_experiment(name, description)

    # Run Management
    def start_run(
        self,
        experiment_name: str,
        run_name: Optional[str] = None
    ) -> Run:
        """Start a new run in an experiment."""
        experiment = self.get_or_create_experiment(experiment_name)

        run_id = self._generate_id("run")
        if not run_name:
            run_name = f"run-{len(experiment.runs) + 1}"

        run = Run(
            run_id=run_id,
            run_name=run_name,
            experiment_id=experiment.experiment_id
        )

        self.runs[run_id] = run
        experiment.runs.append(run_id)
        self._save_state()
        return run

    def end_run(self, run_id: str, status: RunStatus = RunStatus.FINISHED):
        """End a run."""
        if run_id in self.runs:
            self.runs[run_id].status = status
            self.runs[run_id].end_time = datetime.now().isoformat()
            self._save_state()

    def log_param(self, run_id: str, key: str, value: Any):
        """Log a parameter."""
        if run_id in self.runs:
            self.runs[run_id].params[key] = str(value)
            self._save_state()

    def log_params(self, run_id: str, params: Dict[str, Any]):
        """Log multiple parameters."""
        for key, value in params.items():
            self.log_param(run_id, key, value)

    def log_metric(
        self,
        run_id: str,
        key: str,
        value: float,
        step: Optional[int] = None
    ):
        """Log a metric."""
        if run_id in self.runs:
            metric = Metric(
                key=key,
                value=value,
                timestamp=datetime.now().isoformat(),
                step=step
            )
            if key not in self.runs[run_id].metrics:
                self.runs[run_id].metrics[key] = []
            self.runs[run_id].metrics[key].append(metric)
            self._save_state()

    def log_metrics(
        self,
        run_id: str,
        metrics: Dict[str, float],
        step: Optional[int] = None
    ):
        """Log multiple metrics."""
        for key, value in metrics.items():
            self.log_metric(run_id, key, value, step)

    def set_tag(self, run_id: str, key: str, value: str):
        """Set a tag on a run."""
        if run_id in self.runs:
            self.runs[run_id].tags[key] = value
            self._save_state()

    def set_tags(self, run_id: str, tags: Dict[str, str]):
        """Set multiple tags."""
        for key, value in tags.items():
            self.set_tag(run_id, key, value)

    # Model Registry
    def register_model(
        self,
        name: str,
        run_id: str,
        description: str = ""
    ) -> ModelVersion:
        """Register a model from a run."""
        # Create or get registered model
        if name not in self.registered_models:
            self.registered_models[name] = RegisteredModel(
                name=name,
                description=description
            )
            self.model_versions[name] = {}

        # Create new version
        model = self.registered_models[name]
        version = len(model.versions) + 1
        model.versions.append(version)

        # Create model version
        mv = ModelVersion(
            name=name,
            version=version,
            run_id=run_id,
            description=description
        )
        self.model_versions[name][version] = mv

        self._save_state()
        return mv

    def transition_model_stage(
        self,
        name: str,
        version: int,
        stage: ModelStage
    ) -> Optional[ModelVersion]:
        """Transition a model version to a new stage."""
        if name in self.model_versions and version in self.model_versions[name]:
            mv = self.model_versions[name][version]
            mv.stage = stage
            mv.last_updated = datetime.now().isoformat()
            self._save_state()
            return mv
        return None

    def get_model_version(
        self,
        name: str,
        version: Optional[int] = None,
        stage: Optional[ModelStage] = None
    ) -> Optional[ModelVersion]:
        """Get a model version by version number or stage."""
        if name not in self.model_versions:
            return None

        if stage:
            # Find model in specified stage
            for v, mv in self.model_versions[name].items():
                if mv.stage == stage:
                    return mv
            return None

        if version:
            return self.model_versions[name].get(version)

        # Return latest version
        if self.model_versions[name]:
            latest = max(self.model_versions[name].keys())
            return self.model_versions[name][latest]
        return None

    # Query and Analysis
    def search_runs(
        self,
        experiment_name: str,
        filter_params: Optional[Dict[str, str]] = None,
        order_by: Optional[str] = None,
        ascending: bool = True
    ) -> List[Run]:
        """Search runs in an experiment."""
        experiment = self.get_experiment(experiment_name)
        if not experiment:
            return []

        runs = [self.runs[rid] for rid in experiment.runs if rid in self.runs]

        # Filter by params
        if filter_params:
            filtered = []
            for run in runs:
                match = all(
                    run.params.get(k) == v
                    for k, v in filter_params.items()
                )
                if match:
                    filtered.append(run)
            runs = filtered

        # Sort by metric
        if order_by:
            def get_metric(run: Run) -> float:
                if order_by in run.metrics and run.metrics[order_by]:
                    return run.metrics[order_by][-1].value
                return float('inf') if ascending else float('-inf')

            runs.sort(key=get_metric, reverse=not ascending)

        return runs

    def compare_runs(
        self,
        run_ids: List[str],
        metrics: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Compare metrics across runs."""
        comparison = {}
        for run_id in run_ids:
            if run_id in self.runs:
                run = self.runs[run_id]
                comparison[run.run_name] = {
                    "run_id": run_id,
                    "params": run.params,
                    "metrics": {}
                }
                for metric in metrics:
                    if metric in run.metrics and run.metrics[metric]:
                        comparison[run.run_name]["metrics"][metric] = \
                            run.metrics[metric][-1].value

        return comparison

    def get_best_run(
        self,
        experiment_name: str,
        metric: str,
        maximize: bool = True
    ) -> Optional[Run]:
        """Get the best run based on a metric."""
        runs = self.search_runs(
            experiment_name,
            order_by=metric,
            ascending=not maximize
        )
        return runs[0] if runs else None


# =============================================================================
# SIMULATION HELPERS
# =============================================================================

def simulate_training_run(
    tracker: ExperimentTracker,
    experiment_name: str,
    run_name: str,
    params: Dict[str, Any],
    epochs: int = 10
) -> Run:
    """Simulate a training run with metrics."""
    run = tracker.start_run(experiment_name, run_name)

    # Log parameters
    tracker.log_params(run.run_id, params)

    # Simulate training
    base_loss = random.uniform(1.0, 2.0)
    base_acc = random.uniform(0.5, 0.7)

    # Learning rate affects convergence
    lr = float(params.get("learning_rate", 0.001))
    lr_factor = 1.0 if lr < 0.01 else 0.8 if lr < 0.1 else 0.5

    for epoch in range(epochs):
        # Simulate loss decrease
        progress = epoch / epochs
        noise = random.uniform(-0.05, 0.05)
        train_loss = base_loss * (1 - progress * 0.7 * lr_factor) + noise
        val_loss = train_loss * random.uniform(1.0, 1.2)

        # Simulate accuracy increase
        train_acc = min(0.99, base_acc + progress * 0.3 * lr_factor + noise)
        val_acc = train_acc * random.uniform(0.95, 1.0)

        tracker.log_metrics(run.run_id, {
            "train_loss": max(0.1, train_loss),
            "val_loss": max(0.1, val_loss),
            "train_accuracy": min(0.99, max(0.5, train_acc)),
            "val_accuracy": min(0.99, max(0.5, val_acc)),
            "learning_rate": lr
        }, step=epoch)

    # Final metrics
    final_val_acc = tracker.runs[run.run_id].metrics["val_accuracy"][-1].value
    tracker.log_metric(run.run_id, "best_val_accuracy", final_val_acc)

    tracker.end_run(run.run_id)
    return tracker.runs[run.run_id]


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_basic_tracking():
    """Demo 1: Basic experiment tracking."""
    print("=" * 70)
    print("DEMO 1: BASIC EXPERIMENT TRACKING")
    print("=" * 70)

    tracker = ExperimentTracker()

    # Overview
    print("\n📋 Experiment Tracking Components:")
    print("-" * 40)
    print("  • Experiments (project containers)")
    print("  • Runs (individual training sessions)")
    print("  • Parameters (hyperparameters)")
    print("  • Metrics (accuracy, loss, etc.)")
    print("  • Tags (metadata)")

    # Create experiment
    print("\n🔧 Creating Experiment: sentiment-classifier")
    print("-" * 40)

    experiment = tracker.get_or_create_experiment(
        "sentiment-classifier",
        "BERT-based sentiment classification"
    )
    print(f"  Experiment ID: {experiment.experiment_id}")
    print(f"  Name: {experiment.name}")
    print(f"  Created: {experiment.created_time}")

    # Run 1: Baseline
    print("\n📊 Run 1: Baseline (BERT-base)")
    print("-" * 40)

    run1 = simulate_training_run(
        tracker,
        "sentiment-classifier",
        "bert-base-baseline",
        {
            "model": "bert-base-uncased",
            "learning_rate": 0.0001,
            "batch_size": 32,
            "epochs": 10,
            "optimizer": "AdamW",
            "dataset_version": "v3.2"
        },
        epochs=10
    )

    tracker.set_tags(run1.run_id, {
        "team": "nlp",
        "owner": "alice",
        "experiment_type": "baseline"
    })

    print(f"  Run ID: {run1.run_id}")
    print(f"  Parameters:")
    for k, v in run1.params.items():
        print(f"    • {k}: {v}")
    print(f"  Final Metrics:")
    print(f"    • val_accuracy: {run1.metrics['val_accuracy'][-1].value:.4f}")
    print(f"    • val_loss: {run1.metrics['val_loss'][-1].value:.4f}")

    # Run 2: Higher learning rate
    print("\n📊 Run 2: Higher Learning Rate")
    print("-" * 40)

    run2 = simulate_training_run(
        tracker,
        "sentiment-classifier",
        "bert-base-high-lr",
        {
            "model": "bert-base-uncased",
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10,
            "optimizer": "AdamW",
            "dataset_version": "v3.2"
        },
        epochs=10
    )

    print(f"  Run ID: {run2.run_id}")
    print(f"  Final val_accuracy: {run2.metrics['val_accuracy'][-1].value:.4f}")

    # Run 3: Larger batch
    print("\n📊 Run 3: Larger Batch Size")
    print("-" * 40)

    run3 = simulate_training_run(
        tracker,
        "sentiment-classifier",
        "bert-base-large-batch",
        {
            "model": "bert-base-uncased",
            "learning_rate": 0.0001,
            "batch_size": 64,
            "epochs": 10,
            "optimizer": "AdamW",
            "dataset_version": "v3.2"
        },
        epochs=10
    )

    print(f"  Run ID: {run3.run_id}")
    print(f"  Final val_accuracy: {run3.metrics['val_accuracy'][-1].value:.4f}")

    # Summary
    print("\n📈 Experiment Summary:")
    print("-" * 60)
    print(f"  {'Run Name':<25} {'LR':<10} {'Batch':<8} {'Val Acc'}")
    print("-" * 60)
    for run in [run1, run2, run3]:
        lr = run.params.get("learning_rate", "N/A")
        batch = run.params.get("batch_size", "N/A")
        acc = run.metrics["val_accuracy"][-1].value
        print(f"  {run.run_name:<25} {lr:<10} {batch:<8} {acc:.4f}")

    print("\n✅ Demo 1 complete!")
    print(f"📂 Data saved to: {STORAGE_DIR}")


def demo_2_hyperparameter_comparison():
    """Demo 2: Hyperparameter search and comparison."""
    print("=" * 70)
    print("DEMO 2: HYPERPARAMETER SEARCH & COMPARISON")
    print("=" * 70)

    tracker = ExperimentTracker()

    # Create HPO experiment
    print("\n🔍 Running Hyperparameter Search")
    print("-" * 40)

    experiment = tracker.get_or_create_experiment(
        "hpo-sentiment-classifier",
        "Hyperparameter optimization for sentiment classifier"
    )

    # Search space
    search_space = {
        "learning_rate": [0.00001, 0.0001, 0.001, 0.01],
        "batch_size": [16, 32, 64],
        "dropout": [0.1, 0.2, 0.3]
    }

    print(f"\n  Search Space:")
    for param, values in search_space.items():
        print(f"    • {param}: {values}")

    # Run grid search (subset)
    print("\n📊 Running 12 experiments...")
    print("-" * 40)

    runs = []
    for lr in search_space["learning_rate"]:
        for batch in [32]:  # Keep batch fixed for demo
            for dropout in [0.2]:  # Keep dropout fixed for demo
                run = simulate_training_run(
                    tracker,
                    "hpo-sentiment-classifier",
                    f"lr={lr}_bs={batch}_do={dropout}",
                    {
                        "learning_rate": lr,
                        "batch_size": batch,
                        "dropout": dropout,
                        "model": "bert-base-uncased",
                        "epochs": 10
                    },
                    epochs=10
                )
                runs.append(run)
                val_acc = run.metrics["val_accuracy"][-1].value
                print(f"  lr={lr:<8} batch={batch:<4} dropout={dropout:<4} → acc={val_acc:.4f}")

    # Find best run
    print("\n🏆 Best Run:")
    print("-" * 40)

    best_run = tracker.get_best_run(
        "hpo-sentiment-classifier",
        "val_accuracy",
        maximize=True
    )

    if best_run:
        print(f"  Run Name: {best_run.run_name}")
        print(f"  Run ID: {best_run.run_id}")
        print(f"  Parameters:")
        for k, v in best_run.params.items():
            print(f"    • {k}: {v}")
        print(f"  Val Accuracy: {best_run.metrics['val_accuracy'][-1].value:.4f}")

    # Comparison table
    print("\n📊 Run Comparison (sorted by val_accuracy):")
    print("-" * 70)
    print(f"  {'Run Name':<35} {'LR':<10} {'Val Acc':<10} {'Val Loss'}")
    print("-" * 70)

    sorted_runs = tracker.search_runs(
        "hpo-sentiment-classifier",
        order_by="val_accuracy",
        ascending=False
    )

    for run in sorted_runs[:10]:
        lr = run.params.get("learning_rate", "N/A")
        acc = run.metrics["val_accuracy"][-1].value
        loss = run.metrics["val_loss"][-1].value
        print(f"  {run.run_name:<35} {lr:<10} {acc:<10.4f} {loss:.4f}")

    # Learning curve visualization (ASCII)
    print("\n📈 Learning Curves (Best vs Worst):")
    print("-" * 40)

    if len(sorted_runs) >= 2:
        best = sorted_runs[0]
        worst = sorted_runs[-1]

        print(f"\n  Best Run ({best.run_name}):")
        print("  Epoch:    0   1   2   3   4   5   6   7   8   9")
        print("  Val Acc: ", end="")
        for m in best.metrics["val_accuracy"]:
            bar_len = int(m.value * 10)
            print(f"{m.value:.2f}", end=" ")
        print()

        print(f"\n  Worst Run ({worst.run_name}):")
        print("  Epoch:    0   1   2   3   4   5   6   7   8   9")
        print("  Val Acc: ", end="")
        for m in worst.metrics["val_accuracy"]:
            print(f"{m.value:.2f}", end=" ")
        print()

    print("\n✅ Demo 2 complete!")


def demo_3_model_registry():
    """Demo 3: Model registry and versioning."""
    print("=" * 70)
    print("DEMO 3: MODEL REGISTRY & VERSIONING")
    print("=" * 70)

    tracker = ExperimentTracker()

    # Overview
    print("\n📋 Model Registry Stages:")
    print("-" * 40)
    print("""
     ┌─────────────┐
     │    None     │  Just registered
     └──────┬──────┘
            │
            ▼
     ┌─────────────┐
     │   Staging   │  Testing & validation
     └──────┬──────┘
            │
      ┌─────┴─────┐
      │           │
      ▼           ▼
  ┌─────────┐ ┌─────────┐
  │Production│ │Archived │
  │ (Active) │ │(Retired)│
  └─────────┘ └─────────┘
""")

    # Create training runs
    print("\n🔧 Training Models for Registry")
    print("-" * 40)

    run1 = simulate_training_run(
        tracker,
        "production-sentiment",
        "model-v1.0",
        {"model": "bert-base", "learning_rate": 0.0001, "version": "1.0"},
        epochs=10
    )
    print(f"  ✅ Model v1.0 trained (acc: {run1.metrics['val_accuracy'][-1].value:.4f})")

    run2 = simulate_training_run(
        tracker,
        "production-sentiment",
        "model-v1.1",
        {"model": "bert-base", "learning_rate": 0.0001, "dropout": 0.2, "version": "1.1"},
        epochs=10
    )
    print(f"  ✅ Model v1.1 trained (acc: {run2.metrics['val_accuracy'][-1].value:.4f})")

    run3 = simulate_training_run(
        tracker,
        "production-sentiment",
        "model-v2.0",
        {"model": "bert-large", "learning_rate": 0.00005, "version": "2.0"},
        epochs=10
    )
    print(f"  ✅ Model v2.0 trained (acc: {run3.metrics['val_accuracy'][-1].value:.4f})")

    # Register models
    print("\n📦 Registering Models")
    print("-" * 40)

    mv1 = tracker.register_model("SentimentClassifier", run1.run_id, "Initial release")
    print(f"  ✅ Registered SentimentClassifier v{mv1.version}")

    mv2 = tracker.register_model("SentimentClassifier", run2.run_id, "Added dropout")
    print(f"  ✅ Registered SentimentClassifier v{mv2.version}")

    mv3 = tracker.register_model("SentimentClassifier", run3.run_id, "BERT-large upgrade")
    print(f"  ✅ Registered SentimentClassifier v{mv3.version}")

    # Transition stages
    print("\n🔄 Transitioning Model Stages")
    print("-" * 40)

    # v1 -> Production (initial release)
    tracker.transition_model_stage("SentimentClassifier", 1, ModelStage.PRODUCTION)
    print(f"  v1: None → Production (initial release)")

    # v2 -> Staging (testing)
    tracker.transition_model_stage("SentimentClassifier", 2, ModelStage.STAGING)
    print(f"  v2: None → Staging (testing)")

    # v2 passes tests, promote to production
    tracker.transition_model_stage("SentimentClassifier", 2, ModelStage.PRODUCTION)
    print(f"  v2: Staging → Production (passed tests)")

    # v1 -> Archive (replaced)
    tracker.transition_model_stage("SentimentClassifier", 1, ModelStage.ARCHIVED)
    print(f"  v1: Production → Archived (replaced)")

    # v3 -> Staging
    tracker.transition_model_stage("SentimentClassifier", 3, ModelStage.STAGING)
    print(f"  v3: None → Staging (new candidate)")

    # Show registry state
    print("\n📊 Model Registry State:")
    print("-" * 60)
    print(f"  {'Version':<10} {'Stage':<15} {'Description':<25} {'Run ID'}")
    print("-" * 60)

    for version in sorted(tracker.model_versions.get("SentimentClassifier", {}).keys()):
        mv = tracker.model_versions["SentimentClassifier"][version]
        run = tracker.runs.get(mv.run_id)
        acc = run.metrics["val_accuracy"][-1].value if run else 0
        print(f"  v{version:<9} {mv.stage.value:<15} {mv.description[:25]:<25} {mv.run_id[:8]}...")

    # Load production model
    print("\n🔍 Loading Models:")
    print("-" * 40)

    prod_model = tracker.get_model_version("SentimentClassifier", stage=ModelStage.PRODUCTION)
    if prod_model:
        print(f"  Production model: v{prod_model.version}")
        print(f"  Run ID: {prod_model.run_id}")

    staging_model = tracker.get_model_version("SentimentClassifier", stage=ModelStage.STAGING)
    if staging_model:
        print(f"  Staging model: v{staging_model.version}")
        print(f"  Run ID: {staging_model.run_id}")

    print("\n✅ Demo 3 complete!")


def demo_4_experiment_analysis():
    """Demo 4: Experiment analysis and insights."""
    print("=" * 70)
    print("DEMO 4: EXPERIMENT ANALYSIS & INSIGHTS")
    print("=" * 70)

    tracker = ExperimentTracker()

    # Run multiple experiments
    print("\n🔬 Running Analysis Experiments")
    print("-" * 40)

    # Different model architectures
    experiments = [
        ("bert-base", {"model": "bert-base", "hidden_size": 768, "params_m": 110}),
        ("bert-large", {"model": "bert-large", "hidden_size": 1024, "params_m": 340}),
        ("distilbert", {"model": "distilbert", "hidden_size": 768, "params_m": 66}),
        ("roberta", {"model": "roberta", "hidden_size": 768, "params_m": 125}),
    ]

    runs = []
    for name, params in experiments:
        params["learning_rate"] = 0.0001
        params["batch_size"] = 32
        params["epochs"] = 10

        run = simulate_training_run(
            tracker,
            "model-comparison",
            name,
            params,
            epochs=10
        )
        runs.append(run)
        acc = run.metrics["val_accuracy"][-1].value
        print(f"  {name:<15} → val_accuracy: {acc:.4f}")

    # Analysis
    print("\n📊 Model Comparison Analysis")
    print("-" * 70)

    # Accuracy vs model size
    print("\n  Accuracy vs Model Size:")
    print("-" * 50)
    print(f"  {'Model':<15} {'Params (M)':<12} {'Val Acc':<10} {'Efficiency'}")
    print("-" * 50)

    for run in runs:
        model = run.params.get("model", "unknown")
        params_m = float(run.params.get("params_m", 100))
        acc = run.metrics["val_accuracy"][-1].value
        efficiency = acc / (params_m / 100)  # Accuracy per 100M params
        print(f"  {model:<15} {params_m:<12} {acc:<10.4f} {efficiency:.4f}")

    # Best model per metric
    print("\n🏆 Best Models:")
    print("-" * 40)

    # By accuracy
    best_acc_run = max(runs, key=lambda r: r.metrics["val_accuracy"][-1].value)
    print(f"  Best Accuracy: {best_acc_run.params['model']} ({best_acc_run.metrics['val_accuracy'][-1].value:.4f})")

    # By efficiency (smallest model with good accuracy)
    efficiency_scores = []
    for run in runs:
        params_m = float(run.params.get("params_m", 100))
        acc = run.metrics["val_accuracy"][-1].value
        efficiency_scores.append((run, acc / params_m))

    best_efficiency = max(efficiency_scores, key=lambda x: x[1])
    print(f"  Best Efficiency: {best_efficiency[0].params['model']} (score: {best_efficiency[1]:.6f})")

    # Statistical analysis
    print("\n📈 Statistical Summary:")
    print("-" * 40)

    accuracies = [r.metrics["val_accuracy"][-1].value for r in runs]
    print(f"  Mean Accuracy: {statistics.mean(accuracies):.4f}")
    print(f"  Std Dev: {statistics.stdev(accuracies):.4f}")
    print(f"  Min: {min(accuracies):.4f}")
    print(f"  Max: {max(accuracies):.4f}")

    # Learning curve analysis
    print("\n📉 Convergence Analysis:")
    print("-" * 40)

    for run in runs:
        model = run.params.get("model", "unknown")
        accs = [m.value for m in run.metrics["val_accuracy"]]

        # Calculate improvement rate
        early_acc = statistics.mean(accs[:3])
        late_acc = statistics.mean(accs[-3:])
        improvement = late_acc - early_acc

        # Convergence (how much variance in last 3 epochs)
        late_variance = statistics.stdev(accs[-3:]) if len(accs[-3:]) > 1 else 0

        converged = "✅" if late_variance < 0.02 else "⚠️"
        print(f"  {model:<15} Improvement: {improvement:+.4f}  Variance: {late_variance:.4f} {converged}")

    print("\n✅ Demo 4 complete!")


def demo_5_full_mlops_workflow():
    """Demo 5: Full MLOps workflow simulation."""
    print("=" * 70)
    print("DEMO 5: FULL MLOPS WORKFLOW")
    print("=" * 70)

    tracker = ExperimentTracker()

    # Workflow overview
    print("\n📋 MLOps Workflow:")
    print("-" * 40)
    print("""
     ┌─────────────────────────────────────────────────────────────────┐
     │                     MLOPS WORKFLOW                              │
     ├─────────────────────────────────────────────────────────────────┤
     │                                                                 │
     │  1. EXPERIMENT     2. VALIDATE       3. REGISTER               │
     │  ┌───────────┐    ┌───────────┐    ┌───────────┐              │
     │  │ Train     │───►│ Compare   │───►│ Register  │              │
     │  │ Multiple  │    │ Metrics   │    │ Best      │              │
     │  │ Models    │    │ Select    │    │ Model     │              │
     │  └───────────┘    └───────────┘    └───────────┘              │
     │                                           │                    │
     │  6. MONITOR       5. DEPLOY         4. VALIDATE               │
     │  ┌───────────┐    ┌───────────┐    ┌───────────┐              │
     │  │ Track     │◄───│ Promote   │◄───│ Stage &   │              │
     │  │ Drift     │    │ to Prod   │    │ Test      │              │
     │  │ Retrain   │    │           │    │           │              │
     │  └───────────┘    └───────────┘    └───────────┘              │
     │                                                                 │
     └─────────────────────────────────────────────────────────────────┘
""")

    # Step 1: Experiment
    print("\n1️⃣ EXPERIMENT PHASE")
    print("-" * 40)
    print("  Training multiple model configurations...")

    configs = [
        {"model": "bert-base", "lr": 0.0001, "dropout": 0.1},
        {"model": "bert-base", "lr": 0.0001, "dropout": 0.2},
        {"model": "bert-base", "lr": 0.00005, "dropout": 0.1},
        {"model": "bert-base", "lr": 0.00005, "dropout": 0.2},
    ]

    runs = []
    for i, config in enumerate(configs):
        run = simulate_training_run(
            tracker,
            "mlops-workflow",
            f"experiment-{i+1}",
            {
                "model": config["model"],
                "learning_rate": config["lr"],
                "dropout": config["dropout"],
                "epochs": 10
            },
            epochs=10
        )
        runs.append(run)
        acc = run.metrics["val_accuracy"][-1].value
        print(f"  Experiment {i+1}: lr={config['lr']}, dropout={config['dropout']} → acc={acc:.4f}")

    # Step 2: Validate & Select
    print("\n2️⃣ VALIDATION PHASE")
    print("-" * 40)

    best_run = tracker.get_best_run("mlops-workflow", "val_accuracy", maximize=True)
    print(f"  Best model: {best_run.run_name}")
    print(f"  Val Accuracy: {best_run.metrics['val_accuracy'][-1].value:.4f}")
    print(f"  Parameters:")
    for k, v in best_run.params.items():
        print(f"    • {k}: {v}")

    # Check if meets threshold
    threshold = 0.75
    best_acc = best_run.metrics["val_accuracy"][-1].value
    if best_acc >= threshold:
        print(f"\n  ✅ Model meets threshold ({best_acc:.4f} >= {threshold})")
    else:
        print(f"\n  ⚠️ Model below threshold ({best_acc:.4f} < {threshold})")

    # Step 3: Register
    print("\n3️⃣ REGISTRATION PHASE")
    print("-" * 40)

    mv = tracker.register_model(
        "ProductionSentiment",
        best_run.run_id,
        f"Best model from workflow (acc={best_acc:.4f})"
    )
    print(f"  ✅ Registered ProductionSentiment v{mv.version}")
    print(f"  Run ID: {mv.run_id}")

    # Step 4: Stage & Test
    print("\n4️⃣ STAGING PHASE")
    print("-" * 40)

    tracker.transition_model_stage("ProductionSentiment", mv.version, ModelStage.STAGING)
    print(f"  ✅ Model transitioned to Staging")

    # Simulate validation tests
    print("\n  Running validation tests...")
    tests = [
        ("Unit tests", True),
        ("Integration tests", True),
        ("Load test (100 req/s)", True),
        ("Latency test (<100ms)", True),
        ("Accuracy on holdout set", True),
    ]

    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"    {test_name}: {status}")
        all_passed = all_passed and passed

    # Step 5: Deploy
    print("\n5️⃣ DEPLOYMENT PHASE")
    print("-" * 40)

    if all_passed:
        tracker.transition_model_stage("ProductionSentiment", mv.version, ModelStage.PRODUCTION)
        print(f"  ✅ Model promoted to Production!")
        print(f"  Model: ProductionSentiment v{mv.version}")
        print(f"  Stage: {ModelStage.PRODUCTION.value}")

        # Simulate deployment
        print("\n  Deployment details:")
        print("    • Endpoint: https://api.example.com/v1/sentiment")
        print("    • Replicas: 3")
        print("    • Traffic: 100%")
    else:
        print("  ❌ Deployment blocked - tests failed")

    # Step 6: Monitor (simulated)
    print("\n6️⃣ MONITORING PHASE")
    print("-" * 40)

    # Simulate production metrics
    print("  Production metrics (last 24h):")
    print("    • Requests: 125,432")
    print("    • Avg latency: 45ms")
    print("    • P99 latency: 89ms")
    print("    • Error rate: 0.02%")
    print("    • Prediction distribution:")
    print("      - Positive: 58%")
    print("      - Negative: 42%")

    # Drift detection (simulated)
    print("\n  Drift detection:")
    print("    • Feature drift: 🟢 Normal")
    print("    • Prediction drift: 🟢 Normal")
    print("    • Accuracy drift: 🟢 Normal")

    # Summary
    print("\n" + "=" * 70)
    print("📊 WORKFLOW SUMMARY")
    print("=" * 70)
    print(f"""
  Experiments run:     {len(runs)}
  Best accuracy:       {best_acc:.4f}
  Model registered:    ProductionSentiment v{mv.version}
  Current stage:       Production
  Validation tests:    {sum(1 for _, p in tests if p)}/{len(tests)} passed
  Deployment status:   ✅ Active
""")

    print("✅ Demo 5 complete!")
    print(f"\n📂 All data saved to: {STORAGE_DIR}")


def show_usage():
    """Show usage information."""
    print("""
ML Experiment Tracker Toolkit
=============================

A local experiment tracking system demonstrating MLOps concepts.

Usage:
    python deliverable_ml_experiment_tracker.py <demo>

Demos:
    demo1   Basic experiment tracking
    demo2   Hyperparameter search & comparison
    demo3   Model registry & versioning
    demo4   Experiment analysis & insights
    demo5   Full MLOps workflow

Examples:
    python deliverable_ml_experiment_tracker.py demo1
    python deliverable_ml_experiment_tracker.py demo5

Output:
    Experiment data saved to .ml_experiment_tracker/
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_basic_tracking,
        "demo2": demo_2_hyperparameter_comparison,
        "demo3": demo_3_model_registry,
        "demo4": demo_4_experiment_analysis,
        "demo5": demo_5_full_mlops_workflow,
    }

    if command in demos:
        demos[command]()
    elif command in ["help", "-h", "--help"]:
        show_usage()
    else:
        print(f"Unknown command: {command}")
        show_usage()


if __name__ == "__main__":
    main()
