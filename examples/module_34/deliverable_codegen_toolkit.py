#!/usr/bin/env python3
"""
Module 34 Deliverable: Code Generation Toolkit

A comprehensive toolkit for understanding and experimenting with code generation
concepts including Fill-in-the-Middle (FIM), pass@k evaluation, code search,
and completion strategies.

This toolkit demonstrates:
- FIM (Fill-in-the-Middle) transformation for code
- Pass@k metric calculation for code generation
- Code completion simulation with different strategies
- Semantic code search and indexing
- Code analysis and metrics

Usage:
    python deliverable_codegen_toolkit.py demo1  # FIM transformation
    python deliverable_codegen_toolkit.py demo2  # Code completion simulation
    python deliverable_codegen_toolkit.py demo3  # Pass@k evaluation
    python deliverable_codegen_toolkit.py demo4  # Code search index
    python deliverable_codegen_toolkit.py demo5  # Generate report

Author: Neural Dojo
Module: 34 - Code Generation Models
"""

import ast
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class FIMExample:
    """A Fill-in-the-Middle training example."""
    original: str
    prefix: str
    middle: str
    suffix: str
    format: str = "PSM"  # PSM or SPM

    def to_training_format(self) -> str:
        """Convert to training format string."""
        if self.format == "PSM":
            return f"<fim_prefix>{self.prefix}<fim_suffix>{self.suffix}<fim_middle>{self.middle}"
        else:  # SPM
            return f"<fim_suffix>{self.suffix}<fim_prefix>{self.prefix}<fim_middle>{self.middle}"


@dataclass
class CodeProblem:
    """A code generation problem (HumanEval-style)."""
    task_id: str
    prompt: str
    canonical_solution: str
    test: str
    entry_point: str
    description: str = ""


@dataclass
class CompletionResult:
    """Result of a code completion attempt."""
    code: str
    passed: bool
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class CodeChunk:
    """A chunk of code for indexing."""
    content: str
    file_path: str
    chunk_type: str  # function, class, module
    name: str
    start_line: int
    end_line: int
    embedding: Optional[List[float]] = None

    def get_signature(self) -> str:
        """Get function/class signature."""
        lines = self.content.split('\n')
        for line in lines:
            if line.strip().startswith(('def ', 'class ')):
                return line.strip()
        return self.name


@dataclass
class SearchResult:
    """Result from code search."""
    chunk: CodeChunk
    score: float
    match_type: str  # semantic, keyword, name


@dataclass
class PassAtKResult:
    """Results from pass@k evaluation."""
    task_id: str
    n_samples: int
    n_correct: int
    pass_at_1: float
    pass_at_10: float
    pass_at_100: float


@dataclass
class CodeGenReport:
    """Comprehensive code generation analysis report."""
    timestamp: str
    fim_examples: List[Dict]
    completion_strategies: Dict[str, Dict]
    pass_at_k_results: List[Dict]
    search_index_stats: Dict
    recommendations: List[str]


# =============================================================================
# Storage Configuration
# =============================================================================

STORAGE_DIR = Path(".codegen_toolkit")
STORAGE_DIR.mkdir(exist_ok=True)

INDEX_FILE = STORAGE_DIR / "code_index.json"
REPORT_FILE = STORAGE_DIR / "codegen_report.md"


# =============================================================================
# FIM (Fill-in-the-Middle) Functions
# =============================================================================

def create_fim_example(
    code: str,
    split_strategy: str = "random",
    format: str = "PSM"
) -> FIMExample:
    """
    Create a FIM training example from code.

    Args:
        code: Original code string
        split_strategy: How to split - 'random', 'line', 'function'
        format: 'PSM' (Prefix-Suffix-Middle) or 'SPM' (Suffix-Prefix-Middle)

    Returns:
        FIMExample with prefix, middle, suffix
    """
    if split_strategy == "random":
        # Random split point
        if len(code) < 10:
            return FIMExample(code, code, "", "", format)

        # Choose random position, avoiding very start/end
        split_start = random.randint(len(code) // 4, 3 * len(code) // 4)

        # Find natural boundary (line break or statement end)
        boundaries = [i for i, c in enumerate(code) if c in '\n;:']
        if boundaries:
            # Find nearest boundary
            split_start = min(boundaries, key=lambda x: abs(x - split_start))

        # Choose middle length
        remaining = len(code) - split_start
        middle_len = random.randint(min(10, remaining), min(100, remaining))

        prefix = code[:split_start]
        middle = code[split_start:split_start + middle_len]
        suffix = code[split_start + middle_len:]

    elif split_strategy == "line":
        # Split at line boundaries
        lines = code.split('\n')
        if len(lines) < 3:
            return FIMExample(code, code, "", "", format)

        split_line = random.randint(1, len(lines) - 2)
        middle_lines = random.randint(1, min(3, len(lines) - split_line))

        prefix = '\n'.join(lines[:split_line]) + '\n'
        middle = '\n'.join(lines[split_line:split_line + middle_lines])
        suffix = '\n' + '\n'.join(lines[split_line + middle_lines:])

    elif split_strategy == "function":
        # Split at function body (find def, split inside)
        match = re.search(r'(def \w+\([^)]*\):\n)(.*?)(\n(?=def |\nclass |$))',
                         code, re.DOTALL)
        if match:
            prefix = code[:match.start(2)]
            body = match.group(2)
            suffix = code[match.end(2):]

            # Split body in middle
            body_lines = body.split('\n')
            if len(body_lines) > 1:
                mid_point = len(body_lines) // 2
                middle = '\n'.join(body_lines[mid_point:mid_point + 1])
                prefix += '\n'.join(body_lines[:mid_point]) + '\n'
                suffix = '\n'.join(body_lines[mid_point + 1:]) + suffix
            else:
                middle = body
        else:
            # Fallback to line strategy
            return create_fim_example(code, "line", format)
    else:
        raise ValueError(f"Unknown split strategy: {split_strategy}")

    return FIMExample(
        original=code,
        prefix=prefix,
        middle=middle,
        suffix=suffix,
        format=format
    )


def demonstrate_fim_formats(code: str) -> Dict[str, str]:
    """
    Show different FIM format transformations.

    Returns dict with format name -> transformed string.
    """
    example = create_fim_example(code, "line", "PSM")

    formats = {}

    # PSM (Prefix-Suffix-Middle) - Most common
    formats["PSM"] = (
        f"<fim_prefix>{example.prefix}"
        f"<fim_suffix>{example.suffix}"
        f"<fim_middle>{example.middle}"
    )

    # SPM (Suffix-Prefix-Middle)
    formats["SPM"] = (
        f"<fim_suffix>{example.suffix}"
        f"<fim_prefix>{example.prefix}"
        f"<fim_middle>{example.middle}"
    )

    # StarCoder format
    formats["StarCoder"] = (
        f"<fim_prefix>{example.prefix}"
        f"<fim_suffix>{example.suffix}"
        f"<fim_middle>{example.middle}<|endoftext|>"
    )

    # CodeLlama format (uses different tokens)
    formats["CodeLlama"] = (
        f"<PRE> {example.prefix} <SUF> {example.suffix} <MID> {example.middle}"
    )

    # DeepSeek format
    formats["DeepSeek"] = (
        f"<｜fim▁begin｜>{example.prefix}"
        f"<｜fim▁hole｜>{example.suffix}"
        f"<｜fim▁end｜>{example.middle}"
    )

    return formats


def analyze_fim_dataset(codes: List[str], fim_rate: float = 0.5) -> Dict:
    """
    Analyze a dataset for FIM training.

    Args:
        codes: List of code strings
        fim_rate: Proportion to convert to FIM format

    Returns:
        Statistics about the FIM transformation.
    """
    stats = {
        "total_examples": len(codes),
        "fim_examples": 0,
        "regular_examples": 0,
        "avg_prefix_len": 0,
        "avg_middle_len": 0,
        "avg_suffix_len": 0,
        "examples": []
    }

    prefix_lens = []
    middle_lens = []
    suffix_lens = []

    for code in codes:
        if random.random() < fim_rate:
            example = create_fim_example(code, "line")
            stats["fim_examples"] += 1
            prefix_lens.append(len(example.prefix))
            middle_lens.append(len(example.middle))
            suffix_lens.append(len(example.suffix))
            stats["examples"].append({
                "type": "fim",
                "prefix_len": len(example.prefix),
                "middle_len": len(example.middle),
                "suffix_len": len(example.suffix)
            })
        else:
            stats["regular_examples"] += 1
            stats["examples"].append({
                "type": "regular",
                "length": len(code)
            })

    if prefix_lens:
        stats["avg_prefix_len"] = sum(prefix_lens) / len(prefix_lens)
        stats["avg_middle_len"] = sum(middle_lens) / len(middle_lens)
        stats["avg_suffix_len"] = sum(suffix_lens) / len(suffix_lens)

    return stats


# =============================================================================
# Pass@k Evaluation
# =============================================================================

def estimate_pass_at_k(n: int, c: int, k: int) -> float:
    """
    Estimate pass@k from n samples with c correct.

    Uses the unbiased estimator from the Codex paper.

    Args:
        n: Total number of samples generated
        c: Number of samples that passed tests
        k: k value for pass@k metric

    Returns:
        Estimated pass@k probability
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def evaluate_solution(code: str, test: str, entry_point: str) -> CompletionResult:
    """
    Evaluate a code solution against test cases.

    Args:
        code: The generated code solution
        test: Test code to run
        entry_point: Name of the function to test

    Returns:
        CompletionResult with pass/fail and any errors
    """
    import time

    start_time = time.time()

    # Create execution environment
    exec_globals = {}

    try:
        # Execute the solution code
        exec(code, exec_globals)

        # Check if entry point exists
        if entry_point not in exec_globals:
            return CompletionResult(
                code=code,
                passed=False,
                error=f"Entry point '{entry_point}' not found",
                execution_time=time.time() - start_time
            )

        # Execute tests
        exec(test, exec_globals)

        return CompletionResult(
            code=code,
            passed=True,
            execution_time=time.time() - start_time
        )

    except AssertionError as e:
        return CompletionResult(
            code=code,
            passed=False,
            error=f"Assertion failed: {e}",
            execution_time=time.time() - start_time
        )
    except Exception as e:
        return CompletionResult(
            code=code,
            passed=False,
            error=f"{type(e).__name__}: {e}",
            execution_time=time.time() - start_time
        )


def run_pass_at_k_evaluation(
    problem: CodeProblem,
    solutions: List[str],
    ks: List[int] = [1, 10, 100]
) -> PassAtKResult:
    """
    Run pass@k evaluation on a problem.

    Args:
        problem: The code problem
        solutions: List of generated solutions
        ks: Values of k to compute

    Returns:
        PassAtKResult with all metrics
    """
    n = len(solutions)
    results = [evaluate_solution(sol, problem.test, problem.entry_point)
               for sol in solutions]
    c = sum(1 for r in results if r.passed)

    pass_at = {}
    for k in ks:
        if k <= n:
            pass_at[k] = estimate_pass_at_k(n, c, k)
        else:
            pass_at[k] = None

    return PassAtKResult(
        task_id=problem.task_id,
        n_samples=n,
        n_correct=c,
        pass_at_1=pass_at.get(1, 0.0),
        pass_at_10=pass_at.get(10, 0.0) if 10 in pass_at else 0.0,
        pass_at_100=pass_at.get(100, 0.0) if 100 in pass_at else 0.0
    )


# =============================================================================
# Code Completion Simulation
# =============================================================================

class CompletionStrategy:
    """Base class for completion strategies."""

    def __init__(self, name: str):
        self.name = name

    def complete(self, prefix: str, suffix: str = "") -> str:
        """Generate completion. Override in subclass."""
        raise NotImplementedError


class GreedyCompletion(CompletionStrategy):
    """Simulated greedy (temperature=0) completion."""

    def __init__(self):
        super().__init__("greedy")
        self.templates = {
            "def ": self._complete_function,
            "class ": self._complete_class,
            "if ": self._complete_if,
            "for ": self._complete_for,
            "return ": self._complete_return,
        }

    def complete(self, prefix: str, suffix: str = "") -> str:
        """Generate deterministic completion."""
        lines = prefix.rstrip().split('\n')
        last_line = lines[-1] if lines else ""

        # Determine indentation
        indent = len(last_line) - len(last_line.lstrip())
        base_indent = " " * indent

        for pattern, handler in self.templates.items():
            if pattern in last_line:
                return handler(prefix, suffix, base_indent)

        # Default: simple statement
        return "pass"

    def _complete_function(self, prefix: str, suffix: str, indent: str) -> str:
        # Extract function name
        match = re.search(r'def (\w+)\(([^)]*)\)', prefix)
        if match:
            name = match.group(1)
            params = match.group(2)
            if "add" in name.lower():
                return f"\n{indent}    return a + b"
            elif "get" in name.lower():
                return f"\n{indent}    return self._{name[4:]}"
            elif "is_" in name.lower() or "has_" in name.lower():
                return f"\n{indent}    return True"
        return f"\n{indent}    pass"

    def _complete_class(self, prefix: str, suffix: str, indent: str) -> str:
        return f"\n{indent}    def __init__(self):\n{indent}        pass"

    def _complete_if(self, prefix: str, suffix: str, indent: str) -> str:
        return f"\n{indent}    pass"

    def _complete_for(self, prefix: str, suffix: str, indent: str) -> str:
        return f"\n{indent}    pass"

    def _complete_return(self, prefix: str, suffix: str, indent: str) -> str:
        return "None"


class SamplingCompletion(CompletionStrategy):
    """Simulated sampling (temperature>0) completion."""

    def __init__(self, temperature: float = 0.7):
        super().__init__(f"sampling_t{temperature}")
        self.temperature = temperature
        self.variations = [
            ("return ", ["None", "True", "False", "0", "[]", "{}"]),
            ("def ", ["pass", "raise NotImplementedError", "..."]),
        ]

    def complete(self, prefix: str, suffix: str = "") -> str:
        """Generate sampled completion with variation."""
        lines = prefix.rstrip().split('\n')
        last_line = lines[-1] if lines else ""
        indent = len(last_line) - len(last_line.lstrip())
        base_indent = " " * indent

        # Add randomness based on temperature
        for pattern, options in self.variations:
            if pattern in last_line:
                # Higher temperature = more uniform distribution
                weights = [1.0 / (i + 1) ** (1 / self.temperature)
                          for i in range(len(options))]
                total = sum(weights)
                weights = [w / total for w in weights]
                return random.choices(options, weights=weights)[0]

        return f"\n{base_indent}    pass"


class BeamSearchCompletion(CompletionStrategy):
    """Simulated beam search completion."""

    def __init__(self, beam_width: int = 5):
        super().__init__(f"beam_w{beam_width}")
        self.beam_width = beam_width

    def complete(self, prefix: str, suffix: str = "") -> str:
        """Generate completion using beam search simulation."""
        # Simulate beam search by generating multiple candidates
        candidates = []
        scores = []

        greedy = GreedyCompletion()
        sampling = SamplingCompletion(0.5)

        # Generate beam_width candidates
        for i in range(self.beam_width):
            if i == 0:
                # First beam is greedy
                cand = greedy.complete(prefix, suffix)
                score = 0.9
            else:
                # Other beams are sampled
                cand = sampling.complete(prefix, suffix)
                score = 0.7 + random.random() * 0.2

            candidates.append(cand)
            scores.append(score)

        # Return highest scoring
        best_idx = np.argmax(scores)
        return candidates[best_idx]


def compare_completion_strategies(
    test_cases: List[Tuple[str, str]]
) -> Dict[str, List[str]]:
    """
    Compare different completion strategies on test cases.

    Args:
        test_cases: List of (prefix, suffix) tuples

    Returns:
        Dict mapping strategy name to list of completions
    """
    strategies = [
        GreedyCompletion(),
        SamplingCompletion(0.3),
        SamplingCompletion(0.7),
        SamplingCompletion(1.0),
        BeamSearchCompletion(3),
        BeamSearchCompletion(5),
    ]

    results = {s.name: [] for s in strategies}

    for prefix, suffix in test_cases:
        for strategy in strategies:
            completion = strategy.complete(prefix, suffix)
            results[strategy.name].append(completion)

    return results


# =============================================================================
# Code Search and Indexing
# =============================================================================

class CodeIndex:
    """Index for semantic code search."""

    def __init__(self):
        self.chunks: List[CodeChunk] = []
        self.name_index: Dict[str, List[int]] = {}
        self.keyword_index: Dict[str, List[int]] = {}

    def add_chunk(self, chunk: CodeChunk):
        """Add a code chunk to the index."""
        idx = len(self.chunks)
        self.chunks.append(chunk)

        # Index by name
        name_lower = chunk.name.lower()
        if name_lower not in self.name_index:
            self.name_index[name_lower] = []
        self.name_index[name_lower].append(idx)

        # Index by keywords
        keywords = self._extract_keywords(chunk.content)
        for kw in keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = []
            self.keyword_index[kw].append(idx)

        # Generate simple embedding (for demo purposes)
        chunk.embedding = self._generate_embedding(chunk.content)

    def _extract_keywords(self, code: str) -> List[str]:
        """Extract keywords from code."""
        # Remove strings and comments
        code = re.sub(r'\"\"\".*?\"\"\"', '', code, flags=re.DOTALL)
        code = re.sub(r"\'\'\'.*?\'\'\'", '', code, flags=re.DOTALL)
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'"[^"]*"', '', code)
        code = re.sub(r"'[^']*'", '', code)

        # Extract identifiers
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)

        # Filter Python keywords
        python_keywords = {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try',
            'except', 'finally', 'with', 'return', 'yield', 'import',
            'from', 'as', 'pass', 'break', 'continue', 'and', 'or', 'not',
            'in', 'is', 'None', 'True', 'False', 'self', 'cls'
        }

        keywords = [w.lower() for w in identifiers if w.lower() not in python_keywords]
        return list(set(keywords))

    def _generate_embedding(self, text: str, dim: int = 64) -> List[float]:
        """
        Generate a simple embedding for demo purposes.
        In production, use a real code embedding model.
        """
        # Create a deterministic embedding based on text content
        hash_val = hashlib.md5(text.encode()).hexdigest()
        random.seed(hash_val)
        embedding = [random.gauss(0, 1) for _ in range(dim)]
        # Normalize
        norm = np.sqrt(sum(x**2 for x in embedding))
        return [x / norm for x in embedding]

    def search(
        self,
        query: str,
        k: int = 5,
        search_type: str = "hybrid"
    ) -> List[SearchResult]:
        """
        Search the index.

        Args:
            query: Search query
            k: Number of results
            search_type: 'semantic', 'keyword', or 'hybrid'

        Returns:
            List of SearchResult objects
        """
        results = []

        if search_type in ["semantic", "hybrid"]:
            # Semantic search
            query_embedding = self._generate_embedding(query)
            semantic_scores = []
            for chunk in self.chunks:
                if chunk.embedding:
                    score = self._cosine_similarity(query_embedding, chunk.embedding)
                    semantic_scores.append((chunk, score, "semantic"))
            results.extend(semantic_scores)

        if search_type in ["keyword", "hybrid"]:
            # Keyword search
            query_keywords = set(self._extract_keywords(query))
            for chunk in self.chunks:
                chunk_keywords = set(self._extract_keywords(chunk.content))
                overlap = len(query_keywords & chunk_keywords)
                if overlap > 0:
                    score = overlap / max(len(query_keywords), 1)
                    results.append((chunk, score * 0.8, "keyword"))

        if search_type in ["name", "hybrid"]:
            # Name search
            query_lower = query.lower()
            for name, indices in self.name_index.items():
                if query_lower in name or name in query_lower:
                    for idx in indices:
                        results.append((self.chunks[idx], 0.9, "name"))

        # Deduplicate and sort
        seen = set()
        unique_results = []
        for chunk, score, match_type in sorted(results, key=lambda x: -x[1]):
            chunk_id = (chunk.file_path, chunk.start_line)
            if chunk_id not in seen:
                seen.add(chunk_id)
                unique_results.append(SearchResult(chunk, score, match_type))

        return unique_results[:k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = np.sqrt(sum(x**2 for x in a))
        norm_b = np.sqrt(sum(x**2 for x in b))
        return dot / (norm_a * norm_b + 1e-8)

    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "total_chunks": len(self.chunks),
            "unique_names": len(self.name_index),
            "unique_keywords": len(self.keyword_index),
            "chunk_types": Counter(c.chunk_type for c in self.chunks),
            "avg_chunk_lines": np.mean([c.end_line - c.start_line for c in self.chunks]) if self.chunks else 0
        }

    def save(self, path: Path):
        """Save index to file."""
        data = {
            "chunks": [asdict(c) for c in self.chunks],
            "name_index": self.name_index,
            "keyword_index": self.keyword_index
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path):
        """Load index from file."""
        with open(path) as f:
            data = json.load(f)

        self.chunks = [CodeChunk(**c) for c in data["chunks"]]
        self.name_index = data["name_index"]
        self.keyword_index = data["keyword_index"]


def parse_python_file(content: str, file_path: str) -> List[CodeChunk]:
    """
    Parse a Python file into code chunks.

    Args:
        content: File content
        file_path: Path to file

    Returns:
        List of CodeChunk objects (functions and classes)
    """
    chunks = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        # Return whole file as single chunk
        return [CodeChunk(
            content=content,
            file_path=file_path,
            chunk_type="module",
            name=Path(file_path).stem,
            start_line=1,
            end_line=content.count('\n') + 1
        )]

    lines = content.split('\n')

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = node.end_lineno or start
            chunk_content = '\n'.join(lines[start-1:end])
            chunks.append(CodeChunk(
                content=chunk_content,
                file_path=file_path,
                chunk_type="function",
                name=node.name,
                start_line=start,
                end_line=end
            ))
        elif isinstance(node, ast.ClassDef):
            start = node.lineno
            end = node.end_lineno or start
            chunk_content = '\n'.join(lines[start-1:end])
            chunks.append(CodeChunk(
                content=chunk_content,
                file_path=file_path,
                chunk_type="class",
                name=node.name,
                start_line=start,
                end_line=end
            ))

    return chunks if chunks else [CodeChunk(
        content=content,
        file_path=file_path,
        chunk_type="module",
        name=Path(file_path).stem,
        start_line=1,
        end_line=content.count('\n') + 1
    )]


# =============================================================================
# Sample Problems (HumanEval-style)
# =============================================================================

SAMPLE_PROBLEMS = [
    CodeProblem(
        task_id="HumanEval/0",
        prompt='''def has_close_elements(numbers: list, threshold: float) -> bool:
    """Check if in given list of numbers, are any two numbers closer to each other
    than given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
''',
        canonical_solution='''    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False
''',
        test='''
assert has_close_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
assert has_close_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
assert has_close_elements([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True
assert has_close_elements([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False
''',
        entry_point="has_close_elements",
        description="Check if any two numbers in a list are closer than threshold"
    ),
    CodeProblem(
        task_id="HumanEval/1",
        prompt='''def separate_paren_groups(paren_string: str) -> list:
    """Input to this function is a string containing multiple groups of nested
    parentheses. Your goal is to separate those groups into separate strings
    and return the list of those.
    >>> separate_paren_groups('( ) (( )) (( )( ))')
    ['()', '(())', '(()())']
    """
''',
        canonical_solution='''    result = []
    current_string = []
    current_depth = 0

    for c in paren_string:
        if c == '(':
            current_depth += 1
            current_string.append(c)
        elif c == ')':
            current_depth -= 1
            current_string.append(c)
            if current_depth == 0:
                result.append(''.join(current_string))
                current_string = []
    return result
''',
        test='''
assert separate_paren_groups('(()()) ((())) () ((())()())') == ['(()())', '((()))', '()', '((())()())']
assert separate_paren_groups('() (()) ((())) (((())))') == ['()', '(())', '((()))', '(((())))']
''',
        entry_point="separate_paren_groups",
        description="Separate groups of nested parentheses"
    ),
    CodeProblem(
        task_id="HumanEval/2",
        prompt='''def truncate_number(number: float) -> float:
    """Given a positive floating point number, it can be decomposed into
    an integer part and a decimal part. Return the decimal part of the number.
    >>> truncate_number(3.5)
    0.5
    """
''',
        canonical_solution='''    return number % 1.0
''',
        test='''
assert truncate_number(3.5) == 0.5
assert abs(truncate_number(1.25) - 0.25) < 1e-6
assert abs(truncate_number(123.456) - 0.456) < 1e-6
''',
        entry_point="truncate_number",
        description="Return decimal part of a float"
    ),
    CodeProblem(
        task_id="HumanEval/3",
        prompt='''def below_zero(operations: list) -> bool:
    """You're given a list of deposit and withdrawal operations on a bank
    account that starts with zero balance. Your task is to detect if at any
    point the balance falls below zero.
    >>> below_zero([1, 2, 3])
    False
    >>> below_zero([1, 2, -4, 5])
    True
    """
''',
        canonical_solution='''    balance = 0
    for op in operations:
        balance += op
        if balance < 0:
            return True
    return False
''',
        test='''
assert below_zero([]) == False
assert below_zero([1, 2, -3, 1, 2, -3]) == False
assert below_zero([1, 2, -4, 5, 6]) == True
assert below_zero([1, -1, 2, -2, 5, -5, 4, -4]) == False
assert below_zero([1, -1, 2, -2, 5, -5, 4, -5]) == True
''',
        entry_point="below_zero",
        description="Detect if balance goes below zero"
    ),
]


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_fim_transformation():
    """Demo 1: Fill-in-the-Middle Transformation."""
    print("=" * 70)
    print("Demo 1: Fill-in-the-Middle (FIM) Transformation")
    print("=" * 70)
    print()

    # Sample code
    sample_code = '''def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0
    total = sum(numbers)
    count = len(numbers)
    return total / count
'''

    print("Original Code:")
    print("-" * 40)
    print(sample_code)
    print()

    # Create FIM example
    print("FIM Transformation (Line Strategy):")
    print("-" * 40)
    example = create_fim_example(sample_code, "line")
    print(f"Prefix:\n{example.prefix}")
    print(f"\n[CURSOR - Model generates here]")
    print(f"\nMiddle (what model should generate):\n{example.middle}")
    print(f"\nSuffix:\n{example.suffix}")
    print()

    # Show different formats
    print("Different Model Formats:")
    print("-" * 40)
    formats = demonstrate_fim_formats(sample_code)
    for name, formatted in list(formats.items())[:3]:  # Show first 3
        print(f"\n{name}:")
        print(f"  {formatted[:100]}..." if len(formatted) > 100 else f"  {formatted}")
    print()

    # Statistics
    print("FIM Dataset Analysis:")
    print("-" * 40)
    codes = [
        '''def add(a, b):
    return a + b''',
        '''def multiply(x, y):
    result = x * y
    return result''',
        '''class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, n):
        self.value += n
        return self''',
        '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)''',
    ]

    stats = analyze_fim_dataset(codes, fim_rate=0.5)
    print(f"Total examples: {stats['total_examples']}")
    print(f"FIM examples: {stats['fim_examples']} ({100*stats['fim_examples']/stats['total_examples']:.0f}%)")
    print(f"Regular examples: {stats['regular_examples']}")
    if stats['fim_examples'] > 0:
        print(f"Avg prefix length: {stats['avg_prefix_len']:.1f} chars")
        print(f"Avg middle length: {stats['avg_middle_len']:.1f} chars")
        print(f"Avg suffix length: {stats['avg_suffix_len']:.1f} chars")

    print()
    print("✅ FIM enables code insertion, not just continuation!")
    print("   Key insight: Models learn prefix + suffix → middle")
    print()


def demo_2_code_completion():
    """Demo 2: Code Completion Simulation."""
    print("=" * 70)
    print("Demo 2: Code Completion Strategies")
    print("=" * 70)
    print()

    test_cases = [
        ("def add(a, b):", ""),
        ("def is_valid(x):", ""),
        ("class UserManager:\n    ", ""),
        ("for item in items:", ""),
        ("if condition:\n    return ", ""),
    ]

    results = compare_completion_strategies(test_cases)

    print("Completion Comparison:")
    print("-" * 70)

    for i, (prefix, suffix) in enumerate(test_cases):
        print(f"\nCase {i+1}: {prefix[:40]}...")
        print("-" * 40)

        for strategy, completions in results.items():
            completion = completions[i].replace('\n', '\\n')[:50]
            print(f"  {strategy:20s}: {completion}")

    print()
    print("Strategy Analysis:")
    print("-" * 40)

    strategies_info = {
        "greedy": {
            "temperature": 0,
            "pros": "Deterministic, consistent",
            "cons": "Can get stuck, no diversity",
            "use_case": "Single best completion"
        },
        "sampling_t0.3": {
            "temperature": 0.3,
            "pros": "Slight variation, still focused",
            "cons": "May introduce minor errors",
            "use_case": "Code completion with variety"
        },
        "sampling_t0.7": {
            "temperature": 0.7,
            "pros": "Good balance of diversity",
            "cons": "More errors possible",
            "use_case": "Generating multiple options"
        },
        "sampling_t1.0": {
            "temperature": 1.0,
            "pros": "Maximum diversity",
            "cons": "High chance of errors",
            "use_case": "Brainstorming, exploration"
        },
        "beam_w5": {
            "beam_width": 5,
            "pros": "Multiple candidates, best selected",
            "cons": "Slower, higher compute",
            "use_case": "When quality matters most"
        },
    }

    print(f"\n{'Strategy':<15} {'Temp/Width':<12} {'Best For':<30}")
    print("-" * 60)
    for name, info in strategies_info.items():
        temp = info.get('temperature', info.get('beam_width', 'N/A'))
        print(f"{name:<15} {str(temp):<12} {info['use_case']:<30}")

    print()
    print("✅ Different strategies for different needs!")
    print("   - Low temperature: Deterministic completion")
    print("   - High temperature: Creative exploration")
    print("   - Beam search: Quality-focused generation")
    print()


def demo_3_pass_at_k():
    """Demo 3: Pass@k Evaluation."""
    print("=" * 70)
    print("Demo 3: Pass@k Evaluation")
    print("=" * 70)
    print()

    print("What is Pass@k?")
    print("-" * 40)
    print("Pass@k measures the probability that at least one of k generated")
    print("solutions passes all test cases.")
    print()
    print("Formula (unbiased estimator):")
    print("  pass@k = 1 - C(n-c, k) / C(n, k)")
    print("  where n = samples generated, c = correct samples")
    print()

    # Evaluate on sample problems
    print("Evaluation on Sample Problems:")
    print("-" * 40)

    all_results = []

    for problem in SAMPLE_PROBLEMS[:3]:  # First 3 problems
        print(f"\n{problem.task_id}: {problem.description}")

        # Generate "simulated" solutions
        solutions = []
        correct_solution = problem.prompt + problem.canonical_solution

        # Some correct, some wrong
        for i in range(20):
            if i < 12:  # 60% correct
                solutions.append(correct_solution)
            else:  # 40% wrong
                wrong = problem.prompt + "    return None  # Wrong\n"
                solutions.append(wrong)

        random.shuffle(solutions)

        result = run_pass_at_k_evaluation(problem, solutions)
        all_results.append(result)

        print(f"  Samples: {result.n_samples}, Correct: {result.n_correct}")
        print(f"  Pass@1:  {result.pass_at_1:.2%}")
        print(f"  Pass@10: {result.pass_at_10:.2%}")

    print()
    print("Pass@k Interpretation:")
    print("-" * 40)
    print()

    # Show how pass@k varies with n and c
    print("How Pass@k Changes with Accuracy:")
    print(f"{'Accuracy':<12} {'Pass@1':<12} {'Pass@10':<12} {'Pass@100':<12}")
    print("-" * 48)

    for accuracy in [0.1, 0.3, 0.5, 0.7, 0.9]:
        n = 200
        c = int(n * accuracy)
        p1 = estimate_pass_at_k(n, c, 1)
        p10 = estimate_pass_at_k(n, c, 10)
        p100 = estimate_pass_at_k(n, c, 100)
        print(f"{accuracy:<12.0%} {p1:<12.2%} {p10:<12.2%} {p100:<12.2%}")

    print()
    print("✅ Pass@k shows: More samples → Higher success!")
    print("   Key insight: Even 10% accuracy → 65% pass@10")
    print()


def demo_4_code_search():
    """Demo 4: Code Search Index."""
    print("=" * 70)
    print("Demo 4: Code Search and Indexing")
    print("=" * 70)
    print()

    # Sample code to index
    sample_files = {
        "utils/math.py": '''
def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def calculate_average(numbers):
    """Calculate average of a list."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)
''',
        "models/user.py": '''
class User:
    """User model."""

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def get_display_name(self):
        """Return display name."""
        return self.name

    def validate_email(self):
        """Validate email format."""
        return '@' in self.email
''',
        "services/auth.py": '''
def authenticate(username, password):
    """Authenticate a user."""
    # Simplified authentication
    if not username or not password:
        return False
    return True

def hash_password(password):
    """Hash a password."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token):
    """Verify an authentication token."""
    return token is not None and len(token) > 10
'''
    }

    # Build index
    print("Building Code Index...")
    print("-" * 40)

    index = CodeIndex()

    for file_path, content in sample_files.items():
        chunks = parse_python_file(content, file_path)
        for chunk in chunks:
            index.add_chunk(chunk)
        print(f"  Indexed {file_path}: {len(chunks)} chunks")

    stats = index.get_stats()
    print(f"\nIndex Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Unique names: {stats['unique_names']}")
    print(f"  Unique keywords: {stats['unique_keywords']}")
    print(f"  Chunk types: {dict(stats['chunk_types'])}")

    # Search demos
    print()
    print("Search Demos:")
    print("-" * 40)

    queries = [
        "calculate average",
        "user authentication",
        "validate email",
        "hash password",
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = index.search(query, k=3)
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.chunk.name} ({r.chunk.file_path})")
            print(f"     Score: {r.score:.3f}, Type: {r.match_type}")

    # Save index
    index.save(INDEX_FILE)
    print(f"\n✅ Index saved to {INDEX_FILE}")

    print()
    print("Search Strategy Comparison:")
    print("-" * 40)

    query = "user validation"
    print(f"Query: '{query}'")

    for search_type in ["semantic", "keyword", "hybrid"]:
        results = index.search(query, k=2, search_type=search_type)
        print(f"\n  {search_type.capitalize()} search:")
        for r in results:
            print(f"    - {r.chunk.name} (score: {r.score:.3f})")

    print()
    print("✅ Code search enables repository-aware completion!")
    print("   Key insight: RAG for code = better context")
    print()


def demo_5_generate_report():
    """Demo 5: Generate Comprehensive Report."""
    print("=" * 70)
    print("Demo 5: Code Generation Analysis Report")
    print("=" * 70)
    print()

    print("Generating comprehensive report...")

    # Gather data from all demos

    # FIM analysis
    sample_codes = [
        "def add(a, b):\n    return a + b",
        "class User:\n    def __init__(self, name):\n        self.name = name",
        "for i in range(10):\n    print(i)",
    ]
    fim_stats = analyze_fim_dataset(sample_codes, fim_rate=0.5)

    # Completion strategies
    test_cases = [
        ("def add(a, b):", ""),
        ("class User:", ""),
    ]
    completion_results = compare_completion_strategies(test_cases)

    # Pass@k
    pass_at_k_data = []
    for accuracy in [0.2, 0.4, 0.6, 0.8]:
        n = 100
        c = int(n * accuracy)
        pass_at_k_data.append({
            "accuracy": accuracy,
            "pass_at_1": estimate_pass_at_k(n, c, 1),
            "pass_at_10": estimate_pass_at_k(n, c, 10),
            "pass_at_100": estimate_pass_at_k(n, c, 100)
        })

    # Code index stats
    if INDEX_FILE.exists():
        index = CodeIndex()
        index.load(INDEX_FILE)
        index_stats = index.get_stats()
    else:
        index_stats = {"total_chunks": 0, "message": "Run demo4 first"}

    # Generate report
    report_content = f"""# Code Generation Toolkit Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overview

This report analyzes code generation concepts demonstrated in the Code Generation Toolkit.

## 1. Fill-in-the-Middle (FIM) Analysis

FIM enables **insertion** completion, not just **continuation**.

### Key Statistics

| Metric | Value |
|--------|-------|
| Total Examples | {fim_stats['total_examples']} |
| FIM Examples | {fim_stats['fim_examples']} |
| Avg Prefix Length | {fim_stats['avg_prefix_len']:.1f} chars |
| Avg Middle Length | {fim_stats['avg_middle_len']:.1f} chars |
| Avg Suffix Length | {fim_stats['avg_suffix_len']:.1f} chars |

### FIM Format Comparison

| Format | Model | Special Tokens |
|--------|-------|----------------|
| PSM | StarCoder | `<fim_prefix>`, `<fim_suffix>`, `<fim_middle>` |
| SPM | Some models | Suffix first, then prefix |
| CodeLlama | Meta | `<PRE>`, `<SUF>`, `<MID>` |
| DeepSeek | DeepSeek | `<｜fim▁begin｜>`, `<｜fim▁hole｜>`, `<｜fim▁end｜>` |

### Recommendation

Use **50% FIM rate** during training for optimal balance between:
- Standard left-to-right completion
- Insertion/infilling capability

---

## 2. Completion Strategies

Different strategies for different use cases:

| Strategy | Temperature | Best For |
|----------|-------------|----------|
| Greedy | 0.0 | Deterministic, single best |
| Low Sampling | 0.3 | Code completion |
| Medium Sampling | 0.7 | Multiple options |
| High Sampling | 1.0 | Exploration |
| Beam Search | N/A | Quality-critical |

### Recommendation

- **IDE completion**: Greedy or low temperature (0.2-0.3)
- **Test generation**: Medium temperature (0.5-0.7)
- **Code review**: Beam search for accuracy

---

## 3. Pass@k Evaluation

Pass@k measures success probability with k samples.

### Pass@k vs Accuracy

| Accuracy | Pass@1 | Pass@10 | Pass@100 |
|----------|--------|---------|----------|
"""

    for data in pass_at_k_data:
        report_content += f"| {data['accuracy']:.0%} | {data['pass_at_1']:.2%} | {data['pass_at_10']:.2%} | {data['pass_at_100']:.2%} |\n"

    report_content += f"""
### Key Insight

Even with 20% accuracy (pass@1), **pass@10 is 89%**!

This is why models use:
- Multiple sample generation
- Self-consistency / majority voting
- Best-of-n selection

---

## 4. Code Search Index

Repository-aware completion requires semantic search.

### Index Statistics

| Metric | Value |
|--------|-------|
| Total Chunks | {index_stats.get('total_chunks', 'N/A')} |
| Unique Names | {index_stats.get('unique_names', 'N/A')} |
| Unique Keywords | {index_stats.get('unique_keywords', 'N/A')} |

### Search Strategy Comparison

| Strategy | Best For | Speed |
|----------|----------|-------|
| Keyword | Exact matches | Fast |
| Semantic | Concept similarity | Medium |
| Hybrid | General search | Medium |

### Recommendation

Use **hybrid search** combining:
1. Name matching (highest priority)
2. Keyword overlap (fast filtering)
3. Semantic similarity (meaning capture)

---

## 5. Model Comparison

Current state-of-the-art (as of 2024):

| Model | Size | HumanEval | Context | Open |
|-------|------|-----------|---------|------|
| GPT-4 | ~1.8T | 67% | 128K | No |
| Claude 3.5 | ~70B? | 64% | 200K | No |
| DeepSeek 33B | 33B | 56% | 16K | Yes |
| CodeLlama 34B | 34B | 49% | 100K | Yes |
| StarCoder2 15B | 15B | 46% | 16K | Yes |

---

## Key Takeaways

1. **FIM is essential** for real-world code completion
2. **Temperature tuning** matters: lower for completion, higher for generation
3. **Pass@k shows** sampling improves success dramatically
4. **Code search** enables repository-aware generation
5. **Open models** are catching up to proprietary ones

---

*Generated by Neural Dojo Code Generation Toolkit*
"""

    # Save report
    with open(REPORT_FILE, 'w') as f:
        f.write(report_content)

    print(f"✅ Report saved to {REPORT_FILE}")
    print()

    # Print summary
    print("Report Summary:")
    print("-" * 40)
    print(f"  FIM examples analyzed: {fim_stats['total_examples']}")
    print(f"  Completion strategies compared: {len(completion_results)}")
    print(f"  Pass@k data points: {len(pass_at_k_data)}")
    print(f"  Code index chunks: {index_stats.get('total_chunks', 'N/A')}")
    print()

    print("Key Recommendations:")
    print("-" * 40)
    print("  1. Use 50% FIM rate for training")
    print("  2. Temperature 0.2-0.3 for code completion")
    print("  3. Generate multiple samples for better pass@k")
    print("  4. Use hybrid search for code retrieval")
    print("  5. Consider open models (DeepSeek, StarCoder2)")
    print()


def show_help():
    """Show help information."""
    print("=" * 70)
    print("Module 34 Deliverable: Code Generation Toolkit")
    print("=" * 70)
    print()
    print("A toolkit for understanding code generation concepts.")
    print()
    print("Usage:")
    print("  python deliverable_codegen_toolkit.py <command>")
    print()
    print("Commands:")
    print("  demo1    Fill-in-the-Middle (FIM) transformation")
    print("  demo2    Code completion strategy comparison")
    print("  demo3    Pass@k evaluation demonstration")
    print("  demo4    Code search and indexing")
    print("  demo5    Generate comprehensive report")
    print("  help     Show this help message")
    print()
    print("Examples:")
    print("  python deliverable_codegen_toolkit.py demo1  # Learn FIM")
    print("  python deliverable_codegen_toolkit.py demo3  # Understand pass@k")
    print("  python deliverable_codegen_toolkit.py demo5  # Full analysis")
    print()
    print("Storage: Results saved to .codegen_toolkit/")
    print()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        'demo1': demo_1_fim_transformation,
        'demo2': demo_2_code_completion,
        'demo3': demo_3_pass_at_k,
        'demo4': demo_4_code_search,
        'demo5': demo_5_generate_report,
        'help': show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python deliverable_codegen_toolkit.py help' for usage.")


if __name__ == "__main__":
    main()
