# Module 51: Model Deployment & Serving Patterns

**Duration**: 7-8 hours
**Prerequisites**: Module 50 (ML Pipeline Orchestration)
**Status**: 🟢 Complete

---

## Learning Objectives

By the end of this module, you will:
- Deploy ML models as REST APIs with FastAPI
- Implement high-performance serving with gRPC
- Master deployment patterns (canary, blue-green, A/B testing)
- Optimize models for inference (ONNX, TensorRT)
- Use production serving frameworks (TorchServe, Triton)
- Implement model versioning and rollback strategies

---

## Why Model Deployment Matters

Training a great model is only half the battle. Getting it into production, serving predictions at scale, and maintaining it over time - that's where real engineering happens.

**The Deployment Gap**:
```
RESEARCH                           PRODUCTION
========                           ==========

Jupyter notebooks                  REST/gRPC APIs
Single GPU                         Distributed serving
Batch predictions                  Real-time (<100ms)
"Works on my machine"              99.9% uptime SLA
Manual updates                     Automated rollouts
No monitoring                      Full observability
```

**Did You Know?** According to a 2022 Gartner report, only 54% of ML models make it to production. The main barriers? Deployment complexity, lack of MLOps practices, and the gap between data science and engineering teams. This module bridges that gap.

---

## Model Serving Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODEL SERVING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   CLIENTS                                                                │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                                │
│   │   Web   │  │ Mobile  │  │ Backend │                                │
│   │   App   │  │   App   │  │ Service │                                │
│   └────┬────┘  └────┬────┘  └────┬────┘                                │
│        │           │           │                                        │
│        └───────────┴───────────┘                                        │
│                    │                                                     │
│                    ▼                                                     │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │              LOAD BALANCER / API GATEWAY                 │          │
│   │         (Nginx, Kong, AWS ALB, Istio)                   │          │
│   └─────────────────────────────────────────────────────────┘          │
│                    │                                                     │
│        ┌───────────┴───────────┐                                        │
│        ▼                       ▼                                        │
│   ┌─────────┐             ┌─────────┐                                  │
│   │Model v1 │             │Model v2 │   ← Canary / A/B                 │
│   │  (90%)  │             │  (10%)  │                                  │
│   └────┬────┘             └────┬────┘                                  │
│        │                       │                                        │
│        └───────────┬───────────┘                                        │
│                    │                                                     │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │              MODEL SERVING LAYER                         │          │
│   │    FastAPI / TorchServe / Triton / TF Serving           │          │
│   └─────────────────────────────────────────────────────────┘          │
│                    │                                                     │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │              MODEL STORAGE                               │          │
│   │         S3 / GCS / Model Registry                       │          │
│   └─────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## REST API with FastAPI

### Why FastAPI?

FastAPI is the go-to framework for ML model serving in Python:
- **Fast**: Built on Starlette and Pydantic, async by default
- **Type-safe**: Automatic request/response validation
- **Auto-docs**: Swagger UI generated automatically
- **Production-ready**: Used by Netflix, Uber, Microsoft

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np

app = FastAPI(
    title="ML Model API",
    description="Production model serving API",
    version="1.0.0"
)

# Request/Response Models
class PredictionRequest(BaseModel):
    features: List[float] = Field(..., min_items=1, max_items=100)
    model_version: Optional[str] = "latest"

    class Config:
        schema_extra = {
            "example": {
                "features": [0.5, 0.3, 0.8, 0.2],
                "model_version": "v1.2.0"
            }
        }

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str
    latency_ms: float

# Load model (in production, use proper model registry)
model = None  # Your trained model

@app.on_event("startup")
async def load_model():
    global model
    model = load_trained_model("models/production/model.pkl")

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Generate prediction for input features.
    """
    import time
    start = time.time()

    try:
        # Preprocess
        features = np.array(request.features).reshape(1, -1)

        # Predict
        prediction = model.predict(features)[0]
        confidence = model.predict_proba(features).max()

        latency = (time.time() - start) * 1000

        return PredictionResponse(
            prediction=float(prediction),
            confidence=float(confidence),
            model_version=request.model_version,
            latency_ms=latency
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model_loaded": model is not None}

@app.get("/model/info")
async def model_info():
    """Get model metadata."""
    return {
        "name": "churn_predictor",
        "version": "1.2.0",
        "framework": "sklearn",
        "features": 4,
        "classes": ["no_churn", "churn"]
    }
```

### Batch Predictions

```python
from fastapi import BackgroundTasks
from typing import List
import asyncio

class BatchRequest(BaseModel):
    instances: List[List[float]]
    async_mode: bool = False

class BatchResponse(BaseModel):
    predictions: List[float]
    batch_size: int
    total_latency_ms: float

@app.post("/predict/batch", response_model=BatchResponse)
async def predict_batch(request: BatchRequest):
    """
    Batch prediction for multiple instances.
    More efficient than individual calls.
    """
    start = time.time()

    features = np.array(request.instances)
    predictions = model.predict(features).tolist()

    return BatchResponse(
        predictions=predictions,
        batch_size=len(request.instances),
        total_latency_ms=(time.time() - start) * 1000
    )

# Async batch processing
@app.post("/predict/async")
async def predict_async(
    request: BatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit batch for async processing.
    Returns job_id to check status later.
    """
    job_id = generate_job_id()
    background_tasks.add_task(
        process_batch_async,
        job_id,
        request.instances
    )
    return {"job_id": job_id, "status": "processing"}
```

**Did You Know?** FastAPI was created by Sebastián Ramírez in 2018. He was frustrated with the complexity of Flask + Marshmallow + swagger-ui combinations. FastAPI combines all these features with modern Python type hints. It quickly became the fastest-growing Python web framework, reaching 50k GitHub stars in just 4 years.

---

## gRPC for High-Performance Serving

### Why gRPC?

gRPC is Google's high-performance RPC framework, ideal for:
- **Low latency**: Binary protocol (Protocol Buffers)
- **Streaming**: Bi-directional streaming support
- **Strong typing**: Generated client/server code
- **Multi-language**: Same proto works in Python, Go, Java, etc.

```
REST vs gRPC
============

REST (JSON):
┌─────────────────────────────────────────┐
│ {"features": [0.5, 0.3, 0.8], "id": 1}  │
│ ~50 bytes, text parsing required        │
└─────────────────────────────────────────┘

gRPC (Protobuf):
┌─────────────────────────────────────────┐
│ 0x0a0c0d0000003f15cdcc4c3e1d...        │
│ ~20 bytes, binary, no parsing           │
└─────────────────────────────────────────┘

Latency comparison:
REST:  ~10-50ms overhead
gRPC:  ~1-5ms overhead
```

### Protocol Buffer Definition

```protobuf
// model_service.proto

syntax = "proto3";

package ml_serving;

service ModelService {
    // Unary prediction
    rpc Predict(PredictRequest) returns (PredictResponse);

    // Streaming predictions (for real-time data)
    rpc PredictStream(stream PredictRequest) returns (stream PredictResponse);

    // Batch prediction
    rpc PredictBatch(BatchRequest) returns (BatchResponse);

    // Model info
    rpc GetModelInfo(Empty) returns (ModelInfo);
}

message PredictRequest {
    repeated float features = 1;
    string model_version = 2;
}

message PredictResponse {
    float prediction = 1;
    float confidence = 2;
    string model_version = 3;
    float latency_ms = 4;
}

message BatchRequest {
    repeated PredictRequest instances = 1;
}

message BatchResponse {
    repeated PredictResponse predictions = 1;
    int32 batch_size = 2;
    float total_latency_ms = 3;
}

message ModelInfo {
    string name = 1;
    string version = 2;
    string framework = 3;
    int32 num_features = 4;
    repeated string classes = 5;
}

message Empty {}
```

### gRPC Server Implementation

```python
import grpc
from concurrent import futures
import model_service_pb2
import model_service_pb2_grpc
import numpy as np
import time

class ModelServicer(model_service_pb2_grpc.ModelServiceServicer):
    def __init__(self, model):
        self.model = model

    def Predict(self, request, context):
        """Single prediction."""
        start = time.time()

        features = np.array(request.features).reshape(1, -1)
        prediction = self.model.predict(features)[0]
        confidence = self.model.predict_proba(features).max()

        return model_service_pb2.PredictResponse(
            prediction=float(prediction),
            confidence=float(confidence),
            model_version=request.model_version or "v1.0",
            latency_ms=(time.time() - start) * 1000
        )

    def PredictStream(self, request_iterator, context):
        """Streaming predictions - process as they arrive."""
        for request in request_iterator:
            features = np.array(request.features).reshape(1, -1)
            prediction = self.model.predict(features)[0]

            yield model_service_pb2.PredictResponse(
                prediction=float(prediction),
                confidence=0.95,
                model_version="v1.0",
                latency_ms=1.0
            )

    def PredictBatch(self, request, context):
        """Batch prediction."""
        start = time.time()

        responses = []
        for instance in request.instances:
            features = np.array(instance.features).reshape(1, -1)
            prediction = self.model.predict(features)[0]

            responses.append(model_service_pb2.PredictResponse(
                prediction=float(prediction),
                confidence=0.95,
                model_version="v1.0"
            ))

        return model_service_pb2.BatchResponse(
            predictions=responses,
            batch_size=len(responses),
            total_latency_ms=(time.time() - start) * 1000
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_service_pb2_grpc.add_ModelServiceServicer_to_server(
        ModelServicer(model), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

---

## Deployment Patterns

### Pattern 1: Blue-Green Deployment

```
BLUE-GREEN DEPLOYMENT
=====================

Before update:
┌─────────────────────────────────────────┐
│              LOAD BALANCER              │
└────────────────────┬────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   BLUE      │  ← 100% traffic
              │   (v1.0)    │
              └─────────────┘
              ┌─────────────┐
              │   GREEN     │  ← 0% traffic (standby)
              │   (v1.0)    │
              └─────────────┘

Deploy v2.0 to GREEN:
┌─────────────────────────────────────────┐
│              LOAD BALANCER              │
└────────────────────┬────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   BLUE      │  ← 100% traffic
              │   (v1.0)    │
              └─────────────┘
              ┌─────────────┐
              │   GREEN     │  ← Testing v2.0
              │   (v2.0)    │
              └─────────────┘

Switch traffic:
┌─────────────────────────────────────────┐
│              LOAD BALANCER              │
└────────────────────┬────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   BLUE      │  ← 0% traffic (standby)
              │   (v1.0)    │
              └─────────────┘
              ┌─────────────┐
              │   GREEN     │  ← 100% traffic
              │   (v2.0)    │
              └─────────────┘

Rollback if needed: instant switch back to BLUE
```

### Pattern 2: Canary Deployment

```
CANARY DEPLOYMENT
=================

Progressive rollout:

Phase 1: 5% canary
┌─────────────────────────────────────────┐
│              LOAD BALANCER              │
└────────────────────┬────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌─────────────┐       ┌─────────────┐
    │   STABLE    │       │   CANARY    │
    │   (v1.0)    │       │   (v2.0)    │
    │    95%      │       │     5%      │
    └─────────────┘       └─────────────┘

Phase 2: Monitor metrics, increase to 25%
Phase 3: If healthy, increase to 50%
Phase 4: If healthy, promote to 100%

Automatic rollback if:
- Error rate > threshold
- Latency > threshold
- Custom metric violations
```

### Pattern 3: A/B Testing

```python
class ABTestRouter:
    """
    Route requests to different model versions for A/B testing.
    """

    def __init__(self):
        self.experiments = {}

    def create_experiment(
        self,
        experiment_id: str,
        control_model: str,
        treatment_model: str,
        traffic_split: float = 0.5
    ):
        """Create new A/B experiment."""
        self.experiments[experiment_id] = {
            "control": control_model,
            "treatment": treatment_model,
            "split": traffic_split,
            "metrics": {"control": [], "treatment": []}
        }

    def route_request(self, experiment_id: str, user_id: str) -> str:
        """
        Deterministically route user to model variant.
        Same user always gets same variant (for consistency).
        """
        experiment = self.experiments[experiment_id]

        # Hash user_id for deterministic assignment
        hash_value = hash(f"{experiment_id}:{user_id}") % 100
        is_treatment = hash_value < (experiment["split"] * 100)

        return experiment["treatment"] if is_treatment else experiment["control"]

    def record_outcome(
        self,
        experiment_id: str,
        variant: str,
        prediction: float,
        actual: float
    ):
        """Record prediction outcome for analysis."""
        self.experiments[experiment_id]["metrics"][variant].append({
            "prediction": prediction,
            "actual": actual,
            "correct": (prediction > 0.5) == (actual > 0.5)
        })

    def analyze_experiment(self, experiment_id: str) -> dict:
        """
        Statistical analysis of A/B test results.
        """
        from scipy import stats

        exp = self.experiments[experiment_id]
        control = exp["metrics"]["control"]
        treatment = exp["metrics"]["treatment"]

        control_accuracy = sum(m["correct"] for m in control) / len(control)
        treatment_accuracy = sum(m["correct"] for m in treatment) / len(treatment)

        # Statistical significance test
        control_correct = [m["correct"] for m in control]
        treatment_correct = [m["correct"] for m in treatment]

        t_stat, p_value = stats.ttest_ind(control_correct, treatment_correct)

        return {
            "control_accuracy": control_accuracy,
            "treatment_accuracy": treatment_accuracy,
            "improvement": treatment_accuracy - control_accuracy,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "recommendation": "deploy_treatment" if (
                treatment_accuracy > control_accuracy and p_value < 0.05
            ) else "keep_control"
        }
```

**Did You Know?** Netflix runs thousands of A/B tests simultaneously. Their ML models for recommendations are constantly being tested against each other. In 2016, they estimated that their recommendation system is worth $1 billion per year in retained subscribers - all validated through rigorous A/B testing.

---

## Model Optimization

### ONNX: Universal Model Format

ONNX (Open Neural Network Exchange) allows you to:
- Export models from any framework
- Optimize for inference
- Deploy anywhere

```python
import onnx
import onnxruntime as ort
import torch

# Export PyTorch model to ONNX
def export_to_onnx(model, sample_input, output_path):
    """Export PyTorch model to ONNX format."""
    model.eval()

    torch.onnx.export(
        model,
        sample_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )

    # Verify the model
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print(f"Model exported to {output_path}")

# Run inference with ONNX Runtime
class ONNXPredictor:
    def __init__(self, model_path: str):
        # Use GPU if available
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)

        # Get input/output names
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Run inference."""
        return self.session.run(
            [self.output_name],
            {self.input_name: features.astype(np.float32)}
        )[0]

    def benchmark(self, features: np.ndarray, iterations: int = 100) -> dict:
        """Benchmark inference performance."""
        import time

        # Warmup
        for _ in range(10):
            self.predict(features)

        # Benchmark
        latencies = []
        for _ in range(iterations):
            start = time.time()
            self.predict(features)
            latencies.append((time.time() - start) * 1000)

        return {
            "mean_ms": np.mean(latencies),
            "p50_ms": np.percentile(latencies, 50),
            "p95_ms": np.percentile(latencies, 95),
            "p99_ms": np.percentile(latencies, 99),
            "throughput_qps": 1000 / np.mean(latencies)
        }
```

### TensorRT Optimization

```python
# TensorRT for NVIDIA GPU optimization
import tensorrt as trt

def optimize_with_tensorrt(onnx_path: str, engine_path: str):
    """
    Convert ONNX model to TensorRT engine.
    Can provide 2-5x speedup on NVIDIA GPUs.
    """
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX
    with open(onnx_path, 'rb') as f:
        if not parser.parse(f.read()):
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            raise RuntimeError("ONNX parsing failed")

    # Configure builder
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30  # 1GB

    # Enable FP16 for faster inference (with minimal accuracy loss)
    if builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    # Build engine
    engine = builder.build_engine(network, config)

    # Save
    with open(engine_path, 'wb') as f:
        f.write(engine.serialize())

    print(f"TensorRT engine saved to {engine_path}")
```

**Performance Comparison**:
```
Model: ResNet-50, Batch Size: 1, GPU: A100

Framework          Latency (ms)    Throughput (QPS)
─────────────────────────────────────────────────
PyTorch (eager)       15.2              66
PyTorch (compiled)     8.5             118
ONNX Runtime           6.2             161
TensorRT FP32          4.1             244
TensorRT FP16          2.3             435
TensorRT INT8          1.5             667
```

---

## Production Serving Frameworks

### TorchServe

```python
# TorchServe handler example
# Save as model_handler.py

from ts.torch_handler.base_handler import BaseHandler
import torch
import json

class ModelHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.model = None

    def initialize(self, context):
        """Load the model."""
        self.manifest = context.manifest
        model_dir = context.system_properties.get("model_dir")

        # Load model
        model_path = f"{model_dir}/model.pt"
        self.model = torch.jit.load(model_path)
        self.model.eval()

    def preprocess(self, data):
        """Preprocess input data."""
        inputs = []
        for row in data:
            input_data = row.get("data") or row.get("body")
            if isinstance(input_data, (bytes, bytearray)):
                input_data = json.loads(input_data.decode('utf-8'))
            inputs.append(torch.tensor(input_data["features"]))
        return torch.stack(inputs)

    def inference(self, inputs):
        """Run model inference."""
        with torch.no_grad():
            outputs = self.model(inputs)
        return outputs

    def postprocess(self, outputs):
        """Format outputs for response."""
        predictions = outputs.numpy().tolist()
        return [{"prediction": p} for p in predictions]
```

### Triton Inference Server

```python
# Triton model configuration
# config.pbtxt

name: "ensemble_model"
platform: "ensemble"
max_batch_size: 64

input [
  {
    name: "INPUT"
    data_type: TYPE_FP32
    dims: [ -1, 128 ]  # Dynamic batch, 128 features
  }
]

output [
  {
    name: "OUTPUT"
    data_type: TYPE_FP32
    dims: [ -1, 1 ]
  }
]

ensemble_scheduling {
  step [
    {
      model_name: "preprocessing"
      model_version: -1
      input_map {
        key: "INPUT"
        value: "INPUT"
      }
      output_map {
        key: "PROCESSED"
        value: "preprocessed"
      }
    },
    {
      model_name: "main_model"
      model_version: -1
      input_map {
        key: "preprocessed"
        value: "PROCESSED"
      }
      output_map {
        key: "OUTPUT"
        value: "OUTPUT"
      }
    }
  ]
}
```

---

## Model Versioning & Rollback

```python
class ModelRegistry:
    """
    Simple model registry for version management.
    """

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.storage_path / "registry.json"
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if self.registry_file.exists():
            return json.loads(self.registry_file.read_text())
        return {"models": {}, "production": {}}

    def _save_registry(self):
        self.registry_file.write_text(json.dumps(self.registry, indent=2))

    def register_model(
        self,
        model_name: str,
        version: str,
        model_path: str,
        metrics: dict,
        metadata: dict = None
    ):
        """Register a new model version."""
        if model_name not in self.registry["models"]:
            self.registry["models"][model_name] = {}

        self.registry["models"][model_name][version] = {
            "path": model_path,
            "metrics": metrics,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "stage": "staging"
        }

        self._save_registry()
        return f"Registered {model_name}:{version}"

    def promote_to_production(self, model_name: str, version: str):
        """Promote a model version to production."""
        if model_name not in self.registry["models"]:
            raise ValueError(f"Model {model_name} not found")
        if version not in self.registry["models"][model_name]:
            raise ValueError(f"Version {version} not found")

        # Demote current production
        if model_name in self.registry["production"]:
            old_version = self.registry["production"][model_name]
            self.registry["models"][model_name][old_version]["stage"] = "archived"

        # Promote new version
        self.registry["models"][model_name][version]["stage"] = "production"
        self.registry["production"][model_name] = version

        self._save_registry()
        return f"Promoted {model_name}:{version} to production"

    def rollback(self, model_name: str, to_version: str):
        """Rollback to a previous version."""
        return self.promote_to_production(model_name, to_version)

    def get_production_model(self, model_name: str) -> dict:
        """Get current production model info."""
        if model_name not in self.registry["production"]:
            raise ValueError(f"No production model for {model_name}")

        version = self.registry["production"][model_name]
        return {
            "version": version,
            **self.registry["models"][model_name][version]
        }
```

---

## Comparison: Serving Frameworks

```
┌────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│    Feature     │   FastAPI   │ TorchServe  │   Triton    │ TF Serving  │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Framework      │ Any         │ PyTorch     │ Multi       │ TensorFlow  │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Protocol       │ REST        │ REST/gRPC   │ REST/gRPC   │ REST/gRPC   │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Batching       │ Manual      │ Dynamic     │ Dynamic     │ Dynamic     │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ GPU Support    │ Manual      │ Built-in    │ Built-in    │ Built-in    │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Model Format   │ Any         │ TorchScript │ ONNX/TRT    │ SavedModel  │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Complexity     │ Low         │ Medium      │ High        │ Medium      │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Use Case       │ Simple      │ PyTorch     │ High perf   │ TF models   │
│                │ APIs        │ models      │ multi-model │             │
└────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Best Practices

### 1. Health Checks

```python
@app.get("/health")
async def health():
    """Liveness check."""
    return {"status": "alive"}

@app.get("/ready")
async def ready():
    """Readiness check - is the model loaded?"""
    if model is None:
        raise HTTPException(503, "Model not loaded")
    return {"status": "ready", "model_version": model.version}
```

### 2. Graceful Shutdown

```python
import signal

class GracefulShutdown:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGTERM, self._handler)
        signal.signal(signal.SIGINT, self._handler)

    def _handler(self, signum, frame):
        print("Shutdown signal received")
        self.shutdown = True

    async def wait_for_requests(self, timeout: int = 30):
        """Wait for in-flight requests to complete."""
        start = time.time()
        while active_requests > 0 and (time.time() - start) < timeout:
            await asyncio.sleep(0.1)
```

### 3. Request Validation

```python
from pydantic import validator

class PredictionRequest(BaseModel):
    features: List[float]

    @validator('features')
    def validate_features(cls, v):
        if len(v) != 10:
            raise ValueError(f"Expected 10 features, got {len(v)}")
        if any(not (-100 <= f <= 100) for f in v):
            raise ValueError("Features must be in range [-100, 100]")
        return v
```

---

## Summary

```
MODEL DEPLOYMENT PATTERNS
=========================

SERVING OPTIONS:
FastAPI        - Simple, flexible, Python-native
gRPC           - High performance, strong typing
TorchServe     - PyTorch-native, dynamic batching
Triton         - Multi-framework, GPU optimized
TF Serving     - TensorFlow models

DEPLOYMENT PATTERNS:
Blue-Green     - Instant rollback, zero downtime
Canary         - Progressive rollout, risk mitigation
A/B Testing    - Statistical comparison, data-driven

OPTIMIZATION:
ONNX           - Universal format, cross-platform
TensorRT       - NVIDIA GPU optimization (2-5x speedup)
Quantization   - INT8 for smaller models, faster inference

KEY METRICS:
Latency        - P50, P95, P99
Throughput     - Queries per second
Availability   - 99.9% uptime target
```

---

## Next Steps

Module 52 will cover Monitoring & Observability for ML systems, including metrics collection, alerting, and drift detection.

---

_Module 51 Complete!_
_"A model in production is worth a hundred in notebooks."_
