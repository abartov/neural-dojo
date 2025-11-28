# Module 48 Deliverable: ML Experiment Tracker

**A local experiment tracking system demonstrating MLOps concepts: experiments, runs, metrics, model registry, and lifecycle management.**

## Features

- **Experiment Management**: Create and organize experiments with runs
- **Parameter & Metric Logging**: Track hyperparameters and training metrics
- **Model Registry**: Version models with lifecycle stages (None → Staging → Production → Archived)
- **Experiment Analysis**: Compare runs, find best models, statistical summaries
- **Full MLOps Workflow**: End-to-end simulation from training to deployment

## Quick Start

```bash
python deliverable_ml_experiment_tracker.py demo1  # Basic experiment tracking
python deliverable_ml_experiment_tracker.py demo2  # Hyperparameter comparison
python deliverable_ml_experiment_tracker.py demo3  # Model registry
python deliverable_ml_experiment_tracker.py demo4  # Experiment analysis
python deliverable_ml_experiment_tracker.py demo5  # Full MLOps workflow
```

## Key Concepts

### Experiment Tracking Hierarchy

```
Project: sentiment-classifier
├── Experiment: baseline
│   ├── Run: bert-base (params, metrics, tags)
│   ├── Run: bert-large
│   └── Run: distilbert
└── Experiment: hyperparameter-search
    ├── Run: lr=0.001_bs=32
    └── Run: lr=0.0001_bs=64
```

### Model Registry Stages

| Stage | Description |
|-------|-------------|
| None | Just registered |
| Staging | Validation & testing |
| Production | Active in production |
| Archived | Retired model |

### MLOps Workflow

```
Experiment → Validate → Register → Stage → Deploy → Monitor
```

## API Reference

```python
tracker = ExperimentTracker()

# Create experiment
exp = tracker.create_experiment("my-experiment")

# Start run
run = tracker.start_run("my-experiment", "run-1")

# Log params and metrics
tracker.log_params(run.run_id, {"lr": 0.001})
tracker.log_metric(run.run_id, "accuracy", 0.95, step=10)

# End run
tracker.end_run(run.run_id)

# Register model
mv = tracker.register_model("MyModel", run.run_id)

# Promote to production
tracker.transition_model_stage("MyModel", 1, ModelStage.PRODUCTION)

# Load production model
prod_model = tracker.get_model_version("MyModel", stage=ModelStage.PRODUCTION)
```

## Generated Data

```
.ml_experiment_tracker/
├── experiments/
│   ├── {exp_id}.json           # Experiment metadata
│   └── run_{run_id}.json       # Run data (params, metrics)
├── registry/
│   ├── {model_name}.json       # Registered model
│   └── {model_name}_v{N}.json  # Model version
└── artifacts/
    └── (model files, plots, etc.)
```

## MLOps Maturity Model

| Level | Description |
|-------|-------------|
| 0 | No MLOps (notebooks, manual) |
| 1 | DevOps but not MLOps |
| 2 | Automated Training (this toolkit!) |
| 3 | Automated Deployment |
| 4 | Full MLOps (continuous training) |

**Time**: ~3 hours | **Lines**: 1,260 | **Author**: Neural Dojo
