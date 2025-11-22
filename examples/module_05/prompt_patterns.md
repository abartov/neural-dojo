# Prompt Patterns for AI Coding Assistants

Reusable prompt templates for common development tasks.

---

## 🎯 Code Generation

### Pattern 1: Spec-First Development

```
Create a [function/class/module] that:

**Purpose**: [What it does]

**Input**:
- [parameter 1]: [type] - [description]
- [parameter 2]: [type] - [description]

**Output**: [type] - [description]

**Behavior**:
- [specific behavior 1]
- [specific behavior 2]

**Error Handling**:
- [error case 1] → raise/return [error]
- [error case 2] → raise/return [error]

**Example Usage**:
```language
[show how it should be used]
```

**Constraints**:
- [performance requirements]
- [compatibility requirements]
```

**Example**:
```
Create a function that validates email addresses.

**Purpose**: Validate email format according to RFC 5322 (simplified)

**Input**:
- email: str - Email address to validate

**Output**: bool - True if valid, False if invalid

**Behavior**:
- Check for @ symbol
- Check for domain part
- Check for local part
- Allow common TLDs (.com, .org, .net, etc.)

**Error Handling**:
- Empty string → return False
- None → return False

**Example Usage**:
```python
is_valid = validate_email("user@example.com")  # True
is_valid = validate_email("invalid.email")     # False
```

**Constraints**:
- No external dependencies (use stdlib only)
- Must run in O(n) time
```

---

### Pattern 2: Example-Driven Generation

```
I have this [function/class]:

```language
[paste example code]
```

Following the SAME pattern and style, create a [similar function/class] that [does X].

Keep:
- Same naming conventions
- Same error handling approach
- Same documentation style
- Same return types
```

---

## 🐛 Debugging

### Pattern 1: Systematic Debug

```
I have a bug in my code. Help me debug systematically.

**Error Message**:
[full error with stack trace]

**Code**:
```language
[paste the problematic code]
```

**Context**:
- Language/Framework: [e.g., Python 3.11, FastAPI]
- What I expected: [expected behavior]
- What actually happened: [actual behavior]
- When it happens: [always/intermittent/specific conditions]

**What I've tried**:
1. [attempt 1] → [result]
2. [attempt 2] → [result]

**Environment**:
- OS: [Windows/Mac/Linux]
- [Other relevant env info]

Please provide:
1. Root cause analysis
2. Step-by-step fix
3. Explanation of why it happened
4. How to prevent in the future
```

---

### Pattern 2: Rubber Duck Debug

```
I'm trying to [goal] but [problem].

Here's what I know:
- [observation 1]
- [observation 2]

Here's what I've tried:
- [attempt 1]: [result]
- [attempt 2]: [result]

Here's my code:
```language
[code]
```

What am I missing?
```

---

## 🔍 Code Review

### Pattern 1: Security Review

```
Review this code for security vulnerabilities:

```language
[paste code]
```

Check for:
- SQL injection
- XSS (cross-site scripting)
- Authentication/authorization issues
- Sensitive data exposure (passwords, keys, tokens)
- Input validation
- Rate limiting
- CSRF protection

Provide:
- List of vulnerabilities found
- Severity (critical/high/medium/low)
- Specific line numbers
- How to fix each issue
```

---

### Pattern 2: Performance Review

```
Review this code for performance issues:

```language
[paste code]
```

Check for:
- Time complexity (is this O(n²) when it could be O(n)?)
- Database queries (N+1 problems?)
- Memory usage (loading everything into memory?)
- Unnecessary loops or operations
- Missing caching opportunities

Provide:
- Bottlenecks identified
- Time/space complexity analysis
- Specific optimizations with code examples
```

---

## 🧪 Testing

### Pattern 1: Generate Tests

```
Generate comprehensive unit tests for this code:

```language
[paste function/class]
```

Include tests for:
- Happy path (normal usage)
- Edge cases (empty input, max values, etc.)
- Error cases (invalid input)
- Boundary conditions

Use [pytest/unittest/jest/etc.] framework.
Include descriptive test names and docstrings.
```

---

### Pattern 2: Test-Driven Development

```
I want to implement [feature] using TDD.

**Requirements**:
- [requirement 1]
- [requirement 2]

Please:
1. Write test cases first (covering happy path, edge cases, errors)
2. Then show me the implementation that passes all tests

Use [testing framework].
```

---

## 📝 Documentation

### Pattern 1: Generate API Docs

```
Generate API documentation for this endpoint:

```language
[paste endpoint code]
```

Include:
- Endpoint URL and HTTP method
- Request parameters (path, query, body)
- Request body schema (if POST/PUT)
- Response schema
- Example request/response
- Possible error responses
- Authentication requirements

Format: [OpenAPI/Markdown/JSDoc]
```

---

### Pattern 2: Code Explanation

```
Explain this code as if to a [junior developer/non-technical stakeholder]:

```language
[paste code]
```

Include:
- What it does (high level)
- How it works (step by step)
- Why certain decisions were made
- What to watch out for when modifying it
```

---

## 🔧 Refactoring

### Pattern 1: Improve Readability

```
Refactor this code for better readability:

```language
[paste code]
```

Improve:
- Variable naming
- Function decomposition (extract smaller functions)
- Comments (add where helpful, remove obvious ones)
- Code organization

Keep functionality EXACTLY the same.
```

---

### Pattern 2: Apply Pattern

```
Refactor this code to use [design pattern/principle]:

**Current code**:
```language
[paste code]
```

**Pattern to apply**: [e.g., Strategy Pattern, Dependency Injection, SOLID principles]

**Why**: [reason for refactoring]

Show:
- Refactored code
- What changed and why
- Benefits of the new approach
```

---

## 🏗️ Architecture

### Pattern 1: System Design

```
Design the architecture for [system description].

**Requirements**:
- [functional requirement 1]
- [functional requirement 2]

**Non-functional requirements**:
- Scale: [users/requests]
- Performance: [latency/throughput]
- Availability: [uptime SLA]

**Constraints**:
- [budget/tech stack/timeline]

Provide:
- High-level architecture diagram
- Component breakdown
- Data flow
- Technology choices (with reasoning)
- Scaling strategy
```

---

### Pattern 2: Database Schema Design

```
Design a database schema for [domain/feature].

**Entities**:
- [entity 1]: [description and key attributes]
- [entity 2]: [description and key attributes]

**Relationships**:
- [entity A] → [entity B]: [relationship type]

**Queries** we need to support:
- [query 1]
- [query 2]

**Constraints**:
- Database: [PostgreSQL/MySQL/MongoDB/etc.]
- Scale: [expected data volume]

Provide:
- ERD or schema diagram
- Table definitions (DDL)
- Indexes needed
- Normalization level and reasoning
```

---

## 🎓 Learning

### Pattern 1: Explain Concept

```
Explain [concept/technology] as if to someone who knows [baseline knowledge].

Include:
- What it is (simple definition)
- Why it exists (problem it solves)
- How it works (key mechanisms)
- When to use it (use cases)
- Example (concrete code/scenario)
- Common pitfalls

Keep it [concise/detailed] and [beginner-friendly/advanced].
```

---

### Pattern 2: Compare Approaches

```
Compare [approach A] vs [approach B] for [use case].

For each, explain:
- How it works
- Pros and cons
- Performance characteristics
- When to use it
- Code example

Then recommend which to use for my specific case: [describe your case]
```

---

## 🚀 Optimization

### Pattern 1: Performance Optimization

```
This code is slow. Help me optimize it.

**Current code**:
```language
[paste code]
```

**Problem**: [what's slow]

**Benchmark**: Currently takes [time] to process [data size]

**Target**: Should take [target time]

**Constraints**:
- [memory limits]
- [compatibility requirements]

Provide:
- Profiling analysis (where the time is spent)
- Optimized code
- Before/after complexity (Big O)
- Expected speedup
```

---

### Pattern 2: Database Query Optimization

```
Optimize this database query:

```sql
[paste query]
```

**Context**:
- Database: [PostgreSQL/MySQL/etc.]
- Table sizes: [table1: X rows, table2: Y rows]
- Current execution time: [time]
- Existing indexes: [list indexes]

**Problem**: [what's slow - full table scan, N+1, etc.]

Provide:
- Optimized query
- Index recommendations
- EXPLAIN output interpretation
- Expected performance improvement
```

---

## 💡 Tips for Better Prompts

1. **Be Specific**: Vague prompts → vague answers
   - ❌ "Fix this code"
   - ✅ "Fix the null pointer exception on line 42 when user is not logged in"

2. **Provide Context**: AI needs to know your constraints
   - Language/framework version
   - Performance requirements
   - Compatibility needs

3. **Show Examples**: One example is worth 1000 words
   - Show your code style
   - Show expected output
   - Show similar working code

4. **Structure Your Prompts**: Use sections
   - **Problem**, **Context**, **Requirements**, **Constraints**

5. **Iterate**: First answer not perfect? Refine!
   - "That works, but can you optimize for memory?"
   - "Good, now add error handling"

---

## 🎯 Quick Reference

**Need Code?** → Use Spec-First or Example-Driven pattern

**Bug?** → Use Systematic Debug pattern

**Review Code?** → Use Security or Performance Review pattern

**Tests?** → Use Generate Tests or TDD pattern

**Docs?** → Use Generate API Docs pattern

**Refactor?** → Use Improve Readability or Apply Pattern

**Architecture?** → Use System Design pattern

**Learning?** → Use Explain Concept or Compare Approaches

---

**Remember**: These are templates. Adapt them to your specific needs!
