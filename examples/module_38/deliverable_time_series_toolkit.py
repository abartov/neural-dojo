#!/usr/bin/env python3
"""
Module 38 Deliverable: Time Series Forecasting Toolkit

A comprehensive toolkit demonstrating time series analysis, forecasting methods,
and anomaly detection - from classical ARIMA to modern techniques.

Features:
- Time series decomposition and analysis
- ARIMA/SARIMA implementation from scratch
- Prophet-style forecasting
- Temporal feature engineering
- Anomaly detection methods
- Walk-forward cross-validation

Usage:
    python deliverable_time_series_toolkit.py demo1  # Time series decomposition
    python deliverable_time_series_toolkit.py demo2  # ARIMA forecasting
    python deliverable_time_series_toolkit.py demo3  # Feature engineering
    python deliverable_time_series_toolkit.py demo4  # Anomaly detection
    python deliverable_time_series_toolkit.py demo5  # Full report

Author: Neural Dojo
Module: 38 - Time Series & Forecasting
"""

import json
import math
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
import random


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TimeSeriesPoint:
    """A single point in a time series."""
    timestamp: str
    value: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TimeSeriesData:
    """Container for time series data."""
    name: str
    points: List[TimeSeriesPoint]
    frequency: str  # 'daily', 'hourly', 'monthly'

    @property
    def values(self) -> List[float]:
        return [p.value for p in self.points]

    @property
    def timestamps(self) -> List[str]:
        return [p.timestamp for p in self.points]

    def __len__(self) -> int:
        return len(self.points)


@dataclass
class DecompositionResult:
    """Result of time series decomposition."""
    trend: List[float]
    seasonal: List[float]
    residual: List[float]
    period: int


@dataclass
class ForecastResult:
    """Result of a forecast."""
    method: str
    predictions: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    confidence_level: float
    metrics: Dict[str, float]


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    method: str
    anomaly_indices: List[int]
    anomaly_scores: List[float]
    threshold: float


@dataclass
class FeatureSet:
    """Engineered features for time series."""
    feature_names: List[str]
    feature_matrix: List[List[float]]
    target: List[float]


# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_synthetic_time_series(
    n_points: int = 365,
    trend_slope: float = 0.1,
    seasonal_period: int = 7,
    seasonal_amplitude: float = 10.0,
    noise_std: float = 2.0,
    base_value: float = 100.0,
    start_date: str = "2024-01-01",
    add_anomalies: bool = False,
    anomaly_count: int = 5
) -> TimeSeriesData:
    """
    Generate synthetic time series with trend, seasonality, and noise.
    """
    random.seed(42)

    points = []
    start = datetime.strptime(start_date, "%Y-%m-%d")

    anomaly_indices = set()
    if add_anomalies:
        anomaly_indices = set(random.sample(range(n_points), min(anomaly_count, n_points)))

    for i in range(n_points):
        # Trend component
        trend = trend_slope * i

        # Seasonal component (multiple seasonalities)
        weekly = seasonal_amplitude * math.sin(2 * math.pi * i / seasonal_period)
        monthly = (seasonal_amplitude / 2) * math.sin(2 * math.pi * i / 30)
        seasonal = weekly + monthly

        # Noise component
        noise = random.gauss(0, noise_std)

        # Combine
        value = base_value + trend + seasonal + noise

        # Add anomalies
        if i in anomaly_indices:
            value += random.choice([-1, 1]) * random.uniform(20, 40)

        timestamp = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        points.append(TimeSeriesPoint(timestamp=timestamp, value=value))

    return TimeSeriesData(
        name="synthetic_series",
        points=points,
        frequency="daily"
    )


def generate_sales_data(n_days: int = 365) -> TimeSeriesData:
    """Generate realistic retail sales data."""
    random.seed(42)

    points = []
    start = datetime(2024, 1, 1)
    base_sales = 1000

    for i in range(n_days):
        date = start + timedelta(days=i)

        # Trend: 10% annual growth
        trend = base_sales * (1 + 0.1 * i / 365)

        # Weekly seasonality (weekends higher)
        day_of_week = date.weekday()
        if day_of_week >= 5:  # Weekend
            weekly_factor = 1.3
        elif day_of_week == 4:  # Friday
            weekly_factor = 1.1
        else:
            weekly_factor = 0.9

        # Monthly seasonality (end of month spike)
        if date.day >= 25:
            monthly_factor = 1.15
        else:
            monthly_factor = 1.0

        # Holiday effects (simplified)
        holiday_factor = 1.0
        if date.month == 12 and date.day >= 15:
            holiday_factor = 1.5
        elif date.month == 11 and date.day >= 20 and date.day <= 30:
            holiday_factor = 1.3

        # Combine
        value = trend * weekly_factor * monthly_factor * holiday_factor
        value += random.gauss(0, 50)
        value = max(0, value)

        timestamp = date.strftime("%Y-%m-%d")
        points.append(TimeSeriesPoint(timestamp=timestamp, value=round(value, 2)))

    return TimeSeriesData(
        name="retail_sales",
        points=points,
        frequency="daily"
    )


# =============================================================================
# TIME SERIES DECOMPOSITION
# =============================================================================

def moving_average(values: List[float], window: int) -> List[float]:
    """Calculate moving average with centered window."""
    n = len(values)
    result = [float('nan')] * n
    half_window = window // 2

    for i in range(half_window, n - half_window):
        window_values = values[i - half_window:i + half_window + 1]
        result[i] = sum(window_values) / len(window_values)

    return result


def decompose_time_series(
    ts: TimeSeriesData,
    period: int = 7,
    method: str = "additive"
) -> DecompositionResult:
    """
    Decompose time series into trend, seasonal, and residual components.

    Uses classical decomposition:
    1. Estimate trend with moving average
    2. Remove trend to get detrended series
    3. Average detrended values by season position to get seasonal
    4. Residual = original - trend - seasonal
    """
    values = ts.values
    n = len(values)

    # Step 1: Estimate trend using centered moving average
    trend = moving_average(values, period)

    # Step 2: Detrend the series
    if method == "additive":
        detrended = [values[i] - trend[i] if not math.isnan(trend[i]) else float('nan')
                    for i in range(n)]
    else:  # multiplicative
        detrended = [values[i] / trend[i] if not math.isnan(trend[i]) and trend[i] != 0 else float('nan')
                    for i in range(n)]

    # Step 3: Calculate seasonal component by averaging each position
    seasonal_indices = [[] for _ in range(period)]
    for i, val in enumerate(detrended):
        if not math.isnan(val):
            seasonal_indices[i % period].append(val)

    seasonal_pattern = []
    for idx_values in seasonal_indices:
        if idx_values:
            seasonal_pattern.append(sum(idx_values) / len(idx_values))
        else:
            seasonal_pattern.append(0)

    # Normalize seasonal pattern to sum to zero (additive) or mean to 1 (multiplicative)
    if method == "additive":
        mean_seasonal = sum(seasonal_pattern) / len(seasonal_pattern)
        seasonal_pattern = [s - mean_seasonal for s in seasonal_pattern]

    # Extend seasonal pattern to full length
    seasonal = [seasonal_pattern[i % period] for i in range(n)]

    # Step 4: Calculate residual
    residual = []
    for i in range(n):
        if math.isnan(trend[i]):
            residual.append(float('nan'))
        elif method == "additive":
            residual.append(values[i] - trend[i] - seasonal[i])
        else:
            residual.append(values[i] / (trend[i] * seasonal[i]) if trend[i] * seasonal[i] != 0 else float('nan'))

    return DecompositionResult(
        trend=trend,
        seasonal=seasonal,
        residual=residual,
        period=period
    )


# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def adf_test_simple(values: List[float], max_lag: int = 5) -> Dict[str, float]:
    """
    Simplified Augmented Dickey-Fuller test for stationarity.

    Tests H0: series has a unit root (non-stationary)
    vs H1: series is stationary

    Returns approximate test statistic (not p-value for simplicity).
    """
    n = len(values)
    if n < max_lag + 10:
        return {"test_statistic": 0, "critical_value_5pct": -2.86, "is_stationary": False}

    # Calculate first difference
    diff = [values[i] - values[i-1] for i in range(1, n)]

    # Regression: diff_t = alpha + beta * y_{t-1} + lagged diffs + error
    # Simplified: just test if beta (coefficient on lagged level) is significant

    # Estimate beta using simple regression
    y = diff[max_lag:]
    x_level = values[max_lag:-1]

    # Simple regression coefficient
    n_reg = len(y)
    mean_x = sum(x_level) / n_reg
    mean_y = sum(y) / n_reg

    numerator = sum((x_level[i] - mean_x) * (y[i] - mean_y) for i in range(n_reg))
    denominator = sum((x_level[i] - mean_x) ** 2 for i in range(n_reg))

    if denominator == 0:
        return {"test_statistic": 0, "critical_value_5pct": -2.86, "is_stationary": False}

    beta = numerator / denominator

    # Calculate residuals and standard error
    residuals = [y[i] - mean_y - beta * (x_level[i] - mean_x) for i in range(n_reg)]
    sse = sum(r ** 2 for r in residuals)
    se_beta = math.sqrt(sse / (n_reg - 2) / denominator) if n_reg > 2 and sse > 0 else 1

    # Test statistic
    test_stat = beta / se_beta if se_beta > 0 else 0

    # Critical value at 5% for n > 100 is approximately -2.86
    critical_value = -2.86
    is_stationary = test_stat < critical_value

    return {
        "test_statistic": round(test_stat, 4),
        "critical_value_5pct": critical_value,
        "is_stationary": is_stationary
    }


def calculate_acf(values: List[float], max_lag: int = 20) -> List[float]:
    """Calculate autocorrelation function."""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n

    if var == 0:
        return [1.0] + [0.0] * max_lag

    acf = []
    for lag in range(max_lag + 1):
        if lag == 0:
            acf.append(1.0)
        else:
            cov = sum((values[i] - mean) * (values[i - lag] - mean)
                     for i in range(lag, n)) / n
            acf.append(cov / var)

    return acf


def calculate_pacf(values: List[float], max_lag: int = 20) -> List[float]:
    """
    Calculate partial autocorrelation function using Durbin-Levinson recursion.
    """
    acf = calculate_acf(values, max_lag)

    pacf = [1.0]  # lag 0

    # Durbin-Levinson algorithm
    phi = [[0.0] * (max_lag + 1) for _ in range(max_lag + 1)]

    for k in range(1, max_lag + 1):
        # Calculate phi[k][k]
        if k == 1:
            phi[k][k] = acf[1]
        else:
            numerator = acf[k] - sum(phi[k-1][j] * acf[k-j] for j in range(1, k))
            denominator = 1 - sum(phi[k-1][j] * acf[j] for j in range(1, k))

            if abs(denominator) < 1e-10:
                phi[k][k] = 0
            else:
                phi[k][k] = numerator / denominator

        # Update other phi values
        for j in range(1, k):
            phi[k][j] = phi[k-1][j] - phi[k][k] * phi[k-1][k-j]

        pacf.append(phi[k][k])

    return pacf


# =============================================================================
# ARIMA IMPLEMENTATION
# =============================================================================

def difference_series(values: List[float], d: int = 1) -> List[float]:
    """Apply differencing d times."""
    result = values.copy()
    for _ in range(d):
        result = [result[i] - result[i-1] for i in range(1, len(result))]
    return result


def ar_forecast(
    values: List[float],
    p: int,
    n_forecast: int = 10
) -> Tuple[List[float], List[float]]:
    """
    Simple AR(p) model fitting and forecasting.
    Uses Yule-Walker equations for parameter estimation.
    """
    n = len(values)
    if n <= p:
        return [], [0.0] * p

    mean = sum(values) / n
    centered = [v - mean for v in values]

    # Calculate autocorrelations
    acf = calculate_acf(centered, p)

    # Yule-Walker: solve R * phi = r
    # R is the autocorrelation matrix, r is the autocorrelation vector

    # Build Toeplitz matrix R
    R = [[acf[abs(i - j)] for j in range(p)] for i in range(p)]
    r = acf[1:p+1]

    # Solve using simple Gaussian elimination (for small p)
    phi = solve_linear_system(R, r)

    if phi is None:
        phi = [0.0] * p

    # Forecast
    forecasts = []
    history = centered[-p:]

    for _ in range(n_forecast):
        pred = sum(phi[j] * history[-(j+1)] for j in range(p))
        forecasts.append(pred + mean)
        history.append(pred)

    return forecasts, phi


def solve_linear_system(A: List[List[float]], b: List[float]) -> Optional[List[float]]:
    """Solve Ax = b using Gaussian elimination."""
    n = len(b)

    # Augmented matrix
    aug = [A[i][:] + [b[i]] for i in range(n)]

    # Forward elimination
    for col in range(n):
        # Find pivot
        max_row = col
        for row in range(col + 1, n):
            if abs(aug[row][col]) > abs(aug[max_row][col]):
                max_row = row
        aug[col], aug[max_row] = aug[max_row], aug[col]

        if abs(aug[col][col]) < 1e-10:
            continue

        # Eliminate below
        for row in range(col + 1, n):
            factor = aug[row][col] / aug[col][col]
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]

    # Back substitution
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(aug[i][i]) < 1e-10:
            x[i] = 0
        else:
            x[i] = aug[i][n]
            for j in range(i + 1, n):
                x[i] -= aug[i][j] * x[j]
            x[i] /= aug[i][i]

    return x


def arima_forecast(
    ts: TimeSeriesData,
    p: int = 1,
    d: int = 1,
    q: int = 0,
    n_forecast: int = 14,
    confidence: float = 0.95
) -> ForecastResult:
    """
    ARIMA(p, d, q) forecasting.

    Simplified implementation:
    - Applies differencing
    - Fits AR(p) model
    - Ignores MA(q) for simplicity
    - Adds confidence intervals based on residual std
    """
    values = ts.values

    # Step 1: Difference the series
    if d > 0:
        diff_values = difference_series(values, d)
    else:
        diff_values = values

    # Step 2: Fit AR model
    forecasts_diff, phi = ar_forecast(diff_values, p, n_forecast)

    # Step 3: Inverse differencing to get original scale forecasts
    if d > 0:
        forecasts = []
        last_values = values[-d:]

        for i, f in enumerate(forecasts_diff):
            if d == 1:
                new_val = last_values[-1] + f
            else:  # d == 2
                new_val = 2 * last_values[-1] - last_values[-2] + f
            forecasts.append(new_val)
            last_values.append(new_val)
    else:
        forecasts = forecasts_diff

    # Step 4: Calculate confidence intervals
    # Estimate residual standard deviation
    fitted = []
    for i in range(p, len(diff_values)):
        pred = sum(phi[j] * diff_values[i-j-1] for j in range(p))
        fitted.append(pred)

    if fitted:
        residuals = [diff_values[i+p] - fitted[i] for i in range(len(fitted))]
        residual_std = math.sqrt(sum(r**2 for r in residuals) / len(residuals)) if residuals else 1
    else:
        residual_std = 1

    # z-score for confidence level
    z = 1.96 if confidence == 0.95 else 1.645

    # Intervals widen with forecast horizon
    lower = []
    upper = []
    for i, f in enumerate(forecasts):
        margin = z * residual_std * math.sqrt(i + 1)
        lower.append(f - margin)
        upper.append(f + margin)

    # Calculate metrics on training data
    metrics = calculate_forecast_metrics(
        actual=values[-min(20, len(values)):],
        predicted=[values[-min(20, len(values)) - 1]] * min(20, len(values))  # naive baseline
    )

    return ForecastResult(
        method=f"ARIMA({p},{d},{q})",
        predictions=forecasts,
        lower_bound=lower,
        upper_bound=upper,
        confidence_level=confidence,
        metrics=metrics
    )


# =============================================================================
# PROPHET-STYLE FORECASTING
# =============================================================================

def prophet_style_forecast(
    ts: TimeSeriesData,
    n_forecast: int = 30,
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True
) -> ForecastResult:
    """
    Prophet-style decomposable forecasting.

    y(t) = g(t) + s(t) + h(t) + epsilon

    Where:
    - g(t) = trend (piecewise linear)
    - s(t) = seasonality (Fourier series)
    - h(t) = holidays (not implemented here)
    """
    values = ts.values
    n = len(values)

    # Step 1: Fit trend using linear regression
    x = list(range(n))
    mean_x = sum(x) / n
    mean_y = sum(values) / n

    numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0
    intercept = mean_y - slope * mean_x

    trend = [intercept + slope * t for t in range(n)]

    # Step 2: Fit seasonality using Fourier series
    detrended = [values[i] - trend[i] for i in range(n)]

    # Weekly seasonality (period=7, 3 Fourier terms)
    weekly_components = []
    if weekly_seasonality:
        for k in range(1, 4):
            sin_term = [math.sin(2 * math.pi * k * i / 7) for i in range(n)]
            cos_term = [math.cos(2 * math.pi * k * i / 7) for i in range(n)]
            weekly_components.extend([sin_term, cos_term])

    # Yearly seasonality (period=365, 5 Fourier terms)
    yearly_components = []
    if yearly_seasonality:
        for k in range(1, 6):
            sin_term = [math.sin(2 * math.pi * k * i / 365) for i in range(n)]
            cos_term = [math.cos(2 * math.pi * k * i / 365) for i in range(n)]
            yearly_components.extend([sin_term, cos_term])

    # Combine seasonality components
    all_components = weekly_components + yearly_components

    # Fit seasonality coefficients using least squares (simplified)
    seasonal = [0.0] * n
    coefficients = []

    for component in all_components:
        # Simple correlation-based coefficient
        cov = sum(detrended[i] * component[i] for i in range(n)) / n
        var = sum(c ** 2 for c in component) / n
        coef = cov / var if var != 0 else 0
        coefficients.append(coef)

        for i in range(n):
            seasonal[i] += coef * component[i]

    # Step 3: Generate forecasts
    predictions = []
    for t in range(n, n + n_forecast):
        # Trend
        pred = intercept + slope * t

        # Add seasonality
        idx = 0
        if weekly_seasonality:
            for k in range(1, 4):
                pred += coefficients[idx] * math.sin(2 * math.pi * k * t / 7)
                pred += coefficients[idx + 1] * math.cos(2 * math.pi * k * t / 7)
                idx += 2

        if yearly_seasonality:
            for k in range(1, 6):
                pred += coefficients[idx] * math.sin(2 * math.pi * k * t / 365)
                pred += coefficients[idx + 1] * math.cos(2 * math.pi * k * t / 365)
                idx += 2

        predictions.append(pred)

    # Step 4: Calculate residuals for confidence intervals
    fitted = [trend[i] + seasonal[i] for i in range(n)]
    residuals = [values[i] - fitted[i] for i in range(n)]
    residual_std = math.sqrt(sum(r**2 for r in residuals) / n)

    # Confidence intervals
    z = 1.96
    lower = [p - z * residual_std * math.sqrt(1 + (i+1)/n) for i, p in enumerate(predictions)]
    upper = [p + z * residual_std * math.sqrt(1 + (i+1)/n) for i, p in enumerate(predictions)]

    # Metrics
    metrics = {
        "trend_slope": round(slope, 4),
        "residual_std": round(residual_std, 4),
        "r_squared": round(1 - sum(r**2 for r in residuals) / sum((v - mean_y)**2 for v in values), 4)
    }

    return ForecastResult(
        method="Prophet-style",
        predictions=predictions,
        lower_bound=lower,
        upper_bound=upper,
        confidence_level=0.95,
        metrics=metrics
    )


# =============================================================================
# TEMPORAL FEATURE ENGINEERING
# =============================================================================

def engineer_time_features(
    ts: TimeSeriesData,
    lag_periods: List[int] = [1, 7, 14, 28],
    rolling_windows: List[int] = [7, 14, 28],
    include_calendar: bool = True
) -> FeatureSet:
    """
    Create features from time series for ML models.
    """
    values = ts.values
    timestamps = ts.timestamps
    n = len(values)

    max_lookback = max(max(lag_periods), max(rolling_windows))

    feature_names = []
    feature_matrix = []
    target = []

    for i in range(max_lookback, n):
        features = []

        # Lag features
        for lag in lag_periods:
            features.append(values[i - lag])
            if f"lag_{lag}" not in feature_names:
                feature_names.append(f"lag_{lag}")

        # Rolling statistics
        for window in rolling_windows:
            window_values = values[i - window:i]

            # Rolling mean
            roll_mean = sum(window_values) / window
            features.append(roll_mean)
            if f"roll_mean_{window}" not in feature_names:
                feature_names.append(f"roll_mean_{window}")

            # Rolling std
            roll_std = math.sqrt(sum((v - roll_mean)**2 for v in window_values) / window)
            features.append(roll_std)
            if f"roll_std_{window}" not in feature_names:
                feature_names.append(f"roll_std_{window}")

            # Rolling min/max
            features.append(min(window_values))
            features.append(max(window_values))
            if f"roll_min_{window}" not in feature_names:
                feature_names.extend([f"roll_min_{window}", f"roll_max_{window}"])

        # Calendar features
        if include_calendar:
            try:
                dt = datetime.strptime(timestamps[i], "%Y-%m-%d")

                # Day of week (0-6)
                features.append(dt.weekday())
                if "day_of_week" not in feature_names:
                    feature_names.append("day_of_week")

                # Is weekend
                features.append(1 if dt.weekday() >= 5 else 0)
                if "is_weekend" not in feature_names:
                    feature_names.append("is_weekend")

                # Day of month
                features.append(dt.day)
                if "day_of_month" not in feature_names:
                    feature_names.append("day_of_month")

                # Month
                features.append(dt.month)
                if "month" not in feature_names:
                    feature_names.append("month")

                # Cyclical encoding for day of week
                features.append(math.sin(2 * math.pi * dt.weekday() / 7))
                features.append(math.cos(2 * math.pi * dt.weekday() / 7))
                if "dow_sin" not in feature_names:
                    feature_names.extend(["dow_sin", "dow_cos"])

                # Cyclical encoding for month
                features.append(math.sin(2 * math.pi * dt.month / 12))
                features.append(math.cos(2 * math.pi * dt.month / 12))
                if "month_sin" not in feature_names:
                    feature_names.extend(["month_sin", "month_cos"])

            except ValueError:
                # If date parsing fails, add zeros
                for _ in range(8):
                    features.append(0)

        feature_matrix.append(features)
        target.append(values[i])

    return FeatureSet(
        feature_names=feature_names,
        feature_matrix=feature_matrix,
        target=target
    )


# =============================================================================
# ANOMALY DETECTION
# =============================================================================

def detect_anomalies_zscore(
    values: List[float],
    threshold: float = 3.0,
    window: Optional[int] = None
) -> AnomalyResult:
    """
    Detect anomalies using Z-score method.

    If window is specified, uses rolling statistics.
    """
    n = len(values)
    anomaly_indices = []
    scores = []

    if window is None:
        # Global statistics
        mean = sum(values) / n
        std = math.sqrt(sum((v - mean)**2 for v in values) / n)

        for i, v in enumerate(values):
            z = abs(v - mean) / std if std > 0 else 0
            scores.append(z)
            if z > threshold:
                anomaly_indices.append(i)
    else:
        # Rolling statistics
        for i in range(n):
            start = max(0, i - window)
            end = min(n, i + window + 1)
            window_values = values[start:end]

            mean = sum(window_values) / len(window_values)
            std = math.sqrt(sum((v - mean)**2 for v in window_values) / len(window_values))

            z = abs(values[i] - mean) / std if std > 0 else 0
            scores.append(z)
            if z > threshold:
                anomaly_indices.append(i)

    return AnomalyResult(
        method="Z-Score",
        anomaly_indices=anomaly_indices,
        anomaly_scores=scores,
        threshold=threshold
    )


def detect_anomalies_iqr(values: List[float], k: float = 1.5) -> AnomalyResult:
    """
    Detect anomalies using Interquartile Range method.
    """
    sorted_values = sorted(values)
    n = len(sorted_values)

    q1_idx = n // 4
    q3_idx = 3 * n // 4

    q1 = sorted_values[q1_idx]
    q3 = sorted_values[q3_idx]
    iqr = q3 - q1

    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr

    anomaly_indices = []
    scores = []

    for i, v in enumerate(values):
        if v < lower_bound:
            score = (lower_bound - v) / iqr if iqr > 0 else 0
            anomaly_indices.append(i)
        elif v > upper_bound:
            score = (v - upper_bound) / iqr if iqr > 0 else 0
            anomaly_indices.append(i)
        else:
            score = 0
        scores.append(score)

    return AnomalyResult(
        method="IQR",
        anomaly_indices=anomaly_indices,
        anomaly_scores=scores,
        threshold=k
    )


def detect_anomalies_isolation_score(
    values: List[float],
    contamination: float = 0.05
) -> AnomalyResult:
    """
    Simplified isolation-based anomaly detection.

    Points that are far from the center of the distribution
    are more likely to be anomalies.
    """
    n = len(values)
    mean = sum(values) / n
    std = math.sqrt(sum((v - mean)**2 for v in values) / n)

    # Calculate "isolation score" based on distance from center
    scores = []
    for v in values:
        # Normalized distance from mean
        distance = abs(v - mean) / std if std > 0 else 0
        # Transform to score (higher = more anomalous)
        score = 1 - math.exp(-distance / 2)
        scores.append(score)

    # Determine threshold based on contamination
    sorted_scores = sorted(scores, reverse=True)
    threshold_idx = int(n * contamination)
    threshold = sorted_scores[threshold_idx] if threshold_idx < n else 0

    anomaly_indices = [i for i, s in enumerate(scores) if s >= threshold]

    return AnomalyResult(
        method="Isolation Score",
        anomaly_indices=anomaly_indices,
        anomaly_scores=scores,
        threshold=threshold
    )


# =============================================================================
# EVALUATION METRICS
# =============================================================================

def calculate_forecast_metrics(
    actual: List[float],
    predicted: List[float]
) -> Dict[str, float]:
    """Calculate forecasting evaluation metrics."""
    n = min(len(actual), len(predicted))

    if n == 0:
        return {"mae": 0, "rmse": 0, "mape": 0}

    errors = [actual[i] - predicted[i] for i in range(n)]
    abs_errors = [abs(e) for e in errors]
    sq_errors = [e**2 for e in errors]

    # MAE
    mae = sum(abs_errors) / n

    # RMSE
    rmse = math.sqrt(sum(sq_errors) / n)

    # MAPE (handle zeros)
    mape_terms = []
    for i in range(n):
        if actual[i] != 0:
            mape_terms.append(abs(errors[i] / actual[i]))
    mape = (sum(mape_terms) / len(mape_terms) * 100) if mape_terms else 0

    # SMAPE
    smape_terms = []
    for i in range(n):
        denom = abs(actual[i]) + abs(predicted[i])
        if denom != 0:
            smape_terms.append(2 * abs(errors[i]) / denom)
    smape = (sum(smape_terms) / len(smape_terms) * 100) if smape_terms else 0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 2),
        "smape": round(smape, 2)
    }


def walk_forward_validation(
    ts: TimeSeriesData,
    forecast_func,
    n_splits: int = 5,
    horizon: int = 7,
    min_train_size: int = 30
) -> Dict[str, float]:
    """
    Walk-forward cross-validation for time series.

    Proper time series CV that respects temporal ordering.
    """
    values = ts.values
    n = len(values)

    # Calculate split sizes
    test_size = horizon
    step_size = (n - min_train_size - test_size) // n_splits

    all_metrics = {"mae": [], "rmse": [], "mape": []}

    for i in range(n_splits):
        train_end = min_train_size + i * step_size
        test_end = train_end + test_size

        if test_end > n:
            break

        # Create training data
        train_ts = TimeSeriesData(
            name=ts.name,
            points=ts.points[:train_end],
            frequency=ts.frequency
        )

        # Generate forecast
        result = forecast_func(train_ts, horizon)

        # Get actual values
        actual = values[train_end:test_end]
        predicted = result.predictions[:len(actual)]

        # Calculate metrics
        metrics = calculate_forecast_metrics(actual, predicted)

        all_metrics["mae"].append(metrics["mae"])
        all_metrics["rmse"].append(metrics["rmse"])
        all_metrics["mape"].append(metrics["mape"])

    # Average metrics
    return {
        "mean_mae": round(sum(all_metrics["mae"]) / len(all_metrics["mae"]), 4) if all_metrics["mae"] else 0,
        "mean_rmse": round(sum(all_metrics["rmse"]) / len(all_metrics["rmse"]), 4) if all_metrics["rmse"] else 0,
        "mean_mape": round(sum(all_metrics["mape"]) / len(all_metrics["mape"]), 2) if all_metrics["mape"] else 0,
        "n_splits": len(all_metrics["mae"])
    }


# =============================================================================
# VISUALIZATION (ASCII)
# =============================================================================

def plot_time_series_ascii(
    values: List[float],
    title: str = "Time Series",
    width: int = 60,
    height: int = 15,
    forecast: Optional[List[float]] = None,
    anomaly_indices: Optional[List[int]] = None
) -> str:
    """Create ASCII plot of time series."""
    all_values = values + (forecast if forecast else [])
    min_val = min(all_values)
    max_val = max(all_values)
    val_range = max_val - min_val

    if val_range == 0:
        val_range = 1

    # Create canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot historical values
    n_hist = len(values)
    for i, v in enumerate(values):
        x = int(i * (width - 1) / len(all_values))
        y = int((max_val - v) / val_range * (height - 1))
        y = max(0, min(height - 1, y))

        if anomaly_indices and i in anomaly_indices:
            canvas[y][x] = '!'
        else:
            canvas[y][x] = '*'

    # Plot forecast
    if forecast:
        for i, v in enumerate(forecast):
            x = int((n_hist + i) * (width - 1) / len(all_values))
            y = int((max_val - v) / val_range * (height - 1))
            y = max(0, min(height - 1, y))
            canvas[y][x] = 'o'

    # Build output
    lines = [title.center(width)]
    lines.append('─' * width)

    for row in canvas:
        lines.append('│' + ''.join(row) + '│')

    lines.append('─' * width)
    lines.append(f"Range: [{min_val:.1f}, {max_val:.1f}]")

    if forecast:
        lines.append("* = Historical, o = Forecast, ! = Anomaly")

    return '\n'.join(lines)


def plot_decomposition_ascii(decomp: DecompositionResult, width: int = 50) -> str:
    """Create ASCII visualization of decomposition."""
    lines = ["TIME SERIES DECOMPOSITION".center(width)]
    lines.append("=" * width)

    components = [
        ("TREND", decomp.trend),
        ("SEASONAL", decomp.seasonal),
        ("RESIDUAL", decomp.residual)
    ]

    for name, values in components:
        # Filter out NaN values
        valid_values = [v for v in values if not math.isnan(v)]
        if not valid_values:
            continue

        min_val = min(valid_values)
        max_val = max(valid_values)
        mean_val = sum(valid_values) / len(valid_values)

        lines.append(f"\n{name}:")
        lines.append(f"  Min: {min_val:.2f}")
        lines.append(f"  Max: {max_val:.2f}")
        lines.append(f"  Mean: {mean_val:.2f}")

        # Simple sparkline
        if max_val > min_val:
            sparkline = ""
            for v in valid_values[-min(30, len(valid_values)):]:
                normalized = (v - min_val) / (max_val - min_val)
                if normalized < 0.25:
                    sparkline += "▁"
                elif normalized < 0.5:
                    sparkline += "▃"
                elif normalized < 0.75:
                    sparkline += "▅"
                else:
                    sparkline += "▇"
            lines.append(f"  Last 30: {sparkline}")

    return '\n'.join(lines)


def plot_acf_ascii(acf_values: List[float], title: str = "ACF", width: int = 50) -> str:
    """Create ASCII plot of ACF/PACF."""
    lines = [title.center(width)]
    lines.append("=" * width)

    max_bar_width = 30

    for lag, val in enumerate(acf_values[:15]):
        bar_width = int(abs(val) * max_bar_width)
        if val >= 0:
            bar = '█' * bar_width
            line = f"Lag {lag:2d}: [{bar:<{max_bar_width}}] {val:+.3f}"
        else:
            bar = '█' * bar_width
            line = f"Lag {lag:2d}: [{' ' * (max_bar_width - bar_width)}{bar}] {val:+.3f}"
        lines.append(line)

    # Significance bounds (approximate)
    sig_bound = 1.96 / math.sqrt(len(acf_values) * 5)
    lines.append(f"\n95% significance bounds: ±{sig_bound:.3f}")

    return '\n'.join(lines)


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_decomposition():
    """Demo 1: Time Series Decomposition"""
    print("\n" + "=" * 70)
    print("DEMO 1: TIME SERIES DECOMPOSITION")
    print("=" * 70)

    print("\n📊 Generating synthetic time series with trend and seasonality...")
    ts = generate_synthetic_time_series(
        n_points=180,
        trend_slope=0.15,
        seasonal_period=7,
        seasonal_amplitude=10,
        noise_std=3
    )

    print(f"   Generated {len(ts)} data points")
    print(f"   Date range: {ts.timestamps[0]} to {ts.timestamps[-1]}")
    print(f"   Value range: {min(ts.values):.2f} to {max(ts.values):.2f}")

    # Plot raw series
    print("\n" + plot_time_series_ascii(ts.values[:60], "RAW TIME SERIES (first 60 points)", width=60))

    # Decompose
    print("\n📈 Performing classical decomposition (period=7)...")
    decomp = decompose_time_series(ts, period=7)

    print(plot_decomposition_ascii(decomp))

    # Calculate ACF and PACF
    print("\n📉 Calculating autocorrelation functions...")
    acf = calculate_acf(ts.values, max_lag=14)
    pacf = calculate_pacf(ts.values, max_lag=14)

    print(plot_acf_ascii(acf, "AUTOCORRELATION FUNCTION (ACF)"))
    print()
    print(plot_acf_ascii(pacf, "PARTIAL AUTOCORRELATION (PACF)"))

    # Stationarity test
    print("\n🔬 Testing for stationarity (ADF test)...")
    adf_result = adf_test_simple(ts.values)

    print(f"   Test statistic: {adf_result['test_statistic']}")
    print(f"   Critical value (5%): {adf_result['critical_value_5pct']}")
    print(f"   Is stationary: {'✅ Yes' if adf_result['is_stationary'] else '❌ No'}")

    if not adf_result['is_stationary']:
        print("\n   Testing first difference...")
        diff_values = difference_series(ts.values, d=1)
        adf_diff = adf_test_simple(diff_values)
        print(f"   After differencing: {'✅ Stationary' if adf_diff['is_stationary'] else '❌ Still non-stationary'}")

    print("\n✅ Decomposition demo complete!")

    return {
        "n_points": len(ts),
        "decomposition_period": 7,
        "is_stationary": adf_result['is_stationary'],
        "acf_lag_1": round(acf[1], 4),
        "trend_present": True
    }


def demo_2_arima_forecast():
    """Demo 2: ARIMA Forecasting"""
    print("\n" + "=" * 70)
    print("DEMO 2: ARIMA FORECASTING")
    print("=" * 70)

    print("\n📊 Generating time series data...")
    ts = generate_sales_data(n_days=200)

    # Split into train/test
    train_size = 180
    train_ts = TimeSeriesData(
        name=ts.name,
        points=ts.points[:train_size],
        frequency=ts.frequency
    )
    test_values = ts.values[train_size:]

    print(f"   Training points: {train_size}")
    print(f"   Test points: {len(test_values)}")

    # Determine ARIMA parameters
    print("\n🔍 Analyzing series for ARIMA parameters...")

    acf = calculate_acf(train_ts.values, max_lag=10)
    pacf = calculate_pacf(train_ts.values, max_lag=10)

    # Simple heuristic for p and q
    p = sum(1 for i, v in enumerate(pacf[1:6]) if abs(v) > 0.2)
    q = sum(1 for i, v in enumerate(acf[1:6]) if abs(v) > 0.2)
    p = max(1, min(p, 3))
    q = max(0, min(q, 2))

    print(f"   Suggested parameters: ARIMA({p}, 1, {q})")

    # Test different ARIMA configurations
    print("\n📈 Testing ARIMA configurations...")

    configs = [
        (1, 1, 0),
        (2, 1, 0),
        (1, 1, 1),
        (p, 1, q)
    ]

    results = []
    for p_i, d_i, q_i in configs:
        print(f"\n   Testing ARIMA({p_i},{d_i},{q_i})...")

        result = arima_forecast(
            train_ts,
            p=p_i, d=d_i, q=q_i,
            n_forecast=len(test_values)
        )

        metrics = calculate_forecast_metrics(test_values, result.predictions)

        print(f"   MAE: {metrics['mae']:.2f}, RMSE: {metrics['rmse']:.2f}, MAPE: {metrics['mape']:.1f}%")

        results.append({
            "config": f"ARIMA({p_i},{d_i},{q_i})",
            "mae": metrics['mae'],
            "rmse": metrics['rmse'],
            "mape": metrics['mape']
        })

    # Best model
    best = min(results, key=lambda x: x['mae'])
    print(f"\n🏆 Best model: {best['config']} (MAE: {best['mae']:.2f})")

    # Generate final forecast
    print("\n📊 Generating forecast with best model...")
    best_p, best_d, best_q = [int(x) for x in best['config'].replace('ARIMA(', '').replace(')', '').split(',')]

    final_result = arima_forecast(
        train_ts,
        p=best_p, d=best_d, q=best_q,
        n_forecast=20
    )

    print(plot_time_series_ascii(
        train_ts.values[-40:],
        f"HISTORICAL + FORECAST ({best['config']})",
        width=60,
        forecast=final_result.predictions
    ))

    print(f"\n   Forecast for next 5 days:")
    for i in range(5):
        print(f"   Day {i+1}: {final_result.predictions[i]:.2f} "
              f"[{final_result.lower_bound[i]:.2f}, {final_result.upper_bound[i]:.2f}]")

    print("\n✅ ARIMA forecasting demo complete!")

    return {
        "best_model": best['config'],
        "mae": best['mae'],
        "rmse": best['rmse'],
        "forecast_horizon": 20,
        "configs_tested": len(configs)
    }


def demo_3_feature_engineering():
    """Demo 3: Temporal Feature Engineering"""
    print("\n" + "=" * 70)
    print("DEMO 3: TEMPORAL FEATURE ENGINEERING")
    print("=" * 70)

    print("\n📊 Generating time series data...")
    ts = generate_sales_data(n_days=120)

    print(f"   Data points: {len(ts)}")

    # Engineer features
    print("\n🔧 Engineering temporal features...")

    features = engineer_time_features(
        ts,
        lag_periods=[1, 7, 14],
        rolling_windows=[7, 14],
        include_calendar=True
    )

    print(f"\n   Created {len(features.feature_names)} features:")

    # Group features by type
    lag_features = [f for f in features.feature_names if f.startswith('lag_')]
    roll_features = [f for f in features.feature_names if f.startswith('roll_')]
    calendar_features = [f for f in features.feature_names if not f.startswith(('lag_', 'roll_'))]

    print(f"\n   📅 LAG FEATURES ({len(lag_features)}):")
    for f in lag_features:
        print(f"      - {f}")

    print(f"\n   📊 ROLLING FEATURES ({len(roll_features)}):")
    for f in roll_features:
        print(f"      - {f}")

    print(f"\n   🗓️ CALENDAR FEATURES ({len(calendar_features)}):")
    for f in calendar_features:
        print(f"      - {f}")

    # Show sample features
    print("\n   📋 SAMPLE FEATURE MATRIX (last 5 rows):")
    print(f"   {'Feature':<15} " + " ".join(f"{features.feature_names[j]:<12}" for j in range(min(6, len(features.feature_names)))))
    print("   " + "-" * 90)

    for i in range(-5, 0):
        row = features.feature_matrix[i]
        target = features.target[i]
        values_str = " ".join(f"{row[j]:<12.2f}" for j in range(min(6, len(row))))
        print(f"   Row {len(features.feature_matrix)+i+1:<8} {values_str} → Target: {target:.2f}")

    # Feature importance analysis (correlation with target)
    print("\n📈 FEATURE IMPORTANCE (correlation with target):")

    correlations = []
    for j, name in enumerate(features.feature_names):
        feature_values = [row[j] for row in features.feature_matrix]

        mean_f = sum(feature_values) / len(feature_values)
        mean_t = sum(features.target) / len(features.target)

        cov = sum((feature_values[i] - mean_f) * (features.target[i] - mean_t)
                  for i in range(len(features.target))) / len(features.target)

        std_f = math.sqrt(sum((f - mean_f)**2 for f in feature_values) / len(feature_values))
        std_t = math.sqrt(sum((t - mean_t)**2 for t in features.target) / len(features.target))

        corr = cov / (std_f * std_t) if std_f > 0 and std_t > 0 else 0
        correlations.append((name, corr))

    # Sort by absolute correlation
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)

    print("\n   Top 10 most correlated features:")
    for name, corr in correlations[:10]:
        bar = '█' * int(abs(corr) * 20)
        sign = '+' if corr > 0 else '-'
        print(f"   {name:<20} [{bar:<20}] {sign}{abs(corr):.3f}")

    print("\n💡 KEY INSIGHT:")
    print("   Lag features (especially lag_1 and lag_7) typically have")
    print("   the highest correlation with the target in time series!")

    print("\n✅ Feature engineering demo complete!")

    return {
        "total_features": len(features.feature_names),
        "lag_features": len(lag_features),
        "rolling_features": len(roll_features),
        "calendar_features": len(calendar_features),
        "top_feature": correlations[0][0],
        "top_correlation": round(correlations[0][1], 4)
    }


def demo_4_anomaly_detection():
    """Demo 4: Anomaly Detection"""
    print("\n" + "=" * 70)
    print("DEMO 4: ANOMALY DETECTION")
    print("=" * 70)

    print("\n📊 Generating time series with anomalies...")
    ts = generate_synthetic_time_series(
        n_points=100,
        trend_slope=0.05,
        seasonal_period=7,
        seasonal_amplitude=5,
        noise_std=2,
        add_anomalies=True,
        anomaly_count=8
    )

    print(f"   Data points: {len(ts)}")

    # Method 1: Z-Score
    print("\n🔍 METHOD 1: Z-SCORE DETECTION")
    zscore_result = detect_anomalies_zscore(ts.values, threshold=2.5)

    print(f"   Threshold: {zscore_result.threshold} standard deviations")
    print(f"   Anomalies found: {len(zscore_result.anomaly_indices)}")
    if zscore_result.anomaly_indices:
        print(f"   Anomaly indices: {zscore_result.anomaly_indices[:10]}...")

    # Method 2: Rolling Z-Score
    print("\n🔍 METHOD 2: ROLLING Z-SCORE (window=14)")
    rolling_result = detect_anomalies_zscore(ts.values, threshold=2.5, window=14)

    print(f"   Anomalies found: {len(rolling_result.anomaly_indices)}")
    if rolling_result.anomaly_indices:
        print(f"   Anomaly indices: {rolling_result.anomaly_indices[:10]}...")

    # Method 3: IQR
    print("\n🔍 METHOD 3: IQR METHOD")
    iqr_result = detect_anomalies_iqr(ts.values, k=1.5)

    print(f"   Multiplier: {iqr_result.threshold}")
    print(f"   Anomalies found: {len(iqr_result.anomaly_indices)}")
    if iqr_result.anomaly_indices:
        print(f"   Anomaly indices: {iqr_result.anomaly_indices[:10]}...")

    # Method 4: Isolation Score
    print("\n🔍 METHOD 4: ISOLATION SCORE")
    isolation_result = detect_anomalies_isolation_score(ts.values, contamination=0.08)

    print(f"   Contamination: 8%")
    print(f"   Score threshold: {isolation_result.threshold:.4f}")
    print(f"   Anomalies found: {len(isolation_result.anomaly_indices)}")

    # Plot with anomalies highlighted
    print("\n" + plot_time_series_ascii(
        ts.values,
        "TIME SERIES WITH ANOMALIES (! = detected)",
        width=60,
        anomaly_indices=zscore_result.anomaly_indices
    ))

    # Comparison
    print("\n📊 METHOD COMPARISON:")
    print("   " + "-" * 50)
    print(f"   {'Method':<25} {'Anomalies':<15}")
    print("   " + "-" * 50)
    print(f"   {'Z-Score (global)':<25} {len(zscore_result.anomaly_indices):<15}")
    print(f"   {'Z-Score (rolling)':<25} {len(rolling_result.anomaly_indices):<15}")
    print(f"   {'IQR':<25} {len(iqr_result.anomaly_indices):<15}")
    print(f"   {'Isolation Score':<25} {len(isolation_result.anomaly_indices):<15}")

    # Agreement analysis
    all_detected = set(zscore_result.anomaly_indices) | set(rolling_result.anomaly_indices) | \
                   set(iqr_result.anomaly_indices) | set(isolation_result.anomaly_indices)

    consensus = set(zscore_result.anomaly_indices) & set(iqr_result.anomaly_indices) & \
                set(isolation_result.anomaly_indices)

    print(f"\n   Total unique anomalies detected: {len(all_detected)}")
    print(f"   Detected by all methods: {len(consensus)}")

    if consensus:
        print(f"   High-confidence anomalies: {sorted(consensus)[:5]}...")

    print("\n💡 KEY INSIGHT:")
    print("   Different methods have different strengths:")
    print("   - Z-Score: Good for normally distributed data")
    print("   - Rolling Z-Score: Adapts to local patterns")
    print("   - IQR: Robust to outliers in the data itself")
    print("   - Isolation: Good for complex distributions")

    print("\n✅ Anomaly detection demo complete!")

    return {
        "zscore_anomalies": len(zscore_result.anomaly_indices),
        "rolling_anomalies": len(rolling_result.anomaly_indices),
        "iqr_anomalies": len(iqr_result.anomaly_indices),
        "isolation_anomalies": len(isolation_result.anomaly_indices),
        "consensus_anomalies": len(consensus)
    }


def demo_5_full_report():
    """Demo 5: Full Forecasting Report"""
    print("\n" + "=" * 70)
    print("DEMO 5: COMPREHENSIVE TIME SERIES REPORT")
    print("=" * 70)

    print("\n📊 Generating realistic sales data...")
    ts = generate_sales_data(n_days=180)

    # Split data
    train_size = 150
    train_ts = TimeSeriesData(
        name=ts.name,
        points=ts.points[:train_size],
        frequency=ts.frequency
    )
    test_values = ts.values[train_size:]

    print(f"   Training: {train_size} days")
    print(f"   Testing: {len(test_values)} days")

    report = {
        "data_summary": {
            "total_points": len(ts),
            "train_size": train_size,
            "test_size": len(test_values),
            "date_range": f"{ts.timestamps[0]} to {ts.timestamps[-1]}"
        }
    }

    # Section 1: Data Analysis
    print("\n" + "─" * 70)
    print("SECTION 1: DATA ANALYSIS")
    print("─" * 70)

    decomp = decompose_time_series(train_ts, period=7)

    valid_trend = [t for t in decomp.trend if not math.isnan(t)]
    trend_slope = (valid_trend[-1] - valid_trend[0]) / len(valid_trend) if valid_trend else 0

    print(f"\n   ✅ Trend: {'Upward' if trend_slope > 0 else 'Downward'} ({trend_slope:.2f}/day)")
    print(f"   ✅ Seasonality: Weekly (period=7)")

    adf = adf_test_simple(train_ts.values)
    print(f"   ✅ Stationarity: {'Stationary' if adf['is_stationary'] else 'Non-stationary'}")

    report["analysis"] = {
        "trend_direction": "upward" if trend_slope > 0 else "downward",
        "trend_slope_per_day": round(trend_slope, 4),
        "is_stationary": adf["is_stationary"]
    }

    # Section 2: Forecasting Models
    print("\n" + "─" * 70)
    print("SECTION 2: FORECASTING MODEL COMPARISON")
    print("─" * 70)

    models_results = []

    # ARIMA
    print("\n   Testing ARIMA(1,1,0)...")
    arima_result = arima_forecast(train_ts, p=1, d=1, q=0, n_forecast=len(test_values))
    arima_metrics = calculate_forecast_metrics(test_values, arima_result.predictions)
    models_results.append(("ARIMA(1,1,0)", arima_metrics))
    print(f"   MAE: {arima_metrics['mae']:.2f}, MAPE: {arima_metrics['mape']:.1f}%")

    # Prophet-style
    print("\n   Testing Prophet-style...")
    prophet_result = prophet_style_forecast(train_ts, n_forecast=len(test_values))
    prophet_metrics = calculate_forecast_metrics(test_values, prophet_result.predictions)
    models_results.append(("Prophet-style", prophet_metrics))
    print(f"   MAE: {prophet_metrics['mae']:.2f}, MAPE: {prophet_metrics['mape']:.1f}%")

    # Naive (baseline)
    naive_forecast = [train_ts.values[-1]] * len(test_values)
    naive_metrics = calculate_forecast_metrics(test_values, naive_forecast)
    models_results.append(("Naive (baseline)", naive_metrics))
    print(f"\n   Naive baseline: MAE: {naive_metrics['mae']:.2f}, MAPE: {naive_metrics['mape']:.1f}%")

    # Seasonal Naive
    seasonal_naive = [train_ts.values[-7 + (i % 7)] for i in range(len(test_values))]
    seasonal_metrics = calculate_forecast_metrics(test_values, seasonal_naive)
    models_results.append(("Seasonal Naive", seasonal_metrics))
    print(f"   Seasonal naive: MAE: {seasonal_metrics['mae']:.2f}, MAPE: {seasonal_metrics['mape']:.1f}%")

    # Comparison table
    print("\n   " + "─" * 55)
    print(f"   {'Model':<20} {'MAE':<10} {'RMSE':<10} {'MAPE':<10}")
    print("   " + "─" * 55)

    for name, metrics in sorted(models_results, key=lambda x: x[1]['mae']):
        print(f"   {name:<20} {metrics['mae']:<10.2f} {metrics['rmse']:<10.2f} {metrics['mape']:<10.1f}%")

    best_model = min(models_results, key=lambda x: x[1]['mae'])
    print(f"\n   🏆 Best model: {best_model[0]}")

    report["models"] = {m[0]: m[1] for m in models_results}
    report["best_model"] = best_model[0]

    # Section 3: Feature Analysis
    print("\n" + "─" * 70)
    print("SECTION 3: FEATURE IMPORTANCE")
    print("─" * 70)

    features = engineer_time_features(train_ts, lag_periods=[1, 7], rolling_windows=[7])

    correlations = []
    for j, name in enumerate(features.feature_names):
        feature_values = [row[j] for row in features.feature_matrix]

        mean_f = sum(feature_values) / len(feature_values)
        mean_t = sum(features.target) / len(features.target)

        cov = sum((feature_values[i] - mean_f) * (features.target[i] - mean_t)
                  for i in range(len(features.target))) / len(features.target)

        std_f = math.sqrt(sum((f - mean_f)**2 for f in feature_values) / len(feature_values))
        std_t = math.sqrt(sum((t - mean_t)**2 for t in features.target) / len(features.target))

        corr = cov / (std_f * std_t) if std_f > 0 and std_t > 0 else 0
        correlations.append((name, corr))

    correlations.sort(key=lambda x: abs(x[1]), reverse=True)

    print("\n   Top 5 predictive features:")
    for name, corr in correlations[:5]:
        bar = '█' * int(abs(corr) * 15)
        print(f"   {name:<20} [{bar:<15}] {corr:+.3f}")

    report["top_features"] = [{"name": n, "correlation": round(c, 4)} for n, c in correlations[:5]]

    # Section 4: Anomaly Detection
    print("\n" + "─" * 70)
    print("SECTION 4: ANOMALY DETECTION")
    print("─" * 70)

    zscore_result = detect_anomalies_zscore(train_ts.values, threshold=2.5)

    print(f"\n   Z-Score method (threshold=2.5σ):")
    print(f"   Anomalies detected: {len(zscore_result.anomaly_indices)}")

    if zscore_result.anomaly_indices:
        print(f"   Anomaly dates: ", end="")
        for idx in zscore_result.anomaly_indices[:5]:
            print(f"{train_ts.timestamps[idx]}, ", end="")
        print("...")

    report["anomalies"] = {
        "method": "Z-Score",
        "threshold": 2.5,
        "count": len(zscore_result.anomaly_indices)
    }

    # Section 5: Final Recommendations
    print("\n" + "─" * 70)
    print("SECTION 5: RECOMMENDATIONS")
    print("─" * 70)

    print("\n   📋 Based on analysis:")
    print(f"   1. Use {best_model[0]} for forecasting (lowest MAE)")
    print(f"   2. Most important feature: {correlations[0][0]}")
    print(f"   3. Data shows {'strong' if abs(trend_slope) > 0.1 else 'weak'} trend")
    print(f"   4. Monitor {len(zscore_result.anomaly_indices)} detected anomaly periods")

    # Save report
    storage_dir = ".time_series_toolkit"
    os.makedirs(storage_dir, exist_ok=True)

    report_file = os.path.join(storage_dir, "forecast_report.json")

    # Make report JSON serializable
    serializable_report = {
        "timestamp": datetime.now().isoformat(),
        "data_summary": report["data_summary"],
        "analysis": report["analysis"],
        "models": report["models"],
        "best_model": report["best_model"],
        "top_features": report["top_features"],
        "anomalies": report["anomalies"]
    }

    with open(report_file, 'w') as f:
        json.dump(serializable_report, f, indent=2)

    print(f"\n   📁 Report saved to: {report_file}")

    print("\n" + "=" * 70)
    print("✅ COMPREHENSIVE REPORT COMPLETE!")
    print("=" * 70)

    return serializable_report


# =============================================================================
# MAIN
# =============================================================================

def print_usage():
    """Print usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           MODULE 38: TIME SERIES FORECASTING TOOLKIT                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  A comprehensive toolkit for time series analysis and forecasting.            ║
║                                                                               ║
║  USAGE:                                                                       ║
║    python deliverable_time_series_toolkit.py <demo>                           ║
║                                                                               ║
║  DEMOS:                                                                       ║
║    demo1  - Time series decomposition (trend, seasonal, residual)             ║
║    demo2  - ARIMA forecasting with model selection                            ║
║    demo3  - Temporal feature engineering for ML                               ║
║    demo4  - Anomaly detection methods                                         ║
║    demo5  - Full forecasting report                                           ║
║                                                                               ║
║  EXAMPLES:                                                                    ║
║    python deliverable_time_series_toolkit.py demo1                            ║
║    python deliverable_time_series_toolkit.py demo5                            ║
║                                                                               ║
║  KEY CONCEPTS:                                                                ║
║    • Decomposition: Separate trend, seasonality, residuals                    ║
║    • Stationarity: Required for ARIMA, test with ADF                          ║
║    • ARIMA: Classical statistical forecasting                                 ║
║    • Prophet: Decomposable model with holidays                                ║
║    • Feature Engineering: Lags, rolling stats, calendar features              ║
║    • Anomaly Detection: Z-score, IQR, isolation methods                       ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_decomposition,
        "demo2": demo_2_arima_forecast,
        "demo3": demo_3_feature_engineering,
        "demo4": demo_4_anomaly_detection,
        "demo5": demo_5_full_report
    }

    if command in demos:
        result = demos[command]()
        print(f"\n📊 Demo result: {json.dumps(result, indent=2)}")
    elif command == "help":
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
