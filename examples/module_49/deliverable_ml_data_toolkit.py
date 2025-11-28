#!/usr/bin/env python3
"""
ML Data Versioning & Feature Store Toolkit
==========================================

Demonstrate data versioning, feature stores, and data validation concepts:
- DVC-style data versioning with hashing
- Feature store with online/offline capabilities
- Data validation with expectations
- Data lineage tracking

This toolkit simulates DVC, Feast, and Great Expectations for learning purposes.

Usage:
    python deliverable_ml_data_toolkit.py demo1  # Data versioning (DVC-style)
    python deliverable_ml_data_toolkit.py demo2  # Feature store (Feast-style)
    python deliverable_ml_data_toolkit.py demo3  # Data validation (GX-style)
    python deliverable_ml_data_toolkit.py demo4  # Data lineage tracking
    python deliverable_ml_data_toolkit.py demo5  # Full data pipeline

Author: Neural Dojo
"""

import json
import os
import sys
import random
import hashlib
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import math


# =============================================================================
# CONFIGURATION
# =============================================================================

STORAGE_DIR = Path(".ml_data_toolkit")
CACHE_DIR = STORAGE_DIR / "cache"
VERSIONS_DIR = STORAGE_DIR / "versions"
FEATURES_DIR = STORAGE_DIR / "features"
LINEAGE_DIR = STORAGE_DIR / "lineage"


class DataType(Enum):
    """Data types for features."""
    INT64 = "int64"
    FLOAT64 = "float64"
    STRING = "string"
    BOOL = "bool"
    DATETIME = "datetime"


class ValidationStatus(Enum):
    """Validation result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


# =============================================================================
# DATA VERSIONING (DVC-STYLE)
# =============================================================================

@dataclass
class DataVersion:
    """Represents a versioned dataset."""
    path: str
    md5: str
    size: int
    timestamp: str
    message: str = ""
    parent_version: Optional[str] = None

    def to_dvc_file(self) -> str:
        """Generate DVC-style file content."""
        return f"""outs:
  - md5: {self.md5}
    size: {self.size}
    path: {Path(self.path).name}
"""


class DataVersioner:
    """DVC-style data versioning system."""

    def __init__(self):
        """Initialize versioner."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.versions: Dict[str, List[DataVersion]] = {}
        self._load_versions()

    def _compute_hash(self, data: Any) -> str:
        """Compute MD5 hash of data."""
        if isinstance(data, str):
            content = data.encode()
        elif isinstance(data, bytes):
            content = data
        elif isinstance(data, list):
            content = json.dumps(data, sort_keys=True).encode()
        else:
            content = str(data).encode()
        return hashlib.md5(content).hexdigest()

    def _load_versions(self):
        """Load existing versions from disk."""
        for version_file in VERSIONS_DIR.glob("*.json"):
            data = json.loads(version_file.read_text())
            path = data.get("path", "")
            if path not in self.versions:
                self.versions[path] = []
            self.versions[path].append(DataVersion(**data))

    def _save_version(self, version: DataVersion):
        """Save version to disk."""
        version_file = VERSIONS_DIR / f"{version.md5}.json"
        version_file.write_text(json.dumps(asdict(version), indent=2))

    def add(self, path: str, data: Any, message: str = "") -> DataVersion:
        """Add data to version control (like 'dvc add')."""
        # Compute hash
        md5 = self._compute_hash(data)
        size = len(str(data))

        # Get parent version
        parent = None
        if path in self.versions and self.versions[path]:
            parent = self.versions[path][-1].md5

        # Create version
        version = DataVersion(
            path=path,
            md5=md5,
            size=size,
            timestamp=datetime.now().isoformat(),
            message=message,
            parent_version=parent
        )

        # Cache data
        cache_file = CACHE_DIR / md5
        if isinstance(data, (list, dict)):
            cache_file.write_text(json.dumps(data))
        else:
            cache_file.write_text(str(data))

        # Store version
        if path not in self.versions:
            self.versions[path] = []
        self.versions[path].append(version)
        self._save_version(version)

        return version

    def get(self, path: str, version: Optional[str] = None) -> Optional[Any]:
        """Get data by path and optional version."""
        if path not in self.versions:
            return None

        if version:
            # Find specific version
            for v in self.versions[path]:
                if v.md5 == version or v.md5.startswith(version):
                    cache_file = CACHE_DIR / v.md5
                    if cache_file.exists():
                        return json.loads(cache_file.read_text())
            return None

        # Get latest version
        latest = self.versions[path][-1]
        cache_file = CACHE_DIR / latest.md5
        if cache_file.exists():
            try:
                return json.loads(cache_file.read_text())
            except json.JSONDecodeError:
                return cache_file.read_text()
        return None

    def log(self, path: str) -> List[DataVersion]:
        """Get version history for a path."""
        return self.versions.get(path, [])

    def diff(self, path: str, v1: str, v2: str) -> Dict[str, Any]:
        """Compare two versions."""
        data1 = self.get(path, v1)
        data2 = self.get(path, v2)

        if data1 is None or data2 is None:
            return {"error": "Version not found"}

        # Basic diff for lists
        if isinstance(data1, list) and isinstance(data2, list):
            return {
                "v1_count": len(data1),
                "v2_count": len(data2),
                "added": len(data2) - len(data1),
                "v1_hash": self._compute_hash(data1)[:8],
                "v2_hash": self._compute_hash(data2)[:8],
            }

        return {
            "v1_type": type(data1).__name__,
            "v2_type": type(data2).__name__,
        }


# =============================================================================
# FEATURE STORE (FEAST-STYLE)
# =============================================================================

@dataclass
class Feature:
    """A feature definition."""
    name: str
    dtype: DataType
    description: str = ""
    default_value: Any = None


@dataclass
class Entity:
    """An entity (the thing we make predictions about)."""
    name: str
    dtype: DataType = DataType.INT64
    description: str = ""


@dataclass
class FeatureView:
    """A collection of features for an entity."""
    name: str
    entity: str
    features: List[Feature] = field(default_factory=list)
    ttl_days: int = 365
    online: bool = True
    source: str = ""


class FeatureStore:
    """Feast-style feature store."""

    def __init__(self):
        """Initialize feature store."""
        FEATURES_DIR.mkdir(parents=True, exist_ok=True)
        self.entities: Dict[str, Entity] = {}
        self.feature_views: Dict[str, FeatureView] = {}
        self.offline_data: Dict[str, List[Dict]] = {}
        self.online_data: Dict[str, Dict[str, Dict]] = {}

    def register_entity(self, entity: Entity):
        """Register an entity."""
        self.entities[entity.name] = entity

    def register_feature_view(self, feature_view: FeatureView):
        """Register a feature view."""
        self.feature_views[feature_view.name] = feature_view

    def materialize(self, feature_view_name: str, data: List[Dict]):
        """Materialize features to offline and online stores."""
        if feature_view_name not in self.feature_views:
            raise ValueError(f"Feature view {feature_view_name} not found")

        fv = self.feature_views[feature_view_name]
        entity_name = fv.entity

        # Store in offline store
        self.offline_data[feature_view_name] = data

        # Store in online store (latest values per entity)
        if feature_view_name not in self.online_data:
            self.online_data[feature_view_name] = {}

        for row in data:
            entity_value = str(row.get(entity_name))
            self.online_data[feature_view_name][entity_value] = row

    def get_historical_features(
        self,
        entity_df: List[Dict],
        features: List[str]
    ) -> List[Dict]:
        """Get historical features for training (offline store)."""
        results = []

        for entity_row in entity_df:
            result = dict(entity_row)

            for feature_spec in features:
                # Parse feature_view:feature_name
                parts = feature_spec.split(":")
                if len(parts) != 2:
                    continue

                fv_name, feature_name = parts
                if fv_name not in self.offline_data:
                    continue

                fv = self.feature_views.get(fv_name)
                if not fv:
                    continue

                entity_name = fv.entity
                entity_value = entity_row.get(entity_name)

                # Find matching row in offline data
                for row in self.offline_data[fv_name]:
                    if row.get(entity_name) == entity_value:
                        result[feature_spec] = row.get(feature_name)
                        break

            results.append(result)

        return results

    def get_online_features(
        self,
        features: List[str],
        entity_rows: List[Dict]
    ) -> List[Dict]:
        """Get online features for serving (online store)."""
        results = []

        for entity_row in entity_rows:
            result = dict(entity_row)

            for feature_spec in features:
                parts = feature_spec.split(":")
                if len(parts) != 2:
                    continue

                fv_name, feature_name = parts
                if fv_name not in self.online_data:
                    continue

                fv = self.feature_views.get(fv_name)
                if not fv:
                    continue

                entity_name = fv.entity
                entity_value = str(entity_row.get(entity_name))

                if entity_value in self.online_data[fv_name]:
                    row = self.online_data[fv_name][entity_value]
                    result[feature_spec] = row.get(feature_name)

            results.append(result)

        return results


# =============================================================================
# DATA VALIDATION (GREAT EXPECTATIONS STYLE)
# =============================================================================

@dataclass
class ExpectationResult:
    """Result of running an expectation."""
    expectation_type: str
    success: bool
    observed_value: Any
    expected_value: Any = None
    details: str = ""


@dataclass
class ValidationResult:
    """Result of validating a dataset."""
    success: bool
    results: List[ExpectationResult] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


class DataValidator:
    """Great Expectations-style data validator."""

    def __init__(self):
        """Initialize validator."""
        self.expectations: List[Dict] = []

    def expect_column_to_exist(self, column: str) -> 'DataValidator':
        """Expect a column to exist."""
        self.expectations.append({
            "type": "expect_column_to_exist",
            "column": column
        })
        return self

    def expect_column_values_to_not_be_null(self, column: str) -> 'DataValidator':
        """Expect column values to not be null."""
        self.expectations.append({
            "type": "expect_column_values_to_not_be_null",
            "column": column
        })
        return self

    def expect_column_values_to_be_unique(self, column: str) -> 'DataValidator':
        """Expect column values to be unique."""
        self.expectations.append({
            "type": "expect_column_values_to_be_unique",
            "column": column
        })
        return self

    def expect_column_values_to_be_between(
        self,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> 'DataValidator':
        """Expect column values to be between min and max."""
        self.expectations.append({
            "type": "expect_column_values_to_be_between",
            "column": column,
            "min_value": min_value,
            "max_value": max_value
        })
        return self

    def expect_column_values_to_be_in_set(
        self,
        column: str,
        value_set: List[Any]
    ) -> 'DataValidator':
        """Expect column values to be in a set."""
        self.expectations.append({
            "type": "expect_column_values_to_be_in_set",
            "column": column,
            "value_set": value_set
        })
        return self

    def expect_column_mean_to_be_between(
        self,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> 'DataValidator':
        """Expect column mean to be between values."""
        self.expectations.append({
            "type": "expect_column_mean_to_be_between",
            "column": column,
            "min_value": min_value,
            "max_value": max_value
        })
        return self

    def expect_table_row_count_to_be_between(
        self,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> 'DataValidator':
        """Expect table row count to be between values."""
        self.expectations.append({
            "type": "expect_table_row_count_to_be_between",
            "min_value": min_value,
            "max_value": max_value
        })
        return self

    def validate(self, data: List[Dict]) -> ValidationResult:
        """Validate data against expectations."""
        results = []
        all_success = True

        for exp in self.expectations:
            exp_type = exp["type"]

            if exp_type == "expect_column_to_exist":
                column = exp["column"]
                exists = any(column in row for row in data)
                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=exists,
                    observed_value=exists,
                    expected_value=True,
                    details=f"Column '{column}' {'exists' if exists else 'does not exist'}"
                )

            elif exp_type == "expect_column_values_to_not_be_null":
                column = exp["column"]
                null_count = sum(1 for row in data if row.get(column) is None)
                success = null_count == 0
                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=success,
                    observed_value=null_count,
                    expected_value=0,
                    details=f"Column '{column}' has {null_count} null values"
                )

            elif exp_type == "expect_column_values_to_be_unique":
                column = exp["column"]
                values = [row.get(column) for row in data if row.get(column) is not None]
                unique_count = len(set(values))
                total_count = len(values)
                success = unique_count == total_count
                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=success,
                    observed_value=unique_count,
                    expected_value=total_count,
                    details=f"Column '{column}': {unique_count}/{total_count} unique values"
                )

            elif exp_type == "expect_column_values_to_be_between":
                column = exp["column"]
                min_val = exp.get("min_value")
                max_val = exp.get("max_value")
                values = [row.get(column) for row in data if row.get(column) is not None]

                violations = []
                for v in values:
                    if min_val is not None and v < min_val:
                        violations.append(v)
                    if max_val is not None and v > max_val:
                        violations.append(v)

                success = len(violations) == 0
                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=success,
                    observed_value=f"{len(violations)} violations",
                    expected_value=f"[{min_val}, {max_val}]",
                    details=f"Column '{column}': {len(values) - len(violations)}/{len(values)} in range"
                )

            elif exp_type == "expect_column_values_to_be_in_set":
                column = exp["column"]
                value_set = set(exp["value_set"])
                values = [row.get(column) for row in data if row.get(column) is not None]
                invalid = [v for v in values if v not in value_set]

                success = len(invalid) == 0
                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=success,
                    observed_value=f"{len(invalid)} invalid",
                    expected_value=str(value_set),
                    details=f"Column '{column}': {len(values) - len(invalid)}/{len(values)} valid"
                )

            elif exp_type == "expect_column_mean_to_be_between":
                column = exp["column"]
                min_val = exp.get("min_value")
                max_val = exp.get("max_value")
                values = [row.get(column) for row in data
                         if row.get(column) is not None and isinstance(row.get(column), (int, float))]

                if values:
                    mean = statistics.mean(values)
                    success = True
                    if min_val is not None and mean < min_val:
                        success = False
                    if max_val is not None and mean > max_val:
                        success = False

                    result = ExpectationResult(
                        expectation_type=exp_type,
                        success=success,
                        observed_value=round(mean, 2),
                        expected_value=f"[{min_val}, {max_val}]",
                        details=f"Column '{column}' mean: {mean:.2f}"
                    )
                else:
                    result = ExpectationResult(
                        expectation_type=exp_type,
                        success=False,
                        observed_value="No numeric values",
                        expected_value=f"[{min_val}, {max_val}]",
                        details=f"Column '{column}' has no numeric values"
                    )

            elif exp_type == "expect_table_row_count_to_be_between":
                min_val = exp.get("min_value")
                max_val = exp.get("max_value")
                count = len(data)

                success = True
                if min_val is not None and count < min_val:
                    success = False
                if max_val is not None and count > max_val:
                    success = False

                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=success,
                    observed_value=count,
                    expected_value=f"[{min_val}, {max_val}]",
                    details=f"Row count: {count}"
                )

            else:
                result = ExpectationResult(
                    expectation_type=exp_type,
                    success=False,
                    observed_value="Unknown",
                    details=f"Unknown expectation type: {exp_type}"
                )

            results.append(result)
            if not result.success:
                all_success = False

        return ValidationResult(success=all_success, results=results)


# =============================================================================
# DATA LINEAGE
# =============================================================================

@dataclass
class LineageNode:
    """A node in the data lineage graph."""
    id: str
    name: str
    node_type: str  # source, transform, model, output
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class LineageTracker:
    """Track data lineage through pipelines."""

    def __init__(self):
        """Initialize lineage tracker."""
        LINEAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, LineageNode] = {}
        self._load_lineage()

    def _load_lineage(self):
        """Load existing lineage from disk."""
        lineage_file = LINEAGE_DIR / "lineage.json"
        if lineage_file.exists():
            data = json.loads(lineage_file.read_text())
            for node_data in data.get("nodes", []):
                node = LineageNode(**node_data)
                self.nodes[node.id] = node

    def _save_lineage(self):
        """Save lineage to disk."""
        lineage_file = LINEAGE_DIR / "lineage.json"
        data = {"nodes": [asdict(n) for n in self.nodes.values()]}
        lineage_file.write_text(json.dumps(data, indent=2))

    def add_node(
        self,
        name: str,
        node_type: str,
        inputs: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> LineageNode:
        """Add a lineage node."""
        node_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        node = LineageNode(
            id=node_id,
            name=name,
            node_type=node_type,
            inputs=inputs or [],
            metadata=metadata or {}
        )

        # Update outputs of input nodes
        for input_id in node.inputs:
            if input_id in self.nodes:
                self.nodes[input_id].outputs.append(node_id)

        self.nodes[node_id] = node
        self._save_lineage()
        return node

    def get_upstream(self, node_id: str) -> List[LineageNode]:
        """Get all upstream (input) nodes."""
        if node_id not in self.nodes:
            return []

        result = []
        visited = set()

        def traverse(nid):
            if nid in visited or nid not in self.nodes:
                return
            visited.add(nid)
            node = self.nodes[nid]
            for input_id in node.inputs:
                traverse(input_id)
                if input_id in self.nodes:
                    result.append(self.nodes[input_id])

        traverse(node_id)
        return result

    def get_downstream(self, node_id: str) -> List[LineageNode]:
        """Get all downstream (output) nodes."""
        if node_id not in self.nodes:
            return []

        result = []
        visited = set()

        def traverse(nid):
            if nid in visited or nid not in self.nodes:
                return
            visited.add(nid)
            node = self.nodes[nid]
            for output_id in node.outputs:
                if output_id in self.nodes:
                    result.append(self.nodes[output_id])
                traverse(output_id)

        traverse(node_id)
        return result


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_data_versioning():
    """Demo 1: DVC-style data versioning."""
    print("=" * 70)
    print("DEMO 1: DATA VERSIONING (DVC-STYLE)")
    print("=" * 70)

    versioner = DataVersioner()

    # Overview
    print("\n📋 DVC Concepts:")
    print("-" * 40)
    print("  • Track large files with small .dvc files")
    print("  • Store data in remote storage (S3, GCS)")
    print("  • Version data alongside code")
    print("  • Reproducible ML pipelines")

    # Version 1: Initial dataset
    print("\n📊 Version 1: Initial Dataset")
    print("-" * 40)

    data_v1 = [
        {"user_id": 1, "age": 25, "purchases": 10},
        {"user_id": 2, "age": 30, "purchases": 15},
        {"user_id": 3, "age": 35, "purchases": 20},
    ]

    v1 = versioner.add("data/users.csv", data_v1, "Initial user data (3 users)")
    print(f"  Added: data/users.csv")
    print(f"  MD5: {v1.md5}")
    print(f"  Size: {v1.size} bytes")
    print(f"  Rows: {len(data_v1)}")

    # Show DVC file content
    print("\n  Generated .dvc file:")
    print("-" * 40)
    for line in v1.to_dvc_file().split('\n'):
        print(f"  {line}")

    # Version 2: More data
    print("\n📊 Version 2: Add More Users")
    print("-" * 40)

    data_v2 = data_v1 + [
        {"user_id": 4, "age": 28, "purchases": 12},
        {"user_id": 5, "age": 42, "purchases": 25},
    ]

    v2 = versioner.add("data/users.csv", data_v2, "Add 2 more users (5 total)")
    print(f"  Added: data/users.csv")
    print(f"  MD5: {v2.md5}")
    print(f"  Size: {v2.size} bytes")
    print(f"  Rows: {len(data_v2)}")

    # Version 3: Update existing
    print("\n📊 Version 3: Update Purchases")
    print("-" * 40)

    data_v3 = [
        {"user_id": 1, "age": 25, "purchases": 15},  # Updated
        {"user_id": 2, "age": 30, "purchases": 20},  # Updated
        {"user_id": 3, "age": 35, "purchases": 25},  # Updated
        {"user_id": 4, "age": 28, "purchases": 18},  # Updated
        {"user_id": 5, "age": 42, "purchases": 30},  # Updated
    ]

    v3 = versioner.add("data/users.csv", data_v3, "Update purchase counts")
    print(f"  Added: data/users.csv")
    print(f"  MD5: {v3.md5}")
    print(f"  Rows: {len(data_v3)}")

    # Show version log
    print("\n📜 Version Log (like 'dvc log'):")
    print("-" * 60)
    print(f"  {'Version':<12} {'Size':<10} {'Message'}")
    print("-" * 60)

    for version in versioner.log("data/users.csv"):
        short_hash = version.md5[:8]
        print(f"  {short_hash:<12} {version.size:<10} {version.message}")

    # Diff versions
    print("\n🔍 Diff v1 vs v3:")
    print("-" * 40)

    diff = versioner.diff("data/users.csv", v1.md5, v3.md5)
    print(f"  v1 rows: {diff['v1_count']}")
    print(f"  v3 rows: {diff['v2_count']}")
    print(f"  Added: {diff['added']} rows")

    # Checkout old version
    print("\n⏪ Checkout v1 (like 'dvc checkout'):")
    print("-" * 40)

    old_data = versioner.get("data/users.csv", v1.md5)
    print(f"  Retrieved {len(old_data)} rows from v1")
    print(f"  First row: {old_data[0]}")

    print("\n✅ Demo 1 complete!")
    print(f"📂 Data cached in: {CACHE_DIR}")


def demo_2_feature_store():
    """Demo 2: Feast-style feature store."""
    print("=" * 70)
    print("DEMO 2: FEATURE STORE (FEAST-STYLE)")
    print("=" * 70)

    store = FeatureStore()

    # Overview
    print("\n📋 Feature Store Concepts:")
    print("-" * 40)
    print("  • Centralized feature definitions")
    print("  • Same features for training & serving")
    print("  • Offline store (historical, batch)")
    print("  • Online store (real-time, low latency)")

    # Define entity
    print("\n👤 Define Entity: user")
    print("-" * 40)

    user_entity = Entity(
        name="user_id",
        dtype=DataType.INT64,
        description="Unique user identifier"
    )
    store.register_entity(user_entity)
    print(f"  Entity: {user_entity.name}")
    print(f"  Type: {user_entity.dtype.value}")

    # Define features
    print("\n📊 Define Feature View: user_features")
    print("-" * 40)

    user_features = FeatureView(
        name="user_features",
        entity="user_id",
        features=[
            Feature(name="age", dtype=DataType.INT64, description="User age"),
            Feature(name="total_purchases", dtype=DataType.INT64),
            Feature(name="avg_order_value", dtype=DataType.FLOAT64),
            Feature(name="days_since_last_purchase", dtype=DataType.INT64),
            Feature(name="loyalty_tier", dtype=DataType.STRING),
        ],
        ttl_days=365,
        online=True
    )
    store.register_feature_view(user_features)

    print(f"  Feature View: {user_features.name}")
    print(f"  Entity: {user_features.entity}")
    print(f"  Features:")
    for f in user_features.features:
        print(f"    • {f.name}: {f.dtype.value}")

    # Materialize features
    print("\n💾 Materialize Features")
    print("-" * 40)

    feature_data = [
        {"user_id": 1, "age": 25, "total_purchases": 10, "avg_order_value": 45.50,
         "days_since_last_purchase": 5, "loyalty_tier": "gold"},
        {"user_id": 2, "age": 30, "total_purchases": 25, "avg_order_value": 78.25,
         "days_since_last_purchase": 2, "loyalty_tier": "platinum"},
        {"user_id": 3, "age": 35, "total_purchases": 5, "avg_order_value": 32.00,
         "days_since_last_purchase": 30, "loyalty_tier": "silver"},
        {"user_id": 4, "age": 28, "total_purchases": 15, "avg_order_value": 55.75,
         "days_since_last_purchase": 7, "loyalty_tier": "gold"},
        {"user_id": 5, "age": 42, "total_purchases": 50, "avg_order_value": 120.00,
         "days_since_last_purchase": 1, "loyalty_tier": "platinum"},
    ]

    store.materialize("user_features", feature_data)
    print(f"  Materialized {len(feature_data)} rows to offline & online stores")

    # Get historical features (for training)
    print("\n📚 Get Historical Features (Training)")
    print("-" * 40)

    entity_df = [
        {"user_id": 1},
        {"user_id": 2},
        {"user_id": 3},
    ]

    training_data = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "user_features:age",
            "user_features:total_purchases",
            "user_features:avg_order_value",
        ]
    )

    print("  Entity DataFrame → Training DataFrame:")
    for row in training_data:
        print(f"    user_id={row['user_id']}: age={row.get('user_features:age')}, "
              f"purchases={row.get('user_features:total_purchases')}, "
              f"avg_order=${row.get('user_features:avg_order_value', 0):.2f}")

    # Get online features (for serving)
    print("\n⚡ Get Online Features (Serving)")
    print("-" * 40)

    online_features = store.get_online_features(
        features=[
            "user_features:age",
            "user_features:loyalty_tier",
            "user_features:avg_order_value",
        ],
        entity_rows=[{"user_id": 5}]
    )

    print("  Real-time feature lookup for user_id=5:")
    for row in online_features:
        print(f"    age: {row.get('user_features:age')}")
        print(f"    loyalty_tier: {row.get('user_features:loyalty_tier')}")
        print(f"    avg_order_value: ${row.get('user_features:avg_order_value', 0):.2f}")

    # Training vs Serving comparison
    print("\n📊 Training vs Serving Consistency:")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │         SAME FEATURE DEFINITIONS                        │
    │         SAME FEATURE VALUES                             │
    │         NO TRAINING-SERVING SKEW                        │
    └─────────────────────────────────────────────────────────┘

    Training Pipeline:
      store.get_historical_features() → Batch processing → Model

    Serving Pipeline:
      store.get_online_features() → Real-time → Model prediction
    """)

    print("\n✅ Demo 2 complete!")


def demo_3_data_validation():
    """Demo 3: Great Expectations-style data validation."""
    print("=" * 70)
    print("DEMO 3: DATA VALIDATION (GREAT EXPECTATIONS-STYLE)")
    print("=" * 70)

    # Overview
    print("\n📋 Data Validation Concepts:")
    print("-" * 40)
    print("  • Define expectations for your data")
    print("  • Validate data before training")
    print("  • Catch data quality issues early")
    print("  • Document data requirements")

    # Create validator with expectations
    print("\n📝 Define Expectations Suite")
    print("-" * 40)

    validator = DataValidator()
    validator.expect_column_to_exist("user_id")
    validator.expect_column_to_exist("age")
    validator.expect_column_to_exist("email")
    validator.expect_column_values_to_not_be_null("user_id")
    validator.expect_column_values_to_be_unique("user_id")
    validator.expect_column_values_to_be_between("age", min_value=0, max_value=120)
    validator.expect_column_values_to_be_in_set("country", ["US", "UK", "CA", "DE"])
    validator.expect_column_mean_to_be_between("age", min_value=20, max_value=50)
    validator.expect_table_row_count_to_be_between(min_value=3, max_value=1000)

    print(f"  Defined {len(validator.expectations)} expectations:")
    for exp in validator.expectations:
        print(f"    • {exp['type']}")

    # Test with good data
    print("\n✅ Validate Good Data")
    print("-" * 40)

    good_data = [
        {"user_id": 1, "age": 25, "email": "a@test.com", "country": "US"},
        {"user_id": 2, "age": 30, "email": "b@test.com", "country": "UK"},
        {"user_id": 3, "age": 35, "email": "c@test.com", "country": "CA"},
        {"user_id": 4, "age": 28, "email": "d@test.com", "country": "DE"},
        {"user_id": 5, "age": 42, "email": "e@test.com", "country": "US"},
    ]

    result = validator.validate(good_data)
    print(f"  Overall: {'✅ PASSED' if result.success else '❌ FAILED'}")
    print(f"  Results:")
    for r in result.results:
        status = "✅" if r.success else "❌"
        print(f"    {status} {r.expectation_type}: {r.details}")

    # Test with bad data
    print("\n❌ Validate Bad Data")
    print("-" * 40)

    bad_data = [
        {"user_id": 1, "age": 25, "email": "a@test.com", "country": "US"},
        {"user_id": 1, "age": 30, "email": None, "country": "UK"},  # Duplicate user_id, null email
        {"user_id": 3, "age": 150, "email": "c@test.com", "country": "FR"},  # Invalid age, invalid country
        {"user_id": None, "age": 28, "email": "d@test.com", "country": "DE"},  # Null user_id
    ]

    result = validator.validate(bad_data)
    print(f"  Overall: {'✅ PASSED' if result.success else '❌ FAILED'}")
    print(f"  Results:")
    for r in result.results:
        status = "✅" if r.success else "❌"
        print(f"    {status} {r.expectation_type}: {r.details}")

    # Summary
    print("\n📊 Validation Summary:")
    print("-" * 40)
    print("""
    Good Data: All expectations passed
    Bad Data: Multiple failures detected

    Issues Found in Bad Data:
    • Duplicate user_id values
    • Null values in required columns
    • Age out of valid range (150 > 120)
    • Invalid country code ('FR' not in set)
    """)

    print("\n✅ Demo 3 complete!")


def demo_4_data_lineage():
    """Demo 4: Data lineage tracking."""
    print("=" * 70)
    print("DEMO 4: DATA LINEAGE TRACKING")
    print("=" * 70)

    tracker = LineageTracker()

    # Overview
    print("\n📋 Data Lineage Concepts:")
    print("-" * 40)
    print("  • Track data transformations")
    print("  • Understand data dependencies")
    print("  • Impact analysis (what breaks if X changes)")
    print("  • Audit trail and compliance")

    # Build lineage graph
    print("\n🔗 Building Lineage Graph")
    print("-" * 40)

    # Sources
    raw_users = tracker.add_node(
        "raw_users",
        "source",
        metadata={"location": "s3://data/raw/users.parquet", "format": "parquet"}
    )
    print(f"  Added source: raw_users ({raw_users.id})")

    raw_transactions = tracker.add_node(
        "raw_transactions",
        "source",
        metadata={"location": "s3://data/raw/transactions.parquet", "format": "parquet"}
    )
    print(f"  Added source: raw_transactions ({raw_transactions.id})")

    # Transformations
    cleaned_users = tracker.add_node(
        "cleaned_users",
        "transform",
        inputs=[raw_users.id],
        metadata={"operation": "clean_nulls", "script": "clean_users.py"}
    )
    print(f"  Added transform: cleaned_users ({cleaned_users.id})")

    user_features = tracker.add_node(
        "user_features",
        "transform",
        inputs=[cleaned_users.id, raw_transactions.id],
        metadata={"operation": "feature_engineering", "script": "create_features.py"}
    )
    print(f"  Added transform: user_features ({user_features.id})")

    # Model
    model = tracker.add_node(
        "churn_model_v2",
        "model",
        inputs=[user_features.id],
        metadata={"framework": "sklearn", "type": "RandomForest"}
    )
    print(f"  Added model: churn_model_v2 ({model.id})")

    # Output
    predictions = tracker.add_node(
        "churn_predictions",
        "output",
        inputs=[model.id],
        metadata={"destination": "s3://data/predictions/"}
    )
    print(f"  Added output: churn_predictions ({predictions.id})")

    # Visualize lineage
    print("\n📊 Lineage Graph:")
    print("-" * 40)
    print("""
    ┌─────────────────┐     ┌─────────────────┐
    │   raw_users     │     │ raw_transactions│
    │    (source)     │     │    (source)     │
    └────────┬────────┘     └────────┬────────┘
             │                       │
             ▼                       │
    ┌─────────────────┐              │
    │  cleaned_users  │              │
    │  (transform)    │              │
    └────────┬────────┘              │
             │                       │
             └───────────┬───────────┘
                         │
                         ▼
              ┌─────────────────┐
              │  user_features  │
              │  (transform)    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ churn_model_v2  │
              │    (model)      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │churn_predictions│
              │   (output)      │
              └─────────────────┘
    """)

    # Upstream analysis
    print("\n🔍 Upstream Analysis: What does 'churn_model_v2' depend on?")
    print("-" * 40)

    upstream = tracker.get_upstream(model.id)
    for node in upstream:
        print(f"  • {node.name} ({node.node_type})")

    # Downstream analysis (impact)
    print("\n💥 Impact Analysis: What depends on 'raw_users'?")
    print("-" * 40)

    downstream = tracker.get_downstream(raw_users.id)
    for node in downstream:
        print(f"  • {node.name} ({node.node_type})")

    print("\n  ⚠️  If raw_users changes, these components may be affected!")

    print("\n✅ Demo 4 complete!")
    print(f"📂 Lineage saved to: {LINEAGE_DIR}")


def demo_5_full_pipeline():
    """Demo 5: Full data pipeline with versioning, features, validation."""
    print("=" * 70)
    print("DEMO 5: FULL DATA PIPELINE")
    print("=" * 70)

    # Initialize all components
    versioner = DataVersioner()
    feature_store = FeatureStore()
    lineage = LineageTracker()

    print("\n📋 Pipeline Steps:")
    print("-" * 40)
    print("""
    1. Load & Version Raw Data
    2. Validate Data Quality
    3. Engineer Features
    4. Store in Feature Store
    5. Track Lineage
    """)

    # Step 1: Load and version data
    print("\n1️⃣ LOAD & VERSION RAW DATA")
    print("-" * 40)

    raw_data = [
        {"user_id": 1, "age": 25, "purchases": 10, "country": "US", "active": True},
        {"user_id": 2, "age": 30, "purchases": 25, "country": "UK", "active": True},
        {"user_id": 3, "age": 35, "purchases": 5, "country": "CA", "active": False},
        {"user_id": 4, "age": 28, "purchases": 15, "country": "DE", "active": True},
        {"user_id": 5, "age": 42, "purchases": 50, "country": "US", "active": True},
        {"user_id": 6, "age": 33, "purchases": 8, "country": "UK", "active": True},
        {"user_id": 7, "age": 29, "purchases": 12, "country": "CA", "active": True},
        {"user_id": 8, "age": 45, "purchases": 30, "country": "DE", "active": False},
    ]

    version = versioner.add("data/users_raw.csv", raw_data, "Raw user data for pipeline")
    print(f"  ✅ Versioned {len(raw_data)} rows")
    print(f"  Version: {version.md5[:8]}")

    lineage_raw = lineage.add_node("raw_users", "source", metadata={"version": version.md5})

    # Step 2: Validate data
    print("\n2️⃣ VALIDATE DATA QUALITY")
    print("-" * 40)

    validator = DataValidator()
    validator.expect_column_to_exist("user_id")
    validator.expect_column_to_exist("age")
    validator.expect_column_values_to_not_be_null("user_id")
    validator.expect_column_values_to_be_unique("user_id")
    validator.expect_column_values_to_be_between("age", min_value=18, max_value=100)
    validator.expect_column_values_to_be_in_set("country", ["US", "UK", "CA", "DE"])
    validator.expect_table_row_count_to_be_between(min_value=5, max_value=10000)

    result = validator.validate(raw_data)

    if result.success:
        print("  ✅ All validations passed!")
    else:
        print("  ❌ Validation failed!")
        for r in result.results:
            if not r.success:
                print(f"    • {r.expectation_type}: {r.details}")
        return

    # Step 3: Engineer features
    print("\n3️⃣ ENGINEER FEATURES")
    print("-" * 40)

    feature_data = []
    for row in raw_data:
        features = {
            "user_id": row["user_id"],
            "age": row["age"],
            "total_purchases": row["purchases"],
            "purchase_frequency": "high" if row["purchases"] > 20 else "medium" if row["purchases"] > 10 else "low",
            "is_active": row["active"],
            "region": "AMERICAS" if row["country"] in ["US", "CA"] else "EUROPE",
            "age_group": "young" if row["age"] < 30 else "middle" if row["age"] < 40 else "senior",
        }
        feature_data.append(features)

    print(f"  ✅ Engineered {len(feature_data)} feature rows")
    print(f"  Features: {list(feature_data[0].keys())}")

    lineage_features = lineage.add_node(
        "user_features",
        "transform",
        inputs=[lineage_raw.id],
        metadata={"features": list(feature_data[0].keys())}
    )

    # Step 4: Store in feature store
    print("\n4️⃣ STORE IN FEATURE STORE")
    print("-" * 40)

    # Register entity and feature view
    user_entity = Entity(name="user_id", dtype=DataType.INT64)
    feature_store.register_entity(user_entity)

    user_fv = FeatureView(
        name="user_features",
        entity="user_id",
        features=[
            Feature(name="age", dtype=DataType.INT64),
            Feature(name="total_purchases", dtype=DataType.INT64),
            Feature(name="purchase_frequency", dtype=DataType.STRING),
            Feature(name="is_active", dtype=DataType.BOOL),
            Feature(name="region", dtype=DataType.STRING),
            Feature(name="age_group", dtype=DataType.STRING),
        ]
    )
    feature_store.register_feature_view(user_fv)

    # Materialize
    feature_store.materialize("user_features", feature_data)
    print("  ✅ Features materialized to offline & online stores")

    # Step 5: Verify and track lineage
    print("\n5️⃣ VERIFY & TRACK LINEAGE")
    print("-" * 40)

    # Test feature retrieval
    training_features = feature_store.get_historical_features(
        entity_df=[{"user_id": 1}, {"user_id": 5}],
        features=[
            "user_features:age",
            "user_features:purchase_frequency",
            "user_features:region"
        ]
    )

    print("  Training features sample:")
    for row in training_features:
        print(f"    user_id={row['user_id']}: "
              f"age={row.get('user_features:age')}, "
              f"freq={row.get('user_features:purchase_frequency')}, "
              f"region={row.get('user_features:region')}")

    # Online features
    online_result = feature_store.get_online_features(
        features=["user_features:purchase_frequency", "user_features:is_active"],
        entity_rows=[{"user_id": 2}]
    )

    print("\n  Online features for user_id=2:")
    for row in online_result:
        print(f"    purchase_frequency: {row.get('user_features:purchase_frequency')}")
        print(f"    is_active: {row.get('user_features:is_active')}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 PIPELINE SUMMARY")
    print("=" * 70)
    print(f"""
  Raw Data:
    • {len(raw_data)} rows versioned
    • Version: {version.md5[:8]}

  Validation:
    • {len(validator.expectations)} expectations checked
    • Status: ✅ All passed

  Features:
    • {len(feature_data)} feature rows
    • {len(user_fv.features)} features engineered

  Stores:
    • Offline: Ready for training
    • Online: Ready for serving

  Lineage:
    • {len(lineage.nodes)} nodes tracked
    • End-to-end traceability
""")

    print("✅ Demo 5 complete!")
    print(f"\n📂 All data saved to: {STORAGE_DIR}")


def show_usage():
    """Show usage information."""
    print("""
ML Data Versioning & Feature Store Toolkit
==========================================

Demonstrate DVC, Feast, and Great Expectations concepts.

Usage:
    python deliverable_ml_data_toolkit.py <demo>

Demos:
    demo1   Data versioning (DVC-style)
    demo2   Feature store (Feast-style)
    demo3   Data validation (Great Expectations-style)
    demo4   Data lineage tracking
    demo5   Full data pipeline

Examples:
    python deliverable_ml_data_toolkit.py demo1
    python deliverable_ml_data_toolkit.py demo5

Output:
    Data saved to .ml_data_toolkit/
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_data_versioning,
        "demo2": demo_2_feature_store,
        "demo3": demo_3_data_validation,
        "demo4": demo_4_data_lineage,
        "demo5": demo_5_full_pipeline,
    }

    if command in demos:
        demos[command]()
    elif command in ["help", "-h", "--help"]:
        show_usage()
    else:
        print(f"Unknown command: {command}")
        show_usage()


if __name__ == "__main__":
    main()
