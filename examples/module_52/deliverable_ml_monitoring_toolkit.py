#!/usr/bin/env python3
"""
ML Monitoring Toolkit - Module 52 Deliverable

A comprehensive toolkit for monitoring ML models in production:
- Drift detection (data, concept, prediction)
- Performance monitoring with sliding windows
- Model explainability (SHAP-like feature importance)
- Alerting system with configurable thresholds
- Model governance (model cards, audit trails)

Usage:
    python deliverable_ml_monitoring_toolkit.py demo1  # Drift detection
    python deliverable_ml_monitoring_toolkit.py demo2  # Performance monitoring
    python deliverable_ml_monitoring_toolkit.py demo3  # Model explainability
    python deliverable_ml_monitoring_toolkit.py demo4  # Alerting system
    python deliverable_ml_monitoring_toolkit.py demo5  # Model governance

Author: Neural Dojo
Module: 52 - Monitoring & Observability
"""

import json
import math
import random
import sys
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from collections import defaultdict


# =============================================================================
# Configuration
# =============================================================================

STORAGE_DIR = Path(".ml_monitoring_toolkit")
STORAGE_DIR.mkdir(exist_ok=True)


class DriftType(Enum):
    """Types of drift in ML systems."""
    DATA = "data"           # Input feature distribution changes
    CONCEPT = "concept"     # Relationship between X and Y changes
    PREDICTION = "prediction"  # Model output distribution changes


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class DriftResult:
    """Result of drift detection analysis."""
    feature_name: str
    drift_type: str
    metric_name: str
    metric_value: float
    threshold: float
    is_drifted: bool
    reference_stats: Dict[str, float]
    current_stats: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PerformanceMetric:
    """A single performance measurement."""
    metric_name: str
    value: float
    timestamp: str
    model_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PerformanceWindow:
    """Sliding window of performance metrics."""
    window_size: int
    metrics: List[PerformanceMetric] = field(default_factory=list)

    def add(self, metric: PerformanceMetric) -> None:
        self.metrics.append(metric)
        if len(self.metrics) > self.window_size:
            self.metrics = self.metrics[-self.window_size:]

    def mean(self) -> float:
        if not self.metrics:
            return 0.0
        return sum(m.value for m in self.metrics) / len(self.metrics)

    def std(self) -> float:
        if len(self.metrics) < 2:
            return 0.0
        mean = self.mean()
        variance = sum((m.value - mean) ** 2 for m in self.metrics) / len(self.metrics)
        return math.sqrt(variance)

    def trend(self) -> str:
        """Calculate trend direction."""
        if len(self.metrics) < 3:
            return "stable"
        recent = [m.value for m in self.metrics[-3:]]
        if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
            return "improving"
        elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
            return "degrading"
        return "stable"


@dataclass
class FeatureImportance:
    """Feature importance from explainability analysis."""
    feature_name: str
    importance_score: float
    direction: str  # positive or negative
    confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Alert:
    """An alert from the monitoring system."""
    alert_id: str
    title: str
    description: str
    severity: str
    status: str
    source: str
    metric_name: str
    metric_value: float
    threshold: float
    created_at: str
    updated_at: str
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ModelCard:
    """Model documentation card for governance."""
    model_id: str
    model_name: str
    version: str
    description: str
    intended_use: str
    limitations: str
    training_data: str
    evaluation_metrics: Dict[str, float]
    ethical_considerations: str
    created_by: str
    created_at: str
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AuditLogEntry:
    """Audit log entry for model governance."""
    entry_id: str
    timestamp: str
    action: str
    actor: str
    model_id: str
    model_version: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# Drift Detection
# =============================================================================

class DriftDetector:
    """
    Detects drift in ML model inputs and outputs.

    Implements multiple statistical tests:
    - Population Stability Index (PSI)
    - Kolmogorov-Smirnov Test
    - Jensen-Shannon Divergence
    """

    def __init__(self):
        self.reference_distributions: Dict[str, List[float]] = {}
        self.drift_history: List[DriftResult] = []

    def set_reference(self, feature_name: str, values: List[float]) -> None:
        """Set reference distribution for a feature."""
        self.reference_distributions[feature_name] = values
        print(f"  📊 Reference set for '{feature_name}': {len(values)} samples")

    def calculate_psi(
        self,
        reference: List[float],
        current: List[float],
        num_bins: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI).

        PSI measures how much the distribution has shifted:
        - PSI < 0.1: No significant change
        - 0.1 <= PSI < 0.2: Moderate change, monitor closely
        - PSI >= 0.2: Significant change, investigate
        """
        # Create bins from reference data
        min_val = min(min(reference), min(current))
        max_val = max(max(reference), max(current))
        bin_edges = [min_val + i * (max_val - min_val) / num_bins
                     for i in range(num_bins + 1)]

        def get_bin_proportions(data: List[float]) -> List[float]:
            counts = [0] * num_bins
            for val in data:
                for i in range(num_bins):
                    if bin_edges[i] <= val < bin_edges[i + 1]:
                        counts[i] += 1
                        break
                else:
                    counts[-1] += 1  # Last bin includes max value

            # Add small epsilon to avoid division by zero
            total = len(data)
            return [(c + 0.0001) / (total + 0.001) for c in counts]

        ref_props = get_bin_proportions(reference)
        cur_props = get_bin_proportions(current)

        # Calculate PSI
        psi = 0.0
        for ref_p, cur_p in zip(ref_props, cur_props):
            psi += (cur_p - ref_p) * math.log(cur_p / ref_p)

        return psi

    def calculate_ks_statistic(
        self,
        reference: List[float],
        current: List[float]
    ) -> Tuple[float, float]:
        """
        Calculate Kolmogorov-Smirnov statistic.

        Returns (statistic, p-value approximation).
        """
        # Sort both distributions
        ref_sorted = sorted(reference)
        cur_sorted = sorted(current)

        # Create combined sorted list
        all_values = sorted(set(ref_sorted + cur_sorted))

        # Calculate empirical CDFs
        def ecdf_at(data: List[float], x: float) -> float:
            return sum(1 for v in data if v <= x) / len(data)

        # Find maximum difference
        max_diff = 0.0
        for val in all_values:
            diff = abs(ecdf_at(ref_sorted, val) - ecdf_at(cur_sorted, val))
            max_diff = max(max_diff, diff)

        # Approximate p-value using asymptotic distribution
        n = len(reference)
        m = len(current)
        en = math.sqrt(n * m / (n + m))
        p_value = 2 * math.exp(-2 * (en * max_diff) ** 2)
        p_value = min(1.0, max(0.0, p_value))

        return max_diff, p_value

    def calculate_js_divergence(
        self,
        reference: List[float],
        current: List[float],
        num_bins: int = 10
    ) -> float:
        """
        Calculate Jensen-Shannon Divergence.

        JS divergence is symmetric and bounded [0, 1]:
        - 0: Identical distributions
        - 1: Completely different distributions
        """
        min_val = min(min(reference), min(current))
        max_val = max(max(reference), max(current))
        bin_edges = [min_val + i * (max_val - min_val) / num_bins
                     for i in range(num_bins + 1)]

        def get_distribution(data: List[float]) -> List[float]:
            counts = [0] * num_bins
            for val in data:
                for i in range(num_bins):
                    if bin_edges[i] <= val < bin_edges[i + 1]:
                        counts[i] += 1
                        break
                else:
                    counts[-1] += 1
            total = sum(counts)
            return [(c + 0.0001) / (total + 0.001) for c in counts]

        p = get_distribution(reference)
        q = get_distribution(current)
        m = [(pi + qi) / 2 for pi, qi in zip(p, q)]

        def kl_divergence(a: List[float], b: List[float]) -> float:
            return sum(ai * math.log(ai / bi) for ai, bi in zip(a, b) if ai > 0)

        js = 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)
        return js

    def detect_drift(
        self,
        feature_name: str,
        current_values: List[float],
        method: str = "psi",
        threshold: float = 0.2
    ) -> DriftResult:
        """Detect drift for a specific feature."""
        if feature_name not in self.reference_distributions:
            raise ValueError(f"No reference distribution for '{feature_name}'")

        reference = self.reference_distributions[feature_name]

        # Calculate statistics
        ref_mean = sum(reference) / len(reference)
        ref_std = math.sqrt(sum((x - ref_mean)**2 for x in reference) / len(reference))
        cur_mean = sum(current_values) / len(current_values)
        cur_std = math.sqrt(sum((x - cur_mean)**2 for x in current_values) / len(current_values))

        # Calculate drift metric
        if method == "psi":
            metric_value = self.calculate_psi(reference, current_values)
        elif method == "ks":
            metric_value, _ = self.calculate_ks_statistic(reference, current_values)
        elif method == "js":
            metric_value = self.calculate_js_divergence(reference, current_values)
        else:
            raise ValueError(f"Unknown method: {method}")

        result = DriftResult(
            feature_name=feature_name,
            drift_type=DriftType.DATA.value,
            metric_name=method.upper(),
            metric_value=round(metric_value, 4),
            threshold=threshold,
            is_drifted=metric_value >= threshold,
            reference_stats={"mean": round(ref_mean, 4), "std": round(ref_std, 4)},
            current_stats={"mean": round(cur_mean, 4), "std": round(cur_std, 4)}
        )

        self.drift_history.append(result)
        return result

    def get_drift_report(self) -> Dict[str, Any]:
        """Generate comprehensive drift report."""
        if not self.drift_history:
            return {"status": "no_data", "drifted_features": []}

        drifted = [r for r in self.drift_history if r.is_drifted]

        return {
            "status": "drift_detected" if drifted else "healthy",
            "total_checks": len(self.drift_history),
            "drifted_count": len(drifted),
            "drifted_features": [r.feature_name for r in drifted],
            "results": [r.to_dict() for r in self.drift_history]
        }


# =============================================================================
# Performance Monitoring
# =============================================================================

class PerformanceMonitor:
    """
    Monitors model performance over time.

    Features:
    - Sliding window statistics
    - Trend detection
    - Anomaly detection
    - SLA tracking
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics: Dict[str, PerformanceWindow] = {}
        self.sla_thresholds: Dict[str, Dict[str, float]] = {}

    def set_sla(
        self,
        metric_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> None:
        """Set SLA thresholds for a metric."""
        self.sla_thresholds[metric_name] = {
            "min": min_value,
            "max": max_value
        }
        print(f"  📋 SLA set for '{metric_name}': min={min_value}, max={max_value}")

    def record(
        self,
        metric_name: str,
        value: float,
        model_version: str = "v1.0",
        metadata: Optional[Dict] = None
    ) -> PerformanceMetric:
        """Record a performance metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = PerformanceWindow(self.window_size)

        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now().isoformat(),
            model_version=model_version,
            metadata=metadata or {}
        )

        self.metrics[metric_name].add(metric)
        return metric

    def get_statistics(self, metric_name: str) -> Dict[str, Any]:
        """Get statistics for a metric."""
        if metric_name not in self.metrics:
            return {"status": "no_data"}

        window = self.metrics[metric_name]
        values = [m.value for m in window.metrics]

        return {
            "metric_name": metric_name,
            "count": len(values),
            "mean": round(window.mean(), 4),
            "std": round(window.std(), 4),
            "min": round(min(values), 4) if values else None,
            "max": round(max(values), 4) if values else None,
            "trend": window.trend(),
            "latest": round(values[-1], 4) if values else None
        }

    def check_sla(self, metric_name: str) -> Dict[str, Any]:
        """Check if metric is meeting SLA."""
        if metric_name not in self.sla_thresholds:
            return {"status": "no_sla_defined"}

        if metric_name not in self.metrics:
            return {"status": "no_data"}

        sla = self.sla_thresholds[metric_name]
        stats = self.get_statistics(metric_name)
        mean = stats["mean"]

        violations = []
        if sla["min"] is not None and mean < sla["min"]:
            violations.append(f"Below minimum ({mean} < {sla['min']})")
        if sla["max"] is not None and mean > sla["max"]:
            violations.append(f"Above maximum ({mean} > {sla['max']})")

        return {
            "metric_name": metric_name,
            "sla_met": len(violations) == 0,
            "violations": violations,
            "current_mean": mean,
            "thresholds": sla
        }

    def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        num_std: float = 3.0
    ) -> Dict[str, Any]:
        """Detect if a value is anomalous using z-score."""
        if metric_name not in self.metrics:
            return {"is_anomaly": False, "reason": "insufficient_data"}

        window = self.metrics[metric_name]
        if len(window.metrics) < 10:
            return {"is_anomaly": False, "reason": "insufficient_data"}

        mean = window.mean()
        std = window.std()

        if std == 0:
            is_anomaly = value != mean
            z_score = float('inf') if is_anomaly else 0
        else:
            z_score = abs(value - mean) / std
            is_anomaly = z_score > num_std

        return {
            "is_anomaly": is_anomaly,
            "value": round(value, 4),
            "z_score": round(z_score, 4),
            "threshold": num_std,
            "mean": round(mean, 4),
            "std": round(std, 4)
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """Generate dashboard summary."""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "sla_status": {}
        }

        for metric_name in self.metrics:
            dashboard["metrics"][metric_name] = self.get_statistics(metric_name)
            if metric_name in self.sla_thresholds:
                dashboard["sla_status"][metric_name] = self.check_sla(metric_name)

        return dashboard


# =============================================================================
# Model Explainability
# =============================================================================

class ExplainabilityEngine:
    """
    Provides model explainability through feature importance analysis.

    Simulates SHAP-like and LIME-like explanations for demonstration.
    In production, integrate with actual SHAP/LIME libraries.
    """

    def __init__(self):
        self.feature_names: List[str] = []
        self.explanation_cache: Dict[str, List[FeatureImportance]] = {}

    def set_features(self, feature_names: List[str]) -> None:
        """Set feature names for the model."""
        self.feature_names = feature_names
        print(f"  🔍 Features registered: {feature_names}")

    def explain_prediction(
        self,
        input_values: Dict[str, float],
        prediction: float,
        method: str = "shap"
    ) -> List[FeatureImportance]:
        """
        Generate explanation for a single prediction.

        This is a simulation for demonstration purposes.
        In production, use actual SHAP or LIME libraries.
        """
        explanations = []

        # Simulate feature importance calculation
        # In reality, this would use perturbation-based methods
        total_magnitude = sum(abs(v) for v in input_values.values()) + 0.001

        for feature, value in input_values.items():
            # Simulate importance score
            base_importance = abs(value) / total_magnitude
            # Add some realistic variation
            noise = random.uniform(-0.05, 0.05)
            importance = max(0, min(1, base_importance + noise))

            # Determine direction of contribution
            direction = "positive" if value * prediction > 0 else "negative"

            # Confidence based on magnitude
            confidence = min(0.95, 0.5 + abs(value) / (2 * total_magnitude))

            explanations.append(FeatureImportance(
                feature_name=feature,
                importance_score=round(importance, 4),
                direction=direction,
                confidence=round(confidence, 4)
            ))

        # Sort by importance
        explanations.sort(key=lambda x: x.importance_score, reverse=True)

        # Cache for later retrieval
        cache_key = hashlib.md5(str(input_values).encode()).hexdigest()[:8]
        self.explanation_cache[cache_key] = explanations

        return explanations

    def get_global_importance(
        self,
        sample_explanations: List[List[FeatureImportance]]
    ) -> Dict[str, float]:
        """Calculate global feature importance from multiple explanations."""
        importance_sums: Dict[str, List[float]] = defaultdict(list)

        for explanation in sample_explanations:
            for feat_imp in explanation:
                importance_sums[feat_imp.feature_name].append(feat_imp.importance_score)

        global_importance = {}
        for feature, scores in importance_sums.items():
            global_importance[feature] = round(sum(scores) / len(scores), 4)

        return dict(sorted(global_importance.items(), key=lambda x: x[1], reverse=True))

    def format_explanation(
        self,
        explanations: List[FeatureImportance],
        top_k: int = 5
    ) -> str:
        """Format explanation as readable text."""
        lines = ["Top contributing features:"]
        for i, exp in enumerate(explanations[:top_k], 1):
            arrow = "↑" if exp.direction == "positive" else "↓"
            lines.append(
                f"  {i}. {exp.feature_name}: {exp.importance_score:.4f} {arrow} "
                f"(confidence: {exp.confidence:.2%})"
            )
        return "\n".join(lines)


# =============================================================================
# Alerting System
# =============================================================================

class AlertManager:
    """
    Manages alerts from the monitoring system.

    Features:
    - Configurable thresholds
    - Alert aggregation (avoid alert storms)
    - Severity escalation
    - Alert lifecycle management
    """

    def __init__(self):
        self.alerts: List[Alert] = []
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.alert_rules: Dict[str, Callable] = {}
        self.cooldown_minutes: int = 5
        self.last_alert_time: Dict[str, datetime] = {}

    def add_threshold(
        self,
        metric_name: str,
        warning_threshold: float,
        critical_threshold: float,
        comparison: str = "greater"  # greater or less
    ) -> None:
        """Add alert threshold for a metric."""
        self.thresholds[metric_name] = {
            "warning": warning_threshold,
            "critical": critical_threshold,
            "comparison": comparison
        }
        print(f"  🔔 Threshold set for '{metric_name}': "
              f"warning={warning_threshold}, critical={critical_threshold}")

    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        return f"ALR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    def _check_cooldown(self, metric_name: str) -> bool:
        """Check if metric is in cooldown period."""
        if metric_name not in self.last_alert_time:
            return False

        elapsed = datetime.now() - self.last_alert_time[metric_name]
        return elapsed.total_seconds() < self.cooldown_minutes * 60

    def check_and_alert(
        self,
        metric_name: str,
        value: float,
        source: str = "monitoring_system"
    ) -> Optional[Alert]:
        """Check value against thresholds and create alert if needed."""
        if metric_name not in self.thresholds:
            return None

        # Check cooldown
        if self._check_cooldown(metric_name):
            return None

        threshold = self.thresholds[metric_name]
        comparison = threshold["comparison"]

        # Determine severity
        severity = None
        exceeded_threshold = None

        if comparison == "greater":
            if value >= threshold["critical"]:
                severity = AlertSeverity.CRITICAL
                exceeded_threshold = threshold["critical"]
            elif value >= threshold["warning"]:
                severity = AlertSeverity.WARNING
                exceeded_threshold = threshold["warning"]
        else:  # less
            if value <= threshold["critical"]:
                severity = AlertSeverity.CRITICAL
                exceeded_threshold = threshold["critical"]
            elif value <= threshold["warning"]:
                severity = AlertSeverity.WARNING
                exceeded_threshold = threshold["warning"]

        if severity is None:
            return None

        # Create alert
        now = datetime.now()
        alert = Alert(
            alert_id=self._generate_alert_id(),
            title=f"{metric_name} {severity.value.upper()}",
            description=f"{metric_name} value {value} exceeded {severity.value} threshold {exceeded_threshold}",
            severity=severity.value,
            status=AlertStatus.OPEN.value,
            source=source,
            metric_name=metric_name,
            metric_value=value,
            threshold=exceeded_threshold,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )

        self.alerts.append(alert)
        self.last_alert_time[metric_name] = now

        return alert

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id and alert.status == AlertStatus.OPEN.value:
                alert.status = AlertStatus.ACKNOWLEDGED.value
                alert.acknowledged_by = acknowledged_by
                alert.updated_at = datetime.now().isoformat()
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.RESOLVED.value
                alert.resolved_at = datetime.now().isoformat()
                alert.updated_at = datetime.now().isoformat()
                return True
        return False

    def get_open_alerts(self) -> List[Alert]:
        """Get all open alerts."""
        return [a for a in self.alerts if a.status == AlertStatus.OPEN.value]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of all alerts."""
        summary = {
            "total": len(self.alerts),
            "by_status": defaultdict(int),
            "by_severity": defaultdict(int),
            "open_alerts": []
        }

        for alert in self.alerts:
            summary["by_status"][alert.status] += 1
            summary["by_severity"][alert.severity] += 1

        summary["open_alerts"] = [a.to_dict() for a in self.get_open_alerts()]
        summary["by_status"] = dict(summary["by_status"])
        summary["by_severity"] = dict(summary["by_severity"])

        return summary


# =============================================================================
# Model Governance
# =============================================================================

class GovernanceManager:
    """
    Manages model governance and compliance.

    Features:
    - Model cards for documentation
    - Approval workflows
    - Audit trail
    - Version lineage
    """

    def __init__(self):
        self.model_cards: Dict[str, ModelCard] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.storage_path = STORAGE_DIR / "governance.json"

    def _generate_entry_id(self) -> str:
        """Generate unique audit entry ID."""
        return f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    def _log_action(
        self,
        action: str,
        actor: str,
        model_id: str,
        model_version: str,
        details: Dict[str, Any]
    ) -> AuditLogEntry:
        """Create audit log entry."""
        entry = AuditLogEntry(
            entry_id=self._generate_entry_id(),
            timestamp=datetime.now().isoformat(),
            action=action,
            actor=actor,
            model_id=model_id,
            model_version=model_version,
            details=details
        )
        self.audit_log.append(entry)
        return entry

    def create_model_card(
        self,
        model_id: str,
        model_name: str,
        version: str,
        description: str,
        intended_use: str,
        limitations: str,
        training_data: str,
        evaluation_metrics: Dict[str, float],
        ethical_considerations: str,
        created_by: str
    ) -> ModelCard:
        """Create a model card for documentation."""
        card = ModelCard(
            model_id=model_id,
            model_name=model_name,
            version=version,
            description=description,
            intended_use=intended_use,
            limitations=limitations,
            training_data=training_data,
            evaluation_metrics=evaluation_metrics,
            ethical_considerations=ethical_considerations,
            created_by=created_by,
            created_at=datetime.now().isoformat()
        )

        self.model_cards[model_id] = card
        self._log_action(
            action="model_card_created",
            actor=created_by,
            model_id=model_id,
            model_version=version,
            details={"model_name": model_name}
        )

        return card

    def approve_model(
        self,
        model_id: str,
        approved_by: str,
        approval_notes: str = ""
    ) -> bool:
        """Approve a model for production use."""
        if model_id not in self.model_cards:
            return False

        card = self.model_cards[model_id]
        card.approved_by = approved_by
        card.approved_at = datetime.now().isoformat()

        self._log_action(
            action="model_approved",
            actor=approved_by,
            model_id=model_id,
            model_version=card.version,
            details={"approval_notes": approval_notes}
        )

        return True

    def record_deployment(
        self,
        model_id: str,
        model_version: str,
        deployed_by: str,
        environment: str,
        deployment_config: Dict[str, Any]
    ) -> AuditLogEntry:
        """Record model deployment for audit trail."""
        return self._log_action(
            action="model_deployed",
            actor=deployed_by,
            model_id=model_id,
            model_version=model_version,
            details={
                "environment": environment,
                "config": deployment_config
            }
        )

    def record_prediction(
        self,
        model_id: str,
        model_version: str,
        input_hash: str,
        prediction: Any,
        request_id: str
    ) -> AuditLogEntry:
        """Record prediction for audit trail (high-value predictions)."""
        return self._log_action(
            action="prediction_logged",
            actor="system",
            model_id=model_id,
            model_version=model_version,
            details={
                "input_hash": input_hash,
                "prediction": prediction,
                "request_id": request_id
            }
        )

    def get_audit_trail(
        self,
        model_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 50
    ) -> List[AuditLogEntry]:
        """Get filtered audit trail."""
        results = self.audit_log

        if model_id:
            results = [e for e in results if e.model_id == model_id]
        if action:
            results = [e for e in results if e.action == action]

        return results[-limit:]

    def get_compliance_report(self, model_id: str) -> Dict[str, Any]:
        """Generate compliance report for a model."""
        if model_id not in self.model_cards:
            return {"status": "model_not_found"}

        card = self.model_cards[model_id]
        audit_entries = [e for e in self.audit_log if e.model_id == model_id]

        # Check compliance criteria
        checks = {
            "has_model_card": True,
            "has_description": bool(card.description),
            "has_intended_use": bool(card.intended_use),
            "has_limitations": bool(card.limitations),
            "has_training_data_doc": bool(card.training_data),
            "has_eval_metrics": bool(card.evaluation_metrics),
            "has_ethical_considerations": bool(card.ethical_considerations),
            "is_approved": card.approved_by is not None,
            "has_audit_trail": len(audit_entries) > 0
        }

        compliance_score = sum(checks.values()) / len(checks) * 100

        return {
            "model_id": model_id,
            "model_name": card.model_name,
            "version": card.version,
            "compliance_score": round(compliance_score, 1),
            "checks": checks,
            "approved_by": card.approved_by,
            "approved_at": card.approved_at,
            "audit_entries_count": len(audit_entries)
        }

    def save(self) -> None:
        """Save governance data to disk."""
        data = {
            "model_cards": {k: v.to_dict() for k, v in self.model_cards.items()},
            "audit_log": [e.to_dict() for e in self.audit_log]
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  💾 Governance data saved to {self.storage_path}")

    def load(self) -> bool:
        """Load governance data from disk."""
        if not self.storage_path.exists():
            return False

        with open(self.storage_path, 'r') as f:
            data = json.load(f)

        # Reconstruct model cards
        for model_id, card_dict in data.get("model_cards", {}).items():
            self.model_cards[model_id] = ModelCard(**card_dict)

        # Reconstruct audit log
        for entry_dict in data.get("audit_log", []):
            self.audit_log.append(AuditLogEntry(**entry_dict))

        return True


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_drift_detection():
    """
    Demo 1: Drift Detection

    Demonstrates how to detect data drift using multiple statistical methods.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: Drift Detection")
    print("=" * 70)

    detector = DriftDetector()

    # Create reference distribution (training data characteristics)
    print("\n📊 Setting up reference distributions...")
    random.seed(42)

    # Normal distribution for 'age' feature
    age_reference = [random.gauss(35, 10) for _ in range(1000)]
    detector.set_reference("age", age_reference)

    # Normal distribution for 'income' feature
    income_reference = [random.gauss(50000, 15000) for _ in range(1000)]
    detector.set_reference("income", income_reference)

    # Uniform distribution for 'score' feature
    score_reference = [random.uniform(0, 100) for _ in range(1000)]
    detector.set_reference("score", score_reference)

    # Scenario 1: No drift (similar to reference)
    print("\n" + "-" * 40)
    print("Scenario 1: No Drift Expected")
    print("-" * 40)

    age_current_stable = [random.gauss(35, 10) for _ in range(500)]
    result = detector.detect_drift("age", age_current_stable, method="psi", threshold=0.2)
    print(f"\n  Feature: {result.feature_name}")
    print(f"  PSI Value: {result.metric_value}")
    print(f"  Threshold: {result.threshold}")
    print(f"  Drifted: {'❌ YES' if result.is_drifted else '✅ NO'}")
    print(f"  Reference: mean={result.reference_stats['mean']}, std={result.reference_stats['std']}")
    print(f"  Current: mean={result.current_stats['mean']}, std={result.current_stats['std']}")

    # Scenario 2: Mean shift (drift expected)
    print("\n" + "-" * 40)
    print("Scenario 2: Mean Shift (Drift Expected)")
    print("-" * 40)

    age_current_shifted = [random.gauss(45, 10) for _ in range(500)]  # Mean shifted from 35 to 45
    result = detector.detect_drift("age", age_current_shifted, method="psi", threshold=0.2)
    print(f"\n  Feature: {result.feature_name}")
    print(f"  PSI Value: {result.metric_value}")
    print(f"  Threshold: {result.threshold}")
    print(f"  Drifted: {'❌ YES' if result.is_drifted else '✅ NO'}")
    print(f"  Reference: mean={result.reference_stats['mean']}, std={result.reference_stats['std']}")
    print(f"  Current: mean={result.current_stats['mean']}, std={result.current_stats['std']}")

    # Scenario 3: Compare different methods
    print("\n" + "-" * 40)
    print("Scenario 3: Comparing Detection Methods")
    print("-" * 40)

    income_shifted = [random.gauss(70000, 15000) for _ in range(500)]  # Shifted by +20k

    print("\n  Testing income feature with different methods:")
    for method in ["psi", "ks", "js"]:
        result = detector.detect_drift("income", income_shifted, method=method, threshold=0.2)
        print(f"    {method.upper()}: {result.metric_value:.4f} - "
              f"{'❌ DRIFTED' if result.is_drifted else '✅ STABLE'}")

    # Generate drift report
    print("\n" + "-" * 40)
    print("📋 Drift Report Summary")
    print("-" * 40)
    report = detector.get_drift_report()
    print(f"\n  Status: {report['status']}")
    print(f"  Total Checks: {report['total_checks']}")
    print(f"  Drifted Features: {report['drifted_count']}")
    if report['drifted_features']:
        print(f"  Features with Drift: {', '.join(report['drifted_features'])}")

    print("\n✅ Demo 1 Complete: Drift detection with PSI, KS, and JS divergence")


def demo_2_performance_monitoring():
    """
    Demo 2: Performance Monitoring

    Demonstrates sliding window performance tracking, SLA monitoring,
    and anomaly detection.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Performance Monitoring")
    print("=" * 70)

    monitor = PerformanceMonitor(window_size=50)

    # Set SLA thresholds
    print("\n📋 Setting SLA Thresholds...")
    monitor.set_sla("accuracy", min_value=0.85)
    monitor.set_sla("latency_ms", max_value=100)
    monitor.set_sla("throughput_qps", min_value=500)

    # Simulate performance metrics over time
    print("\n📊 Recording performance metrics...")
    random.seed(42)

    # Good performance period
    print("\n  Phase 1: Healthy performance")
    for i in range(30):
        monitor.record("accuracy", 0.92 + random.uniform(-0.02, 0.02))
        monitor.record("latency_ms", 45 + random.uniform(-10, 10))
        monitor.record("throughput_qps", 750 + random.uniform(-50, 50))

    # Degradation period
    print("  Phase 2: Performance degradation")
    for i in range(20):
        # Accuracy drops, latency increases
        monitor.record("accuracy", 0.85 + random.uniform(-0.05, 0.02))
        monitor.record("latency_ms", 80 + random.uniform(-5, 20))
        monitor.record("throughput_qps", 550 + random.uniform(-100, 50))

    # Get statistics
    print("\n" + "-" * 40)
    print("📈 Current Statistics")
    print("-" * 40)

    for metric in ["accuracy", "latency_ms", "throughput_qps"]:
        stats = monitor.get_statistics(metric)
        print(f"\n  {metric}:")
        print(f"    Mean: {stats['mean']}")
        print(f"    Std: {stats['std']}")
        print(f"    Min: {stats['min']} / Max: {stats['max']}")
        print(f"    Trend: {stats['trend']}")
        print(f"    Latest: {stats['latest']}")

    # Check SLA compliance
    print("\n" + "-" * 40)
    print("📋 SLA Compliance Check")
    print("-" * 40)

    for metric in ["accuracy", "latency_ms", "throughput_qps"]:
        sla_result = monitor.check_sla(metric)
        status = "✅ MET" if sla_result['sla_met'] else "❌ VIOLATED"
        print(f"\n  {metric}: {status}")
        print(f"    Current Mean: {sla_result['current_mean']}")
        print(f"    Thresholds: {sla_result['thresholds']}")
        if sla_result['violations']:
            for v in sla_result['violations']:
                print(f"    ⚠️ {v}")

    # Anomaly detection
    print("\n" + "-" * 40)
    print("🔍 Anomaly Detection")
    print("-" * 40)

    test_values = [
        ("accuracy", 0.95, "slightly high"),
        ("accuracy", 0.60, "very low - anomaly expected"),
        ("latency_ms", 45, "normal"),
        ("latency_ms", 250, "very high - anomaly expected"),
    ]

    for metric, value, description in test_values:
        result = monitor.detect_anomaly(metric, value)
        status = "⚠️ ANOMALY" if result['is_anomaly'] else "✅ Normal"
        print(f"\n  {metric} = {value} ({description})")
        print(f"    Status: {status}")
        print(f"    Z-Score: {result.get('z_score', 'N/A')}")

    # Dashboard
    print("\n" + "-" * 40)
    print("📊 Dashboard Summary")
    print("-" * 40)
    dashboard = monitor.get_dashboard()
    print(f"\n  Timestamp: {dashboard['timestamp'][:19]}")
    print(f"  Metrics Tracked: {len(dashboard['metrics'])}")
    print(f"  SLAs Defined: {len(dashboard['sla_status'])}")

    print("\n✅ Demo 2 Complete: Performance monitoring with SLA tracking")


def demo_3_explainability():
    """
    Demo 3: Model Explainability

    Demonstrates feature importance analysis similar to SHAP/LIME.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Model Explainability")
    print("=" * 70)

    explainer = ExplainabilityEngine()

    # Set up features
    print("\n🔍 Setting up model features...")
    features = ["age", "income", "credit_score", "debt_ratio", "employment_years"]
    explainer.set_features(features)

    # Explain individual predictions
    print("\n" + "-" * 40)
    print("Individual Prediction Explanations")
    print("-" * 40)

    # Case 1: High-risk prediction
    print("\n  📌 Case 1: High-Risk Customer (Prediction: 0.85)")
    input_1 = {
        "age": 23,
        "income": 35000,
        "credit_score": 580,
        "debt_ratio": 0.65,
        "employment_years": 1
    }

    exp_1 = explainer.explain_prediction(input_1, prediction=0.85, method="shap")
    print(f"\n  Input: {input_1}")
    print(f"\n  {explainer.format_explanation(exp_1)}")

    # Case 2: Low-risk prediction
    print("\n  📌 Case 2: Low-Risk Customer (Prediction: 0.15)")
    input_2 = {
        "age": 45,
        "income": 120000,
        "credit_score": 780,
        "debt_ratio": 0.20,
        "employment_years": 15
    }

    exp_2 = explainer.explain_prediction(input_2, prediction=0.15, method="shap")
    print(f"\n  Input: {input_2}")
    print(f"\n  {explainer.format_explanation(exp_2)}")

    # Case 3: Borderline case
    print("\n  📌 Case 3: Borderline Customer (Prediction: 0.52)")
    input_3 = {
        "age": 35,
        "income": 65000,
        "credit_score": 680,
        "debt_ratio": 0.40,
        "employment_years": 5
    }

    exp_3 = explainer.explain_prediction(input_3, prediction=0.52, method="shap")
    print(f"\n  Input: {input_3}")
    print(f"\n  {explainer.format_explanation(exp_3)}")

    # Global feature importance
    print("\n" + "-" * 40)
    print("📊 Global Feature Importance")
    print("-" * 40)

    # Generate more sample explanations
    random.seed(42)
    sample_explanations = [exp_1, exp_2, exp_3]
    for _ in range(7):
        random_input = {
            "age": random.randint(20, 70),
            "income": random.randint(25000, 200000),
            "credit_score": random.randint(500, 850),
            "debt_ratio": random.uniform(0.1, 0.8),
            "employment_years": random.randint(0, 30)
        }
        exp = explainer.explain_prediction(random_input, prediction=random.uniform(0, 1))
        sample_explanations.append(exp)

    global_importance = explainer.get_global_importance(sample_explanations)

    print("\n  Average importance across all predictions:")
    for feature, importance in global_importance.items():
        bar = "█" * int(importance * 50)
        print(f"    {feature:20s}: {importance:.4f} {bar}")

    print("\n✅ Demo 3 Complete: Model explainability with feature importance")


def demo_4_alerting():
    """
    Demo 4: Alerting System

    Demonstrates threshold-based alerting, alert lifecycle management,
    and alert aggregation.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Alerting System")
    print("=" * 70)

    alert_manager = AlertManager()
    alert_manager.cooldown_minutes = 0  # Disable cooldown for demo

    # Set up alert thresholds
    print("\n🔔 Setting up alert thresholds...")
    alert_manager.add_threshold("accuracy", warning_threshold=0.85, critical_threshold=0.80, comparison="less")
    alert_manager.add_threshold("latency_p99", warning_threshold=200, critical_threshold=500, comparison="greater")
    alert_manager.add_threshold("error_rate", warning_threshold=0.05, critical_threshold=0.10, comparison="greater")

    # Simulate metric values and generate alerts
    print("\n" + "-" * 40)
    print("Simulating Metric Values")
    print("-" * 40)

    test_scenarios = [
        ("accuracy", 0.92, "healthy"),
        ("accuracy", 0.83, "warning level"),
        ("accuracy", 0.75, "critical level"),
        ("latency_p99", 150, "healthy"),
        ("latency_p99", 250, "warning level"),
        ("latency_p99", 600, "critical level"),
        ("error_rate", 0.02, "healthy"),
        ("error_rate", 0.07, "warning level"),
    ]

    created_alerts = []
    for metric, value, description in test_scenarios:
        alert = alert_manager.check_and_alert(metric, value, source="demo_system")
        status = "✅ No Alert" if alert is None else f"⚠️ {alert.severity.upper()}"
        print(f"\n  {metric} = {value} ({description})")
        print(f"    Result: {status}")
        if alert:
            print(f"    Alert ID: {alert.alert_id}")
            print(f"    Title: {alert.title}")
            created_alerts.append(alert)

    # Alert lifecycle
    print("\n" + "-" * 40)
    print("Alert Lifecycle Management")
    print("-" * 40)

    if created_alerts:
        # Acknowledge first alert
        first_alert = created_alerts[0]
        print(f"\n  Acknowledging alert: {first_alert.alert_id}")
        success = alert_manager.acknowledge_alert(first_alert.alert_id, "oncall_engineer")
        print(f"    Success: {'✅' if success else '❌'}")
        print(f"    New Status: {first_alert.status}")
        print(f"    Acknowledged By: {first_alert.acknowledged_by}")

        # Resolve second alert
        if len(created_alerts) > 1:
            second_alert = created_alerts[1]
            print(f"\n  Resolving alert: {second_alert.alert_id}")
            success = alert_manager.resolve_alert(second_alert.alert_id)
            print(f"    Success: {'✅' if success else '❌'}")
            print(f"    New Status: {second_alert.status}")

    # Get open alerts
    print("\n" + "-" * 40)
    print("📋 Open Alerts")
    print("-" * 40)

    open_alerts = alert_manager.get_open_alerts()
    print(f"\n  Open Alert Count: {len(open_alerts)}")
    for alert in open_alerts:
        print(f"\n  • [{alert.severity.upper()}] {alert.title}")
        print(f"    ID: {alert.alert_id}")
        print(f"    Value: {alert.metric_value} (threshold: {alert.threshold})")
        print(f"    Created: {alert.created_at[:19]}")

    # Alert summary
    print("\n" + "-" * 40)
    print("📊 Alert Summary")
    print("-" * 40)

    summary = alert_manager.get_alert_summary()
    print(f"\n  Total Alerts: {summary['total']}")
    print(f"\n  By Status:")
    for status, count in summary['by_status'].items():
        print(f"    {status}: {count}")
    print(f"\n  By Severity:")
    for severity, count in summary['by_severity'].items():
        print(f"    {severity}: {count}")

    print("\n✅ Demo 4 Complete: Alerting system with lifecycle management")


def demo_5_governance():
    """
    Demo 5: Model Governance

    Demonstrates model cards, approval workflows, audit trails,
    and compliance reporting.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Model Governance")
    print("=" * 70)

    governance = GovernanceManager()

    # Create model card
    print("\n📝 Creating Model Card...")

    card = governance.create_model_card(
        model_id="credit-risk-v1",
        model_name="Credit Risk Classifier",
        version="1.0.0",
        description="A gradient boosting model that predicts credit default risk for loan applications. "
                    "Uses customer demographics, financial history, and employment information.",
        intended_use="Production deployment for automated credit scoring in the loan approval pipeline. "
                     "Should be used as one factor among many in the final lending decision.",
        limitations="- May underperform for customers with thin credit files\n"
                    "- Not validated for commercial loans\n"
                    "- Requires at least 6 months of credit history",
        training_data="Training: 500,000 loan applications from 2019-2022\n"
                      "Validation: 100,000 applications from 2023\n"
                      "Features: 45 derived features from raw customer data",
        evaluation_metrics={
            "auc_roc": 0.89,
            "precision": 0.82,
            "recall": 0.78,
            "f1_score": 0.80,
            "ks_statistic": 0.52
        },
        ethical_considerations="- Regular bias audits for protected classes (gender, race, age)\n"
                               "- Disparate impact testing performed quarterly\n"
                               "- Explainability required for adverse action notices",
        created_by="ml_team@company.com"
    )

    print(f"\n  ✅ Model Card Created: {card.model_name} v{card.version}")
    print(f"  Model ID: {card.model_id}")
    print(f"  Created By: {card.created_by}")
    print(f"  Created At: {card.created_at[:19]}")

    # Display model card
    print("\n" + "-" * 40)
    print("📋 Model Card Details")
    print("-" * 40)

    print(f"\n  Model: {card.model_name}")
    print(f"  Version: {card.version}")
    print(f"\n  Description:\n    {card.description[:100]}...")
    print(f"\n  Evaluation Metrics:")
    for metric, value in card.evaluation_metrics.items():
        print(f"    {metric}: {value}")

    # Approval workflow
    print("\n" + "-" * 40)
    print("✍️ Approval Workflow")
    print("-" * 40)

    print(f"\n  Initial Status: Awaiting Approval")
    print(f"  Approved By: {card.approved_by or 'None'}")

    success = governance.approve_model(
        model_id="credit-risk-v1",
        approved_by="risk_committee@company.com",
        approval_notes="Approved after review of bias metrics and explainability"
    )

    print(f"\n  ✅ Model Approved!")
    print(f"  Approved By: {card.approved_by}")
    print(f"  Approved At: {card.approved_at[:19]}")

    # Record deployment
    print("\n" + "-" * 40)
    print("🚀 Recording Deployment")
    print("-" * 40)

    deployment_entry = governance.record_deployment(
        model_id="credit-risk-v1",
        model_version="1.0.0",
        deployed_by="mlops@company.com",
        environment="production",
        deployment_config={
            "replicas": 3,
            "cpu_limit": "2",
            "memory_limit": "4Gi",
            "max_batch_size": 100
        }
    )

    print(f"\n  ✅ Deployment Recorded")
    print(f"  Environment: production")
    print(f"  Deployed By: mlops@company.com")
    print(f"  Entry ID: {deployment_entry.entry_id}")

    # Record some predictions (for audit trail)
    print("\n" + "-" * 40)
    print("📊 Recording Predictions (Audit Trail)")
    print("-" * 40)

    for i in range(3):
        entry = governance.record_prediction(
            model_id="credit-risk-v1",
            model_version="1.0.0",
            input_hash=f"hash_{random.randint(10000, 99999)}",
            prediction=round(random.uniform(0, 1), 4),
            request_id=f"req_{random.randint(100000, 999999)}"
        )
        print(f"\n  Prediction logged: {entry.entry_id}")

    # View audit trail
    print("\n" + "-" * 40)
    print("📜 Audit Trail")
    print("-" * 40)

    audit_entries = governance.get_audit_trail(model_id="credit-risk-v1")
    print(f"\n  Total Entries: {len(audit_entries)}")

    for entry in audit_entries[-5:]:  # Last 5 entries
        print(f"\n  [{entry.timestamp[:19]}] {entry.action}")
        print(f"    Actor: {entry.actor}")
        print(f"    Model: {entry.model_id} v{entry.model_version}")

    # Compliance report
    print("\n" + "-" * 40)
    print("📋 Compliance Report")
    print("-" * 40)

    report = governance.get_compliance_report("credit-risk-v1")

    print(f"\n  Model: {report['model_name']} v{report['version']}")
    print(f"  Compliance Score: {report['compliance_score']}%")
    print(f"\n  Compliance Checks:")
    for check, passed in report['checks'].items():
        status = "✅" if passed else "❌"
        print(f"    {status} {check.replace('_', ' ').title()}")

    print(f"\n  Approved By: {report['approved_by']}")
    print(f"  Audit Entries: {report['audit_entries_count']}")

    # Save governance data
    print("\n" + "-" * 40)
    governance.save()

    print("\n✅ Demo 5 Complete: Model governance with audit trails")


def print_usage():
    """Print usage information."""
    print("""
ML Monitoring Toolkit - Module 52 Deliverable
==============================================

Usage:
    python deliverable_ml_monitoring_toolkit.py <demo>

Available Demos:
    demo1    Drift detection (PSI, KS, JS divergence)
    demo2    Performance monitoring with SLA tracking
    demo3    Model explainability (feature importance)
    demo4    Alerting system with lifecycle management
    demo5    Model governance and compliance

Examples:
    python deliverable_ml_monitoring_toolkit.py demo1
    python deliverable_ml_monitoring_toolkit.py demo2
    python deliverable_ml_monitoring_toolkit.py demo3
    python deliverable_ml_monitoring_toolkit.py demo4
    python deliverable_ml_monitoring_toolkit.py demo5

Each demo is self-contained and demonstrates key monitoring concepts.
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_drift_detection,
        "demo2": demo_2_performance_monitoring,
        "demo3": demo_3_explainability,
        "demo4": demo_4_alerting,
        "demo5": demo_5_governance,
    }

    if command in demos:
        print("\n🔬 ML Monitoring Toolkit - Module 52")
        print("=" * 70)
        demos[command]()
        print("\n" + "=" * 70)
        print("🎉 Demo completed successfully!")
    elif command == "help":
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
