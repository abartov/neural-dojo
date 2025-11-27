# Module 34: Code Generation Models

**Last Updated**: 2025-11-27
**Status**: 🟢 Complete
**Duration**: 6-7 hours
**Prerequisites**: Module 33 (Diffusion Models)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand how code-specialized LLMs differ from general text models
- Master Fill-in-the-Middle (FIM) training and why it matters
- Know the major code models: Codex, CodeLlama, StarCoder, DeepSeek Coder
- Evaluate code generation with HumanEval, MBPP, and SWE-bench
- Build practical code generation and completion systems
- Understand how AI coding assistants (Copilot, Cursor, Claude Code) work

---

## 📖 The Rise of AI-Powered Coding

### The Programming Revolution

In 2021, something remarkable happened. OpenAI released Codex, a model fine-tuned on code that could write programs from natural language descriptions. Within months, GitHub Copilot launched, and suddenly millions of developers had an AI pair programmer.

By 2024, studies showed that developers using AI coding assistants were completing tasks 55% faster. The question shifted from "Will AI write code?" to "How do we build better code models?"

**Did You Know?** When GitHub Copilot launched in 2021, it was trained on a fine-tuned version of GPT-3 called Codex. The model had seen 54 million GitHub repositories during training—roughly 159 GB of Python code alone. Mark Chen, one of the lead researchers, noted that Codex could solve about 28% of HumanEval problems on the first try, but with 100 samples and best-of selection, it could solve 70%. This insight led to the widespread adoption of "sampling and ranking" strategies in code generation.

---

## 🏗️ Architecture of Code Models

### Why Code Needs Special Treatment

Code isn't just text with different vocabulary. It has unique properties that general language models struggle with:

**1. Strict Syntax**
```python
# Natural language is forgiving:
"I want make a function that adds numbers"  # Understandable!

# Code is not:
def add(a b):  # SyntaxError! Missing comma
    return a + b
```

**2. Long-Range Dependencies**
```python
class DataProcessor:
    def __init__(self, config):
        self.config = config  # Defined here

    # ... 200 lines later ...

    def process(self, data):
        threshold = self.config.threshold  # Must remember self.config!
```

**3. Semantic Precision**
```python
# "Sort the list" in natural language → many valid interpretations
# In code, these are all different:
sorted(items)                    # Returns new list
items.sort()                     # Modifies in place
sorted(items, reverse=True)      # Descending
sorted(items, key=lambda x: x.name)  # By attribute
```

**4. Cross-File Context**
```python
# models/user.py
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

# services/auth.py - needs to know User's structure!
from models.user import User

def create_user(data: dict) -> User:
    return User(name=data['name'], email=data['email'])
```

### The Code Model Recipe

Modern code models share common architectural patterns:

```
┌─────────────────────────────────────────────────────────────┐
│                    CODE MODEL ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. BASE ARCHITECTURE                                       │
│     └─ Decoder-only Transformer (like GPT)                 │
│        └─ Causal attention for autoregressive generation   │
│                                                             │
│  2. VOCABULARY                                              │
│     └─ Code-optimized tokenizer                            │
│        └─ Fewer tokens per line (efficiency)               │
│        └─ Preserve indentation structure                    │
│                                                             │
│  3. CONTEXT LENGTH                                          │
│     └─ Longer than text models (4K → 16K → 100K+)         │
│        └─ RoPE (Rotary Position Embeddings)                │
│        └─ ALiBi (Attention with Linear Biases)             │
│                                                             │
│  4. TRAINING OBJECTIVE                                      │
│     └─ Next-token prediction (standard)                    │
│     └─ Fill-in-the-Middle (FIM) - code-specific!          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Did You Know?** The tokenizer choice dramatically affects code model performance. StarCoder uses a tokenizer trained specifically on code, where common patterns like `def __init__(self` become single or few tokens. In contrast, GPT-2's tokenizer (trained on web text) splits Python indentation inefficiently—four spaces might become 4 separate tokens instead of 1. BigCode researchers found that a code-optimized tokenizer reduced the average tokens per Python file by 30%, effectively giving the model 30% more context.

---

## 📚 Fill-in-the-Middle (FIM): The Key Innovation

### Why Completion Isn't Enough

Traditional language models generate left-to-right. They're great at continuing text:

```python
# Given this prefix:
def calculate_average(numbers):
    total = sum(numbers)

# Model continues:
    count = len(numbers)
    return total / count
```

But real programming often requires **insertion**:

```python
def calculate_average(numbers):
    # <-- Need to add validation HERE
    total = sum(numbers)
    count = len(numbers)
    return total / count
```

You have context **before** and **after** the cursor. Standard left-to-right models can't use the "after" context!

### FIM Training: Teaching Insertion

FIM transforms training examples to teach models insertion:

**Original Code:**
```python
def greet(name):
    message = f"Hello, {name}!"
    return message
```

**FIM Transformation (PSM format):**
```
<PREFIX>def greet(name):
    message = <SUFFIX>
    return message<MIDDLE>f"Hello, {name}!"
```

The model learns to:
1. See the prefix (code before cursor)
2. See the suffix (code after cursor)
3. Generate the middle (what goes at cursor)

### FIM Formats

Different models use different FIM conventions:

**PSM (Prefix-Suffix-Middle)** - Most common:
```
<fim_prefix>def add(a, b):
    <fim_suffix>
    return result<fim_middle>result = a + b
```

**SPM (Suffix-Prefix-Middle)** - Some models:
```
<fim_suffix>
    return result<fim_prefix>def add(a, b):
    <fim_middle>result = a + b
```

**Implementation Example:**
```python
def apply_fim_transform(code: str, fim_rate: float = 0.5) -> str:
    """Transform code for FIM training."""
    if random.random() > fim_rate:
        return code  # Regular left-to-right example

    # Choose random split point
    split_point = random.randint(0, len(code))

    prefix = code[:split_point]
    suffix = code[split_point:]

    # Find natural boundary (line break)
    if '\n' in suffix:
        boundary = suffix.index('\n')
        middle = suffix[:boundary]
        suffix = suffix[boundary:]
    else:
        middle = suffix
        suffix = ""

    # PSM format
    return f"<fim_prefix>{prefix}<fim_suffix>{suffix}<fim_middle>{middle}"
```

**Did You Know?** The FIM technique was introduced in the "Efficient Training of Language Models to Fill in the Middle" paper by Bavarian et al. (2022). They discovered something surprising: training with just 50% FIM examples (mixed with regular left-to-right) gives you the benefits of FIM without hurting standard completion performance. Too much FIM (>90%) actually degraded both capabilities. This "sweet spot" finding shaped how all major code models are trained today.

---

## 🏆 The Code Model Landscape

### Evolution of Code Models

```
Timeline of Major Code Models:

2020 ─────────────────────────────────────────────────────────
     │
     └─ GPT-3: General model, decent at code

2021 ─────────────────────────────────────────────────────────
     │
     ├─ Codex (OpenAI): First dedicated code model
     │  └─ GPT-3 fine-tuned on GitHub code
     │  └─ Powered GitHub Copilot v1
     │
     └─ CodeParrot (HuggingFace): Open-source attempt

2022 ─────────────────────────────────────────────────────────
     │
     ├─ InCoder (Meta): First open FIM model
     │
     ├─ SantaCoder (BigCode): 1.1B, strong performance
     │
     └─ CodeGen (Salesforce): Multi-turn code generation

2023 ─────────────────────────────────────────────────────────
     │
     ├─ StarCoder (BigCode): 15B, open, multilingual
     │  └─ 80+ programming languages
     │  └─ 8K context
     │
     ├─ CodeLlama (Meta): 7B/13B/34B
     │  └─ Based on Llama 2
     │  └─ 100K context (rope scaling)
     │  └─ Python-specialized variant
     │
     └─ WizardCoder: Evol-Instruct for code

2024 ─────────────────────────────────────────────────────────
     │
     ├─ DeepSeek Coder (DeepSeek): 1.3B to 33B
     │  └─ State-of-the-art open model
     │  └─ 16K context
     │
     ├─ StarCoder2 (BigCode): 3B/7B/15B
     │  └─ Trained on The Stack v2
     │  └─ 619 languages
     │
     ├─ CodeQwen (Alibaba): 1.5B/7B
     │  └─ Strong multilingual code
     │
     └─ Codestral (Mistral): 22B
         └─ Fill-in-the-middle focus
         └─ 32K context
```

### Model Comparison

| Model | Size | Context | HumanEval | Open Weights | FIM |
|-------|------|---------|-----------|--------------|-----|
| GPT-4 | ~1.8T | 128K | 67.0% | No | Yes |
| Claude 3.5 Sonnet | ~70B? | 200K | 64.0% | No | Yes |
| CodeLlama-34B | 34B | 100K | 48.8% | Yes | Yes |
| DeepSeek Coder 33B | 33B | 16K | 56.1% | Yes | Yes |
| StarCoder2-15B | 15B | 16K | 46.3% | Yes | Yes |
| Codestral-22B | 22B | 32K | 57.1% | Partial | Yes |

### Specialized Variants

**CodeLlama Family:**
```
CodeLlama Base (7B/13B/34B)
    │
    ├─ CodeLlama-Python: Fine-tuned on Python
    │  └─ Better for Python-specific tasks
    │
    └─ CodeLlama-Instruct: Instruction-tuned
       └─ Better for chat/explanation
       └─ "Explain this code" works better
```

**Did You Know?** DeepSeek Coder achieved state-of-the-art performance among open models by using a novel "repo-level" pretraining approach. Instead of training on random code files, they constructed training examples that maintained the file structure of entire repositories. This taught the model about import relationships, API consistency, and project organization. The 33B model outperformed CodeLlama-34B despite being trained on less data, demonstrating that training data organization matters as much as quantity.

---

## 📊 Evaluating Code Generation

### HumanEval: The Standard Benchmark

HumanEval consists of 164 hand-written Python programming problems:

**Example Problem:**
```python
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """Check if in given list of numbers, are any two numbers
    closer to each other than given threshold.

    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
```

The model must generate the function body. It passes if the code works on hidden test cases.

**Pass@k Metric:**
- Generate k samples
- Pass@k = probability at least one passes
- Common: pass@1, pass@10, pass@100

```python
def estimate_pass_at_k(n: int, c: int, k: int) -> float:
    """
    Estimate pass@k from n samples with c correct.

    Args:
        n: Total samples generated
        c: Number that passed tests
        k: k for pass@k metric

    Uses unbiased estimator from Codex paper.
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))
```

### MBPP: More Problems, More Diversity

MBPP (Mostly Basic Python Programming) has 974 problems:
- Simpler than HumanEval on average
- Better statistical significance
- Includes natural language descriptions

**Example:**
```python
"""
Write a function to find the volume of a sphere.
assert math.isclose(volume_sphere(10), 4188.79, rel_tol=0.01)
"""
```

### SWE-bench: Real-World Evaluation

SWE-bench uses real GitHub issues from popular projects:

```
┌─────────────────────────────────────────────────────────────┐
│                    SWE-BENCH TASK                           │
├─────────────────────────────────────────────────────────────┤
│ Repository: django/django                                   │
│ Issue: QuerySet.bulk_create() fails with OnConflict         │
│                                                             │
│ Given:                                                      │
│   - Full repository code                                    │
│   - Issue description                                       │
│   - Failing test case                                       │
│                                                             │
│ Model must:                                                 │
│   - Locate relevant files                                   │
│   - Understand the codebase                                 │
│   - Generate a patch that fixes the issue                   │
│   - Pass existing tests + the new test                      │
└─────────────────────────────────────────────────────────────┘
```

**Why SWE-bench Matters:**
- Tests real software engineering (not isolated functions)
- Requires understanding large codebases
- Current models score ~15-25% (much harder!)

**Did You Know?** When SWE-bench was released in 2023 by Princeton researchers, the best models solved only 1.3% of issues. By late 2024, agentic systems combining Claude with search and tool use reached ~49% on the full benchmark. The key insight? Code generation alone isn't enough—models need to search, read, understand, and iteratively refine. Carlos Jimenez, the lead author, designed SWE-bench specifically to resist "benchmark gaming" by using real issues that were created after model training cutoffs.

---

## 🛠️ Building Code Generation Systems

### Basic Code Completion

```python
def complete_code(
    prefix: str,
    suffix: str = "",
    model: str = "deepseek-coder",
    max_tokens: int = 256,
    temperature: float = 0.2
) -> str:
    """Complete code given prefix and optional suffix (FIM)."""

    if suffix:
        # FIM mode
        prompt = f"<fim_prefix>{prefix}<fim_suffix>{suffix}<fim_middle>"
    else:
        # Standard completion
        prompt = prefix

    response = client.completions.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["<fim_suffix>", "\n\n\n"]  # Stop tokens
    )

    return response.choices[0].text
```

### Multi-Sample Generation with Ranking

```python
def generate_with_ranking(
    prompt: str,
    n_samples: int = 10,
    test_cases: List[Tuple[Any, Any]] = None
) -> str:
    """Generate multiple samples and rank by test passing."""

    samples = []
    for _ in range(n_samples):
        code = complete_code(prompt, temperature=0.8)
        samples.append(code)

    if test_cases:
        # Rank by test passing
        scores = []
        for code in samples:
            passed = sum(
                run_test(code, inp, expected)
                for inp, expected in test_cases
            )
            scores.append(passed)

        best_idx = np.argmax(scores)
        return samples[best_idx]

    # Without tests, return most common (majority voting)
    from collections import Counter
    return Counter(samples).most_common(1)[0][0]
```

### Repository-Aware Generation

```python
class RepoContextBuilder:
    """Build context from repository for better generation."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.file_index = self._build_index()

    def _build_index(self) -> Dict[str, str]:
        """Index all code files."""
        index = {}
        for ext in ['.py', '.js', '.ts', '.java']:
            for path in self.repo_path.rglob(f'*{ext}'):
                relative = path.relative_to(self.repo_path)
                index[str(relative)] = path.read_text()
        return index

    def get_relevant_context(
        self,
        current_file: str,
        cursor_position: int,
        max_context_tokens: int = 4000
    ) -> str:
        """Get relevant context for code completion."""

        context_parts = []

        # 1. Current file content
        current_content = self.file_index.get(current_file, "")
        context_parts.append(f"# Current file: {current_file}\n{current_content}")

        # 2. Imported files
        imports = self._extract_imports(current_content)
        for imp in imports:
            if imp in self.file_index:
                context_parts.append(
                    f"# Imported: {imp}\n{self.file_index[imp][:2000]}"
                )

        # 3. Similar files (by name/directory)
        similar = self._find_similar_files(current_file)
        for path in similar[:3]:
            context_parts.append(
                f"# Related: {path}\n{self.file_index[path][:1000]}"
            )

        # Combine and truncate
        full_context = "\n\n".join(context_parts)
        return self._truncate_to_tokens(full_context, max_context_tokens)
```

---

## 💻 How AI Coding Assistants Work

### GitHub Copilot Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GITHUB COPILOT FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  IDE Plugin                                                 │
│      │                                                      │
│      ▼                                                      │
│  Context Gathering                                          │
│      │                                                      │
│      ├─ Current file content                               │
│      ├─ Cursor position                                     │
│      ├─ Open tabs (limited)                                │
│      ├─ File path/name                                      │
│      └─ Language detection                                  │
│      │                                                      │
│      ▼                                                      │
│  Prompt Construction                                        │
│      │                                                      │
│      ├─ Path: # file: src/utils/auth.py                    │
│      ├─ Context: (nearby code)                             │
│      ├─ Prefix: (code before cursor)                       │
│      └─ Suffix: (code after cursor) - FIM                  │
│      │                                                      │
│      ▼                                                      │
│  API Call (Codex/GPT-4)                                    │
│      │                                                      │
│      ▼                                                      │
│  Post-Processing                                            │
│      │                                                      │
│      ├─ Syntax validation                                  │
│      ├─ Duplicate detection                                │
│      ├─ Confidence scoring                                 │
│      └─ Multi-line vs single-line                          │
│      │                                                      │
│      ▼                                                      │
│  Ghost Text Display                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Cursor: RAG for Code

Cursor introduced repository-wide RAG for code completion:

```python
# Simplified Cursor-style RAG
class CursorStyleRAG:
    def __init__(self, repo_path: str):
        self.embedder = CodeEmbedder()
        self.index = self._build_vector_index(repo_path)

    def _build_vector_index(self, repo_path: str):
        """Build semantic index of code chunks."""
        chunks = []
        for file in Path(repo_path).rglob("*.py"):
            content = file.read_text()
            # Chunk by functions/classes
            for chunk in self._chunk_by_ast(content):
                embedding = self.embedder.embed(chunk)
                chunks.append({
                    "content": chunk,
                    "embedding": embedding,
                    "file": str(file)
                })
        return VectorIndex(chunks)

    def get_context(self, query: str, current_file: str) -> str:
        """Retrieve relevant code context."""
        query_embedding = self.embedder.embed(query)

        # Semantic search
        similar = self.index.search(query_embedding, k=10)

        # Filter and rank
        # - Prefer same directory
        # - Prefer imported modules
        # - Prefer recently edited
        ranked = self._rank_results(similar, current_file)

        return self._format_context(ranked[:5])
```

### Claude Code: Agentic Approach

Claude Code (which you're using!) takes an agentic approach:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE APPROACH                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Request                                               │
│      │                                                      │
│      ▼                                                      │
│  Planning Phase                                             │
│      │                                                      │
│      ├─ Understand the task                                │
│      ├─ Identify files to read                             │
│      └─ Plan implementation steps                          │
│      │                                                      │
│      ▼                                                      │
│  Tool Use Loop                                              │
│      │                                                      │
│      ├─ Read files (full content, not snippets)            │
│      ├─ Search codebase (Grep, Glob)                       │
│      ├─ Execute commands (Bash)                            │
│      ├─ Edit files (surgical edits)                        │
│      └─ Verify changes (run tests)                         │
│      │                                                      │
│      ▼                                                      │
│  Iteration                                                  │
│      │                                                      │
│      └─ If tests fail → analyze → fix → retry              │
│                                                             │
│  KEY DIFFERENCE: Full file understanding, not just         │
│  autocomplete. Treats coding as problem-solving.           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Did You Know?** GitHub Copilot's prompt engineering is surprisingly sophisticated. Research by Xu et al. (2023) reverse-engineered Copilot's prompts and found it includes: (1) the file path as a comment, (2) language-specific context limits, (3) snippet ranking by relevance, and (4) dynamic context window adjustment based on completion confidence. They also found that including just the file name in a comment improved completion accuracy by 5-10% on repository-specific APIs.

---

## 🔍 Advanced Techniques

### Speculative Decoding for Speed

Code completion must be fast (<100ms). Speculative decoding helps:

```python
def speculative_decode(
    prompt: str,
    draft_model: Model,  # Small, fast (1B)
    target_model: Model,  # Large, accurate (34B)
    k: int = 4
) -> str:
    """Generate tokens speculatively for faster inference."""

    tokens = tokenize(prompt)

    while not is_complete(tokens):
        # 1. Draft model generates k tokens quickly
        draft_tokens = draft_model.generate(tokens, n=k)

        # 2. Target model verifies all k at once (batched)
        probs = target_model.get_probs(tokens + draft_tokens)

        # 3. Accept tokens while they match target's distribution
        accepted = 0
        for i, token in enumerate(draft_tokens):
            if accept_token(token, probs[i]):
                accepted += 1
            else:
                break

        tokens.extend(draft_tokens[:accepted])

        # 4. If rejected early, sample from target
        if accepted < k:
            tokens.append(target_model.sample(tokens))

    return detokenize(tokens)
```

### Constrained Decoding for Valid Syntax

Force syntactically valid output:

```python
from lark import Lark

class SyntaxConstrainedDecoder:
    """Generate only syntactically valid code."""

    def __init__(self, grammar_path: str):
        self.parser = Lark.open(grammar_path)

    def get_valid_next_tokens(
        self,
        partial_code: str,
        all_tokens: List[str]
    ) -> List[str]:
        """Return tokens that keep code parseable."""
        valid = []

        for token in all_tokens:
            candidate = partial_code + token
            try:
                # Check if still parseable (with error recovery)
                self.parser.parse(candidate, on_error=self._allow_incomplete)
                valid.append(token)
            except:
                pass

        return valid

    def decode_with_constraints(
        self,
        model: Model,
        prompt: str
    ) -> str:
        """Generate with syntax constraints."""
        tokens = []

        while True:
            # Get model's token probabilities
            probs = model.get_next_token_probs(prompt + ''.join(tokens))

            # Filter to valid tokens
            valid = self.get_valid_next_tokens(''.join(tokens), vocab)

            # Sample from valid tokens only
            valid_probs = {t: probs[t] for t in valid}
            next_token = sample_from(valid_probs)

            if next_token == '<eos>':
                break
            tokens.append(next_token)

        return ''.join(tokens)
```

### Type-Aware Generation

Use type hints to constrain generation:

```python
def type_guided_completion(
    context: str,
    expected_type: str,
    model: Model
) -> str:
    """Generate code that satisfies type constraints."""

    type_examples = {
        "List[int]": ["[1, 2, 3]", "list(range(10))", "sorted(items)"],
        "str": ['"hello"', "f'value: {x}'", "text.strip()"],
        "bool": ["True", "False", "x > 0", "item in collection"],
        "Dict[str, Any]": ["{'key': value}", "dict(zip(keys, vals))"],
    }

    # Add type hint to prompt
    enhanced_prompt = f"""
{context}
# Note: Return type should be {expected_type}
# Examples of valid expressions:
{chr(10).join(f'#   {ex}' for ex in type_examples.get(expected_type, []))}
"""

    # Generate with lower temperature for type safety
    result = model.generate(enhanced_prompt, temperature=0.1)

    # Validate with type checker
    if not type_check(result, expected_type):
        # Retry with explicit type
        result = model.generate(
            enhanced_prompt + f"\n# Must return {expected_type}:\nreturn ",
            temperature=0.0
        )

    return result
```

---

## 🎯 Practical Applications

### 1. Code Review Bot

```python
class CodeReviewBot:
    """Automated code review using LLMs."""

    REVIEW_PROMPT = """Review this code change for:
1. Bugs or logic errors
2. Security vulnerabilities
3. Performance issues
4. Style/readability improvements

Provide specific, actionable feedback.

```diff
{diff}
```

Review:"""

    def review_pr(self, diff: str) -> List[ReviewComment]:
        response = self.model.generate(
            self.REVIEW_PROMPT.format(diff=diff),
            max_tokens=1000
        )
        return self._parse_review(response)

    def _parse_review(self, response: str) -> List[ReviewComment]:
        """Parse review into structured comments."""
        comments = []
        # Extract line numbers and feedback
        # Format: L{line}: {comment}
        for line in response.split('\n'):
            if match := re.match(r'L(\d+):\s*(.+)', line):
                comments.append(ReviewComment(
                    line=int(match.group(1)),
                    comment=match.group(2)
                ))
        return comments
```

### 2. Test Generation

```python
def generate_tests(
    function_code: str,
    context: str = ""
) -> str:
    """Generate unit tests for a function."""

    prompt = f"""Write comprehensive unit tests for this function.
Include:
- Happy path tests
- Edge cases (empty, None, boundary values)
- Error cases (invalid input)

Context:
{context}

Function:
```python
{function_code}
```

Tests (using pytest):
```python
"""

    tests = model.generate(prompt, max_tokens=1000)

    # Validate tests are syntactically correct
    try:
        ast.parse(tests)
    except SyntaxError:
        # Retry with simpler prompt
        tests = model.generate(
            f"Write a test for:\n{function_code}\n\ndef test_",
            max_tokens=500
        )

    return tests
```

### 3. Documentation Generator

```python
def generate_docstring(
    function_code: str,
    style: str = "google"
) -> str:
    """Generate docstring for a function."""

    style_examples = {
        "google": '''
def example(param1: int, param2: str) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When something is wrong.
    """''',
        "numpy": '''
def example(param1, param2):
    """
    Short description.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str
        Description of param2.

    Returns
    -------
    bool
        Description of return value.
    """'''
    }

    prompt = f"""Add a {style}-style docstring to this function.

Style example:
{style_examples[style]}

Function to document:
{function_code}

Function with docstring:
"""

    return model.generate(prompt, temperature=0.3)
```

---

## 🧪 Hands-On Exercises

### Exercise 1: Build a Simple Code Completer

```python
# TODO: Implement a code completion function
def simple_completer(prefix: str, suffix: str = "") -> str:
    """
    Complete code given prefix and optional suffix.

    If suffix is provided, use FIM format.
    Otherwise, use standard completion.

    Test cases:
    1. prefix="def add(a, b):\n    ", suffix=""
       → "return a + b"
    2. prefix="def greet(name):\n    message = ", suffix="\n    return message"
       → 'f"Hello, {name}!"'
    """
    pass
```

### Exercise 2: Implement Pass@k Evaluation

```python
# TODO: Evaluate a model on HumanEval-style problems
def evaluate_pass_at_k(
    model: Model,
    problems: List[Dict],
    k: int = 10,
    n_samples: int = 20
) -> float:
    """
    Evaluate model on coding problems.

    Each problem has:
    - prompt: The function signature and docstring
    - test: Test code to validate solution
    - entry_point: Function name to call

    Returns pass@k score.
    """
    pass
```

### Exercise 3: Build a Code Search System

```python
# TODO: Build semantic code search
class CodeSearchEngine:
    """
    Search a codebase semantically.

    Features:
    1. Index code by function/class
    2. Embed with code-specific model
    3. Search by natural language query
    4. Return relevant code snippets
    """

    def index_repository(self, repo_path: str):
        """Index all code files."""
        pass

    def search(self, query: str, k: int = 5) -> List[CodeSnippet]:
        """Search for relevant code."""
        pass
```

---

## 📚 Further Reading

### Papers
- "Evaluating Large Language Models Trained on Code" (Codex paper, 2021)
- "StarCoder: May the Source Be with You!" (BigCode, 2023)
- "Code Llama: Open Foundation Models for Code" (Meta, 2023)
- "DeepSeek Coder: When the Large Language Model Meets Programming" (2024)
- "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (2023)
- "Efficient Training of Language Models to Fill in the Middle" (FIM paper, 2022)

### Tutorials
- HuggingFace Code Generation Guide
- BigCode Documentation
- DeepSeek Coder Examples

### Benchmarks
- HumanEval: github.com/openai/human-eval
- MBPP: github.com/google-research/google-research/tree/master/mbpp
- SWE-bench: swe-bench.github.io

---

## 💡 Did You Know? (Bonus)

### The 100K Context Breakthrough

CodeLlama's 100K context window wasn't magic—it came from a clever RoPE (Rotary Position Embedding) scaling trick. Raymond Li and the Meta team discovered that if you train briefly on longer sequences while adjusting the RoPE base frequency, the model learns to extrapolate positions it never saw during original training. They went from 4K → 16K → 100K context with minimal additional training, enabling whole-repository understanding.

---

## ✅ Knowledge Check

1. **What is FIM and why is it important for code completion?**

2. **Explain the difference between pass@1 and pass@100 metrics.**

3. **Why do code models need longer context windows than text models?**

4. **How does speculative decoding speed up code generation?**

5. **What makes SWE-bench harder than HumanEval?**

---

## ⏭️ Next Steps

You now understand how AI coding assistants work under the hood! In Module 35, we'll explore **RLHF (Reinforcement Learning from Human Feedback)**—how models like ChatGPT learn to be helpful, harmless, and honest.

**Up Next**: Module 35 - RLHF & How LLMs Are Trained 🔮

---

_Module 34 Complete! You now understand code generation models!_
_"The best code model doesn't just complete—it understands."_
