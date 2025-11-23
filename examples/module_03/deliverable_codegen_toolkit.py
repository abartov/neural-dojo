#!/usr/bin/env python3
"""
Module 03 Deliverable: Code Generation Workflow Toolkit

A production-ready CLI tool for managing AI-powered code generation workflows.

Features:
- Template library for reusable code generation specs
- AI-powered code generation with multiple models
- Automatic test generation
- Security and quality code review
- Iteration tracking and version control
- Export/import workflows

Author: Neural Dojo
Date: 2025-11-23
"""

import json
import re
import os
import ast
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

# Optional dependencies (graceful degradation)
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CodeSpec:
    """Specification for code generation."""
    id: str
    name: str
    description: str
    requirements: List[str]
    language: str = "python"
    includes_tests: bool = True
    security_requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_prompt(self) -> str:
        """Convert specification to generation prompt."""
        prompt = f"# {self.name}\n\n{self.description}\n\n"

        if self.requirements:
            prompt += "## Requirements:\n"
            for req in self.requirements:
                prompt += f"- {req}\n"
            prompt += "\n"

        if self.security_requirements:
            prompt += "## Security Requirements:\n"
            for req in self.security_requirements:
                prompt += f"- {req}\n"
            prompt += "\n"

        if self.constraints:
            prompt += "## Constraints:\n"
            for con in self.constraints:
                prompt += f"- {con}\n"
            prompt += "\n"

        if self.examples:
            prompt += "## Examples:\n"
            for ex in self.examples:
                prompt += f"{ex}\n\n"

        prompt += f"\nGenerate production-quality {self.language} code."
        if self.includes_tests:
            prompt += " Include comprehensive tests."

        return prompt


@dataclass
class GeneratedCode:
    """Generated code with metadata."""
    spec_id: str
    code: str
    tests: Optional[str] = None
    version: int = 1
    model: str = "claude-sonnet-4-5"
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    review_results: Dict[str, Any] = field(default_factory=dict)
    iteration_notes: str = ""


@dataclass
class CodeReviewResult:
    """Results from code review."""
    passed: bool
    security_issues: List[Dict[str, str]] = field(default_factory=list)
    quality_issues: List[Dict[str, str]] = field(default_factory=list)
    complexity_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class CodeGenToolkit:
    """
    Code Generation Workflow Toolkit.

    Manages code generation templates, generates code with AI,
    performs security/quality reviews, and tracks iterations.
    """

    def __init__(self, storage_dir: str = ".codegen_toolkit"):
        """
        Initialize the toolkit.

        Args:
            storage_dir: Directory for storing specs and generated code
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.specs_file = self.storage_dir / "specs.json"
        self.generated_file = self.storage_dir / "generated.json"

        self.specs: Dict[str, CodeSpec] = {}
        self.generated: Dict[str, List[GeneratedCode]] = {}

        # Initialize AI client if available
        self.client = None
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("ANTHROPIC_API_KEY not set - AI features disabled")
        else:
            logger.warning("anthropic package not installed - AI features disabled")

        # Load existing data
        self._load_specs()
        self._load_generated()

    def _load_specs(self):
        """Load specifications from storage."""
        if self.specs_file.exists():
            with open(self.specs_file, 'r') as f:
                data = json.load(f)
                self.specs = {
                    k: CodeSpec(**v) for k, v in data.items()
                }
            logger.info(f"Loaded {len(self.specs)} specifications")

    def _save_specs(self):
        """Save specifications to storage."""
        with open(self.specs_file, 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.specs.items()},
                f,
                indent=2
            )

    def _load_generated(self):
        """Load generated code from storage."""
        if self.generated_file.exists():
            with open(self.generated_file, 'r') as f:
                data = json.load(f)
                self.generated = {
                    k: [GeneratedCode(**item) for item in v]
                    for k, v in data.items()
                }
            logger.info(f"Loaded {sum(len(v) for v in self.generated.values())} generated code items")

    def _save_generated(self):
        """Save generated code to storage."""
        with open(self.generated_file, 'w') as f:
            json.dump(
                {k: [asdict(item) for item in v] for k, v in self.generated.items()},
                f,
                indent=2
            )

    def add_spec(
        self,
        name: str,
        description: str,
        requirements: List[str],
        language: str = "python",
        security_requirements: List[str] = None,
        constraints: List[str] = None,
        examples: List[str] = None
    ) -> CodeSpec:
        """
        Add a code generation specification.

        Args:
            name: Specification name
            description: What to generate
            requirements: Functional requirements
            language: Programming language
            security_requirements: Security constraints
            constraints: Technical constraints
            examples: Example code or usage

        Returns:
            Created CodeSpec
        """
        spec_id = name.lower().replace(" ", "_")

        spec = CodeSpec(
            id=spec_id,
            name=name,
            description=description,
            requirements=requirements,
            language=language,
            security_requirements=security_requirements or [],
            constraints=constraints or [],
            examples=examples or []
        )

        self.specs[spec_id] = spec
        self._save_specs()

        logger.info(f"Added specification: {name}")
        return spec

    def generate_code(
        self,
        spec_id: str,
        model: str = "claude-sonnet-4-5",
        iteration_notes: str = ""
    ) -> Optional[GeneratedCode]:
        """
        Generate code from specification using AI.

        Args:
            spec_id: Specification ID
            model: AI model to use
            iteration_notes: Notes about this iteration

        Returns:
            GeneratedCode object or None if failed
        """
        if spec_id not in self.specs:
            logger.error(f"Specification not found: {spec_id}")
            return None

        if not self.client:
            logger.error("AI client not available - set ANTHROPIC_API_KEY")
            return None

        spec = self.specs[spec_id]
        prompt = spec.to_prompt()

        try:
            # Generate code
            logger.info(f"Generating code for: {spec.name}")
            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            code_text = response.content[0].text

            # Try to separate code and tests
            code, tests = self._extract_code_and_tests(code_text)

            # Determine version number
            version = 1
            if spec_id in self.generated:
                version = len(self.generated[spec_id]) + 1

            # Create generated code object
            generated = GeneratedCode(
                spec_id=spec_id,
                code=code,
                tests=tests,
                version=version,
                model=model,
                iteration_notes=iteration_notes
            )

            # Store
            if spec_id not in self.generated:
                self.generated[spec_id] = []
            self.generated[spec_id].append(generated)
            self._save_generated()

            logger.info(f"Code generated successfully (version {version})")
            return generated

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return None

    def _extract_code_and_tests(self, text: str) -> tuple[str, Optional[str]]:
        """
        Extract code and tests from AI response.

        Args:
            text: AI response text

        Returns:
            (code, tests) tuple
        """
        # Look for code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', text, re.DOTALL)

        if not code_blocks:
            return text, None

        # Heuristic: blocks with "test" or "def test_" are test code
        code_parts = []
        test_parts = []

        for block in code_blocks:
            if 'def test_' in block or 'import pytest' in block or 'import unittest' in block:
                test_parts.append(block)
            else:
                code_parts.append(block)

        code = '\n\n'.join(code_parts) if code_parts else code_blocks[0]
        tests = '\n\n'.join(test_parts) if test_parts else None

        return code, tests

    def review_code(self, spec_id: str, version: int = -1) -> Optional[CodeReviewResult]:
        """
        Review generated code for security and quality issues.

        Args:
            spec_id: Specification ID
            version: Version to review (-1 for latest)

        Returns:
            CodeReviewResult or None
        """
        if spec_id not in self.generated:
            logger.error(f"No generated code for: {spec_id}")
            return None

        generated_list = self.generated[spec_id]
        if version == -1:
            generated = generated_list[-1]
        elif 0 <= version < len(generated_list):
            generated = generated_list[version]
        else:
            logger.error(f"Invalid version: {version}")
            return None

        code = generated.code

        # Perform static analysis
        security_issues = self._check_security(code)
        quality_issues = self._check_quality(code)
        complexity_score = self._calculate_complexity(code)
        recommendations = self._generate_recommendations(
            security_issues,
            quality_issues,
            complexity_score
        )

        result = CodeReviewResult(
            passed=len(security_issues) == 0 and len(quality_issues) < 3,
            security_issues=security_issues,
            quality_issues=quality_issues,
            complexity_score=complexity_score,
            recommendations=recommendations
        )

        # Store review results
        generated.review_results = asdict(result)
        self._save_generated()

        return result

    def _check_security(self, code: str) -> List[Dict[str, str]]:
        """Check for common security issues."""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return [{"type": "syntax_error", "severity": "HIGH", "message": "Code has syntax errors"}]

        # Check for SQL injection patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'execute':
                        # Check if query is constructed with f-strings or +
                        for arg in node.args:
                            if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                                issues.append({
                                    "type": "sql_injection",
                                    "severity": "HIGH",
                                    "message": f"Potential SQL injection at line {node.lineno}",
                                    "line": node.lineno
                                })

        # Check for command injection (os.system, subprocess with shell=True)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'system':
                        issues.append({
                            "type": "command_injection",
                            "severity": "HIGH",
                            "message": f"os.system() is vulnerable to command injection at line {node.lineno}",
                            "line": node.lineno
                        })
                elif isinstance(node.func, ast.Name):
                    if node.func.id == 'eval' or node.func.id == 'exec':
                        issues.append({
                            "type": "code_injection",
                            "severity": "CRITICAL",
                            "message": f"Use of {node.func.id}() is dangerous at line {node.lineno}",
                            "line": node.lineno
                        })

        # Check for hardcoded secrets
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if any(keyword in var_name for keyword in ['password', 'secret', 'key', 'token']):
                            if isinstance(node.value, ast.Constant):
                                issues.append({
                                    "type": "hardcoded_secret",
                                    "severity": "HIGH",
                                    "message": f"Potential hardcoded secret '{target.id}' at line {node.lineno}",
                                    "line": node.lineno
                                })

        return issues

    def _check_quality(self, code: str) -> List[Dict[str, str]]:
        """Check for code quality issues."""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        # Check for mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "type": "mutable_default",
                            "severity": "MEDIUM",
                            "message": f"Mutable default argument in '{node.name}' at line {node.lineno}",
                            "line": node.lineno
                        })

        # Check for bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append({
                        "type": "bare_except",
                        "severity": "MEDIUM",
                        "message": f"Bare except clause at line {node.lineno}",
                        "line": node.lineno
                    })

        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if ast.get_docstring(node) is None:
                    issues.append({
                        "type": "missing_docstring",
                        "severity": "LOW",
                        "message": f"Missing docstring for '{node.name}' at line {node.lineno}",
                        "line": node.lineno
                    })

        return issues

    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity score (simplified cyclomatic complexity)."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 100.0  # Max complexity for unparseable code

        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return min(complexity / 10.0 * 100, 100)  # Normalize to 0-100

    def _generate_recommendations(
        self,
        security_issues: List[Dict[str, str]],
        quality_issues: List[Dict[str, str]],
        complexity_score: float
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if security_issues:
            recommendations.append(f"Fix {len(security_issues)} security issue(s) before deployment")

        if len(quality_issues) >= 5:
            recommendations.append("Consider refactoring - too many quality issues")

        if complexity_score > 50:
            recommendations.append("High complexity - consider breaking into smaller functions")

        # Type-specific recommendations
        for issue in security_issues:
            if issue['type'] == 'sql_injection':
                recommendations.append("Use parameterized queries to prevent SQL injection")
            elif issue['type'] == 'command_injection':
                recommendations.append("Use subprocess.run() with list of arguments instead of shell=True")

        for issue in quality_issues:
            if issue['type'] == 'mutable_default':
                recommendations.append("Replace mutable default arguments with None and initialize in function body")

        if not recommendations:
            recommendations.append("Code looks good! Consider adding more edge case tests")

        return recommendations

    def list_specs(self) -> List[CodeSpec]:
        """List all specifications."""
        return list(self.specs.values())

    def get_spec(self, spec_id: str) -> Optional[CodeSpec]:
        """Get specification by ID."""
        return self.specs.get(spec_id)

    def get_generated(self, spec_id: str, version: int = -1) -> Optional[GeneratedCode]:
        """Get generated code by spec ID and version."""
        if spec_id not in self.generated:
            return None

        generated_list = self.generated[spec_id]
        if version == -1:
            return generated_list[-1]
        elif 0 <= version < len(generated_list):
            return generated_list[version]

        return None

    def export_code(self, spec_id: str, version: int = -1, output_dir: str = "output") -> bool:
        """
        Export generated code to files.

        Args:
            spec_id: Specification ID
            version: Version to export (-1 for latest)
            output_dir: Output directory

        Returns:
            True if successful
        """
        generated = self.get_generated(spec_id, version)
        if not generated:
            logger.error(f"No generated code found for {spec_id}")
            return False

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Export main code
        code_file = output_path / f"{spec_id}.py"
        with open(code_file, 'w') as f:
            f.write(generated.code)
        logger.info(f"Exported code to {code_file}")

        # Export tests if available
        if generated.tests:
            test_file = output_path / f"test_{spec_id}.py"
            with open(test_file, 'w') as f:
                f.write(generated.tests)
            logger.info(f"Exported tests to {test_file}")

        return True

    def print_spec(self, spec_id: str):
        """Print specification details."""
        spec = self.get_spec(spec_id)
        if not spec:
            print(f"❌ Specification not found: {spec_id}")
            return

        print(f"\n{'='*60}")
        print(f"📋 {spec.name}")
        print(f"{'='*60}")
        print(f"\n📝 Description: {spec.description}")
        print(f"🔤 Language: {spec.language}")
        print(f"✅ Tests: {'Yes' if spec.includes_tests else 'No'}")

        if spec.requirements:
            print(f"\n📌 Requirements:")
            for req in spec.requirements:
                print(f"  • {req}")

        if spec.security_requirements:
            print(f"\n🔒 Security Requirements:")
            for req in spec.security_requirements:
                print(f"  • {req}")

        if spec.constraints:
            print(f"\n⚙️  Constraints:")
            for con in spec.constraints:
                print(f"  • {con}")

        # Show generated versions
        if spec_id in self.generated:
            versions = self.generated[spec_id]
            print(f"\n📦 Generated Versions: {len(versions)}")
            for i, gen in enumerate(versions):
                review_status = "✅" if gen.review_results.get('passed') else "⚠️"
                print(f"  v{gen.version}: {review_status} {gen.generated_at[:10]} ({gen.model})")

    def print_review(self, spec_id: str, version: int = -1):
        """Print code review results."""
        generated = self.get_generated(spec_id, version)
        if not generated:
            print(f"❌ No generated code found for {spec_id}")
            return

        if not generated.review_results:
            print(f"⚠️  No review results available - run review first")
            return

        result = CodeReviewResult(**generated.review_results)

        print(f"\n{'='*60}")
        print(f"🔍 Code Review - {spec_id} v{generated.version}")
        print(f"{'='*60}")

        status = "✅ PASSED" if result.passed else "❌ NEEDS WORK"
        print(f"\nStatus: {status}")
        print(f"Complexity: {result.complexity_score:.1f}/100")

        if result.security_issues:
            print(f"\n🚨 Security Issues ({len(result.security_issues)}):")
            for issue in result.security_issues:
                print(f"  [{issue['severity']}] {issue['message']}")

        if result.quality_issues:
            print(f"\n⚠️  Quality Issues ({len(result.quality_issues)}):")
            for issue in result.quality_issues:
                print(f"  [{issue['severity']}] {issue['message']}")

        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"  • {rec}")


def demo_1_basic_workflow():
    """Demo 1: Basic code generation workflow."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Code Generation Workflow")
    print("="*60)

    toolkit = CodeGenToolkit()

    # Add specification
    print("\n📝 Adding specification...")
    spec = toolkit.add_spec(
        name="Email Validator",
        description="Python function to validate email addresses",
        requirements=[
            "Accept email string as input",
            "Return True if valid, False otherwise",
            "Check for @ symbol and domain",
            "Maximum 254 characters",
            "Handle edge cases (empty, None, special chars)"
        ],
        security_requirements=[
            "No code injection vulnerabilities",
            "Validate input types"
        ],
        constraints=[
            "Use standard library only (no external dependencies)",
            "Include type hints",
            "Include comprehensive docstring"
        ]
    )

    print(f"✅ Specification added: {spec.name}")

    # Show specification
    toolkit.print_spec("email_validator")

    print("\n✅ Demo 1 complete!")


def demo_2_code_generation():
    """Demo 2: Generate code with AI (requires API key)."""
    print("\n" + "="*60)
    print("DEMO 2: AI Code Generation")
    print("="*60)

    toolkit = CodeGenToolkit()

    # Check if AI is available
    if not toolkit.client:
        print("\n⚠️  API key not set - skipping AI generation")
        print("Set ANTHROPIC_API_KEY to use code generation features")
        return

    # Generate code
    print("\n🤖 Generating code...")
    generated = toolkit.generate_code(
        "email_validator",
        iteration_notes="Initial implementation"
    )

    if generated:
        print(f"\n✅ Code generated successfully (v{generated.version})")
        print(f"\nCode preview:")
        print("-" * 60)
        lines = generated.code.split('\n')[:15]
        for line in lines:
            print(line)
        if len(generated.code.split('\n')) > 15:
            print("...")

        if generated.tests:
            print(f"\nTests preview:")
            print("-" * 60)
            lines = generated.tests.split('\n')[:10]
            for line in lines:
                print(line)
            if len(generated.tests.split('\n')) > 10:
                print("...")

    print("\n✅ Demo 2 complete!")


def demo_3_code_review():
    """Demo 3: Review generated code for security and quality."""
    print("\n" + "="*60)
    print("DEMO 3: Code Review")
    print("="*60)

    toolkit = CodeGenToolkit()

    # Add a spec with intentionally problematic code for demo
    print("\n📝 Adding specification with security requirements...")
    toolkit.add_spec(
        name="Database Query",
        description="Function to query user database",
        requirements=[
            "Accept user_id parameter",
            "Query users table",
            "Return user data as dict"
        ],
        security_requirements=[
            "Prevent SQL injection",
            "Use parameterized queries"
        ]
    )

    # Simulate generated code with issues (for demo purposes)
    problematic_code = '''
def query_user(user_id):
    """Query user by ID."""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # VULNERABLE: SQL injection possible!
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()
    return result

def process_file(filename):
    """Process uploaded file."""
    # VULNERABLE: Path traversal possible!
    with open(filename) as f:
        return f.read()

password = "hardcoded_secret_123"  # VULNERABLE: Hardcoded secret!
'''

    # Manually add to generated (normally would come from AI)
    from datetime import datetime
    generated = GeneratedCode(
        spec_id="database_query",
        code=problematic_code,
        version=1,
        model="manual",
        generated_at=datetime.now().isoformat()
    )
    toolkit.generated["database_query"] = [generated]
    toolkit._save_generated()

    # Review the code
    print("\n🔍 Reviewing code for security and quality issues...")
    result = toolkit.review_code("database_query")

    if result:
        toolkit.print_review("database_query")

    print("\n✅ Demo 3 complete!")


def demo_4_iteration_tracking():
    """Demo 4: Track multiple iterations of code generation."""
    print("\n" + "="*60)
    print("DEMO 4: Iteration Tracking")
    print("="*60)

    toolkit = CodeGenToolkit()

    # Show email_validator iterations (if exists)
    spec_id = "email_validator"

    if spec_id in toolkit.generated:
        print(f"\n📦 Showing all versions of '{spec_id}':")

        for generated in toolkit.generated[spec_id]:
            print(f"\n--- Version {generated.version} ---")
            print(f"Generated: {generated.generated_at}")
            print(f"Model: {generated.model}")
            if generated.iteration_notes:
                print(f"Notes: {generated.iteration_notes}")

            # Show review status
            if generated.review_results:
                result = CodeReviewResult(**generated.review_results)
                status = "✅ PASSED" if result.passed else "❌ NEEDS WORK"
                print(f"Review: {status}")
                print(f"  Security issues: {len(result.security_issues)}")
                print(f"  Quality issues: {len(result.quality_issues)}")
                print(f"  Complexity: {result.complexity_score:.1f}/100")
    else:
        print(f"\n⚠️  No generated code found for '{spec_id}'")
        print("Run demo_2 first to generate code")

    print("\n✅ Demo 4 complete!")


def main():
    """Main CLI interface."""
    import sys

    if len(sys.argv) < 2:
        print("Code Generation Workflow Toolkit")
        print("\nUsage:")
        print("  python deliverable_codegen_toolkit.py <command>")
        print("\nCommands:")
        print("  demo1    - Basic workflow (add spec)")
        print("  demo2    - Generate code with AI (requires API key)")
        print("  demo3    - Code review (security & quality)")
        print("  demo4    - Iteration tracking")
        print("  all      - Run all demos")
        return

    command = sys.argv[1]

    if command == "demo1":
        demo_1_basic_workflow()
    elif command == "demo2":
        demo_2_code_generation()
    elif command == "demo3":
        demo_3_code_review()
    elif command == "demo4":
        demo_4_iteration_tracking()
    elif command == "all":
        demo_1_basic_workflow()
        demo_2_code_generation()
        demo_3_code_review()
        demo_4_iteration_tracking()
    else:
        print(f"Unknown command: {command}")
        return


if __name__ == "__main__":
    main()
