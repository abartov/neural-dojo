#!/usr/bin/env python3
"""
Module 2: Code-Specific Tasks

Demonstrates prompts optimized for common coding tasks:
- Code explanation
- Code review
- Refactoring
- Test generation
- Documentation
- Debugging

KEY INSIGHT: Different tasks need different prompt structures!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# Sample code for demonstrations
SAMPLE_CODE = """
def calculate_discount(price, discount_percent, membership_level):
    if membership_level == 'gold':
        discount_percent += 10
    elif membership_level == 'silver':
        discount_percent += 5

    discount = price * (discount_percent / 100)
    final_price = price - discount

    return final_price
"""


def code_explanation_prompt():
    """
    Prompt for explaining code with depth.
    """
    prompt = f"""
Explain this Python function comprehensively:

```python
{SAMPLE_CODE}
```

Provide:
1. **High-level purpose** (1-2 sentences)
2. **Step-by-step breakdown**:
   - What each line does
   - Why it's structured this way
3. **Parameters**:
   - Type and purpose of each
4. **Return value**:
   - What it returns and why
5. **Edge cases to consider**:
   - What could go wrong?
   - Missing validation?
6. **Complexity analysis**:
   - Time: O(?)
   - Space: O(?)

Be thorough but concise.
"""
    return prompt


def code_review_prompt():
    """
    Prompt for comprehensive code review.
    """
    prompt = f"""
You are a senior engineer doing a code review.

Review this Python function:

```python
{SAMPLE_CODE}
```

Check for:
1. **Logic errors or bugs**
2. **Type safety issues**
3. **Missing error handling**
4. **Code clarity and naming**
5. **Performance concerns**
6. **Security vulnerabilities**
7. **Best practices violations**

For each issue found, provide:
- **Issue**: [description]
- **Severity**: Critical/High/Medium/Low
- **Why it matters**: [explanation]
- **Fix**: [corrected code snippet]

Then provide the complete refactored version.
"""
    return prompt


def refactoring_prompt():
    """
    Prompt for code refactoring.
    """
    prompt = f"""
Refactor this Python function to improve:
- Readability
- Maintainability
- Type safety
- Error handling

Original code:
```python
{SAMPLE_CODE}
```

Provide:
1. **Refactored code** with:
   - Type hints
   - Docstring (Google style)
   - Input validation
   - Better variable names (if needed)
   - Error handling

2. **Changelog**:
   - What changed and why
   - Trade-offs made (if any)

3. **Before/After comparison**:
   - Readability: [improvement]
   - Safety: [improvement]
   - Maintainability: [improvement]

Show the complete refactored function.
"""
    return prompt


def test_generation_prompt():
    """
    Prompt for generating comprehensive tests.
    """
    prompt = f"""
Generate pytest tests for this function:

```python
{SAMPLE_CODE}
```

Requirements:
1. **Happy path tests**:
   - Normal usage scenarios
   - Different membership levels

2. **Edge case tests**:
   - Zero discount
   - 100% discount
   - Negative values
   - None values
   - Invalid membership levels

3. **Parametrize** where appropriate

4. Include:
   - Descriptive test names
   - Arrange-Act-Assert pattern
   - Clear assertions with messages

5. Aim for >90% coverage

Show the complete test file with all imports.
"""
    return prompt


def documentation_prompt():
    """
    Prompt for adding documentation.
    """
    prompt = f"""
Add comprehensive documentation to this function:

```python
{SAMPLE_CODE}
```

Requirements:
1. **Docstring** (Google style):
   - Summary line
   - Detailed description
   - Args: with types and descriptions
   - Returns: with type and description
   - Raises: potential exceptions
   - Examples: 2-3 usage examples

2. **Inline comments**:
   - Only for non-obvious logic
   - Explain WHY, not WHAT

3. **Type hints**:
   - For all parameters
   - For return value
   - Use appropriate types (int, float, str, Optional, Literal)

Show the fully documented function.
"""
    return prompt


def debugging_prompt():
    """
    Prompt for systematic debugging.
    """
    buggy_code = """
def get_user_stats(users):
    total_age = sum([user['age'] for user in users])
    avg_age = total_age / len(users)

    active_users = [u for u in users if u['status'] == 'active']
    active_percent = (len(active_users) / len(users)) * 100

    return {
        'avg_age': avg_age,
        'active_percent': active_percent
    }

# Fails with: TypeError: 'NoneType' object is not subscriptable
# When called with: get_user_stats([{'name': 'Alice', 'age': 30, 'status': 'active'}, None])
"""

    prompt = f"""
Debug this Python function systematically:

```python
{buggy_code}
```

Process:
1. **Identify the error**:
   - What line causes it?
   - What's the exact error?

2. **Root cause analysis**:
   - Why does this happen?
   - What assumptions does the code make?

3. **Reproduce**:
   - Show the exact input that triggers it
   - Explain the execution flow

4. **Fix options** (provide 2-3):
   - Option A: [approach]
     - Pros: ...
     - Cons: ...
     - Code: [show fix]

   - Option B: [approach]
     - Pros: ...
     - Cons: ...
     - Code: [show fix]

5. **Best solution**:
   - Which option is best and why?
   - Show complete fixed code

6. **Prevention**:
   - How to prevent similar bugs?
   - What tests would catch this?

7. **Additional edge cases to consider**:
   - What else could go wrong?
"""
    return prompt


def optimization_prompt():
    """
    Prompt for performance optimization.
    """
    slow_code = """
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
"""

    prompt = f"""
Optimize this Python function for performance:

```python
{slow_code}
```

Analysis:
1. **Current complexity**:
   - Time: O(?)
   - Space: O(?)
   - Explain why

2. **Bottlenecks**:
   - What makes it slow?
   - What operations are expensive?

3. **Optimization opportunities**:
   - List 3 potential improvements

4. **Optimized solution**:
   - Show improved code
   - New time complexity: O(?)
   - New space complexity: O(?)

5. **Trade-offs**:
   - What did we sacrifice (if anything)?
   - When is the optimized version better?
   - When might the original be preferable?

6. **Benchmarking suggestion**:
   - How to measure the improvement?
   - What input sizes to test?

Show the complete optimized function with explanation.
"""
    return prompt


def run_prompt(prompt: str, label: str):
    """Execute a prompt and display results."""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"\nPrompt Length: {len(prompt)} chars")
    print(f"\n{'-'*60}\nResponse:")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(result)

    return result


def main():
    """
    Main demonstration of code-specific prompts.
    """
    print("\n" + "="*60)
    print("MODULE 2: CODE-SPECIFIC TASKS")
    print("="*60)
    print("\nKEY INSIGHT: Different tasks need different prompt structures!")
    print("="*60)

    print("\nSample code we'll work with:")
    print(SAMPLE_CODE)

    # 1. Code Explanation
    print("\n" + "📖"*30)
    print("TASK 1: CODE EXPLANATION")
    print("📖"*30)
    run_prompt(code_explanation_prompt(), "Comprehensive Code Explanation")

    # 2. Code Review
    print("\n" + "🔍"*30)
    print("TASK 2: CODE REVIEW")
    print("🔍"*30)
    run_prompt(code_review_prompt(), "Senior Engineer Code Review")

    # 3. Refactoring
    print("\n" + "♻️"*30)
    print("TASK 3: REFACTORING")
    print("♻️"*30)
    run_prompt(refactoring_prompt(), "Code Refactoring")

    # 4. Test Generation
    print("\n" + "🧪"*30)
    print("TASK 4: TEST GENERATION")
    print("🧪"*30)
    run_prompt(test_generation_prompt(), "Comprehensive Test Suite")

    # 5. Documentation
    print("\n" + "📝"*30)
    print("TASK 5: DOCUMENTATION")
    print("📝"*30)
    run_prompt(documentation_prompt(), "Full Documentation")

    # 6. Debugging
    print("\n" + "🐛"*30)
    print("TASK 6: DEBUGGING")
    print("🐛"*30)
    run_prompt(debugging_prompt(), "Systematic Debugging")

    # 7. Optimization
    print("\n" + "⚡"*30)
    print("TASK 7: OPTIMIZATION")
    print("⚡"*30)
    run_prompt(optimization_prompt(), "Performance Optimization")

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. Task-specific prompts work better:")
    print("   - Explanation: Focus on understanding")
    print("   - Review: Focus on issues and fixes")
    print("   - Refactoring: Focus on improvements")
    print("   - Testing: Focus on coverage")
    print("   - Documentation: Focus on clarity")
    print("   - Debugging: Focus on root cause")
    print("   - Optimization: Focus on performance")
    print("")
    print("2. Prompt structure matters:")
    print("   - Clear task definition")
    print("   - Specific requirements")
    print("   - Expected output format")
    print("   - Context and constraints")
    print("")
    print("3. Be explicit about depth:")
    print("   - 'Explain comprehensively' vs 'Explain briefly'")
    print("   - 'List issues' vs 'Analyze and fix'")
    print("   - '90% coverage' vs 'Basic tests'")
    print("")
    print("4. Request actionable outputs:")
    print("   - Not just 'review', but 'review and provide fixes'")
    print("   - Not just 'explain bug', but 'show solution'")
    print("   - Not just 'suggest', but 'implement'")
    print("")
    print("5. Include evaluation criteria:")
    print("   - Complexity analysis")
    print("   - Trade-offs")
    print("   - Before/after comparison")
    print("   - Success metrics")
    print("")
    print("6. Build a task library:")
    print("   - Save these prompts")
    print("   - Customize for your codebase")
    print("   - Share with team")
    print("="*60)

    print("\n💻 Pro Tips:")
    print("   - Combine tasks: 'Review, refactor, and add tests'")
    print("   - Use in CI/CD: Automated code reviews")
    print("   - Integrate with IDE: Quick prompts via hotkeys")
    print("   - Build workflows: Explain → Review → Refactor → Test")

    print("\n🔧 Integration Ideas:")
    print("   - Pre-commit hook: Auto code review")
    print("   - PR comments: Automated suggestions")
    print("   - Documentation: Auto-generate on commit")
    print("   - Onboarding: Explain codebase to new devs")


if __name__ == "__main__":
    main()
