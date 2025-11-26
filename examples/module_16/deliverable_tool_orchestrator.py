#!/usr/bin/env python3
"""
Module 16 Deliverable: Tool Orchestrator

A comprehensive tool orchestration system for building and managing
AI agents with custom tools. Features tool creation, agent configuration,
execution logging, and performance analysis.

Features:
- Tool registry with validation and categorization
- Agent builder with customizable behavior
- Execution logging and analytics
- Tool performance benchmarking
- Interactive agent mode

Usage:
    python deliverable_tool_orchestrator.py demo1  # Tool registry demo
    python deliverable_tool_orchestrator.py demo2  # Agent execution demo
    python deliverable_tool_orchestrator.py demo3  # Performance analysis
    python deliverable_tool_orchestrator.py chat   # Interactive chat mode

Requirements:
    pip install langchain-core langchain-google-genai pydantic

Author: Neural Dojo - Module 16
"""

import os
import sys
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Callable, Type
from datetime import datetime
from pathlib import Path
from enum import Enum
import statistics

from langchain_core.tools import tool, BaseTool, StructuredTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


# ============================================================================
# CONFIGURATION
# ============================================================================

STORAGE_DIR = Path(".tool_orchestrator")
TOOLS_FILE = STORAGE_DIR / "tools.json"
EXECUTIONS_FILE = STORAGE_DIR / "executions.json"
ANALYTICS_FILE = STORAGE_DIR / "analytics.json"


class ToolCategory(str, Enum):
    """Categories for organizing tools."""
    MATH = "math"
    DATA = "data"
    WEB = "web"
    FILE = "file"
    SYSTEM = "system"
    CUSTOM = "custom"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ToolDefinition:
    """Definition of a tool in the registry."""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    call_count: int = 0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    last_used: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolDefinition":
        return cls(**data)


@dataclass
class ToolExecution:
    """Record of a single tool execution."""
    tool_name: str
    input_args: Dict[str, Any]
    output: str
    latency_ms: float
    success: bool
    error_message: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolExecution":
        return cls(**data)


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    description: str
    tools: List[str]
    system_prompt: str
    max_iterations: int = 5
    temperature: float = 0.0
    provider: str = "google"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        return cls(**data)


@dataclass
class ToolAnalytics:
    """Analytics for tool usage."""
    tool_name: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    error_rate: float
    last_24h_calls: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# PERSISTENCE
# ============================================================================

def ensure_storage():
    """Ensure storage directory exists."""
    STORAGE_DIR.mkdir(exist_ok=True)


def save_json(path: Path, data: Any):
    """Save data to JSON file."""
    ensure_storage()
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(path: Path, default: Any = None) -> Any:
    """Load data from JSON file."""
    if not path.exists():
        return default if default is not None else {}
    with open(path, 'r') as f:
        return json.load(f)


# ============================================================================
# BUILT-IN TOOLS
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression.

    Supports: +, -, *, /, ** (power), % (modulo), parentheses.

    Args:
        expression: Math expression like "2 + 2" or "(10 + 5) * 3"

    Returns:
        The calculated result.
    """
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Error: Only numbers and operators (+, -, *, /, **, %) allowed"
        result = eval(expression)
        return f"{result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def string_processor(text: str, operation: str = "length") -> str:
    """Process text strings.

    Operations: length, upper, lower, reverse, words

    Args:
        text: The text to process
        operation: What to do (length/upper/lower/reverse/words)

    Returns:
        Processed text or count.
    """
    ops = {
        "length": lambda t: str(len(t)),
        "upper": lambda t: t.upper(),
        "lower": lambda t: t.lower(),
        "reverse": lambda t: t[::-1],
        "words": lambda t: str(len(t.split())),
    }
    func = ops.get(operation)
    if not func:
        return f"Unknown operation: {operation}. Use: length, upper, lower, reverse, words"
    return func(text)


@tool
def datetime_tool(operation: str = "now", value: str = "") -> str:
    """Work with dates and times.

    Operations:
    - now: Current date and time
    - date: Current date only
    - time: Current time only
    - weekday: Day of the week for a date (value=YYYY-MM-DD)
    - diff: Days between two dates (value=YYYY-MM-DD,YYYY-MM-DD)

    Args:
        operation: What to do (now/date/time/weekday/diff)
        value: Additional value for some operations

    Returns:
        Date/time information.
    """
    from datetime import datetime as dt, timedelta

    now = dt.now()

    if operation == "now":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif operation == "date":
        return now.strftime("%Y-%m-%d")
    elif operation == "time":
        return now.strftime("%H:%M:%S")
    elif operation == "weekday":
        if value:
            try:
                d = dt.strptime(value, "%Y-%m-%d")
                return d.strftime("%A")
            except:
                return "Error: Use YYYY-MM-DD format"
        return now.strftime("%A")
    elif operation == "diff":
        try:
            d1, d2 = value.split(",")
            date1 = dt.strptime(d1.strip(), "%Y-%m-%d")
            date2 = dt.strptime(d2.strip(), "%Y-%m-%d")
            return str(abs((date2 - date1).days))
        except:
            return "Error: Use format YYYY-MM-DD,YYYY-MM-DD"
    else:
        return f"Unknown operation: {operation}"


@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units.

    Supported: km/mi, kg/lb, c/f (temperature), m/ft

    Args:
        value: The value to convert
        from_unit: Source unit (km, mi, kg, lb, c, f, m, ft)
        to_unit: Target unit

    Returns:
        Converted value.
    """
    conversions = {
        ("km", "mi"): lambda v: v * 0.621371,
        ("mi", "km"): lambda v: v * 1.60934,
        ("kg", "lb"): lambda v: v * 2.20462,
        ("lb", "kg"): lambda v: v * 0.453592,
        ("c", "f"): lambda v: v * 9/5 + 32,
        ("f", "c"): lambda v: (v - 32) * 5/9,
        ("m", "ft"): lambda v: v * 3.28084,
        ("ft", "m"): lambda v: v * 0.3048,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return f"Unknown conversion: {from_unit} to {to_unit}"

    result = conversions[key](value)
    return f"{value} {from_unit} = {result:.4f} {to_unit}"


@tool
def json_helper(operation: str, data: str) -> str:
    """Work with JSON data.

    Operations:
    - validate: Check if JSON is valid
    - format: Pretty-print JSON
    - keys: List top-level keys
    - count: Count top-level items

    Args:
        operation: What to do (validate/format/keys/count)
        data: JSON string to process

    Returns:
        Result of the operation.
    """
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        if operation == "validate":
            return f"Invalid JSON: {str(e)}"
        return f"Error parsing JSON: {str(e)}"

    if operation == "validate":
        return "Valid JSON"
    elif operation == "format":
        return json.dumps(parsed, indent=2)
    elif operation == "keys":
        if isinstance(parsed, dict):
            return ", ".join(parsed.keys())
        return "Error: JSON is not an object"
    elif operation == "count":
        if isinstance(parsed, (list, dict)):
            return str(len(parsed))
        return "1"
    else:
        return f"Unknown operation: {operation}"


# Map of all built-in tools
BUILTIN_TOOLS = {
    "calculator": calculator,
    "string_processor": string_processor,
    "datetime_tool": datetime_tool,
    "unit_converter": unit_converter,
    "json_helper": json_helper,
}


# ============================================================================
# TOOL REGISTRY
# ============================================================================

class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.definitions: Dict[str, ToolDefinition] = {}
        self.load_builtin_tools()
        self.load_definitions()

    def load_builtin_tools(self):
        """Load all built-in tools."""
        for name, tool_obj in BUILTIN_TOOLS.items():
            self.tools[name] = tool_obj
            if name not in self.definitions:
                self.definitions[name] = ToolDefinition(
                    name=name,
                    description=tool_obj.description.split('\n')[0],
                    category=self._infer_category(name),
                    parameters=self._extract_params(tool_obj),
                )

    def load_definitions(self):
        """Load tool definitions from storage."""
        data = load_json(TOOLS_FILE, {})
        for name, defn in data.items():
            if name not in self.definitions:
                self.definitions[name] = ToolDefinition.from_dict(defn)

    def save_definitions(self):
        """Save tool definitions to storage."""
        data = {name: defn.to_dict() for name, defn in self.definitions.items()}
        save_json(TOOLS_FILE, data)

    def _infer_category(self, name: str) -> str:
        """Infer tool category from name."""
        categories = {
            "calculator": ToolCategory.MATH.value,
            "string": ToolCategory.DATA.value,
            "datetime": ToolCategory.DATA.value,
            "unit": ToolCategory.MATH.value,
            "json": ToolCategory.DATA.value,
            "file": ToolCategory.FILE.value,
            "web": ToolCategory.WEB.value,
        }
        for key, cat in categories.items():
            if key in name.lower():
                return cat
        return ToolCategory.CUSTOM.value

    def _extract_params(self, tool_obj: Any) -> Dict[str, Any]:
        """Extract parameter schema from tool."""
        if hasattr(tool_obj, 'args_schema') and tool_obj.args_schema:
            return tool_obj.args_schema.model_json_schema().get('properties', {})
        return {}

    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_tools(self, names: List[str]) -> List[Any]:
        """Get multiple tools by name."""
        return [self.tools[n] for n in names if n in self.tools]

    def list_tools(self) -> List[ToolDefinition]:
        """List all tool definitions."""
        return list(self.definitions.values())

    def get_by_category(self, category: str) -> List[ToolDefinition]:
        """Get tools by category."""
        return [d for d in self.definitions.values() if d.category == category]

    def record_execution(self, tool_name: str, latency_ms: float, success: bool):
        """Record a tool execution for analytics."""
        if tool_name in self.definitions:
            defn = self.definitions[tool_name]
            defn.call_count += 1
            defn.last_used = datetime.now().isoformat()
            if not success:
                defn.error_count += 1
            # Update rolling average
            old_avg = defn.avg_latency_ms
            defn.avg_latency_ms = old_avg + (latency_ms - old_avg) / defn.call_count
            self.save_definitions()


# ============================================================================
# EXECUTION TRACKER
# ============================================================================

class ExecutionTracker:
    """Track tool executions for analytics."""

    def __init__(self):
        self.executions: List[ToolExecution] = []
        self.load_executions()

    def load_executions(self):
        """Load executions from storage."""
        data = load_json(EXECUTIONS_FILE, [])
        self.executions = [ToolExecution.from_dict(e) for e in data]

    def save_executions(self):
        """Save executions to storage."""
        # Keep only last 1000 executions
        recent = self.executions[-1000:]
        save_json(EXECUTIONS_FILE, [e.to_dict() for e in recent])

    def record(self, execution: ToolExecution):
        """Record a tool execution."""
        self.executions.append(execution)
        self.save_executions()

    def get_analytics(self, tool_name: str) -> Optional[ToolAnalytics]:
        """Get analytics for a specific tool."""
        tool_execs = [e for e in self.executions if e.tool_name == tool_name]
        if not tool_execs:
            return None

        latencies = [e.latency_ms for e in tool_execs]
        successful = [e for e in tool_execs if e.success]
        failed = [e for e in tool_execs if not e.success]

        # Count last 24h
        cutoff = datetime.now().timestamp() - 86400
        last_24h = [
            e for e in tool_execs
            if datetime.fromisoformat(e.timestamp).timestamp() > cutoff
        ]

        return ToolAnalytics(
            tool_name=tool_name,
            total_calls=len(tool_execs),
            successful_calls=len(successful),
            failed_calls=len(failed),
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            min_latency_ms=min(latencies) if latencies else 0,
            max_latency_ms=max(latencies) if latencies else 0,
            error_rate=len(failed) / len(tool_execs) if tool_execs else 0,
            last_24h_calls=len(last_24h),
        )

    def get_all_analytics(self) -> List[ToolAnalytics]:
        """Get analytics for all tools."""
        tool_names = set(e.tool_name for e in self.executions)
        return [self.get_analytics(name) for name in tool_names if self.get_analytics(name)]


# ============================================================================
# TOOL EXECUTOR (with tracking)
# ============================================================================

class TrackedToolExecutor:
    """Execute tools with tracking."""

    def __init__(self, registry: ToolRegistry, tracker: ExecutionTracker):
        self.registry = registry
        self.tracker = tracker

    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool and track the result."""
        tool_obj = self.registry.get_tool(tool_name)
        if not tool_obj:
            return f"Error: Tool '{tool_name}' not found"

        start_time = time.time()
        success = True
        error_msg = None
        output = ""

        try:
            output = tool_obj.invoke(args)
        except Exception as e:
            success = False
            error_msg = str(e)
            output = f"Error: {error_msg}"

        latency_ms = (time.time() - start_time) * 1000

        # Record execution
        execution = ToolExecution(
            tool_name=tool_name,
            input_args=args,
            output=output,
            latency_ms=latency_ms,
            success=success,
            error_message=error_msg,
        )
        self.tracker.record(execution)
        self.registry.record_execution(tool_name, latency_ms, success)

        return output


# ============================================================================
# AGENT BUILDER
# ============================================================================

class AgentBuilder:
    """Build and run agents with tools."""

    def __init__(self, registry: ToolRegistry, executor: TrackedToolExecutor):
        self.registry = registry
        self.executor = executor
        self.configs: Dict[str, AgentConfig] = {}

    def create_agent(
        self,
        name: str,
        tools: List[str],
        system_prompt: str = "",
        provider: str = "google"
    ) -> Optional[AgentConfig]:
        """Create an agent configuration."""
        # Validate tools exist
        for tool_name in tools:
            if tool_name not in self.registry.tools:
                print(f"⚠️ Unknown tool: {tool_name}")
                return None

        if not system_prompt:
            tool_names = ", ".join(tools)
            system_prompt = f"""You are a helpful assistant with access to these tools: {tool_names}.
Use tools when they would help answer questions accurately.
Be concise in your responses."""

        config = AgentConfig(
            name=name,
            description=f"Agent with tools: {', '.join(tools)}",
            tools=tools,
            system_prompt=system_prompt,
            provider=provider,
        )
        self.configs[name] = config
        return config

    def get_langchain_agent(self, config: AgentConfig):
        """Create a LangChain agent from config."""
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        # Get LLM
        llm = self._get_llm(config.provider)
        if not llm:
            return None

        # Get tools
        tools = self.registry.get_tools(config.tools)

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", config.system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=config.max_iterations,
            handle_parsing_errors=True,
        )

        return executor

    def _get_llm(self, provider: str):
        """Get LLM for provider."""
        if provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("❌ GOOGLE_API_KEY not set")
                return None
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                api_key=api_key
            )
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("❌ ANTHROPIC_API_KEY not set")
                return None
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0,
                api_key=api_key
            )
        return None


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo1_tool_registry():
    """Demo 1: Tool Registry and Execution."""
    print("\n" + "="*60)
    print("🔧 DEMO 1: Tool Registry and Execution")
    print("="*60)

    registry = ToolRegistry()
    tracker = ExecutionTracker()
    executor = TrackedToolExecutor(registry, tracker)

    # List all tools
    print("\n📦 Registered Tools:")
    print("-" * 40)
    for defn in registry.list_tools():
        print(f"  • {defn.name} [{defn.category}]")
        print(f"    {defn.description}")
        print()

    # Execute tools
    print("\n⚡ Tool Execution Examples:")
    print("-" * 40)

    tests = [
        ("calculator", {"expression": "15 * 7 + 3"}),
        ("string_processor", {"text": "Hello World", "operation": "upper"}),
        ("datetime_tool", {"operation": "now"}),
        ("unit_converter", {"value": 100, "from_unit": "km", "to_unit": "mi"}),
        ("json_helper", {"operation": "validate", "data": '{"name": "test"}'}),
    ]

    for tool_name, args in tests:
        result = executor.execute(tool_name, args)
        print(f"\n  {tool_name}({args})")
        print(f"  → {result}")

    # Show stats
    print("\n📊 Execution Stats:")
    print("-" * 40)
    for defn in registry.list_tools():
        if defn.call_count > 0:
            print(f"  {defn.name}: {defn.call_count} calls, avg {defn.avg_latency_ms:.2f}ms")


def demo2_agent_execution():
    """Demo 2: Agent with Tools."""
    print("\n" + "="*60)
    print("🤖 DEMO 2: Agent with Tools")
    print("="*60)

    registry = ToolRegistry()
    tracker = ExecutionTracker()
    executor = TrackedToolExecutor(registry, tracker)
    builder = AgentBuilder(registry, executor)

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️ No API key found. Showing agent configuration only.\n")

        config = builder.create_agent(
            name="math_assistant",
            tools=["calculator", "unit_converter", "datetime_tool"],
        )

        print("📋 Agent Configuration:")
        print(f"  Name: {config.name}")
        print(f"  Tools: {', '.join(config.tools)}")
        print(f"  Max Iterations: {config.max_iterations}")
        print(f"\n  System Prompt:\n  {config.system_prompt}")

        print("\n💡 To run the agent, set an API key:")
        print("  export GOOGLE_API_KEY='your-key'")
        print("  python deliverable_tool_orchestrator.py demo2")
        return

    # Create and run agent
    provider = "google" if os.getenv("GOOGLE_API_KEY") else "anthropic"

    config = builder.create_agent(
        name="math_assistant",
        tools=["calculator", "unit_converter", "datetime_tool"],
        provider=provider,
    )

    agent = builder.get_langchain_agent(config)
    if not agent:
        return

    print("\n📋 Agent Created:")
    print(f"  Name: {config.name}")
    print(f"  Tools: {', '.join(config.tools)}")

    # Test queries
    queries = [
        "What is 25 times 17?",
        "Convert 100 miles to kilometers",
        "What's the current date and time?",
    ]

    for query in queries:
        print(f"\n{'─'*40}")
        print(f"❓ {query}")
        try:
            result = agent.invoke({"input": query})
            print(f"✅ {result['output']}")
        except Exception as e:
            print(f"❌ Error: {e}")


def demo3_analytics():
    """Demo 3: Tool Performance Analytics."""
    print("\n" + "="*60)
    print("📊 DEMO 3: Performance Analytics")
    print("="*60)

    registry = ToolRegistry()
    tracker = ExecutionTracker()
    executor = TrackedToolExecutor(registry, tracker)

    # Run multiple executions for benchmarking
    print("\n🔄 Running benchmark (10 executions per tool)...")

    benchmarks = [
        ("calculator", [
            {"expression": "1 + 1"},
            {"expression": "100 * 50"},
            {"expression": "(15 + 25) * 3"},
        ]),
        ("string_processor", [
            {"text": "hello", "operation": "upper"},
            {"text": "WORLD", "operation": "lower"},
            {"text": "test", "operation": "length"},
        ]),
        ("datetime_tool", [
            {"operation": "now"},
            {"operation": "date"},
            {"operation": "weekday"},
        ]),
    ]

    for tool_name, test_cases in benchmarks:
        print(f"\n  Benchmarking {tool_name}...")
        for _ in range(3):
            for args in test_cases:
                executor.execute(tool_name, args)

    # Show analytics
    print("\n📈 Performance Analytics:")
    print("-" * 60)
    print(f"{'Tool':<20} {'Calls':<8} {'Success':<8} {'Avg (ms)':<10} {'Errors':<8}")
    print("-" * 60)

    for analytics in tracker.get_all_analytics():
        print(
            f"{analytics.tool_name:<20} "
            f"{analytics.total_calls:<8} "
            f"{analytics.successful_calls:<8} "
            f"{analytics.avg_latency_ms:<10.2f} "
            f"{analytics.failed_calls:<8}"
        )

    # Tool usage summary
    print("\n📦 Tool Usage Summary:")
    print("-" * 40)
    for defn in registry.list_tools():
        status = "✅ Active" if defn.call_count > 0 else "⚪ Unused"
        print(f"  {defn.name}: {status} ({defn.call_count} calls)")


def demo_interactive_chat():
    """Interactive chat mode with agent."""
    print("\n" + "="*60)
    print("💬 Interactive Agent Chat")
    print("="*60)

    registry = ToolRegistry()
    tracker = ExecutionTracker()
    executor = TrackedToolExecutor(registry, tracker)
    builder = AgentBuilder(registry, executor)

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️ No API key found.")
        print("Set GOOGLE_API_KEY or ANTHROPIC_API_KEY to use chat mode.")
        return

    provider = "google" if os.getenv("GOOGLE_API_KEY") else "anthropic"

    # Create agent with all tools
    config = builder.create_agent(
        name="assistant",
        tools=list(BUILTIN_TOOLS.keys()),
        system_prompt="""You are a helpful assistant with access to various tools.
Use tools when they would help answer questions accurately.
Available tools: calculator, string_processor, datetime_tool, unit_converter, json_helper.
Be helpful and concise.""",
        provider=provider,
    )

    agent = builder.get_langchain_agent(config)
    if not agent:
        return

    print(f"\n🤖 Agent ready! Using {provider}.")
    print("Available tools:", ", ".join(config.tools))
    print("\nType 'quit' to exit, 'tools' to list tools, 'stats' for analytics.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye! 👋")
                break

            if user_input.lower() == "tools":
                print("\n📦 Available Tools:")
                for name in config.tools:
                    defn = registry.definitions.get(name)
                    if defn:
                        print(f"  • {name}: {defn.description}")
                print()
                continue

            if user_input.lower() == "stats":
                print("\n📊 Session Stats:")
                for analytics in tracker.get_all_analytics():
                    print(f"  {analytics.tool_name}: {analytics.total_calls} calls")
                print()
                continue

            # Run agent
            result = agent.invoke({"input": user_input})
            print(f"\nAssistant: {result['output']}\n")

        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def print_help():
    """Print help information."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🔧 Tool Orchestrator - Module 16                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  A comprehensive tool orchestration system for AI agents.    ║
║                                                              ║
║  USAGE:                                                      ║
║    python deliverable_tool_orchestrator.py <command>         ║
║                                                              ║
║  COMMANDS:                                                   ║
║    demo1   Tool registry and direct execution                ║
║    demo2   Agent with tools (requires API key)               ║
║    demo3   Performance analytics and benchmarking            ║
║    chat    Interactive chat mode (requires API key)          ║
║    help    Show this help message                            ║
║                                                              ║
║  BUILT-IN TOOLS:                                             ║
║    • calculator      - Math expressions                      ║
║    • string_processor - Text operations                      ║
║    • datetime_tool   - Date/time functions                   ║
║    • unit_converter  - Unit conversions                      ║
║    • json_helper     - JSON operations                       ║
║                                                              ║
║  API KEYS:                                                   ║
║    export GOOGLE_API_KEY='your-key'  (for Gemini)           ║
║    export ANTHROPIC_API_KEY='your-key'  (for Claude)        ║
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
        demo1_tool_registry()
    elif command == "demo2":
        demo2_agent_execution()
    elif command == "demo3":
        demo3_analytics()
    elif command == "chat":
        demo_interactive_chat()
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
