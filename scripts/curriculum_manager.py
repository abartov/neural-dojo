#!/usr/bin/env python3
"""
Curriculum Manager for Neural Dojo

Helps manage, validate, and expand the curriculum structure.
Run with: python scripts/curriculum_manager.py <command>

Commands:
    validate    - Check curriculum integrity
    status      - Show curriculum statistics
    add-module  - Add a new module (interactive)
    generate    - Generate MODULE_INDEX.md from MASTER_CURRICULUM.md
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
CURRICULUM_DIR = PROJECT_ROOT / "docs" / "curriculum"
NOTES_DIR = CURRICULUM_DIR / "notes"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

MASTER_FILE = CURRICULUM_DIR / "MASTER_CURRICULUM.md"
INDEX_FILE = CURRICULUM_DIR / "MODULE_INDEX.md"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Module:
    """Represents a curriculum module."""
    id: str  # e.g., "1.1", "2", "1.4"
    name: str
    status: str  # complete, in_progress, not_started
    phase: int
    duration: str = ""
    prerequisites: list[str] = field(default_factory=list)
    theory_file: Optional[Path] = None
    examples_dir: Optional[Path] = None
    has_deliverable: bool = False


@dataclass
class Phase:
    """Represents a curriculum phase."""
    id: int
    name: str
    modules: list[Module] = field(default_factory=list)


@dataclass
class Curriculum:
    """Complete curriculum structure."""
    phases: list[Phase] = field(default_factory=list)
    total_modules: int = 0
    complete_modules: int = 0


# ============================================================================
# Parsing Functions
# ============================================================================

def parse_master_curriculum() -> Curriculum:
    """Parse MASTER_CURRICULUM.md to extract structure."""
    if not MASTER_FILE.exists():
        print(f"Error: {MASTER_FILE} not found")
        sys.exit(1)

    content = MASTER_FILE.read_text()
    curriculum = Curriculum()
    current_phase = None

    # Phase pattern: ## Phase X: Name
    phase_pattern = re.compile(r"^## Phase (\d+): (.+)$", re.MULTILINE)

    # Module pattern: ### Module X.Y: Name or ### Module X: Name
    module_pattern = re.compile(
        r"^### Module ([\d.]+): (.+?)(?:\s*🔮)?$",
        re.MULTILINE
    )

    # Status pattern: - **Status**: 🟢 Complete
    status_pattern = re.compile(r"\*\*Status\*\*:\s*(🟢|🟡|⚪|🔴)\s*(\w+)")

    # Find all phases
    phases_found = []
    for match in phase_pattern.finditer(content):
        phase_id = int(match.group(1))
        phase_name = match.group(2).strip()
        phases_found.append((phase_id, phase_name, match.start()))

    # Find all modules and associate with phases
    modules_found = []
    for match in module_pattern.finditer(content):
        module_id = match.group(1)
        module_name = match.group(2).strip()
        pos = match.start()

        # Find status after this module
        status_match = status_pattern.search(content, pos, pos + 500)
        status = "unknown"
        if status_match:
            status = status_match.group(2).lower()

        modules_found.append((module_id, module_name, status, pos))

    # Associate modules with phases
    for i, (phase_id, phase_name, phase_pos) in enumerate(phases_found):
        next_phase_pos = phases_found[i + 1][2] if i + 1 < len(phases_found) else len(content)

        phase = Phase(id=phase_id, name=phase_name)

        for mod_id, mod_name, mod_status, mod_pos in modules_found:
            if phase_pos <= mod_pos < next_phase_pos:
                module = Module(
                    id=mod_id,
                    name=mod_name,
                    status=mod_status,
                    phase=phase_id,
                )
                phase.modules.append(module)

        curriculum.phases.append(phase)

    # Calculate totals
    curriculum.total_modules = sum(len(p.modules) for p in curriculum.phases)
    curriculum.complete_modules = sum(
        1 for p in curriculum.phases
        for m in p.modules
        if m.status == "complete"
    )

    return curriculum


def find_theory_file(module_id: str) -> Optional[Path]:
    """Find the theory file for a module."""
    # Try different patterns
    patterns = []

    if '.' in module_id:
        # Decimal notation: 1.4 -> module_01.4_*
        parts = module_id.split('.')
        phase = parts[0].zfill(2)
        submodule = parts[1]
        patterns.append(f"module_{phase}.{submodule}_*.md")
    else:
        # Integer notation: 2 -> module_02_*
        patterns.append(f"module_{module_id.zfill(2)}_*.md")
        patterns.append(f"module_0{module_id}_*.md")

    for pattern in patterns:
        matches = list(NOTES_DIR.glob(pattern))
        if matches:
            return matches[0]

    return None


def find_examples_dir(module_id: str) -> Optional[Path]:
    """Find the examples directory for a module."""
    # Try different patterns
    patterns = []

    if '.' in module_id:
        # Decimal notation: 1.4 -> module_01.4 or module_1.4
        parts = module_id.split('.')
        phase = parts[0].zfill(2)
        submodule = parts[1]
        patterns.append(f"module_{phase}.{submodule}")
        patterns.append(f"module_{module_id}")
        # Also check base phase directory for legacy modules (1.1, 1.3 share module_01)
        patterns.append(f"module_{phase}")
    else:
        # Integer notation: 2 -> module_02 or module_2
        patterns.append(f"module_{module_id.zfill(2)}")
        patterns.append(f"module_{module_id}")
        patterns.append(f"module_0{module_id}")

    for pattern in patterns:
        path = EXAMPLES_DIR / pattern
        if path.exists() and path.is_dir():
            return path

    return None


# ============================================================================
# Validation Functions
# ============================================================================

def validate_curriculum() -> tuple[list[str], list[str]]:
    """Validate curriculum structure. Returns (errors, warnings)."""
    errors = []
    warnings = []

    curriculum = parse_master_curriculum()

    print(f"\n📋 Validating {curriculum.total_modules} modules...")

    for phase in curriculum.phases:
        for module in phase.modules:
            # Check theory file
            theory = find_theory_file(module.id)
            if not theory:
                if module.status == "complete":
                    errors.append(f"Module {module.id}: Missing theory file (marked complete)")
                else:
                    warnings.append(f"Module {module.id}: Missing theory file")

            # Check examples directory
            examples = find_examples_dir(module.id)
            if not examples:
                if module.status == "complete":
                    errors.append(f"Module {module.id}: Missing examples directory (marked complete)")
                else:
                    warnings.append(f"Module {module.id}: Missing examples directory")
            else:
                # Check for deliverable
                deliverables = list(examples.glob("deliverable_*.py"))
                if not deliverables:
                    warnings.append(f"Module {module.id}: No deliverable file found")

    return errors, warnings


def print_status():
    """Print curriculum status."""
    curriculum = parse_master_curriculum()

    print("\n" + "=" * 60)
    print("  Neural Dojo Curriculum Status")
    print("=" * 60)

    print(f"\n📊 Overall: {curriculum.complete_modules}/{curriculum.total_modules} modules complete")
    progress = (curriculum.complete_modules / curriculum.total_modules * 100) if curriculum.total_modules > 0 else 0
    print(f"   Progress: {progress:.1f}%")

    print("\n📚 Phases:")
    for phase in curriculum.phases:
        complete = sum(1 for m in phase.modules if m.status == "complete")
        total = len(phase.modules)
        status = "🟢" if complete == total else "🟡" if complete > 0 else "⚪"
        print(f"   {status} Phase {phase.id}: {phase.name}")
        print(f"      {complete}/{total} modules ({complete/total*100:.0f}%)")

    print("\n📝 Recent/New Modules:")
    for phase in curriculum.phases:
        for module in phase.modules:
            if module.status != "complete":
                status_emoji = {"in_progress": "🟡", "unknown": "❓"}.get(module.status, "⚪")
                print(f"   {status_emoji} Module {module.id}: {module.name}")


def suggest_next_module_id(phase_id: int) -> str:
    """Suggest the next available module ID for a phase."""
    curriculum = parse_master_curriculum()

    for phase in curriculum.phases:
        if phase.id == phase_id:
            # Find highest decimal module ID
            max_decimal = 0
            for module in phase.modules:
                if '.' in module.id:
                    parts = module.id.split('.')
                    if int(parts[0]) == phase_id:
                        max_decimal = max(max_decimal, int(parts[1]))

            return f"{phase_id}.{max_decimal + 1}"

    return f"{phase_id}.1"


# ============================================================================
# Commands
# ============================================================================

def cmd_validate():
    """Validate command."""
    errors, warnings = validate_curriculum()

    if errors:
        print("\n❌ Errors found:")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print("\n⚠️ Warnings:")
        for warning in warnings[:10]:  # Limit to 10
            print(f"   • {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more")

    if not errors and not warnings:
        print("\n✅ Curriculum validation passed!")
    elif not errors:
        print(f"\n✅ No critical errors. {len(warnings)} warnings.")
    else:
        print(f"\n❌ {len(errors)} errors, {len(warnings)} warnings.")
        sys.exit(1)


def cmd_status():
    """Status command."""
    print_status()


def cmd_add_module():
    """Interactive module addition."""
    print("\n📦 Add New Module")
    print("=" * 40)

    curriculum = parse_master_curriculum()

    print("\nAvailable phases:")
    for phase in curriculum.phases:
        print(f"  {phase.id}: {phase.name}")

    try:
        phase_id = int(input("\nEnter phase number: "))
    except ValueError:
        print("Invalid phase number")
        sys.exit(1)

    suggested_id = suggest_next_module_id(phase_id)
    print(f"\nSuggested module ID: {suggested_id}")

    module_id = input(f"Module ID [{suggested_id}]: ").strip() or suggested_id
    module_name = input("Module name: ").strip()

    if not module_name:
        print("Module name is required")
        sys.exit(1)

    print(f"\n📋 Will create:")
    print(f"   Module ID: {module_id}")
    print(f"   Name: {module_name}")
    print(f"   Theory: docs/curriculum/notes/module_{module_id.replace('.', '_')}_{module_name.lower().replace(' ', '_')}.md")
    print(f"   Examples: examples/module_{module_id}/")

    confirm = input("\nProceed? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)

    # Create files
    safe_name = module_name.lower().replace(' ', '_').replace('-', '_')
    safe_name = re.sub(r'[^a-z0-9_]', '', safe_name)

    theory_file = NOTES_DIR / f"module_{module_id.replace('.', '_')}_{safe_name}.md"
    examples_dir = EXAMPLES_DIR / f"module_{module_id}"

    # Create theory template
    theory_content = f"""# Module {module_id}: {module_name}

**Last Updated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
**Status**: ⚪ Not Started
**Duration**: X-Y hours
**Prerequisites**: [List prerequisites]

---

## 🎯 Learning Objectives

By the end of this module, you will:
- [Objective 1]
- [Objective 2]
- [Objective 3]

---

## 📖 Theory

### Introduction

[Content here]

---

## 💻 Hands-On Practice

### Exercise 1: [Name]

[Step-by-step instructions]

---

## 🎯 Deliverables

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## 📚 Further Reading

- [Resource 1]
- [Resource 2]

---

## 💡 Did You Know?

[Interesting facts]

---

## ⏭️ Next Steps

[Next module reference]
"""

    theory_file.write_text(theory_content)
    print(f"✅ Created {theory_file}")

    examples_dir.mkdir(exist_ok=True)
    readme = examples_dir / "README.md"
    readme.write_text(f"# Module {module_id} Examples: {module_name}\n\nExamples for this module.\n")
    print(f"✅ Created {examples_dir}/")

    print(f"\n🎉 Module {module_id} scaffolding created!")
    print("   Don't forget to:")
    print("   1. Update MASTER_CURRICULUM.md")
    print("   2. Update MODULE_INDEX.md")
    print("   3. Write the theory content")
    print("   4. Create the deliverable")


def show_help():
    """Show help message."""
    print(__doc__)


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        "validate": cmd_validate,
        "status": cmd_status,
        "add-module": cmd_add_module,
        "help": show_help,
        "--help": show_help,
        "-h": show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
