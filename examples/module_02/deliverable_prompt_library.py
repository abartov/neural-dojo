#!/usr/bin/env python3
"""
Prompt Library & Testing Framework - Module 02 Deliverable
===========================================================

Production-ready CLI tool for managing, testing, and optimizing prompts.

Features:
---------
1. Prompt Template System - Reusable prompts with variables
2. A/B Testing Framework - Compare prompt versions
3. Version Management - Track changes, rollback
4. Performance Testing - Evaluate prompt quality
5. Library Management - Search, filter, organize

Author: Neural Dojo
Module: 02 - Prompt Engineering Fundamentals
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from anthropic import Anthropic
import time


@dataclass
class PromptTemplate:
    """A reusable prompt template with variables."""
    id: str
    name: str
    description: str
    template: str
    category: str
    tags: List[str]
    variables: List[str] = field(default_factory=list)
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    performance_history: List[Dict[str, Any]] = field(default_factory=list)

    def render(self, **kwargs) -> str:
        """Render template with variables."""
        rendered = self.template
        for var in self.variables:
            if var not in kwargs:
                raise ValueError(f"Missing variable: {var}")
            rendered = rendered.replace(f"{{{var}}}", str(kwargs[var]))
        return rendered

    def extract_variables(self):
        """Extract variables from template."""
        self.variables = list(set(re.findall(r'\{(\w+)\}', self.template)))


@dataclass
class TestCase:
    """Test case for prompt evaluation."""
    inputs: Dict[str, str]
    expected_contains: Optional[List[str]] = None
    expected_not_contains: Optional[List[str]] = None
    expected_min_length: Optional[int] = None
    expected_max_length: Optional[int] = None


@dataclass
class TestResult:
    """Result of a prompt test."""
    prompt_id: str
    prompt_version: int
    test_case_index: int
    rendered_prompt: str
    response: str
    response_time: float
    passed: bool
    failures: List[str] = field(default_factory=list)
    score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ABTestResult:
    """Result of an A/B test between two prompts."""
    prompt_a_id: str
    prompt_b_id: str
    test_cases_count: int
    prompt_a_wins: int
    prompt_b_wins: int
    ties: int
    prompt_a_avg_score: float
    prompt_b_avg_score: float
    prompt_a_avg_time: float
    prompt_b_avg_time: float
    winner: Optional[str] = None
    confidence: str = "low"  # low, medium, high


class PromptLibrary:
    """
    Manage a library of reusable prompts with testing and versioning.
    """

    def __init__(self, library_dir: Path = Path('.prompt_library'), api_key: Optional[str] = None):
        """
        Initialize the prompt library.

        Args:
            library_dir: Directory to store prompts and test results
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
        """
        self.library_dir = library_dir
        self.library_dir.mkdir(exist_ok=True)

        self.prompts_file = self.library_dir / 'prompts.json'
        self.tests_dir = self.library_dir / 'tests'
        self.tests_dir.mkdir(exist_ok=True)

        self.prompts: Dict[str, PromptTemplate] = {}
        self.load_prompts()

        # API client
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            print("⚠️  Warning: No API key found. Testing features will be disabled.")
            print("   Set ANTHROPIC_API_KEY environment variable to enable testing.")
            self.client = None
        else:
            self.client = Anthropic(api_key=self.api_key)

    def load_prompts(self):
        """Load prompts from disk."""
        if self.prompts_file.exists():
            with open(self.prompts_file, 'r') as f:
                data = json.load(f)
                self.prompts = {
                    pid: PromptTemplate(**pdata)
                    for pid, pdata in data.items()
                }

    def save_prompts(self):
        """Save prompts to disk."""
        with open(self.prompts_file, 'w') as f:
            json.dump(
                {pid: asdict(p) for pid, p in self.prompts.items()},
                f,
                indent=2
            )

    def add_prompt(
        self,
        name: str,
        template: str,
        description: str,
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> PromptTemplate:
        """Add a new prompt to the library."""
        prompt_id = name.lower().replace(" ", "_")

        if prompt_id in self.prompts:
            raise ValueError(f"Prompt '{prompt_id}' already exists. Use update_prompt() instead.")

        prompt = PromptTemplate(
            id=prompt_id,
            name=name,
            description=description,
            template=template,
            category=category,
            tags=tags or []
        )
        prompt.extract_variables()

        self.prompts[prompt_id] = prompt
        self.save_prompts()

        return prompt

    def update_prompt(self, prompt_id: str, template: Optional[str] = None, **kwargs) -> PromptTemplate:
        """Update an existing prompt (creates new version)."""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt '{prompt_id}' not found")

        prompt = self.prompts[prompt_id]

        # Create new version
        prompt.version += 1
        prompt.updated_at = datetime.now().isoformat()

        if template:
            prompt.template = template
            prompt.extract_variables()

        for key, value in kwargs.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)

        self.save_prompts()
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Get a prompt by ID."""
        return self.prompts.get(prompt_id)

    def search_prompts(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[PromptTemplate]:
        """Search prompts by query, category, or tags."""
        results = list(self.prompts.values())

        if query:
            query = query.lower()
            results = [
                p for p in results
                if query in p.name.lower() or query in p.description.lower()
            ]

        if category:
            results = [p for p in results if p.category == category]

        if tags:
            results = [
                p for p in results
                if any(tag in p.tags for tag in tags)
            ]

        return results

    def test_prompt(
        self,
        prompt_id: str,
        test_cases: List[TestCase],
        model: str = "claude-sonnet-4-5-20250929"
    ) -> List[TestResult]:
        """Test a prompt with multiple test cases."""
        if not self.client:
            raise RuntimeError("API client not initialized. Set ANTHROPIC_API_KEY.")

        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_id}' not found")

        results = []

        for i, test_case in enumerate(test_cases):
            # Render prompt
            try:
                rendered = prompt.render(**test_case.inputs)
            except ValueError as e:
                results.append(TestResult(
                    prompt_id=prompt_id,
                    prompt_version=prompt.version,
                    test_case_index=i,
                    rendered_prompt="",
                    response="",
                    response_time=0.0,
                    passed=False,
                    failures=[str(e)]
                ))
                continue

            # Call API
            start_time = time.time()
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=1500,
                    messages=[{"role": "user", "content": rendered}]
                )
                response_text = response.content[0].text
                response_time = time.time() - start_time
            except Exception as e:
                results.append(TestResult(
                    prompt_id=prompt_id,
                    prompt_version=prompt.version,
                    test_case_index=i,
                    rendered_prompt=rendered,
                    response="",
                    response_time=0.0,
                    passed=False,
                    failures=[f"API error: {str(e)}"]
                ))
                continue

            # Evaluate response
            passed = True
            failures = []
            score = 100.0

            if test_case.expected_contains:
                for expected in test_case.expected_contains:
                    if expected.lower() not in response_text.lower():
                        passed = False
                        failures.append(f"Missing expected text: '{expected}'")
                        score -= 20

            if test_case.expected_not_contains:
                for not_expected in test_case.expected_not_contains:
                    if not_expected.lower() in response_text.lower():
                        passed = False
                        failures.append(f"Contains unexpected text: '{not_expected}'")
                        score -= 20

            if test_case.expected_min_length:
                if len(response_text) < test_case.expected_min_length:
                    passed = False
                    failures.append(
                        f"Response too short: {len(response_text)} < {test_case.expected_min_length}"
                    )
                    score -= 10

            if test_case.expected_max_length:
                if len(response_text) > test_case.expected_max_length:
                    passed = False
                    failures.append(
                        f"Response too long: {len(response_text)} > {test_case.expected_max_length}"
                    )
                    score -= 10

            score = max(0, score)

            results.append(TestResult(
                prompt_id=prompt_id,
                prompt_version=prompt.version,
                test_case_index=i,
                rendered_prompt=rendered,
                response=response_text,
                response_time=response_time,
                passed=passed,
                failures=failures,
                score=score
            ))

        # Save test results
        test_file = self.tests_dir / f"{prompt_id}_v{prompt.version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(test_file, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)

        # Update performance history
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        prompt.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'version': prompt.version,
            'test_cases_count': len(test_cases),
            'avg_score': avg_score,
            'passed': sum(1 for r in results if r.passed),
            'failed': sum(1 for r in results if not r.passed)
        })
        self.save_prompts()

        return results

    def ab_test(
        self,
        prompt_a_id: str,
        prompt_b_id: str,
        test_cases: List[TestCase],
        model: str = "claude-sonnet-4-5-20250929"
    ) -> ABTestResult:
        """Run A/B test between two prompts."""
        print(f"\n🧪 Running A/B Test: {prompt_a_id} vs {prompt_b_id}")
        print(f"Test cases: {len(test_cases)}\n")

        # Test both prompts
        print(f"Testing Prompt A ({prompt_a_id})...")
        results_a = self.test_prompt(prompt_a_id, test_cases, model)

        print(f"Testing Prompt B ({prompt_b_id})...")
        results_b = self.test_prompt(prompt_b_id, test_cases, model)

        # Compare results
        wins_a = 0
        wins_b = 0
        ties = 0

        for ra, rb in zip(results_a, results_b):
            if ra.score > rb.score:
                wins_a += 1
            elif rb.score > ra.score:
                wins_b += 1
            else:
                ties += 1

        avg_score_a = sum(r.score for r in results_a) / len(results_a) if results_a else 0
        avg_score_b = sum(r.score for r in results_b) / len(results_b) if results_b else 0

        avg_time_a = sum(r.response_time for r in results_a) / len(results_a) if results_a else 0
        avg_time_b = sum(r.response_time for r in results_b) / len(results_b) if results_b else 0

        # Determine winner
        winner = None
        confidence = "low"

        if wins_a > wins_b:
            winner = prompt_a_id
            win_rate = wins_a / len(test_cases)
            if win_rate >= 0.8:
                confidence = "high"
            elif win_rate >= 0.6:
                confidence = "medium"
        elif wins_b > wins_a:
            winner = prompt_b_id
            win_rate = wins_b / len(test_cases)
            if win_rate >= 0.8:
                confidence = "high"
            elif win_rate >= 0.6:
                confidence = "medium"

        result = ABTestResult(
            prompt_a_id=prompt_a_id,
            prompt_b_id=prompt_b_id,
            test_cases_count=len(test_cases),
            prompt_a_wins=wins_a,
            prompt_b_wins=wins_b,
            ties=ties,
            prompt_a_avg_score=avg_score_a,
            prompt_b_avg_score=avg_score_b,
            prompt_a_avg_time=avg_time_a,
            prompt_b_avg_time=avg_time_b,
            winner=winner,
            confidence=confidence
        )

        # Save A/B test result
        ab_file = self.tests_dir / f"ab_{prompt_a_id}_vs_{prompt_b_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(ab_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)

        return result

    def print_library(self):
        """Print all prompts in the library."""
        if not self.prompts:
            print("📚 Prompt library is empty. Add prompts with add_prompt().")
            return

        print("\n" + "="*80)
        print(f"📚 PROMPT LIBRARY ({len(self.prompts)} prompts)")
        print("="*80)

        by_category = {}
        for prompt in self.prompts.values():
            if prompt.category not in by_category:
                by_category[prompt.category] = []
            by_category[prompt.category].append(prompt)

        for category, prompts in sorted(by_category.items()):
            print(f"\n📁 {category.upper()} ({len(prompts)} prompts):")
            for prompt in sorted(prompts, key=lambda p: p.name):
                print(f"\n  • {prompt.name} (v{prompt.version})")
                print(f"    ID: {prompt.id}")
                print(f"    {prompt.description}")
                if prompt.tags:
                    print(f"    Tags: {', '.join(prompt.tags)}")
                if prompt.variables:
                    print(f"    Variables: {', '.join(prompt.variables)}")
                if prompt.performance_history:
                    last_perf = prompt.performance_history[-1]
                    print(f"    Last test: {last_perf['passed']}/{last_perf['test_cases_count']} passed, avg score: {last_perf['avg_score']:.1f}")

        print()

    def print_prompt(self, prompt_id: str):
        """Print detailed information about a prompt."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            print(f"❌ Prompt '{prompt_id}' not found")
            return

        print("\n" + "="*80)
        print(f"📄 PROMPT: {prompt.name}")
        print("="*80)
        print(f"\nID: {prompt.id}")
        print(f"Category: {prompt.category}")
        print(f"Version: {prompt.version}")
        print(f"Tags: {', '.join(prompt.tags) if prompt.tags else 'None'}")
        print(f"Variables: {', '.join(prompt.variables) if prompt.variables else 'None'}")
        print(f"\nDescription:")
        print(prompt.description)
        print(f"\nTemplate:")
        print("-" * 80)
        print(prompt.template)
        print("-" * 80)

        if prompt.performance_history:
            print(f"\n📊 Performance History ({len(prompt.performance_history)} tests):")
            for i, perf in enumerate(prompt.performance_history[-5:], 1):  # Last 5
                print(f"\n  Test {i} (v{perf['version']}): {perf['passed']}/{perf['test_cases_count']} passed")
                print(f"    Average score: {perf['avg_score']:.1f}")
                print(f"    Timestamp: {perf['timestamp']}")

        print()

    def print_ab_test_result(self, result: ABTestResult):
        """Print A/B test result."""
        print("\n" + "="*80)
        print("🧪 A/B TEST RESULTS")
        print("="*80)

        print(f"\nPrompt A: {result.prompt_a_id}")
        print(f"Prompt B: {result.prompt_b_id}")
        print(f"Test cases: {result.test_cases_count}")

        print(f"\n📊 Win/Loss Record:")
        print(f"  Prompt A wins: {result.prompt_a_wins} ({result.prompt_a_wins/result.test_cases_count*100:.1f}%)")
        print(f"  Prompt B wins: {result.prompt_b_wins} ({result.prompt_b_wins/result.test_cases_count*100:.1f}%)")
        print(f"  Ties: {result.ties} ({result.ties/result.test_cases_count*100:.1f}%)")

        print(f"\n⭐ Average Scores:")
        print(f"  Prompt A: {result.prompt_a_avg_score:.1f}/100")
        print(f"  Prompt B: {result.prompt_b_avg_score:.1f}/100")

        print(f"\n⚡ Average Response Time:")
        print(f"  Prompt A: {result.prompt_a_avg_time:.2f}s")
        print(f"  Prompt B: {result.prompt_b_avg_time:.2f}s")

        if result.winner:
            emoji = "🏆" if result.confidence == "high" else "🥈" if result.confidence == "medium" else "🥉"
            print(f"\n{emoji} WINNER: {result.winner}")
            print(f"Confidence: {result.confidence.upper()}")
        else:
            print(f"\n🤝 TIE - No clear winner")

        print()


# ============================================================================
# Demo Functions
# ============================================================================

def demo_library_management():
    """Demonstrate prompt library management."""
    print("\n" + "="*80)
    print("DEMO 1: Prompt Library Management")
    print("="*80)
    print("\nManaging a library of reusable prompts...\n")

    library = PromptLibrary()

    # Add sample prompts
    library.add_prompt(
        name="Code Explainer",
        template="Explain this {language} code in simple terms:\n\n{code}\n\nFocus on what it does and why.",
        description="Explains code in simple terms for documentation",
        category="development",
        tags=["code", "documentation", "explanation"]
    )

    library.add_prompt(
        name="Bug Debugger",
        template="Debug this error:\n\nError: {error}\n\nCode:\n{code}\n\nExplain the root cause and suggest a fix.",
        description="Helps debug code errors with AI assistance",
        category="development",
        tags=["debugging", "errors", "troubleshooting"]
    )

    library.add_prompt(
        name="Email Writer",
        template="Write a {tone} email to {recipient} about {subject}.\n\nKey points:\n{key_points}",
        description="Generates professional emails",
        category="communication",
        tags=["email", "writing", "business"]
    )

    print("✅ Added 3 prompts to library")

    # Display library
    library.print_library()

    # Search prompts
    print("\n🔍 Searching for prompts with tag 'debugging'...")
    results = library.search_prompts(tags=["debugging"])
    print(f"Found {len(results)} prompts:")
    for p in results:
        print(f"  • {p.name}")

    # Show detailed prompt
    library.print_prompt("code_explainer")


def demo_prompt_testing():
    """Demonstrate prompt testing."""
    print("\n" + "="*80)
    print("DEMO 2: Prompt Testing")
    print("="*80)
    print("\nTesting prompts with automated test cases...\n")

    library = PromptLibrary()

    # Add a prompt for testing
    library.add_prompt(
        name="Python Explainer",
        template="Explain this Python code concisely:\n\n{code}\n\nKeep it under 100 words.",
        description="Explains Python code concisely",
        category="development",
        tags=["python", "explanation"]
    )

    if not library.client:
        print("⚠️  Skipping API testing (no API key)")
        return

    # Define test cases
    test_cases = [
        TestCase(
            inputs={"code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"},
            expected_contains=["factorial", "recursive"],
            expected_max_length=600
        ),
        TestCase(
            inputs={"code": "squares = [x**2 for x in range(10)]"},
            expected_contains=["list", "comprehension"],
            expected_max_length=600
        )
    ]

    # Test the prompt
    print(f"Testing 'python_explainer' with {len(test_cases)} test cases...")
    results = library.test_prompt("python_explainer", test_cases)

    # Print results
    passed = sum(1 for r in results if r.passed)
    print(f"\n✅ Test Results: {passed}/{len(results)} passed")

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"\n  Test {i}: {status} (Score: {result.score:.1f}/100, Time: {result.response_time:.2f}s)")
        if result.failures:
            for failure in result.failures:
                print(f"    - {failure}")


def demo_ab_testing():
    """Demonstrate A/B testing."""
    print("\n" + "="*80)
    print("DEMO 3: A/B Testing")
    print("="*80)
    print("\nComparing two prompt versions side-by-side...\n")

    library = PromptLibrary()

    # Version A: Simple prompt
    library.add_prompt(
        name="Summarizer A",
        template="Summarize this text:\n\n{text}",
        description="Simple summarization prompt",
        category="writing",
        tags=["summarization"]
    )

    # Version B: Detailed prompt with instructions
    library.add_prompt(
        name="Summarizer B",
        template="Summarize the following text in 2-3 sentences. Focus on the main points and key takeaways:\n\n{text}\n\nSummary:",
        description="Detailed summarization prompt with structure",
        category="writing",
        tags=["summarization"]
    )

    if not library.client:
        print("⚠️  Skipping A/B testing (no API key)")
        print("\n💡 With API key, you would see:")
        print("  - Win/loss record between prompts")
        print("  - Average scores and response times")
        print("  - Statistical confidence in winner")
        print("  - Detailed comparison metrics")
        return

    # Define test cases
    test_text = """
    Artificial intelligence (AI) is rapidly transforming the software industry.
    Developers are using AI tools for code generation, debugging, and optimization.
    Tools like GitHub Copilot and ChatGPT have become essential productivity aids.
    However, AI also raises concerns about code quality, security, and developer skill atrophy.
    """

    test_cases = [
        TestCase(
            inputs={"text": test_text},
            expected_contains=["AI", "developers"],
            expected_min_length=50,
            expected_max_length=400
        )
    ]

    # Run A/B test
    result = library.ab_test("summarizer_a", "summarizer_b", test_cases)
    library.print_ab_test_result(result)


def demo_version_management():
    """Demonstrate prompt version management."""
    print("\n" + "="*80)
    print("DEMO 4: Version Management")
    print("="*80)
    print("\nTracking prompt changes over time...\n")

    library = PromptLibrary()

    # Create initial prompt
    prompt = library.add_prompt(
        name="Code Reviewer",
        template="Review this code:\n\n{code}",
        description="Code review prompt",
        category="development",
        tags=["code-review"]
    )

    print(f"✅ Created 'code_reviewer' (v{prompt.version})")
    print(f"   Template: {prompt.template[:50]}...")

    # Update version 1 → 2
    prompt = library.update_prompt(
        "code_reviewer",
        template="Review this {language} code for quality and best practices:\n\n{code}\n\nProvide specific improvement suggestions."
    )

    print(f"\n✅ Updated to v{prompt.version}")
    print(f"   Template: {prompt.template[:80]}...")

    # Update version 2 → 3
    prompt = library.update_prompt(
        "code_reviewer",
        template="Review this {language} code:\n\n{code}\n\nAnalyze:\n1. Code quality\n2. Best practices\n3. Potential bugs\n4. Performance\n\nProvide specific, actionable feedback."
    )

    print(f"\n✅ Updated to v{prompt.version}")
    print(f"   Template: {prompt.template[:80]}...")

    # Show version history
    library.print_prompt("code_reviewer")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║               Prompt Library & Testing Framework v1.0                     ║
║                   Module 02 - Neural Dojo Deliverable                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

Production-ready CLI tool for managing and testing prompts.

USAGE:
    python deliverable_prompt_library.py <command>

COMMANDS:
    demo1    - Library Management (add, search, view prompts)
    demo2    - Prompt Testing (automated test cases)
    demo3    - A/B Testing (compare prompt versions)
    demo4    - Version Management (track prompt changes)
    all      - Run all demonstrations

EXAMPLES:
    python deliverable_prompt_library.py demo1
    python deliverable_prompt_library.py all

REQUIREMENTS:
    - Python 3.10+
    - anthropic library (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable (optional, for testing)

NOTE:
    Library management works without API key. Testing features require API key.

For more information, see DELIVERABLE_README.md
""")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'demo1':
        demo_library_management()
    elif command == 'demo2':
        demo_prompt_testing()
    elif command == 'demo3':
        demo_ab_testing()
    elif command == 'demo4':
        demo_version_management()
    elif command == 'all':
        demo_library_management()
        input("\nPress Enter to continue to demo 2...")
        demo_prompt_testing()
        input("\nPress Enter to continue to demo 3...")
        demo_ab_testing()
        input("\nPress Enter to continue to demo 4...")
        demo_version_management()

        print("\n" + "="*80)
        print("✅ All demonstrations complete!")
        print("="*80)
        print("\n📁 Check .prompt_library/ directory for saved prompts and test results")
        print("💡 Use this library in your own projects for systematic prompt management!")
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run without arguments to see usage.")
        sys.exit(1)


if __name__ == '__main__':
    main()
