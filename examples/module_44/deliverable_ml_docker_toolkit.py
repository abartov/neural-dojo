#!/usr/bin/env python3
"""
Module 44 Deliverable: ML Docker Toolkit

A comprehensive toolkit for containerizing ML applications including:
- Dockerfile generation for various ML scenarios
- Docker Compose stack generation
- Image analysis and optimization recommendations
- Build time estimation
- Security scanning (basic)

Author: Neural Dojo
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

STORAGE_DIR = Path(".ml_docker_toolkit")
DOCKERFILES_DIR = STORAGE_DIR / "dockerfiles"
COMPOSE_DIR = STORAGE_DIR / "compose"


class BaseImage(Enum):
    """Available base images for ML containers."""
    PYTHON_SLIM = "python:3.10-slim"
    PYTHON_ALPINE = "python:3.10-alpine"
    PYTHON_FULL = "python:3.10"
    CUDA_RUNTIME = "nvidia/cuda:11.8-cudnn8-runtime-ubuntu22.04"
    CUDA_DEVEL = "nvidia/cuda:11.8-cudnn8-devel-ubuntu22.04"
    PYTORCH = "pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime"
    TENSORFLOW = "tensorflow/tensorflow:2.13.0-gpu"


class MLScenario(Enum):
    """Common ML deployment scenarios."""
    INFERENCE_API = "inference_api"
    TRAINING = "training"
    BATCH_PROCESSING = "batch_processing"
    JUPYTER_DEV = "jupyter_dev"
    STREAMLIT_APP = "streamlit_app"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DockerfileConfig:
    """Configuration for generating a Dockerfile."""
    scenario: MLScenario
    base_image: BaseImage
    python_version: str = "3.10"
    gpu_enabled: bool = False
    multi_stage: bool = True
    non_root_user: bool = True
    health_check: bool = True
    port: int = 8000
    requirements_file: str = "requirements.txt"
    source_dir: str = "src"
    model_dir: Optional[str] = "models"
    entry_point: str = "src.main:app"
    extra_apt_packages: list = field(default_factory=list)
    extra_pip_packages: list = field(default_factory=list)
    environment_vars: dict = field(default_factory=dict)
    labels: dict = field(default_factory=dict)


@dataclass
class ComposeService:
    """Configuration for a Docker Compose service."""
    name: str
    image: Optional[str] = None
    build_context: Optional[str] = None
    dockerfile: Optional[str] = None
    ports: list = field(default_factory=list)
    volumes: list = field(default_factory=list)
    environment: dict = field(default_factory=dict)
    depends_on: list = field(default_factory=list)
    gpu_enabled: bool = False
    replicas: int = 1
    memory_limit: Optional[str] = None
    healthcheck: Optional[dict] = None


@dataclass
class ComposeConfig:
    """Configuration for generating docker-compose.yml."""
    project_name: str
    services: list = field(default_factory=list)
    volumes: list = field(default_factory=list)
    networks: list = field(default_factory=list)


@dataclass
class ImageAnalysis:
    """Analysis results for a Docker image."""
    base_image: str
    estimated_size_mb: float
    layer_count: int
    has_gpu_support: bool
    security_issues: list = field(default_factory=list)
    optimization_tips: list = field(default_factory=list)
    build_time_estimate_min: float = 0


@dataclass
class DockerfileTemplate:
    """A generated Dockerfile with metadata."""
    name: str
    scenario: str
    content: str
    config: DockerfileConfig
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# DOCKERFILE GENERATOR
# =============================================================================

class DockerfileGenerator:
    """Generates optimized Dockerfiles for ML applications."""

    # Base image sizes (approximate MB)
    IMAGE_SIZES = {
        BaseImage.PYTHON_SLIM: 150,
        BaseImage.PYTHON_ALPINE: 50,
        BaseImage.PYTHON_FULL: 1000,
        BaseImage.CUDA_RUNTIME: 3500,
        BaseImage.CUDA_DEVEL: 5500,
        BaseImage.PYTORCH: 6000,
        BaseImage.TENSORFLOW: 5000,
    }

    # Common ML dependency sizes (MB)
    DEPENDENCY_SIZES = {
        "torch": 2000,
        "tensorflow": 1500,
        "transformers": 500,
        "scikit-learn": 200,
        "pandas": 100,
        "numpy": 50,
        "fastapi": 50,
        "uvicorn": 20,
        "gunicorn": 10,
        "streamlit": 300,
        "jupyter": 500,
    }

    def __init__(self):
        """Initialize the generator."""
        self.templates: list[DockerfileTemplate] = []

    def generate(self, config: DockerfileConfig) -> str:
        """Generate a Dockerfile based on configuration."""
        if config.multi_stage:
            return self._generate_multistage(config)
        else:
            return self._generate_single_stage(config)

    def _generate_multistage(self, config: DockerfileConfig) -> str:
        """Generate a multi-stage Dockerfile."""
        lines = []

        # Header comment
        lines.extend([
            f"# Dockerfile for {config.scenario.value}",
            f"# Generated by ML Docker Toolkit on {datetime.now().strftime('%Y-%m-%d')}",
            f"# Base: {config.base_image.value}",
            "",
        ])

        # Builder stage
        lines.extend([
            "# ============================================",
            "# Stage 1: Builder",
            "# ============================================",
            f"FROM {self._get_builder_base(config)} AS builder",
            "",
            "WORKDIR /app",
            "",
        ])

        # Build dependencies
        if config.extra_apt_packages or self._needs_build_tools(config):
            apt_packages = ["build-essential"] + config.extra_apt_packages
            lines.extend([
                "# Install build dependencies",
                "RUN apt-get update && apt-get install -y --no-install-recommends \\",
                *[f"    {pkg} \\" for pkg in apt_packages[:-1]],
                f"    {apt_packages[-1]} \\",
                "    && rm -rf /var/lib/apt/lists/*",
                "",
            ])

        # Create virtual environment
        lines.extend([
            "# Create virtual environment",
            "RUN python -m venv /opt/venv",
            'ENV PATH="/opt/venv/bin:$PATH"',
            "",
        ])

        # Install Python dependencies
        lines.extend([
            "# Install Python dependencies (cached layer)",
            f"COPY {config.requirements_file} .",
            f"RUN pip install --no-cache-dir -r {config.requirements_file}",
        ])

        if config.extra_pip_packages:
            pip_packages = " ".join(config.extra_pip_packages)
            lines.append(f"RUN pip install --no-cache-dir {pip_packages}")

        lines.append("")

        # Production stage
        lines.extend([
            "# ============================================",
            "# Stage 2: Production",
            "# ============================================",
            f"FROM {config.base_image.value} AS production",
            "",
            "WORKDIR /app",
            "",
        ])

        # Runtime dependencies
        runtime_apt = self._get_runtime_apt_packages(config)
        if runtime_apt:
            lines.extend([
                "# Install runtime dependencies",
                "RUN apt-get update && apt-get install -y --no-install-recommends \\",
                *[f"    {pkg} \\" for pkg in runtime_apt[:-1]],
                f"    {runtime_apt[-1]} \\",
                "    && rm -rf /var/lib/apt/lists/*",
                "",
            ])

        # Copy virtual environment
        lines.extend([
            "# Copy virtual environment from builder",
            "COPY --from=builder /opt/venv /opt/venv",
            'ENV PATH="/opt/venv/bin:$PATH"',
            "",
        ])

        # Non-root user
        if config.non_root_user:
            lines.extend([
                "# Create non-root user",
                "RUN groupadd -r appgroup && useradd -r -g appgroup appuser",
                "",
            ])

        # Copy application code
        lines.extend([
            "# Copy application code",
        ])

        owner = "--chown=appuser:appgroup " if config.non_root_user else ""
        lines.append(f"COPY {owner}{config.source_dir}/ ./{config.source_dir}/")

        if config.model_dir:
            lines.append(f"COPY {owner}{config.model_dir}/ ./{config.model_dir}/")

        lines.append("")

        # Environment variables
        lines.extend([
            "# Environment variables",
            "ENV PYTHONUNBUFFERED=1",
            "ENV PYTHONDONTWRITEBYTECODE=1",
        ])

        if config.gpu_enabled:
            lines.extend([
                "ENV NVIDIA_VISIBLE_DEVICES=all",
                "ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility",
            ])

        for key, value in config.environment_vars.items():
            lines.append(f"ENV {key}={value}")

        lines.append("")

        # Labels
        if config.labels:
            lines.append("# Labels")
            for key, value in config.labels.items():
                lines.append(f'LABEL {key}="{value}"')
            lines.append("")

        # Switch to non-root user
        if config.non_root_user:
            lines.extend([
                "# Switch to non-root user",
                "USER appuser",
                "",
            ])

        # Expose port
        if config.port:
            lines.extend([
                "# Expose port",
                f"EXPOSE {config.port}",
                "",
            ])

        # Health check
        if config.health_check and config.scenario in [MLScenario.INFERENCE_API, MLScenario.STREAMLIT_APP]:
            lines.extend([
                "# Health check",
                f'HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\',
                f'    CMD curl -f http://localhost:{config.port}/health || exit 1',
                "",
            ])

        # Entry point based on scenario
        lines.extend(self._get_entrypoint(config))

        return "\n".join(lines)

    def _generate_single_stage(self, config: DockerfileConfig) -> str:
        """Generate a single-stage Dockerfile (simpler, larger)."""
        lines = [
            f"# Dockerfile for {config.scenario.value} (single-stage)",
            f"# Generated by ML Docker Toolkit",
            "",
            f"FROM {config.base_image.value}",
            "",
            "WORKDIR /app",
            "",
            f"COPY {config.requirements_file} .",
            f"RUN pip install --no-cache-dir -r {config.requirements_file}",
            "",
            f"COPY {config.source_dir}/ ./{config.source_dir}/",
        ]

        if config.model_dir:
            lines.append(f"COPY {config.model_dir}/ ./{config.model_dir}/")

        lines.extend([
            "",
            "ENV PYTHONUNBUFFERED=1",
        ])

        if config.port:
            lines.append(f"EXPOSE {config.port}")

        lines.extend([""] + self._get_entrypoint(config))

        return "\n".join(lines)

    def _get_builder_base(self, config: DockerfileConfig) -> str:
        """Get the appropriate builder base image."""
        if config.gpu_enabled:
            return BaseImage.CUDA_DEVEL.value
        return f"python:{config.python_version}-slim"

    def _needs_build_tools(self, config: DockerfileConfig) -> bool:
        """Check if build tools are needed."""
        return config.gpu_enabled or config.scenario == MLScenario.TRAINING

    def _get_runtime_apt_packages(self, config: DockerfileConfig) -> list:
        """Get runtime APT packages needed."""
        packages = []
        if config.health_check:
            packages.append("curl")
        return packages

    def _get_entrypoint(self, config: DockerfileConfig) -> list:
        """Get the entry point command based on scenario."""
        lines = ["# Run application"]

        if config.scenario == MLScenario.INFERENCE_API:
            lines.append(
                f'CMD ["gunicorn", "{config.entry_point}", '
                f'"--workers", "4", '
                f'"--worker-class", "uvicorn.workers.UvicornWorker", '
                f'"--bind", "0.0.0.0:{config.port}", '
                f'"--timeout", "120"]'
            )
        elif config.scenario == MLScenario.TRAINING:
            lines.append('ENTRYPOINT ["python", "-m", "src.train"]')
            lines.append("# Pass arguments: docker run myapp --epochs 100")
        elif config.scenario == MLScenario.BATCH_PROCESSING:
            lines.append('ENTRYPOINT ["python", "-m", "src.batch"]')
        elif config.scenario == MLScenario.JUPYTER_DEV:
            lines.append(
                'CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", '
                '"--no-browser", "--allow-root"]'
            )
        elif config.scenario == MLScenario.STREAMLIT_APP:
            lines.append(
                f'CMD ["streamlit", "run", "src/app.py", '
                f'"--server.port={config.port}", "--server.address=0.0.0.0"]'
            )

        return lines

    def analyze(self, config: DockerfileConfig, requirements: list[str] = None) -> ImageAnalysis:
        """Analyze the expected image characteristics."""
        base_size = self.IMAGE_SIZES.get(config.base_image, 500)

        # Estimate dependency sizes
        dep_size = 0
        if requirements:
            for req in requirements:
                # Extract package name from requirement
                pkg_name = re.split(r'[<>=!~\[]', req)[0].lower().strip()
                dep_size += self.DEPENDENCY_SIZES.get(pkg_name, 20)

        # Multi-stage reduces size by ~20%
        if config.multi_stage:
            total_size = base_size * 0.3 + dep_size  # Only runtime base + deps
        else:
            total_size = base_size + dep_size

        # Layer count estimate
        layer_count = 8 if config.multi_stage else 5
        if config.extra_apt_packages:
            layer_count += 1
        if config.non_root_user:
            layer_count += 1

        # Security analysis
        security_issues = []
        if not config.non_root_user:
            security_issues.append("Running as root user (security risk)")
        if not config.multi_stage:
            security_issues.append("Single-stage build may include build tools")
        if config.base_image == BaseImage.PYTHON_FULL:
            security_issues.append("Full Python image has larger attack surface")

        # Optimization tips
        tips = []
        if not config.multi_stage:
            tips.append("Use multi-stage build to reduce image size by ~20-50%")
        if config.base_image == BaseImage.PYTHON_FULL:
            tips.append("Use python:3.10-slim instead of full image")
        if not config.health_check and config.scenario == MLScenario.INFERENCE_API:
            tips.append("Add health check for production reliability")
        if config.gpu_enabled and config.base_image not in [BaseImage.CUDA_RUNTIME, BaseImage.CUDA_DEVEL]:
            tips.append("Use nvidia/cuda base image for GPU support")

        # Build time estimate (very rough)
        build_time = 2  # Base time in minutes
        build_time += dep_size / 500  # ~2 min per 500MB of deps
        if config.gpu_enabled:
            build_time += 3  # CUDA setup takes longer

        return ImageAnalysis(
            base_image=config.base_image.value,
            estimated_size_mb=total_size,
            layer_count=layer_count,
            has_gpu_support=config.gpu_enabled,
            security_issues=security_issues,
            optimization_tips=tips,
            build_time_estimate_min=round(build_time, 1)
        )

    def save_template(self, name: str, config: DockerfileConfig) -> Path:
        """Save a generated Dockerfile template."""
        DOCKERFILES_DIR.mkdir(parents=True, exist_ok=True)

        content = self.generate(config)
        template = DockerfileTemplate(
            name=name,
            scenario=config.scenario.value,
            content=content,
            config=config
        )

        self.templates.append(template)

        # Save Dockerfile
        dockerfile_path = DOCKERFILES_DIR / f"Dockerfile.{name}"
        with open(dockerfile_path, 'w') as f:
            f.write(content)

        return dockerfile_path


# =============================================================================
# DOCKER COMPOSE GENERATOR
# =============================================================================

class ComposeGenerator:
    """Generates Docker Compose configurations for ML stacks."""

    # Pre-defined service templates
    SERVICE_TEMPLATES = {
        "qdrant": ComposeService(
            name="qdrant",
            image="qdrant/qdrant:latest",
            ports=["6333:6333"],
            volumes=["qdrant-data:/qdrant/storage"],
        ),
        "redis": ComposeService(
            name="redis",
            image="redis:7-alpine",
            ports=["6379:6379"],
            volumes=["redis-data:/data"],
        ),
        "postgres": ComposeService(
            name="postgres",
            image="postgres:15-alpine",
            ports=["5432:5432"],
            volumes=["postgres-data:/var/lib/postgresql/data"],
            environment={
                "POSTGRES_USER": "mluser",
                "POSTGRES_PASSWORD": "mlpassword",
                "POSTGRES_DB": "mldb",
            },
        ),
        "mlflow": ComposeService(
            name="mlflow",
            image="ghcr.io/mlflow/mlflow:v2.8.0",
            ports=["5000:5000"],
            volumes=["mlflow-data:/mlflow"],
            environment={
                "MLFLOW_BACKEND_STORE_URI": "sqlite:///mlflow/mlflow.db",
            },
        ),
        "minio": ComposeService(
            name="minio",
            image="minio/minio:latest",
            ports=["9000:9000", "9001:9001"],
            volumes=["minio-data:/data"],
            environment={
                "MINIO_ROOT_USER": "minioadmin",
                "MINIO_ROOT_PASSWORD": "minioadmin",
            },
        ),
    }

    def __init__(self):
        """Initialize the generator."""
        pass

    def generate(self, config: ComposeConfig) -> str:
        """Generate docker-compose.yml content."""
        lines = [
            f"# Docker Compose for {config.project_name}",
            f"# Generated by ML Docker Toolkit on {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "version: '3.8'",
            "",
            "services:",
        ]

        for service in config.services:
            lines.extend(self._generate_service(service))

        # Volumes
        if config.volumes:
            lines.extend(["", "volumes:"])
            for vol in config.volumes:
                lines.append(f"  {vol}:")

        # Networks
        if config.networks:
            lines.extend(["", "networks:"])
            for net in config.networks:
                lines.append(f"  {net}:")
                lines.append("    driver: bridge")

        return "\n".join(lines)

    def _generate_service(self, service: ComposeService) -> list:
        """Generate YAML for a single service."""
        lines = [f"  {service.name}:"]

        if service.image:
            lines.append(f"    image: {service.image}")

        if service.build_context:
            lines.append("    build:")
            lines.append(f"      context: {service.build_context}")
            if service.dockerfile:
                lines.append(f"      dockerfile: {service.dockerfile}")

        if service.ports:
            lines.append("    ports:")
            for port in service.ports:
                lines.append(f'      - "{port}"')

        if service.volumes:
            lines.append("    volumes:")
            for vol in service.volumes:
                lines.append(f"      - {vol}")

        if service.environment:
            lines.append("    environment:")
            for key, value in service.environment.items():
                lines.append(f"      - {key}={value}")

        if service.depends_on:
            lines.append("    depends_on:")
            for dep in service.depends_on:
                lines.append(f"      - {dep}")

        if service.gpu_enabled:
            lines.extend([
                "    deploy:",
                "      resources:",
                "        reservations:",
                "          devices:",
                "            - driver: nvidia",
                "              count: 1",
                "              capabilities: [gpu]",
            ])
        elif service.memory_limit:
            lines.extend([
                "    deploy:",
                "      resources:",
                "        limits:",
                f"          memory: {service.memory_limit}",
            ])

        if service.healthcheck:
            lines.append("    healthcheck:")
            for key, value in service.healthcheck.items():
                lines.append(f"      {key}: {value}")

        lines.append("")
        return lines

    def create_ml_stack(
        self,
        project_name: str,
        include_api: bool = True,
        include_qdrant: bool = False,
        include_redis: bool = False,
        include_mlflow: bool = False,
        include_postgres: bool = False,
        gpu_enabled: bool = False,
    ) -> ComposeConfig:
        """Create a pre-configured ML stack."""
        services = []
        volumes = []

        # API service
        if include_api:
            api_service = ComposeService(
                name="api",
                build_context=".",
                dockerfile="Dockerfile",
                ports=["8000:8000"],
                volumes=["./src:/app/src", "model-cache:/app/models"],
                environment={
                    "MODEL_PATH": "/app/models",
                    "LOG_LEVEL": "INFO",
                },
                gpu_enabled=gpu_enabled,
                healthcheck={
                    "test": '["CMD", "curl", "-f", "http://localhost:8000/health"]',
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": "3",
                },
            )

            depends = []
            if include_qdrant:
                depends.append("qdrant")
            if include_redis:
                depends.append("redis")
            if include_postgres:
                depends.append("postgres")
            api_service.depends_on = depends

            services.append(api_service)
            volumes.append("model-cache")

        # Add infrastructure services
        if include_qdrant:
            services.append(self.SERVICE_TEMPLATES["qdrant"])
            volumes.append("qdrant-data")

        if include_redis:
            services.append(self.SERVICE_TEMPLATES["redis"])
            volumes.append("redis-data")

        if include_mlflow:
            services.append(self.SERVICE_TEMPLATES["mlflow"])
            volumes.append("mlflow-data")

        if include_postgres:
            services.append(self.SERVICE_TEMPLATES["postgres"])
            volumes.append("postgres-data")

        return ComposeConfig(
            project_name=project_name,
            services=services,
            volumes=volumes,
        )

    def save(self, config: ComposeConfig, filename: str = "docker-compose.yml") -> Path:
        """Save the Docker Compose configuration."""
        COMPOSE_DIR.mkdir(parents=True, exist_ok=True)

        content = self.generate(config)
        filepath = COMPOSE_DIR / filename

        with open(filepath, 'w') as f:
            f.write(content)

        return filepath


# =============================================================================
# DOCKERIGNORE GENERATOR
# =============================================================================

class DockerignoreGenerator:
    """Generates .dockerignore files for ML projects."""

    DEFAULT_PATTERNS = [
        "# Git",
        ".git",
        ".gitignore",
        ".gitattributes",
        "",
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "*.egg-info/",
        ".eggs/",
        "*.egg",
        ".venv/",
        "venv/",
        "ENV/",
        "",
        "# IDE",
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "",
        "# Testing",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".tox/",
        "",
        "# Documentation",
        "docs/",
        "*.md",
        "!README.md",
        "",
        "# Notebooks (optional)",
        "notebooks/",
        "*.ipynb",
        "",
        "# Data (should be mounted, not copied)",
        "data/raw/",
        "data/interim/",
        "data/external/",
        "",
        "# Large model files (should be mounted)",
        "*.h5",
        "*.pkl",
        "*.joblib",
        "*.pt",
        "*.pth",
        "*.onnx",
        "*.bin",
        "",
        "# ML experiment tracking",
        "wandb/",
        "mlruns/",
        "runs/",
        "logs/",
        "",
        "# Docker",
        "Dockerfile*",
        "docker-compose*",
        ".docker/",
        "",
        "# Environment",
        ".env",
        ".env.*",
        "*.local",
        "",
        "# Misc",
        ".DS_Store",
        "Thumbs.db",
        "Makefile",
        "",
    ]

    def generate(self, extra_patterns: list = None) -> str:
        """Generate .dockerignore content."""
        patterns = self.DEFAULT_PATTERNS.copy()

        if extra_patterns:
            patterns.extend(["# Custom patterns"] + extra_patterns + [""])

        return "\n".join(patterns)

    def save(self, filepath: Path = None, extra_patterns: list = None) -> Path:
        """Save the .dockerignore file."""
        if filepath is None:
            filepath = STORAGE_DIR / ".dockerignore.template"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(self.generate(extra_patterns))

        return filepath


# =============================================================================
# PRESETS
# =============================================================================

DOCKERFILE_PRESETS = {
    "fastapi-inference": DockerfileConfig(
        scenario=MLScenario.INFERENCE_API,
        base_image=BaseImage.PYTHON_SLIM,
        multi_stage=True,
        non_root_user=True,
        health_check=True,
        port=8000,
        entry_point="src.main:app",
        labels={
            "maintainer": "ml-team",
            "version": "1.0.0",
        },
    ),
    "fastapi-inference-gpu": DockerfileConfig(
        scenario=MLScenario.INFERENCE_API,
        base_image=BaseImage.CUDA_RUNTIME,
        gpu_enabled=True,
        multi_stage=True,
        non_root_user=True,
        health_check=True,
        port=8000,
        entry_point="src.main:app",
    ),
    "training-gpu": DockerfileConfig(
        scenario=MLScenario.TRAINING,
        base_image=BaseImage.PYTORCH,
        gpu_enabled=True,
        multi_stage=False,  # Need build tools for some packages
        non_root_user=False,  # Training often needs root for data access
        health_check=False,
        port=None,
    ),
    "batch-processing": DockerfileConfig(
        scenario=MLScenario.BATCH_PROCESSING,
        base_image=BaseImage.PYTHON_SLIM,
        multi_stage=True,
        non_root_user=True,
        health_check=False,
        port=None,
    ),
    "jupyter-dev": DockerfileConfig(
        scenario=MLScenario.JUPYTER_DEV,
        base_image=BaseImage.PYTORCH,
        gpu_enabled=True,
        multi_stage=False,
        non_root_user=False,
        health_check=False,
        port=8888,
    ),
    "streamlit-app": DockerfileConfig(
        scenario=MLScenario.STREAMLIT_APP,
        base_image=BaseImage.PYTHON_SLIM,
        multi_stage=True,
        non_root_user=True,
        health_check=True,
        port=8501,
        entry_point="src.app:main",
    ),
}


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_dockerfile_generation():
    """Demo 1: Generate Dockerfiles for different ML scenarios."""
    print("=" * 70)
    print("DEMO 1: DOCKERFILE GENERATION")
    print("=" * 70)
    print()

    generator = DockerfileGenerator()

    # Show available presets
    print("📋 Available Dockerfile Presets:")
    print("-" * 40)
    for name, config in DOCKERFILE_PRESETS.items():
        gpu = "🎮 GPU" if config.gpu_enabled else "💻 CPU"
        stage = "Multi-stage" if config.multi_stage else "Single-stage"
        print(f"  • {name}")
        print(f"    {gpu} | {stage} | {config.scenario.value}")
    print()

    # Generate FastAPI inference Dockerfile
    print("🔧 Generating: FastAPI Inference (CPU)")
    print("-" * 40)
    config = DOCKERFILE_PRESETS["fastapi-inference"]
    dockerfile = generator.generate(config)

    # Show first 30 lines
    lines = dockerfile.split('\n')
    for line in lines[:30]:
        print(f"  {line}")
    print(f"  ... ({len(lines) - 30} more lines)")
    print()

    # Save the Dockerfile
    path = generator.save_template("fastapi-inference", config)
    print(f"💾 Saved to: {path}")
    print()

    # Generate GPU training Dockerfile
    print("🔧 Generating: GPU Training Container")
    print("-" * 40)
    config = DOCKERFILE_PRESETS["training-gpu"]
    dockerfile = generator.generate(config)

    lines = dockerfile.split('\n')
    for line in lines[:25]:
        print(f"  {line}")
    print(f"  ... ({len(lines) - 25} more lines)")
    print()

    path = generator.save_template("training-gpu", config)
    print(f"💾 Saved to: {path}")
    print()

    print("✅ Demo 1 complete!")


def demo_2_image_analysis():
    """Demo 2: Analyze Docker image characteristics."""
    print("=" * 70)
    print("DEMO 2: IMAGE ANALYSIS & OPTIMIZATION")
    print("=" * 70)
    print()

    generator = DockerfileGenerator()

    # Sample requirements
    requirements = [
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "gunicorn>=21.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ]

    print("📦 Sample requirements.txt:")
    for req in requirements:
        print(f"  {req}")
    print()

    # Analyze different configurations
    configs_to_analyze = [
        ("Single-stage, Full Python", DockerfileConfig(
            scenario=MLScenario.INFERENCE_API,
            base_image=BaseImage.PYTHON_FULL,
            multi_stage=False,
            non_root_user=False,
            health_check=False,
        )),
        ("Multi-stage, Slim Python", DockerfileConfig(
            scenario=MLScenario.INFERENCE_API,
            base_image=BaseImage.PYTHON_SLIM,
            multi_stage=True,
            non_root_user=True,
            health_check=True,
        )),
        ("GPU Runtime", DockerfileConfig(
            scenario=MLScenario.INFERENCE_API,
            base_image=BaseImage.CUDA_RUNTIME,
            gpu_enabled=True,
            multi_stage=True,
            non_root_user=True,
            health_check=True,
        )),
    ]

    print("📊 Image Analysis Comparison:")
    print("-" * 70)
    print(f"{'Configuration':<30} {'Size (MB)':<12} {'Layers':<8} {'Issues':<8}")
    print("-" * 70)

    for name, config in configs_to_analyze:
        analysis = generator.analyze(config, requirements)
        issues = len(analysis.security_issues)
        print(f"{name:<30} {analysis.estimated_size_mb:<12.0f} {analysis.layer_count:<8} {issues:<8}")

    print()

    # Detailed analysis of optimized config
    print("🔍 Detailed Analysis: Multi-stage, Slim Python")
    print("-" * 40)
    _, config = configs_to_analyze[1]
    analysis = generator.analyze(config, requirements)

    print(f"  Base Image: {analysis.base_image}")
    print(f"  Estimated Size: {analysis.estimated_size_mb:.0f} MB")
    print(f"  Layer Count: {analysis.layer_count}")
    print(f"  GPU Support: {'Yes' if analysis.has_gpu_support else 'No'}")
    print(f"  Build Time: ~{analysis.build_time_estimate_min:.1f} minutes")
    print()

    if analysis.security_issues:
        print("  ⚠️ Security Issues:")
        for issue in analysis.security_issues:
            print(f"    • {issue}")
    else:
        print("  ✅ No security issues detected")
    print()

    if analysis.optimization_tips:
        print("  💡 Optimization Tips:")
        for tip in analysis.optimization_tips:
            print(f"    • {tip}")
    else:
        print("  ✅ Already optimized!")
    print()

    print("✅ Demo 2 complete!")


def demo_3_compose_generation():
    """Demo 3: Generate Docker Compose stacks."""
    print("=" * 70)
    print("DEMO 3: DOCKER COMPOSE GENERATION")
    print("=" * 70)
    print()

    generator = ComposeGenerator()

    # Show available service templates
    print("📋 Available Service Templates:")
    print("-" * 40)
    for name, service in generator.SERVICE_TEMPLATES.items():
        ports = ", ".join(service.ports) if service.ports else "none"
        print(f"  • {name}: {service.image} (ports: {ports})")
    print()

    # Generate a basic RAG stack
    print("🔧 Generating: RAG Application Stack")
    print("-" * 40)

    config = generator.create_ml_stack(
        project_name="rag-app",
        include_api=True,
        include_qdrant=True,
        include_redis=True,
        gpu_enabled=True,
    )

    compose_yaml = generator.generate(config)
    print(compose_yaml)
    print()

    path = generator.save(config, "docker-compose.rag.yml")
    print(f"💾 Saved to: {path}")
    print()

    # Generate an MLOps stack
    print("🔧 Generating: MLOps Development Stack")
    print("-" * 40)

    config = generator.create_ml_stack(
        project_name="mlops-dev",
        include_api=True,
        include_mlflow=True,
        include_postgres=True,
        gpu_enabled=False,
    )

    compose_yaml = generator.generate(config)
    print(compose_yaml)
    print()

    path = generator.save(config, "docker-compose.mlops.yml")
    print(f"💾 Saved to: {path}")
    print()

    print("✅ Demo 3 complete!")


def demo_4_dockerignore():
    """Demo 4: Generate optimized .dockerignore files."""
    print("=" * 70)
    print("DEMO 4: DOCKERIGNORE GENERATION")
    print("=" * 70)
    print()

    generator = DockerignoreGenerator()

    print("📋 Default .dockerignore for ML projects:")
    print("-" * 40)

    content = generator.generate()
    lines = content.split('\n')

    # Show with line numbers
    for i, line in enumerate(lines[:40], 1):
        print(f"  {i:2}: {line}")
    print(f"  ... ({len(lines) - 40} more lines)")
    print()

    # Generate with custom patterns
    print("🔧 Adding custom patterns:")
    print("-" * 40)
    custom_patterns = [
        "*.safetensors",
        "checkpoints/",
        "outputs/",
    ]

    for pattern in custom_patterns:
        print(f"  + {pattern}")
    print()

    content = generator.generate(custom_patterns)
    path = generator.save(extra_patterns=custom_patterns)
    print(f"💾 Saved to: {path}")
    print()

    # Show size impact
    print("📊 .dockerignore Impact:")
    print("-" * 40)
    print("  Without .dockerignore:")
    print("    • Build context includes ALL files")
    print("    • .git/ alone can be 100+ MB")
    print("    • __pycache__/ adds unnecessary files")
    print("    • Model files bloat context transfer")
    print()
    print("  With proper .dockerignore:")
    print("    • Build context is minimal")
    print("    • Faster docker build command")
    print("    • No secrets accidentally included")
    print("    • Smaller attack surface")
    print()

    print("✅ Demo 4 complete!")


def demo_5_full_project():
    """Demo 5: Generate a complete Docker setup for an ML project."""
    print("=" * 70)
    print("DEMO 5: FULL PROJECT DOCKER SETUP")
    print("=" * 70)
    print()

    project_name = "sentiment-classifier"

    print(f"🚀 Setting up Docker for: {project_name}")
    print("-" * 40)

    # Initialize generators
    dockerfile_gen = DockerfileGenerator()
    compose_gen = ComposeGenerator()
    dockerignore_gen = DockerignoreGenerator()

    # Create project directory structure
    project_dir = STORAGE_DIR / "projects" / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate production Dockerfile
    print("\n1️⃣ Generating production Dockerfile...")
    prod_config = DockerfileConfig(
        scenario=MLScenario.INFERENCE_API,
        base_image=BaseImage.PYTHON_SLIM,
        multi_stage=True,
        non_root_user=True,
        health_check=True,
        port=8000,
        entry_point="src.main:app",
        environment_vars={
            "MODEL_NAME": "distilbert-sentiment",
            "MAX_BATCH_SIZE": "32",
        },
        labels={
            "app": project_name,
            "maintainer": "ml-team",
        },
    )

    dockerfile = dockerfile_gen.generate(prod_config)
    dockerfile_path = project_dir / "Dockerfile"
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile)
    print(f"   ✅ {dockerfile_path}")

    # 2. Generate development Dockerfile
    print("\n2️⃣ Generating development Dockerfile...")
    dev_config = DockerfileConfig(
        scenario=MLScenario.JUPYTER_DEV,
        base_image=BaseImage.PYTORCH,
        gpu_enabled=True,
        multi_stage=False,
        non_root_user=False,
        health_check=False,
        port=8888,
    )

    dev_dockerfile = dockerfile_gen.generate(dev_config)
    dev_path = project_dir / "Dockerfile.dev"
    with open(dev_path, 'w') as f:
        f.write(dev_dockerfile)
    print(f"   ✅ {dev_path}")

    # 3. Generate docker-compose.yml
    print("\n3️⃣ Generating docker-compose.yml...")
    compose_config = compose_gen.create_ml_stack(
        project_name=project_name,
        include_api=True,
        include_redis=True,
        include_mlflow=True,
        gpu_enabled=False,
    )

    compose_yaml = compose_gen.generate(compose_config)
    compose_path = project_dir / "docker-compose.yml"
    with open(compose_path, 'w') as f:
        f.write(compose_yaml)
    print(f"   ✅ {compose_path}")

    # 4. Generate .dockerignore
    print("\n4️⃣ Generating .dockerignore...")
    dockerignore = dockerignore_gen.generate([
        "*.safetensors",
        "checkpoints/",
    ])
    ignore_path = project_dir / ".dockerignore"
    with open(ignore_path, 'w') as f:
        f.write(dockerignore)
    print(f"   ✅ {ignore_path}")

    # 5. Generate Makefile for convenience
    print("\n5️⃣ Generating Makefile...")
    makefile_content = f"""# Makefile for {project_name}
# Generated by ML Docker Toolkit

.PHONY: build run dev test clean

# Build production image
build:
\tdocker build -t {project_name}:latest .

# Run production container
run:
\tdocker run -p 8000:8000 {project_name}:latest

# Start development environment
dev:
\tdocker-compose up -d
\t@echo "Services started:"
\t@echo "  API: http://localhost:8000"
\t@echo "  MLflow: http://localhost:5000"

# Run tests in container
test:
\tdocker run --rm {project_name}:latest pytest

# Stop all services
stop:
\tdocker-compose down

# Clean up
clean:
\tdocker-compose down -v
\tdocker rmi {project_name}:latest || true

# View logs
logs:
\tdocker-compose logs -f api

# Shell into API container
shell:
\tdocker-compose exec api bash
"""

    makefile_path = project_dir / "Makefile"
    with open(makefile_path, 'w') as f:
        f.write(makefile_content)
    print(f"   ✅ {makefile_path}")

    # Summary
    print("\n" + "=" * 70)
    print("📁 Generated Project Structure:")
    print("=" * 70)
    print(f"""
{project_name}/
├── Dockerfile           # Production multi-stage build
├── Dockerfile.dev       # Development with Jupyter
├── docker-compose.yml   # Full stack (API + Redis + MLflow)
├── .dockerignore        # Optimized for ML projects
└── Makefile            # Convenient commands
""")

    print("🚀 Quick Start Commands:")
    print("-" * 40)
    print(f"  cd {project_dir}")
    print("  make build     # Build production image")
    print("  make dev       # Start development stack")
    print("  make logs      # View logs")
    print("  make clean     # Clean up")
    print()

    # Analyze the production image
    analysis = dockerfile_gen.analyze(prod_config, [
        "torch", "transformers", "fastapi", "uvicorn"
    ])

    print("📊 Production Image Analysis:")
    print("-" * 40)
    print(f"  Estimated Size: {analysis.estimated_size_mb:.0f} MB")
    print(f"  Build Time: ~{analysis.build_time_estimate_min:.1f} minutes")
    print(f"  Security Issues: {len(analysis.security_issues)}")
    print()

    print("✅ Demo 5 complete!")
    print(f"\n📂 All files saved to: {project_dir}")


def print_usage():
    """Print usage information."""
    print("""
ML Docker Toolkit - Containerize ML Applications

Usage: python deliverable_ml_docker_toolkit.py <command>

Commands:
  demo1    Generate Dockerfiles for different ML scenarios
  demo2    Analyze Docker image characteristics
  demo3    Generate Docker Compose stacks
  demo4    Generate optimized .dockerignore files
  demo5    Generate complete Docker setup for ML project

Examples:
  python deliverable_ml_docker_toolkit.py demo1
  python deliverable_ml_docker_toolkit.py demo5
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    # Ensure storage directory exists
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_dockerfile_generation()
    elif command == "demo2":
        demo_2_image_analysis()
    elif command == "demo3":
        demo_3_compose_generation()
    elif command == "demo4":
        demo_4_dockerignore()
    elif command == "demo5":
        demo_5_full_project()
    elif command in ["help", "-h", "--help"]:
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
