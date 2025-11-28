# Module 47: Advanced Kubernetes for AI/ML

**Last Updated**: 2025-11-28
**Status**: 🟢 Complete
**Duration**: 8-9 hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master Kubeflow for end-to-end ML workflows
- Implement KServe for production model serving
- Deploy Ray clusters on Kubernetes for distributed computing
- Use NVIDIA Triton Inference Server for high-performance inference
- Understand when to use each tool and their trade-offs

---

## 📖 Theory

### The ML Platform Stack on Kubernetes

In Module 46, you learned Kubernetes fundamentals. Now we build the ML platform layer on top:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ML PLATFORM LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Kubeflow   │  │    KServe    │  │     Ray      │              │
│  │  (Pipelines) │  │  (Serving)   │  │ (Distributed)│              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │    Triton    │  │    Seldon    │  │   MLflow     │              │
│  │ (Inference)  │  │   (Serving)  │  │  (Tracking)  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
├─────────────────────────────────────────────────────────────────────┤
│                     KUBERNETES LAYER                                │
│  Pods | Services | Deployments | Jobs | HPA | PVC | GPU Scheduling │
├─────────────────────────────────────────────────────────────────────┤
│                     INFRASTRUCTURE                                  │
│  Cloud VMs | Bare Metal | GPU Nodes | Storage | Networking          │
└─────────────────────────────────────────────────────────────────────┘
```

**Did You Know?** Google developed Kubeflow in 2017 when they realized their internal ML platform (TFX) was too tightly coupled to Google infrastructure. The name combines "Kubernetes" and "flow" (as in TensorFlow). By 2023, Kubeflow had become the de facto standard for ML on Kubernetes, with over 10,000 GitHub stars and adoption by companies like Spotify, Bloomberg, and Uber.

---

## 1. Kubeflow: End-to-End ML Platform

### What is Kubeflow?

Kubeflow is an open-source ML platform that makes deploying ML workflows on Kubernetes simple, portable, and scalable.

```
KUBEFLOW COMPONENTS
===================

┌─────────────────────────────────────────────────────────────────┐
│                        KUBEFLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Pipelines  │  │  Notebooks  │  │   Katib     │             │
│  │   (DAGs)    │  │  (Jupyter)  │  │(AutoML/HPO) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Training   │  │   KServe    │  │   Central   │             │
│  │  Operators  │  │  (Serving)  │  │  Dashboard  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Kubeflow Pipelines

Pipelines are the heart of Kubeflow - they let you define ML workflows as code.

```python
# Kubeflow Pipeline Example
from kfp import dsl
from kfp.dsl import component, Output, Input, Dataset, Model

@component(
    base_image="python:3.10",
    packages_to_install=["pandas", "scikit-learn"]
)
def preprocess_data(
    raw_data: Input[Dataset],
    processed_data: Output[Dataset]
):
    """Preprocess raw data for training."""
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(raw_data.path)

    # Feature engineering
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)

    pd.DataFrame(df_scaled).to_csv(processed_data.path, index=False)

@component(
    base_image="python:3.10",
    packages_to_install=["pandas", "scikit-learn", "joblib"]
)
def train_model(
    training_data: Input[Dataset],
    model: Output[Model],
    n_estimators: int = 100
):
    """Train a RandomForest model."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import joblib

    df = pd.read_csv(training_data.path)
    X = df.drop('target', axis=1)
    y = df['target']

    clf = RandomForestClassifier(n_estimators=n_estimators)
    clf.fit(X, y)

    joblib.dump(clf, model.path)

@component(
    base_image="python:3.10",
    packages_to_install=["pandas", "scikit-learn", "joblib"]
)
def evaluate_model(
    model: Input[Model],
    test_data: Input[Dataset]
) -> float:
    """Evaluate model accuracy."""
    import pandas as pd
    from sklearn.metrics import accuracy_score
    import joblib

    clf = joblib.load(model.path)
    df = pd.read_csv(test_data.path)
    X = df.drop('target', axis=1)
    y = df['target']

    predictions = clf.predict(X)
    return accuracy_score(y, predictions)

@dsl.pipeline(
    name="ML Training Pipeline",
    description="End-to-end ML training pipeline"
)
def ml_pipeline(n_estimators: int = 100):
    """Define the ML pipeline DAG."""

    # Step 1: Preprocess
    preprocess_task = preprocess_data(
        raw_data=dsl.importer(
            artifact_uri="gs://my-bucket/raw-data.csv",
            artifact_class=Dataset
        )
    )

    # Step 2: Train (depends on preprocess)
    train_task = train_model(
        training_data=preprocess_task.outputs["processed_data"],
        n_estimators=n_estimators
    )

    # Step 3: Evaluate (depends on train)
    evaluate_task = evaluate_model(
        model=train_task.outputs["model"],
        test_data=preprocess_task.outputs["processed_data"]
    )
```

### Pipeline Visualization

```
KUBEFLOW PIPELINE DAG
=====================

     ┌───────────────┐
     │  Raw Data     │
     │  (GCS/S3)     │
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │  Preprocess   │
     │  Component    │
     └───────┬───────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
┌─────────┐    ┌─────────┐
│  Train  │    │  Test   │
│  Data   │    │  Data   │
└────┬────┘    └────┬────┘
     │              │
     ▼              │
┌─────────┐        │
│  Train  │        │
│  Model  │        │
└────┬────┘        │
     │              │
     └──────┬───────┘
            │
            ▼
     ┌───────────────┐
     │   Evaluate    │
     │   Accuracy    │
     └───────────────┘
```

**Did You Know?** Kubeflow Pipelines was inspired by Apache Airflow, but designed specifically for ML. The key insight was that ML workflows need artifact tracking (models, datasets) built-in, not just task orchestration. Jeremy Lewi, one of Kubeflow's creators at Google, said: "We realized ML engineers were spending 80% of their time on infrastructure, not actual ML."

### Katib: Hyperparameter Optimization

Katib is Kubeflow's AutoML component for hyperparameter tuning.

```yaml
# Katib Experiment for Hyperparameter Search
apiVersion: kubeflow.org/v1beta1
kind: Experiment
metadata:
  name: random-search-experiment
  namespace: kubeflow
spec:
  objective:
    type: maximize
    goal: 0.99
    objectiveMetricName: accuracy
  algorithm:
    algorithmName: random
  parallelTrialCount: 3
  maxTrialCount: 12
  maxFailedTrialCount: 3
  parameters:
    - name: learning_rate
      parameterType: double
      feasibleSpace:
        min: "0.001"
        max: "0.1"
    - name: batch_size
      parameterType: int
      feasibleSpace:
        min: "16"
        max: "128"
    - name: num_layers
      parameterType: int
      feasibleSpace:
        min: "2"
        max: "5"
  trialTemplate:
    primaryContainerName: training-container
    trialParameters:
      - name: learningRate
        reference: learning_rate
      - name: batchSize
        reference: batch_size
      - name: numLayers
        reference: num_layers
    trialSpec:
      apiVersion: batch/v1
      kind: Job
      spec:
        template:
          spec:
            containers:
              - name: training-container
                image: myregistry/trainer:latest
                command:
                  - python
                  - train.py
                  - --lr=${trialParameters.learningRate}
                  - --batch-size=${trialParameters.batchSize}
                  - --num-layers=${trialParameters.numLayers}
                resources:
                  limits:
                    nvidia.com/gpu: 1
            restartPolicy: Never
```

### Katib Search Algorithms

```
KATIB ALGORITHMS
================

RANDOM SEARCH
  ┌─────────────────────────────────┐
  │ • • •   •  •    • •  •   •     │  Simple, parallelizable
  │   •  •    •  • •   •    • •    │  Good baseline
  │ •   •  •   •    • •  •    •    │
  └─────────────────────────────────┘

GRID SEARCH
  ┌─────────────────────────────────┐
  │ • • • • • • • • • • • • • • •  │  Exhaustive but expensive
  │ • • • • • • • • • • • • • • •  │  O(n^d) complexity
  │ • • • • • • • • • • • • • • •  │
  └─────────────────────────────────┘

BAYESIAN OPTIMIZATION
  ┌─────────────────────────────────┐
  │         • •                     │  Smart sampling
  │       •     •                   │  Uses surrogate model
  │     •         •   • •           │  Best for expensive evals
  └─────────────────────────────────┘

HYPERBAND / ASHA
  ┌─────────────────────────────────┐
  │ Round 1: ████████████████████   │  Early stopping
  │ Round 2: ████████████           │  Prune bad configs
  │ Round 3: ██████                 │  Efficient resource use
  │ Round 4: ███                    │
  └─────────────────────────────────┘
```

---

## 2. KServe: Production Model Serving

### What is KServe?

KServe (formerly KFServing) provides serverless inference on Kubernetes with autoscaling, canary deployments, and multi-framework support.

```
KSERVE ARCHITECTURE
===================

                    ┌─────────────────────────────────┐
                    │         Istio Gateway           │
                    └───────────────┬─────────────────┘
                                    │
                    ┌───────────────┴─────────────────┐
                    │         KServe Controller       │
                    └───────────────┬─────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   Predictor   │         │  Transformer  │         │   Explainer   │
│   (Model)     │         │ (Pre/Post)    │         │   (SHAP)      │
└───────────────┘         └───────────────┘         └───────────────┘
        │                           │                           │
        │           KNATIVE SERVING (Autoscale)                │
        └───────────────────────────┴───────────────────────────┘
```

### InferenceService Definition

```yaml
# KServe InferenceService
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
  namespace: ml-serving
spec:
  predictor:
    # Model framework (auto-detected server)
    sklearn:
      storageUri: "gs://my-bucket/models/sklearn/iris"
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
        limits:
          cpu: 1
          memory: 1Gi

    # Autoscaling configuration
    minReplicas: 1
    maxReplicas: 10
    scaleTarget: 10  # Concurrent requests per replica
    scaleMetric: concurrency
```

### Multi-Framework Support

```yaml
# PyTorch Model
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: pytorch-cifar10
spec:
  predictor:
    pytorch:
      storageUri: "gs://my-bucket/models/pytorch/cifar10"
      resources:
        limits:
          nvidia.com/gpu: 1

---
# TensorFlow Model
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: tensorflow-flowers
spec:
  predictor:
    tensorflow:
      storageUri: "gs://my-bucket/models/tensorflow/flowers"
      runtimeVersion: "2.13.0"

---
# XGBoost Model
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: xgboost-credit
spec:
  predictor:
    xgboost:
      storageUri: "gs://my-bucket/models/xgboost/credit"

---
# Hugging Face Transformers
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: bert-sentiment
spec:
  predictor:
    model:
      modelFormat:
        name: huggingface
      storageUri: "gs://my-bucket/models/bert-sentiment"
      resources:
        limits:
          nvidia.com/gpu: 1
```

**Did You Know?** KServe was originally called KFServing (Kubeflow Serving) but was renamed in 2021 to reflect that it had grown beyond Kubeflow. The project now has its own governance under the Linux Foundation AI & Data. Companies like Bloomberg and IBM use KServe to serve thousands of models in production.

### Canary Deployments

```yaml
# Canary Deployment with Traffic Split
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sentiment-classifier
spec:
  predictor:
    # Canary version (10% traffic)
    canaryTrafficPercent: 10
    pytorch:
      storageUri: "gs://my-bucket/models/sentiment-v2"
      resources:
        limits:
          nvidia.com/gpu: 1

  # Previous version (90% traffic)
  # Automatically managed by KServe
```

```
CANARY DEPLOYMENT FLOW
======================

     100% traffic                    90%/10% split
         │                               │
         ▼                               ▼
    ┌─────────┐                 ┌─────────────────┐
    │ Model   │      ───►       │  ┌─────────┐   │
    │  v1     │                 │  │ Model   │90%│
    └─────────┘                 │  │  v1     │◄──┤
                                │  └─────────┘   │
                                │  ┌─────────┐   │
                                │  │ Model   │10%│
                                │  │  v2     │◄──┤
                                │  └─────────┘   │
                                └─────────────────┘
                                         │
                                         ▼
                                Gradual rollout
                                  20% → 50% → 100%
```

### Transformers (Pre/Post Processing)

```yaml
# InferenceService with Transformer
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: image-classifier
spec:
  # Pre-processing transformer
  transformer:
    containers:
      - name: image-transformer
        image: myregistry/image-transformer:latest
        resources:
          requests:
            cpu: 100m
            memory: 256Mi

  # Main predictor
  predictor:
    pytorch:
      storageUri: "gs://my-bucket/models/resnet50"
      resources:
        limits:
          nvidia.com/gpu: 1
```

```
TRANSFORMER PIPELINE
====================

Request     ┌─────────────┐     ┌─────────────┐     Response
   ───────► │ Transformer │────►│  Predictor  │────────►
            │ (Preprocess)│     │   (Model)   │
            │             │◄────│             │
            │(Postprocess)│     │             │
            └─────────────┘     └─────────────┘

Example Flow:
1. Receive image URL
2. Transformer: Download, resize, normalize
3. Predictor: Run inference
4. Transformer: Format response, add metadata
```

---

## 3. Ray on Kubernetes: Distributed Computing

### What is Ray?

Ray is a distributed computing framework that makes it easy to scale Python applications. On Kubernetes, Ray enables distributed training, hyperparameter tuning, and serving.

```
RAY ARCHITECTURE
================

┌─────────────────────────────────────────────────────────────────┐
│                         RAY CLUSTER                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                                           │
│  │   HEAD NODE     │   GCS (Global Control Store)              │
│  │  ┌───────────┐  │   - Actor registry                        │
│  │  │ Raylet    │  │   - Object directory                      │
│  │  │ GCS       │  │   - Placement groups                      │
│  │  │ Dashboard │  │                                           │
│  │  └───────────┘  │                                           │
│  └────────┬────────┘                                           │
│           │                                                     │
│  ┌────────┴────────┬────────────────┬────────────────┐         │
│  │                 │                │                │         │
│  ▼                 ▼                ▼                ▼         │
│ ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│ │ Worker  │    │ Worker  │    │ Worker  │    │ Worker  │      │
│ │ Node 1  │    │ Node 2  │    │ Node 3  │    │ Node 4  │      │
│ │ (GPU)   │    │ (GPU)   │    │ (GPU)   │    │ (GPU)   │      │
│ └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### RayCluster on Kubernetes

```yaml
# RayCluster Custom Resource
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ml-ray-cluster
  namespace: ray-system
spec:
  rayVersion: '2.7.0'

  # Head node configuration
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      num-cpus: '0'  # Head doesn't run tasks
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray-ml:2.7.0-py310-gpu
            ports:
              - containerPort: 6379  # GCS
              - containerPort: 8265  # Dashboard
              - containerPort: 10001 # Client
            resources:
              requests:
                cpu: 2
                memory: 8Gi
              limits:
                cpu: 4
                memory: 16Gi

  # Worker node configuration
  workerGroupSpecs:
    - groupName: gpu-workers
      replicas: 4
      minReplicas: 1
      maxReplicas: 10
      rayStartParams:
        num-gpus: '1'
      template:
        spec:
          containers:
            - name: ray-worker
              image: rayproject/ray-ml:2.7.0-py310-gpu
              resources:
                requests:
                  cpu: 4
                  memory: 16Gi
                limits:
                  cpu: 8
                  memory: 32Gi
                  nvidia.com/gpu: 1
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule
```

**Did You Know?** Ray was created at UC Berkeley's RISELab by Robert Nishihara and Philipp Moritz. The name "Ray" refers to a ray of light, symbolizing how tasks "fan out" across a cluster. Anyscale, the company behind Ray, raised $100M in Series C funding in 2021. OpenAI uses Ray for distributed training of their largest models.

### Ray Train: Distributed Training

```python
# Distributed PyTorch Training with Ray Train
import ray
from ray import train
from ray.train.torch import TorchTrainer
from ray.train import ScalingConfig
import torch
import torch.nn as nn

def train_func():
    """Training function executed on each worker."""
    # Get distributed context
    rank = train.get_context().get_world_rank()
    world_size = train.get_context().get_world_size()

    # Model
    model = nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 10)
    )

    # Wrap for distributed training
    model = train.torch.prepare_model(model)

    # DataLoader
    train_loader = get_train_dataloader()
    train_loader = train.torch.prepare_data_loader(train_loader)

    # Training loop
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(10):
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

        # Report metrics
        train.report({"loss": loss.item(), "epoch": epoch})

# Create trainer
trainer = TorchTrainer(
    train_func,
    scaling_config=ScalingConfig(
        num_workers=4,
        use_gpu=True,
        resources_per_worker={"CPU": 4, "GPU": 1}
    )
)

# Run distributed training
result = trainer.fit()
print(f"Final loss: {result.metrics['loss']}")
```

### Ray Tune: Hyperparameter Tuning

```python
# Hyperparameter Tuning with Ray Tune
from ray import tune
from ray.tune.schedulers import ASHAScheduler
from ray.tune.search.optuna import OptunaSearch

def trainable(config):
    """Training function with hyperparameters."""
    model = build_model(
        hidden_size=config["hidden_size"],
        num_layers=config["num_layers"],
        dropout=config["dropout"]
    )

    for epoch in range(100):
        loss = train_epoch(model, config["lr"], config["batch_size"])
        accuracy = evaluate(model)

        # Report to Ray Tune
        tune.report(loss=loss, accuracy=accuracy)

# Search space
search_space = {
    "lr": tune.loguniform(1e-5, 1e-2),
    "batch_size": tune.choice([16, 32, 64, 128]),
    "hidden_size": tune.choice([64, 128, 256, 512]),
    "num_layers": tune.randint(2, 6),
    "dropout": tune.uniform(0.1, 0.5)
}

# ASHA Scheduler (early stopping)
scheduler = ASHAScheduler(
    max_t=100,
    grace_period=10,
    reduction_factor=2
)

# Optuna search algorithm
search_alg = OptunaSearch(metric="accuracy", mode="max")

# Run tuning
analysis = tune.run(
    trainable,
    config=search_space,
    num_samples=50,
    scheduler=scheduler,
    search_alg=search_alg,
    resources_per_trial={"cpu": 4, "gpu": 1}
)

print(f"Best config: {analysis.best_config}")
print(f"Best accuracy: {analysis.best_result['accuracy']}")
```

### Ray Serve: Model Serving

```python
# Model Serving with Ray Serve
from ray import serve
from ray.serve.handle import DeploymentHandle
import torch

@serve.deployment(
    num_replicas=3,
    ray_actor_options={"num_gpus": 1}
)
class SentimentClassifier:
    def __init__(self):
        self.model = torch.load("model.pt")
        self.model.eval()
        self.tokenizer = load_tokenizer()

    async def __call__(self, request):
        text = await request.json()

        # Tokenize
        inputs = self.tokenizer(
            text["text"],
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            prediction = torch.argmax(outputs.logits, dim=-1)

        return {
            "sentiment": "positive" if prediction == 1 else "negative",
            "confidence": torch.softmax(outputs.logits, dim=-1).max().item()
        }

# Deployment composition
@serve.deployment
class Ensemble:
    def __init__(self, model_a: DeploymentHandle, model_b: DeploymentHandle):
        self.model_a = model_a
        self.model_b = model_b

    async def __call__(self, request):
        # Fan out to both models
        result_a = await self.model_a.remote(request)
        result_b = await self.model_b.remote(request)

        # Ensemble logic
        return {
            "model_a": result_a,
            "model_b": result_b,
            "ensemble": average_predictions(result_a, result_b)
        }

# Deploy
serve.run(SentimentClassifier.bind())
```

---

## 4. NVIDIA Triton Inference Server

### What is Triton?

Triton is a high-performance inference server supporting multiple frameworks (TensorFlow, PyTorch, ONNX, TensorRT) with features like dynamic batching and model ensembles.

```
TRITON ARCHITECTURE
===================

                    ┌─────────────────────────────────┐
                    │         Client Requests         │
                    │    (HTTP/gRPC/C API)            │
                    └───────────────┬─────────────────┘
                                    │
                    ┌───────────────┴─────────────────┐
                    │      TRITON INFERENCE SERVER    │
                    ├─────────────────────────────────┤
                    │  ┌───────────────────────────┐  │
                    │  │    Request Scheduler      │  │
                    │  │   (Dynamic Batching)      │  │
                    │  └─────────────┬─────────────┘  │
                    │                │                │
                    │  ┌─────────────┴─────────────┐  │
                    │  │                           │  │
                    │  ▼           ▼           ▼   │  │
                    │ ┌────┐    ┌────┐    ┌────┐  │  │
                    │ │ TF │    │ PT │    │ONNX│  │  │
                    │ │Back│    │Back│    │Back│  │  │
                    │ │end │    │end │    │end │  │  │
                    │ └────┘    └────┘    └────┘  │  │
                    │                             │  │
                    │  Model Repository           │  │
                    │  /models/                   │  │
                    └─────────────────────────────────┘
```

### Model Repository Structure

```
MODEL REPOSITORY
================

models/
├── bert_sentiment/
│   ├── config.pbtxt           # Model configuration
│   └── 1/                     # Version 1
│       └── model.onnx
│
├── image_classifier/
│   ├── config.pbtxt
│   ├── 1/                     # Version 1
│   │   └── model.savedmodel/
│   └── 2/                     # Version 2 (latest)
│       └── model.savedmodel/
│
└── ensemble_pipeline/
    ├── config.pbtxt           # Ensemble config
    └── 1/
        └── (empty - ensemble only)
```

### Model Configuration

```protobuf
# config.pbtxt for BERT model
name: "bert_sentiment"
platform: "onnxruntime_onnx"
max_batch_size: 32

input [
  {
    name: "input_ids"
    data_type: TYPE_INT64
    dims: [ -1 ]  # Variable sequence length
  },
  {
    name: "attention_mask"
    data_type: TYPE_INT64
    dims: [ -1 ]
  }
]

output [
  {
    name: "logits"
    data_type: TYPE_FP32
    dims: [ 2 ]  # Binary classification
  }
]

# Dynamic batching
dynamic_batching {
  preferred_batch_size: [ 8, 16, 32 ]
  max_queue_delay_microseconds: 100000
}

# Instance groups (GPU allocation)
instance_group [
  {
    count: 2
    kind: KIND_GPU
    gpus: [ 0, 1 ]
  }
]

# Model warmup
model_warmup [
  {
    name: "warmup_requests"
    batch_size: 8
    inputs {
      key: "input_ids"
      value: {
        data_type: TYPE_INT64
        dims: [ 128 ]
        zero_data: true
      }
    }
    inputs {
      key: "attention_mask"
      value: {
        data_type: TYPE_INT64
        dims: [ 128 ]
        zero_data: true
      }
    }
  }
]
```

**Did You Know?** NVIDIA Triton can achieve up to 10x better throughput than naive serving through dynamic batching. The server waits a few milliseconds to collect multiple requests, then processes them as a single batch on the GPU. This is crucial because GPUs are designed for parallel processing - a batch of 32 images takes almost the same time as 1 image on a modern GPU.

### Dynamic Batching

```
DYNAMIC BATCHING
================

Without Batching:                With Dynamic Batching:
─────────────────                ─────────────────────

Req 1 ─► GPU ─► Resp 1          Req 1 ─┐
                                Req 2 ─┼─► GPU ─► Batch Resp
Req 2 ─► GPU ─► Resp 2          Req 3 ─┘
                                        │
Req 3 ─► GPU ─► Resp 3          (Wait up to max_delay)

3 GPU calls                      1 GPU call
High latency per request         Lower avg latency
Low throughput                   High throughput
```

### Triton on Kubernetes

```yaml
# Triton Deployment on Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: triton-inference-server
  namespace: ml-serving
spec:
  replicas: 2
  selector:
    matchLabels:
      app: triton-server
  template:
    metadata:
      labels:
        app: triton-server
    spec:
      containers:
        - name: triton
          image: nvcr.io/nvidia/tritonserver:23.10-py3
          args:
            - tritonserver
            - --model-repository=s3://my-bucket/models
            - --strict-model-config=false
            - --log-verbose=1
          ports:
            - containerPort: 8000  # HTTP
              name: http
            - containerPort: 8001  # gRPC
              name: grpc
            - containerPort: 8002  # Metrics
              name: metrics
          resources:
            requests:
              cpu: 4
              memory: 16Gi
            limits:
              cpu: 8
              memory: 32Gi
              nvidia.com/gpu: 2
          livenessProbe:
            httpGet:
              path: /v2/health/live
              port: 8000
            initialDelaySeconds: 60
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /v2/health/ready
              port: 8000
            initialDelaySeconds: 60
            periodSeconds: 10
          volumeMounts:
            - name: model-cache
              mountPath: /models
      volumes:
        - name: model-cache
          emptyDir:
            sizeLimit: 50Gi
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule

---
# Service for Triton
apiVersion: v1
kind: Service
metadata:
  name: triton-service
  namespace: ml-serving
spec:
  selector:
    app: triton-server
  ports:
    - name: http
      port: 8000
      targetPort: 8000
    - name: grpc
      port: 8001
      targetPort: 8001
    - name: metrics
      port: 8002
      targetPort: 8002
  type: LoadBalancer
```

### Model Ensemble

```protobuf
# Ensemble config for preprocessing + inference
name: "image_pipeline"
platform: "ensemble"
max_batch_size: 32

input [
  {
    name: "raw_image"
    data_type: TYPE_UINT8
    dims: [ -1, -1, 3 ]  # Variable size image
  }
]

output [
  {
    name: "classification"
    data_type: TYPE_FP32
    dims: [ 1000 ]  # ImageNet classes
  }
]

ensemble_scheduling {
  step [
    {
      model_name: "image_preprocessor"
      model_version: -1
      input_map {
        key: "raw_image"
        value: "raw_image"
      }
      output_map {
        key: "processed_image"
        value: "preprocessed"
      }
    },
    {
      model_name: "resnet50"
      model_version: -1
      input_map {
        key: "input"
        value: "preprocessed"
      }
      output_map {
        key: "output"
        value: "classification"
      }
    }
  ]
}
```

```
ENSEMBLE PIPELINE
=================

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Raw Image     │────►│  Preprocessor   │────►│    ResNet50     │
│   (UINT8)       │     │  (Python/ONNX)  │     │   (TensorRT)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              │   Resize, Normalize    │   Classification
                              │   ToTensor             │
                              ▼                        ▼
                        [3, 224, 224]            [1000 classes]
```

---

## 5. Tool Comparison: When to Use What

### Decision Matrix

```
WHEN TO USE WHAT
================

┌────────────────────┬──────────────────────────────────────────────────┐
│     Use Case       │              Recommended Tool                    │
├────────────────────┼──────────────────────────────────────────────────┤
│ ML Pipelines       │ Kubeflow Pipelines                               │
│ (ETL → Train →     │ - Native K8s integration                         │
│  Evaluate)         │ - Artifact tracking built-in                     │
├────────────────────┼──────────────────────────────────────────────────┤
│ Hyperparameter     │ Katib (simple) or Ray Tune (advanced)            │
│ Tuning             │ - Katib: K8s-native, simple                      │
│                    │ - Ray Tune: More algorithms, Python-native       │
├────────────────────┼──────────────────────────────────────────────────┤
│ Distributed        │ Ray Train                                        │
│ Training           │ - Easy PyTorch/TensorFlow distribution           │
│                    │ - Fault tolerance built-in                       │
├────────────────────┼──────────────────────────────────────────────────┤
│ Model Serving      │ KServe (general) or Triton (high-performance)    │
│ (Simple)           │ - KServe: Serverless, easy canary                │
│                    │ - Triton: Dynamic batching, multi-framework      │
├────────────────────┼──────────────────────────────────────────────────┤
│ High-Throughput    │ NVIDIA Triton                                    │
│ Inference          │ - Dynamic batching (10x throughput)              │
│                    │ - TensorRT optimization                          │
│                    │ - Multi-model serving                            │
├────────────────────┼──────────────────────────────────────────────────┤
│ LLM Serving        │ vLLM or TensorRT-LLM (via Triton)                │
│                    │ - PagedAttention for memory efficiency           │
│                    │ - Continuous batching                            │
├────────────────────┼──────────────────────────────────────────────────┤
│ Full Platform      │ Kubeflow (all-in-one)                            │
│                    │ - Notebooks, Pipelines, Serving, AutoML          │
│                    │ - Steep learning curve but comprehensive         │
└────────────────────┴──────────────────────────────────────────────────┘
```

### Complexity vs Capability

```
COMPLEXITY VS CAPABILITY
========================

High │                                    ┌─────────┐
     │                           ┌────────│Kubeflow │
     │                    ┌──────│        │Platform │
     │             ┌──────│ Ray  └─────────────────┘
C    │      ┌──────│Triton│Cluster
A    │      │      │Server│
P    │      │      └──────┘
A    │      │KServe│
B    │      └──────┘
I    │
L    │  ┌──────────┐
I    │  │ Vanilla  │
T    │  │ K8s      │
Y    │  │Deployment│
     │  └──────────┘
Low  └─────────────────────────────────────────────────►
                     COMPLEXITY / LEARNING CURVE
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Deploy KServe Model

```bash
# Install KServe
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.11.0/kserve.yaml

# Deploy sklearn model
kubectl apply -f - <<EOF
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
spec:
  predictor:
    sklearn:
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
EOF

# Test inference
curl -X POST http://sklearn-iris.default.svc.cluster.local/v1/models/sklearn-iris:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": [[5.1, 3.5, 1.4, 0.2]]}'
```

### Exercise 2: Create Kubeflow Pipeline

```python
# Create and submit a simple pipeline
from kfp import dsl, compiler

@dsl.component
def add(a: float, b: float) -> float:
    return a + b

@dsl.component
def multiply(a: float, b: float) -> float:
    return a * b

@dsl.pipeline(name="math-pipeline")
def math_pipeline(x: float = 2.0, y: float = 3.0):
    add_task = add(a=x, b=y)
    multiply_task = multiply(a=add_task.output, b=2.0)

# Compile
compiler.Compiler().compile(math_pipeline, "pipeline.yaml")
```

### Exercise 3: Deploy Ray Cluster

```bash
# Install Ray operator
helm install kuberay-operator kuberay/kuberay-operator

# Deploy RayCluster
kubectl apply -f ray-cluster.yaml

# Submit job
ray job submit --address http://ray-head:8265 -- python train.py
```

---

## 📚 Further Reading

### Documentation
- [Kubeflow Documentation](https://www.kubeflow.org/docs/)
- [KServe User Guide](https://kserve.github.io/website/)
- [Ray on Kubernetes](https://docs.ray.io/en/latest/cluster/kubernetes.html)
- [Triton Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/)

### Papers & Articles
- "Kubeflow: Machine Learning on Kubernetes" (Google, 2018)
- "Ray: A Distributed Framework for Emerging AI Applications" (UC Berkeley, 2018)
- "Serving DNNs at Scale with Triton" (NVIDIA, 2021)

---

## ✅ Knowledge Check

1. **What are the main components of Kubeflow?**

2. **How does KServe handle canary deployments?**

3. **What is dynamic batching in Triton, and why is it important?**

4. **When would you choose Ray over Kubeflow for distributed training?**

5. **What's the difference between KServe and Triton for model serving?**

---

## ⏭️ Next Steps

You now understand the advanced Kubernetes tools for ML! These are what companies like Google, Netflix, and Uber use to run ML at scale.

**Up Next**: Module 48 - MLOps & Experiment Tracking (MLflow, Weights & Biases)

---

_Module 47 Complete! You now understand Kubeflow, KServe, Ray, and Triton!_
_"The ML platform is what turns experiments into production systems."_
