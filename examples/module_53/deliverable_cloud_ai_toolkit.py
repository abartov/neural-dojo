#!/usr/bin/env python3
"""
Cloud AI Toolkit - Module 53 Deliverable

A comprehensive toolkit for AI-powered proactive cloud management:
- Anomaly detection for infrastructure metrics
- Predictive autoscaling with ML
- Capacity planning and forecasting
- Metrics simulation and analysis

Usage:
    python deliverable_cloud_ai_toolkit.py demo1  # Anomaly detection
    python deliverable_cloud_ai_toolkit.py demo2  # Predictive autoscaling
    python deliverable_cloud_ai_toolkit.py demo3  # Capacity planning
    python deliverable_cloud_ai_toolkit.py demo4  # Metrics simulation
    python deliverable_cloud_ai_toolkit.py demo5  # Full proactive management

Author: Neural Dojo
Module: 53 - AI for Proactive Cloud Management
"""

import json
import math
import random
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from collections import deque


# =============================================================================
# Configuration
# =============================================================================

STORAGE_DIR = Path(".cloud_ai_toolkit")
STORAGE_DIR.mkdir(exist_ok=True)


class AnomalyType(Enum):
    """Types of anomalies detected."""
    SPIKE = "spike"
    DROP = "drop"
    TREND_CHANGE = "trend_change"
    SEASONALITY_BREAK = "seasonality_break"


class ScalingAction(Enum):
    """Autoscaling actions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_CHANGE = "no_change"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MetricPoint:
    """A single metric measurement."""
    timestamp: str
    value: float
    metric_name: str
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    timestamp: str
    metric_name: str
    value: float
    expected_value: float
    anomaly_type: str
    severity: str
    confidence: float
    method: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ScalingDecision:
    """Autoscaling decision record."""
    timestamp: str
    current_replicas: int
    desired_replicas: int
    action: str
    predicted_load: float
    current_load: float
    reason: str
    confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CapacityForecast:
    """Capacity planning forecast."""
    forecast_date: str
    predicted_usage: float
    confidence_lower: float
    confidence_upper: float
    utilization_percent: float
    risk_level: str
    recommendation: str

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# Metrics Generator (Simulates Real Infrastructure)
# =============================================================================

class MetricsGenerator:
    """
    Generates realistic infrastructure metrics with:
    - Daily seasonality (peak hours)
    - Weekly patterns
    - Gradual trends
    - Random noise
    - Optional anomalies
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.base_cpu = 40.0
        self.base_memory = 55.0
        self.base_requests = 1000.0

    def generate_time_series(
        self,
        metric_name: str,
        hours: int = 168,  # 1 week
        interval_minutes: int = 5,
        include_anomalies: bool = True
    ) -> List[MetricPoint]:
        """Generate realistic time series data."""
        points = []
        start_time = datetime.now() - timedelta(hours=hours)
        num_points = (hours * 60) // interval_minutes

        base_value = {
            "cpu_percent": self.base_cpu,
            "memory_percent": self.base_memory,
            "requests_per_second": self.base_requests,
            "latency_ms": 50.0,
            "error_rate": 0.01
        }.get(metric_name, 50.0)

        # Generate anomaly positions
        anomaly_positions = set()
        if include_anomalies:
            num_anomalies = max(1, num_points // 100)
            anomaly_positions = set(random.sample(range(num_points), num_anomalies))

        for i in range(num_points):
            timestamp = start_time + timedelta(minutes=i * interval_minutes)
            hour = timestamp.hour
            day_of_week = timestamp.weekday()

            # Base value
            value = base_value

            # Daily seasonality (peak during business hours)
            daily_factor = 1.0 + 0.3 * math.sin((hour - 6) * math.pi / 12)
            if 9 <= hour <= 17:
                daily_factor *= 1.2

            # Weekly pattern (lower on weekends)
            if day_of_week >= 5:
                daily_factor *= 0.6

            # Apply seasonality
            value *= daily_factor

            # Add gradual trend (slight growth)
            trend = 1.0 + (i / num_points) * 0.1
            value *= trend

            # Add random noise
            noise = random.gauss(0, base_value * 0.05)
            value += noise

            # Inject anomalies
            if i in anomaly_positions:
                if random.random() > 0.5:
                    value *= random.uniform(1.5, 2.5)  # Spike
                else:
                    value *= random.uniform(0.3, 0.6)  # Drop

            # Ensure non-negative
            value = max(0, value)

            # Cap percentages at 100
            if "percent" in metric_name:
                value = min(100, value)

            points.append(MetricPoint(
                timestamp=timestamp.isoformat(),
                value=round(value, 2),
                metric_name=metric_name,
                labels={"host": "server-1", "env": "production"}
            ))

        return points


# =============================================================================
# Anomaly Detection
# =============================================================================

class AnomalyDetector:
    """
    Multi-method anomaly detection for infrastructure metrics.

    Methods:
    - Z-Score (statistical)
    - Modified Z-Score (MAD-based)
    - Isolation Forest (simulated)
    - Seasonal decomposition
    """

    def __init__(self, sensitivity: float = 3.0):
        self.sensitivity = sensitivity
        self.history: Dict[str, deque] = {}
        self.window_size = 100

    def _get_history(self, metric_name: str) -> deque:
        """Get or create history buffer for a metric."""
        if metric_name not in self.history:
            self.history[metric_name] = deque(maxlen=self.window_size)
        return self.history[metric_name]

    def _zscore(self, value: float, values: List[float]) -> float:
        """Calculate Z-score."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        if std == 0:
            return 0.0
        return (value - mean) / std

    def _mad_score(self, value: float, values: List[float]) -> float:
        """Calculate Modified Z-Score using MAD."""
        if len(values) < 2:
            return 0.0
        sorted_vals = sorted(values)
        median = sorted_vals[len(sorted_vals) // 2]
        mad = sorted(abs(v - median) for v in values)[len(values) // 2]
        if mad == 0:
            return 0.0
        return 0.6745 * (value - median) / mad

    def _isolation_score(self, value: float, values: List[float]) -> float:
        """
        Simulated Isolation Forest score.
        In production, use sklearn.ensemble.IsolationForest
        """
        if len(values) < 10:
            return 0.0

        # Approximate isolation: how far from nearest cluster
        sorted_vals = sorted(values)
        percentile = sum(1 for v in sorted_vals if v < value) / len(sorted_vals)

        # Extreme percentiles indicate potential anomalies
        if percentile < 0.05 or percentile > 0.95:
            return abs(percentile - 0.5) * 4
        return abs(percentile - 0.5) * 2

    def detect(
        self,
        metric_name: str,
        value: float,
        timestamp: str
    ) -> Optional[AnomalyResult]:
        """Detect if a value is anomalous using ensemble of methods."""
        history = self._get_history(metric_name)
        values = list(history)

        # Need minimum history
        if len(values) < 20:
            history.append(value)
            return None

        # Calculate scores from multiple methods
        zscore = abs(self._zscore(value, values))
        mad_score = abs(self._mad_score(value, values))
        isolation = self._isolation_score(value, values)

        # Voting: anomaly if 2+ methods agree
        votes = sum([
            zscore > self.sensitivity,
            mad_score > self.sensitivity,
            isolation > 0.8
        ])

        # Update history
        history.append(value)

        if votes >= 2:
            # Determine anomaly type
            mean = sum(values) / len(values)
            if value > mean * 1.5:
                anomaly_type = AnomalyType.SPIKE
            elif value < mean * 0.5:
                anomaly_type = AnomalyType.DROP
            else:
                anomaly_type = AnomalyType.TREND_CHANGE

            # Calculate severity
            max_score = max(zscore, mad_score, isolation * 3)
            if max_score > 5:
                severity = AlertSeverity.CRITICAL
            elif max_score > 3.5:
                severity = AlertSeverity.WARNING
            else:
                severity = AlertSeverity.INFO

            confidence = min(0.99, 0.5 + (votes / 3) * 0.5)

            return AnomalyResult(
                timestamp=timestamp,
                metric_name=metric_name,
                value=round(value, 2),
                expected_value=round(mean, 2),
                anomaly_type=anomaly_type.value,
                severity=severity.value,
                confidence=round(confidence, 3),
                method="ensemble",
                details={
                    "zscore": round(zscore, 2),
                    "mad_score": round(mad_score, 2),
                    "isolation_score": round(isolation, 2),
                    "votes": votes
                }
            )

        return None

    def get_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get current statistics for a metric."""
        history = self._get_history(metric_name)
        values = list(history)

        if not values:
            return {}

        sorted_vals = sorted(values)
        n = len(sorted_vals)

        return {
            "count": n,
            "mean": round(sum(values) / n, 2),
            "std": round(math.sqrt(sum((v - sum(values)/n)**2 for v in values) / n), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "p50": round(sorted_vals[n // 2], 2),
            "p95": round(sorted_vals[int(n * 0.95)], 2) if n > 20 else None
        }


# =============================================================================
# Predictive Autoscaler
# =============================================================================

class PredictiveAutoscaler:
    """
    ML-powered autoscaler that predicts future load and scales proactively.

    Features:
    - Exponential smoothing for short-term prediction
    - Seasonal pattern recognition
    - Conservative scale-down (aggressive scale-up)
    - Configurable target utilization
    """

    def __init__(
        self,
        min_replicas: int = 2,
        max_replicas: int = 50,
        target_utilization: float = 0.7,
        capacity_per_replica: float = 100.0,
        prediction_horizon_minutes: int = 15
    ):
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.target_utilization = target_utilization
        self.capacity_per_replica = capacity_per_replica
        self.prediction_horizon = prediction_horizon_minutes

        self.history: deque = deque(maxlen=288)  # 24 hours at 5-min intervals
        self.current_replicas = min_replicas
        self.decisions: List[ScalingDecision] = []
        self.cooldown_until: Optional[datetime] = None
        self.scale_down_delay = 3  # Require N consecutive signals

        self._scale_down_signals = 0

    def _exponential_smoothing(
        self,
        values: List[float],
        alpha: float = 0.3
    ) -> float:
        """Simple exponential smoothing for prediction."""
        if not values:
            return 0.0
        result = values[0]
        for v in values[1:]:
            result = alpha * v + (1 - alpha) * result
        return result

    def _predict_load(self, lookahead_steps: int = 3) -> float:
        """Predict load N steps ahead."""
        if len(self.history) < 10:
            return list(self.history)[-1] if self.history else 0.0

        values = list(self.history)

        # Weight recent values more heavily
        recent = values[-10:]
        smoothed = self._exponential_smoothing(recent, alpha=0.4)

        # Calculate trend
        if len(values) >= 20:
            recent_avg = sum(values[-10:]) / 10
            older_avg = sum(values[-20:-10]) / 10
            trend = (recent_avg - older_avg) / 10
        else:
            trend = 0

        # Project forward
        predicted = smoothed + trend * lookahead_steps

        # Check for seasonal pattern (same time yesterday)
        if len(values) >= 288:  # 24 hours of history
            yesterday_value = values[-288 + lookahead_steps]
            # Blend with seasonal
            predicted = 0.7 * predicted + 0.3 * yesterday_value

        return max(0, predicted)

    def _calculate_desired_replicas(self, predicted_load: float) -> int:
        """Calculate optimal replica count for predicted load."""
        required_capacity = predicted_load / self.target_utilization
        desired = math.ceil(required_capacity / self.capacity_per_replica)
        return max(self.min_replicas, min(self.max_replicas, desired))

    def record_load(self, load: float) -> None:
        """Record current load for prediction."""
        self.history.append(load)

    def make_decision(self, current_load: float) -> ScalingDecision:
        """Make scaling decision based on predicted load."""
        timestamp = datetime.now()

        # Check cooldown
        if self.cooldown_until and timestamp < self.cooldown_until:
            return ScalingDecision(
                timestamp=timestamp.isoformat(),
                current_replicas=self.current_replicas,
                desired_replicas=self.current_replicas,
                action=ScalingAction.NO_CHANGE.value,
                predicted_load=current_load,
                current_load=current_load,
                reason="In cooldown period",
                confidence=1.0
            )

        # Record load
        self.record_load(current_load)

        # Predict future load
        predicted_load = self._predict_load(lookahead_steps=3)
        desired = self._calculate_desired_replicas(predicted_load)

        # Determine action
        if desired > self.current_replicas:
            # Scale up aggressively
            action = ScalingAction.SCALE_UP
            reason = f"Predicted load {predicted_load:.0f} requires {desired} replicas"
            self._scale_down_signals = 0
            self.cooldown_until = timestamp + timedelta(minutes=2)
            confidence = min(0.95, 0.6 + len(self.history) / 500)

        elif desired < self.current_replicas:
            # Scale down conservatively
            self._scale_down_signals += 1

            if self._scale_down_signals >= self.scale_down_delay:
                action = ScalingAction.SCALE_DOWN
                reason = f"Stable low load for {self.scale_down_delay} periods"
                self._scale_down_signals = 0
                self.cooldown_until = timestamp + timedelta(minutes=5)
                confidence = 0.8
            else:
                action = ScalingAction.NO_CHANGE
                desired = self.current_replicas
                reason = f"Waiting for {self.scale_down_delay - self._scale_down_signals} more signals to scale down"
                confidence = 0.7

        else:
            action = ScalingAction.NO_CHANGE
            reason = "Current capacity is optimal"
            self._scale_down_signals = 0
            confidence = 0.9

        # Apply scaling
        if action in [ScalingAction.SCALE_UP, ScalingAction.SCALE_DOWN]:
            self.current_replicas = desired

        decision = ScalingDecision(
            timestamp=timestamp.isoformat(),
            current_replicas=self.current_replicas,
            desired_replicas=desired,
            action=action.value,
            predicted_load=round(predicted_load, 2),
            current_load=round(current_load, 2),
            reason=reason,
            confidence=round(confidence, 3)
        )

        self.decisions.append(decision)
        return decision

    def get_summary(self) -> Dict[str, Any]:
        """Get autoscaler summary."""
        if not self.decisions:
            return {"status": "no_decisions"}

        scale_ups = sum(1 for d in self.decisions if d.action == ScalingAction.SCALE_UP.value)
        scale_downs = sum(1 for d in self.decisions if d.action == ScalingAction.SCALE_DOWN.value)

        return {
            "current_replicas": self.current_replicas,
            "total_decisions": len(self.decisions),
            "scale_ups": scale_ups,
            "scale_downs": scale_downs,
            "history_points": len(self.history),
            "avg_confidence": round(sum(d.confidence for d in self.decisions) / len(self.decisions), 3)
        }


# =============================================================================
# Capacity Planner
# =============================================================================

class CapacityPlanner:
    """
    ML-powered capacity planning for infrastructure.

    Features:
    - Growth trend analysis
    - Utilization forecasting
    - Threshold crossing predictions
    - Recommendations for capacity changes
    """

    def __init__(
        self,
        total_capacity: float,
        warning_threshold: float = 0.7,
        critical_threshold: float = 0.85
    ):
        self.total_capacity = total_capacity
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.history: List[Tuple[datetime, float]] = []

    def add_data_point(self, usage: float, timestamp: Optional[datetime] = None) -> None:
        """Add usage data point."""
        ts = timestamp or datetime.now()
        self.history.append((ts, usage))

    def _fit_growth_model(self) -> Tuple[str, float, float]:
        """
        Fit growth model to historical data.
        Returns: (model_type, slope, intercept)
        """
        if len(self.history) < 2:
            return ("insufficient_data", 0, 0)

        # Convert to numeric for regression
        start_time = self.history[0][0]
        x = [(ts - start_time).total_seconds() / 86400 for ts, _ in self.history]  # Days
        y = [usage for _, usage in self.history]

        n = len(x)
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # Linear regression
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return ("flat", 0, y_mean)

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Determine growth type
        if abs(slope) < 0.01 * y_mean:
            model_type = "stable"
        elif slope > 0:
            model_type = "growing"
        else:
            model_type = "declining"

        return (model_type, slope, intercept)

    def forecast(self, days_ahead: int = 30) -> List[CapacityForecast]:
        """Generate capacity forecast."""
        if len(self.history) < 7:
            return []

        model_type, slope, intercept = self._fit_growth_model()

        forecasts = []
        start_time = self.history[0][0]
        current_day = (self.history[-1][0] - start_time).total_seconds() / 86400

        # Calculate prediction error from history
        predictions = [slope * ((ts - start_time).total_seconds() / 86400) + intercept
                       for ts, _ in self.history]
        actuals = [usage for _, usage in self.history]
        errors = [abs(p - a) for p, a in zip(predictions, actuals)]
        std_error = math.sqrt(sum(e**2 for e in errors) / len(errors)) if errors else 0

        for day in range(1, days_ahead + 1):
            future_day = current_day + day
            predicted = slope * future_day + intercept

            # Confidence interval (widens with distance)
            confidence_factor = 1 + (day / days_ahead) * 0.5
            margin = std_error * 1.96 * confidence_factor

            lower = max(0, predicted - margin)
            upper = predicted + margin

            utilization = predicted / self.total_capacity
            upper_utilization = upper / self.total_capacity

            # Determine risk level
            if upper_utilization >= self.critical_threshold:
                risk_level = "critical"
                recommendation = "Immediate capacity expansion required"
            elif upper_utilization >= self.warning_threshold:
                risk_level = "warning"
                recommendation = "Plan capacity expansion within 2 weeks"
            elif utilization >= self.warning_threshold * 0.8:
                risk_level = "elevated"
                recommendation = "Monitor closely, plan expansion if trend continues"
            else:
                risk_level = "normal"
                recommendation = "Capacity sufficient"

            forecast_date = (self.history[-1][0] + timedelta(days=day)).strftime("%Y-%m-%d")

            forecasts.append(CapacityForecast(
                forecast_date=forecast_date,
                predicted_usage=round(predicted, 2),
                confidence_lower=round(lower, 2),
                confidence_upper=round(upper, 2),
                utilization_percent=round(utilization * 100, 1),
                risk_level=risk_level,
                recommendation=recommendation
            ))

        return forecasts

    def find_threshold_crossing(self, threshold: float = 0.85) -> Optional[str]:
        """Predict when capacity threshold will be crossed."""
        model_type, slope, intercept = self._fit_growth_model()

        if slope <= 0:
            return None  # Not growing

        target_usage = self.total_capacity * threshold
        start_time = self.history[0][0]
        current_day = (self.history[-1][0] - start_time).total_seconds() / 86400

        # Solve for day when predicted = target
        days_until = (target_usage - intercept) / slope - current_day

        if days_until <= 0:
            return "Already exceeded"

        crossing_date = self.history[-1][0] + timedelta(days=days_until)
        return crossing_date.strftime("%Y-%m-%d")

    def get_summary(self) -> Dict[str, Any]:
        """Get capacity planning summary."""
        if len(self.history) < 2:
            return {"status": "insufficient_data"}

        model_type, slope, _ = self._fit_growth_model()
        current_usage = self.history[-1][1]
        current_utilization = current_usage / self.total_capacity

        daily_growth = slope
        monthly_growth = slope * 30

        return {
            "total_capacity": self.total_capacity,
            "current_usage": round(current_usage, 2),
            "current_utilization": f"{current_utilization * 100:.1f}%",
            "growth_model": model_type,
            "daily_growth": round(daily_growth, 2),
            "monthly_growth": round(monthly_growth, 2),
            "warning_crossing": self.find_threshold_crossing(self.warning_threshold),
            "critical_crossing": self.find_threshold_crossing(self.critical_threshold),
            "data_points": len(self.history)
        }


# =============================================================================
# Proactive Manager (Combines All Components)
# =============================================================================

class ProactiveCloudManager:
    """
    Unified proactive cloud management system.

    Integrates:
    - Anomaly detection
    - Predictive autoscaling
    - Capacity planning
    """

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.autoscaler = PredictiveAutoscaler()
        self.capacity_planner = CapacityPlanner(total_capacity=10000)

        self.anomalies: List[AnomalyResult] = []
        self.alerts: List[Dict] = []

    def process_metric(
        self,
        metric_name: str,
        value: float,
        timestamp: str
    ) -> Dict[str, Any]:
        """Process a single metric through all systems."""
        result = {
            "metric": metric_name,
            "value": value,
            "timestamp": timestamp,
            "anomaly": None,
            "scaling": None
        }

        # Anomaly detection
        anomaly = self.anomaly_detector.detect(metric_name, value, timestamp)
        if anomaly:
            self.anomalies.append(anomaly)
            result["anomaly"] = anomaly.to_dict()

            # Generate alert
            self.alerts.append({
                "timestamp": timestamp,
                "severity": anomaly.severity,
                "metric": metric_name,
                "message": f"Anomaly detected: {anomaly.anomaly_type} "
                           f"(value={value}, expected={anomaly.expected_value})"
            })

        # Autoscaling (for load metrics)
        if metric_name in ["requests_per_second", "cpu_percent"]:
            decision = self.autoscaler.make_decision(value)
            if decision.action != ScalingAction.NO_CHANGE.value:
                result["scaling"] = decision.to_dict()

        # Capacity planning
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00").split("+")[0])
        self.capacity_planner.add_data_point(value, ts)

        return result

    def get_dashboard(self) -> Dict[str, Any]:
        """Generate management dashboard."""
        return {
            "timestamp": datetime.now().isoformat(),
            "anomalies": {
                "total": len(self.anomalies),
                "critical": sum(1 for a in self.anomalies if a.severity == "critical"),
                "warning": sum(1 for a in self.anomalies if a.severity == "warning"),
                "recent": [a.to_dict() for a in self.anomalies[-5:]]
            },
            "autoscaling": self.autoscaler.get_summary(),
            "capacity": self.capacity_planner.get_summary(),
            "alerts": {
                "total": len(self.alerts),
                "recent": self.alerts[-10:]
            }
        }


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_anomaly_detection():
    """
    Demo 1: Anomaly Detection

    Demonstrates multi-method anomaly detection on infrastructure metrics.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: Anomaly Detection for Infrastructure Metrics")
    print("=" * 70)

    detector = AnomalyDetector(sensitivity=2.5)
    generator = MetricsGenerator(seed=42)

    # Generate CPU metrics with anomalies
    print("\n📊 Generating CPU metrics (1 week, 5-min intervals)...")
    cpu_metrics = generator.generate_time_series(
        "cpu_percent",
        hours=168,
        interval_minutes=5,
        include_anomalies=True
    )
    print(f"  Generated {len(cpu_metrics)} data points")

    # Process metrics and detect anomalies
    print("\n🔍 Running anomaly detection...")
    anomalies = []

    for point in cpu_metrics:
        result = detector.detect(
            point.metric_name,
            point.value,
            point.timestamp
        )
        if result:
            anomalies.append(result)

    print(f"\n  Total anomalies detected: {len(anomalies)}")

    # Show anomaly breakdown
    print("\n" + "-" * 40)
    print("Anomaly Breakdown")
    print("-" * 40)

    by_type = {}
    by_severity = {}
    for a in anomalies:
        by_type[a.anomaly_type] = by_type.get(a.anomaly_type, 0) + 1
        by_severity[a.severity] = by_severity.get(a.severity, 0) + 1

    print("\n  By Type:")
    for t, count in by_type.items():
        print(f"    {t}: {count}")

    print("\n  By Severity:")
    for s, count in by_severity.items():
        icon = "🔴" if s == "critical" else "🟡" if s == "warning" else "🔵"
        print(f"    {icon} {s}: {count}")

    # Show sample anomalies
    print("\n" + "-" * 40)
    print("Sample Anomalies")
    print("-" * 40)

    for anomaly in anomalies[:5]:
        print(f"\n  📌 {anomaly.timestamp[:19]}")
        print(f"     Value: {anomaly.value} (expected: {anomaly.expected_value})")
        print(f"     Type: {anomaly.anomaly_type}")
        print(f"     Severity: {anomaly.severity}")
        print(f"     Confidence: {anomaly.confidence:.1%}")
        print(f"     Scores: z={anomaly.details['zscore']}, "
              f"mad={anomaly.details['mad_score']}, "
              f"iso={anomaly.details['isolation_score']}")

    # Show statistics
    print("\n" + "-" * 40)
    print("📈 Metric Statistics")
    print("-" * 40)
    stats = detector.get_statistics("cpu_percent")
    for key, value in stats.items():
        if value is not None:
            print(f"  {key}: {value}")

    print("\n✅ Demo 1 Complete: Multi-method anomaly detection")


def demo_2_predictive_autoscaling():
    """
    Demo 2: Predictive Autoscaling

    Demonstrates ML-powered autoscaling that predicts future load.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Predictive Autoscaling")
    print("=" * 70)

    autoscaler = PredictiveAutoscaler(
        min_replicas=2,
        max_replicas=20,
        target_utilization=0.7,
        capacity_per_replica=100
    )

    generator = MetricsGenerator(seed=123)

    # Generate request metrics
    print("\n📊 Generating request load (24 hours)...")
    metrics = generator.generate_time_series(
        "requests_per_second",
        hours=24,
        interval_minutes=5,
        include_anomalies=False
    )

    # Simulate autoscaling decisions
    print("\n⚖️ Simulating autoscaling decisions...")
    decisions_log = []

    for point in metrics:
        decision = autoscaler.make_decision(point.value)

        if decision.action != ScalingAction.NO_CHANGE.value:
            decisions_log.append({
                "time": point.timestamp[11:16],
                "load": point.value,
                "action": decision.action,
                "replicas": decision.current_replicas,
                "reason": decision.reason[:50]
            })

    # Show scaling timeline
    print("\n" + "-" * 40)
    print("Scaling Events Timeline")
    print("-" * 40)

    for event in decisions_log[:15]:
        action_icon = "⬆️" if event["action"] == "scale_up" else "⬇️"
        print(f"\n  {event['time']} {action_icon} {event['action'].upper()}")
        print(f"    Load: {event['load']:.0f} RPS → Replicas: {event['replicas']}")
        print(f"    Reason: {event['reason']}")

    # Show summary
    print("\n" + "-" * 40)
    print("📊 Autoscaling Summary")
    print("-" * 40)
    summary = autoscaler.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Compare reactive vs predictive
    print("\n" + "-" * 40)
    print("📈 Reactive vs Predictive Comparison")
    print("-" * 40)

    print("""
  Reactive Autoscaling:
    • Responds AFTER load increase
    • 2-5 minute scaling delay
    • Users experience degradation during scaling

  Predictive Autoscaling:
    • Scales BEFORE load increase
    • Proactive capacity provisioning
    • Smooth user experience

  This demo showed {0} proactive scaling events!
    """.format(summary["scale_ups"]))

    print("\n✅ Demo 2 Complete: Predictive autoscaling with ML")


def demo_3_capacity_planning():
    """
    Demo 3: Capacity Planning

    Demonstrates ML-powered capacity planning and forecasting.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Capacity Planning & Forecasting")
    print("=" * 70)

    planner = CapacityPlanner(
        total_capacity=10000,
        warning_threshold=0.7,
        critical_threshold=0.85
    )

    # Simulate 60 days of historical data with growth
    print("\n📊 Generating 60 days of usage history...")
    random.seed(456)

    base_usage = 5000
    daily_growth = 50
    start_date = datetime.now() - timedelta(days=60)

    for day in range(60):
        date = start_date + timedelta(days=day)
        # Base + growth + weekly pattern + noise
        usage = base_usage + (daily_growth * day)
        usage *= (1 + 0.1 * math.sin(day * 2 * math.pi / 7))  # Weekly cycle
        usage += random.gauss(0, 100)  # Noise
        planner.add_data_point(usage, date)

    # Get current summary
    print("\n" + "-" * 40)
    print("📊 Current Capacity Status")
    print("-" * 40)
    summary = planner.get_summary()

    print(f"\n  Total Capacity: {summary['total_capacity']:,}")
    print(f"  Current Usage: {summary['current_usage']:,.0f}")
    print(f"  Utilization: {summary['current_utilization']}")
    print(f"  Growth Model: {summary['growth_model']}")
    print(f"  Daily Growth: {summary['daily_growth']:+.0f} units/day")
    print(f"  Monthly Growth: {summary['monthly_growth']:+.0f} units/month")

    # Show threshold crossings
    print("\n" + "-" * 40)
    print("⚠️ Threshold Crossing Predictions")
    print("-" * 40)
    print(f"\n  70% Warning: {summary['warning_crossing'] or 'Not predicted'}")
    print(f"  85% Critical: {summary['critical_crossing'] or 'Not predicted'}")

    # Generate forecast
    print("\n" + "-" * 40)
    print("🔮 30-Day Capacity Forecast")
    print("-" * 40)

    forecasts = planner.forecast(days_ahead=30)

    # Show weekly forecasts
    for forecast in forecasts[::7]:  # Every 7 days
        risk_icon = {
            "critical": "🔴",
            "warning": "🟡",
            "elevated": "🟠",
            "normal": "🟢"
        }.get(forecast.risk_level, "⚪")

        print(f"\n  {forecast.forecast_date}:")
        print(f"    Predicted Usage: {forecast.predicted_usage:,.0f} "
              f"[{forecast.confidence_lower:,.0f} - {forecast.confidence_upper:,.0f}]")
        print(f"    Utilization: {forecast.utilization_percent}%")
        print(f"    {risk_icon} Risk: {forecast.risk_level.upper()}")
        print(f"    → {forecast.recommendation}")

    print("\n✅ Demo 3 Complete: Capacity planning with ML forecasting")


def demo_4_metrics_simulation():
    """
    Demo 4: Metrics Simulation

    Demonstrates realistic infrastructure metrics generation.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Infrastructure Metrics Simulation")
    print("=" * 70)

    generator = MetricsGenerator(seed=789)

    metrics_to_generate = [
        ("cpu_percent", "CPU Utilization"),
        ("memory_percent", "Memory Usage"),
        ("requests_per_second", "Request Rate"),
        ("latency_ms", "Response Latency"),
        ("error_rate", "Error Rate")
    ]

    print("\n📊 Generating multi-metric time series (48 hours)...")

    for metric_name, display_name in metrics_to_generate:
        print(f"\n" + "-" * 40)
        print(f"📈 {display_name} ({metric_name})")
        print("-" * 40)

        metrics = generator.generate_time_series(
            metric_name,
            hours=48,
            interval_minutes=15,
            include_anomalies=True
        )

        values = [m.value for m in metrics]
        n = len(values)

        # Calculate statistics
        mean = sum(values) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / n)
        sorted_vals = sorted(values)

        print(f"\n  Data Points: {n}")
        print(f"  Mean: {mean:.2f}")
        print(f"  Std Dev: {std:.2f}")
        print(f"  Min: {min(values):.2f}")
        print(f"  Max: {max(values):.2f}")
        print(f"  P50: {sorted_vals[n // 2]:.2f}")
        print(f"  P95: {sorted_vals[int(n * 0.95)]:.2f}")

        # Show mini time series visualization
        print(f"\n  24h Pattern (hourly avg):")
        hourly_avg = {}
        for m in metrics:
            hour = int(m.timestamp[11:13])
            if hour not in hourly_avg:
                hourly_avg[hour] = []
            hourly_avg[hour].append(m.value)

        for hour in sorted(hourly_avg.keys()):
            avg = sum(hourly_avg[hour]) / len(hourly_avg[hour])
            bar_len = int((avg / max(values)) * 30)
            bar = "█" * bar_len
            print(f"    {hour:02d}:00 │{bar} {avg:.1f}")

    print("\n✅ Demo 4 Complete: Multi-metric simulation with patterns")


def demo_5_proactive_management():
    """
    Demo 5: Full Proactive Cloud Management

    Demonstrates the complete integrated system.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Full Proactive Cloud Management System")
    print("=" * 70)

    manager = ProactiveCloudManager()
    generator = MetricsGenerator(seed=999)

    # Generate metrics
    print("\n🔧 Initializing Proactive Cloud Manager...")
    print("  Components:")
    print("    ✓ Anomaly Detector (ensemble methods)")
    print("    ✓ Predictive Autoscaler (ML-based)")
    print("    ✓ Capacity Planner (growth modeling)")

    print("\n📊 Processing 24 hours of metrics...")

    metrics = generator.generate_time_series(
        "cpu_percent",
        hours=24,
        interval_minutes=5,
        include_anomalies=True
    )

    events = []
    for point in metrics:
        result = manager.process_metric(
            point.metric_name,
            point.value,
            point.timestamp
        )
        if result.get("anomaly") or result.get("scaling"):
            events.append(result)

    # Show significant events
    print("\n" + "-" * 40)
    print("🚨 Significant Events")
    print("-" * 40)

    for event in events[:10]:
        print(f"\n  {event['timestamp'][11:19]} │ {event['metric']}: {event['value']:.1f}")

        if event.get("anomaly"):
            a = event["anomaly"]
            print(f"    ⚠️ ANOMALY: {a['anomaly_type']} ({a['severity']})")
            print(f"       Expected: {a['expected_value']}, Confidence: {a['confidence']:.1%}")

        if event.get("scaling"):
            s = event["scaling"]
            icon = "⬆️" if s["action"] == "scale_up" else "⬇️"
            print(f"    {icon} SCALING: {s['action']} to {s['desired_replicas']} replicas")
            print(f"       Predicted load: {s['predicted_load']:.0f}")

    # Show dashboard
    print("\n" + "-" * 40)
    print("📊 Management Dashboard")
    print("-" * 40)

    dashboard = manager.get_dashboard()

    print("\n  ANOMALIES:")
    print(f"    Total: {dashboard['anomalies']['total']}")
    print(f"    Critical: {dashboard['anomalies']['critical']}")
    print(f"    Warning: {dashboard['anomalies']['warning']}")

    print("\n  AUTOSCALING:")
    for key, value in dashboard["autoscaling"].items():
        print(f"    {key}: {value}")

    print("\n  CAPACITY:")
    for key, value in dashboard["capacity"].items():
        if value is not None:
            print(f"    {key}: {value}")

    print("\n  ALERTS:")
    print(f"    Total: {dashboard['alerts']['total']}")

    # Summary
    print("\n" + "-" * 40)
    print("💡 Proactive Management Benefits")
    print("-" * 40)
    print("""
  Traditional (Reactive):
    Problem → Alert → Investigate → Fix → Recover
    Result: Downtime, user impact, stress

  AI-Powered (Proactive):
    Anomaly Predicted → Auto-Scale → Prevent Issue
    Result: No downtime, happy users, calm ops

  This system detected {0} anomalies and made {1} scaling decisions
  BEFORE they could impact users!
    """.format(
        dashboard['anomalies']['total'],
        dashboard['autoscaling'].get('scale_ups', 0) + dashboard['autoscaling'].get('scale_downs', 0)
    ))

    print("\n✅ Demo 5 Complete: Full proactive cloud management")


def print_usage():
    """Print usage information."""
    print("""
Cloud AI Toolkit - Module 53 Deliverable
=========================================

Usage:
    python deliverable_cloud_ai_toolkit.py <demo>

Available Demos:
    demo1    Anomaly detection for infrastructure metrics
    demo2    Predictive autoscaling with ML
    demo3    Capacity planning and forecasting
    demo4    Infrastructure metrics simulation
    demo5    Full proactive cloud management system

Examples:
    python deliverable_cloud_ai_toolkit.py demo1
    python deliverable_cloud_ai_toolkit.py demo2
    python deliverable_cloud_ai_toolkit.py demo3
    python deliverable_cloud_ai_toolkit.py demo4
    python deliverable_cloud_ai_toolkit.py demo5

Each demo demonstrates key AI-powered cloud management concepts.
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_anomaly_detection,
        "demo2": demo_2_predictive_autoscaling,
        "demo3": demo_3_capacity_planning,
        "demo4": demo_4_metrics_simulation,
        "demo5": demo_5_proactive_management,
    }

    if command in demos:
        print("\n☁️ Cloud AI Toolkit - Module 53")
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
