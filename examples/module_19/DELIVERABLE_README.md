# Module 19 Deliverable: AI Framework Selector Toolkit

**A comprehensive toolkit for selecting and evaluating AI frameworks based on project requirements.**

## Features

- **Interactive Questionnaire**: Answer questions to get personalized recommendations
- **Scoring Engine**: Weighted scoring based on use case, experience, timeline
- **Framework Database**: 7 frameworks with detailed profiles
- **Comparison Matrix**: Side-by-side feature comparison
- **Export Reports**: Generate markdown reports for team review

## Quick Start

```bash
# Interactive recommendation (best starting point)
python deliverable_framework_selector.py recommend

# Compare all frameworks
python deliverable_framework_selector.py compare

# Quick analysis with sample profiles
python deliverable_framework_selector.py analyze

# Full demonstration
python deliverable_framework_selector.py demo
```

## Frameworks Covered

| Framework | Category | Best For |
|-----------|----------|----------|
| **LangChain** | Orchestration | Flexible LLM apps |
| **LangGraph** | Orchestration | Stateful agents |
| **LlamaIndex** | Data Framework | RAG, indexing |
| **CrewAI** | Multi-Agent | Role-based teams |
| **AutoGen** | Research | Conversational agents |
| **Haystack** | Data Framework | Search applications |
| **Semantic Kernel** | Enterprise | Azure integration |

## Scoring Algorithm

The selector scores frameworks based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Use Case Match | 30% | Primary and secondary use cases |
| Experience Fit | 20% | Team skill level vs learning curve |
| Production Need | 20% | Production readiness requirement |
| Timeline Fit | 15% | Speed to implement |
| Community | 15% | Support and ecosystem |

## Questionnaire Topics

1. **Primary Use Case**: RAG, Agents, Multi-Agent, Chatbot, etc.
2. **Secondary Use Cases**: Additional features needed
3. **Team Size**: Solo to large team
4. **Experience Level**: Beginner to advanced
5. **Production Required**: Yes/No
6. **Budget Constraints**: Free/open-source preference
7. **Timeline**: ASAP to months
8. **Existing Stack**: Current technologies

## Output Example

```
#1 LlamaIndex (Score: 85%)
===========================
Description: Data framework for LLM applications

Why this framework:
  + Strong match for rag
  + Easy to learn
  + Excellent for RAG
  + Simple API for indexing

Considerations:
  - Less flexible for agents

Quick Start:
  pip install llama-index
  Website: https://llamaindex.ai
```

## Export Report

The toolkit can export detailed markdown reports:

```bash
python deliverable_framework_selector.py recommend
# Answer questions...
# Report exported to .framework_selector/framework_report.md
```

Report includes:
- Project profile summary
- Top 3 recommendations with scores
- Reasons and concerns for each
- Comparison matrix
- Install commands and links

## Use Case Mapping

| Use Case | Recommended Framework |
|----------|----------------------|
| RAG | LlamaIndex |
| Agents | LangChain + LangGraph |
| Multi-Agent | CrewAI or LangGraph |
| Code Generation | AutoGen |
| Search | Haystack |
| Enterprise/Azure | Semantic Kernel |

## Decision Tree

```
What's your primary use case?
          │
    ┌─────┼─────┐
    │     │     │
   RAG  Agents Multi
    │     │     │
    ▼     ▼     ▼
LlamaIndex  LangChain  CrewAI
              │
         Complex?
              │
         LangGraph
```

## Extending

Add new frameworks by extending the `FRAMEWORKS` dictionary:

```python
FRAMEWORKS["new_framework"] = Framework(
    name="New Framework",
    category=FrameworkCategory.ORCHESTRATION,
    description="Description here",
    strengths=["Strength 1", "Strength 2"],
    weaknesses=["Weakness 1"],
    use_cases=[UseCase.AGENTS],
    learning_curve="medium",
    production_ready=True,
    community_size="medium",
    documentation_quality="good",
    install_command="pip install new-framework",
    website="https://example.com"
)
```

## Storage

Data persists in `.framework_selector/`:

```
.framework_selector/
├── recommendations.json    # Saved recommendations
└── framework_report.md     # Exported reports
```

---

**Time**: ~3 hours | **Lines**: 550+ | **Author**: Neural Dojo
