# Module 2 Examples: Prompt Engineering Fundamentals

**Module**: Prompt Engineering Fundamentals 🔮
**Purpose**: Master the art of crafting effective prompts for LLMs

---

## 📋 Prerequisites

```bash
# Ensure you have API keys configured
cp ../../.env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY

# Install dependencies
pip install -r requirements.txt
```

---

## 📂 Examples Structure

### 🎯 Technique Demonstrations

#### 1. **Zero-Shot vs Few-Shot** (`01_zero_vs_few_shot.py`)
- Compares zero-shot and few-shot prompting
- Shows dramatic improvement with examples
- **Run**: `python 01_zero_vs_few_shot.py`

#### 2. **Chain-of-Thought** (`02_chain_of_thought.py`)
- Demonstrates CoT prompting for reasoning
- Compares with/without "show your work"
- **Run**: `python 02_chain_of_thought.py`

#### 3. **Role Prompting** (`03_role_prompting.py`)
- Same question, different roles
- Shows how roles affect output
- **Run**: `python 03_role_prompting.py`

#### 4. **Structured Outputs** (`04_structured_outputs.py`)
- Getting JSON, tables, specific formats
- Using constraints for consistency
- **Run**: `python 04_structured_outputs.py`

#### 5. **Iterative Refinement** (`05_iterative_refinement.py`)
- Progressive prompt improvement
- Real conversation flow
- **Run**: `python 05_iterative_refinement.py`

---

### 🛠️ Practical Applications

#### 6. **Prompt Library** (`06_prompt_library.py`)
- Reusable prompt templates
- Template engine for common tasks
- **Run**: `python 06_prompt_library.py`

#### 7. **Code Tasks** (`07_code_tasks.py`)
- Explanation, debugging, refactoring prompts
- Real coding use cases
- **Run**: `python 07_code_tasks.py`

---

### 🔒 Security

#### 8. **Prompt Injection Demo** (`08_prompt_injection.py`)
- Demonstrates injection attacks
- Shows defense mechanisms
- **Run**: `python 08_prompt_injection.py`

---

## 🎯 Learning Objectives

After running these examples, you will:

- ✅ Understand when to use zero-shot vs few-shot
- ✅ Apply chain-of-thought for complex reasoning
- ✅ Use role prompting effectively
- ✅ Get structured, consistent outputs
- ✅ Build reusable prompt templates
- ✅ Recognize and defend against prompt injection

---

## 💡 Tips for Success

### Running Examples

1. **Read the code first** - Understanding the technique before seeing output
2. **Modify prompts** - Experiment with different variations
3. **Compare results** - See how small changes affect output
4. **Build your library** - Save prompts that work well for you

### Best Practices

- **Start simple** (zero-shot) → Add examples if needed (few-shot)
- **Use CoT** for anything requiring multi-step reasoning
- **Specify format** when you need structured output
- **Iterate!** First prompt is rarely perfect

---

## 📊 Expected Insights

### Zero-Shot vs Few-Shot
You'll see that 2-3 examples can improve accuracy from ~60% to ~95% on structured tasks.

### Chain-of-Thought
Complex reasoning problems improve 20-40% just by adding "Let's think step by step"

### Role Prompting
Same question to "5-year-old teacher" vs "PhD professor" = completely different (both useful!) answers

---

## 🚀 Next Steps

1. **Run all examples** to see techniques in action
2. **Complete Module 2 deliverables** in `docs/deliverables/`
3. **Build your prompt library** with templates you'll actually use
4. **Apply to real projects** (kaizen, vibe, contrarian)

---

## 📝 Notes

- All examples use Claude API (easily adaptable to OpenAI)
- Each example is self-contained and runnable
- Prompts are designed to be educational AND practical

---

**Built with AI assistance as part of Neural Dojo 🥋🧠⚡**
