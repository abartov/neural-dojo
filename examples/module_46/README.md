# Module 46 Deliverable: ML Kubernetes Toolkit

**Generate production-ready Kubernetes manifests for ML workloads with GPU support, autoscaling, and persistent storage.**

## Features

- **Deployment Presets**: Pre-configured templates for inference (CPU/GPU) and high-memory workloads
- **Training Job Generation**: GPU training jobs with distributed training support
- **HPA Autoscaling**: Horizontal Pod Autoscaler with custom scaling behavior
- **Storage Management**: PVC generation for models, training data, and checkpoints
- **Full Stack Generation**: Complete inference stack with namespace, configmap, deployment, service, and HPA

## Quick Start

```bash
python deliverable_ml_k8s_toolkit.py demo1  # Deployment manifests (CPU/GPU)
python deliverable_ml_k8s_toolkit.py demo2  # Training job manifests
python deliverable_ml_k8s_toolkit.py demo3  # HPA autoscaling config
python deliverable_ml_k8s_toolkit.py demo4  # Persistent storage (PVCs)
python deliverable_ml_k8s_toolkit.py demo5  # Complete inference stack
```

## Deployment Presets

| Preset | GPU | Replicas | Memory | Use Case |
|--------|-----|----------|--------|----------|
| `inference-cpu` | No | 3 | 2Gi | Lightweight models |
| `inference-gpu` | 1 | 2 | 16Gi | GPU inference |
| `high-memory` | 1 | 2 | 64Gi | Large models (LLMs) |

## Job Presets

| Preset | GPUs | Memory | Use Case |
|--------|------|--------|----------|
| `training-gpu` | 1 | 32Gi | Single GPU training |
| `distributed-training` | 4 | 64Gi | Multi-GPU training |
| `batch-inference` | 0 | 8Gi | CPU batch processing |

## Generated Manifests

```
.ml_k8s_toolkit/
└── manifests/
    ├── deployment-inference-cpu.yaml
    ├── deployment-inference-gpu.yaml
    ├── job-training-gpu.yaml
    ├── job-distributed-training.yaml
    ├── hpa-inference.yaml
    ├── pvc-model-storage.yaml
    └── stacks/
        └── sentiment-classifier/
            ├── namespace.yaml
            ├── configmap.yaml
            ├── pvc.yaml
            ├── deployment.yaml
            ├── service.yaml
            ├── hpa.yaml
            └── all-in-one.yaml
```

## Key Concepts

### GPU Scheduling

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
nodeSelector:
  accelerator: nvidia-tesla-v100
```

### Autoscaling Behavior

```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 0    # Scale up immediately
    policies:
      - type: Percent
        value: 100                    # Double pods
        periodSeconds: 15
  scaleDown:
    stabilizationWindowSeconds: 300  # Wait 5 minutes
    policies:
      - type: Percent
        value: 10                     # 10% reduction per minute
```

### Storage Patterns

| Access Mode | Use Case |
|-------------|----------|
| ReadWriteOnce (RWO) | Training checkpoints (single pod) |
| ReadOnlyMany (ROX) | Model serving (multiple pods) |
| ReadWriteMany (RWX) | Shared datasets (multiple pods) |

## Production Deployment

```bash
# Deploy complete inference stack
kubectl apply -f .ml_k8s_toolkit/manifests/stacks/sentiment-classifier/all-in-one.yaml

# Check status
kubectl get all -n ml-production

# View HPA status
kubectl get hpa -n ml-production

# Scale manually (if needed)
kubectl scale deployment sentiment-classifier --replicas=5 -n ml-production
```

**Time**: ~3 hours | **Lines**: 1,084 | **Author**: Neural Dojo
