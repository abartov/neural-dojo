# Module 13 Deliverable: RAG vs Fine-tuning Decision Engine

**Make data-driven decisions about AI customization strategies.**

## Features

- Multi-factor decision analysis (knowledge, citations, style, latency, data)
- Detailed cost projections (monthly, yearly, 3-year)
- Risk assessment with mitigation strategies
- Implementation roadmap generation
- JSON export for documentation
- Historical analysis tracking

## Quick Start

```bash
# Run all demos
python deliverable_decision_engine.py

# Specific demos
python deliverable_decision_engine.py demo1    # Customer support analysis
python deliverable_decision_engine.py demo2    # Legal assistant analysis
python deliverable_decision_engine.py demo3    # Cost comparison scenarios
python deliverable_decision_engine.py demo4    # Interactive analysis

# Full interactive mode
python deliverable_decision_engine.py analyze

# Help
python deliverable_decision_engine.py help
```

## The Core Framework

### The Fundamental Question

**Ask yourself: Is this about KNOWLEDGE or BEHAVIOR?**

| What You Need | Approach | Why |
|---------------|----------|-----|
| Facts that change | RAG | Dynamic knowledge injection |
| Specific writing style | Fine-tuning | Encode behavior in weights |
| Both | Hybrid | Combine RAG + LoRA |

### Decision Factors

1. **Knowledge Update Frequency**
   - Realtime/Daily/Weekly → RAG
   - Monthly/Yearly/Static → Either (consider other factors)

2. **Citation Requirements**
   - Required/Important → RAG (natural attribution)
   - Not needed → Either

3. **Style Requirements**
   - Critical/Important → Fine-tuning (consistent behavior)
   - Minimal → RAG is fine

4. **Latency Tolerance**
   - Strict (<100ms) → Fine-tuning (no retrieval overhead)
   - Flexible (>500ms) → RAG is fine

5. **Training Data Availability**
   - <50 examples → RAG only
   - 50-200 examples → LoRA
   - >200 examples → Full fine-tuning possible

## Cost Model (2025 Pricing)

```
GPT-4o Base:
  Input:  $2.50/1M tokens
  Output: $10.00/1M tokens

GPT-4o Fine-tuned:
  Input:  $3.75/1M tokens  (1.5x)
  Output: $15.00/1M tokens (1.5x)
  Training: $25.00/1M tokens

Vector Database:
  Free tier: $0/month (limited)
  Starter:   $70/month
  Standard:  $150/month

LoRA Training:
  Base: $50 + $0.10/example
  Max:  $200 (capped)
```

## Example Output

```
══════════════════════════════════════════════════════════════════════════════
  RAG vs FINE-TUNING DECISION ENGINE - ANALYSIS REPORT
══════════════════════════════════════════════════════════════════════════════

  PROJECT: Legal Research Assistant
  Research case law and draft legal documents with citations

  Parameters:
    - Monthly queries: 50,000
    - Training examples: 1,000
    - Knowledge updates: Weekly updates
    - Citation need: Legal/compliance requirement
    - Style need: Must match exact style
    - Latency tolerance: < 2s acceptable

──────────────────────────────────────────────────────────────────────────────
  RECOMMENDATION: 🔀 HYBRID
  Confidence: 68%
──────────────────────────────────────────────────────────────────────────────

  REASONING:
    1. Knowledge changes weekly - RAG provides dynamic updates
    2. Citations required/important - RAG enables natural source attribution
    3. Style requirements are significant - fine-tuning ensures consistency
    4. Sufficient training data (1000) enables effective fine-tuning

  COST PROJECTIONS:
  Approach            Monthly        Year 1        Year 3     One-time
  ───────────────────────────────────────────────────────────────────
  RAG                  $1,295       $15,540       $46,620           $0
  Fine-tuning          $2,718       $32,629       $97,863         $125
  Hybrid               $1,295       $15,695       $46,775         $155

  RISK ASSESSMENT: Medium
  Risk Factors:
    ⚠️  More complex architecture to maintain
  Mitigations:
    ✓ Use well-documented, modular design

  IMPLEMENTATION ROADMAP:
    Phase 1: RAG Infrastructure (2-3 weeks)
    Phase 2: Style Data Collection (1 week)
    Phase 3: LoRA Fine-tuning (1 week)
    Phase 4: Integration (1 week)
    Phase 5: End-to-End Testing (1-2 weeks)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DecisionEngine                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  UseCase                    Analysis                            │
│  ┌──────────────────┐       ┌──────────────────────────────┐   │
│  │ name             │  ───▶ │ recommended_approach         │   │
│  │ knowledge_freq   │       │ confidence                   │   │
│  │ citation_need    │       │ reasoning[]                  │   │
│  │ style_need       │       │ cost_projections{}           │   │
│  │ latency_tolerance│       │ risk_assessment              │   │
│  │ training_examples│       │ implementation_roadmap[]     │   │
│  │ monthly_queries  │       │ alternatives[]               │   │
│  └──────────────────┘       └──────────────────────────────┘   │
│                                                                 │
│  Methods:                                                       │
│  • calculate_scores() - Multi-factor decision scoring          │
│  • calculate_costs() - Detailed cost projections               │
│  • assess_risks() - Risk identification and mitigation         │
│  • generate_roadmap() - Implementation planning                │
│  • analyze() - Complete analysis pipeline                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Persistence

Analyses are saved to `.decision_engine/analyses.json`:

```json
{
  "use_case": {
    "name": "Legal Research Assistant",
    "knowledge_frequency": "weekly",
    "citation_need": "required",
    ...
  },
  "recommended_approach": "Hybrid",
  "confidence": 0.68,
  "reasoning": [...],
  "cost_projections": {...},
  "timestamp": "2025-11-24T14:30:00"
}
```

## Key Insights

### When RAG Wins
- Knowledge changes frequently (weekly or faster)
- Citations are required for compliance
- Limited training data (<100 examples)
- Large document corpus to search
- Cost-sensitive at high volume

### When Fine-tuning Wins
- Specific style/behavior is critical
- Knowledge is static
- Strict latency requirements (<100ms)
- Abundant high-quality training data
- Security requires no external data access

### When Hybrid Wins
- Need both dynamic knowledge AND specific behavior
- Building production-grade systems
- Want best quality at reasonable cost
- Complex enterprise use cases

## Extending the Engine

### Add Custom Pricing

```python
PRICING_2025["custom_model"] = {
    "input_per_million": 1.00,
    "output_per_million": 5.00,
}
```

### Add Custom Factors

```python
class SecurityRequirement(Enum):
    HIGH = ("high", "No external data access", -3)  # Penalizes RAG
    MEDIUM = ("medium", "Encrypted connections OK", 0)
    LOW = ("low", "Standard security", 0)
```

## Files

```
examples/module_13/
├── deliverable_decision_engine.py  # Main tool (600+ lines)
├── DELIVERABLE_README.md           # This file
├── 01_decision_framework.py        # Decision framework demo
├── 02_cost_analysis.py             # Cost analysis demo
├── README.md                       # Module overview
├── requirements.txt                # Dependencies (minimal)
└── .gitignore                      # Excludes .decision_engine/
```

## Portfolio Value

This deliverable demonstrates:
- **Data-driven decision making** for AI architecture
- **Cost modeling** with real pricing data
- **Risk assessment** frameworks
- **Production planning** with implementation roadmaps
- **Clean architecture** (dataclasses, enums, separation of concerns)

---

**Time**: ~4-5 hours | **Lines**: 600+ | **Author**: Neural Dojo
