# Module 38 Deliverable: Time Series Forecasting Toolkit

**Master time series analysis from classical ARIMA to modern techniques.**

## Features

- Time series decomposition (trend, seasonality, residual)
- ARIMA/SARIMA implementation from scratch
- Prophet-style forecasting
- Temporal feature engineering for ML
- Multiple anomaly detection methods
- Walk-forward cross-validation
- ASCII visualization

## Quick Start

```bash
python deliverable_time_series_toolkit.py demo1  # Decomposition
python deliverable_time_series_toolkit.py demo2  # ARIMA forecasting
python deliverable_time_series_toolkit.py demo3  # Feature engineering
python deliverable_time_series_toolkit.py demo4  # Anomaly detection
python deliverable_time_series_toolkit.py demo5  # Full report
```

## Demos

### Demo 1: Time Series Decomposition
Decompose a time series into its fundamental components:
- **Trend**: Long-term direction (up/down)
- **Seasonality**: Repeating patterns (weekly, yearly)
- **Residual**: Random noise after removing trend and seasonality

Also calculates ACF/PACF and performs stationarity testing.

### Demo 2: ARIMA Forecasting
Implements ARIMA from scratch:
- Differencing for stationarity
- AR(p) parameter estimation via Yule-Walker
- Model selection comparing multiple configurations
- Confidence intervals for forecasts

### Demo 3: Feature Engineering
Creates ML-ready features from time series:
- **Lag features**: Values from 1, 7, 14, 28 days ago
- **Rolling statistics**: Mean, std, min, max over windows
- **Calendar features**: Day of week, month, cyclical encodings
- Feature importance analysis via correlation

### Demo 4: Anomaly Detection
Multiple methods to detect unusual patterns:
- **Z-Score**: Global standard deviation threshold
- **Rolling Z-Score**: Local adaptive detection
- **IQR Method**: Robust to outliers
- **Isolation Score**: Distance-based detection

### Demo 5: Full Report
Comprehensive analysis including:
- Data analysis and stationarity
- Model comparison (ARIMA, Prophet, baselines)
- Feature importance ranking
- Anomaly detection
- Recommendations

## Key Concepts

### Time Series Components
```
y(t) = Trend + Seasonality + Residual

Trend:      ╱╱╱ (long-term direction)
Seasonality: ∿∿∿ (repeating patterns)
Residual:   ∼∼∼ (random noise)
```

### ARIMA(p, d, q)
- **p**: AutoRegressive order (how many lags)
- **d**: Differencing order (for stationarity)
- **q**: Moving Average order (error terms)

### Feature Engineering for Time Series
```
Raw timestamp → Multiple features:
├── Lag features (yesterday, last week)
├── Rolling stats (7-day average, std)
├── Calendar (day of week, month)
└── Cyclical (sin/cos encodings)
```

## Forecasting Methods Compared

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| ARIMA | Single series, clear patterns | Interpretable, fast | Requires stationarity |
| Prophet | Business data with holidays | Easy to use, robust | Less flexible |
| Seasonal Naive | Strong seasonality | Simple baseline | Ignores trend |
| ML + Features | Complex patterns | Flexible | Needs more data |

## Anomaly Detection Methods

| Method | Description | Best For |
|--------|-------------|----------|
| Z-Score | Distance from mean in std devs | Normal distributions |
| Rolling Z-Score | Local statistics | Non-stationary series |
| IQR | Quartile-based bounds | Skewed distributions |
| Isolation | Distance-based scoring | Complex patterns |

## Example Output

```
DEMO 2: ARIMA FORECASTING
══════════════════════════════════════════════════════

📊 Generating time series data...
   Training points: 180
   Test points: 20

📈 Testing ARIMA configurations...

   Testing ARIMA(1,1,0)...
   MAE: 52.34, RMSE: 67.89, MAPE: 4.2%

   Testing ARIMA(2,1,0)...
   MAE: 48.91, RMSE: 63.45, MAPE: 3.9%

🏆 Best model: ARIMA(2,1,0) (MAE: 48.91)
```

## Dependencies

```
# No external dependencies required!
# Pure Python implementation using only:
# - math
# - random
# - json
# - datetime
# - dataclasses
```

## Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| MAE | mean(\|actual - pred\|) | Average error magnitude |
| RMSE | sqrt(mean((actual - pred)²)) | Penalizes large errors |
| MAPE | mean(\|error/actual\|) × 100% | Percentage error |
| SMAPE | Symmetric MAPE | Handles zeros better |

## Walk-Forward Validation

Proper time series cross-validation:
```
Fold 1: Train [▓▓▓░░░░░] Test [▓░░░░░░░]
Fold 2: Train [▓▓▓▓░░░░] Test [░▓░░░░░░]
Fold 3: Train [▓▓▓▓▓░░░] Test [░░▓░░░░░]
─────────────────────────────────────────→ time

Always train on PAST, test on FUTURE!
```

---

**Time**: ~7-8 hours | **Lines**: 1400+ | **Author**: Neural Dojo
