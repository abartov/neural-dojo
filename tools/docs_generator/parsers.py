"""
Parsers for extracting structure from MASTER_CURRICULUM.md

Adapted for Neural Dojo curriculum format:
- ## Phase N: Title (Weeks X-Y)
- ### Module N: Title or ### Module N.N: Title
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SubModule:
    """Represents a sub-module (e.g., 1.1, 1.2)."""

    number: str  # "1.1", "1.2", etc.
    title: str
    theory_file: str | None = None
    size_info: str | None = None  # "52K, 1,205 lines"
    topics: list[str] = field(default_factory=list)


@dataclass
class Module:
    """Represents a curriculum module."""

    number: str  # Can be "1", "1.1", "9.1", etc.
    title: str
    status: str  # "complete", "in_progress", "pending", "theory_only"
    theory_file: str | None = None
    theory_files: list[dict] = field(default_factory=list)
    sub_modules: list[SubModule] = field(default_factory=list)
    code_file: str | None = None
    code_files: list[str] = field(default_factory=list)
    duration: str | None = None
    prerequisites: str | None = None
    deliverable: str | None = None
    content: str | None = None
    files: str | None = None  # Files reference
    learning_objectives: list[str] = field(default_factory=list)
    deliverables_list: list[str] = field(default_factory=list)
    is_heureka: bool = False
    raw_content: list[str] = field(default_factory=list)


@dataclass
class Phase:
    """Represents a curriculum phase."""

    number: str  # "1", "2", etc.
    title: str
    weeks: str
    status: str  # "complete", "in_progress", "pending"
    goal: str | None = None
    modules: list[Module] = field(default_factory=list)


@dataclass
class CurriculumData:
    """Parsed curriculum data."""

    title: str
    last_updated: str
    total_modules: int
    phases: list[Phase] = field(default_factory=list)

    def modules_by_status(self) -> dict[str, int]:
        """Count modules by status."""
        counts = {"complete": 0, "in_progress": 0, "pending": 0, "theory_only": 0}
        for phase in self.phases:
            for module in phase.modules:
                if module.status in counts:
                    counts[module.status] += 1
        return counts

    def all_modules(self) -> list[Module]:
        """Get flat list of all modules."""
        modules = []
        for phase in self.phases:
            modules.extend(phase.modules)
        return modules


def parse_status(line: str) -> str:
    """Parse status from a module or phase line."""
    line_lower = line.lower()

    # Complete - check both emoji and text
    if "🟢" in line or "✅" in line:
        return "complete"
    if "complete" in line_lower and "not" not in line_lower:
        return "complete"

    # In progress
    if "🟡" in line or "in progress" in line_lower:
        return "in_progress"

    # Theory only
    if "📝" in line or "theory only" in line_lower:
        return "theory_only"

    # Not started / Pending
    if "⚪" in line or "not started" in line_lower or "pending" in line_lower:
        return "pending"

    # Blocked
    if "🔴" in line or "blocked" in line_lower:
        return "blocked"

    return "pending"


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    """Extract all [name](path) links from text."""
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def parse_curriculum(file_path: Path) -> CurriculumData:
    """
    Parse MASTER_CURRICULUM.md and extract phases and modules.

    Neural Dojo format:
    - ## Phase N: Title (Weeks X-Y)
    - ### Module N: Title or ### Module N.N: Title

    Args:
        file_path: Path to MASTER_CURRICULUM.md

    Returns:
        CurriculumData with phases and modules
    """
    content = file_path.read_text()
    lines = content.split("\n")

    # Extract metadata
    title = "Neural Dojo: Master Curriculum"
    last_updated = ""
    total_modules = 56  # Default

    for line in lines[:20]:
        if line.startswith("**Last Updated**:"):
            last_updated = line.split(":", 1)[1].strip()
        if "modules" in line.lower():
            match = re.search(r"(\d+)\s*modules", line.lower())
            if match:
                total_modules = int(match.group(1))

    phases: list[Phase] = []
    current_phase: Phase | None = None
    current_module: Module | None = None
    in_learning_objectives = False
    in_deliverables = False
    i = 0

    # Phase pattern - matches ## Phase N: Title (Weeks X-Y)
    phase_pattern = re.compile(
        r"##\s+Phase\s+(\d+):\s*([^(]+)\s*\(Weeks?\s*([\d-]+)\)",
        re.IGNORECASE,
    )

    # Module pattern - matches ### Module N: Title or ### Module N.N: Title
    module_pattern = re.compile(
        r"###\s+Module\s+(\d+(?:\.\d+)?)[:\s]+(.+?)(?:\s*(🔮|🟢|🟡|⚪|🔴|✅))*\s*$"
    )

    while i < len(lines):
        line = lines[i]

        # Check for phase header
        phase_match = phase_pattern.match(line)
        if phase_match:
            phase_num = phase_match.group(1)
            phase_title = phase_match.group(2).strip()
            phase_weeks = phase_match.group(3)

            # Look for status in progress table earlier in file
            phase_status = "pending"

            current_phase = Phase(
                number=phase_num,
                title=phase_title,
                weeks=phase_weeks,
                status=phase_status,
            )
            phases.append(current_phase)
            current_module = None
            in_learning_objectives = False
            in_deliverables = False
            i += 1
            continue

        # Check for module header
        module_match = module_pattern.match(line)
        if module_match and current_phase:
            module_num = module_match.group(1)
            module_title = module_match.group(2).strip()
            # Clean up title
            module_title = re.sub(r"\s*(🔮|🟢|🟡|⚪|🔴|✅)+\s*$", "", module_title).strip()

            is_heureka = "🔮" in line

            current_module = Module(
                number=module_num,
                title=module_title,
                status="pending",  # Will be updated from metadata
                is_heureka=is_heureka,
            )
            current_phase.modules.append(current_module)
            in_learning_objectives = False
            in_deliverables = False
            i += 1
            continue

        # Parse module details
        if current_module:
            # Check for section headers
            if line.startswith("**Learning Objectives**"):
                in_learning_objectives = True
                in_deliverables = False
                i += 1
                continue
            elif line.startswith("**Deliverables**"):
                in_deliverables = True
                in_learning_objectives = False
                i += 1
                continue
            elif line.startswith("**") and ":" in line:
                in_learning_objectives = False
                in_deliverables = False

            # Parse bullet points
            if line.startswith("- "):
                detail = line[2:].strip()
                current_module.raw_content.append(line)

                # In learning objectives section
                if in_learning_objectives:
                    current_module.learning_objectives.append(detail)
                # In deliverables section
                elif in_deliverables:
                    current_module.deliverables_list.append(detail)
                # Metadata lines
                elif detail.startswith("**Duration**:"):
                    current_module.duration = detail.split(":", 1)[1].strip()
                elif detail.startswith("**Prerequisites**:"):
                    current_module.prerequisites = detail.split(":", 1)[1].strip()
                elif detail.startswith("**Status**:"):
                    status_text = detail.split(":", 1)[1].strip()
                    current_module.status = parse_status(status_text)

            # Files reference
            if line.startswith("**Files**:"):
                current_module.files = line.split(":", 1)[1].strip()
                # Extract theory file path
                links = extract_markdown_links(line)
                for name, path in links:
                    if path.endswith(".md"):
                        current_module.theory_files.append({"name": name, "path": path})
                        if not current_module.theory_file:
                            current_module.theory_file = path

        i += 1

    # Update phase statuses based on module completion
    for phase in phases:
        if not phase.modules:
            phase.status = "pending"
        elif all(m.status == "complete" for m in phase.modules):
            phase.status = "complete"
        elif any(m.status in ("complete", "in_progress") for m in phase.modules):
            phase.status = "in_progress"
        else:
            phase.status = "pending"

    return CurriculumData(
        title=title,
        last_updated=last_updated,
        total_modules=total_modules,
        phases=phases,
    )


def generate_module_index(curriculum: CurriculumData, config=None) -> str:
    """
    Generate MODULE_INDEX.md content from parsed curriculum.

    Args:
        curriculum: Parsed curriculum data
        config: Optional path config

    Returns:
        Markdown string for MODULE_INDEX.md
    """
    lines = [
        "# Module Index",
        "",
        "*Auto-generated from MASTER_CURRICULUM.md*",
        "",
        f"**Last Updated**: {curriculum.last_updated}",
        "",
    ]

    # Progress summary
    counts = curriculum.modules_by_status()
    total_complete = counts["complete"]
    total = sum(counts.values())

    lines.extend(
        [
            f"## Progress: {total_complete}/{total} modules ({100*total_complete//total if total else 0}%)",
            "",
            f"- **Complete**: {counts['complete']}",
            f"- **In Progress**: {counts['in_progress']}",
            f"- **Theory Only**: {counts['theory_only']}",
            f"- **Pending**: {counts['pending']}",
            "",
            "---",
            "",
        ]
    )

    # Status emoji mapping
    status_emoji = {
        "complete": "🟢",
        "theory_only": "📝",
        "in_progress": "🟡",
        "pending": "⚪",
        "blocked": "🔴",
    }

    # Generate phase sections
    for phase in curriculum.phases:
        phase_complete = sum(1 for m in phase.modules if m.status == "complete")
        phase_total = len(phase.modules)
        phase_status = status_emoji.get(phase.status, "⚪")

        lines.append(f"## Phase {phase.number}: {phase.title} {phase_status}")
        lines.append(f"**Weeks {phase.weeks}** | {phase_complete}/{phase_total} complete")
        lines.append("")

        for module in phase.modules:
            status = status_emoji.get(module.status, "⚪")
            heureka = " 🔮" if module.is_heureka else ""

            lines.append(f"### Module {module.number}: {module.title} {status}{heureka}")
            lines.append("")

            # Duration and prerequisites
            if module.duration:
                lines.append(f"- **Duration**: {module.duration}")
            if module.prerequisites:
                lines.append(f"- **Prerequisites**: {module.prerequisites}")

            # Theory file
            if module.theory_files:
                theory_links = []
                for t in module.theory_files:
                    theory_links.append(f"[{t['name']}]({t['path']})")
                lines.append(f"- **Theory**: {', '.join(theory_links)}")

            # Files reference
            if module.files:
                lines.append(f"- **Files**: {module.files}")

            # Learning objectives (abbreviated)
            if module.learning_objectives:
                lines.append("- **Objectives**:")
                for obj in module.learning_objectives[:3]:  # Limit to 3
                    lines.append(f"  - {obj}")
                if len(module.learning_objectives) > 3:
                    lines.append(f"  - *... and {len(module.learning_objectives) - 3} more*")

            lines.append("")

        lines.append("---")
        lines.append("")

    # Footer
    lines.extend(
        [
            "*Generated by tools/docs_generator*",
            "",
            "**Regenerate:** `python -m tools.docs_generator --index`",
        ]
    )

    return "\n".join(lines)
