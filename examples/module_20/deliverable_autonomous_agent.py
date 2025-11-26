#!/usr/bin/env python3
"""
Module 20 Deliverable: Autonomous Agent Framework

A comprehensive framework demonstrating advanced agentic AI patterns including:
- Multi-tier memory systems (short-term, long-term, episodic, summary)
- Planning algorithms (Plan-and-Execute, ReWOO, Tree of Thought)
- Multi-agent collaboration (Supervisor, Swarm, Debate)
- Self-improvement through reflection and learning

This framework can operate with or without actual LLM APIs, using intelligent
simulation for demonstration purposes.

Usage:
    python deliverable_autonomous_agent.py demo1  # Research Agent demo
    python deliverable_autonomous_agent.py demo2  # Problem Solver demo
    python deliverable_autonomous_agent.py demo3  # Multi-Agent Team demo
    python deliverable_autonomous_agent.py demo4  # Self-Improving Agent demo
    python deliverable_autonomous_agent.py help   # Show help

Author: Neural Dojo
"""

import json
import hashlib
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import math
import re
from collections import Counter


# =============================================================================
# STORAGE AND CONFIGURATION
# =============================================================================

STORAGE_DIR = ".autonomous_agent"


def ensure_storage_dir():
    """Create storage directory if it doesn't exist."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)


def save_json(filename: str, data: Any) -> None:
    """Save data to JSON file."""
    ensure_storage_dir()
    filepath = os.path.join(STORAGE_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filename: str) -> Optional[Any]:
    """Load data from JSON file."""
    filepath = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


# =============================================================================
# ENUMS AND TYPES
# =============================================================================

class AgentRole(Enum):
    """Roles agents can take in multi-agent systems."""
    SUPERVISOR = "supervisor"
    WORKER = "worker"
    CRITIC = "critic"
    RESEARCHER = "researcher"
    PLANNER = "planner"
    EXECUTOR = "executor"


class MemoryType(Enum):
    """Types of memory in the agent system."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class PlanningStrategy(Enum):
    """Planning strategies available."""
    PLAN_AND_EXECUTE = "plan_and_execute"
    REWOO = "rewoo"
    TREE_OF_THOUGHT = "tree_of_thought"
    REFLEXION = "reflexion"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Memory:
    """A single memory entry."""
    content: str
    memory_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5
    access_count: int = 0
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Memory":
        return cls(**data)


@dataclass
class PlanStep:
    """A step in a plan."""
    step_id: int
    description: str
    dependencies: List[int] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    evidence: List[str] = field(default_factory=list)


@dataclass
class Plan:
    """A complete plan for a task."""
    goal: str
    steps: List[PlanStep]
    strategy: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    recipient: str
    content: str
    message_type: str = "task"  # task, result, feedback, query
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Reflection:
    """Self-reflection record."""
    task: str
    outcome: str
    success: bool
    lessons_learned: List[str]
    improvements: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentState:
    """Complete state of an agent."""
    name: str
    role: str
    goals: List[str]
    current_task: Optional[str] = None
    plan: Optional[Plan] = None
    memories: List[Memory] = field(default_factory=list)
    reflections: List[Reflection] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


# =============================================================================
# EMBEDDING MODEL (Simulated for API-free operation)
# =============================================================================

class SimpleEmbeddingModel:
    """Word-frequency based embedding model for demonstration."""

    def __init__(self, dim: int = 128):
        self.dim = dim
        self.vocab: Dict[str, int] = {}
        self.next_idx = 0

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()

    def _get_word_idx(self, word: str) -> int:
        """Get or create index for a word."""
        if word not in self.vocab:
            self.vocab[word] = self.next_idx % self.dim
            self.next_idx += 1
        return self.vocab[word]

    def embed(self, text: str) -> List[float]:
        """Create embedding for text."""
        tokens = self._tokenize(text)
        embedding = [0.0] * self.dim

        for token in tokens:
            idx = self._get_word_idx(token)
            embedding[idx] += 1.0

        # Normalize
        magnitude = math.sqrt(sum(x*x for x in embedding)) or 1.0
        return [x / magnitude for x in embedding]

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1)) or 1.0
        mag2 = math.sqrt(sum(b * b for b in vec2)) or 1.0
        return dot / (mag1 * mag2)


# =============================================================================
# SIMULATED LLM (For API-free demonstration)
# =============================================================================

class SimulatedLLM:
    """
    Intelligent simulation of LLM responses for demonstration.
    Uses pattern matching and templates to provide realistic responses.
    """

    def __init__(self, persona: str = "assistant"):
        self.persona = persona
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a simulated response based on the prompt."""
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Planning prompts
        if "create a plan" in prompt_lower or "break down" in prompt_lower:
            return self._generate_plan(prompt)

        # Research prompts
        if "research" in prompt_lower or "find information" in prompt_lower:
            return self._generate_research(prompt)

        # Analysis prompts
        if "analyze" in prompt_lower or "evaluate" in prompt_lower:
            return self._generate_analysis(prompt)

        # Reflection prompts
        if "reflect" in prompt_lower or "what did you learn" in prompt_lower:
            return self._generate_reflection(prompt)

        # Summary prompts
        if "summarize" in prompt_lower or "summary" in prompt_lower:
            return self._generate_summary(prompt)

        # Decision prompts
        if "decide" in prompt_lower or "choose" in prompt_lower:
            return self._generate_decision(prompt)

        # Default response
        return self._generate_default(prompt)

    def _generate_plan(self, prompt: str) -> str:
        """Generate a planning response."""
        # Extract key terms from prompt
        words = prompt.lower().split()
        task_words = [w for w in words if len(w) > 4 and w not in
                      ['create', 'break', 'steps', 'please', 'following']][:3]

        steps = [
            f"1. Research and gather information about {' '.join(task_words[:2])}",
            f"2. Analyze requirements and constraints",
            f"3. Design solution approach for {task_words[0] if task_words else 'the task'}",
            f"4. Implement the core functionality",
            f"5. Test and validate results",
            f"6. Refine based on feedback"
        ]
        return "\n".join(steps)

    def _generate_research(self, prompt: str) -> str:
        """Generate a research response."""
        topic = prompt.split("about")[-1].strip()[:50] if "about" in prompt.lower() else "the topic"

        return f"""Research findings on {topic}:

Key Points:
1. This is a complex topic with multiple dimensions
2. Current approaches include both traditional and modern methods
3. Best practices emphasize iterative refinement
4. Performance depends heavily on context and requirements

Recommendations:
- Start with a baseline implementation
- Measure and iterate
- Consider trade-offs between complexity and maintainability"""

    def _generate_analysis(self, prompt: str) -> str:
        """Generate an analysis response."""
        return """Analysis Results:

Strengths:
- Clear structure and organization
- Good coverage of key aspects
- Appropriate level of detail

Areas for Improvement:
- Could benefit from more specific examples
- Consider edge cases more thoroughly
- Add quantitative metrics where possible

Overall Assessment: The approach is sound with room for optimization."""

    def _generate_reflection(self, prompt: str) -> str:
        """Generate a reflection response."""
        return """Reflection:

What Worked Well:
1. Breaking down the problem into manageable steps
2. Using iterative refinement
3. Maintaining clear documentation

What Could Be Improved:
1. More thorough initial analysis
2. Better handling of edge cases
3. Earlier validation of assumptions

Key Lessons:
- Planning upfront saves time overall
- Regular checkpoints help catch issues early
- Documentation aids understanding and maintenance"""

    def _generate_summary(self, prompt: str) -> str:
        """Generate a summary response."""
        return """Summary:

The task was completed successfully through a systematic approach:
1. Initial analysis identified key requirements
2. A structured plan guided execution
3. Regular validation ensured quality
4. Iterative refinement improved outcomes

Key outcomes achieved with clear documentation and reproducible methodology."""

    def _generate_decision(self, prompt: str) -> str:
        """Generate a decision response."""
        return """Decision Analysis:

After evaluating the options:
- Option A: Good for simplicity, may limit scalability
- Option B: More complex but flexible
- Option C: Best performance, higher implementation cost

Recommendation: Option B provides the best balance of flexibility and
maintainability for most use cases. Option A for simple scenarios."""

    def _generate_default(self, prompt: str) -> str:
        """Generate a default response."""
        return f"""As a {self.persona}, I've processed your request.

Key observations:
1. The task involves multiple components
2. A systematic approach is recommended
3. Results can be validated through testing

I'm ready to proceed with the next steps or provide more detail on any aspect."""


# =============================================================================
# MEMORY SYSTEM
# =============================================================================

class HybridMemorySystem:
    """
    Multi-tier memory system combining short-term, long-term, and episodic memory.
    Supports semantic search, importance-based retention, and memory consolidation.
    """

    def __init__(self, embedding_model: Optional[SimpleEmbeddingModel] = None):
        self.embedding_model = embedding_model or SimpleEmbeddingModel()
        self.short_term: List[Memory] = []
        self.long_term: List[Memory] = []
        self.episodic: List[Memory] = []
        self.max_short_term = 20
        self.importance_threshold = 0.6

    def add(self, content: str, memory_type: MemoryType = MemoryType.SHORT_TERM,
            importance: float = 0.5, metadata: Optional[Dict] = None) -> Memory:
        """Add a new memory."""
        embedding = self.embedding_model.embed(content)

        memory = Memory(
            content=content,
            memory_type=memory_type.value,
            importance=importance,
            embedding=embedding,
            metadata=metadata or {}
        )

        # Add to appropriate store
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term.append(memory)
            self._consolidate_short_term()
        elif memory_type == MemoryType.EPISODIC:
            self.episodic.append(memory)
        else:
            self.long_term.append(memory)

        return memory

    def _consolidate_short_term(self):
        """Move important memories from short-term to long-term."""
        if len(self.short_term) > self.max_short_term:
            # Move important memories to long-term
            for memory in self.short_term[:]:
                if memory.importance >= self.importance_threshold:
                    memory.memory_type = MemoryType.LONG_TERM.value
                    self.long_term.append(memory)
                    self.short_term.remove(memory)

            # Remove oldest low-importance memories
            while len(self.short_term) > self.max_short_term:
                self.short_term.pop(0)

    def search(self, query: str, top_k: int = 5,
               memory_types: Optional[List[MemoryType]] = None) -> List[Tuple[Memory, float]]:
        """Search memories by semantic similarity."""
        query_embedding = self.embedding_model.embed(query)

        # Collect memories to search
        memories_to_search = []
        type_values = [mt.value for mt in (memory_types or list(MemoryType))]

        for memory in self.short_term + self.long_term + self.episodic:
            if memory.memory_type in type_values:
                memories_to_search.append(memory)

        # Calculate similarities
        scored = []
        for memory in memories_to_search:
            if memory.embedding:
                sim = SimpleEmbeddingModel.cosine_similarity(query_embedding, memory.embedding)
                scored.append((memory, sim))

        # Sort by similarity and return top_k
        scored.sort(key=lambda x: x[1], reverse=True)

        # Update access counts
        for memory, _ in scored[:top_k]:
            memory.access_count += 1

        return scored[:top_k]

    def get_context(self, query: str, max_tokens: int = 1000) -> str:
        """Get relevant context from memory for a query."""
        results = self.search(query, top_k=5)

        context_parts = []
        total_length = 0

        for memory, score in results:
            if total_length + len(memory.content) < max_tokens:
                context_parts.append(f"[{memory.memory_type}] {memory.content}")
                total_length += len(memory.content)

        return "\n".join(context_parts)

    def summarize(self) -> Dict[str, Any]:
        """Get summary statistics of memory system."""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "episodic_count": len(self.episodic),
            "total_memories": len(self.short_term) + len(self.long_term) + len(self.episodic),
            "average_importance": sum(m.importance for m in self.long_term) / len(self.long_term) if self.long_term else 0
        }

    def save(self, filename: str = "memory_state.json"):
        """Save memory state to file."""
        data = {
            "short_term": [m.to_dict() for m in self.short_term],
            "long_term": [m.to_dict() for m in self.long_term],
            "episodic": [m.to_dict() for m in self.episodic]
        }
        save_json(filename, data)

    def load(self, filename: str = "memory_state.json"):
        """Load memory state from file."""
        data = load_json(filename)
        if data:
            self.short_term = [Memory.from_dict(m) for m in data.get("short_term", [])]
            self.long_term = [Memory.from_dict(m) for m in data.get("long_term", [])]
            self.episodic = [Memory.from_dict(m) for m in data.get("episodic", [])]


# =============================================================================
# PLANNING ENGINE
# =============================================================================

class PlanningEngine:
    """
    Multi-strategy planning engine supporting various planning algorithms.
    """

    def __init__(self, llm: Optional[SimulatedLLM] = None):
        self.llm = llm or SimulatedLLM("planner")

    def create_plan(self, goal: str, strategy: PlanningStrategy = PlanningStrategy.PLAN_AND_EXECUTE,
                    context: str = "") -> Plan:
        """Create a plan for the given goal using the specified strategy."""

        if strategy == PlanningStrategy.PLAN_AND_EXECUTE:
            return self._plan_and_execute(goal, context)
        elif strategy == PlanningStrategy.REWOO:
            return self._rewoo_plan(goal, context)
        elif strategy == PlanningStrategy.TREE_OF_THOUGHT:
            return self._tree_of_thought(goal, context)
        else:
            return self._plan_and_execute(goal, context)

    def _plan_and_execute(self, goal: str, context: str) -> Plan:
        """Standard Plan-and-Execute approach."""
        prompt = f"""Create a plan to achieve this goal: {goal}

Context: {context}

Break this down into clear, actionable steps."""

        plan_text = self.llm.generate(prompt)
        steps = self._parse_plan_steps(plan_text)

        return Plan(
            goal=goal,
            steps=steps,
            strategy=PlanningStrategy.PLAN_AND_EXECUTE.value
        )

    def _rewoo_plan(self, goal: str, context: str) -> Plan:
        """
        ReWOO (Reasoning Without Observation) approach.
        Creates a plan with evidence placeholders before execution.
        """
        prompt = f"""Plan for: {goal}

Using ReWOO methodology, create a plan where each step specifies:
- The action to take
- The evidence it will produce (as #E1, #E2, etc.)
- Dependencies on prior evidence

Context: {context}"""

        plan_text = self.llm.generate(prompt)
        steps = self._parse_plan_steps(plan_text)

        # Add evidence placeholders
        for i, step in enumerate(steps):
            step.evidence = [f"#E{i+1}"]

        return Plan(
            goal=goal,
            steps=steps,
            strategy=PlanningStrategy.REWOO.value
        )

    def _tree_of_thought(self, goal: str, context: str) -> Plan:
        """
        Tree of Thought approach - explores multiple reasoning paths.
        """
        # Generate multiple approaches
        approaches = []
        for i in range(3):
            prompt = f"""Goal: {goal}

Generate approach #{i+1} for solving this (be creative and different from standard approaches):

Context: {context}"""
            approach = self.llm.generate(prompt)
            approaches.append(approach)

        # Evaluate approaches
        best_idx = 0  # In real implementation, would score each approach

        # Create plan from best approach
        steps = self._parse_plan_steps(approaches[best_idx])

        return Plan(
            goal=goal,
            steps=steps,
            strategy=PlanningStrategy.TREE_OF_THOUGHT.value
        )

    def _parse_plan_steps(self, plan_text: str) -> List[PlanStep]:
        """Parse plan text into structured steps."""
        lines = plan_text.strip().split('\n')
        steps = []
        step_id = 0

        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Clean up the line
                clean_line = re.sub(r'^[\d\.\-\)\s]+', '', line).strip()
                if clean_line:
                    steps.append(PlanStep(
                        step_id=step_id,
                        description=clean_line,
                        dependencies=[step_id - 1] if step_id > 0 else []
                    ))
                    step_id += 1

        return steps if steps else [PlanStep(step_id=0, description="Execute the task")]

    def execute_step(self, step: PlanStep, context: str = "") -> str:
        """Execute a single plan step."""
        step.status = "in_progress"

        prompt = f"""Execute this step: {step.description}

Context: {context}

Provide the result of executing this step."""

        result = self.llm.generate(prompt)
        step.result = result
        step.status = "completed"

        return result


# =============================================================================
# MULTI-AGENT COLLABORATION
# =============================================================================

class Agent:
    """
    Base agent class with memory, planning, and collaboration capabilities.
    """

    def __init__(self, name: str, role: AgentRole,
                 llm: Optional[SimulatedLLM] = None,
                 memory: Optional[HybridMemorySystem] = None):
        self.name = name
        self.role = role
        self.llm = llm or SimulatedLLM(role.value)
        self.memory = memory or HybridMemorySystem()
        self.planning = PlanningEngine(self.llm)
        self.message_inbox: List[AgentMessage] = []
        self.message_outbox: List[AgentMessage] = []
        self.reflections: List[Reflection] = []

    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent."""
        self.message_inbox.append(message)
        self.memory.add(
            f"Message from {message.sender}: {message.content}",
            MemoryType.EPISODIC,
            importance=0.7
        )

    def send_message(self, recipient: str, content: str,
                     message_type: str = "task") -> AgentMessage:
        """Send a message to another agent."""
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            content=content,
            message_type=message_type
        )
        self.message_outbox.append(message)
        return message

    def process_task(self, task: str) -> str:
        """Process a task and return the result."""
        # Get relevant context from memory
        context = self.memory.get_context(task)

        prompt = f"""As a {self.role.value}, process this task:

Task: {task}

Relevant context from memory:
{context}

Provide your response."""

        result = self.llm.generate(prompt)

        # Store the interaction in memory
        self.memory.add(f"Task: {task}", MemoryType.EPISODIC, importance=0.6)
        self.memory.add(f"Result: {result}", MemoryType.EPISODIC, importance=0.5)

        return result

    def reflect(self, task: str, outcome: str, success: bool) -> Reflection:
        """Reflect on a completed task."""
        prompt = f"""Reflect on this task:

Task: {task}
Outcome: {outcome}
Success: {success}

What did you learn? What could be improved?"""

        reflection_text = self.llm.generate(prompt)

        reflection = Reflection(
            task=task,
            outcome=outcome,
            success=success,
            lessons_learned=["Systematic approach is effective",
                            "Context from memory helps",
                            "Iteration improves results"],
            improvements=["Could gather more context upfront",
                         "Should validate assumptions earlier"]
        )

        self.reflections.append(reflection)

        # Store reflection in memory
        self.memory.add(
            f"Reflection on '{task}': {reflection_text}",
            MemoryType.LONG_TERM,
            importance=0.8
        )

        return reflection


class SupervisorAgent(Agent):
    """
    Supervisor agent that coordinates worker agents.
    """

    def __init__(self, name: str = "Supervisor"):
        super().__init__(name, AgentRole.SUPERVISOR)
        self.workers: Dict[str, Agent] = {}

    def add_worker(self, worker: Agent):
        """Add a worker agent."""
        self.workers[worker.name] = worker

    def delegate_task(self, task: str) -> Dict[str, Any]:
        """Delegate a task to appropriate workers and aggregate results."""
        results = {"task": task, "delegations": [], "final_result": ""}

        # Analyze task to determine which workers to use
        prompt = f"""Analyze this task and determine how to delegate it:

Task: {task}

Available workers: {list(self.workers.keys())}

Which workers should handle which parts?"""

        delegation_plan = self.llm.generate(prompt)

        # Simulate delegation to each worker
        worker_results = []
        for worker_name, worker in self.workers.items():
            sub_task = f"Your part of: {task}"
            result = worker.process_task(sub_task)

            # Send/receive messages
            self.send_message(worker_name, sub_task, "task")
            worker.receive_message(AgentMessage(
                sender=self.name,
                recipient=worker_name,
                content=sub_task,
                message_type="task"
            ))

            worker_results.append({
                "worker": worker_name,
                "result": result
            })
            results["delegations"].append({
                "worker": worker_name,
                "sub_task": sub_task,
                "result": result
            })

        # Aggregate results
        aggregate_prompt = f"""Aggregate these worker results:

{json.dumps(worker_results, indent=2)}

Provide a unified final result."""

        results["final_result"] = self.llm.generate(aggregate_prompt)

        return results


class SwarmAgent(Agent):
    """
    Agent that participates in swarm collaboration.
    Can hand off tasks to other swarm members.
    """

    def __init__(self, name: str, specialty: str):
        super().__init__(name, AgentRole.WORKER)
        self.specialty = specialty
        self.peers: Dict[str, "SwarmAgent"] = {}

    def add_peer(self, peer: "SwarmAgent"):
        """Add a peer agent to the swarm."""
        self.peers[peer.name] = peer

    def should_handoff(self, task: str) -> Optional[str]:
        """Determine if task should be handed off to a peer."""
        task_lower = task.lower()

        # Simple heuristic - check if task matches our specialty
        if self.specialty.lower() not in task_lower:
            # Find a peer whose specialty matches better
            for peer_name, peer in self.peers.items():
                if peer.specialty.lower() in task_lower:
                    return peer_name

        return None

    def process_task(self, task: str) -> Tuple[str, List[str]]:
        """Process task, potentially handing off to peers."""
        handoff_chain = [self.name]

        # Check for handoff
        handoff_to = self.should_handoff(task)
        if handoff_to and handoff_to in self.peers:
            # Hand off to peer
            self.send_message(handoff_to, task, "handoff")
            result, chain = self.peers[handoff_to].process_task(task)
            handoff_chain.extend(chain)
            return result, handoff_chain

        # Process ourselves
        result = super().process_task(task)
        return result, handoff_chain


class DebateAgent(Agent):
    """
    Agent that participates in multi-agent debate.
    """

    def __init__(self, name: str, perspective: str):
        super().__init__(name, AgentRole.CRITIC)
        self.perspective = perspective

    def argue_position(self, topic: str, previous_arguments: List[str] = None) -> str:
        """Present an argument from this agent's perspective."""
        prev_args = "\n".join(previous_arguments) if previous_arguments else "None"

        prompt = f"""Topic: {topic}

Your perspective: {self.perspective}

Previous arguments:
{prev_args}

Present your argument from your perspective, responding to previous points if relevant."""

        return self.llm.generate(prompt)


# =============================================================================
# AUTONOMOUS AGENT FRAMEWORK
# =============================================================================

class AutonomousAgent:
    """
    Full-featured autonomous agent combining memory, planning, and self-improvement.
    """

    def __init__(self, name: str, goals: List[str],
                 planning_strategy: PlanningStrategy = PlanningStrategy.PLAN_AND_EXECUTE):
        self.name = name
        self.goals = goals
        self.llm = SimulatedLLM(name)
        self.memory = HybridMemorySystem()
        self.planning = PlanningEngine(self.llm)
        self.planning_strategy = planning_strategy
        self.current_plan: Optional[Plan] = None
        self.task_history: List[Dict] = []
        self.reflections: List[Reflection] = []
        self.performance_score = 0.5

    def think(self, observation: str) -> str:
        """Process an observation and decide on action."""
        # Get context from memory
        context = self.memory.get_context(observation)

        prompt = f"""Current goals: {self.goals}

Observation: {observation}

Relevant memories:
{context}

What should be done next? Think step by step."""

        thought = self.llm.generate(prompt)

        # Store thinking in memory
        self.memory.add(f"Observation: {observation}", MemoryType.SHORT_TERM)
        self.memory.add(f"Thought: {thought}", MemoryType.SHORT_TERM)

        return thought

    def plan(self, task: str) -> Plan:
        """Create a plan for a task."""
        context = self.memory.get_context(task)

        # Add relevant reflections to context
        if self.reflections:
            recent_lessons = [r.lessons_learned for r in self.reflections[-3:]]
            context += f"\n\nLessons from past experiences: {recent_lessons}"

        self.current_plan = self.planning.create_plan(
            task,
            self.planning_strategy,
            context
        )

        return self.current_plan

    def execute(self, task: str) -> Dict[str, Any]:
        """Execute a task with full autonomous behavior."""
        result = {
            "task": task,
            "plan": None,
            "steps_executed": [],
            "final_result": "",
            "reflection": None
        }

        # Think about the task
        thought = self.think(task)

        # Create plan
        plan = self.plan(task)
        result["plan"] = {
            "goal": plan.goal,
            "strategy": plan.strategy,
            "steps": [s.description for s in plan.steps]
        }

        # Execute each step
        for step in plan.steps:
            step_context = self.memory.get_context(step.description)
            step_result = self.planning.execute_step(step, step_context)
            result["steps_executed"].append({
                "step": step.description,
                "result": step_result
            })

            # Store step execution in memory
            self.memory.add(
                f"Executed: {step.description} -> {step_result}",
                MemoryType.EPISODIC,
                importance=0.6
            )

        # Generate final result
        final_prompt = f"""Task: {task}

Steps executed:
{json.dumps(result['steps_executed'], indent=2)}

Provide a final summary of the results."""

        result["final_result"] = self.llm.generate(final_prompt)

        # Reflect on the task
        reflection = self._reflect(task, result["final_result"])
        result["reflection"] = {
            "lessons": reflection.lessons_learned,
            "improvements": reflection.improvements
        }

        # Store in task history
        self.task_history.append(result)

        return result

    def _reflect(self, task: str, outcome: str) -> Reflection:
        """Reflect on task execution."""
        # Simulate success based on task completion
        success = "error" not in outcome.lower() and "fail" not in outcome.lower()

        reflection = Reflection(
            task=task,
            outcome=outcome,
            success=success,
            lessons_learned=[
                "Planning before execution improves results",
                "Memory context helps with decision making",
                "Breaking down tasks aids completion"
            ],
            improvements=[
                "Could validate assumptions earlier",
                "Should gather more context for complex tasks"
            ]
        )

        self.reflections.append(reflection)

        # Update performance score
        self.performance_score = 0.7 * self.performance_score + 0.3 * (1.0 if success else 0.0)

        # Store reflection in long-term memory
        self.memory.add(
            f"Reflection on '{task}': Success={success}, Lessons learned",
            MemoryType.LONG_TERM,
            importance=0.8
        )

        return reflection

    def save_state(self, filename: str = "agent_state.json"):
        """Save agent state."""
        state = {
            "name": self.name,
            "goals": self.goals,
            "planning_strategy": self.planning_strategy.value,
            "performance_score": self.performance_score,
            "task_history_count": len(self.task_history),
            "reflections_count": len(self.reflections)
        }
        save_json(filename, state)
        self.memory.save(f"{self.name}_memory.json")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "name": self.name,
            "goals": self.goals,
            "strategy": self.planning_strategy.value,
            "performance_score": round(self.performance_score, 2),
            "tasks_completed": len(self.task_history),
            "reflections": len(self.reflections),
            "memory_summary": self.memory.summarize(),
            "llm_calls": self.llm.call_count
        }


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo1_research_agent():
    """Demo 1: Research Agent with Memory and Planning"""
    print("\n" + "=" * 70)
    print("DEMO 1: Research Agent with Memory and Planning")
    print("=" * 70)

    # Create autonomous research agent
    agent = AutonomousAgent(
        name="ResearchBot",
        goals=["Find accurate information", "Synthesize findings", "Provide clear summaries"],
        planning_strategy=PlanningStrategy.PLAN_AND_EXECUTE
    )

    # Give the agent some background knowledge
    agent.memory.add(
        "Machine learning is a subset of AI that enables systems to learn from data",
        MemoryType.LONG_TERM,
        importance=0.9
    )
    agent.memory.add(
        "Neural networks are inspired by biological neural systems",
        MemoryType.LONG_TERM,
        importance=0.8
    )
    agent.memory.add(
        "Transformers revolutionized NLP with attention mechanisms",
        MemoryType.LONG_TERM,
        importance=0.9
    )

    print("\n📚 Agent initialized with background knowledge")
    print(f"   Memory: {agent.memory.summarize()}")

    # Execute a research task
    task = "Research the impact of transformer architecture on modern AI applications"
    print(f"\n🔬 Task: {task}")

    result = agent.execute(task)

    print("\n📋 Plan created:")
    for i, step in enumerate(result['plan']['steps'], 1):
        print(f"   {i}. {step}")

    print("\n⚡ Steps executed:")
    for step_result in result['steps_executed']:
        print(f"\n   Step: {step_result['step']}")
        print(f"   Result: {step_result['result'][:200]}...")

    print(f"\n📝 Final Result:\n{result['final_result']}")

    print("\n💡 Reflection:")
    print(f"   Lessons: {result['reflection']['lessons']}")
    print(f"   Improvements: {result['reflection']['improvements']}")

    # Show agent status
    status = agent.get_status()
    print(f"\n📊 Agent Status:")
    print(f"   Performance Score: {status['performance_score']}")
    print(f"   Tasks Completed: {status['tasks_completed']}")
    print(f"   LLM Calls Made: {status['llm_calls']}")

    # Save state
    agent.save_state()
    print("\n✅ Agent state saved")

    return agent


def demo2_problem_solver():
    """Demo 2: Problem Solver with Tree of Thought"""
    print("\n" + "=" * 70)
    print("DEMO 2: Problem Solver with Tree of Thought Planning")
    print("=" * 70)

    # Create problem-solving agent with ToT strategy
    agent = AutonomousAgent(
        name="ProblemSolver",
        goals=["Solve complex problems", "Explore multiple approaches", "Find optimal solutions"],
        planning_strategy=PlanningStrategy.TREE_OF_THOUGHT
    )

    # Add domain knowledge
    agent.memory.add(
        "Complex problems often have multiple valid solutions",
        MemoryType.LONG_TERM,
        importance=0.8
    )
    agent.memory.add(
        "Breaking down problems into sub-problems aids understanding",
        MemoryType.LONG_TERM,
        importance=0.9
    )

    print("\n🧠 Problem Solver initialized with Tree of Thought strategy")

    # Complex problem to solve
    task = "Design a scalable microservices architecture for an e-commerce platform"
    print(f"\n🎯 Problem: {task}")

    # First, let the agent think
    thought = agent.think(task)
    print(f"\n💭 Agent's Initial Thinking:\n{thought}")

    # Now execute with full planning
    result = agent.execute(task)

    print(f"\n🌳 Tree of Thought Plan (Strategy: {result['plan']['strategy']}):")
    for i, step in enumerate(result['plan']['steps'], 1):
        print(f"   Branch {i}: {step}")

    print(f"\n🏁 Solution:\n{result['final_result']}")

    # Compare with other strategies
    print("\n" + "-" * 50)
    print("📊 Strategy Comparison:")

    strategies = [
        PlanningStrategy.PLAN_AND_EXECUTE,
        PlanningStrategy.REWOO,
        PlanningStrategy.TREE_OF_THOUGHT
    ]

    comparison_results = []
    for strategy in strategies:
        test_agent = AutonomousAgent(
            name="TestAgent",
            goals=["Solve problems"],
            planning_strategy=strategy
        )
        test_result = test_agent.execute(task)
        comparison_results.append({
            "strategy": strategy.value,
            "steps": len(test_result['plan']['steps']),
            "llm_calls": test_agent.llm.call_count
        })

    print(f"\n   {'Strategy':<20} {'Steps':<10} {'LLM Calls':<10}")
    print(f"   {'-'*40}")
    for cr in comparison_results:
        print(f"   {cr['strategy']:<20} {cr['steps']:<10} {cr['llm_calls']:<10}")

    print("\n✅ Problem solving complete")

    return agent


def demo3_multi_agent_team():
    """Demo 3: Multi-Agent Team Collaboration"""
    print("\n" + "=" * 70)
    print("DEMO 3: Multi-Agent Team Collaboration")
    print("=" * 70)

    # Create supervisor
    supervisor = SupervisorAgent("TeamLead")

    # Create specialized workers
    researcher = Agent("Researcher", AgentRole.RESEARCHER)
    analyst = Agent("Analyst", AgentRole.WORKER)
    writer = Agent("Writer", AgentRole.WORKER)

    # Add workers to supervisor
    supervisor.add_worker(researcher)
    supervisor.add_worker(analyst)
    supervisor.add_worker(writer)

    print("\n👥 Team Created:")
    print(f"   Supervisor: {supervisor.name}")
    print(f"   Workers: {list(supervisor.workers.keys())}")

    # Team task
    task = "Create a comprehensive report on the future of AI in healthcare"
    print(f"\n📋 Team Task: {task}")

    result = supervisor.delegate_task(task)

    print("\n📨 Delegation Results:")
    for delegation in result['delegations']:
        print(f"\n   Worker: {delegation['worker']}")
        print(f"   Sub-task: {delegation['sub_task']}")
        print(f"   Result preview: {delegation['result'][:150]}...")

    print(f"\n📝 Aggregated Result:\n{result['final_result']}")

    # Show message flow
    print("\n📬 Message Flow:")
    for msg in supervisor.message_outbox[:5]:
        print(f"   {msg.sender} → {msg.recipient}: [{msg.message_type}] {msg.content[:50]}...")

    # Demonstrate swarm collaboration
    print("\n" + "-" * 50)
    print("🐝 Swarm Collaboration Demo:")

    # Create swarm agents
    code_agent = SwarmAgent("CodeExpert", "code")
    design_agent = SwarmAgent("DesignExpert", "design")
    test_agent = SwarmAgent("TestExpert", "testing")

    # Connect peers
    code_agent.add_peer(design_agent)
    code_agent.add_peer(test_agent)
    design_agent.add_peer(code_agent)
    design_agent.add_peer(test_agent)
    test_agent.add_peer(code_agent)
    test_agent.add_peer(design_agent)

    # Test handoff
    tasks = [
        "Write code for user authentication",
        "Design the login interface",
        "Create testing strategy for auth"
    ]

    print("\n   Swarm handoff demonstration:")
    for t in tasks:
        result, chain = code_agent.process_task(t)
        print(f"   Task: '{t[:40]}...'")
        print(f"   Handoff chain: {' → '.join(chain)}")

    print("\n✅ Multi-agent collaboration complete")

    return supervisor


def demo4_self_improving_agent():
    """Demo 4: Self-Improving Agent with Reflection"""
    print("\n" + "=" * 70)
    print("DEMO 4: Self-Improving Agent with Reflection")
    print("=" * 70)

    # Create agent that learns from experience
    agent = AutonomousAgent(
        name="LearningAgent",
        goals=["Complete tasks effectively", "Learn from mistakes", "Continuously improve"],
        planning_strategy=PlanningStrategy.REFLEXION
    )

    print("\n🎓 Learning Agent initialized")
    print(f"   Initial Performance Score: {agent.performance_score}")

    # Series of tasks to learn from
    tasks = [
        "Analyze a dataset and identify patterns",
        "Optimize a slow database query",
        "Debug a memory leak in an application",
        "Design a caching strategy for an API"
    ]

    print("\n📚 Learning through task execution:")

    for i, task in enumerate(tasks, 1):
        print(f"\n   --- Task {i}/{len(tasks)} ---")
        print(f"   Task: {task}")

        result = agent.execute(task)

        # Show learning progress
        print(f"   Steps: {len(result['steps_executed'])}")
        print(f"   Performance: {agent.performance_score:.2f}")
        print(f"   New lessons: {result['reflection']['lessons'][:2]}")

    # Show final learning state
    print("\n" + "-" * 50)
    print("📊 Learning Summary:")

    status = agent.get_status()
    print(f"   Final Performance Score: {status['performance_score']}")
    print(f"   Total Tasks Completed: {status['tasks_completed']}")
    print(f"   Total Reflections: {status['reflections']}")
    print(f"   Memory Stats: {status['memory_summary']}")

    # Show memory search capabilities
    print("\n🔍 Memory Search Demo:")
    query = "optimization patterns"
    memories = agent.memory.search(query, top_k=3)
    print(f"   Query: '{query}'")
    for mem, score in memories:
        print(f"   [{score:.3f}] {mem.content[:60]}...")

    # Show reflection evolution
    print("\n💡 Reflection Evolution:")
    for i, ref in enumerate(agent.reflections[:3], 1):
        print(f"   Reflection {i}:")
        print(f"      Task: {ref.task[:40]}...")
        print(f"      Success: {ref.success}")

    # Save learned state
    agent.save_state("learning_agent_state.json")
    print("\n✅ Learned state saved")

    return agent


def show_help():
    """Show help information."""
    print("\n" + "=" * 70)
    print("AUTONOMOUS AGENT FRAMEWORK - Module 20 Deliverable")
    print("=" * 70)

    print("""
This framework demonstrates advanced agentic AI patterns:

FEATURES:
  • Multi-tier Memory System (short-term, long-term, episodic)
  • Planning Algorithms (Plan-and-Execute, ReWOO, Tree of Thought)
  • Multi-Agent Collaboration (Supervisor, Swarm, Debate)
  • Self-Improvement through Reflection

DEMOS:
  demo1  - Research Agent with memory and planning
  demo2  - Problem Solver with Tree of Thought
  demo3  - Multi-Agent Team collaboration
  demo4  - Self-Improving Agent with reflection

USAGE:
  python deliverable_autonomous_agent.py demo1
  python deliverable_autonomous_agent.py demo2
  python deliverable_autonomous_agent.py demo3
  python deliverable_autonomous_agent.py demo4
  python deliverable_autonomous_agent.py help

ARCHITECTURE:
  ┌─────────────────────────────────────────────┐
  │           Autonomous Agent                  │
  │  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
  │  │  Memory  │ │ Planning │ │ Reflection  │  │
  │  │  System  │ │  Engine  │ │   Module    │  │
  │  └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
  │       │            │              │         │
  │       └────────────┴──────────────┘         │
  │                    │                        │
  │         ┌──────────┴──────────┐             │
  │         │    LLM Interface    │             │
  │         └─────────────────────┘             │
  └─────────────────────────────────────────────┘

No API keys required - uses intelligent simulation for demonstration.

Author: Neural Dojo | Module 20: Advanced Agentic AI 🔮
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo1_research_agent()
    elif command == "demo2":
        demo2_problem_solver()
    elif command == "demo3":
        demo3_multi_agent_team()
    elif command == "demo4":
        demo4_self_improving_agent()
    elif command == "help":
        show_help()
    elif command == "all":
        demo1_research_agent()
        demo2_problem_solver()
        demo3_multi_agent_team()
        demo4_self_improving_agent()
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run 'python deliverable_autonomous_agent.py help' for usage")


if __name__ == "__main__":
    main()
