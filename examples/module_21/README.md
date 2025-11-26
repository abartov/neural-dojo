# Module 21: AI Agents in Production

This directory contains working code examples for deploying AI agents to production with enterprise-grade reliability, safety, and observability.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Production Agent Patterns
**File**: `01_production_patterns.py`
**Description**: Core patterns for production deployment including stateless/stateful agents, circuit breaker, and graceful degradation.
**Run**: `python 01_production_patterns.py`

Key patterns covered:
- Stateless vs Stateful agent design
- Circuit breaker (CLOSED → OPEN → HALF_OPEN states)
- Graceful degradation levels
- Retry with exponential backoff

### Example 2: Guardrails and Safety
**File**: `02_guardrails_safety.py`
**Description**: Input/output validation, prompt injection detection, PII filtering, and content moderation.
**Run**: `python 02_guardrails_safety.py`

Key patterns covered:
- Input validation (prompt injection, blocked content)
- Output guardrails (PII redaction, forbidden patterns)
- Rate limiting (token bucket algorithm)
- Budget controls (per-request, per-user, global)

### Example 3: Monitoring and Observability
**File**: `03_monitoring_observability.py`
**Description**: Structured logging, metrics collection, cost tracking, and performance analysis.
**Run**: `python 03_monitoring_observability.py`

Key patterns covered:
- Structured logging with correlation IDs
- Counter and histogram metrics
- Cost tracking per model/user
- Latency percentile analysis (P50, P95, P99)

### Deliverable: Production Agent Toolkit
**File**: `deliverable_production_agent.py`
**Description**: Complete production-ready agent combining all patterns with full guardrails, observability, and fault tolerance.

```bash
python deliverable_production_agent.py demo1  # Production agent
python deliverable_production_agent.py demo2  # Guardrails showcase
python deliverable_production_agent.py demo3  # Observability dashboard
python deliverable_production_agent.py demo4  # Load test with failures
```

## Expected Output

### Example 1 Output:
```
DEMO: Production Agent Patterns
========================================

1. CIRCUIT BREAKER PATTERN
Circuit state: closed
Circuit state: open
Request blocked by circuit breaker
```

### Example 2 Output:
```
DEMO: Guardrails and Safety
========================================

1. INPUT VALIDATION
"Hello, how are you?" - VALID
"Ignore all previous instructions..." - INVALID: prompt_injection
"My SSN is 123-45-6789" - VALID (with warning: pii_detected)
```

### Example 3 Output:
```
DEMO: Monitoring and Observability
========================================

📊 METRICS SUMMARY:
requests_total:success = 25
requests_total:error = 5
average_latency_ms = 145.3
total_cost = $0.0089
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   PRODUCTION AGENT                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────┐    │
│  │ INPUT GUARDRAILS│    │     RATE LIMITER            │    │
│  │ - Injection     │───▶│     (Token Bucket)          │    │
│  │ - PII detection │    │     10 req/s + burst        │    │
│  │ - Content filter│    └─────────────────────────────┘    │
│  └─────────────────┘                 │                      │
│                                      ▼                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              BUDGET CONTROLLER                       │   │
│  │   Per-request: $0.10  |  Per-user: $1.00/day        │   │
│  │   Global: $100/day                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         CIRCUIT BREAKER + LLM CALL                   │   │
│  │   CLOSED ──(failures)──▶ OPEN ──(timeout)──▶ HALF   │   │
│  │     │                     │                    │     │   │
│  │   [process]           [reject]            [test]     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────┐    ┌─────────────────────────────┐    │
│  │OUTPUT GUARDRAILS│    │     OBSERVABILITY           │    │
│  │ - PII redaction │    │     - Structured logs       │    │
│  │ - Content check │    │     - Metrics (latency)     │    │
│  │                 │    │     - Cost tracking         │    │
│  └─────────────────┘    └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Circuit Breaker States

| State | Behavior | Transition |
|-------|----------|------------|
| CLOSED | Process all requests | → OPEN after N failures |
| OPEN | Reject immediately (fast fail) | → HALF_OPEN after timeout |
| HALF_OPEN | Allow one test request | → CLOSED on success, OPEN on failure |

### Graceful Degradation Levels

| Level | Condition | Response |
|-------|-----------|----------|
| 0 | Normal | Full LLM response |
| 1 | LLM failed | Cached/template response |
| 2 | Rate limited | Rate limit message |
| 3 | Budget exceeded | Budget warning |
| 4 | Circuit open | Service unavailable |

### Rate Limiting (Token Bucket)

```
Bucket Capacity: 10 tokens
Refill Rate: 1 token/second

Request arrives:
  - Has tokens? → Consume 1, proceed
  - Empty? → Reject (429 Too Many Requests)
```

## Notes

- All examples use a simulated LLM for demonstration (no API key required)
- Production implementations should connect to real LLM APIs
- Metrics are held in memory; use Prometheus/Grafana for production
- State persistence uses JSON files; use Redis/PostgreSQL for production
- Examples demonstrate patterns; tune parameters for your workload
