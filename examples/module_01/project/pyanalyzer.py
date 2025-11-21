#!/usr/bin/env python3
"""
Python File Analyzer - Module 1 Main Project

A CLI tool to analyze Python files and report code metrics.

Built with AI assistance demonstrating the 5 AI coding patterns:
- Specification: Clear requirements → AI generates structure
- Iteration: Refined through multiple iterations
- Example: Test examples → More tests generated
- Explanation: AI explained AST traversal
- Debugging: AI helped fix edge cases

Author: Neural Dojo Student (with AI assistance)
"""

import ast
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class CodeMetrics:
    """
    Metrics extracted from Python code.

    Attributes:
        functions: Number of function definitions
        classes: Number of class definitions
        lines: Lines of code (excluding blanks and comments)
        complexity: Simple complexity score (if/while/for count)
    """
    functions: int = 0
    classes: int = 0
    lines: int = 0
    complexity: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output."""
        return asdict(self)


class PythonAnalyzer(ast.NodeVisitor):
    """
    AST visitor to extract metrics from Python code.

    Uses the visitor pattern to walk the abstract syntax tree
    and count various code elements.
    """

    def __init__(self):
        """Initialize metrics counters."""
        self.metrics = CodeMetrics()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Count function definitions."""
        self.metrics.functions += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Count async function definitions."""
        self.metrics.functions += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Count class definitions."""
        self.metrics.classes += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Count if statements for complexity."""
        self.metrics.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Count while loops for complexity."""
        self.metrics.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Count for loops for complexity."""
        self.metrics.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Count async for loops for complexity."""
        self.metrics.complexity += 1
        self.generic_visit(node)


def count_lines(file_path: Path) -> int:
    """
    Count lines of code excluding blanks and comments.

    Args:
        file_path: Path to Python file

    Returns:
        Number of non-blank, non-comment lines
    """
    lines = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            # Skip blank lines and comment-only lines
            if stripped and not stripped.startswith('#'):
                lines += 1
    return lines


def analyze_file(file_path: Path) -> Optional[CodeMetrics]:
    """
    Analyze a single Python file.

    Args:
        file_path: Path to Python file

    Returns:
        CodeMetrics object with analysis results, or None if error

    Raises:
        FileNotFoundError: If file doesn't exist
        SyntaxError: If file contains invalid Python
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # Read and parse file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python syntax in {file_path}: {e}")

    # Analyze AST
    analyzer = PythonAnalyzer()
    analyzer.visit(tree)

    # Count lines separately (AST doesn't track this)
    analyzer.metrics.lines = count_lines(file_path)

    return analyzer.metrics


def analyze_directory(dir_path: Path) -> CodeMetrics:
    """
    Analyze all Python files in a directory recursively.

    Args:
        dir_path: Path to directory

    Returns:
        Aggregated CodeMetrics for all files

    Raises:
        ValueError: If path is not a directory
    """
    if not dir_path.is_dir():
        raise ValueError(f"Not a directory: {dir_path}")

    aggregate = CodeMetrics()
    python_files = list(dir_path.rglob("*.py"))

    if not python_files:
        print(f"⚠️  No Python files found in {dir_path}", file=sys.stderr)
        return aggregate

    # Analyze each file
    for file_path in python_files:
        try:
            metrics = analyze_file(file_path)
            if metrics:
                aggregate.functions += metrics.functions
                aggregate.classes += metrics.classes
                aggregate.lines += metrics.lines
                aggregate.complexity += metrics.complexity
        except (SyntaxError, FileNotFoundError) as e:
            print(f"⚠️  Skipping {file_path}: {e}", file=sys.stderr)
            continue

    return aggregate


def format_pretty_output(path: Path, metrics: CodeMetrics, is_directory: bool = False) -> str:
    """
    Format metrics as pretty terminal output.

    Args:
        path: Path that was analyzed
        metrics: Metrics to display
        is_directory: True if analyzing directory

    Returns:
        Formatted string for terminal display
    """
    output = []
    output.append("🐍 Python File Analyzer")
    output.append("━" * 60)
    output.append("")

    if is_directory:
        output.append(f"📁 Directory: {path}")
    else:
        output.append(f"📁 File: {path}")

    output.append("")
    output.append("📊 Metrics:")
    output.append(f"  Functions:  {metrics.functions}")
    output.append(f"  Classes:    {metrics.classes}")
    output.append(f"  Lines:      {metrics.lines:,} (excluding blanks/comments)")
    output.append(f"  Complexity: {metrics.complexity}")
    output.append("")
    output.append("✨ Analysis complete!")

    return "\n".join(output)


def format_json_output(path: Path, metrics: CodeMetrics, is_directory: bool = False) -> str:
    """
    Format metrics as JSON output.

    Args:
        path: Path that was analyzed
        metrics: Metrics to display
        is_directory: True if analyzing directory

    Returns:
        JSON string
    """
    data = {
        "type": "directory" if is_directory else "file",
        "path": str(path),
        "metrics": metrics.to_dict()
    }
    return json.dumps(data, indent=2)


def main():
    """
    Main CLI entry point.

    Parses arguments and orchestrates analysis.
    """
    parser = argparse.ArgumentParser(
        description="Analyze Python files for code metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.py              Analyze single file
  %(prog)s src/                 Analyze directory recursively
  %(prog)s file.py --json       Output as JSON

Metrics:
  Functions:  Count of function/async function definitions
  Classes:    Count of class definitions
  Lines:      Non-blank, non-comment lines
  Complexity: Count of if/while/for statements (simple heuristic)
        """
    )

    parser.add_argument(
        'path',
        type=Path,
        help='Path to Python file or directory'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Validate path exists
    if not args.path.exists():
        print(f"❌ Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Analyze based on type
    try:
        if args.path.is_file():
            metrics = analyze_file(args.path)
            if args.json:
                output = format_json_output(args.path, metrics, is_directory=False)
            else:
                output = format_pretty_output(args.path, metrics, is_directory=False)

        elif args.path.is_dir():
            metrics = analyze_directory(args.path)
            if args.json:
                output = format_json_output(args.path, metrics, is_directory=True)
            else:
                output = format_pretty_output(args.path, metrics, is_directory=True)
        else:
            print(f"❌ Error: Not a file or directory: {args.path}", file=sys.stderr)
            sys.exit(1)

        print(output)

    except (SyntaxError, FileNotFoundError, ValueError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
