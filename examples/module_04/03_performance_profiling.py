#!/usr/bin/env python3
"""
Module 4: Performance Profiling and Optimization with AI
Demonstrates using AI to analyze and fix performance bottlenecks.

This example shows:
- Profiling with cProfile
- Identifying O(n²) → O(n) optimizations
- AI-assisted algorithm optimization
- Before/after comparisons
"""

import cProfile
import pstats
import io
import time
from typing import List
import sys


def print_header(title: str) -> None:
    """Print formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def profile_function(func, *args):
    """Profile a function and return stats."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args)
    profiler.disable()

    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(10)  # Top 10

    return result, s.getvalue()


# ==============================================================================
# Example 1: O(n²) → O(n) - Duplicate Detection
# ==============================================================================

def example_1_duplicate_detection():
    """Optimize duplicate detection from O(n²) to O(n)."""
    print("\n--- Example 1: Duplicate Detection ---\n")

    print("❌ SLOW CODE (O(n²)):")
    print("""
def has_duplicates_slow(items: List[int]) -> bool:
    '''Check for duplicates using nested loops.'''
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False
    """)

    def has_duplicates_slow(items: List[int]) -> bool:
        """O(n²) nested loop approach."""
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i] == items[j]:
                    return True
        return False

    print("🤖 AI Analysis:")
    print("   Complexity: O(n²) - nested loops over same list")
    print("   Bottleneck: Comparing every pair of items")
    print("   Fix: Use set for O(n) lookup")

    print("\n✅ OPTIMIZED CODE (O(n)):")
    print("""
def has_duplicates_fast(items: List[int]) -> bool:
    '''Check for duplicates using set.'''
    return len(items) != len(set(items))
    """)

    def has_duplicates_fast(items: List[int]) -> bool:
        """O(n) set-based approach."""
        return len(items) != len(set(items))

    # Benchmark
    test_data = list(range(1000)) + [500]  # Duplicate at end

    start = time.time()
    result_slow = has_duplicates_slow(test_data)
    time_slow = time.time() - start

    start = time.time()
    result_fast = has_duplicates_fast(test_data)
    time_fast = time.time() - start

    print(f"""
Benchmark (1000 items with duplicate):
- Slow O(n²): {time_slow * 1000:.2f}ms
- Fast O(n):  {time_fast * 1000:.2f}ms
- Speedup:    {time_slow / time_fast:.1f}x faster!
    """)

    assert result_slow == result_fast == True
    print("✓ Both methods correct, fast version is", f"{time_slow / time_fast:.0f}x faster!")


# ==============================================================================
# Example 2: Inefficient String Concatenation
# ==============================================================================

def example_2_string_concat():
    """Optimize string concatenation."""
    print("\n--- Example 2: String Concatenation ---\n")

    print("❌ SLOW CODE (O(n²)):")
    print("""
def join_strings_slow(strings: List[str]) -> str:
    '''Concatenate strings using +'''
    result = ""
    for s in strings:
        result = result + s  # Creates new string each time!
    return result
    """)

    def join_strings_slow(strings: List[str]) -> str:
        """Slow string concatenation."""
        result = ""
        for s in strings:
            result = result + s
        return result

    print("🤖 AI Analysis:")
    print("   Problem: Strings are immutable - each + creates a new string")
    print("   Complexity: O(n²) - copying grows with each iteration")
    print("   Fix: Use ''.join() for O(n) performance")

    print("\n✅ OPTIMIZED CODE (O(n)):")
    print("""
def join_strings_fast(strings: List[str]) -> str:
    '''Use built-in join method.'''
    return ''.join(strings)
    """)

    def join_strings_fast(strings: List[str]) -> str:
        """Fast string joining."""
        return ''.join(strings)

    # Benchmark
    test_data = ["x" * 100 for _ in range(100)]

    start = time.time()
    result_slow = join_strings_slow(test_data)
    time_slow = time.time() - start

    start = time.time()
    result_fast = join_strings_fast(test_data)
    time_fast = time.time() - start

    print(f"""
Benchmark (100 strings, 100 chars each):
- Slow (+):   {time_slow * 1000:.2f}ms
- Fast (join): {time_fast * 1000:.2f}ms
- Speedup:     {time_slow / time_fast:.1f}x faster!
    """)

    assert result_slow == result_fast
    print("✓ Optimized version is", f"{time_slow / time_fast:.0f}x faster!")


# ==============================================================================
# Example 3: List Comprehension vs Loop
# ==============================================================================

def example_3_list_comprehension():
    """Compare list comprehension vs loop."""
    print("\n--- Example 3: List Comprehension vs Loop ---\n")

    print("❌ SLOWER CODE:")
    print("""
def squares_loop(n: int) -> List[int]:
    result = []
    for i in range(n):
        result.append(i * i)
    return result
    """)

    def squares_loop(n: int) -> List[int]:
        """Using loop and append."""
        result = []
        for i in range(n):
            result.append(i * i)
        return result

    print("🤖 AI Analysis:")
    print("   Loop with append: Multiple function calls, slower")
    print("   Fix: List comprehension is optimized in C")

    print("\n✅ FASTER CODE:")
    print("""
def squares_comprehension(n: int) -> List[int]:
    return [i * i for i in range(n)]
    """)

    def squares_comprehension(n: int) -> List[int]:
        """Using list comprehension."""
        return [i * i for i in range(n)]

    # Benchmark
    n = 10000

    start = time.time()
    result_loop = squares_loop(n)
    time_loop = time.time() - start

    start = time.time()
    result_comp = squares_comprehension(n)
    time_comp = time.time() - start

    print(f"""
Benchmark (10,000 squares):
- Loop:         {time_loop * 1000:.2f}ms
- Comprehension: {time_comp * 1000:.2f}ms
- Speedup:       {time_loop / time_comp:.1f}x faster!
    """)

    assert result_loop == result_comp
    print("✓ List comprehension is", f"{time_loop / time_comp:.1f}x faster!")


# ==============================================================================
# Example 4: Generator for Memory Efficiency
# ==============================================================================

def example_4_generator():
    """Compare list vs generator for memory."""
    print("\n--- Example 4: Generator vs List ---\n")

    print("❌ MEMORY-HEAVY CODE:")
    print("""
def get_squares_list(n: int) -> List[int]:
    '''Returns list - stores all in memory.'''
    return [i * i for i in range(n)]

# For n=1,000,000: ~8MB in memory
    """)

    def get_squares_list(n: int) -> List[int]:
        """Returns list - all in memory."""
        return [i * i for i in range(n)]

    print("🤖 AI Analysis:")
    print("   Problem: List stores all values in memory")
    print("   If only iterating once, wasteful")
    print("   Fix: Use generator for lazy evaluation")

    print("\n✅ MEMORY-EFFICIENT CODE:")
    print("""
def get_squares_generator(n: int):
    '''Returns generator - computes on demand.'''
    return (i * i for i in range(n))

# For n=1,000,000: ~200 bytes (just the generator object!)
    """)

    def get_squares_generator(n: int):
        """Returns generator - lazy evaluation."""
        return (i * i for i in range(n))

    # Compare memory (conceptually)
    import sys

    n = 100
    list_result = get_squares_list(n)
    gen_result = get_squares_generator(n)

    list_size = sys.getsizeof(list_result)
    gen_size = sys.getsizeof(gen_result)

    print(f"""
Memory comparison (n=100):
- List:      {list_size} bytes
- Generator: {gen_size} bytes
- Savings:   {(list_size / gen_size):.1f}x less memory!

For n=1,000,000:
- List:      ~8MB
- Generator: ~200 bytes
    """)

    # Verify they produce same results
    list_result2 = get_squares_list(n)
    gen_result2 = list(get_squares_generator(n))
    assert list_result2 == gen_result2
    print("✓ Both produce same results, generator uses less memory!")


# ==============================================================================
# Example 5: Caching with @lru_cache
# ==============================================================================

def example_5_caching():
    """Demonstrate caching for expensive functions."""
    print("\n--- Example 5: Caching with @lru_cache ---\n")

    print("❌ SLOW CODE (Recomputes Every Time):")
    print("""
def fibonacci_slow(n: int) -> int:
    '''Compute nth Fibonacci number (no caching).'''
    if n < 2:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)

# fibonacci_slow(30) takes ~1 second (exponential time!)
    """)

    def fibonacci_slow(n: int) -> int:
        """No caching - exponential time."""
        if n < 2:
            return n
        return fibonacci_slow(n-1) + fibonacci_slow(n-2)

    print("🤖 AI Analysis:")
    print("   Problem: Recalculates same values repeatedly")
    print("   Complexity: O(2^n) - exponential!")
    print("   Fix: Add @lru_cache to memoize results")

    print("\n✅ OPTIMIZED CODE (With Caching):")
    print("""
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_fast(n: int) -> int:
    '''Cached Fibonacci computation.'''
    if n < 2:
        return n
    return fibonacci_fast(n-1) + fibonacci_fast(n-2)

# fibonacci_fast(30) takes <1ms! (cached results)
    """)

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def fibonacci_fast(n: int) -> int:
        """With caching - O(n) time."""
        if n < 2:
            return n
        return fibonacci_fast(n-1) + fibonacci_fast(n-2)

    # Benchmark
    n = 30

    start = time.time()
    result_slow = fibonacci_slow(n)
    time_slow = time.time() - start

    start = time.time()
    result_fast = fibonacci_fast(n)
    time_fast = time.time() - start

    print(f"""
Benchmark (Fibonacci {n}):
- No cache:   {time_slow * 1000:.2f}ms
- With cache: {time_fast * 1000:.2f}ms
- Speedup:    {time_slow / time_fast:.0f}x faster!

Result: {result_fast}
    """)

    assert result_slow == result_fast
    print(f"✓ Caching makes it {time_slow / time_fast:.0f}x faster!")


# ==============================================================================
# Main Function
# ==============================================================================

def main():
    """Run all performance profiling examples."""
    print_header("Module 4: Performance Profiling & Optimization")

    print("""
This module demonstrates how to identify and fix performance bottlenecks with AI.

AI Effectiveness for Performance: ⭐⭐⭐ (Moderate - needs profiling data!)

Why AI helps:
- Spots obvious algorithmic issues (O(n²) → O(n))
- Suggests Python idioms (comprehensions, generators)
- Recommends caching strategies
- Identifies inefficient patterns

Limitation: Can't profile your actual code - you need to provide data!
    """)

    try:
        example_1_duplicate_detection()
        example_2_string_concat()
        example_3_list_comprehension()
        example_4_generator()
        example_5_caching()

        print_header("All Examples Completed Successfully!")
        print("""
Key Takeaways:
1. ALWAYS profile first - don't guess at bottlenecks
2. AI is great at spotting O(n²) → O(n) optimizations
3. Provide profiling data to AI for best results
4. Measure before and after to verify improvements
5. Optimize the 20% of code that takes 80% of time

Common Optimizations:
- O(n²) → O(n): Use sets/dicts instead of nested loops
- String concat: Use ''.join() not +
- List building: Use comprehensions not loops
- Memory: Use generators for large sequences
- Repeated calculations: Use @lru_cache

Next Steps:
- Profile your own code with cProfile
- Find the bottleneck (80/20 rule)
- Ask AI for optimization strategies
- Measure improvements
- Move on to async debugging!
        """)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
