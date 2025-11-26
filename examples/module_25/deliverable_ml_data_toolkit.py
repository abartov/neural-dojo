#!/usr/bin/env python3
"""
Module 25 Deliverable: ML Data Toolkit

A comprehensive toolkit for machine learning data preparation, analysis,
and visualization. Provides reusable functions for the complete ML data
pipeline from raw data to model-ready features.

Features:
- Data loading and exploration
- Automated data cleaning and preprocessing
- Feature engineering utilities
- Statistical analysis and profiling
- Visualization generation
- NumPy performance benchmarks
- JSON-based configuration and caching

Usage:
    python deliverable_ml_data_toolkit.py demo1    # Data profiling
    python deliverable_ml_data_toolkit.py demo2    # Feature engineering
    python deliverable_ml_data_toolkit.py demo3    # Visualization generation
    python deliverable_ml_data_toolkit.py demo4    # NumPy benchmarks
    python deliverable_ml_data_toolkit.py demo5    # Full pipeline
    python deliverable_ml_data_toolkit.py help     # Show help
"""

import json
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# Storage directory for caching and outputs
STORAGE_DIR = Path(__file__).parent / ".ml_data_toolkit"
STORAGE_DIR.mkdir(exist_ok=True)

PLOTS_DIR = STORAGE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

CACHE_FILE = STORAGE_DIR / "cache.json"
PROFILE_FILE = STORAGE_DIR / "data_profiles.json"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ColumnProfile:
    """Profile of a single column."""
    name: str
    dtype: str
    count: int
    missing: int
    missing_pct: float
    unique: int
    unique_pct: float
    # Numeric stats (if applicable)
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    # Categorical stats (if applicable)
    top_values: Optional[Dict[str, int]] = None


@dataclass
class DataProfile:
    """Complete profile of a dataset."""
    name: str
    rows: int
    columns: int
    memory_mb: float
    created_at: str
    column_profiles: List[ColumnProfile] = field(default_factory=list)
    # Dataset-level stats
    total_missing: int = 0
    total_missing_pct: float = 0.0
    numeric_columns: List[str] = field(default_factory=list)
    categorical_columns: List[str] = field(default_factory=list)
    datetime_columns: List[str] = field(default_factory=list)


@dataclass
class FeatureEngineeringResult:
    """Result of feature engineering operations."""
    original_features: int
    new_features: int
    total_features: int
    operations_applied: List[str] = field(default_factory=list)
    feature_names: List[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark."""
    operation: str
    python_time_ms: float
    numpy_time_ms: float
    speedup: float
    size: int


@dataclass
class PipelineResult:
    """Result of running the complete ML pipeline."""
    original_shape: Tuple[int, int]
    final_shape: Tuple[int, int]
    cleaning_steps: List[str] = field(default_factory=list)
    feature_engineering_steps: List[str] = field(default_factory=list)
    train_size: int = 0
    test_size: int = 0


# =============================================================================
# Core Classes
# =============================================================================

class DataProfiler:
    """
    Generate comprehensive profiles of datasets.

    Analyzes structure, statistics, and quality of data.
    """

    def __init__(self):
        self.profiles: Dict[str, DataProfile] = {}
        self._load_cache()

    def _load_cache(self):
        """Load cached profiles."""
        if PROFILE_FILE.exists():
            try:
                with open(PROFILE_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert back to dataclasses
                    for name, profile_dict in data.items():
                        cols = [ColumnProfile(**c) for c in profile_dict.pop('column_profiles', [])]
                        self.profiles[name] = DataProfile(**profile_dict, column_profiles=cols)
            except (json.JSONDecodeError, TypeError):
                self.profiles = {}

    def _save_cache(self):
        """Save profiles to cache."""
        data = {}
        for name, profile in self.profiles.items():
            profile_dict = asdict(profile)
            data[name] = profile_dict

        with open(PROFILE_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def profile(self, df: pd.DataFrame, name: str = "dataset") -> DataProfile:
        """
        Generate a comprehensive profile of the DataFrame.

        Args:
            df: DataFrame to profile
            name: Name for the profile

        Returns:
            DataProfile with complete statistics
        """
        print(f"\n{'='*60}")
        print(f"Profiling Dataset: {name}")
        print(f"{'='*60}")

        # Basic info
        rows, cols = df.shape
        memory_mb = df.memory_usage(deep=True).sum() / 1e6

        print(f"\n Shape: {rows:,} rows x {cols} columns")
        print(f" Memory: {memory_mb:.2f} MB")

        # Classify columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        print(f"\n Column Types:")
        print(f"   Numeric: {len(numeric_cols)}")
        print(f"   Categorical: {len(categorical_cols)}")
        print(f"   Datetime: {len(datetime_cols)}")

        # Profile each column
        column_profiles = []

        print(f"\n{'─'*60}")
        print(f" Column Profiles:")
        print(f"{'─'*60}")

        for col in df.columns:
            profile = self._profile_column(df, col)
            column_profiles.append(profile)

            # Print summary
            missing_str = f"{profile.missing_pct:.1f}%" if profile.missing > 0 else "0%"
            print(f"   {col:<25} {profile.dtype:<10} missing: {missing_str:<8} unique: {profile.unique}")

        # Calculate total missing
        total_missing = sum(p.missing for p in column_profiles)
        total_missing_pct = (total_missing / (rows * cols)) * 100 if rows * cols > 0 else 0

        # Create profile
        profile = DataProfile(
            name=name,
            rows=rows,
            columns=cols,
            memory_mb=round(memory_mb, 2),
            created_at=datetime.now().isoformat(),
            column_profiles=column_profiles,
            total_missing=total_missing,
            total_missing_pct=round(total_missing_pct, 2),
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            datetime_columns=datetime_cols
        )

        # Cache it
        self.profiles[name] = profile
        self._save_cache()

        print(f"\n Total Missing: {total_missing:,} ({total_missing_pct:.2f}%)")
        print(f" Profile saved to: {PROFILE_FILE}")

        return profile

    def _profile_column(self, df: pd.DataFrame, col: str) -> ColumnProfile:
        """Profile a single column."""
        series = df[col]

        count = len(series)
        missing = series.isna().sum()
        missing_pct = (missing / count) * 100 if count > 0 else 0
        unique = series.nunique()
        unique_pct = (unique / count) * 100 if count > 0 else 0

        profile = ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            count=count,
            missing=int(missing),
            missing_pct=round(missing_pct, 2),
            unique=int(unique),
            unique_pct=round(unique_pct, 2)
        )

        # Numeric stats
        if pd.api.types.is_numeric_dtype(series):
            profile.mean = round(float(series.mean()), 4) if not series.isna().all() else None
            profile.std = round(float(series.std()), 4) if not series.isna().all() else None
            profile.min = round(float(series.min()), 4) if not series.isna().all() else None
            profile.q25 = round(float(series.quantile(0.25)), 4) if not series.isna().all() else None
            profile.median = round(float(series.median()), 4) if not series.isna().all() else None
            profile.q75 = round(float(series.quantile(0.75)), 4) if not series.isna().all() else None
            profile.max = round(float(series.max()), 4) if not series.isna().all() else None
            profile.skewness = round(float(series.skew()), 4) if not series.isna().all() else None
            profile.kurtosis = round(float(series.kurtosis()), 4) if not series.isna().all() else None

        # Categorical stats
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
            top_values = series.value_counts().head(5).to_dict()
            profile.top_values = {str(k): int(v) for k, v in top_values.items()}

        return profile

    def print_report(self, profile: DataProfile):
        """Print a detailed profile report."""
        print(f"\n{'='*60}")
        print(f" DATA PROFILE REPORT: {profile.name}")
        print(f"{'='*60}")

        print(f"\n OVERVIEW")
        print(f"   Rows: {profile.rows:,}")
        print(f"   Columns: {profile.columns}")
        print(f"   Memory: {profile.memory_mb:.2f} MB")
        print(f"   Total Missing: {profile.total_missing:,} ({profile.total_missing_pct:.1f}%)")

        print(f"\n COLUMN TYPES")
        print(f"   Numeric: {len(profile.numeric_columns)}")
        print(f"   Categorical: {len(profile.categorical_columns)}")
        print(f"   Datetime: {len(profile.datetime_columns)}")

        # Numeric column details
        if profile.numeric_columns:
            print(f"\n NUMERIC COLUMNS")
            for col_profile in profile.column_profiles:
                if col_profile.name in profile.numeric_columns:
                    print(f"\n   {col_profile.name}:")
                    print(f"      Range: [{col_profile.min}, {col_profile.max}]")
                    print(f"      Mean: {col_profile.mean}, Std: {col_profile.std}")
                    print(f"      Median: {col_profile.median}")
                    print(f"      Skewness: {col_profile.skewness}")

        # Categorical column details
        if profile.categorical_columns:
            print(f"\n CATEGORICAL COLUMNS")
            for col_profile in profile.column_profiles:
                if col_profile.name in profile.categorical_columns:
                    print(f"\n   {col_profile.name}: {col_profile.unique} unique values")
                    if col_profile.top_values:
                        for val, count in list(col_profile.top_values.items())[:3]:
                            print(f"      {val}: {count}")


class DataCleaner:
    """
    Clean and preprocess datasets for ML.

    Handles missing values, outliers, duplicates, and type conversions.
    """

    def __init__(self):
        self.cleaning_log: List[str] = []

    def clean(self, df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
        """
        Clean the DataFrame using specified configuration.

        Args:
            df: DataFrame to clean
            config: Cleaning configuration (optional)

        Returns:
            Cleaned DataFrame
        """
        config = config or {}
        self.cleaning_log = []

        df_clean = df.copy()
        original_rows = len(df_clean)

        print(f"\n{'='*60}")
        print(f"Cleaning Dataset")
        print(f"{'='*60}")
        print(f"Original shape: {df_clean.shape}")

        # 1. Remove duplicates
        if config.get('remove_duplicates', True):
            before = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            removed = before - len(df_clean)
            if removed > 0:
                self.cleaning_log.append(f"Removed {removed} duplicate rows")
                print(f" Removed {removed} duplicate rows")

        # 2. Handle missing values
        missing_strategy = config.get('missing_strategy', 'smart')
        df_clean = self._handle_missing(df_clean, missing_strategy)

        # 3. Handle outliers
        if config.get('handle_outliers', False):
            outlier_method = config.get('outlier_method', 'clip')
            outlier_threshold = config.get('outlier_threshold', 3.0)
            df_clean = self._handle_outliers(df_clean, outlier_method, outlier_threshold)

        # 4. Convert types
        if config.get('optimize_types', True):
            df_clean = self._optimize_types(df_clean)

        print(f"\nFinal shape: {df_clean.shape}")
        print(f"Rows retained: {len(df_clean)}/{original_rows} ({100*len(df_clean)/original_rows:.1f}%)")

        return df_clean

    def _handle_missing(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """Handle missing values based on strategy."""
        missing_before = df.isna().sum().sum()

        if strategy == 'drop':
            df = df.dropna()
            self.cleaning_log.append("Dropped rows with missing values")

        elif strategy == 'smart':
            # Numeric: fill with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isna().any():
                    df[col] = df[col].fillna(df[col].median())

            # Categorical: fill with mode
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            for col in cat_cols:
                if df[col].isna().any():
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col] = df[col].fillna(mode_val.iloc[0])

            self.cleaning_log.append("Filled missing: numeric=median, categorical=mode")

        elif strategy == 'zero':
            df = df.fillna(0)
            self.cleaning_log.append("Filled missing values with 0")

        missing_after = df.isna().sum().sum()
        if missing_before > missing_after:
            print(f" Handled missing: {missing_before} -> {missing_after}")

        return df

    def _handle_outliers(self, df: pd.DataFrame, method: str, threshold: float) -> pd.DataFrame:
        """Handle outliers in numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers_handled = 0

        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()

            if std > 0:
                z_scores = np.abs((df[col] - mean) / std)
                outlier_mask = z_scores > threshold
                outlier_count = outlier_mask.sum()

                if outlier_count > 0:
                    if method == 'clip':
                        lower = mean - threshold * std
                        upper = mean + threshold * std
                        df[col] = df[col].clip(lower, upper)
                    elif method == 'remove':
                        df = df[~outlier_mask]

                    outliers_handled += outlier_count

        if outliers_handled > 0:
            self.cleaning_log.append(f"Handled {outliers_handled} outliers ({method})")
            print(f" Handled {outliers_handled} outliers using {method}")

        return df

    def _optimize_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types for memory efficiency."""
        original_memory = df.memory_usage(deep=True).sum() / 1e6

        # Convert object columns with low cardinality to category
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique
                df[col] = df[col].astype('category')

        # Downcast numeric types
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')

        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')

        new_memory = df.memory_usage(deep=True).sum() / 1e6
        savings = original_memory - new_memory

        if savings > 0.01:
            self.cleaning_log.append(f"Optimized types: saved {savings:.2f}MB")
            print(f" Optimized types: {original_memory:.2f}MB -> {new_memory:.2f}MB")

        return df


class FeatureEngineer:
    """
    Create and transform features for ML models.

    Provides common feature engineering operations.
    """

    def __init__(self):
        self.operations_log: List[str] = []

    def engineer_features(self, df: pd.DataFrame, config: Optional[Dict] = None) -> Tuple[pd.DataFrame, FeatureEngineeringResult]:
        """
        Apply feature engineering operations.

        Args:
            df: DataFrame to transform
            config: Feature engineering configuration

        Returns:
            Tuple of (transformed DataFrame, result summary)
        """
        config = config or {}
        self.operations_log = []

        df_eng = df.copy()
        original_features = len(df_eng.columns)

        print(f"\n{'='*60}")
        print(f"Feature Engineering")
        print(f"{'='*60}")
        print(f"Original features: {original_features}")

        # 1. Polynomial features
        if config.get('polynomial', False):
            poly_cols = config.get('polynomial_columns', [])
            degree = config.get('polynomial_degree', 2)
            df_eng = self._add_polynomial_features(df_eng, poly_cols, degree)

        # 2. Interaction features
        if config.get('interactions', False):
            interaction_cols = config.get('interaction_columns', [])
            df_eng = self._add_interaction_features(df_eng, interaction_cols)

        # 3. Binning
        if config.get('binning', False):
            bin_cols = config.get('binning_columns', {})
            df_eng = self._add_binned_features(df_eng, bin_cols)

        # 4. Log transform
        if config.get('log_transform', False):
            log_cols = config.get('log_columns', [])
            df_eng = self._add_log_features(df_eng, log_cols)

        # 5. Date features
        datetime_cols = df_eng.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0 and config.get('date_features', True):
            df_eng = self._add_date_features(df_eng, datetime_cols.tolist())

        # 6. One-hot encoding
        if config.get('one_hot', True):
            cat_cols = df_eng.select_dtypes(include=['object', 'category']).columns.tolist()
            if cat_cols:
                df_eng = pd.get_dummies(df_eng, columns=cat_cols, drop_first=True)
                self.operations_log.append(f"One-hot encoded {len(cat_cols)} columns")

        new_features = len(df_eng.columns) - original_features

        result = FeatureEngineeringResult(
            original_features=original_features,
            new_features=new_features,
            total_features=len(df_eng.columns),
            operations_applied=self.operations_log.copy(),
            feature_names=df_eng.columns.tolist()
        )

        print(f"New features created: {new_features}")
        print(f"Total features: {result.total_features}")
        print(f"\nOperations applied:")
        for op in self.operations_log:
            print(f"   {op}")

        return df_eng, result

    def _add_polynomial_features(self, df: pd.DataFrame, columns: List[str], degree: int) -> pd.DataFrame:
        """Add polynomial features."""
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()[:3]

        for col in columns:
            if col in df.columns:
                for d in range(2, degree + 1):
                    df[f'{col}_pow{d}'] = df[col] ** d

        self.operations_log.append(f"Added polynomial features (degree={degree}) for {len(columns)} columns")
        print(f" Added polynomial features for: {columns}")
        return df

    def _add_interaction_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Add interaction features between columns."""
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()[:4]

        for i, col1 in enumerate(columns):
            for col2 in columns[i+1:]:
                if col1 in df.columns and col2 in df.columns:
                    df[f'{col1}_x_{col2}'] = df[col1] * df[col2]

        n_interactions = len(columns) * (len(columns) - 1) // 2
        self.operations_log.append(f"Added {n_interactions} interaction features")
        print(f" Added {n_interactions} interaction features")
        return df

    def _add_binned_features(self, df: pd.DataFrame, bin_config: Dict) -> pd.DataFrame:
        """Add binned versions of continuous features."""
        for col, n_bins in bin_config.items():
            if col in df.columns:
                df[f'{col}_binned'] = pd.cut(df[col], bins=n_bins, labels=False)

        self.operations_log.append(f"Binned {len(bin_config)} columns")
        print(f" Binned columns: {list(bin_config.keys())}")
        return df

    def _add_log_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Add log-transformed features."""
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()[:3]

        for col in columns:
            if col in df.columns and (df[col] > 0).all():
                df[f'{col}_log'] = np.log1p(df[col])

        self.operations_log.append(f"Log-transformed {len(columns)} columns")
        print(f" Log-transformed: {columns}")
        return df

    def _add_date_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Extract features from datetime columns."""
        for col in columns:
            if col in df.columns:
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_dayofweek'] = df[col].dt.dayofweek
                df[f'{col}_is_weekend'] = (df[col].dt.dayofweek >= 5).astype(int)

        self.operations_log.append(f"Extracted date features from {len(columns)} columns")
        print(f" Extracted date features from: {columns}")
        return df

    def scale_features(self, df: pd.DataFrame, method: str = 'standard') -> Tuple[pd.DataFrame, Dict]:
        """
        Scale numeric features.

        Args:
            df: DataFrame to scale
            method: 'standard' (z-score) or 'minmax'

        Returns:
            Tuple of (scaled DataFrame, scaling parameters)
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        params = {}

        df_scaled = df.copy()

        for col in numeric_cols:
            if method == 'standard':
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    df_scaled[col] = (df[col] - mean) / std
                params[col] = {'mean': mean, 'std': std}
            elif method == 'minmax':
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df_scaled[col] = (df[col] - min_val) / (max_val - min_val)
                params[col] = {'min': min_val, 'max': max_val}

        print(f" Scaled {len(numeric_cols)} columns using {method} scaling")
        return df_scaled, params


class DataVisualizer:
    """
    Generate visualizations for data analysis.

    Creates publication-quality plots for EDA.
    """

    def __init__(self, output_dir: Path = PLOTS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        sns.set_theme(style='whitegrid')

    def generate_eda_report(self, df: pd.DataFrame, target_col: Optional[str] = None) -> List[str]:
        """
        Generate comprehensive EDA visualizations.

        Args:
            df: DataFrame to visualize
            target_col: Target column for supervised learning

        Returns:
            List of generated plot paths
        """
        print(f"\n{'='*60}")
        print(f"Generating EDA Visualizations")
        print(f"{'='*60}")

        plots_generated = []

        # 1. Distribution plots for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:6]
        if len(numeric_cols) > 0:
            path = self._plot_distributions(df, numeric_cols.tolist())
            plots_generated.append(path)

        # 2. Correlation heatmap
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            path = self._plot_correlation(numeric_df)
            plots_generated.append(path)

        # 3. Target distribution (if provided)
        if target_col and target_col in df.columns:
            path = self._plot_target(df, target_col)
            plots_generated.append(path)

        # 4. Categorical distributions
        cat_cols = df.select_dtypes(include=['object', 'category']).columns[:4]
        if len(cat_cols) > 0:
            path = self._plot_categorical(df, cat_cols.tolist())
            plots_generated.append(path)

        # 5. Missing data visualization
        if df.isna().any().any():
            path = self._plot_missing(df)
            plots_generated.append(path)

        print(f"\n Generated {len(plots_generated)} plots")
        print(f" Saved to: {self.output_dir}")

        return plots_generated

    def _plot_distributions(self, df: pd.DataFrame, columns: List[str]) -> str:
        """Plot distributions of numeric columns."""
        n_cols = min(len(columns), 6)
        n_rows = (n_cols + 2) // 3

        fig, axes = plt.subplots(n_rows, 3, figsize=(15, 4 * n_rows))
        axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes

        for idx, col in enumerate(columns[:6]):
            ax = axes[idx]
            sns.histplot(df[col].dropna(), kde=True, ax=ax, color='steelblue')
            ax.set_title(f'{col}', fontsize=12)
            ax.set_xlabel('')

        # Hide empty subplots
        for idx in range(len(columns), len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle('Feature Distributions', fontsize=14, fontweight='bold')
        plt.tight_layout()

        path = self.output_dir / 'distributions.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   {path.name}")
        return str(path)

    def _plot_correlation(self, df: pd.DataFrame) -> str:
        """Plot correlation heatmap."""
        corr = df.corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                    center=0, square=True, linewidths=0.5, ax=ax,
                    cbar_kws={'shrink': 0.8})
        ax.set_title('Feature Correlations', fontsize=14, fontweight='bold')

        plt.tight_layout()
        path = self.output_dir / 'correlation.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   {path.name}")
        return str(path)

    def _plot_target(self, df: pd.DataFrame, target_col: str) -> str:
        """Plot target variable distribution."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Distribution
        if df[target_col].nunique() < 10:
            # Categorical target
            df[target_col].value_counts().plot(kind='bar', ax=axes[0], color='steelblue')
            axes[0].set_title('Target Distribution (Count)')

            df[target_col].value_counts().plot(kind='pie', ax=axes[1], autopct='%1.1f%%')
            axes[1].set_title('Target Distribution (%)')
        else:
            # Continuous target
            sns.histplot(df[target_col], kde=True, ax=axes[0], color='steelblue')
            axes[0].set_title('Target Distribution')

            sns.boxplot(y=df[target_col], ax=axes[1], color='steelblue')
            axes[1].set_title('Target Box Plot')

        plt.suptitle(f'Target Variable: {target_col}', fontsize=14, fontweight='bold')
        plt.tight_layout()

        path = self.output_dir / 'target_distribution.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   {path.name}")
        return str(path)

    def _plot_categorical(self, df: pd.DataFrame, columns: List[str]) -> str:
        """Plot categorical column distributions."""
        n_cols = len(columns)
        fig, axes = plt.subplots(1, n_cols, figsize=(4 * n_cols, 4))
        axes = [axes] if n_cols == 1 else axes

        for idx, col in enumerate(columns):
            df[col].value_counts().head(10).plot(kind='barh', ax=axes[idx], color='steelblue')
            axes[idx].set_title(f'{col}', fontsize=12)
            axes[idx].set_xlabel('Count')

        plt.suptitle('Categorical Feature Distributions', fontsize=14, fontweight='bold')
        plt.tight_layout()

        path = self.output_dir / 'categorical.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   {path.name}")
        return str(path)

    def _plot_missing(self, df: pd.DataFrame) -> str:
        """Plot missing data pattern."""
        missing = df.isna().sum()
        missing = missing[missing > 0].sort_values(ascending=True)

        if len(missing) == 0:
            return ""

        fig, ax = plt.subplots(figsize=(10, max(4, len(missing) * 0.3)))
        missing.plot(kind='barh', ax=ax, color='coral')
        ax.set_xlabel('Missing Count')
        ax.set_title('Missing Data by Column', fontsize=14, fontweight='bold')

        plt.tight_layout()
        path = self.output_dir / 'missing_data.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   {path.name}")
        return str(path)


class NumpyBenchmarker:
    """
    Benchmark NumPy vs pure Python performance.

    Demonstrates the power of vectorization.
    """

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_benchmarks(self, sizes: Optional[List[int]] = None) -> List[BenchmarkResult]:
        """
        Run comprehensive benchmarks.

        Args:
            sizes: List of array sizes to test

        Returns:
            List of benchmark results
        """
        sizes = sizes or [1000, 10000, 100000, 1000000]
        self.results = []

        print(f"\n{'='*60}")
        print(f"NumPy Performance Benchmarks")
        print(f"{'='*60}")

        # 1. Vector addition
        print(f"\n Vector Addition:")
        print(f"{'Size':<12} {'Python (ms)':<15} {'NumPy (ms)':<15} {'Speedup':<10}")
        print(f"{'-'*52}")

        for size in sizes:
            result = self._benchmark_vector_add(size)
            self.results.append(result)
            print(f"{size:<12,} {result.python_time_ms:<15.3f} {result.numpy_time_ms:<15.3f} {result.speedup:<10.1f}x")

        # 2. Dot product
        print(f"\n Dot Product:")
        print(f"{'Size':<12} {'Python (ms)':<15} {'NumPy (ms)':<15} {'Speedup':<10}")
        print(f"{'-'*52}")

        for size in sizes:
            result = self._benchmark_dot_product(size)
            self.results.append(result)
            print(f"{size:<12,} {result.python_time_ms:<15.3f} {result.numpy_time_ms:<15.3f} {result.speedup:<10.1f}x")

        # 3. Matrix multiplication
        print(f"\n Matrix Multiplication:")
        print(f"{'Size':<12} {'Python (ms)':<15} {'NumPy (ms)':<15} {'Speedup':<10}")
        print(f"{'-'*52}")

        matrix_sizes = [50, 100, 200, 500]
        for size in matrix_sizes:
            result = self._benchmark_matmul(size)
            self.results.append(result)

            py_str = f"{result.python_time_ms:.3f}" if result.python_time_ms < 60000 else "too slow"
            print(f"{size}x{size:<8} {py_str:<15} {result.numpy_time_ms:<15.3f} {result.speedup:<10.1f}x")

        # 4. Statistical operations
        print(f"\n Statistical Operations (size=1,000,000):")
        result = self._benchmark_statistics(1000000)
        self.results.append(result)
        print(f"   Python: {result.python_time_ms:.3f}ms")
        print(f"   NumPy:  {result.numpy_time_ms:.3f}ms")
        print(f"   Speedup: {result.speedup:.1f}x")

        return self.results

    def _time_function(self, func: Callable, n_runs: int = 5) -> float:
        """Time a function execution."""
        times = []
        for _ in range(n_runs):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append((end - start) * 1000)
        return np.mean(times)

    def _benchmark_vector_add(self, size: int) -> BenchmarkResult:
        """Benchmark vector addition."""
        # Python
        py_a = list(range(size))
        py_b = list(range(size))
        py_time = self._time_function(lambda: [a + b for a, b in zip(py_a, py_b)])

        # NumPy
        np_a = np.arange(size)
        np_b = np.arange(size)
        np_time = self._time_function(lambda: np_a + np_b)

        return BenchmarkResult(
            operation="vector_add",
            python_time_ms=py_time,
            numpy_time_ms=np_time,
            speedup=py_time / np_time if np_time > 0 else float('inf'),
            size=size
        )

    def _benchmark_dot_product(self, size: int) -> BenchmarkResult:
        """Benchmark dot product."""
        # Python
        py_a = list(range(size))
        py_b = list(range(size))
        py_time = self._time_function(lambda: sum(a * b for a, b in zip(py_a, py_b)))

        # NumPy
        np_a = np.arange(size, dtype=np.float64)
        np_b = np.arange(size, dtype=np.float64)
        np_time = self._time_function(lambda: np.dot(np_a, np_b))

        return BenchmarkResult(
            operation="dot_product",
            python_time_ms=py_time,
            numpy_time_ms=np_time,
            speedup=py_time / np_time if np_time > 0 else float('inf'),
            size=size
        )

    def _benchmark_matmul(self, size: int) -> BenchmarkResult:
        """Benchmark matrix multiplication."""
        # Python (only for small sizes)
        if size <= 200:
            py_a = [[float(i + j) for j in range(size)] for i in range(size)]
            py_b = [[float(i * j) for j in range(size)] for i in range(size)]

            def py_matmul():
                result = [[0.0 for _ in range(size)] for _ in range(size)]
                for i in range(size):
                    for j in range(size):
                        for k in range(size):
                            result[i][j] += py_a[i][k] * py_b[k][j]
                return result

            py_time = self._time_function(py_matmul, n_runs=1)
        else:
            py_time = float('inf')

        # NumPy
        np_a = np.random.randn(size, size)
        np_b = np.random.randn(size, size)
        np_time = self._time_function(lambda: np_a @ np_b)

        speedup = py_time / np_time if np_time > 0 and py_time < float('inf') else 1000

        return BenchmarkResult(
            operation="matmul",
            python_time_ms=py_time,
            numpy_time_ms=np_time,
            speedup=speedup,
            size=size
        )

    def _benchmark_statistics(self, size: int) -> BenchmarkResult:
        """Benchmark statistical operations."""
        # Python
        py_data = [float(x) for x in range(size)]

        def py_stats():
            mean = sum(py_data) / len(py_data)
            variance = sum((x - mean) ** 2 for x in py_data) / len(py_data)
            return mean, variance ** 0.5

        py_time = self._time_function(py_stats)

        # NumPy
        np_data = np.arange(size, dtype=np.float64)
        np_time = self._time_function(lambda: (np_data.mean(), np_data.std()))

        return BenchmarkResult(
            operation="statistics",
            python_time_ms=py_time,
            numpy_time_ms=np_time,
            speedup=py_time / np_time if np_time > 0 else float('inf'),
            size=size
        )


# =============================================================================
# Demo Functions
# =============================================================================

def create_sample_dataset(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Create a sample dataset for demonstrations."""
    np.random.seed(seed)

    df = pd.DataFrame({
        'age': np.random.normal(35, 10, n).clip(18, 70).astype(int),
        'income': np.random.lognormal(10.5, 0.5, n),
        'credit_score': np.random.normal(650, 100, n).clip(300, 850).astype(int),
        'num_accounts': np.random.poisson(3, n),
        'tenure_months': np.random.exponential(30, n).clip(1, 120).astype(int),
        'employment_type': np.random.choice(['Full-time', 'Part-time', 'Self-employed', 'Unemployed'], n),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n, p=[0.4, 0.35, 0.2, 0.05]),
        'is_active': np.random.choice([0, 1], n, p=[0.2, 0.8]),
    })

    # Add target with some correlation to features
    churn_prob = 0.1 + 0.15 * (df['age'] < 25) + 0.1 * (df['credit_score'] < 600) + 0.05 * (df['tenure_months'] < 12)
    df['churned'] = (np.random.rand(n) < churn_prob).astype(int)

    # Add some missing values
    df.loc[np.random.choice(df.index, int(n * 0.05)), 'income'] = np.nan
    df.loc[np.random.choice(df.index, int(n * 0.03)), 'credit_score'] = np.nan

    return df


def demo_1_data_profiling():
    """Demo 1: Data profiling and exploration."""
    print("\n" + "="*70)
    print(" DEMO 1: DATA PROFILING")
    print("="*70)

    # Create sample data
    df = create_sample_dataset(1000)

    # Profile it
    profiler = DataProfiler()
    profile = profiler.profile(df, "customer_churn")

    # Print detailed report
    profiler.print_report(profile)

    print("\n" + "="*70)
    print(" PROFILING COMPLETE")
    print("="*70)


def demo_2_feature_engineering():
    """Demo 2: Feature engineering."""
    print("\n" + "="*70)
    print(" DEMO 2: FEATURE ENGINEERING")
    print("="*70)

    # Create sample data
    df = create_sample_dataset(500)

    # Clean it first
    cleaner = DataCleaner()
    df_clean = cleaner.clean(df, {
        'missing_strategy': 'smart',
        'remove_duplicates': True,
        'optimize_types': True
    })

    # Engineer features
    engineer = FeatureEngineer()
    df_eng, result = engineer.engineer_features(df_clean, {
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

    print(f"\n Final dataset shape: {df_scaled.shape}")
    print(f" Sample columns: {list(df_scaled.columns)[:10]}...")

    print("\n" + "="*70)
    print(" FEATURE ENGINEERING COMPLETE")
    print("="*70)


def demo_3_visualization():
    """Demo 3: Data visualization."""
    print("\n" + "="*70)
    print(" DEMO 3: DATA VISUALIZATION")
    print("="*70)

    # Create sample data
    df = create_sample_dataset(500)

    # Generate visualizations
    visualizer = DataVisualizer()
    plots = visualizer.generate_eda_report(df, target_col='churned')

    print(f"\n Generated plots:")
    for plot in plots:
        print(f"   {plot}")

    print("\n" + "="*70)
    print(" VISUALIZATION COMPLETE")
    print("="*70)


def demo_4_numpy_benchmarks():
    """Demo 4: NumPy performance benchmarks."""
    print("\n" + "="*70)
    print(" DEMO 4: NUMPY PERFORMANCE BENCHMARKS")
    print("="*70)

    benchmarker = NumpyBenchmarker()
    results = benchmarker.run_benchmarks()

    # Summary
    print(f"\n SUMMARY")
    print(f"{'─'*52}")

    total_py = sum(r.python_time_ms for r in results if r.python_time_ms < float('inf'))
    total_np = sum(r.numpy_time_ms for r in results)

    print(f" Total Python time: {total_py:.1f}ms")
    print(f" Total NumPy time: {total_np:.1f}ms")
    print(f" Average speedup: {total_py/total_np:.1f}x")

    print("\n Key Takeaway: NumPy is 10-1000x faster than pure Python!")
    print(" Always vectorize your operations for ML workloads.")

    print("\n" + "="*70)
    print(" BENCHMARKS COMPLETE")
    print("="*70)


def demo_5_full_pipeline():
    """Demo 5: Complete ML data pipeline."""
    print("\n" + "="*70)
    print(" DEMO 5: COMPLETE ML DATA PIPELINE")
    print("="*70)

    # Create sample data
    print("\n Step 1: Create raw dataset")
    df = create_sample_dataset(1000)
    print(f" Raw data shape: {df.shape}")
    print(f" Missing values: {df.isna().sum().sum()}")

    # Profile
    print("\n Step 2: Profile data")
    profiler = DataProfiler()
    profile = profiler.profile(df, "pipeline_demo")

    # Clean
    print("\n Step 3: Clean data")
    cleaner = DataCleaner()
    df_clean = cleaner.clean(df, {
        'missing_strategy': 'smart',
        'remove_duplicates': True,
        'handle_outliers': True,
        'outlier_method': 'clip',
        'outlier_threshold': 3.0,
        'optimize_types': True
    })

    # Engineer features
    print("\n Step 4: Engineer features")
    engineer = FeatureEngineer()
    df_eng, fe_result = engineer.engineer_features(df_clean, {
        'polynomial': True,
        'polynomial_columns': ['age', 'credit_score'],
        'polynomial_degree': 2,
        'log_transform': True,
        'log_columns': ['income'],
        'one_hot': True
    })

    # Scale
    print("\n Step 5: Scale features")
    target_col = 'churned'
    X = df_eng.drop(columns=[target_col])
    y = df_eng[target_col]

    X_scaled, scale_params = engineer.scale_features(X, method='standard')

    # Split
    print("\n Step 6: Train/test split")
    train_size = int(0.8 * len(X_scaled))
    X_train, X_test = X_scaled.iloc[:train_size], X_scaled.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    print(f" Training set: {X_train.shape}")
    print(f" Test set: {X_test.shape}")
    print(f" Target distribution (train): {y_train.value_counts().to_dict()}")

    # Visualize
    print("\n Step 7: Generate visualizations")
    visualizer = DataVisualizer()
    plots = visualizer.generate_eda_report(df_clean, target_col=target_col)

    # Pipeline summary
    print(f"\n{'='*60}")
    print(f" PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f" Original shape: {df.shape}")
    print(f" Final shape: {X_scaled.shape}")
    print(f" Features created: {fe_result.new_features}")
    print(f" Cleaning steps: {len(cleaner.cleaning_log)}")
    print(f" Plots generated: {len(plots)}")
    print(f" Data ready for ML training!")

    print("\n" + "="*70)
    print(" PIPELINE COMPLETE")
    print("="*70)


def show_help():
    """Show help information."""
    print("""
ML Data Toolkit - Module 25 Deliverable
========================================

A comprehensive toolkit for machine learning data preparation.

Usage:
    python deliverable_ml_data_toolkit.py <command>

Commands:
    demo1    - Data profiling and exploration
    demo2    - Feature engineering pipeline
    demo3    - Data visualization generation
    demo4    - NumPy performance benchmarks
    demo5    - Complete ML data pipeline
    help     - Show this help message

Examples:
    python deliverable_ml_data_toolkit.py demo1
    python deliverable_ml_data_toolkit.py demo4
    python deliverable_ml_data_toolkit.py demo5

Features:
    - DataProfiler: Analyze dataset structure and quality
    - DataCleaner: Handle missing values, outliers, duplicates
    - FeatureEngineer: Create and transform features
    - DataVisualizer: Generate EDA visualizations
    - NumpyBenchmarker: Compare NumPy vs Python performance

Output:
    - Profiles saved to: .ml_data_toolkit/data_profiles.json
    - Plots saved to: .ml_data_toolkit/plots/

Dependencies:
    - numpy
    - pandas
    - matplotlib
    - seaborn
    """)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_data_profiling()
    elif command == "demo2":
        demo_2_feature_engineering()
    elif command == "demo3":
        demo_3_visualization()
    elif command == "demo4":
        demo_4_numpy_benchmarks()
    elif command == "demo5":
        demo_5_full_pipeline()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands.")
        sys.exit(1)
