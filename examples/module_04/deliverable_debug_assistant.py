#!/usr/bin/env python3
"""
AI Debugging Assistant - Module 04 Deliverable
===============================================

Production-ready CLI tool for AI-assisted debugging and optimization.

Features:
---------
1. Error Analysis - Parse stack traces and suggest fixes
2. Performance Profiling - Profile code and get optimization suggestions
3. Code Quality Scanner - Detect common bug patterns
4. Debugging Prompt Generator - Create effective AI debugging prompts
5. Session Logger - Document debugging sessions automatically
6. Interactive Demos - Demonstrate debugging workflow

Author: Neural Dojo
Module: 04 - AI-Assisted Debugging & Optimization
"""

import sys
import os
import re
import traceback
import cProfile
import pstats
import io
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from anthropic import Anthropic


@dataclass
class ErrorAnalysis:
    """Structured error analysis result."""
    error_type: str
    error_message: str
    file_path: Optional[str]
    line_number: Optional[int]
    stack_trace: List[str]
    code_context: Optional[str]
    ai_analysis: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: Optional[str] = None  # high, medium, low


@dataclass
class PerformanceAnalysis:
    """Performance profiling result."""
    total_time: float
    function_calls: int
    hotspots: List[Dict[str, Any]]
    ai_suggestions: Optional[str] = None
    optimization_opportunities: Optional[List[str]] = None


@dataclass
class DebuggingSession:
    """Debugging session record."""
    session_id: str
    timestamp: str
    problem_description: str
    error_analysis: Optional[ErrorAnalysis] = None
    performance_analysis: Optional[PerformanceAnalysis] = None
    solution: Optional[str] = None
    time_spent: Optional[float] = None
    ai_effectiveness: Optional[int] = None  # 1-10


class AIDebugAssistant:
    """
    AI-powered debugging assistant for Python code.

    Combines traditional debugging tools (profiling, static analysis)
    with AI-powered suggestions and explanations.
    """

    def __init__(self, api_key: Optional[str] = None, log_dir: Path = Path('.debug_logs')):
        """
        Initialize the debugging assistant.

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            log_dir: Directory for debugging session logs
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            print("⚠️  Warning: No API key found. AI features will be disabled.")
            print("   Set ANTHROPIC_API_KEY environment variable to enable AI analysis.")
            self.client = None
        else:
            self.client = Anthropic(api_key=self.api_key)

        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.sessions: List[DebuggingSession] = []

    def analyze_error(self, error: Exception, code: Optional[str] = None) -> ErrorAnalysis:
        """
        Analyze an error and provide AI-powered suggestions.

        Args:
            error: The exception to analyze
            code: Optional source code context

        Returns:
            ErrorAnalysis with diagnosis and suggestions
        """
        # Extract error information
        tb = traceback.extract_tb(error.__traceback__)
        stack_trace = traceback.format_exception(type(error), error, error.__traceback__)

        error_type = type(error).__name__
        error_message = str(error)

        # Get file and line info from traceback
        file_path = None
        line_number = None
        code_context = None

        if tb:
            last_frame = tb[-1]
            file_path = last_frame.filename
            line_number = last_frame.lineno

            # Try to read code context
            if code is None and file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        start = max(0, line_number - 3)
                        end = min(len(lines), line_number + 2)
                        code_context = ''.join(lines[start:end])
                except:
                    pass
            elif code:
                code_context = code

        analysis = ErrorAnalysis(
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            stack_trace=stack_trace,
            code_context=code_context
        )

        # Get AI analysis if available
        if self.client and code_context:
            analysis.ai_analysis, analysis.suggested_fix, analysis.confidence = self._get_ai_fix(analysis)

        return analysis

    def _get_ai_fix(self, analysis: ErrorAnalysis) -> Tuple[str, str, str]:
        """
        Get AI-powered fix suggestions.

        Returns:
            (analysis, suggested_fix, confidence)
        """
        prompt = f"""Analyze this Python error and provide a fix:

Error Type: {analysis.error_type}
Error Message: {analysis.error_message}
Line: {analysis.line_number}

Code Context:
```python
{analysis.code_context}
```

Stack Trace:
{''.join(analysis.stack_trace[-5:])}

Please provide:
1. Root cause analysis (2-3 sentences)
2. Suggested fix (code)
3. Confidence level (high/medium/low)

Format your response as:
ANALYSIS: [your analysis]
FIX: ```python
[fixed code]
```
CONFIDENCE: [high/medium/low]
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Parse response
            analysis_match = re.search(r'ANALYSIS:\s*(.+?)(?=FIX:|CONFIDENCE:|$)', content, re.DOTALL)
            fix_match = re.search(r'FIX:\s*```python\s*(.+?)\s*```', content, re.DOTALL)
            confidence_match = re.search(r'CONFIDENCE:\s*(\w+)', content, re.IGNORECASE)

            ai_analysis = analysis_match.group(1).strip() if analysis_match else "Analysis not available"
            suggested_fix = fix_match.group(1).strip() if fix_match else content
            confidence = confidence_match.group(1).lower() if confidence_match else "medium"

            return ai_analysis, suggested_fix, confidence

        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}")
            return "AI analysis unavailable", "No fix suggested", "low"

    def profile_code(self, func, *args, **kwargs) -> PerformanceAnalysis:
        """
        Profile a function and get AI optimization suggestions.

        Args:
            func: Function to profile
            *args, **kwargs: Arguments to pass to function

        Returns:
            PerformanceAnalysis with profiling results and AI suggestions
        """
        # Profile the function
        profiler = cProfile.Profile()
        profiler.enable()

        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()

        profiler.disable()

        # Get stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

        stats_output = s.getvalue()

        # Parse hotspots
        hotspots = self._parse_profiler_output(stats_output)

        total_time = (end_time - start_time).total_seconds()
        function_calls = stats.total_calls

        analysis = PerformanceAnalysis(
            total_time=total_time,
            function_calls=function_calls,
            hotspots=hotspots
        )

        # Get AI suggestions if available
        if self.client:
            analysis.ai_suggestions, analysis.optimization_opportunities = self._get_optimization_suggestions(
                analysis, func
            )

        return analysis

    def _parse_profiler_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse cProfile output into structured hotspots."""
        hotspots = []
        lines = output.split('\n')

        # Skip header lines
        for line in lines:
            if 'ncalls' in line or 'tottime' in line or not line.strip():
                continue

            # Try to parse profiler line
            parts = line.split()
            if len(parts) >= 6:
                try:
                    hotspots.append({
                        'ncalls': parts[0],
                        'tottime': float(parts[1]),
                        'percall': float(parts[2]),
                        'cumtime': float(parts[3]),
                        'function': ' '.join(parts[5:])
                    })
                except:
                    continue

        return hotspots[:5]  # Top 5 hotspots

    def _get_optimization_suggestions(self, analysis: PerformanceAnalysis, func) -> Tuple[str, List[str]]:
        """Get AI-powered optimization suggestions."""
        # Get function source if possible
        try:
            import inspect
            source = inspect.getsource(func)
        except:
            source = "Source code not available"

        hotspots_text = "\n".join([
            f"  - {h['function']}: {h['tottime']:.3f}s ({h['ncalls']} calls)"
            for h in analysis.hotspots
        ])

        prompt = f"""Analyze this performance profile and suggest optimizations:

Function: {func.__name__}
Total Time: {analysis.total_time:.3f}s
Total Calls: {analysis.function_calls}

Top Hotspots:
{hotspots_text}

Source Code:
```python
{source}
```

Please provide:
1. Performance analysis (identify bottlenecks)
2. 3-5 specific optimization suggestions
3. Expected complexity improvements

Format:
ANALYSIS: [your analysis]
SUGGESTIONS:
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion 3]
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Parse response
            analysis_match = re.search(r'ANALYSIS:\s*(.+?)(?=SUGGESTIONS:|$)', content, re.DOTALL)
            suggestions_match = re.search(r'SUGGESTIONS:\s*(.+)', content, re.DOTALL)

            ai_analysis = analysis_match.group(1).strip() if analysis_match else "Analysis not available"

            suggestions = []
            if suggestions_match:
                sugg_text = suggestions_match.group(1).strip()
                suggestions = [s.strip('- ').strip() for s in sugg_text.split('\n') if s.strip().startswith('-')]

            return ai_analysis, suggestions

        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}")
            return "AI analysis unavailable", []

    def scan_code_quality(self, code: str) -> List[Dict[str, str]]:
        """
        Scan code for common bug patterns.

        Args:
            code: Python source code to scan

        Returns:
            List of potential issues found
        """
        issues = []

        try:
            tree = ast.parse(code)

            # Check for common patterns
            for node in ast.walk(tree):
                # Check for bare except
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            'type': 'bare_except',
                            'line': node.lineno,
                            'message': 'Bare except clause - catches all exceptions including system exits',
                            'severity': 'medium'
                        })

                # Check for mutable default arguments
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append({
                                'type': 'mutable_default',
                                'line': node.lineno,
                                'message': f'Mutable default argument in function {node.name}',
                                'severity': 'high'
                            })

                # Check for == None instead of is None
                if isinstance(node, ast.Compare):
                    for op, comp in zip(node.ops, node.comparators):
                        if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) and comp.value is None:
                            issues.append({
                                'type': 'none_comparison',
                                'line': node.lineno,
                                'message': 'Use "is None" instead of "== None"',
                                'severity': 'low'
                            })

        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'line': e.lineno,
                'message': f'Syntax error: {e.msg}',
                'severity': 'critical'
            })

        return issues

    def generate_debug_prompt(self, problem: str, context: Dict[str, Any]) -> str:
        """
        Generate an effective debugging prompt for AI.

        Args:
            problem: Description of the problem
            context: Additional context (error, code, environment, etc.)

        Returns:
            Well-structured debugging prompt
        """
        prompt_parts = [
            f"Debug this Python error systematically:\n",
            f"Problem: {problem}\n"
        ]

        if 'error' in context:
            prompt_parts.append(f"\nError Message:\n{context['error']}\n")

        if 'code' in context:
            prompt_parts.append(f"\nCode:\n```python\n{context['code']}\n```\n")

        if 'expected' in context:
            prompt_parts.append(f"\nExpected Behavior: {context['expected']}\n")

        if 'actual' in context:
            prompt_parts.append(f"Actual Behavior: {context['actual']}\n")

        if 'environment' in context:
            prompt_parts.append(f"\nEnvironment:\n{context['environment']}\n")

        if 'tried' in context:
            prompt_parts.append(f"\nAlready Tried:\n{context['tried']}\n")

        prompt_parts.append("""
Please:
1. Identify the root cause
2. Explain WHY this error occurs
3. Provide 2-3 potential solutions with trade-offs
4. Recommend the best solution with rationale
5. Show the fixed code
6. Suggest tests to prevent recurrence
""")

        return ''.join(prompt_parts)

    def log_session(self, session: DebuggingSession):
        """
        Log a debugging session to disk.

        Args:
            session: DebuggingSession to log
        """
        self.sessions.append(session)

        # Save to JSON
        log_file = self.log_dir / f"session_{session.session_id}.json"
        with open(log_file, 'w') as f:
            json.dump(asdict(session), f, indent=2, default=str)

        print(f"✅ Session logged to {log_file}")

    def print_error_analysis(self, analysis: ErrorAnalysis):
        """Pretty print error analysis."""
        print("\n" + "="*80)
        print("🐛 ERROR ANALYSIS")
        print("="*80)
        print(f"\nError Type: {analysis.error_type}")
        print(f"Message: {analysis.error_message}")

        if analysis.file_path:
            print(f"Location: {analysis.file_path}:{analysis.line_number}")

        if analysis.code_context:
            print(f"\nCode Context:")
            print("-" * 80)
            print(analysis.code_context)
            print("-" * 80)

        if analysis.ai_analysis:
            print(f"\n🤖 AI Analysis:")
            print(analysis.ai_analysis)
            print(f"\nConfidence: {analysis.confidence.upper()}")

        if analysis.suggested_fix:
            print(f"\n💡 Suggested Fix:")
            print("-" * 80)
            print(analysis.suggested_fix)
            print("-" * 80)

        print()

    def print_performance_analysis(self, analysis: PerformanceAnalysis):
        """Pretty print performance analysis."""
        print("\n" + "="*80)
        print("⚡ PERFORMANCE ANALYSIS")
        print("="*80)
        print(f"\nTotal Time: {analysis.total_time:.3f}s")
        print(f"Function Calls: {analysis.function_calls:,}")

        print(f"\nTop Hotspots:")
        for i, hotspot in enumerate(analysis.hotspots, 1):
            print(f"  {i}. {hotspot['function']}")
            print(f"     Time: {hotspot['tottime']:.3f}s ({hotspot['ncalls']} calls)")

        if analysis.ai_suggestions:
            print(f"\n🤖 AI Optimization Suggestions:")
            print(analysis.ai_suggestions)

        if analysis.optimization_opportunities:
            print(f"\n💡 Optimization Opportunities:")
            for i, opp in enumerate(analysis.optimization_opportunities, 1):
                print(f"  {i}. {opp}")

        print()


# ============================================================================
# Demo Functions
# ============================================================================

def demo_error_analysis():
    """Demonstrate error analysis with buggy code."""
    print("\n" + "="*80)
    print("DEMO 1: Error Analysis")
    print("="*80)
    print("\nAnalyzing a buggy function with AI assistance...\n")

    assistant = AIDebugAssistant()

    # Buggy code
    buggy_code = """
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

# This will crash with ZeroDivisionError
result = calculate_average([])
"""

    print("Buggy Code:")
    print("-" * 80)
    print(buggy_code)
    print("-" * 80)

    # Execute and catch error
    try:
        exec(buggy_code)
    except Exception as e:
        analysis = assistant.analyze_error(e, buggy_code)
        assistant.print_error_analysis(analysis)

        # Log session
        session = DebuggingSession(
            session_id=f"demo1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            problem_description="ZeroDivisionError in calculate_average",
            error_analysis=analysis,
            solution="Add empty list check",
            ai_effectiveness=9
        )
        assistant.log_session(session)


def demo_performance_profiling():
    """Demonstrate performance profiling with slow code."""
    print("\n" + "="*80)
    print("DEMO 2: Performance Profiling")
    print("="*80)
    print("\nProfiling slow code and getting optimization suggestions...\n")

    assistant = AIDebugAssistant()

    # Slow function (O(n²))
    def find_duplicates_slow(items):
        """Slow O(n²) implementation."""
        duplicates = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i] == items[j] and items[i] not in duplicates:
                    duplicates.append(items[i])
        return duplicates

    print("Function to profile:")
    print("-" * 80)
    print("""
def find_duplicates_slow(items):
    '''Slow O(n²) implementation.'''
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
""")
    print("-" * 80)

    # Profile it
    test_data = list(range(100)) * 2  # 200 items with duplicates
    print(f"\nProfiling with {len(test_data)} items...")

    analysis = assistant.profile_code(find_duplicates_slow, test_data)
    assistant.print_performance_analysis(analysis)

    # Log session
    session = DebuggingSession(
        session_id=f"demo2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        timestamp=datetime.now().isoformat(),
        problem_description="Slow O(n²) duplicate finding",
        performance_analysis=analysis,
        solution="Use set-based approach for O(n) complexity",
        ai_effectiveness=8
    )
    assistant.log_session(session)


def demo_code_quality_scan():
    """Demonstrate code quality scanning."""
    print("\n" + "="*80)
    print("DEMO 3: Code Quality Scanning")
    print("="*80)
    print("\nScanning code for common bug patterns...\n")

    assistant = AIDebugAssistant()

    # Code with issues
    problematic_code = """
def process_items(items, cache={}):  # Mutable default!
    try:
        for item in items:
            if item == None:  # Should use 'is None'
                continue
            cache[item] = process(item)
    except:  # Bare except!
        pass
    return cache
"""

    print("Code to scan:")
    print("-" * 80)
    print(problematic_code)
    print("-" * 80)

    issues = assistant.scan_code_quality(problematic_code)

    print(f"\n🔍 Found {len(issues)} potential issues:\n")
    for i, issue in enumerate(issues, 1):
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        emoji = severity_emoji.get(issue['severity'], '⚪')
        print(f"{i}. {emoji} Line {issue['line']}: {issue['message']}")
        print(f"   Type: {issue['type']} | Severity: {issue['severity']}")
        print()


def demo_prompt_generation():
    """Demonstrate debugging prompt generation."""
    print("\n" + "="*80)
    print("DEMO 4: Debugging Prompt Generation")
    print("="*80)
    print("\nGenerating structured debugging prompts for AI...\n")

    assistant = AIDebugAssistant()

    context = {
        'error': 'KeyError: "user_id" at line 42 in process_request()',
        'code': """
def process_request(data):
    user_id = data['user_id']  # Line 42
    return get_user(user_id)
""",
        'expected': 'Extract user_id from request data',
        'actual': 'Crashes when user_id key is missing',
        'environment': 'Python 3.11, FastAPI 0.109, Docker',
        'tried': 'Verified client sends user_id, checked middleware'
    }

    prompt = assistant.generate_debug_prompt(
        "KeyError when processing request",
        context
    )

    print("Generated Debugging Prompt:")
    print("="*80)
    print(prompt)
    print("="*80)
    print("\n💡 This prompt includes:")
    print("  ✓ Clear problem description")
    print("  ✓ Full error message")
    print("  ✓ Code context")
    print("  ✓ Expected vs actual behavior")
    print("  ✓ Environment details")
    print("  ✓ What was already tried")
    print("  ✓ Specific questions for AI")
    print("\n📋 Copy this prompt to Claude/ChatGPT for analysis!")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                      AI Debugging Assistant v1.0                          ║
║                   Module 04 - Neural Dojo Deliverable                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

Production-ready CLI tool for AI-assisted debugging and optimization.

USAGE:
    python deliverable_debug_assistant.py <command>

COMMANDS:
    demo1    - Error Analysis (parse stack traces, suggest fixes)
    demo2    - Performance Profiling (profile code, optimize)
    demo3    - Code Quality Scan (detect common bug patterns)
    demo4    - Prompt Generation (create effective AI prompts)
    all      - Run all demonstrations

EXAMPLES:
    python deliverable_debug_assistant.py demo1
    python deliverable_debug_assistant.py all

REQUIREMENTS:
    - Python 3.10+
    - anthropic library (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable (optional, for AI features)

NOTE:
    AI features require ANTHROPIC_API_KEY. Without it, basic analysis still works.

For more information, see DELIVERABLE_README.md
""")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'demo1':
        demo_error_analysis()
    elif command == 'demo2':
        demo_performance_profiling()
    elif command == 'demo3':
        demo_code_quality_scan()
    elif command == 'demo4':
        demo_prompt_generation()
    elif command == 'all':
        demo_error_analysis()
        input("\nPress Enter to continue to demo 2...")
        demo_performance_profiling()
        input("\nPress Enter to continue to demo 3...")
        demo_code_quality_scan()
        input("\nPress Enter to continue to demo 4...")
        demo_prompt_generation()

        print("\n" + "="*80)
        print("✅ All demonstrations complete!")
        print("="*80)
        print("\n📁 Check .debug_logs/ directory for session logs")
        print("💡 Use this assistant in your own projects for AI-powered debugging!")
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run without arguments to see usage.")
        sys.exit(1)


if __name__ == '__main__':
    main()
