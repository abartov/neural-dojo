"""
Module 1: AI Coding Pattern #1 - Specification Pattern

Demonstrates how to get AI to generate code from a clear specification.

AI PROMPT USED:
---------------
Create a Python function that:
- Takes a list of integers
- Returns the top 3 most frequent numbers
- If there's a tie, include all tied numbers
- Return empty list if input is empty
- Add type hints and docstring
"""

from typing import List
from collections import Counter


def top_frequent_numbers(numbers: List[int], top_n: int = 3) -> List[int]:
    """
    Returns the top N most frequent numbers from the input list.

    If there's a tie in frequency, all tied numbers are included.

    Args:
        numbers: List of integers to analyze
        top_n: Number of top frequent items to return (default: 3)

    Returns:
        List of most frequent numbers, empty if input is empty

    Examples:
        >>> top_frequent_numbers([1, 1, 2, 2, 2, 3])
        [2, 1]
        >>> top_frequent_numbers([])
        []
        >>> top_frequent_numbers([1, 1, 2, 2, 3, 3])  # All tied
        [1, 2, 3]
    """
    if not numbers:
        return []

    counter = Counter(numbers)

    # Get the nth highest frequency
    if len(counter) < top_n:
        return [num for num, _ in counter.most_common()]

    frequencies = [count for _, count in counter.most_common()]
    nth_freq = frequencies[top_n - 1] if top_n <= len(frequencies) else 0

    # Include all numbers with frequency >= nth highest
    return [num for num, count in counter.items() if count >= nth_freq]


def demonstrate_specification_pattern():
    """
    Demonstrates the Specification Pattern with test cases.

    KEY INSIGHT: The clearer your specification, the better the code AI generates.
    """
    print("=" * 60)
    print("AI CODING PATTERN #1: SPECIFICATION PATTERN")
    print("=" * 60)
    print()
    print("✨ CONCEPT: Write detailed specs, let AI generate code")
    print()

    test_cases = [
        {
            "name": "Basic case",
            "input": [1, 1, 2, 2, 2, 3, 3, 3, 3, 4],
            "expected": "Top 3 should be: [3, 2, 1]"
        },
        {
            "name": "With ties",
            "input": [1, 1, 2, 2, 3, 3],
            "expected": "All three tied, return all: [1, 2, 3]"
        },
        {
            "name": "Empty list",
            "input": [],
            "expected": "Empty list: []"
        },
        {
            "name": "Single element",
            "input": [42],
            "expected": "Single element: [42]"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        result = top_frequent_numbers(test["input"])
        print(f"{i}. {test['name']}")
        print(f"   Input:    {test['input']}")
        print(f"   Output:   {result}")
        print(f"   Expected: {test['expected']}")
        print()

    print("=" * 60)
    print("💡 LESSONS:")
    print("   - Clear spec → Correct code")
    print("   - Type hints included automatically")
    print("   - Docstring with examples generated")
    print("   - Edge cases handled")
    print("   - AI-generated code is often well-documented!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_specification_pattern()
