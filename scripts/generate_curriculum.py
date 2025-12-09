#!/usr/bin/env python3
"""
Curriculum Generator for Neural Dojo

Reads curriculum.yaml and generates:
  - MASTER_CURRICULUM.md
  - MODULE_INDEX.md
  - Validates file structure

Usage:
    python scripts/generate_curriculum.py           # Generate all files
    python scripts/generate_curriculum.py validate  # Validate only
    python scripts/generate_curriculum.py status    # Show status
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
CURRICULUM_FILE = PROJECT_ROOT / "curriculum.yaml"
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
    phase_id: int
    seq: int
    name: str
    legacy_id: str
    hours: str
    status: str
    prerequisites: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    heureka: bool = False

    @property
    def global_id(self) -> str:
        """Generate global module ID like '1.4' or '2.1'."""
        return f"{self.phase_id}.{self.seq}"

    @property
    def theory_file(self) -> Optional[Path]:
        """Find theory file for this module."""
        # Build patterns based on legacy_id
        patterns = []

        if '.' in self.legacy_id:
            # Decimal: "01.1" -> module_01.1_*.md
            patterns.append(f"module_{self.legacy_id}_*.md")
            # Also try without leading zero
            parts = self.legacy_id.split('.')
            patterns.append(f"module_{parts[0].lstrip('0') or '0'}.{parts[1]}_*.md")
        else:
            # Integer: "02" -> module_02_*.md
            patterns.append(f"module_{self.legacy_id}_*.md")
            patterns.append(f"module_{self.legacy_id.zfill(2)}_*.md")

        for pattern in patterns:
            matches = list(NOTES_DIR.glob(pattern))
            if matches:
                return matches[0]
        return None

    @property
    def examples_dir(self) -> Optional[Path]:
        """Find examples directory for this module."""
        patterns = []

        if '.' in self.legacy_id:
            # Decimal: "01.4" -> module_01.4/
            patterns.append(f"module_{self.legacy_id}")
            # Also check base directory for shared modules (1.1, 1.3 use module_01)
            parts = self.legacy_id.split('.')
            patterns.append(f"module_{parts[0]}")
        else:
            # Integer: "02" -> module_02/
            patterns.append(f"module_{self.legacy_id}")
            patterns.append(f"module_{self.legacy_id.zfill(2)}")

        for pattern in patterns:
            path = EXAMPLES_DIR / pattern
            if path.exists() and path.is_dir():
                return path
        return None

    @property
    def status_emoji(self) -> str:
        """Get status emoji."""
        return {
            "complete": "🟢",
            "in_progress": "🟡",
            "not_started": "⚪",
            "blocked": "🔴",
        }.get(self.status, "❓")


@dataclass
class Phase:
    """Represents a curriculum phase."""
    id: int
    name: str
    description: str
    weeks: str
    status: str
    modules: list[Module] = field(default_factory=list)

    @property
    def complete_count(self) -> int:
        return sum(1 for m in self.modules if m.status == "complete")

    @property
    def total_count(self) -> int:
        return len(self.modules)

    @property
    def progress_pct(self) -> int:
        if self.total_count == 0:
            return 0
        return int(self.complete_count / self.total_count * 100)

    @property
    def status_emoji(self) -> str:
        if self.complete_count == self.total_count:
            return "🟢"
        elif self.complete_count > 0:
            return "🟡"
        return "⚪"


@dataclass
class Curriculum:
    """Complete curriculum."""
    version: str
    title: str
    subtitle: str
    settings: dict
    phases: list[Phase] = field(default_factory=list)

    @property
    def total_modules(self) -> int:
        return sum(p.total_count for p in self.phases)

    @property
    def complete_modules(self) -> int:
        return sum(p.complete_count for p in self.phases)

    @property
    def progress_pct(self) -> int:
        if self.total_modules == 0:
            return 0
        return int(self.complete_modules / self.total_modules * 100)


# ============================================================================
# YAML Loading
# ============================================================================

def load_curriculum() -> Curriculum:
    """Load curriculum from YAML file."""
    if not CURRICULUM_FILE.exists():
        print(f"Error: {CURRICULUM_FILE} not found")
        sys.exit(1)

    with open(CURRICULUM_FILE) as f:
        data = yaml.safe_load(f)

    phases = []
    for phase_data in data.get("phases", []):
        modules = []
        for mod_data in phase_data.get("modules", []):
            module = Module(
                phase_id=phase_data["id"],
                seq=mod_data["seq"],
                name=mod_data["name"],
                legacy_id=str(mod_data.get("legacy_id", mod_data["seq"])),
                hours=mod_data.get("hours", ""),
                status=mod_data.get("status", "not_started"),
                prerequisites=mod_data.get("prerequisites", []),
                objectives=mod_data.get("objectives", []),
                deliverables=mod_data.get("deliverables", []),
                heureka=mod_data.get("heureka", False),
            )
            modules.append(module)

        phase = Phase(
            id=phase_data["id"],
            name=phase_data["name"],
            description=phase_data.get("description", ""),
            weeks=phase_data.get("weeks", ""),
            status=phase_data.get("status", "not_started"),
            modules=modules,
        )
        phases.append(phase)

    return Curriculum(
        version=data.get("version", "1.0.0"),
        title=data.get("title", "Neural Dojo"),
        subtitle=data.get("subtitle", ""),
        settings=data.get("settings", {}),
        phases=phases,
    )


# ============================================================================
# Generator Functions
# ============================================================================

def generate_master_curriculum(curriculum: Curriculum) -> str:
    """Generate MASTER_CURRICULUM.md content."""
    lines = []

    # Header
    lines.append(f"# {curriculum.title}")
    lines.append("")
    lines.append(f"**{curriculum.subtitle}**")
    lines.append("")
    lines.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**Version**: {curriculum.version}")
    lines.append(f"**Status**: {curriculum.complete_modules}/{curriculum.total_modules} modules complete ({curriculum.progress_pct}%)")
    lines.append(f"**Total Duration**: {curriculum.total_modules} modules, {curriculum.settings.get('total_weeks', 'TBD')} weeks ({curriculum.settings.get('total_hours', 'TBD')} hours)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Progress Table
    lines.append("## 📊 Progress Tracking")
    lines.append("")
    lines.append("| Phase | Name | Modules | Status |")
    lines.append("|-------|------|---------|--------|")

    for phase in curriculum.phases:
        status = f"{phase.status_emoji} {phase.complete_count}/{phase.total_count} ({phase.progress_pct}%)"
        lines.append(f"| {phase.id} | {phase.name} | {phase.total_count} | {status} |")

    lines.append(f"| **Total** | | **{curriculum.total_modules}** | **{curriculum.progress_pct}%** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Phases and Modules
    for phase in curriculum.phases:
        lines.append(f"## Phase {phase.id}: {phase.name}")
        lines.append("")
        lines.append(f"**{phase.description}**")
        lines.append("")
        if phase.weeks:
            lines.append(f"**Weeks**: {phase.weeks}")
            lines.append("")

        for module in phase.modules:
            heureka = " 🔮" if module.heureka else ""
            lines.append(f"### Module {module.global_id}: {module.name}{heureka}")
            lines.append("")
            lines.append(f"- **Duration**: {module.hours} hours")
            lines.append(f"- **Status**: {module.status_emoji} {module.status.replace('_', ' ').title()}")

            if module.prerequisites:
                prereqs = ", ".join(module.prerequisites)
                lines.append(f"- **Prerequisites**: {prereqs}")

            # Theory file link
            if module.theory_file:
                rel_path = module.theory_file.relative_to(CURRICULUM_DIR)
                lines.append(f"- **Theory**: [{module.theory_file.name}]({rel_path})")

            # Examples link
            if module.examples_dir:
                rel_path = module.examples_dir.relative_to(PROJECT_ROOT)
                lines.append(f"- **Examples**: [{module.examples_dir.name}/]({rel_path}/)")

            lines.append("")

            if module.objectives:
                lines.append("**Learning Objectives**:")
                for obj in module.objectives[:4]:  # Limit to 4
                    lines.append(f"- {obj}")
                if len(module.objectives) > 4:
                    lines.append(f"- *... and {len(module.objectives) - 4} more*")
                lines.append("")

            if module.deliverables:
                lines.append("**Deliverables**:")
                for deliv in module.deliverables:
                    check = "✅" if module.status == "complete" else "[ ]"
                    lines.append(f"- {check} {deliv}")
                lines.append("")

            lines.append("---")
            lines.append("")

    # Footer
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated from curriculum.yaml*")

    return "\n".join(lines)


def generate_module_index(curriculum: Curriculum) -> str:
    """Generate MODULE_INDEX.md content."""
    lines = []

    # Header
    lines.append("# Module Index")
    lines.append("")
    lines.append("*Auto-generated from curriculum.yaml*")
    lines.append("")
    lines.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"## Progress: {curriculum.complete_modules}/{curriculum.total_modules} modules ({curriculum.progress_pct}%)")
    lines.append("")

    # Quick stats
    in_progress = sum(1 for p in curriculum.phases for m in p.modules if m.status == "in_progress")
    not_started = sum(1 for p in curriculum.phases for m in p.modules if m.status == "not_started")

    lines.append(f"- **Complete**: {curriculum.complete_modules}")
    lines.append(f"- **In Progress**: {in_progress}")
    lines.append(f"- **Not Started**: {not_started}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Phases
    for phase in curriculum.phases:
        lines.append(f"## Phase {phase.id}: {phase.name} {phase.status_emoji}")
        lines.append("")
        lines.append(f"**Weeks {phase.weeks}** | {phase.complete_count}/{phase.total_count} complete")
        lines.append("")

        for module in phase.modules:
            heureka = " 🔮" if module.heureka else ""
            lines.append(f"### Module {module.global_id}: {module.name} {module.status_emoji}{heureka}")
            lines.append("")
            lines.append(f"- **Duration**: {module.hours} hours")

            if module.prerequisites:
                lines.append(f"- **Prerequisites**: {', '.join(module.prerequisites)}")

            if module.theory_file:
                rel_path = module.theory_file.relative_to(CURRICULUM_DIR)
                lines.append(f"- **Theory**: [{module.theory_file.name}]({rel_path})")

            if module.examples_dir:
                rel_path = f"../../{module.examples_dir.relative_to(PROJECT_ROOT)}"
                lines.append(f"- **Examples**: [{module.examples_dir.name}/]({rel_path}/)")

            if module.objectives:
                lines.append("- **Objectives**:")
                for obj in module.objectives[:3]:
                    lines.append(f"  - {obj}")
                if len(module.objectives) > 3:
                    lines.append(f"  - *... and {len(module.objectives) - 3} more*")

            lines.append("")

            # Next module link
            next_mod = get_next_module(curriculum, module)
            if next_mod:
                anchor = f"module-{next_mod.global_id.replace('.', '')}-{next_mod.name.lower().replace(' ', '-').replace('&', '').replace('/', '')}"
                lines.append(f"→ **Next**: [Module {next_mod.global_id}: {next_mod.name}](#{anchor})")
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def get_next_module(curriculum: Curriculum, current: Module) -> Optional[Module]:
    """Get the next module in sequence."""
    all_modules = [m for p in curriculum.phases for m in p.modules]
    for i, m in enumerate(all_modules):
        if m.phase_id == current.phase_id and m.seq == current.seq:
            if i + 1 < len(all_modules):
                return all_modules[i + 1]
    return None


# ============================================================================
# Validation
# ============================================================================

def validate_curriculum(curriculum: Curriculum) -> tuple[list[str], list[str]]:
    """Validate curriculum structure."""
    errors = []
    warnings = []

    for phase in curriculum.phases:
        for module in phase.modules:
            # Check theory file
            if not module.theory_file:
                if module.status == "complete":
                    errors.append(f"Module {module.global_id}: Missing theory file (marked complete)")
                else:
                    warnings.append(f"Module {module.global_id}: Missing theory file")

            # Check examples directory
            if not module.examples_dir:
                if module.status == "complete":
                    errors.append(f"Module {module.global_id}: Missing examples directory (marked complete)")
                else:
                    warnings.append(f"Module {module.global_id}: Missing examples directory")
            else:
                # Check for deliverable
                deliverables = list(module.examples_dir.glob("deliverable_*.py"))
                if not deliverables and module.status == "complete":
                    warnings.append(f"Module {module.global_id}: No deliverable file")

    return errors, warnings


# ============================================================================
# Commands
# ============================================================================

def cmd_generate():
    """Generate curriculum files."""
    print("📚 Loading curriculum.yaml...")
    curriculum = load_curriculum()

    print(f"   Found {len(curriculum.phases)} phases, {curriculum.total_modules} modules")

    # Validate first
    errors, warnings = validate_curriculum(curriculum)
    if errors:
        print("\n❌ Validation errors:")
        for e in errors:
            print(f"   • {e}")
        print("\nFix errors before generating.")
        sys.exit(1)

    # Generate MASTER_CURRICULUM.md
    print("\n📝 Generating MASTER_CURRICULUM.md...")
    master_content = generate_master_curriculum(curriculum)
    MASTER_FILE.write_text(master_content)
    print(f"   ✅ Written to {MASTER_FILE}")

    # Generate MODULE_INDEX.md
    print("\n📝 Generating MODULE_INDEX.md...")
    index_content = generate_module_index(curriculum)
    INDEX_FILE.write_text(index_content)
    print(f"   ✅ Written to {INDEX_FILE}")

    # Summary
    print("\n" + "=" * 50)
    print("✅ Generation complete!")
    print(f"   Modules: {curriculum.complete_modules}/{curriculum.total_modules} ({curriculum.progress_pct}%)")

    if warnings:
        print(f"\n⚠️ {len(warnings)} warnings (non-blocking):")
        for w in warnings[:5]:
            print(f"   • {w}")
        if len(warnings) > 5:
            print(f"   ... and {len(warnings) - 5} more")


def cmd_validate():
    """Validate only."""
    print("📚 Loading curriculum.yaml...")
    curriculum = load_curriculum()

    print(f"   Validating {curriculum.total_modules} modules...")

    errors, warnings = validate_curriculum(curriculum)

    if errors:
        print("\n❌ Errors:")
        for e in errors:
            print(f"   • {e}")

    if warnings:
        print(f"\n⚠️ Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"   • {w}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more")

    if not errors and not warnings:
        print("\n✅ Validation passed!")
    elif not errors:
        print(f"\n✅ No critical errors. {len(warnings)} warnings.")
    else:
        print(f"\n❌ {len(errors)} errors, {len(warnings)} warnings.")
        sys.exit(1)


def cmd_status():
    """Show status."""
    curriculum = load_curriculum()

    print("\n" + "=" * 60)
    print(f"  {curriculum.title}")
    print("=" * 60)

    print(f"\n📊 Overall: {curriculum.complete_modules}/{curriculum.total_modules} ({curriculum.progress_pct}%)")

    print("\n📚 Phases:")
    for phase in curriculum.phases:
        print(f"   {phase.status_emoji} Phase {phase.id}: {phase.name}")
        print(f"      {phase.complete_count}/{phase.total_count} ({phase.progress_pct}%)")

    # Show in-progress modules
    in_progress = [m for p in curriculum.phases for m in p.modules if m.status == "in_progress"]
    if in_progress:
        print("\n🟡 In Progress:")
        for m in in_progress:
            print(f"   • Module {m.global_id}: {m.name}")


def cmd_help():
    """Show help."""
    print(__doc__)


# ============================================================================
# Main
# ============================================================================

def main():
    if len(sys.argv) < 2:
        cmd_generate()
        return

    command = sys.argv[1].lower()

    commands = {
        "generate": cmd_generate,
        "validate": cmd_validate,
        "status": cmd_status,
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        cmd_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
