# Module 48: MLOps & Experiment Tracking

**Last Updated**: 2025-11-28
**Status**: 🟢 Complete
**Duration**: 6-7 hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master MLflow for experiment tracking and model registry
- Learn Weights & Biases (W&B) for experiment visualization
- Implement model versioning and lifecycle management
- Compare experiments and select best models systematically
- Understand MLOps maturity levels and best practices

---

## 📖 Theory

### The Experiment Tracking Problem

Without proper tracking, ML development becomes chaos:

```
THE ML REPRODUCIBILITY CRISIS
=============================

Without Tracking:
─────────────────
"Which hyperparameters gave us 94% accuracy?"
"Was that model trained on v2 or v3 of the dataset?"
"Who changed the preprocessing pipeline?"
"Can we reproduce last month's best model?"

        ┌─────────┐
        │ model_  │
        │ final.pt│
        └─────────┘
        ┌─────────┐
        │ model_  │
        │final_v2 │
        └─────────┘
        ┌─────────┐
        │ model_  │
        │FINAL_   │
        │ real.pt │
        └─────────┘
        ┌─────────┐
        │ model_  │
        │best_use │
        │_this.pt │
        └─────────┘

With Tracking:
──────────────
Experiment: sentiment-classifier-v2
├── Run 1: lr=0.001, acc=0.89, dataset=v3.2
├── Run 2: lr=0.0001, acc=0.91, dataset=v3.2  ← Best
├── Run 3: lr=0.01, acc=0.85, dataset=v3.2
└── Run 4: lr=0.0001, acc=0.92, dataset=v3.3  ← Production
```

**Did You Know?** A 2019 study found that only 15% of ML papers could be reproduced from their descriptions alone. Google's internal research showed that teams waste an average of 40% of their time on "ML debt" - debugging, versioning, and reproducing experiments. This led to the development of tools like MLflow and TFX.

---

## 1. MLflow: The Open-Source Standard

### What is MLflow?

MLflow is an open-source platform for managing the end-to-end ML lifecycle:

```
MLFLOW COMPONENTS
=================

┌─────────────────────────────────────────────────────────────────────┐
│                           MLFLOW                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │    Tracking     │  │    Projects     │  │     Models      │    │
│  │                 │  │                 │  │                 │    │
│  │ • Parameters    │  │ • Reproducible  │  │ • Model Format  │    │
│  │ • Metrics       │  │   packaging     │  │ • Deployment    │    │
│  │ • Artifacts     │  │ • Dependencies  │  │ • Serving       │    │
│  │ • Source code   │  │ • Entry points  │  │ • Flavors       │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Model Registry                          │   │
│  │                                                              │   │
│  │  • Model versioning    • Stage transitions                  │   │
│  │  • Annotations         • Webhooks/Automation                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Basic Experiment Tracking

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# Set experiment
mlflow.set_experiment("sentiment-classifier")

# Start a run
with mlflow.start_run(run_name="random-forest-baseline"):
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("dataset_version", "v3.2")

    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)

    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average='weighted')

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("train_samples", len(X_train))

    # Log model
    mlflow.sklearn.log_model(model, "model")

    # Log artifacts (plots, data samples, etc.)
    mlflow.log_artifact("confusion_matrix.png")

    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

### Tracking Server Architecture

```
MLFLOW TRACKING ARCHITECTURE
============================

                    ┌─────────────────────────────┐
                    │      MLflow UI              │
                    │   http://localhost:5000     │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │    MLflow Tracking Server   │
                    │         (API)               │
                    └─────────────┬───────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
     ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
     │  Backend Store  │ │ Artifact Store  │ │  Model Registry │
     │   (Metadata)    │ │   (Files)       │ │   (Versions)    │
     │                 │ │                 │ │                 │
     │ • SQLite        │ │ • Local files   │ │ • Staging       │
     │ • PostgreSQL    │ │ • S3            │ │ • Production    │
     │ • MySQL         │ │ • GCS           │ │ • Archived      │
     │                 │ │ • Azure Blob    │ │                 │
     └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Autologging

MLflow can automatically log parameters and metrics for popular frameworks:

```python
import mlflow
import mlflow.pytorch

# Enable autologging for PyTorch
mlflow.pytorch.autolog()

# Now training automatically logs:
# - Model architecture
# - Optimizer parameters
# - Loss curves
# - Model checkpoints
trainer = Trainer(model, train_loader, val_loader)
trainer.train(epochs=10)
```

**Supported Frameworks**:
- scikit-learn
- PyTorch / PyTorch Lightning
- TensorFlow / Keras
- XGBoost / LightGBM
- Hugging Face Transformers
- FastAI
- Spark MLlib

**Did You Know?** MLflow was created by Databricks in 2018 and open-sourced immediately. The name comes from "Machine Learning flow." Within 2 years, it became the most popular open-source MLOps tool with over 10,000 GitHub stars. Today, MLflow is governed by the Linux Foundation and is used by companies like Microsoft, Facebook, and Uber.

### Model Registry

The Model Registry provides model versioning and lifecycle management:

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register a model
model_uri = f"runs:/{run_id}/model"
model_version = mlflow.register_model(model_uri, "SentimentClassifier")

# Add description
client.update_model_version(
    name="SentimentClassifier",
    version=model_version.version,
    description="BERT-based sentiment classifier trained on v3.2 dataset"
)

# Transition to staging
client.transition_model_version_stage(
    name="SentimentClassifier",
    version=model_version.version,
    stage="Staging"
)

# After validation, promote to production
client.transition_model_version_stage(
    name="SentimentClassifier",
    version=model_version.version,
    stage="Production"
)
```

### Model Lifecycle

```
MODEL REGISTRY STAGES
=====================

    ┌─────────────┐
    │    None     │  Model just registered
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Staging   │  Validation & testing
    └──────┬──────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Production│ │Archived │
│(Active)  │ │(Retired)│
└─────────┘ └─────────┘

Stage Transitions:
  None → Staging:       Model ready for testing
  Staging → Production: Passed all validation
  Production → Staging: Rolling back
  Any → Archived:       Model retired
```

### Loading Models from Registry

```python
import mlflow.pyfunc

# Load latest production model
model = mlflow.pyfunc.load_model(
    model_uri="models:/SentimentClassifier/Production"
)

# Load specific version
model_v2 = mlflow.pyfunc.load_model(
    model_uri="models:/SentimentClassifier/2"
)

# Inference
predictions = model.predict(input_data)
```

---

## 2. Weights & Biases (W&B)

### What is W&B?

Weights & Biases is a commercial MLOps platform with powerful visualization and collaboration features:

```
W&B COMPONENTS
==============

┌─────────────────────────────────────────────────────────────────────┐
│                     WEIGHTS & BIASES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │    Experiments  │  │     Sweeps      │  │    Artifacts    │    │
│  │                 │  │                 │  │                 │    │
│  │ • Real-time     │  │ • Hyperparameter│  │ • Dataset       │    │
│  │   logging       │  │   optimization  │  │   versioning    │    │
│  │ • Interactive   │  │ • Bayesian      │  │ • Model         │    │
│  │   charts        │  │   search        │  │   versioning    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │     Tables      │  │     Reports     │  │     Launch      │    │
│  │                 │  │                 │  │                 │    │
│  │ • Data viz      │  │ • Shareable     │  │ • Job queuing   │    │
│  │ • Comparisons   │  │   notebooks     │  │ • Compute       │    │
│  │ • Filtering     │  │ • Collaboration │  │   management    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Basic W&B Logging

```python
import wandb
import torch
import torch.nn as nn

# Initialize run
wandb.init(
    project="sentiment-classifier",
    config={
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32,
        "architecture": "BERT-base",
        "dataset": "sentiment-v3.2"
    }
)

# Training loop with logging
for epoch in range(wandb.config.epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        # Forward pass
        output = model(data)
        loss = criterion(output, target)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Log metrics
        wandb.log({
            "train_loss": loss.item(),
            "epoch": epoch,
            "batch": batch_idx
        })

    # Log validation metrics
    val_loss, val_acc = evaluate(model, val_loader)
    wandb.log({
        "val_loss": val_loss,
        "val_accuracy": val_acc,
        "epoch": epoch
    })

# Save model artifact
artifact = wandb.Artifact("model", type="model")
artifact.add_file("model.pt")
wandb.log_artifact(artifact)

wandb.finish()
```

**Did You Know?** Weights & Biases was founded in 2017 by Lukas Biewald, who previously founded CrowdFlower (now Figure Eight). The name comes from the fundamental parameters in neural networks - weights and biases. W&B raised $200M in Series C funding in 2022 at a $1B valuation. OpenAI, NVIDIA, and Toyota Research all use W&B for their ML experiments.

### W&B Sweeps (Hyperparameter Optimization)

```python
import wandb

# Define sweep configuration
sweep_config = {
    "method": "bayes",  # bayes, random, grid
    "metric": {
        "name": "val_accuracy",
        "goal": "maximize"
    },
    "parameters": {
        "learning_rate": {
            "min": 0.0001,
            "max": 0.1,
            "distribution": "log_uniform_values"
        },
        "batch_size": {
            "values": [16, 32, 64, 128]
        },
        "hidden_size": {
            "min": 64,
            "max": 512,
            "distribution": "int_uniform"
        },
        "dropout": {
            "min": 0.1,
            "max": 0.5
        }
    },
    "early_terminate": {
        "type": "hyperband",
        "min_iter": 3
    }
}

# Create sweep
sweep_id = wandb.sweep(sweep_config, project="sentiment-classifier")

# Define training function
def train():
    wandb.init()

    model = build_model(
        hidden_size=wandb.config.hidden_size,
        dropout=wandb.config.dropout
    )

    # Training code...
    for epoch in range(10):
        train_epoch(model, wandb.config.learning_rate, wandb.config.batch_size)
        val_acc = evaluate(model)
        wandb.log({"val_accuracy": val_acc})

# Run sweep
wandb.agent(sweep_id, train, count=50)
```

### W&B Tables for Data Visualization

```python
import wandb
import pandas as pd

# Create a table with predictions
table = wandb.Table(columns=["text", "true_label", "predicted", "confidence"])

for text, true, pred, conf in predictions:
    table.add_data(text, true, pred, conf)

wandb.log({"predictions": table})

# Log confusion matrix
wandb.log({
    "confusion_matrix": wandb.plot.confusion_matrix(
        y_true=y_true,
        preds=y_pred,
        class_names=["negative", "positive"]
    )
})

# Log PR curve
wandb.log({
    "pr_curve": wandb.plot.pr_curve(
        y_true=y_true,
        y_probas=y_probas,
        labels=["negative", "positive"]
    )
})
```

---

## 3. MLflow vs W&B Comparison

### Feature Comparison

```
MLFLOW vs W&B
=============

┌──────────────────────┬─────────────────────┬─────────────────────┐
│      Feature         │       MLflow        │         W&B         │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ Open Source          │ ✅ Yes              │ ⚠️ Partial          │
│ Self-hosted          │ ✅ Yes              │ ✅ Yes (Enterprise) │
│ Free tier            │ ✅ Unlimited        │ ✅ 100GB storage    │
│ Real-time logging    │ ⚠️ Polling          │ ✅ Streaming        │
│ Visualization        │ ⚠️ Basic            │ ✅ Advanced         │
│ Collaboration        │ ⚠️ Basic            │ ✅ Teams, Reports   │
│ HPO built-in         │ ❌ No               │ ✅ Sweeps           │
│ Model Registry       │ ✅ Yes              │ ✅ Yes (Artifacts)  │
│ Model Serving        │ ✅ Yes              │ ❌ No               │
│ Framework Integrations│ ✅ Extensive       │ ✅ Extensive        │
│ Learning Curve       │ ⚠️ Medium           │ ✅ Easy             │
└──────────────────────┴─────────────────────┴─────────────────────┘

When to Use What:
─────────────────
MLflow:
  • Self-hosted requirement
  • Model serving needed
  • Full lifecycle management
  • Cost-sensitive teams

W&B:
  • Best-in-class visualization
  • Team collaboration
  • Hyperparameter sweeps
  • Quick setup needed
```

---

## 4. Experiment Organization Best Practices

### Project Structure

```
EXPERIMENT ORGANIZATION
=======================

Project: sentiment-classifier
├── Experiment: baseline
│   ├── Run: logistic-regression
│   ├── Run: random-forest
│   └── Run: naive-bayes
│
├── Experiment: bert-experiments
│   ├── Run: bert-base-uncased
│   ├── Run: bert-large-uncased
│   ├── Run: distilbert
│   └── Run: roberta-base
│
├── Experiment: hyperparameter-search
│   ├── Run: sweep-2024-01-15-001
│   ├── Run: sweep-2024-01-15-002
│   └── ... (50 runs)
│
└── Experiment: production-candidates
    ├── Run: candidate-v1.0
    ├── Run: candidate-v1.1
    └── Run: candidate-v1.2
```

### Tagging Strategy

```python
# Good tagging practices
mlflow.set_tags({
    # Experiment metadata
    "experiment_type": "hyperparameter_search",
    "team": "nlp",
    "owner": "alice@company.com",

    # Data information
    "dataset_version": "v3.2",
    "data_split": "stratified",
    "train_samples": "50000",

    # Model information
    "model_family": "transformer",
    "model_size": "base",
    "pretrained": "true",

    # Environment
    "gpu": "A100",
    "framework_version": "pytorch-2.0",

    # Status
    "status": "validated",
    "deployed": "false"
})
```

### Metric Logging Guidelines

```python
# Step-level metrics (logged frequently)
for step, batch in enumerate(train_loader):
    loss = train_step(batch)
    mlflow.log_metric("train_loss", loss, step=step)

# Epoch-level metrics
for epoch in range(num_epochs):
    train_metrics = train_epoch()
    val_metrics = evaluate()

    mlflow.log_metrics({
        "train_loss": train_metrics["loss"],
        "train_accuracy": train_metrics["accuracy"],
        "val_loss": val_metrics["loss"],
        "val_accuracy": val_metrics["accuracy"],
        "learning_rate": get_lr(optimizer)
    }, step=epoch)

# Final metrics (logged once)
mlflow.log_metrics({
    "best_val_accuracy": best_accuracy,
    "total_training_time": training_time,
    "final_model_size_mb": model_size
})
```

---

## 5. MLOps Maturity Model

### Maturity Levels

```
MLOPS MATURITY MODEL
====================

Level 0: No MLOps
─────────────────
• Manual, script-driven process
• No experiment tracking
• Jupyter notebooks in production
• Model versioning via file names

Level 1: DevOps but not MLOps
────────────────────────────
• Version control for code
• Basic CI/CD for deployment
• Manual model training
• No experiment tracking

Level 2: Automated Training
──────────────────────────
• Experiment tracking (MLflow/W&B)
• Automated training pipelines
• Model registry
• Manual deployment

Level 3: Automated Deployment
────────────────────────────
• CI/CD for models
• Automated testing (data + model)
• A/B testing / Canary deployments
• Manual monitoring

Level 4: Full MLOps
──────────────────
• Continuous training
• Automated retraining triggers
• Model monitoring & drift detection
• Automated rollback
• Feature store integration
```

**Did You Know?** Google published their MLOps maturity model in 2021, describing how they evolved from "ML code is a small fraction of real ML systems" to fully automated systems. They estimated that Level 0 to Level 2 represents 95% of organizations, with only 5% achieving Level 3 or higher. The journey from Level 0 to Level 4 typically takes 2-4 years.

---

## 6. Production Experiment Tracking Setup

### MLflow Production Architecture

```yaml
# docker-compose.yml for MLflow
version: '3.8'

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.0
    ports:
      - "5000:5000"
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://user:pass@postgres:5432/mlflow
      - MLFLOW_ARTIFACT_ROOT=s3://mlflow-artifacts/
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri postgresql://user:pass@postgres:5432/mlflow
      --default-artifact-root s3://mlflow-artifacts/
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mlflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Client Configuration

```python
import mlflow
import os

# Configure MLflow client
mlflow.set_tracking_uri("http://mlflow-server:5000")

# Or via environment variable
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-server:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"  # If using MinIO

# Now all logging goes to the server
with mlflow.start_run():
    mlflow.log_param("model", "bert-base")
    mlflow.log_metric("accuracy", 0.95)
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Set Up MLflow Tracking

```bash
# Install MLflow
pip install mlflow

# Start local tracking server
mlflow server --host 0.0.0.0 --port 5000

# In another terminal, run experiments
python train.py
```

### Exercise 2: Create W&B Experiment

```python
# Install wandb
pip install wandb

# Login
wandb login

# Run training with logging
python train_with_wandb.py
```

### Exercise 3: Implement Model Registry Workflow

```python
# Register model
mlflow.register_model(f"runs:/{run_id}/model", "MyModel")

# Promote through stages
client.transition_model_version_stage("MyModel", 1, "Staging")
# After testing...
client.transition_model_version_stage("MyModel", 1, "Production")
```

---

## 📚 Further Reading

### Documentation
- [MLflow Documentation](https://mlflow.org/docs/latest/)
- [Weights & Biases Docs](https://docs.wandb.ai/)
- [MLflow Model Registry Guide](https://mlflow.org/docs/latest/model-registry.html)

### Papers & Articles
- "Hidden Technical Debt in Machine Learning Systems" (Google, 2015)
- "MLOps: Continuous Delivery and Automation Pipelines" (Google, 2021)
- "Challenges in Deploying Machine Learning" (Paleyes et al., 2022)

---

## ✅ Knowledge Check

1. **What are the four main components of MLflow?**

2. **When would you choose W&B over MLflow?**

3. **What are the stages in MLflow Model Registry?**

4. **How does W&B Sweeps differ from Katib?**

5. **What is MLOps Level 3 and what does it require?**

---

## ⏭️ Next Steps

You now understand experiment tracking and model registry! These are essential for reproducible ML.

**Up Next**: Module 49 - Data Versioning & Feature Stores (DVC, Feast)

---

_Module 48 Complete! You now understand MLflow and W&B!_
_"What gets measured gets managed. What gets tracked gets improved."_
