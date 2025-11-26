#!/usr/bin/env python3
"""
Module 20 Example 03: Multi-Agent Collaboration

This example demonstrates different multi-agent architectures:
1. Supervisor Pattern: One agent manages a team of workers
2. Swarm Pattern: Agents collaborate as peers with handoffs
3. Debate Pattern: Agents argue different positions
4. Hierarchical Pattern: Nested teams with supervisors

Multi-agent systems can solve problems that single agents cannot.
Different architectures suit different types of tasks.

Usage:
    python 03_multi_agent_collaboration.py demo1  # Supervisor pattern
    python 03_multi_agent_collaboration.py demo2  # Swarm pattern
    python 03_multi_agent_collaboration.py demo3  # Debate pattern
    python 03_multi_agent_collaboration.py demo4  # Compare architectures
"""

import json
import random
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Storage directory
STORAGE_DIR = Path(".multi_agent_demo")


# =============================================================================
# AGENT ROLES AND MESSAGES
# =============================================================================

class AgentRole(Enum):
    """Predefined agent roles."""
    SUPERVISOR = "supervisor"
    RESEARCHER = "researcher"
    WRITER = "writer"
    CRITIC = "critic"
    CODER = "coder"
    ANALYST = "analyst"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    recipient: str
    content: str
    message_type: str = "task"  # task, result, feedback, handoff
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "type": self.message_type
        }


# =============================================================================
# SIMULATED LLM
# =============================================================================

class SimulatedLLM:
    """Simulated LLM for demonstrations."""

    def __init__(self, agent_name: str = "default"):
        self.agent_name = agent_name
        self.call_count = 0

    def generate(self, prompt: str) -> str:
        """Generate a response based on agent role."""
        self.call_count += 1
        time.sleep(0.05)  # Simulate latency

        prompt_lower = prompt.lower()

        # Researcher responses
        if "researcher" in self.agent_name.lower() or "research" in prompt_lower:
            return self._researcher_response(prompt)

        # Writer responses
        if "writer" in self.agent_name.lower() or "write" in prompt_lower:
            return self._writer_response(prompt)

        # Critic responses
        if "critic" in self.agent_name.lower() or "review" in prompt_lower or "critique" in prompt_lower:
            return self._critic_response(prompt)

        # Supervisor/Planning responses
        if "supervisor" in self.agent_name.lower() or "coordinate" in prompt_lower or "plan" in prompt_lower:
            return self._supervisor_response(prompt)

        # Debate responses
        if "arguing for" in prompt_lower:
            return self._proponent_response(prompt)
        if "arguing against" in prompt_lower:
            return self._opponent_response(prompt)
        if "judge" in prompt_lower or "verdict" in prompt_lower:
            return self._judge_response(prompt)

        # Suitability check
        if "how well-suited" in prompt_lower:
            return str(random.randint(5, 9))

        return f"[{self.agent_name}] Task completed. Analysis indicates positive outcomes."

    def _researcher_response(self, prompt: str) -> str:
        return """Research findings:
1. Key insight: The topic has significant relevance to current trends
2. Statistics: 78% of industry experts recommend this approach
3. Case study: Company X achieved 40% improvement using similar methods
4. Sources: IEEE papers, industry reports, expert interviews
5. Recommendation: Further investigation into implementation details needed"""

    def _writer_response(self, prompt: str) -> str:
        return """Written content:

The evolution of this field represents a paradigm shift in how we approach
complex problems. By leveraging advanced techniques and proven methodologies,
organizations can achieve remarkable improvements in efficiency and outcomes.

Key takeaways:
- Adoption is accelerating across industries
- Best practices are emerging from early adopters
- The future holds even greater potential

This comprehensive analysis demonstrates the value of systematic approaches."""

    def _critic_response(self, prompt: str) -> str:
        return """Critical Review:

Strengths:
+ Well-structured argument with clear logic
+ Good use of supporting evidence
+ Appropriate scope and depth

Areas for Improvement:
- Could include more specific examples
- Some claims need additional citations
- Consider addressing potential counterarguments

Overall Assessment: 7.5/10 - Good quality with room for enhancement.
Recommendation: Minor revisions would strengthen the final output."""

    def _supervisor_response(self, prompt: str) -> str:
        return json.dumps({
            "plan": [
                {"worker": "researcher", "task": "Research the topic and gather key facts"},
                {"worker": "writer", "task": "Transform research into clear content"},
                {"worker": "critic", "task": "Review and suggest improvements"}
            ],
            "synthesis_instructions": "Combine research insights with polished writing, incorporating critic's feedback"
        })

    def _proponent_response(self, prompt: str) -> str:
        return """Arguments IN FAVOR:

1. Proven Track Record: Multiple studies demonstrate effectiveness
2. Economic Benefits: Cost savings of 30-50% reported
3. Scalability: Successfully deployed at enterprise scale
4. Innovation Driver: Enables new capabilities previously impossible
5. Industry Support: Major players are investing heavily

The evidence clearly supports adoption of this approach."""

    def _opponent_response(self, prompt: str) -> str:
        return """Arguments AGAINST:

1. Implementation Complexity: Significant technical challenges
2. Cost Concerns: High initial investment required
3. Risk Factors: Unproven in certain edge cases
4. Skills Gap: Requires specialized expertise
5. Alternatives Exist: Simpler solutions may suffice

We should proceed with caution and consider alternatives."""

    def _judge_response(self, prompt: str) -> str:
        return """Verdict:

After careful consideration of both positions:

Strongest FOR arguments:
- Economic benefits are well-documented
- Innovation potential is significant

Strongest AGAINST arguments:
- Implementation complexity is valid concern
- Risk factors deserve attention

CONCLUSION: The FOR side presents a stronger case based on evidence,
but AGAINST raises legitimate concerns about implementation.

RECOMMENDATION: Proceed with careful planning, pilot programs,
and risk mitigation strategies."""


# =============================================================================
# PATTERN 1: SUPERVISOR
# =============================================================================

@dataclass
class WorkerAgent:
    """A specialized worker agent."""
    name: str
    role: AgentRole
    system_prompt: str
    llm: SimulatedLLM = field(default=None)

    def __post_init__(self):
        if self.llm is None:
            self.llm = SimulatedLLM(self.name)

    def process(self, task: str, context: str = "") -> str:
        """Process a task and return result."""
        prompt = f"""{self.system_prompt}

Context: {context}

Task: {task}

Your response:"""

        return self.llm.generate(prompt)


class SupervisorAgent:
    """
    Supervisor Pattern: One agent manages a team of workers.

    The supervisor:
    1. Receives tasks from users
    2. Creates a plan for delegation
    3. Assigns tasks to appropriate workers
    4. Synthesizes results

    Good for: Well-defined workflows, quality control
    Trade-off: Single point of coordination, bottleneck potential
    """

    def __init__(self, workers: List[WorkerAgent]):
        self.llm = SimulatedLLM("supervisor")
        self.workers = {w.name: w for w in workers}
        self.message_history: List[AgentMessage] = []

    def delegate(self, task: str) -> Tuple[str, List[AgentMessage]]:
        """Delegate a task to appropriate workers."""
        self.message_history = []

        # Get delegation plan
        worker_descriptions = "\n".join([
            f"- {name} ({w.role.value}): {w.system_prompt[:50]}..."
            for name, w in self.workers.items()
        ])

        planning_prompt = f"""You are a supervisor coordinating a team.

Available workers:
{worker_descriptions}

Task: {task}

Create a plan for delegation in JSON format."""

        response = self.llm.generate(planning_prompt)

        try:
            plan = json.loads(response)
        except json.JSONDecodeError:
            plan = {"plan": [{"worker": list(self.workers.keys())[0], "task": task}]}

        # Execute the plan
        results = {}
        context = f"Original task: {task}\n\n"

        print(f"\n  Supervisor delegating {len(plan.get('plan', []))} tasks...")

        for step in plan.get("plan", []):
            worker_name = step.get("worker")
            worker_task = step.get("task")

            if worker_name not in self.workers:
                continue

            worker = self.workers[worker_name]

            # Add context from previous results
            if results:
                context += "Previous work:\n"
                for name, result in results.items():
                    context += f"  {name}: {result[:100]}...\n"

            # Record task assignment
            self.message_history.append(AgentMessage(
                sender="supervisor",
                recipient=worker_name,
                content=worker_task,
                message_type="task"
            ))

            # Get worker's result
            print(f"    → {worker_name}: {worker_task[:40]}...")
            result = worker.process(worker_task, context)
            results[worker_name] = result

            # Record result
            self.message_history.append(AgentMessage(
                sender=worker_name,
                recipient="supervisor",
                content=result,
                message_type="result"
            ))
            print(f"    ← {worker_name}: {result[:40]}...")

        # Synthesize final output
        synthesis_prompt = f"""Synthesize these worker outputs into a final response.

Worker outputs:
{json.dumps({k: v[:200] for k, v in results.items()}, indent=2)}

Final synthesized response:"""

        final_result = self.llm.generate(synthesis_prompt)

        return final_result, self.message_history


# =============================================================================
# PATTERN 2: SWARM
# =============================================================================

@dataclass
class SwarmAgent:
    """An agent in a swarm that can hand off to others."""
    name: str
    role: str
    description: str
    system_prompt: str
    llm: SimulatedLLM = field(default=None)

    def __post_init__(self):
        if self.llm is None:
            self.llm = SimulatedLLM(self.name)

    def should_handle(self, task: str) -> float:
        """Return confidence (0-1) that this agent should handle the task."""
        prompt = f"""You are {self.name}, a {self.role}.
Your specialty: {self.description}

Task: {task}

On a scale of 0-10, how well-suited are you to handle this?
Respond with just a number."""

        response = self.llm.generate(prompt)
        try:
            return float(response.strip()) / 10.0
        except:
            return 0.5

    def process(self, task: str, context: str = "") -> Tuple[str, Optional[str]]:
        """Process task. Returns (response, handoff_to) or (response, None)."""
        prompt = f"""{self.system_prompt}

Context: {context}

Task: {task}

Complete this task. If you need to hand off to a specialist,
end with "HANDOFF: [specialist_type]"

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
    """
    Swarm Pattern: Agents collaborate as peers with handoffs.

    In a swarm:
    1. Best-suited agent takes the task
    2. Agent can hand off to others
    3. No central coordinator
    4. Work flows organically

    Good for: Flexible workflows, expertise-based routing
    Trade-off: Less predictable, may have routing inefficiencies
    """

    def __init__(self, agents: List[SwarmAgent], max_handoffs: int = 5):
        self.agents = {a.name: a for a in agents}
        self.max_handoffs = max_handoffs
        self.message_history: List[AgentMessage] = []

    def find_best_agent(self, task: str, exclude: List[str] = None) -> SwarmAgent:
        """Find the best agent for a task."""
        exclude = exclude or []
        candidates = [a for a in self.agents.values() if a.name not in exclude]

        if not candidates:
            return list(self.agents.values())[0]

        # Simple scoring: use role matching
        task_lower = task.lower()
        scores = []
        for agent in candidates:
            score = 0.5  # Base score
            if agent.role.lower() in task_lower:
                score += 0.3
            if any(word in task_lower for word in agent.description.lower().split()):
                score += 0.2
            scores.append((score, agent))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[0][1]

    def run(self, task: str) -> Tuple[str, List[AgentMessage]]:
        """Run the swarm to complete a task."""
        self.message_history = []
        context = f"Original task: {task}\n\n"
        results = []
        handoffs = 0
        excluded = []

        current_task = task

        print(f"\n  Swarm starting with task...")

        while handoffs < self.max_handoffs:
            agent = self.find_best_agent(current_task, excluded)

            print(f"    → {agent.name} ({agent.role}) handling...")

            # Record assignment
            self.message_history.append(AgentMessage(
                sender="swarm",
                recipient=agent.name,
                content=current_task,
                message_type="task"
            ))

            # Process
            result, handoff = agent.process(current_task, context)
            results.append(f"{agent.name}: {result}")
            context += f"{agent.name}'s work:\n{result}\n\n"

            # Record result
            self.message_history.append(AgentMessage(
                sender=agent.name,
                recipient="swarm",
                content=result,
                message_type="result"
            ))

            print(f"    ← {agent.name}: {result[:40]}...")

            if handoff:
                print(f"    ↻ Handoff to: {handoff}")
                current_task = f"Continue from {agent.name}'s work: {handoff}"
                excluded.append(agent.name)
                handoffs += 1

                # Record handoff
                self.message_history.append(AgentMessage(
                    sender=agent.name,
                    recipient=handoff,
                    content=f"Handing off: {handoff}",
                    message_type="handoff"
                ))
            else:
                break

        final_result = "\n\n---\n\n".join(results)
        return final_result, self.message_history


# =============================================================================
# PATTERN 3: DEBATE
# =============================================================================

@dataclass
class DebateAgent:
    """An agent that argues a position."""
    name: str
    position: str  # "for" or "against"
    llm: SimulatedLLM = field(default=None)

    def __post_init__(self):
        if self.llm is None:
            self.llm = SimulatedLLM(f"{self.name}_{self.position}")

    def make_argument(self, topic: str, opponent_args: List[str] = None) -> str:
        """Make an argument for the position."""
        opponent_text = ""
        if opponent_args:
            opponent_text = f"\n\nOpponent's arguments:\n" + "\n".join(opponent_args[-2:])

        prompt = f"""You are arguing {self.position.upper()} the following topic.

Topic: {topic}
{opponent_text}

Make your strongest argument. Be persuasive and use evidence."""

        return self.llm.generate(prompt)


class DebateArena:
    """
    Debate Pattern: Agents argue different positions.

    In a debate:
    1. Agents take opposing positions
    2. Multiple rounds of arguments
    3. A judge evaluates and decides

    Good for: Finding truth through adversarial process, balanced analysis
    Trade-off: More computation, may amplify biases
    """

    def __init__(self, rounds: int = 2):
        self.judge_llm = SimulatedLLM("judge")
        self.rounds = rounds
        self.message_history: List[AgentMessage] = []

    def debate(self, topic: str) -> Tuple[str, List[AgentMessage]]:
        """Run a debate on a topic."""
        self.message_history = []

        for_agent = DebateAgent("Proponent", "for")
        against_agent = DebateAgent("Opponent", "against")

        for_args = []
        against_args = []

        print(f"\n  Debate: '{topic[:40]}...'")

        for round_num in range(self.rounds):
            print(f"\n  Round {round_num + 1}:")

            # FOR side argues
            for_arg = for_agent.make_argument(topic, against_args)
            for_args.append(for_arg)
            print(f"    FOR: {for_arg[:60]}...")

            self.message_history.append(AgentMessage(
                sender="Proponent",
                recipient="Opponent",
                content=for_arg,
                message_type="argument"
            ))

            # AGAINST side responds
            against_arg = against_agent.make_argument(topic, for_args)
            against_args.append(against_arg)
            print(f"    AGAINST: {against_arg[:60]}...")

            self.message_history.append(AgentMessage(
                sender="Opponent",
                recipient="Proponent",
                content=against_arg,
                message_type="argument"
            ))

        # Judge decides
        print(f"\n  Judge deliberating...")
        verdict = self._judge(topic, for_args, against_args)

        self.message_history.append(AgentMessage(
            sender="Judge",
            recipient="all",
            content=verdict,
            message_type="verdict"
        ))

        return verdict, self.message_history

    def _judge(self, topic: str, for_args: List[str], against_args: List[str]) -> str:
        """Neutral judge evaluates the debate."""
        prompt = f"""You are a neutral judge evaluating this debate.

Topic: {topic}

Arguments FOR:
{chr(10).join(for_args)}

Arguments AGAINST:
{chr(10).join(against_args)}

Provide your verdict with:
1. Strongest arguments from each side
2. Your balanced conclusion"""

        return self.judge_llm.generate(prompt)


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_supervisor():
    """Demo 1: Supervisor pattern."""
    print("\n" + "="*60)
    print("DEMO 1: SUPERVISOR PATTERN")
    print("="*60)

    # Create worker team
    workers = [
        WorkerAgent(
            name="researcher",
            role=AgentRole.RESEARCHER,
            system_prompt="You are a thorough researcher. Find facts and cite sources."
        ),
        WorkerAgent(
            name="writer",
            role=AgentRole.WRITER,
            system_prompt="You are a skilled writer. Create clear, engaging content."
        ),
        WorkerAgent(
            name="critic",
            role=AgentRole.CRITIC,
            system_prompt="You are a critical reviewer. Find issues and suggest improvements."
        )
    ]

    supervisor = SupervisorAgent(workers)

    task = "Create a comprehensive analysis of AI agent architectures"

    print(f"\nTask: '{task}'")
    result, messages = supervisor.delegate(task)

    print(f"\n--- Final Result ---")
    print(result[:300] + "...")

    print(f"\n--- Message Flow ({len(messages)} messages) ---")
    for msg in messages:
        print(f"  {msg.sender} → {msg.recipient}: [{msg.message_type}]")

    print("\n--- Analysis ---")
    print("Supervisor Pattern:")
    print("  + Clear hierarchy and control")
    print("  + Quality assurance through oversight")
    print("  + Predictable workflow")
    print("  - Supervisor is bottleneck")
    print("  - Workers can't collaborate directly")


def demo_2_swarm():
    """Demo 2: Swarm pattern."""
    print("\n" + "="*60)
    print("DEMO 2: SWARM PATTERN")
    print("="*60)

    # Create swarm agents
    agents = [
        SwarmAgent(
            name="data_expert",
            role="data analyst",
            description="Analyzes data and provides insights",
            system_prompt="You analyze data and extract meaningful patterns."
        ),
        SwarmAgent(
            name="strategy_expert",
            role="strategist",
            description="Develops strategies and recommendations",
            system_prompt="You develop actionable strategies based on analysis."
        ),
        SwarmAgent(
            name="implementation_expert",
            role="implementer",
            description="Creates implementation plans",
            system_prompt="You create detailed implementation plans."
        )
    ]

    swarm = SwarmCoordinator(agents, max_handoffs=3)

    task = "Develop a data-driven strategy for improving customer retention"

    print(f"\nTask: '{task}'")
    result, messages = swarm.run(task)

    print(f"\n--- Final Result ---")
    print(result[:400] + "...")

    print(f"\n--- Message Flow ({len(messages)} messages) ---")
    for msg in messages:
        print(f"  {msg.sender} → {msg.recipient}: [{msg.message_type}]")

    print("\n--- Analysis ---")
    print("Swarm Pattern:")
    print("  + Flexible, organic workflow")
    print("  + Expertise-based routing")
    print("  + No central bottleneck")
    print("  - Less predictable")
    print("  - May have routing inefficiencies")


def demo_3_debate():
    """Demo 3: Debate pattern."""
    print("\n" + "="*60)
    print("DEMO 3: DEBATE PATTERN")
    print("="*60)

    arena = DebateArena(rounds=2)

    topic = "Should organizations prioritize AI automation over human workforce expansion?"

    print(f"\nTopic: '{topic}'")
    verdict, messages = arena.debate(topic)

    print(f"\n--- Judge's Verdict ---")
    print(verdict)

    print(f"\n--- Message Flow ({len(messages)} messages) ---")
    for msg in messages:
        print(f"  {msg.sender} → {msg.recipient}: [{msg.message_type}]")

    print("\n--- Analysis ---")
    print("Debate Pattern:")
    print("  + Finds truth through adversarial process")
    print("  + Surfaces different perspectives")
    print("  + Balanced analysis")
    print("  - More computation required")
    print("  - May amplify existing biases")


def demo_4_compare():
    """Demo 4: Compare all architectures."""
    print("\n" + "="*60)
    print("DEMO 4: COMPARING MULTI-AGENT ARCHITECTURES")
    print("="*60)

    task = "Evaluate the feasibility of a new AI product launch"

    # Track results
    results = {}

    # Supervisor
    print("\n--- Running Supervisor Pattern ---")
    workers = [
        WorkerAgent("researcher", AgentRole.RESEARCHER, "Research expert"),
        WorkerAgent("analyst", AgentRole.ANALYST, "Analysis expert"),
        WorkerAgent("critic", AgentRole.CRITIC, "Critical reviewer")
    ]
    supervisor = SupervisorAgent(workers)
    _, supervisor_msgs = supervisor.delegate(task)
    results["Supervisor"] = len(supervisor_msgs)

    # Swarm
    print("\n--- Running Swarm Pattern ---")
    agents = [
        SwarmAgent("market_expert", "market analyst", "Market analysis", "Analyze markets"),
        SwarmAgent("tech_expert", "tech lead", "Technical feasibility", "Assess technology"),
        SwarmAgent("business_expert", "business analyst", "Business viability", "Evaluate business")
    ]
    swarm = SwarmCoordinator(agents)
    _, swarm_msgs = swarm.run(task)
    results["Swarm"] = len(swarm_msgs)

    # Debate
    print("\n--- Running Debate Pattern ---")
    arena = DebateArena(rounds=2)
    _, debate_msgs = arena.debate(f"Is this product launch feasible: {task}")
    results["Debate"] = len(debate_msgs)

    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)

    print("\n| Architecture | Messages | Best For                        |")
    print("|--------------|----------|----------------------------------|")
    print(f"| Supervisor   | {results['Supervisor']:8} | Structured workflows, QA        |")
    print(f"| Swarm        | {results['Swarm']:8} | Flexible, expertise-based       |")
    print(f"| Debate       | {results['Debate']:8} | Balanced analysis, truth-finding|")

    print("\n--- Recommendations ---")
    print("1. Supervisor: Use when you need oversight and quality control")
    print("2. Swarm: Use when tasks need to flow to experts organically")
    print("3. Debate: Use when you need balanced perspectives on decisions")
    print("4. Hierarchical: Use for large organizations with multiple teams")
    print("5. Hybrid: Combine patterns based on specific requirements")


def show_usage():
    """Show usage information."""
    print(__doc__)
    print("\nAvailable demos:")
    print("  demo1 - Supervisor pattern")
    print("  demo2 - Swarm pattern")
    print("  demo3 - Debate pattern")
    print("  demo4 - Compare all architectures")


def main():
    """Main entry point."""
    STORAGE_DIR.mkdir(exist_ok=True)

    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_supervisor()
    elif command == "demo2":
        demo_2_swarm()
    elif command == "demo3":
        demo_3_debate()
    elif command == "demo4":
        demo_4_compare()
    elif command == "all":
        demo_1_supervisor()
        demo_2_swarm()
        demo_3_debate()
        demo_4_compare()
    else:
        print(f"Unknown command: {command}")
        show_usage()


if __name__ == "__main__":
    main()
