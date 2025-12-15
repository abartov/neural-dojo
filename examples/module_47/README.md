# Module 47 Deliverable: ML Advanced Kubernetes Toolkit

**Generate production-ready manifests for advanced ML platforms: Kubeflow, KServe, Ray, and Triton.**

## Features

- **Kubeflow Pipelines**: DAG workflows with Katib hyperparameter tuning
- **KServe**: Serverless inference with canary deployments and transformers
- **Ray Clusters**: Distributed training, tuning, and serving
- **NVIDIA Triton**: High-performance inference with dynamic batching

## Quick Start

```bash
python deliverable_ml_advanced_k8s_toolkit.py demo1  # Kubeflow pipelines
python deliverable_ml_advanced_k8s_toolkit.py demo2  # KServe deployments
python deliverable_ml_advanced_k8s_toolkit.py demo3  # Ray clusters
python deliverable_ml_advanced_k8s_toolkit.py demo4  # Triton server
python deliverable_ml_advanced_k8s_toolkit.py demo5  # Complete ML platform
```

## Platform Components

| Tool | Use Case | Key Features |
|------|----------|--------------|
| **Kubeflow** | ML Pipelines | DAG workflows, Katib HPO, Notebooks |
| **KServe** | Model Serving | Serverless, auto-scale, canary |
| **Ray** | Distributed Compute | Train, Tune, Serve, Data |
| **Triton** | High-Throughput Inference | Dynamic batching, multi-framework |

## Generated Manifests

```
.ml_advanced_k8s_toolkit/
└── manifests/
    ├── kubeflow/
    │   ├── kubeflow-training-pipeline.yaml
    │   └── katib-bert-tuning.yaml
    ├── kserve/
    │   ├── kserve-sklearn.yaml
    │   ├── kserve-pytorch-gpu.yaml
    │   ├── kserve-canary.yaml
    │   └── kserve-with-transformer.yaml
    ├── ray/
    │   ├── ray-gpu-cluster.yaml
    │   ├── ray-high-memory-cluster.yaml
    │   ├── ray-training-job.yaml
    │   └── ray-service.yaml
    ├── triton/
    │   ├── triton-deployment.yaml
    │   └── models/
    │       ├── bert_sentiment/config.pbtxt
    │       ├── resnet50/config.pbtxt
    │       └── image_pipeline/config.pbtxt
    └── stacks/
        └── ml-platform/
            ├── 01-namespace.yaml
            ├── 02-ray-cluster.yaml
            ├── 03-triton-server.yaml
            ├── 04-kserve-classifier.yaml
            ├── 05-kserve-embeddings.yaml
            ├── 06-kubeflow-pipeline.yaml
            ├── 07-katib-experiment.yaml
            └── all-in-one.yaml
```

## When to Use What

| Use Case | Recommended Tool |
|----------|-----------------|
| ML Pipelines (ETL → Train → Deploy) | Kubeflow Pipelines |
| Hyperparameter Tuning | Katib (simple) or Ray Tune (advanced) |
| Distributed Training | Ray Train |
| Serverless Inference | KServe |
| High-Throughput Inference | NVIDIA Triton |
| LLM Serving | vLLM or TensorRT-LLM |

## Key Concepts

### KServe Canary Deployment

```yaml
spec:
  predictor:
    canaryTrafficPercent: 10  # 10% to new model
    pytorch:
      storageUri: "gs://bucket/model-v2"
```

### Ray Cluster Auto-scaling

```yaml
workerGroupSpecs:
  - replicas: 4
    minReplicas: 1
    maxReplicas: 10
```

### Triton Dynamic Batching

```protobuf
dynamic_batching {
  preferred_batch_size: [ 8, 16, 32 ]
  max_queue_delay_microseconds: 100000
}
```

## Production Deployment

```bash
# Deploy complete ML platform
kubectl apply -f .ml_advanced_k8s_toolkit/manifests/stacks/ml-platform/all-in-one.yaml

# Check status
kubectl get all -n ml-production
kubectl get rayclusters -n ml-production
kubectl get inferenceservices -n ml-production
```

**Time**: ~4 hours | **Lines**: 1,785 | **Author**: Neural Dojo
