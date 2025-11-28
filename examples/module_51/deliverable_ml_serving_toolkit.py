#!/usr/bin/env python3
"""
ML Model Serving Toolkit

A comprehensive toolkit demonstrating model deployment and serving patterns
including REST APIs, deployment strategies (canary, blue-green, A/B testing),
model versioning, and performance optimization.

Features:
- Model server simulation (FastAPI-style)
- Deployment patterns (canary, blue-green, A/B)
- Model registry with versioning
- Traffic routing and load balancing
- Performance benchmarking
- Health checks and graceful shutdown

Author: Neural Dojo
Module: 51 - Model Deployment & Serving Patterns
"""

import json
import time
import random
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import sys
import math

# Storage directory
SERVING_DIR = Path(".ml_serving_toolkit")
SERVING_DIR.mkdir(exist_ok=True)
(SERVING_DIR / "models").mkdir(exist_ok=True)
(SERVING_DIR / "logs").mkdir(exist_ok=True)
(SERVING_DIR / "metrics").mkdir(exist_ok=True)


class ModelStage(Enum):
    """Model lifecycle stages."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class DeploymentStrategy(Enum):
    """Deployment strategies."""
    RECREATE = "recreate"          # Stop old, start new
    BLUE_GREEN = "blue_green"      # Instant switch
    CANARY = "canary"              # Progressive rollout
    AB_TEST = "ab_test"            # Statistical comparison


@dataclass
class ModelVersion:
    """A specific version of a model."""
    name: str
    version: str
    accuracy: float
    latency_ms: float
    stage: ModelStage = ModelStage.DEVELOPMENT
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def predict(self, features: List[float]) -> Tuple[float, float]:
        """Simulate model prediction with realistic latency."""
        # Simulate processing time
        time.sleep(self.latency_ms / 1000)

        # Simulate prediction based on features
        prediction = sum(f * (i + 1) for i, f in enumerate(features)) % 1.0

        # Confidence based on model accuracy
        confidence = self.accuracy * (0.9 + random.random() * 0.1)

        return prediction, confidence

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "accuracy": self.accuracy,
            "latency_ms": self.latency_ms,
            "stage": self.stage.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class PredictionRequest:
    """Request for model prediction."""
    request_id: str
    features: List[float]
    model_version: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PredictionResponse:
    """Response from model prediction."""
    request_id: str
    prediction: float
    confidence: float
    model_version: str
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat()
        }


class ModelRegistry:
    """
    Model registry for version management.

    Simulates MLflow/Weights & Biases model registry.
    """

    def __init__(self):
        self.models: Dict[str, Dict[str, ModelVersion]] = {}
        self.production: Dict[str, str] = {}  # model_name -> version

    def register(self, model: ModelVersion) -> str:
        """Register a new model version."""
        if model.name not in self.models:
            self.models[model.name] = {}

        self.models[model.name][model.version] = model
        return f"Registered {model.name}:{model.version}"

    def get_model(self, name: str, version: Optional[str] = None) -> Optional[ModelVersion]:
        """Get a model by name and optional version."""
        if name not in self.models:
            return None

        if version:
            return self.models[name].get(version)

        # Return production version if no version specified
        if name in self.production:
            return self.models[name].get(self.production[name])

        # Return latest version
        versions = list(self.models[name].keys())
        return self.models[name].get(versions[-1]) if versions else None

    def promote(self, name: str, version: str, stage: ModelStage) -> str:
        """Promote model to a new stage."""
        if name not in self.models or version not in self.models[name]:
            return f"Model {name}:{version} not found"

        model = self.models[name][version]
        old_stage = model.stage
        model.stage = stage

        if stage == ModelStage.PRODUCTION:
            # Archive current production
            if name in self.production:
                old_prod = self.models[name].get(self.production[name])
                if old_prod:
                    old_prod.stage = ModelStage.ARCHIVED

            self.production[name] = version

        return f"Promoted {name}:{version} from {old_stage.value} to {stage.value}"

    def list_models(self) -> List[Dict]:
        """List all registered models."""
        result = []
        for name, versions in self.models.items():
            for version, model in versions.items():
                result.append(model.to_dict())
        return result


class TrafficRouter:
    """
    Route traffic between model versions.

    Supports canary, blue-green, and A/B testing patterns.
    """

    def __init__(self):
        self.routes: Dict[str, Dict] = {}
        self.metrics: Dict[str, List[Dict]] = {}

    def configure_canary(
        self,
        model_name: str,
        stable_version: str,
        canary_version: str,
        canary_percent: float
    ):
        """Configure canary deployment."""
        self.routes[model_name] = {
            "strategy": DeploymentStrategy.CANARY,
            "stable": stable_version,
            "canary": canary_version,
            "canary_percent": canary_percent
        }
        self.metrics[model_name] = []

    def configure_blue_green(
        self,
        model_name: str,
        blue_version: str,
        green_version: str,
        active: str = "blue"
    ):
        """Configure blue-green deployment."""
        self.routes[model_name] = {
            "strategy": DeploymentStrategy.BLUE_GREEN,
            "blue": blue_version,
            "green": green_version,
            "active": active
        }

    def configure_ab_test(
        self,
        model_name: str,
        control_version: str,
        treatment_version: str,
        treatment_percent: float = 50.0
    ):
        """Configure A/B test."""
        self.routes[model_name] = {
            "strategy": DeploymentStrategy.AB_TEST,
            "control": control_version,
            "treatment": treatment_version,
            "treatment_percent": treatment_percent
        }
        self.metrics[f"{model_name}_control"] = []
        self.metrics[f"{model_name}_treatment"] = []

    def route(self, model_name: str, user_id: Optional[str] = None) -> str:
        """Route request to appropriate model version."""
        if model_name not in self.routes:
            return "latest"

        route = self.routes[model_name]
        strategy = route["strategy"]

        if strategy == DeploymentStrategy.CANARY:
            # Random routing based on canary percentage
            if random.random() * 100 < route["canary_percent"]:
                return route["canary"]
            return route["stable"]

        elif strategy == DeploymentStrategy.BLUE_GREEN:
            # Route to active deployment
            active = route["active"]
            return route[active]

        elif strategy == DeploymentStrategy.AB_TEST:
            # Deterministic routing based on user_id
            if user_id:
                hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                if (hash_val % 100) < route["treatment_percent"]:
                    return route["treatment"]
            return route["control"]

        return "latest"

    def switch_blue_green(self, model_name: str):
        """Switch active deployment in blue-green."""
        if model_name not in self.routes:
            return

        route = self.routes[model_name]
        if route["strategy"] != DeploymentStrategy.BLUE_GREEN:
            return

        route["active"] = "green" if route["active"] == "blue" else "blue"

    def update_canary_percent(self, model_name: str, new_percent: float):
        """Update canary traffic percentage."""
        if model_name in self.routes:
            route = self.routes[model_name]
            if route["strategy"] == DeploymentStrategy.CANARY:
                route["canary_percent"] = new_percent

    def record_metric(
        self,
        model_name: str,
        version: str,
        latency_ms: float,
        success: bool
    ):
        """Record request metric for analysis."""
        key = model_name
        if self.routes.get(model_name, {}).get("strategy") == DeploymentStrategy.AB_TEST:
            route = self.routes[model_name]
            variant = "treatment" if version == route["treatment"] else "control"
            key = f"{model_name}_{variant}"

        if key not in self.metrics:
            self.metrics[key] = []

        self.metrics[key].append({
            "version": version,
            "latency_ms": latency_ms,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def analyze_ab_test(self, model_name: str) -> Dict:
        """Analyze A/B test results."""
        control_key = f"{model_name}_control"
        treatment_key = f"{model_name}_treatment"

        if control_key not in self.metrics or treatment_key not in self.metrics:
            return {"error": "No metrics found"}

        control = self.metrics[control_key]
        treatment = self.metrics[treatment_key]

        if not control or not treatment:
            return {"error": "Insufficient data"}

        control_success = sum(1 for m in control if m["success"]) / len(control)
        treatment_success = sum(1 for m in treatment if m["success"]) / len(treatment)

        control_latency = sum(m["latency_ms"] for m in control) / len(control)
        treatment_latency = sum(m["latency_ms"] for m in treatment) / len(treatment)

        # Simple statistical significance (would use scipy.stats in production)
        improvement = treatment_success - control_success
        significant = abs(improvement) > 0.05 and len(control) > 30 and len(treatment) > 30

        return {
            "control": {
                "samples": len(control),
                "success_rate": control_success,
                "avg_latency_ms": control_latency
            },
            "treatment": {
                "samples": len(treatment),
                "success_rate": treatment_success,
                "avg_latency_ms": treatment_latency
            },
            "improvement": improvement,
            "significant": significant,
            "recommendation": "deploy_treatment" if improvement > 0 and significant else "keep_control"
        }


class ModelServer:
    """
    Model serving server.

    Simulates FastAPI-based model serving with health checks,
    batching, and metrics collection.
    """

    def __init__(self, registry: ModelRegistry, router: TrafficRouter):
        self.registry = registry
        self.router = router
        self.request_count = 0
        self.error_count = 0
        self.latencies: List[float] = []
        self.is_healthy = True
        self.is_ready = False

    def startup(self):
        """Initialize server (load models, etc.)."""
        print("  Starting server...")
        time.sleep(0.1)  # Simulate startup
        self.is_ready = True
        print("  Server ready!")

    def shutdown(self):
        """Graceful shutdown."""
        print("  Shutting down...")
        self.is_ready = False
        time.sleep(0.1)  # Simulate graceful drain
        print("  Server stopped.")

    def health_check(self) -> Dict:
        """Liveness check."""
        return {"status": "healthy" if self.is_healthy else "unhealthy"}

    def readiness_check(self) -> Dict:
        """Readiness check."""
        return {
            "status": "ready" if self.is_ready else "not_ready",
            "models_loaded": len(self.registry.models)
        }

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Handle prediction request."""
        start_time = time.time()
        self.request_count += 1

        try:
            # Route to appropriate model version
            model_name = request.model_version or "default"
            version = self.router.route(model_name, request.user_id)

            # Get model
            model = self.registry.get_model(model_name, version)
            if not model:
                # Use any available model
                for name, versions in self.registry.models.items():
                    for v, m in versions.items():
                        model = m
                        version = v
                        break
                    break

            if not model:
                raise ValueError("No model available")

            # Make prediction
            prediction, confidence = model.predict(request.features)

            latency_ms = (time.time() - start_time) * 1000
            self.latencies.append(latency_ms)

            # Record metrics
            self.router.record_metric(model_name, version, latency_ms, True)

            return PredictionResponse(
                request_id=request.request_id,
                prediction=prediction,
                confidence=confidence,
                model_version=f"{model.name}:{version}",
                latency_ms=latency_ms
            )

        except Exception as e:
            self.error_count += 1
            latency_ms = (time.time() - start_time) * 1000
            self.router.record_metric("error", "error", latency_ms, False)
            raise

    def predict_batch(self, requests: List[PredictionRequest]) -> List[PredictionResponse]:
        """Handle batch prediction."""
        return [self.predict(req) for req in requests]

    def get_metrics(self) -> Dict:
        """Get server metrics."""
        if not self.latencies:
            return {"error": "No requests processed"}

        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)

        return {
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "latency": {
                "mean_ms": sum(self.latencies) / n,
                "p50_ms": sorted_latencies[int(n * 0.5)],
                "p95_ms": sorted_latencies[int(n * 0.95)] if n > 20 else sorted_latencies[-1],
                "p99_ms": sorted_latencies[int(n * 0.99)] if n > 100 else sorted_latencies[-1]
            },
            "throughput_qps": self.request_count / max(sum(self.latencies) / 1000, 0.001)
        }


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo1_model_server():
    """
    Demo 1: Basic model server.

    Shows model registration, serving, and metrics.
    """
    print("=" * 70)
    print("DEMO 1: BASIC MODEL SERVER")
    print("=" * 70)

    print("\n📋 Model Serving Concepts:")
    print("-" * 40)
    print("  • Register models in registry")
    print("  • Serve predictions via API")
    print("  • Health checks for orchestration")
    print("  • Metrics collection")

    # Create registry and router
    registry = ModelRegistry()
    router = TrafficRouter()

    # Register models
    print("\n📦 Registering Models:")
    print("-" * 40)

    model_v1 = ModelVersion(
        name="churn_predictor",
        version="1.0.0",
        accuracy=0.85,
        latency_ms=10,
        metadata={"framework": "sklearn", "features": 10}
    )
    registry.register(model_v1)
    print(f"  ✅ Registered {model_v1.name}:{model_v1.version}")

    model_v2 = ModelVersion(
        name="churn_predictor",
        version="2.0.0",
        accuracy=0.92,
        latency_ms=15,
        metadata={"framework": "xgboost", "features": 10}
    )
    registry.register(model_v2)
    print(f"  ✅ Registered {model_v2.name}:{model_v2.version}")

    # Promote to production
    result = registry.promote("churn_predictor", "1.0.0", ModelStage.PRODUCTION)
    print(f"\n  {result}")

    # Create server
    server = ModelServer(registry, router)
    server.startup()

    # Health checks
    print("\n🏥 Health Checks:")
    print("-" * 40)
    print(f"  Liveness: {server.health_check()}")
    print(f"  Readiness: {server.readiness_check()}")

    # Make predictions
    print("\n🔮 Making Predictions:")
    print("-" * 40)

    for i in range(5):
        request = PredictionRequest(
            request_id=f"req_{i}",
            features=[random.random() for _ in range(10)],
            model_version="churn_predictor"
        )
        response = server.predict(request)
        print(f"  Request {i}: prediction={response.prediction:.3f}, "
              f"confidence={response.confidence:.3f}, "
              f"latency={response.latency_ms:.2f}ms")

    # Metrics
    print("\n📊 Server Metrics:")
    print("-" * 40)
    metrics = server.get_metrics()
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Error rate: {metrics['error_rate']:.2%}")
    print(f"  Mean latency: {metrics['latency']['mean_ms']:.2f}ms")
    print(f"  P95 latency: {metrics['latency']['p95_ms']:.2f}ms")

    server.shutdown()
    print("\n✅ Demo 1 complete!")


def demo2_blue_green():
    """
    Demo 2: Blue-green deployment.

    Shows instant traffic switching between versions.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: BLUE-GREEN DEPLOYMENT")
    print("=" * 70)

    print("\n📋 Blue-Green Concepts:")
    print("-" * 40)
    print("  • Two identical environments (blue/green)")
    print("  • Deploy to inactive environment")
    print("  • Instant traffic switch")
    print("  • Instant rollback if needed")

    # Setup
    registry = ModelRegistry()
    router = TrafficRouter()

    # Register blue (current) and green (new) versions
    blue_model = ModelVersion("recommender", "1.0.0", 0.85, 12)
    green_model = ModelVersion("recommender", "2.0.0", 0.90, 10)

    registry.register(blue_model)
    registry.register(green_model)

    # Configure blue-green
    router.configure_blue_green(
        "recommender",
        blue_version="1.0.0",
        green_version="2.0.0",
        active="blue"
    )

    server = ModelServer(registry, router)
    server.startup()

    print("\n🔵 Phase 1: Blue Active (v1.0.0)")
    print("-" * 40)

    for i in range(3):
        request = PredictionRequest(
            request_id=f"blue_{i}",
            features=[random.random() for _ in range(5)],
            model_version="recommender"
        )
        response = server.predict(request)
        print(f"  Request {i}: version={response.model_version}, "
              f"latency={response.latency_ms:.2f}ms")

    print("\n🔄 Switching to Green (v2.0.0)...")
    router.switch_blue_green("recommender")
    print("  Traffic switched!")

    print("\n🟢 Phase 2: Green Active (v2.0.0)")
    print("-" * 40)

    for i in range(3):
        request = PredictionRequest(
            request_id=f"green_{i}",
            features=[random.random() for _ in range(5)],
            model_version="recommender"
        )
        response = server.predict(request)
        print(f"  Request {i}: version={response.model_version}, "
              f"latency={response.latency_ms:.2f}ms")

    print("\n⚠️ Issue detected! Rolling back...")
    router.switch_blue_green("recommender")
    print("  Rolled back to Blue!")

    print("\n🔵 Phase 3: Blue Active Again (v1.0.0)")
    print("-" * 40)

    for i in range(2):
        request = PredictionRequest(
            request_id=f"rollback_{i}",
            features=[random.random() for _ in range(5)],
            model_version="recommender"
        )
        response = server.predict(request)
        print(f"  Request {i}: version={response.model_version}")

    print("\n📊 Blue-Green Summary:")
    print("-" * 40)
    print("  ✅ Zero-downtime deployment")
    print("  ✅ Instant rollback capability")
    print("  ⚠️ Requires 2x infrastructure")

    server.shutdown()
    print("\n✅ Demo 2 complete!")


def demo3_canary():
    """
    Demo 3: Canary deployment.

    Shows progressive traffic shifting.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: CANARY DEPLOYMENT")
    print("=" * 70)

    print("\n📋 Canary Concepts:")
    print("-" * 40)
    print("  • Deploy new version to small % of traffic")
    print("  • Monitor metrics")
    print("  • Gradually increase if healthy")
    print("  • Auto-rollback if metrics degrade")

    # Setup
    registry = ModelRegistry()
    router = TrafficRouter()

    stable = ModelVersion("fraud_detector", "1.0.0", 0.88, 15)
    canary = ModelVersion("fraud_detector", "2.0.0", 0.93, 12)

    registry.register(stable)
    registry.register(canary)

    server = ModelServer(registry, router)
    server.startup()

    # Progressive rollout
    stages = [
        (5, "Initial canary (5%)"),
        (25, "Increase to 25%"),
        (50, "Increase to 50%"),
        (100, "Full rollout (100%)")
    ]

    for canary_percent, description in stages:
        print(f"\n🐤 {description}")
        print("-" * 40)

        router.configure_canary(
            "fraud_detector",
            stable_version="1.0.0",
            canary_version="2.0.0",
            canary_percent=canary_percent
        )

        # Simulate requests
        stable_count = 0
        canary_count = 0

        for i in range(20):
            request = PredictionRequest(
                request_id=f"canary_{canary_percent}_{i}",
                features=[random.random() for _ in range(8)],
                model_version="fraud_detector"
            )
            response = server.predict(request)

            if "1.0.0" in response.model_version:
                stable_count += 1
            else:
                canary_count += 1

        actual_canary_percent = canary_count / 20 * 100
        print(f"  Stable (v1.0.0): {stable_count} requests ({stable_count/20*100:.0f}%)")
        print(f"  Canary (v2.0.0): {canary_count} requests ({canary_count/20*100:.0f}%)")
        print(f"  Target: {canary_percent}%, Actual: {actual_canary_percent:.0f}%")

    print("\n📊 Canary Summary:")
    print("-" * 40)
    print("  ✅ Gradual rollout reduces risk")
    print("  ✅ Can monitor real traffic")
    print("  ✅ Easy rollback by reducing %")

    server.shutdown()
    print("\n✅ Demo 3 complete!")


def demo4_ab_testing():
    """
    Demo 4: A/B testing for models.

    Shows statistical comparison of model versions.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: A/B TESTING")
    print("=" * 70)

    print("\n📋 A/B Testing Concepts:")
    print("-" * 40)
    print("  • Split traffic between control/treatment")
    print("  • Deterministic user assignment")
    print("  • Statistical significance testing")
    print("  • Data-driven decisions")

    # Setup
    registry = ModelRegistry()
    router = TrafficRouter()

    control = ModelVersion("pricing_model", "1.0.0", 0.85, 20)
    treatment = ModelVersion("pricing_model", "2.0.0", 0.89, 18)

    registry.register(control)
    registry.register(treatment)

    router.configure_ab_test(
        "pricing_model",
        control_version="1.0.0",
        treatment_version="2.0.0",
        treatment_percent=50.0
    )

    server = ModelServer(registry, router)
    server.startup()

    print("\n🧪 Running A/B Test:")
    print("-" * 40)

    # Simulate many requests with different users
    control_count = 0
    treatment_count = 0
    users_seen = {}

    for i in range(100):
        user_id = f"user_{i % 20}"  # 20 unique users

        request = PredictionRequest(
            request_id=f"ab_{i}",
            features=[random.random() for _ in range(6)],
            model_version="pricing_model",
            user_id=user_id
        )
        response = server.predict(request)

        version = response.model_version

        # Track which version each user gets
        if user_id not in users_seen:
            users_seen[user_id] = version

        # Verify deterministic assignment
        assert users_seen[user_id] == version, "User assignment not deterministic!"

        if "1.0.0" in version:
            control_count += 1
        else:
            treatment_count += 1

    print(f"  Control (v1.0.0): {control_count} requests")
    print(f"  Treatment (v2.0.0): {treatment_count} requests")
    print(f"  Unique users: {len(users_seen)}")

    # Analyze results
    print("\n📊 A/B Test Analysis:")
    print("-" * 40)

    analysis = router.analyze_ab_test("pricing_model")

    print(f"\n  Control Group:")
    print(f"    Samples: {analysis['control']['samples']}")
    print(f"    Success Rate: {analysis['control']['success_rate']:.2%}")
    print(f"    Avg Latency: {analysis['control']['avg_latency_ms']:.2f}ms")

    print(f"\n  Treatment Group:")
    print(f"    Samples: {analysis['treatment']['samples']}")
    print(f"    Success Rate: {analysis['treatment']['success_rate']:.2%}")
    print(f"    Avg Latency: {analysis['treatment']['avg_latency_ms']:.2f}ms")

    print(f"\n  Results:")
    print(f"    Improvement: {analysis['improvement']:.2%}")
    print(f"    Statistically Significant: {analysis['significant']}")
    print(f"    Recommendation: {analysis['recommendation']}")

    server.shutdown()
    print("\n✅ Demo 4 complete!")


def demo5_performance():
    """
    Demo 5: Performance benchmarking.

    Shows latency percentiles and throughput measurement.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: PERFORMANCE BENCHMARKING")
    print("=" * 70)

    print("\n📋 Performance Concepts:")
    print("-" * 40)
    print("  • Latency percentiles (P50, P95, P99)")
    print("  • Throughput (QPS)")
    print("  • Warm-up period")
    print("  • Load testing")

    # Setup different model configurations
    configs = [
        ("Fast Model", ModelVersion("benchmark", "fast", 0.85, 5)),
        ("Accurate Model", ModelVersion("benchmark", "accurate", 0.95, 25)),
        ("Balanced Model", ModelVersion("benchmark", "balanced", 0.90, 12)),
    ]

    results = []

    for name, model in configs:
        print(f"\n⚡ Benchmarking: {name}")
        print("-" * 40)

        registry = ModelRegistry()
        router = TrafficRouter()
        registry.register(model)
        registry.promote("benchmark", model.version, ModelStage.PRODUCTION)

        server = ModelServer(registry, router)
        server.startup()

        # Warmup
        print("  Warming up...")
        for _ in range(10):
            request = PredictionRequest(
                request_id="warmup",
                features=[random.random() for _ in range(10)],
                model_version="benchmark"
            )
            server.predict(request)

        # Clear metrics
        server.latencies = []
        server.request_count = 0

        # Benchmark
        print("  Running benchmark (100 requests)...")
        start_time = time.time()

        for i in range(100):
            request = PredictionRequest(
                request_id=f"bench_{i}",
                features=[random.random() for _ in range(10)],
                model_version="benchmark"
            )
            server.predict(request)

        total_time = time.time() - start_time

        metrics = server.get_metrics()
        metrics["name"] = name
        metrics["total_time_s"] = total_time
        metrics["accuracy"] = model.accuracy
        results.append(metrics)

        print(f"  Mean latency: {metrics['latency']['mean_ms']:.2f}ms")
        print(f"  P95 latency: {metrics['latency']['p95_ms']:.2f}ms")
        print(f"  Throughput: {100/total_time:.1f} QPS")

        server.shutdown()

    # Comparison
    print("\n📊 Performance Comparison:")
    print("-" * 60)
    print(f"{'Model':<20} {'Accuracy':<10} {'P50 (ms)':<10} {'P95 (ms)':<10} {'QPS':<10}")
    print("-" * 60)

    for r in results:
        qps = 100 / r["total_time_s"]
        print(f"{r['name']:<20} {r['accuracy']:<10.2%} "
              f"{r['latency']['p50_ms']:<10.2f} "
              f"{r['latency']['p95_ms']:<10.2f} "
              f"{qps:<10.1f}")

    print("\n📈 Recommendations:")
    print("-" * 40)
    print("  • Low latency requirement → Fast Model")
    print("  • High accuracy requirement → Accurate Model")
    print("  • Balance both → Balanced Model")

    print("\n✅ Demo 5 complete!")
    print(f"📂 Serving data saved to: {SERVING_DIR}")


def show_help():
    """Show help information."""
    help_text = """
ML Model Serving Toolkit
========================

A comprehensive toolkit demonstrating model deployment and serving patterns.

Usage:
    python deliverable_ml_serving_toolkit.py <demo>

Available Demos:
    demo1   Basic model server (registration, prediction, metrics)
    demo2   Blue-green deployment (instant switch)
    demo3   Canary deployment (progressive rollout)
    demo4   A/B testing (statistical comparison)
    demo5   Performance benchmarking (latency, throughput)

Examples:
    python deliverable_ml_serving_toolkit.py demo1
    python deliverable_ml_serving_toolkit.py demo2
    python deliverable_ml_serving_toolkit.py demo5

Key Concepts:
    Model Registry     Version management for models
    Traffic Router     Direct requests to model versions
    Blue-Green         Instant switch, instant rollback
    Canary             Progressive rollout, risk reduction
    A/B Testing        Statistical model comparison
    Benchmarking       Latency percentiles, throughput

Production Tools:
    FastAPI            REST API framework
    gRPC               High-performance RPC
    TorchServe         PyTorch model serving
    Triton             Multi-framework GPU serving
    TF Serving         TensorFlow serving
    """
    print(help_text)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo1_model_server,
        "demo2": demo2_blue_green,
        "demo3": demo3_canary,
        "demo4": demo4_ab_testing,
        "demo5": demo5_performance,
        "help": show_help,
        "--help": show_help,
        "-h": show_help
    }

    if command in demos:
        demos[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
