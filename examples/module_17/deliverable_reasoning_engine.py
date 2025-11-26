#!/usr/bin/env python3
"""
Module 17 Deliverable: Reasoning Engine

A comprehensive reasoning system that combines multiple techniques:
- Chain-of-Thought prompting (Zero-shot, Few-shot, Structured)
- ReAct pattern for tool-augmented reasoning
- Self-consistency for reliable answers
- Program-Aided Language Models (PAL)
- Automatic technique selection based on problem type

Features:
- Problem type detection (math, logic, factual, multi-step)
- Adaptive reasoning strategy selection
- Confidence scoring
- Reasoning trace logging
- Benchmark suite for evaluation

Usage:
    python deliverable_reasoning_engine.py demo1  # Reasoning techniques
    python deliverable_reasoning_engine.py demo2  # ReAct with tools
    python deliverable_reasoning_engine.py demo3  # Benchmark evaluation
    python deliverable_reasoning_engine.py solve "Your question here"

Requirements:
    pip install langchain-core langchain-google-genai pydantic

Author: Neural Dojo - Module 17
"""

import os
import sys
import json
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Callable, Tuple
from datetime import datetime
from pathlib import Path
from collections import Counter
from enum import Enum


# ============================================================================
# CONFIGURATION
# ============================================================================

STORAGE_DIR = Path(".reasoning_engine")
TRACES_FILE = STORAGE_DIR / "reasoning_traces.json"
BENCHMARKS_FILE = STORAGE_DIR / "benchmarks.json"


class ProblemType(str, Enum):
    """Types of reasoning problems."""
    ARITHMETIC = "arithmetic"
    MULTI_STEP = "multi_step"
    LOGIC = "logic"
    FACTUAL = "factual"
    TRICK = "trick"
    UNKNOWN = "unknown"


class ReasoningStrategy(str, Enum):
    """Reasoning strategies."""
    ZERO_SHOT_COT = "zero_shot_cot"
    FEW_SHOT_COT = "few_shot_cot"
    SELF_CONSISTENCY = "self_consistency"
    REACT = "react"
    PAL = "pal"
    LEAST_TO_MOST = "least_to_most"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ReasoningTrace:
    """A single reasoning trace."""
    question: str
    strategy: str
    reasoning: str
    answer: str
    confidence: float
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReasoningTrace":
        return cls(**data)


@dataclass
class BenchmarkResult:
    """Result from a benchmark run."""
    strategy: str
    total_problems: int
    correct: int
    accuracy: float
    avg_latency_ms: float
    avg_confidence: float
    problems: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# PERSISTENCE
# ============================================================================

def ensure_storage():
    """Ensure storage directory exists."""
    STORAGE_DIR.mkdir(exist_ok=True)


def save_trace(trace: ReasoningTrace):
    """Save a reasoning trace."""
    ensure_storage()
    traces = load_traces()
    traces.append(trace.to_dict())
    # Keep last 100 traces
    traces = traces[-100:]
    with open(TRACES_FILE, 'w') as f:
        json.dump(traces, f, indent=2)


def load_traces() -> List[Dict[str, Any]]:
    """Load reasoning traces."""
    if not TRACES_FILE.exists():
        return []
    with open(TRACES_FILE, 'r') as f:
        return json.load(f)


# ============================================================================
# LLM INTERFACE
# ============================================================================

def get_llm(temperature: float = 0.0):
    """Get LLM with specified temperature."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=temperature,
        )
    else:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=temperature,
        )


# ============================================================================
# PROBLEM CLASSIFICATION
# ============================================================================

def classify_problem(question: str) -> ProblemType:
    """Classify the type of reasoning problem."""
    question_lower = question.lower()

    # Arithmetic indicators
    arithmetic_words = ['calculate', 'compute', 'sum', 'total', 'multiply', 'divide', 'add', 'subtract']
    if any(word in question_lower for word in arithmetic_words):
        return ProblemType.ARITHMETIC

    # Check for numbers
    numbers = re.findall(r'\d+', question)

    # Multi-step indicators
    multi_step_words = ['then', 'after', 'first', 'next', 'finally', 'total', 'altogether']
    if len(numbers) >= 2 and any(word in question_lower for word in multi_step_words):
        return ProblemType.MULTI_STEP

    # Logic indicators
    logic_words = ['if', 'all', 'some', 'none', 'must', 'can we conclude', 'therefore', 'implies']
    if any(word in question_lower for word in logic_words):
        return ProblemType.LOGIC

    # Trick question indicators
    trick_patterns = ['all but', 'except', 'besides', 'how many', 'what\'s wrong']
    if any(pattern in question_lower for pattern in trick_patterns):
        return ProblemType.TRICK

    # Factual question indicators
    factual_words = ['what is the', 'who is', 'where is', 'when did', 'capital of', 'population']
    if any(word in question_lower for word in factual_words):
        return ProblemType.FACTUAL

    # Default to multi-step if has numbers
    if numbers:
        return ProblemType.MULTI_STEP

    return ProblemType.UNKNOWN


def select_strategy(problem_type: ProblemType) -> ReasoningStrategy:
    """Select the best reasoning strategy for a problem type."""
    strategy_map = {
        ProblemType.ARITHMETIC: ReasoningStrategy.PAL,
        ProblemType.MULTI_STEP: ReasoningStrategy.SELF_CONSISTENCY,
        ProblemType.LOGIC: ReasoningStrategy.ZERO_SHOT_COT,
        ProblemType.FACTUAL: ReasoningStrategy.REACT,
        ProblemType.TRICK: ReasoningStrategy.ZERO_SHOT_COT,
        ProblemType.UNKNOWN: ReasoningStrategy.ZERO_SHOT_COT,
    }
    return strategy_map.get(problem_type, ReasoningStrategy.ZERO_SHOT_COT)


# ============================================================================
# REASONING STRATEGIES
# ============================================================================

def extract_answer(text: str) -> Optional[str]:
    """Extract the final answer from a response."""
    patterns = [
        r'(?:final\s+)?answer[:\s]+(.+?)(?:\n|$)',
        r'therefore[,:\s]+(.+?)(?:\n|$)',
        r'=\s*(-?\d+\.?\d*)\s*(?:\n|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower(), re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip('.,!?')

    numbers = re.findall(r'-?\d+\.?\d*', text)
    return numbers[-1] if numbers else None


class ReasoningEngine:
    """Main reasoning engine."""

    def __init__(self):
        self.llm = None
        self.traces: List[ReasoningTrace] = []
        self.tools = self._init_tools()

    def _init_tools(self) -> Dict[str, Callable]:
        """Initialize available tools for ReAct."""
        return {
            "calculate": self._tool_calculate,
            "search": self._tool_search,
        }

    def _tool_calculate(self, expression: str) -> str:
        """Calculate a math expression."""
        try:
            allowed = set("0123456789+-*/().% ")
            if all(c in allowed for c in expression):
                return str(eval(expression))
            return "Error: Invalid expression"
        except Exception as e:
            return f"Error: {e}"

    def _tool_search(self, query: str) -> str:
        """Simulated knowledge search."""
        knowledge = {
            "population france": "67.75 million",
            "capital france": "Paris",
            "eiffel tower": "330 meters tall",
            "speed of light": "299,792,458 m/s",
        }
        query_lower = query.lower()
        for key, value in knowledge.items():
            if key in query_lower:
                return value
        return f"No information found for: {query}"

    def solve(
        self,
        question: str,
        strategy: Optional[ReasoningStrategy] = None
    ) -> ReasoningTrace:
        """Solve a problem using the specified or auto-selected strategy."""
        start_time = time.time()

        # Auto-select strategy if not specified
        if strategy is None:
            problem_type = classify_problem(question)
            strategy = select_strategy(problem_type)

        # Get LLM
        self.llm = get_llm(temperature=0)
        if not self.llm:
            return ReasoningTrace(
                question=question,
                strategy=strategy.value,
                reasoning="No API key available",
                answer="[Requires API key]",
                confidence=0.0,
                latency_ms=0,
                metadata={"error": "no_api_key"}
            )

        # Execute strategy
        if strategy == ReasoningStrategy.ZERO_SHOT_COT:
            reasoning, answer, confidence = self._zero_shot_cot(question)
        elif strategy == ReasoningStrategy.SELF_CONSISTENCY:
            reasoning, answer, confidence = self._self_consistency(question)
        elif strategy == ReasoningStrategy.PAL:
            reasoning, answer, confidence = self._pal(question)
        elif strategy == ReasoningStrategy.REACT:
            reasoning, answer, confidence = self._react(question)
        elif strategy == ReasoningStrategy.LEAST_TO_MOST:
            reasoning, answer, confidence = self._least_to_most(question)
        else:
            reasoning, answer, confidence = self._zero_shot_cot(question)

        latency_ms = (time.time() - start_time) * 1000

        trace = ReasoningTrace(
            question=question,
            strategy=strategy.value,
            reasoning=reasoning,
            answer=answer,
            confidence=confidence,
            latency_ms=latency_ms,
            metadata={"problem_type": classify_problem(question).value}
        )

        self.traces.append(trace)
        save_trace(trace)

        return trace

    def _zero_shot_cot(self, question: str) -> Tuple[str, str, float]:
        """Zero-shot chain-of-thought."""
        prompt = f"""Answer this question. Let's think step by step.

Question: {question}

Let me work through this step by step:"""

        response = self.llm.invoke(prompt).content
        answer = extract_answer(response) or "Could not extract answer"

        return response, answer, 0.7

    def _self_consistency(
        self,
        question: str,
        num_samples: int = 3
    ) -> Tuple[str, str, float]:
        """Self-consistency with multiple samples."""
        prompt = f"""Solve this problem step by step.

Question: {question}

Solution:"""

        # Use higher temperature for diversity
        llm_diverse = get_llm(temperature=0.7)
        answers = []
        reasonings = []

        for _ in range(num_samples):
            response = llm_diverse.invoke(prompt).content
            reasonings.append(response)
            answer = extract_answer(response)
            if answer:
                answers.append(answer)

        if not answers:
            return reasonings[0] if reasonings else "", "Could not extract", 0.0

        # Vote
        answer_counts = Counter(answers)
        most_common = answer_counts.most_common(1)[0]

        confidence = most_common[1] / len(answers)
        combined_reasoning = f"[Self-consistency with {num_samples} samples]\n\n"
        combined_reasoning += reasonings[0][:500]

        return combined_reasoning, most_common[0], confidence

    def _pal(self, question: str) -> Tuple[str, str, float]:
        """Program-Aided Language Models."""
        prompt = f"""Solve this problem by writing Python code.

Problem: {question}

```python
# Calculate the answer
"""

        response = self.llm.invoke(prompt).content

        # Extract code
        code_match = re.search(r'```python\n?(.*?)```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        else:
            code = response

        # Execute code
        try:
            import io
            import contextlib

            f = io.StringIO()
            namespace = {}
            with contextlib.redirect_stdout(f):
                exec(code, {"__builtins__": __builtins__}, namespace)

            output = f.getvalue().strip()
            if output:
                return f"Code:\n{code}\n\nOutput: {output}", output, 0.9
            else:
                for var in ['result', 'answer', 'total']:
                    if var in namespace:
                        return f"Code:\n{code}", str(namespace[var]), 0.9
                return f"Code:\n{code}", "No output", 0.5
        except Exception as e:
            return f"Code error: {e}\n\n{code}", str(e), 0.3

    def _react(self, question: str, max_iterations: int = 3) -> Tuple[str, str, float]:
        """ReAct reasoning with tools."""
        tool_descriptions = "\n".join([
            f"- {name}: Use for {name}" for name in self.tools.keys()
        ])

        prompt = f"""You are an assistant with tools. Use this format:

Thought: [your reasoning]
Action: [tool(args)]
Observation: [result]
... repeat as needed ...
Final Answer: [answer]

Tools: {tool_descriptions}

Question: {question}
Thought:"""

        conversation = prompt
        full_reasoning = []

        for _ in range(max_iterations):
            response = self.llm.invoke(conversation).content
            full_reasoning.append(response)

            if "Final Answer:" in response:
                match = re.search(r'Final Answer:\s*(.+?)(?:\n|$)', response)
                answer = match.group(1).strip() if match else "Unknown"
                return "\n".join(full_reasoning), answer, 0.8

            # Parse action
            action_match = re.search(r'Action:\s*(\w+)\(([^)]*)\)', response)
            if action_match:
                tool_name = action_match.group(1).lower()
                args = action_match.group(2)

                if tool_name in self.tools:
                    observation = self.tools[tool_name](args)
                else:
                    observation = f"Unknown tool: {tool_name}"

                conversation += response + f"\nObservation: {observation}\nThought:"
            else:
                conversation += response + "\nThought:"

        return "\n".join(full_reasoning), "Max iterations reached", 0.5

    def _least_to_most(self, question: str) -> Tuple[str, str, float]:
        """Least-to-most decomposition."""
        # Decompose
        decompose_prompt = f"""Break this problem into simpler sub-problems:

Problem: {question}

Sub-problems (one per line):"""

        decomposition = self.llm.invoke(decompose_prompt).content
        subproblems = [
            line.strip() for line in decomposition.split('\n')
            if line.strip() and not line.startswith('#')
        ][:3]

        # Solve each
        solutions = []
        context = ""

        for subproblem in subproblems:
            solve_prompt = f"""Given: {context if context else "No previous info"}

Solve: {subproblem}"""
            solution = self.llm.invoke(solve_prompt).content
            solutions.append(f"Sub: {subproblem}\nSol: {solution[:100]}")
            context += f"\n{subproblem}: {solution[:50]}"

        # Final
        final_prompt = f"""Given:
{chr(10).join(solutions)}

Answer: {question}"""
        final = self.llm.invoke(final_prompt).content
        answer = extract_answer(final) or "Unknown"

        return f"Decomposition:\n{decomposition}\n\nFinal:\n{final}", answer, 0.75


# ============================================================================
# BENCHMARK SUITE
# ============================================================================

BENCHMARK_PROBLEMS = [
    {
        "question": "A store has 23 apples. If 7 are sold and 12 more arrive, how many?",
        "answer": "28",
        "type": "arithmetic"
    },
    {
        "question": "Roger has 5 balls. He buys 2 cans with 3 balls each. How many total?",
        "answer": "11",
        "type": "multi_step"
    },
    {
        "question": "A farmer has 17 sheep. All but 9 run away. How many left?",
        "answer": "9",
        "type": "trick"
    },
    {
        "question": "If John is taller than Mary, and Mary is taller than Bob, is John taller than Bob?",
        "answer": "yes",
        "type": "logic"
    },
    {
        "question": "What is 15 multiplied by 7?",
        "answer": "105",
        "type": "arithmetic"
    },
]


def run_benchmark(engine: ReasoningEngine, strategy: ReasoningStrategy) -> BenchmarkResult:
    """Run benchmark with specified strategy."""
    results = []
    correct = 0
    total_latency = 0
    total_confidence = 0

    for problem in BENCHMARK_PROBLEMS:
        trace = engine.solve(problem["question"], strategy)

        # Check if correct
        expected = str(problem["answer"]).lower()
        actual = str(trace.answer).lower()
        is_correct = expected in actual or actual in expected

        if is_correct:
            correct += 1

        total_latency += trace.latency_ms
        total_confidence += trace.confidence

        results.append({
            "question": problem["question"],
            "expected": problem["answer"],
            "actual": trace.answer,
            "correct": is_correct,
            "confidence": trace.confidence,
        })

    n = len(BENCHMARK_PROBLEMS)
    return BenchmarkResult(
        strategy=strategy.value,
        total_problems=n,
        correct=correct,
        accuracy=correct / n,
        avg_latency_ms=total_latency / n,
        avg_confidence=total_confidence / n,
        problems=results
    )


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo1_reasoning_techniques():
    """Demo 1: Different reasoning techniques."""
    print("\n" + "="*70)
    print("🧠 DEMO 1: Reasoning Techniques")
    print("="*70)

    engine = ReasoningEngine()

    strategies = [
        (ReasoningStrategy.ZERO_SHOT_COT, "Zero-Shot CoT"),
        (ReasoningStrategy.SELF_CONSISTENCY, "Self-Consistency"),
        (ReasoningStrategy.PAL, "Program-Aided (PAL)"),
    ]

    question = "A bookshelf has 4 shelves. Each shelf has 8 books. If 5 books are removed, how many remain?"
    expected = "27"

    print(f"\n📝 Question: {question}")
    print(f"   Expected: {expected}")

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️ No API key. Showing strategy descriptions:\n")
        for strategy, name in strategies:
            print(f"   • {name}")
        return

    for strategy, name in strategies:
        print(f"\n{'─'*60}")
        print(f"📌 Strategy: {name}")

        trace = engine.solve(question, strategy)

        print(f"   Answer: {trace.answer}")
        print(f"   Confidence: {trace.confidence:.0%}")
        print(f"   Latency: {trace.latency_ms:.0f}ms")

        is_correct = expected in trace.answer or trace.answer in expected
        print(f"   {'✅ Correct' if is_correct else '❌ Incorrect'}")


def demo2_react_with_tools():
    """Demo 2: ReAct with tools."""
    print("\n" + "="*70)
    print("🔧 DEMO 2: ReAct with Tools")
    print("="*70)

    engine = ReasoningEngine()

    questions = [
        "What is the population of France divided by 2?",
        "What is 15 * 7 + 23?",
    ]

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️ No API key. ReAct would use these tools:")
        print("   • calculate(expression) - Math calculations")
        print("   • search(query) - Knowledge lookup")
        return

    for question in questions:
        print(f"\n{'─'*60}")
        print(f"📝 Question: {question}")

        trace = engine.solve(question, ReasoningStrategy.REACT)

        print(f"\n📋 Reasoning:")
        print(trace.reasoning[:400] + "..." if len(trace.reasoning) > 400 else trace.reasoning)
        print(f"\n✅ Answer: {trace.answer}")


def demo3_benchmark():
    """Demo 3: Benchmark evaluation."""
    print("\n" + "="*70)
    print("📊 DEMO 3: Benchmark Evaluation")
    print("="*70)

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️ No API key. Benchmark would test:")
        for p in BENCHMARK_PROBLEMS[:3]:
            print(f"   • {p['question'][:50]}... ({p['type']})")
        return

    engine = ReasoningEngine()

    print("\n🔄 Running benchmark with Zero-Shot CoT...")
    result = run_benchmark(engine, ReasoningStrategy.ZERO_SHOT_COT)

    print(f"\n📈 Results:")
    print(f"   Accuracy: {result.accuracy:.0%} ({result.correct}/{result.total_problems})")
    print(f"   Avg Latency: {result.avg_latency_ms:.0f}ms")
    print(f"   Avg Confidence: {result.avg_confidence:.0%}")

    print(f"\n📋 Details:")
    for p in result.problems:
        status = "✅" if p["correct"] else "❌"
        print(f"   {status} {p['question'][:40]}... → {p['actual']}")


def demo_solve(question: str):
    """Solve a single question with auto-selected strategy."""
    print("\n" + "="*70)
    print("🤔 Solving Your Question")
    print("="*70)

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️ No API key found.")
        print("   Set GOOGLE_API_KEY or ANTHROPIC_API_KEY")
        return

    engine = ReasoningEngine()
    problem_type = classify_problem(question)
    strategy = select_strategy(problem_type)

    print(f"\n📝 Question: {question}")
    print(f"   Problem Type: {problem_type.value}")
    print(f"   Selected Strategy: {strategy.value}")

    trace = engine.solve(question)

    print(f"\n📋 Reasoning:")
    print(trace.reasoning[:500] + "..." if len(trace.reasoning) > 500 else trace.reasoning)

    print(f"\n✅ Answer: {trace.answer}")
    print(f"   Confidence: {trace.confidence:.0%}")
    print(f"   Latency: {trace.latency_ms:.0f}ms")


def print_help():
    """Print help information."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🧠 Reasoning Engine - Module 17                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  A comprehensive reasoning system with multiple strategies.  ║
║                                                              ║
║  USAGE:                                                      ║
║    python deliverable_reasoning_engine.py <command>          ║
║                                                              ║
║  COMMANDS:                                                   ║
║    demo1            Reasoning techniques comparison          ║
║    demo2            ReAct with tools demonstration           ║
║    demo3            Benchmark evaluation                     ║
║    solve "question" Solve a specific question                ║
║    help             Show this help message                   ║
║                                                              ║
║  STRATEGIES:                                                 ║
║    • Zero-Shot CoT   - "Let's think step by step"           ║
║    • Self-Consistency - Multiple paths, vote on answer       ║
║    • PAL             - Generate code for calculations        ║
║    • ReAct           - Reason + Act with tools              ║
║    • Least-to-Most   - Decompose into sub-problems          ║
║                                                              ║
║  EXAMPLES:                                                   ║
║    python deliverable_reasoning_engine.py demo1              ║
║    python deliverable_reasoning_engine.py solve "What is 15*7?"║
║                                                              ║
║  API KEYS:                                                   ║
║    export GOOGLE_API_KEY='your-key'                         ║
║    export ANTHROPIC_API_KEY='your-key'                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo1_reasoning_techniques()
    elif command == "demo2":
        demo2_react_with_tools()
    elif command == "demo3":
        demo3_benchmark()
    elif command == "solve":
        if len(sys.argv) < 3:
            print("Usage: python deliverable_reasoning_engine.py solve \"Your question\"")
            return
        question = " ".join(sys.argv[2:])
        demo_solve(question)
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
