"""
Module 01 Deliverable: AI Coding Tools Overview

Summarize key tooling choices before diving deeper into agentic IDEs and CLI assistants.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ToolOption:
    """Represents a recommended AI coding tool."""

    name: str
    strengths: str
    best_for: str


def recommended_stack() -> List[ToolOption]:
    """Return a curated starter stack."""
    return [
        ToolOption(
            name="Claude Code",
            strengths="multi-file reasoning, quick edits, strong analysis",
            best_for="core editing and refactors",
        ),
        ToolOption(
            name="Cursor",
            strengths="Composer for multi-file changes, built-in evals",
            best_for="project-scale edits",
        ),
        ToolOption(
            name="Aider",
            strengths="git-native workflow, lightweight",
            best_for="terminal-first pairing",
        ),
    ]


def format_table(options: List[ToolOption]) -> str:
    """Render a small markdown table for quick sharing."""
    lines = ["| Tool | Strengths | Best for |", "| --- | --- | --- |"]
    for opt in options:
        lines.append(f"| {opt.name} | {opt.strengths} | {opt.best_for} |")
    return "\n".join(lines)


def main() -> None:
    """Print the tool recommendations."""
    print("# Recommended AI Coding Stack\n")
    print(format_table(recommended_stack()))
    print("\nTip: start with one IDE assistant + one CLI assistant; add others as needed.")


if __name__ == "__main__":
    main()
