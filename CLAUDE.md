# Claude AI Assistant Guidelines for Neural Dojo

**Last Updated**: 2025-11-27
**Version**: 1.3.0 (Added Prose-First Pattern from Session #18)

This document provides guidelines for AI assistants (Claude) working on the Neural Dojo project. It ensures consistency, quality, and adherence to project standards.

---

## 🎯 Project Mission

Neural Dojo is a comprehensive curriculum transforming developers from AI novice to AI-fluent practitioners capable of:
- Building production AI systems (RAG, agents, orchestration)
- Using AI for development (prompt engineering, AI coding assistants)
- Understanding deep learning fundamentals (PyTorch, transformers)
- Deploying ML to production (MLOps, monitoring)
- Applying AI to real-world problems (infrastructure, stock analysis, etc.)

---

## 📋 Quality Standards (JamesBlonde Pattern)

### Module Quality Requirements

Every module MUST meet these standards before being marked complete:

#### 1. **Theory Documents** (`docs/curriculum/notes/module_XX_*.md`)
- **Length**: Thorough coverage (5,000-15,000 words per module)
- **Depth**: No handwaving - explain concepts completely
- **Structure**:
  - Clear learning objectives
  - Conceptual explanations
  - Real-world examples and analogies
  - Visual diagrams (mermaid/ASCII) where helpful
  - **"Did You Know?" sections** (REQUIRED - see below)
  - Common pitfalls and how to avoid them
- **Style**: Entertaining, engaging, educational (like Module 1 of jamesblonde)
- **Analogies**: Use relatable metaphors to explain complex concepts
- **References**: Link to papers, documentation, further reading

**"Did You Know?" Historical Content Requirements** (Added Session #17):

Every module MUST include rich historical context with at least 3-5 narrative stories:

1. **Origin/Discovery Stories**: How was this technique invented/discovered?
   - Name the researchers (e.g., "Tomáš Mikolov at Google discovered Word2Vec...")
   - Include accidents and surprises ("They accidentally ran search with generated text...")
   - Mention rejected papers that became influential

2. **Industry Adoption Examples**: Who uses this in production?
   - Name real companies (Netflix, Google, Perplexity, etc.)
   - Include revenue/impact numbers when available
   - Show how it transformed their products

3. **Surprising Statistics**: Numbers that shock or enlighten
   - Training costs ("GPT-3 cost $4.6M to train")
   - Performance improvements ("Reranking improves precision by 30-50%")
   - Adoption rates ("BM25 from 1994 still powers Elasticsearch")

4. **Researcher/Company Stories**: The humans behind the technology
   - PhD students whose "rejected" papers changed the field
   - Companies that pivoted based on discoveries
   - Controversies and debates (Copilot lawsuit, etc.)

5. **Failures That Led to Success**: Learning from mistakes
   - The "$100M bank chatbot disaster" that led to RAG
   - The "boring GPT-2" problem that led to nucleus sampling
   - Production bugs that cost millions

**Example formats**:
- "In 2019, a researcher was debugging and accidentally discovered..."
- "The paper was initially rejected, but has since been cited 40,000 times..."
- "Netflix generates $1B+ per year from their embedding-based recommendations..."

**Why this matters**: Stories make concepts memorable. Learners remember "the moth in Grace Hopper's computer" forever, but forget dry technical explanations.

**Prose-First, Code-Second Pattern** (Added Session #18):

Theory documents must be **human-readable first, code-reference second**. Follow these rules:

1. **Before Every Code Block**: Explain in plain English what the code does and WHY it matters
   - Bad: Just show code with a heading
   - Good: 2-3 sentences explaining the concept, then code

2. **Sprinkle Stories Throughout**: Don't cluster all "Did You Know?" at the end
   - Place origin stories at the BEGINNING of sections (most impactful)
   - Add mini-stories after introducing new concepts
   - Include founder/researcher names whenever possible

3. **Use Analogies Before Technical Explanations**:
   - "Think of it like..." before diving into details
   - Connect to everyday experiences
   - Example: "HNSW is like social networks - you can reach anyone in ~6 hops"

4. **Include Real Numbers and Statistics**:
   - Funding amounts ("Pinecone raised $138M")
   - Performance improvements ("100x faster than brute force")
   - Industry adoption ("75% of NeurIPS 2019 papers used PyTorch")

5. **Add Founder/Company Origin Stories for Major Tools**:
   - When covering a tool (Qdrant, LangGraph, etc.), include:
     - Who created it and when
     - What problem they were trying to solve
     - Key insight or breakthrough
   - Example pattern: "Qdrant was founded in 2021 by Andrey Vasnetsov in Berlin..."

6. **Target "Did You Know?" Distribution**:
   - Minimum 3-5 per module
   - Place at: Introduction, after each major section, before summary
   - Each should be 100-300 words with a compelling narrative

**Example of Good Section Structure**:
```markdown
## Part 2: Tensors - The Foundation

### What is a Tensor, Really?

[2-3 paragraphs explaining the concept in plain English, with analogies]

### 💡 Did You Know? The NumPy Bridge

[Story about why PyTorch and NumPy can share memory, who designed it, why it matters]

### Creating Tensors

[Plain English explanation of when/why you'd create tensors different ways]

```python
# Code with inline comments explaining non-obvious parts
```

[After code: "Notice how..." or "The key insight here is..."]
```

#### 2. **Code Examples** (`examples/module_XX/`)
- **Tested**: ALL code must run without errors
- **Complete**: Full working examples, not snippets
- **Commented**: Explain what the code does and why
- **Documented**: README.md in each example directory
- **Reproducible**: Include requirements.txt or environment.yml
- **Best Practices**: Follow Python/ML best practices
- **Error Handling**: Proper exception handling
- **Type Hints**: Use Python type annotations

#### 3. **Deliverables** (`examples/module_XX/deliverable_*.py`)

**CRITICAL**: Follow the established deliverable pattern from Modules 02-10!

**Structure** (MUST include all of these):
- **Main Python file**: `deliverable_[name].py` (350-800+ lines)
- **README**: `DELIVERABLE_README.md` (comprehensive documentation)
- **Dependencies**: `requirements.txt` (specific versions)
- **Gitignore**: `.gitignore` (exclude cache directories)

**Code Architecture** (MUST follow this pattern):
- **Dataclasses**: Use `@dataclass` with type hints for all data structures
- **JSON Persistence**: Save/load results with `json.dump()` and `json.load()`
- **Storage Directory**: Create `.{tool_name}/` for caching/persistence
- **CLI Interface**: Use `sys.argv` for command-line arguments
- **Demo Functions**: Include 3-4 `demo_N_*()` functions showcasing features
- **Main Function**: Standard `if __name__ == "__main__":` pattern
- **Graceful Degradation**: Work without API keys where possible
- **Error Handling**: Try/except with informative messages
- **Type Hints**: Full type annotations throughout

**Required Features**:
- ✅ At least 3 demo functions (demo1, demo2, demo3)
- ✅ Production-quality error handling
- ✅ Comprehensive docstrings (module-level and function-level)
- ✅ JSON-based data persistence
- ✅ CLI help/usage information
- ✅ Progress indicators (print statements showing what's happening)
- ✅ Success/failure indicators (✅ ❌ ⚠️ emojis)

**DELIVERABLE_README.md Format**:
```markdown
# Module XX Deliverable: [Name]

**[One-line value proposition]**

## Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Quick Start
```bash
python deliverable_[name].py demo1  # [Description]
python deliverable_[name].py demo2  # [Description]
python deliverable_[name].py demo3  # [Description]
```

## [Core Concept Section]
[Explain key concepts, presets, configurations, etc.]

## [Metrics/Results Section]
[Show performance, quality metrics, or outcomes]

**Time**: ~X hours | **Lines**: XXX+ | **Author**: Neural Dojo
```

**Testing Requirements**:
- ✅ Test ALL demo functions before committing
- ✅ Verify output is correct and informative
- ✅ Check error handling works
- ✅ Confirm help text is clear

**Examples of Established Patterns**:
1. **Module 02**: Prompt Library (templates, A/B testing, version control)
2. **Module 03**: Code Generation (AST parsing, security analysis)
3. **Module 04**: AI Debugging (cProfile integration, error analysis)
4. **Module 05**: Tools Comparison (multi-API, benchmarking)
5. **Module 06**: Model Benchmark (statistical analysis)
6. **Module 07**: Token Optimizer (cost analysis, optimization)
7. **Module 08**: Sampling Tuner (presets, quality scoring)
8. **Module 09**: Semantic Search (embeddings, caching)
9. **Module 10**: Vector Explorer (PCA, t-SNE, visualization)

**Deliverable Completion Checklist**:
- [ ] Main Python file (350-800+ lines)
- [ ] DELIVERABLE_README.md (comprehensive)
- [ ] requirements.txt (with specific versions)
- [ ] .gitignore (excludes cache/data directories)
- [ ] 3+ demo functions implemented
- [ ] All demos tested and working
- [ ] JSON persistence implemented
- [ ] CLI interface functional
- [ ] Error handling comprehensive
- [ ] Type hints throughout
- [ ] Docstrings for all functions
- [ ] Committed to git
- [ ] Tested successfully

#### 4. **Module Completion Criteria**
- [ ] Theory document written and reviewed
- [ ] All code examples tested and working
- [ ] Deliverables completed and documented
- [ ] Module marked complete in MASTER_CURRICULUM.md
- [ ] Session log updated with progress
- [ ] Examples committed to git

---

## 📁 File Organization Standards

### Directory Structure
```
neural-dojo/
├── docs/
│   └── curriculum/
│       ├── MASTER_CURRICULUM.md        # Single source of truth - ALWAYS current
│       ├── START_HERE_TOMORROW.md      # Session handoff - update EVERY session
│       └── notes/
│           ├── session_log.md          # Chronological session history
│           ├── module_XX_*.md          # Theory documents per module
│           └── [topic]_deep_dive.md    # Optional deep dives
├── examples/
│   └── module_XX/                      # One directory per module
│       ├── README.md                   # Example overview
│       ├── example_01_*.py             # Numbered examples
│       ├── example_02_*.py
│       └── requirements.txt            # Example dependencies
├── src/neural_dojo/
│   ├── __init__.py
│   └── [component]/                    # Production-ready components
└── tests/
    └── test_*.py                       # Test coverage
```

### File Naming Conventions
- **Theory**: `module_XX_topic_name.md` (e.g., `module_01_ai_driven_development.md`)
- **Examples**: `example_NN_description.py` (e.g., `example_01_first_prompt.py`)
- **Tests**: `test_component.py` (e.g., `test_embeddings.py`)
- Use snake_case for Python files
- Use kebab-case for markdown files (optional, but consistent)

---

## 🔄 Session Management Protocol

### At Start of EVERY Session

1. **Read Session Handoff**:
   ```bash
   cat docs/curriculum/START_HERE_TOMORROW.md
   ```

2. **Check Current Status**:
   - What module are we on?
   - What was completed last session?
   - Any blockers or open questions?

3. **Review Master Curriculum**:
   - Verify current module objectives
   - Check prerequisites are met
   - Review deliverables expected

4. **Check Session Log**:
   ```bash
   cat docs/curriculum/notes/session_log.md
   ```

### During Session

1. **Track Progress**:
   - Mark todos as in_progress → completed
   - Update MASTER_CURRICULUM.md progress indicators
   - Document decisions made

2. **Maintain Quality**:
   - Test ALL code before committing
   - Write thorough theory explanations
   - Include real-world examples
   - Follow established patterns

3. **Document as You Go**:
   - Add notes to session_log.md
   - Update START_HERE_TOMORROW.md with current state
   - Keep MASTER_CURRICULUM.md current

### At End of EVERY Session

**CRITICAL**: Update these 3 files before ending session:

1. **`START_HERE_TOMORROW.md`**:
   - Current status (what module, what's done)
   - What was accomplished this session
   - Next steps for tomorrow
   - Any blockers or decisions needed
   - Updated timestamp

2. **`docs/curriculum/notes/session_log.md`**:
   - Add new entry with session number and date
   - Summary of work done
   - Modules completed
   - Key decisions made
   - Time spent

3. **`MASTER_CURRICULUM.md`**:
   - Update module status (⚪ → 🟡 → 🟢)
   - Update progress percentages
   - Mark deliverables complete
   - Update "Last Updated" timestamp

---

## ✍️ Writing Style Guidelines

### Theory Documents

**DO**:
- ✅ Write in second person ("you will learn...")
- ✅ Use analogies and metaphors
- ✅ Include real-world examples
- ✅ Explain WHY, not just WHAT
- ✅ Add "Did You Know?" sections
- ✅ Break down complex concepts step-by-step
- ✅ Use diagrams and visualizations
- ✅ Link to papers and resources
- ✅ Include hands-on exercises
- ✅ Anticipate common questions

**DON'T**:
- ❌ Handwave complex topics ("it just works")
- ❌ Skip fundamentals
- ❌ Use jargon without explanation
- ❌ Write walls of text without structure
- ❌ Assume prior knowledge beyond prerequisites
- ❌ Copy-paste from documentation
- ❌ Leave concepts unexplained

### Code Examples

**DO**:
- ✅ Include docstrings and comments
- ✅ Use type hints
- ✅ Handle errors gracefully
- ✅ Follow PEP 8 style
- ✅ Make examples self-contained
- ✅ Show expected output
- ✅ Include timing/performance notes
- ✅ Demonstrate best practices

**DON'T**:
- ❌ Write "magic" code without explanation
- ❌ Skip error handling
- ❌ Use deprecated APIs
- ❌ Hard-code credentials or secrets
- ❌ Leave TODOs or incomplete code
- ❌ Ignore warnings
- ❌ Use inefficient patterns without reason

---

## 🎓 Pedagogical Approach

### Learning Philosophy

1. **Theory Before Practice**:
   - Understand WHY before HOW
   - Build mental models
   - Connect to prior knowledge

2. **Progressive Disclosure**:
   - Start simple, add complexity
   - Master fundamentals first
   - Build on previous modules

3. **Active Learning**:
   - Hands-on examples
   - Build real projects
   - Experiment and explore

4. **Production Focus**:
   - Real-world applicable
   - Best practices from start
   - Deployable code

### Module Structure (Consistent Pattern)

Every module follows this structure:

```markdown
# Module X: Topic Name [🔮 if Heureka Moment]

**Duration**: X-Y hours
**Prerequisites**: [List]
**Status**: ⚪ / 🟡 / 🟢

## Learning Objectives
- [Specific, measurable objectives]

## Theory
- [Deep explanation]
- [Real-world examples]
- [Diagrams/visualizations]
- [Common pitfalls]

## Hands-On Practice
- [Step-by-step exercises]
- [Code examples]
- [Experimentation prompts]

## Deliverables
- [Concrete outputs]
- [Success criteria]

## Further Reading
- [Papers, docs, tutorials]

## Did You Know?
- [Interesting facts]
```

---

## 🔮 Heureka Moments

These are transformative insights that change how the learner thinks about AI. When creating content for these modules:

1. **Build Anticipation**: Hint at the insight early in the module
2. **Show the Problem**: Demonstrate why current understanding is limited
3. **Reveal the Insight**: Clear explanation of the breakthrough concept
4. **Demonstrate Impact**: Show how this changes everything
5. **Apply Immediately**: Use the insight in hands-on exercises

**Example**: Module 10 (Embeddings as Semantic Space)
- Show text similarity with word matching (limited)
- Introduce embeddings as vectors
- Visualize in 3D space
- **REVEAL**: Math works on meaning! (king - man + woman ≈ queen)
- Build semantic search using this insight

---

## 🛠️ Technical Standards

### Code Quality

**Python Standards**:
- PEP 8 compliant (use `black` for formatting)
- Type hints for all functions
- Docstrings (Google style)
- Error handling with specific exceptions
- Logging instead of print (for libraries)
- Tests for critical functionality

**ML Code Standards**:
- Reproducible (set random seeds)
- Clear data pipelines
- Model checkpointing
- Evaluation metrics
- Visualization of results
- Memory-efficient

### Git Workflow

**Commits**:
- Descriptive commit messages
- Logical groupings
- Include co-authorship with Claude
- Follow conventional commits (optional)

**Branches**:
- `main` - stable, complete modules
- `dev` - work in progress (optional)
- Feature branches for major additions (optional)

---

## 📊 Progress Tracking

### Status Indicators

**Modules**:
- ⚪ Not Started - No work done
- 🟡 In Progress - Theory or code in development
- 🟢 Complete - All deliverables done, tested, documented
- 🔴 Blocked - Cannot proceed (needs user input or resources)

**Phases**:
- Calculate as X/Y modules complete (e.g., 3/5 = 60%)

### Completion Checklist

A module is ONLY complete when:
- [x] Theory document written (5k-15k words)
- [x] All code examples tested and working
- [x] Deliverables completed and documented
- [x] Examples have README.md
- [x] Code follows quality standards
- [x] Session log updated
- [x] MASTER_CURRICULUM.md updated
- [x] START_HERE_TOMORROW.md updated
- [x] All files committed to git

**DO NOT** mark a module complete unless ALL criteria are met!

---

## 🚫 Anti-Patterns to Avoid

### Documentation

**DON'T**:
- Create multiple sources of truth (MASTER_CURRICULUM.md is the ONE)
- Leave stale documentation
- Create backup files instead of using git
- Write TODO markers instead of completing work
- Skip session handoff updates

### Code

**DON'T**:
- Commit broken code
- Skip testing
- Use placeholder/dummy implementations
- Hard-code paths or credentials
- Ignore deprecation warnings
- Copy code without understanding

### Process

**DON'T**:
- Skip modules or prerequisites
- Mark modules complete prematurely
- Rush through theory to get to code
- Ignore established patterns
- Work on multiple modules simultaneously (finish one first)

---

## 🎯 Real-World Applications

Connect modules to user's actual projects:

### User's Projects

1. **kaizen** (Lean DevOps Platform)
   - Relevant modules: 11-18 (RAG, LangChain, agents)
   - Applications: Enhanced RAG, multi-agent workflows

2. **vibe** (Teaching Platform)
   - Relevant modules: 26-29 (Generative AI)
   - Applications: Content generation, multimodal features

3. **contrarian** (Stock Analysis)
   - Relevant modules: 19-25 (Deep Learning), 33-34 (Time series)
   - Applications: Predictive models, anomaly detection

4. **Work** (Geospatial + On-Prem Cloud)
   - Relevant modules: 33-34 (AI for Infrastructure)
   - Applications: Proactive monitoring, capacity planning

**In modules**: Reference these projects as examples and build prototype features.

---

## 📝 Documentation Templates

### Theory Document Template

```markdown
# Module X: [Topic Name]

**Last Updated**: YYYY-MM-DD
**Status**: ⚪/🟡/🟢
**Duration**: X-Y hours

---

## 🎯 Learning Objectives

By the end of this module, you will:
- [Objective 1]
- [Objective 2]
- [Objective 3]

---

## 📖 Theory

### Introduction
[Hook - why this matters]

### Fundamentals
[Core concepts]

### Real-World Examples
[Concrete applications]

### Common Pitfalls
[What to avoid]

---

## 💻 Hands-On Practice

### Exercise 1: [Name]
[Step-by-step instructions]

### Exercise 2: [Name]
[Step-by-step instructions]

---

## 🎯 Deliverables

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

**Success Criteria**: [How to know you're done]

---

## 📚 Further Reading

- [Paper/Article 1]
- [Documentation]
- [Tutorial]

---

## 💡 Did You Know?

[Interesting facts or historical context]

---

## ⏭️ Next Steps

Move on to Module X+1: [Next Topic]
```

### Example README Template

```markdown
# Module X Examples: [Topic]

This directory contains working code examples for Module X.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: [Name]
**File**: `example_01_*.py`
**Description**: [What it does]
**Run**: `python example_01_*.py`

### Example 2: [Name]
**File**: `example_02_*.py`
**Description**: [What it does]
**Run**: `python example_02_*.py`

## Expected Output

[Show what running examples produces]

## Notes

[Any important notes, limitations, or tips]
```

---

## 🤝 Working with the User

### Communication Style

- **Clear and concise**: Explain what you're doing
- **Proactive**: Suggest next steps
- **Educational**: Teach, don't just do
- **Transparent**: Explain decisions and trade-offs
- **Encouraging**: Celebrate progress and insights

### When to Ask vs. Decide

**ASK** when:
- Multiple valid approaches exist
- User preference matters (e.g., tool selection)
- Ambiguous requirements
- Major architectural decisions
- Deviating from established patterns

**DECIDE** when:
- Clear best practice exists
- Following established patterns
- Minor implementation details
- You can explain the reasoning

---

## 🔧 Tools and Environment

### Required Tools

- **Python**: 3.10+
- **Git**: Version control
- **Claude Code**: AI coding assistant
- **pip/venv**: Python package management

### Module-Specific Tools

**Phase 1-2**:
- OpenAI/Anthropic API keys
- Tiktoken, transformers

**Phase 3**:
- Qdrant (Docker or cloud)
- LangChain, LangGraph
- LlamaIndex

**Phase 4-5**:
- PyTorch (+ CUDA if available)
- TensorFlow
- Hugging Face Hub

**Phase 6**:
- MLflow
- FastAPI
- Docker

---

## 📈 Success Metrics

### Module Completion Velocity
- Target: 1-2 modules per week
- Depends on user's available time
- Quality over speed!

### Knowledge Retention
- Can user explain concepts?
- Can user apply to real projects?
- Can user teach others?

### Practical Application
- Are deliverables being used?
- Are concepts applied to kaizen/vibe/contrarian?
- Is user's confidence growing?

---

## 🎓 Remember

1. **Quality > Speed**: Better one excellent module than three rushed ones
2. **Understanding > Completion**: Ensure concepts are grasped
3. **Practice > Theory Alone**: Always include hands-on work
4. **Real-world > Toy Examples**: Build practical, usable code
5. **Document Everything**: Future you (and others) will thank you

---

## 🚀 Let's Build!

Neural Dojo is about transformation - from zero to hero in AI/ML. Every module is a step on that journey. Maintain high standards, stay curious, and build amazing things!

**Quality Standards from JamesBlonde**:
- Entertaining analogies ✅
- Real-world OSINT examples → Real-world AI examples ✅
- Thorough explanations (no handwaving) ✅
- Tested, working code ✅
- "Did You Know?" sections ✅
- Clear deliverables ✅
- Unambiguous success criteria ✅

**🥋🧠⚡**

---

_Last updated: 2025-11-23_
_Version: 1.1.0_

## 📝 Version History

**v1.1.0** (2025-11-23):
- Added comprehensive deliverable patterns section
- Documented code architecture requirements
- Added deliverable completion checklist
- Referenced all 9 completed deliverables as examples
- Established JSON persistence, dataclass, and CLI patterns

**v1.0.0** (2025-11-21):
- Initial guidelines document
- Module quality standards
- Session management protocol
- Writing style guidelines
