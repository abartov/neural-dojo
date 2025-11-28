#!/usr/bin/env python3
"""
ML DevOps Toolkit - Module 43 Deliverable

A comprehensive toolkit for ML DevOps including:
- Git workflow automation for ML projects
- Pre-commit configuration generation
- Data and model quality testing framework
- Project structure templates
- DVC pipeline helpers

Usage:
    python deliverable_ml_devops_toolkit.py demo1  # Git workflow helper
    python deliverable_ml_devops_toolkit.py demo2  # Pre-commit setup
    python deliverable_ml_devops_toolkit.py demo3  # Data quality tests
    python deliverable_ml_devops_toolkit.py demo4  # Model quality tests
    python deliverable_ml_devops_toolkit.py demo5  # Project template

Author: Neural Dojo
Module: 43 - DevOps Fundamentals for ML Engineers
"""

import json
import hashlib
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Callable, Any, Tuple
from pathlib import Path
import random


# ============================================
# CONFIGURATION
# ============================================

STORAGE_DIR = Path(".ml_devops_toolkit")
CONFIG_FILE = STORAGE_DIR / "config.json"
REPORTS_DIR = STORAGE_DIR / "reports"

random.seed(42)


def ensure_storage():
    """Create storage directories if needed."""
    STORAGE_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


# ============================================
# ENUMS AND DATA CLASSES
# ============================================

class BranchType(Enum):
    """Types of Git branches for ML projects."""
    FEATURE = "feature"
    FIX = "fix"
    EXPERIMENT = "experiment"
    MODEL = "model"
    DATA = "data"
    HOTFIX = "hotfix"


class TestResult(Enum):
    """Test result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class BranchInfo:
    """Information about a Git branch."""
    name: str
    branch_type: BranchType
    description: str
    is_valid: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class CommitInfo:
    """Information about a commit message."""
    message: str
    commit_type: str
    scope: Optional[str]
    description: str
    is_valid: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class DataQualityResult:
    """Result of data quality tests."""
    test_name: str
    status: TestResult
    details: str
    severity: Severity
    recommendation: str = ""


@dataclass
class ModelQualityResult:
    """Result of model quality tests."""
    test_name: str
    status: TestResult
    metric_name: str
    metric_value: float
    threshold: float
    severity: Severity


@dataclass
class PreCommitConfig:
    """Pre-commit configuration."""
    hooks: List[Dict]
    generated_at: str


# ============================================
# GIT WORKFLOW HELPERS
# ============================================

class GitWorkflowHelper:
    """
    Helper for ML Git workflows.

    Provides branch naming, commit message formatting,
    and workflow validation.
    """

    BRANCH_PATTERNS = {
        BranchType.FEATURE: r"^feature/[a-z0-9-]+$",
        BranchType.FIX: r"^fix/[a-z0-9-]+$",
        BranchType.EXPERIMENT: r"^(experiment|exp)/[a-z0-9-]+$",
        BranchType.MODEL: r"^model/[a-z0-9-]+$",
        BranchType.DATA: r"^data/[a-z0-9-]+$",
        BranchType.HOTFIX: r"^hotfix/[a-z0-9-]+$",
    }

    COMMIT_TYPES = {
        "feat": "New feature",
        "fix": "Bug fix",
        "exp": "Experiment (ML-specific)",
        "data": "Data changes (ML-specific)",
        "model": "Model changes (ML-specific)",
        "perf": "Performance improvement",
        "refactor": "Code refactoring",
        "test": "Adding/updating tests",
        "docs": "Documentation",
        "chore": "Maintenance",
        "ci": "CI/CD changes",
    }

    def __init__(self):
        self.validated_branches: List[BranchInfo] = []
        self.validated_commits: List[CommitInfo] = []

    def suggest_branch_name(
        self,
        branch_type: BranchType,
        description: str
    ) -> str:
        """
        Suggest a properly formatted branch name.

        Args:
            branch_type: Type of branch (feature, experiment, etc.)
            description: Human-readable description

        Returns:
            Properly formatted branch name
        """
        # Convert description to kebab-case
        clean = description.lower()
        clean = re.sub(r'[^a-z0-9\s-]', '', clean)
        clean = re.sub(r'\s+', '-', clean)
        clean = re.sub(r'-+', '-', clean)
        clean = clean.strip('-')

        prefix = branch_type.value
        if branch_type == BranchType.EXPERIMENT:
            prefix = "exp"  # Short form

        return f"{prefix}/{clean}"

    def validate_branch_name(self, branch_name: str) -> BranchInfo:
        """Validate a branch name against ML conventions."""
        issues = []
        detected_type = None

        # Check against patterns
        for branch_type, pattern in self.BRANCH_PATTERNS.items():
            if re.match(pattern, branch_name):
                detected_type = branch_type
                break

        if detected_type is None:
            issues.append("Branch name doesn't match any known pattern")

            # Try to detect issues
            if not "/" in branch_name:
                issues.append("Missing branch type prefix (e.g., feature/, exp/)")

            if branch_name != branch_name.lower():
                issues.append("Branch names should be lowercase")

            if " " in branch_name:
                issues.append("Branch names should not contain spaces")

            if re.search(r'[^a-z0-9/-]', branch_name):
                issues.append("Branch names should only contain letters, numbers, and hyphens")

        # Extract description
        parts = branch_name.split("/", 1)
        description = parts[1] if len(parts) > 1 else branch_name

        result = BranchInfo(
            name=branch_name,
            branch_type=detected_type or BranchType.FEATURE,
            description=description,
            is_valid=len(issues) == 0,
            issues=issues
        )

        self.validated_branches.append(result)
        return result

    def format_commit_message(
        self,
        commit_type: str,
        description: str,
        scope: Optional[str] = None,
        body: Optional[str] = None,
        experiment_info: Optional[Dict] = None
    ) -> str:
        """
        Format a commit message following conventions.

        Args:
            commit_type: Type of commit (feat, fix, exp, etc.)
            description: Short description
            scope: Optional scope (e.g., model, data)
            body: Optional longer description
            experiment_info: Optional experiment details for exp commits

        Returns:
            Formatted commit message
        """
        # Header
        if scope:
            header = f"{commit_type}({scope}): {description}"
        else:
            header = f"{commit_type}: {description}"

        message = header

        # Body
        if body:
            message += f"\n\n{body}"

        # Experiment info
        if experiment_info and commit_type == "exp":
            exp_section = "\n\nExperiment Details:"
            exp_section += f"\n- Hypothesis: {experiment_info.get('hypothesis', 'N/A')}"
            exp_section += f"\n- Result: {experiment_info.get('result', 'N/A')}"

            if "metrics" in experiment_info:
                exp_section += "\n\nMetrics:"
                for metric, value in experiment_info["metrics"].items():
                    exp_section += f"\n- {metric}: {value}"

            message += exp_section

        return message

    def validate_commit_message(self, message: str) -> CommitInfo:
        """Validate a commit message against conventions."""
        issues = []
        lines = message.strip().split("\n")
        header = lines[0]

        # Parse header
        commit_type = ""
        scope = None
        description = ""

        # Check format: type(scope): description or type: description
        match = re.match(r'^(\w+)(?:\(([^)]+)\))?: (.+)$', header)

        if match:
            commit_type = match.group(1)
            scope = match.group(2)
            description = match.group(3)

            if commit_type not in self.COMMIT_TYPES:
                issues.append(f"Unknown commit type: {commit_type}")
                issues.append(f"Valid types: {', '.join(self.COMMIT_TYPES.keys())}")
        else:
            issues.append("Commit message doesn't follow format: type: description")

        # Check header length
        if len(header) > 72:
            issues.append(f"Header too long ({len(header)} chars, max 72)")

        # Check description starts with lowercase
        if description and description[0].isupper():
            issues.append("Description should start with lowercase")

        # Check for period at end
        if description and description.endswith("."):
            issues.append("Description should not end with period")

        result = CommitInfo(
            message=message,
            commit_type=commit_type,
            scope=scope,
            description=description,
            is_valid=len(issues) == 0,
            issues=issues
        )

        self.validated_commits.append(result)
        return result

    def generate_experiment_commit(
        self,
        experiment_name: str,
        hypothesis: str,
        result: str,
        metrics: Dict[str, float]
    ) -> str:
        """Generate a well-formatted experiment commit message."""
        return self.format_commit_message(
            commit_type="exp",
            description=experiment_name,
            experiment_info={
                "hypothesis": hypothesis,
                "result": result,
                "metrics": metrics
            }
        )


# ============================================
# PRE-COMMIT CONFIGURATION
# ============================================

class PreCommitGenerator:
    """
    Generate pre-commit configurations for ML projects.
    """

    def __init__(self):
        self.hooks: List[Dict] = []

    def generate_config(
        self,
        include_formatting: bool = True,
        include_linting: bool = True,
        include_security: bool = True,
        include_ml_specific: bool = True,
        include_notebook: bool = True
    ) -> PreCommitConfig:
        """
        Generate a complete pre-commit configuration.

        Args:
            include_formatting: Include Black, isort
            include_linting: Include flake8, mypy
            include_security: Include bandit, secrets detection
            include_ml_specific: Include ML-specific hooks
            include_notebook: Include notebook cleaning

        Returns:
            PreCommitConfig with hooks list
        """
        repos = []

        # Basic hooks
        repos.append({
            "repo": "https://github.com/pre-commit/pre-commit-hooks",
            "rev": "v4.5.0",
            "hooks": [
                {"id": "trailing-whitespace"},
                {"id": "end-of-file-fixer"},
                {"id": "check-yaml"},
                {"id": "check-json"},
                {"id": "check-added-large-files", "args": ["--maxkb=1000"]},
                {"id": "detect-private-key"},
                {"id": "check-merge-conflict"},
            ]
        })

        if include_formatting:
            repos.append({
                "repo": "https://github.com/psf/black",
                "rev": "24.3.0",
                "hooks": [{"id": "black", "language_version": "python3.10"}]
            })
            repos.append({
                "repo": "https://github.com/pycqa/isort",
                "rev": "5.13.2",
                "hooks": [{"id": "isort", "args": ["--profile", "black"]}]
            })

        if include_linting:
            repos.append({
                "repo": "https://github.com/pycqa/flake8",
                "rev": "7.0.0",
                "hooks": [{"id": "flake8", "args": ["--max-line-length=100"]}]
            })
            repos.append({
                "repo": "https://github.com/pre-commit/mirrors-mypy",
                "rev": "v1.8.0",
                "hooks": [{
                    "id": "mypy",
                    "additional_dependencies": ["types-requests", "numpy"]
                }]
            })

        if include_security:
            repos.append({
                "repo": "https://github.com/PyCQA/bandit",
                "rev": "1.7.7",
                "hooks": [{
                    "id": "bandit",
                    "args": ["-r", "src/"],
                    "exclude": "tests/"
                }]
            })

        if include_notebook:
            repos.append({
                "repo": "https://github.com/kynan/nbstripout",
                "rev": "0.7.1",
                "hooks": [{"id": "nbstripout"}]
            })

        if include_ml_specific:
            repos.append({
                "repo": "local",
                "hooks": [
                    {
                        "id": "check-no-secrets-in-config",
                        "name": "Check no secrets in config",
                        "entry": "python scripts/check_secrets.py",
                        "language": "python",
                        "files": r"\.(yaml|yml|json|ini|env)$"
                    },
                    {
                        "id": "validate-model-config",
                        "name": "Validate model config",
                        "entry": "python scripts/validate_config.py",
                        "language": "python",
                        "files": r"configs/.*\.(yaml|yml)$"
                    },
                    {
                        "id": "check-data-not-committed",
                        "name": "Check large data files",
                        "entry": "python scripts/check_large_files.py",
                        "language": "python",
                        "types": ["file"]
                    }
                ]
            })

        return PreCommitConfig(
            hooks=repos,
            generated_at=datetime.now().isoformat()
        )

    def to_yaml(self, config: PreCommitConfig) -> str:
        """Convert config to YAML format."""
        lines = ["repos:"]

        for repo in config.hooks:
            lines.append(f"  - repo: {repo['repo']}")
            if "rev" in repo:
                lines.append(f"    rev: {repo['rev']}")
            lines.append("    hooks:")

            for hook in repo["hooks"]:
                lines.append(f"      - id: {hook['id']}")
                for key, value in hook.items():
                    if key != "id":
                        if isinstance(value, list):
                            lines.append(f"        {key}:")
                            for item in value:
                                lines.append(f"          - {item}")
                        else:
                            lines.append(f"        {key}: {value}")

        return "\n".join(lines)


# ============================================
# DATA QUALITY TESTING
# ============================================

class DataQualityTester:
    """
    Test data quality for ML projects.
    """

    def __init__(self):
        self.results: List[DataQualityResult] = []

    def test_no_missing_values(
        self,
        data: Dict[str, List],
        critical_columns: List[str]
    ) -> DataQualityResult:
        """Test that critical columns have no missing values."""
        missing_counts = {}

        for col in critical_columns:
            if col in data:
                missing = sum(1 for v in data[col] if v is None or v == "")
                if missing > 0:
                    missing_counts[col] = missing

        if missing_counts:
            details = ", ".join(f"{k}: {v}" for k, v in missing_counts.items())
            result = DataQualityResult(
                test_name="No Missing Values",
                status=TestResult.FAILED,
                details=f"Missing values found: {details}",
                severity=Severity.CRITICAL,
                recommendation="Fill or remove rows with missing values in critical columns"
            )
        else:
            result = DataQualityResult(
                test_name="No Missing Values",
                status=TestResult.PASSED,
                details=f"All {len(critical_columns)} critical columns complete",
                severity=Severity.INFO
            )

        self.results.append(result)
        return result

    def test_label_distribution(
        self,
        labels: List[Any],
        max_imbalance_ratio: float = 3.0
    ) -> DataQualityResult:
        """Test that labels are reasonably balanced."""
        from collections import Counter

        counts = Counter(labels)
        if len(counts) < 2:
            result = DataQualityResult(
                test_name="Label Distribution",
                status=TestResult.WARNING,
                details="Only one label class found",
                severity=Severity.HIGH,
                recommendation="Verify data contains multiple classes"
            )
        else:
            max_count = max(counts.values())
            min_count = min(counts.values())
            ratio = max_count / min_count if min_count > 0 else float('inf')

            if ratio > max_imbalance_ratio:
                result = DataQualityResult(
                    test_name="Label Distribution",
                    status=TestResult.WARNING,
                    details=f"Imbalance ratio {ratio:.1f}:1 exceeds threshold {max_imbalance_ratio}:1",
                    severity=Severity.MEDIUM,
                    recommendation="Consider oversampling, undersampling, or class weights"
                )
            else:
                result = DataQualityResult(
                    test_name="Label Distribution",
                    status=TestResult.PASSED,
                    details=f"Imbalance ratio {ratio:.1f}:1 within threshold",
                    severity=Severity.INFO
                )

        self.results.append(result)
        return result

    def test_no_duplicates(
        self,
        data: Dict[str, List],
        key_columns: List[str]
    ) -> DataQualityResult:
        """Test that there are no duplicate rows based on key columns."""
        if not key_columns or not all(c in data for c in key_columns):
            result = DataQualityResult(
                test_name="No Duplicates",
                status=TestResult.SKIPPED,
                details="Key columns not found in data",
                severity=Severity.INFO
            )
            self.results.append(result)
            return result

        n_rows = len(data[key_columns[0]])
        seen = set()
        duplicates = 0

        for i in range(n_rows):
            key = tuple(data[col][i] for col in key_columns)
            if key in seen:
                duplicates += 1
            seen.add(key)

        if duplicates > 0:
            result = DataQualityResult(
                test_name="No Duplicates",
                status=TestResult.FAILED,
                details=f"Found {duplicates} duplicate rows",
                severity=Severity.HIGH,
                recommendation="Remove or investigate duplicate rows"
            )
        else:
            result = DataQualityResult(
                test_name="No Duplicates",
                status=TestResult.PASSED,
                details=f"No duplicates found in {n_rows} rows",
                severity=Severity.INFO
            )

        self.results.append(result)
        return result

    def test_value_ranges(
        self,
        data: Dict[str, List],
        ranges: Dict[str, Tuple[float, float]]
    ) -> DataQualityResult:
        """Test that values are within expected ranges."""
        violations = {}

        for col, (min_val, max_val) in ranges.items():
            if col not in data:
                continue

            out_of_range = sum(
                1 for v in data[col]
                if v is not None and (v < min_val or v > max_val)
            )

            if out_of_range > 0:
                violations[col] = out_of_range

        if violations:
            details = ", ".join(f"{k}: {v} violations" for k, v in violations.items())
            result = DataQualityResult(
                test_name="Value Ranges",
                status=TestResult.FAILED,
                details=f"Out of range values: {details}",
                severity=Severity.HIGH,
                recommendation="Clip, transform, or investigate out-of-range values"
            )
        else:
            result = DataQualityResult(
                test_name="Value Ranges",
                status=TestResult.PASSED,
                details=f"All values within expected ranges",
                severity=Severity.INFO
            )

        self.results.append(result)
        return result

    def test_no_data_leakage(
        self,
        train_ids: List[Any],
        test_ids: List[Any]
    ) -> DataQualityResult:
        """Test that train and test sets don't overlap."""
        train_set = set(train_ids)
        test_set = set(test_ids)
        overlap = train_set & test_set

        if overlap:
            result = DataQualityResult(
                test_name="No Data Leakage",
                status=TestResult.FAILED,
                details=f"Found {len(overlap)} IDs in both train and test sets",
                severity=Severity.CRITICAL,
                recommendation="Remove overlapping samples from one of the sets"
            )
        else:
            result = DataQualityResult(
                test_name="No Data Leakage",
                status=TestResult.PASSED,
                details="No overlap between train and test sets",
                severity=Severity.INFO
            )

        self.results.append(result)
        return result

    def get_summary(self) -> Dict:
        """Get summary of all test results."""
        return {
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.status == TestResult.PASSED),
            "failed": sum(1 for r in self.results if r.status == TestResult.FAILED),
            "warnings": sum(1 for r in self.results if r.status == TestResult.WARNING),
            "skipped": sum(1 for r in self.results if r.status == TestResult.SKIPPED),
        }


# ============================================
# MODEL QUALITY TESTING
# ============================================

class ModelQualityTester:
    """
    Test model quality for ML projects.
    """

    def __init__(self):
        self.results: List[ModelQualityResult] = []

    def test_accuracy_threshold(
        self,
        y_true: List,
        y_pred: List,
        threshold: float = 0.8
    ) -> ModelQualityResult:
        """Test that accuracy meets minimum threshold."""
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        accuracy = correct / len(y_true) if y_true else 0

        result = ModelQualityResult(
            test_name="Accuracy Threshold",
            status=TestResult.PASSED if accuracy >= threshold else TestResult.FAILED,
            metric_name="accuracy",
            metric_value=accuracy,
            threshold=threshold,
            severity=Severity.CRITICAL if accuracy < threshold else Severity.INFO
        )

        self.results.append(result)
        return result

    def test_no_class_collapse(
        self,
        y_pred: List,
        min_classes: int = 2
    ) -> ModelQualityResult:
        """Test that model predicts multiple classes."""
        unique_preds = set(y_pred)
        n_classes = len(unique_preds)

        result = ModelQualityResult(
            test_name="No Class Collapse",
            status=TestResult.PASSED if n_classes >= min_classes else TestResult.FAILED,
            metric_name="unique_predictions",
            metric_value=float(n_classes),
            threshold=float(min_classes),
            severity=Severity.HIGH if n_classes < min_classes else Severity.INFO
        )

        self.results.append(result)
        return result

    def test_prediction_variance(
        self,
        predictions: List[float],
        min_variance: float = 0.01
    ) -> ModelQualityResult:
        """Test that predictions have sufficient variance."""
        if not predictions:
            result = ModelQualityResult(
                test_name="Prediction Variance",
                status=TestResult.SKIPPED,
                metric_name="variance",
                metric_value=0.0,
                threshold=min_variance,
                severity=Severity.INFO
            )
            self.results.append(result)
            return result

        mean = sum(predictions) / len(predictions)
        variance = sum((p - mean) ** 2 for p in predictions) / len(predictions)

        result = ModelQualityResult(
            test_name="Prediction Variance",
            status=TestResult.PASSED if variance >= min_variance else TestResult.WARNING,
            metric_name="variance",
            metric_value=variance,
            threshold=min_variance,
            severity=Severity.MEDIUM if variance < min_variance else Severity.INFO
        )

        self.results.append(result)
        return result

    def test_latency_threshold(
        self,
        latencies_ms: List[float],
        max_p99_ms: float = 100
    ) -> ModelQualityResult:
        """Test that inference latency meets requirements."""
        sorted_latencies = sorted(latencies_ms)
        p99_idx = int(len(sorted_latencies) * 0.99)
        p99 = sorted_latencies[p99_idx] if sorted_latencies else 0

        result = ModelQualityResult(
            test_name="Latency P99",
            status=TestResult.PASSED if p99 <= max_p99_ms else TestResult.WARNING,
            metric_name="p99_latency_ms",
            metric_value=p99,
            threshold=max_p99_ms,
            severity=Severity.MEDIUM if p99 > max_p99_ms else Severity.INFO
        )

        self.results.append(result)
        return result

    def test_no_regression(
        self,
        current_accuracy: float,
        baseline_accuracy: float,
        tolerance: float = 0.01
    ) -> ModelQualityResult:
        """Test that new model doesn't regress vs baseline."""
        min_acceptable = baseline_accuracy - tolerance

        result = ModelQualityResult(
            test_name="No Regression",
            status=TestResult.PASSED if current_accuracy >= min_acceptable else TestResult.FAILED,
            metric_name="accuracy_vs_baseline",
            metric_value=current_accuracy,
            threshold=min_acceptable,
            severity=Severity.CRITICAL if current_accuracy < min_acceptable else Severity.INFO
        )

        self.results.append(result)
        return result

    def get_summary(self) -> Dict:
        """Get summary of all test results."""
        return {
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.status == TestResult.PASSED),
            "failed": sum(1 for r in self.results if r.status == TestResult.FAILED),
            "warnings": sum(1 for r in self.results if r.status == TestResult.WARNING),
        }


# ============================================
# PROJECT TEMPLATE GENERATOR
# ============================================

class ProjectTemplateGenerator:
    """
    Generate ML project templates.
    """

    def __init__(self):
        self.structure: Dict = {}

    def generate_structure(self, project_name: str) -> Dict:
        """Generate standard ML project structure."""
        self.structure = {
            project_name: {
                ".github": {
                    "workflows": {
                        "ci.yml": "# CI pipeline",
                        "train.yml": "# Training pipeline",
                    }
                },
                "configs": {
                    "model": {
                        "base.yaml": self._model_config(),
                    },
                    "training": {
                        "default.yaml": self._training_config(),
                    }
                },
                "data": {
                    "raw": {".gitkeep": ""},
                    "processed": {".gitkeep": ""},
                    ".gitignore": "*.csv\n*.parquet\n*.pkl\n!.gitkeep",
                },
                "models": {
                    "checkpoints": {".gitkeep": ""},
                    ".gitignore": "*.pkl\n*.pt\n*.h5\n!.gitkeep",
                },
                "notebooks": {
                    "exploration": {".gitkeep": ""},
                    "experiments": {".gitkeep": ""},
                },
                "src": {
                    "__init__.py": "",
                    "data": {
                        "__init__.py": "",
                        "load.py": self._data_loader(),
                        "preprocess.py": self._preprocessor(),
                    },
                    "models": {
                        "__init__.py": "",
                        "train.py": self._trainer(),
                        "evaluate.py": self._evaluator(),
                    },
                    "utils": {
                        "__init__.py": "",
                        "config.py": self._config_loader(),
                    }
                },
                "tests": {
                    "__init__.py": "",
                    "test_data.py": self._test_data(),
                    "test_model.py": self._test_model(),
                },
                "scripts": {
                    "train.py": self._train_script(),
                    "evaluate.py": self._eval_script(),
                },
                ".pre-commit-config.yaml": self._precommit_config(),
                "pyproject.toml": self._pyproject(),
                "requirements.txt": self._requirements(),
                "requirements-dev.txt": self._requirements_dev(),
                "Makefile": self._makefile(),
                "README.md": self._readme(project_name),
                ".gitignore": self._gitignore(),
            }
        }
        return self.structure

    def _model_config(self) -> str:
        return """# Model configuration
model:
  name: my_model
  version: v1.0.0
  architecture: transformer

parameters:
  hidden_size: 768
  num_layers: 12
  dropout: 0.1
"""

    def _training_config(self) -> str:
        return """# Training configuration
training:
  batch_size: 32
  learning_rate: 0.001
  epochs: 10
  early_stopping_patience: 3

data:
  train_path: data/processed/train.csv
  val_path: data/processed/val.csv

logging:
  experiment_name: baseline
  log_every_n_steps: 100
"""

    def _data_loader(self) -> str:
        return '''"""Data loading utilities."""

def load_data(path: str):
    """Load data from path."""
    # Implementation here
    pass
'''

    def _preprocessor(self) -> str:
        return '''"""Data preprocessing utilities."""

def preprocess(data):
    """Preprocess data."""
    # Implementation here
    pass
'''

    def _trainer(self) -> str:
        return '''"""Model training utilities."""

def train(model, data, config):
    """Train model."""
    # Implementation here
    pass
'''

    def _evaluator(self) -> str:
        return '''"""Model evaluation utilities."""

def evaluate(model, data):
    """Evaluate model."""
    # Implementation here
    pass
'''

    def _config_loader(self) -> str:
        return '''"""Configuration loading utilities."""
import yaml

def load_config(path: str) -> dict:
    """Load YAML configuration."""
    with open(path) as f:
        return yaml.safe_load(f)
'''

    def _test_data(self) -> str:
        return '''"""Data quality tests."""
import pytest

def test_no_missing_values():
    """Test that data has no missing values."""
    pass

def test_label_distribution():
    """Test label distribution is balanced."""
    pass
'''

    def _test_model(self) -> str:
        return '''"""Model quality tests."""
import pytest

def test_accuracy_threshold():
    """Test model accuracy meets threshold."""
    pass

def test_no_regression():
    """Test model doesn't regress vs baseline."""
    pass
'''

    def _train_script(self) -> str:
        return '''#!/usr/bin/env python3
"""Training entry point."""
import argparse
from src.utils.config import load_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training/default.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    # Training logic here
    print(f"Training with config: {args.config}")

if __name__ == "__main__":
    main()
'''

    def _eval_script(self) -> str:
        return '''#!/usr/bin/env python3
"""Evaluation entry point."""
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    args = parser.parse_args()

    # Evaluation logic here
    print(f"Evaluating model: {args.model}")

if __name__ == "__main__":
    main()
'''

    def _precommit_config(self) -> str:
        return """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
"""

    def _pyproject(self) -> str:
        return """[project]
name = "ml-project"
version = "0.1.0"
requires-python = ">=3.10"

[tool.black]
line-length = 100

[tool.isort]
profile = "black"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

    def _requirements(self) -> str:
        return """numpy>=1.21.0
pandas>=1.5.0
scikit-learn>=1.0.0
pyyaml>=6.0
"""

    def _requirements_dev(self) -> str:
        return """pytest>=7.0.0
black>=24.0.0
isort>=5.13.0
flake8>=7.0.0
pre-commit>=3.6.0
"""

    def _makefile(self) -> str:
        return """.PHONY: install test lint train

install:
\tpip install -r requirements.txt
\tpip install -r requirements-dev.txt
\tpre-commit install

test:
\tpytest tests/ -v

lint:
\tblack src/ tests/
\tisort src/ tests/
\tflake8 src/ tests/

train:
\tpython scripts/train.py
"""

    def _readme(self, project_name: str) -> str:
        return f"""# {project_name}

## Setup

```bash
make install
```

## Training

```bash
make train
```

## Testing

```bash
make test
```
"""

    def _gitignore(self) -> str:
        return """# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/

# Virtual environments
venv/
.env

# IDE
.idea/
.vscode/
*.swp

# Data and models (tracked by DVC)
*.csv
*.pkl
*.pt
*.h5

# OS
.DS_Store
"""

    def print_structure(self, structure: Dict = None, indent: int = 0) -> str:
        """Print project structure as tree."""
        if structure is None:
            structure = self.structure

        lines = []
        for name, content in structure.items():
            prefix = "  " * indent
            if isinstance(content, dict):
                lines.append(f"{prefix}{name}/")
                lines.append(self.print_structure(content, indent + 1))
            else:
                lines.append(f"{prefix}{name}")

        return "\n".join(lines)


# ============================================
# DEMO FUNCTIONS
# ============================================

def demo_1_git_workflow():
    """Demo 1: Git Workflow Helper"""
    print("=" * 70)
    print("DEMO 1: GIT WORKFLOW HELPER")
    print("=" * 70)

    helper = GitWorkflowHelper()

    # Branch name suggestions
    print("\n📝 Branch Name Suggestions:")
    print("-" * 40)

    examples = [
        (BranchType.EXPERIMENT, "test BERT large model"),
        (BranchType.FEATURE, "Add streaming inference"),
        (BranchType.FIX, "Memory leak in batch processing"),
        (BranchType.DATA, "Incorporate Q4 feedback"),
        (BranchType.MODEL, "Improved embeddings v3"),
    ]

    for branch_type, desc in examples:
        suggested = helper.suggest_branch_name(branch_type, desc)
        print(f"   {branch_type.value:12} + '{desc}'")
        print(f"   → {suggested}\n")

    # Branch validation
    print("\n🔍 Branch Name Validation:")
    print("-" * 40)

    test_branches = [
        "feature/add-preprocessing",
        "exp/bert-large-v2",
        "test",
        "My Feature",
        "experiment/test_underscore",
    ]

    for branch in test_branches:
        result = helper.validate_branch_name(branch)
        status = "✅" if result.is_valid else "❌"
        print(f"\n   {status} '{branch}'")
        if result.issues:
            for issue in result.issues:
                print(f"      • {issue}")

    # Commit message formatting
    print("\n📝 Commit Message Formatting:")
    print("-" * 40)

    # Standard commit
    msg = helper.format_commit_message(
        commit_type="feat",
        description="add streaming support for inference API",
        scope="api"
    )
    print(f"\n   Standard commit:\n   {msg}")

    # Experiment commit
    exp_msg = helper.generate_experiment_commit(
        experiment_name="BERT-large with attention fix",
        hypothesis="Fixing attention dropout will improve accuracy",
        result="Accuracy improved from 0.85 to 0.89",
        metrics={"accuracy": 0.89, "f1": 0.87, "latency_ms": 45}
    )
    print(f"\n   Experiment commit:\n{exp_msg}")

    # Commit validation
    print("\n🔍 Commit Message Validation:")
    print("-" * 40)

    test_commits = [
        "feat: add new feature",
        "exp: test BERT large model",
        "Fixed stuff",
        "feat: Add new feature.",  # Uppercase + period
    ]

    for commit in test_commits:
        result = helper.validate_commit_message(commit)
        status = "✅" if result.is_valid else "❌"
        print(f"\n   {status} '{commit}'")
        if result.issues:
            for issue in result.issues:
                print(f"      • {issue}")

    print("\n✅ Demo 1 complete!")


def demo_2_precommit_setup():
    """Demo 2: Pre-commit Configuration"""
    print("=" * 70)
    print("DEMO 2: PRE-COMMIT CONFIGURATION GENERATOR")
    print("=" * 70)

    generator = PreCommitGenerator()

    # Generate full config
    print("\n📝 Generating Full Pre-commit Config...")
    print("-" * 40)

    config = generator.generate_config(
        include_formatting=True,
        include_linting=True,
        include_security=True,
        include_ml_specific=True,
        include_notebook=True
    )

    yaml_output = generator.to_yaml(config)

    print(f"\n   Generated at: {config.generated_at}")
    print(f"   Total repos: {len(config.hooks)}")
    print(f"   Total hooks: {sum(len(r['hooks']) for r in config.hooks)}")

    print("\n📄 Generated .pre-commit-config.yaml:")
    print("-" * 40)
    # Print first 50 lines
    lines = yaml_output.split("\n")[:50]
    for line in lines:
        print(f"   {line}")
    if len(yaml_output.split("\n")) > 50:
        print(f"   ... ({len(yaml_output.split(chr(10))) - 50} more lines)")

    # Minimal config
    print("\n📝 Generating Minimal Config (formatting only)...")
    print("-" * 40)

    minimal = generator.generate_config(
        include_formatting=True,
        include_linting=False,
        include_security=False,
        include_ml_specific=False,
        include_notebook=False
    )

    print(f"   Repos: {len(minimal.hooks)}")
    print(f"   Hooks: {sum(len(r['hooks']) for r in minimal.hooks)}")

    print("\n✅ Demo 2 complete!")


def demo_3_data_quality():
    """Demo 3: Data Quality Testing"""
    print("=" * 70)
    print("DEMO 3: DATA QUALITY TESTING")
    print("=" * 70)

    tester = DataQualityTester()

    # Simulate dataset
    print("\n📊 Simulating Dataset...")
    print("-" * 40)

    data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "text": ["sample1", "sample2", None, "sample4", "sample5",
                 "sample6", "sample7", "sample8", "sample9", "sample10"],
        "label": [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],  # Imbalanced
        "age": [25, 30, 35, 150, 28, 32, 45, 50, 22, 38],  # 150 out of range
        "score": [0.5, 0.8, 0.3, 0.9, 0.7, 0.6, 0.4, 0.85, 0.55, 0.75],
    }

    train_ids = [1, 2, 3, 4, 5, 6, 7]
    test_ids = [7, 8, 9, 10]  # ID 7 in both! Leakage!

    print(f"   Rows: {len(data['id'])}")
    print(f"   Columns: {list(data.keys())}")

    # Run tests
    print("\n🔍 Running Data Quality Tests...")
    print("-" * 40)

    # Test 1: Missing values
    result = tester.test_no_missing_values(data, ["id", "text", "label"])
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      {result.details}")
    if result.recommendation:
        print(f"      → {result.recommendation}")

    # Test 2: Label distribution
    result = tester.test_label_distribution(data["label"], max_imbalance_ratio=2.0)
    status = "✅" if result.status == TestResult.PASSED else "⚠️" if result.status == TestResult.WARNING else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      {result.details}")
    if result.recommendation:
        print(f"      → {result.recommendation}")

    # Test 3: Duplicates
    result = tester.test_no_duplicates(data, ["id"])
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      {result.details}")

    # Test 4: Value ranges
    result = tester.test_value_ranges(data, {"age": (0, 120), "score": (0, 1)})
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      {result.details}")
    if result.recommendation:
        print(f"      → {result.recommendation}")

    # Test 5: Data leakage
    result = tester.test_no_data_leakage(train_ids, test_ids)
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      {result.details}")
    if result.recommendation:
        print(f"      → {result.recommendation}")

    # Summary
    summary = tester.get_summary()
    print("\n📊 Summary:")
    print(f"   Total: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Warnings: {summary['warnings']}")

    print("\n✅ Demo 3 complete!")


def demo_4_model_quality():
    """Demo 4: Model Quality Testing"""
    print("=" * 70)
    print("DEMO 4: MODEL QUALITY TESTING")
    print("=" * 70)

    tester = ModelQualityTester()

    # Simulate predictions
    print("\n📊 Simulating Model Predictions...")
    print("-" * 40)

    y_true = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1] * 10  # 100 samples
    y_pred = [0, 1, 0, 1, 0, 0, 0, 1, 0, 1] * 10  # 90% accuracy

    latencies = [random.uniform(20, 80) for _ in range(100)]
    latencies.append(150)  # One slow request

    print(f"   Samples: {len(y_true)}")
    print(f"   Classes: {set(y_true)}")

    # Run tests
    print("\n🔍 Running Model Quality Tests...")
    print("-" * 40)

    # Test 1: Accuracy threshold
    result = tester.test_accuracy_threshold(y_true, y_pred, threshold=0.85)
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      {result.metric_name}: {result.metric_value:.1%} (threshold: {result.threshold:.1%})")

    # Test 2: No class collapse
    result = tester.test_no_class_collapse(y_pred, min_classes=2)
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      Unique predictions: {int(result.metric_value)} (min: {int(result.threshold)})")

    # Test 3: Prediction variance
    predictions = [random.uniform(0.3, 0.7) for _ in range(100)]
    result = tester.test_prediction_variance(predictions, min_variance=0.01)
    status = "✅" if result.status == TestResult.PASSED else "⚠️"
    print(f"\n   {status} {result.test_name}")
    print(f"      Variance: {result.metric_value:.4f} (min: {result.threshold})")

    # Test 4: Latency
    result = tester.test_latency_threshold(latencies, max_p99_ms=100)
    status = "✅" if result.status == TestResult.PASSED else "⚠️"
    print(f"\n   {status} {result.test_name}")
    print(f"      P99 latency: {result.metric_value:.1f}ms (max: {result.threshold}ms)")

    # Test 5: No regression
    current_accuracy = 0.90
    baseline_accuracy = 0.88
    result = tester.test_no_regression(current_accuracy, baseline_accuracy, tolerance=0.01)
    status = "✅" if result.status == TestResult.PASSED else "❌"
    print(f"\n   {status} {result.test_name}")
    print(f"      Current: {result.metric_value:.1%} vs Baseline: {baseline_accuracy:.1%}")

    # Summary
    summary = tester.get_summary()
    print("\n📊 Summary:")
    print(f"   Total: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Warnings: {summary['warnings']}")

    print("\n✅ Demo 4 complete!")


def demo_5_project_template():
    """Demo 5: Project Template Generator"""
    print("=" * 70)
    print("DEMO 5: PROJECT TEMPLATE GENERATOR")
    print("=" * 70)

    generator = ProjectTemplateGenerator()

    # Generate structure
    print("\n📁 Generating ML Project Structure...")
    print("-" * 40)

    structure = generator.generate_structure("my_ml_project")

    # Print tree
    print("\n   Project Structure:")
    tree = generator.print_structure()
    for line in tree.split("\n")[:40]:  # First 40 lines
        print(f"   {line}")
    if len(tree.split("\n")) > 40:
        print(f"   ... ({len(tree.split(chr(10))) - 40} more items)")

    # Show key files
    print("\n📄 Key Configuration Files:")
    print("-" * 40)

    print("\n   Makefile:")
    makefile = generator._makefile()
    for line in makefile.split("\n")[:10]:
        print(f"   {line}")

    print("\n   requirements.txt:")
    reqs = generator._requirements()
    for line in reqs.split("\n"):
        print(f"   {line}")

    print("\n   pyproject.toml:")
    pyproject = generator._pyproject()
    for line in pyproject.split("\n")[:15]:
        print(f"   {line}")

    print("\n📋 Template Includes:")
    print("-" * 40)
    print("   ✅ GitHub Actions workflows (CI, training)")
    print("   ✅ Model and training configs (YAML)")
    print("   ✅ Source code structure (src/)")
    print("   ✅ Test framework (tests/)")
    print("   ✅ Pre-commit configuration")
    print("   ✅ Makefile for common commands")
    print("   ✅ Proper .gitignore for ML projects")

    print("\n✅ Demo 5 complete!")


def print_usage():
    """Print usage instructions."""
    print("""
ML DevOps Toolkit - Module 43 Deliverable
==========================================

Usage:
    python deliverable_ml_devops_toolkit.py <command>

Commands:
    demo1   - Git Workflow Helper
              Branch naming, commit formatting, validation

    demo2   - Pre-commit Configuration
              Generate .pre-commit-config.yaml for ML projects

    demo3   - Data Quality Testing
              Test for missing values, imbalance, leakage

    demo4   - Model Quality Testing
              Test accuracy, latency, regression

    demo5   - Project Template Generator
              Generate complete ML project structure

Examples:
    python deliverable_ml_devops_toolkit.py demo1
    python deliverable_ml_devops_toolkit.py demo5
    """)


def main():
    """Main entry point."""
    ensure_storage()

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_git_workflow()
    elif command == "demo2":
        demo_2_precommit_setup()
    elif command == "demo3":
        demo_3_data_quality()
    elif command == "demo4":
        demo_4_model_quality()
    elif command == "demo5":
        demo_5_project_template()
    elif command in ["help", "-h", "--help"]:
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
