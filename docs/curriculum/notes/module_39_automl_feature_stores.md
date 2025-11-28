# Module 39: AutoML & Feature Stores

**Last Updated**: 2025-11-28
**Status**: In Progress
**Duration**: 5-6 hours

---

## Learning Objectives

By the end of this module, you will:
- Understand AutoML and when to use it
- Master AutoGluon for automated machine learning
- Learn feature store concepts and architecture
- Implement automated feature engineering
- Build end-to-end ML pipelines

---

## The AutoML Revolution

Imagine you're a chef at a restaurant. Traditional ML is like cooking everything from scratch - you select ingredients (features), decide cooking methods (algorithms), adjust seasoning (hyperparameters), and taste-test constantly (validation). It requires years of expertise.

AutoML is like having a robot chef that tries hundreds of recipes automatically, learns from each attempt, and presents you with the best dish. You just need to provide the ingredients and describe what you want.

```
TRADITIONAL ML WORKFLOW:
────────────────────────
Data → [Manual Feature Eng] → [Choose Algorithm] → [Tune Hyperparameters] → Model
         ↑                         ↑                      ↑
         │                         │                      │
    Requires expertise       Requires expertise     Takes days/weeks
         │                         │                      │
         └─────────────────────────┴──────────────────────┘
                     TIME: Days to Weeks


AUTOML WORKFLOW:
────────────────
Data → [AutoML System] → Best Model
            │
            ├── Tries 100+ algorithms
            ├── Engineers features automatically
            ├── Tunes hyperparameters
            └── Ensembles best models

       TIME: Minutes to Hours
```

**Did You Know?** In the 2019 AutoML Challenge, AutoGluon achieved top-3 results on 39 out of 39 datasets, often beating solutions that took ML experts weeks to develop. The total computation time? About 4 hours per dataset with no human intervention!

---

## Why AutoML Matters

### The ML Expertise Gap

```
REALITY OF ML IN INDUSTRY:
──────────────────────────

Companies with ML needs:    ████████████████████ 1,000,000+
Companies with ML experts:  ███                  ~50,000
Expert ML engineers:        █                    ~300,000

Gap: 95%+ of companies can't hire ML experts!

AutoML bridges this gap:
- Democratizes ML (anyone can use it)
- Accelerates expert productivity (10x faster)
- Establishes strong baselines automatically
```

### When to Use AutoML

```
USE AUTOML:
───────────
✅ Establishing baselines quickly
✅ Tabular data problems
✅ Time-constrained projects
✅ Non-expert teams
✅ Comparing many algorithms
✅ Hyperparameter optimization

DON'T USE AUTOML (alone):
─────────────────────────
❌ Custom architectures needed
❌ Domain-specific constraints
❌ Real-time inference requirements
❌ Highly specialized problems
❌ When interpretability is critical
```

---

## AutoML Landscape

### Major AutoML Frameworks

```
AUTOML FRAMEWORK COMPARISON:
────────────────────────────

┌──────────────────────────────────────────────────────────────────┐
│  FRAMEWORK      │ BEST FOR           │ KEY STRENGTH              │
├──────────────────────────────────────────────────────────────────┤
│  AutoGluon      │ Tabular, general   │ Best accuracy, ensembles  │
│  (Amazon)       │                    │                           │
├──────────────────────────────────────────────────────────────────┤
│  auto-sklearn   │ scikit-learn users │ Meta-learning, warm-start │
│  (Freiburg)     │                    │                           │
├──────────────────────────────────────────────────────────────────┤
│  H2O AutoML     │ Enterprise         │ Production-ready, scaling │
│  (H2O.ai)       │                    │                           │
├──────────────────────────────────────────────────────────────────┤
│  FLAML          │ Fast experiments   │ Low compute, fast         │
│  (Microsoft)    │                    │                           │
├──────────────────────────────────────────────────────────────────┤
│  PyCaret        │ Low-code ML        │ Simple API, visualization │
│  (Open Source)  │                    │                           │
└──────────────────────────────────────────────────────────────────┘
```

### AutoGluon Deep Dive

AutoGluon (by Amazon) consistently wins ML competitions:

```
AUTOGLUON ARCHITECTURE:
───────────────────────

                    Input Data
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
        ┌───────┐   ┌───────┐   ┌───────┐
        │NN     │   │GBM    │   │Linear │
        │Models │   │Models │   │Models │
        └───┬───┘   └───┬───┘   └───┬───┘
            │           │           │
            │    ┌──────┼──────┐    │
            │    │      │      │    │
            ▼    ▼      ▼      ▼    ▼
        ┌─────────────────────────────┐
        │     MULTI-LAYER STACKING    │
        │  (Ensemble of ensembles)    │
        └──────────────┬──────────────┘
                       │
                       ▼
                  Best Model


MODELS AUTOGLUON TRIES:
───────────────────────
Neural Networks:
  - TabularNN (custom for tabular)
  - FastAI neural network

Gradient Boosting:
  - LightGBM
  - CatBoost
  - XGBoost

Linear Models:
  - Ridge/Lasso regression
  - Linear SVM

Ensemble:
  - Weighted ensemble
  - Multi-layer stacking
```

**Did You Know?** AutoGluon's "multi-layer stacking" is unique. Instead of just averaging model predictions, it trains a second layer of models on the first layer's predictions, then a third layer, and so on. This recursive ensembling often improves accuracy by 1-3% - which can mean millions in revenue for businesses!

---

## AutoML Under the Hood

### Algorithm Selection

How does AutoML choose which algorithms to try?

```
ALGORITHM SELECTION STRATEGIES:
───────────────────────────────

1. EXHAUSTIVE SEARCH
   Try ALL algorithms, all hyperparameters
   Problem: Computationally infeasible!

   10 algorithms × 100 hyperparameter combos = 1,000 models
   If each takes 1 minute = 16+ hours


2. META-LEARNING (auto-sklearn approach)
   Learn from past datasets which algorithms work best

   "This dataset looks like Dataset #4,523 from our database.
    Random Forest worked best there, let's try that first!"

   Steps:
   a) Extract meta-features from dataset
   b) Find similar historical datasets
   c) Start with algorithms that worked on those


3. BAYESIAN OPTIMIZATION
   Smart search that learns as it goes

   ┌──────────────────────────────────────────────┐
   │ Iteration 1: Try random config → Score: 0.75 │
   │ Iteration 2: Try another → Score: 0.82      │
   │ Iteration 3: Try similar to best → 0.85     │
   │ ...learns that high learning_rate is bad... │
   │ Iteration 50: Optimal found → 0.91          │
   └──────────────────────────────────────────────┘


4. BANDIT-BASED (Hyperband/ASHA)
   Give more resources to promising configs

   Start: 100 configs with 1 epoch each
   Keep:  Top 25 configs, train for 4 epochs
   Keep:  Top 6 configs, train for 16 epochs
   Keep:  Top 2 configs, train to completion

   Result: Find best config with 10x less compute!
```

### Hyperparameter Optimization

```
HYPERPARAMETER SEARCH SPACE:
────────────────────────────

LightGBM example:
┌─────────────────────────────────────────────────┐
│  Parameter        │  Search Space              │
├─────────────────────────────────────────────────┤
│  n_estimators     │  [100, 200, 500, 1000]     │
│  learning_rate    │  [0.01, 0.05, 0.1, 0.3]    │
│  max_depth        │  [3, 5, 7, 10, -1]         │
│  num_leaves       │  [15, 31, 63, 127]         │
│  min_child_weight │  [1e-3, 1e-2, 0.1, 1]      │
│  subsample        │  [0.5, 0.7, 0.9, 1.0]      │
│  colsample_bytree │  [0.5, 0.7, 0.9, 1.0]      │
└─────────────────────────────────────────────────┘

Total combinations: 4×4×5×4×4×4×4 = 20,480 configs!

Smart search finds good config in ~50 trials
Exhaustive search needs 20,480 trials
Speedup: 400x
```

---

## Automated Feature Engineering

### Why Automate Feature Engineering?

```
FEATURE ENGINEERING REALITY:
────────────────────────────

Time spent on ML projects:
┌──────────────────────────────────────────────────────┐
│  Data Collection      ████████████         25%       │
│  Data Cleaning        ████████████████     35%       │
│  Feature Engineering  ██████████████       30%       │
│  Model Training       ████                 10%       │
└──────────────────────────────────────────────────────┘

Feature engineering is:
- Time-consuming (30% of project time)
- Requires domain expertise
- Often repetitive across projects
- Critical for model performance

"Give me better features, and I'll give you a better model."
                                    - Every ML Engineer
```

### Automated Feature Engineering Techniques

```
AUTO-FEATURE TECHNIQUES:
────────────────────────

1. AGGREGATION (for relational data)
   ─────────────────────────────────
   customer_id → orders table

   Auto-generated features:
   - count(orders)
   - sum(order_amount)
   - avg(order_amount)
   - max(order_amount)
   - days_since_last_order


2. TRANSFORMATION
   ───────────────
   Original: [price, quantity]

   Auto-generated:
   - log(price)
   - sqrt(quantity)
   - price * quantity  (interaction)
   - price / quantity  (ratio)
   - price ** 2        (polynomial)


3. TIME-BASED (from timestamps)
   ────────────────────────────
   Original: purchase_datetime

   Auto-generated:
   - hour_of_day
   - day_of_week
   - is_weekend
   - month
   - quarter
   - days_since_signup


4. ENCODING (for categoricals)
   ───────────────────────────
   Original: category = ["A", "B", "C"]

   Auto-generated:
   - One-hot encoding
   - Target encoding
   - Frequency encoding
   - Label encoding
```

### Featuretools: Deep Feature Synthesis

```
DEEP FEATURE SYNTHESIS (DFS):
─────────────────────────────

Given relational tables, automatically generate features:

TABLES:
  customers(id, signup_date, country)
  orders(id, customer_id, date, amount)
  products(id, order_id, product_type, price)


DFS GENERATES:
──────────────
Depth 1: Simple aggregations
  - COUNT(orders)
  - SUM(orders.amount)
  - AVG(orders.amount)

Depth 2: Stacked aggregations
  - COUNT(orders.products)
  - AVG(orders.SUM(products.price))
  - MODE(orders.MODE(products.product_type))

Depth 3: Triple-stacked!
  - STD(orders.AVG(products.price))

Result: 100s of features from 3 tables!


PRIMITIVES USED:
────────────────
Aggregation: sum, mean, count, max, min, std, mode
Transform: year, month, weekday, cum_sum, diff
```

**Did You Know?** In the 2015 KDD Cup, a team used Featuretools to generate over 1,000 features automatically. They finished in the top 10% of the competition with minimal manual feature engineering. The winning insight: more features (properly regularized) often beats carefully hand-crafted few features.

---

## Feature Stores

### What is a Feature Store?

Think of a feature store as a "data warehouse for ML features" - a centralized repository where teams can share, discover, and reuse features.

```
WITHOUT FEATURE STORE:
──────────────────────

Team A: Builds "customer_lifetime_value" feature
        ├── Writes SQL query
        ├── Schedules daily job
        └── Stores in their own table

Team B: Needs same feature
        ├── Doesn't know Team A has it
        ├── Builds their own version
        └── Gets slightly different results!

Team C: Needs feature for real-time inference
        ├── Can't use batch SQL
        └── Builds third version!

Result: 3 versions of the same feature, inconsistent!


WITH FEATURE STORE:
───────────────────

               ┌─────────────────────────────┐
               │      FEATURE STORE          │
               │  ┌─────────────────────┐    │
               │  │ customer_lifetime_  │    │
               │  │ value               │    │
               │  │ - Batch: Daily SQL  │    │
               │  │ - Online: Redis     │    │
               │  │ - Owner: Team A     │    │
               │  │ - Version: 2.3      │    │
               │  └─────────────────────┘    │
               └──────────────┬──────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
        Team A             Team B             Team C
     (training)          (training)        (inference)

All teams use the SAME feature definition!
```

### Feature Store Architecture

```
FEATURE STORE COMPONENTS:
─────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                     FEATURE STORE                                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  FEATURE REGISTRY                          │ │
│  │  - Feature definitions (schema, transformations)           │ │
│  │  - Metadata (owner, description, data lineage)            │ │
│  │  - Versioning                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┴────────────────────┐             │
│         │                                         │              │
│  ┌──────▼──────┐                         ┌───────▼───────┐      │
│  │ OFFLINE     │                         │ ONLINE        │      │
│  │ STORE       │                         │ STORE         │      │
│  │             │                         │               │      │
│  │ - Historical│         Sync            │ - Latest      │      │
│  │ - Training  │ ◄──────────────────────►│ - Real-time   │      │
│  │ - BigQuery/ │                         │ - Redis/      │      │
│  │   S3/HDFS   │                         │   DynamoDB    │      │
│  └─────────────┘                         └───────────────┘      │
│         │                                         │              │
│         │                                         │              │
│  ┌──────▼──────────────────────────────────────────▼──────┐     │
│  │                    SERVING LAYER                        │     │
│  │   - Batch serving (training)                           │     │
│  │   - Online serving (inference)                         │     │
│  │   - Point-in-time correctness                          │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Point-in-Time Correctness

This is the MOST important concept in feature stores:

```
POINT-IN-TIME PROBLEM:
──────────────────────

Training data preparation:
  "What was the customer's purchase_count on 2024-01-15?"

WRONG APPROACH (data leakage!):
  SELECT purchase_count FROM current_features
  WHERE customer_id = 123

  Problem: Returns TODAY's count, not 2024-01-15's!
  The model trains on future information = cheating!


CORRECT APPROACH (point-in-time join):
  SELECT purchase_count FROM feature_history
  WHERE customer_id = 123
  AND feature_timestamp <= '2024-01-15'
  ORDER BY feature_timestamp DESC
  LIMIT 1

  Returns: Value as it was on 2024-01-15 ✓


TIMELINE:
─────────
          2024-01-15          Today
              │                 │
              ▼                 ▼
    ──────────●─────────────────●──────►
              │                 │
        Training event     Don't use
         Use features      these values!
         from HERE
```

**Did You Know?** Uber's feature store "Michelangelo" serves over 10 million feature vector lookups per second. They estimate that having a centralized feature store reduced their ML feature development time by 50% and virtually eliminated training-serving skew issues that previously caused silent model degradation.

---

## Feast: Open Source Feature Store

### Feast Architecture

```
FEAST COMPONENTS:
─────────────────

┌─────────────────────────────────────────────────────────────┐
│                         FEAST                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   FEATURE REPO                        │   │
│  │   feature_store.yaml   # Configuration                │   │
│  │   features.py          # Feature definitions          │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            │ feast apply                     │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   REGISTRY                            │   │
│  │   - Feature views                                     │   │
│  │   - Entities                                          │   │
│  │   - Data sources                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│            ┌───────────────┼───────────────┐                │
│            │               │               │                 │
│            ▼               ▼               ▼                 │
│     ┌───────────┐   ┌───────────┐   ┌───────────┐          │
│     │ Offline   │   │ Online    │   │ Serving   │          │
│     │ Store     │   │ Store     │   │ API       │          │
│     │ (Parquet) │   │ (Redis)   │   │ (gRPC)    │          │
│     └───────────┘   └───────────┘   └───────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Defining Features in Feast

```python
# features.py

from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Float32, Int64

# Define entity (the thing we're building features for)
customer = Entity(
    name="customer_id",
    join_keys=["customer_id"],
    description="Customer identifier"
)

# Define data source
customer_stats_source = FileSource(
    path="data/customer_stats.parquet",
    timestamp_field="event_timestamp"
)

# Define feature view
customer_stats = FeatureView(
    name="customer_stats",
    entities=[customer],
    ttl=timedelta(days=90),  # How long features are valid
    schema=[
        Field(name="total_purchases", dtype=Int64),
        Field(name="avg_order_value", dtype=Float32),
        Field(name="days_since_last_order", dtype=Int64),
    ],
    online=True,   # Serve from online store
    source=customer_stats_source,
)
```

### Using Feast

```python
# Training: Get historical features
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Entity dataframe (what we want features for)
entity_df = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5],
    "event_timestamp": pd.to_datetime(["2024-01-15"] * 5)
})

# Get training data with point-in-time correctness!
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_stats:total_purchases",
        "customer_stats:avg_order_value",
        "customer_stats:days_since_last_order"
    ]
).to_df()


# Inference: Get online features
feature_vector = store.get_online_features(
    features=[
        "customer_stats:total_purchases",
        "customer_stats:avg_order_value",
    ],
    entity_rows=[{"customer_id": 123}]
).to_dict()

# Returns: {"customer_id": [123], "total_purchases": [47], ...}
```

---

## ML Pipeline Automation

### End-to-End ML Pipeline

```
AUTOMATED ML PIPELINE:
──────────────────────

┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Data   │──►│ Feature │──►│ Model   │──►│ Model   │──►│ Deploy  │
│ Ingest  │   │   Eng   │   │ Train   │   │  Eval   │   │         │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
 Scheduled    Feature       AutoML       Metrics      A/B Test
   Jobs       Store        Trains       Tracked      or Canary

ORCHESTRATION:
  - Airflow / Dagster / Prefect
  - MLflow for experiment tracking
  - Feature store for features
  - Model registry for models
  - CI/CD for deployment
```

### MLflow Integration

```
MLFLOW EXPERIMENT TRACKING:
───────────────────────────

with mlflow.start_run():
    # Log parameters
    mlflow.log_param("model_type", "LightGBM")
    mlflow.log_param("n_estimators", 100)

    # Train model
    model = train_model(...)

    # Log metrics
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("f1_score", 0.93)

    # Log model
    mlflow.sklearn.log_model(model, "model")


MLFLOW UI shows:
┌────────────────────────────────────────────────────────────┐
│  Run ID    │ Model     │ n_estimators │ Accuracy │ F1     │
├────────────────────────────────────────────────────────────┤
│  abc123    │ LightGBM  │ 100          │ 0.95     │ 0.93   │
│  def456    │ XGBoost   │ 200          │ 0.94     │ 0.92   │
│  ghi789    │ RF        │ 150          │ 0.92     │ 0.90   │
└────────────────────────────────────────────────────────────┘

Easy comparison across experiments!
```

---

## Practical AutoML Workflow

### Step-by-Step AutoML Process

```
PRODUCTION AUTOML WORKFLOW:
───────────────────────────

1. DATA PREPARATION
   ├── Load data
   ├── Basic cleaning (handle missing, remove duplicates)
   ├── Define target variable
   └── Split train/validation/test

2. QUICK AUTOML RUN (1 hour)
   ├── Use AutoGluon with time_limit=3600
   ├── Get baseline performance
   └── Identify promising models

3. ANALYZE RESULTS
   ├── Check feature importance
   ├── Look for data leakage
   └── Understand model behavior

4. EXTENDED RUN (optional)
   ├── Run AutoGluon with more time
   ├── Try different presets (best_quality vs optimize_for_deployment)
   └── Experiment with hyperparameter ranges

5. MODEL SELECTION
   ├── Compare accuracy vs inference time
   ├── Consider interpretability needs
   └── Check model size for deployment

6. PRODUCTION PREPARATION
   ├── Export best model
   ├── Create feature pipeline
   ├── Set up monitoring
   └── Deploy with gradual rollout
```

### AutoGluon Presets

```
AUTOGLUON PRESETS:
──────────────────

PRESET: "best_quality"
  - Maximum accuracy
  - Uses all algorithms
  - Deep stacking ensembles
  - Time: 4-8x longer
  - Use for: Final production models

PRESET: "high_quality"
  - Near-optimal accuracy
  - Good ensemble
  - Reasonable time
  - Use for: Most use cases

PRESET: "good_quality"
  - Good accuracy
  - Faster training
  - Use for: Prototyping

PRESET: "medium_quality"
  - Decent accuracy
  - Much faster
  - Use for: Quick baselines

PRESET: "optimize_for_deployment"
  - Single model (no ensemble)
  - Fast inference
  - Smaller model size
  - Use for: Real-time serving
```

---

## Common Pitfalls and Best Practices

### AutoML Pitfalls

```
COMMON AUTOML MISTAKES:
───────────────────────

1. DATA LEAKAGE
   ───────────────
   Problem: Target information leaks into features

   Example: Predicting "will customer churn?"
   Bad feature: "cancellation_date" (directly reveals answer!)

   Solution: Review feature importance, suspicious features
             that are too predictive are often leaky


2. OVERFITTING TO VALIDATION
   ──────────────────────────
   Problem: Running AutoML many times, picking best

   Each run: Accuracy = 0.91, 0.92, 0.93, 0.94, 0.90...
   Pick best: 0.94!
   Test set:  0.88  (overfit to validation)

   Solution: Hold out a TRUE test set, evaluate once at end


3. IGNORING BUSINESS CONSTRAINTS
   ───────────────────────────────
   Problem: Best model has 200ms latency, need < 10ms

   AutoGluon best model: Stacked ensemble
   Inference time: 200ms

   Solution: Use optimize_for_deployment preset
             or constrain model types


4. FEATURE STORE SKEW
   ────────────────────
   Problem: Training features differ from serving features

   Training: feature_v1 (old transformation)
   Serving:  feature_v2 (new transformation)

   Solution: Use feature store with versioning
```

### Best Practices

```
AUTOML BEST PRACTICES:
──────────────────────

1. START SIMPLE
   - Run quick AutoML first (30 min - 1 hour)
   - Get baseline before investing more time
   - Understand what's possible

2. FEATURE ENGINEERING STILL MATTERS
   - AutoML optimizes models, not features
   - Domain features often help
   - Combine AutoML + manual feature eng

3. USE PROPER VALIDATION
   - Time-based splits for time series
   - Stratified for imbalanced classes
   - Group splits for related samples

4. MONITOR IN PRODUCTION
   - Track feature distributions
   - Monitor model performance
   - Set up drift detection

5. DOCUMENT EVERYTHING
   - Which AutoML settings?
   - What features used?
   - Business metrics impact?
```

**Did You Know?** Google's AutoML Tables (now part of Vertex AI) automatically applies over 100 different data preprocessing and feature engineering transformations. When tested on the OpenML benchmark suite, it achieved state-of-the-art results on 60% of datasets - often surpassing manually tuned models!

---

## Summary

```
KEY CONCEPTS RECAP:
───────────────────

AUTOML:
  - Automates algorithm selection + hyperparameter tuning
  - AutoGluon: Best accuracy, multi-layer stacking
  - Use presets based on needs (quality vs speed)

FEATURE STORES:
  - Centralized feature management
  - Point-in-time correctness for training
  - Online/offline serving
  - Feast: Open source, easy to start

AUTOMATED FEATURE ENGINEERING:
  - Aggregations, transformations, time features
  - Featuretools for deep feature synthesis
  - Still combine with domain knowledge

ML PIPELINES:
  - End-to-end automation
  - MLflow for experiment tracking
  - Orchestration (Airflow, Dagster)


WHEN TO USE WHAT:
─────────────────

┌─────────────────────────────────────────────────────────────┐
│  SCENARIO                  │  RECOMMENDATION                │
├─────────────────────────────────────────────────────────────┤
│  Quick baseline            │  AutoGluon, medium_quality     │
│  Production model          │  AutoGluon, best_quality       │
│  Real-time serving         │  AutoGluon, optimize_for_deployment│
│  Feature reuse             │  Feast feature store           │
│  Relational data           │  Featuretools + AutoML         │
│  Team collaboration        │  Feature store + MLflow        │
└─────────────────────────────────────────────────────────────┘
```

---

## Further Reading

### Tools
- **AutoGluon**: https://auto.gluon.ai/
- **Feast**: https://feast.dev/
- **MLflow**: https://mlflow.org/
- **Featuretools**: https://featuretools.alteryx.com/

### Papers
- "AutoGluon-Tabular: Robust and Accurate AutoML for Structured Data" (2020)
- "Feast: Feature Store for Machine Learning" (2021)
- "Auto-sklearn 2.0" (2020)

---

## Next Steps

You've completed Phase 8: Classical ML! You now understand:
- Gradient boosting (XGBoost, LightGBM)
- Time series forecasting (ARIMA, Prophet)
- AutoML and feature stores

**Up Next**: Phase 9 - AI Safety & Evaluation

---

_Module 39 Complete!_
_"AutoML doesn't replace ML engineers - it multiplies their productivity."_
