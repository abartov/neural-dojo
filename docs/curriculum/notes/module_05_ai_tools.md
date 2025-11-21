# Module 5: Building with AI Coding Assistants

**Last Updated**: 2025-11-21
**Status**: 🟢 Complete
**Duration**: 5-6 hours
**Prerequisites**: Modules 1-4

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master Claude Code workflows and best practices
- Understand GitHub Copilot patterns and limitations
- Learn Cursor IDE advanced features
- Build a complete project using AI assistance
- Develop your personal AI-assisted development workflow
- Know when to use which tool

---

## 📖 Introduction

You've learned AI development patterns (Module 1), prompt engineering (Module 2), code generation (Module 3), and debugging (Module 4).

**Now it's time to put it all together**: Building real projects with AI coding assistants as your daily tools.

---

## 🛠️ The AI Coding Assistant Landscape

### Current Tools (2024-2025)

**1. Claude Code**
- Context-aware conversations
- Long context windows (200K tokens)
- Excellent for complex reasoning
- File operations and git integration
- **Best for**: Architecture, refactoring, complex problems

**2. GitHub Copilot**
- Inline code suggestions
- Fast autocomplete
- IDE integration
- **Best for**: Boilerplate, standard patterns, quick completions

**3. Cursor IDE**
- Full IDE with AI built-in
- Chat + inline suggestions
- Codebase understanding
- **Best for**: Greenfield projects, rapid prototyping

**4. Others**
- Tabnine: Privacy-focused
- Codeium: Free alternative
- Amazon CodeWhisperer: AWS-optimized

---

## 🔮 Claude Code: Deep Dive

### What Makes Claude Code Special

**Strengths**:
- ✅ Long context (can see entire files)
- ✅ Multi-file understanding
- ✅ Sophisticated reasoning
- ✅ Git operations
- ✅ File manipulation
- ✅ Terminal command execution

**Use Cases**:
1. **Architecture decisions**: "Should I use X or Y pattern?"
2. **Refactoring**: "Refactor this module to use dependency injection"
3. **Complex debugging**: "Why is this distributed system failing?"
4. **Documentation**: "Generate API docs for this module"
5. **Code review**: "Review this PR for issues"

---

### Claude Code Workflows

#### Workflow 1: Feature Development

```
You: "I need to add user authentication to my FastAPI app.
      Use JWT tokens, integrate with PostgreSQL users table,
      add login/logout/refresh endpoints."

Claude: [Analyzes codebase]
        [Generates auth module]
        [Updates existing code]
        [Creates tests]
        [Updates docs]

You: [Review, test, iterate]
```

**Key**: Provide context about existing codebase.

---

#### Workflow 2: Debugging Complex Issues

```
You: "Users reporting intermittent 500 errors on /api/orders
      Logs show: [paste logs]
      Recent changes: [git diff]
      Help debug systematically"

Claude: [Analyzes logs]
        [Reviews recent changes]
        [Identifies likely causes]
        [Suggests investigation steps]
        [Proposes fixes]

You: [Test hypotheses]
     [Apply fix]
     [Verify]
```

---

#### Workflow 3: Code Review

```
You: "Review this PR: [link or paste diff]
      Focus on: security, performance, maintainability"

Claude: [Analyzes changes]
        [Identifies issues]
        [Suggests improvements]
        [Provides fixed code]

You: [Address feedback]
     [Update PR]
```

---

### Claude Code Best Practices

**1. Provide Context**
```
Bad: "Fix this function"

Good: "This function processes orders in our e-commerce system.
       It's slow when handling >100 items.
       Context: We use PostgreSQL, Redis cache, background workers.
       [paste function]"
```

**2. Iterate Visibly**
```
"That approach works but uses too much memory.
 Can we optimize for memory at the cost of some CPU?"
```

**3. Ask for Explanations**
```
"Explain this solution as if to a junior developer.
 Why is this approach better than [alternative]?"
```

**4. Request Multiple Options**
```
"Give me 3 approaches:
 1. Quick fix (may have limitations)
 2. Proper refactor (more work)
 3. Long-term solution (architectural change)"
```

---

## 🚀 GitHub Copilot: Deep Dive

### What Makes Copilot Special

**Strengths**:
- ✅ Lightning-fast suggestions
- ✅ Inline code completion
- ✅ Learns your coding style
- ✅ Works in IDE flow
- ✅ Great for boilerplate

**Use Cases**:
1. **Autocomplete**: Type function name, get implementation
2. **Tests**: Write test structure, Copilot fills in assertions
3. **Boilerplate**: CRUD operations, API endpoints
4. **Standard patterns**: Error handling, logging
5. **Comments to code**: Write comment, get implementation

---

### Copilot Workflows

#### Workflow 1: Test-Driven Development

```python
# 1. Write test structure
def test_calculate_discount():
    # Test happy path
    # [Copilot suggests: assert calculate_discount(100, 0.1) == 90]

    # Test edge cases
    # [Copilot suggests: assert calculate_discount(0, 0.1) == 0]
    # [Copilot suggests: assert calculate_discount(100, 0) == 100]

# 2. Implement function
def calculate_discount(amount, rate):
    # [Copilot suggests full implementation]
    ...
```

---

#### Workflow 2: Pattern Replication

```python
# You have this:
def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

# Type: def get_user_by_email
# Copilot suggests:
def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()

# Copilot learned the pattern!
```

---

#### Workflow 3: Comment-Driven Development

```python
# Calculate fibonacci number recursively with memoization
# [Copilot suggests full implementation]

# Parse ISO 8601 date string to datetime object
# [Copilot suggests full implementation]

# Validate email address using regex
# [Copilot suggests full implementation]
```

---

### Copilot Best Practices

**1. Clear Comments**
```python
# Bad: "do the thing"
# Good: "Parse CSV file and return list of dictionaries with headers as keys"
```

**2. Function Names**
```python
# Descriptive names trigger better suggestions
def validate_email_format(email: str) -> bool:
    # Copilot knows what to do!
```

**3. Type Hints**
```python
def process_users(users: List[Dict[str, Any]]) -> List[str]:
    # Type hints guide Copilot's suggestions
```

**4. Review Suggestions**
```python
# Always review before accepting!
# Check for:
# - Correctness
# - Security (SQL injection, XSS)
# - Performance
# - Edge cases
```

---

## 💻 Cursor IDE: Deep Dive

### What Makes Cursor Special

**Strengths**:
- ✅ Full IDE with AI integrated
- ✅ Codebase-wide understanding
- ✅ Chat + inline suggestions
- ✅ Cmd+K for quick edits
- ✅ Great for greenfield projects

**Use Cases**:
1. **New projects**: "Build a FastAPI app with auth"
2. **Rapid prototyping**: Quick iterations
3. **Learning**: Explore new frameworks
4. **Refactoring**: Large-scale changes

---

### Cursor Workflows

#### Cmd+K: Quick Edits

```
Select code → Cmd+K → "Add error handling"
[Cursor modifies in place]

Select function → Cmd+K → "Add type hints and docstring"
[Cursor updates function]
```

**Fast for**: Small, localized changes

---

#### Chat: Complex Tasks

```
Chat: "Add authentication middleware to this FastAPI app.
       Use JWT tokens, store in cookies, refresh token flow."

[Cursor generates:
 - middleware.py
 - auth_service.py
 - tests
 - updates main.py]
```

**Fast for**: Multi-file changes

---

#### Codebase Chat: Understanding

```
Chat: "How does user authentication work in this codebase?"

[Cursor analyzes files, explains flow]

Chat: "Where should I add a new admin role?"

[Cursor suggests files to modify]
```

**Fast for**: Onboarding to codebases

---

## 🎯 Choosing the Right Tool

### Decision Matrix

| Task | Best Tool | Why |
|------|-----------|-----|
| Writing new function | Copilot | Fast inline suggestions |
| Architecture decision | Claude Code | Deep reasoning |
| Quick edit | Cursor Cmd+K | In-place modification |
| Multi-file refactor | Claude Code | Context-aware changes |
| Autocomplete boilerplate | Copilot | Fastest completions |
| Learning codebase | Cursor Chat | Codebase understanding |
| Complex debugging | Claude Code | Systematic analysis |
| Rapid prototyping | Cursor | Full IDE + AI |

---

### Combined Workflow

**Example**: Building a feature

1. **Architecture** (Claude Code): "Design user notification system"
2. **Implementation** (Copilot): Write code with inline suggestions
3. **Refactoring** (Cursor): Large-scale code improvements
4. **Debugging** (Claude Code): Complex bug investigation
5. **Testing** (Copilot): Generate test cases

**Use multiple tools for their strengths!**

---

## 🏗️ Real-World Project Workflow

### Project: Building a REST API

**Phase 1: Setup** (Cursor)
```
"Create FastAPI project structure:
- src/api (routes, models, schemas)
- src/core (config, dependencies)
- src/db (database, migrations)
- tests/
- Docker setup
- CI/CD with GitHub Actions"
```

**Phase 2: Core Features** (Copilot + Claude Code)
- Use Copilot for CRUD endpoints (fast!)
- Use Claude Code for complex business logic

**Phase 3: Testing** (Copilot)
- Write test structures
- Let Copilot fill in test cases

**Phase 4: Optimization** (Claude Code)
- Profile code
- Ask Claude for optimization strategies

**Phase 5: Documentation** (Claude Code)
- Generate API docs
- Write README

---

## ⚡ Productivity Patterns

### Pattern 1: Rubber Ducking with AI

**When stuck**:
```
"I'm trying to [goal].
I've tried [attempt 1], but [problem].
Then I tried [attempt 2], but [problem].

Here's my current code: [paste]

What am I missing?"
```

Often clarifies your thinking!

---

### Pattern 2: Progressive Refinement

**Don't aim for perfect first try**:
```
Round 1: "Generate basic user registration"
[Review, test]

Round 2: "Add email validation and password strength check"
[Review, test]

Round 3: "Add rate limiting and CAPTCHA"
[Review, test]
```

Build incrementally with AI.

---

### Pattern 3: Style Learning

**Show AI your style**:
```
"I have these existing functions: [paste 2-3 examples]

Following this SAME style, generate: [new function]"
```

AI matches your conventions!

---

## 🚫 Common Pitfalls

### Pitfall 1: Autopilot Mode

**Problem**: Accepting all suggestions without review.

**Solution**: Always review, especially for:
- Security (SQL injection, XSS)
- Performance (n+1 queries, memory leaks)
- Business logic (edge cases)

---

### Pitfall 2: Context Overload

**Problem**: Asking AI about entire codebase.

**Solution**: Provide focused context:
```
Bad: "Fix my app"

Good: "This authentication module has a bug: [specific issue]
      Relevant files: [paste 2-3 files]
      Error: [specific error]"
```

---

### Pitfall 3: Not Testing

**Problem**: Trusting AI-generated code works.

**Solution**: Test everything!
```
1. Unit tests for functions
2. Integration tests for workflows
3. Manual testing for UX
4. Security testing
```

---

## 📊 Measuring Productivity

### Metrics to Track

**Before AI Tools**:
- Time to complete feature
- Bug rate
- Test coverage

**With AI Tools**:
- Same metrics
- Time saved on boilerplate
- Time to onboard to new codebase

**Typical Gains**:
- 30-50% faster on boilerplate
- 20-30% faster on overall development
- 50%+ faster writing tests
- 70%+ faster on documentation

---

## 💡 Advanced Techniques

### Technique 1: Chain of Thought

```
"Let's solve this step by step:
1. First, identify the data structures we need
2. Then, design the algorithm
3. Then, implement with error handling
4. Finally, add tests"
```

Structured approach yields better code.

---

### Technique 2: Specification First

```
# Write specification
"""
Function: process_payment
Input: amount (float), payment_method (str), user_id (int)
Output: Transaction object
Errors: InvalidPayment, InsufficientFunds
Side effects: Updates database, sends email
"""

# Then ask AI to implement
```

---

### Technique 3: Test First

```
# 1. Write tests
def test_payment_processing():
    result = process_payment(100.0, "credit_card", user_id=1)
    assert result.status == "success"
    assert result.amount == 100.0

# 2. Ask AI to implement function that passes tests
```

---

## ✅ Daily Workflow Checklist

### Morning
- [ ] Review yesterday's AI-generated code
- [ ] Plan tasks suitable for AI assistance
- [ ] Identify blockers AI might help with

### During Development
- [ ] Use AI for boilerplate (Copilot)
- [ ] Consult AI for architecture (Claude Code)
- [ ] Review all AI suggestions critically
- [ ] Test frequently

### Before Committing
- [ ] Review all AI-generated code
- [ ] Run full test suite
- [ ] Check for security issues
- [ ] Verify documentation accuracy

---

## 🎓 Key Takeaways

1. **Different tools, different strengths**: Use the right tool for the task
2. **AI amplifies, doesn't replace**: You're still the developer
3. **Review is non-negotiable**: Never trust blindly
4. **Iterate freely**: First generation rarely perfect
5. **Combine tools**: Use multiple AI assistants
6. **Measure impact**: Track productivity gains
7. **Keep learning**: Tools evolve rapidly

---

## 🚀 Your Personal Workflow

### Design Your Workflow

**Morning Planning**:
- [What you'll do]

**Coding**:
- [When you use Copilot]
- [When you use Claude Code]
- [When you use Cursor]

**Review**:
- [Your review process]

**Testing**:
- [Your testing approach]

### Continuous Improvement

**Weekly Review**:
- What worked well?
- What didn't?
- How to improve?

**Monthly Assessment**:
- Productivity gains
- Quality metrics
- New techniques learned

---

## 📚 Further Reading

- GitHub Copilot Documentation
- Cursor IDE Docs
- Anthropic Claude for Code
- "AI-Assisted Programming" research papers
- r/ClaudeAI, r/github_copilot communities

---

## 🎉 Phase 1 Complete!

**Congratulations!** You've completed **Phase 1: AI-Native Development**!

You now know:
- ✅ AI development patterns (Module 1)
- ✅ Prompt engineering (Module 2)
- ✅ Code generation (Module 3)
- ✅ AI-assisted debugging (Module 4)
- ✅ AI coding tools (Module 5)

**Next**: Phase 2 - Generative AI Fundamentals (Modules 6-10)

You'll learn how LLMs actually work under the hood!

---

**Remember**: AI tools are powerful, but you're the architect. Use them wisely, review critically, and keep learning.

**Let's build! 🥋🧠⚡**

---

_Last updated: 2025-11-21_
_Version: 1.0_
