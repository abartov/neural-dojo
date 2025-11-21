#!/usr/bin/env python3
"""
Module 2: Iterative Refinement

Demonstrates how to progressively improve prompts based on outputs.
The first prompt is never perfect - iterate!

KEY INSIGHT: Prompting is iterative. Start basic, refine based on results.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def iteration_1_basic():
    """
    Iteration 1: Start with a basic prompt.
    Problem: Too vague, inconsistent format.
    """
    prompt = """
    Explain the Model-View-Controller (MVC) pattern.
    """
    return prompt


def iteration_2_add_structure():
    """
    Iteration 2: Add structure to the request.
    Improvement: Consistent sections, but still too abstract.
    """
    prompt = """
    Explain the Model-View-Controller (MVC) pattern.

    Include:
    - What it is
    - Why it's used
    - Example
    """
    return prompt


def iteration_3_add_constraints():
    """
    Iteration 3: Add constraints for clarity.
    Improvement: More concrete, better example.
    """
    prompt = """
    Explain the Model-View-Controller (MVC) pattern.

    Requirements:
    - Keep it concise (under 200 words)
    - Use a web application as the example
    - Explain each component (Model, View, Controller) separately
    - Show how they interact
    """
    return prompt


def iteration_4_specify_format():
    """
    Iteration 4: Specify exact format.
    Improvement: Structured output, easier to use.
    """
    prompt = """
    Explain the Model-View-Controller (MVC) pattern.

    Format:
    ## Overview (2 sentences)

    ## Components
    ### Model
    - Purpose: ...
    - Example: ...

    ### View
    - Purpose: ...
    - Example: ...

    ### Controller
    - Purpose: ...
    - Example: ...

    ## Flow (Step-by-step)
    1. User action: ...
    2. Controller: ...
    3. Model: ...
    4. View: ...

    Example: A blog application
    Keep each section under 50 words.
    """
    return prompt


def iteration_5_add_context():
    """
    Iteration 5: Add context and role.
    Improvement: Tailored to audience, practical focus.
    """
    prompt = """
    You are a senior backend engineer teaching a junior developer.

    Explain the Model-View-Controller (MVC) pattern in the context of building
    a REST API with Python Flask.

    Format:
    ## Overview (2 sentences)

    ## Components with Flask Examples
    ### Model (SQLAlchemy)
    - Purpose: ...
    - Code snippet: [show User model]

    ### View (JSON responses)
    - Purpose: ...
    - Code snippet: [show API response]

    ### Controller (Flask routes)
    - Purpose: ...
    - Code snippet: [show route handler]

    ## Real Flow Example
    Walk through: GET /api/users/123

    ## Common Mistakes
    - [mistake 1]
    - [mistake 2]

    Keep technical, practical, and concise.
    """
    return prompt


def run_prompt(prompt: str, label: str, iteration: int):
    """Execute a prompt and display results."""
    print(f"\n{'='*60}")
    print(f"ITERATION {iteration}: {label}")
    print(f"{'='*60}")
    print(f"\nPrompt:\n{prompt[:300]}...")
    print(f"\n{'-'*60}\nResponse:")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(result)

    return result


def demonstrate_code_generation_refinement():
    """
    Show iterative refinement for code generation.
    """
    print("\n" + "💻"*30)
    print("CODE GENERATION REFINEMENT")
    print("💻"*30)

    # Iteration 1: Too vague
    iter1 = """
Write a function to validate email addresses.
"""

    # Iteration 2: Add requirements
    iter2 = """
Write a Python function to validate email addresses.

Requirements:
- Check for @ symbol
- Check for domain
- Return boolean
"""

    # Iteration 3: Add edge cases
    iter3 = """
Write a Python function to validate email addresses.

Requirements:
- Check format: user@domain.com
- Allow subdomains: user@mail.domain.com
- Reject: missing @, multiple @, spaces, no domain
- Include docstring
- Include type hints
- Return boolean

Add 5 test cases showing edge cases.
"""

    # Iteration 4: Specify implementation
    iter4 = """
Write a Python function to validate email addresses.

Requirements:
- Use regex for validation
- RFC 5322 compliant (basic)
- Type hints (email: str -> bool)
- Google-style docstring with examples
- Handle None and empty string gracefully

Include:
1. The function with full implementation
2. 5 test cases (pytest format)
3. Brief comment explaining the regex pattern

Keep it production-ready (proper error handling).
"""

    run_prompt(iter1, "Vague Request", 1)
    run_prompt(iter2, "With Requirements", 2)
    run_prompt(iter3, "With Edge Cases", 3)
    run_prompt(iter4, "Production Ready", 4)


def demonstrate_debugging_refinement():
    """
    Show iterative refinement for debugging help.
    """
    print("\n" + "🐛"*30)
    print("DEBUGGING HELP REFINEMENT")
    print("🐛"*30)

    buggy_code = """
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

# Error: TypeError when calling process_data([1, 2, '3', 4])
"""

    # Iteration 1: Basic request
    iter1 = f"""
Fix this code:
{buggy_code}
"""

    # Iteration 2: Add debugging steps
    iter2 = f"""
Debug this code systematically:

{buggy_code}

Steps:
1. Identify the error
2. Explain why it occurs
3. Provide fix
"""

    # Iteration 3: Add requirements for solution
    iter3 = f"""
Debug this code systematically:

{buggy_code}

Requirements:
1. Identify the root cause
2. Explain why TypeError occurs with mixed types
3. Provide 2 solutions:
   a) Filter out invalid items
   b) Handle gracefully with try/except
4. Show which solution is better and why
5. Add type hints to prevent this
6. Write a test that would catch this bug
"""

    run_prompt(iter1, "Basic Fix Request", 1)
    run_prompt(iter2, "Systematic Debugging", 2)
    run_prompt(iter3, "Complete Solution", 3)


def demonstrate_feedback_loop():
    """
    Show the feedback loop of refinement.
    """
    print("\n" + "🔄"*30)
    print("REFINEMENT FEEDBACK LOOP")
    print("🔄"*30)

    print("""
The Iterative Refinement Process:

1. START: Basic prompt
   ↓
2. RUN: Get initial output
   ↓
3. EVALUATE: What's wrong?
   - Too vague?
   - Wrong format?
   - Missing details?
   - Not practical enough?
   ↓
4. REFINE: Add specifics
   - Constraints
   - Format requirements
   - Examples
   - Context
   ↓
5. REPEAT: Until satisfactory

Real Example:
-----------
❌ "Explain Docker"
   → Too broad, 2000 words, not useful

❌ "Explain Docker in 200 words"
   → Better length, but too abstract

❌ "Explain Docker with a practical example in 200 words"
   → Good, but what example?

✅ "Explain Docker using a Python web app deployment example.
    Include: what it solves, key concepts (image, container),
    and a 5-line Dockerfile. Keep under 200 words."
   → Perfect! Practical, concrete, right length.

Each iteration builds on feedback from previous output.
""")


def show_refinement_patterns():
    """
    Display common refinement patterns.
    """
    print("\n" + "📋"*30)
    print("COMMON REFINEMENT PATTERNS")
    print("📋"*30)

    print("""
Refinement Pattern Cheat Sheet:

1. **Too Vague** → Add constraints
   Before: "Explain REST APIs"
   After:  "Explain REST APIs: HTTP methods, status codes,
            JSON format. Use a user CRUD API as example. 300 words."

2. **Wrong Format** → Specify structure
   Before: "List Python libraries for ML"
   After:  "List Python libraries for ML as table:
            | Library | Purpose | When to Use |"

3. **Too Abstract** → Add concrete examples
   Before: "Explain async programming"
   After:  "Explain async programming with 2 examples:
            1) Sequential vs async HTTP requests
            2) Real code showing async/await in Python"

4. **Wrong Level** → Adjust expertise
   Before: "Explain neural networks"
   After:  "Explain neural networks to someone with Python
            experience but no ML background. Use code examples."

5. **Too Long** → Add length constraint
   Before: "Explain microservices"
   After:  "Explain microservices in under 150 words.
            Focus on: what, why, when to use."

6. **Not Actionable** → Request specific output
   Before: "Help me improve this code"
   After:  "Review this code for: 1) bugs, 2) performance,
            3) security. For each issue: severity + fixed code."

7. **Missing Context** → Add background
   Before: "Should I use Redis?"
   After:  "I'm building a Python Flask API with 10K users.
            Should I use Redis for session storage vs PostgreSQL?
            Consider: cost, complexity, scalability."

8. **Generic Response** → Add role/persona
   Before: "Explain design patterns"
   After:  "You're a senior engineer. Explain 3 design patterns
            using real production examples you've implemented."
""")


def main():
    """
    Main demonstration of iterative refinement.
    """
    print("\n" + "="*60)
    print("MODULE 2: ITERATIVE REFINEMENT")
    print("="*60)
    print("\nKEY INSIGHT: First prompt is never perfect - iterate!")
    print("="*60)

    # Basic iterative improvement
    print("\n" + "🔄"*30)
    print("BASIC EXAMPLE: Explaining MVC")
    print("🔄"*30)

    run_prompt(iteration_1_basic(), "Basic (Too Vague)", 1)
    run_prompt(iteration_2_add_structure(), "Add Structure", 2)
    run_prompt(iteration_3_add_constraints(), "Add Constraints", 3)
    run_prompt(iteration_4_specify_format(), "Specify Format", 4)
    run_prompt(iteration_5_add_context(), "Add Context + Role", 5)

    # Code generation refinement
    demonstrate_code_generation_refinement()

    # Debugging refinement
    demonstrate_debugging_refinement()

    # Feedback loop explanation
    demonstrate_feedback_loop()

    # Refinement patterns
    show_refinement_patterns()

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. First prompt is a DRAFT")
    print("   - Expect to iterate 2-5 times")
    print("   - Each iteration improves specificity")
    print("2. Evaluate every output:")
    print("   - Is it too vague?")
    print("   - Is the format right?")
    print("   - Is it actionable?")
    print("   - Is the level appropriate?")
    print("3. Common refinements:")
    print("   - Add constraints (length, format)")
    print("   - Add examples")
    print("   - Add context")
    print("   - Adjust role/expertise")
    print("   - Specify structure")
    print("4. Build a refinement checklist:")
    print("   - [ ] Clear objective?")
    print("   - [ ] Specific format?")
    print("   - [ ] Appropriate length?")
    print("   - [ ] Concrete examples?")
    print("   - [ ] Right expertise level?")
    print("   - [ ] Actionable output?")
    print("5. Save successful prompts:")
    print("   - Build your prompt library")
    print("   - Reuse refined versions")
    print("   - Share with team")
    print("6. Refinement strategies:")
    print("   - Start broad → narrow down")
    print("   - Start narrow → add context")
    print("   - Compare outputs side-by-side")
    print("   - A/B test different approaches")
    print("="*60)

    print("\n🔄 Pro Tips:")
    print("   - Keep a 'refinement log' of what works")
    print("   - Use version control for prompt iterations")
    print("   - Test prompts with multiple inputs")
    print("   - Collaborate: others spot issues you miss")


if __name__ == "__main__":
    main()
