#!/usr/bin/env python3
"""
Module 2: Building a Prompt Library

Demonstrates how to create reusable prompt templates for common tasks.

KEY INSIGHT: Don't reinvent prompts! Build templates you can reuse.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class PromptLibrary:
    """
    Reusable prompt templates for common development tasks.

    Usage:
        lib = PromptLibrary()
        prompt = lib.explain_code(language="Python", code=my_code)
        response = run_prompt(prompt)
    """

    @staticmethod
    def explain_code(language: str, code: str) -> str:
        """Explain code with line-by-line breakdown."""
        return f"""
Explain this {language} code:

```{language.lower()}
{code}
```

Provide:
1. High-level summary (1-2 sentences)
2. Line-by-line breakdown
3. Time/space complexity analysis
4. Potential improvements or concerns
"""

    @staticmethod
    def debug_code(language: str, code: str, error: str) -> str:
        """Debug code with systematic analysis."""
        return f"""
Debug this {language} code that's throwing: {error}

```{language.lower()}
{code}
```

Please:
1. Identify the root cause
2. Explain WHY this error occurs
3. Provide the corrected code
4. Suggest how to prevent similar issues
5. List edge cases to test
"""

    @staticmethod
    def generate_tests(language: str, code: str, framework: str = "pytest") -> str:
        """Generate comprehensive tests."""
        return f"""
Generate {framework} tests for this {language} function:

```{language.lower()}
{code}
```

Include tests for:
- Happy path (expected usage)
- Edge cases (empty, null, boundaries)
- Error conditions
- Type validation (if applicable)

Aim for >90% code coverage.
"""

    @staticmethod
    def code_review(language: str, code: str) -> str:
        """Perform code review as senior engineer."""
        return f"""
Review this {language} code as a senior engineer:

```{language.lower()}
{code}
```

Check for:
- Logic errors or bugs
- Security vulnerabilities
- Performance issues
- Code style and best practices
- Missing error handling
- Documentation quality

Format each issue as:
Issue: [description]
Severity: Critical/High/Medium/Low
Suggestion: [how to fix]
Fixed Code: [corrected version]
"""

    @staticmethod
    def refactor_code(language: str, code: str, goals: str = "readability, performance, maintainability") -> str:
        """Refactor code for improvement."""
        return f"""
Refactor this {language} code to improve: {goals}

Original Code:
```{language.lower()}
{code}
```

Provide:
1. Refactored code
2. Explanation of each change
3. Before/After comparison for key metrics:
   - Readability: [improvement]
   - Performance: [improvement]
   - Maintainability: [improvement]
"""

    @staticmethod
    def document_code(language: str, code: str, style: str = "Google") -> str:
        """Generate documentation."""
        return f"""
Add comprehensive {style}-style documentation to this {language} code:

```{language.lower()}
{code}
```

Include:
- Module/file docstring
- Function/method docstrings
- Parameter descriptions with types
- Return value descriptions
- Example usage
- Notes about edge cases or limitations
"""

    @staticmethod
    def translate_code(from_lang: str, to_lang: str, code: str) -> str:
        """Translate code between languages."""
        return f"""
Translate this {from_lang} code to {to_lang}:

```{from_lang.lower()}
{code}
```

Requirements:
1. Preserve the logic and behavior
2. Use idiomatic {to_lang} patterns
3. Include type hints (if {to_lang} supports them)
4. Add comments explaining {to_lang}-specific features
5. Note any differences in behavior between languages
"""

    @staticmethod
    def optimize_code(language: str, code: str, metric: str = "time complexity") -> str:
        """Optimize code for specific metric."""
        return f"""
Optimize this {language} code for {metric}:

```{language.lower()}
{code}
```

Provide:
1. Current {metric}: [analysis]
2. Optimization opportunities: [list]
3. Optimized code
4. Improved {metric}: [analysis]
5. Trade-offs made: [if any]
6. Benchmarking suggestions
"""


def run_prompt(prompt: str) -> str:
    """Execute a prompt and return the response."""
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def demonstrate_library():
    """
    Demonstrate the prompt library with real examples.
    """
    print("\n" + "="*60)
    print("PROMPT LIBRARY DEMONSTRATION")
    print("="*60)

    lib = PromptLibrary()

    # Example 1: Explain Code
    print("\n" + "📖"*30)
    print("1. EXPLAIN CODE")
    print("="*60)

    code_to_explain = """
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
"""

    prompt = lib.explain_code("Python", code_to_explain)
    print(f"Prompt Generated:\n{prompt}")
    print("\n" + "-"*60)
    print("Response:")
    response = run_prompt(prompt)
    print(response)

    # Example 2: Debug Code
    print("\n\n" + "🐛"*30)
    print("2. DEBUG CODE")
    print("="*60)

    buggy_code = """
def get_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count
"""

    prompt = lib.debug_code("Python", buggy_code, "ZeroDivisionError when called with empty list")
    print(f"Prompt Generated:\n{prompt}")
    print("\n" + "-"*60)
    print("Response:")
    response = run_prompt(prompt)
    print(response)

    # Example 3: Generate Tests
    print("\n\n" + "🧪"*30)
    print("3. GENERATE TESTS")
    print("="*60)

    function_to_test = """
def is_palindrome(s: str) -> bool:
    s = s.lower().replace(" ", "")
    return s == s[::-1]
"""

    prompt = lib.generate_tests("Python", function_to_test)
    print(f"Prompt Generated:\n{prompt}")
    print("\n" + "-"*60)
    print("Response:")
    response = run_prompt(prompt)
    print(response)


def show_library_usage():
    """
    Show how to use the library in practice.
    """
    print("\n\n" + "💡"*30)
    print("USING THE PROMPT LIBRARY IN YOUR WORKFLOW")
    print("="*60)

    print("""
# In your code:
from prompt_library import PromptLibrary

lib = PromptLibrary()

# Need to understand some code?
prompt = lib.explain_code("Python", mysterious_code)
explanation = your_llm_call(prompt)

# Found a bug?
prompt = lib.debug_code("Python", buggy_code, error_message)
fix = your_llm_call(prompt)

# Need tests?
prompt = lib.generate_tests("Python", new_function)
tests = your_llm_call(prompt)

# Code review before committing?
prompt = lib.code_review("Python", your_changes)
review = your_llm_call(prompt)
""")


def main():
    """
    Main demonstration.
    """
    print("\n" + "="*60)
    print("MODULE 2: BUILDING A PROMPT LIBRARY")
    print("="*60)
    print("\nKEY INSIGHT: Reusable templates = 10x productivity!")
    print("="*60)

    demonstrate_library()

    show_library_usage()

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. Build templates for repetitive tasks")
    print("2. Parameterize: language, code, goals, etc.")
    print("3. Include clear instructions in templates")
    print("4. Start with 5-10 common tasks:")
    print("   - Code explanation")
    print("   - Debugging")
    print("   - Test generation")
    print("   - Code review")
    print("   - Refactoring")
    print("   - Documentation")
    print("   - Translation")
    print("   - Optimization")
    print("5. Iterate: Improve templates based on results")
    print("6. Share: Build org-wide prompt libraries!")
    print("="*60)

    print("\n💾 Next Steps:")
    print("- Save these templates")
    print("- Create your own for your specific tasks")
    print("- Build a personal prompt library")
    print("- Share effective prompts with your team")


if __name__ == "__main__":
    main()
