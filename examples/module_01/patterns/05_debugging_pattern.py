"""
Module 1: AI Coding Pattern #5 - Debugging Pattern

Demonstrates using AI to debug common errors.

AI DEBUGGING PROMPTS:
---------------------
1. "This code throws [error]. Why?"
2. "Why is my function returning None?"
3. "Find the bug in this implementation"
4. "This code is slow. How can I optimize it?"
"""

from typing import List, Dict, Optional


# BUG EXAMPLE 1: NoneType Error (very common!)
class UserDatabase:
    """Mock user database."""

    def __init__(self):
        self.users = {
            1: {"name": "Alice", "email": "alice@example.com"},
            2: {"name": "Bob", "email": "bob@example.com"},
        }

    def fetch_user(self, user_id: int) -> Optional[Dict]:
        """Fetch user by ID, returns None if not found."""
        return self.users.get(user_id)


def get_user_name_buggy(db: UserDatabase, user_id: int) -> str:
    """
    BUGGY VERSION: Throws TypeError for missing users!

    ERROR: TypeError: 'NoneType' object is not subscriptable

    AI DEBUG EXPLANATION:
    ---------------------
    The error occurs at: user['name']

    WHY: db.fetch_user() returns None when user_id doesn't exist,
    but we try to subscript None with ['name'].

    WHEN: Always fails when user_id is not in database.

    FIX: Check for None before accessing!
    """
    user = db.fetch_user(user_id)
    return user['name']  # ← CRASH if user is None!


def get_user_name_fixed(db: UserDatabase, user_id: int) -> str:
    """
    FIXED VERSION: Handles None properly.

    AI SUGGESTED FIX:
    -----------------
    1. Check if user is None
    2. Return appropriate default or raise exception
    3. Add type hints to make contract clear
    """
    user = db.fetch_user(user_id)
    if user is None:
        return "Unknown User"
    return user['name']


# BUG EXAMPLE 2: Off-by-one error in list operations
def get_last_n_items_buggy(items: List[str], n: int) -> List[str]:
    """
    BUGGY VERSION: Returns n+1 items instead of n!

    EXAMPLE:
    get_last_n_items_buggy(['a', 'b', 'c', 'd', 'e'], 2)
    Expected: ['d', 'e']
    Actual:   ['c', 'd', 'e']  # ← 3 items instead of 2!

    AI DEBUG EXPLANATION:
    ---------------------
    BUG: items[-n:] when n=2 starts at index -2, which gives last 2 items.
    But items[-n-1:] starts at index -3, giving last 3 items!

    The logic is inverted. We want items[-n:], not items[-n-1:].
    """
    return items[-n-1:]  # ← BUG HERE!


def get_last_n_items_fixed(items: List[str], n: int) -> List[str]:
    """
    FIXED VERSION: Returns exactly n items.

    AI SUGGESTED FIX:
    -----------------
    Use items[-n:] for last n items.
    Also handle edge cases: n > len(items), n <= 0.
    """
    if n <= 0:
        return []
    return items[-n:]


# BUG EXAMPLE 3: Mutable default argument (subtle Python gotcha!)
def add_item_buggy(item: str, items: List[str] = []) -> List[str]:
    """
    BUGGY VERSION: Mutable default argument trap!

    WEIRD BEHAVIOR:
    add_item_buggy('a')  → ['a']
    add_item_buggy('b')  → ['a', 'b']  # ← Unexpected! Should be ['b']

    AI DEBUG EXPLANATION:
    ---------------------
    DEFAULT ARGUMENT IS EVALUATED ONCE at function definition!
    The default list [] is created once and reused across all calls.

    This is a famous Python gotcha: never use mutable defaults!

    FIX: Use None as default, create new list inside function.
    """
    items.append(item)
    return items


def add_item_fixed(item: str, items: List[str] = None) -> List[str]:
    """
    FIXED VERSION: Use None as default.

    AI SUGGESTED FIX:
    -----------------
    1. Default to None (immutable)
    2. Create new list if None
    3. Now each call gets its own list
    """
    if items is None:
        items = []
    items.append(item)
    return items


# BUG EXAMPLE 4: Logic error in conditional
def is_valid_age_buggy(age: int) -> bool:
    """
    BUGGY VERSION: Logic error allows negative ages!

    BUG: age < 0 or age > 150 returns True for negative ages
    This is wrong! Negative age should be invalid (False).

    AI DEBUG EXPLANATION:
    ---------------------
    Logical error: "or" should be "and"

    Current: age < 0 or age > 150
    - age = -5: -5 < 0 is True → returns True (WRONG!)
    - age = 200: 200 > 150 is True → returns True (WRONG!)

    The condition is checking if age is OUT of range,
    but we want to check if it's IN range.

    FIX: Use "and" or invert the logic.
    """
    return age < 0 or age > 150  # ← BUG: should use "and" or invert!


def is_valid_age_fixed(age: int) -> bool:
    """
    FIXED VERSION: Correct logic.

    AI SUGGESTED FIXES (two approaches):
    -----------------------------------
    Approach 1: return 0 <= age <= 150 (Pythonic!)
    Approach 2: return age >= 0 and age <= 150 (explicit)

    Both are correct. Approach 1 is more Pythonic.
    """
    return 0 <= age <= 150


def demonstrate_debugging_pattern():
    """
    Demonstrates the Debugging Pattern.

    KEY INSIGHT: Paste code + error → AI explains and fixes!
    """
    print("=" * 60)
    print("AI CODING PATTERN #5: DEBUGGING PATTERN")
    print("=" * 60)
    print()
    print("✨ CONCEPT: Paste error + code → AI debugs and explains")
    print()

    db = UserDatabase()

    # Example 1: NoneType Error
    print("BUG 1: NoneType Error")
    print("-" * 60)
    try:
        result = get_user_name_buggy(db, 999)
    except TypeError as e:
        print(f"  ❌ BUGGY version crashed: {e}")

    result = get_user_name_fixed(db, 999)
    print(f"  ✅ FIXED version: '{result}'")
    print()

    # Example 2: Off-by-one error
    print("BUG 2: Off-by-one Error")
    print("-" * 60)
    items = ['a', 'b', 'c', 'd', 'e']
    buggy_result = get_last_n_items_buggy(items, 2)
    fixed_result = get_last_n_items_fixed(items, 2)
    print(f"  Items: {items}")
    print(f"  ❌ BUGGY (wanted 2, got {len(buggy_result)}): {buggy_result}")
    print(f"  ✅ FIXED (got 2): {fixed_result}")
    print()

    # Example 3: Mutable default argument
    print("BUG 3: Mutable Default Argument")
    print("-" * 60)
    print("  ❌ BUGGY version:")
    result1 = add_item_buggy('first')
    result2 = add_item_buggy('second')  # ← Reuses same list!
    print(f"     Call 1: {result1}")
    print(f"     Call 2: {result2} (Oops! Contains 'first' too!)")

    print("  ✅ FIXED version:")
    result3 = add_item_fixed('first')
    result4 = add_item_fixed('second')  # ← New list each time
    print(f"     Call 1: {result3}")
    print(f"     Call 2: {result4} (Correct!)")
    print()

    # Example 4: Logic error
    print("BUG 4: Logic Error in Conditional")
    print("-" * 60)
    test_ages = [-5, 0, 25, 150, 200]
    print("  Testing ages: ", test_ages)
    print("  ❌ BUGGY results:")
    for age in test_ages:
        result = is_valid_age_buggy(age)
        print(f"     Age {age:3}: {result}")

    print("  ✅ FIXED results:")
    for age in test_ages:
        result = is_valid_age_fixed(age)
        status = "Valid" if result else "Invalid"
        print(f"     Age {age:3}: {status}")
    print()

    print("=" * 60)
    print("💡 LESSONS:")
    print("   - Paste error message + code → AI finds bug")
    print("   - AI explains WHY the bug occurs")
    print("   - AI suggests multiple fix approaches")
    print("   - Much faster than Stack Overflow search")
    print("   - AI catches subtle bugs (mutable defaults, etc.)")
    print("   - Great for learning from mistakes!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_debugging_pattern()
