# Module 21: AI Agents in Production
# Or: How to Ship AI Without Getting Fired

**Last Updated**: 2025-11-26
**Status**: Complete
**Reading Time**: 6-7 hours
**Prerequisites**: Module 20

---

## Learning Objectives

By the end of this module, you will:
- Deploy AI agents to production environments safely
- Implement comprehensive guardrails and safety systems
- Build observability and monitoring for agent behavior
- Control costs and optimize agent efficiency
- Handle failures gracefully with recovery strategies
- Design agents for scalability and reliability

---

## Theory

### Introduction: From Prototype to Production

You've built sophisticated agents with memory, planning, and multi-agent collaboration. But there's a massive gap between a working prototype and a production system. This module bridges that gap.

**The Production Gap**:
```
Prototype Agent                    Production Agent
─────────────────                 ─────────────────
✅ Works in demos                 ✅ Works at scale
❌ No error handling              ✅ Graceful degradation
❌ Unlimited costs                ✅ Budget controls
❌ No monitoring                  ✅ Full observability
❌ Trust all inputs               ✅ Input validation
❌ Single user                    ✅ Multi-tenant
❌ No safety                      ✅ Guardrails everywhere
```

> **Did You Know?** In 2023, a major bank's customer service chatbot was jailbroken by users who convinced it to reveal internal policies, offer unauthorized discounts, and even insult the bank's competitors. The incident cost millions in refunds and reputational damage. This is why guardrails aren't optional—they're essential.

---

## 1. Production Architecture Patterns

### 1.1 The Production Agent Stack

A production-ready agent system has multiple layers:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│  (Rate limiting, Auth, Request validation)                   │
├─────────────────────────────────────────────────────────────┤
│                    Input Guardrails                          │
│  (Content filtering, Prompt injection detection)             │
├─────────────────────────────────────────────────────────────┤
│                    Agent Orchestrator                        │
│  (Planning, Tool selection, State management)                │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Memory     │    Tools     │     LLM      │   Retrieval    │
│   System     │   Registry   │   Router     │    (RAG)       │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                   Output Guardrails                          │
│  (Response validation, PII filtering, Tone check)            │
├─────────────────────────────────────────────────────────────┤
│                   Observability Layer                        │
│  (Logging, Metrics, Tracing, Alerting)                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Synchronous vs Asynchronous Agents

**Synchronous Agents**:
- User waits for response
- Suitable for: Chat, Q&A, simple tasks
- Timeout: 30-60 seconds typically
- Pattern: Request → Process → Response

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Synchronous: user waits
    response = await agent.process(request.message)
    return {"response": response}
```

**Asynchronous Agents**:
- User submits task, polls for result
- Suitable for: Research, document analysis, complex workflows
- Timeout: Minutes to hours
- Pattern: Submit → Job ID → Poll → Result

```python
@app.post("/tasks")
async def submit_task(request: TaskRequest):
    job_id = await task_queue.submit(request)
    return {"job_id": job_id, "status": "queued"}

@app.get("/tasks/{job_id}")
async def get_task_status(job_id: str):
    return await task_queue.get_status(job_id)
```

> **Did You Know?** OpenAI's Assistants API uses an asynchronous pattern internally. When you create a "Run", you're actually submitting a job that processes in the background. This allows for complex, multi-step agent workflows that would timeout in a synchronous model.

### 1.3 Stateless vs Stateful Agents

**Stateless Agents**:
- No memory between requests
- Each request is independent
- Easier to scale (any instance can handle any request)
- Suitable for: Simple Q&A, one-shot tasks

**Stateful Agents**:
- Maintain conversation/task state
- Requires session affinity or external state store
- More complex but enables sophisticated interactions
- Suitable for: Multi-turn conversations, long-running tasks

**Hybrid Approach** (Recommended):
```python
class HybridAgent:
    def __init__(self):
        self.state_store = RedisStateStore()  # External state

    async def process(self, session_id: str, message: str):
        # Load state (stateful behavior)
        state = await self.state_store.get(session_id)

        # Process (stateless core logic)
        response, new_state = await self.agent.process(message, state)

        # Save state (externalized)
        await self.state_store.set(session_id, new_state, ttl=3600)

        return response
```

---

## 2. Guardrails and Safety Systems

### 2.1 The Defense-in-Depth Model

Production agents need multiple layers of defense:

```
Layer 1: Input Validation
    ↓ (passes)
Layer 2: Content Filtering
    ↓ (passes)
Layer 3: Prompt Injection Detection
    ↓ (passes)
Layer 4: Agent Processing
    ↓ (generates)
Layer 5: Output Validation
    ↓ (passes)
Layer 6: PII/Sensitive Data Filtering
    ↓ (passes)
Layer 7: Response to User
```

### 2.2 Input Guardrails

**Content Filtering**:
```python
class ContentFilter:
    """Filter harmful or inappropriate content."""

    BLOCKED_CATEGORIES = [
        "violence", "hate_speech", "sexual_content",
        "self_harm", "illegal_activities"
    ]

    def __init__(self):
        self.classifier = load_content_classifier()

    def check(self, text: str) -> FilterResult:
        scores = self.classifier.predict(text)

        blocked = []
        for category in self.BLOCKED_CATEGORIES:
            if scores.get(category, 0) > 0.8:
                blocked.append(category)

        return FilterResult(
            allowed=len(blocked) == 0,
            blocked_categories=blocked,
            scores=scores
        )
```

**Prompt Injection Detection**:
```python
class PromptInjectionDetector:
    """Detect attempts to manipulate agent behavior."""

    INJECTION_PATTERNS = [
        r"ignore (all )?(previous|prior|above) instructions",
        r"you are now",
        r"pretend (you are|to be)",
        r"act as",
        r"new instructions:",
        r"system prompt:",
        r"forget everything",
        r"disregard .* instructions",
    ]

    def __init__(self):
        self.patterns = [re.compile(p, re.I) for p in self.INJECTION_PATTERNS]
        self.ml_detector = load_injection_classifier()

    def check(self, text: str) -> InjectionResult:
        # Rule-based detection
        for pattern in self.patterns:
            if pattern.search(text):
                return InjectionResult(
                    detected=True,
                    method="pattern",
                    confidence=0.95
                )

        # ML-based detection
        score = self.ml_detector.predict(text)
        if score > 0.8:
            return InjectionResult(
                detected=True,
                method="ml_classifier",
                confidence=score
            )

        return InjectionResult(detected=False, confidence=1 - score)
```

> **Did You Know?** In 2024, researchers demonstrated "indirect prompt injection" where malicious instructions were hidden in web pages that an agent retrieved. When the agent processed the page, it followed the hidden instructions. This is why output from tools also needs validation!

### 2.3 Output Guardrails

**Response Validation**:
```python
class OutputValidator:
    """Validate agent responses before sending to user."""

    def __init__(self, config: ValidatorConfig):
        self.max_length = config.max_length
        self.required_tone = config.tone  # professional, friendly, etc.
        self.blocked_patterns = config.blocked_patterns
        self.pii_detector = PIIDetector()

    def validate(self, response: str) -> ValidationResult:
        issues = []

        # Length check
        if len(response) > self.max_length:
            issues.append("response_too_long")

        # PII check
        pii_found = self.pii_detector.scan(response)
        if pii_found:
            issues.append(f"pii_detected: {pii_found}")

        # Blocked content check
        for pattern in self.blocked_patterns:
            if pattern.search(response):
                issues.append("blocked_content")

        # Tone check (using LLM)
        tone_ok = self.check_tone(response)
        if not tone_ok:
            issues.append("inappropriate_tone")

        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            sanitized=self.sanitize(response) if issues else response
        )

    def sanitize(self, response: str) -> str:
        """Remove or redact problematic content."""
        # Redact PII
        response = self.pii_detector.redact(response)
        # Truncate if needed
        if len(response) > self.max_length:
            response = response[:self.max_length] + "..."
        return response
```

**PII Detection and Filtering**:
```python
class PIIDetector:
    """Detect and redact Personally Identifiable Information."""

    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }

    def scan(self, text: str) -> List[str]:
        """Find PII types present in text."""
        found = []
        for pii_type, pattern in self.PATTERNS.items():
            if re.search(pattern, text):
                found.append(pii_type)
        return found

    def redact(self, text: str) -> str:
        """Replace PII with redaction markers."""
        for pii_type, pattern in self.PATTERNS.items():
            text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", text)
        return text
```

### 2.4 Guardrails Frameworks

Several frameworks help implement guardrails:

**NeMo Guardrails** (NVIDIA):
- Define rails in natural language
- Programmable safety behaviors
- Integration with LangChain

```yaml
# config/rails.co
define user express harmful intent
  user said something harmful

define bot refuse harmful request
  bot refuse to help with harmful request
  bot explain why and offer alternative

define flow harmful_intent
  user express harmful intent
  bot refuse harmful request
```

**Guardrails AI**:
- XML-based specification
- Structured output validation
- Automatic retry on failures

```python
from guardrails import Guard
from guardrails.validators import ValidLength, ToxicLanguage

guard = Guard().use_many(
    ValidLength(min=10, max=500, on_fail="reask"),
    ToxicLanguage(on_fail="filter")
)

response = guard(
    llm_api=llm.generate,
    prompt="Answer the user's question..."
)
```

**Lakera Guard**:
- Prompt injection detection API
- Content moderation
- PII detection

```python
import lakera_guard

result = lakera_guard.check(
    input=user_message,
    checks=["prompt_injection", "pii", "content_moderation"]
)
if result.flagged:
    raise SecurityError(result.reason)
```

---

## 3. Observability and Monitoring

### 3.1 The Three Pillars of Observability

**Logs**: What happened?
**Metrics**: How much/how often?
**Traces**: How did it flow?

```
┌─────────────────────────────────────────────────────────┐
│                    Observability                         │
├─────────────────┬─────────────────┬─────────────────────┤
│      Logs       │     Metrics     │       Traces        │
├─────────────────┼─────────────────┼─────────────────────┤
│ Structured JSON │ Counters/Gauges │ Request spans       │
│ Request IDs     │ Latency histograms│ Tool calls        │
│ Error details   │ Token usage     │ LLM invocations     │
│ Agent decisions │ Cost tracking   │ Memory operations   │
└─────────────────┴─────────────────┴─────────────────────┘
```

### 3.2 Structured Logging

```python
import structlog
from datetime import datetime

logger = structlog.get_logger()

class AgentLogger:
    """Structured logging for agent operations."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = logger.bind(agent_id=agent_id)

    def log_request(self, request_id: str, user_id: str, message: str):
        self.logger.info(
            "agent_request",
            request_id=request_id,
            user_id=user_id,
            message_length=len(message),
            timestamp=datetime.utcnow().isoformat()
        )

    def log_tool_call(self, request_id: str, tool: str, args: dict,
                      result: str, latency_ms: float):
        self.logger.info(
            "tool_call",
            request_id=request_id,
            tool=tool,
            args=args,
            result_length=len(result),
            latency_ms=latency_ms
        )

    def log_llm_call(self, request_id: str, model: str,
                     input_tokens: int, output_tokens: int,
                     latency_ms: float, cost: float):
        self.logger.info(
            "llm_call",
            request_id=request_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost
        )

    def log_error(self, request_id: str, error: Exception, context: dict):
        self.logger.error(
            "agent_error",
            request_id=request_id,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context
        )
```

### 3.3 Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
agent_requests_total = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_id', 'status']
)

tool_calls_total = Counter(
    'tool_calls_total',
    'Total tool invocations',
    ['agent_id', 'tool_name', 'status']
)

# Histograms
request_latency = Histogram(
    'agent_request_latency_seconds',
    'Request latency',
    ['agent_id'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

llm_latency = Histogram(
    'llm_call_latency_seconds',
    'LLM call latency',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Gauges
active_sessions = Gauge(
    'agent_active_sessions',
    'Number of active agent sessions',
    ['agent_id']
)

token_usage = Counter(
    'llm_tokens_total',
    'Total tokens used',
    ['model', 'token_type']  # input/output
)

cost_total = Counter(
    'agent_cost_usd_total',
    'Total cost in USD',
    ['agent_id', 'cost_type']  # llm/tool/storage
)
```

### 3.4 Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

class TracedAgent:
    """Agent with distributed tracing."""

    async def process(self, request_id: str, message: str):
        with tracer.start_as_current_span(
            "agent.process",
            attributes={"request_id": request_id}
        ) as span:
            try:
                # Input validation
                with tracer.start_span("validate_input"):
                    self.validate(message)

                # Planning
                with tracer.start_span("planning") as plan_span:
                    plan = await self.create_plan(message)
                    plan_span.set_attribute("plan_steps", len(plan.steps))

                # Execute steps
                for i, step in enumerate(plan.steps):
                    with tracer.start_span(f"execute_step_{i}") as step_span:
                        step_span.set_attribute("step_type", step.type)

                        if step.type == "tool_call":
                            with tracer.start_span("tool_call") as tool_span:
                                tool_span.set_attribute("tool", step.tool)
                                result = await self.call_tool(step)

                        elif step.type == "llm_call":
                            with tracer.start_span("llm_call") as llm_span:
                                result = await self.call_llm(step)
                                llm_span.set_attribute("tokens", result.tokens)

                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
```

> **Did You Know?** LangSmith by LangChain provides specialized tracing for LLM applications. It captures the full "trace tree" of agent operations, making it easy to debug complex multi-step workflows. Many production teams use it alongside general-purpose tracing like Jaeger or Datadog.

### 3.5 Alerting Strategy

```python
# Alert definitions (Prometheus AlertManager format)
ALERT_RULES = """
groups:
- name: agent_alerts
  rules:

  # High error rate
  - alert: AgentHighErrorRate
    expr: rate(agent_requests_total{status="error"}[5m]) / rate(agent_requests_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Agent {{ $labels.agent_id }} has high error rate"

  # Slow responses
  - alert: AgentSlowResponses
    expr: histogram_quantile(0.95, rate(agent_request_latency_seconds_bucket[5m])) > 10
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Agent {{ $labels.agent_id }} p95 latency > 10s"

  # High cost
  - alert: AgentHighCost
    expr: increase(agent_cost_usd_total[1h]) > 100
    labels:
      severity: warning
    annotations:
      summary: "Agent {{ $labels.agent_id }} spent > $100 in last hour"

  # Guardrail violations
  - alert: GuardrailViolations
    expr: rate(guardrail_violations_total[5m]) > 10
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High rate of guardrail violations"
"""
```

---

## 4. Cost Control and Optimization

### 4.1 Understanding Agent Costs

```
Agent Cost Breakdown
────────────────────
├── LLM Calls (60-80% typically)
│   ├── Input tokens
│   ├── Output tokens
│   └── Model selection
├── Embeddings (10-20%)
│   ├── Document embedding
│   └── Query embedding
├── Vector Storage (5-10%)
│   ├── Storage costs
│   └── Query costs
├── Tool Execution (5-10%)
│   ├── API calls
│   └── Compute
└── Infrastructure (5-10%)
    ├── Hosting
    └── Bandwidth
```

### 4.2 Cost Tracking System

```python
from dataclasses import dataclass, field
from typing import Dict
import json

@dataclass
class CostTracker:
    """Track costs per request and aggregate."""

    # Cost per 1K tokens (example rates)
    LLM_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }

    EMBEDDING_COSTS = {
        "text-embedding-3-small": 0.00002,  # per 1K tokens
        "text-embedding-3-large": 0.00013,
    }

    request_id: str
    costs: Dict[str, float] = field(default_factory=dict)

    def track_llm_call(self, model: str, input_tokens: int, output_tokens: int):
        rates = self.LLM_COSTS.get(model, {"input": 0.01, "output": 0.03})
        cost = (input_tokens / 1000 * rates["input"] +
                output_tokens / 1000 * rates["output"])

        self.costs["llm"] = self.costs.get("llm", 0) + cost
        return cost

    def track_embedding(self, model: str, tokens: int):
        rate = self.EMBEDDING_COSTS.get(model, 0.0001)
        cost = tokens / 1000 * rate

        self.costs["embedding"] = self.costs.get("embedding", 0) + cost
        return cost

    def track_tool(self, tool: str, cost: float):
        self.costs["tools"] = self.costs.get("tools", 0) + cost
        return cost

    @property
    def total(self) -> float:
        return sum(self.costs.values())

    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "costs": self.costs,
            "total": self.total
        }
```

### 4.3 Budget Controls

```python
class BudgetController:
    """Enforce budget limits on agent operations."""

    def __init__(self, config: BudgetConfig):
        self.per_request_limit = config.per_request_limit  # e.g., $0.50
        self.per_user_daily_limit = config.per_user_daily_limit  # e.g., $5.00
        self.global_daily_limit = config.global_daily_limit  # e.g., $1000.00
        self.cost_store = CostStore()

    async def check_budget(self, user_id: str, estimated_cost: float) -> BudgetCheck:
        """Check if operation is within budget."""

        # Check per-request limit
        if estimated_cost > self.per_request_limit:
            return BudgetCheck(
                allowed=False,
                reason=f"Estimated cost ${estimated_cost:.2f} exceeds per-request limit"
            )

        # Check user daily limit
        user_daily = await self.cost_store.get_user_daily(user_id)
        if user_daily + estimated_cost > self.per_user_daily_limit:
            return BudgetCheck(
                allowed=False,
                reason=f"User daily budget exhausted"
            )

        # Check global daily limit
        global_daily = await self.cost_store.get_global_daily()
        if global_daily + estimated_cost > self.global_daily_limit:
            return BudgetCheck(
                allowed=False,
                reason=f"Global daily budget exhausted"
            )

        return BudgetCheck(allowed=True, remaining_user=self.per_user_daily_limit - user_daily)

    async def record_cost(self, user_id: str, cost: float):
        """Record actual cost after operation."""
        await self.cost_store.record(user_id, cost)
```

### 4.4 Cost Optimization Strategies

**1. Model Routing**:
```python
class ModelRouter:
    """Route to appropriate model based on task complexity."""

    def select_model(self, task: str, complexity: str) -> str:
        if complexity == "simple":
            return "claude-3-haiku"  # Fast and cheap
        elif complexity == "medium":
            return "claude-3-sonnet"  # Balanced
        else:
            return "claude-3-opus"  # Best quality

    def estimate_complexity(self, message: str) -> str:
        """Estimate task complexity from message."""
        # Simple heuristics
        if len(message) < 100:
            return "simple"
        if any(word in message.lower() for word in ["analyze", "compare", "evaluate"]):
            return "complex"
        return "medium"
```

**2. Caching**:
```python
class ResponseCache:
    """Cache LLM responses for similar queries."""

    def __init__(self, embedding_model, similarity_threshold: float = 0.95):
        self.cache = {}  # query_hash -> (embedding, response)
        self.embedding_model = embedding_model
        self.threshold = similarity_threshold

    def get(self, query: str) -> Optional[str]:
        query_embedding = self.embedding_model.embed(query)

        for cached_embedding, response in self.cache.values():
            similarity = cosine_similarity(query_embedding, cached_embedding)
            if similarity > self.threshold:
                return response

        return None

    def set(self, query: str, response: str):
        query_embedding = self.embedding_model.embed(query)
        query_hash = hashlib.md5(query.encode()).hexdigest()
        self.cache[query_hash] = (query_embedding, response)
```

**3. Token Optimization**:
```python
class TokenOptimizer:
    """Optimize prompts to reduce token usage."""

    def optimize_system_prompt(self, prompt: str) -> str:
        """Compress system prompt while preserving meaning."""
        # Remove redundant whitespace
        prompt = " ".join(prompt.split())

        # Remove verbose phrases
        verbose_to_concise = {
            "Please note that": "Note:",
            "It is important to": "",
            "Make sure to": "",
            "You should always": "Always",
        }
        for verbose, concise in verbose_to_concise.items():
            prompt = prompt.replace(verbose, concise)

        return prompt

    def truncate_context(self, context: str, max_tokens: int) -> str:
        """Intelligently truncate context to fit budget."""
        tokens = self.tokenizer.encode(context)
        if len(tokens) <= max_tokens:
            return context

        # Keep most relevant parts (beginning and end often most important)
        half = max_tokens // 2
        kept_tokens = tokens[:half] + tokens[-half:]
        return self.tokenizer.decode(kept_tokens)
```

> **Did You Know?** One startup reduced their LLM costs by 70% simply by implementing a semantic cache. Most user queries cluster around common topics, and cache hit rates of 30-40% are typical in customer service applications.

---

## 5. Failure Handling and Recovery

### 5.1 Failure Taxonomy

```
Agent Failures
├── Transient Failures (retry-able)
│   ├── Network timeouts
│   ├── Rate limits (429)
│   ├── Service unavailable (503)
│   └── Temporary API errors
├── Permanent Failures (not retry-able)
│   ├── Invalid input (400)
│   ├── Authentication failure (401)
│   ├── Resource not found (404)
│   └── Validation errors
├── Logical Failures
│   ├── Agent stuck in loop
│   ├── Invalid tool selection
│   ├── Contradictory planning
│   └── Hallucination detected
└── Safety Failures
    ├── Guardrail violation
    ├── Budget exceeded
    ├── Rate limit exceeded
    └── Timeout exceeded
```

### 5.2 Retry Strategy

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    min_wait: float = 1.0
    max_wait: float = 60.0
    exponential_base: float = 2.0

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((TimeoutError, RateLimitError, ServiceUnavailableError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def call_llm_with_retry(prompt: str, model: str) -> str:
    """Call LLM with automatic retry on transient failures."""
    return await llm_client.generate(prompt, model=model)


class SmartRetry:
    """Intelligent retry with fallback strategies."""

    def __init__(self):
        self.primary_model = "claude-3-sonnet"
        self.fallback_model = "claude-3-haiku"

    async def call_with_fallback(self, prompt: str) -> str:
        """Try primary model, fall back to cheaper model if needed."""
        try:
            return await call_llm_with_retry(prompt, self.primary_model)
        except (RateLimitError, BudgetExceededError):
            # Fall back to cheaper model
            logger.warning(f"Falling back to {self.fallback_model}")
            return await call_llm_with_retry(prompt, self.fallback_model)
        except Exception as e:
            # Last resort: cached response or graceful degradation
            cached = self.cache.get(prompt)
            if cached:
                return cached
            raise AgentFailureError(f"All retry strategies exhausted: {e}")
```

### 5.3 Circuit Breaker Pattern

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Prevent cascade failures with circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: timedelta = timedelta(seconds=30),
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0

    def can_execute(self) -> bool:
        """Check if request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if we should try half-open
            if datetime.now() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls

        return False

    def record_success(self):
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                # Recovered!
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0

    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test
            self.state = CircuitState.OPEN
```

### 5.4 Graceful Degradation

```python
class GracefulDegradation:
    """Provide degraded service when full service unavailable."""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.fallback_responses = FallbackResponses()

    async def process(self, message: str) -> AgentResponse:
        """Process with graceful degradation."""
        try:
            # Try full agent
            return await self.agent.process(message)

        except RateLimitError:
            # Degradation level 1: Use cached/templated response
            return self.fallback_responses.get_rate_limited()

        except BudgetExceededError:
            # Degradation level 2: Inform user
            return AgentResponse(
                content="I've reached my usage limit for now. Please try again later.",
                degraded=True,
                reason="budget_exceeded"
            )

        except ServiceUnavailableError:
            # Degradation level 3: Basic functionality only
            return await self.basic_response(message)

        except Exception as e:
            # Degradation level 4: Error response
            logger.error(f"Agent failure: {e}")
            return AgentResponse(
                content="I'm having trouble processing your request. Please try again.",
                degraded=True,
                reason="service_error"
            )

    async def basic_response(self, message: str) -> AgentResponse:
        """Provide basic response without full agent capabilities."""
        # Use simple pattern matching or FAQ lookup
        intent = self.classify_intent(message)
        if intent in self.fallback_responses.intents:
            return self.fallback_responses.get(intent)
        return self.fallback_responses.get_default()
```

---

## 6. Scaling Agents

### 6.1 Horizontal Scaling

```
                    Load Balancer
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ Agent 1 │      │ Agent 2 │      │ Agent 3 │
   └────┬────┘      └────┬────┘      └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                  ┌──────┴──────┐
                  ▼             ▼
           ┌──────────┐  ┌──────────┐
           │  Redis   │  │  Vector  │
           │  State   │  │    DB    │
           └──────────┘  └──────────┘
```

**Key Requirements**:
- Externalized state (Redis, PostgreSQL)
- Stateless agent instances
- Shared vector store
- Session affinity for long conversations (optional)

### 6.2 Queue-Based Processing

```python
from celery import Celery

app = Celery('agent_tasks', broker='redis://localhost:6379/0')

@app.task(bind=True, max_retries=3)
def process_agent_task(self, task_id: str, user_id: str, message: str):
    """Process agent task asynchronously."""
    try:
        agent = get_agent_instance()
        result = agent.process(message)

        # Store result
        store_result(task_id, result)

        # Notify user (webhook, WebSocket, etc.)
        notify_user(user_id, task_id, "completed")

    except TransientError as e:
        # Retry with exponential backoff
        self.retry(exc=e, countdown=2 ** self.request.retries)

    except PermanentError as e:
        store_error(task_id, str(e))
        notify_user(user_id, task_id, "failed")
```

### 6.3 Rate Limiting

```python
from redis import Redis
from datetime import datetime

class RateLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self, redis: Redis):
        self.redis = redis

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> RateLimitResult:
        """Check if request is within rate limit."""

        now = datetime.now().timestamp()
        window_start = now - window_seconds

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current entries
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(now): now})

        # Set expiry
        pipe.expire(key, window_seconds)

        results = pipe.execute()
        current_count = results[1]

        if current_count >= limit:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=datetime.fromtimestamp(window_start + window_seconds)
            )

        return RateLimitResult(
            allowed=True,
            remaining=limit - current_count - 1,
            reset_at=datetime.fromtimestamp(window_start + window_seconds)
        )
```

---

## 7. Security Best Practices

### 7.1 Security Checklist

```
Production Security Checklist
────────────────────────────

□ Authentication & Authorization
  □ API key/token authentication
  □ User-level permissions
  □ Tool access controls
  □ Rate limiting per user

□ Input Security
  □ Input validation
  □ Prompt injection detection
  □ Content filtering
  □ Size limits on inputs

□ Output Security
  □ Response validation
  □ PII filtering
  □ Sensitive data masking
  □ Output length limits

□ Data Security
  □ Encryption at rest
  □ Encryption in transit
  □ Minimal data retention
  □ Audit logging

□ Tool Security
  □ Principle of least privilege
  □ Input sanitization for tools
  □ Output validation from tools
  □ Allowlist for external APIs

□ Operational Security
  □ Secret management (no hardcoded keys)
  □ Log sanitization
  □ Error message sanitization
  □ Regular security audits
```

### 7.2 Secure Tool Implementation

```python
class SecureTool:
    """Base class for secure tool implementation."""

    def __init__(self):
        self.allowed_operations = set()
        self.max_input_size = 10000
        self.rate_limiter = RateLimiter()

    def validate_input(self, input_data: dict) -> bool:
        """Validate tool input."""
        # Size check
        if len(str(input_data)) > self.max_input_size:
            raise InputTooLargeError()

        # Schema validation
        if not self.schema.is_valid(input_data):
            raise InvalidInputError()

        return True

    def check_permission(self, operation: str, user_context: dict) -> bool:
        """Check if operation is allowed."""
        if operation not in self.allowed_operations:
            raise OperationNotAllowedError(operation)

        # Check user-level permissions
        user_permissions = user_context.get("permissions", [])
        if operation not in user_permissions:
            raise PermissionDeniedError()

        return True

    async def execute(self, operation: str, params: dict, user_context: dict) -> str:
        """Execute tool with security checks."""
        # Rate limit check
        if not self.rate_limiter.check(user_context["user_id"]):
            raise RateLimitExceededError()

        # Permission check
        self.check_permission(operation, user_context)

        # Input validation
        self.validate_input(params)

        # Execute
        result = await self._execute_internal(operation, params)

        # Output validation
        return self.sanitize_output(result)
```

---

## Did You Know?

### Production War Stories

1. **The $100K Mistake**: A startup's agent was deployed without cost controls. A bug caused it to enter an infinite loop, making thousands of GPT-4 calls before anyone noticed. Total bill: $100,000+. Lesson: Always implement budget limits!

2. **The Jailbreak Incident**: A company's customer service bot was jailbroken by users who shared prompts on social media. The bot revealed internal pricing strategies, offered unauthorized 90% discounts, and insulted competitors. The company had to honor thousands of dollars in discounts and faced PR backlash.

3. **The Data Leak**: An agent with RAG access to internal documents was deployed publicly. Users discovered they could ask "what are all the documents in your knowledge base?" and extract sensitive information. Always validate what information agents can access and share!

4. **The Loop of Doom**: An agent was given tools to create and execute code. A user asked it to "optimize itself," and it entered a recursive self-improvement loop that crashed the server. Lesson: Think carefully about what tools agents can use together.

### Industry Practices

- **Anthropic** uses Constitutional AI to make Claude self-critique before responding
- **OpenAI** runs extensive red-teaming before deploying new models
- **Google** has a dedicated "AI Red Team" that tries to break their systems
- **Microsoft** implements multiple layers of content filtering in Azure OpenAI

---

## Summary

### Key Takeaways

1. **Defense in Depth**: Multiple layers of guardrails, not just one
2. **Observability**: You can't fix what you can't see
3. **Cost Control**: Budget limits prevent runaway costs
4. **Graceful Degradation**: Fail safely, not catastrophically
5. **Security First**: Every input is potentially malicious

### Production Readiness Checklist

```
□ Guardrails
  □ Input validation
  □ Prompt injection detection
  □ Output filtering
  □ PII protection

□ Observability
  □ Structured logging
  □ Metrics collection
  □ Distributed tracing
  □ Alerting

□ Cost Management
  □ Cost tracking
  □ Budget controls
  □ Model routing
  □ Caching

□ Reliability
  □ Retry strategies
  □ Circuit breakers
  □ Graceful degradation
  □ Fallback responses

□ Security
  □ Authentication
  □ Authorization
  □ Encryption
  □ Audit logging

□ Scalability
  □ Stateless design
  □ External state store
  □ Queue-based processing
  □ Rate limiting
```

---

## Further Reading

- [LangSmith Documentation](https://docs.smith.langchain.com/) - Tracing for LLM apps
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) - NVIDIA's guardrails framework
- [Guardrails AI](https://www.guardrailsai.com/) - Output validation framework
- [OpenTelemetry for Python](https://opentelemetry.io/docs/instrumentation/python/) - Distributed tracing
- [The Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html) - Martin Fowler

---

## ️ What's Next

Congratulations! You've completed **Phase 4: Frameworks & Agents**! 🎉

You now have:
- LangChain mastery
- Function calling and tools
- Chain-of-thought reasoning
- LangGraph stateful workflows
- Framework comparison skills
- Advanced agentic AI patterns
- Production deployment knowledge

**Next Phase**: Phase 5: Multimodal AI
- Module 22: Speech AI
- Module 23: Vision AI
- Module 24: Video AI

---

_Module 21: AI Agents in Production_
_Part of Neural Dojo: From Zero to AI Guru_
_Time to deploy those agents safely! 🚀_
