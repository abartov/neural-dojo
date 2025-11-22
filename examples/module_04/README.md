# Module 4 Examples: AI-Assisted Debugging & Optimization

This directory contains hands-on examples demonstrating how to use AI to debug and optimize code effectively.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples Overview

### 1. Syntax & Type Debugging (`01_syntax_debugging.py`)
**Description**: Demonstrates using AI to fix common syntax and type errors
**Run**: `python 01_syntax_debugging.py`
**What it shows**:
- Fixing syntax errors (missing colons, parentheses)
- Type mismatch resolution
- Import error debugging
- Quick iteration with AI suggestions

### 2. Logic Error Debugging (`02_logic_debugging.py`)
**Description**: Finding and fixing logic errors with AI assistance
**Run**: `python 02_logic_debugging.py`
**What it shows**:
- Off-by-one errors
- Wrong conditional logic
- Edge case handling
- AI-guided root cause analysis

### 3. Performance Profiling (`03_performance_profiling.py`)
**Description**: Using AI to analyze and optimize performance bottlenecks
**Run**: `python 03_performance_profiling.py`
**What it shows**:
- Profiling with cProfile
- Identifying O(n²) algorithms
- Optimization strategies
- Before/after comparisons
- AI-assisted algorithmic improvements

### 4. Async & Concurrent Debugging (`04_async_debugging.py`)
**Description**: Debugging asynchronous code with AI help
**Run**: `python 04_async_debugging.py`
**What it shows**:
- Common async/await mistakes
- Race condition patterns (AI limitations)
- Proper async error handling
- When to use AI vs traditional debugging

### 5. Integration Debugging (`05_integration_debugging.py`)
**Description**: Debugging API calls and external integrations
**Run**: `python 05_integration_debugging.py`
**What it shows**:
- API authentication errors
- Request/response debugging
- Error interpretation
- AI-assisted troubleshooting workflow

### 6. Optimization Examples (`06_optimization_examples.py`)
**Description**: Comprehensive optimization demonstrations
**Run**: `python 06_optimization_examples.py`
**What it shows**:
- Algorithmic optimization (O(n²) → O(n log n))
- Code-level optimization (list comprehensions, generators)
- Memory optimization
- Database query optimization patterns

### 7. Debugging Patterns (`07_debugging_patterns.py`)
**Description**: Systematic debugging patterns and strategies
**Run**: `python 07_debugging_patterns.py`
**What it shows**:
- Binary search debugging
- Differential debugging (environment differences)
- Regression debugging (git bisect approach)
- Rubber duck debugging with AI

## Quick Start

### Run All Examples

```bash
# Syntax debugging
python 01_syntax_debugging.py

# Logic errors
python 02_logic_debugging.py

# Performance profiling
python 03_performance_profiling.py

# Async debugging
python 04_async_debugging.py

# Integration debugging
python 05_integration_debugging.py

# Optimization examples
python 06_optimization_examples.py

# Debugging patterns
python 07_debugging_patterns.py
```

## Learning Path

1. **Start with `01_syntax_debugging.py`**: Learn the basics of AI-assisted debugging
2. **Move to `02_logic_debugging.py`**: Understand AI's strengths in logic analysis
3. **Try `03_performance_profiling.py`**: Learn to combine profiling tools with AI
4. **Explore `04_async_debugging.py`**: Understand AI's limitations
5. **Practice `05_integration_debugging.py`**: Real-world API debugging
6. **Study `06_optimization_examples.py`**: See optimization strategies in action
7. **Master `07_debugging_patterns.py`**: Learn systematic approaches

## Expected Output

Each example demonstrates:
- ✅ The buggy code (commented out or in a separate function)
- ✅ AI's analysis of the problem
- ✅ The fix with explanations
- ✅ Test cases showing before/after
- ✅ Commentary on AI's effectiveness

### Example Output from `01_syntax_debugging.py`:

```
=== Syntax & Type Debugging with AI ===

Example 1: Missing Colon
❌ BUGGY CODE:
def greet(name)  # Missing colon!
    return f"Hello, {name}"

🤖 AI Analysis:
   SyntaxError: expected ':' after function definition
   Fix: Add colon after parameter list

✅ FIXED CODE:
def greet(name):
    return f"Hello, {name}"

✓ Test passed: greet("World") = "Hello, World"
```

## Tips for Using These Examples

1. **Read the buggy code first**: Try to spot the error yourself
2. **Compare with AI's approach**: See how AI analyzes the problem
3. **Test the fixes**: Run the corrected code
4. **Experiment**: Modify examples to create new bugs and practice debugging

## Common Patterns Demonstrated

### Pattern 1: Systematic Investigation
```python
# 1. Reproduce the bug
# 2. Gather error information
# 3. Create minimal reproduction
# 4. Ask AI for analysis
# 5. Verify solution
# 6. Add tests
```

### Pattern 2: Combine Tools + AI
```python
# 1. Use profiler (cProfile, memory_profiler)
# 2. Get concrete data (time, memory, call counts)
# 3. Share data with AI
# 4. Get optimization suggestions
# 5. Benchmark improvements
```

### Pattern 3: Iterative Refinement
```python
# 1. Initial AI suggestion
# 2. Test → doesn't fully work
# 3. Provide new error to AI
# 4. Refined suggestion
# 5. Test → works!
```

## Real-World Applications

These examples connect to your projects:

### kaizen (Lean DevOps Platform)
- Debug RAG query issues
- Optimize vector search performance
- Fix async API integration bugs
- Performance tune database queries

### vibe (Teaching Platform)
- Debug content generation errors
- Optimize API response times
- Fix authentication issues
- Improve database query efficiency

### contrarian (Stock Analysis)
- Debug data processing pipelines
- Optimize time series calculations
- Fix API integration errors
- Performance tune analysis algorithms

## Troubleshooting

### Examples won't run
```bash
# Check Python version (need 3.12+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Run with verbose output
python -v 01_syntax_debugging.py
```

### Import errors
```bash
# Ensure virtual environment is activated
source ../../../venv/bin/activate  # or your venv path

# Verify packages installed
pip list
```

## Further Reading

- Python Debugging with pdb: https://docs.python.org/3/library/pdb.html
- cProfile Documentation: https://docs.python.org/3/library/profile.html
- asyncio Debugging: https://docs.python.org/3/library/asyncio-dev.html
- "Debugging: The 9 Indispensable Rules" by David Agans

---

**Remember**: AI is a debugging assistant, not a replacement for understanding your code. Use these examples to learn systematic debugging approaches!

🐛 → 🤖 → ✅ Happy debugging!
