# Module 46: Kubernetes Fundamentals for ML

**Last Updated**: 2025-11-28
**Status**: 🟢 Complete
**Duration**: 7-8 hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand Kubernetes architecture and core concepts
- Deploy ML inference services on Kubernetes
- Configure GPU scheduling with NVIDIA GPU Operator
- Manage resources (CPU, memory, GPU) for ML workloads
- Implement autoscaling for inference services
- Set up persistent storage for models and data

---

## 📖 Why Kubernetes for ML?

### The Scaling Challenge

Your ML model works great on your laptop. Now you need to:
- Serve 10,000 requests per second
- Handle traffic spikes during peak hours
- Deploy updates without downtime
- Run across multiple servers
- Manage GPU resources efficiently

```
THE PRODUCTION ML SCALING PROBLEM
=================================

Single Server:
┌─────────────────┐
│   ML Model      │  ← What happens when this dies?
│   (1 instance)  │  ← Can't handle 10K req/sec
└─────────────────┘  ← No GPU sharing

Kubernetes Solution:
┌─────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Pod 1   │  │ Pod 2   │  │ Pod 3   │  │ Pod N   │   │
│  │(replica)│  │(replica)│  │(replica)│  │(replica)│   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
│       ↑            ↑            ↑            ↑         │
│       └────────────┴────────────┴────────────┘         │
│                         │                               │
│                  Load Balancer                          │
│                         │                               │
│                    Autoscaler                           │
│            (scale based on CPU/GPU/queue)               │
└─────────────────────────────────────────────────────────┘
```

**Did You Know?** Google runs over 2 billion containers per week using Borg, the internal predecessor to Kubernetes. When Google open-sourced Kubernetes in 2014, they brought 15 years of container orchestration experience. The name "Kubernetes" (κυβερνήτης) is Greek for "helmsman" or "pilot."

### What Kubernetes Solves for ML

```
┌─────────────────────────────────────────────────────────────────────┐
│                 KUBERNETES BENEFITS FOR ML                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. SCALABILITY                                                     │
│     Auto-scale from 1 to 100 replicas based on load                │
│     Handle traffic spikes without manual intervention               │
│                                                                     │
│  2. HIGH AVAILABILITY                                               │
│     If a pod dies, Kubernetes restarts it automatically            │
│     Spread replicas across nodes for fault tolerance                │
│                                                                     │
│  3. GPU MANAGEMENT                                                  │
│     Schedule ML workloads on GPU nodes                              │
│     Share GPUs across multiple pods (MIG, time-slicing)            │
│                                                                     │
│  4. RESOURCE EFFICIENCY                                             │
│     Pack multiple workloads on same hardware                        │
│     Set limits to prevent noisy neighbors                           │
│                                                                     │
│  5. DEPLOYMENT FLEXIBILITY                                          │
│     Rolling updates, canary deployments, blue-green                 │
│     Rollback instantly if deployment fails                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Kubernetes Architecture

### Core Components

```
KUBERNETES CLUSTER ARCHITECTURE
================================

┌─────────────────────────────────────────────────────────────────────┐
│                        CONTROL PLANE                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  API Server  │  │  Scheduler   │  │  Controller  │              │
│  │              │  │              │  │   Manager    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         │                │                  │                       │
│         └────────────────┴──────────────────┘                       │
│                          │                                          │
│                    ┌─────┴─────┐                                    │
│                    │   etcd    │  (cluster state database)          │
│                    └───────────┘                                    │
└─────────────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   WORKER NODE   │  │   WORKER NODE   │  │   GPU NODE      │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │  kubelet  │  │  │  │  kubelet  │  │  │  │  kubelet  │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │kube-proxy │  │  │  │kube-proxy │  │  │  │kube-proxy │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │ Container │  │  │  │ Container │  │  │  │  NVIDIA   │  │
│  │  Runtime  │  │  │  │  Runtime  │  │  │  │  Runtime  │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │
│                 │  │                 │  │  ┌───────────┐  │
│  [Pod][Pod]     │  │  [Pod][Pod]     │  │  │    GPU    │  │
│                 │  │                 │  │  └───────────┘  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Key Concepts

```yaml
# Pod: Smallest deployable unit (one or more containers)
# Deployment: Manages replica sets and rolling updates
# Service: Stable network endpoint for pods
# ConfigMap: Configuration data
# Secret: Sensitive data (API keys, passwords)
# PersistentVolume: Storage that outlives pods
# Namespace: Virtual cluster for isolation

CONCEPT HIERARCHY
=================

Namespace (isolation boundary)
    │
    └── Deployment (manages replicas)
            │
            └── ReplicaSet (ensures N pods running)
                    │
                    └── Pod (runs containers)
                            │
                            └── Container (your app)
```

**Did You Know?** The Kubernetes "control loop" pattern is inspired by control theory in engineering. The controller continuously compares the desired state (specified in YAML) with the actual state (observed in cluster), and takes actions to reconcile any differences. This is why Kubernetes is "declarative"—you tell it what you want, not how to get there.

---

## 📦 Core Kubernetes Objects

### Pod

The smallest deployable unit. Usually one container, but can be multiple.

```yaml
# pod.yaml - Basic ML inference pod
apiVersion: v1
kind: Pod
metadata:
  name: ml-inference
  labels:
    app: sentiment-classifier
spec:
  containers:
  - name: model
    image: myregistry/sentiment:v1.0
    ports:
    - containerPort: 8000
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
    env:
    - name: MODEL_PATH
      value: "/models/sentiment.pt"
    volumeMounts:
    - name: model-storage
      mountPath: /models
  volumes:
  - name: model-storage
    persistentVolumeClaim:
      claimName: model-pvc
```

### Deployment

Manages pods with replicas, rolling updates, and rollbacks.

```yaml
# deployment.yaml - ML inference deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentiment-classifier
  labels:
    app: sentiment-classifier
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentiment-classifier
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: sentiment-classifier
    spec:
      containers:
      - name: model
        image: myregistry/sentiment:v1.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Service

Stable network endpoint that load-balances across pods.

```yaml
# service.yaml - Expose deployment
apiVersion: v1
kind: Service
metadata:
  name: sentiment-service
spec:
  selector:
    app: sentiment-classifier
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP  # Internal only

---
# For external access
apiVersion: v1
kind: Service
metadata:
  name: sentiment-service-external
spec:
  selector:
    app: sentiment-classifier
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer  # Gets external IP
```

### Service Types

```
SERVICE TYPES
=============

ClusterIP (default):
┌─────────────────────────────────┐
│         Cluster Only            │
│  Internal IP: 10.96.0.1:80     │
│  Only accessible within cluster │
└─────────────────────────────────┘

NodePort:
┌─────────────────────────────────┐
│  External: <NodeIP>:30000-32767 │
│  Opens port on every node       │
└─────────────────────────────────┘

LoadBalancer:
┌─────────────────────────────────┐
│  External: Cloud Load Balancer  │
│  Gets public IP from cloud      │
│  (AWS ELB, GCP LB, Azure LB)   │
└─────────────────────────────────┘

Ingress (not a Service, but related):
┌─────────────────────────────────┐
│  HTTP/HTTPS routing             │
│  Path-based: /api → service-a   │
│              /ml  → service-b   │
└─────────────────────────────────┘
```

---

## 🎮 GPU Scheduling for ML

### The GPU Challenge

GPUs are expensive resources. Kubernetes needs to:
1. Know which nodes have GPUs
2. Schedule GPU workloads appropriately
3. Prevent over-allocation
4. Support GPU sharing (optional)

### NVIDIA GPU Operator

```
NVIDIA GPU OPERATOR COMPONENTS
==============================

┌─────────────────────────────────────────────────────────────────┐
│                     GPU NODE                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  GPU Operator                            │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐  │   │
│  │  │ NVIDIA Driver │  │ Container     │  │ Device      │  │   │
│  │  │ (Auto-install)│  │ Toolkit       │  │ Plugin      │  │   │
│  │  └───────────────┘  └───────────────┘  └─────────────┘  │   │
│  │                                                          │   │
│  │  ┌───────────────┐  ┌───────────────┐                   │   │
│  │  │ DCGM Exporter │  │ GPU Feature   │                   │   │
│  │  │ (Monitoring)  │  │ Discovery     │                   │   │
│  │  └───────────────┘  └───────────────┘                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    GPU Hardware                          │   │
│  │  [GPU 0: A100 80GB] [GPU 1: A100 80GB]                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Did You Know?** NVIDIA's A100 GPU introduced Multi-Instance GPU (MIG) technology, which can partition a single GPU into up to 7 isolated instances. This means 7 different ML models can run on one A100 with guaranteed isolation—no noisy neighbor problems. MIG is particularly useful for inference workloads.

### Requesting GPUs

```yaml
# gpu-pod.yaml - Request GPU resources
apiVersion: v1
kind: Pod
metadata:
  name: gpu-training
spec:
  containers:
  - name: trainer
    image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
    resources:
      limits:
        nvidia.com/gpu: 1  # Request 1 GPU
    command: ["python", "train.py"]
  # Ensure scheduling on GPU node
  nodeSelector:
    accelerator: nvidia-tesla-a100
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
```

### GPU Resource Types

```yaml
# Different GPU configurations
resources:
  limits:
    # Whole GPU
    nvidia.com/gpu: 1

    # MIG (Multi-Instance GPU) - A100 only
    nvidia.com/mig-1g.5gb: 1   # 1/7 of A100
    nvidia.com/mig-2g.10gb: 1  # 2/7 of A100
    nvidia.com/mig-3g.20gb: 1  # 3/7 of A100

    # Time-slicing (shared GPU)
    # Configured via GPU Operator config
```

### GPU Scheduling Strategy

```yaml
# Training job - needs dedicated GPU
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: myregistry/trainer:v1
        resources:
          limits:
            nvidia.com/gpu: 4  # 4 GPUs for distributed training
            memory: "64Gi"
            cpu: "16"
      restartPolicy: Never
      # Use GPU node pool
      nodeSelector:
        node-pool: gpu-training
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
```

---

## 📊 Resource Management

### Resource Requests vs Limits

```
REQUESTS VS LIMITS
==================

requests: What the container is GUARANTEED
limits:   Maximum the container CAN use

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  requests.memory: 1Gi    limits.memory: 2Gi                    │
│  ├──────────────────────┼─────────────────────┤                │
│  0                      1Gi                  2Gi               │
│  │◄─── Guaranteed ─────►│◄─── Burstable ────►│                │
│                                                                 │
│  If pod exceeds limit → OOMKilled (Out of Memory)              │
│  If pod exceeds request but under limit → OK (if available)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

CPU: Throttled (not killed) if exceeds limit
Memory: OOMKilled if exceeds limit
GPU: Cannot exceed limit (hard boundary)
```

### QoS Classes

```yaml
# Guaranteed QoS (highest priority)
# requests == limits for all containers
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "500m"

# Burstable QoS (medium priority)
# requests < limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

# BestEffort QoS (lowest priority, evicted first)
# No requests or limits specified
resources: {}
```

### Resource Quotas

```yaml
# Limit resources per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ml-team-quota
  namespace: ml-team
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "200Gi"
    limits.cpu: "200"
    limits.memory: "400Gi"
    requests.nvidia.com/gpu: "8"
    pods: "50"
    persistentvolumeclaims: "20"
```

---

## 📈 Autoscaling for ML

### Horizontal Pod Autoscaler (HPA)

Scale replicas based on metrics.

```yaml
# hpa.yaml - Scale based on CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sentiment-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sentiment-classifier
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

### Custom Metrics for ML

```yaml
# Scale based on inference queue length
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference-server
  minReplicas: 1
  maxReplicas: 50
  metrics:
  # Custom metric from Prometheus
  - type: Pods
    pods:
      metric:
        name: inference_queue_length
      target:
        type: AverageValue
        averageValue: "10"  # Scale when queue > 10 per pod
  # GPU utilization (requires DCGM)
  - type: External
    external:
      metric:
        name: dcgm_gpu_utilization
      target:
        type: AverageValue
        averageValue: "80"
```

### Vertical Pod Autoscaler (VPA)

Adjust resource requests/limits automatically.

```yaml
# vpa.yaml - Auto-tune resources
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ml-inference-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-inference
  updatePolicy:
    updateMode: "Auto"  # Or "Off" for recommendations only
  resourcePolicy:
    containerPolicies:
    - containerName: model
      minAllowed:
        cpu: "100m"
        memory: "256Mi"
      maxAllowed:
        cpu: "4"
        memory: "8Gi"
```

---

## 💾 Persistent Storage for ML

### Storage Architecture

```
KUBERNETES STORAGE MODEL
========================

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Pod                                                            │
│  ┌─────────────────┐                                           │
│  │   Container     │                                           │
│  │  /models (mount)│ ──────┐                                   │
│  └─────────────────┘       │                                   │
│                            │                                   │
│  PersistentVolumeClaim     │                                   │
│  ┌─────────────────┐       │                                   │
│  │   model-pvc     │ ◄─────┘                                   │
│  │   10Gi, RWO     │                                           │
│  └────────┬────────┘                                           │
│           │ binds to                                           │
│           ▼                                                    │
│  PersistentVolume                                              │
│  ┌─────────────────┐                                           │
│  │   model-pv      │                                           │
│  │   NFS/EBS/GCS   │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### PersistentVolumeClaim for Models

```yaml
# pvc.yaml - Request storage for models
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-storage
spec:
  accessModes:
    - ReadWriteOnce  # RWO: Single node read-write
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd  # SSD for fast model loading

---
# For shared model access (multiple pods)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-models
spec:
  accessModes:
    - ReadOnlyMany  # ROX: Multiple nodes read-only
  resources:
    requests:
      storage: 100Gi
  storageClassName: nfs  # NFS for shared access
```

### Access Modes

```
ACCESS MODES
============

ReadWriteOnce (RWO):
- Single node can mount as read-write
- Use for: Training checkpoints, single-replica inference

ReadOnlyMany (ROX):
- Multiple nodes can mount as read-only
- Use for: Shared models across inference replicas

ReadWriteMany (RWX):
- Multiple nodes can mount as read-write
- Use for: Distributed training, shared logs
- Requires: NFS, CephFS, GlusterFS

ReadWriteOncePod (RWOP):
- Single pod can mount as read-write
- K8s 1.22+ only
```

---

## 🚀 ML Deployment Patterns

### Pattern 1: Simple Inference Service

```yaml
# Complete inference deployment
apiVersion: v1
kind: Namespace
metadata:
  name: ml-inference

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: model-config
  namespace: ml-inference
data:
  MODEL_NAME: "sentiment-classifier"
  MODEL_VERSION: "v1.0"
  MAX_BATCH_SIZE: "32"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentiment-api
  namespace: ml-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentiment-api
  template:
    metadata:
      labels:
        app: sentiment-api
    spec:
      containers:
      - name: api
        image: myregistry/sentiment:v1.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: model-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60

---
apiVersion: v1
kind: Service
metadata:
  name: sentiment-api
  namespace: ml-inference
spec:
  selector:
    app: sentiment-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Pattern 2: GPU Training Job

```yaml
# Training job with GPU
apiVersion: batch/v1
kind: Job
metadata:
  name: bert-finetuning
  namespace: ml-training
spec:
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: trainer
        image: myregistry/bert-trainer:v1
        command: ["python", "train.py"]
        args:
          - "--epochs=10"
          - "--batch-size=32"
          - "--learning-rate=2e-5"
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "4"
        volumeMounts:
        - name: data
          mountPath: /data
        - name: checkpoints
          mountPath: /checkpoints
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: training-data
      - name: checkpoints
        persistentVolumeClaim:
          claimName: checkpoints
      restartPolicy: OnFailure
      nodeSelector:
        accelerator: nvidia-tesla-v100
```

### Pattern 3: Model A/B Testing

```yaml
# Canary deployment with Istio
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: sentiment-routing
spec:
  hosts:
  - sentiment-api
  http:
  - match:
    - headers:
        x-model-version:
          exact: "v2"
    route:
    - destination:
        host: sentiment-api-v2
  - route:
    - destination:
        host: sentiment-api-v1
        weight: 90
    - destination:
        host: sentiment-api-v2
        weight: 10  # 10% traffic to new model
```

---

## 🔧 Essential kubectl Commands

```bash
# CLUSTER INFO
kubectl cluster-info
kubectl get nodes
kubectl get nodes -o wide  # With IPs

# DEPLOYMENTS
kubectl get deployments
kubectl describe deployment <name>
kubectl scale deployment <name> --replicas=5
kubectl rollout status deployment <name>
kubectl rollout history deployment <name>
kubectl rollout undo deployment <name>

# PODS
kubectl get pods
kubectl get pods -o wide  # With node info
kubectl describe pod <name>
kubectl logs <pod-name>
kubectl logs <pod-name> -f  # Follow
kubectl logs <pod-name> --previous  # Previous container
kubectl exec -it <pod-name> -- bash  # Shell into pod

# SERVICES
kubectl get services
kubectl describe service <name>
kubectl port-forward service/<name> 8080:80  # Local access

# GPU NODES
kubectl get nodes -l accelerator=nvidia
kubectl describe node <gpu-node> | grep -A5 "Allocated resources"

# RESOURCES
kubectl top nodes
kubectl top pods
kubectl get resourcequota

# DEBUGGING
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pod <pod-name>  # Check Events section
kubectl logs <pod-name> --all-containers
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Deploy Inference Service

Create a Kubernetes deployment for an ML inference API:
- 3 replicas
- Health checks
- Resource limits
- LoadBalancer service

### Exercise 2: GPU Training Job

Create a Job for model training:
- Request 1 GPU
- Mount data volume
- Save checkpoints

### Exercise 3: Autoscaling

Configure HPA for inference service:
- Scale 2-10 replicas
- Target 70% CPU
- Custom queue metric

---

## 📚 Further Reading

### Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [Kubeflow](https://www.kubeflow.org/)

### Tools
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [k9s](https://k9scli.io/) - Terminal UI for K8s
- [Lens](https://k8slens.dev/) - K8s IDE

### ML on Kubernetes
- [Seldon Core](https://www.seldon.io/) - ML deployment
- [KServe](https://kserve.github.io/) - Serverless inference
- [Ray on Kubernetes](https://docs.ray.io/en/latest/cluster/kubernetes/)

---

## ✅ Knowledge Check

1. **What is a Pod and how does it differ from a container?**

2. **How do you request GPU resources in Kubernetes?**

3. **What's the difference between requests and limits?**

4. **How does HPA scale ML inference services?**

5. **What access mode would you use for shared model storage?**

---

## ⏭️ Next Steps

You now understand Kubernetes for ML! Key takeaways:
- Pods are the smallest unit, Deployments manage replicas
- GPU scheduling requires NVIDIA GPU Operator
- Resource requests guarantee capacity, limits cap usage
- HPA scales based on CPU, memory, or custom metrics
- PVCs provide persistent storage for models

**Up Next**: Module 47 - FastAPI for ML Serving

---

_Module 46 Complete! You now understand Kubernetes for ML!_
_"Kubernetes: Because your model deserves to scale."_
