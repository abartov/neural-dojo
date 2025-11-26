#!/usr/bin/env python3
"""
Module 17, Example 3: Self-Consistency and Advanced Reasoning

This example demonstrates advanced reasoning techniques:
1. Self-Consistency - Multiple reasoning paths for robust answers
2. Least-to-Most Prompting - Break complex into simple
3. Program-Aided Language Models (PAL) - Generate code for reasoning
4. Reasoning quality evaluation

Usage:
    export GOOGLE_API_KEY="your-key"
    python 03_self_consistency.py

Author: Neural Dojo - Module 17
"""

import os
import sys
import re
from typing import Optional, List, Dict, Any, Tuple
from collections import Counter
from dataclasses import dataclass

# Check for API key
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")


def get_llm(temperature: float = 0.0):
    """Get LLM with specified temperature."""
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=temperature,
        )
    elif os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=temperature,
        )
    return None


# ============================================================================
# SELF-CONSISTENCY
# ============================================================================

@dataclass
class SelfConsistencyResult:
    """Result from self-consistency sampling."""
    answer: str
    confidence: float
    all_answers: List[str]
    reasoning_paths: List[str]


def extract_final_answer(response: str) -> Optional[str]:
    """Extract the final answer from a CoT response."""
    # Look for explicit answer markers
    patterns = [
        r'(?:final\s+)?answer[:\s]+(.+?)(?:\n|$)',
        r'therefore[,:\s]+(.+?)(?:\n|$)',
        r'(?:so|thus)[,:\s]+(?:the answer is\s+)?(.+?)(?:\n|$)',
        r'=\s*(\d+\.?\d*)\s*$',
    ]

    response_lower = response.lower()
    for pattern in patterns:
        match = re.search(pattern, response_lower, re.IGNORECASE)
        if match:
            answer = match.group(1).strip()
            # Clean up the answer
            answer = re.sub(r'[.,!?]$', '', answer)
            return answer

    # Fall back to last number
    numbers = re.findall(r'-?\d+\.?\d*', response)
    if numbers:
        return numbers[-1]

    return None


def self_consistent_cot(
    question: str,
    num_samples: int = 5,
    temperature: float = 0.7
) -> SelfConsistencyResult:
    """
    Generate multiple reasoning paths and vote on the answer.

    Self-consistency improves reliability by:
    1. Generating diverse reasoning paths
    2. Extracting answer from each path
    3. Voting for the most common answer
    """
    if not API_KEY:
        # Return mock result for demo
        return SelfConsistencyResult(
            answer="[Requires API key]",
            confidence=0.0,
            all_answers=[],
            reasoning_paths=[]
        )

    llm = get_llm(temperature=temperature)

    prompt = f"""Solve this problem step by step. Show your reasoning clearly.

Question: {question}

Let me work through this step by step:"""

    answers = []
    reasoning_paths = []

    for i in range(num_samples):
        response = llm.invoke(prompt).content
        reasoning_paths.append(response)

        answer = extract_final_answer(response)
        if answer:
            answers.append(answer)

    # Vote for most common answer
    if not answers:
        return SelfConsistencyResult(
            answer="Could not extract answers",
            confidence=0.0,
            all_answers=[],
            reasoning_paths=reasoning_paths
        )

    answer_counts = Counter(answers)
    most_common = answer_counts.most_common(1)[0]

    return SelfConsistencyResult(
        answer=most_common[0],
        confidence=most_common[1] / len(answers),
        all_answers=answers,
        reasoning_paths=reasoning_paths
    )


# ============================================================================
# LEAST-TO-MOST PROMPTING
# ============================================================================

def least_to_most_prompt(question: str) -> str:
    """Generate a least-to-most decomposition prompt."""
    return f"""To solve complex problems, first break them into simpler sub-problems.

Question: {question}

Step 1: Identify the sub-problems
What simpler questions do we need to answer first?

Step 2: List sub-problems from simplest to most complex

Step 3: Solve each sub-problem in order

Step 4: Combine solutions for the final answer

Let's begin:

Step 1: Sub-problems needed:"""


def solve_least_to_most(question: str) -> Tuple[str, List[str]]:
    """Solve using least-to-most decomposition."""
    if not API_KEY:
        return "[Requires API key]", []

    llm = get_llm(temperature=0)

    # Step 1: Decompose
    decomposition_prompt = f"""Break this problem into simpler sub-problems:

Problem: {question}

List the sub-problems from simplest to most complex (one per line):"""

    decomposition = llm.invoke(decomposition_prompt).content

    # Step 2: Solve each sub-problem
    subproblems = [line.strip() for line in decomposition.split('\n')
                   if line.strip() and not line.strip().startswith('#')][:5]

    solutions = []
    context = ""

    for subproblem in subproblems:
        if not subproblem:
            continue

        solve_prompt = f"""Given what we know:
{context if context else "(No previous solutions yet)"}

Solve this sub-problem: {subproblem}

Solution:"""

        solution = llm.invoke(solve_prompt).content
        solutions.append(f"{subproblem}\n→ {solution}")
        context += f"\n- {subproblem}: {solution[:100]}"

    # Step 3: Final answer
    final_prompt = f"""Given these solutions:
{chr(10).join(solutions)}

Answer the original question: {question}

Final Answer:"""

    final_answer = llm.invoke(final_prompt).content

    return final_answer, solutions


# ============================================================================
# PROGRAM-AIDED LANGUAGE MODELS (PAL)
# ============================================================================

PAL_PROMPT = """Solve this problem by writing Python code.
Write code that calculates the answer and prints it.

Problem: {question}

```python
# Solution
"""


def solve_with_pal(question: str) -> Tuple[str, str]:
    """Solve using Program-Aided Language Models approach."""
    if not API_KEY:
        return "[Requires API key]", "# No API key"

    llm = get_llm(temperature=0)

    prompt = PAL_PROMPT.format(question=question)
    response = llm.invoke(prompt).content

    # Extract code
    code_match = re.search(r'```python\n?(.*?)```', response, re.DOTALL)
    if code_match:
        code = code_match.group(1)
    else:
        # Try to find code without markers
        code = response.strip()
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]

    # Execute the code
    try:
        # Create a namespace for execution
        namespace = {}
        exec(code, {"__builtins__": __builtins__, "print": print}, namespace)

        # Try to capture print output
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            exec(code, {"__builtins__": __builtins__})

        output = f.getvalue().strip()
        if output:
            return output, code
        else:
            # Look for result variable
            for var in ['result', 'answer', 'total']:
                if var in namespace:
                    return str(namespace[var]), code

            return "Code executed but no output", code

    except Exception as e:
        return f"Error executing code: {e}", code


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_self_consistency():
    """Demonstrate self-consistency technique."""
    print("\n" + "="*70)
    print("🎯 DEMO: Self-Consistency")
    print("="*70)

    print("""
Self-consistency generates multiple reasoning paths and votes on the answer.

Different paths might make different errors, but correct reasoning
tends to converge on the same answer.

    Path 1: 23 - 7 = 16, 16 + 12 = 28 ✓
    Path 2: 23 + 12 = 35, 35 - 7 = 28 ✓
    Path 3: 23 - 7 = 15, 15 + 12 = 27 ✗ (arithmetic error)

    Vote: 28 wins (2 out of 3)
    """)

    question = "A store has 23 apples. If 7 are sold and 12 more arrive, how many apples are there?"

    print(f"📝 Question: {question}")
    print(f"   Expected: 28")

    if not API_KEY:
        print("\n⚠️ No API key. Self-consistency would:")
        print("   1. Generate 5 different reasoning traces")
        print("   2. Extract answer from each trace")
        print("   3. Vote for the most common answer")
        print("   4. Report confidence based on agreement")
        return

    print(f"\n🔄 Generating 5 reasoning paths...")

    result = self_consistent_cot(question, num_samples=5, temperature=0.7)

    print(f"\n📊 Results:")
    print(f"   Answers found: {result.all_answers}")
    print(f"   Most common: {result.answer}")
    print(f"   Confidence: {result.confidence:.0%}")

    if result.confidence == 1.0:
        print(f"\n   ✅ All paths agreed - high confidence!")
    elif result.confidence >= 0.6:
        print(f"\n   ⚠️ Some disagreement but majority confident")
    else:
        print(f"\n   ❌ Low agreement - answer may be unreliable")


def demo_least_to_most():
    """Demonstrate least-to-most prompting."""
    print("\n" + "="*70)
    print("📊 DEMO: Least-to-Most Prompting")
    print("="*70)

    print("""
Least-to-most breaks complex problems into simpler sub-problems,
solving from simplest to most complex.

    Complex: "Last year, Amy was twice Ben's age. Amy is 20. How old is Ben?"

    Sub-problems (simplest → hardest):
    1. How old was Amy last year? (20 - 1 = 19)
    2. If Amy was twice Ben's age, how old was Ben? (19 / 2 = 9.5)
    3. How old is Ben this year? (9.5 + 1 = 10.5)
    """)

    question = "A train travels from City A to City B at 60 mph, then from City B to City C at 40 mph. If A to B is 120 miles and B to C is 80 miles, what is the average speed for the entire trip?"

    print(f"📝 Question: {question}")
    print("   (This requires computing total distance and total time)")

    if not API_KEY:
        print("\n⚠️ No API key. Least-to-most would decompose into:")
        print("   1. What is the total distance?")
        print("   2. How long does A→B take?")
        print("   3. How long does B→C take?")
        print("   4. What is total time?")
        print("   5. Average speed = total distance / total time")
        return

    print("\n🔄 Solving with least-to-most decomposition...")

    answer, steps = solve_least_to_most(question)

    print("\n📋 Solution Steps:")
    for i, step in enumerate(steps[:5], 1):
        print(f"\n   Step {i}:")
        print(f"   {step[:200]}..." if len(step) > 200 else f"   {step}")

    print(f"\n✅ Final Answer: {answer[:300]}...")


def demo_pal():
    """Demonstrate Program-Aided Language Models."""
    print("\n" + "="*70)
    print("💻 DEMO: Program-Aided Language Models (PAL)")
    print("="*70)

    print("""
PAL generates Python code instead of natural language reasoning.
The code is then executed to get the accurate answer.

This eliminates arithmetic errors that LLMs commonly make!
    """)

    problems = [
        "If a bookshelf has 5 shelves and each shelf has 8 books, and you remove 13 books, how many remain?",
        "A train travels 150 miles in 2.5 hours. What is its speed in miles per hour?",
        "If you invest $1000 at 5% annual interest, how much will you have after 3 years? (compound interest)",
    ]

    for problem in problems:
        print(f"\n{'─'*70}")
        print(f"📝 Problem: {problem}")

        if not API_KEY:
            print("   PAL would generate Python code to solve this")
            continue

        answer, code = solve_with_pal(problem)

        print(f"\n💻 Generated Code:")
        print("   " + code.replace("\n", "\n   ")[:300])

        print(f"\n✅ Answer: {answer}")


def demo_reasoning_comparison():
    """Compare different reasoning approaches."""
    print("\n" + "="*70)
    print("⚖️ DEMO: Comparing Reasoning Approaches")
    print("="*70)

    question = "A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?"

    print(f"📝 Question (Trick Question!): {question}")
    print("   Expected: 9 (not 17-9=8!)")

    print("""
This is a trick question that tests reading comprehension.
"All but 9" means 9 remain, not "all minus 9".

Let's see how different approaches handle it:
    """)

    if not API_KEY:
        print("⚠️ No API key. Would compare:")
        print("   • Zero-shot CoT")
        print("   • Self-consistency (5 samples)")
        print("   • PAL (code generation)")
        return

    llm = get_llm(temperature=0)

    # Zero-shot CoT
    cot_prompt = f"Answer this carefully. Let's think step by step.\n\nQuestion: {question}\n\nStep by step:"
    cot_response = llm.invoke(cot_prompt).content
    cot_answer = extract_final_answer(cot_response)

    print(f"\n📌 Zero-shot CoT:")
    print(f"   Response: {cot_response[:150]}...")
    print(f"   Answer: {cot_answer}")

    # Self-consistency
    sc_result = self_consistent_cot(question, num_samples=3, temperature=0.5)
    print(f"\n🎯 Self-Consistency (3 paths):")
    print(f"   Answers: {sc_result.all_answers}")
    print(f"   Final: {sc_result.answer} (confidence: {sc_result.confidence:.0%})")

    # PAL
    pal_answer, pal_code = solve_with_pal(question)
    print(f"\n💻 PAL (code):")
    print(f"   Code: {pal_code[:100]}...")
    print(f"   Answer: {pal_answer}")

    print(f"\n📊 Comparison:")
    correct = "9"
    print(f"   CoT: {'✅' if str(cot_answer) == correct else '❌'} {cot_answer}")
    print(f"   Self-Consistency: {'✅' if str(sc_result.answer) == correct else '❌'} {sc_result.answer}")
    print(f"   PAL: {'✅' if correct in str(pal_answer) else '❌'} {pal_answer}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("="*70)
    print("🧠 Advanced Reasoning Techniques - Module 17, Example 3")
    print("="*70)
    print("""
    Beyond basic Chain-of-Thought, these techniques improve reliability:

    1. SELF-CONSISTENCY
       Generate multiple paths, vote on the answer

    2. LEAST-TO-MOST PROMPTING
       Break complex into simple, solve incrementally

    3. PROGRAM-AIDED LANGUAGE MODELS (PAL)
       Generate code instead of text reasoning
    """)

    if not API_KEY:
        print("⚠️ No API key found.")
        print("   Set GOOGLE_API_KEY or ANTHROPIC_API_KEY for full demos.\n")

    # Run demos
    demo_self_consistency()
    demo_least_to_most()
    demo_pal()
    demo_reasoning_comparison()

    # Summary
    print("\n" + "="*70)
    print("📚 KEY TAKEAWAYS")
    print("="*70)
    print("""
    1. SELF-CONSISTENCY
       - Multiple samples catch random errors
       - Voting increases reliability
       - Higher temperature = more diverse paths
       - Confidence = agreement level

    2. LEAST-TO-MOST
       - Good for multi-step word problems
       - Build solution incrementally
       - Each step uses previous solutions
       - Reduces error propagation

    3. PAL (PROGRAM-AIDED)
       - Perfect for math problems
       - No arithmetic errors
       - Code is verifiable
       - Combine with CoT for explanation

    4. CHOOSING THE RIGHT TECHNIQUE
       - Simple math → PAL
       - Multi-step logic → Least-to-most
       - Need reliability → Self-consistency
       - General reasoning → Zero-shot CoT

    🎯 Match the technique to the problem type!
    """)


if __name__ == "__main__":
    main()
