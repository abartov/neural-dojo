#!/usr/bin/env python3
"""
Module 46 Deliverable: ML Kubernetes Toolkit

A comprehensive toolkit for deploying ML workloads on Kubernetes including:
- Manifest generation for deployments, services, jobs
- GPU scheduling configuration
- Resource quota management
- Autoscaling configuration
- Storage setup for models

Author: Neural Dojo
"""

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

STORAGE_DIR = Path(".ml_k8s_toolkit")
MANIFESTS_DIR = STORAGE_DIR / "manifests"


class WorkloadType(Enum):
    """Types of ML workloads."""
    INFERENCE = "inference"
    TRAINING = "training"
    BATCH = "batch"
    NOTEBOOK = "notebook"


class ServiceType(Enum):
    """Kubernetes service types."""
    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"


class GPUType(Enum):
    """GPU types for scheduling."""
    NONE = "none"
    NVIDIA_T4 = "nvidia-tesla-t4"
    NVIDIA_V100 = "nvidia-tesla-v100"
    NVIDIA_A100 = "nvidia-tesla-a100"
    NVIDIA_A10G = "nvidia-tesla-a10g"


class AccessMode(Enum):
    """PVC access modes."""
    RWO = "ReadWriteOnce"
    ROX = "ReadOnlyMany"
    RWX = "ReadWriteMany"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ResourceConfig:
    """Resource requests and limits."""
    cpu_request: str = "500m"
    cpu_limit: str = "1000m"
    memory_request: str = "1Gi"
    memory_limit: str = "2Gi"
    gpu_count: int = 0
    gpu_type: GPUType = GPUType.NONE


@dataclass
class DeploymentConfig:
    """Configuration for a Kubernetes deployment."""
    name: str
    image: str
    replicas: int = 3
    namespace: str = "default"
    port: int = 8000
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    env_vars: dict = field(default_factory=dict)
    config_map: Optional[str] = None
    secret: Optional[str] = None
    health_path: str = "/health"
    model_volume: Optional[str] = None
    node_selector: dict = field(default_factory=dict)


@dataclass
class ServiceConfig:
    """Configuration for a Kubernetes service."""
    name: str
    deployment: str
    port: int = 80
    target_port: int = 8000
    service_type: ServiceType = ServiceType.CLUSTER_IP
    namespace: str = "default"


@dataclass
class JobConfig:
    """Configuration for a Kubernetes job."""
    name: str
    image: str
    namespace: str = "default"
    command: list = field(default_factory=list)
    args: list = field(default_factory=list)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    env_vars: dict = field(default_factory=dict)
    data_volume: Optional[str] = None
    checkpoint_volume: Optional[str] = None
    backoff_limit: int = 3
    ttl_seconds: int = 3600


@dataclass
class HPAConfig:
    """Configuration for Horizontal Pod Autoscaler."""
    name: str
    deployment: str
    namespace: str = "default"
    min_replicas: int = 2
    max_replicas: int = 10
    cpu_target: int = 70
    memory_target: int = 80
    scale_down_window: int = 300


@dataclass
class PVCConfig:
    """Configuration for PersistentVolumeClaim."""
    name: str
    namespace: str = "default"
    size: str = "10Gi"
    access_mode: AccessMode = AccessMode.RWO
    storage_class: str = "standard"


# =============================================================================
# MANIFEST GENERATORS
# =============================================================================

class ManifestGenerator:
    """Generates Kubernetes manifests for ML workloads."""

    def __init__(self):
        """Initialize the generator."""
        pass

    def generate_deployment(self, config: DeploymentConfig) -> str:
        """Generate a Deployment manifest."""
        # Build container spec
        container = {
            "name": config.name,
            "image": config.image,
            "ports": [{"containerPort": config.port}],
            "resources": {
                "requests": {
                    "cpu": config.resources.cpu_request,
                    "memory": config.resources.memory_request,
                },
                "limits": {
                    "cpu": config.resources.cpu_limit,
                    "memory": config.resources.memory_limit,
                },
            },
            "readinessProbe": {
                "httpGet": {
                    "path": config.health_path,
                    "port": config.port,
                },
                "initialDelaySeconds": 30,
                "periodSeconds": 10,
            },
            "livenessProbe": {
                "httpGet": {
                    "path": config.health_path,
                    "port": config.port,
                },
                "initialDelaySeconds": 60,
                "periodSeconds": 30,
            },
        }

        # Add GPU resources
        if config.resources.gpu_count > 0:
            container["resources"]["limits"]["nvidia.com/gpu"] = config.resources.gpu_count

        # Add environment variables
        if config.env_vars:
            container["env"] = [
                {"name": k, "value": str(v)} for k, v in config.env_vars.items()
            ]

        # Add config map reference
        if config.config_map:
            container["envFrom"] = [{"configMapRef": {"name": config.config_map}}]

        # Add volume mounts
        volume_mounts = []
        volumes = []

        if config.model_volume:
            volume_mounts.append({
                "name": "model-storage",
                "mountPath": "/models",
            })
            volumes.append({
                "name": "model-storage",
                "persistentVolumeClaim": {"claimName": config.model_volume},
            })

        if volume_mounts:
            container["volumeMounts"] = volume_mounts

        # Build pod spec
        pod_spec = {
            "containers": [container],
        }

        if volumes:
            pod_spec["volumes"] = volumes

        if config.node_selector:
            pod_spec["nodeSelector"] = config.node_selector

        # Add GPU tolerations
        if config.resources.gpu_count > 0:
            pod_spec["tolerations"] = [{
                "key": "nvidia.com/gpu",
                "operator": "Exists",
                "effect": "NoSchedule",
            }]
            if config.resources.gpu_type != GPUType.NONE:
                pod_spec["nodeSelector"] = {
                    "accelerator": config.resources.gpu_type.value
                }

        # Build deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "labels": {"app": config.name},
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {"app": config.name},
                },
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxSurge": 1,
                        "maxUnavailable": 0,
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {"app": config.name},
                    },
                    "spec": pod_spec,
                },
            },
        }

        return self._to_yaml(deployment)

    def generate_service(self, config: ServiceConfig) -> str:
        """Generate a Service manifest."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
            },
            "spec": {
                "selector": {"app": config.deployment},
                "ports": [{
                    "port": config.port,
                    "targetPort": config.target_port,
                }],
                "type": config.service_type.value,
            },
        }

        return self._to_yaml(service)

    def generate_job(self, config: JobConfig) -> str:
        """Generate a Job manifest."""
        container = {
            "name": config.name,
            "image": config.image,
            "resources": {
                "limits": {
                    "cpu": config.resources.cpu_limit,
                    "memory": config.resources.memory_limit,
                },
            },
        }

        if config.command:
            container["command"] = config.command
        if config.args:
            container["args"] = config.args

        # Add GPU
        if config.resources.gpu_count > 0:
            container["resources"]["limits"]["nvidia.com/gpu"] = config.resources.gpu_count

        # Add env vars
        if config.env_vars:
            container["env"] = [
                {"name": k, "value": str(v)} for k, v in config.env_vars.items()
            ]

        # Add volume mounts
        volume_mounts = []
        volumes = []

        if config.data_volume:
            volume_mounts.append({
                "name": "data",
                "mountPath": "/data",
            })
            volumes.append({
                "name": "data",
                "persistentVolumeClaim": {"claimName": config.data_volume},
            })

        if config.checkpoint_volume:
            volume_mounts.append({
                "name": "checkpoints",
                "mountPath": "/checkpoints",
            })
            volumes.append({
                "name": "checkpoints",
                "persistentVolumeClaim": {"claimName": config.checkpoint_volume},
            })

        if volume_mounts:
            container["volumeMounts"] = volume_mounts

        pod_spec = {
            "containers": [container],
            "restartPolicy": "OnFailure",
        }

        if volumes:
            pod_spec["volumes"] = volumes

        # GPU scheduling
        if config.resources.gpu_count > 0:
            pod_spec["tolerations"] = [{
                "key": "nvidia.com/gpu",
                "operator": "Exists",
                "effect": "NoSchedule",
            }]
            if config.resources.gpu_type != GPUType.NONE:
                pod_spec["nodeSelector"] = {
                    "accelerator": config.resources.gpu_type.value
                }

        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
            },
            "spec": {
                "backoffLimit": config.backoff_limit,
                "ttlSecondsAfterFinished": config.ttl_seconds,
                "template": {
                    "spec": pod_spec,
                },
            },
        }

        return self._to_yaml(job)

    def generate_hpa(self, config: HPAConfig) -> str:
        """Generate a HorizontalPodAutoscaler manifest."""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": config.deployment,
                },
                "minReplicas": config.min_replicas,
                "maxReplicas": config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.cpu_target,
                            },
                        },
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.memory_target,
                            },
                        },
                    },
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": config.scale_down_window,
                        "policies": [{
                            "type": "Percent",
                            "value": 10,
                            "periodSeconds": 60,
                        }],
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 0,
                        "policies": [{
                            "type": "Percent",
                            "value": 100,
                            "periodSeconds": 15,
                        }],
                    },
                },
            },
        }

        return self._to_yaml(hpa)

    def generate_pvc(self, config: PVCConfig) -> str:
        """Generate a PersistentVolumeClaim manifest."""
        pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
            },
            "spec": {
                "accessModes": [config.access_mode.value],
                "resources": {
                    "requests": {
                        "storage": config.size,
                    },
                },
                "storageClassName": config.storage_class,
            },
        }

        return self._to_yaml(pvc)

    def generate_namespace(self, name: str) -> str:
        """Generate a Namespace manifest."""
        ns = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": name,
            },
        }
        return self._to_yaml(ns)

    def generate_config_map(self, name: str, namespace: str, data: dict) -> str:
        """Generate a ConfigMap manifest."""
        cm = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": namespace,
            },
            "data": {k: str(v) for k, v in data.items()},
        }
        return self._to_yaml(cm)

    def _to_yaml(self, obj: dict, indent: int = 0) -> str:
        """Convert dict to YAML string (simple implementation)."""
        lines = []
        self._dict_to_yaml(obj, lines, indent)
        return "\n".join(lines)

    def _dict_to_yaml(self, obj, lines, indent):
        """Recursively convert dict to YAML lines."""
        prefix = "  " * indent

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)) and value:
                    lines.append(f"{prefix}{key}:")
                    self._dict_to_yaml(value, lines, indent + 1)
                elif isinstance(value, list) and not value:
                    lines.append(f"{prefix}{key}: []")
                elif isinstance(value, dict) and not value:
                    lines.append(f"{prefix}{key}: {{}}")
                elif value is None:
                    lines.append(f"{prefix}{key}: null")
                elif isinstance(value, bool):
                    lines.append(f"{prefix}{key}: {str(value).lower()}")
                elif isinstance(value, (int, float)):
                    lines.append(f"{prefix}{key}: {value}")
                else:
                    # String value
                    if "\n" in str(value) or ":" in str(value):
                        lines.append(f'{prefix}{key}: "{value}"')
                    else:
                        lines.append(f"{prefix}{key}: {value}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    first = True
                    for key, value in item.items():
                        if first:
                            lines.append(f"{prefix}- {key}:")
                            first = False
                            if isinstance(value, (dict, list)) and value:
                                self._dict_to_yaml(value, lines, indent + 2)
                            else:
                                # Remove last line and add inline
                                lines[-1] = f"{prefix}- {key}: {value}"
                        else:
                            if isinstance(value, (dict, list)) and value:
                                lines.append(f"{prefix}  {key}:")
                                self._dict_to_yaml(value, lines, indent + 2)
                            else:
                                lines.append(f"{prefix}  {key}: {value}")
                else:
                    lines.append(f"{prefix}- {item}")

    def save(self, manifest: str, filename: str) -> Path:
        """Save manifest to file."""
        MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = MANIFESTS_DIR / filename
        with open(filepath, 'w') as f:
            f.write(manifest)
        return filepath


# =============================================================================
# PRESETS
# =============================================================================

DEPLOYMENT_PRESETS = {
    "inference-cpu": DeploymentConfig(
        name="ml-inference",
        image="myregistry/model:latest",
        replicas=3,
        port=8000,
        resources=ResourceConfig(
            cpu_request="500m",
            cpu_limit="1000m",
            memory_request="1Gi",
            memory_limit="2Gi",
        ),
    ),
    "inference-gpu": DeploymentConfig(
        name="ml-inference-gpu",
        image="myregistry/model:latest",
        replicas=2,
        port=8000,
        resources=ResourceConfig(
            cpu_request="2",
            cpu_limit="4",
            memory_request="8Gi",
            memory_limit="16Gi",
            gpu_count=1,
            gpu_type=GPUType.NVIDIA_T4,
        ),
    ),
    "high-memory": DeploymentConfig(
        name="llm-inference",
        image="myregistry/llm:latest",
        replicas=2,
        port=8000,
        resources=ResourceConfig(
            cpu_request="4",
            cpu_limit="8",
            memory_request="32Gi",
            memory_limit="64Gi",
            gpu_count=1,
            gpu_type=GPUType.NVIDIA_A100,
        ),
    ),
}

JOB_PRESETS = {
    "training-gpu": JobConfig(
        name="model-training",
        image="pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime",
        command=["python", "train.py"],
        args=["--epochs=10", "--batch-size=32"],
        resources=ResourceConfig(
            cpu_limit="8",
            memory_limit="32Gi",
            gpu_count=1,
            gpu_type=GPUType.NVIDIA_V100,
        ),
    ),
    "distributed-training": JobConfig(
        name="distributed-training",
        image="pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime",
        command=["torchrun", "--nproc_per_node=4", "train.py"],
        resources=ResourceConfig(
            cpu_limit="16",
            memory_limit="64Gi",
            gpu_count=4,
            gpu_type=GPUType.NVIDIA_A100,
        ),
    ),
    "batch-inference": JobConfig(
        name="batch-inference",
        image="myregistry/batch:latest",
        command=["python", "batch_predict.py"],
        resources=ResourceConfig(
            cpu_limit="4",
            memory_limit="8Gi",
        ),
    ),
}


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_deployment_generation():
    """Demo 1: Generate Kubernetes deployments for ML."""
    print("=" * 70)
    print("DEMO 1: DEPLOYMENT MANIFEST GENERATION")
    print("=" * 70)
    print()

    generator = ManifestGenerator()

    print("📋 Available Deployment Presets:")
    print("-" * 40)
    for name, config in DEPLOYMENT_PRESETS.items():
        gpu = f"🎮 {config.resources.gpu_count} GPU" if config.resources.gpu_count > 0 else "💻 CPU"
        print(f"  • {name}")
        print(f"    {gpu} | {config.replicas} replicas | {config.resources.memory_limit} memory")
    print()

    # Generate CPU inference deployment
    print("🔧 Generating: CPU Inference Deployment")
    print("-" * 40)

    config = DEPLOYMENT_PRESETS["inference-cpu"]
    manifest = generator.generate_deployment(config)

    lines = manifest.split('\n')
    for line in lines[:35]:
        print(f"  {line}")
    print(f"  ... ({len(lines) - 35} more lines)")
    print()

    path = generator.save(manifest, "deployment-inference-cpu.yaml")
    print(f"💾 Saved to: {path}")
    print()

    # Generate GPU inference deployment
    print("🔧 Generating: GPU Inference Deployment")
    print("-" * 40)

    config = DEPLOYMENT_PRESETS["inference-gpu"]
    manifest = generator.generate_deployment(config)

    lines = manifest.split('\n')
    for line in lines[:40]:
        print(f"  {line}")
    print(f"  ... ({len(lines) - 40} more lines)")
    print()

    path = generator.save(manifest, "deployment-inference-gpu.yaml")
    print(f"💾 Saved to: {path}")
    print()

    print("✅ Demo 1 complete!")


def demo_2_training_jobs():
    """Demo 2: Generate training job manifests."""
    print("=" * 70)
    print("DEMO 2: TRAINING JOB GENERATION")
    print("=" * 70)
    print()

    generator = ManifestGenerator()

    print("📋 Available Job Presets:")
    print("-" * 40)
    for name, config in JOB_PRESETS.items():
        gpu = f"🎮 {config.resources.gpu_count} GPU" if config.resources.gpu_count > 0 else "💻 CPU"
        print(f"  • {name}")
        print(f"    {gpu} | {config.resources.memory_limit} memory")
    print()

    # Generate GPU training job
    print("🔧 Generating: GPU Training Job")
    print("-" * 40)

    config = JOB_PRESETS["training-gpu"]
    config.data_volume = "training-data"
    config.checkpoint_volume = "checkpoints"

    manifest = generator.generate_job(config)

    for line in manifest.split('\n'):
        print(f"  {line}")
    print()

    path = generator.save(manifest, "job-training-gpu.yaml")
    print(f"💾 Saved to: {path}")
    print()

    # Generate distributed training job
    print("🔧 Generating: Distributed Training Job (4 GPU)")
    print("-" * 40)

    config = JOB_PRESETS["distributed-training"]
    manifest = generator.generate_job(config)

    for line in manifest.split('\n')[:30]:
        print(f"  {line}")
    print(f"  ...")
    print()

    path = generator.save(manifest, "job-distributed-training.yaml")
    print(f"💾 Saved to: {path}")
    print()

    print("✅ Demo 2 complete!")


def demo_3_autoscaling():
    """Demo 3: Generate autoscaling configuration."""
    print("=" * 70)
    print("DEMO 3: AUTOSCALING CONFIGURATION")
    print("=" * 70)
    print()

    generator = ManifestGenerator()

    print("📊 Autoscaling Overview:")
    print("-" * 40)
    print("""
  HPA (Horizontal Pod Autoscaler):
  ┌─────────────────────────────────────────────┐
  │  Metrics (CPU/Memory/Custom)                │
  │           │                                 │
  │           ▼                                 │
  │  ┌─────────────────┐                       │
  │  │  Scale Decision │                       │
  │  └────────┬────────┘                       │
  │           │                                 │
  │           ▼                                 │
  │  Replicas: 2 ──► 3 ──► 5 ──► 10           │
  └─────────────────────────────────────────────┘
""")

    # Generate HPA
    print("🔧 Generating: HPA for Inference Service")
    print("-" * 40)

    hpa_config = HPAConfig(
        name="inference-hpa",
        deployment="ml-inference",
        namespace="ml-serving",
        min_replicas=2,
        max_replicas=20,
        cpu_target=70,
        memory_target=80,
        scale_down_window=300,
    )

    manifest = generator.generate_hpa(hpa_config)

    for line in manifest.split('\n'):
        print(f"  {line}")
    print()

    path = generator.save(manifest, "hpa-inference.yaml")
    print(f"💾 Saved to: {path}")
    print()

    # Explain scaling behavior
    print("📈 Scaling Behavior:")
    print("-" * 40)
    print(f"  Target CPU: {hpa_config.cpu_target}%")
    print(f"  Target Memory: {hpa_config.memory_target}%")
    print(f"  Min Replicas: {hpa_config.min_replicas}")
    print(f"  Max Replicas: {hpa_config.max_replicas}")
    print(f"  Scale Down Window: {hpa_config.scale_down_window}s")
    print()
    print("  Scale Up: Immediate (no stabilization)")
    print("  Scale Down: Wait 5 min, then 10% per minute")
    print()

    print("✅ Demo 3 complete!")


def demo_4_storage():
    """Demo 4: Generate storage configuration."""
    print("=" * 70)
    print("DEMO 4: PERSISTENT STORAGE CONFIGURATION")
    print("=" * 70)
    print()

    generator = ManifestGenerator()

    print("💾 Storage Access Modes:")
    print("-" * 40)
    print("""
  ReadWriteOnce (RWO):  Single node read-write
  ReadOnlyMany (ROX):   Multiple nodes read-only
  ReadWriteMany (RWX):  Multiple nodes read-write
""")

    # Generate PVCs for different use cases
    pvc_configs = [
        PVCConfig(
            name="model-storage",
            namespace="ml-serving",
            size="50Gi",
            access_mode=AccessMode.ROX,  # Shared models
            storage_class="fast-ssd",
        ),
        PVCConfig(
            name="training-data",
            namespace="ml-training",
            size="500Gi",
            access_mode=AccessMode.RWO,
            storage_class="standard",
        ),
        PVCConfig(
            name="checkpoints",
            namespace="ml-training",
            size="100Gi",
            access_mode=AccessMode.RWO,
            storage_class="fast-ssd",
        ),
    ]

    for config in pvc_configs:
        print(f"🔧 Generating: {config.name} PVC")
        print("-" * 40)

        manifest = generator.generate_pvc(config)

        for line in manifest.split('\n'):
            print(f"  {line}")
        print()

        path = generator.save(manifest, f"pvc-{config.name}.yaml")
        print(f"💾 Saved to: {path}")
        print()

    print("✅ Demo 4 complete!")


def demo_5_full_stack():
    """Demo 5: Generate complete ML inference stack."""
    print("=" * 70)
    print("DEMO 5: COMPLETE ML INFERENCE STACK")
    print("=" * 70)
    print()

    project_name = "sentiment-classifier"
    namespace = "ml-production"

    print(f"🚀 Generating complete stack for: {project_name}")
    print("-" * 40)

    generator = ManifestGenerator()

    # Create output directory
    stack_dir = MANIFESTS_DIR / "stacks" / project_name
    stack_dir.mkdir(parents=True, exist_ok=True)

    manifests = []

    # 1. Namespace
    print("\n1️⃣ Generating Namespace...")
    ns_manifest = generator.generate_namespace(namespace)
    manifests.append(("namespace.yaml", ns_manifest))
    print(f"   ✅ {namespace}")

    # 2. ConfigMap
    print("\n2️⃣ Generating ConfigMap...")
    config_data = {
        "MODEL_NAME": "sentiment-classifier",
        "MODEL_VERSION": "v1.0.0",
        "MAX_BATCH_SIZE": "32",
        "LOG_LEVEL": "INFO",
    }
    cm_manifest = generator.generate_config_map("model-config", namespace, config_data)
    manifests.append(("configmap.yaml", cm_manifest))
    print(f"   ✅ model-config")

    # 3. PVC for models
    print("\n3️⃣ Generating PVC...")
    pvc_config = PVCConfig(
        name="model-storage",
        namespace=namespace,
        size="20Gi",
        access_mode=AccessMode.ROX,
        storage_class="fast-ssd",
    )
    pvc_manifest = generator.generate_pvc(pvc_config)
    manifests.append(("pvc.yaml", pvc_manifest))
    print(f"   ✅ model-storage (20Gi)")

    # 4. Deployment
    print("\n4️⃣ Generating Deployment...")
    deploy_config = DeploymentConfig(
        name=project_name,
        image=f"myregistry/{project_name}:v1.0.0",
        replicas=3,
        namespace=namespace,
        port=8000,
        resources=ResourceConfig(
            cpu_request="500m",
            cpu_limit="1000m",
            memory_request="1Gi",
            memory_limit="2Gi",
        ),
        config_map="model-config",
        model_volume="model-storage",
        health_path="/health",
    )
    deploy_manifest = generator.generate_deployment(deploy_config)
    manifests.append(("deployment.yaml", deploy_manifest))
    print(f"   ✅ {project_name} (3 replicas)")

    # 5. Service
    print("\n5️⃣ Generating Service...")
    svc_config = ServiceConfig(
        name=f"{project_name}-svc",
        deployment=project_name,
        port=80,
        target_port=8000,
        service_type=ServiceType.LOAD_BALANCER,
        namespace=namespace,
    )
    svc_manifest = generator.generate_service(svc_config)
    manifests.append(("service.yaml", svc_manifest))
    print(f"   ✅ {project_name}-svc (LoadBalancer)")

    # 6. HPA
    print("\n6️⃣ Generating HPA...")
    hpa_config = HPAConfig(
        name=f"{project_name}-hpa",
        deployment=project_name,
        namespace=namespace,
        min_replicas=2,
        max_replicas=10,
        cpu_target=70,
    )
    hpa_manifest = generator.generate_hpa(hpa_config)
    manifests.append(("hpa.yaml", hpa_manifest))
    print(f"   ✅ {project_name}-hpa (2-10 replicas)")

    # Save all manifests
    print("\n💾 Saving manifests...")
    for filename, content in manifests:
        filepath = stack_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✅ {filepath}")

    # Generate combined manifest
    combined = "---\n".join([m[1] for m in manifests])
    combined_path = stack_dir / "all-in-one.yaml"
    with open(combined_path, 'w') as f:
        f.write(combined)
    print(f"   ✅ {combined_path}")

    # Summary
    print("\n" + "=" * 70)
    print("📁 Generated Stack Structure:")
    print("=" * 70)
    print(f"""
{project_name}/
├── namespace.yaml      # Namespace: {namespace}
├── configmap.yaml      # Model configuration
├── pvc.yaml            # Model storage (20Gi)
├── deployment.yaml     # Inference service (3 replicas)
├── service.yaml        # LoadBalancer service
├── hpa.yaml            # Autoscaling (2-10 replicas)
└── all-in-one.yaml     # Combined manifest
""")

    print("🚀 Deployment Commands:")
    print("-" * 40)
    print(f"  # Deploy all at once")
    print(f"  kubectl apply -f {stack_dir}/all-in-one.yaml")
    print()
    print(f"  # Or deploy individually")
    print(f"  kubectl apply -f {stack_dir}/namespace.yaml")
    print(f"  kubectl apply -f {stack_dir}/configmap.yaml")
    print(f"  kubectl apply -f {stack_dir}/pvc.yaml")
    print(f"  kubectl apply -f {stack_dir}/deployment.yaml")
    print(f"  kubectl apply -f {stack_dir}/service.yaml")
    print(f"  kubectl apply -f {stack_dir}/hpa.yaml")
    print()
    print(f"  # Check status")
    print(f"  kubectl get all -n {namespace}")
    print()

    print("✅ Demo 5 complete!")
    print(f"\n📂 All files saved to: {stack_dir}")


def print_usage():
    """Print usage information."""
    print("""
ML Kubernetes Toolkit - Deploy ML on Kubernetes

Usage: python deliverable_ml_k8s_toolkit.py <command>

Commands:
  demo1    Generate deployment manifests
  demo2    Generate training job manifests
  demo3    Generate autoscaling configuration
  demo4    Generate storage configuration
  demo5    Generate complete ML stack

Examples:
  python deliverable_ml_k8s_toolkit.py demo1
  python deliverable_ml_k8s_toolkit.py demo5
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_deployment_generation()
    elif command == "demo2":
        demo_2_training_jobs()
    elif command == "demo3":
        demo_3_autoscaling()
    elif command == "demo4":
        demo_4_storage()
    elif command == "demo5":
        demo_5_full_stack()
    elif command in ["help", "-h", "--help"]:
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
