#!/usr/bin/env python3
"""
Module 4: Debugging Patterns and Strategies
Shows systematic debugging approaches.

Patterns:
- Binary search debugging
- Differential debugging
- Regression debugging
- Rubber duck debugging with AI
"""

import sys


def example_1_binary_search():
    """Binary search debugging pattern."""
    print("\n--- Pattern 1: Binary Search Debugging ---\n")

    print("Problem: Bug somewhere in 1000-line codebase")
    print("\nApproach:")
    print("1. Add logging at middle point (line 500)")
    print("2. If bug before middle: search first half")
    print("3. If bug after middle: search second half")
    print("4. Repeat until found")
    print("\nWith AI:")
    print("  'Help me add strategic logging to binary search this bug'")
    print("  AI suggests key points to log")
    print("\n✓ Reduces O(n) search to O(log n)!\n")


def example_2_differential_debugging():
    """Differential debugging pattern."""
    print("\n--- Pattern 2: Differential Debugging ---\n")

    print("Problem: Code works on dev, fails on prod")
    print("\nSystematic comparison:")
    print("  Dev:  Python 3.11, macOS, SQLite")
    print("  Prod: Python 3.11, Linux, PostgreSQL")
    print("\nWith AI:")
    print("""
  Prompt: 'Code works on dev (Mac/SQLite) but fails on prod (Linux/Postgres).
           Error: [paste error]
           What environmental differences could cause this?'

  AI suggests:
  - Line ending differences (\\n vs \\r\\n)
  - Path separators (/ vs \\\\)
  - Database-specific SQL
  - Case sensitivity
  - File permissions
    """)
    print("✓ AI systematically considers environment differences!\n")


def example_3_regression_debugging():
    """Regression debugging pattern."""
    print("\n--- Pattern 3: Regression Debugging ---\n")

    print("Problem: Recent change broke something")
    print("\nApproach:")
    print("1. git diff main feature-branch")
    print("2. Identify what changed")
    print("3. Connect change to failure")
    print("\nWith AI:")
    print("""
  Prompt: 'After this change: [git diff]
           This test started failing: [test output]
           What in the change could cause this?'

  AI analyzes diff and points to likely cause
    """)
    print("✓ AI connects changes to failures!\n")


def example_4_rubber_duck():
    """Rubber duck debugging with AI."""
    print("\n--- Pattern 4: Rubber Duck Debugging ---\n")

    print("Explaining problem to AI often reveals solution!")
    print("\nExample conversation:")
    print("""
  You: 'I have a bug where users aren't receiving emails.

       What I know:
       - Email function is called (I added logging)
       - SMTP connection succeeds
       - No error messages
       - Emails not arriving

       What I've tried:
       - Checked spam folder - not there
       - Verified email addresses - they're correct
       - Tested with my own email - same issue

       My hypothesis: Maybe email is being sent but rejected?'

  AI: 'Your logging shows the function is called and SMTP connects.
       But do you log the actual send() call return value?
       SMTP might connect but fail to send.

       Try:
       result = smtp.send_message(msg)
       logger.info(f"Send result: {result}")

       Also check: Are you calling smtp.quit() or closing connection
       before message is sent?'

  You: 'Oh! I'm not waiting for send_message() to complete.
       I was closing the connection immediately. That's the bug!'
    """)
    print("\n✓ Explaining problem systematically often reveals the bug!\n")


def example_5_minimal_reproduction():
    """Creating minimal reproduction."""
    print("\n--- Pattern 5: Minimal Reproduction ---\n")

    print("Problem: Bug in 500-line file")
    print("\nApproach:")
    print("1. Copy code to new file")
    print("2. Remove unrelated code")
    print("3. Keep removing until bug disappears")
    print("4. Last thing removed caused bug!")
    print("\nWith AI:")
    print("  Provide minimal 10-line reproduction")
    print("  AI debugs much faster with less context")
    print("\n✓ Minimal reproduction makes debugging 10x easier!\n")


def example_6_systematic_checklist():
    """Systematic debugging checklist."""
    print("\n--- Pattern 6: Systematic Checklist ---\n")

    print("Before asking AI, check:")
    print("  □ Can I reproduce it consistently?")
    print("  □ Do I have the full error message?")
    print("  □ Did something change recently?")
    print("  □ Does it work anywhere (dev/test)?")
    print("  □ What's the minimal reproduction?")
    print("\nGive AI:")
    print("  ✓ Error message + stack trace")
    print("  ✓ Minimal code that reproduces")
    print("  ✓ Expected vs actual behavior")
    print("  ✓ Environment (versions, OS)")
    print("  ✓ Recent changes")
    print("\n✓ Better context = Better AI suggestions!\n")


def main():
    """Run debugging pattern examples."""
    print("=" * 60)
    print("  Debugging Patterns and Strategies")
    print("=" * 60)
    print()

    example_1_binary_search()
    example_2_differential_debugging()
    example_3_regression_debugging()
    example_4_rubber_duck()
    example_5_minimal_reproduction()
    example_6_systematic_checklist()

    print("Key Patterns:")
    print("1. Binary Search: O(log n) instead of O(n)")
    print("2. Differential: Compare working vs failing environments")
    print("3. Regression: git diff + failure analysis")
    print("4. Rubber Duck: Explain problem systematically")
    print("5. Minimal Reproduction: Isolate the bug")
    print("6. Checklist: Gather context before debugging")
    print("\nAI amplifies these patterns - but you need the workflow!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
