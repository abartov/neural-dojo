#!/usr/bin/env python3
"""
ML Advanced Kubernetes Toolkit
==============================

Generate production-ready manifests for advanced ML platforms on Kubernetes:
- Kubeflow Pipelines
- KServe InferenceServices
- Ray Clusters
- NVIDIA Triton Inference Server

This toolkit generates YAML manifests that can be applied to any Kubernetes cluster.

Usage:
    python deliverable_ml_advanced_k8s_toolkit.py demo1  # Kubeflow pipelines
    python deliverable_ml_advanced_k8s_toolkit.py demo2  # KServe deployments
    python deliverable_ml_advanced_k8s_toolkit.py demo3  # Ray clusters
    python deliverable_ml_advanced_k8s_toolkit.py demo4  # Triton server
    python deliverable_ml_advanced_k8s_toolkit.py demo5  # Full ML platform stack

Author: Neural Dojo
"""

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# =============================================================================
# CONFIGURATION
# =============================================================================

STORAGE_DIR = Path(".ml_advanced_k8s_toolkit")
MANIFESTS_DIR = STORAGE_DIR / "manifests"


class MLFramework(Enum):
    """Supported ML frameworks."""
    SKLEARN = "sklearn"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    XGBOOST = "xgboost"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"


class RayWorkerType(Enum):
    """Ray worker node types."""
    CPU = "cpu"
    GPU = "gpu"
    HIGH_MEMORY = "high-memory"


class TritonBackend(Enum):
    """Triton backend types."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnxruntime"
    TENSORRT = "tensorrt"
    PYTHON = "python"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class KubeflowPipelineConfig:
    """Configuration for Kubeflow Pipeline."""
    name: str
    description: str = "ML Pipeline"
    namespace: str = "kubeflow"
    steps: list = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    schedule: Optional[str] = None  # Cron schedule


@dataclass
class KubeflowStepConfig:
    """Configuration for a pipeline step."""
    name: str
    image: str
    command: list
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    resources: dict = field(default_factory=lambda: {
        "cpu": "1",
        "memory": "2Gi"
    })
    gpu: int = 0


@dataclass
class KServeConfig:
    """Configuration for KServe InferenceService."""
    name: str
    namespace: str = "ml-serving"
    framework: MLFramework = MLFramework.SKLEARN
    storage_uri: str = ""
    min_replicas: int = 1
    max_replicas: int = 10
    target_concurrency: int = 10
    resources: dict = field(default_factory=lambda: {
        "cpu": "500m",
        "memory": "1Gi"
    })
    gpu: int = 0
    canary_percent: int = 0
    transformer_image: Optional[str] = None


@dataclass
class RayClusterConfig:
    """Configuration for Ray Cluster."""
    name: str
    namespace: str = "ray-system"
    ray_version: str = "2.7.0"
    head_cpu: int = 2
    head_memory: str = "8Gi"
    worker_type: RayWorkerType = RayWorkerType.GPU
    num_workers: int = 4
    min_workers: int = 1
    max_workers: int = 10
    worker_cpu: int = 4
    worker_memory: str = "16Gi"
    worker_gpu: int = 1


@dataclass
class TritonConfig:
    """Configuration for Triton Inference Server."""
    name: str
    namespace: str = "ml-serving"
    model_repository: str = "s3://my-bucket/models"
    replicas: int = 2
    cpu: int = 4
    memory: str = "16Gi"
    gpu: int = 1
    enable_metrics: bool = True
    dynamic_batching: bool = True
    max_batch_size: int = 32


@dataclass
class TritonModelConfig:
    """Configuration for a Triton model."""
    name: str
    backend: TritonBackend = TritonBackend.ONNX
    max_batch_size: int = 32
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    instance_count: int = 1
    gpu_ids: list = field(default_factory=lambda: [0])
    dynamic_batching: bool = True
    preferred_batch_sizes: list = field(default_factory=lambda: [8, 16, 32])


# =============================================================================
# KUBEFLOW PIPELINE GENERATOR
# =============================================================================

class KubeflowPipelineGenerator:
    """Generate Kubeflow Pipeline manifests."""

    @staticmethod
    def generate_pipeline(config: KubeflowPipelineConfig) -> str:
        """Generate Kubeflow Pipeline YAML."""
        # Generate component definitions
        components = []
        for i, step in enumerate(config.steps):
            component = KubeflowPipelineGenerator._generate_component(step, i)
            components.append(component)

        # Generate workflow
        workflow = f"""# Kubeflow Pipeline: {config.name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: {config.name}-
  namespace: {config.namespace}
  labels:
    pipelines.kubeflow.org/pipeline-sdk-type: kfp
spec:
  entrypoint: {config.name}
  arguments:
    parameters:
"""
        # Add parameters
        for param_name, param_default in config.parameters.items():
            workflow += f"""      - name: {param_name}
        value: "{param_default}"
"""

        # Add templates
        workflow += f"""
  templates:
    - name: {config.name}
      dag:
        tasks:
"""
        # Add DAG tasks
        for i, step in enumerate(config.steps):
            deps = f"\n          dependencies: [{', '.join(step.inputs)}]" if step.inputs else ""
            workflow += f"""          - name: {step.name}
            template: {step.name}-template{deps}
"""

        # Add component templates
        for i, step in enumerate(config.steps):
            workflow += KubeflowPipelineGenerator._generate_template(step)

        return workflow

    @staticmethod
    def _generate_component(step: KubeflowStepConfig, index: int) -> str:
        """Generate component definition."""
        return f"""
# Component: {step.name}
# Image: {step.image}
# GPU: {step.gpu}
"""

    @staticmethod
    def _generate_template(step: KubeflowStepConfig) -> str:
        """Generate Argo workflow template for a step."""
        gpu_resources = ""
        if step.gpu > 0:
            gpu_resources = f"""
                nvidia.com/gpu: {step.gpu}"""

        tolerations = ""
        if step.gpu > 0:
            tolerations = """
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule"""

        return f"""
    - name: {step.name}-template
      container:
        image: {step.image}
        command: {json.dumps(step.command)}
        resources:
          requests:
            cpu: {step.resources.get('cpu', '1')}
            memory: {step.resources.get('memory', '2Gi')}
          limits:
            cpu: {step.resources.get('cpu', '1')}
            memory: {step.resources.get('memory', '2Gi')}{gpu_resources}{tolerations}
"""

    @staticmethod
    def generate_katib_experiment(
        name: str,
        namespace: str = "kubeflow",
        objective_metric: str = "accuracy",
        objective_type: str = "maximize",
        goal: float = 0.95,
        algorithm: str = "random",
        parameters: list = None,
        max_trials: int = 12,
        parallel_trials: int = 3,
        training_image: str = "myregistry/trainer:latest"
    ) -> str:
        """Generate Katib Experiment for hyperparameter tuning."""
        if parameters is None:
            parameters = [
                {"name": "learning_rate", "type": "double", "min": "0.001", "max": "0.1"},
                {"name": "batch_size", "type": "int", "min": "16", "max": "128"},
            ]

        params_yaml = ""
        for param in parameters:
            params_yaml += f"""    - name: {param['name']}
      parameterType: {param['type']}
      feasibleSpace:
        min: "{param['min']}"
        max: "{param['max']}"
"""

        trial_params = ""
        for param in parameters:
            trial_params += f"""      - name: {param['name']}
        reference: {param['name']}
"""

        cmd_args = " ".join([f"--{p['name']}=${{trialParameters.{p['name']}}}" for p in parameters])

        return f"""# Katib Experiment: {name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}

apiVersion: kubeflow.org/v1beta1
kind: Experiment
metadata:
  name: {name}
  namespace: {namespace}
spec:
  objective:
    type: {objective_type}
    goal: {goal}
    objectiveMetricName: {objective_metric}
  algorithm:
    algorithmName: {algorithm}
  parallelTrialCount: {parallel_trials}
  maxTrialCount: {max_trials}
  maxFailedTrialCount: 3
  parameters:
{params_yaml}
  trialTemplate:
    primaryContainerName: training-container
    trialParameters:
{trial_params}
    trialSpec:
      apiVersion: batch/v1
      kind: Job
      spec:
        template:
          spec:
            containers:
              - name: training-container
                image: {training_image}
                command:
                  - python
                  - train.py
                  - {cmd_args}
            restartPolicy: Never
"""


# =============================================================================
# KSERVE GENERATOR
# =============================================================================

class KServeGenerator:
    """Generate KServe InferenceService manifests."""

    FRAMEWORK_CONFIGS = {
        MLFramework.SKLEARN: {
            "predictor_type": "sklearn",
            "default_resources": {"cpu": "500m", "memory": "1Gi"},
        },
        MLFramework.PYTORCH: {
            "predictor_type": "pytorch",
            "default_resources": {"cpu": "2", "memory": "8Gi"},
        },
        MLFramework.TENSORFLOW: {
            "predictor_type": "tensorflow",
            "default_resources": {"cpu": "2", "memory": "8Gi"},
        },
        MLFramework.XGBOOST: {
            "predictor_type": "xgboost",
            "default_resources": {"cpu": "1", "memory": "2Gi"},
        },
        MLFramework.HUGGINGFACE: {
            "predictor_type": "huggingface",
            "default_resources": {"cpu": "4", "memory": "16Gi"},
        },
    }

    @staticmethod
    def generate_inference_service(config: KServeConfig) -> str:
        """Generate KServe InferenceService YAML."""
        framework_config = KServeGenerator.FRAMEWORK_CONFIGS.get(
            config.framework,
            {"predictor_type": "sklearn", "default_resources": {"cpu": "500m", "memory": "1Gi"}}
        )

        gpu_limits = ""
        if config.gpu > 0:
            gpu_limits = f"""
                nvidia.com/gpu: {config.gpu}"""

        canary_config = ""
        if config.canary_percent > 0:
            canary_config = f"""
    canaryTrafficPercent: {config.canary_percent}"""

        transformer_config = ""
        if config.transformer_image:
            transformer_config = f"""
  transformer:
    containers:
      - name: transformer
        image: {config.transformer_image}
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
"""

        return f"""# KServe InferenceService: {config.name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}
# Framework: {config.framework.value}

apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: {config.name}
  namespace: {config.namespace}
  annotations:
    sidecar.istio.io/inject: "true"
spec:{transformer_config}
  predictor:{canary_config}
    minReplicas: {config.min_replicas}
    maxReplicas: {config.max_replicas}
    scaleTarget: {config.target_concurrency}
    scaleMetric: concurrency
    {framework_config['predictor_type']}:
      storageUri: "{config.storage_uri}"
      resources:
        requests:
          cpu: {config.resources.get('cpu', '500m')}
          memory: {config.resources.get('memory', '1Gi')}
        limits:
          cpu: {config.resources.get('cpu', '500m')}
          memory: {config.resources.get('memory', '1Gi')}{gpu_limits}
"""

    @staticmethod
    def generate_canary_rollout(
        name: str,
        namespace: str,
        framework: MLFramework,
        current_uri: str,
        canary_uri: str,
        canary_percent: int = 10
    ) -> str:
        """Generate KServe with canary deployment."""
        framework_type = KServeGenerator.FRAMEWORK_CONFIGS.get(
            framework, {"predictor_type": "sklearn"}
        )["predictor_type"]

        return f"""# KServe Canary Deployment: {name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}
# Canary Traffic: {canary_percent}%

apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: {name}
  namespace: {namespace}
spec:
  predictor:
    canaryTrafficPercent: {canary_percent}
    {framework_type}:
      storageUri: "{canary_uri}"
      resources:
        requests:
          cpu: 1
          memory: 2Gi

---
# Note: The default predictor with {100 - canary_percent}% traffic
# is automatically managed by KServe from the previous version
# Current model: {current_uri}
# Canary model: {canary_uri}
"""


# =============================================================================
# RAY CLUSTER GENERATOR
# =============================================================================

class RayClusterGenerator:
    """Generate Ray Cluster manifests."""

    WORKER_PRESETS = {
        RayWorkerType.CPU: {
            "cpu": 4,
            "memory": "8Gi",
            "gpu": 0,
            "image": "rayproject/ray:2.7.0-py310",
        },
        RayWorkerType.GPU: {
            "cpu": 4,
            "memory": "16Gi",
            "gpu": 1,
            "image": "rayproject/ray-ml:2.7.0-py310-gpu",
        },
        RayWorkerType.HIGH_MEMORY: {
            "cpu": 8,
            "memory": "64Gi",
            "gpu": 1,
            "image": "rayproject/ray-ml:2.7.0-py310-gpu",
        },
    }

    @staticmethod
    def generate_ray_cluster(config: RayClusterConfig) -> str:
        """Generate RayCluster Custom Resource."""
        worker_preset = RayClusterGenerator.WORKER_PRESETS.get(
            config.worker_type,
            RayClusterGenerator.WORKER_PRESETS[RayWorkerType.GPU]
        )

        gpu_config = ""
        tolerations = ""
        if config.worker_gpu > 0:
            gpu_config = f"""
                nvidia.com/gpu: {config.worker_gpu}"""
            tolerations = """
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule"""

        return f"""# RayCluster: {config.name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}
# Worker Type: {config.worker_type.value}

apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: {config.name}
  namespace: {config.namespace}
spec:
  rayVersion: '{config.ray_version}'

  # Head node configuration
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      num-cpus: '0'  # Head doesn't run tasks
    template:
      spec:
        containers:
          - name: ray-head
            image: {worker_preset['image']}
            ports:
              - containerPort: 6379
                name: gcs
              - containerPort: 8265
                name: dashboard
              - containerPort: 10001
                name: client
            resources:
              requests:
                cpu: {config.head_cpu}
                memory: {config.head_memory}
              limits:
                cpu: {config.head_cpu * 2}
                memory: {config.head_memory}
            lifecycle:
              preStop:
                exec:
                  command: ["/bin/sh", "-c", "ray stop"]

  # Worker node configuration
  workerGroupSpecs:
    - groupName: {config.worker_type.value}-workers
      replicas: {config.num_workers}
      minReplicas: {config.min_workers}
      maxReplicas: {config.max_workers}
      rayStartParams:
        num-gpus: '{config.worker_gpu}'
      template:
        spec:
          containers:
            - name: ray-worker
              image: {worker_preset['image']}
              resources:
                requests:
                  cpu: {config.worker_cpu}
                  memory: {config.worker_memory}
                limits:
                  cpu: {config.worker_cpu * 2}
                  memory: {config.worker_memory}{gpu_config}
              lifecycle:
                preStop:
                  exec:
                    command: ["/bin/sh", "-c", "ray stop"]{tolerations}
"""

    @staticmethod
    def generate_ray_job(
        name: str,
        cluster_name: str,
        namespace: str = "ray-system",
        entrypoint: str = "python train.py",
        runtime_env: dict = None
    ) -> str:
        """Generate RayJob for submitting work to cluster."""
        runtime_env_yaml = ""
        if runtime_env:
            runtime_env_yaml = f"""
  runtimeEnvYAML: |
{json.dumps(runtime_env, indent=4)}"""

        return f"""# RayJob: {name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}

apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: {name}
  namespace: {namespace}
spec:
  entrypoint: {entrypoint}
  clusterSelector:
    ray.io/cluster: {cluster_name}{runtime_env_yaml}
  ttlSecondsAfterFinished: 600
  shutdownAfterJobFinishes: false
"""

    @staticmethod
    def generate_ray_service(
        name: str,
        namespace: str = "ray-system",
        serve_config: dict = None
    ) -> str:
        """Generate RayService for model serving."""
        if serve_config is None:
            serve_config = {
                "import_path": "serve_app:app",
                "num_replicas": 2,
                "ray_actor_options": {"num_gpus": 1}
            }

        return f"""# RayService: {name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}

apiVersion: ray.io/v1
kind: RayService
metadata:
  name: {name}
  namespace: {namespace}
spec:
  serveConfigV2: |
    applications:
      - name: {name}
        import_path: {serve_config.get('import_path', 'serve_app:app')}
        deployments:
          - name: model
            num_replicas: {serve_config.get('num_replicas', 2)}
            ray_actor_options:
              num_gpus: {serve_config.get('ray_actor_options', {}).get('num_gpus', 1)}
  rayClusterConfig:
    rayVersion: '2.7.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ray-head
              image: rayproject/ray-ml:2.7.0-py310-gpu
              resources:
                limits:
                  cpu: 2
                  memory: 8Gi
    workerGroupSpecs:
      - groupName: gpu-workers
        replicas: 2
        rayStartParams:
          num-gpus: '1'
        template:
          spec:
            containers:
              - name: ray-worker
                image: rayproject/ray-ml:2.7.0-py310-gpu
                resources:
                  limits:
                    cpu: 4
                    memory: 16Gi
                    nvidia.com/gpu: 1
            tolerations:
              - key: nvidia.com/gpu
                operator: Exists
                effect: NoSchedule
"""


# =============================================================================
# TRITON GENERATOR
# =============================================================================

class TritonGenerator:
    """Generate NVIDIA Triton Inference Server manifests."""

    @staticmethod
    def generate_triton_deployment(config: TritonConfig) -> str:
        """Generate Triton Deployment and Service."""
        gpu_resources = ""
        if config.gpu > 0:
            gpu_resources = f"""
                nvidia.com/gpu: {config.gpu}"""

        tolerations = ""
        if config.gpu > 0:
            tolerations = """
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule"""

        return f"""# Triton Inference Server: {config.name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {config.name}
  namespace: {config.namespace}
  labels:
    app: triton-server
spec:
  replicas: {config.replicas}
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
            - --model-repository={config.model_repository}
            - --strict-model-config=false
            - --log-verbose=1
          ports:
            - containerPort: 8000
              name: http
            - containerPort: 8001
              name: grpc
            - containerPort: 8002
              name: metrics
          resources:
            requests:
              cpu: {config.cpu}
              memory: {config.memory}
            limits:
              cpu: {config.cpu * 2}
              memory: {config.memory}{gpu_resources}
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
            sizeLimit: 50Gi{tolerations}

---
apiVersion: v1
kind: Service
metadata:
  name: {config.name}-service
  namespace: {config.namespace}
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
"""

    @staticmethod
    def generate_model_config(config: TritonModelConfig) -> str:
        """Generate Triton model config.pbtxt."""
        # Generate inputs
        inputs_config = ""
        for inp in config.inputs:
            dims = ", ".join(str(d) for d in inp.get("dims", [-1]))
            inputs_config += f"""
input [
  {{
    name: "{inp['name']}"
    data_type: {inp.get('dtype', 'TYPE_FP32')}
    dims: [ {dims} ]
  }}
]
"""

        # Generate outputs
        outputs_config = ""
        for out in config.outputs:
            dims = ", ".join(str(d) for d in out.get("dims", [-1]))
            outputs_config += f"""
output [
  {{
    name: "{out['name']}"
    data_type: {out.get('dtype', 'TYPE_FP32')}
    dims: [ {dims} ]
  }}
]
"""

        # Dynamic batching config
        batching_config = ""
        if config.dynamic_batching:
            preferred = ", ".join(str(s) for s in config.preferred_batch_sizes)
            batching_config = f"""
dynamic_batching {{
  preferred_batch_size: [ {preferred} ]
  max_queue_delay_microseconds: 100000
}}
"""

        # Instance group config
        gpus = ", ".join(str(g) for g in config.gpu_ids)
        instance_config = f"""
instance_group [
  {{
    count: {config.instance_count}
    kind: KIND_GPU
    gpus: [ {gpus} ]
  }}
]
"""

        return f"""# Triton Model Config: {config.name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}
# Backend: {config.backend.value}

name: "{config.name}"
platform: "{config.backend.value}"
max_batch_size: {config.max_batch_size}
{inputs_config}{outputs_config}{batching_config}{instance_config}
"""

    @staticmethod
    def generate_ensemble_config(
        name: str,
        steps: list,
        max_batch_size: int = 32
    ) -> str:
        """Generate Triton ensemble model config."""
        steps_config = ""
        for step in steps:
            input_map = ""
            for inp_key, inp_val in step.get("input_map", {}).items():
                input_map += f"""
        input_map {{
          key: "{inp_key}"
          value: "{inp_val}"
        }}"""
            output_map = ""
            for out_key, out_val in step.get("output_map", {}).items():
                output_map += f"""
        output_map {{
          key: "{out_key}"
          value: "{out_val}"
        }}"""

            steps_config += f"""
    {{
      model_name: "{step['model_name']}"
      model_version: {step.get('version', -1)}{input_map}{output_map}
    }}"""

        return f"""# Triton Ensemble Config: {name}
# Generated by ML Advanced K8s Toolkit on {datetime.now().strftime('%Y-%m-%d')}

name: "{name}"
platform: "ensemble"
max_batch_size: {max_batch_size}

ensemble_scheduling {{
  step [{steps_config}
  ]
}}
"""


# =============================================================================
# MANIFEST MANAGER
# =============================================================================

class ManifestManager:
    """Manage generated manifests."""

    def __init__(self):
        """Initialize manifest manager."""
        MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    def save_manifest(self, name: str, content: str, subdir: str = "") -> Path:
        """Save manifest to file."""
        if subdir:
            save_dir = MANIFESTS_DIR / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = MANIFESTS_DIR

        path = save_dir / f"{name}.yaml"
        path.write_text(content)
        return path

    def save_config(self, name: str, content: str, subdir: str = "") -> Path:
        """Save config file (e.g., config.pbtxt)."""
        if subdir:
            save_dir = MANIFESTS_DIR / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = MANIFESTS_DIR

        path = save_dir / name
        # Create parent directories if name contains subdirectories
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_kubeflow_pipelines():
    """Demo 1: Generate Kubeflow Pipeline manifests."""
    print("=" * 70)
    print("DEMO 1: KUBEFLOW PIPELINE GENERATION")
    print("=" * 70)

    manager = ManifestManager()

    # Overview
    print("\n📋 Kubeflow Pipeline Components:")
    print("-" * 40)
    print("  • Pipelines (DAG workflows)")
    print("  • Katib (Hyperparameter tuning)")
    print("  • Training Operators")
    print("  • Notebooks (Jupyter)")

    # Generate training pipeline
    print("\n🔧 Generating: ML Training Pipeline")
    print("-" * 40)

    pipeline_config = KubeflowPipelineConfig(
        name="ml-training-pipeline",
        description="End-to-end ML training pipeline",
        namespace="kubeflow",
        steps=[
            KubeflowStepConfig(
                name="preprocess",
                image="python:3.10",
                command=["python", "preprocess.py"],
                resources={"cpu": "2", "memory": "4Gi"}
            ),
            KubeflowStepConfig(
                name="train",
                image="pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime",
                command=["python", "train.py"],
                inputs=["preprocess"],
                resources={"cpu": "4", "memory": "16Gi"},
                gpu=1
            ),
            KubeflowStepConfig(
                name="evaluate",
                image="python:3.10",
                command=["python", "evaluate.py"],
                inputs=["train"],
                resources={"cpu": "2", "memory": "4Gi"}
            ),
        ],
        parameters={
            "learning_rate": "0.001",
            "batch_size": "32",
            "epochs": "10"
        }
    )

    pipeline_yaml = KubeflowPipelineGenerator.generate_pipeline(pipeline_config)
    path = manager.save_manifest("kubeflow-training-pipeline", pipeline_yaml, "kubeflow")
    print(f"  💾 Saved to: {path}")

    # Show pipeline structure
    print("\n📊 Pipeline DAG:")
    print("-" * 40)
    print("""
     ┌────────────────┐
     │   Parameters   │
     │  lr, batch, ep │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │   Preprocess   │
     │   (CPU: 2)     │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │     Train      │
     │  (GPU: 1)      │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │   Evaluate     │
     │   (CPU: 2)     │
     └────────────────┘
""")

    # Generate Katib experiment
    print("\n🔧 Generating: Katib Hyperparameter Experiment")
    print("-" * 40)

    katib_yaml = KubeflowPipelineGenerator.generate_katib_experiment(
        name="bert-tuning-experiment",
        namespace="kubeflow",
        objective_metric="accuracy",
        objective_type="maximize",
        goal=0.95,
        algorithm="bayesian",
        parameters=[
            {"name": "learning_rate", "type": "double", "min": "0.00001", "max": "0.001"},
            {"name": "batch_size", "type": "int", "min": "8", "max": "64"},
            {"name": "num_layers", "type": "int", "min": "2", "max": "6"},
        ],
        max_trials=20,
        parallel_trials=4
    )

    path = manager.save_manifest("katib-bert-tuning", katib_yaml, "kubeflow")
    print(f"  💾 Saved to: {path}")

    # Show Katib config
    print("\n📈 Katib Search Configuration:")
    print("-" * 40)
    print("  Algorithm: Bayesian Optimization")
    print("  Max Trials: 20")
    print("  Parallel Trials: 4")
    print("  Objective: Maximize accuracy (goal: 0.95)")
    print("\n  Parameters:")
    print("    • learning_rate: [0.00001, 0.001] (double)")
    print("    • batch_size: [8, 64] (int)")
    print("    • num_layers: [2, 6] (int)")

    print("\n✅ Demo 1 complete!")


def demo_2_kserve_deployments():
    """Demo 2: Generate KServe InferenceService manifests."""
    print("=" * 70)
    print("DEMO 2: KSERVE INFERENCE SERVICE GENERATION")
    print("=" * 70)

    manager = ManifestManager()

    # Overview
    print("\n📋 KServe Features:")
    print("-" * 40)
    print("  • Serverless inference")
    print("  • Auto-scaling (0 to N)")
    print("  • Canary deployments")
    print("  • Multi-framework support")
    print("  • Transformers (pre/post processing)")

    # Generate sklearn model
    print("\n🔧 Generating: SKLearn InferenceService")
    print("-" * 40)

    sklearn_config = KServeConfig(
        name="sklearn-classifier",
        namespace="ml-serving",
        framework=MLFramework.SKLEARN,
        storage_uri="gs://my-bucket/models/sklearn/classifier",
        min_replicas=1,
        max_replicas=10,
        target_concurrency=10,
        resources={"cpu": "500m", "memory": "1Gi"}
    )

    sklearn_yaml = KServeGenerator.generate_inference_service(sklearn_config)
    path = manager.save_manifest("kserve-sklearn", sklearn_yaml, "kserve")
    print(f"  💾 Saved to: {path}")

    # Generate PyTorch model with GPU
    print("\n🔧 Generating: PyTorch GPU InferenceService")
    print("-" * 40)

    pytorch_config = KServeConfig(
        name="pytorch-bert",
        namespace="ml-serving",
        framework=MLFramework.PYTORCH,
        storage_uri="gs://my-bucket/models/pytorch/bert-sentiment",
        min_replicas=1,
        max_replicas=5,
        target_concurrency=5,
        resources={"cpu": "2", "memory": "8Gi"},
        gpu=1
    )

    pytorch_yaml = KServeGenerator.generate_inference_service(pytorch_config)
    path = manager.save_manifest("kserve-pytorch-gpu", pytorch_yaml, "kserve")
    print(f"  💾 Saved to: {path}")

    # Generate canary deployment
    print("\n🔧 Generating: Canary Deployment (90/10 split)")
    print("-" * 40)

    canary_yaml = KServeGenerator.generate_canary_rollout(
        name="sentiment-classifier",
        namespace="ml-serving",
        framework=MLFramework.PYTORCH,
        current_uri="gs://my-bucket/models/sentiment-v1",
        canary_uri="gs://my-bucket/models/sentiment-v2",
        canary_percent=10
    )

    path = manager.save_manifest("kserve-canary", canary_yaml, "kserve")
    print(f"  💾 Saved to: {path}")

    # Show canary diagram
    print("\n🔄 Canary Deployment Flow:")
    print("-" * 40)
    print("""
     Incoming Traffic
           │
           ▼
     ┌───────────────────────┐
     │   Istio Gateway       │
     │   (Traffic Split)     │
     └───────────┬───────────┘
                 │
         ┌───────┴───────┐
         │               │
    90%  ▼          10%  ▼
    ┌─────────┐    ┌─────────┐
    │ Model   │    │ Model   │
    │  v1     │    │  v2     │
    │(Current)│    │(Canary) │
    └─────────┘    └─────────┘
""")

    # Generate with transformer
    print("\n🔧 Generating: InferenceService with Transformer")
    print("-" * 40)

    transformer_config = KServeConfig(
        name="image-classifier-with-transform",
        namespace="ml-serving",
        framework=MLFramework.PYTORCH,
        storage_uri="gs://my-bucket/models/resnet50",
        min_replicas=2,
        max_replicas=20,
        resources={"cpu": "4", "memory": "8Gi"},
        gpu=1,
        transformer_image="myregistry/image-transformer:latest"
    )

    transformer_yaml = KServeGenerator.generate_inference_service(transformer_config)
    path = manager.save_manifest("kserve-with-transformer", transformer_yaml, "kserve")
    print(f"  💾 Saved to: {path}")

    # Summary table
    print("\n📊 Generated KServe Deployments:")
    print("-" * 60)
    print(f"  {'Name':<35} {'Framework':<12} {'GPU'}")
    print("-" * 60)
    print(f"  {'sklearn-classifier':<35} {'sklearn':<12} {'No'}")
    print(f"  {'pytorch-bert':<35} {'pytorch':<12} {'Yes (1)'}")
    print(f"  {'sentiment-classifier (canary)':<35} {'pytorch':<12} {'Yes (1)'}")
    print(f"  {'image-classifier-with-transform':<35} {'pytorch':<12} {'Yes (1)'}")

    print("\n✅ Demo 2 complete!")


def demo_3_ray_clusters():
    """Demo 3: Generate Ray Cluster manifests."""
    print("=" * 70)
    print("DEMO 3: RAY CLUSTER GENERATION")
    print("=" * 70)

    manager = ManifestManager()

    # Overview
    print("\n📋 Ray Components:")
    print("-" * 40)
    print("  • Ray Core (distributed Python)")
    print("  • Ray Train (distributed training)")
    print("  • Ray Tune (hyperparameter tuning)")
    print("  • Ray Serve (model serving)")
    print("  • Ray Data (data processing)")

    # Generate GPU cluster
    print("\n🔧 Generating: GPU Training Cluster")
    print("-" * 40)

    gpu_cluster_config = RayClusterConfig(
        name="ml-training-cluster",
        namespace="ray-system",
        ray_version="2.7.0",
        head_cpu=2,
        head_memory="8Gi",
        worker_type=RayWorkerType.GPU,
        num_workers=4,
        min_workers=1,
        max_workers=10,
        worker_cpu=4,
        worker_memory="16Gi",
        worker_gpu=1
    )

    cluster_yaml = RayClusterGenerator.generate_ray_cluster(gpu_cluster_config)
    path = manager.save_manifest("ray-gpu-cluster", cluster_yaml, "ray")
    print(f"  💾 Saved to: {path}")

    # Show cluster diagram
    print("\n📊 Cluster Architecture:")
    print("-" * 40)
    print("""
     ┌─────────────────────────────────────────────┐
     │              RAY CLUSTER                    │
     ├─────────────────────────────────────────────┤
     │  ┌─────────────────┐                        │
     │  │   HEAD NODE     │  Dashboard: :8265      │
     │  │  CPU: 2         │  Client: :10001        │
     │  │  Memory: 8Gi    │  GCS: :6379            │
     │  └────────┬────────┘                        │
     │           │                                 │
     │  ┌────────┴────────┬──────────┬──────────┐ │
     │  │                 │          │          │ │
     │  ▼                 ▼          ▼          ▼ │
     │ ┌────────┐   ┌────────┐ ┌────────┐ ┌────────┐
     │ │Worker 1│   │Worker 2│ │Worker 3│ │Worker 4│
     │ │GPU: 1  │   │GPU: 1  │ │GPU: 1  │ │GPU: 1  │
     │ │CPU: 4  │   │CPU: 4  │ │CPU: 4  │ │CPU: 4  │
     │ └────────┘   └────────┘ └────────┘ └────────┘
     │                                             │
     │  Auto-scaling: 1-10 workers                 │
     └─────────────────────────────────────────────┘
""")

    # Generate high-memory cluster
    print("\n🔧 Generating: High-Memory Cluster (LLM Training)")
    print("-" * 40)

    hm_cluster_config = RayClusterConfig(
        name="llm-training-cluster",
        namespace="ray-system",
        worker_type=RayWorkerType.HIGH_MEMORY,
        num_workers=2,
        min_workers=1,
        max_workers=4,
        worker_cpu=8,
        worker_memory="64Gi",
        worker_gpu=1
    )

    hm_cluster_yaml = RayClusterGenerator.generate_ray_cluster(hm_cluster_config)
    path = manager.save_manifest("ray-high-memory-cluster", hm_cluster_yaml, "ray")
    print(f"  💾 Saved to: {path}")

    # Generate RayJob
    print("\n🔧 Generating: Ray Training Job")
    print("-" * 40)

    job_yaml = RayClusterGenerator.generate_ray_job(
        name="distributed-training-job",
        cluster_name="ml-training-cluster",
        namespace="ray-system",
        entrypoint="python train.py --epochs 10",
        runtime_env={
            "pip": ["torch", "transformers", "datasets"],
            "working_dir": "s3://my-bucket/code/training"
        }
    )

    path = manager.save_manifest("ray-training-job", job_yaml, "ray")
    print(f"  💾 Saved to: {path}")

    # Generate RayService
    print("\n🔧 Generating: Ray Serve Deployment")
    print("-" * 40)

    service_yaml = RayClusterGenerator.generate_ray_service(
        name="ml-inference-service",
        namespace="ray-system",
        serve_config={
            "import_path": "model_serve:app",
            "num_replicas": 4,
            "ray_actor_options": {"num_gpus": 1}
        }
    )

    path = manager.save_manifest("ray-service", service_yaml, "ray")
    print(f"  💾 Saved to: {path}")

    # Summary table
    print("\n📊 Generated Ray Resources:")
    print("-" * 60)
    print(f"  {'Resource':<30} {'Workers':<12} {'GPUs'}")
    print("-" * 60)
    print(f"  {'ml-training-cluster':<30} {'4 (1-10)':<12} {'4'}")
    print(f"  {'llm-training-cluster':<30} {'2 (1-4)':<12} {'2'}")
    print(f"  {'distributed-training-job':<30} {'Uses cluster':<12} {'-'}")
    print(f"  {'ml-inference-service':<30} {'4 replicas':<12} {'4'}")

    print("\n✅ Demo 3 complete!")


def demo_4_triton_server():
    """Demo 4: Generate NVIDIA Triton Inference Server manifests."""
    print("=" * 70)
    print("DEMO 4: NVIDIA TRITON INFERENCE SERVER GENERATION")
    print("=" * 70)

    manager = ManifestManager()

    # Overview
    print("\n📋 Triton Features:")
    print("-" * 40)
    print("  • Multi-framework (TF, PyTorch, ONNX, TensorRT)")
    print("  • Dynamic batching (10x throughput)")
    print("  • Model ensemble pipelines")
    print("  • HTTP/gRPC/C API")
    print("  • Prometheus metrics")

    # Generate Triton deployment
    print("\n🔧 Generating: Triton Server Deployment")
    print("-" * 40)

    triton_config = TritonConfig(
        name="triton-inference-server",
        namespace="ml-serving",
        model_repository="s3://my-bucket/models",
        replicas=2,
        cpu=4,
        memory="16Gi",
        gpu=2,
        enable_metrics=True,
        dynamic_batching=True
    )

    triton_yaml = TritonGenerator.generate_triton_deployment(triton_config)
    path = manager.save_manifest("triton-deployment", triton_yaml, "triton")
    print(f"  💾 Saved to: {path}")

    # Show architecture
    print("\n📊 Triton Architecture:")
    print("-" * 40)
    print("""
     ┌─────────────────────────────────────────────┐
     │         TRITON INFERENCE SERVER             │
     ├─────────────────────────────────────────────┤
     │  Ports:                                     │
     │    HTTP:    8000  (REST API)                │
     │    gRPC:    8001  (High performance)        │
     │    Metrics: 8002  (Prometheus)              │
     ├─────────────────────────────────────────────┤
     │  ┌─────────────────────────────────┐        │
     │  │     Dynamic Batching Scheduler  │        │
     │  │  (Wait up to 100ms, batch 8-32) │        │
     │  └───────────────┬─────────────────┘        │
     │                  │                          │
     │    ┌─────────────┼─────────────┐            │
     │    │             │             │            │
     │    ▼             ▼             ▼            │
     │  ┌─────┐     ┌─────┐     ┌─────┐          │
     │  │ TF  │     │ PT  │     │ONNX │          │
     │  │Back │     │Back │     │Back │          │
     │  └─────┘     └─────┘     └─────┘          │
     │                                            │
     │  GPU: 2x NVIDIA                            │
     │  Replicas: 2                               │
     └─────────────────────────────────────────────┘
""")

    # Generate model config
    print("\n🔧 Generating: BERT Model Config (config.pbtxt)")
    print("-" * 40)

    bert_config = TritonModelConfig(
        name="bert_sentiment",
        backend=TritonBackend.ONNX,
        max_batch_size=32,
        inputs=[
            {"name": "input_ids", "dtype": "TYPE_INT64", "dims": [-1]},
            {"name": "attention_mask", "dtype": "TYPE_INT64", "dims": [-1]},
        ],
        outputs=[
            {"name": "logits", "dtype": "TYPE_FP32", "dims": [2]},
        ],
        instance_count=2,
        gpu_ids=[0, 1],
        dynamic_batching=True,
        preferred_batch_sizes=[8, 16, 32]
    )

    config_pbtxt = TritonGenerator.generate_model_config(bert_config)
    path = manager.save_config("bert_sentiment/config.pbtxt", config_pbtxt, "triton/models")
    print(f"  💾 Saved to: {path}")

    # Show config preview
    print("\n  Config Preview:")
    for line in config_pbtxt.split('\n')[:20]:
        print(f"    {line}")
    print("    ...")

    # Generate ResNet config
    print("\n🔧 Generating: ResNet Model Config")
    print("-" * 40)

    resnet_config = TritonModelConfig(
        name="resnet50",
        backend=TritonBackend.TENSORRT,
        max_batch_size=64,
        inputs=[
            {"name": "input", "dtype": "TYPE_FP32", "dims": [3, 224, 224]},
        ],
        outputs=[
            {"name": "output", "dtype": "TYPE_FP32", "dims": [1000]},
        ],
        instance_count=2,
        gpu_ids=[0, 1],
        dynamic_batching=True,
        preferred_batch_sizes=[16, 32, 64]
    )

    config_pbtxt = TritonGenerator.generate_model_config(resnet_config)
    path = manager.save_config("resnet50/config.pbtxt", config_pbtxt, "triton/models")
    print(f"  💾 Saved to: {path}")

    # Generate ensemble config
    print("\n🔧 Generating: Ensemble Pipeline Config")
    print("-" * 40)

    ensemble_config = TritonGenerator.generate_ensemble_config(
        name="image_pipeline",
        steps=[
            {
                "model_name": "image_preprocessor",
                "version": -1,
                "input_map": {"raw_image": "raw_image"},
                "output_map": {"processed_image": "preprocessed"}
            },
            {
                "model_name": "resnet50",
                "version": -1,
                "input_map": {"input": "preprocessed"},
                "output_map": {"output": "classification"}
            }
        ],
        max_batch_size=32
    )

    path = manager.save_config("image_pipeline/config.pbtxt", ensemble_config, "triton/models")
    print(f"  💾 Saved to: {path}")

    # Show ensemble diagram
    print("\n📊 Ensemble Pipeline:")
    print("-" * 40)
    print("""
     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
     │  Raw Image  │────►│ Preprocessor│────►│  ResNet50   │
     │  (UINT8)    │     │  (Python)   │     │ (TensorRT)  │
     └─────────────┘     └─────────────┘     └─────────────┘
                              │                     │
                         Resize, Norm          Classification
                              │                     │
                              ▼                     ▼
                        [3, 224, 224]        [1000 classes]
""")

    # Summary
    print("\n📊 Generated Triton Resources:")
    print("-" * 60)
    print(f"  {'Resource':<35} {'Type':<15} {'GPUs'}")
    print("-" * 60)
    print(f"  {'triton-inference-server':<35} {'Deployment':<15} {'2'}")
    print(f"  {'bert_sentiment/config.pbtxt':<35} {'Model Config':<15} {'2'}")
    print(f"  {'resnet50/config.pbtxt':<35} {'Model Config':<15} {'2'}")
    print(f"  {'image_pipeline/config.pbtxt':<35} {'Ensemble':<15} {'-'}")

    print("\n✅ Demo 4 complete!")


def demo_5_full_ml_platform():
    """Demo 5: Generate complete ML platform stack."""
    print("=" * 70)
    print("DEMO 5: COMPLETE ML PLATFORM STACK")
    print("=" * 70)

    manager = ManifestManager()

    platform_name = "ml-platform"
    namespace = "ml-production"

    print(f"\n🚀 Generating complete stack for: {platform_name}")
    print("-" * 40)

    # Create stack directory
    stack_dir = f"stacks/{platform_name}"

    # 1. Namespace
    print("\n1️⃣ Generating Namespace...")
    namespace_yaml = f"""# Namespace for ML Platform
apiVersion: v1
kind: Namespace
metadata:
  name: {namespace}
  labels:
    istio-injection: enabled
"""
    path = manager.save_manifest("01-namespace", namespace_yaml, stack_dir)
    print(f"   ✅ {namespace}")

    # 2. Ray Cluster for training
    print("\n2️⃣ Generating Ray Cluster (Training)...")
    ray_config = RayClusterConfig(
        name=f"{platform_name}-ray",
        namespace=namespace,
        worker_type=RayWorkerType.GPU,
        num_workers=4,
        max_workers=8
    )
    ray_yaml = RayClusterGenerator.generate_ray_cluster(ray_config)
    path = manager.save_manifest("02-ray-cluster", ray_yaml, stack_dir)
    print(f"   ✅ {platform_name}-ray (4-8 GPU workers)")

    # 3. Triton for high-performance inference
    print("\n3️⃣ Generating Triton Server (Inference)...")
    triton_config = TritonConfig(
        name=f"{platform_name}-triton",
        namespace=namespace,
        model_repository=f"s3://my-bucket/{platform_name}/models",
        replicas=2,
        gpu=2
    )
    triton_yaml = TritonGenerator.generate_triton_deployment(triton_config)
    path = manager.save_manifest("03-triton-server", triton_yaml, stack_dir)
    print(f"   ✅ {platform_name}-triton (2 replicas, 4 GPUs)")

    # 4. KServe for serverless inference
    print("\n4️⃣ Generating KServe InferenceServices...")

    # Primary model
    kserve_primary = KServeConfig(
        name=f"{platform_name}-classifier",
        namespace=namespace,
        framework=MLFramework.PYTORCH,
        storage_uri=f"gs://my-bucket/{platform_name}/models/classifier",
        min_replicas=2,
        max_replicas=20,
        gpu=1
    )
    kserve_primary_yaml = KServeGenerator.generate_inference_service(kserve_primary)
    path = manager.save_manifest("04-kserve-classifier", kserve_primary_yaml, stack_dir)
    print(f"   ✅ {platform_name}-classifier (2-20 replicas)")

    # Embedding model
    kserve_embed = KServeConfig(
        name=f"{platform_name}-embeddings",
        namespace=namespace,
        framework=MLFramework.HUGGINGFACE,
        storage_uri=f"gs://my-bucket/{platform_name}/models/embeddings",
        min_replicas=1,
        max_replicas=10,
        gpu=1
    )
    kserve_embed_yaml = KServeGenerator.generate_inference_service(kserve_embed)
    path = manager.save_manifest("05-kserve-embeddings", kserve_embed_yaml, stack_dir)
    print(f"   ✅ {platform_name}-embeddings (1-10 replicas)")

    # 5. Kubeflow Pipeline for training
    print("\n5️⃣ Generating Kubeflow Pipeline...")
    pipeline_config = KubeflowPipelineConfig(
        name=f"{platform_name}-training",
        namespace="kubeflow",
        steps=[
            KubeflowStepConfig(
                name="fetch-data",
                image="python:3.10",
                command=["python", "fetch_data.py"]
            ),
            KubeflowStepConfig(
                name="preprocess",
                image="python:3.10",
                command=["python", "preprocess.py"],
                inputs=["fetch-data"]
            ),
            KubeflowStepConfig(
                name="train",
                image="pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime",
                command=["python", "train.py"],
                inputs=["preprocess"],
                gpu=1
            ),
            KubeflowStepConfig(
                name="evaluate",
                image="python:3.10",
                command=["python", "evaluate.py"],
                inputs=["train"]
            ),
            KubeflowStepConfig(
                name="deploy",
                image="bitnami/kubectl:latest",
                command=["kubectl", "apply", "-f", "kserve.yaml"],
                inputs=["evaluate"]
            ),
        ],
        parameters={"model_name": platform_name, "epochs": "10"}
    )
    pipeline_yaml = KubeflowPipelineGenerator.generate_pipeline(pipeline_config)
    path = manager.save_manifest("06-kubeflow-pipeline", pipeline_yaml, stack_dir)
    print(f"   ✅ {platform_name}-training pipeline")

    # 6. Katib for hyperparameter tuning
    print("\n6️⃣ Generating Katib Experiment...")
    katib_yaml = KubeflowPipelineGenerator.generate_katib_experiment(
        name=f"{platform_name}-hpo",
        namespace="kubeflow",
        objective_metric="val_accuracy",
        goal=0.95,
        algorithm="bayesian",
        max_trials=20,
        parallel_trials=4
    )
    path = manager.save_manifest("07-katib-experiment", katib_yaml, stack_dir)
    print(f"   ✅ {platform_name}-hpo (Bayesian, 20 trials)")

    # Generate all-in-one manifest
    print("\n7️⃣ Generating All-in-One Manifest...")
    all_manifests = [
        namespace_yaml,
        ray_yaml,
        triton_yaml,
        kserve_primary_yaml,
        kserve_embed_yaml,
    ]
    all_in_one = "\n---\n".join(all_manifests)
    path = manager.save_manifest("all-in-one", all_in_one, stack_dir)
    print(f"   ✅ all-in-one.yaml")

    # Show platform architecture
    print("\n" + "=" * 70)
    print("📁 Generated Platform Structure:")
    print("=" * 70)
    print(f"""
{platform_name}/
├── 01-namespace.yaml           # Namespace: {namespace}
├── 02-ray-cluster.yaml         # Ray cluster for training
├── 03-triton-server.yaml       # Triton for high-throughput inference
├── 04-kserve-classifier.yaml   # KServe classifier service
├── 05-kserve-embeddings.yaml   # KServe embedding service
├── 06-kubeflow-pipeline.yaml   # Training pipeline
├── 07-katib-experiment.yaml    # Hyperparameter tuning
└── all-in-one.yaml             # Combined manifest
""")

    # Platform architecture diagram
    print("📊 Platform Architecture:")
    print("-" * 70)
    print("""
┌─────────────────────────────────────────────────────────────────────────┐
│                         ML PLATFORM STACK                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TRAINING LAYER                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │   │
│  │  │   Kubeflow   │───►│     Ray      │───►│    Katib     │       │   │
│  │  │  Pipelines   │    │   Cluster    │    │    (HPO)     │       │   │
│  │  └──────────────┘    │  (4-8 GPU)   │    └──────────────┘       │   │
│  │                      └──────────────┘                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ Model artifacts                    │
│                                    ▼                                    │
│  SERVING LAYER                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ┌──────────────────────┐    ┌──────────────────────┐           │   │
│  │  │       Triton         │    │       KServe         │           │   │
│  │  │  (High-throughput)   │    │    (Serverless)      │           │   │
│  │  │  - Dynamic batching  │    │  - Auto-scaling      │           │   │
│  │  │  - Multi-model       │    │  - Canary deploys    │           │   │
│  │  │  - 4 GPUs            │    │  - 2 services        │           │   │
│  │  └──────────────────────┘    └──────────────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
""")

    # Deployment commands
    print("\n🚀 Deployment Commands:")
    print("-" * 40)
    print(f"""
  # Deploy all at once
  kubectl apply -f {MANIFESTS_DIR}/{stack_dir}/all-in-one.yaml

  # Or deploy individually
  kubectl apply -f {MANIFESTS_DIR}/{stack_dir}/01-namespace.yaml
  kubectl apply -f {MANIFESTS_DIR}/{stack_dir}/02-ray-cluster.yaml
  kubectl apply -f {MANIFESTS_DIR}/{stack_dir}/03-triton-server.yaml
  kubectl apply -f {MANIFESTS_DIR}/{stack_dir}/04-kserve-classifier.yaml
  kubectl apply -f {MANIFESTS_DIR}/{stack_dir}/05-kserve-embeddings.yaml

  # Check status
  kubectl get all -n {namespace}
  kubectl get rayclusters -n {namespace}
  kubectl get inferenceservices -n {namespace}
""")

    print("\n✅ Demo 5 complete!")
    print(f"\n📂 All files saved to: {MANIFESTS_DIR}/{stack_dir}")


def show_usage():
    """Show usage information."""
    print("""
ML Advanced Kubernetes Toolkit
==============================

Generate production-ready manifests for advanced ML platforms on Kubernetes.

Usage:
    python deliverable_ml_advanced_k8s_toolkit.py <demo>

Demos:
    demo1   Kubeflow Pipelines & Katib
    demo2   KServe InferenceServices
    demo3   Ray Clusters & Jobs
    demo4   NVIDIA Triton Server
    demo5   Complete ML Platform Stack

Examples:
    python deliverable_ml_advanced_k8s_toolkit.py demo1
    python deliverable_ml_advanced_k8s_toolkit.py demo5

Output:
    Generated manifests are saved to .ml_advanced_k8s_toolkit/manifests/
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_kubeflow_pipelines,
        "demo2": demo_2_kserve_deployments,
        "demo3": demo_3_ray_clusters,
        "demo4": demo_4_triton_server,
        "demo5": demo_5_full_ml_platform,
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
