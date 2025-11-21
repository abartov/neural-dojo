"""
Module 1: AI Coding Pattern #3 - Example Pattern

Demonstrates how AI can replicate patterns from examples.

AI PROMPT USED:
---------------
"I have this function:

def get_user_name(user_id: int) -> str:
    '''Get user's name from database.'''
    user = db.get('users', user_id)
    return user['name'] if user else 'Unknown'

Write similar functions for:
- get_user_email
- get_user_age
- get_user_address

Follow the same pattern exactly."
"""

from typing import Optional, Any, Dict


# Mock database for demonstration
class MockDB:
    """Simple mock database for demonstration."""

    def __init__(self):
        self.data = {
            'users': {
                1: {'name': 'Alice', 'email': 'alice@example.com', 'age': 30, 'address': '123 Main St'},
                2: {'name': 'Bob', 'email': 'bob@example.com', 'age': 25, 'address': '456 Oak Ave'},
                3: {'name': 'Charlie', 'email': 'charlie@example.com', 'age': 35, 'address': '789 Pine Rd'},
            }
        }

    def get(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """Get record from table by id."""
        return self.data.get(table, {}).get(id)


# Initialize mock database
db = MockDB()


# ORIGINAL EXAMPLE FUNCTION
def get_user_name(user_id: int) -> str:
    """Get user's name from database."""
    user = db.get('users', user_id)
    return user['name'] if user else 'Unknown'


# AI-GENERATED FUNCTIONS (following the pattern)
def get_user_email(user_id: int) -> str:
    """Get user's email from database."""
    user = db.get('users', user_id)
    return user['email'] if user else 'Unknown'


def get_user_age(user_id: int) -> int:
    """Get user's age from database."""
    user = db.get('users', user_id)
    return user['age'] if user else 0


def get_user_address(user_id: int) -> str:
    """Get user's address from database."""
    user = db.get('users', user_id)
    return user['address'] if user else 'Unknown'


# BONUS: AI can also generate batch operations following the same pattern
def get_users_names(user_ids: list[int]) -> list[str]:
    """Get multiple users' names from database."""
    return [get_user_name(user_id) for user_id in user_ids]


def get_users_emails(user_ids: list[int]) -> list[str]:
    """Get multiple users' emails from database."""
    return [get_user_email(user_id) for user_id in user_ids]


def demonstrate_example_pattern():
    """
    Demonstrates the Example Pattern.

    KEY INSIGHT: Show AI what you want, it will replicate the pattern!
    """
    print("=" * 60)
    print("AI CODING PATTERN #3: EXAMPLE PATTERN")
    print("=" * 60)
    print()
    print("✨ CONCEPT: Show one example, AI generates similar functions")
    print()

    user_ids = [1, 2, 3, 999]  # 999 doesn't exist (test default)

    print("ORIGINAL FUNCTION: get_user_name()")
    print("-" * 60)
    for uid in user_ids:
        result = get_user_name(uid)
        print(f"  User {uid}: {result}")
    print()

    print("AI-GENERATED: get_user_email() (same pattern)")
    print("-" * 60)
    for uid in user_ids:
        result = get_user_email(uid)
        print(f"  User {uid}: {result}")
    print()

    print("AI-GENERATED: get_user_age() (same pattern)")
    print("-" * 60)
    for uid in user_ids:
        result = get_user_age(uid)
        print(f"  User {uid}: {result}")
    print()

    print("AI-GENERATED: get_user_address() (same pattern)")
    print("-" * 60)
    for uid in user_ids:
        result = get_user_address(uid)
        print(f"  User {uid}: {result}")
    print()

    print("BONUS: Batch operations (extended pattern)")
    print("-" * 60)
    batch_ids = [1, 2, 3]
    names = get_users_names(batch_ids)
    emails = get_users_emails(batch_ids)
    print(f"  Names:  {names}")
    print(f"  Emails: {emails}")
    print()

    print("=" * 60)
    print("💡 LESSONS:")
    print("   - AI excels at pattern matching")
    print("   - Show one good example → Get many similar functions")
    print("   - Consistent code style across all generated functions")
    print("   - Great for CRUD operations, API wrappers, etc.")
    print("   - AI can even extend the pattern (batch operations)")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_example_pattern()
