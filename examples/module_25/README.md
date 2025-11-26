# Module 25: Python for Machine Learning

This directory contains examples and tools for mastering the Scientific Python ecosystem - the foundation of all machine learning in Python.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: NumPy Fundamentals
**File**: `example_01_numpy_fundamentals.py`

Comprehensive guide to NumPy including:
- Array creation and manipulation
- Indexing and slicing
- Broadcasting
- Vectorized operations
- Linear algebra
- Performance benchmarks (NumPy vs pure Python)
- ML-specific operations

```bash
python example_01_numpy_fundamentals.py
```

### Example 2: pandas Essentials
**File**: `example_02_pandas_essentials.py`

Complete pandas tutorial covering:
- DataFrame creation and exploration
- Data selection (.loc, .iloc, boolean indexing)
- Data cleaning (missing values, duplicates, types)
- Transformations (apply, map, cut)
- Groupby and aggregation
- Merging and joining
- Pivot tables and reshaping
- Time series operations
- ML preprocessing pipeline

```bash
python example_02_pandas_essentials.py
```

### Example 3: Data Visualization
**File**: `example_03_visualization.py`

matplotlib and seaborn visualization guide:
- matplotlib basics (line, scatter, bar, histogram)
- Subplots and multiple plots
- seaborn statistical visualizations
- Correlation heatmaps
- Pair plots for EDA
- ML-specific visualizations (training curves, confusion matrix, ROC, feature importance)
- Complete EDA dashboard

```bash
python example_03_visualization.py
```

Plots are saved to `plots/` directory.

## Main Deliverable: ML Data Toolkit

**File**: `deliverable_ml_data_toolkit.py`

A comprehensive toolkit for ML data preparation with:

- **DataProfiler**: Analyze dataset structure, statistics, and quality
- **DataCleaner**: Handle missing values, outliers, duplicates
- **FeatureEngineer**: Create polynomial, interaction, and transformed features
- **DataVisualizer**: Generate EDA visualizations automatically
- **NumpyBenchmarker**: Compare NumPy vs Python performance

### Quick Start

```bash
# Data profiling
python deliverable_ml_data_toolkit.py demo1

# Feature engineering
python deliverable_ml_data_toolkit.py demo2

# Generate visualizations
python deliverable_ml_data_toolkit.py demo3

# NumPy benchmarks
python deliverable_ml_data_toolkit.py demo4

# Complete ML pipeline
python deliverable_ml_data_toolkit.py demo5

# Show help
python deliverable_ml_data_toolkit.py help
```

## Key Concepts

### NumPy - The Foundation
- Arrays are 10-1000x faster than Python lists
- Broadcasting enables elegant, vectorized operations
- Linear algebra operations power all ML algorithms
- **Rule**: Never write Python loops for numerical computation!

### pandas - Data Manipulation
- DataFrame is your primary data structure for ML
- 80% of ML work is data preparation
- Handle missing values BEFORE training
- One-hot encode categorical variables

### Visualization - Understanding Data
- Always visualize before modeling
- Correlation heatmaps reveal feature relationships
- Distribution plots identify outliers and skewness
- Use appropriate plots for different data types

## Performance Results (from demo4)

| Operation | Size | Python | NumPy | Speedup |
|-----------|------|--------|-------|---------|
| Vector Add | 1M | ~800ms | ~3ms | ~270x |
| Dot Product | 1M | ~600ms | ~2ms | ~300x |
| Matrix Mult | 500x500 | too slow | ~20ms | >1000x |
| Statistics | 1M | ~400ms | ~5ms | ~80x |

## Output Files

```
.ml_data_toolkit/
├── data_profiles.json    # Cached data profiles
├── cache.json            # General cache
└── plots/
    ├── distributions.png
    ├── correlation.png
    ├── target_distribution.png
    ├── categorical.png
    └── missing_data.png
```

## Notes

- NumPy operations leverage optimized BLAS/LAPACK libraries
- pandas built on NumPy for performance
- Visualization helps catch data quality issues early
- These tools form the foundation for PyTorch and TensorFlow

## Further Reading

- [NumPy User Guide](https://numpy.org/doc/stable/user/index.html)
- [pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
