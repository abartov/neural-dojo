"""
Configuration for the documentation generator.

Adapted for Neural Dojo AI curriculum.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PathConfig:
    """Path configuration for documentation sources and outputs."""

    # Project root (auto-detected)
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)

    @property
    def curriculum_dir(self) -> Path:
        return self.project_root / "docs" / "curriculum"

    @property
    def master_curriculum(self) -> Path:
        return self.curriculum_dir / "MASTER_CURRICULUM.md"

    @property
    def module_index(self) -> Path:
        return self.curriculum_dir / "MODULE_INDEX.md"

    @property
    def notes_dir(self) -> Path:
        return self.curriculum_dir / "notes"

    @property
    def examples_dir(self) -> Path:
        return self.project_root / "examples"

    @property
    def html_output_dir(self) -> Path:
        return self.project_root / "docs" / "_site"


# Status markers used in curriculum
STATUS_MARKERS = {
    "complete": "🟢",
    "in_progress": "🟡",
    "pending": "⚪",
    "theory_only": "📝",
    "blocked": "🔴",
}

# Phase status patterns
PHASE_COMPLETE_PATTERN = "Complete"
PHASE_IN_PROGRESS_PATTERN = "In Progress"


def get_default_config() -> PathConfig:
    """Get default path configuration."""
    return PathConfig()
