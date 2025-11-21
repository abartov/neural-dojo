# Python File Analyzer 🐍

**Module 1 Main Project**: A CLI tool to analyze Python files and report code metrics.

Built with AI assistance as part of Neural Dojo's Module 1: AI-Driven Development.

---

## Features

✅ **Analyze single Python files**
- Function count
- Class count
- Lines of code (excluding blanks and comments)
- Complexity score (if/while/for statements)

✅ **Recursive directory analysis**
- Scan all `.py` files in a directory
- Aggregate statistics

✅ **Multiple output formats**
- Pretty terminal output (default)
- JSON output (`--json` flag)

✅ **Robust error handling**
- File not found
- Invalid Python syntax
- Permission errors

✅ **Professional code quality**
- Type hints throughout
- Comprehensive docstrings
- Full test coverage
- PEP 8 compliant

---

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Analyze a single file

```bash
python pyanalyzer.py path/to/file.py
```

Example output:
```
🐍 Python File Analyzer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 File: path/to/file.py

📊 Metrics:
  Functions:  12
  Classes:    3
  Lines:      247 (excluding blanks/comments)
  Complexity: 23

✨ Analysis complete!
```

### Analyze a directory (recursive)

```bash
python pyanalyzer.py path/to/directory/
```

Example output:
```
🐍 Python File Analyzer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Directory: path/to/directory/

📊 Aggregate Metrics (15 files analyzed):
  Functions:  127
  Classes:    18
  Lines:      3,842 (excluding blanks/comments)
  Complexity: 234

✨ Analysis complete!
```

### JSON output

```bash
python pyanalyzer.py path/to/file.py --json
```

Example output:
```json
{
  "type": "file",
  "path": "path/to/file.py",
  "metrics": {
    "functions": 12,
    "classes": 3,
    "lines": 247,
    "complexity": 23
  }
}
```

---

## How It Works

### Analysis Process

1. **Parse Python file** using `ast` module
2. **Walk the AST** to count:
   - `FunctionDef` and `AsyncFunctionDef` nodes (functions)
   - `ClassDef` nodes (classes)
   - `If`, `While`, `For` nodes (complexity)
3. **Count lines** excluding:
   - Blank lines
   - Comment lines (starting with `#`)
4. **Format output** as pretty print or JSON

### Complexity Score

Simple heuristic based on control flow statements:
- Each `if` statement: +1
- Each `while` loop: +1
- Each `for` loop: +1

Higher score = more complex code (more branching)

---

## Testing

Run the test suite:

```bash
pytest test_pyanalyzer.py -v
```

Run with coverage:

```bash
pytest test_pyanalyzer.py --cov=pyanalyzer --cov-report=term-missing
```

Expected output:
```
test_pyanalyzer.py::test_analyze_simple_file PASSED
test_pyanalyzer.py::test_analyze_with_classes PASSED
test_pyanalyzer.py::test_analyze_with_complexity PASSED
test_pyanalyzer.py::test_file_not_found PASSED
test_pyanalyzer.py::test_invalid_python PASSED
test_pyanalyzer.py::test_empty_file PASSED
test_pyanalyzer.py::test_directory_analysis PASSED
test_pyanalyzer.py::test_json_output PASSED

---------- coverage: platform darwin, python 3.10.x -----------
Name             Stmts   Miss  Cover   Missing
----------------------------------------------
pyanalyzer.py      123      0   100%
----------------------------------------------
TOTAL              123      0   100%
```

---

## Project Structure

```
project/
├── README.md              # This file
├── pyanalyzer.py          # Main CLI tool
├── test_pyanalyzer.py     # Test suite
└── requirements.txt       # Dependencies
```

---

## Implementation Details

### Key Design Decisions

**Why AST over regex?**
- Accurately handles edge cases (strings with 'def', etc.)
- Understands Python syntax properly
- Reliable and maintainable

**Why argparse?**
- Standard library (no dependencies)
- Automatic help generation
- Good error messages

**Why both pretty and JSON output?**
- Pretty: Human-friendly for quick checks
- JSON: Machine-readable for pipelines

### Code Quality Standards

- ✅ Type hints on all functions
- ✅ Google-style docstrings
- ✅ Error handling with specific exceptions
- ✅ Comprehensive test coverage
- ✅ PEP 8 compliant

---

## Example Use Cases

### 1. Code Review

```bash
# Check complexity before code review
python pyanalyzer.py src/complex_module.py
# If complexity > 50, consider refactoring
```

### 2. Project Statistics

```bash
# Get overview of entire codebase
python pyanalyzer.py src/ --json > stats.json
```

### 3. CI/CD Pipeline

```bash
# Add to CI to track code metrics over time
python pyanalyzer.py src/ --json | jq '.metrics.complexity'
# Alert if complexity exceeds threshold
```

---

## Limitations

**Current Scope**:
- Only analyzes Python files
- Simple complexity metric (not cyclomatic complexity)
- Doesn't analyze imports or dependencies
- Doesn't detect code smells

**Possible Extensions** (for future modules):
- Cyclomatic complexity
- Halstead metrics
- Code duplication detection
- Dependency graph visualization
- Integration with pylint/flake8

---

## AI-Assisted Development Notes

This project was built using AI coding assistants, demonstrating the patterns from Module 1:

1. **Specification Pattern**: Clear requirements → AI generates initial structure
2. **Iteration Pattern**: Refined through multiple iterations
3. **Example Pattern**: Showed test examples → AI generated more tests
4. **Explanation Pattern**: Asked AI to explain AST traversal
5. **Debugging Pattern**: AI helped fix edge cases

**Time saved**: ~60% compared to coding from scratch
**AI contribution**: ~70% of code generated by AI, 30% manual refinement

---

## Contributing

This is a learning project for Neural Dojo. Feel free to:
- Add more metrics
- Improve output formatting
- Add configuration file support
- Create visualizations

---

## License

Part of Neural Dojo curriculum. For educational purposes.

---

**Built with ❤️ and AI 🤖 in Neural Dojo 🥋🧠⚡**
