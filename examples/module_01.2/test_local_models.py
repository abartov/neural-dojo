#!/usr/bin/env python3
"""
Module 1.2: Test Local AI Models
Tests Ollama installation and coding model quality
"""

import json
import subprocess
import sys
import time
from typing import Dict, List, Optional


def check_color_support() -> bool:
    """Check if terminal supports colors."""
    return sys.stdout.isatty()


# ANSI color codes
if check_color_support():
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
else:
    GREEN = YELLOW = RED = BLUE = BOLD = RESET = ""


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{BOLD}{BLUE}{text}{RESET}")
    print("=" * len(text))


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{YELLOW}⚠️{RESET}  {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{RED}❌{RESET} {text}")


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_installed_models() -> List[str]:
    """Get list of installed Ollama models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []

        # Parse output (skip header line)
        lines = result.stdout.strip().split("\n")[1:]
        models = []
        for line in lines:
            # First column is model name
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception as e:
        print_error(f"Failed to get models: {e}")
        return []


def test_model(model_name: str, task: str) -> Optional[Dict]:
    """
    Test a model with a coding task.

    Returns:
        Dict with 'response', 'time', and 'success' keys, or None if failed
    """
    print(f"\n  Testing {BOLD}{model_name}{RESET}...")
    print(f"  Task: {task}")

    try:
        start_time = time.time()

        result = subprocess.run(
            ["ollama", "run", model_name, task],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"  {GREEN}Response time:{RESET} {elapsed:.1f}s")
            print(f"  {GREEN}Response:{RESET}")
            # Print first 200 chars of response
            preview = response[:200] + "..." if len(response) > 200 else response
            for line in preview.split("\n"):
                print(f"    {line}")

            return {
                "response": response,
                "time": elapsed,
                "success": True,
            }
        else:
            print_error(f"Model returned error: {result.stderr}")
            return {
                "response": result.stderr,
                "time": elapsed,
                "success": False,
            }

    except subprocess.TimeoutExpired:
        print_error("Test timed out (>60s)")
        return None
    except Exception as e:
        print_error(f"Test failed: {e}")
        return None


def rate_code_quality(response: str) -> str:
    """
    Simple heuristic to rate code quality.

    Returns:
        Star rating string
    """
    score = 0

    # Check if response contains code
    if "def " in response or "function " in response or "=>" in response:
        score += 1

    # Check for type hints (Python)
    if "->" in response or ": str" in response or ": int" in response:
        score += 1

    # Check for docstring or comments
    if '"""' in response or "'''" in response or "#" in response or "//" in response:
        score += 1

    # Check for proper formatting
    if "\n" in response and "    " in response:  # Has indentation
        score += 1

    # Length check (not too short, not too long)
    if 50 < len(response) < 500:
        score += 1

    # Convert to stars
    stars = "⭐" * score
    return stars if stars else "❌ (No code generated)"


def main():
    """Main test runner."""
    print_header("🧪 Testing Local AI Models")
    print("Module 1.2: Local Models for AI Coding")
    print()

    # Check if Ollama is running
    print("1. Checking Ollama service...")
    if check_ollama_running():
        print_success("Ollama is running on http://localhost:11434")
    else:
        print_error("Ollama is not running!")
        print()
        print("  Start Ollama with:")
        print("    ollama serve")
        print()
        print("  Or on macOS with Homebrew:")
        print("    brew services start ollama")
        sys.exit(1)

    # Get installed models
    print("\n2. Getting installed models...")
    models = get_installed_models()

    if not models:
        print_error("No models installed!")
        print()
        print("  Install a model with:")
        print("    ollama pull qwen2.5-coder:7b")
        print()
        print("  Or run the setup script:")
        print("    bash setup_ollama.sh")
        sys.exit(1)

    print_success(f"Found {len(models)} installed model(s):")
    for model in models:
        print(f"  • {model}")

    # Filter to coding models only
    coding_models = [
        m for m in models
        if any(keyword in m.lower() for keyword in [
            "coder", "code", "llama", "qwen", "deepseek", "phi", "gemma"
        ])
    ]

    if not coding_models:
        print_warning("No coding-specific models found")
        print("  Using all installed models for testing...")
        coding_models = models

    # Test each coding model
    print_header(f"\n3. Testing {len(coding_models)} coding model(s)")

    test_tasks = [
        "Write a Python function to reverse a string. Include type hints and a docstring.",
        "Write a function to check if a number is prime. Make it efficient.",
    ]

    results = {}

    for model in coding_models:
        model_results = []
        for i, task in enumerate(test_tasks, 1):
            print(f"\n  Task {i}/{len(test_tasks)}:")
            result = test_model(model, task)
            if result:
                quality = rate_code_quality(result["response"])
                print(f"  {GREEN}Quality:{RESET} {quality}")
                model_results.append(result)
            else:
                model_results.append({"success": False})

        results[model] = model_results

    # Summary
    print_header("\n📊 Test Summary")

    for model, model_results in results.items():
        successful = sum(1 for r in model_results if r.get("success", False))
        total = len(model_results)
        avg_time = sum(r.get("time", 0) for r in model_results if r.get("success")) / max(successful, 1)

        if successful == total:
            print_success(f"{model}")
        elif successful > 0:
            print_warning(f"{model}")
        else:
            print_error(f"{model}")

        print(f"  Passed: {successful}/{total} tests")
        if successful > 0:
            print(f"  Avg response time: {avg_time:.1f}s")

    # Final status
    all_passed = all(
        all(r.get("success", False) for r in model_results)
        for model_results in results.values()
    )

    print()
    if all_passed:
        print_success("All tests passed! 🎉")
        print()
        print("Next steps:")
        print("  • Try Aider: aider --model ollama/" + coding_models[0])
        print("  • Configure Continue.dev: cp continue_config.json ~/.continue/config.json")
        print("  • Read setup guide: cat aider_with_local.md")
    else:
        print_warning("Some tests failed")
        print()
        print("Troubleshooting:")
        print("  • Ensure models are fully downloaded: ollama pull <model>")
        print("  • Check Ollama logs: ollama logs")
        print("  • Try re-running: python test_local_models.py")

    print()


if __name__ == "__main__":
    main()
