#!/usr/bin/env python3
"""
Module 17, Example 1: Chain-of-Thought Prompting

This example demonstrates the power of chain-of-thought (CoT) prompting:
1. Direct prompting vs CoT comparison
2. Zero-shot CoT ("Let's think step by step")
3. Few-shot CoT with examples
4. Different CoT trigger phrases

The Heureka Moment: Adding "Let's think step by step" can dramatically
improve reasoning accuracy - sometimes by 2-3x!

Usage:
    # Requires GOOGLE_API_KEY or ANTHROPIC_API_KEY
    export GOOGLE_API_KEY="your-key"
    python 01_chain_of_thought.py

Author: Neural Dojo - Module 17
"""

import os
import sys
from typing import Optional, List, Dict, Tuple

# Check for API key before importing LangChain
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")


def get_llm():
    """Get the appropriate LLM based on available API key."""
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
        )
    elif os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0,
        )
    return None


# ============================================================================
# TEST PROBLEMS
# ============================================================================

MATH_PROBLEMS = [
    {
        "question": "A store has 23 apples. If 7 are sold and 12 more arrive, how many apples are there?",
        "answer": 28,
        "category": "arithmetic"
    },
    {
        "question": "Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?",
        "answer": 11,
        "category": "multi-step"
    },
    {
        "question": "A farmer has 17 sheep. All but 9 run away. How many sheep does he have left?",
        "answer": 9,
        "category": "trick question"
    },
    {
        "question": "If a train travels 60 miles in 1 hour, how far will it travel in 2.5 hours?",
        "answer": 150,
        "category": "rate problem"
    },
    {
        "question": "A bookshelf has 3 shelves. Each shelf has 8 books. If 5 books are removed, how many books remain?",
        "answer": 19,
        "category": "multi-step"
    },
]

LOGIC_PROBLEMS = [
    {
        "question": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly?",
        "answer": "No",
        "category": "syllogism"
    },
    {
        "question": "John is taller than Mary. Mary is taller than Bob. Is John taller than Bob?",
        "answer": "Yes",
        "category": "transitive"
    },
    {
        "question": "A bat and ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "answer": "$0.05",
        "category": "cognitive bias"
    },
]


# ============================================================================
# PROMPTING STRATEGIES
# ============================================================================

def prompt_direct(question: str) -> str:
    """Direct prompting without CoT."""
    return f"""Answer this question with just the final answer (number or Yes/No).

Question: {question}
Answer:"""


def prompt_zero_shot_cot(question: str) -> str:
    """Zero-shot CoT with 'Let's think step by step'."""
    return f"""Answer this question. Let's think step by step.

Question: {question}

Let me work through this step by step:"""


def prompt_few_shot_cot(question: str) -> str:
    """Few-shot CoT with examples."""
    return f"""Solve the following problems step by step.

Example 1:
Question: A basket has 10 apples. If 3 are eaten and 5 more are added, how many apples are there?
Solution: Let me work through this step by step:
1. Starting apples: 10
2. After eating 3: 10 - 3 = 7
3. After adding 5: 7 + 5 = 12
Answer: 12

Example 2:
Question: Tom has 4 toy cars. He buys 3 boxes of cars. Each box has 2 cars. How many cars does he have?
Solution: Let me work through this step by step:
1. Starting cars: 4
2. New cars from boxes: 3 boxes × 2 cars = 6 cars
3. Total cars: 4 + 6 = 10
Answer: 10

Now solve this problem:
Question: {question}
Solution: Let me work through this step by step:"""


def prompt_structured_cot(question: str) -> str:
    """Structured CoT with explicit format."""
    return f"""Solve this problem using the following structure:

PROBLEM: {question}

UNDERSTANDING:
- What do we know?
- What do we need to find?

APPROACH:
- What steps will solve this?

SOLUTION:
- Step-by-step calculations

ANSWER:
- Final numerical answer

Begin:

PROBLEM: {question}

UNDERSTANDING:"""


# ============================================================================
# EVALUATION
# ============================================================================

def extract_number(text: str) -> Optional[float]:
    """Extract the final number from a response."""
    import re

    # Look for "Answer: X" or "= X" patterns first
    patterns = [
        r'[Aa]nswer[:\s]+\$?(-?\d+\.?\d*)',
        r'[Ff]inal [Aa]nswer[:\s]+\$?(-?\d+\.?\d*)',
        r'=\s*\$?(-?\d+\.?\d*)\s*$',
        r'(?:is|are|have|has|equals?|total[s]?)[:\s]+\$?(-?\d+\.?\d*)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    # Fall back to last number in text
    numbers = re.findall(r'-?\d+\.?\d*', text)
    if numbers:
        try:
            return float(numbers[-1])
        except ValueError:
            pass

    return None


def extract_yes_no(text: str) -> Optional[str]:
    """Extract Yes/No answer from response."""
    text_lower = text.lower()

    # Check for explicit answers
    if 'yes' in text_lower and 'no' not in text_lower:
        return 'Yes'
    if 'no' in text_lower and 'yes' not in text_lower:
        return 'No'

    # Check for "cannot conclude" patterns (implies No)
    if any(phrase in text_lower for phrase in ['cannot conclude', 'can\'t conclude', 'not necessarily']):
        return 'No'

    # Check for "can conclude" or "true" patterns
    if any(phrase in text_lower for phrase in ['can conclude', 'is true', 'must be']):
        return 'Yes'

    return None


def evaluate_response(response: str, expected: any, category: str) -> Tuple[bool, str]:
    """Evaluate if response matches expected answer."""
    if isinstance(expected, (int, float)):
        extracted = extract_number(response)
        if extracted is not None:
            # Allow small floating point differences
            correct = abs(extracted - expected) < 0.01
            return correct, f"Extracted: {extracted}, Expected: {expected}"
        return False, f"Could not extract number from response"

    elif isinstance(expected, str):
        if expected in ['Yes', 'No']:
            extracted = extract_yes_no(response)
            if extracted:
                return extracted == expected, f"Extracted: {extracted}, Expected: {expected}"
            return False, "Could not extract Yes/No answer"

        # String matching
        return expected.lower() in response.lower(), f"Looking for: {expected}"

    return False, "Unknown expected type"


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_direct_vs_cot():
    """Compare direct prompting to zero-shot CoT."""
    print("\n" + "="*70)
    print("🧪 DEMO: Direct Prompting vs Chain-of-Thought")
    print("="*70)

    if not API_KEY:
        print("\n⚠️ No API key found. Showing example prompts only.\n")
        print("DIRECT PROMPT:")
        print(prompt_direct(MATH_PROBLEMS[0]["question"]))
        print("\nZERO-SHOT COT PROMPT:")
        print(prompt_zero_shot_cot(MATH_PROBLEMS[0]["question"]))
        return

    llm = get_llm()

    results = {"direct": {"correct": 0, "total": 0}, "cot": {"correct": 0, "total": 0}}

    for problem in MATH_PROBLEMS[:3]:  # Test first 3
        print(f"\n{'─'*70}")
        print(f"📝 Question: {problem['question']}")
        print(f"   Expected: {problem['answer']} ({problem['category']})")

        # Direct prompting
        direct_prompt = prompt_direct(problem["question"])
        direct_response = llm.invoke(direct_prompt).content
        direct_correct, direct_detail = evaluate_response(
            direct_response, problem["answer"], problem["category"]
        )
        results["direct"]["total"] += 1
        if direct_correct:
            results["direct"]["correct"] += 1

        print(f"\n   📌 DIRECT:")
        print(f"      Response: {direct_response[:100]}...")
        print(f"      {'✅' if direct_correct else '❌'} {direct_detail}")

        # Zero-shot CoT
        cot_prompt = prompt_zero_shot_cot(problem["question"])
        cot_response = llm.invoke(cot_prompt).content
        cot_correct, cot_detail = evaluate_response(
            cot_response, problem["answer"], problem["category"]
        )
        results["cot"]["total"] += 1
        if cot_correct:
            results["cot"]["correct"] += 1

        print(f"\n   🔗 CHAIN-OF-THOUGHT:")
        print(f"      Response: {cot_response[:200]}...")
        print(f"      {'✅' if cot_correct else '❌'} {cot_detail}")

    # Summary
    print(f"\n{'─'*70}")
    print("📊 RESULTS:")
    direct_acc = results["direct"]["correct"] / results["direct"]["total"] * 100
    cot_acc = results["cot"]["correct"] / results["cot"]["total"] * 100
    print(f"   Direct:     {results['direct']['correct']}/{results['direct']['total']} ({direct_acc:.0f}%)")
    print(f"   Zero-Shot CoT: {results['cot']['correct']}/{results['cot']['total']} ({cot_acc:.0f}%)")

    if cot_acc > direct_acc:
        improvement = (cot_acc - direct_acc) / max(direct_acc, 1) * 100
        print(f"\n   🎯 CoT improved accuracy by {improvement:.0f}%!")


def demo_few_shot_cot():
    """Demonstrate few-shot CoT with examples."""
    print("\n" + "="*70)
    print("🎓 DEMO: Few-Shot Chain-of-Thought")
    print("="*70)

    if not API_KEY:
        print("\n⚠️ No API key found. Showing example prompt only.\n")
        print("FEW-SHOT COT PROMPT:")
        print(prompt_few_shot_cot(MATH_PROBLEMS[1]["question"]))
        return

    llm = get_llm()

    # Test a harder problem
    problem = MATH_PROBLEMS[1]  # Tennis balls problem

    print(f"\n📝 Problem: {problem['question']}")
    print(f"   Expected: {problem['answer']}")

    # Few-shot CoT
    prompt = prompt_few_shot_cot(problem["question"])
    response = llm.invoke(prompt).content

    print(f"\n📋 Few-Shot CoT Response:")
    print("─" * 50)
    print(response)
    print("─" * 50)

    correct, detail = evaluate_response(response, problem["answer"], problem["category"])
    print(f"\n{'✅ Correct!' if correct else '❌ Incorrect'} {detail}")


def demo_cot_triggers():
    """Test different CoT trigger phrases."""
    print("\n" + "="*70)
    print("🔑 DEMO: Different CoT Trigger Phrases")
    print("="*70)

    triggers = [
        ("Let's think step by step", "Standard"),
        ("Let's break this down", "Decomposition"),
        ("Let's analyze this carefully", "Analytical"),
        ("First, let me understand the problem", "Comprehension"),
        ("Let me work through this", "Process-oriented"),
    ]

    if not API_KEY:
        print("\n⚠️ No API key found. Showing trigger phrases:\n")
        for trigger, style in triggers:
            print(f"  • {trigger} ({style})")
        return

    llm = get_llm()
    problem = MATH_PROBLEMS[4]  # Bookshelf problem

    print(f"\n📝 Problem: {problem['question']}")
    print(f"   Expected: {problem['answer']}")

    for trigger, style in triggers:
        prompt = f"""Answer this question. {trigger}.

Question: {problem['question']}

{trigger}:"""

        response = llm.invoke(prompt).content
        correct, _ = evaluate_response(response, problem["answer"], problem["category"])

        print(f"\n   {'✅' if correct else '❌'} {style}: \"{trigger}\"")


def demo_structured_reasoning():
    """Demonstrate structured CoT format."""
    print("\n" + "="*70)
    print("📐 DEMO: Structured Chain-of-Thought")
    print("="*70)

    if not API_KEY:
        print("\n⚠️ No API key found. Showing structured prompt:\n")
        print(prompt_structured_cot(MATH_PROBLEMS[2]["question"]))
        return

    llm = get_llm()

    # Use the trick question
    problem = MATH_PROBLEMS[2]  # "All but 9 run away"

    print(f"\n📝 Problem (Trick Question): {problem['question']}")
    print(f"   Expected: {problem['answer']}")

    prompt = prompt_structured_cot(problem["question"])
    response = llm.invoke(prompt).content

    print(f"\n📋 Structured CoT Response:")
    print("─" * 50)
    print(response)
    print("─" * 50)

    correct, detail = evaluate_response(response, problem["answer"], problem["category"])
    print(f"\n{'✅ Correct!' if correct else '❌ Incorrect'} {detail}")


def demo_logic_problems():
    """Test CoT on logic problems."""
    print("\n" + "="*70)
    print("🧠 DEMO: Logic Problems with CoT")
    print("="*70)

    if not API_KEY:
        print("\n⚠️ No API key found. Showing logic problems:\n")
        for p in LOGIC_PROBLEMS:
            print(f"  • {p['question']}")
            print(f"    Category: {p['category']}, Answer: {p['answer']}\n")
        return

    llm = get_llm()

    for problem in LOGIC_PROBLEMS:
        print(f"\n{'─'*70}")
        print(f"📝 Question: {problem['question']}")
        print(f"   Category: {problem['category']}")
        print(f"   Expected: {problem['answer']}")

        prompt = f"""Answer this logic question. Think through it carefully step by step.

Question: {problem['question']}

Let me analyze this step by step:"""

        response = llm.invoke(prompt).content

        print(f"\n📋 Response:")
        print(response[:300] + "..." if len(response) > 300 else response)

        correct, detail = evaluate_response(response, problem["answer"], problem["category"])
        print(f"\n{'✅' if correct else '❌'} {detail}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("="*70)
    print("🔗 Chain-of-Thought Prompting - Module 17, Example 1")
    print("="*70)
    print("""
    This example demonstrates the power of Chain-of-Thought prompting.

    The Heureka Moment: Adding "Let's think step by step" makes the
    model show its reasoning, which dramatically improves accuracy!

    Key Techniques:
    1. Zero-Shot CoT - Just add the magic phrase
    2. Few-Shot CoT - Provide example reasoning
    3. Structured CoT - Explicit format for reasoning
    """)

    if not API_KEY:
        print("⚠️ No API key found.")
        print("   Set GOOGLE_API_KEY or ANTHROPIC_API_KEY to run full demos.")
        print("   Running in example mode...\n")

    # Run demos
    demo_direct_vs_cot()
    demo_few_shot_cot()
    demo_cot_triggers()
    demo_structured_reasoning()
    demo_logic_problems()

    # Summary
    print("\n" + "="*70)
    print("📚 KEY TAKEAWAYS")
    print("="*70)
    print("""
    1. ZERO-SHOT COT
       Just add "Let's think step by step" for instant improvement.
       Works across many reasoning tasks without examples.

    2. FEW-SHOT COT
       Provide 2-3 examples of step-by-step reasoning.
       More consistent format and better for domain-specific tasks.

    3. STRUCTURED COT
       Use explicit format (UNDERSTANDING, APPROACH, SOLUTION).
       Best for complex problems that benefit from organization.

    4. TRIGGER PHRASES MATTER
       "Let's think step by step" is best for general use.
       Different triggers for different task types.

    5. NOT A SILVER BULLET
       CoT helps most with multi-step reasoning.
       Less useful for simple factual recall.

    🔮 Remember: Making AI "think out loud" is the foundation
       of modern AI agents and reasoning systems!
    """)


if __name__ == "__main__":
    main()
