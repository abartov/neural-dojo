# Module 40 Deliverable: AI Safety Toolkit

**A comprehensive toolkit for implementing AI safety measures including prompt injection detection, content moderation, fairness analysis, and runtime guardrails.**

## Features

- **Prompt Injection Detection**: Detect jailbreaks, direct overrides, roleplay attacks, encoding bypasses
- **Content Moderation**: Multi-category classification (hate speech, violence, self-harm, PII, etc.)
- **Fairness Analysis**: Demographic parity, equalized odds, disparate impact metrics
- **Runtime Guardrails**: Configurable input/output filtering with audit logging
- **Safety Audits**: Complete pipeline combining all safety checks

## Quick Start

```bash
# Prompt injection detection
python deliverable_ai_safety_toolkit.py demo1

# Content moderation
python deliverable_ai_safety_toolkit.py demo2

# Fairness analysis for ML models
python deliverable_ai_safety_toolkit.py demo3

# Runtime guardrails
python deliverable_ai_safety_toolkit.py demo4

# Complete safety audit
python deliverable_ai_safety_toolkit.py demo5
```

## Core Components

### 1. Prompt Injection Detector

Detects various injection attack types:

| Attack Type | Description | Severity |
|-------------|-------------|----------|
| Direct Override | "Ignore previous instructions..." | HIGH |
| Roleplay Jailbreak | "You are now an AI without restrictions..." | HIGH |
| DAN Jailbreak | "Do Anything Now" and similar | CRITICAL |
| System Prompt Extraction | "Reveal your system prompt..." | MEDIUM |
| Encoding Bypass | Base64/hex encoding attacks | MEDIUM |
| Hypothetical Framing | "Hypothetically speaking..." | LOW |

### 2. Content Moderator

Multi-category content classification:

- **Hate Speech**: Discriminatory language, slurs
- **Harassment**: Personal attacks, bullying
- **Violence**: Threats, violent content
- **Sexual**: Explicit/adult content
- **Self-Harm**: Suicide, self-injury references
- **Dangerous**: Illegal activities, weapons
- **PII**: Personally identifiable information

### 3. Fairness Analyzer

ML fairness metrics:

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Demographic Parity | Equal positive rates across groups | Diff < 0.1 |
| Equalized Odds (TPR) | Equal true positive rates | Diff < 0.1 |
| Equalized Odds (FPR) | Equal false positive rates | Diff < 0.1 |
| Disparate Impact | Ratio of positive rates | Ratio > 0.8 |

### 4. Guardrails System

Configurable runtime protection:

```python
from deliverable_ai_safety_toolkit import (
    GuardrailsSystem,
    create_topic_restriction_guard,
    create_pii_redaction_guard,
    create_length_limit_guard
)

guardrails = GuardrailsSystem()
guardrails.add_input_guard(create_topic_restriction_guard(["weapons", "drugs"]))
guardrails.add_output_guard(create_pii_redaction_guard())

action, result, _ = guardrails.check_input("user message")
```

## Safety Audit Report

The complete audit combines all checks:

```
┌────────────────────────────────────────────────────┐
│              SAFETY AUDIT PIPELINE                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  User Input                                        │
│       │                                            │
│       ▼                                            │
│  ┌─────────────────┐                              │
│  │ 1. Injection    │ → Detect prompt attacks      │
│  │    Detection    │                              │
│  └─────────────────┘                              │
│       │                                            │
│       ▼                                            │
│  ┌─────────────────┐                              │
│  │ 2. Content      │ → Classify harmful content   │
│  │    Moderation   │                              │
│  └─────────────────┘                              │
│       │                                            │
│       ▼                                            │
│  ┌─────────────────┐                              │
│  │ 3. Input        │ → Apply topic restrictions   │
│  │    Guards       │                              │
│  └─────────────────┘                              │
│       │                                            │
│       ▼                                            │
│     [LLM Processing]                               │
│       │                                            │
│       ▼                                            │
│  ┌─────────────────┐                              │
│  │ 4. Output       │ → Redact PII, limit length   │
│  │    Guards       │                              │
│  └─────────────────┘                              │
│       │                                            │
│       ▼                                            │
│  Risk Score + Recommendations                      │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Risk Scoring

Overall risk score (0-1) combines:

- Injection detection (0-0.4)
- Content moderation (0-0.3)
- Guardrail triggers (0-0.2)

**Score Interpretation:**
- < 0.2: Low risk, safe to proceed
- 0.2-0.5: Medium risk, flag for review
- > 0.5: High risk, block or escalate

## Extending the Toolkit

### Custom Guards

```python
from deliverable_ai_safety_toolkit import Guard, GuardResult, GuardAction

def my_custom_check(content: str) -> GuardResult:
    if "forbidden_word" in content.lower():
        return GuardResult(
            guard_name="custom",
            action=GuardAction.BLOCK,
            message="Forbidden content detected"
        )
    return GuardResult(guard_name="custom", action=GuardAction.ALLOW)

custom_guard = Guard(
    name="custom_guard",
    description="My custom safety check",
    check_fn=my_custom_check,
    priority=10
)
```

### Custom Fairness Metrics

```python
from deliverable_ai_safety_toolkit import FairnessAnalyzer

analyzer = FairnessAnalyzer()

# Change thresholds
analyzer.THRESHOLDS[FairnessMetric.DISPARATE_IMPACT] = 0.9  # Stricter
```

## Output Files

Results are saved to `.ai_safety_toolkit/`:

- `safety_audits.json`: Complete audit logs
- `incidents.json`: Flagged incidents

## Key Concepts

### The Alignment Problem

AI optimizes what we specify, not what we want. Safety is about:
1. Preventing misuse (bad actors)
2. Preventing accidents (unintended harm)
3. Ensuring alignment (correct objectives)

### Defense in Depth

No single safety measure is sufficient:
- Training-time safety (RLHF, Constitutional AI)
- Input filtering (injection detection)
- Output filtering (content moderation)
- Monitoring (audit logs)

### Fairness Trade-offs

Different fairness metrics can be mutually exclusive. Choose based on:
- Legal requirements (disparate impact for lending)
- Domain needs (equalized odds for medical diagnosis)
- Stakeholder values (demographic parity for visibility)

## Production Considerations

This toolkit demonstrates concepts. For production:

1. **Use trained classifiers** - Perspective API, OpenAI Moderation
2. **Add human review** - Edge cases need human judgment
3. **Implement rate limiting** - Prevent abuse
4. **Log everything** - Audit trails for compliance
5. **Regular updates** - New attacks emerge constantly

---

**Time**: ~8 hours | **Lines**: 1400+ | **Author**: Neural Dojo
