#!/usr/bin/env python3
"""
Module 4: Logic Error Debugging with AI
Demonstrates how to use AI to find and fix logic errors.

This example shows:
- Off-by-one errors
- Wrong conditional logic
- Edge case handling
- Systematic debugging with AI
"""

from typing import List
import sys


def print_header(title: str) -> None:
    """Print formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_example(num: int, title: str) -> None:
    """Print example header."""
    print(f"\n--- Example {num}: {title} ---\n")


# ==============================================================================
# Example 1: Off-by-One Error
# ==============================================================================

def example_1_off_by_one():
    """Demonstrate fixing off-by-one errors."""
    print_example(1, "Off-by-One Error")

    print("❌ BUGGY CODE:")
    print("""
def get_first_n_items(items: List[str], n: int) -> List[str]:
    '''Get first n items from list.'''
    return items[0:n-1]  # Bug! Returns n-1 items, not n

result = get_first_n_items(['a', 'b', 'c', 'd'], 3)
# Expected: ['a', 'b', 'c']
# Actual: ['a', 'b']  # Only 2 items!
    """)

    print("🤖 AI Analysis:")
    print("   Problem: items[0:n-1] returns n-1 items, not n")
    print("   Why: Python slicing is exclusive of end index")
    print("   Fix: Use items[0:n] or items[:n]")

    print("\n✅ FIXED CODE:")
    def get_first_n_items(items: List[str], n: int) -> List[str]:
        """Get first n items from list."""
        return items[:n]  # Fixed!

    result = get_first_n_items(['a', 'b', 'c', 'd'], 3)
    print(f"""
def get_first_n_items(items: List[str], n: int) -> List[str]:
    return items[:n]  # Correct slicing

result = get_first_n_items(['a', 'b', 'c', 'd'], 3)
print(result)  # {result}
    """)

    assert len(result) == 3, f"Expected 3 items, got {len(result)}"
    assert result == ['a', 'b', 'c'], f"Wrong result: {result}"
    print("✓ Test passed!")


# ==============================================================================
# Example 2: Wrong Conditional Logic
# ==============================================================================

def example_2_wrong_conditional():
    """Demonstrate fixing incorrect conditionals."""
    print_example(2, "Wrong Conditional Logic")

    print("❌ BUGGY CODE:")
    print("""
def is_valid_password(password: str) -> bool:
    '''Check if password meets requirements.'''
    has_length = len(password) >= 8
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)

    # Bug: Using OR instead of AND!
    return has_length or has_digit or has_upper

# "12345678" passes (has length + digits, but no uppercase!)
# Should fail: needs all three conditions
    """)

    print("🤖 AI Analysis:")
    print("   Problem: Using OR means ANY condition passing is enough")
    print("   Should use AND so ALL conditions must pass")
    print("   Fix: Change 'or' to 'and'")

    print("\n✅ FIXED CODE:")
    def is_valid_password(password: str) -> bool:
        """Check if password meets all requirements."""
        has_length = len(password) >= 8
        has_digit = any(c.isdigit() for c in password)
        has_upper = any(c.isupper() for c in password)
        return has_length and has_digit and has_upper  # Fixed!

    test_cases = [
        ("12345678", False),  # No uppercase
        ("Password", False),  # No digit
        ("Pass1", False),  # Too short
        ("Password1", True),  # Valid!
    ]

    print("""
def is_valid_password(password: str) -> bool:
    has_length = len(password) >= 8
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    return has_length and has_digit and has_upper  # All must be True
    """)

    for password, expected in test_cases:
        result = is_valid_password(password)
        status = "✓" if result == expected else "✗"
        print(f"{status} is_valid_password('{password}') = {result} (expected {expected})")
        assert result == expected, f"Test failed for '{password}'"

    print("\n✓ All tests passed!")


# ==============================================================================
# Example 3: Edge Case - Empty List
# ==============================================================================

def example_3_edge_case_empty():
    """Demonstrate handling edge cases."""
    print_example(3, "Edge Case: Empty List")

    print("❌ BUGGY CODE:")
    print("""
def find_max(numbers: List[int]) -> int:
    '''Find maximum number in list.'''
    max_val = numbers[0]  # Crashes if list is empty!
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

result = find_max([])  # IndexError!
    """)

    print("🤖 AI Analysis:")
    print("   Problem: numbers[0] fails when list is empty")
    print("   Fix: Check if list is empty first")
    print("   Consider: What should empty list return? None? Raise exception?")

    print("\n✅ FIXED CODE:")
    def find_max(numbers: List[int]) -> int:
        """Find maximum number in list."""
        if not numbers:
            raise ValueError("Cannot find max of empty list")
        max_val = numbers[0]
        for num in numbers[1:]:
            if num > max_val:
                max_val = num
        return max_val

    # Alternative: Use Python's built-in max()
    def find_max_v2(numbers: List[int]) -> int:
        """Find maximum using built-in."""
        if not numbers:
            raise ValueError("Cannot find max of empty list")
        return max(numbers)

    print("""
def find_max(numbers: List[int]) -> int:
    if not numbers:  # Edge case check!
        raise ValueError("Cannot find max of empty list")
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val
    """)

    # Test normal case
    result1 = find_max([3, 1, 4, 1, 5])
    print(f"\nfind_max([3, 1, 4, 1, 5]) = {result1}")
    assert result1 == 5, "Normal case failed"

    # Test edge case
    try:
        find_max([])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"find_max([]) → ValueError: {e}")
        print("✓ Edge case handled correctly!")


# ==============================================================================
# Example 4: Wrong Loop Bounds
# ==============================================================================

def example_4_wrong_loop_bounds():
    """Demonstrate fixing loop bound errors."""
    print_example(4, "Wrong Loop Bounds")

    print("❌ BUGGY CODE:")
    print("""
def sum_pairs(numbers: List[int]) -> int:
    '''Sum adjacent pairs: [1,2,3,4] → (1+2)+(3+4) = 10'''
    total = 0
    for i in range(len(numbers)):  # Bug: goes out of bounds!
        total += numbers[i] + numbers[i+1]
    return total

result = sum_pairs([1, 2, 3, 4])  # IndexError on last iteration!
    """)

    print("🤖 AI Analysis:")
    print("   Problem: range(len(numbers)) includes last index")
    print("   numbers[i+1] on last iteration goes out of bounds")
    print("   Fix: range(len(numbers) - 1) or range(0, len(numbers), 2)")

    print("\n✅ FIXED CODE:")
    def sum_pairs(numbers: List[int]) -> int:
        """Sum adjacent pairs."""
        total = 0
        for i in range(0, len(numbers) - 1, 2):  # Step by 2, stop before last
            total += numbers[i] + numbers[i+1]
        return total

    result = sum_pairs([1, 2, 3, 4])
    print(f"""
def sum_pairs(numbers: List[int]) -> int:
    total = 0
    for i in range(0, len(numbers) - 1, 2):  # Fixed bounds!
        total += numbers[i] + numbers[i+1]
    return total

result = sum_pairs([1, 2, 3, 4])
print(result)  # {result} = (1+2)+(3+4) = 10
    """)

    assert result == 10, f"Expected 10, got {result}"
    print("✓ Test passed!")


# ==============================================================================
# Example 5: Boundary Condition
# ==============================================================================

def example_5_boundary_condition():
    """Demonstrate fixing boundary condition bugs."""
    print_example(5, "Boundary Condition")

    print("❌ BUGGY CODE:")
    print("""
def is_valid_score(score: int) -> bool:
    '''Check if score is in valid range [0, 100].'''
    return score > 0 and score < 100  # Bug: excludes 0 and 100!

# is_valid_score(0) → False  (should be True!)
# is_valid_score(100) → False  (should be True!)
    """)

    print("🤖 AI Analysis:")
    print("   Problem: Using > and < excludes boundary values")
    print("   Range [0, 100] means inclusive of both 0 and 100")
    print("   Fix: Use >= and <=")

    print("\n✅ FIXED CODE:")
    def is_valid_score(score: int) -> bool:
        """Check if score is in valid range [0, 100] inclusive."""
        return score >= 0 and score <= 100  # Fixed!
        # Alternative: return 0 <= score <= 100  # Python's chained comparison

    test_cases = [
        (-1, False),
        (0, True),   # Boundary
        (50, True),
        (100, True),  # Boundary
        (101, False),
    ]

    print("""
def is_valid_score(score: int) -> bool:
    return 0 <= score <= 100  # Inclusive boundaries

Test cases:
    """)

    for score, expected in test_cases:
        result = is_valid_score(score)
        status = "✓" if result == expected else "✗"
        print(f"{status} is_valid_score({score:3d}) = {result:5} (expected {expected})")
        assert result == expected, f"Test failed for score={score}"

    print("\n✓ All boundary tests passed!")


# ==============================================================================
# Example 6: Variable Uninitialized in Branch
# ==============================================================================

def example_6_uninitialized_variable():
    """Demonstrate fixing uninitialized variable bugs."""
    print_example(6, "Uninitialized Variable")

    print("❌ BUGGY CODE:")
    print("""
def calculate_discount(total: float) -> float:
    '''Calculate discount based on total.'''
    if total > 100:
        discount = total * 0.1
    return total - discount  # UnboundLocalError if total <= 100!

result = calculate_discount(50)  # Crashes!
    """)

    print("🤖 AI Analysis:")
    print("   Problem: 'discount' only defined in if-branch")
    print("   When total <= 100, discount is not defined")
    print("   Fix: Initialize discount before the if statement")

    print("\n✅ FIXED CODE:")
    def calculate_discount(total: float) -> float:
        """Calculate discount with proper initialization."""
        discount = 0.0  # Initialize for all cases!
        if total > 100:
            discount = total * 0.1
        return total - discount

    test_cases = [
        (50, 50.0),    # No discount
        (100, 100.0),  # No discount (not > 100)
        (150, 135.0),  # 10% discount
        (200, 180.0),  # 10% discount
    ]

    print("""
def calculate_discount(total: float) -> float:
    discount = 0.0  # Initialize first!
    if total > 100:
        discount = total * 0.1
    return total - discount

Test cases:
    """)

    for total, expected in test_cases:
        result = calculate_discount(total)
        status = "✓" if abs(result - expected) < 0.01 else "✗"
        print(f"{status} calculate_discount({total}) = ${result:.2f} (expected ${expected:.2f})")
        assert abs(result - expected) < 0.01, f"Test failed for total={total}"

    print("\n✓ All tests passed!")


# ==============================================================================
# Main Function
# ==============================================================================

def main():
    """Run all logic debugging examples."""
    print_header("Module 4: Logic Error Debugging with AI")

    print("""
This module demonstrates how AI helps find logic errors with proper context.

AI Effectiveness for Logic Errors: ⭐⭐⭐⭐ (Good with context!)

Why AI is good at this:
- Recognizes common logic patterns
- Spots off-by-one errors
- Identifies missing edge cases
- Suggests systematic fixes

Key: Provide good context (expected vs actual behavior)
    """)

    try:
        example_1_off_by_one()
        example_2_wrong_conditional()
        example_3_edge_case_empty()
        example_4_wrong_loop_bounds()
        example_5_boundary_condition()
        example_6_uninitialized_variable()

        print_header("All Examples Completed Successfully!")
        print("""
Key Takeaways:
1. AI is GOOD at logic errors when given expected vs actual behavior
2. Provide test cases showing the bug
3. AI spots common patterns (off-by-one, wrong operators, etc.)
4. Always test edge cases after fixing
5. Consider all branches and conditions

Next Steps:
- Practice creating minimal reproductions
- Learn to describe expected behavior clearly
- Test edge cases systematically
- Move on to performance profiling!
        """)

        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
