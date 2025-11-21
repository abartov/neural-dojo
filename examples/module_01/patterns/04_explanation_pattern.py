"""
Module 1: AI Coding Pattern #4 - Explanation Pattern

Demonstrates using AI to understand and explain code.

AI PROMPT EXAMPLES:
-------------------
1. "Explain this code line by line: [code]"
2. "What does this algorithm do?"
3. "Why is this code inefficient?"
4. "What are the edge cases this code handles?"
"""

import time
from typing import List, Callable
from functools import wraps


# Example 1: Complex one-liner that benefits from explanation
def fibonacci_recursive(n: int) -> int:
    """
    Fibonacci using recursion (elegant but inefficient).

    AI EXPLANATION:
    ---------------
    This is a direct implementation of the mathematical definition:
    - fib(0) = 0 (base case)
    - fib(1) = 1 (base case)
    - fib(n) = fib(n-1) + fib(n-2) for n > 1

    TIME COMPLEXITY: O(2^n) - exponential!
    Each call branches into two more calls, creating exponential growth.

    Example for fib(5):
    fib(5) calls fib(4) and fib(3)
    fib(4) calls fib(3) and fib(2)
    fib(3) called twice! (and gets recalculated both times)

    This is why it's slow for larger n.
    """
    return n if n < 2 else fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


# Example 2: Optimized version (AI can explain the improvement)
def fibonacci_memoized(n: int, memo: dict = None) -> int:
    """
    Fibonacci with memoization (much faster).

    AI EXPLANATION OF IMPROVEMENT:
    -------------------------------
    This uses "memoization" - caching previously computed results.

    KEY INSIGHT: fib(3) is computed once and reused, not recalculated!

    HOW IT WORKS:
    1. Check if n is already in memo (cached)
    2. If yes, return cached result (O(1))
    3. If no, compute it and store in memo
    4. Return result

    TIME COMPLEXITY: O(n) - linear! Each value computed only once.
    SPACE COMPLEXITY: O(n) - need to store n results in memo.

    This is ~1000x faster for n=30!
    """
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n < 2:
        return n
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]


# Example 3: Decorator pattern (AI can explain this advanced concept)
def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.

    AI EXPLANATION OF DECORATORS:
    ------------------------------
    A decorator is a function that wraps another function to extend its behavior.

    HOW THIS WORKS:
    1. @timing_decorator above a function is syntax sugar for:
       func = timing_decorator(func)

    2. The decorator returns a 'wrapper' function that:
       - Records start time
       - Calls the original function
       - Records end time
       - Prints elapsed time
       - Returns original function's result

    3. @wraps(func) preserves the original function's metadata
       (name, docstring, etc.)

    PRACTICAL USE: Add timing to any function without modifying its code!
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"  {func.__name__}({args[0]}) took {end - start:.6f} seconds")
        return result
    return wrapper


# Apply decorator to both fibonacci functions
@timing_decorator
def fib_slow(n: int) -> int:
    """Timed recursive fibonacci."""
    return fibonacci_recursive(n)


@timing_decorator
def fib_fast(n: int) -> int:
    """Timed memoized fibonacci."""
    return fibonacci_memoized(n)


# Example 4: List comprehension vs traditional loop (AI explains the difference)
def squares_traditional(numbers: List[int]) -> List[int]:
    """
    Traditional loop approach.

    AI EXPLANATION:
    ---------------
    Explicit loop with temporary list:
    1. Create empty result list
    2. Iterate through each number
    3. Calculate square
    4. Append to result list
    5. Return result list

    VERBOSE but very clear what's happening.
    """
    result = []
    for num in numbers:
        result.append(num ** 2)
    return result


def squares_comprehension(numbers: List[int]) -> List[int]:
    """
    List comprehension approach.

    AI EXPLANATION:
    ---------------
    Pythonic one-liner: [expression for item in iterable]

    BENEFITS:
    - More concise (1 line vs 4)
    - Faster (optimized in CPython)
    - More readable once you're familiar
    - Functional programming style

    WHEN TO USE: Simple transformations (like this)
    WHEN NOT TO USE: Complex logic (use traditional loop)
    """
    return [num ** 2 for num in numbers]


def demonstrate_explanation_pattern():
    """
    Demonstrates the Explanation Pattern.

    KEY INSIGHT: AI is an excellent teacher! Use it to understand code.
    """
    print("=" * 60)
    print("AI CODING PATTERN #4: EXPLANATION PATTERN")
    print("=" * 60)
    print()
    print("✨ CONCEPT: Use AI to understand and learn from code")
    print()

    # Example 1: Performance comparison
    print("EXAMPLE 1: Recursive vs Memoized Fibonacci")
    print("-" * 60)
    print("Computing fib(25)...")
    result1 = fib_slow(25)
    result2 = fib_fast(25)
    print(f"  Results: {result1} (slow) vs {result2} (fast)")
    print("  → AI explained WHY memoization is 1000x faster!")
    print()

    # Example 2: Decorator explanation
    print("EXAMPLE 2: Understanding Decorators")
    print("-" * 60)
    print("The @timing_decorator is syntax sugar that wraps functions")
    print("to add timing without modifying the original function code.")
    print("  → AI explained how decorators work!")
    print()

    # Example 3: Pythonic patterns
    print("EXAMPLE 3: Traditional Loop vs List Comprehension")
    print("-" * 60)
    numbers = [1, 2, 3, 4, 5]
    result_trad = squares_traditional(numbers)
    result_comp = squares_comprehension(numbers)
    print(f"  Input: {numbers}")
    print(f"  Traditional loop:       {result_trad}")
    print(f"  List comprehension:     {result_comp}")
    print("  → AI explained when to use each approach!")
    print()

    print("=" * 60)
    print("💡 LESSONS:")
    print("   - Ask AI to explain complex code line-by-line")
    print("   - AI can identify performance issues")
    print("   - AI knows best practices and patterns")
    print("   - Use AI as your patient coding teacher")
    print("   - Great for learning new languages/frameworks")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_explanation_pattern()
