# Module 38: Time Series & Forecasting

**Last Updated**: 2025-11-28
**Status**: In Progress
**Duration**: 7-8 hours

---

## Learning Objectives

By the end of this module, you will:
- Understand time series fundamentals (stationarity, seasonality, trends)
- Master classical forecasting methods (ARIMA, Prophet)
- Build deep learning time series models (LSTM, Transformers)
- Implement temporal feature engineering
- Build anomaly detection systems for time series data

---

## Why Time Series Matters

Imagine you're a weather forecaster in ancient Egypt, watching the Nile's water levels. Each year, the river floods, bringing life-giving water to crops. But when will it flood? How high will it rise? Your entire civilization depends on predicting a pattern that repeats over time.

This is time series analysis - finding patterns in sequential data to predict the future. And it's everywhere:

```
Where Time Series Lives:
├── Finance
│   ├── Stock prices (hourly, daily)
│   ├── Trading volumes
│   └── Economic indicators
├── Operations
│   ├── Server load prediction
│   ├── Inventory forecasting
│   └── Energy demand
├── IoT & Sensors
│   ├── Temperature monitoring
│   ├── Equipment vibration
│   └── Network traffic
└── Business
    ├── Sales forecasting
    ├── Customer demand
    └── Resource planning
```

**Did You Know?** Amazon's demand forecasting system processes over 300 million time series daily. Each product in each warehouse is a separate time series. Getting forecasts right by just 1% accuracy improvement saved them over $100 million annually in inventory costs!

---

## The Anatomy of Time Series

### What Makes Time Series Special?

Unlike regular tabular data where rows are independent, time series has a crucial property: **temporal dependency**. Today's value depends on yesterday's value, which depends on the day before, and so on.

```
Regular Data vs Time Series:

REGULAR TABULAR DATA:
┌─────────────────────────────────────┐
│  Row 1: [features] → [label]        │  Each row is independent
│  Row 2: [features] → [label]        │  Order doesn't matter
│  Row 3: [features] → [label]        │  Shuffle = same model
└─────────────────────────────────────┘

TIME SERIES DATA:
┌─────────────────────────────────────┐
│  t=1: value₁ ────────────┐          │
│  t=2: value₂ ←───────────┤          │  Each depends on past
│  t=3: value₃ ←───────────┤          │  Order is EVERYTHING
│  t=4: value₄ ←───────────┘          │  Shuffle = destroy data
└─────────────────────────────────────┘
```

### The Three Components of Time Series

Every time series can be decomposed into three fundamental components:

```
TIME SERIES = TREND + SEASONALITY + RESIDUAL

               Original Signal
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
  TREND        SEASONALITY      RESIDUAL
(long-term)   (repeating)     (random noise)
    │               │               │
    │               │               │
    ▼               ▼               ▼
  ╱              ╱╲╱╲            ∼∼∼∼
 ╱              ╱  ╲ ╱          ∼  ∼
╱              ╱    ╲          ∼    ∼


Example: Retail Sales
─────────────────────
TREND: Sales growing 5% per year (business expansion)
SEASONALITY: Spikes every December (holiday shopping)
RESIDUAL: Random day-to-day variation
```

**The Grocery Store Analogy**: Imagine tracking daily milk sales:
- **Trend**: Sales slowly increasing as neighborhood population grows
- **Seasonality**: Higher on weekends (families cook more), lower mid-week
- **Weekly pattern**: People buy on payday (biweekly)
- **Residual**: Random - maybe a recipe went viral on TikTok today

---

## Stationarity: The Foundation of Forecasting

### What is Stationarity?

A time series is **stationary** if its statistical properties don't change over time. Think of it like a calm lake versus a river flowing to the ocean.

```
STATIONARY (Like a Calm Lake):
─────────────────────────────
Statistical properties stay constant over time.
Mean: μ ≈ constant
Variance: σ² ≈ constant
Autocorrelation: same pattern

       ──────────────────────────
      ╱╲  ╱╲  ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
     ╱  ╲╱  ╲╱  ╲╱  ╲╱  ╲╱  ╲╱  ╲
    ──────────────────────────────


NON-STATIONARY (Like a River to Ocean):
───────────────────────────────────────
Properties change over time.
Mean: drifting up or down
Variance: expanding or contracting

                            ╱╲
                          ╱╲╱ ╲
                      ╱╲╱╲╱    ╲╱╲
                 ╱╲╱╲╱              ╲
         ╱╲╱╲╱╲╱                     ╲
    ╱╲╱╲╱
   ╱
```

### Why Stationarity Matters

Most classical forecasting methods **require** stationarity. Here's why:

```python
# Non-stationary: Yesterday's patterns don't apply to tomorrow
# Because the underlying process is changing!

# Example: Stock price in 2020 vs 2024
# - Different economic conditions
# - Different company size
# - Different market sentiment
# Can't just extrapolate!

# Solution: Make it stationary through DIFFERENCING
# Instead of predicting price, predict CHANGE in price
#
# price_t → change_t = price_t - price_{t-1}
```

### Testing for Stationarity: The ADF Test

The Augmented Dickey-Fuller (ADF) test tells us if a series is stationary:

```
ADF TEST INTERPRETATION:
────────────────────────

H₀ (Null): Series has a unit root (NON-stationary)
H₁ (Alt): Series is stationary

p-value < 0.05 → Reject H₀ → Series IS stationary
p-value ≥ 0.05 → Fail to reject → Series is NOT stationary

Example Results:
────────────────
Raw stock prices:     p = 0.87  → Non-stationary (expected!)
First difference:     p = 0.001 → Stationary (good for ARIMA)
Log returns:          p = 0.001 → Stationary (finance standard)
```

**Did You Know?** The unit root concept comes from the characteristic equation of an AR process. If the root equals 1 (a "unit root"), shocks to the system persist forever rather than dying out. This is why stock prices are non-stationary - a $10 increase today doesn't mean it'll drop $10 tomorrow. The change is permanent!

---

## Classical Methods: ARIMA

### The ARIMA Family

ARIMA stands for **A**uto**R**egressive **I**ntegrated **M**oving **A**verage. It's the Swiss Army knife of time series forecasting.

```
ARIMA COMPONENTS:
─────────────────

AR (AutoRegressive) - p:
  "Today depends on recent past values"
  y_t = c + φ₁·y_{t-1} + φ₂·y_{t-2} + ... + ε_t

  Like: "Temperature today ≈ 0.9 × temperature yesterday"


I (Integrated) - d:
  "How many times we difference to make stationary"
  d=0: Already stationary
  d=1: First difference (y_t - y_{t-1})
  d=2: Second difference (rarely needed)

  Like: "Don't predict price, predict price CHANGE"


MA (Moving Average) - q:
  "Today depends on recent forecast errors"
  y_t = c + ε_t + θ₁·ε_{t-1} + θ₂·ε_{t-2} + ...

  Like: "I was wrong by X yesterday, adjust for that"


ARIMA(p, d, q) notation:
────────────────────────
ARIMA(1, 0, 0) = AR(1) - Simple autoregressive
ARIMA(0, 1, 1) = IMA(1,1) - Random walk with MA
ARIMA(1, 1, 1) = Common balanced model
ARIMA(5, 1, 0) = AR with 5 lags, differenced once
```

### Seasonal ARIMA: SARIMA

For data with seasonality (most real data!), we use SARIMA:

```
SARIMA(p, d, q)(P, D, Q, s)
           │         │
           │         └── Seasonal components
           └── Non-seasonal components

s = seasonal period (12 for monthly, 7 for daily with weekly pattern)

Example: Monthly sales with yearly seasonality
SARIMA(1, 1, 1)(1, 1, 1, 12)
  │  │  │  │  │  │  │
  │  │  │  │  │  │  └── 12-month seasonal period
  │  │  │  │  │  └── Seasonal MA(1)
  │  │  │  │  └── Seasonal difference (year-over-year)
  │  │  │  └── Seasonal AR(1)
  │  │  └── Non-seasonal MA(1)
  │  └── Non-seasonal difference
  └── Non-seasonal AR(1)
```

### How to Choose ARIMA Parameters

The traditional approach uses ACF and PACF plots:

```
ACF (Autocorrelation Function):
───────────────────────────────
Correlation between y_t and y_{t-k} for all lags k

Interpretation:
- Slow decay → Non-stationary (need differencing)
- Cuts off after lag q → MA(q) model
- Decays exponentially → AR model

PACF (Partial Autocorrelation Function):
────────────────────────────────────────
Correlation between y_t and y_{t-k} AFTER removing
effect of intermediate lags

Interpretation:
- Cuts off after lag p → AR(p) model
- Decays exponentially → MA model


CHOOSING p AND q:
─────────────────
┌─────────────┬──────────────┬──────────────┐
│   Pattern   │     ACF      │    PACF      │
├─────────────┼──────────────┼──────────────┤
│   AR(p)     │ Exponential  │ Cuts off     │
│             │ decay        │ after lag p  │
├─────────────┼──────────────┼──────────────┤
│   MA(q)     │ Cuts off     │ Exponential  │
│             │ after lag q  │ decay        │
├─────────────┼──────────────┼──────────────┤
│  ARMA(p,q)  │ Exponential  │ Exponential  │
│             │ decay        │ decay        │
└─────────────┴──────────────┴──────────────┘
```

**Did You Know?** Box and Jenkins developed the ARIMA methodology in 1970, and it remained the gold standard for forecasting for over 40 years. Their book "Time Series Analysis: Forecasting and Control" has been cited over 60,000 times. George Box famously said, "All models are wrong, but some are useful."

---

## Facebook Prophet: Democratizing Forecasting

### Why Prophet Changed Everything

In 2017, Facebook released Prophet, making forecasting accessible to analysts without deep statistical expertise:

```
TRADITIONAL ARIMA WORKFLOW:
───────────────────────────
1. Check stationarity (ADF test)
2. Apply differencing if needed
3. Examine ACF/PACF plots
4. Choose p, d, q parameters
5. Fit model, check residuals
6. If residuals bad, go back to step 3
7. Handle seasonality separately
8. Add external regressors manually
9. Deal with missing data
10. Hope it works...

PROPHET WORKFLOW:
─────────────────
1. prophet.fit(df)
2. prophet.predict(future)
3. Done! 🎉
```

### How Prophet Works

Prophet uses a decomposable model with three components:

```
y(t) = g(t) + s(t) + h(t) + ε_t

Where:
g(t) = Trend (growth)
s(t) = Seasonality (Fourier series)
h(t) = Holidays/events
ε_t  = Error term


TREND MODEL:
────────────
Linear:     g(t) = k·t + m
Logistic:   g(t) = C / (1 + exp(-k(t - m)))

Prophet automatically detects "changepoints" where
the growth rate k changes!

      Before Facebook's Algorithm Change
                ╱╱╱╱
               ╱
              ╱
             ╱
      ──────╱
            │
            └── Changepoint detected!


SEASONALITY (Fourier Series):
─────────────────────────────
s(t) = Σ [aₙ·cos(2πnt/P) + bₙ·sin(2πnt/P)]

For yearly seasonality (P=365.25):
  - 10 Fourier terms by default
  - Captures complex patterns

For weekly seasonality (P=7):
  - 3 Fourier terms by default
  - Captures day-of-week effects
```

### Prophet's Secret Weapons

```
PROPHET ADVANTAGES:
───────────────────

1. HANDLES MISSING DATA
   ───────────────────
   No need to interpolate! Prophet just ignores gaps.

2. ROBUST TO OUTLIERS
   ───────────────────
   Uses robust regression internally.

3. CHANGEPOINT DETECTION
   ──────────────────────
   Automatically finds where trends change.

4. HOLIDAY EFFECTS
   ────────────────
   Built-in support for irregular events.
   holidays = pd.DataFrame({
       'holiday': ['superbowl', 'thanksgiving'],
       'ds': ['2024-02-11', '2024-11-28']
   })

5. INTERPRETABLE COMPONENTS
   ────────────────────────
   See exactly what each component contributes.

6. UNCERTAINTY INTERVALS
   ──────────────────────
   Automatic prediction intervals!
```

**Did You Know?** Prophet was developed by Sean Taylor and Ben Letham at Facebook to forecast daily active users and ad revenue. They needed something that "worked out of the box" for thousands of time series with minimal human intervention. The name "Prophet" reflects their goal: to make accurate predictions (prophecies) about the future.

---

## Deep Learning for Time Series

### When to Use Deep Learning

```
CLASSICAL vs DEEP LEARNING DECISION:
────────────────────────────────────

Use CLASSICAL (ARIMA, Prophet) when:
├── Single time series
├── Clear seasonality patterns
├── Limited data (<1000 points)
├── Interpretability needed
├── Fast training required
└── Simple relationships

Use DEEP LEARNING when:
├── Multiple related time series
├── Complex, non-linear patterns
├── Lots of data (>10,000 points)
├── Multiple input variables
├── State-of-the-art accuracy needed
└── Willing to trade interpretability
```

### Recurrent Neural Networks (RNNs)

RNNs were designed specifically for sequential data:

```
VANILLA RNN:
────────────
Each timestep, the hidden state carries information forward.

h_t = tanh(W_h · h_{t-1} + W_x · x_t + b)
y_t = W_y · h_t + b_y

                    ┌───────────────────────────────────────┐
                    │                                       │
                    ▼                                       │
 x_1 ─→ [RNN] ─→ h_1 ─→ [RNN] ─→ h_2 ─→ [RNN] ─→ h_3 ─→ [RNN] ─→ h_4
          │              │              │              │
          ▼              ▼              ▼              ▼
         y_1            y_2            y_3            y_4


PROBLEM: Vanishing Gradients!
─────────────────────────────
As we backpropagate through many timesteps,
gradients get multiplied repeatedly.

0.9 × 0.9 × 0.9 × ... × 0.9 (100 times) ≈ 0.000027

The gradient vanishes! Can't learn long-term dependencies.
```

### LSTM: Long Short-Term Memory

LSTMs solve the vanishing gradient problem with gates:

```
LSTM CELL ARCHITECTURE:
───────────────────────

        ┌─────────────────────────────────────────────────┐
        │                                                 │
        │   ┌─────┐     ┌─────┐     ┌─────┐              │
 c_{t-1}───►│  ×  │────►│  +  │────►│     │─────────► c_t│
        │   └──┬──┘     └──┬──┘     │     │              │
        │      │           │        │     │              │
        │   ┌──┴──┐     ┌──┴──┐     │     │              │
        │   │ f_t │     │ i_t │     │     │              │
        │   │Forget│    │Input│     │     │              │
        │   │ Gate │    │ Gate│     │     │              │
        │   └──┬──┘     └──┬──┘     │     │              │
        │      │     ×     │        │  ×  │              │
        │      │     │     │        │     │              │
        │      │  ┌──┴──┐  │        │     │              │
        │      │  │ c̃_t │  │        │     │              │
        │      │  │ New │  │        │     │              │
        │      │  │Memory│ │        │     │              │
        │      │  └──┬──┘  │        └──┬──┘              │
        │      │     │     │           │                 │
        │      └──┬──┴──┬──┘        ┌──┴──┐              │
        │         │     │           │ o_t │              │
        │         │     │           │Output│             │
        │         │     │           │ Gate │             │
        │         │     │           └──┬──┘              │
        │         │     │              │                 │
 h_{t-1}─────────►│─────│──────────────►──────────► h_t  │
        │         │     │                                │
        │         │     │                                │
        └─────────┴─────┴────────────────────────────────┘
                  │     │
                  x_t   x_t


GATE FUNCTIONS:
───────────────
f_t = σ(W_f · [h_{t-1}, x_t] + b_f)   # Forget gate
i_t = σ(W_i · [h_{t-1}, x_t] + b_i)   # Input gate
o_t = σ(W_o · [h_{t-1}, x_t] + b_o)   # Output gate
c̃_t = tanh(W_c · [h_{t-1}, x_t] + b_c) # New memory

c_t = f_t ⊙ c_{t-1} + i_t ⊙ c̃_t      # Cell state update
h_t = o_t ⊙ tanh(c_t)                 # Hidden state

The cell state c_t acts like a "conveyor belt" -
information can flow unchanged through time!
```

**Did You Know?** LSTMs were invented by Sepp Hochreiter and Jürgen Schmidhuber in 1997. For years, the paper was largely ignored because computing power wasn't sufficient. It wasn't until 2014-2015 that LSTMs became practical, winning competitions and powering Google Translate. Schmidhuber often jokes that deep learning's success came 20 years late!

### GRU: A Simpler Alternative

Gated Recurrent Units simplify LSTMs while keeping most benefits:

```
GRU vs LSTM:
────────────

LSTM: 3 gates (forget, input, output) + cell state
GRU:  2 gates (reset, update) + no cell state

GRU EQUATIONS:
z_t = σ(W_z · [h_{t-1}, x_t])         # Update gate
r_t = σ(W_r · [h_{t-1}, x_t])         # Reset gate
h̃_t = tanh(W · [r_t ⊙ h_{t-1}, x_t])  # Candidate
h_t = (1 - z_t) ⊙ h_{t-1} + z_t ⊙ h̃_t # New state


COMPARISON:
───────────
┌──────────────┬───────────┬───────────┐
│   Aspect     │   LSTM    │    GRU    │
├──────────────┼───────────┼───────────┤
│ Parameters   │ More      │ Fewer     │
│ Training     │ Slower    │ Faster    │
│ Performance  │ ≈ Same    │ ≈ Same    │
│ Long deps    │ Slightly  │ Slightly  │
│              │ better    │ worse     │
└──────────────┴───────────┴───────────┘

Rule of thumb: Try GRU first (faster), switch to
LSTM if you need longer memory.
```

---

## Transformers for Time Series

### Why Transformers Work for Time Series

The same attention mechanism that revolutionized NLP works for time series:

```
ATTENTION IN TIME SERIES:
─────────────────────────

Traditional RNN: Sequential processing
  t=1 → t=2 → t=3 → t=4 → ... → t=100

  Problem: Information from t=1 might not reach t=100!

Transformer: Direct connections to ALL timesteps

       t=1  t=2  t=3  t=4  ...  t=100
        │    │    │    │         │
        └────┴────┴────┴─────────┘
                   │
              Attention can
              directly access
              any timestep!

Example: Forecasting energy demand
─────────────────────────────────
To predict Monday 8am demand, attention can:
- Look at last Monday 8am (7 days ago)
- Look at yesterday 8am
- Look at same day last year
- Ignore irrelevant midnight data

It LEARNS which past times are relevant!
```

### Temporal Fusion Transformer (TFT)

Google's TFT is state-of-the-art for time series:

```
TFT ARCHITECTURE:
─────────────────

┌─────────────────────────────────────────────────────┐
│                   OUTPUT LAYER                       │
│              (Quantile predictions)                  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              TEMPORAL SELF-ATTENTION                 │
│         (Which past times matter most?)              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              LSTM ENCODER-DECODER                    │
│            (Sequential processing)                   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│            VARIABLE SELECTION NETWORK                │
│    (Which input features are important?)             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                   INPUT EMBEDDING                    │
│   Static vars | Past observed | Known future         │
│   (store ID)  | (past sales)  | (promotions)         │
└─────────────────────────────────────────────────────┘


TFT INNOVATIONS:
────────────────
1. Variable Selection: Learns which features matter
2. Static Enrichment: Uses metadata (store type, etc.)
3. Interpretable Attention: See which past times mattered
4. Multi-horizon: Predicts multiple future steps at once
5. Quantile Output: Uncertainty estimates built-in
```

**Did You Know?** The 2020 M5 Forecasting Competition on Kaggle (42,840 time series of Walmart sales) was won by teams using LightGBM, not deep learning! This surprised many researchers. The lesson: for many real-world problems, gradient boosting with good feature engineering still beats complex neural networks. Deep learning shines when you have millions of related time series.

---

## Temporal Feature Engineering

### Creating Features from Time

Raw timestamps hide valuable information:

```
FROM A SINGLE TIMESTAMP, EXTRACT:
─────────────────────────────────

datetime: 2024-11-28 14:30:00 (Thanksgiving Thursday)

Calendar Features:
├── year: 2024
├── month: 11
├── day: 28
├── hour: 14
├── minute: 30
├── day_of_week: 3 (Thursday)
├── day_of_year: 333
├── week_of_year: 48
├── quarter: 4
├── is_weekend: False
├── is_month_start: False
├── is_month_end: False
└── is_year_end: False

Cyclical Encoding (for neural networks):
├── hour_sin: sin(2π × 14/24) = 0.866
├── hour_cos: cos(2π × 14/24) = -0.5
├── day_sin: sin(2π × 3/7) = 0.975
├── day_cos: cos(2π × 3/7) = -0.223
└── month_sin/cos: ...

Holiday Features:
├── is_holiday: True (Thanksgiving)
├── days_to_holiday: 0
├── days_since_holiday: 0
└── holiday_type: "thanksgiving"
```

### Lag Features: Looking Back in Time

```
LAG FEATURES:
─────────────
The most powerful time series features!

Original data:
─────────────
│ Date       │ Sales │
├────────────┼───────┤
│ 2024-11-25 │  100  │
│ 2024-11-26 │  120  │
│ 2024-11-27 │  110  │
│ 2024-11-28 │  ???  │  ← Predict this

With lag features:
─────────────────
│ Date       │ Sales │ lag_1 │ lag_2 │ lag_7 │
├────────────┼───────┼───────┼───────┼───────┤
│ 2024-11-25 │  100  │   95  │   90  │   98  │
│ 2024-11-26 │  120  │  100  │   95  │  115  │
│ 2024-11-27 │  110  │  120  │  100  │  105  │
│ 2024-11-28 │  ???  │  110  │  120  │  102  │
                │      │      │
                │      │      └── Same day last week
                │      └── 2 days ago
                └── Yesterday's sales

Now the model can learn:
"Sales ≈ 0.3×lag_1 + 0.1×lag_2 + 0.5×lag_7"
```

### Rolling Statistics

```
ROLLING WINDOW FEATURES:
────────────────────────

│ Date       │ Sales │ roll_mean_7 │ roll_std_7 │ roll_max_7 │
├────────────┼───────┼─────────────┼────────────┼────────────┤
│ 2024-11-28 │  ???  │    107.5    │    8.2     │    120     │

roll_mean_7 = mean of last 7 days' sales
roll_std_7  = std dev of last 7 days (volatility!)
roll_max_7  = max of last 7 days (recent peak)


EXPANDING WINDOW (cumulative):
─────────────────────────────
│ Date       │ Sales │ expanding_mean │ days_since_start │
├────────────┼───────┼────────────────┼──────────────────┤
│ 2024-11-28 │  ???  │     98.5       │       333        │

expanding_mean = mean of ALL historical data
Useful for detecting regime changes!


EXPONENTIAL MOVING AVERAGE:
───────────────────────────
EMA gives more weight to recent observations.

EMA_t = α × value_t + (1-α) × EMA_{t-1}

α = 0.1: Slow EMA (long memory)
α = 0.5: Fast EMA (recent focus)
```

**Did You Know?** The most important feature in many time series competitions is simply "same day last year" (lag_365 or lag_364 depending on day-of-week alignment). In the M5 competition, this single feature provided more predictive power than dozens of other engineered features combined!

---

## Anomaly Detection in Time Series

### What Makes an Anomaly?

```
TYPES OF ANOMALIES:
───────────────────

1. POINT ANOMALY
   A single value that's unusual

   Normal: 100, 102, 98, 105, [500], 101, 99
                              ^^^^ Point anomaly!

2. CONTEXTUAL ANOMALY
   Normal in one context, anomalous in another

   Summer: 85°F normal
   Winter: 85°F ANOMALY! (should be ~40°F)

3. COLLECTIVE ANOMALY
   A sequence that's unusual as a group

   Normal: ~100, ~100, ~100
   Anomaly: 50, 50, 50, 50, 50  (individually ok, but...)
            ^^^^^^^^^^^^^^^^^
            Five consecutive lows is suspicious!


REAL-WORLD EXAMPLES:
────────────────────
├── Fraud Detection: Unusual spending pattern
├── Server Monitoring: CPU spike at 3am
├── Manufacturing: Machine vibration change
├── Healthcare: Heart rate irregularity
└── Finance: Flash crash in stock price
```

### Statistical Methods

```
Z-SCORE METHOD:
───────────────
z = (x - μ) / σ

If |z| > 3, it's an anomaly (3-sigma rule)

        │           ▲
        │          ╱ ╲
        │         ╱   ╲
        │        ╱     ╲     99.7% of data
        │       ╱       ╲    within ±3σ
        │      ╱         ╲
        │     ╱           ╲
        │────╱─────────────╲────
        │   -3σ   μ        3σ
        │    │             │
        └────┴─────────────┴────
           Anomaly zone!


IQR METHOD (Robust to outliers):
────────────────────────────────
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1

Lower bound = Q1 - 1.5 × IQR
Upper bound = Q3 + 1.5 × IQR

Values outside bounds = anomalies
```

### Machine Learning Methods

```
ISOLATION FOREST:
─────────────────
Idea: Anomalies are easier to isolate!

Normal points: Need many splits to isolate
Anomalies: Few splits to isolate (they're "far" from others)

                  │
           ┌──────┴──────┐
           │             │
     ┌─────┴─────┐       ●  ← Anomaly isolated in 1 split!
     │           │
   ┌─┴─┐       ┌─┴─┐
   ●   ●       ●   ●  ← Normal points need more splits


Isolation score = average path length to isolate point
Low path length = likely anomaly


AUTOENCODERS FOR ANOMALY DETECTION:
───────────────────────────────────

Train autoencoder on NORMAL data only:
  Input → [Encoder] → Latent → [Decoder] → Reconstruction

For new data:
  reconstruction_error = ||input - reconstructed||

  Normal data: Low error (autoencoder learned these patterns)
  Anomalies: High error (never seen before, can't reconstruct!)

        Reconstruction Error
              │
    Anomaly   │    ●
    threshold │─────────────●────
              │      ●    ●
              │   ●●●●●●●●●
              │  ●  ●  ●
              └──────────────────
                   Data points
```

**Did You Know?** Netflix uses time series anomaly detection to monitor their 200+ microservices. They process millions of metrics per second and need to detect issues within seconds. Their system "Telltale" uses a combination of statistical methods and machine learning, automatically learning what's "normal" for each service without human labeling!

---

## Forecasting at Scale

### The Multiple Time Series Problem

```
SINGLE vs MULTIPLE TIME SERIES:
───────────────────────────────

SINGLE TIME SERIES (Traditional):
─────────────────────────────────
One model per series. Works for 1-100 series.

Product A → ARIMA_A
Product B → ARIMA_B
Product C → ARIMA_C
...
Time: O(n) models to train


MULTIPLE TIME SERIES (Modern):
──────────────────────────────
One model for ALL series. Essential for 1000+ series.

Product A ──┐
Product B ──┼──→ [Global Model] ──→ All forecasts
Product C ──┤
...        ─┘

Benefits:
- Learns patterns across series
- Handles cold start (new products)
- Much faster (1 model, not n)
- Often more accurate!
```

### Hierarchical Forecasting

```
HIERARCHY EXAMPLE (Retail):
───────────────────────────

                    Total Company
                         │
           ┌─────────────┼─────────────┐
           │             │             │
        Region A     Region B      Region C
           │             │             │
      ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
      │    │    │   │    │    │   │    │    │
    Store Store Store Store Store Store Store Store Store
      1    2    3    4    5    6    7    8    9


RECONCILIATION PROBLEM:
───────────────────────
If you forecast each level independently:
  Total forecast: $1,000,000
  Sum of regions:   $950,000  ← Doesn't match!

Solutions:
1. Top-down: Forecast total, split proportionally
2. Bottom-up: Forecast stores, sum up
3. Optimal reconciliation: Combine all levels optimally
```

---

## Practical Considerations

### Handling Missing Data

```
STRATEGIES FOR MISSING VALUES:
──────────────────────────────

1. FORWARD FILL (LOCF)
   Last Observation Carried Forward
   [10, 20, NaN, NaN, 50] → [10, 20, 20, 20, 50]
   Good for: Slow-changing data (prices, states)

2. BACKWARD FILL
   [10, NaN, NaN, 40, 50] → [10, 40, 40, 40, 50]
   Good for: When future is more relevant

3. LINEAR INTERPOLATION
   [10, NaN, NaN, 40, 50] → [10, 20, 30, 40, 50]
   Good for: Smooth continuous data

4. SEASONAL INTERPOLATION
   Use same time from previous cycle
   Good for: Strongly seasonal data

5. MODEL-BASED IMPUTATION
   Train model on non-missing data, predict missing
   Good for: Complex patterns
```

### Evaluation Metrics

```
FORECASTING METRICS:
────────────────────

MAE (Mean Absolute Error):
  MAE = mean(|actual - predicted|)
  Interpretable: "Average error is $X"

RMSE (Root Mean Square Error):
  RMSE = sqrt(mean((actual - predicted)²))
  Penalizes large errors more

MAPE (Mean Absolute Percentage Error):
  MAPE = mean(|actual - predicted| / |actual|) × 100%
  Scale-independent
  Problem: undefined when actual = 0!

SMAPE (Symmetric MAPE):
  SMAPE = mean(2|A - P| / (|A| + |P|)) × 100%
  Handles zeros better

MASE (Mean Absolute Scaled Error):
  MASE = MAE / MAE_of_naive_forecast
  < 1 means better than naive
  The gold standard for academics!


WHICH TO USE?
─────────────
├── Business stakeholders: MAE (easy to explain)
├── Scale comparison: MAPE/SMAPE
├── Academic: MASE
└── Optimization: Usually RMSE (differentiable)
```

### Avoiding Data Leakage

```
TIME SERIES CROSS-VALIDATION:
─────────────────────────────

WRONG (standard k-fold):
────────────────────────
Randomly split data - FUTURE leaks into PAST!
  Train: [▓▓▓░░▓▓░▓▓]  (random mix)
  Test:  [░░░▓▓░░▓░░]

  Model might see Dec 2024 in training,
  then "predict" Nov 2024 in test. CHEATING!


CORRECT (time-based):
─────────────────────

Walk-forward validation:
  Fold 1: Train [▓▓▓░░░░░░░] Test [░▓░░░░░░░░]
  Fold 2: Train [▓▓▓▓░░░░░░] Test [░░▓░░░░░░░]
  Fold 3: Train [▓▓▓▓▓░░░░░] Test [░░░▓░░░░░░]
  Fold 4: Train [▓▓▓▓▓▓░░░░] Test [░░░░▓░░░░░]
          ─────────────────────────────────────→ time

Always train on PAST, test on FUTURE!


GAP BETWEEN TRAIN AND TEST:
───────────────────────────
If forecasting 7 days ahead, leave 7-day gap:
  Train: [▓▓▓▓▓▓░░░░░░░░] Gap [░░░░░░░] Test [▓▓▓]

Prevents target leakage through lagged features!
```

---

## Hands-On Exercises

### Exercise 1: Build ARIMA Forecaster

```python
# TODO: Implement ARIMA pipeline
# 1. Load time series data
# 2. Test for stationarity (ADF test)
# 3. Apply differencing if needed
# 4. Choose p, q using ACF/PACF
# 5. Fit ARIMA model
# 6. Generate forecasts with confidence intervals
# 7. Evaluate using walk-forward validation
```

### Exercise 2: Prophet vs ARIMA Comparison

```python
# TODO: Compare Prophet and ARIMA
# 1. Load same dataset
# 2. Train both models
# 3. Compare forecasts
# 4. Evaluate on hold-out set
# 5. Analyze component decomposition
```

### Exercise 3: LSTM Time Series Model

```python
# TODO: Build LSTM for time series
# 1. Create sequences (look_back windows)
# 2. Build LSTM architecture
# 3. Train with proper time-split
# 4. Compare to classical methods
```

---

## Summary

```
TIME SERIES FORECASTING TOOLKIT:
────────────────────────────────

┌───────────────────────────────────────────────────────────┐
│                    CLASSICAL METHODS                       │
├────────────────┬──────────────────────────────────────────┤
│ ARIMA/SARIMA   │ Statistical, interpretable, good baseline│
│ Prophet        │ Easy to use, handles holidays, robust    │
│ Exponential    │ Simple, fast, good for benchmarking      │
│ Smoothing      │                                          │
└────────────────┴──────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                  DEEP LEARNING METHODS                     │
├────────────────┬──────────────────────────────────────────┤
│ LSTM/GRU       │ Sequential, good for medium-length deps  │
│ Transformer    │ Parallel, great for long dependencies    │
│ TFT            │ State-of-art, interpretable attention    │
│ N-BEATS        │ Pure DL, no hand-crafted features        │
└────────────────┴──────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                   ENSEMBLE / HYBRID                        │
├────────────────┬──────────────────────────────────────────┤
│ LightGBM+Lags  │ Often wins competitions! Simple & fast   │
│ Stacking       │ Combine multiple model predictions       │
│ Weighted Avg   │ Average classical + DL forecasts         │
└────────────────┴──────────────────────────────────────────┘


DECISION FLOWCHART:
───────────────────
                 Start
                   │
      ┌────────────┴────────────┐
      │   How many series?      │
      └────────────┬────────────┘
                   │
          ┌───────┴───────┐
         <10            >100
          │               │
          ▼               ▼
       ARIMA/         Global
       Prophet        Model
          │               │
    ┌─────┴─────┐   ┌─────┴─────┐
    │Seasonality│   │  >10k pts │
    └─────┬─────┘   └─────┬─────┘
        Yes│No          Yes│No
          │  │            │  │
          ▼  ▼            ▼  ▼
     SARIMA AR       Transformer LightGBM
     Prophet          TFT        +Lags
```

---

## Further Reading

### Papers
- "Time Series Forecasting with Prophet" (Taylor & Letham, 2017)
- "Temporal Fusion Transformers" (Lim et al., 2020)
- "N-BEATS: Neural Basis Expansion Analysis" (Oreshkin et al., 2020)
- "Deep Learning for Time Series Forecasting" (Lim & Zohren, 2021)

### Libraries
- **statsmodels**: ARIMA, exponential smoothing
- **Prophet**: Facebook's forecasting library
- **GluonTS**: Amazon's deep learning time series
- **Darts**: Unified interface for all methods
- **sktime**: scikit-learn compatible time series

---

## Next Steps

You now understand time series forecasting from classical ARIMA to modern transformers!

**Up Next**: Module 39 - AutoML & Feature Stores

---

_Module 38 Complete!_
_"The best forecast is the one that's useful, not the one that's most complex."_
