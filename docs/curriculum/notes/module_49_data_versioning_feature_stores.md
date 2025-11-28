# Module 49: Data Versioning & Feature Stores

**Last Updated**: 2025-11-28
**Status**: 🟢 Complete
**Duration**: 6-7 hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master DVC for dataset and model versioning
- Understand feature stores and implement Feast
- Implement data validation with Great Expectations
- Build reproducible ML pipelines with versioned data
- Understand data lineage and governance

---

## 📖 Theory

### The Data Management Problem

Data is the foundation of ML, but it's often treated as an afterthought:

```
THE DATA CHAOS PROBLEM
======================

Without Versioning:
───────────────────
"Which version of the dataset was model v2.3 trained on?"
"Did someone update the preprocessing script?"
"Why do we get different results on the same code?"

    data/
    ├── train.csv
    ├── train_v2.csv
    ├── train_final.csv
    ├── train_FINAL_real.csv
    └── train_USE_THIS_ONE.csv

With DVC:
─────────
    data/
    └── train.csv.dvc  ← Tracked in Git, points to versioned data

    git log:
    - commit abc123: "Add train data v3.2 (50K samples)"
    - commit def456: "Update train data v3.1 (45K samples)"
    - commit ghi789: "Initial train data v3.0 (40K samples)"
```

**Did You Know?** A 2022 survey by Gartner found that 85% of AI projects fail, with "data quality issues" cited as the #1 reason. Google's ML team reported that data-related issues cause 60% of production ML failures. This led to the "Data-Centric AI" movement championed by Andrew Ng, shifting focus from model architecture to data quality and versioning.

---

## 1. DVC: Data Version Control

### What is DVC?

DVC (Data Version Control) is Git for data and ML models. It tracks large files, datasets, and ML pipelines.

```
DVC ARCHITECTURE
================

┌─────────────────────────────────────────────────────────────────────┐
│                           DVC                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   Data Files    │  │    Pipelines    │  │    Metrics      │    │
│  │                 │  │                 │  │                 │    │
│  │ • .dvc files    │  │ • dvc.yaml      │  │ • dvc metrics   │    │
│  │ • Remote storage│  │ • Reproducible  │  │ • Experiments   │    │
│  │ • Cache         │  │ • Dependencies  │  │ • Comparisons   │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Remote Storage                            │   │
│  │  S3 | GCS | Azure Blob | SSH | Local | HTTP | HDFS          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Basic DVC Workflow

```bash
# Initialize DVC in a Git repo
cd my-ml-project
git init
dvc init

# Add data to DVC tracking
dvc add data/train.csv
# Creates: data/train.csv.dvc (small text file, tracked by Git)
# Actual data stored in .dvc/cache/

# Commit the .dvc file
git add data/train.csv.dvc data/.gitignore
git commit -m "Add training data v1.0"

# Push data to remote storage
dvc remote add -d myremote s3://my-bucket/dvc-cache
dvc push

# Later: pull data on another machine
git clone <repo>
dvc pull
```

### .dvc File Format

```yaml
# data/train.csv.dvc
outs:
  - md5: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    size: 1048576
    path: train.csv
```

### DVC Pipelines

DVC can track entire ML pipelines with dependencies:

```yaml
# dvc.yaml
stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - src/preprocess.py
      - data/raw/
    params:
      - preprocess.split_ratio
    outs:
      - data/processed/

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/
    params:
      - train.learning_rate
      - train.epochs
    outs:
      - models/model.pkl
    metrics:
      - metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/processed/test.csv
    metrics:
      - evaluation.json:
          cache: false
```

```
DVC PIPELINE DAG
================

     ┌────────────────┐
     │   data/raw/    │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │  preprocess    │
     │                │
     │  deps:         │
     │  - raw data    │
     │  - script      │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │    train       │
     │                │
     │  deps:         │
     │  - processed   │
     │  - params      │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │   evaluate     │
     │                │
     │  outputs:      │
     │  - metrics     │
     └────────────────┘
```

**Did You Know?** DVC was created by Dmitry Petrov, a former Microsoft data scientist, in 2017. The name is a play on "CSV" (Comma-Separated Values), which is ironic since DVC handles any file type. Iterative.ai, the company behind DVC, raised $20M in funding. DVC is used by companies like Intel, Microsoft, and Hugging Face.

### DVC Experiments

```bash
# Run experiment with parameter changes
dvc exp run -S train.learning_rate=0.001 -S train.epochs=20

# List experiments
dvc exp show

# Compare experiments
dvc exp diff exp-abc123 exp-def456

# Apply best experiment
dvc exp apply exp-abc123
git commit -m "Apply best experiment"
```

---

## 2. Feature Stores

### The Feature Engineering Problem

```
FEATURE ENGINEERING CHAOS
=========================

Without Feature Store:
──────────────────────
Team A: "We compute user_age from birthdate"
Team B: "We compute age from signup_year - birth_year"
Team C: "We use age_bucket categorical feature"

Result: Same feature, 3 different implementations!

Training vs Serving Skew:
────────────────────────
Training: Features computed in batch (Spark, 1 hour lag)
Serving:  Features computed in real-time (different code)
Result:   Model works in training, fails in production!

With Feature Store:
──────────────────
┌─────────────────────────────────────────────────────────────────┐
│                     FEATURE STORE                               │
├─────────────────────────────────────────────────────────────────┤
│  Single source of truth for all features                        │
│  Same features for training AND serving                         │
│  Versioning, lineage, discovery                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Feast: Open-Source Feature Store

```
FEAST ARCHITECTURE
==================

┌─────────────────────────────────────────────────────────────────────┐
│                           FEAST                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ Feature Repo    │  │  Offline Store  │  │  Online Store   │    │
│  │                 │  │                 │  │                 │    │
│  │ • Definitions   │  │ • Historical    │  │ • Low latency   │    │
│  │ • Transformations│ │ • Batch queries │  │ • Real-time     │    │
│  │ • Metadata      │  │ • Training data │  │ • Serving       │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                              │                     │               │
│                              ▼                     ▼               │
│                       ┌───────────┐         ┌───────────┐         │
│                       │ BigQuery  │         │   Redis   │         │
│                       │ Snowflake │         │ DynamoDB  │         │
│                       │ Redshift  │         │ Postgres  │         │
│                       └───────────┘         └───────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Feast Feature Definitions

```python
# feature_repo/features.py
from datetime import timedelta
from feast import Entity, Feature, FeatureView, FileSource, ValueType

# Define entity (the thing we're making predictions about)
user = Entity(
    name="user_id",
    value_type=ValueType.INT64,
    description="User identifier"
)

# Define data source
user_features_source = FileSource(
    path="data/user_features.parquet",
    event_timestamp_column="event_timestamp",
    created_timestamp_column="created_timestamp"
)

# Define feature view
user_features = FeatureView(
    name="user_features",
    entities=["user_id"],
    ttl=timedelta(days=365),
    features=[
        Feature(name="age", dtype=ValueType.INT64),
        Feature(name="total_purchases", dtype=ValueType.INT64),
        Feature(name="avg_order_value", dtype=ValueType.FLOAT),
        Feature(name="days_since_last_purchase", dtype=ValueType.INT64),
        Feature(name="favorite_category", dtype=ValueType.STRING),
    ],
    online=True,
    source=user_features_source
)
```

### Using Feast

```python
from feast import FeatureStore
import pandas as pd

# Initialize feature store
store = FeatureStore(repo_path="feature_repo/")

# Get training data (historical features)
entity_df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "event_timestamp": pd.to_datetime(["2024-01-01"] * 5)
})

training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_features:age",
        "user_features:total_purchases",
        "user_features:avg_order_value",
    ]
).to_df()

# Get online features (real-time serving)
online_features = store.get_online_features(
    features=[
        "user_features:age",
        "user_features:total_purchases",
        "user_features:avg_order_value",
    ],
    entity_rows=[{"user_id": 123}]
).to_dict()
```

**Did You Know?** Feature stores emerged from Uber's Michelangelo platform (2017), which was built to solve the training-serving skew problem. Uber found that 60% of their ML bugs came from feature engineering inconsistencies. Feast was created by Gojek and later joined the Linux Foundation AI & Data. Today, major cloud providers have their own feature stores: AWS SageMaker Feature Store, GCP Vertex AI Feature Store, and Azure Machine Learning Feature Store.

---

## 3. Data Validation with Great Expectations

### Why Data Validation?

```
DATA QUALITY ISSUES
===================

Common Problems:
────────────────
• Missing values increased from 1% to 15%
• Categorical column has new unexpected values
• Numerical column has outliers (negative ages)
• Data distribution shifted (concept drift)
• Schema changed (new columns, renamed fields)

Without Validation:
───────────────────
Data pipeline runs successfully...
Model trains successfully...
Model deployed successfully...
💥 Model makes terrible predictions!
"Why is the model predicting -$500 orders?"

With Great Expectations:
───────────────────────
✅ Data validated before training
✅ Expectations documented
✅ Failed validations alert immediately
✅ Data quality is part of CI/CD
```

### Great Expectations Concepts

```
GREAT EXPECTATIONS ARCHITECTURE
===============================

┌─────────────────────────────────────────────────────────────────────┐
│                    GREAT EXPECTATIONS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Expectations   │  │   Datasources   │  │   Checkpoints   │    │
│  │                 │  │                 │  │                 │    │
│  │ • Rules         │  │ • Pandas        │  │ • Validation    │    │
│  │ • Tests         │  │ • Spark         │  │   runs          │    │
│  │ • Documentation │  │ • SQL           │  │ • Actions       │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Data Docs                                 │   │
│  │  Auto-generated HTML documentation of expectations          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Common Expectations

```python
import great_expectations as gx

# Create context
context = gx.get_context()

# Define expectations for a dataset
expectation_suite = context.add_expectation_suite("user_data_suite")

# Column existence
validator.expect_column_to_exist("user_id")
validator.expect_column_to_exist("age")
validator.expect_column_to_exist("email")

# Data types
validator.expect_column_values_to_be_of_type("user_id", "int64")
validator.expect_column_values_to_be_of_type("age", "int64")
validator.expect_column_values_to_be_of_type("email", "str")

# Null checks
validator.expect_column_values_to_not_be_null("user_id")
validator.expect_column_values_to_not_be_null("email")

# Value ranges
validator.expect_column_values_to_be_between("age", min_value=0, max_value=120)
validator.expect_column_values_to_be_between("purchase_amount", min_value=0)

# Uniqueness
validator.expect_column_values_to_be_unique("user_id")
validator.expect_column_values_to_be_unique("email")

# Patterns
validator.expect_column_values_to_match_regex(
    "email",
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Categorical values
validator.expect_column_values_to_be_in_set(
    "country",
    ["US", "UK", "CA", "DE", "FR"]
)

# Distribution checks
validator.expect_column_mean_to_be_between("age", min_value=25, max_value=45)
validator.expect_column_stdev_to_be_between("purchase_amount", min_value=10, max_value=100)

# Row count
validator.expect_table_row_count_to_be_between(min_value=1000, max_value=1000000)

# Column count
validator.expect_table_column_count_to_equal(15)
```

### Running Validations

```python
# Create checkpoint for automated validation
checkpoint = context.add_checkpoint(
    name="user_data_checkpoint",
    validations=[
        {
            "batch_request": {
                "datasource_name": "my_datasource",
                "data_asset_name": "user_data",
            },
            "expectation_suite_name": "user_data_suite",
        }
    ]
)

# Run checkpoint
results = checkpoint.run()

# Check if validation passed
if not results.success:
    print("Data validation failed!")
    for result in results.run_results.values():
        for validation_result in result.validation_result.results:
            if not validation_result.success:
                print(f"  ❌ {validation_result.expectation_config.expectation_type}")
```

**Did You Know?** Great Expectations was created by Abe Gong and James Campbell in 2017 at Superconductive, a data reliability startup. The name comes from the Charles Dickens novel, symbolizing the "expectations" we have for our data. The project has over 8,000 GitHub stars and is used by companies like GitHub, Shopify, and Heineken.

---

## 4. Data Lineage & Governance

### What is Data Lineage?

```
DATA LINEAGE
============

Lineage tracks where data comes from and where it goes:

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Raw Data   │────►│ Transformed │────►│   Model     │
│  (S3)       │     │   (Spark)   │     │  Features   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Training   │────►│   Model     │
                    │   Data      │     │  v2.3.1     │
                    └─────────────┘     └─────────────┘

Questions Lineage Answers:
─────────────────────────
• What data was used to train model v2.3.1?
• Which models will be affected if table X changes?
• Who created this feature and when?
• What transformations were applied to this data?
```

### Data Governance Best Practices

```
DATA GOVERNANCE CHECKLIST
=========================

✅ Version Control
   • All data versioned (DVC)
   • All code versioned (Git)
   • All configs versioned

✅ Data Quality
   • Expectations defined (Great Expectations)
   • Automated validation in pipelines
   • Alerting on failures

✅ Documentation
   • Data dictionaries
   • Feature definitions
   • Schema documentation

✅ Access Control
   • Role-based access
   • Audit logging
   • PII handling

✅ Lineage
   • End-to-end tracking
   • Impact analysis
   • Reproducibility
```

---

## 5. Tool Comparison

### When to Use What

```
TOOL SELECTION MATRIX
=====================

┌────────────────────┬─────────────────────────────────────────────────┐
│     Problem        │              Solution                           │
├────────────────────┼─────────────────────────────────────────────────┤
│ Version large      │ DVC                                             │
│ datasets           │ • Git-like workflow for data                    │
│                    │ • Remote storage integration                    │
├────────────────────┼─────────────────────────────────────────────────┤
│ Share features     │ Feast / Feature Store                           │
│ across teams       │ • Centralized definitions                       │
│                    │ • Same features train & serve                   │
├────────────────────┼─────────────────────────────────────────────────┤
│ Validate data      │ Great Expectations                              │
│ quality            │ • Schema validation                             │
│                    │ • Distribution checks                           │
├────────────────────┼─────────────────────────────────────────────────┤
│ Track data         │ OpenLineage / DataHub                           │
│ lineage            │ • End-to-end tracking                           │
│                    │ • Impact analysis                               │
├────────────────────┼─────────────────────────────────────────────────┤
│ All-in-one         │ DVC + Great Expectations + Feast                │
│ data platform      │ • Full data lifecycle                           │
│                    │ • Can be overwhelming for small teams           │
└────────────────────┴─────────────────────────────────────────────────┘
```

### Complexity vs Value

```
TOOL COMPLEXITY
===============

High │                              ┌─────────────┐
     │                     ┌────────│ Full Data   │
     │              ┌──────│        │ Platform    │
     │       ┌──────│Feast │        └─────────────┘
V    │       │      │      │
A    │       │      └──────┘
L    │       │ Great
U    │       │ Expectations
E    │       └──────┘
     │ ┌──────┐
     │ │ DVC  │
     │ └──────┘
     │
Low  └─────────────────────────────────────────────────►
                     COMPLEXITY
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Set Up DVC

```bash
# Initialize
pip install dvc dvc-s3
git init
dvc init

# Add data
dvc add data/train.csv
git add data/train.csv.dvc
git commit -m "Add training data"

# Set up remote
dvc remote add -d myremote s3://bucket/path
dvc push
```

### Exercise 2: Define Feast Features

```python
from feast import Entity, Feature, FeatureView

# Define features following Feast patterns
user = Entity(name="user_id", value_type=ValueType.INT64)
```

### Exercise 3: Create Expectations

```python
import great_expectations as gx

context = gx.get_context()
suite = context.add_expectation_suite("my_suite")
# Add expectations...
```

---

## 📚 Further Reading

### Documentation
- [DVC Documentation](https://dvc.org/doc)
- [Feast Documentation](https://docs.feast.dev/)
- [Great Expectations](https://docs.greatexpectations.io/)

### Papers & Articles
- "Hidden Technical Debt in Machine Learning Systems" (Google, 2015)
- "Data Management Challenges in Production ML" (Polyzotis et al., 2018)
- "Feast: Feature Store for Machine Learning" (Gojek, 2020)

---

## ✅ Knowledge Check

1. **What problem does DVC solve that Git doesn't?**

2. **What is training-serving skew and how do feature stores prevent it?**

3. **Name 5 common Great Expectations validators.**

4. **When would you choose Feast over just using DVC?**

5. **What is data lineage and why is it important?**

---

## ⏭️ Next Steps

You now understand data versioning and feature stores! These are critical for reproducible ML.

**Up Next**: Module 50 - ML Pipeline & Workflow Orchestration

---

_Module 49 Complete! You now understand DVC, Feast, and Great Expectations!_
_"Bad data = bad models. Version your data like you version your code."_
