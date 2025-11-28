#!/usr/bin/env python3
"""
Module 39 Deliverable: AutoML & Feature Store Toolkit

A comprehensive toolkit demonstrating automated machine learning,
feature engineering, and feature store concepts.

Features:
- AutoML-style model selection and hyperparameter tuning
- Automated feature engineering (aggregations, transformations)
- Feature store simulation (registry, versioning, serving)
- ML pipeline orchestration
- Experiment tracking

Usage:
    python deliverable_automl_toolkit.py demo1  # AutoML model selection
    python deliverable_automl_toolkit.py demo2  # Automated feature engineering
    python deliverable_automl_toolkit.py demo3  # Feature store simulation
    python deliverable_automl_toolkit.py demo4  # End-to-end ML pipeline
    python deliverable_automl_toolkit.py demo5  # Full report

Author: Neural Dojo
Module: 39 - AutoML & Feature Stores
"""

import json
import math
import os
import sys
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any, Callable
from collections import defaultdict


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for a model."""
    name: str
    model_type: str
    hyperparameters: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ModelResult:
    """Result of training a model."""
    config: ModelConfig
    train_score: float
    val_score: float
    test_score: Optional[float]
    training_time: float
    feature_importance: Dict[str, float]


@dataclass
class AutoMLResult:
    """Result of AutoML run."""
    best_model: ModelResult
    all_models: List[ModelResult]
    total_time: float
    n_models_tried: int
    search_strategy: str


@dataclass
class Feature:
    """A feature definition."""
    name: str
    dtype: str
    description: str
    version: str
    owner: str
    created_at: str
    transformation: Optional[str] = None
    source_columns: Optional[List[str]] = None


@dataclass
class FeatureView:
    """A collection of related features."""
    name: str
    entity: str
    features: List[Feature]
    ttl_days: int
    online: bool
    offline: bool


@dataclass
class FeatureVector:
    """Retrieved features for an entity."""
    entity_id: Any
    features: Dict[str, Any]
    timestamp: str
    version: str


@dataclass
class Experiment:
    """ML experiment tracking."""
    run_id: str
    name: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    artifacts: List[str]
    timestamp: str
    status: str


# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_tabular_dataset(
    n_samples: int = 1000,
    n_features: int = 10,
    n_informative: int = 5,
    noise: float = 0.1,
    task: str = "classification"
) -> Tuple[List[List[float]], List[float], List[str]]:
    """Generate synthetic tabular dataset."""
    random.seed(42)

    feature_names = [f"feature_{i}" for i in range(n_features)]

    X = []
    y = []

    # Generate informative features
    for _ in range(n_samples):
        row = []
        target_value = 0

        for j in range(n_features):
            value = random.gauss(0, 1)
            row.append(value)

            # First n_informative features contribute to target
            if j < n_informative:
                weight = (j + 1) / n_informative
                target_value += weight * value

        # Add noise
        target_value += random.gauss(0, noise)

        X.append(row)

        if task == "classification":
            y.append(1 if target_value > 0 else 0)
        else:
            y.append(target_value)

    return X, y, feature_names


def generate_customer_data(n_customers: int = 500) -> Dict[str, List[Dict]]:
    """Generate relational customer data for feature engineering."""
    random.seed(42)

    # Customer table
    customers = []
    for i in range(n_customers):
        signup_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        customers.append({
            "customer_id": i,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
            "country": random.choice(["US", "UK", "CA", "DE", "FR"]),
            "age": random.randint(18, 70),
            "premium": random.random() > 0.7
        })

    # Orders table
    orders = []
    order_id = 0
    for customer in customers:
        n_orders = random.randint(0, 20)
        for _ in range(n_orders):
            order_date = datetime.strptime(customer["signup_date"], "%Y-%m-%d") + \
                        timedelta(days=random.randint(1, 300))
            orders.append({
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(10, 500), 2),
                "status": random.choice(["completed", "completed", "completed", "returned"])
            })
            order_id += 1

    # Products table
    products = []
    for order in orders:
        n_items = random.randint(1, 5)
        for _ in range(n_items):
            products.append({
                "order_id": order["order_id"],
                "product_type": random.choice(["electronics", "clothing", "books", "home", "food"]),
                "price": round(random.uniform(5, 200), 2),
                "quantity": random.randint(1, 3)
            })

    return {
        "customers": customers,
        "orders": orders,
        "products": products
    }


# =============================================================================
# SIMPLE ML MODELS (for demonstration)
# =============================================================================

class SimpleDecisionStump:
    """Simple decision stump (1-level tree)."""

    def __init__(self):
        self.feature_idx = 0
        self.threshold = 0
        self.left_pred = 0
        self.right_pred = 1

    def fit(self, X: List[List[float]], y: List[float]):
        n_samples = len(X)
        n_features = len(X[0])

        best_score = float('inf')

        for feat_idx in range(n_features):
            values = [X[i][feat_idx] for i in range(n_samples)]
            thresholds = sorted(set(values))[::max(1, len(set(values))//10)]

            for threshold in thresholds:
                left_y = [y[i] for i in range(n_samples) if X[i][feat_idx] <= threshold]
                right_y = [y[i] for i in range(n_samples) if X[i][feat_idx] > threshold]

                if not left_y or not right_y:
                    continue

                left_pred = sum(left_y) / len(left_y)
                right_pred = sum(right_y) / len(right_y)

                # Calculate MSE
                score = 0
                for i in range(n_samples):
                    pred = left_pred if X[i][feat_idx] <= threshold else right_pred
                    score += (y[i] - pred) ** 2

                if score < best_score:
                    best_score = score
                    self.feature_idx = feat_idx
                    self.threshold = threshold
                    self.left_pred = left_pred
                    self.right_pred = right_pred

    def predict(self, X: List[List[float]]) -> List[float]:
        predictions = []
        for row in X:
            if row[self.feature_idx] <= self.threshold:
                predictions.append(self.left_pred)
            else:
                predictions.append(self.right_pred)
        return predictions


class SimpleLinearModel:
    """Simple linear regression."""

    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 100):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.weights = []
        self.bias = 0

    def fit(self, X: List[List[float]], y: List[float]):
        n_samples = len(X)
        n_features = len(X[0])

        self.weights = [0.0] * n_features
        self.bias = 0.0

        for _ in range(self.n_iter):
            for i in range(n_samples):
                pred = sum(self.weights[j] * X[i][j] for j in range(n_features)) + self.bias
                error = y[i] - pred

                for j in range(n_features):
                    self.weights[j] += self.lr * error * X[i][j] / n_samples
                self.bias += self.lr * error / n_samples

    def predict(self, X: List[List[float]]) -> List[float]:
        predictions = []
        for row in X:
            pred = sum(self.weights[j] * row[j] for j in range(len(row))) + self.bias
            predictions.append(pred)
        return predictions


class SimpleGradientBoosting:
    """Simple gradient boosting with decision stumps."""

    def __init__(self, n_estimators: int = 10, learning_rate: float = 0.1):
        self.n_estimators = n_estimators
        self.lr = learning_rate
        self.estimators = []
        self.init_pred = 0

    def fit(self, X: List[List[float]], y: List[float]):
        n_samples = len(X)
        self.init_pred = sum(y) / len(y)

        predictions = [self.init_pred] * n_samples

        for _ in range(self.n_estimators):
            # Calculate residuals
            residuals = [y[i] - predictions[i] for i in range(n_samples)]

            # Fit tree to residuals
            tree = SimpleDecisionStump()
            tree.fit(X, residuals)
            self.estimators.append(tree)

            # Update predictions
            tree_preds = tree.predict(X)
            for i in range(n_samples):
                predictions[i] += self.lr * tree_preds[i]

    def predict(self, X: List[List[float]]) -> List[float]:
        predictions = [self.init_pred] * len(X)

        for tree in self.estimators:
            tree_preds = tree.predict(X)
            for i in range(len(X)):
                predictions[i] += self.lr * tree_preds[i]

        return predictions


# =============================================================================
# AUTOML IMPLEMENTATION
# =============================================================================

def calculate_mse(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate mean squared error."""
    n = len(y_true)
    return sum((y_true[i] - y_pred[i]) ** 2 for i in range(n)) / n


def calculate_accuracy(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate accuracy for classification."""
    n = len(y_true)
    correct = 0
    for i in range(n):
        pred = y_pred[i]
        # Handle NaN predictions
        if math.isnan(pred):
            pred = 0.5
        correct += 1 if round(pred) == y_true[i] else 0
    return correct / n


def calculate_r2(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate R² score."""
    mean_y = sum(y_true) / len(y_true)
    ss_tot = sum((y - mean_y) ** 2 for y in y_true)
    ss_res = sum((y_true[i] - y_pred[i]) ** 2 for i in range(len(y_true)))
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0


def train_test_split(
    X: List[List[float]],
    y: List[float],
    test_size: float = 0.2
) -> Tuple[List[List[float]], List[List[float]], List[float], List[float]]:
    """Split data into train and test sets."""
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


def generate_hyperparameter_configs(
    model_type: str,
    n_configs: int = 5
) -> List[Dict[str, Any]]:
    """Generate hyperparameter configurations to try."""
    configs = []

    if model_type == "linear":
        learning_rates = [0.001, 0.01, 0.05, 0.1, 0.2]
        iterations = [50, 100, 200]

        for lr in learning_rates[:n_configs]:
            for n_iter in iterations[:2]:
                configs.append({
                    "learning_rate": lr,
                    "n_iterations": n_iter
                })

    elif model_type == "gradient_boosting":
        n_estimators = [5, 10, 20, 30]
        learning_rates = [0.05, 0.1, 0.2, 0.3]

        for n_est in n_estimators[:n_configs]:
            for lr in learning_rates[:2]:
                configs.append({
                    "n_estimators": n_est,
                    "learning_rate": lr
                })

    elif model_type == "decision_stump":
        configs.append({})  # No hyperparameters

    return configs[:n_configs]


def run_automl(
    X: List[List[float]],
    y: List[float],
    feature_names: List[str],
    task: str = "regression",
    time_budget: int = 60,
    n_configs_per_model: int = 3
) -> AutoMLResult:
    """
    Run AutoML to find the best model.

    Tries multiple model types with different hyperparameters.
    """
    import time
    start_time = time.time()

    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5)

    model_types = ["linear", "gradient_boosting", "decision_stump"]
    all_results = []

    for model_type in model_types:
        configs = generate_hyperparameter_configs(model_type, n_configs_per_model)

        for config in configs:
            train_start = time.time()

            # Create and train model
            if model_type == "linear":
                model = SimpleLinearModel(**config)
            elif model_type == "gradient_boosting":
                model = SimpleGradientBoosting(**config)
            else:
                model = SimpleDecisionStump()

            model.fit(X_train, y_train)

            # Evaluate
            train_pred = model.predict(X_train)
            val_pred = model.predict(X_val)

            if task == "regression":
                train_score = calculate_r2(y_train, train_pred)
                val_score = calculate_r2(y_val, val_pred)
            else:
                train_score = calculate_accuracy(y_train, train_pred)
                val_score = calculate_accuracy(y_val, val_pred)

            training_time = time.time() - train_start

            # Feature importance (simplified)
            importance = {}
            if model_type == "linear" and hasattr(model, 'weights'):
                total_weight = sum(abs(w) for w in model.weights) or 1
                for i, name in enumerate(feature_names):
                    importance[name] = abs(model.weights[i]) / total_weight
            elif model_type == "gradient_boosting":
                # Count feature usage in stumps
                feature_counts = defaultdict(int)
                for est in model.estimators:
                    feature_counts[feature_names[est.feature_idx]] += 1
                total = sum(feature_counts.values()) or 1
                for name in feature_names:
                    importance[name] = feature_counts[name] / total
            else:
                for name in feature_names:
                    importance[name] = 1.0 / len(feature_names)

            result = ModelResult(
                config=ModelConfig(
                    name=f"{model_type}_{len(all_results)}",
                    model_type=model_type,
                    hyperparameters=config
                ),
                train_score=train_score,
                val_score=val_score,
                test_score=None,
                training_time=training_time,
                feature_importance=importance
            )

            all_results.append(result)

            # Check time budget
            if time.time() - start_time > time_budget:
                break

        if time.time() - start_time > time_budget:
            break

    # Find best model
    best_result = max(all_results, key=lambda x: x.val_score)

    # Evaluate on test set
    if best_result.config.model_type == "linear":
        best_model = SimpleLinearModel(**best_result.config.hyperparameters)
    elif best_result.config.model_type == "gradient_boosting":
        best_model = SimpleGradientBoosting(**best_result.config.hyperparameters)
    else:
        best_model = SimpleDecisionStump()

    best_model.fit(X_train + X_val, y_train + y_val)
    test_pred = best_model.predict(X_test)

    if task == "regression":
        best_result.test_score = calculate_r2(y_test, test_pred)
    else:
        best_result.test_score = calculate_accuracy(y_test, test_pred)

    total_time = time.time() - start_time

    return AutoMLResult(
        best_model=best_result,
        all_models=all_results,
        total_time=total_time,
        n_models_tried=len(all_results),
        search_strategy="grid_search"
    )


# =============================================================================
# AUTOMATED FEATURE ENGINEERING
# =============================================================================

def auto_feature_engineering(
    data: Dict[str, List[Dict]],
    entity: str = "customer_id",
    target_table: str = "customers"
) -> Tuple[List[Dict], List[str]]:
    """
    Automatically generate features from relational data.

    Implements deep feature synthesis (simplified).
    """
    customers = data["customers"]
    orders = data["orders"]
    products = data["products"]

    # Build lookup tables
    orders_by_customer = defaultdict(list)
    for order in orders:
        orders_by_customer[order["customer_id"]].append(order)

    products_by_order = defaultdict(list)
    for product in products:
        products_by_order[product["order_id"]].append(product)

    feature_records = []
    feature_names = []

    for customer in customers:
        cid = customer["customer_id"]
        cust_orders = orders_by_customer[cid]

        features = {
            "customer_id": cid,
            "original_age": customer["age"],
            "original_premium": 1 if customer["premium"] else 0,
        }

        # Order aggregations
        if cust_orders:
            amounts = [o["amount"] for o in cust_orders]
            features["order_count"] = len(cust_orders)
            features["order_sum"] = sum(amounts)
            features["order_mean"] = sum(amounts) / len(amounts)
            features["order_max"] = max(amounts)
            features["order_min"] = min(amounts)
            features["order_std"] = math.sqrt(sum((a - features["order_mean"])**2 for a in amounts) / len(amounts)) if len(amounts) > 1 else 0

            # Status aggregations
            completed = sum(1 for o in cust_orders if o["status"] == "completed")
            features["completed_ratio"] = completed / len(cust_orders)

            # Time features
            order_dates = [datetime.strptime(o["order_date"], "%Y-%m-%d") for o in cust_orders]
            features["days_since_last_order"] = (datetime(2024, 1, 1) - max(order_dates)).days
            features["days_since_first_order"] = (datetime(2024, 1, 1) - min(order_dates)).days
            features["order_frequency"] = len(cust_orders) / max(1, features["days_since_first_order"])

            # Product aggregations (depth 2)
            all_products = []
            for order in cust_orders:
                all_products.extend(products_by_order[order["order_id"]])

            if all_products:
                prices = [p["price"] for p in all_products]
                quantities = [p["quantity"] for p in all_products]
                features["product_count"] = len(all_products)
                features["avg_product_price"] = sum(prices) / len(prices)
                features["total_quantity"] = sum(quantities)

                # Category counts
                for cat in ["electronics", "clothing", "books", "home", "food"]:
                    features[f"cat_{cat}_count"] = sum(1 for p in all_products if p["product_type"] == cat)
            else:
                features["product_count"] = 0
                features["avg_product_price"] = 0
                features["total_quantity"] = 0
                for cat in ["electronics", "clothing", "books", "home", "food"]:
                    features[f"cat_{cat}_count"] = 0
        else:
            features["order_count"] = 0
            features["order_sum"] = 0
            features["order_mean"] = 0
            features["order_max"] = 0
            features["order_min"] = 0
            features["order_std"] = 0
            features["completed_ratio"] = 0
            features["days_since_last_order"] = 365
            features["days_since_first_order"] = 0
            features["order_frequency"] = 0
            features["product_count"] = 0
            features["avg_product_price"] = 0
            features["total_quantity"] = 0
            for cat in ["electronics", "clothing", "books", "home", "food"]:
                features[f"cat_{cat}_count"] = 0

        # Country encoding
        for country in ["US", "UK", "CA", "DE", "FR"]:
            features[f"country_{country}"] = 1 if customer["country"] == country else 0

        feature_records.append(features)

    # Get feature names (excluding customer_id)
    if feature_records:
        feature_names = [k for k in feature_records[0].keys() if k != "customer_id"]

    return feature_records, feature_names


# =============================================================================
# FEATURE STORE SIMULATION
# =============================================================================

class FeatureStore:
    """Simulated feature store."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.registry: Dict[str, FeatureView] = {}
        self.offline_store: Dict[str, List[Dict]] = {}
        self.online_store: Dict[str, Dict[str, Any]] = {}
        self.version = "1.0.0"
        self.storage_dir = ".automl_toolkit"
        os.makedirs(self.storage_dir, exist_ok=True)

    def register_feature_view(self, feature_view: FeatureView):
        """Register a feature view."""
        self.registry[feature_view.name] = feature_view
        print(f"   ✅ Registered feature view: {feature_view.name}")
        print(f"      Entity: {feature_view.entity}")
        print(f"      Features: {len(feature_view.features)}")
        print(f"      Online: {feature_view.online}, Offline: {feature_view.offline}")

    def materialize(self, feature_view_name: str, data: List[Dict]):
        """Materialize features to offline and online stores."""
        if feature_view_name not in self.registry:
            raise ValueError(f"Feature view {feature_view_name} not registered")

        fv = self.registry[feature_view_name]

        # Store in offline store
        self.offline_store[feature_view_name] = data

        # Store latest in online store (by entity)
        if fv.online:
            for record in data:
                entity_key = str(record.get(fv.entity, "unknown"))
                self.online_store[f"{feature_view_name}:{entity_key}"] = record

        print(f"   ✅ Materialized {len(data)} records to {feature_view_name}")

    def get_historical_features(
        self,
        feature_view_name: str,
        entity_ids: List[Any],
        features: List[str],
        timestamp: Optional[str] = None
    ) -> List[FeatureVector]:
        """Get historical features (for training)."""
        if feature_view_name not in self.offline_store:
            return []

        data = self.offline_store[feature_view_name]
        fv = self.registry[feature_view_name]

        results = []
        entity_data = {str(d[fv.entity]): d for d in data}

        for eid in entity_ids:
            if str(eid) in entity_data:
                record = entity_data[str(eid)]
                feature_values = {f: record.get(f, None) for f in features}
                results.append(FeatureVector(
                    entity_id=eid,
                    features=feature_values,
                    timestamp=timestamp or datetime.now().isoformat(),
                    version=self.version
                ))

        return results

    def get_online_features(
        self,
        feature_view_name: str,
        entity_id: Any,
        features: List[str]
    ) -> Optional[FeatureVector]:
        """Get online features (for inference)."""
        key = f"{feature_view_name}:{entity_id}"

        if key not in self.online_store:
            return None

        record = self.online_store[key]
        feature_values = {f: record.get(f, None) for f in features}

        return FeatureVector(
            entity_id=entity_id,
            features=feature_values,
            timestamp=datetime.now().isoformat(),
            version=self.version
        )

    def list_feature_views(self) -> List[str]:
        """List all registered feature views."""
        return list(self.registry.keys())

    def describe_feature_view(self, name: str) -> Optional[FeatureView]:
        """Get feature view details."""
        return self.registry.get(name)

    def save(self):
        """Save feature store state."""
        state = {
            "name": self.name,
            "version": self.version,
            "registry": {
                name: {
                    "name": fv.name,
                    "entity": fv.entity,
                    "features": [asdict(f) for f in fv.features],
                    "ttl_days": fv.ttl_days,
                    "online": fv.online,
                    "offline": fv.offline
                }
                for name, fv in self.registry.items()
            },
            "offline_store_keys": list(self.offline_store.keys()),
            "online_store_size": len(self.online_store)
        }

        with open(os.path.join(self.storage_dir, "feature_store.json"), 'w') as f:
            json.dump(state, f, indent=2)


# =============================================================================
# EXPERIMENT TRACKING
# =============================================================================

class ExperimentTracker:
    """Simple experiment tracking."""

    def __init__(self, experiment_name: str = "default"):
        self.experiment_name = experiment_name
        self.runs: List[Experiment] = []
        self.current_run: Optional[Experiment] = None
        self.storage_dir = ".automl_toolkit"
        os.makedirs(self.storage_dir, exist_ok=True)

    def start_run(self, run_name: str = None) -> str:
        """Start a new run."""
        run_id = f"run_{len(self.runs)}_{random.randint(1000, 9999)}"

        self.current_run = Experiment(
            run_id=run_id,
            name=run_name or run_id,
            parameters={},
            metrics={},
            artifacts=[],
            timestamp=datetime.now().isoformat(),
            status="running"
        )

        return run_id

    def log_param(self, key: str, value: Any):
        """Log a parameter."""
        if self.current_run:
            self.current_run.parameters[key] = value

    def log_metric(self, key: str, value: float):
        """Log a metric."""
        if self.current_run:
            self.current_run.metrics[key] = value

    def log_artifact(self, name: str):
        """Log an artifact."""
        if self.current_run:
            self.current_run.artifacts.append(name)

    def end_run(self, status: str = "completed"):
        """End the current run."""
        if self.current_run:
            self.current_run.status = status
            self.runs.append(self.current_run)
            self.current_run = None

    def get_best_run(self, metric: str = "val_score") -> Optional[Experiment]:
        """Get the best run by a metric."""
        valid_runs = [r for r in self.runs if metric in r.metrics]
        if not valid_runs:
            return None
        return max(valid_runs, key=lambda r: r.metrics[metric])

    def save(self):
        """Save experiment history."""
        data = {
            "experiment_name": self.experiment_name,
            "runs": [asdict(r) for r in self.runs]
        }

        with open(os.path.join(self.storage_dir, "experiments.json"), 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# ML PIPELINE
# =============================================================================

def run_ml_pipeline(
    data: Dict[str, List[Dict]],
    tracker: ExperimentTracker,
    feature_store: FeatureStore
) -> Dict[str, Any]:
    """Run end-to-end ML pipeline."""
    results = {}

    # Step 1: Feature Engineering
    print("\n   📊 Step 1: Feature Engineering")
    feature_records, feature_names = auto_feature_engineering(data)
    print(f"      Generated {len(feature_names)} features for {len(feature_records)} customers")
    results["n_features"] = len(feature_names)

    # Step 2: Register Features
    print("\n   📁 Step 2: Register Features in Feature Store")
    features = [
        Feature(
            name=name,
            dtype="float",
            description=f"Auto-generated feature: {name}",
            version="1.0.0",
            owner="automl_pipeline",
            created_at=datetime.now().isoformat()
        )
        for name in feature_names
    ]

    fv = FeatureView(
        name="customer_features",
        entity="customer_id",
        features=features,
        ttl_days=30,
        online=True,
        offline=True
    )
    feature_store.register_feature_view(fv)
    feature_store.materialize("customer_features", feature_records)

    # Step 3: Prepare Training Data
    print("\n   🔧 Step 3: Prepare Training Data")

    # Create target (predict if customer has high order value)
    X = []
    y = []
    filtered_names = [f for f in feature_names if f not in ["order_sum", "order_mean"]]

    for record in feature_records:
        row = []
        for f in filtered_names:
            val = record.get(f, 0)
            # Clean NaN and invalid values
            if val is None or (isinstance(val, float) and math.isnan(val)):
                val = 0
            row.append(val)
        X.append(row)
        # Target: high value customer (order_sum > median)
        y.append(1 if record.get("order_sum", 0) > 500 else 0)

    print(f"      Training samples: {len(X)}, Features: {len(filtered_names)}")

    # Step 4: Run AutoML
    print("\n   🤖 Step 4: Run AutoML")
    tracker.start_run("automl_classification")
    tracker.log_param("task", "classification")
    tracker.log_param("n_samples", len(X))
    tracker.log_param("n_features", len(filtered_names))

    automl_result = run_automl(
        X, y, filtered_names,
        task="classification",
        time_budget=30,
        n_configs_per_model=3
    )

    tracker.log_metric("val_score", automl_result.best_model.val_score)
    tracker.log_metric("test_score", automl_result.best_model.test_score or 0)
    tracker.log_metric("n_models_tried", automl_result.n_models_tried)
    tracker.log_artifact("best_model")
    tracker.end_run()

    print(f"      Best model: {automl_result.best_model.config.model_type}")
    print(f"      Validation accuracy: {automl_result.best_model.val_score:.4f}")
    print(f"      Test accuracy: {automl_result.best_model.test_score:.4f}")

    results["automl"] = {
        "best_model": automl_result.best_model.config.model_type,
        "val_score": automl_result.best_model.val_score,
        "test_score": automl_result.best_model.test_score,
        "n_models_tried": automl_result.n_models_tried
    }

    # Step 5: Save Pipeline
    print("\n   💾 Step 5: Save Pipeline")
    feature_store.save()
    tracker.save()
    print("      Saved feature store and experiments")

    return results


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_automl():
    """Demo 1: AutoML Model Selection"""
    print("\n" + "=" * 70)
    print("DEMO 1: AUTOML MODEL SELECTION")
    print("=" * 70)

    print("\n📊 Generating tabular dataset...")
    X, y, feature_names = generate_tabular_dataset(
        n_samples=500,
        n_features=8,
        n_informative=4,
        noise=0.2,
        task="regression"
    )

    print(f"   Samples: {len(X)}")
    print(f"   Features: {len(feature_names)}")
    print(f"   Task: Regression")

    print("\n🤖 Running AutoML...")
    print("   Trying multiple model types and hyperparameters...")

    result = run_automl(
        X, y, feature_names,
        task="regression",
        time_budget=30,
        n_configs_per_model=4
    )

    print(f"\n   ⏱️ Total time: {result.total_time:.2f}s")
    print(f"   📈 Models tried: {result.n_models_tried}")

    print("\n📊 MODEL LEADERBOARD:")
    print("   " + "-" * 60)
    print(f"   {'Model':<25} {'Type':<15} {'Val R²':<10} {'Time':<10}")
    print("   " + "-" * 60)

    # Sort by validation score
    sorted_models = sorted(result.all_models, key=lambda x: x.val_score, reverse=True)

    for i, model in enumerate(sorted_models[:8]):
        marker = "🏆" if i == 0 else "  "
        print(f"   {marker} {model.config.name:<23} {model.config.model_type:<15} "
              f"{model.val_score:<10.4f} {model.training_time:<10.3f}s")

    best = result.best_model
    print(f"\n🏆 BEST MODEL: {best.config.name}")
    print(f"   Type: {best.config.model_type}")
    print(f"   Hyperparameters: {best.config.hyperparameters}")
    print(f"   Train R²: {best.train_score:.4f}")
    print(f"   Validation R²: {best.val_score:.4f}")
    print(f"   Test R²: {best.test_score:.4f}")

    print("\n📊 FEATURE IMPORTANCE:")
    sorted_importance = sorted(best.feature_importance.items(), key=lambda x: x[1], reverse=True)

    for name, importance in sorted_importance[:5]:
        bar = "█" * int(importance * 30)
        print(f"   {name:<15} [{bar:<30}] {importance:.3f}")

    print("\n✅ AutoML demo complete!")

    return {
        "n_models": result.n_models_tried,
        "best_model": best.config.model_type,
        "val_score": round(best.val_score, 4),
        "test_score": round(best.test_score, 4),
        "total_time": round(result.total_time, 2)
    }


def demo_2_feature_engineering():
    """Demo 2: Automated Feature Engineering"""
    print("\n" + "=" * 70)
    print("DEMO 2: AUTOMATED FEATURE ENGINEERING")
    print("=" * 70)

    print("\n📊 Generating relational data...")
    data = generate_customer_data(n_customers=200)

    print(f"   Customers: {len(data['customers'])}")
    print(f"   Orders: {len(data['orders'])}")
    print(f"   Products: {len(data['products'])}")

    print("\n🔧 Running Deep Feature Synthesis...")
    feature_records, feature_names = auto_feature_engineering(data)

    print(f"\n   ✅ Generated {len(feature_names)} features!")

    # Categorize features
    original = [f for f in feature_names if f.startswith("original_")]
    aggregations = [f for f in feature_names if any(f.startswith(p) for p in ["order_", "product_", "total_", "avg_", "completed_"])]
    time_features = [f for f in feature_names if "days_" in f or "frequency" in f]
    category_features = [f for f in feature_names if f.startswith("cat_") or f.startswith("country_")]

    print("\n   📋 FEATURE CATEGORIES:")
    print(f"   Original features: {len(original)}")
    for f in original:
        print(f"      - {f}")

    print(f"\n   Aggregation features: {len(aggregations)}")
    for f in aggregations[:6]:
        print(f"      - {f}")
    if len(aggregations) > 6:
        print(f"      ... and {len(aggregations) - 6} more")

    print(f"\n   Time-based features: {len(time_features)}")
    for f in time_features:
        print(f"      - {f}")

    print(f"\n   Category features: {len(category_features)}")
    for f in category_features[:5]:
        print(f"      - {f}")
    if len(category_features) > 5:
        print(f"      ... and {len(category_features) - 5} more")

    # Show sample data
    print("\n   📋 SAMPLE FEATURE VALUES (Customer 0):")
    sample = feature_records[0]
    print(f"   " + "-" * 50)
    for name in ["order_count", "order_sum", "order_mean", "days_since_last_order", "product_count"]:
        if name in sample:
            print(f"   {name:<25} {sample[name]:.2f}")

    # Feature statistics
    print("\n   📊 FEATURE STATISTICS:")
    for name in ["order_count", "order_sum", "order_mean"]:
        values = [r[name] for r in feature_records]
        mean_val = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        print(f"   {name:<20} min={min_val:.1f}, max={max_val:.1f}, mean={mean_val:.1f}")

    print("\n💡 DEEP FEATURE SYNTHESIS:")
    print("   Depth 1: customer → orders (COUNT, SUM, MEAN, MAX, MIN)")
    print("   Depth 2: customer → orders → products (AVG price, COUNT)")
    print("   Transforms: Time features, category encoding")

    print("\n✅ Feature engineering demo complete!")

    return {
        "n_customers": len(data['customers']),
        "n_orders": len(data['orders']),
        "n_products": len(data['products']),
        "n_features_generated": len(feature_names),
        "categories": {
            "original": len(original),
            "aggregations": len(aggregations),
            "time": len(time_features),
            "categorical": len(category_features)
        }
    }


def demo_3_feature_store():
    """Demo 3: Feature Store Simulation"""
    print("\n" + "=" * 70)
    print("DEMO 3: FEATURE STORE SIMULATION")
    print("=" * 70)

    print("\n📁 Initializing Feature Store...")
    store = FeatureStore(name="demo_store")

    # Generate and engineer features
    print("\n📊 Preparing feature data...")
    data = generate_customer_data(n_customers=100)
    feature_records, feature_names = auto_feature_engineering(data)

    # Create feature definitions
    print("\n📝 Defining features...")
    features = [
        Feature(
            name="order_count",
            dtype="int64",
            description="Total number of orders by customer",
            version="1.0.0",
            owner="data_team",
            created_at=datetime.now().isoformat(),
            transformation="COUNT(orders)",
            source_columns=["orders.order_id"]
        ),
        Feature(
            name="order_sum",
            dtype="float64",
            description="Total order value",
            version="1.0.0",
            owner="data_team",
            created_at=datetime.now().isoformat(),
            transformation="SUM(orders.amount)",
            source_columns=["orders.amount"]
        ),
        Feature(
            name="avg_product_price",
            dtype="float64",
            description="Average price of products purchased",
            version="1.0.0",
            owner="data_team",
            created_at=datetime.now().isoformat(),
            transformation="AVG(orders.products.price)",
            source_columns=["products.price"]
        ),
        Feature(
            name="days_since_last_order",
            dtype="int64",
            description="Days since customer's last order",
            version="1.0.0",
            owner="data_team",
            created_at=datetime.now().isoformat(),
            transformation="DATEDIFF(NOW(), MAX(orders.order_date))",
            source_columns=["orders.order_date"]
        ),
    ]

    # Register feature view
    print("\n📋 Registering Feature View...")
    fv = FeatureView(
        name="customer_features",
        entity="customer_id",
        features=features,
        ttl_days=30,
        online=True,
        offline=True
    )
    store.register_feature_view(fv)

    # Materialize features
    print("\n💾 Materializing Features...")
    store.materialize("customer_features", feature_records)

    # Demonstrate historical feature retrieval
    print("\n📊 HISTORICAL FEATURES (for training):")
    entity_ids = [0, 1, 2, 3, 4]
    feature_list = ["order_count", "order_sum", "avg_product_price", "days_since_last_order"]

    historical = store.get_historical_features(
        "customer_features",
        entity_ids,
        feature_list,
        timestamp="2024-01-15"
    )

    print(f"   Retrieving features for customers: {entity_ids}")
    print(f"   Point-in-time: 2024-01-15")
    print("\n   " + "-" * 70)
    print(f"   {'Customer':<12} {'order_count':<12} {'order_sum':<12} {'avg_price':<12} {'days_since':<12}")
    print("   " + "-" * 70)

    for fv in historical:
        print(f"   {fv.entity_id:<12} "
              f"{fv.features['order_count']:<12.0f} "
              f"{fv.features['order_sum']:<12.2f} "
              f"{fv.features['avg_product_price']:<12.2f} "
              f"{fv.features['days_since_last_order']:<12.0f}")

    # Demonstrate online feature retrieval
    print("\n⚡ ONLINE FEATURES (for inference):")
    print("   Simulating real-time feature lookup...")

    for cid in [0, 5, 10]:
        online = store.get_online_features(
            "customer_features",
            cid,
            ["order_count", "order_sum"]
        )
        if online:
            print(f"   Customer {cid}: order_count={online.features['order_count']:.0f}, "
                  f"order_sum=${online.features['order_sum']:.2f}")

    # Save feature store
    print("\n💾 Saving Feature Store...")
    store.save()
    print("   Saved to .automl_toolkit/feature_store.json")

    print("\n💡 FEATURE STORE BENEFITS:")
    print("   ✅ Centralized feature definitions")
    print("   ✅ Point-in-time correctness for training")
    print("   ✅ Low-latency online serving")
    print("   ✅ Feature versioning and lineage")
    print("   ✅ Team collaboration and reuse")

    print("\n✅ Feature store demo complete!")

    return {
        "feature_views": len(store.list_feature_views()),
        "n_features": len(features),
        "offline_records": len(feature_records),
        "online_entities": len(store.online_store)
    }


def demo_4_ml_pipeline():
    """Demo 4: End-to-End ML Pipeline"""
    print("\n" + "=" * 70)
    print("DEMO 4: END-TO-END ML PIPELINE")
    print("=" * 70)

    print("\n🔄 Running automated ML pipeline...")
    print("\n   Pipeline stages:")
    print("   1. Feature Engineering (auto)")
    print("   2. Feature Store Registration")
    print("   3. Training Data Preparation")
    print("   4. AutoML Model Selection")
    print("   5. Save Pipeline")

    # Initialize components
    print("\n📦 Initializing pipeline components...")
    tracker = ExperimentTracker("customer_prediction")
    store = FeatureStore("pipeline_store")

    # Generate data
    print("\n📊 Loading source data...")
    data = generate_customer_data(n_customers=300)

    # Run pipeline
    results = run_ml_pipeline(data, tracker, store)

    # Show experiment history
    print("\n📈 EXPERIMENT TRACKING:")
    print("   " + "-" * 50)

    for run in tracker.runs:
        print(f"   Run: {run.name}")
        print(f"   Status: {run.status}")
        print(f"   Parameters: {run.parameters}")
        print(f"   Metrics: val_score={run.metrics.get('val_score', 'N/A'):.4f}, "
              f"test_score={run.metrics.get('test_score', 'N/A'):.4f}")

    best_run = tracker.get_best_run("val_score")
    if best_run:
        print(f"\n   🏆 Best Run: {best_run.name}")
        print(f"      Validation Score: {best_run.metrics.get('val_score', 0):.4f}")

    print("\n💡 PIPELINE AUTOMATION:")
    print("   ✅ Features auto-generated from relational data")
    print("   ✅ Features registered in feature store")
    print("   ✅ AutoML selected best model automatically")
    print("   ✅ All experiments tracked and saved")

    print("\n✅ ML pipeline demo complete!")

    return {
        "n_features": results["n_features"],
        "best_model": results["automl"]["best_model"],
        "test_accuracy": round(results["automl"]["test_score"], 4),
        "n_experiments": len(tracker.runs)
    }


def demo_5_full_report():
    """Demo 5: Full AutoML Report"""
    print("\n" + "=" * 70)
    print("DEMO 5: COMPREHENSIVE AUTOML REPORT")
    print("=" * 70)

    report = {
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }

    # Section 1: Data Overview
    print("\n" + "─" * 70)
    print("SECTION 1: DATA OVERVIEW")
    print("─" * 70)

    data = generate_customer_data(n_customers=300)
    print(f"\n   Source tables:")
    print(f"   ├── customers: {len(data['customers'])} records")
    print(f"   ├── orders: {len(data['orders'])} records")
    print(f"   └── products: {len(data['products'])} records")

    avg_orders = len(data['orders']) / len(data['customers'])
    avg_products = len(data['products']) / len(data['orders']) if data['orders'] else 0
    print(f"\n   Statistics:")
    print(f"   ├── Avg orders per customer: {avg_orders:.1f}")
    print(f"   └── Avg products per order: {avg_products:.1f}")

    report["sections"]["data"] = {
        "customers": len(data['customers']),
        "orders": len(data['orders']),
        "products": len(data['products'])
    }

    # Section 2: Feature Engineering
    print("\n" + "─" * 70)
    print("SECTION 2: AUTOMATED FEATURE ENGINEERING")
    print("─" * 70)

    feature_records, feature_names = auto_feature_engineering(data)

    print(f"\n   Deep Feature Synthesis Results:")
    print(f"   ├── Total features generated: {len(feature_names)}")
    print(f"   ├── Aggregation features: {len([f for f in feature_names if 'order_' in f or 'product_' in f])}")
    print(f"   ├── Time-based features: {len([f for f in feature_names if 'days_' in f])}")
    print(f"   └── Categorical features: {len([f for f in feature_names if 'cat_' in f or 'country_' in f])}")

    report["sections"]["features"] = {
        "total": len(feature_names),
        "feature_names": feature_names[:10]
    }

    # Section 3: AutoML Results
    print("\n" + "─" * 70)
    print("SECTION 3: AUTOML MODEL SELECTION")
    print("─" * 70)

    # Prepare data for AutoML
    X = []
    y = []
    for record in feature_records:
        row = [record.get(f, 0) for f in feature_names if f not in ["order_sum", "order_mean"]]
        X.append(row)
        y.append(1 if record.get("order_sum", 0) > 500 else 0)

    filtered_names = [f for f in feature_names if f not in ["order_sum", "order_mean"]]

    print(f"\n   Running AutoML...")
    automl_result = run_automl(
        X, y, filtered_names,
        task="classification",
        time_budget=30,
        n_configs_per_model=4
    )

    print(f"\n   Models evaluated: {automl_result.n_models_tried}")
    print(f"   Total time: {automl_result.total_time:.2f}s")

    print("\n   Model Leaderboard (Top 5):")
    sorted_models = sorted(automl_result.all_models, key=lambda x: x.val_score, reverse=True)

    print("   " + "-" * 55)
    print(f"   {'Rank':<6} {'Model':<20} {'Val Accuracy':<15} {'Train Time':<12}")
    print("   " + "-" * 55)

    for i, model in enumerate(sorted_models[:5]):
        print(f"   {i+1:<6} {model.config.model_type:<20} {model.val_score:<15.4f} {model.training_time:<12.3f}s")

    best = automl_result.best_model
    print(f"\n   🏆 Best Model: {best.config.model_type}")
    print(f"      Hyperparameters: {best.config.hyperparameters}")
    print(f"      Test Accuracy: {best.test_score:.4f}")

    report["sections"]["automl"] = {
        "n_models": automl_result.n_models_tried,
        "best_model": best.config.model_type,
        "val_score": round(best.val_score, 4),
        "test_score": round(best.test_score, 4)
    }

    # Section 4: Feature Importance
    print("\n" + "─" * 70)
    print("SECTION 4: FEATURE IMPORTANCE")
    print("─" * 70)

    sorted_importance = sorted(best.feature_importance.items(), key=lambda x: x[1], reverse=True)

    print("\n   Top 10 Most Important Features:")
    for i, (name, importance) in enumerate(sorted_importance[:10]):
        bar = "█" * int(importance * 25)
        print(f"   {i+1:2}. {name:<25} [{bar:<25}] {importance:.3f}")

    report["sections"]["feature_importance"] = {
        name: round(imp, 4) for name, imp in sorted_importance[:10]
    }

    # Section 5: Recommendations
    print("\n" + "─" * 70)
    print("SECTION 5: RECOMMENDATIONS")
    print("─" * 70)

    print("\n   📋 Based on AutoML analysis:")
    print(f"   1. Best model type: {best.config.model_type}")
    print(f"   2. Most predictive feature: {sorted_importance[0][0]}")
    print(f"   3. Expected accuracy: {best.test_score:.1%}")

    print("\n   💡 Suggestions:")
    print("   ├── Consider more training data for better performance")
    print("   ├── Try longer AutoML time budget for exhaustive search")
    print("   ├── Monitor feature drift in production")
    print("   └── Use feature store for consistent serving")

    # Save report
    storage_dir = ".automl_toolkit"
    os.makedirs(storage_dir, exist_ok=True)

    report_file = os.path.join(storage_dir, "automl_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n   📁 Report saved to: {report_file}")

    print("\n" + "=" * 70)
    print("✅ COMPREHENSIVE REPORT COMPLETE!")
    print("=" * 70)

    return report


# =============================================================================
# MAIN
# =============================================================================

def print_usage():
    """Print usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              MODULE 39: AUTOML & FEATURE STORE TOOLKIT                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  A comprehensive toolkit for automated machine learning and feature stores.   ║
║                                                                               ║
║  USAGE:                                                                       ║
║    python deliverable_automl_toolkit.py <demo>                                ║
║                                                                               ║
║  DEMOS:                                                                       ║
║    demo1  - AutoML model selection and hyperparameter tuning                  ║
║    demo2  - Automated feature engineering (Deep Feature Synthesis)            ║
║    demo3  - Feature store simulation (registry, serving)                      ║
║    demo4  - End-to-end ML pipeline                                            ║
║    demo5  - Full AutoML report                                                ║
║                                                                               ║
║  EXAMPLES:                                                                    ║
║    python deliverable_automl_toolkit.py demo1                                 ║
║    python deliverable_automl_toolkit.py demo5                                 ║
║                                                                               ║
║  KEY CONCEPTS:                                                                ║
║    • AutoML: Automated model selection and hyperparameter tuning              ║
║    • Feature Engineering: Auto-generate features from relational data         ║
║    • Feature Store: Centralized feature management and serving                ║
║    • ML Pipeline: End-to-end automation                                       ║
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
        "demo1": demo_1_automl,
        "demo2": demo_2_feature_engineering,
        "demo3": demo_3_feature_store,
        "demo4": demo_4_ml_pipeline,
        "demo5": demo_5_full_report
    }

    if command in demos:
        result = demos[command]()
        print(f"\n📊 Demo result: {json.dumps(result, indent=2, default=str)}")
    elif command == "help":
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
