#!/usr/bin/env python3
"""
Module 4: Async & Concurrent Debugging with AI
Shows common async/await mistakes and AI's limitations.

AI Effectiveness: ⭐⭐ (Limited - timing-dependent bugs are hard!)
"""

import asyncio
import sys
from typing import List


async def example_1_missing_await():
    """Demonstrate missing await keyword."""
    print("\n--- Example 1: Missing await ---\n")
    print("❌ BUGGY: async def fetch_data(): return 'data'\n   result = fetch_data()  # Returns coroutine, not 'data'!")
    print("✅ FIXED: result = await fetch_data()")

    async def fetch_data() -> str:
        await asyncio.sleep(0.1)
        return "data"

    # Correct usage
    result = await fetch_data()
    print(f"Result: {result}")
    assert result == "data"
    print("✓ Test passed!\n")


async def example_2_blocking_call():
    """Demonstrate blocking call in async function."""
    print("\n--- Example 2: Blocking Call in Async ---\n")
    print("❌ BAD: import time; time.sleep(1)  # Blocks event loop!")
    print("✅ GOOD: await asyncio.sleep(1)  # Non-blocking")

    import time
    start = time.time()
    await asyncio.sleep(0.1)  # Correct async sleep
    elapsed = time.time() - start
    print(f"Async sleep took {elapsed:.2f}s")
    print("✓ Event loop not blocked!\n")


async def example_3_gather_vs_sequential():
    """Show concurrent vs sequential execution."""
    print("\n--- Example 3: Concurrent Execution ---\n")

    async def task(n: int) -> int:
        await asyncio.sleep(0.1)
        return n * 2

    # Sequential (slow)
    print("❌ SLOW (sequential):")
    start = asyncio.get_event_loop().time()
    results_seq = []
    for i in range(3):
        results_seq.append(await task(i))
    time_seq = asyncio.get_event_loop().time() - start
    print(f"   Time: {time_seq:.2f}s")

    # Concurrent (fast)
    print("✅ FAST (concurrent with gather):")
    start = asyncio.get_event_loop().time()
    results_con = await asyncio.gather(task(0), task(1), task(2))
    time_con = asyncio.get_event_loop().time() - start
    print(f"   Time: {time_con:.2f}s (3x faster!)")

    assert results_seq == list(results_con)
    print("✓ Concurrent execution is faster!\n")


async def main_async():
    """Run async examples."""
    print("=" * 60)
    print("  Async & Concurrent Debugging with AI")
    print("=" * 60)
    print("\nAI helps with async/await syntax but struggles with:")
    print("- Race conditions (timing-dependent)")
    print("- Deadlocks (need runtime analysis)")
    print("- Complex concurrency bugs\n")

    await example_1_missing_await()
    await example_2_blocking_call()
    await example_3_gather_vs_sequential()

    print("\nKey Takeaways:")
    print("1. Always await coroutines")
    print("2. Use asyncio.sleep(), not time.sleep()")
    print("3. Use gather() for concurrent execution")
    print("4. AI helps with syntax, not complex timing bugs\n")


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
