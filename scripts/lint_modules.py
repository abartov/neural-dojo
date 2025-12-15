#!/usr/bin/env python3
"""
Lightweight lint for module examples.

Checks:
- README.md exists per examples/module_XX
- Deliverables have docstring, type hints, and an entrypoint (main/demo or __main__ guard)

Usage:
  python scripts/lint_modules.py
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"

TYPE_HINT_PATTERNS = [
    ": str",
    ": int",
    ": float",
    ": bool",
    ": list",
    ": dict",
    ": List[",
    ": Dict[",
    ": Optional[",
    "-> ",
]


def has_docstring(content: str) -> bool:
    """Return True if the first code line is a docstring."""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#!"):
            continue
        if stripped.startswith("#"):
            continue
        return stripped.startswith('"""') or stripped.startswith("'''")
    return False


def has_entrypoint(content: str) -> bool:
    """Check for a main/demo function or __main__ guard."""
    return ("if __name__" in content) or ("def main" in content) or ("def demo" in content)


def has_type_hints(content: str) -> bool:
    """Check for common type hint patterns."""
    return any(pattern in content for pattern in TYPE_HINT_PATTERNS)


def lint_module(module_dir: Path) -> list[str]:
    """Collect issues for a single module directory."""
    errors: list[str] = []
    warnings: list[str] = []

    readme = module_dir / "README.md"
    alt_readme = module_dir / "DELIVERABLE_README.md"
    has_readme = readme.exists()
    has_alt_readme = alt_readme.exists()

    deliverables = sorted(module_dir.glob("deliverable_*.py"))
    if not deliverables:
        warnings.append("No deliverable_*.py found")
    else:
        if not has_readme and not has_alt_readme:
            errors.append("Missing README.md (or DELIVERABLE_README.md)")
        elif not has_readme and has_alt_readme:
            warnings.append("README.md missing (using DELIVERABLE_README.md)")

        for deliverable in deliverables:
            content = deliverable.read_text()

            if not has_docstring(content):
                errors.append(f"{deliverable.name}: missing module docstring")

            if not has_entrypoint(content):
                errors.append(f"{deliverable.name}: missing main/demo entrypoint or __main__ guard")

            if not has_type_hints(content):
                errors.append(f"{deliverable.name}: missing type hints")

    return errors, warnings


def main() -> int:
    modules = sorted(p for p in EXAMPLES_DIR.glob("module_*") if p.is_dir())

    total = 0
    modules_with_errors = 0
    modules_with_warnings = 0

    for module_dir in modules:
        total += 1
        errors, warnings = lint_module(module_dir)
        if errors:
            modules_with_errors += 1
            print(f"❌ {module_dir.name}")
            for issue in errors:
                print(f"   • {issue}")
            for warn in warnings:
                modules_with_warnings += 1
                print(f"   • (warn) {warn}")
        elif warnings:
            modules_with_warnings += 1
            print(f"⚠️  {module_dir.name}")
            for warn in warnings:
                print(f"   • (warn) {warn}")

    if modules_with_errors:
        print(f"\n❌ {modules_with_errors}/{total} modules have errors.")
        return 1

    if modules_with_warnings:
        print(f"\n⚠️  {modules_with_warnings} modules have warnings (no hard failures).")

    print(f"✅ {total} modules passed lint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
