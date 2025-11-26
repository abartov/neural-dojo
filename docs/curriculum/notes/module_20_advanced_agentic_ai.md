# Module 20: Advanced Agentic AI

**Last Updated**: 2025-11-25
**Status**: 🟢 Complete
**Duration**: 8-9 hours

---

## Learning Objectives

By the end of this module, you will:
- Master agent memory systems (short-term, long-term, episodic, summary)
- Implement planning algorithms (ReWOO, Plan-and-Execute, Tree of Thought)
- Build multi-agent collaborative systems
- Design agent architectures (supervisor, swarm, hierarchical)
- Implement self-improvement patterns (reflection, self-correction)
- Understand when and how agents create their own tools

---

## The Heureka Moment

**Agents with memory and planning can solve problems they couldn't before!**

Think about the difference between:
1. A calculator (stateless, single operation)
2. A spreadsheet (state, but human-driven planning)
3. A human accountant (memory, planning, collaboration, self-correction)

We've built systems like #1 and #2. This module teaches you to build #3.

---

## Part 1: Agent Memory Systems

### The Memory Problem

Consider this conversation:

```
User: My name is Alex and I work at TechCorp.
Agent: Nice to meet you, Alex from TechCorp!

[1000 messages later...]

User: Where do I work again?
Agent: I'm sorry, I don't have information about where you work.
```

Without memory, agents are goldfish - brilliant in the moment, but unable to build relationships or learn from experience.

### Did You Know?

In 2023, researchers at Stanford created "Generative Agents" - 25 AI characters living in a Sims-like world. Each agent had three memory types: a "memory stream" of observations, a "reflection" system for synthesizing insights, and a "plan" for daily activities. The agents spontaneously organized a Valentine's Day party, spread gossip about each other, and formed social cliques - all emergent behavior from the memory architecture!

The paper "Generative Agents: Interactive Simulacra of Human Behavior" has been cited 2,000+ times since April 2023.

### Memory Types

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT MEMORY ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  SHORT-TERM  │  │   LONG-TERM  │  │   EPISODIC   │          │
│  │   (Buffer)   │  │   (Vector)   │  │  (Specific)  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └────────────┬────┴────────────┬────┘                   │
│                      │                 │                        │
│              ┌───────▼───────┐ ┌───────▼───────┐               │
│              │    SUMMARY    │ │   SEMANTIC    │               │
│              │  (Compressed) │ │   (Indexed)   │               │
│              └───────────────┘ └───────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 1. Short-Term Memory (Conversation Buffer)

The simplest form - keep recent messages in context.

```python
from typing import List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ConversationBuffer:
    """Short-term memory: recent conversation history."""
    messages: List[Message] = field(default_factory=list)
    max_messages: int = 20  # Keep last N messages

    def add(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
        # Trim to max size
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> str:
        """Format messages for LLM context."""
        return "\n".join([
            f"{m.role}: {m.content}"
            for m in self.messages
        ])

    def clear(self):
        self.messages = []
```

**Limitations**:
- Fixed window size
- Loses information outside window
- No semantic understanding of what's important

#### 2. Long-Term Memory (Vector Store)

Store experiences as embeddings, retrieve relevant ones when needed.

```python
from dataclasses import dataclass, field
from typing import List, Optional
import json

@dataclass
class MemoryEntry:
    """A single memory with embedding."""
    content: str
    embedding: List[float]
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""
    importance: float = 1.0  # How significant is this memory?

class VectorMemory:
    """Long-term memory using vector similarity."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.memories: List[MemoryEntry] = []

    def store(self, content: str, metadata: dict = None):
        """Store a new memory."""
        embedding = self.embedding_model.embed(content)
        importance = self._calculate_importance(content)

        memory = MemoryEntry(
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
            importance=importance
        )
        self.memories.append(memory)

    def retrieve(self, query: str, k: int = 5) -> List[MemoryEntry]:
        """Retrieve k most relevant memories."""
        query_embedding = self.embedding_model.embed(query)

        # Calculate similarity scores
        scored = []
        for memory in self.memories:
            similarity = self._cosine_similarity(
                query_embedding,
                memory.embedding
            )
            # Weight by importance and recency
            score = similarity * memory.importance
            scored.append((score, memory))

        # Return top k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:k]]

    def _calculate_importance(self, content: str) -> float:
        """Estimate importance of a memory."""
        # Simple heuristics - could use LLM for better scoring
        importance = 1.0

        # Questions are often important
        if "?" in content:
            importance += 0.2

        # Personal information
        personal_keywords = ["my name", "i work", "i live", "my email"]
        for kw in personal_keywords:
            if kw in content.lower():
                importance += 0.3

        # Preferences and decisions
        if any(w in content.lower() for w in ["prefer", "want", "decided", "chose"]):
            importance += 0.2

        return min(importance, 2.0)  # Cap at 2x

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
```

#### 3. Episodic Memory (Specific Experiences)

Remember specific interactions as coherent episodes, not just isolated facts.

```python
@dataclass
class Episode:
    """A complete interaction episode."""
    episode_id: str
    title: str
    summary: str
    messages: List[Message]
    outcome: str  # What was achieved?
    lessons: List[str]  # What was learned?
    created_at: datetime
    embedding: List[float] = field(default_factory=list)

class EpisodicMemory:
    """Stores complete interaction episodes."""

    def __init__(self, llm, embedding_model):
        self.llm = llm
        self.embedding_model = embedding_model
        self.episodes: List[Episode] = []

    def create_episode(self, messages: List[Message]) -> Episode:
        """Create an episode from a conversation."""
        # Use LLM to summarize and extract lessons
        conversation = "\n".join([
            f"{m.role}: {m.content}" for m in messages
        ])

        analysis_prompt = f"""Analyze this conversation and extract:
1. A short title (5-10 words)
2. A one-paragraph summary
3. The outcome (what was achieved)
4. Key lessons learned (bullet points)

Conversation:
{conversation}

Respond in JSON format:
{{
    "title": "...",
    "summary": "...",
    "outcome": "...",
    "lessons": ["...", "..."]
}}"""

        response = self.llm.generate(analysis_prompt)
        analysis = json.loads(response)

        episode = Episode(
            episode_id=f"ep_{len(self.episodes)}",
            title=analysis["title"],
            summary=analysis["summary"],
            messages=messages,
            outcome=analysis["outcome"],
            lessons=analysis["lessons"],
            created_at=datetime.now(),
            embedding=self.embedding_model.embed(analysis["summary"])
        )

        self.episodes.append(episode)
        return episode

    def recall_similar(self, situation: str, k: int = 3) -> List[Episode]:
        """Recall episodes similar to current situation."""
        query_embedding = self.embedding_model.embed(situation)

        scored = []
        for episode in self.episodes:
            similarity = self._cosine_similarity(
                query_embedding,
                episode.embedding
            )
            scored.append((similarity, episode))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:k]]
```

#### 4. Summary Memory (Compressed History)

As conversations grow, compress older history into summaries.

```python
class SummaryMemory:
    """Progressive summarization of conversation history."""

    def __init__(self, llm, summary_interval: int = 10):
        self.llm = llm
        self.summary_interval = summary_interval
        self.summaries: List[str] = []
        self.current_buffer: List[Message] = []

    def add_message(self, message: Message):
        """Add message, summarize if needed."""
        self.current_buffer.append(message)

        if len(self.current_buffer) >= self.summary_interval:
            self._summarize_buffer()

    def _summarize_buffer(self):
        """Summarize current buffer and clear it."""
        conversation = "\n".join([
            f"{m.role}: {m.content}"
            for m in self.current_buffer
        ])

        prompt = f"""Summarize this conversation segment concisely.
Focus on:
- Key information exchanged
- Decisions made
- Action items or tasks
- Important context for future reference

Conversation:
{conversation}

Summary:"""

        summary = self.llm.generate(prompt)
        self.summaries.append(summary)
        self.current_buffer = []

    def get_context(self) -> str:
        """Get full context: summaries + current buffer."""
        context_parts = []

        if self.summaries:
            context_parts.append("Previous conversation summary:")
            context_parts.extend(self.summaries)
            context_parts.append("\nRecent messages:")

        for msg in self.current_buffer:
            context_parts.append(f"{msg.role}: {msg.content}")

        return "\n".join(context_parts)
```

### Combining Memory Systems

The most capable agents combine multiple memory types:

```python
class HybridMemory:
    """Combined memory system for agents."""

    def __init__(self, llm, embedding_model):
        self.short_term = ConversationBuffer(max_messages=20)
        self.long_term = VectorMemory(embedding_model)
        self.episodic = EpisodicMemory(llm, embedding_model)
        self.summary = SummaryMemory(llm, summary_interval=15)

    def add_interaction(self, role: str, content: str):
        """Record an interaction across all memory systems."""
        message = Message(role=role, content=content)

        # Short-term: always add
        self.short_term.add(role, content)

        # Summary: track for periodic summarization
        self.summary.add_message(message)

        # Long-term: store important memories
        if self._is_important(content):
            self.long_term.store(
                content,
                metadata={"role": role}
            )

    def get_relevant_context(self, query: str) -> str:
        """Build context from all memory systems."""
        context_parts = []

        # Summaries of older conversations
        summary_context = self.summary.get_context()
        if summary_context:
            context_parts.append(f"History Summary:\n{summary_context}")

        # Relevant long-term memories
        memories = self.long_term.retrieve(query, k=5)
        if memories:
            memory_text = "\n".join([m.content for m in memories])
            context_parts.append(f"Relevant Memories:\n{memory_text}")

        # Similar past episodes
        episodes = self.episodic.recall_similar(query, k=2)
        if episodes:
            episode_text = "\n".join([
                f"- {ep.title}: {ep.summary}"
                for ep in episodes
            ])
            context_parts.append(f"Similar Past Situations:\n{episode_text}")

        # Recent conversation
        recent = self.short_term.get_context()
        context_parts.append(f"Recent Conversation:\n{recent}")

        return "\n\n".join(context_parts)

    def _is_important(self, content: str) -> bool:
        """Determine if content should go to long-term memory."""
        # Store user messages with personal info or explicit facts
        important_patterns = [
            "my name", "i am", "i work", "i live",
            "remember", "don't forget", "important",
            "always", "never", "prefer"
        ]
        content_lower = content.lower()
        return any(p in content_lower for p in important_patterns)
```

### Did You Know?

The concept of working memory in AI agents was inspired by cognitive psychology. Alan Baddeley's model of human working memory (1974) proposed a "phonological loop" for verbal information, a "visuospatial sketchpad" for visual information, and a "central executive" that coordinates them.

Modern AI agents mirror this: short-term buffers, long-term vector stores, and an LLM "executive" that decides what to remember and retrieve!

---

## Part 2: Planning Algorithms

### Why Agents Need Planning

Without planning, agents operate reactively - responding to each input without considering future steps. This leads to:

- Inefficient tool use (calling the same API repeatedly)
- Incomplete task execution (forgetting steps)
- Poor handling of dependencies (doing things out of order)

Planning transforms agents from reactive responders to proactive problem-solvers.

### Did You Know?

The Plan-and-Execute pattern was popularized by BabyAGI in April 2023 - a 140-line Python script that went viral on Twitter. Created by Yohei Nakajima (a VC!), it used GPT-4 to create a task list, execute tasks, and generate new tasks based on results. Within a week, it had 15,000 GitHub stars and spawned dozens of "autonomous agent" projects.

The key insight: separating planning from execution lets you use different models for each - a larger model for planning, smaller for execution.

### Planning Pattern 1: Plan-and-Execute

Create a plan first, then execute each step.

```
┌──────────────────────────────────────────────────────────────┐
│                    PLAN-AND-EXECUTE FLOW                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   Task   │───▶│  Planner │───▶│   Plan   │              │
│  └──────────┘    └──────────┘    └────┬─────┘              │
│                                       │                     │
│        ┌──────────────────────────────┘                     │
│        ▼                                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Step 1  │───▶│  Step 2  │───▶│  Step 3  │───▶ Result   │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  [Execute]       [Execute]       [Execute]                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

```python
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from enum import Enum

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
    """Agent that plans before executing."""

    def __init__(self, llm, tools: Dict[str, Callable]):
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

For each step, specify:
1. What to do
2. Which tool to use (if any)
3. What input to give the tool

Respond in JSON format:
{{
    "steps": [
        {{
            "description": "Step description",
            "tool": "tool_name or null",
            "tool_input": "input string or null",
            "depends_on": []  // list of step indices this depends on
        }}
    ]
}}"""

        response = self.llm.generate(prompt)
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

    def execute_plan(self, plan: Plan) -> str:
        """Execute a plan step by step."""
        results = []

        for step in plan.steps:
            # Check dependencies
            for dep_id in step.depends_on:
                dep_step = plan.steps[dep_id]
                if dep_step.status != StepStatus.COMPLETED:
                    step.status = StepStatus.FAILED
                    step.result = f"Dependency {dep_id} not completed"
                    continue

            step.status = StepStatus.IN_PROGRESS
            print(f"Executing: {step.description}")

            try:
                if step.tool and step.tool in self.tools:
                    # Execute tool
                    result = self.tools[step.tool](step.tool_input)
                else:
                    # Use LLM for reasoning step
                    result = self.llm.generate(
                        f"Complete this step: {step.description}\n"
                        f"Context from previous steps: {results}"
                    )

                step.result = result
                step.status = StepStatus.COMPLETED
                results.append(f"Step {step.step_id}: {result}")

            except Exception as e:
                step.status = StepStatus.FAILED
                step.result = str(e)
                results.append(f"Step {step.step_id} failed: {e}")

        # Summarize results
        return self._summarize_execution(plan, results)

    def _summarize_execution(self, plan: Plan, results: List[str]) -> str:
        """Summarize the execution results."""
        prompt = f"""Summarize the results of executing this plan.

Original goal: {plan.goal}

Execution results:
{chr(10).join(results)}

Provide a concise summary of what was accomplished and any issues."""

        return self.llm.generate(prompt)

    def run(self, task: str) -> str:
        """Plan and execute a task."""
        print(f"Creating plan for: {task}")
        plan = self.create_plan(task)

        print(f"Plan created with {len(plan.steps)} steps:")
        for step in plan.steps:
            print(f"  {step.step_id}. {step.description}")

        print("\nExecuting plan...")
        result = self.execute_plan(plan)

        return result
```

### Planning Pattern 2: ReWOO (Reason Without Observation)

Traditional ReAct interleaves reasoning and observation. ReWOO separates them:
1. **Plan all tool calls upfront** (without seeing results)
2. **Execute all tools**
3. **Solve using all results**

This reduces LLM calls dramatically!

```
┌────────────────────────────────────────────────────────────────┐
│                         ReWOO PATTERN                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Traditional ReAct (5 LLM calls):                              │
│  Think → Act → Observe → Think → Act → Observe → Think → ...   │
│                                                                │
│  ReWOO (2 LLM calls):                                          │
│  Plan [Tool1, Tool2, Tool3] → Execute All → Solve              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

```python
@dataclass
class ReWOOPlan:
    """A ReWOO-style plan with evidence variables."""
    steps: List[Dict[str, str]]  # {plan, tool, input, evidence_var}

class ReWOOAgent:
    """ReWOO: Reason Without Observation.

    Plans all tool calls upfront, executes them,
    then solves using all evidence.
    """

    def __init__(self, llm, tools: Dict[str, Callable]):
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

Create a plan where each step has:
- Plan: What to do and why
- Tool: Which tool to use
- Input: Input for the tool (can reference #E[n])
- Evidence: #E[n] where n is step number

Example format:
Step 1:
Plan: Search for information about X
Tool: web_search
Input: "query about X"
Evidence: #E1

Step 2:
Plan: Analyze the search results from #E1
Tool: analyze
Input: #E1
Evidence: #E2

Create your plan:"""

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
                tool_input = tool_input.replace(var, value)

            # Execute tool
            if tool_name and tool_name in self.tools:
                try:
                    result = self.tools[tool_name](tool_input)
                    evidence[evidence_var] = str(result)
                except Exception as e:
                    evidence[evidence_var] = f"Error: {e}"
            else:
                evidence[evidence_var] = f"Unknown tool: {tool_name}"

        return evidence

    def solve(self, task: str, plan: ReWOOPlan, evidence: Dict[str, str]) -> str:
        """Solve the task using collected evidence."""
        plan_text = "\n".join([
            f"Step {i}: {s['plan']}"
            for i, s in enumerate(plan.steps, 1)
        ])

        evidence_text = "\n".join([
            f"{var}: {value[:500]}..."  # Truncate long evidence
            for var, value in evidence.items()
        ])

        prompt = f"""Solve this task using the evidence collected.

Task: {task}

Plan executed:
{plan_text}

Evidence collected:
{evidence_text}

Based on this evidence, provide your final answer:"""

        return self.llm.generate(prompt)

    def run(self, task: str) -> str:
        """Full ReWOO execution: Plan → Execute → Solve."""
        print("Planning...")
        plan = self.plan(task)

        print(f"Executing {len(plan.steps)} tool calls...")
        evidence = self.execute(plan)

        print("Solving...")
        result = self.solve(task, plan, evidence)

        return result
```

### Planning Pattern 3: Tree of Thought (ToT)

Explore multiple reasoning paths, evaluate each, and select the best.

```
┌───────────────────────────────────────────────────────────────────┐
│                      TREE OF THOUGHT                              │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│                        [Problem]                                  │
│                            │                                      │
│              ┌─────────────┼─────────────┐                        │
│              ▼             ▼             ▼                        │
│         [Path A]      [Path B]      [Path C]                      │
│         score:0.7     score:0.9     score:0.4                     │
│              │             │             │                        │
│              │      ┌──────┴──────┐      X (pruned)               │
│              │      ▼             ▼                               │
│              │  [Path B1]    [Path B2]                            │
│              │  score:0.95   score:0.85                           │
│              │      │                                             │
│              │      ▼                                             │
│              │  [Solution] ← SELECTED                             │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

```python
from dataclasses import dataclass, field
from typing import List, Optional
import heapq

@dataclass
class ThoughtNode:
    """A node in the thought tree."""
    thought: str
    score: float
    parent: Optional['ThoughtNode'] = None
    children: List['ThoughtNode'] = field(default_factory=list)
    depth: int = 0

    def __lt__(self, other):
        # For heap comparison (higher score = better)
        return self.score > other.score

class TreeOfThoughtAgent:
    """Explores multiple reasoning paths."""

    def __init__(self, llm, branching_factor: int = 3, max_depth: int = 3):
        self.llm = llm
        self.branching_factor = branching_factor
        self.max_depth = max_depth

    def generate_thoughts(self, problem: str, current_path: List[str]) -> List[str]:
        """Generate possible next thoughts."""
        path_text = " → ".join(current_path) if current_path else "Starting fresh"

        prompt = f"""Problem: {problem}

Current reasoning path: {path_text}

Generate {self.branching_factor} different next steps or approaches.
Each should be a distinct way to continue solving this problem.
Be creative and consider different angles.

Format each as a separate paragraph."""

        response = self.llm.generate(prompt)

        # Split into separate thoughts
        thoughts = [t.strip() for t in response.split("\n\n") if t.strip()]
        return thoughts[:self.branching_factor]

    def evaluate_thought(self, problem: str, path: List[str]) -> float:
        """Score how promising a thought path is (0-1)."""
        path_text = " → ".join(path)

        prompt = f"""Problem: {problem}

Reasoning path so far: {path_text}

Rate this reasoning path on a scale of 0-10:
- 10: Excellent progress toward solution
- 7-9: Good progress, promising direction
- 4-6: Some progress, but uncertain
- 1-3: Poor direction, likely wrong
- 0: Dead end

Consider:
1. Does this make logical sense?
2. Is it making progress toward the goal?
3. Are there any errors or contradictions?

Respond with just a number (0-10):"""

        response = self.llm.generate(prompt)
        try:
            score = float(response.strip()) / 10.0
            return min(max(score, 0.0), 1.0)
        except:
            return 0.5

    def solve(self, problem: str) -> str:
        """Solve using tree of thought exploration."""
        # Initialize with root node
        root = ThoughtNode(thought="Start", score=1.0, depth=0)

        # Priority queue for best-first search
        frontier = [root]
        best_path = []
        best_score = 0.0

        while frontier:
            current = heapq.heappop(frontier)

            # Build current path
            path = []
            node = current
            while node.parent:
                path.append(node.thought)
                node = node.parent
            path.reverse()

            # Check if we've reached max depth
            if current.depth >= self.max_depth:
                if current.score > best_score:
                    best_score = current.score
                    best_path = path
                continue

            # Generate and evaluate children
            thoughts = self.generate_thoughts(problem, path)

            for thought in thoughts:
                child_path = path + [thought]
                score = self.evaluate_thought(problem, child_path)

                child = ThoughtNode(
                    thought=thought,
                    score=score,
                    parent=current,
                    depth=current.depth + 1
                )
                current.children.append(child)

                # Only explore promising paths
                if score > 0.3:
                    heapq.heappush(frontier, child)

                # Track best
                if score > best_score:
                    best_score = score
                    best_path = child_path

        # Generate final answer from best path
        return self._synthesize_answer(problem, best_path)

    def _synthesize_answer(self, problem: str, path: List[str]) -> str:
        """Synthesize final answer from the best reasoning path."""
        path_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(path)])

        prompt = f"""Problem: {problem}

Best reasoning path found:
{path_text}

Based on this reasoning, provide the final answer:"""

        return self.llm.generate(prompt)
```

### Did You Know?

The Tree of Thoughts paper (Yao et al., 2023) showed that GPT-4 with ToT solved 74% of "Game of 24" puzzles (make 24 from 4 numbers), compared to just 4% with standard prompting! The key was allowing the model to explore multiple paths and backtrack from dead ends - something humans do naturally but standard LLM prompting prevents.

---

## Part 3: Multi-Agent Architectures

### Why Multiple Agents?

Single agents have limitations:
- **Context limits**: One agent can't hold all relevant information
- **Specialization**: Different tasks need different "personalities"
- **Verification**: Self-checking is less effective than peer review
- **Parallelism**: Some tasks can be done simultaneously

### Did You Know?

In 2023, researchers at Microsoft Research created AutoGen, where agents could automatically create other agents! In one experiment, an "AgentBuilder" agent created specialized agents for different subtasks, assembled them into a team, and coordinated their work - all autonomously.

The paper noted that multi-agent debate improved factual accuracy by 15-20% over single-agent responses, because agents caught each other's mistakes.

### Architecture 1: Supervisor Pattern

One agent manages a team of specialized workers.

```
┌───────────────────────────────────────────────────────────────────┐
│                      SUPERVISOR PATTERN                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│                      ┌──────────────┐                             │
│                      │  SUPERVISOR  │                             │
│                      │  (Manager)   │                             │
│                      └──────┬───────┘                             │
│                             │                                     │
│           ┌─────────────────┼─────────────────┐                   │
│           │                 │                 │                   │
│           ▼                 ▼                 ▼                   │
│    ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│    │ RESEARCHER │   │   WRITER   │   │   CRITIC   │              │
│    │  (Worker)  │   │  (Worker)  │   │  (Worker)  │              │
│    └────────────┘   └────────────┘   └────────────┘              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

class AgentRole(Enum):
    SUPERVISOR = "supervisor"
    RESEARCHER = "researcher"
    WRITER = "writer"
    CRITIC = "critic"
    CODER = "coder"

@dataclass
class AgentMessage:
    """Message between agents."""
    sender: str
    recipient: str
    content: str
    message_type: str = "task"  # task, result, feedback

@dataclass
class WorkerAgent:
    """A specialized worker agent."""
    name: str
    role: AgentRole
    system_prompt: str
    llm: Any
    tools: Dict[str, Callable] = field(default_factory=dict)

    def process(self, task: str, context: str = "") -> str:
        """Process a task and return result."""
        prompt = f"""{self.system_prompt}

Context: {context}

Task: {task}

Your response:"""

        return self.llm.generate(prompt)

class SupervisorAgent:
    """Supervisor that coordinates worker agents."""

    def __init__(self, llm, workers: List[WorkerAgent]):
        self.llm = llm
        self.workers = {w.name: w for w in workers}
        self.message_history: List[AgentMessage] = []

    def delegate(self, task: str) -> str:
        """Delegate a task to appropriate workers."""
        # Determine which workers to use
        worker_descriptions = "\n".join([
            f"- {name} ({w.role.value}): {w.system_prompt[:100]}..."
            for name, w in self.workers.items()
        ])

        planning_prompt = f"""You are a supervisor coordinating a team.

Available workers:
{worker_descriptions}

Task to complete: {task}

Create a plan specifying:
1. Which workers to use (in order)
2. What task to give each worker
3. How to combine their outputs

Respond in JSON:
{{
    "plan": [
        {{"worker": "worker_name", "task": "specific task"}},
        ...
    ],
    "synthesis_instructions": "how to combine outputs"
}}"""

        response = self.llm.generate(planning_prompt)
        plan = json.loads(response)

        # Execute the plan
        results = {}
        context = f"Original task: {task}\n\n"

        for step in plan["plan"]:
            worker_name = step["worker"]
            worker_task = step["task"]

            if worker_name not in self.workers:
                continue

            worker = self.workers[worker_name]

            # Include previous results as context
            if results:
                context += "Previous results:\n"
                for name, result in results.items():
                    context += f"{name}: {result[:500]}...\n"

            # Get worker's output
            result = worker.process(worker_task, context)
            results[worker_name] = result

            # Track message
            self.message_history.append(AgentMessage(
                sender="supervisor",
                recipient=worker_name,
                content=worker_task,
                message_type="task"
            ))
            self.message_history.append(AgentMessage(
                sender=worker_name,
                recipient="supervisor",
                content=result,
                message_type="result"
            ))

        # Synthesize final output
        synthesis_prompt = f"""Synthesize these worker outputs into a final response.

Instructions: {plan["synthesis_instructions"]}

Worker outputs:
{json.dumps(results, indent=2)}

Final synthesized response:"""

        return self.llm.generate(synthesis_prompt)

# Example usage
def create_content_team(llm) -> SupervisorAgent:
    """Create a content creation team."""
    workers = [
        WorkerAgent(
            name="researcher",
            role=AgentRole.RESEARCHER,
            system_prompt="""You are a thorough researcher.
            Find relevant facts, statistics, and examples.
            Always cite your sources.""",
            llm=llm
        ),
        WorkerAgent(
            name="writer",
            role=AgentRole.WRITER,
            system_prompt="""You are a skilled writer.
            Transform research into engaging, clear content.
            Use vivid examples and clear explanations.""",
            llm=llm
        ),
        WorkerAgent(
            name="critic",
            role=AgentRole.CRITIC,
            system_prompt="""You are a critical reviewer.
            Check for errors, unclear explanations, and missing information.
            Suggest specific improvements.""",
            llm=llm
        )
    ]

    return SupervisorAgent(llm, workers)
```

### Architecture 2: Peer-to-Peer (Swarm)

Agents collaborate as equals, passing work between each other.

```
┌───────────────────────────────────────────────────────────────────┐
│                       SWARM PATTERN                               │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│         ┌────────────┐          ┌────────────┐                   │
│         │  Agent A   │◄────────▶│  Agent B   │                   │
│         └─────┬──────┘          └──────┬─────┘                   │
│               │                        │                          │
│               │    ┌────────────┐      │                          │
│               └───▶│  Agent C   │◄─────┘                          │
│                    └────────────┘                                 │
│                                                                   │
│  Each agent can hand off to any other agent based on the task.   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

```python
@dataclass
class SwarmAgent:
    """An agent in a swarm that can hand off to others."""
    name: str
    role: str
    description: str
    system_prompt: str
    llm: Any

    def should_handle(self, task: str) -> float:
        """Return confidence (0-1) that this agent should handle the task."""
        prompt = f"""You are {self.name}, a {self.role}.
Your specialty: {self.description}

Task: {task}

On a scale of 0-10, how well-suited are you to handle this task?
Consider your expertise and the task requirements.
Respond with just a number."""

        response = self.llm.generate(prompt)
        try:
            return float(response.strip()) / 10.0
        except:
            return 0.5

    def process(self, task: str, context: str = "") -> tuple[str, Optional[str]]:
        """Process task. Returns (response, handoff_to) or (response, None)."""
        prompt = f"""{self.system_prompt}

Context: {context}

Task: {task}

Complete this task. If you need to hand off part of the work to a
specialist, end your response with "HANDOFF: [specialist_type]"

Your response:"""

        response = self.llm.generate(prompt)

        # Check for handoff
        if "HANDOFF:" in response:
            parts = response.split("HANDOFF:")
            result = parts[0].strip()
            handoff = parts[1].strip()
            return result, handoff

        return response, None

class SwarmCoordinator:
    """Coordinates a swarm of peer agents."""

    def __init__(self, agents: List[SwarmAgent], max_handoffs: int = 5):
        self.agents = {a.name: a for a in agents}
        self.max_handoffs = max_handoffs

    def find_best_agent(self, task: str, exclude: List[str] = None) -> SwarmAgent:
        """Find the best agent for a task."""
        exclude = exclude or []
        candidates = [a for a in self.agents.values() if a.name not in exclude]

        if not candidates:
            # Return any agent if all excluded
            return list(self.agents.values())[0]

        scores = [(a.should_handle(task), a) for a in candidates]
        scores.sort(key=lambda x: x[0], reverse=True)

        return scores[0][1]

    def run(self, task: str) -> str:
        """Run the swarm to complete a task."""
        context = f"Original task: {task}\n\n"
        results = []
        handoffs = 0
        excluded = []

        current_task = task

        while handoffs < self.max_handoffs:
            # Find best agent
            agent = self.find_best_agent(current_task, excluded)

            print(f"Agent '{agent.name}' handling task...")

            # Process
            result, handoff = agent.process(current_task, context)
            results.append(f"{agent.name}: {result}")
            context += f"{agent.name}'s work:\n{result}\n\n"

            if handoff:
                # Find agent matching handoff description
                current_task = f"Continue from {agent.name}'s work: {handoff}"
                excluded.append(agent.name)
                handoffs += 1
            else:
                break

        # Combine results
        return "\n\n---\n\n".join(results)
```

### Architecture 3: Hierarchical Teams

Nested teams with supervisors at each level.

```
┌───────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL PATTERN                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│                    ┌──────────────┐                               │
│                    │   EXECUTIVE  │                               │
│                    │  (Top-level) │                               │
│                    └──────┬───────┘                               │
│                           │                                       │
│            ┌──────────────┼──────────────┐                        │
│            ▼              ▼              ▼                        │
│     ┌────────────┐ ┌────────────┐ ┌────────────┐                 │
│     │  RESEARCH  │ │  WRITING   │ │    QA      │                 │
│     │   LEAD     │ │   LEAD     │ │   LEAD     │                 │
│     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘                 │
│           │              │              │                         │
│      ┌────┼────┐    ┌────┼────┐    ┌────┼────┐                   │
│      ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼                   │
│     [W1] [W2] [W3] [W4] [W5] [W6] [W7] [W8] [W9]                 │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Architecture 4: Debate

Agents argue different positions to find the truth.

```python
@dataclass
class DebateAgent:
    """An agent that argues a position."""
    name: str
    position: str  # "for" or "against" or "neutral"
    llm: Any

    def make_argument(self, topic: str, opponent_args: List[str] = None) -> str:
        """Make an argument for the position."""
        opponent_text = ""
        if opponent_args:
            opponent_text = f"\n\nOpponent's arguments:\n" + "\n".join(opponent_args)

        prompt = f"""You are arguing {self.position} the following topic.

Topic: {topic}
{opponent_text}

Make your strongest argument. Be persuasive and use evidence.
If responding to opponent's arguments, address their points directly."""

        return self.llm.generate(prompt)

class DebateArena:
    """Facilitates debates between agents."""

    def __init__(self, llm, rounds: int = 3):
        self.llm = llm
        self.rounds = rounds

    def debate(self, topic: str) -> str:
        """Run a debate on a topic."""
        for_agent = DebateAgent("Proponent", "FOR", self.llm)
        against_agent = DebateAgent("Opponent", "AGAINST", self.llm)

        for_args = []
        against_args = []

        for round_num in range(self.rounds):
            print(f"\n=== Round {round_num + 1} ===")

            # For side argues
            for_arg = for_agent.make_argument(topic, against_args)
            for_args.append(for_arg)
            print(f"\nFOR: {for_arg[:200]}...")

            # Against side responds
            against_arg = against_agent.make_argument(topic, for_args)
            against_args.append(against_arg)
            print(f"\nAGAINST: {against_arg[:200]}...")

        # Judge decides
        return self._judge(topic, for_args, against_args)

    def _judge(self, topic: str, for_args: List[str], against_args: List[str]) -> str:
        """Neutral judge evaluates the debate."""
        prompt = f"""You are a neutral judge evaluating this debate.

Topic: {topic}

Arguments FOR:
{chr(10).join(for_args)}

Arguments AGAINST:
{chr(10).join(against_args)}

Evaluate the debate and provide:
1. The stronger arguments from each side
2. Weaknesses in each side's reasoning
3. Your balanced conclusion on the topic
4. What additional information would help resolve this

Your verdict:"""

        return self.llm.generate(prompt)
```

### Did You Know?

Google DeepMind's Gemini team found that using three agents to verify each other's work reduced hallucinations by 40%! The pattern: one agent generates, second agent critiques, third agent synthesizes. They called it "Constitutional AI meets Multi-Agent Debate."

---

## Part 4: Self-Improvement Patterns

### Reflection: Agents That Evaluate Themselves

```python
class ReflectiveAgent:
    """Agent that reflects on and improves its own outputs."""

    def __init__(self, llm, max_iterations: int = 3):
        self.llm = llm
        self.max_iterations = max_iterations

    def generate_with_reflection(self, task: str) -> str:
        """Generate output with self-reflection loop."""

        # Initial generation
        output = self._generate(task)

        for i in range(self.max_iterations):
            # Reflect on output
            critique = self._reflect(task, output)

            # Check if good enough
            if self._is_satisfactory(critique):
                print(f"Satisfied after {i+1} iterations")
                break

            # Improve based on reflection
            output = self._improve(task, output, critique)

        return output

    def _generate(self, task: str) -> str:
        """Generate initial output."""
        return self.llm.generate(f"Complete this task:\n{task}")

    def _reflect(self, task: str, output: str) -> str:
        """Reflect on the output quality."""
        prompt = f"""Critically evaluate this output for the given task.

Task: {task}

Output:
{output}

Provide specific feedback on:
1. Correctness: Are there any errors or mistakes?
2. Completeness: Is anything missing?
3. Clarity: Is it clear and well-organized?
4. Quality: How could it be improved?

Be specific and constructive:"""

        return self.llm.generate(prompt)

    def _is_satisfactory(self, critique: str) -> bool:
        """Determine if the output is good enough."""
        prompt = f"""Based on this critique, is the output satisfactory?

Critique:
{critique}

Answer YES if the output is good enough with only minor issues.
Answer NO if there are significant problems that need fixing.

Answer (YES/NO):"""

        response = self.llm.generate(prompt)
        return "YES" in response.upper()

    def _improve(self, task: str, output: str, critique: str) -> str:
        """Improve output based on reflection."""
        prompt = f"""Improve this output based on the critique.

Original task: {task}

Current output:
{output}

Critique:
{critique}

Provide an improved version that addresses the critique:"""

        return self.llm.generate(prompt)
```

### Self-Correction: Fixing Mistakes Iteratively

```python
class SelfCorrectingAgent:
    """Agent that detects and corrects its own mistakes."""

    def __init__(self, llm, tools: Dict[str, Callable]):
        self.llm = llm
        self.tools = tools

    def execute_with_verification(self, task: str) -> str:
        """Execute task with self-verification."""

        # Generate solution
        solution = self._solve(task)

        # Verify the solution
        verification = self._verify(task, solution)

        if verification["is_correct"]:
            return solution

        # Self-correct based on errors found
        corrected = self._correct(task, solution, verification["errors"])

        # Verify again (could loop, but limiting to one correction)
        return corrected

    def _solve(self, task: str) -> str:
        """Generate a solution."""
        return self.llm.generate(f"Solve this task:\n{task}")

    def _verify(self, task: str, solution: str) -> dict:
        """Verify the solution for errors."""
        prompt = f"""Verify this solution for correctness.

Task: {task}

Solution:
{solution}

Check for:
1. Logical errors
2. Factual mistakes
3. Missing steps
4. Inconsistencies

Respond in JSON:
{{
    "is_correct": true/false,
    "errors": ["error1", "error2", ...],
    "confidence": 0.0-1.0
}}"""

        response = self.llm.generate(prompt)
        return json.loads(response)

    def _correct(self, task: str, solution: str, errors: List[str]) -> str:
        """Correct the solution based on identified errors."""
        prompt = f"""Fix these errors in the solution.

Task: {task}

Current solution:
{solution}

Errors to fix:
{chr(10).join(f"- {e}" for e in errors)}

Provide a corrected solution:"""

        return self.llm.generate(prompt)
```

### Tool Creation: Agents That Build Tools

The most advanced pattern: agents that create new tools when needed!

```python
class ToolCreatingAgent:
    """Agent that can create new tools."""

    def __init__(self, llm):
        self.llm = llm
        self.tools: Dict[str, Callable] = {}
        self.tool_code: Dict[str, str] = {}

    def needs_new_tool(self, task: str) -> tuple[bool, str]:
        """Determine if a new tool is needed."""
        tools_desc = "\n".join([
            f"- {name}: {func.__doc__}"
            for name, func in self.tools.items()
        ]) or "No tools available"

        prompt = f"""Do you need a new tool to complete this task?

Task: {task}

Available tools:
{tools_desc}

If existing tools are sufficient, respond: NO

If a new tool is needed, respond:
YES: [description of tool needed]"""

        response = self.llm.generate(prompt)

        if response.startswith("YES:"):
            return True, response[4:].strip()
        return False, ""

    def create_tool(self, description: str) -> str:
        """Create a new tool based on description."""
        prompt = f"""Create a Python function for this tool.

Tool description: {description}

Requirements:
1. Single function with clear docstring
2. Use only standard library
3. Handle errors gracefully
4. Return a string result

```python
def tool_name(input_str: str) -> str:
    '''Tool description'''
    # Implementation
    return result
```

Provide the function code:"""

        response = self.llm.generate(prompt)

        # Extract code from response
        code = self._extract_code(response)

        # Safely execute to define the function
        tool_name = self._execute_and_register(code)

        return tool_name

    def _extract_code(self, response: str) -> str:
        """Extract Python code from response."""
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        return response.strip()

    def _execute_and_register(self, code: str) -> str:
        """Execute code and register the tool."""
        # Create a restricted namespace
        namespace = {"__builtins__": __builtins__}

        try:
            exec(code, namespace)

            # Find the function that was defined
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("_"):
                    self.tools[name] = obj
                    self.tool_code[name] = code
                    return name
        except Exception as e:
            print(f"Error creating tool: {e}")

        return ""

    def run(self, task: str) -> str:
        """Run task, creating tools if needed."""
        # Check if new tool needed
        needs_tool, tool_desc = self.needs_new_tool(task)

        if needs_tool:
            print(f"Creating new tool: {tool_desc}")
            tool_name = self.create_tool(tool_desc)
            if tool_name:
                print(f"Created tool: {tool_name}")

        # Now solve the task with available tools
        tools_desc = "\n".join([
            f"- {name}: {func.__doc__}"
            for name, func in self.tools.items()
        ])

        prompt = f"""Solve this task using available tools.

Task: {task}

Available tools:
{tools_desc}

To use a tool, write: USE_TOOL(tool_name, "input")

Your solution:"""

        response = self.llm.generate(prompt)

        # Execute any tool calls
        return self._execute_tool_calls(response)

    def _execute_tool_calls(self, response: str) -> str:
        """Execute tool calls in the response."""
        import re

        pattern = r'USE_TOOL\((\w+),\s*"([^"]*)"\)'

        def replace_call(match):
            tool_name = match.group(1)
            tool_input = match.group(2)

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](tool_input)
                    return f"[{tool_name} result: {result}]"
                except Exception as e:
                    return f"[{tool_name} error: {e}]"
            return f"[Unknown tool: {tool_name}]"

        return re.sub(pattern, replace_call, response)
```

### Did You Know?

In early 2024, researchers demonstrated "Voyager" - a Minecraft agent that could write its own skill code! When it needed to mine diamonds but didn't know how, it:
1. Explored the world to understand the problem
2. Wrote Python code for a mining skill
3. Tested the skill and debugged failures
4. Saved the skill to a library for future use

By the end, Voyager had created a library of 70+ reusable skills, all self-written!

---

## Part 5: Putting It All Together

### The Complete Autonomous Agent

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import json

@dataclass
class AutonomousAgentConfig:
    """Configuration for the autonomous agent."""
    max_iterations: int = 10
    enable_reflection: bool = True
    enable_tool_creation: bool = False
    memory_type: str = "hybrid"  # simple, vector, hybrid

class AutonomousAgent:
    """
    A complete autonomous agent with:
    - Hybrid memory (short-term, long-term, episodic)
    - Planning (Plan-and-Execute)
    - Self-reflection and correction
    - Tool creation (optional)
    """

    def __init__(
        self,
        llm,
        embedding_model,
        tools: Dict[str, Callable] = None,
        config: AutonomousAgentConfig = None
    ):
        self.llm = llm
        self.embedding_model = embedding_model
        self.tools = tools or {}
        self.config = config or AutonomousAgentConfig()

        # Initialize memory
        self.memory = HybridMemory(llm, embedding_model)

        # Initialize sub-systems
        self.planner = PlanAndExecuteAgent(llm, self.tools)
        self.reflector = ReflectiveAgent(llm) if config.enable_reflection else None
        self.tool_creator = ToolCreatingAgent(llm) if config.enable_tool_creation else None

    def run(self, task: str) -> str:
        """Run the agent on a task."""
        print(f"\n{'='*60}")
        print(f"TASK: {task}")
        print(f"{'='*60}\n")

        # Step 1: Retrieve relevant context from memory
        context = self.memory.get_relevant_context(task)
        print(f"Retrieved {len(context)} characters of context")

        # Step 2: Check if we need new tools
        if self.tool_creator:
            needs_tool, tool_desc = self.tool_creator.needs_new_tool(task)
            if needs_tool:
                print(f"Creating new tool: {tool_desc}")
                tool_name = self.tool_creator.create_tool(tool_desc)
                if tool_name:
                    self.tools[tool_name] = self.tool_creator.tools[tool_name]

        # Step 3: Create and execute plan
        print("\nCreating plan...")
        plan = self.planner.create_plan(f"{context}\n\nTask: {task}")

        print(f"Plan has {len(plan.steps)} steps:")
        for step in plan.steps:
            print(f"  - {step.description}")

        print("\nExecuting plan...")
        result = self.planner.execute_plan(plan)

        # Step 4: Self-reflect and improve if enabled
        if self.reflector:
            print("\nReflecting on output...")
            result = self.reflector.generate_with_reflection(
                f"Task: {task}\n\nInitial result: {result}"
            )

        # Step 5: Store interaction in memory
        self.memory.add_interaction("user", task)
        self.memory.add_interaction("assistant", result)

        print(f"\n{'='*60}")
        print("COMPLETED")
        print(f"{'='*60}\n")

        return result

    def chat(self, message: str) -> str:
        """Chat interface for interactive use."""
        # Add to memory
        self.memory.add_interaction("user", message)

        # Get context
        context = self.memory.get_relevant_context(message)

        # Generate response
        prompt = f"""You are a helpful assistant with memory and planning capabilities.

{context}

User: {message}
Assistant:"""

        response = self.llm.generate(prompt)

        # Store response
        self.memory.add_interaction("assistant", response)

        return response
```

---

## Common Pitfalls

### 1. Memory Overload
**Problem**: Storing too much in memory leads to slow retrieval and irrelevant context.
**Solution**: Use importance scoring, TTL (time-to-live), and periodic cleanup.

### 2. Planning Paralysis
**Problem**: Agent spends too long planning, never executing.
**Solution**: Set max planning time, use simpler plans for simple tasks.

### 3. Infinite Reflection Loops
**Problem**: Agent keeps finding issues and never stops improving.
**Solution**: Set max iterations, use confidence thresholds.

### 4. Tool Explosion
**Problem**: Agent creates too many tools, many redundant.
**Solution**: Check for similar tools before creating, implement tool cleanup.

### 5. Context Window Exhaustion
**Problem**: Memory + plan + conversation exceeds context limit.
**Solution**: Aggressive summarization, hierarchical context loading.

---

## Best Practices

### Memory Design
1. **Start simple**: Begin with conversation buffer, add complexity as needed
2. **Importance scoring**: Not all information deserves long-term storage
3. **Periodic consolidation**: Merge similar memories, summarize old ones
4. **Test retrieval**: Ensure the right memories come back for queries

### Planning
1. **Match complexity**: Simple tasks don't need Tree of Thought
2. **Monitor execution**: Track which plans succeed/fail
3. **Allow replanning**: Plans should be flexible, not rigid
4. **Limit depth**: Deep plans are often unnecessary

### Multi-Agent
1. **Clear roles**: Each agent should have a distinct specialty
2. **Explicit handoffs**: Make agent transitions clear
3. **Prevent loops**: Limit how many times agents can pass work
4. **Log everything**: Track all inter-agent communication

### Self-Improvement
1. **Set limits**: Max iterations, max corrections
2. **Quality metrics**: Define what "good enough" means
3. **Save learnings**: Store successful patterns for reuse
4. **Human oversight**: Critical decisions should involve humans

---

## Further Reading

### Papers
1. **Generative Agents** (Stanford, 2023) - Memory architecture for AI characters
2. **Tree of Thoughts** (Yao et al., 2023) - Deliberate reasoning
3. **ReWOO** (Xu et al., 2023) - Efficient planning
4. **AutoGen** (Microsoft, 2023) - Multi-agent conversations
5. **Voyager** (NVIDIA, 2023) - Self-improving Minecraft agent

### Documentation
- LangGraph: https://langchain-ai.github.io/langgraph/
- AutoGen: https://microsoft.github.io/autogen/
- CrewAI: https://docs.crewai.com/

### Tutorials
- Building agents with memory: LangChain docs
- Multi-agent patterns: AutoGen examples
- Planning algorithms: LangGraph tutorials

---

## Exercises

### Exercise 1: Build a Memory System
Create a hybrid memory system that:
1. Stores conversation in short-term buffer
2. Extracts facts to long-term memory
3. Summarizes old conversations
4. Retrieves relevant context

### Exercise 2: Implement Plan-and-Execute
Build an agent that:
1. Takes a complex task
2. Creates a multi-step plan
3. Executes each step with tools
4. Handles failures gracefully

### Exercise 3: Create a Multi-Agent Team
Design a team of 3 agents:
1. Researcher (finds information)
2. Writer (creates content)
3. Critic (reviews and improves)

### Exercise 4: Add Self-Reflection
Extend an agent with:
1. Output evaluation
2. Iterative improvement
3. Quality thresholds
4. Maximum iterations

---

## Deliverables

- [ ] **Agent Memory Demo**: Working hybrid memory system
- [ ] **Planning Agent**: Plan-and-execute implementation
- [ ] **Multi-Agent Team**: Supervisor + workers pattern
- [ ] **Autonomous Agent Framework**: Complete agent with all features

**Success Criteria**:
- Memory correctly retrieves relevant context
- Plans execute successfully
- Multi-agent collaboration produces better output than single agent
- Self-reflection improves output quality

---

## Next Steps

Move on to **Module 21: AI Agents in Production** to learn:
- Deploying agents to production
- Safety guardrails
- Monitoring and observability
- Cost control
- Failure handling

---

**You've discovered the Heureka Moment: Agents with memory and planning can solve problems they couldn't before!**

This is the foundation for building truly autonomous AI systems. In Module 21, you'll learn how to deploy these agents safely and reliably.

---

_Last updated: 2025-11-25_
_Status: Complete_
_Module 20: Advanced Agentic AI_
