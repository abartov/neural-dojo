# Module 52: Monitoring, Governance & Production Best Practices

**Duration**: 7-8 hours
**Prerequisites**: Module 51 (Model Deployment Patterns)
**Status**: 🟢 Complete

---

## The $569 Million Mistake Nobody Saw Coming

**San Francisco, California. October 2021. 3:14 PM.**

The dashboard showed green. Uptime: 99.99%. Latency: 45ms average. Error rate: 0.001%. By every traditional metric, Zillow's home-buying algorithm was performing flawlessly.

But deep in the numbers, something was wrong.

The model had been trained on years of housing market data. It learned patterns: location, square footage, bedrooms, school districts. It made predictions, and Zillow bought houses based on those predictions. Thousands of them.

Then COVID-19 rewired the housing market. Remote work changed where people wanted to live. Urban flight reversed suburban decline. Interest rates dropped, then spiked. The patterns the model had learned no longer applied—but nobody told the model. It kept predicting. Zillow kept buying.

By the time someone noticed, Zillow had accumulated $569 million in losses. The entire iBuying division was shut down. 2,000 employees lost their jobs. And the model? It never crashed. It never threw an error. It just quietly, confidently, catastrophically, got things wrong.

> "We had dashboards for everything except the one thing that mattered: whether the model was still learning the right thing."
> — An anonymous Zillow engineer, post-mortem interview, 2022

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

Think of ML monitoring like a pilot's instrument panel versus a car dashboard. A car dashboard tells you speed, fuel, and engine temperature—if something breaks, you'll hear it or feel it. A pilot's panel monitors dozens of hidden systems because at 35,000 feet, you can't just "pull over" when something feels wrong. ML models are like aircraft: they can be producing subtly wrong results while all surface metrics look fine. By the time you notice something's wrong, you might already be in a nosedive. You need instruments that monitor what the human eye can't see.

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

Think of drift like changing road conditions for a self-driving car. Data drift is when the road surface changes—maybe you trained on dry asphalt, but now it's rainy and covered with leaves. Concept drift is when the traffic laws change—same roads, same cars, but red now means go. Both require your model to adapt, but detecting them requires watching different signals. Miss them, and your model drives confidently off a cliff.

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

Think of model performance monitoring like tracking a patient's vital signs in an ICU—it's literally a matter of life and death for your ML system. You don't just check temperature once—you monitor it continuously, set alarms for dangerous ranges, and look at trends over time. A fever that spikes briefly is different from one that rises slowly over days. Similarly, model accuracy that drops suddenly (bug? bad deployment?) needs different treatment than accuracy that erodes gradually (drift). The metrics below are your model's vital signs—know what's normal, what's dangerous, and what trends to watch.

> **💡 Did You Know?** Netflix monitors over 200 different metrics for their recommendation models. Their "A/B testing at scale" system evaluates model changes against millions of users simultaneously, catching performance degradation before it affects the broader user base. They estimate that their recommendation system drives 80% of what users watch—making monitoring not just important, but existential to their business.

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

Think of model explainability like a doctor explaining a diagnosis. Saying "you have diabetes" isn't helpful—you need to know *why*: "Your blood sugar is 250, your A1C is 9.5, and you have family history." SHAP and LIME do the same for model predictions. Instead of "loan denied," they tell you "denied because income-to-debt ratio is 0.7 (pushed prediction negative by 0.3), credit score is 580 (pushed negative by 0.2), and account age is 6 months (pushed negative by 0.1)." Now you can act: pay down debt, wait for better credit history, or appeal the decision.

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

Think of alerting like a smoke detector in your house. You don't want it to alarm every time you cook toast (alert fatigue), but you absolutely need it to wake you up during a real fire. The art of ML alerting is calibrating your "smoke detectors" to catch real problems without crying wolf. Too sensitive? Your team ignores alerts and misses the real fire. Not sensitive enough? You're Zillow, discovering you've lost half a billion dollars. Set thresholds based on business impact, not arbitrary statistics.

> **💡 Did You Know?** Google's SRE team (Site Reliability Engineering) pioneered the concept of "error budgets" for alerting. Instead of trying to achieve 100% uptime (impossible), they set acceptable error rates (e.g., 99.9% availability = 8.76 hours downtime/year). As long as you stay within your "budget," you don't alert. This philosophy has been adopted by ML teams for model performance—allowing natural variance while alerting on true degradation.

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

Think of model governance like the FDA approval process for medications. Before a drug reaches patients, it needs documentation of what it's for, who should (and shouldn't) take it, potential side effects, and ongoing monitoring requirements. Model governance is the same for AI: every model needs a "label" explaining its intended use, known limitations, and potential harms. In regulated industries like healthcare and finance, this isn't optional—it's the law. Even in unregulated domains, good governance saves you from deploying a "medication" that turns out to be poison.

> **💡 Did You Know?** The EU AI Act, which went into effect in 2024, requires "high-risk" AI systems (used in hiring, credit scoring, healthcare, etc.) to maintain detailed documentation, undergo third-party audits, and implement continuous monitoring. Companies face fines up to €35 million or 7% of global revenue for non-compliance. Model governance went from "nice to have" to "mandatory" overnight.

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

## Hands-On Exercises

### Exercise 1: Build a Drift Detector

Create a complete drift detection system that monitors a model in production.

**Your task**: Implement a drift monitor that:
1. Accepts baseline (training) data
2. Monitors incoming production data
3. Calculates PSI for each feature
4. Triggers alerts when drift exceeds thresholds

```python
class ProductionDriftMonitor:
    """
    Monitor production data for drift against training baseline.
    """

    def __init__(self, baseline_data: pd.DataFrame, alert_threshold: float = 0.1):
        """
        Initialize with baseline (training) data.

        Args:
            baseline_data: DataFrame with training features
            alert_threshold: PSI threshold for alerts
        """
        self.baseline_data = baseline_data
        self.alert_threshold = alert_threshold
        self.feature_names = baseline_data.columns.tolist()
        self.drift_history = []

    def calculate_psi(self, feature: str, production_data: pd.DataFrame) -> float:
        """Calculate PSI for a single feature."""
        # YOUR CODE HERE
        pass

    def check_drift(self, production_data: pd.DataFrame) -> dict:
        """
        Check all features for drift.

        Returns dict with:
        - feature_psi: PSI for each feature
        - drifted_features: list of features exceeding threshold
        - alert_level: 'none', 'warning', or 'critical'
        """
        # YOUR CODE HERE
        pass

    def generate_report(self) -> str:
        """Generate a human-readable drift report."""
        # YOUR CODE HERE
        pass

# Test your implementation
baseline = pd.DataFrame({
    'age': np.random.normal(35, 10, 10000),
    'income': np.random.normal(60000, 20000, 10000),
    'credit_score': np.random.normal(700, 50, 10000)
})

# Simulate drift: production data is different
production = pd.DataFrame({
    'age': np.random.normal(40, 12, 1000),  # Shifted mean
    'income': np.random.normal(60000, 25000, 1000),  # Increased variance
    'credit_score': np.random.normal(680, 60, 1000)  # Shifted and spread
})

monitor = ProductionDriftMonitor(baseline, alert_threshold=0.1)
results = monitor.check_drift(production)
print(monitor.generate_report())
```

### Exercise 2: Create an ML Monitoring Dashboard

Build a Grafana-compatible monitoring system using Prometheus metrics.

**Your task**: Create a `ModelMonitor` class that:
1. Exports prediction latency histograms
2. Tracks prediction counts by model version
3. Monitors rolling accuracy
4. Alerts on performance degradation

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from datetime import datetime

class ModelMonitor:
    """
    Production ML model monitor with Prometheus metrics.
    """

    def __init__(self, model_name: str, model_version: str, port: int = 8000):
        # Define your metrics here
        # YOUR CODE HERE
        pass

    def record_prediction(
        self,
        input_features: dict,
        prediction: float,
        latency_ms: float
    ):
        """Record a single prediction."""
        # YOUR CODE HERE
        pass

    def record_ground_truth(self, prediction_id: str, actual: float):
        """Record ground truth when it becomes available."""
        # YOUR CODE HERE
        pass

    def get_rolling_accuracy(self, window_size: int = 1000) -> float:
        """Calculate accuracy over recent predictions."""
        # YOUR CODE HERE
        pass

    def check_alerts(self) -> list:
        """Check if any alert conditions are met."""
        # YOUR CODE HERE
        pass

# Test your implementation
monitor = ModelMonitor("fraud_detector", "v2.1.0", port=8000)

# Simulate predictions
for i in range(100):
    latency = np.random.exponential(50)
    monitor.record_prediction(
        input_features={'amount': 100 * i, 'merchant': 'test'},
        prediction=np.random.random(),
        latency_ms=latency
    )

# Check for alerts
alerts = monitor.check_alerts()
for alert in alerts:
    print(f"ALERT: {alert}")
```

### Exercise 3: Implement Model Explainability

Build a prediction explainer that works with any scikit-learn compatible model.

**Your task**: Create a `PredictionExplainer` class that:
1. Accepts any trained model
2. Generates SHAP explanations for predictions
3. Produces human-readable explanations
4. Identifies the top contributing features

```python
import shap

class PredictionExplainer:
    """
    Explain individual predictions using SHAP.
    """

    def __init__(self, model, feature_names: list, background_data: np.ndarray):
        """
        Initialize explainer.

        Args:
            model: Trained model with predict() method
            feature_names: List of feature names
            background_data: Sample of training data for SHAP baseline
        """
        # YOUR CODE HERE
        pass

    def explain_prediction(
        self,
        instance: np.ndarray,
        top_n: int = 5
    ) -> dict:
        """
        Explain a single prediction.

        Returns:
        - prediction: Model output
        - base_value: Expected value (average prediction)
        - top_features: Top N contributing features with SHAP values
        - explanation: Human-readable string
        """
        # YOUR CODE HERE
        pass

    def generate_text_explanation(
        self,
        feature_contributions: dict,
        prediction: float
    ) -> str:
        """Generate natural language explanation."""
        # YOUR CODE HERE
        pass

# Test your implementation
from sklearn.ensemble import RandomForestClassifier

# Train a simple model
X_train = np.random.randn(1000, 5)
y_train = (X_train.sum(axis=1) > 0).astype(int)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Create explainer
explainer = PredictionExplainer(
    model,
    feature_names=['f1', 'f2', 'f3', 'f4', 'f5'],
    background_data=X_train[:100]
)

# Explain a prediction
instance = np.array([[0.5, -1.2, 0.3, 0.8, -0.5]])
explanation = explainer.explain_prediction(instance)
print(explanation['explanation'])
```

### Exercise 4: Build a Model Governance System

Create a complete model registry with governance features.

**Your task**: Implement a `ModelRegistry` that:
1. Tracks model versions and metadata
2. Enforces approval workflows
3. Maintains audit logs
4. Validates models before deployment

```python
from dataclasses import dataclass
from enum import Enum

class ModelStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"

@dataclass
class ModelVersion:
    name: str
    version: str
    status: ModelStatus
    metrics: dict
    created_by: str
    created_at: datetime
    approved_by: str = None
    approved_at: datetime = None

class ModelRegistry:
    """
    Model registry with governance controls.
    """

    def __init__(self, required_metrics: list, approval_required: bool = True):
        """
        Initialize registry.

        Args:
            required_metrics: Metrics that must be provided
            approval_required: Whether approval is needed before deployment
        """
        # YOUR CODE HERE
        pass

    def register_model(
        self,
        name: str,
        version: str,
        model_artifact: any,
        metrics: dict,
        created_by: str
    ) -> ModelVersion:
        """Register a new model version."""
        # YOUR CODE HERE
        pass

    def submit_for_review(self, name: str, version: str) -> bool:
        """Submit model for approval review."""
        # YOUR CODE HERE
        pass

    def approve_model(
        self,
        name: str,
        version: str,
        approved_by: str,
        comments: str = ""
    ) -> bool:
        """Approve a model for deployment."""
        # YOUR CODE HERE
        pass

    def deploy_model(self, name: str, version: str) -> bool:
        """Deploy an approved model."""
        # YOUR CODE HERE
        pass

    def get_audit_log(self, name: str = None) -> list:
        """Get audit trail for models."""
        # YOUR CODE HERE
        pass

# Test your implementation
registry = ModelRegistry(
    required_metrics=['accuracy', 'precision', 'recall'],
    approval_required=True
)

# Register model
version = registry.register_model(
    name="fraud_detector",
    version="v1.0.0",
    model_artifact=model,
    metrics={'accuracy': 0.95, 'precision': 0.92, 'recall': 0.88},
    created_by="data_scientist@company.com"
)

# Try to deploy (should fail - not approved)
try:
    registry.deploy_model("fraud_detector", "v1.0.0")
except ValueError as e:
    print(f"Expected error: {e}")

# Get approval and deploy
registry.submit_for_review("fraud_detector", "v1.0.0")
registry.approve_model("fraud_detector", "v1.0.0", "ml_lead@company.com")
registry.deploy_model("fraud_detector", "v1.0.0")

# View audit log
for event in registry.get_audit_log("fraud_detector"):
    print(event)
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
