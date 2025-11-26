# Module 21 Deliverable: Production Agent Toolkit

**Enterprise-grade agent infrastructure with guardrails, observability, and fault tolerance.**

## Features

- **Input/Output Guardrails**: Prompt injection detection, PII filtering, content moderation
- **Rate Limiting**: Token bucket algorithm with per-user limits
- **Budget Control**: Per-request, per-user, and global cost limits
- **Circuit Breaker**: Automatic failure detection and recovery
- **Graceful Degradation**: Multiple fallback levels for continuous availability
- **Structured Logging**: JSON logs with correlation IDs and context
- **Metrics Dashboard**: Latency percentiles, cost tracking, success rates
- **State Persistence**: JSON-based state save/load for continuity

## Quick Start

```bash
# Basic production agent demo
python deliverable_production_agent.py demo1

# Guardrails showcase (prompt injection, PII, content filtering)
python deliverable_production_agent.py demo2

# Observability dashboard with metrics
python deliverable_production_agent.py demo3

# Load test with simulated failures
python deliverable_production_agent.py demo4
```

## Production Patterns Implemented

### 1. Guardrails

**Input Guardrails:**
- Prompt injection detection (pattern matching for manipulation attempts)
- Blocked content filtering (violence, illegal, explicit content)
- Length limits (prevent abuse)
- PII detection (SSN, email, phone - warn but allow)

**Output Guardrails:**
- PII redaction (automatically mask sensitive data in responses)
- Forbidden pattern blocking (system prompts, credentials)
- Length limits (prevent runaway responses)

### 2. Rate Limiting (Token Bucket)

```
┌─────────────────────────────────────────┐
│           Token Bucket                  │
│  ┌──────────────────────────────┐      │
│  │ ● ● ● ● ● ● ● ● ○ ○         │      │
│  │      8/10 tokens             │      │
│  └──────────────────────────────┘      │
│  Refill: 1 token/second                │
│  Burst: 10 tokens max                  │
└─────────────────────────────────────────┘
```

### 3. Circuit Breaker States

```
    ┌─────────┐
    │ CLOSED  │◄────── Normal operation
    └────┬────┘        (failures < threshold)
         │
    failure_count >= threshold
         │
         ▼
    ┌─────────┐
    │  OPEN   │◄────── Reject all requests
    └────┬────┘        (fast fail)
         │
    timeout elapsed
         │
         ▼
   ┌──────────┐
   │HALF_OPEN │◄────── Test recovery
   └────┬─────┘        (allow one request)
        │
   success → CLOSED
   failure → OPEN
```

### 4. Graceful Degradation Levels

| Level | Trigger | Response Strategy |
|-------|---------|-------------------|
| 0 | Normal | Full LLM response |
| 1 | LLM slow/failed | Cached/template response |
| 2 | Rate limited | Rate limit message |
| 3 | Budget exceeded | Budget warning |
| 4 | Circuit open | Service unavailable message |

## Metrics & Observability

The toolkit tracks comprehensive metrics:

**Request Metrics:**
- `requests_total{status}` - Success/error counts
- `guardrails_triggered{type}` - Guardrail activations
- `circuit_breaker_state` - Current state

**Latency Metrics:**
- Mean, median, P95, P99, max latency
- Per-user latency breakdown

**Cost Metrics:**
- Total cost across all requests
- Per-user cost breakdown
- Per-model cost tracking

**Example Output:**
```
📈 METRICS DASHBOARD
==================================================
   Requests:
      requests_total:status=success: 27
      requests_total:status=error: 3

   Latency:
      Mean: 104.3ms
      Median: 105.2ms
      P95: 105.3ms
      Max: 105.3ms

   Costs:
      Total: $0.0037
      alice: $0.0013
      bob: $0.0012
```

## Configuration Options

Customize the agent behavior through parameters:

```python
agent = ProductionAgent(
    agent_id="my_agent",
    rate_limit=10,           # Requests per second
    rate_burst=20,           # Burst capacity
    budget_per_request=0.10, # Max cost per request
    budget_per_user=1.00,    # Max daily user budget
    budget_global=100.0,     # Global daily budget
    failure_threshold=5,     # Circuit breaker threshold
    recovery_timeout=30.0    # Circuit recovery time
)
```

## State Persistence

The agent automatically saves state to `.production_agent/`:

```
.production_agent/
├── state.json          # Agent state (circuit, budgets)
├── metrics.json        # Metrics data
└── logs/               # Structured log files
```

Load previous state on startup:
```python
agent = ProductionAgent.load_state("my_agent")
```

## Safety Features

The guardrails catch common attack vectors:

| Attack Type | Detection Method | Action |
|-------------|------------------|--------|
| Prompt injection | Pattern matching | Block request |
| PII exposure | Regex patterns | Redact in output |
| Content manipulation | Keyword filtering | Block request |
| Denial of service | Rate limiting | Throttle user |
| Cost attacks | Budget limits | Reject request |

## Integration Example

```python
from deliverable_production_agent import ProductionAgent

# Initialize with production settings
agent = ProductionAgent(
    agent_id="customer_support",
    rate_limit=5,
    budget_per_user=0.50
)

# Process request with full safety
result = agent.process_request(
    user_id="user_123",
    message="How do I reset my password?"
)

if result.success:
    print(result.response)
else:
    print(f"Error: {result.error}")
    print(f"Guardrails: {result.guardrails_triggered}")

# Get observability data
print(agent.get_metrics_summary())
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Agent                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Input     │  │   Rate      │  │      Budget         │ │
│  │ Guardrails  │─▶│  Limiter    │─▶│    Controller       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Circuit Breaker + LLM                   │   │
│  │    (with retry logic and graceful degradation)       │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Output    │  │   Metrics   │  │      Logger         │ │
│  │ Guardrails  │  │  Collector  │  │   (structured)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Always enable guardrails** - Never deploy without input validation
2. **Set conservative budgets** - Start low, increase based on usage
3. **Monitor metrics** - Set up alerts for anomalies
4. **Test failure modes** - Use demo4 to understand degradation
5. **Log everything** - Structured logs enable debugging and auditing
6. **Plan for scale** - Token bucket scales better than fixed windows

**Time**: ~4 hours | **Lines**: 600+ | **Author**: Neural Dojo
