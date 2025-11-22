#!/usr/bin/env python3
"""
Module 4: Code Optimization Examples
Shows before/after optimizations in various scenarios.

Demonstrates:
- Algorithmic optimizations
- Python idioms
- Memory optimizations
- Database query patterns (conceptual)
"""

import sys
from typing import List, Dict


def example_1_algorithm_optimization():
    """O(n²) → O(n) optimization."""
    print("\n--- Example 1: Find Common Elements ---\n")

    print("❌ SLOW O(n²):")
    print("""
def find_common_slow(list1, list2):
    common = []
    for item in list1:
        if item in list2:  # O(n) lookup each time!
            common.append(item)
    return common
    """)

    print("✅ FAST O(n):")
    print("""
def find_common_fast(list1, list2):
    set2 = set(list2)  # O(n) to build, O(1) lookup
    return [item for item in list1 if item in set2]
    """)

    def find_common_fast(list1, list2):
        set2 = set(list2)
        return [item for item in list1 if item in set2]

    result = find_common_fast([1, 2, 3], [2, 3, 4])
    print(f"Result: {result}")
    print("Speedup: ~100x for large lists!\n")


def example_2_early_return():
    """Use early returns to avoid unnecessary work."""
    print("\n--- Example 2: Early Return Pattern ---\n")

    print("❌ DOES UNNECESSARY WORK:")
    print("""
def is_valid(data):
    valid = True
    if not data:
        valid = False
    if not isinstance(data, dict):
        valid = False
    if "required_field" not in data:
        valid = False
    return valid
    """)

    print("✅ EARLY RETURN:")
    print("""
def is_valid(data):
    if not data:
        return False
    if not isinstance(data, dict):
        return False
    if "required_field" not in data:
        return False
    return True
    """)
    print("Exits immediately when condition fails!\n")


def example_3_avoid_repeated_calculations():
    """Cache repeated calculations."""
    print("\n--- Example 3: Avoid Repeated Calculations ---\n")

    print("❌ RECALCULATES:")
    print("""
for item in items:
    total = sum(all_items)  # Recalculates every iteration!
    percentage = item / total
    """)

    print("✅ CALCULATE ONCE:")
    print("""
total = sum(all_items)  # Calculate once!
for item in items:
    percentage = item / total
    """)
    print("Move invariant calculations outside loops!\n")


def example_4_database_patterns():
    """Database query optimization patterns."""
    print("\n--- Example 4: Database Optimization Patterns ---\n")

    print("❌ N+1 QUERY PROBLEM:")
    print("""
users = User.query.all()  # 1 query
for user in users:
    posts = user.posts.all()  # N queries!
# Total: 1 + N queries
    """)

    print("✅ EAGER LOADING:")
    print("""
users = User.query.options(
    joinedload(User.posts)
).all()  # 1 query with JOIN!
for user in users:
    posts = user.posts  # No additional query
# Total: 1 query
    """)
    print("Always use eager loading for relationships!\n")


def example_5_memory_efficiency():
    """Memory-efficient patterns."""
    print("\n--- Example 5: Memory Efficiency ---\n")

    print("❌ LOADS ALL INTO MEMORY:")
    print("""
def process_large_file(filename):
    lines = open(filename).readlines()  # Entire file in memory!
    for line in lines:
        process(line)
    """)

    print("✅ STREAMS LINE BY LINE:")
    print("""
def process_large_file(filename):
    with open(filename) as f:
        for line in f:  # One line at a time!
            process(line)
    """)
    print("Can handle files larger than RAM!\n")


def main():
    """Run optimization examples."""
    print("=" * 60)
    print("  Code Optimization Examples")
    print("=" * 60)
    print()

    example_1_algorithm_optimization()
    example_2_early_return()
    example_3_avoid_repeated_calculations()
    example_4_database_patterns()
    example_5_memory_efficiency()

    print("Key Optimization Patterns:")
    print("1. O(n²) → O(n): Use sets/dicts for lookups")
    print("2. Early returns: Fail fast, avoid unnecessary work")
    print("3. Hoist invariants: Move calculations outside loops")
    print("4. N+1 queries: Use eager loading/joins")
    print("5. Memory: Stream data, use generators")
    print("\nAI can suggest all of these patterns!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
