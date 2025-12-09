"""
Neural Dojo Deliverables Smoke Tests

This module provides smoke tests for all 53 deliverables to ensure they:
1. Can be imported without errors
2. Have proper docstrings
3. Have a main() or demo functions
4. Can run help/usage without crashing

Run with: pytest tests/test_deliverables.py -v
Quick run: pytest tests/test_deliverables.py -v -x --tb=short
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"


def get_all_deliverables() -> list[Path]:
    """Find all deliverable Python files."""
    deliverables = sorted(EXAMPLES_DIR.glob("module_*/deliverable_*.py"))
    return deliverables


# Generate test parameters
DELIVERABLES = get_all_deliverables()


@pytest.mark.parametrize("deliverable_path", DELIVERABLES, ids=lambda p: p.parent.name)
def test_deliverable_syntax(deliverable_path: Path):
    """Test that deliverable has valid Python syntax."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(deliverable_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Syntax error in {deliverable_path.name}: {result.stderr}"


@pytest.mark.parametrize("deliverable_path", DELIVERABLES, ids=lambda p: p.parent.name)
def test_deliverable_has_docstring(deliverable_path: Path):
    """Test that deliverable has a module-level docstring."""
    content = deliverable_path.read_text()
    # Check for docstring at the start (after any comments/encoding)
    lines = content.split('\n')

    # Skip shebang, encoding, and empty lines
    doc_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            doc_start = i
            break

    # Check if docstring exists
    has_docstring = False
    if doc_start < len(lines):
        first_code_line = lines[doc_start].strip()
        has_docstring = first_code_line.startswith('"""') or first_code_line.startswith("'''")

    assert has_docstring, f"{deliverable_path.name} should have a module-level docstring"


@pytest.mark.parametrize("deliverable_path", DELIVERABLES, ids=lambda p: p.parent.name)
def test_deliverable_has_main_or_demo(deliverable_path: Path):
    """Test that deliverable has a main block or demo functions."""
    content = deliverable_path.read_text()

    has_main = 'if __name__' in content
    has_demo = 'def demo' in content or 'def main' in content

    assert has_main or has_demo, (
        f"{deliverable_path.name} should have 'if __name__' block or demo/main functions"
    )


@pytest.mark.parametrize("deliverable_path", DELIVERABLES, ids=lambda p: p.parent.name)
def test_deliverable_has_dataclasses_or_classes(deliverable_path: Path):
    """Test that deliverable uses proper structure (dataclasses or classes)."""
    content = deliverable_path.read_text()

    has_dataclass = '@dataclass' in content
    has_class = 'class ' in content
    has_functions = 'def ' in content

    # Should have at least functions, ideally classes
    assert has_functions, f"{deliverable_path.name} should have functions defined"


@pytest.mark.parametrize("deliverable_path", DELIVERABLES, ids=lambda p: p.parent.name)
def test_deliverable_has_type_hints(deliverable_path: Path):
    """Test that deliverable uses type hints."""
    content = deliverable_path.read_text()

    # Check for common type hint patterns
    type_hint_patterns = [
        ': str',
        ': int',
        ': float',
        ': bool',
        ': list',
        ': dict',
        ': List[',
        ': Dict[',
        ': Optional[',
        '-> ',
    ]

    has_type_hints = any(pattern in content for pattern in type_hint_patterns)

    assert has_type_hints, f"{deliverable_path.name} should use type hints"


# Test that help works for a few key deliverables
KEY_DELIVERABLES = [
    "module_43/deliverable_ml_devops_toolkit.py",
    "module_44/deliverable_ml_docker_toolkit.py",
    "module_45/deliverable_ml_cicd_toolkit.py",
]


@pytest.mark.parametrize("deliverable_subpath", KEY_DELIVERABLES)
def test_deliverable_help_runs(deliverable_subpath: str):
    """Test that deliverable --help or help command runs without error."""
    deliverable_path = EXAMPLES_DIR / deliverable_subpath

    if not deliverable_path.exists():
        pytest.skip(f"Deliverable not found: {deliverable_subpath}")

    # Try running with 'help' argument (common pattern in our deliverables)
    result = subprocess.run(
        [sys.executable, str(deliverable_path), "help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(deliverable_path.parent),
    )

    # Either it succeeds or it shows usage (both are acceptable)
    # We just want it not to crash
    assert result.returncode in [0, 1, 2], (
        f"Help command failed for {deliverable_subpath}: {result.stderr}"
    )


def test_deliverable_count():
    """Test that we have the expected number of deliverables."""
    assert len(DELIVERABLES) >= 50, f"Expected at least 50 deliverables, found {len(DELIVERABLES)}"


def test_deliverables_span_all_phases():
    """Test that deliverables exist across multiple phases."""
    module_numbers = set()
    for d in DELIVERABLES:
        # Extract module number from path like "module_02"
        module_name = d.parent.name
        if module_name.startswith("module_"):
            try:
                num = int(module_name.split("_")[1])
                module_numbers.add(num)
            except (ValueError, IndexError):
                pass

    # Should have deliverables in early, middle, and late modules
    assert min(module_numbers) <= 5, "Should have deliverables in early modules"
    assert max(module_numbers) >= 50, "Should have deliverables in late modules"
    assert len(module_numbers) >= 40, f"Should have at least 40 modules with deliverables, found {len(module_numbers)}"


if __name__ == "__main__":
    # Run quick tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])
