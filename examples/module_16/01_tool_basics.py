#!/usr/bin/env python3
"""
Module 16, Example 1: Tool Basics and Function Schemas

This example demonstrates the fundamentals of creating tools in LangChain:
1. Using the @tool decorator (simplest approach)
2. Using StructuredTool for more control
3. Using BaseTool for maximum flexibility
4. Inspecting tool schemas

Tools are the bridge between LLMs and external functionality.
The LLM decides when and how to call tools based on their descriptions.

Usage:
    python 01_tool_basics.py

No API key required - this example focuses on tool creation.
"""

from typing import Optional, Type
from langchain_core.tools import tool, StructuredTool, BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
import json


# ============================================================================
# METHOD 1: The @tool Decorator (Simplest)
# ============================================================================

@tool
def simple_calculator(expression: str) -> str:
    """Calculate a mathematical expression.

    Use this tool when the user needs to perform mathematical calculations.
    Supports basic operations: +, -, *, /, ** (power), % (modulo).

    Args:
        expression: A mathematical expression like "2 + 2" or "10 * 5"

    Returns:
        The result of the calculation as a string.
    """
    try:
        # WARNING: eval() is dangerous in production!
        # Use a safe parser like ast.literal_eval or numexpr
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Only numbers and basic operators allowed"
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def get_word_count(text: str, count_type: str = "words") -> str:
    """Count words, characters, or sentences in text.

    Use this when the user wants to analyze text length or statistics.

    Args:
        text: The text to analyze
        count_type: What to count - 'words', 'characters', or 'sentences'

    Returns:
        The count as a formatted string.
    """
    if count_type == "words":
        count = len(text.split())
        return f"Word count: {count}"
    elif count_type == "characters":
        count = len(text)
        return f"Character count: {count}"
    elif count_type == "sentences":
        count = text.count('.') + text.count('!') + text.count('?')
        return f"Sentence count: {count}"
    else:
        return f"Unknown count type: {count_type}. Use 'words', 'characters', or 'sentences'"


# ============================================================================
# METHOD 2: StructuredTool (More Control)
# ============================================================================

class TemperatureConversionInput(BaseModel):
    """Input schema for temperature conversion."""
    value: float = Field(description="The temperature value to convert")
    from_unit: str = Field(
        description="Source unit: 'celsius', 'fahrenheit', or 'kelvin'"
    )
    to_unit: str = Field(
        description="Target unit: 'celsius', 'fahrenheit', or 'kelvin'"
    )


def convert_temperature_impl(
    value: float,
    from_unit: str,
    to_unit: str
) -> str:
    """Implementation of temperature conversion."""
    # First convert to Celsius as intermediate
    if from_unit == "celsius":
        celsius = value
    elif from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        return f"Unknown source unit: {from_unit}"

    # Then convert from Celsius to target
    if to_unit == "celsius":
        result = celsius
    elif to_unit == "fahrenheit":
        result = celsius * 9 / 5 + 32
    elif to_unit == "kelvin":
        result = celsius + 273.15
    else:
        return f"Unknown target unit: {to_unit}"

    return f"{value}°{from_unit[0].upper()} = {result:.2f}°{to_unit[0].upper()}"


# Create the tool with StructuredTool
temperature_converter = StructuredTool.from_function(
    func=convert_temperature_impl,
    name="temperature_converter",
    description="""Convert temperatures between Celsius, Fahrenheit, and Kelvin.
    Use this when the user wants to convert temperature values between different units.
    Examples: "Convert 100°F to Celsius" or "What is 0°C in Kelvin?" """,
    args_schema=TemperatureConversionInput,
    return_direct=False  # LLM will process the result
)


# ============================================================================
# METHOD 3: BaseTool Subclass (Maximum Flexibility)
# ============================================================================

class DateCalculatorInput(BaseModel):
    """Input schema for date calculations."""
    operation: str = Field(
        description="Operation: 'days_between', 'add_days', or 'day_of_week'"
    )
    date1: str = Field(description="First date in YYYY-MM-DD format")
    date2: Optional[str] = Field(
        default=None,
        description="Second date (for days_between) or days to add (for add_days)"
    )


class DateCalculatorTool(BaseTool):
    """A comprehensive date calculation tool."""

    name: str = "date_calculator"
    description: str = """Perform date calculations.

    Operations:
    - 'days_between': Calculate days between two dates (needs date1 and date2)
    - 'add_days': Add/subtract days from a date (date2 should be number of days)
    - 'day_of_week': Get the day of the week for a date

    Dates should be in YYYY-MM-DD format (e.g., '2024-01-15').
    """
    args_schema: Type[BaseModel] = DateCalculatorInput

    def _run(
        self,
        operation: str,
        date1: str,
        date2: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the date calculation."""
        from datetime import datetime, timedelta

        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")

            if operation == "days_between":
                if not date2:
                    return "Error: days_between requires two dates"
                d2 = datetime.strptime(date2, "%Y-%m-%d")
                diff = abs((d2 - d1).days)
                return f"Days between {date1} and {date2}: {diff}"

            elif operation == "add_days":
                if not date2:
                    return "Error: add_days requires number of days"
                days = int(date2)
                result = d1 + timedelta(days=days)
                return f"{date1} + {days} days = {result.strftime('%Y-%m-%d')}"

            elif operation == "day_of_week":
                day_name = d1.strftime("%A")
                return f"{date1} is a {day_name}"

            else:
                return f"Unknown operation: {operation}"

        except ValueError as e:
            return f"Error: {str(e)}. Use YYYY-MM-DD format for dates."

    async def _arun(
        self,
        operation: str,
        date1: str,
        date2: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version (required for async agents)."""
        return self._run(operation, date1, date2, run_manager)


# Instantiate the tool
date_calculator = DateCalculatorTool()


# ============================================================================
# DEMO: Inspect Tool Schemas
# ============================================================================

def print_tool_info(tool_obj, name: str):
    """Print detailed information about a tool."""
    print(f"\n{'='*60}")
    print(f"📦 {name}")
    print('='*60)

    print(f"\n📌 Name: {tool_obj.name}")
    print(f"\n📝 Description:\n{tool_obj.description}")

    # Get the schema
    if hasattr(tool_obj, 'args_schema') and tool_obj.args_schema:
        schema = tool_obj.args_schema.model_json_schema()
        print(f"\n🔧 Parameters Schema:")
        print(json.dumps(schema, indent=2))

    # Show return type if available
    if hasattr(tool_obj, 'return_direct'):
        print(f"\n↩️  Return Direct: {tool_obj.return_direct}")


def demo_tools():
    """Demonstrate each tool in action."""
    print("\n" + "="*60)
    print("🎯 TOOL DEMONSTRATIONS")
    print("="*60)

    # Demo 1: Simple Calculator
    print("\n📊 Calculator Tool:")
    print(f"   Input: '15 * 7 + 3'")
    print(f"   Output: {simple_calculator.invoke({'expression': '15 * 7 + 3'})}")

    print(f"\n   Input: '2 ** 10'")
    print(f"   Output: {simple_calculator.invoke({'expression': '2 ** 10'})}")

    # Demo 2: Word Count
    print("\n📝 Word Count Tool:")
    sample_text = "Hello world. This is a test. How many words?"
    print(f"   Text: '{sample_text}'")
    print(f"   Words: {get_word_count.invoke({'text': sample_text, 'count_type': 'words'})}")
    print(f"   Sentences: {get_word_count.invoke({'text': sample_text, 'count_type': 'sentences'})}")

    # Demo 3: Temperature Converter
    print("\n🌡️  Temperature Converter Tool:")
    print(f"   Input: 100°F to Celsius")
    print(f"   Output: {temperature_converter.invoke({'value': 100, 'from_unit': 'fahrenheit', 'to_unit': 'celsius'})}")

    print(f"\n   Input: 0°C to Kelvin")
    print(f"   Output: {temperature_converter.invoke({'value': 0, 'from_unit': 'celsius', 'to_unit': 'kelvin'})}")

    # Demo 4: Date Calculator
    print("\n📅 Date Calculator Tool:")
    print(f"   Days between 2024-01-01 and 2024-12-31:")
    print(f"   {date_calculator.invoke({'operation': 'days_between', 'date1': '2024-01-01', 'date2': '2024-12-31'})}")

    print(f"\n   Add 100 days to 2024-01-01:")
    print(f"   {date_calculator.invoke({'operation': 'add_days', 'date1': '2024-01-01', 'date2': '100'})}")

    print(f"\n   What day is 2024-07-04?")
    print(f"   {date_calculator.invoke({'operation': 'day_of_week', 'date1': '2024-07-04'})}")


def main():
    """Main function demonstrating tool basics."""
    print("="*60)
    print("🔧 LangChain Tool Basics - Module 16, Example 1")
    print("="*60)
    print("""
    This example demonstrates three ways to create LangChain tools:

    1. @tool decorator - Quick and simple for basic tools
    2. StructuredTool - More control over schema and behavior
    3. BaseTool class - Maximum flexibility for complex tools

    Each method produces a tool that LLMs can call to extend
    their capabilities beyond text generation.
    """)

    # Collect all tools
    all_tools = [
        (simple_calculator, "@tool Decorator"),
        (get_word_count, "@tool Decorator"),
        (temperature_converter, "StructuredTool"),
        (date_calculator, "BaseTool Subclass")
    ]

    # Show tool information
    print("\n" + "="*60)
    print("📋 TOOL SCHEMAS")
    print("="*60)
    print("""
    Tool schemas tell the LLM:
    - What the tool is called
    - What it does (description is CRUCIAL!)
    - What parameters it accepts
    - What types those parameters should be
    """)

    for tool_obj, method in all_tools:
        print_tool_info(tool_obj, f"{tool_obj.name} ({method})")

    # Demonstrate tools
    demo_tools()

    # Summary
    print("\n" + "="*60)
    print("📚 KEY TAKEAWAYS")
    print("="*60)
    print("""
    1. @tool decorator: Fastest way to create tools
       - Uses docstring as description
       - Infers schema from type hints
       - Best for simple tools

    2. StructuredTool: Balance of control and simplicity
       - Explicit schema with Pydantic
       - Reusable with different functions
       - Best for well-defined inputs

    3. BaseTool subclass: Full customization
       - Override _run and _arun methods
       - Custom validation and logic
       - Best for complex tools

    ⚠️  Remember: The DESCRIPTION is what the LLM uses to
        decide when to call your tool. Make it clear!
    """)


if __name__ == "__main__":
    main()
