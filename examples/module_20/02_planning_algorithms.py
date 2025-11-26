#!/usr/bin/env python3
"""
Module 20 Example 02: Planning Algorithms

This example demonstrates different planning patterns for AI agents:
1. Plan-and-Execute: Create plan first, then execute steps
2. ReWOO: Plan all tool calls upfront, execute, then solve
3. Tree of Thought: Explore multiple reasoning paths

Planning transforms agents from reactive responders to proactive
problem-solvers. Different patterns have different trade-offs.

Usage:
    python 02_planning_algorithms.py demo1  # Plan-and-Execute
    python 02_planning_algorithms.py demo2  # ReWOO pattern
    python 02_planning_algorithms.py demo3  # Tree of Thought
    python 02_planning_algorithms.py demo4  # Compare all patterns
"""

import json
import random
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple

# Storage directory
STORAGE_DIR = Path(".planning_demo")


# =============================================================================
# SIMULATED LLM (For demo without API)
# =============================================================================

class SimulatedLLM:
    """
    Simulated LLM for demonstrations.

    In production, you'd replace this with:
    - langchain_google_genai.ChatGoogleGenerativeAI
    - langchain_anthropic.ChatAnthropic
    - langchain_openai.ChatOpenAI
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.call_count = 0

    def generate(self, prompt: str) -> str:
        """Generate a response (simulated)."""
        self.call_count += 1

        if self.verbose:
            print(f"  [LLM Call #{self.call_count}]")

        # Simulate some latency
        time.sleep(0.1)

        # Pattern matching for different prompts
        prompt_lower = prompt.lower()

        # Plan generation
        if "create a step-by-step plan" in prompt_lower:
            return self._generate_plan(prompt)

        # Plan parsing (ReWOO style)
        if "plan how to solve" in prompt_lower:
            return self._generate_rewoo_plan(prompt)

        # Thought generation (ToT)
        if "generate" in prompt_lower and "different next steps" in prompt_lower:
            return self._generate_thoughts(prompt)

        # Evaluation (ToT)
        if "rate this reasoning path" in prompt_lower:
            return str(random.randint(5, 9))

        # Summary
        if "summarize" in prompt_lower:
            return "Task completed successfully with all steps executed."

        # Synthesis
        if "synthesize" in prompt_lower or "based on this reasoning" in prompt_lower:
            return "Based on the analysis, the solution involves systematic problem decomposition and execution."

        # Default response
        return "Analysis complete. Proceeding with the next step."

    def _generate_plan(self, prompt: str) -> str:
        """Generate a plan based on the task."""
        return json.dumps({
            "steps": [
                {
                    "description": "Analyze the requirements and constraints",
                    "tool": None,
                    "tool_input": None,
                    "depends_on": []
                },
                {
                    "description": "Search for relevant information",
                    "tool": "search",
                    "tool_input": "relevant information",
                    "depends_on": [0]
                },
                {
                    "description": "Calculate the result based on findings",
                    "tool": "calculate",
                    "tool_input": "process data",
                    "depends_on": [1]
                },
                {
                    "description": "Format and present the final answer",
                    "tool": None,
                    "tool_input": None,
                    "depends_on": [2]
                }
            ]
        })

    def _generate_rewoo_plan(self, prompt: str) -> str:
        """Generate a ReWOO-style plan."""
        return """Step 1:
Plan: Search for relevant information to understand the problem
Tool: search
Input: "problem context"
Evidence: #E1

Step 2:
Plan: Analyze the search results from #E1
Tool: analyze
Input: #E1
Evidence: #E2

Step 3:
Plan: Calculate final answer using analysis from #E2
Tool: calculate
Input: #E2
Evidence: #E3"""

    def _generate_thoughts(self, prompt: str) -> str:
        """Generate multiple reasoning paths."""
        thoughts = [
            "First, we could break down the problem into smaller components and solve each independently.",
            "Alternatively, we could use an iterative approach, refining our solution with each step.",
            "A third option is to find similar solved problems and adapt their solutions to our case."
        ]
        return "\n\n".join(thoughts)


# =============================================================================
# SIMULATED TOOLS
# =============================================================================

def create_demo_tools() -> Dict[str, Callable]:
    """Create demo tools for the agent."""

    def search(query: str) -> str:
        """Search for information."""
        return f"Search results for '{query}': Found 3 relevant documents about the topic."

    def calculate(expression: str) -> str:
        """Perform calculations."""
        return f"Calculation result for '{expression}': Result = 42"

    def analyze(data: str) -> str:
        """Analyze data."""
        return f"Analysis of '{data[:30]}...': Data shows positive trends with 85% confidence."

    def format_output(content: str) -> str:
        """Format output for presentation."""
        return f"Formatted: {content}"

    return {
        "search": search,
        "calculate": calculate,
        "analyze": analyze,
        "format": format_output
    }


# =============================================================================
# PATTERN 1: PLAN-AND-EXECUTE
# =============================================================================

class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """A single step in the plan."""
    step_id: int
    description: str
    tool: Optional[str] = None
    tool_input: Optional[str] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    depends_on: List[int] = field(default_factory=list)


@dataclass
class Plan:
    """A complete execution plan."""
    goal: str
    steps: List[PlanStep]
    current_step: int = 0


class PlanAndExecuteAgent:
    """
    Plan-and-Execute Agent.

    This pattern:
    1. Creates a detailed plan first
    2. Executes each step sequentially
    3. Handles dependencies between steps
    4. Reports on execution results

    Good for: Complex multi-step tasks
    Trade-off: Requires upfront planning, less adaptive
    """

    def __init__(self, llm: SimulatedLLM, tools: Dict[str, Callable]):
        self.llm = llm
        self.tools = tools

    def create_plan(self, task: str) -> Plan:
        """Create a plan for the given task."""
        tools_description = "\n".join([
            f"- {name}: {func.__doc__}"
            for name, func in self.tools.items()
        ])

        prompt = f"""Create a step-by-step plan to accomplish this task.

Task: {task}

Available tools:
{tools_description}

Respond in JSON format with steps array."""

        response = self.llm.generate(prompt)

        try:
            data = json.loads(response)
            steps = [
                PlanStep(
                    step_id=i,
                    description=s["description"],
                    tool=s.get("tool"),
                    tool_input=s.get("tool_input"),
                    depends_on=s.get("depends_on", [])
                )
                for i, s in enumerate(data["steps"])
            ]
            return Plan(goal=task, steps=steps)
        except json.JSONDecodeError:
            # Fallback plan
            return Plan(goal=task, steps=[
                PlanStep(0, "Analyze task", None, None),
                PlanStep(1, "Execute solution", None, None, depends_on=[0])
            ])

    def execute_plan(self, plan: Plan) -> str:
        """Execute a plan step by step."""
        results = []

        for step in plan.steps:
            # Check dependencies
            deps_met = True
            for dep_id in step.depends_on:
                dep_step = plan.steps[dep_id]
                if dep_step.status != StepStatus.COMPLETED:
                    deps_met = False
                    break

            if not deps_met:
                step.status = StepStatus.FAILED
                step.result = "Dependencies not met"
                continue

            step.status = StepStatus.IN_PROGRESS
            print(f"  Executing step {step.step_id}: {step.description}")

            try:
                if step.tool and step.tool in self.tools:
                    result = self.tools[step.tool](step.tool_input or "")
                else:
                    result = self.llm.generate(
                        f"Complete this step: {step.description}"
                    )

                step.result = result
                step.status = StepStatus.COMPLETED
                results.append(f"Step {step.step_id}: {result}")
                print(f"    ✓ {result[:50]}...")

            except Exception as e:
                step.status = StepStatus.FAILED
                step.result = str(e)
                results.append(f"Step {step.step_id} failed: {e}")

        return "\n".join(results)

    def run(self, task: str) -> Tuple[str, int]:
        """Plan and execute a task. Returns (result, llm_calls)."""
        self.llm.call_count = 0

        print(f"\n--- Creating plan for: '{task}' ---")
        plan = self.create_plan(task)

        print(f"\n--- Plan with {len(plan.steps)} steps ---")
        for step in plan.steps:
            deps = f" (depends on: {step.depends_on})" if step.depends_on else ""
            tool = f" [tool: {step.tool}]" if step.tool else ""
            print(f"  {step.step_id}. {step.description}{tool}{deps}")

        print(f"\n--- Executing plan ---")
        result = self.execute_plan(plan)

        return result, self.llm.call_count


# =============================================================================
# PATTERN 2: REWOO (Reason Without Observation)
# =============================================================================

@dataclass
class ReWOOPlan:
    """A ReWOO-style plan with evidence variables."""
    steps: List[Dict[str, str]]


class ReWOOAgent:
    """
    ReWOO: Reason Without Observation.

    This pattern:
    1. Plans ALL tool calls upfront (without seeing results)
    2. Executes all tools in batch
    3. Solves the problem using all evidence

    Good for: Reducing LLM calls, parallelizable execution
    Trade-off: Can't adapt plan based on intermediate results
    """

    def __init__(self, llm: SimulatedLLM, tools: Dict[str, Callable]):
        self.llm = llm
        self.tools = tools

    def plan(self, task: str) -> ReWOOPlan:
        """Create a plan with evidence variables."""
        tools_desc = "\n".join([
            f"- {name}: {func.__doc__}"
            for name, func in self.tools.items()
        ])

        prompt = f"""Plan how to solve this task using the available tools.
Use #E[n] as placeholder for evidence from step n.

Task: {task}

Available tools:
{tools_desc}

Create a plan with steps that reference evidence variables."""

        response = self.llm.generate(prompt)
        return self._parse_plan(response)

    def _parse_plan(self, response: str) -> ReWOOPlan:
        """Parse the planner output into structured steps."""
        steps = []
        current_step = {}

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("Step"):
                if current_step:
                    steps.append(current_step)
                current_step = {}
            elif line.startswith("Plan:"):
                current_step["plan"] = line[5:].strip()
            elif line.startswith("Tool:"):
                current_step["tool"] = line[5:].strip()
            elif line.startswith("Input:"):
                current_step["input"] = line[6:].strip()
            elif line.startswith("Evidence:"):
                current_step["evidence_var"] = line[9:].strip()

        if current_step:
            steps.append(current_step)

        return ReWOOPlan(steps=steps)

    def execute(self, plan: ReWOOPlan) -> Dict[str, str]:
        """Execute all planned tool calls, collecting evidence."""
        evidence = {}

        for i, step in enumerate(plan.steps, 1):
            tool_name = step.get("tool")
            tool_input = step.get("input", "")
            evidence_var = step.get("evidence_var", f"#E{i}")

            # Substitute previous evidence into input
            for var, value in evidence.items():
                tool_input = tool_input.replace(var, str(value))

            print(f"  Executing: {step.get('plan', 'Step')[:40]}...")

            # Execute tool
            if tool_name and tool_name in self.tools:
                try:
                    result = self.tools[tool_name](tool_input)
                    evidence[evidence_var] = result
                    print(f"    ✓ {evidence_var}: {result[:40]}...")
                except Exception as e:
                    evidence[evidence_var] = f"Error: {e}"
            else:
                evidence[evidence_var] = f"Simulated result for: {tool_input}"

        return evidence

    def solve(self, task: str, plan: ReWOOPlan, evidence: Dict[str, str]) -> str:
        """Solve the task using collected evidence."""
        plan_text = "\n".join([
            f"Step {i}: {s.get('plan', 'N/A')}"
            for i, s in enumerate(plan.steps, 1)
        ])

        evidence_text = "\n".join([
            f"{var}: {value[:100]}"
            for var, value in evidence.items()
        ])

        prompt = f"""Solve this task using the evidence collected.

Task: {task}

Plan executed:
{plan_text}

Evidence collected:
{evidence_text}

Synthesize the final answer:"""

        return self.llm.generate(prompt)

    def run(self, task: str) -> Tuple[str, int]:
        """Full ReWOO execution. Returns (result, llm_calls)."""
        self.llm.call_count = 0

        print(f"\n--- Planning (without observation) ---")
        plan = self.plan(task)

        print(f"\n--- Plan with {len(plan.steps)} steps ---")
        for i, step in enumerate(plan.steps, 1):
            print(f"  {i}. {step.get('plan', 'N/A')[:50]}... [{step.get('tool', 'N/A')}]")

        print(f"\n--- Executing all tools ---")
        evidence = self.execute(plan)

        print(f"\n--- Solving with evidence ---")
        result = self.solve(task, plan, evidence)

        return result, self.llm.call_count


# =============================================================================
# PATTERN 3: TREE OF THOUGHT (ToT)
# =============================================================================

@dataclass
class ThoughtNode:
    """A node in the thought tree."""
    thought: str
    score: float
    parent: Optional['ThoughtNode'] = None
    children: List['ThoughtNode'] = field(default_factory=list)
    depth: int = 0


class TreeOfThoughtAgent:
    """
    Tree of Thought: Explores multiple reasoning paths.

    This pattern:
    1. Generates multiple possible next thoughts
    2. Evaluates each thought path
    3. Prunes low-scoring paths
    4. Continues exploring best paths
    5. Synthesizes answer from best path

    Good for: Complex reasoning, problems with multiple solutions
    Trade-off: More LLM calls, slower execution
    """

    def __init__(self, llm: SimulatedLLM, branching_factor: int = 3, max_depth: int = 2):
        self.llm = llm
        self.branching_factor = branching_factor
        self.max_depth = max_depth

    def generate_thoughts(self, problem: str, current_path: List[str]) -> List[str]:
        """Generate possible next thoughts."""
        path_text = " -> ".join(current_path) if current_path else "Start"

        prompt = f"""Problem: {problem}

Current reasoning path: {path_text}

Generate {self.branching_factor} different next steps or approaches.
Each should be distinct.

Format each as a separate paragraph."""

        response = self.llm.generate(prompt)

        # Parse thoughts
        thoughts = [t.strip() for t in response.split("\n\n") if t.strip()]
        return thoughts[:self.branching_factor]

    def evaluate_thought(self, problem: str, path: List[str]) -> float:
        """Score how promising a thought path is."""
        path_text = " -> ".join(path)

        prompt = f"""Problem: {problem}

Reasoning path: {path_text}

Rate this reasoning path on a scale of 0-10.
Respond with just a number."""

        response = self.llm.generate(prompt)
        try:
            score = float(response.strip()) / 10.0
            return min(max(score, 0.0), 1.0)
        except:
            return 0.5

    def solve(self, problem: str) -> Tuple[str, List[str], int]:
        """Solve using tree of thought exploration. Returns (result, best_path, llm_calls)."""
        self.llm.call_count = 0

        print(f"\n--- Exploring reasoning paths ---")

        # Simple BFS exploration
        best_path = []
        best_score = 0.0

        # Level 0: Generate initial thoughts
        initial_thoughts = self.generate_thoughts(problem, [])
        print(f"\nLevel 0: Generated {len(initial_thoughts)} initial thoughts")

        for i, thought in enumerate(initial_thoughts):
            path = [thought]
            score = self.evaluate_thought(problem, path)
            print(f"  [{score:.2f}] {thought[:50]}...")

            if score > best_score:
                best_score = score
                best_path = path

            # Explore deeper if promising
            if score > 0.5 and self.max_depth > 1:
                deeper_thoughts = self.generate_thoughts(problem, path)
                print(f"    Exploring deeper ({len(deeper_thoughts)} thoughts)...")

                for dt in deeper_thoughts:
                    deep_path = path + [dt]
                    deep_score = self.evaluate_thought(problem, deep_path)
                    print(f"      [{deep_score:.2f}] {dt[:40]}...")

                    if deep_score > best_score:
                        best_score = deep_score
                        best_path = deep_path

        print(f"\n--- Best path found (score: {best_score:.2f}) ---")
        for i, step in enumerate(best_path):
            print(f"  {i+1}. {step[:60]}...")

        # Synthesize answer
        print(f"\n--- Synthesizing answer ---")
        path_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(best_path)])

        prompt = f"""Problem: {problem}

Best reasoning path:
{path_text}

Based on this reasoning, provide the final answer."""

        result = self.llm.generate(prompt)

        return result, best_path, self.llm.call_count


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_plan_and_execute():
    """Demo 1: Plan-and-Execute pattern."""
    print("\n" + "="*60)
    print("DEMO 1: PLAN-AND-EXECUTE PATTERN")
    print("="*60)

    llm = SimulatedLLM(verbose=True)
    tools = create_demo_tools()
    agent = PlanAndExecuteAgent(llm, tools)

    task = "Find information about Python frameworks and calculate their popularity scores"

    result, llm_calls = agent.run(task)

    print(f"\n--- Results ---")
    print(f"LLM calls: {llm_calls}")
    print(f"Result: {result[:200]}...")

    print("\n--- Analysis ---")
    print("Plan-and-Execute:")
    print("  + Creates structured, trackable plans")
    print("  + Handles dependencies between steps")
    print("  + Good for complex multi-step tasks")
    print("  - Requires upfront planning overhead")
    print("  - Less adaptive to unexpected results")


def demo_2_rewoo():
    """Demo 2: ReWOO pattern."""
    print("\n" + "="*60)
    print("DEMO 2: REWOO (REASON WITHOUT OBSERVATION)")
    print("="*60)

    llm = SimulatedLLM(verbose=True)
    tools = create_demo_tools()
    agent = ReWOOAgent(llm, tools)

    task = "Analyze the best approach for building a chatbot"

    result, llm_calls = agent.run(task)

    print(f"\n--- Results ---")
    print(f"LLM calls: {llm_calls}")
    print(f"Result: {result[:200]}...")

    print("\n--- Analysis ---")
    print("ReWOO (Reason Without Observation):")
    print("  + Minimal LLM calls (typically 2-3)")
    print("  + All tool calls can be parallelized")
    print("  + Efficient for independent operations")
    print("  - Can't adapt based on intermediate results")
    print("  - May plan suboptimally without feedback")


def demo_3_tree_of_thought():
    """Demo 3: Tree of Thought pattern."""
    print("\n" + "="*60)
    print("DEMO 3: TREE OF THOUGHT (ToT)")
    print("="*60)

    llm = SimulatedLLM(verbose=True)
    agent = TreeOfThoughtAgent(llm, branching_factor=3, max_depth=2)

    problem = "How should we design a scalable AI agent architecture?"

    result, best_path, llm_calls = agent.solve(problem)

    print(f"\n--- Results ---")
    print(f"LLM calls: {llm_calls}")
    print(f"Result: {result[:200]}...")

    print("\n--- Analysis ---")
    print("Tree of Thought:")
    print("  + Explores multiple reasoning paths")
    print("  + Can backtrack from dead ends")
    print("  + Good for complex problems")
    print("  - Many LLM calls (expensive)")
    print("  - Slower execution")


def demo_4_compare_patterns():
    """Demo 4: Compare all patterns."""
    print("\n" + "="*60)
    print("DEMO 4: COMPARING PLANNING PATTERNS")
    print("="*60)

    task = "Create a strategy for improving AI model performance"

    results = {}

    # Plan-and-Execute
    print("\n--- Running Plan-and-Execute ---")
    llm1 = SimulatedLLM(verbose=False)
    agent1 = PlanAndExecuteAgent(llm1, create_demo_tools())
    _, calls1 = agent1.run(task)
    results["Plan-and-Execute"] = calls1

    # ReWOO
    print("\n--- Running ReWOO ---")
    llm2 = SimulatedLLM(verbose=False)
    agent2 = ReWOOAgent(llm2, create_demo_tools())
    _, calls2 = agent2.run(task)
    results["ReWOO"] = calls2

    # Tree of Thought
    print("\n--- Running Tree of Thought ---")
    llm3 = SimulatedLLM(verbose=False)
    agent3 = TreeOfThoughtAgent(llm3, branching_factor=2, max_depth=2)
    _, _, calls3 = agent3.solve(task)
    results["Tree of Thought"] = calls3

    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)

    print("\n| Pattern           | LLM Calls | Best For                    |")
    print("|-------------------|-----------|------------------------------|")
    print(f"| Plan-and-Execute  | {results['Plan-and-Execute']:9} | Complex multi-step tasks     |")
    print(f"| ReWOO             | {results['ReWOO']:9} | Cost-efficient, parallelizable|")
    print(f"| Tree of Thought   | {results['Tree of Thought']:9} | Complex reasoning problems   |")

    print("\n--- Recommendations ---")
    print("1. Simple tasks: Skip planning, use direct execution")
    print("2. Multi-step tasks: Use Plan-and-Execute")
    print("3. Cost-sensitive: Use ReWOO (minimal LLM calls)")
    print("4. Complex reasoning: Use Tree of Thought")
    print("5. Production: Often combine patterns based on task type")


def show_usage():
    """Show usage information."""
    print(__doc__)
    print("\nAvailable demos:")
    print("  demo1 - Plan-and-Execute pattern")
    print("  demo2 - ReWOO (Reason Without Observation)")
    print("  demo3 - Tree of Thought")
    print("  demo4 - Compare all patterns")


def main():
    """Main entry point."""
    STORAGE_DIR.mkdir(exist_ok=True)

    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_plan_and_execute()
    elif command == "demo2":
        demo_2_rewoo()
    elif command == "demo3":
        demo_3_tree_of_thought()
    elif command == "demo4":
        demo_4_compare_patterns()
    elif command == "all":
        demo_1_plan_and_execute()
        demo_2_rewoo()
        demo_3_tree_of_thought()
        demo_4_compare_patterns()
    else:
        print(f"Unknown command: {command}")
        show_usage()


if __name__ == "__main__":
    main()
