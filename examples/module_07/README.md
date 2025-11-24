# Module 7 Examples: Tokenization & Text Processing

This directory contains working code examples for Module 7: Tokenization & Text Processing.

## Overview

These examples demonstrate how LLMs tokenize text and how to optimize token usage for cost-effective AI applications. You'll learn to count tokens, optimize prompts, and handle multilingual tokenization.

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

**Note**: These examples use `tiktoken`, OpenAI's tokenizer library. While we use it for demonstration, the concepts apply to all LLM tokenizers (Claude, Llama, etc.).

## Examples

### Example 1: Token Counter (`01_token_counter.py`)

**What it does**: Demonstrates basic token counting using tiktoken.

**Run**:
```bash
python 01_token_counter.py
```

**You'll learn**:
- How to count tokens in text
- How text is split into tokens
- Token efficiency across different content types
- API cost estimation
- Context window analysis

**Key concepts**:
- 1 token ≈ 0.75 words (English)
- 1 token ≈ 4 characters (English)
- Code uses 3-4x more tokens than prose
- Different models have different context windows

**Example output**:
```
TEXT: Hello, world!
Token count: 4
Tokens: ['Hello', ',', ' world', '!']
```

---

### Example 2: Token Optimization (`02_optimization.py`)

**What it does**: Demonstrates 6 strategies for reducing token counts and API costs.

**Run**:
```bash
python 02_optimization.py
```

**You'll learn**:
- Remove unnecessary verbosity (30-50% savings)
- Minimize system prompts (60-70% savings)
- Use efficient formatting (30-40% savings)
- Batch processing strategies
- Real-world RAG system optimization
- When to optimize vs when to preserve clarity

**Optimization strategies covered**:
1. **Remove Verbosity**: "Could you please..." → "Write..."
2. **Minimize System Prompts**: Keep them short and essential
3. **Efficient Formatting**: Minify JSON, remove whitespace
4. **Careful Abbreviations**: Balance brevity with clarity
5. **Batch Processing**: Combine multiple requests
6. **Remove Unnecessary Examples**: When model can infer

**Cost impact**:
- At 1M requests/month, 20-30% optimization = thousands in savings
- RAG systems benefit most (large context chunks)
- High-volume chatbots see immediate ROI

---

### Example 3: Multilingual Tokenization (`03_multilingual.py`)

**What it does**: Compares tokenization efficiency across 15+ languages.

**Run**:
```bash
python 03_multilingual.py
```

**You'll learn**:
- How different languages tokenize differently
- Why non-English text uses more tokens
- Cost implications for multilingual applications
- Emoji and special character tokenization
- Best practices for multilingual apps

**Key findings**:
- **English**: Baseline (most efficient)
- **European languages** (Spanish, French, German): 1.2-1.5x tokens
- **Cyrillic** (Russian): 2-2.5x tokens
- **CJK** (Chinese, Japanese, Korean): 2-3x tokens
- **Arabic, Hebrew**: 2-2.5x tokens
- **Emoji**: 1-10 tokens (complex emoji like flags are expensive!)

**Cost impact**:
- 1M requests in Japanese = 2-3x cost vs English
- Budget accordingly for multilingual applications
- Consider language-specific models for high-volume languages

---

## Quick Start

**Run all examples in sequence**:
```bash
python 01_token_counter.py
python 02_optimization.py
python 03_multilingual.py
```

**Or run individually to focus on specific topics.**

---

## Key Takeaways

### Token Counting
- Always count tokens before making API calls
- Use tiktoken for GPT models, anthropic SDK for Claude
- Budget for 20-30% more tokens than you estimate

### Optimization
- High-volume applications benefit most from optimization
- Balance token savings with output quality
- Even 10-20% optimization = significant savings at scale
- RAG systems have highest optimization potential

### Multilingual
- Non-English languages use 1.5-3x more tokens
- Test tokenization in ALL target languages before launch
- Budget 2-3x API costs for multilingual applications
- Consider multilingual models (Llama, mBERT) for better efficiency

### Real-World Applications
- **Chatbots**: Optimize system prompts and responses
- **RAG Systems**: Carefully manage context token budgets
- **Code Generation**: Budget 3-4x tokens vs prose
- **Multilingual Apps**: Budget 2-3x for non-English

---

## Common Gotchas

1. **Whitespace matters**: "Hello world" ≠ "Helloworld" (different tokenization)
2. **Capitalization matters**: "PYTHON" uses more tokens than "python"
3. **Numbers tokenize differently**: Large numbers may be multiple tokens
4. **Code is expensive**: Plan for 3-4x token usage
5. **Emoji are unpredictable**: Simple emoji = 1-2 tokens, complex = 5-10 tokens

---

## Cost Calculator

**Quick reference** (2025 pricing - check current rates!):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-4o | $2.50 | $10.00 |
| GPT-4-turbo | $10.00 | $30.00 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude 3 Opus | $15.00 | $75.00 |

**Example scenarios** (using GPT-4o pricing):

| Use Case | Tokens/Request | Requests/Month | Monthly Cost |
|----------|----------------|----------------|--------------|
| Simple chatbot | 200 | 100K | $25 |
| RAG system | 1000 | 50K | $125 |
| Code generation | 500 | 20K | $25 |
| Multilingual chatbot (Japanese) | 400 | 100K | $100 |

**With 20% optimization**:
- Simple chatbot: $25 → $20 (save $5/month = $60/year)
- RAG system: $125 → $100 (save $25/month = $300/year)

**Note**: Prices drop regularly! GPT-4 launched at $0.03/1K (2023) → GPT-4o now $0.0025/1K (2025) = **12x cheaper!**

---

## Practical Exercises

After running the examples, try these exercises:

1. **Analyze your own prompts**:
   - Copy a prompt you use frequently
   - Run it through `01_token_counter.py`
   - Identify optimization opportunities
   - Measure token savings

2. **Optimize a real prompt**:
   - Take a verbose prompt
   - Apply optimization strategies from `02_optimization.py`
   - Compare token counts before/after
   - Calculate cost savings at scale

3. **Test multilingual support**:
   - If building multilingual app, use `03_multilingual.py`
   - Test tokenization in your target languages
   - Budget API costs accordingly

4. **Build a RAG context manager**:
   - Write a function that fits max documents in context window
   - Use token counting to determine how many docs to include
   - Test with different context window sizes

---

## Tips for Production

### Always Count Tokens
```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Before API call
token_count = count_tokens(prompt)
if token_count > MAX_TOKENS:
    # Truncate or optimize
    prompt = optimize_prompt(prompt, MAX_TOKENS)
```

### Monitor in Production
```python
# Log token usage
logger.info(f"Request tokens: {input_tokens}, Response tokens: {output_tokens}, Cost: ${cost}")

# Track by endpoint/feature
metrics.record("api.tokens.input", input_tokens, tags={"feature": "chat"})
metrics.record("api.tokens.output", output_tokens, tags={"feature": "chat"})
```

### Implement Token Budgets
```python
class TokenBudget:
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def can_fit(self, text: str) -> bool:
        tokens = count_tokens(text)
        return self.used_tokens + tokens <= self.max_tokens

    def add(self, text: str) -> bool:
        tokens = count_tokens(text)
        if self.can_fit(text):
            self.used_tokens += tokens
            return True
        return False
```

---

## Further Reading

- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) - Visualize tokenization
- [Tiktoken GitHub](https://github.com/openai/tiktoken) - Fast tokenizer library
- [BPE Paper](https://arxiv.org/abs/1508.07909) - Original BPE algorithm
- [SentencePiece Paper](https://arxiv.org/abs/1808.06226) - Language-agnostic tokenization

---

## Next Steps

After mastering tokenization:
- **Module 8**: Text Generation & Sampling Strategies
  - How LLMs generate text
  - Temperature, top-p, top-k sampling
  - Controlling output quality

---

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'tiktoken'`
**Solution**: Run `pip install -r requirements.txt`

**Issue**: Different token counts than expected
**Solution**: Different models use different tokenizers. GPT-4 tokenizer ≠ Claude tokenizer ≠ Llama tokenizer.

**Issue**: Token count seems high
**Solution**: Remember code, whitespace, and special characters all count as tokens!

---

**🥋 Neural Dojo - Master tokenization, optimize costs, build efficiently! 🧠⚡**
