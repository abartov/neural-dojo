#!/usr/bin/env python3
"""
Module 2: Chain-of-Thought (CoT) Prompting

Demonstrates how asking AI to "show its work" dramatically improves
accuracy on reasoning tasks.

KEY INSIGHT: Adding "Let's think step by step" can improve accuracy by 20-40%!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def without_cot():
    """
    Standard prompting: Direct question → Direct answer
    """
    prompt = """
    A farmer has 17 sheep. All but 9 die. How many sheep are left?
    """
    return prompt


def with_cot():
    """
    Chain-of-Thought: Ask AI to show its reasoning
    """
    prompt = """
    A farmer has 17 sheep. All but 9 die. How many sheep are left?

    Let's think step by step:
    """
    return prompt


def run_prompt(prompt: str, label: str):
    """Execute a prompt and display results."""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"\nPrompt: {prompt}")
    print(f"\n{'-'*60}\nResponse:")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(result)

    return result


def math_problem_comparison():
    """
    Compare CoT on a tricky math word problem.
    """
    print("\n" + "🧮"*30)
    print("TASK: Math Word Problem")
    print("🧮"*30)

    # Without CoT
    without = """
    If you're running a race and you pass the person in 2nd place, what place are you in?
    """

    # With CoT
    with_ = """
    If you're running a race and you pass the person in 2nd place, what place are you in?

    Let's reason through this step by step:
    """

    run_prompt(without, "❌ WITHOUT CHAIN-OF-THOUGHT")
    run_prompt(with_, "✅ WITH CHAIN-OF-THOUGHT")


def code_debugging_with_cot():
    """
    Show CoT for debugging code.
    """
    print("\n" + "🐛"*30)
    print("TASK: Code Debugging")
    print("🐛"*30)

    # Without CoT (direct fix)
    without = """
    Fix this buggy Python function:

    def get_average(numbers):
        return sum(numbers) / len(numbers)

    # Test: get_average([]) raises ZeroDivisionError
    """

    # With CoT (reasoned debugging)
    with_ = """
    Debug this Python function step by step:

    def get_average(numbers):
        return sum(numbers) / len(numbers)

    # Test: get_average([]) raises ZeroDivisionError

    Let's debug systematically:
    1. What's the error?
    2. Why does it occur?
    3. What should the function do for empty lists?
    4. How to fix it?
    5. What other edge cases should we consider?
    """

    run_prompt(without, "❌ WITHOUT CoT (Quick Fix)")
    run_prompt(with_, "✅ WITH CoT (Systematic Debugging)")


def logic_puzzle_with_cot():
    """
    Chain-of-thought for logic puzzles.
    """
    print("\n" + "🧩"*30)
    print("TASK: Logic Puzzle")
    print("🧩"*30)

    # Without CoT
    without = """
    You have two hourglasses: one measures 7 minutes, one measures 4 minutes.
    How can you measure exactly 9 minutes?
    """

    # With CoT
    with_ = """
    You have two hourglasses: one measures 7 minutes, one measures 4 minutes.
    How can you measure exactly 9 minutes?

    Let's solve this step by step:
    1. What operations can we do with hourglasses?
    2. What combinations of 7 and 4 can give us 9?
    3. Can we start both at the same time?
    4. What happens when one finishes?
    """

    run_prompt(without, "❌ WITHOUT CoT")
    run_prompt(with_, "✅ WITH CoT")


def cot_for_decision_making():
    """
    Using CoT for architectural/design decisions.
    """
    print("\n" + "🏗️"*30)
    print("TASK: Technical Decision")
    print("🏗️"*30)

    prompt = """
    Should I use a microservices architecture or a monolith for my startup's web application?

    Context:
    - Team size: 3 developers
    - Expected users: 10K in first year
    - Budget: Limited
    - Timeline: 3 months to MVP

    Think through this decision step by step:
    1. What are the trade-offs?
    2. What does team size suggest?
    3. What does the timeline suggest?
    4. What about future scalability?
    5. What's the recommendation and why?
    """

    run_prompt(prompt, "✅ CoT for TECHNICAL DECISIONS")


def main():
    """
    Main demonstration of Chain-of-Thought prompting.
    """
    print("\n" + "="*60)
    print("MODULE 2: CHAIN-OF-THOUGHT PROMPTING")
    print("="*60)
    print("\nKEY INSIGHT: Making AI show its work improves accuracy!")
    print("Magic words: 'Let's think step by step'")
    print("="*60)

    # Basic comparison
    run_prompt(without_cot(), "❌ WITHOUT CHAIN-OF-THOUGHT")
    run_prompt(with_cot(), "✅ WITH CHAIN-OF-THOUGHT")

    # Math problem
    math_problem_comparison()

    # Code debugging
    code_debugging_with_cot()

    # Logic puzzle
    logic_puzzle_with_cot()

    # Decision making
    cot_for_decision_making()

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. CoT improves reasoning accuracy by 20-40%")
    print("2. Makes debugging easier (see where AI went wrong)")
    print("3. Works for:")
    print("   - Math and logic problems")
    print("   - Code debugging")
    print("   - Technical decisions")
    print("   - Multi-step reasoning")
    print("4. Trigger phrases:")
    print("   - 'Let's think step by step'")
    print("   - 'Let's work through this'")
    print("   - 'Show your reasoning'")
    print("5. Small cost: Uses more tokens (longer response)")
    print("   But worth it for accuracy!")
    print("="*60)


if __name__ == "__main__":
    main()
