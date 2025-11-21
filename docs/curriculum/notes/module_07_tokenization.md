# Module 7: Tokenization & Text Processing

**Last Updated**: 2025-11-21
**Status**: 🟢 Complete
**Duration**: 4-5 hours
**Prerequisites**: Module 6

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand how text becomes tokens
- Learn different tokenization algorithms (BPE, WordPiece, SentencePiece)
- Master token counting and optimization
- Understand why token limits matter for costs and performance
- Handle multilingual text tokenization
- Optimize prompts for token efficiency

---

## 📖 Introduction

**Question**: Why does "Hello world" cost more than "Hi there" even though they're both simple greetings?

**Answer**: Tokenization.

LLMs don't process raw text. They process **tokens** - and the number of tokens determines:
- API costs (charged per token)
- Context window limits (max tokens processable)
- Generation speed (more tokens = slower)

**This module teaches you the hidden language of LLMs**: How text becomes tokens.

---

## 🔤 What Are Tokens?

### The Simple Definition

**Token**: A unit of text that the model processes.

**Not necessarily**:
- A word
- A character
- A fixed length

**Examples**:
```
"Hello world" → ["Hello", " world"] (2 tokens)
"Hello" → ["Hello"] (1 token)
"Hellooooo" → ["Hello", "o", "o", "o", "o"] (5 tokens)
```

---

### Why Not Just Characters?

**Problem with characters**:
- Vocabulary = 256 (for ASCII/UTF-8)
- Sequences very long: "Hello" = 5 tokens
- Model must learn letter combinations → words

**Problem with words**:
- Vocabulary = millions (all words in all languages)
- Can't handle new words or typos
- Different languages have different word structures

**Subword tokenization** = Sweet spot!
- Vocabulary = 30K-100K tokens
- Handles new words (break into known parts)
- Efficient sequence lengths

---

## 🧬 Tokenization Algorithms

### 1. Byte-Pair Encoding (BPE)

**Used by**: GPT-2, GPT-3, GPT-4, many others

**How it works**:

**Step 1**: Start with character-level splits
```
"lower" → ["l", "o", "w", "e", "r"]
```

**Step 2**: Find most frequent pair
```
"l" + "o" appears most → merge to "lo"
"lower" → ["lo", "w", "e", "r"]
```

**Step 3**: Repeat until vocabulary size reached
```
Iteration 2: "lo" + "w" → "low"
"lower" → ["low", "e", "r"]

Iteration 3: "low" + "e" → "lowe"
"lower" → ["lowe", "r"]

Iteration 4: "lowe" + "r" → "lower"
"lower" → ["lower"]
```

**Result**: Common words = 1 token, rare words = multiple tokens

---

**Example**:
```
Common word: "the" → 1 token (appears billions of times)
Rare word: "antidisestablishmentarianism" → 7 tokens
Code: "def fibonacci" → 2 tokens ("def", " fibonacci")
```

**Advantage**: Works with any text, handles rare words gracefully

**Disadvantage**: Sensitive to whitespace and capitalization

---

### 2. WordPiece

**Used by**: BERT, many Google models

**Similar to BPE but**:
- Merges based on likelihood increase (not just frequency)
- Uses `##` prefix for non-initial subwords

**Example**:
```
"unhappiness" → ["un", "##happiness"]
"happiness" → ["happiness"]
```

The `##` indicates this is not the start of a word.

**Advantage**: Better handles word morphology

**Disadvantage**: Still sensitive to preprocessing

---

### 3. SentencePiece

**Used by**: Llama, T5, many multilingual models

**Key difference**: Treats space as a character (`▁`)

**Example**:
```
"Hello world" → ["▁Hello", "▁world"]
```

**Advantages**:
- Language-agnostic (works for languages without spaces: Chinese, Japanese)
- No pre-tokenization needed
- Reversible (can convert back to original text)

**This is the modern standard for new models!**

---

## 📊 Token Counting Examples

### English Text

```python
"Hello, world!"
# GPT: 4 tokens ["Hello", ",", " world", "!"]

"The quick brown fox jumps over the lazy dog"
# GPT: 9 tokens

"I'm learning about tokenization"
# GPT: 5 tokens ["I", "'m", " learning", " about", " tokenization"]
```

**Pattern**: Common words = 1 token each

---

### Code

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# GPT: ~40 tokens
```

**Code is expensive!**
- Keywords: 1 token each
- Variable names: Often 1-2 tokens
- Indentation: Tokens!
- Each space/newline: Tokens!

**Did You Know?** 🤓
Code typically uses 3-4x more tokens than English prose for the same character count. This is why API costs add up fast for code generation!

---

### Multilingual Text

```python
"Hello" (English) → 1 token
"Bonjour" (French) → 1 token
"こんにちは" (Japanese) → 3-5 tokens
"مرحبا" (Arabic) → 2-3 tokens
```

**Key insight**: Models trained primarily on English tokenize non-English less efficiently.

**This is why**: Multilingual models use SentencePiece and train on diverse languages!

---

### Special Tokens

**Most tokenizers include special tokens**:
- `<|endoftext|>`: End of document
- `<|im_start|>`, `<|im_end|>`: Message boundaries
- `<|pad|>`: Padding token
- `<|unk|>`: Unknown token (for untokenizable text)

**These don't appear in output but**:
- Count toward context window
- Used internally by model

---

## 🔢 Token Math: Why It Matters

### API Costs

**OpenAI GPT-4**:
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

**Example Conversation**:
```
System: "You are a helpful assistant" → 6 tokens
User: "Write a Python function to reverse a string" → 9 tokens
Assistant: [200 token response]

Cost = (6 + 9) * $0.03/1000 + 200 * $0.06/1000
     = $0.00045 + $0.012
     = $0.01245 per request
```

**At scale**:
- 1M requests/month = $12,450/month
- Optimizing prompt from 100 → 50 tokens = 50% cost savings!

---

### Context Window Limits

**Claude 3.5 Sonnet**: 200,000 token context window

**What fits**:
- ~150,000 words of text
- ~75,000 lines of code
- Or: Entire codebase + conversation + RAG docs

**But if you exceed**:
- Request fails
- Must chunk/truncate
- Lose context

**Token counting is critical for**:
- RAG systems (how much context to include?)
- Long conversations (when to summarize?)
- Document processing (can this fit?)

---

## 🎯 Token Optimization Strategies

### Strategy 1: Shorter Prompts

**Before** (15 tokens):
```
"Could you please help me by writing a function that calculates"
```

**After** (7 tokens):
```
"Write a function to calculate"
```

**Savings**: 53% fewer tokens

**When to use**: High-volume, simple tasks

---

### Strategy 2: Remove Boilerplate

**Before** (25 tokens):
```
System: "You are a helpful AI assistant created by Anthropic. You should always be polite and respectful."
```

**After** (8 tokens):
```
System: "You are a helpful assistant."
```

**Savings**: 68% fewer tokens

**When to use**: Unless specific behavior needed, keep system prompts short

---

### Strategy 3: Efficient Formatting

**Before** (JSON with whitespace):
```json
{
  "name": "John",
  "age": 30,
  "city": "New York"
}
```
**Tokens**: ~20

**After** (minified):
```json
{"name":"John","age":30,"city":"New York"}
```
**Tokens**: ~12

**Savings**: 40% fewer tokens

---

### Strategy 4: Use Abbreviations (Carefully!)

**Before**:
```
"Analyze the following document and provide a summary"
```

**After**:
```
"Analyze and summarize:"
```

**But**: Only if it doesn't hurt clarity!

**Balance**: Token savings vs model performance

---

### Strategy 5: Batch Processing

**Instead of**:
```
10 separate requests with same system prompt (repeated 10x)
```

**Do**:
```
1 request with 10 items, 1 system prompt
```

**Savings**: Massive for high system prompt overhead

---

## 🧪 Token Counter Tools

### Using Tiktoken (OpenAI's tokenizer)

```python
import tiktoken

# For GPT-4
encoding = tiktoken.encoding_for_model("gpt-4")

text = "Hello, world!"
tokens = encoding.encode(text)

print(f"Text: {text}")
print(f"Tokens: {tokens}")
print(f"Token count: {len(tokens)}")
print(f"Decoded: {[encoding.decode([t]) for t in tokens]}")
```

**Output**:
```
Text: Hello, world!
Tokens: [9906, 11, 1917, 0]
Token count: 4
Decoded: ['Hello', ',', ' world', '!']
```

---

### Anthropic Token Counting

**Option 1**: Use API response
```python
response = client.messages.create(...)
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
```

**Option 2**: Count before sending (approximate)
```python
# Rule of thumb: 1 token ≈ 4 characters for English
estimated_tokens = len(text) / 4
```

---

### Online Tools

**Tokenizer Visualizers**:
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer)
- [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers)

**Use these to**:
- Understand how your text is tokenized
- Optimize prompts
- Debug unexpected token counts

---

## 🌍 Multilingual Tokenization

### The Challenge

**English-centric training** → inefficient non-English tokenization

**Example**:
```
"Hello" (English) → 1 token
"Привет" (Russian) → 3 tokens (same meaning!)
```

**Impact**:
- Higher costs for non-English users
- Worse performance (more tokens = more to process)
- Unfair pricing (same content costs more)

---

### Solutions

**1. Multilingual Tokenizers**:
- SentencePiece with multilingual training corpus
- Models: mBERT, XLM-R, multilingual GPT models

**2. Language-Specific Fine-tuning**:
- Train tokenizer on target language
- Used in language-specific variants (e.g., CamemBERT for French)

**3. Byte-Level Tokenization**:
- Fall back to byte-level encoding for rare scripts
- Ensures all text is tokenizable

---

### Best Practices for Multilingual

**If building multilingual app**:
1. Test token counts in all target languages
2. Budget for 2-3x token usage for non-English
3. Consider language-specific models for high-volume languages
4. Use SentencePiece-based models (Llama, T5)

---

## 🐛 Common Tokenization Gotchas

### Gotcha 1: Whitespace Matters

```python
"Hello world" → 2 tokens
"Helloworld" → 2 tokens (different split!)
```

**Lesson**: Whitespace affects tokenization

---

### Gotcha 2: Capitalization Matters

```python
"Python" → 1 token
"python" → 1 token
"PYTHON" → 2 tokens (["PY", "THON"])
```

**Lesson**: Consistent casing can save tokens

---

### Gotcha 3: Numbers

```python
"123" → 1 token
"12345" → 1 token
"123456789" → 2-3 tokens
```

**Numbers tokenized differently than text!**

---

### Gotcha 4: Code is Expensive

```python
# 50 characters of English prose: ~12 tokens
# 50 characters of Python code: ~25 tokens
```

**Lesson**: Budget more for code generation tasks

---

### Gotcha 5: Emoji

```python
"😀" → 1-2 tokens (depending on tokenizer)
"🏴󠁧󠁢󠁳󠁣󠁴󠁿" → 7-8 tokens (flag: Scotland)
```

**Lesson**: Emoji can be surprisingly expensive!

---

## 💡 Real-World Applications

### RAG Systems

**Problem**: How much context to include?

**Solution**: Token counting!

```python
def prepare_rag_context(query, docs, max_tokens=150000):
    """Include as many docs as fit in context window."""
    context_tokens = count_tokens(query)
    included_docs = []

    for doc in docs:
        doc_tokens = count_tokens(doc)
        if context_tokens + doc_tokens < max_tokens:
            included_docs.append(doc)
            context_tokens += doc_tokens
        else:
            break

    return included_docs
```

---

### Conversation Summarization

**Problem**: Long conversations exceed context window

**Solution**: Summarize old messages when token limit approached

```python
def manage_conversation(messages, max_tokens=8000):
    """Summarize old messages to stay under limit."""
    total_tokens = sum(count_tokens(m) for m in messages)

    if total_tokens > max_tokens * 0.8:  # 80% threshold
        # Summarize first half of conversation
        old_messages = messages[:len(messages)//2]
        summary = summarize(old_messages)  # Using LLM
        messages = [summary] + messages[len(messages)//2:]

    return messages
```

---

### Cost Optimization

**Before**:
```python
# Calling API without token awareness
response = call_llm(long_prompt)  # ???  tokens
```

**After**:
```python
# Count tokens first
token_count = count_tokens(long_prompt)
estimated_cost = token_count * COST_PER_TOKEN

if estimated_cost > budget:
    # Optimize or truncate prompt
    prompt = optimize_prompt(long_prompt, max_tokens=budget / COST_PER_TOKEN)

response = call_llm(prompt)
```

---

## 🎓 Key Takeaways

1. **Tokens ≠ words**: Subword tokenization is the standard
2. **BPE, WordPiece, SentencePiece**: Different algorithms, similar goals
3. **Code is expensive**: ~3-4x tokens compared to prose
4. **Multilingual is harder**: Non-English uses more tokens
5. **Count before calling**: Avoid surprises in API costs
6. **Optimize prompts**: Shorter prompts = lower costs + faster
7. **Context limits are real**: Token counting prevents failures
8. **Special tokens exist**: Don't forget about system prompts and message boundaries

---

## 🚫 Common Misconceptions

### Myth 1: "1 token = 1 word"
**Reality**: 1 token ≈ 0.75 words (English). Varies by language and content type.

### Myth 2: "Tokenization is just splitting on spaces"
**Reality**: Complex algorithm (BPE/WordPiece/SentencePiece) that learns from data.

### Myth 3: "All models use same tokenizer"
**Reality**: Each model family has its own tokenizer. GPT ≠ Claude ≠ Llama.

### Myth 4: "Token count doesn't matter for small prompts"
**Reality**: At scale, even small optimizations = big savings.

### Myth 5: "Tokenization is deterministic"
**Reality**: Yes, but depends on the specific tokenizer version!

---

## 📚 Further Reading

### Papers
- ["Neural Machine Translation of Rare Words with Subword Units"](https://arxiv.org/abs/1508.07909) (Sennrich et al., 2016) - BPE
- ["SentencePiece: A simple and language independent approach"](https://arxiv.org/abs/1808.06226) (Kudo & Richardson, 2018)

### Tools
- [Tiktoken](https://github.com/openai/tiktoken) - OpenAI's fast tokenizer
- [Hugging Face Tokenizers](https://github.com/huggingface/tokenizers) - Fast, multilingual
- [SentencePiece](https://github.com/google/sentencepiece) - Google's tokenizer

### Interactive
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) - Visualize GPT tokenization
- [Hugging Face Tokenizer Playground](https://huggingface.co/spaces/Xenova/the-tokenizer-playground)

---

## ✅ Knowledge Check

Before moving to Module 8, you should be able to:

- [ ] Explain what a token is
- [ ] Describe how BPE tokenization works
- [ ] Calculate approximate token counts for text
- [ ] Understand why code uses more tokens than prose
- [ ] Optimize prompts for token efficiency
- [ ] Use tiktoken or similar tools to count tokens
- [ ] Explain why multilingual tokenization is challenging
- [ ] Apply token counting to real-world problems (RAG, conversations)

---

## 🎯 What's Next

**Module 8**: Text Generation & Sampling Strategies
- How LLMs generate text (autoregressive generation)
- Temperature, top-p, top-k sampling
- Controlling generation quality
- Repetition penalties

**You'll learn**:
- Why temperature=0.0 gives same output every time
- How to make models more creative (or more focused)
- Why some outputs are better than others

---

**Remember**: Tokens are the currency of LLMs. Understanding tokenization helps you optimize costs, stay within context limits, and build better AI systems.

**Let's learn how to generate text! 🥋🧠⚡**

---

_Last updated: 2025-11-21_
_Version: 1.0_
