#!/usr/bin/env python3
"""
Module 16, Example 2: Custom LangChain Tools

This example demonstrates building practical, production-ready tools:
1. Developer tools (file operations, code search)
2. API integration tools (weather, web search simulation)
3. Error handling patterns
4. Tool validation and security
5. Async tools for parallel execution

Usage:
    python 02_custom_tools.py

No API key required for demos - uses simulated responses.
"""

import os
import subprocess
import asyncio
import json
from typing import Optional, List, Dict, Any, Type
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool, StructuredTool, BaseTool, ToolException
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# DEVELOPER TOOLS
# ============================================================================

@tool
def read_file(file_path: str, max_lines: int = 100) -> str:
    """Read the contents of a file.

    Use this to examine source code, configuration files, logs,
    or any text file. Returns the first N lines.

    Args:
        file_path: Path to the file (relative or absolute)
        max_lines: Maximum lines to read (default: 100)

    Returns:
        File contents or error message.
    """
    try:
        path = Path(file_path).resolve()

        # Security: prevent reading sensitive files
        sensitive_patterns = ['.env', 'credentials', 'secret', '.ssh', 'password']
        if any(p in str(path).lower() for p in sensitive_patterns):
            return "⚠️ Security: Cannot read potentially sensitive files"

        if not path.exists():
            return f"❌ File not found: {file_path}"

        if not path.is_file():
            return f"❌ Not a file: {file_path}"

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[:max_lines]
            content = ''.join(lines)

            if len(lines) == max_lines:
                total_lines = sum(1 for _ in open(path))
                content += f"\n\n... (showing {max_lines} of {total_lines} lines)"

            return content

    except PermissionError:
        return f"❌ Permission denied: {file_path}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


@tool
def list_directory(directory: str = ".", pattern: str = "*") -> str:
    """List files and directories in a path.

    Use this to explore directory structure, find files,
    or understand project layout.

    Args:
        directory: Directory path to list (default: current)
        pattern: Glob pattern to filter (e.g., "*.py", "*.md")

    Returns:
        List of files/directories with metadata.
    """
    try:
        path = Path(directory).resolve()

        if not path.exists():
            return f"❌ Directory not found: {directory}"

        if not path.is_dir():
            return f"❌ Not a directory: {directory}"

        items = list(path.glob(pattern))[:50]  # Limit results

        if not items:
            return f"No files matching '{pattern}' in {directory}"

        result = [f"📁 Contents of {path}:\n"]
        for item in sorted(items):
            if item.is_dir():
                result.append(f"  📂 {item.name}/")
            else:
                size = item.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                result.append(f"  📄 {item.name} ({size_str})")

        if len(items) == 50:
            result.append("\n  ... (limited to 50 items)")

        return '\n'.join(result)

    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"


@tool
def search_in_files(
    pattern: str,
    directory: str = ".",
    file_extension: str = ".py"
) -> str:
    """Search for a pattern in files using grep-like functionality.

    Use this to find function definitions, imports, variable usage,
    TODO comments, or any text pattern across files.

    Args:
        pattern: Text or regex pattern to search for
        directory: Directory to search in (default: current)
        file_extension: File extension to filter (e.g., ".py", ".js")

    Returns:
        Matching lines with file paths and line numbers.
    """
    try:
        path = Path(directory).resolve()

        if not path.exists():
            return f"❌ Directory not found: {directory}"

        results = []
        file_count = 0
        match_count = 0

        for file_path in path.rglob(f"*{file_extension}"):
            if file_count >= 100:  # Limit files searched
                break

            # Skip hidden and common non-source directories
            if any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv']
                   for part in file_path.parts):
                continue

            file_count += 1

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.lower() in line.lower():
                            match_count += 1
                            if match_count <= 30:  # Limit matches shown
                                rel_path = file_path.relative_to(path)
                                results.append(f"{rel_path}:{line_num}: {line.strip()[:100]}")
            except Exception:
                continue

        if not results:
            return f"No matches for '{pattern}' in {file_extension} files"

        header = f"Found {match_count} matches in {file_count} files:\n\n"
        content = '\n'.join(results)

        if match_count > 30:
            content += f"\n\n... ({match_count - 30} more matches not shown)"

        return header + content

    except Exception as e:
        return f"❌ Error searching: {str(e)}"


# ============================================================================
# SAFE SHELL COMMAND TOOL
# ============================================================================

class SafeShellInput(BaseModel):
    """Input schema for safe shell commands."""
    command: str = Field(description="The shell command to execute")

    @field_validator('command')
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Validate command is safe to execute."""
        # Whitelist of allowed command prefixes
        allowed_prefixes = [
            'git ', 'git status', 'git log', 'git diff', 'git branch',
            'python ', 'python3 ',
            'pip list', 'pip show',
            'ls ', 'pwd', 'echo ', 'date', 'whoami',
            'pytest ', 'npm test', 'npm run',
            'cat ', 'head ', 'tail ', 'wc ',
        ]

        if not any(v.strip().startswith(p) for p in allowed_prefixes):
            raise ValueError(
                f"Command not in whitelist. Allowed: git, python, pip list, ls, pwd, etc."
            )

        # Block dangerous patterns even in allowed commands
        dangerous = [
            'rm ', 'rm -', 'rmdir',
            '> /', '| rm', '| sudo',
            'sudo', 'chmod', 'chown',
            '; rm', '&& rm', '|| rm',
            '--delete', '--force',
        ]

        if any(d in v for d in dangerous):
            raise ValueError(f"Command contains blocked pattern")

        return v


@tool(args_schema=SafeShellInput)
def run_safe_command(command: str) -> str:
    """Execute a safe, whitelisted shell command.

    Use this for:
    - Git operations: status, log, diff, branch
    - Python scripts: python script.py
    - Project info: ls, pwd, pip list
    - Tests: pytest, npm test

    Blocked operations: rm, sudo, chmod, file deletion

    Args:
        command: The shell command (must be in whitelist)

    Returns:
        Command output or error message.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"

        if not output.strip():
            output = "✅ Command completed with no output"

        return output[:5000]  # Limit output size

    except subprocess.TimeoutExpired:
        return "❌ Command timed out (30 second limit)"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ============================================================================
# API INTEGRATION TOOLS (Simulated for demo)
# ============================================================================

@tool
def get_weather(location: str, units: str = "metric") -> str:
    """Get current weather for a location.

    Use when user asks about weather, temperature, or conditions
    for a specific city or location.

    Args:
        location: City name (e.g., "Tokyo", "New York", "London")
        units: 'metric' (Celsius) or 'imperial' (Fahrenheit)

    Returns:
        Weather information or error message.

    Note: This is a simulated response for demo purposes.
    """
    # Simulated weather data
    weather_data = {
        "tokyo": {"temp": 18, "condition": "Partly Cloudy", "humidity": 65},
        "new york": {"temp": 22, "condition": "Sunny", "humidity": 45},
        "london": {"temp": 14, "condition": "Rainy", "humidity": 80},
        "paris": {"temp": 16, "condition": "Cloudy", "humidity": 70},
        "sydney": {"temp": 25, "condition": "Clear", "humidity": 55},
    }

    loc_lower = location.lower()
    data = weather_data.get(loc_lower)

    if not data:
        # Default weather for unknown locations
        data = {"temp": 20, "condition": "Clear", "humidity": 50}

    temp = data["temp"]
    if units == "imperial":
        temp = temp * 9/5 + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"

    return f"""🌤️ Weather for {location.title()}:
    Temperature: {temp}{unit_symbol}
    Condition: {data['condition']}
    Humidity: {data['humidity']}%
    (Simulated data for demo)"""


@tool
def search_web(query: str, num_results: int = 3) -> str:
    """Search the web for information.

    Use when the user needs current information, facts,
    or data that might not be in your training data.

    Args:
        query: Search query
        num_results: Number of results to return (1-5)

    Returns:
        Search results or error message.

    Note: This is a simulated response for demo purposes.
    """
    num_results = min(max(num_results, 1), 5)

    # Simulated search results
    simulated_results = [
        {
            "title": f"Result 1 for '{query}'",
            "snippet": f"This is a simulated search result about {query}. "
                      "In production, this would contain real web content.",
            "url": "https://example.com/result1"
        },
        {
            "title": f"Result 2 for '{query}'",
            "snippet": f"Another relevant result discussing {query} with "
                      "additional context and information.",
            "url": "https://example.com/result2"
        },
        {
            "title": f"Wikipedia: {query}",
            "snippet": f"{query} is a topic with extensive documentation. "
                      "This simulated result represents Wikipedia content.",
            "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        },
    ]

    results = simulated_results[:num_results]
    formatted = [f"🔍 Web Search Results for '{query}':\n"]

    for i, r in enumerate(results, 1):
        formatted.append(f"\n{i}. {r['title']}")
        formatted.append(f"   {r['snippet']}")
        formatted.append(f"   URL: {r['url']}")

    formatted.append("\n\n(Simulated results for demo - integrate real search API for production)")

    return '\n'.join(formatted)


# ============================================================================
# ASYNC TOOLS FOR PARALLEL EXECUTION
# ============================================================================

class AsyncWeatherInput(BaseModel):
    """Input for async weather tool."""
    locations: List[str] = Field(
        description="List of city names to get weather for"
    )


class AsyncWeatherTool(BaseTool):
    """Get weather for multiple locations in parallel."""

    name: str = "get_weather_multi"
    description: str = """Get weather for multiple locations simultaneously.

    Use this when the user asks about weather in multiple cities.
    More efficient than calling get_weather multiple times.

    Args:
        locations: List of city names (e.g., ["Tokyo", "London", "Paris"])
    """
    args_schema: Type[BaseModel] = AsyncWeatherInput

    def _run(
        self,
        locations: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous version - runs async internally."""
        return asyncio.run(self._arun(locations, run_manager))

    async def _arun(
        self,
        locations: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Fetch weather for all locations in parallel."""

        async def fetch_weather(location: str) -> dict:
            """Simulate async API call."""
            await asyncio.sleep(0.1)  # Simulate network latency

            weather_data = {
                "tokyo": {"temp": 18, "condition": "Partly Cloudy"},
                "london": {"temp": 14, "condition": "Rainy"},
                "paris": {"temp": 16, "condition": "Cloudy"},
                "new york": {"temp": 22, "condition": "Sunny"},
            }

            data = weather_data.get(location.lower(), {"temp": 20, "condition": "Clear"})
            return {"location": location, **data}

        # Fetch all in parallel
        tasks = [fetch_weather(loc) for loc in locations[:5]]
        results = await asyncio.gather(*tasks)

        # Format results
        lines = ["🌍 Weather Report:\n"]
        for r in results:
            lines.append(f"  {r['location']}: {r['temp']}°C, {r['condition']}")

        lines.append("\n(Fetched in parallel - simulated)")
        return '\n'.join(lines)


async_weather_tool = AsyncWeatherTool()


# ============================================================================
# ERROR HANDLING PATTERNS
# ============================================================================

def custom_error_handler(error: Exception) -> str:
    """Convert errors into helpful messages for the LLM."""
    error_msg = str(error)

    # Provide specific guidance based on error type
    if "not found" in error_msg.lower():
        return f"""❌ Error: {error_msg}

Suggestions:
- Check if the file/path exists
- Verify spelling and case sensitivity
- Try listing the directory first with list_directory"""

    elif "permission" in error_msg.lower():
        return f"""❌ Permission Error: {error_msg}

Suggestions:
- This file may be protected
- Try a different file or directory"""

    elif "timeout" in error_msg.lower():
        return f"""❌ Timeout Error: {error_msg}

Suggestions:
- The operation took too long
- Try a simpler query or smaller scope"""

    else:
        return f"""❌ Error: {error_msg}

Please try a different approach or ask the user for clarification."""


@tool
def risky_operation(action: str) -> str:
    """A tool that demonstrates error handling patterns.

    Args:
        action: The action to perform ('succeed', 'fail', 'timeout')

    Returns:
        Success message or formatted error message.
    """
    if action == "succeed":
        return "✅ Operation completed successfully!"
    elif action == "fail":
        return custom_error_handler(Exception("File not found: /nonexistent/path"))
    elif action == "timeout":
        return custom_error_handler(Exception("Operation timed out after 30 seconds"))
    else:
        return custom_error_handler(Exception(f"Unknown action: {action}"))


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_developer_tools():
    """Demonstrate developer tools."""
    print("\n" + "="*60)
    print("🛠️  DEVELOPER TOOLS DEMO")
    print("="*60)

    # List directory
    print("\n📁 List Directory:")
    print(list_directory.invoke({"directory": ".", "pattern": "*.py"}))

    # Read file (this file)
    print("\n📄 Read File (first 20 lines of this script):")
    result = read_file.invoke({"file_path": __file__, "max_lines": 20})
    print(result[:500] + "...")

    # Search in files
    print("\n🔍 Search for 'def ' in Python files:")
    print(search_in_files.invoke({
        "pattern": "def ",
        "directory": ".",
        "file_extension": ".py"
    }))


def demo_safe_commands():
    """Demonstrate safe shell commands."""
    print("\n" + "="*60)
    print("💻 SAFE SHELL COMMANDS DEMO")
    print("="*60)

    # Safe commands
    print("\n✅ Safe: pwd")
    print(run_safe_command.invoke({"command": "pwd"}))

    print("\n✅ Safe: git status (if in git repo)")
    print(run_safe_command.invoke({"command": "git status"}))

    # Blocked command (will be caught by validation)
    print("\n❌ Blocked: rm -rf /")
    try:
        result = run_safe_command.invoke({"command": "rm -rf /"})
        print(result)
    except Exception as e:
        print(f"Blocked: {e}")


def demo_api_tools():
    """Demonstrate API integration tools."""
    print("\n" + "="*60)
    print("🌐 API INTEGRATION TOOLS DEMO")
    print("="*60)

    # Weather
    print("\n🌤️ Weather Tool:")
    print(get_weather.invoke({"location": "Tokyo", "units": "metric"}))

    print("\n" + get_weather.invoke({"location": "New York", "units": "imperial"}))

    # Web search
    print("\n🔍 Web Search Tool:")
    print(search_web.invoke({"query": "LangChain tools", "num_results": 2}))


def demo_async_tools():
    """Demonstrate async/parallel tools."""
    print("\n" + "="*60)
    print("⚡ ASYNC PARALLEL TOOLS DEMO")
    print("="*60)

    print("\n🌍 Get weather for multiple cities in parallel:")
    result = async_weather_tool.invoke({
        "locations": ["Tokyo", "London", "Paris", "New York"]
    })
    print(result)


def demo_error_handling():
    """Demonstrate error handling patterns."""
    print("\n" + "="*60)
    print("🛡️ ERROR HANDLING DEMO")
    print("="*60)

    print("\n✅ Success case:")
    print(risky_operation.invoke({"action": "succeed"}))

    print("\n❌ Failure case:")
    print(risky_operation.invoke({"action": "fail"}))

    print("\n⏱️ Timeout case:")
    print(risky_operation.invoke({"action": "timeout"}))


def main():
    """Main function demonstrating custom tools."""
    print("="*60)
    print("🔧 Custom LangChain Tools - Module 16, Example 2")
    print("="*60)
    print("""
    This example demonstrates building production-ready tools:

    1. Developer Tools - File operations, search, shell commands
    2. API Tools - Weather, web search (simulated)
    3. Async Tools - Parallel execution for efficiency
    4. Error Handling - Graceful degradation patterns
    5. Security - Input validation and whitelisting
    """)

    # Run all demos
    demo_developer_tools()
    demo_safe_commands()
    demo_api_tools()
    demo_async_tools()
    demo_error_handling()

    # Summary
    print("\n" + "="*60)
    print("📚 KEY TAKEAWAYS")
    print("="*60)
    print("""
    1. SECURITY FIRST
       - Validate all inputs with Pydantic
       - Whitelist allowed operations
       - Block dangerous patterns
       - Never trust user input directly

    2. ERROR HANDLING
       - Use handle_tool_error for graceful failures
       - Provide helpful error messages
       - Guide the LLM to try alternatives

    3. ASYNC FOR EFFICIENCY
       - Use async tools when calling external APIs
       - Parallel execution saves time
       - LLMs can request multiple tool calls

    4. CLEAR DESCRIPTIONS
       - Explain WHEN to use the tool
       - Document all parameters
       - Include examples in descriptions

    5. LIMIT OUTPUT
       - Truncate large outputs
       - Set reasonable defaults
       - Prevent overwhelming the LLM
    """)


if __name__ == "__main__":
    main()
