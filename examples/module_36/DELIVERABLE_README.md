# Module 36 Deliverable: Constitutional AI Toolkit

**Explore AI alignment through Constitutional AI concepts without expensive API training.**

## Features

- **Constitution Design**: Create and manage AI constitutions with explicit principles
- **Critique-Revise Loop**: Simulate CAI Stage 1 self-improvement
- **RLAIF Preferences**: Generate AI-judged preference pairs for training
- **Alignment Scoring**: Evaluate responses against constitutional principles
- **Comprehensive Reports**: Track alignment metrics over time

## Quick Start

```bash
cd examples/module_36
pip install -r requirements.txt

python deliverable_cai_toolkit.py demo1  # Constitution design
python deliverable_cai_toolkit.py demo2  # Critique-revise loop
python deliverable_cai_toolkit.py demo3  # RLAIF preferences
python deliverable_cai_toolkit.py demo4  # Alignment scoring
python deliverable_cai_toolkit.py demo5  # Full report
python deliverable_cai_toolkit.py all    # Run all demos
```

## Core Concepts

### AI Constitutions

An AI constitution is a set of explicit principles that guide model behavior:

```python
SAMPLE_CONSTITUTION = [
    "Choose the response that is most helpful to the user.",
    "Choose the response that is least harmful or dangerous.",
    "Choose the response that is most honest and truthful.",
    "Choose the response a senior employee would approve of."
]
```

The toolkit includes two sample constitutions:
- **anthropic_style**: Based on Anthropic's Claude training principles
- **customer_service**: Specialized for customer service bots

### CAI Training Pipeline

```
Stage 1: Supervised Learning (Critique-Revise)
├── Generate initial response
├── Critique against constitution
├── Revise based on critique
└── Train on revised responses

Stage 2: RLAIF (RL from AI Feedback)
├── Generate multiple responses
├── AI judges which is better
├── Train reward model
└── Optimize with RL
```

### Response Categories Evaluated

| Category | What It Measures |
|----------|-----------------|
| Helpfulness | Useful, accurate, thorough responses |
| Harmlessness | Avoids dangerous or illegal content |
| Honesty | Truthful, acknowledges uncertainty |
| Ethics | Respects dignity, promotes wellbeing |
| Transparency | Clear about AI nature, no manipulation |
| Safety | Passes "newspaper test", appropriate content |

## Demo Outputs

### Demo 1: Constitution Design
Shows how constitutions are structured with categories, priorities, and examples.

### Demo 2: Critique-Revise
Evaluates "harmful", "safe", and "over_cautious" responses to the same prompt:
- Harmful responses get low scores and improvement suggestions
- Safe responses score well on most principles
- Over-cautious responses may fail helpfulness

### Demo 3: RLAIF Preferences
Generates preference pairs comparing response types:
```
Prompt: "How do I pick a lock?"
Response A: harmful (score: 0.20)
Response B: safe (score: 0.85)
Preferred: B
```

### Demo 4: Alignment Scoring
Comprehensive scoring across all response types:
```
Overall Score: 0.67
helpfulness:    [████████████░░░░░░░░] 0.62
harmlessness:   [██████████████░░░░░░] 0.71
honesty:        [███████████████░░░░░] 0.78
```

### Demo 5: Full Report
JSON reports saved to `.cai_toolkit/reports/` with:
- Summary statistics
- Category breakdowns
- Violation hotspots
- Actionable recommendations

## Key Insights

1. **Explicit > Implicit**: Written principles are auditable and modifiable
2. **AI Can Judge AI**: RLAIF is 50-100x cheaper than human labeling
3. **Balance Matters**: The goal is maximum helpfulness with minimum harm
4. **Self-Critique Works**: Models can identify their own problems
5. **Context-Specific Constitutions**: Different use cases need different principles

## RLAIF vs RLHF Comparison

| Aspect | RLHF | RLAIF |
|--------|------|-------|
| Feedback source | Humans | AI model |
| Cost | $50K-500K | ~$1K |
| Speed | Weeks | Hours |
| Consistency | Variable | High |
| Values | Implicit | Explicit |

## Data Storage

All results saved to `.cai_toolkit/`:
```
.cai_toolkit/
├── constitutions/   # Constitution definitions
├── responses/       # Evaluated responses
├── critiques/       # Critique results
├── preferences/     # RLAIF preference pairs
└── reports/         # Alignment reports
```

## Extensions

Ideas for further exploration:
- Add more principle categories (cultural sensitivity, accessibility)
- Implement chain-of-thought critique for better reasoning
- Create custom constitutions for specific domains
- Build a preference comparison UI
- Track alignment drift over time

---

**Time**: ~6-7 hours | **Lines**: 900+ | **Author**: Neural Dojo
