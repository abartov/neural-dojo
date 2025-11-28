# Module 52: Monitoring, Governance & Production Best Practices

**Duration**: 7-8 hours
**Prerequisites**: Module 51 (Model Deployment Patterns)
**Status**: 🟢 Complete

---

## Learning Objectives

By the end of this module, you will:
- Monitor ML models in production effectively
- Detect data drift and concept drift
- Implement model explainability (SHAP, LIME)
- Build alerting systems for ML metrics
- Establish model governance frameworks
- Use observability tools (Prometheus, Grafana, Evidently)

---

## Why ML Monitoring Matters

Traditional software monitoring tracks uptime and latency. ML systems need more: they can fail silently while appearing healthy. A model can return predictions with low latency and high uptime, yet produce increasingly wrong results as the world changes.

**The Silent Failure Problem**:
```
TRADITIONAL SOFTWARE              ML SYSTEMS
==================               ==========

Fail loud                        Fail silent
Crash = Alert                    Wrong prediction = ???
Deterministic                    Probabilistic
Code doesn't change              Data changes constantly
Binary: works/broken             Gradual degradation
```

**Did You Know?** In 2020, Zillow's home-buying algorithm silently degraded due to COVID-19 changing housing market patterns. The model kept making predictions, but they were increasingly wrong. By the time they noticed, Zillow had accumulated $569 million in losses and had to shut down the entire business unit. Proper drift monitoring could have caught this early.

---

## The ML Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ML MONITORING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DATA LAYER                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│   │  Input Data │  │ Predictions │  │Ground Truth │                    │
│   │  Features   │  │   Outputs   │  │  (delayed)  │                    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                    │
│          │               │               │                              │
│          └───────────────┼───────────────┘                              │
│                          │                                              │
│   MONITORING LAYER       ▼                                              │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │                 ML MONITORING                            │          │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │          │
│   │  │  Data   │  │ Model   │  │Concept  │  │ System  │    │          │
│   │  │  Drift  │  │ Perf    │  │ Drift   │  │ Metrics │    │          │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │          │
│   └─────────────────────────────────────────────────────────┘          │
│                          │                                              │
│   ALERTING LAYER         ▼                                              │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │  Prometheus → Alertmanager → PagerDuty/Slack/Email      │          │
│   └─────────────────────────────────────────────────────────┘          │
│                          │                                              │
│   VISUALIZATION          ▼                                              │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │  Grafana Dashboards │ Evidently Reports │ Custom UIs    │          │
│   └─────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Types of Drift

### Data Drift (Covariate Shift)

The input data distribution changes, even if the relationship between inputs and outputs stays the same.

```
DATA DRIFT EXAMPLE
==================

Training Data (2023):              Production Data (2024):
┌────────────────────┐            ┌────────────────────┐
│ Age: 25-45 (80%)   │            │ Age: 18-65 (even)  │
│ Income: $50K-100K  │    →       │ Income: $30K-150K  │
│ Urban: 70%         │            │ Urban: 50%         │
└────────────────────┘            └────────────────────┘

The model learned from a specific population.
Now it sees a different population.
May still work, but performance likely degraded.
```

### Concept Drift

The relationship between inputs and outputs changes, even if input distribution stays the same.

```
CONCEPT DRIFT EXAMPLE
=====================

Before COVID-19:                   After COVID-19:
┌────────────────────┐            ┌────────────────────┐
│ Remote work = low  │            │ Remote work = high │
│ housing demand     │    →       │ housing demand     │
│                    │            │                    │
│ Same features,     │            │ Same features,     │
│ same people        │            │ DIFFERENT behavior │
└────────────────────┘            └────────────────────┘

The world changed. Same inputs now mean different things.
```

### Prediction Drift

The model's output distribution changes unexpectedly.

```python
# Detecting prediction drift
def detect_prediction_drift(
    reference_predictions: np.ndarray,
    current_predictions: np.ndarray,
    threshold: float = 0.05
) -> dict:
    """
    Detect if prediction distribution has shifted.
    Uses Kolmogorov-Smirnov test.
    """
    from scipy import stats

    statistic, p_value = stats.ks_2samp(
        reference_predictions,
        current_predictions
    )

    return {
        "statistic": statistic,
        "p_value": p_value,
        "drift_detected": p_value < threshold,
        "reference_mean": np.mean(reference_predictions),
        "current_mean": np.mean(current_predictions),
        "reference_std": np.std(reference_predictions),
        "current_std": np.std(current_predictions)
    }
```

**Did You Know?** The term "concept drift" was coined by Gerhard Widmer and Miroslav Kubat in 1996 in their paper "Learning in the Presence of Concept Drift and Hidden Contexts." They were studying how machine learning systems could adapt when the underlying patterns they learned were no longer valid - a problem that's become even more critical in the age of real-time ML systems.

---

## Statistical Drift Detection Methods

### Population Stability Index (PSI)

```python
def calculate_psi(
    reference: np.ndarray,
    current: np.ndarray,
    bins: int = 10
) -> float:
    """
    Calculate Population Stability Index.

    PSI < 0.1: No significant change
    PSI 0.1-0.25: Moderate change, investigate
    PSI > 0.25: Significant change, action required
    """
    # Create bins from reference data
    _, bin_edges = np.histogram(reference, bins=bins)

    # Calculate percentages in each bin
    ref_percents = np.histogram(reference, bins=bin_edges)[0] / len(reference)
    cur_percents = np.histogram(current, bins=bin_edges)[0] / len(current)

    # Avoid division by zero
    ref_percents = np.clip(ref_percents, 0.0001, 1)
    cur_percents = np.clip(cur_percents, 0.0001, 1)

    # PSI formula
    psi = np.sum((cur_percents - ref_percents) * np.log(cur_percents / ref_percents))

    return psi
```

### Kolmogorov-Smirnov Test

```python
def ks_drift_test(
    reference: np.ndarray,
    current: np.ndarray,
    alpha: float = 0.05
) -> dict:
    """
    Kolmogorov-Smirnov test for distribution comparison.
    """
    from scipy import stats

    statistic, p_value = stats.ks_2samp(reference, current)

    return {
        "statistic": statistic,
        "p_value": p_value,
        "drift_detected": p_value < alpha,
        "interpretation": (
            "Distributions are different" if p_value < alpha
            else "No significant difference"
        )
    }
```

### Jensen-Shannon Divergence

```python
def js_divergence(
    reference: np.ndarray,
    current: np.ndarray,
    bins: int = 50
) -> float:
    """
    Jensen-Shannon Divergence - symmetric measure of distribution difference.

    JS = 0: Identical distributions
    JS = 1: Completely different distributions
    """
    from scipy.spatial.distance import jensenshannon

    # Create histograms (probability distributions)
    all_data = np.concatenate([reference, current])
    _, bin_edges = np.histogram(all_data, bins=bins)

    ref_hist = np.histogram(reference, bins=bin_edges, density=True)[0]
    cur_hist = np.histogram(current, bins=bin_edges, density=True)[0]

    # Normalize
    ref_hist = ref_hist / ref_hist.sum()
    cur_hist = cur_hist / cur_hist.sum()

    return jensenshannon(ref_hist, cur_hist)
```

---

## Model Performance Monitoring

### Key Metrics to Track

```
CLASSIFICATION METRICS
======================

Metric          Formula                         When to Use
──────────────────────────────────────────────────────────────
Accuracy        (TP + TN) / Total              Balanced classes
Precision       TP / (TP + FP)                 Cost of FP is high
Recall          TP / (TP + FN)                 Cost of FN is high
F1 Score        2 * (P * R) / (P + R)          Imbalanced classes
AUC-ROC         Area under ROC curve           Ranking quality
Log Loss        -Σ y*log(p)                    Probability quality


REGRESSION METRICS
==================

Metric          Formula                         Interpretation
──────────────────────────────────────────────────────────────
MAE             |y - ŷ| / n                    Average error magnitude
RMSE            √(Σ(y - ŷ)² / n)               Penalizes large errors
MAPE            |y - ŷ| / y * 100              Percentage error
R²              1 - SS_res / SS_tot            Variance explained
```

### Sliding Window Monitoring

```python
class SlidingWindowMonitor:
    """
    Monitor metrics over sliding time windows.
    """

    def __init__(self, window_size: int = 1000, alert_threshold: float = 0.1):
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        self.predictions = []
        self.actuals = []
        self.baseline_accuracy = None

    def add_prediction(self, prediction: float, actual: float):
        """Add a new prediction-actual pair."""
        self.predictions.append(prediction)
        self.actuals.append(actual)

        # Keep only window_size recent samples
        if len(self.predictions) > self.window_size:
            self.predictions.pop(0)
            self.actuals.pop(0)

    def set_baseline(self):
        """Set current performance as baseline."""
        self.baseline_accuracy = self.calculate_accuracy()

    def calculate_accuracy(self) -> float:
        """Calculate accuracy over current window."""
        if not self.predictions:
            return 0.0

        correct = sum(
            1 for p, a in zip(self.predictions, self.actuals)
            if (p > 0.5) == (a > 0.5)
        )
        return correct / len(self.predictions)

    def check_degradation(self) -> dict:
        """Check if model performance has degraded."""
        current_accuracy = self.calculate_accuracy()

        if self.baseline_accuracy is None:
            return {"status": "no_baseline", "current_accuracy": current_accuracy}

        degradation = self.baseline_accuracy - current_accuracy

        return {
            "baseline_accuracy": self.baseline_accuracy,
            "current_accuracy": current_accuracy,
            "degradation": degradation,
            "alert": degradation > self.alert_threshold,
            "message": (
                f"ALERT: Accuracy dropped by {degradation:.2%}"
                if degradation > self.alert_threshold
                else "Performance within acceptable range"
            )
        }
```

---

## Model Explainability

### SHAP (SHapley Additive exPlanations)

SHAP values explain how much each feature contributed to a prediction.

```python
import shap

def explain_prediction_shap(model, X_sample, feature_names):
    """
    Explain a single prediction using SHAP.
    """
    # Create explainer
    explainer = shap.TreeExplainer(model)  # For tree-based models
    # Or: explainer = shap.KernelExplainer(model.predict, X_background)

    # Get SHAP values
    shap_values = explainer.shap_values(X_sample)

    # Create explanation
    explanation = {
        "base_value": explainer.expected_value,
        "prediction": model.predict(X_sample)[0],
        "feature_contributions": {
            feature_names[i]: shap_values[0][i]
            for i in range(len(feature_names))
        }
    }

    # Sort by absolute contribution
    sorted_contributions = sorted(
        explanation["feature_contributions"].items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    explanation["top_features"] = sorted_contributions[:5]

    return explanation

# Example output:
# {
#     "base_value": 0.35,
#     "prediction": 0.82,
#     "top_features": [
#         ("credit_score", 0.25),
#         ("income", 0.15),
#         ("age", -0.08),
#         ("employment_years", 0.12),
#         ("debt_ratio", 0.03)
#     ]
# }
```

### LIME (Local Interpretable Model-agnostic Explanations)

```python
from lime.lime_tabular import LimeTabularExplainer

def explain_prediction_lime(model, X_train, X_sample, feature_names):
    """
    Explain a single prediction using LIME.
    """
    explainer = LimeTabularExplainer(
        X_train,
        feature_names=feature_names,
        class_names=['negative', 'positive'],
        mode='classification'
    )

    explanation = explainer.explain_instance(
        X_sample,
        model.predict_proba,
        num_features=10
    )

    return {
        "prediction": model.predict_proba([X_sample])[0],
        "explanation": explanation.as_list(),
        "local_model_r2": explanation.score
    }
```

**Did You Know?** SHAP was developed by Scott Lundberg at the University of Washington in 2017. The key insight was connecting game theory (Shapley values from 1953!) with machine learning explanations. Shapley values were originally designed to fairly distribute payouts among players in cooperative games - Lundberg realized the same math could "fairly" distribute prediction credit among features.

---

## Alerting and Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
PREDICTION_COUNTER = Counter(
    'ml_predictions_total',
    'Total number of predictions',
    ['model_name', 'model_version']
)

PREDICTION_LATENCY = Histogram(
    'ml_prediction_latency_seconds',
    'Prediction latency in seconds',
    ['model_name'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

MODEL_ACCURACY = Gauge(
    'ml_model_accuracy',
    'Current model accuracy (rolling window)',
    ['model_name', 'model_version']
)

DRIFT_SCORE = Gauge(
    'ml_drift_score',
    'Current drift score (PSI)',
    ['model_name', 'feature_name']
)

class PrometheusMLMonitor:
    """
    Export ML metrics to Prometheus.
    """

    def __init__(self, model_name: str, model_version: str, port: int = 8000):
        self.model_name = model_name
        self.model_version = model_version
        start_http_server(port)

    def record_prediction(self, latency_seconds: float):
        """Record a prediction."""
        PREDICTION_COUNTER.labels(
            model_name=self.model_name,
            model_version=self.model_version
        ).inc()

        PREDICTION_LATENCY.labels(
            model_name=self.model_name
        ).observe(latency_seconds)

    def update_accuracy(self, accuracy: float):
        """Update rolling accuracy gauge."""
        MODEL_ACCURACY.labels(
            model_name=self.model_name,
            model_version=self.model_version
        ).set(accuracy)

    def update_drift_score(self, feature_name: str, psi: float):
        """Update drift score for a feature."""
        DRIFT_SCORE.labels(
            model_name=self.model_name,
            feature_name=feature_name
        ).set(psi)
```

### Alert Rules (Prometheus)

```yaml
# prometheus_alerts.yml
groups:
  - name: ml_alerts
    rules:
      - alert: ModelAccuracyDrop
        expr: ml_model_accuracy < 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Model accuracy dropped below 85%"
          description: "Model {{ $labels.model_name }} accuracy is {{ $value }}"

      - alert: HighPredictionLatency
        expr: histogram_quantile(0.95, ml_prediction_latency_seconds_bucket) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency exceeds 500ms"

      - alert: DataDriftDetected
        expr: ml_drift_score > 0.25
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Significant data drift detected"
          description: "Feature {{ $labels.feature_name }} PSI is {{ $value }}"

      - alert: PredictionVolumeAnomaly
        expr: |
          abs(
            rate(ml_predictions_total[5m])
            - rate(ml_predictions_total[1h] offset 1d)
          ) / rate(ml_predictions_total[1h] offset 1d) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Unusual prediction volume detected"
```

---

## Model Governance

### Model Card

```python
@dataclass
class ModelCard:
    """
    Model documentation for governance and transparency.

    Based on Google's Model Cards paper (2019).
    """
    # Basic Info
    name: str
    version: str
    description: str
    owner: str
    created_date: datetime

    # Intended Use
    primary_use_cases: List[str]
    out_of_scope_uses: List[str]
    target_users: List[str]

    # Training Data
    training_data_description: str
    training_data_size: int
    training_data_date_range: Tuple[datetime, datetime]

    # Evaluation
    metrics: Dict[str, float]
    evaluation_data_description: str
    performance_across_groups: Dict[str, Dict[str, float]]

    # Ethical Considerations
    known_limitations: List[str]
    potential_biases: List[str]
    mitigation_strategies: List[str]

    # Deployment
    deployment_environment: str
    monitoring_metrics: List[str]
    update_frequency: str

    def to_markdown(self) -> str:
        """Generate markdown documentation."""
        return f"""
# Model Card: {self.name}

## Overview
- **Version**: {self.version}
- **Owner**: {self.owner}
- **Created**: {self.created_date.strftime('%Y-%m-%d')}

## Description
{self.description}

## Intended Use
### Primary Use Cases
{chr(10).join(f'- {use}' for use in self.primary_use_cases)}

### Out of Scope
{chr(10).join(f'- {use}' for use in self.out_of_scope_uses)}

## Training Data
{self.training_data_description}
- Size: {self.training_data_size:,} samples

## Performance Metrics
{chr(10).join(f'- **{k}**: {v:.4f}' for k, v in self.metrics.items())}

## Known Limitations
{chr(10).join(f'- {lim}' for lim in self.known_limitations)}

## Ethical Considerations
### Potential Biases
{chr(10).join(f'- {bias}' for bias in self.potential_biases)}

### Mitigation Strategies
{chr(10).join(f'- {strat}' for strat in self.mitigation_strategies)}
"""
```

### Audit Trail

```python
@dataclass
class AuditEvent:
    """Single audit event for model governance."""
    timestamp: datetime
    event_type: str  # trained, deployed, predictions, retrained, retired
    model_name: str
    model_version: str
    actor: str  # who triggered the event
    details: Dict[str, Any]

class ModelAuditLog:
    """
    Maintain audit trail for model governance.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.events: List[AuditEvent] = []

    def log_event(
        self,
        event_type: str,
        model_name: str,
        model_version: str,
        actor: str,
        details: Dict = None
    ):
        """Log an audit event."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            model_name=model_name,
            model_version=model_version,
            actor=actor,
            details=details or {}
        )
        self.events.append(event)
        self._persist(event)

    def _persist(self, event: AuditEvent):
        """Persist event to storage."""
        log_file = self.storage_path / f"audit_{datetime.now().strftime('%Y%m')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(event), default=str) + '\n')

    def query(
        self,
        model_name: str = None,
        event_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[AuditEvent]:
        """Query audit events."""
        results = self.events

        if model_name:
            results = [e for e in results if e.model_name == model_name]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if start_date:
            results = [e for e in results if e.timestamp >= start_date]
        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        return results
```

---

## ML Monitoring Tools Comparison

```
┌────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│    Tool        │   Drift     │   Metrics   │   Alerts    │   Cost      │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Evidently      │ ✅ Built-in │ ✅ ML+sys   │ ⚠️ Basic    │ Free/OS     │
│ WhyLabs        │ ✅ Advanced │ ✅ ML-focus │ ✅ Built-in │ Free tier   │
│ Arize          │ ✅ Advanced │ ✅ ML-focus │ ✅ Built-in │ Paid        │
│ Fiddler        │ ✅ Built-in │ ✅ ML-focus │ ✅ Built-in │ Paid        │
│ MLflow         │ ⚠️ Basic    │ ✅ ML-focus │ ❌ Manual   │ Free/OS     │
│ Prometheus     │ ❌ Manual   │ ✅ System   │ ✅ Built-in │ Free/OS     │
│ Datadog        │ ⚠️ Manual   │ ✅ System   │ ✅ Built-in │ Paid        │
└────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘

Recommendation:
- Start: Evidently + Prometheus + Grafana (all free)
- Scale: WhyLabs or Arize for advanced ML monitoring
- Enterprise: Fiddler or Datadog ML Monitoring
```

---

## Best Practices

### 1. Monitor Everything

```
WHAT TO MONITOR
===============

Input Data:
  □ Feature distributions (per feature)
  □ Missing value rates
  □ Outlier rates
  □ Volume/throughput

Model Outputs:
  □ Prediction distribution
  □ Confidence distribution
  □ Prediction latency
  □ Error rates

Performance (when labels available):
  □ Accuracy/F1/AUC (classification)
  □ MAE/RMSE (regression)
  □ Performance by segment

System:
  □ CPU/Memory/GPU utilization
  □ Request latency
  □ Error rates
  □ Queue depths
```

### 2. Set Appropriate Thresholds

```python
# Don't alert on every fluctuation
DRIFT_THRESHOLDS = {
    "psi_warning": 0.1,      # Investigate
    "psi_critical": 0.25,    # Action required

    "accuracy_warning": 0.05,  # 5% drop from baseline
    "accuracy_critical": 0.10, # 10% drop from baseline

    "latency_p95_warning": 200,   # ms
    "latency_p95_critical": 500,  # ms
}

# Use sliding windows to smooth noise
MONITORING_WINDOWS = {
    "latency": "5m",      # Fast-changing
    "accuracy": "1h",     # Slower-changing
    "drift": "1d",        # Slowest-changing
}
```

### 3. Establish Runbooks

```markdown
# Model Degradation Runbook

## Alert: ModelAccuracyDrop

### Severity: Warning (< 85% accuracy)

### Immediate Actions:
1. Check recent prediction volume (unusual traffic?)
2. Check input data drift dashboard
3. Check recent deployments (new model version?)

### Investigation:
1. Compare feature distributions: current vs training
2. Check for concept drift in specific segments
3. Review recent ground truth labels

### Remediation Options:
1. Roll back to previous model version
2. Increase traffic to shadow model for comparison
3. Trigger model retraining pipeline
4. Escalate to ML team if >10% degradation

### Escalation:
- Warning: ML team Slack channel
- Critical: PagerDuty on-call
```

---

## Summary

```
ML MONITORING ESSENTIALS
========================

DRIFT TYPES:
  Data Drift    → Input distribution changed
  Concept Drift → Input-output relationship changed
  Prediction Drift → Output distribution changed

DETECTION METHODS:
  PSI           → Population Stability Index
  KS Test       → Distribution comparison
  JS Divergence → Symmetric distance measure

EXPLAINABILITY:
  SHAP          → Feature contributions (game theory)
  LIME          → Local linear approximations

GOVERNANCE:
  Model Cards   → Documentation for transparency
  Audit Logs    → Track all model events
  Access Control → Who can deploy/modify

TOOLS:
  Prometheus    → Metrics collection
  Grafana       → Visualization
  Evidently     → ML-specific monitoring
  WhyLabs       → Advanced drift detection

BEST PRACTICES:
  ✅ Monitor inputs, outputs, AND performance
  ✅ Set thresholds with baselines
  ✅ Create runbooks for alerts
  ✅ Automate retraining when needed
  ✅ Document everything (model cards)
```

---

## Congratulations!

You've completed Phase 10: DevOps & MLOps! You now have a comprehensive understanding of:
- DevOps fundamentals for ML
- Docker and containerization
- CI/CD pipelines
- Kubernetes for ML workloads
- Advanced K8s (Kubeflow, KServe, Triton)
- MLOps and experiment tracking
- Data versioning and feature stores
- Pipeline orchestration
- Model deployment patterns
- **Monitoring and observability**

---

_Module 52 Complete! Phase 10 Complete!_
_"You can't improve what you can't measure. In ML, you can't trust what you don't monitor."_
