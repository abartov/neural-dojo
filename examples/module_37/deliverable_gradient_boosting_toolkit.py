#!/usr/bin/env python3
"""
Gradient Boosting Toolkit - Module 37 Deliverable

A hands-on toolkit for understanding gradient boosting:
- Decision trees from scratch
- Gradient boosting from scratch
- Comparison with XGBoost/LightGBM/CatBoost (if available)
- Hyperparameter tuning demonstration
- Feature importance analysis

Author: Neural Dojo
Date: 2025-11-27
"""

import json
import math
import os
import sys
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from collections import Counter


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TreeNode:
    """A node in a decision tree."""
    feature_index: Optional[int] = None
    threshold: Optional[float] = None
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None
    value: Optional[float] = None
    is_leaf: bool = False
    n_samples: int = 0
    impurity: float = 0.0


@dataclass
class DecisionTree:
    """A simple decision tree for regression."""
    root: Optional[TreeNode] = None
    max_depth: int = 5
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    n_features: int = 0


@dataclass
class GradientBoostingModel:
    """Gradient boosting ensemble."""
    trees: List[DecisionTree] = field(default_factory=list)
    learning_rate: float = 0.1
    n_estimators: int = 100
    initial_prediction: float = 0.0
    train_losses: List[float] = field(default_factory=list)


@dataclass
class ModelComparison:
    """Results from comparing different models."""
    model_name: str
    train_time: float
    predict_time: float
    mse: float
    r2: float
    n_samples: int
    n_features: int


@dataclass
class FeatureImportance:
    """Feature importance results."""
    feature_index: int
    feature_name: str
    importance: float
    rank: int


# =============================================================================
# STORAGE
# =============================================================================

STORAGE_DIR = Path(".gb_toolkit")


def ensure_storage():
    """Create storage directory if needed."""
    STORAGE_DIR.mkdir(exist_ok=True)
    (STORAGE_DIR / "models").mkdir(exist_ok=True)
    (STORAGE_DIR / "results").mkdir(exist_ok=True)
    (STORAGE_DIR / "comparisons").mkdir(exist_ok=True)


def save_json(data: dict, category: str, name: str):
    """Save data to JSON file."""
    ensure_storage()
    path = STORAGE_DIR / category / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def load_json(category: str, name: str) -> Optional[dict]:
    """Load data from JSON file."""
    path = STORAGE_DIR / category / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# =============================================================================
# SYNTHETIC DATA GENERATION
# =============================================================================

def generate_regression_data(
    n_samples: int = 1000,
    n_features: int = 10,
    noise: float = 0.1,
    seed: int = 42
) -> Tuple[List[List[float]], List[float], List[str]]:
    """
    Generate synthetic regression data.

    Creates data with:
    - Linear relationships
    - Non-linear relationships
    - Interactions
    - Noise
    """
    random.seed(seed)

    feature_names = [f"feature_{i}" for i in range(n_features)]
    X = []
    y = []

    for _ in range(n_samples):
        # Generate features
        features = [random.gauss(0, 1) for _ in range(n_features)]

        # Target: combination of linear and non-linear terms
        target = 0.0

        # Linear terms (first 3 features)
        target += 2.0 * features[0]
        target += -1.5 * features[1]
        target += 0.5 * features[2]

        # Non-linear terms
        if n_features > 3:
            target += features[3] ** 2  # Quadratic
        if n_features > 4:
            target += math.sin(features[4] * 2)  # Periodic
        if n_features > 5:
            target += max(0, features[5])  # ReLU-like

        # Interaction
        if n_features > 1:
            target += 0.5 * features[0] * features[1]

        # Add noise
        target += random.gauss(0, noise)

        X.append(features)
        y.append(target)

    return X, y, feature_names


def generate_classification_data(
    n_samples: int = 1000,
    n_features: int = 10,
    seed: int = 42
) -> Tuple[List[List[float]], List[int], List[str]]:
    """Generate synthetic binary classification data."""
    random.seed(seed)

    feature_names = [f"feature_{i}" for i in range(n_features)]
    X = []
    y = []

    for _ in range(n_samples):
        features = [random.gauss(0, 1) for _ in range(n_features)]

        # Decision boundary
        score = features[0] + 0.5 * features[1] - features[2]
        if n_features > 3:
            score += 0.3 * features[3] ** 2

        # Add noise via sigmoid
        prob = 1 / (1 + math.exp(-score))
        label = 1 if random.random() < prob else 0

        X.append(features)
        y.append(label)

    return X, y, feature_names


def train_test_split(
    X: List[List[float]],
    y: List[float],
    test_size: float = 0.2,
    seed: int = 42
) -> Tuple[List[List[float]], List[List[float]], List[float], List[float]]:
    """Split data into train and test sets."""
    random.seed(seed)

    n = len(X)
    indices = list(range(n))
    random.shuffle(indices)

    split_idx = int(n * (1 - test_size))

    train_idx = indices[:split_idx]
    test_idx = indices[split_idx:]

    X_train = [X[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_train = [y[i] for i in train_idx]
    y_test = [y[i] for i in test_idx]

    return X_train, X_test, y_train, y_test


# =============================================================================
# DECISION TREE IMPLEMENTATION
# =============================================================================

def calculate_mse(y: List[float]) -> float:
    """Calculate mean squared error from mean."""
    if len(y) == 0:
        return 0.0
    mean = sum(y) / len(y)
    return sum((yi - mean) ** 2 for yi in y) / len(y)


def calculate_variance_reduction(
    y_parent: List[float],
    y_left: List[float],
    y_right: List[float]
) -> float:
    """Calculate variance reduction from a split."""
    if len(y_left) == 0 or len(y_right) == 0:
        return 0.0

    n = len(y_parent)
    n_left = len(y_left)
    n_right = len(y_right)

    var_parent = calculate_mse(y_parent)
    var_left = calculate_mse(y_left)
    var_right = calculate_mse(y_right)

    weighted_var = (n_left / n) * var_left + (n_right / n) * var_right

    return var_parent - weighted_var


def find_best_split(
    X: List[List[float]],
    y: List[float],
    feature_indices: List[int]
) -> Tuple[Optional[int], Optional[float], float]:
    """
    Find the best split for a node.

    Returns:
        (best_feature, best_threshold, best_variance_reduction)
    """
    best_feature = None
    best_threshold = None
    best_reduction = 0.0

    for feature_idx in feature_indices:
        # Get unique values for this feature
        values = sorted(set(row[feature_idx] for row in X))

        # Try splitting at each midpoint
        for i in range(len(values) - 1):
            threshold = (values[i] + values[i + 1]) / 2

            # Split data
            y_left = [y[j] for j, row in enumerate(X) if row[feature_idx] <= threshold]
            y_right = [y[j] for j, row in enumerate(X) if row[feature_idx] > threshold]

            # Calculate variance reduction
            reduction = calculate_variance_reduction(y, y_left, y_right)

            if reduction > best_reduction:
                best_reduction = reduction
                best_feature = feature_idx
                best_threshold = threshold

    return best_feature, best_threshold, best_reduction


def build_tree(
    X: List[List[float]],
    y: List[float],
    max_depth: int,
    min_samples_split: int,
    min_samples_leaf: int,
    depth: int = 0,
    feature_subset_ratio: float = 1.0
) -> TreeNode:
    """
    Recursively build a decision tree.

    Args:
        X: Feature matrix
        y: Target values
        max_depth: Maximum tree depth
        min_samples_split: Minimum samples to split
        min_samples_leaf: Minimum samples in leaf
        depth: Current depth
        feature_subset_ratio: Fraction of features to consider at each split
    """
    node = TreeNode(n_samples=len(y), impurity=calculate_mse(y))

    # Stopping conditions
    if (depth >= max_depth or
        len(y) < min_samples_split or
        len(set(y)) == 1):
        node.is_leaf = True
        node.value = sum(y) / len(y) if y else 0.0
        return node

    # Select feature subset (for randomness like Random Forest)
    n_features = len(X[0]) if X else 0
    n_select = max(1, int(n_features * feature_subset_ratio))
    feature_indices = random.sample(range(n_features), n_select)

    # Find best split
    best_feature, best_threshold, best_reduction = find_best_split(
        X, y, feature_indices
    )

    # No good split found
    if best_feature is None or best_reduction <= 0:
        node.is_leaf = True
        node.value = sum(y) / len(y) if y else 0.0
        return node

    # Split data
    left_indices = [i for i, row in enumerate(X) if row[best_feature] <= best_threshold]
    right_indices = [i for i, row in enumerate(X) if row[best_feature] > best_threshold]

    # Check minimum leaf samples
    if len(left_indices) < min_samples_leaf or len(right_indices) < min_samples_leaf:
        node.is_leaf = True
        node.value = sum(y) / len(y) if y else 0.0
        return node

    # Create split
    node.feature_index = best_feature
    node.threshold = best_threshold

    X_left = [X[i] for i in left_indices]
    y_left = [y[i] for i in left_indices]
    X_right = [X[i] for i in right_indices]
    y_right = [y[i] for i in right_indices]

    node.left = build_tree(
        X_left, y_left, max_depth, min_samples_split,
        min_samples_leaf, depth + 1, feature_subset_ratio
    )
    node.right = build_tree(
        X_right, y_right, max_depth, min_samples_split,
        min_samples_leaf, depth + 1, feature_subset_ratio
    )

    return node


def predict_single(node: TreeNode, x: List[float]) -> float:
    """Predict for a single sample."""
    if node.is_leaf:
        return node.value

    if x[node.feature_index] <= node.threshold:
        return predict_single(node.left, x)
    else:
        return predict_single(node.right, x)


def predict_tree(tree: DecisionTree, X: List[List[float]]) -> List[float]:
    """Predict for multiple samples."""
    return [predict_single(tree.root, x) for x in X]


def fit_decision_tree(
    X: List[List[float]],
    y: List[float],
    max_depth: int = 5,
    min_samples_split: int = 2,
    min_samples_leaf: int = 1
) -> DecisionTree:
    """Fit a decision tree to data."""
    tree = DecisionTree(
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        n_features=len(X[0]) if X else 0
    )

    tree.root = build_tree(
        X, y, max_depth, min_samples_split, min_samples_leaf
    )

    return tree


# =============================================================================
# GRADIENT BOOSTING IMPLEMENTATION
# =============================================================================

def fit_gradient_boosting(
    X: List[List[float]],
    y: List[float],
    n_estimators: int = 100,
    learning_rate: float = 0.1,
    max_depth: int = 3,
    min_samples_split: int = 2,
    subsample: float = 1.0,
    verbose: bool = False
) -> GradientBoostingModel:
    """
    Fit a gradient boosting model from scratch.

    This implements gradient boosting for regression with MSE loss.
    Each tree fits the negative gradient (residuals for MSE).
    """
    model = GradientBoostingModel(
        learning_rate=learning_rate,
        n_estimators=n_estimators
    )

    # Initial prediction: mean of targets
    model.initial_prediction = sum(y) / len(y)

    # Current predictions
    predictions = [model.initial_prediction] * len(y)

    for i in range(n_estimators):
        # Calculate residuals (negative gradient for MSE)
        residuals = [y[j] - predictions[j] for j in range(len(y))]

        # Subsample if requested
        if subsample < 1.0:
            n_subsample = max(1, int(len(X) * subsample))
            indices = random.sample(range(len(X)), n_subsample)
            X_sample = [X[j] for j in indices]
            residuals_sample = [residuals[j] for j in indices]
        else:
            X_sample = X
            residuals_sample = residuals

        # Fit tree to residuals
        tree = fit_decision_tree(
            X_sample,
            residuals_sample,
            max_depth=max_depth,
            min_samples_split=min_samples_split
        )
        model.trees.append(tree)

        # Update predictions
        tree_preds = predict_tree(tree, X)
        predictions = [
            predictions[j] + learning_rate * tree_preds[j]
            for j in range(len(predictions))
        ]

        # Calculate and store training loss
        mse = sum((y[j] - predictions[j]) ** 2 for j in range(len(y))) / len(y)
        model.train_losses.append(mse)

        if verbose and (i + 1) % 10 == 0:
            print(f"  Iteration {i + 1}/{n_estimators}, MSE: {mse:.4f}")

    return model


def predict_gradient_boosting(
    model: GradientBoostingModel,
    X: List[List[float]]
) -> List[float]:
    """Make predictions with gradient boosting model."""
    predictions = [model.initial_prediction] * len(X)

    for tree in model.trees:
        tree_preds = predict_tree(tree, X)
        predictions = [
            predictions[j] + model.learning_rate * tree_preds[j]
            for j in range(len(predictions))
        ]

    return predictions


# =============================================================================
# METRICS
# =============================================================================

def mean_squared_error(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate MSE."""
    return sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)) / len(y_true)


def r2_score(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate R-squared."""
    mean_y = sum(y_true) / len(y_true)
    ss_tot = sum((yt - mean_y) ** 2 for yt in y_true)
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred))

    if ss_tot == 0:
        return 0.0

    return 1 - (ss_res / ss_tot)


def accuracy(y_true: List[int], y_pred: List[int]) -> float:
    """Calculate accuracy for classification."""
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return correct / len(y_true)


# =============================================================================
# FEATURE IMPORTANCE
# =============================================================================

def calculate_feature_importance(
    model: GradientBoostingModel,
    feature_names: List[str]
) -> List[FeatureImportance]:
    """
    Calculate feature importance based on split frequency.

    In production, you'd use:
    - Split-based importance (frequency * improvement)
    - Permutation importance
    - SHAP values
    """
    importance_counts = Counter()

    def count_splits(node: TreeNode):
        if node is None or node.is_leaf:
            return
        importance_counts[node.feature_index] += 1
        count_splits(node.left)
        count_splits(node.right)

    # Count splits across all trees
    for tree in model.trees:
        count_splits(tree.root)

    # Normalize
    total = sum(importance_counts.values()) or 1
    importances = []

    for i, name in enumerate(feature_names):
        imp = importance_counts.get(i, 0) / total
        importances.append(FeatureImportance(
            feature_index=i,
            feature_name=name,
            importance=imp,
            rank=0
        ))

    # Rank by importance
    importances.sort(key=lambda x: x.importance, reverse=True)
    for rank, fi in enumerate(importances, 1):
        fi.rank = rank

    return importances


# =============================================================================
# HYPERPARAMETER TUNING
# =============================================================================

def grid_search_cv(
    X: List[List[float]],
    y: List[float],
    param_grid: Dict[str, List[Any]],
    n_folds: int = 5
) -> Tuple[Dict[str, Any], float]:
    """
    Simple grid search with cross-validation.

    Args:
        X: Feature matrix
        y: Target values
        param_grid: Parameters to search
        n_folds: Number of CV folds

    Returns:
        (best_params, best_score)
    """
    # Generate all parameter combinations
    keys = list(param_grid.keys())
    values = list(param_grid.values())

    def product(*args):
        if not args:
            return [()]
        result = []
        for item in args[0]:
            for rest in product(*args[1:]):
                result.append((item,) + rest)
        return result

    combinations = product(*values)

    best_score = float('inf')
    best_params = None

    print(f"  Testing {len(combinations)} parameter combinations...")

    for combo in combinations:
        params = dict(zip(keys, combo))

        # Cross-validation
        fold_scores = []
        fold_size = len(X) // n_folds

        for fold in range(n_folds):
            # Split data
            val_start = fold * fold_size
            val_end = val_start + fold_size

            X_train = X[:val_start] + X[val_end:]
            y_train = y[:val_start] + y[val_end:]
            X_val = X[val_start:val_end]
            y_val = y[val_start:val_end]

            # Train model
            model = fit_gradient_boosting(
                X_train, y_train,
                n_estimators=params.get('n_estimators', 50),
                learning_rate=params.get('learning_rate', 0.1),
                max_depth=params.get('max_depth', 3),
                verbose=False
            )

            # Evaluate
            preds = predict_gradient_boosting(model, X_val)
            mse = mean_squared_error(y_val, preds)
            fold_scores.append(mse)

        avg_score = sum(fold_scores) / len(fold_scores)

        if avg_score < best_score:
            best_score = avg_score
            best_params = params

    return best_params, best_score


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_decision_tree():
    """
    Demo 1: Decision Tree from Scratch

    Build and visualize a decision tree.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: Decision Tree from Scratch")
    print("=" * 70)

    # Generate data
    print("\n📊 Generating synthetic regression data...")
    X, y, feature_names = generate_regression_data(
        n_samples=500,
        n_features=5,
        noise=0.5
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    print(f"   Features: {len(feature_names)}")

    # Train decision tree
    print("\n🌳 Training decision tree...")
    start = time.time()
    tree = fit_decision_tree(
        X_train, y_train,
        max_depth=5,
        min_samples_split=10
    )
    train_time = time.time() - start

    # Evaluate
    print("\n📈 Evaluating model...")
    train_preds = predict_tree(tree, X_train)
    test_preds = predict_tree(tree, X_test)

    train_mse = mean_squared_error(y_train, train_preds)
    test_mse = mean_squared_error(y_test, test_preds)
    train_r2 = r2_score(y_train, train_preds)
    test_r2 = r2_score(y_test, test_preds)

    print(f"\n📊 Results:")
    print(f"   Training MSE: {train_mse:.4f}")
    print(f"   Test MSE:     {test_mse:.4f}")
    print(f"   Training R²:  {train_r2:.4f}")
    print(f"   Test R²:      {test_r2:.4f}")
    print(f"   Training time: {train_time:.3f}s")

    # Visualize tree structure
    print("\n🌲 Tree Structure (first 3 levels):")

    def print_tree(node, depth=0, prefix="Root"):
        if node is None or depth > 2:
            return
        indent = "  " * depth
        if node.is_leaf:
            print(f"{indent}{prefix}: Leaf(value={node.value:.2f}, n={node.n_samples})")
        else:
            print(f"{indent}{prefix}: Split on {feature_names[node.feature_index]} <= {node.threshold:.2f} (n={node.n_samples})")
            print_tree(node.left, depth + 1, "Left")
            print_tree(node.right, depth + 1, "Right")

    print_tree(tree.root)

    print("\n💡 Key Insight: Single decision trees are interpretable but prone to overfitting!")
    print("   Notice the gap between training and test performance.")


def demo_2_gradient_boosting():
    """
    Demo 2: Gradient Boosting from Scratch

    Build a gradient boosting model step by step.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Gradient Boosting from Scratch")
    print("=" * 70)

    # Generate data
    print("\n📊 Generating synthetic regression data...")
    X, y, feature_names = generate_regression_data(
        n_samples=300,
        n_features=6,
        noise=0.3
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")

    # Train gradient boosting
    print("\n🚀 Training gradient boosting model...")
    print("   Parameters: n_estimators=30, learning_rate=0.1, max_depth=3")

    start = time.time()
    model = fit_gradient_boosting(
        X_train, y_train,
        n_estimators=30,
        learning_rate=0.1,
        max_depth=3,
        verbose=True
    )
    train_time = time.time() - start

    # Evaluate
    print("\n📈 Evaluating model...")
    train_preds = predict_gradient_boosting(model, X_train)
    test_preds = predict_gradient_boosting(model, X_test)

    train_mse = mean_squared_error(y_train, train_preds)
    test_mse = mean_squared_error(y_test, test_preds)
    train_r2 = r2_score(y_train, train_preds)
    test_r2 = r2_score(y_test, test_preds)

    print(f"\n📊 Results:")
    print(f"   Training MSE: {train_mse:.4f}")
    print(f"   Test MSE:     {test_mse:.4f}")
    print(f"   Training R²:  {train_r2:.4f}")
    print(f"   Test R²:      {test_r2:.4f}")
    print(f"   Training time: {train_time:.3f}s")
    print(f"   Number of trees: {len(model.trees)}")

    # Show learning curve
    print("\n📉 Learning Curve (MSE over iterations):")
    checkpoints = [0, 4, 9, 14, 19, 29]
    for i in checkpoints:
        if i < len(model.train_losses):
            bar_len = int((1 - model.train_losses[i] / model.train_losses[0]) * 30)
            bar = "█" * max(0, bar_len) + "░" * (30 - max(0, bar_len))
            print(f"   Iter {i+1:3d}: [{bar}] MSE={model.train_losses[i]:.4f}")

    # Feature importance
    print("\n📊 Feature Importance (by split frequency):")
    importances = calculate_feature_importance(model, feature_names)
    for fi in importances[:5]:
        bar_len = int(fi.importance * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"   {fi.rank}. {fi.feature_name:12s} [{bar}] {fi.importance:.3f}")

    print("\n💡 Key Insight: Gradient boosting reduces error iteratively!")
    print("   Each tree corrects the mistakes of previous trees.")


def demo_3_hyperparameter_tuning():
    """
    Demo 3: Hyperparameter Tuning

    Find optimal parameters using grid search.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Hyperparameter Tuning")
    print("=" * 70)

    # Generate data
    print("\n📊 Generating synthetic data...")
    X, y, _ = generate_regression_data(
        n_samples=500,  # Smaller for faster tuning
        n_features=8,
        noise=0.3
    )

    # Define parameter grid (small for demo speed)
    param_grid = {
        'n_estimators': [10, 15],
        'learning_rate': [0.1, 0.2],
        'max_depth': [2, 3]
    }

    print("\n🔧 Parameter Grid:")
    for param, values in param_grid.items():
        print(f"   {param}: {values}")

    # Run grid search
    print("\n🔍 Running grid search with 3-fold CV...")
    start = time.time()
    best_params, best_score = grid_search_cv(
        X, y, param_grid, n_folds=3
    )
    search_time = time.time() - start

    print(f"\n✅ Best Parameters Found:")
    for param, value in best_params.items():
        print(f"   {param}: {value}")
    print(f"   Best CV MSE: {best_score:.4f}")
    print(f"   Search time: {search_time:.1f}s")

    # Train final model with best params
    print("\n🏆 Training final model with best parameters...")
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    final_model = fit_gradient_boosting(
        X_train, y_train,
        **best_params,
        verbose=False
    )

    final_preds = predict_gradient_boosting(final_model, X_test)
    final_mse = mean_squared_error(y_test, final_preds)
    final_r2 = r2_score(y_test, final_preds)

    print(f"\n📊 Final Model Performance:")
    print(f"   Test MSE: {final_mse:.4f}")
    print(f"   Test R²:  {final_r2:.4f}")

    print("\n💡 Key Insight: Hyperparameter tuning can significantly improve performance!")
    print("   In practice, use Optuna or similar for more efficient search.")


def demo_4_compare_implementations():
    """
    Demo 4: Compare with Production Libraries

    Compare our implementation with XGBoost/LightGBM if available.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Compare with Production Libraries")
    print("=" * 70)

    # Generate data
    print("\n📊 Generating synthetic data...")
    X, y, feature_names = generate_regression_data(
        n_samples=400,
        n_features=6,
        noise=0.3
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    results = []

    # Our implementation
    print("\n🏠 Testing our from-scratch implementation...")
    start = time.time()
    our_model = fit_gradient_boosting(
        X_train, y_train,
        n_estimators=20,
        learning_rate=0.1,
        max_depth=3,
        verbose=False
    )
    our_train_time = time.time() - start

    start = time.time()
    our_preds = predict_gradient_boosting(our_model, X_test)
    our_pred_time = time.time() - start

    our_mse = mean_squared_error(y_test, our_preds)
    our_r2 = r2_score(y_test, our_preds)

    results.append(ModelComparison(
        model_name="From Scratch",
        train_time=our_train_time,
        predict_time=our_pred_time,
        mse=our_mse,
        r2=our_r2,
        n_samples=len(X_train),
        n_features=len(feature_names)
    ))

    # Try sklearn
    try:
        from sklearn.ensemble import GradientBoostingRegressor

        print("🔧 Testing scikit-learn GradientBoostingRegressor...")
        sklearn_model = GradientBoostingRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=3
        )

        start = time.time()
        sklearn_model.fit(X_train, y_train)
        sklearn_train_time = time.time() - start

        start = time.time()
        sklearn_preds = sklearn_model.predict(X_test)
        sklearn_pred_time = time.time() - start

        sklearn_mse = mean_squared_error(y_test, sklearn_preds.tolist())
        sklearn_r2 = r2_score(y_test, sklearn_preds.tolist())

        results.append(ModelComparison(
            model_name="sklearn",
            train_time=sklearn_train_time,
            predict_time=sklearn_pred_time,
            mse=sklearn_mse,
            r2=sklearn_r2,
            n_samples=len(X_train),
            n_features=len(feature_names)
        ))
    except ImportError:
        print("   ⚠️  scikit-learn not installed")

    # Try XGBoost
    try:
        import xgboost as xgb

        print("⚡ Testing XGBoost...")
        xgb_model = xgb.XGBRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=3,
            verbosity=0
        )

        start = time.time()
        xgb_model.fit(X_train, y_train)
        xgb_train_time = time.time() - start

        start = time.time()
        xgb_preds = xgb_model.predict(X_test)
        xgb_pred_time = time.time() - start

        xgb_mse = mean_squared_error(y_test, xgb_preds.tolist())
        xgb_r2 = r2_score(y_test, xgb_preds.tolist())

        results.append(ModelComparison(
            model_name="XGBoost",
            train_time=xgb_train_time,
            predict_time=xgb_pred_time,
            mse=xgb_mse,
            r2=xgb_r2,
            n_samples=len(X_train),
            n_features=len(feature_names)
        ))
    except ImportError:
        print("   ⚠️  XGBoost not installed (pip install xgboost)")

    # Try LightGBM
    try:
        import lightgbm as lgb

        print("💡 Testing LightGBM...")
        lgb_model = lgb.LGBMRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=3,
            verbose=-1
        )

        start = time.time()
        lgb_model.fit(X_train, y_train)
        lgb_train_time = time.time() - start

        start = time.time()
        lgb_preds = lgb_model.predict(X_test)
        lgb_pred_time = time.time() - start

        lgb_mse = mean_squared_error(y_test, lgb_preds.tolist())
        lgb_r2 = r2_score(y_test, lgb_preds.tolist())

        results.append(ModelComparison(
            model_name="LightGBM",
            train_time=lgb_train_time,
            predict_time=lgb_pred_time,
            mse=lgb_mse,
            r2=lgb_r2,
            n_samples=len(X_train),
            n_features=len(feature_names)
        ))
    except ImportError:
        print("   ⚠️  LightGBM not installed (pip install lightgbm)")

    # Show results
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    print("\n📊 Performance Comparison:")
    print(f"\n{'Model':<15} {'Train Time':>12} {'Pred Time':>12} {'MSE':>10} {'R²':>10}")
    print("-" * 60)

    for r in results:
        print(f"{r.model_name:<15} {r.train_time:>10.4f}s {r.predict_time:>10.4f}s {r.mse:>10.4f} {r.r2:>10.4f}")

    # Save comparison
    save_json(
        [asdict(r) for r in results],
        "comparisons",
        f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    print("\n💡 Key Insight: Production libraries are optimized for speed!")
    print("   Our from-scratch version helps understand the algorithm.")
    print("   Use XGBoost/LightGBM/CatBoost for production workloads.")


def demo_5_full_report():
    """
    Demo 5: Generate Full Analysis Report

    Comprehensive analysis with all components.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Full Analysis Report")
    print("=" * 70)

    # Generate data
    print("\n📊 Generating comprehensive dataset...")
    X, y, feature_names = generate_regression_data(
        n_samples=300,
        n_features=6,
        noise=0.3
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    report = {
        "generated_at": datetime.now().isoformat(),
        "data": {
            "n_samples": len(X),
            "n_features": len(feature_names),
            "train_size": len(X_train),
            "test_size": len(X_test)
        }
    }

    # Compare different configurations
    print("\n🔬 Testing different configurations...")

    configs = [
        {"n_estimators": 10, "max_depth": 2, "learning_rate": 0.1},
        {"n_estimators": 15, "max_depth": 3, "learning_rate": 0.1},
        {"n_estimators": 20, "max_depth": 3, "learning_rate": 0.05},
        {"n_estimators": 15, "max_depth": 4, "learning_rate": 0.1},
    ]

    config_results = []

    for i, config in enumerate(configs, 1):
        print(f"\n   Config {i}: {config}")

        model = fit_gradient_boosting(X_train, y_train, **config, verbose=False)
        preds = predict_gradient_boosting(model, X_test)

        mse = mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        config_results.append({
            "config": config,
            "mse": mse,
            "r2": r2
        })

        print(f"      MSE: {mse:.4f}, R²: {r2:.4f}")

    report["configurations"] = config_results

    # Find best config
    best_config = min(config_results, key=lambda x: x["mse"])
    print(f"\n✅ Best Configuration:")
    print(f"   {best_config['config']}")
    print(f"   MSE: {best_config['mse']:.4f}, R²: {best_config['r2']:.4f}")

    # Train final model
    print("\n🏆 Training final model with best configuration...")
    final_model = fit_gradient_boosting(
        X_train, y_train,
        **best_config["config"],
        verbose=False
    )

    # Feature importance
    importances = calculate_feature_importance(final_model, feature_names)
    report["feature_importance"] = [asdict(fi) for fi in importances]

    print("\n📊 Feature Importance Ranking:")
    for fi in importances[:5]:
        bar_len = int(fi.importance * 40)
        bar = "█" * bar_len
        print(f"   {fi.rank}. {fi.feature_name:<12} {bar} {fi.importance:.3f}")

    # Learning dynamics
    print("\n📉 Learning Dynamics:")
    print(f"   Initial MSE: {final_model.train_losses[0]:.4f}")
    print(f"   Final MSE:   {final_model.train_losses[-1]:.4f}")
    print(f"   Improvement: {(1 - final_model.train_losses[-1]/final_model.train_losses[0])*100:.1f}%")

    # Save report
    report["best_config"] = best_config
    save_json(report, "results", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"""
📋 Analysis Complete!

Key Findings:
1. Dataset: {len(X)} samples, {len(feature_names)} features
2. Best Configuration: {best_config['config']}
3. Test Performance: MSE={best_config['mse']:.4f}, R²={best_config['r2']:.4f}
4. Top Feature: {importances[0].feature_name} (importance={importances[0].importance:.3f})
5. Training reduced MSE by {(1 - final_model.train_losses[-1]/final_model.train_losses[0])*100:.1f}%

Report saved to: .gb_toolkit/results/
    """)

    print("💡 Key Insight: Gradient boosting is highly effective on tabular data!")
    print("   For production, use XGBoost/LightGBM with proper hyperparameter tuning.")


def print_help():
    """Print usage information."""
    print("""
Gradient Boosting Toolkit - Module 37 Deliverable
==================================================

A hands-on toolkit for understanding gradient boosting.

USAGE:
    python deliverable_gradient_boosting_toolkit.py <command>

COMMANDS:
    demo1   - Decision Tree from Scratch
    demo2   - Gradient Boosting from Scratch
    demo3   - Hyperparameter Tuning
    demo4   - Compare with Production Libraries
    demo5   - Full Analysis Report
    all     - Run all demos
    help    - Show this help message

EXAMPLES:
    python deliverable_gradient_boosting_toolkit.py demo1
    python deliverable_gradient_boosting_toolkit.py all

CONCEPTS COVERED:
    1. Decision Trees: Recursive partitioning, information gain
    2. Gradient Boosting: Sequential tree fitting on residuals
    3. Hyperparameters: n_estimators, learning_rate, max_depth
    4. Feature Importance: Split-based importance
    5. Production Libraries: XGBoost, LightGBM comparison

WHY TABULAR ML MATTERS:
    - ~80% of production ML uses tree-based models
    - Works great on structured business data
    - Handles mixed feature types natively
    - Fast training and inference
    - Highly interpretable

DATA STORAGE:
    Results saved to .gb_toolkit/ directory
    """)


def main():
    """Main entry point."""
    ensure_storage()

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_decision_tree()
    elif command == "demo2":
        demo_2_gradient_boosting()
    elif command == "demo3":
        demo_3_hyperparameter_tuning()
    elif command == "demo4":
        demo_4_compare_implementations()
    elif command == "demo5":
        demo_5_full_report()
    elif command == "all":
        demo_1_decision_tree()
        demo_2_gradient_boosting()
        demo_3_hyperparameter_tuning()
        demo_4_compare_implementations()
        demo_5_full_report()
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETE!")
        print("=" * 70)
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
