"""
Module 01.2 Deliverable: Local Models Checklist

Create a lightweight, reproducible checklist for standing up local LLMs (e.g., Ollama) alongside cloud models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class LocalModelPlan:
    """Configuration plan for a local model stack."""

    model: str
    gpu_required: bool
    disk_gb: int
    notes: str


def recommended_local_models() -> List[LocalModelPlan]:
    """Return a small starter set for experimentation."""
    return [
        LocalModelPlan(model="llama3.2:3b", gpu_required=False, disk_gb=4, notes="fast prompt dev"),
        LocalModelPlan(model="mistral:7b", gpu_required=False, disk_gb=8, notes="balanced quality"),
        LocalModelPlan(model="llama3.1:8b", gpu_required=True, disk_gb=16, notes="higher quality"),
    ]


def main() -> None:
    """Print the checklist for local model setup."""
    print("# Local Models Checklist\n")
    for plan in recommended_local_models():
        gpu = "GPU" if plan.gpu_required else "CPU-ok"
        print(f"- {plan.model} ({gpu}, ~{plan.disk_gb}GB): {plan.notes}")
    print("\nRemember to pin versions and cache weights to avoid repeated downloads.")


if __name__ == "__main__":
    main()
