"""
Module 1: AI Coding Pattern #2 - Iteration Pattern

Demonstrates iterative refinement with AI.

AI CONVERSATION SIMULATED:
---------------------------
Iteration 1: "Create a function to validate email addresses"
→ AI generates basic regex

Iteration 2: "Add support for internationalized domains"
→ AI updates with unicode support

Iteration 3: "Add validation for common typos like gmial.com"
→ AI adds typo detection

This file shows the FINAL result after 3 iterations.
"""

import re
from typing import Tuple


# ITERATION 1: Basic email validation
def validate_email_v1(email: str) -> bool:
    """Basic email validation (first iteration)."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ITERATION 2: Add internationalized domain support
def validate_email_v2(email: str) -> bool:
    """Email validation with internationalized domains (second iteration)."""
    # Updated to handle unicode characters in domain
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    try:
        # Handle internationalized domain names
        local, domain = email.rsplit('@', 1)
        # Encode internationalized domains to ASCII (IDNA encoding)
        domain_encoded = domain.encode('idna').decode('ascii')
        normalized_email = f"{local}@{domain_encoded}"
        return bool(re.match(pattern, normalized_email))
    except (ValueError, UnicodeError):
        return False


# ITERATION 3: Add typo detection
def validate_email_v3(email: str) -> Tuple[bool, str]:
    """
    Email validation with typo detection (final iteration).

    Returns:
        Tuple of (is_valid, message)
    """
    # Common email provider typos
    typo_map = {
        'gmial.com': 'gmail.com',
        'gmai.com': 'gmail.com',
        'yahooo.com': 'yahoo.com',
        'yaho.com': 'yahoo.com',
        'hotmial.com': 'hotmail.com',
        'outlok.com': 'outlook.com',
    }

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    try:
        local, domain = email.rsplit('@', 1)

        # Check for typos
        domain_lower = domain.lower()
        if domain_lower in typo_map:
            suggested = typo_map[domain_lower]
            return False, f"Did you mean {local}@{suggested}?"

        # Handle internationalized domains
        domain_encoded = domain.encode('idna').decode('ascii')
        normalized_email = f"{local}@{domain_encoded}"

        if re.match(pattern, normalized_email):
            return True, "Valid email"
        else:
            return False, "Invalid email format"

    except (ValueError, UnicodeError):
        return False, "Invalid email format"


def demonstrate_iteration_pattern():
    """
    Demonstrates the Iteration Pattern with progressive improvements.

    KEY INSIGHT: Don't expect perfection first try. Iterate with AI!
    """
    print("=" * 60)
    print("AI CODING PATTERN #2: ITERATION PATTERN")
    print("=" * 60)
    print()
    print("✨ CONCEPT: Start simple, refine iteratively")
    print()

    test_emails = [
        ("user@example.com", "Basic valid email"),
        ("user@münchen.de", "Internationalized domain"),
        ("user@gmial.com", "Common typo"),
        ("invalid.email", "Missing @ symbol"),
        ("user@yaho.com", "Another typo"),
    ]

    # Show progression through iterations
    print("ITERATION 1: Basic validation")
    print("-" * 60)
    for email, description in test_emails[:2]:
        result = validate_email_v1(email)
        print(f"  {email:30} → {'✅ Valid' if result else '❌ Invalid'}")
    print()

    print("ITERATION 2: Added internationalized domain support")
    print("-" * 60)
    for email, description in test_emails[:3]:
        result = validate_email_v2(email)
        print(f"  {email:30} → {'✅ Valid' if result else '❌ Invalid'}")
    print()

    print("ITERATION 3: Added typo detection")
    print("-" * 60)
    for email, description in test_emails:
        is_valid, message = validate_email_v3(email)
        status = "✅" if is_valid else "❌"
        print(f"  {email:30} → {status} {message}")
    print()

    print("=" * 60)
    print("💡 LESSONS:")
    print("   - Start with basic version")
    print("   - Each iteration adds one feature")
    print("   - Faster than trying to specify everything upfront")
    print("   - AI handles incremental changes well")
    print("   - You discover requirements as you iterate")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_iteration_pattern()
