"""
Module 55 Deliverable: AI/ML History Timeline

Provide a concise, scriptable timeline of key AI/ML milestones for quick reference or quiz generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TimelineEvent:
    """A notable milestone in AI/ML history."""

    year: int
    title: str
    note: str


def load_timeline() -> List[TimelineEvent]:
    """Return a curated set of milestones."""
    return [
        TimelineEvent(1956, "Dartmouth Workshop", "AI term coined; symbolic AI foundation"),
        TimelineEvent(1986, "Backprop revival", "Rumelhart, Hinton, Williams popularize backprop"),
        TimelineEvent(2012, "AlexNet", "Deep CNNs win ImageNet; modern DL era begins"),
        TimelineEvent(2017, "Attention Is All You Need", "Transformers reshape sequence modeling"),
        TimelineEvent(2022, "Instruction tuning surge", "RLHF/instruction-tuned LLMs reach mainstream"),
    ]


def main() -> None:
    """Print the timeline."""
    print("# AI/ML History Highlights\n")
    for event in load_timeline():
        print(f"- {event.year}: {event.title} — {event.note}")
    print("\nUse these as anchors for quizzes or context in other modules.")


if __name__ == "__main__":
    main()
