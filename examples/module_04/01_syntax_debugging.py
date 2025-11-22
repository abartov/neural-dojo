#!/usr/bin/env python3
"""
Module 4: Syntax & Type Debugging with AI
Demonstrates how to use AI to fix common syntax and type errors quickly.

This example shows:
- Syntax errors AI catches easily (missing colons, parentheses)
- Type mismatch debugging
- Import error resolution
- Iterative debugging workflow
"""

from typing import List, Dict, Union
import sys


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_example(num: int, title: str) -> None:
    """Print example header."""
    print(f"\n--- Example {num}: {title} ---\n")


# ==============================================================================
# Example 1: Missing Colon (Common Syntax Error)
# ==============================================================================

def example_1_missing_colon():
    """Demonstrate fixing missing colon syntax error."""
    print_example(1, "Missing Colon")

    print("❌ BUGGY CODE (commented out to prevent syntax error):")
    print("""
def greet(name)  # Missing colon!
    return f"Hello, {name}"
    """)

    print("🤖 AI Analysis:")
    print("   SyntaxError: expected ':' after function definition")
    print("   Fix: Add colon after parameter list")

    print("\n✅ FIXED CODE:")
    def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}"

    # Show the fix works
    result = greet("World")
    print(f"""
def greet(name: str) -> str:
    return f"Hello, {{name}}"

result = greet("World")
print(result)  # {result}
    """)

    assert result == "Hello, World", "Test failed!"
    print("✓ Test passed!")


# ==============================================================================
# Example 2: Type Mismatch
# ==============================================================================

def example_2_type_mismatch():
    """Demonstrate fixing type errors."""
    print_example(2, "Type Mismatch")

    print("❌ BUGGY CODE:")
    print("""
def calculate_average(numbers: List[int]) -> float:
    return sum(numbers) / len(numbers)

# Called with string instead of list!
result = calculate_average("123")  # TypeError!
    """)

    print("🤖 AI Analysis:")
    print("   TypeError: 'str' object cannot be interpreted as an integer")
    print("   Problem: Function expects List[int], got str")
    print("   Fix: Either convert string to list, or fix caller")

    print("\n✅ FIXED CODE:")
    def calculate_average(numbers: List[int]) -> float:
        """Calculate average of a list of numbers."""
        if not numbers:
            return 0.0
        return sum(numbers) / len(numbers)

    # Fix 1: Pass correct type
    result1 = calculate_average([1, 2, 3])
    print(f"""
result = calculate_average([1, 2, 3])
print(result)  # {result1}
    """)

    # Fix 2: Convert string to list if needed
    def calculate_average_from_string(numbers_str: str) -> float:
        """Calculate average from string of digits."""
        numbers = [int(ch) for ch in numbers_str if ch.isdigit()]
        return calculate_average(numbers)

    result2 = calculate_average_from_string("123")
    print(f"""
# Alternative: Convert string to numbers
result = calculate_average_from_string("123")
print(result)  # {result2}
    """)

    assert result1 == 2.0, "Test 1 failed!"
    assert result2 == 2.0, "Test 2 failed!"
    print("✓ Both tests passed!")


# ==============================================================================
# Example 3: Missing Import
# ==============================================================================

def example_3_missing_import():
    """Demonstrate fixing import errors."""
    print_example(3, "Missing Import")

    print("❌ BUGGY CODE:")
    print("""
def parse_config(config_str: str) -> Dict:
    # json not imported!
    return json.loads(config_str)  # NameError!
    """)

    print("🤖 AI Analysis:")
    print("   NameError: name 'json' is not defined")
    print("   Fix: Add 'import json' at the top")

    print("\n✅ FIXED CODE:")
    import json

    def parse_config(config_str: str) -> Dict:
        """Parse JSON configuration string."""
        return json.loads(config_str)

    result = parse_config('{"name": "test", "value": 42}')
    print(f"""
import json

def parse_config(config_str: str) -> Dict:
    return json.loads(config_str)

result = parse_config('{{"name": "test", "value": 42}}')
print(result)  # {result}
    """)

    assert result == {"name": "test", "value": 42}, "Test failed!"
    print("✓ Test passed!")


# ==============================================================================
# Example 4: Indentation Error
# ==============================================================================

def example_4_indentation_error():
    """Demonstrate fixing indentation errors."""
    print_example(4, "Indentation Error")

    print("❌ BUGGY CODE:")
    print("""
def process_items(items: List[str]) -> List[str]:
    results = []
    for item in items:
    results.append(item.upper())  # Wrong indentation!
    return results
    """)

    print("🤖 AI Analysis:")
    print("   IndentationError: expected an indented block")
    print("   Fix: Indent line 4 by 4 spaces (inside the for loop)")

    print("\n✅ FIXED CODE:")
    def process_items(items: List[str]) -> List[str]:
        """Process items by converting to uppercase."""
        results = []
        for item in items:
            results.append(item.upper())  # Properly indented
        return results

    result = process_items(["hello", "world"])
    print(f"""
def process_items(items: List[str]) -> List[str]:
    results = []
    for item in items:
        results.append(item.upper())  # Fixed indentation
    return results

result = process_items(["hello", "world"])
print(result)  # {result}
    """)

    assert result == ["HELLO", "WORLD"], "Test failed!"
    print("✓ Test passed!")


# ==============================================================================
# Example 5: None/Null Errors
# ==============================================================================

def example_5_none_errors():
    """Demonstrate fixing NoneType attribute errors."""
    print_example(5, "NoneType AttributeError")

    print("❌ BUGGY CODE:")
    print("""
def get_user_name(user_id: int) -> str:
    user = find_user(user_id)  # May return None
    return user.name  # AttributeError if None!

def find_user(user_id: int) -> Dict:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)  # Returns None if not found
    """)

    print("🤖 AI Analysis:")
    print("   AttributeError: 'NoneType' object has no attribute 'name'")
    print("   Problem: user can be None when user_id not found")
    print("   Fix: Add null check before accessing attributes")

    print("\n✅ FIXED CODE:")
    def find_user(user_id: int) -> Union[Dict, None]:
        """Find user by ID."""
        users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
        return users.get(user_id)

    def get_user_name(user_id: int) -> str:
        """Get user name with proper null handling."""
        user = find_user(user_id)
        if user is None:
            return "Unknown User"
        return user["name"]

    result1 = get_user_name(1)  # Found
    result2 = get_user_name(999)  # Not found
    print(f"""
def get_user_name(user_id: int) -> str:
    user = find_user(user_id)
    if user is None:  # Null check!
        return "Unknown User"
    return user["name"]

print(get_user_name(1))    # {result1}
print(get_user_name(999))  # {result2}
    """)

    assert result1 == "Alice", "Test 1 failed!"
    assert result2 == "Unknown User", "Test 2 failed!"
    print("✓ Both tests passed!")


# ==============================================================================
# Example 6: Wrong Function Signature
# ==============================================================================

def example_6_wrong_signature():
    """Demonstrate fixing function signature mismatches."""
    print_example(6, "Function Signature Mismatch")

    print("❌ BUGGY CODE:")
    print("""
def format_price(price: float) -> str:
    return f"${price:.2f}"

# Called with wrong number of arguments
result = format_price(19.99, "USD")  # TypeError!
    """)

    print("🤖 AI Analysis:")
    print("   TypeError: format_price() takes 1 positional argument but 2 were given")
    print("   Fix: Add currency parameter to function signature")

    print("\n✅ FIXED CODE:")
    def format_price(price: float, currency: str = "USD") -> str:
        """Format price with currency symbol."""
        symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
        symbol = symbols.get(currency, "$")
        return f"{symbol}{price:.2f}"

    result1 = format_price(19.99)  # Uses default
    result2 = format_price(19.99, "EUR")
    print(f"""
def format_price(price: float, currency: str = "USD") -> str:
    symbols = {{"USD": "$", "EUR": "€", "GBP": "£"}}
    symbol = symbols.get(currency, "$")
    return f"{{symbol}}{{price:.2f}}"

print(format_price(19.99))         # {result1}
print(format_price(19.99, "EUR"))  # {result2}
    """)

    assert result1 == "$19.99", "Test 1 failed!"
    assert result2 == "€19.99", "Test 2 failed!"
    print("✓ Both tests passed!")


# ==============================================================================
# Example 7: Dictionary KeyError
# ==============================================================================

def example_7_keyerror():
    """Demonstrate fixing KeyError."""
    print_example(7, "Dictionary KeyError")

    print("❌ BUGGY CODE:")
    print("""
config = {"host": "localhost", "port": 8000}
database = config["database"]  # KeyError!
    """)

    print("🤖 AI Analysis:")
    print("   KeyError: 'database'")
    print("   Problem: Key 'database' doesn't exist in config dict")
    print("   Fix: Use .get() with default, or check key exists")

    print("\n✅ FIXED CODE:")
    config = {"host": "localhost", "port": 8000}

    # Fix 1: Use .get() with default
    database1 = config.get("database", "default_db")

    # Fix 2: Check before accessing
    database2 = config["database"] if "database" in config else "default_db"

    print(f"""
# Fix 1: Use .get() with default
database = config.get("database", "default_db")
print(database)  # {database1}

# Fix 2: Check key exists
database = config["database"] if "database" in config else "default_db"
print(database)  # {database2}
    """)

    assert database1 == "default_db", "Test 1 failed!"
    assert database2 == "default_db", "Test 2 failed!"
    print("✓ Both tests passed!")


# ==============================================================================
# Example 8: String Formatting Error
# ==============================================================================

def example_8_string_formatting():
    """Demonstrate fixing string formatting errors."""
    print_example(8, "String Formatting Error")

    print("❌ BUGGY CODE:")
    print("""
name = "Alice"
age = 30
message = f"User {name} is {age years old"  # Missing closing brace!
    """)

    print("🤖 AI Analysis:")
    print("   SyntaxError: f-string: expecting '}'")
    print("   Fix: Add closing brace after 'age'")

    print("\n✅ FIXED CODE:")
    name = "Alice"
    age = 30
    message = f"User {name} is {age} years old"

    print(f"""
name = "Alice"
age = 30
message = f"User {{name}} is {{age}} years old"
print(message)  # {message}
    """)

    assert message == "User Alice is 30 years old", "Test failed!"
    print("✓ Test passed!")


# ==============================================================================
# Main Function
# ==============================================================================

def main():
    """Run all syntax debugging examples."""
    print_header("Module 4: Syntax & Type Debugging with AI")

    print("""
This module demonstrates how AI excels at catching and fixing syntax and type errors.

AI Effectiveness for Syntax Errors: ⭐⭐⭐⭐⭐ (Excellent!)

Why AI is great at this:
- Clear error messages with line numbers
- Common patterns seen in training data
- Unambiguous fixes
- Fast iteration
    """)

    try:
        example_1_missing_colon()
        example_2_type_mismatch()
        example_3_missing_import()
        example_4_indentation_error()
        example_5_none_errors()
        example_6_wrong_signature()
        example_7_keyerror()
        example_8_string_formatting()

        print_header("All Examples Completed Successfully!")
        print("""
Key Takeaways:
1. AI is EXCELLENT at fixing syntax errors (95%+ success rate)
2. Always provide full error messages to AI
3. Type hints help AI understand your intent
4. Most syntax errors fixed in < 10 seconds with AI
5. Still verify fixes - understand, don't just copy

Next Steps:
- Try breaking code intentionally and fixing with AI
- Practice providing good context to AI
- Learn to read error messages effectively
- Move on to logic debugging (more challenging!)
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
