# Module 25 Deliverable: ML Data Toolkit

**Your complete toolkit for machine learning data preparation, analysis, and visualization.**

## Features

- **DataProfiler**: Generate comprehensive dataset profiles with statistics
- **DataCleaner**: Handle missing values, outliers, duplicates automatically
- **FeatureEngineer**: Create polynomial, interaction, log, and encoded features
- **DataVisualizer**: Generate publication-quality EDA visualizations
- **NumpyBenchmarker**: Demonstrate NumPy's performance advantages

## Quick Start

```bash
python deliverable_ml_data_toolkit.py demo1  # Data profiling
python deliverable_ml_data_toolkit.py demo2  # Feature engineering
python deliverable_ml_data_toolkit.py demo3  # Generate visualizations
python deliverable_ml_data_toolkit.py demo4  # NumPy benchmarks
python deliverable_ml_data_toolkit.py demo5  # Complete ML pipeline
```

## Components

### DataProfiler

Generates detailed profiles of your dataset:

```python
from deliverable_ml_data_toolkit import DataProfiler, create_sample_dataset

df = create_sample_dataset(1000)
profiler = DataProfiler()
profile = profiler.profile(df, "my_dataset")
profiler.print_report(profile)
```

Profile includes:
- Shape, memory usage
- Column types (numeric, categorical, datetime)
- Missing value counts and percentages
- Statistical summaries (mean, std, quartiles, skewness)
- Top values for categorical columns

### DataCleaner

Automated data cleaning:

```python
from deliverable_ml_data_toolkit import DataCleaner

cleaner = DataCleaner()
df_clean = cleaner.clean(df, {
    'missing_strategy': 'smart',      # 'smart', 'drop', 'zero'
    'remove_duplicates': True,
    'handle_outliers': True,
    'outlier_method': 'clip',         # 'clip' or 'remove'
    'outlier_threshold': 3.0,         # Z-score threshold
    'optimize_types': True
})
```

### FeatureEngineer

Create features for ML:

```python
from deliverable_ml_data_toolkit import FeatureEngineer

engineer = FeatureEngineer()
df_eng, result = engineer.engineer_features(df, {
    'polynomial': True,
    'polynomial_columns': ['age', 'income'],
    'polynomial_degree': 2,
    'interactions': True,
    'interaction_columns': ['age', 'income', 'credit_score'],
    'log_transform': True,
    'log_columns': ['income'],
    'one_hot': True
})

# Scale features
df_scaled, params = engineer.scale_features(df_eng, method='standard')
```

### DataVisualizer

Generate EDA visualizations:

```python
from deliverable_ml_data_toolkit import DataVisualizer

visualizer = DataVisualizer()
plots = visualizer.generate_eda_report(df, target_col='churned')
```

Generated plots:
- Feature distributions with KDE
- Correlation heatmap
- Target variable distribution
- Categorical feature distributions
- Missing data visualization

### NumpyBenchmarker

Compare NumPy vs Python performance:

```python
from deliverable_ml_data_toolkit import NumpyBenchmarker

benchmarker = NumpyBenchmarker()
results = benchmarker.run_benchmarks()
```

## Performance Highlights

| Operation | Python | NumPy | Speedup |
|-----------|--------|-------|---------|
| Vector Add (1M) | ~800ms | ~3ms | **~270x** |
| Dot Product (1M) | ~600ms | ~2ms | **~300x** |
| Matrix Mult (500x500) | >60s | ~20ms | **>1000x** |
| Statistics (1M) | ~400ms | ~5ms | **~80x** |

## Output Structure

```
.ml_data_toolkit/
├── data_profiles.json    # Cached profiles (JSON persistence)
├── cache.json            # General cache
└── plots/
    ├── distributions.png
    ├── correlation.png
    ├── target_distribution.png
    ├── categorical.png
    ├── missing_data.png
    └── ...
```

## Complete Pipeline Example

```python
from deliverable_ml_data_toolkit import (
    DataProfiler, DataCleaner, FeatureEngineer,
    DataVisualizer, create_sample_dataset
)

# 1. Load data
df = create_sample_dataset(1000)

# 2. Profile
profiler = DataProfiler()
profile = profiler.profile(df, "customer_data")

# 3. Clean
cleaner = DataCleaner()
df_clean = cleaner.clean(df, {'missing_strategy': 'smart'})

# 4. Engineer features
engineer = FeatureEngineer()
df_eng, result = engineer.engineer_features(df_clean, {
    'polynomial': True,
    'log_transform': True,
    'one_hot': True
})

# 5. Scale
X = df_eng.drop(columns=['churned'])
y = df_eng['churned']
X_scaled, params = engineer.scale_features(X)

# 6. Visualize
visualizer = DataVisualizer()
plots = visualizer.generate_eda_report(df_clean, 'churned')

# 7. Split and train!
train_size = int(0.8 * len(X_scaled))
X_train, X_test = X_scaled.iloc[:train_size], X_scaled.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
```

## Key Takeaways

1. **NumPy is essential**: 10-1000x faster than pure Python
2. **pandas for data wrangling**: 80% of ML is data preparation
3. **Always visualize**: Catch issues before they ruin your model
4. **Clean before training**: Handle missing values and outliers
5. **Feature engineering matters**: Often more important than model choice

**Time**: ~5 hours | **Lines**: 900+ | **Author**: Neural Dojo
