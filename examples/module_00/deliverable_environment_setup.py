"""
Module 00 Deliverable: Environment Setup Checklist

Quick, scriptable checks to ensure the learner's environment is ready before starting the curriculum.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class EnvCheckResult:
    """Represents a single environment check."""

    name: str
    ok: bool
    detail: str


def check_python_version(min_major: int = 3, min_minor: int = 10) -> EnvCheckResult:
    """Ensure Python meets the minimum version requirement."""
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (min_major, min_minor)
    detail = f"Detected {major}.{minor}, required >= {min_major}.{min_minor}"
    return EnvCheckResult(name="Python version", ok=ok, detail=detail)


def check_virtualenv() -> EnvCheckResult:
    """Detect if a virtual environment is active."""
    in_venv = sys.prefix != sys.base_prefix
    detail = "venv active" if in_venv else "venv not active"
    return EnvCheckResult(name="Virtual environment", ok=in_venv, detail=detail)


def check_repo_structure() -> EnvCheckResult:
    """Confirm the repo layout exists (docs/, examples/, scripts/)."""
    expected = ["docs", "examples", "scripts", "curriculum.yaml"]
    missing = [p for p in expected if not Path(p).exists()]
    ok = not missing
    detail = "All present" if ok else f"Missing: {', '.join(missing)}"
    return EnvCheckResult(name="Repository structure", ok=ok, detail=detail)


def run_checks() -> List[EnvCheckResult]:
    """Run all checks and return their results."""
    return [check_python_version(), check_virtualenv(), check_repo_structure()]


def summary(results: List[EnvCheckResult]) -> Dict[str, int]:
    """Summarize pass/fail counts."""
    passed = sum(1 for r in results if r.ok)
    failed = len(results) - passed
    return {"passed": passed, "failed": failed}


def main() -> None:
    """Execute environment checks and print a quick report."""
    print("🔍 Running environment setup checks...\n")
    results = run_checks()
    for res in results:
        status = "✅" if res.ok else "⚠️"
        print(f"{status} {res.name}: {res.detail}")

    totals = summary(results)
    print(f"\nSummary: {totals['passed']} passed, {totals['failed']} failed")
    print(f"Platform: {platform.system()} {platform.release()}")
    if totals["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
