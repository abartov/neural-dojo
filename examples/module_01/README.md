# Module 1 Examples: AI-Driven Development

**Module**: Foundations of AI-Driven Development
**Purpose**: Demonstrate AI coding patterns and complete first AI-assisted project

---

## 📋 Prerequisites

```bash
# Create/activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📂 Examples Structure

### 🎨 Pattern Demonstrations

These examples demonstrate the 5 core AI coding patterns from Module 1:

#### 1. **Specification Pattern** (`patterns/01_specification_pattern.py`)
- Shows how to write clear specifications for AI
- Example: Top frequent numbers function generated from spec
- **Run**: `python patterns/01_specification_pattern.py`

#### 2. **Iteration Pattern** (`patterns/02_iteration_pattern.py`)
- Demonstrates iterative refinement with AI
- Example: Email validator evolving through iterations
- **Run**: `python patterns/02_iteration_pattern.py`

#### 3. **Example Pattern** (`patterns/03_example_pattern.py`)
- Shows pattern matching with examples
- Example: Generating similar functions from one example
- **Run**: `python patterns/03_example_pattern.py`

#### 4. **Explanation Pattern** (`patterns/04_explanation_pattern.py`)
- Code explanation and learning use case
- Example: Understanding complex algorithms
- **Run**: `python patterns/04_explanation_pattern.py`

#### 5. **Debugging Pattern** (`patterns/05_debugging_pattern.py`)
- Using AI to debug issues
- Example: Common error patterns and fixes
- **Run**: `python patterns/05_debugging_pattern.py`

---

### 🏗️ Main Project: Python File Analyzer

**Location**: `project/`

A complete CLI tool that analyzes Python files for metrics like function count, class count, lines of code, and complexity score.

**Features**:
- ✅ Analyze single Python files
- ✅ Recursive directory analysis
- ✅ Multiple output formats (pretty, JSON)
- ✅ Type hints throughout
- ✅ Comprehensive error handling
- ✅ Full test coverage

**Quick Start**:
```bash
cd project/

# Analyze a single file
python pyanalyzer.py path/to/file.py

# Analyze a directory recursively
python pyanalyzer.py path/to/directory/

# JSON output
python pyanalyzer.py path/to/file.py --json

# Run tests
pytest test_pyanalyzer.py -v
```

**See**: `project/README.md` for full documentation

---

## 🎯 Learning Objectives

After working through these examples, you will:

- ✅ Understand how to structure prompts for AI coding assistants
- ✅ Know when to use each of the 5 AI coding patterns
- ✅ Have built a complete CLI tool with AI assistance
- ✅ Know how to iterate and refine AI-generated code
- ✅ Understand AI's strengths and limitations in practice

---

## 💡 Tips for Success

### Working with AI Coding Assistants

1. **Be Specific**: Clear specs = better code
2. **Iterate**: Don't expect perfection on first try
3. **Verify**: Always test AI-generated code
4. **Learn**: Understand what the AI generates
5. **Refine**: Use follow-up prompts to improve

### Running Examples

- Each pattern example is self-contained and runnable
- Read the code comments to understand the AI interaction flow
- Try modifying the examples to practice AI coding
- Use these patterns as templates for your own projects

---

## 📊 Expected Output

### Pattern Examples

Each pattern example demonstrates the technique with working code and output showing results.

### Main Project Output

```bash
$ python project/pyanalyzer.py project/pyanalyzer.py

🐍 Python File Analyzer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 File: project/pyanalyzer.py

📊 Metrics:
  Functions:  8
  Classes:    1
  Lines:      247 (excluding blanks/comments)
  Complexity: 23

✨ Analysis complete!
```

---

## 🧪 Testing

All examples include tests. Run tests for the main project:

```bash
cd project/
pytest test_pyanalyzer.py -v

# With coverage
pytest test_pyanalyzer.py --cov=pyanalyzer
```

---

## 🚀 Next Steps

1. **Run all pattern examples** to see AI coding patterns in action
2. **Build the main project** by following the project README
3. **Complete Module 1 deliverables** in `docs/deliverables/`
4. **Move to Module 2** for prompt engineering deep dive

---

## 📚 Additional Resources

- Module 1 Theory: `docs/curriculum/notes/module_01_ai_driven_development.md`
- Claude Code Docs: https://docs.anthropic.com/
- GitHub Copilot Docs: https://docs.github.com/en/copilot

---

**Built with AI assistance as part of Neural Dojo 🥋🧠⚡**
