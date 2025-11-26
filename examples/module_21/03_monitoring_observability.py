#!/usr/bin/env python3
"""
Module 21 Example 03: Monitoring and Observability

Demonstrates monitoring and observability for production AI agents:
- Structured logging with request tracing
- Metrics collection and aggregation
- Cost tracking and analysis
- Performance monitoring

Usage:
    python 03_monitoring_observability.py demo1  # Structured logging
    python 03_monitoring_observability.py demo2  # Metrics collection
    python 03_monitoring_observability.py demo3  # Cost tracking
    python 03_monitoring_observability.py demo4  # Performance analysis

Author: Neural Dojo
"""

import sys
import json
import time
import random
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from statistics import mean, median, stdev
import threading


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    event: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    latency_ms: Optional[float] = None
    tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


@dataclass
class Metric:
    """A single metric data point."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class CostRecord:
    """Record of cost incurred."""
    request_id: str
    user_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PerformanceRecord:
    """Record of request performance."""
    request_id: str
    latency_ms: float
    time_to_first_token_ms: Optional[float] = None
    tool_calls: int = 0
    llm_calls: int = 0
    memory_lookups: int = 0
    success: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# STRUCTURED LOGGING
# =============================================================================

class StructuredLogger:
    """Structured logging with JSON output."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logs: List[LogEntry] = []

    def _log(self, level: str, event: str, **kwargs):
        """Create and store log entry."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            event=event,
            agent_id=self.agent_id,
            **kwargs
        )
        self.logs.append(entry)
        return entry

    def info(self, event: str, **kwargs) -> LogEntry:
        return self._log("INFO", event, **kwargs)

    def warning(self, event: str, **kwargs) -> LogEntry:
        return self._log("WARNING", event, **kwargs)

    def error(self, event: str, **kwargs) -> LogEntry:
        return self._log("ERROR", event, **kwargs)

    def debug(self, event: str, **kwargs) -> LogEntry:
        return self._log("DEBUG", event, **kwargs)

    # Agent-specific logging methods
    def log_request_start(self, request_id: str, user_id: str, message: str):
        return self.info(
            "request_start",
            request_id=request_id,
            user_id=user_id,
            metadata={"message_length": len(message)}
        )

    def log_request_end(self, request_id: str, latency_ms: float,
                        tokens: int, cost: float, success: bool = True):
        event = "request_complete" if success else "request_failed"
        level = "INFO" if success else "ERROR"
        return self._log(
            level, event,
            request_id=request_id,
            latency_ms=latency_ms,
            tokens=tokens,
            cost_usd=cost
        )

    def log_llm_call(self, request_id: str, model: str,
                     input_tokens: int, output_tokens: int,
                     latency_ms: float, cost: float):
        return self.info(
            "llm_call",
            request_id=request_id,
            latency_ms=latency_ms,
            tokens=input_tokens + output_tokens,
            cost_usd=cost,
            metadata={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
        )

    def log_tool_call(self, request_id: str, tool: str,
                      latency_ms: float, success: bool = True):
        return self.info(
            "tool_call",
            request_id=request_id,
            latency_ms=latency_ms,
            metadata={"tool": tool, "success": success}
        )

    def log_guardrail_triggered(self, request_id: str, guardrail: str,
                                 reason: str):
        return self.warning(
            "guardrail_triggered",
            request_id=request_id,
            metadata={"guardrail": guardrail, "reason": reason}
        )

    def get_logs(self, level: Optional[str] = None,
                 event: Optional[str] = None) -> List[LogEntry]:
        """Filter and retrieve logs."""
        result = self.logs
        if level:
            result = [l for l in result if l.level == level]
        if event:
            result = [l for l in result if l.event == event]
        return result

    def export_json(self) -> str:
        """Export all logs as JSON."""
        return json.dumps([asdict(l) for l in self.logs], indent=2, default=str)


# =============================================================================
# METRICS COLLECTION
# =============================================================================

class MetricsCollector:
    """Collect and aggregate metrics."""

    def __init__(self):
        self.counters: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _labels_key(self, labels: Dict[str, str]) -> str:
        """Convert labels dict to string key."""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def inc_counter(self, name: str, value: float = 1.0,
                    labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        with self._lock:
            label_key = self._labels_key(labels or {})
            self.counters[name][label_key] += value

    def set_gauge(self, name: str, value: float,
                  labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        with self._lock:
            label_key = self._labels_key(labels or {})
            key = f"{name}:{label_key}" if label_key else name
            self.gauges[key] = value

    def observe_histogram(self, name: str, value: float,
                          labels: Optional[Dict[str, str]] = None):
        """Record a histogram observation."""
        with self._lock:
            label_key = self._labels_key(labels or {})
            key = f"{name}:{label_key}" if label_key else name
            self.histograms[key].append(value)

    def get_counter(self, name: str) -> Dict[str, float]:
        """Get counter values."""
        return dict(self.counters.get(name, {}))

    def get_gauge(self, name: str) -> Optional[float]:
        """Get gauge value."""
        return self.gauges.get(name)

    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        # Aggregate all label variants
        values = []
        for key, vals in self.histograms.items():
            if key.startswith(name):
                values.extend(vals)

        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": mean(values),
            "median": median(values),
            "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 20 else max(values),
            "p99": sorted(values)[int(len(values) * 0.99)] if len(values) > 100 else max(values),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in set(k.split(":")[0] for k in self.histograms.keys())
            }
        }


class AgentMetrics:
    """Metrics specific to AI agents."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.collector = MetricsCollector()

    def record_request(self, status: str = "success"):
        """Record a request."""
        self.collector.inc_counter(
            "agent_requests_total",
            labels={"agent_id": self.agent_id, "status": status}
        )

    def record_latency(self, latency_ms: float):
        """Record request latency."""
        self.collector.observe_histogram(
            "agent_request_latency_ms",
            latency_ms,
            labels={"agent_id": self.agent_id}
        )

    def record_tokens(self, input_tokens: int, output_tokens: int, model: str):
        """Record token usage."""
        self.collector.inc_counter(
            "llm_tokens_total",
            input_tokens,
            labels={"model": model, "type": "input"}
        )
        self.collector.inc_counter(
            "llm_tokens_total",
            output_tokens,
            labels={"model": model, "type": "output"}
        )

    def record_cost(self, cost_usd: float, model: str):
        """Record cost."""
        self.collector.inc_counter(
            "agent_cost_usd_total",
            cost_usd,
            labels={"agent_id": self.agent_id, "model": model}
        )

    def record_tool_call(self, tool: str, success: bool = True):
        """Record tool invocation."""
        self.collector.inc_counter(
            "tool_calls_total",
            labels={"tool": tool, "status": "success" if success else "error"}
        )

    def record_guardrail_violation(self, guardrail: str):
        """Record guardrail violation."""
        self.collector.inc_counter(
            "guardrail_violations_total",
            labels={"guardrail": guardrail}
        )

    def set_active_sessions(self, count: int):
        """Set number of active sessions."""
        self.collector.set_gauge(
            "agent_active_sessions",
            count,
            labels={"agent_id": self.agent_id}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get all agent metrics."""
        return self.collector.get_summary()


# =============================================================================
# COST TRACKING
# =============================================================================

class CostTracker:
    """Track and analyze costs."""

    # Cost per 1K tokens
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }

    def __init__(self):
        self.records: List[CostRecord] = []

    def calculate_cost(self, model: str, input_tokens: int,
                       output_tokens: int) -> float:
        """Calculate cost for token usage."""
        rates = self.MODEL_COSTS.get(model, {"input": 0.01, "output": 0.03})
        return (input_tokens / 1000 * rates["input"] +
                output_tokens / 1000 * rates["output"])

    def record(self, request_id: str, user_id: str, model: str,
               input_tokens: int, output_tokens: int) -> CostRecord:
        """Record a cost event."""
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        record = CostRecord(
            request_id=request_id,
            user_id=user_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost
        )

        self.records.append(record)
        return record

    def get_total_cost(self) -> float:
        """Get total cost."""
        return sum(r.cost_usd for r in self.records)

    def get_cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        by_model = defaultdict(float)
        for r in self.records:
            by_model[r.model] += r.cost_usd
        return dict(by_model)

    def get_cost_by_user(self) -> Dict[str, float]:
        """Get cost breakdown by user."""
        by_user = defaultdict(float)
        for r in self.records:
            by_user[r.user_id] += r.cost_usd
        return dict(by_user)

    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        if not self.records:
            return {"total": 0, "records": 0}

        return {
            "total_cost_usd": self.get_total_cost(),
            "total_records": len(self.records),
            "average_cost": self.get_total_cost() / len(self.records),
            "by_model": self.get_cost_by_model(),
            "by_user": self.get_cost_by_user(),
            "total_tokens": {
                "input": sum(r.input_tokens for r in self.records),
                "output": sum(r.output_tokens for r in self.records),
            }
        }


# =============================================================================
# PERFORMANCE TRACKING
# =============================================================================

class PerformanceTracker:
    """Track and analyze performance."""

    def __init__(self):
        self.records: List[PerformanceRecord] = []

    def record(self, request_id: str, latency_ms: float,
               tool_calls: int = 0, llm_calls: int = 1,
               memory_lookups: int = 0, success: bool = True) -> PerformanceRecord:
        """Record performance data."""
        record = PerformanceRecord(
            request_id=request_id,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            llm_calls=llm_calls,
            memory_lookups=memory_lookups,
            success=success
        )
        self.records.append(record)
        return record

    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        latencies = [r.latency_ms for r in self.records]
        if not latencies:
            return {}

        sorted_latencies = sorted(latencies)
        return {
            "count": len(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "mean": mean(latencies),
            "median": median(latencies),
            "stdev": stdev(latencies) if len(latencies) > 1 else 0,
            "p50": sorted_latencies[int(len(latencies) * 0.5)],
            "p90": sorted_latencies[int(len(latencies) * 0.9)],
            "p95": sorted_latencies[int(len(latencies) * 0.95)],
            "p99": sorted_latencies[int(len(latencies) * 0.99)] if len(latencies) > 100 else max(latencies),
        }

    def get_success_rate(self) -> float:
        """Get success rate."""
        if not self.records:
            return 0.0
        successes = sum(1 for r in self.records if r.success)
        return successes / len(self.records)

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.records:
            return {}

        return {
            "total_requests": len(self.records),
            "success_rate": self.get_success_rate(),
            "latency": self.get_latency_stats(),
            "averages": {
                "tool_calls": mean(r.tool_calls for r in self.records),
                "llm_calls": mean(r.llm_calls for r in self.records),
                "memory_lookups": mean(r.memory_lookups for r in self.records),
            }
        }


# =============================================================================
# SIMULATED AGENT FOR DEMOS
# =============================================================================

class ObservableAgent:
    """Agent with full observability instrumentation."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = StructuredLogger(agent_id)
        self.metrics = AgentMetrics(agent_id)
        self.cost_tracker = CostTracker()
        self.performance_tracker = PerformanceTracker()

    def process(self, request_id: str, user_id: str, message: str) -> str:
        """Process request with full observability."""
        start_time = time.time()

        # Log request start
        self.logger.log_request_start(request_id, user_id, message)

        try:
            # Simulate processing
            model = random.choice(["claude-3-haiku", "claude-3-sonnet"])
            input_tokens = len(message.split()) * 2
            output_tokens = random.randint(50, 200)

            # Simulate LLM call
            llm_latency = random.uniform(100, 500)
            time.sleep(llm_latency / 1000)  # Simulate actual latency

            cost = self.cost_tracker.calculate_cost(model, input_tokens, output_tokens)

            # Log LLM call
            self.logger.log_llm_call(
                request_id, model, input_tokens, output_tokens, llm_latency, cost
            )

            # Record metrics
            self.metrics.record_tokens(input_tokens, output_tokens, model)
            self.metrics.record_cost(cost, model)

            # Simulate tool calls (sometimes)
            tool_calls = 0
            if random.random() > 0.7:
                tool_calls = random.randint(1, 3)
                for i in range(tool_calls):
                    tool = random.choice(["search", "calculator", "datetime"])
                    tool_latency = random.uniform(10, 100)
                    self.logger.log_tool_call(request_id, tool, tool_latency)
                    self.metrics.record_tool_call(tool)

            # Calculate total latency
            total_latency = (time.time() - start_time) * 1000

            # Record cost
            self.cost_tracker.record(
                request_id, user_id, model, input_tokens, output_tokens
            )

            # Record performance
            self.performance_tracker.record(
                request_id, total_latency,
                tool_calls=tool_calls, llm_calls=1
            )

            # Log completion
            self.logger.log_request_end(
                request_id, total_latency,
                input_tokens + output_tokens, cost, success=True
            )

            self.metrics.record_request("success")
            self.metrics.record_latency(total_latency)

            return f"Processed: {message[:50]}..."

        except Exception as e:
            total_latency = (time.time() - start_time) * 1000
            self.logger.log_request_end(
                request_id, total_latency, 0, 0, success=False
            )
            self.metrics.record_request("error")
            raise


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo1_structured_logging():
    """Demo 1: Structured Logging"""
    print("\n" + "=" * 70)
    print("DEMO 1: Structured Logging")
    print("=" * 70)

    logger = StructuredLogger("demo_agent")

    print("\n📝 Structured logging provides:")
    print("   - JSON-formatted logs for easy parsing")
    print("   - Request ID correlation across operations")
    print("   - Consistent fields for metrics extraction")

    # Generate some logs
    request_id = str(uuid.uuid4())[:8]
    user_id = "user_123"

    logger.log_request_start(request_id, user_id, "Hello, world!")
    logger.log_llm_call(request_id, "claude-3-sonnet", 50, 100, 234.5, 0.0015)
    logger.log_tool_call(request_id, "search", 45.2, success=True)
    logger.log_request_end(request_id, 312.5, 150, 0.0015, success=True)

    # Simulate an error
    error_request_id = str(uuid.uuid4())[:8]
    logger.log_request_start(error_request_id, "user_456", "Bad request")
    logger.log_guardrail_triggered(error_request_id, "content_filter", "blocked_category: violence")

    print("\n📋 Sample log entries:\n")
    for log in logger.logs[:3]:
        print(f"   {log.to_json()}")
        print()

    print(f"\n📊 Log summary:")
    print(f"   Total entries: {len(logger.logs)}")
    print(f"   By level: INFO={len(logger.get_logs('INFO'))}, "
          f"WARNING={len(logger.get_logs('WARNING'))}, "
          f"ERROR={len(logger.get_logs('ERROR'))}")

    print("\n✅ Structured logging demo complete")


def demo2_metrics_collection():
    """Demo 2: Metrics Collection"""
    print("\n" + "=" * 70)
    print("DEMO 2: Metrics Collection")
    print("=" * 70)

    metrics = AgentMetrics("demo_agent")

    print("\n📝 Metrics provide:")
    print("   - Counters: Total counts (requests, tokens, errors)")
    print("   - Gauges: Current values (active sessions)")
    print("   - Histograms: Distributions (latency percentiles)")

    # Simulate some traffic
    print("\n📊 Simulating 100 requests...\n")

    for i in range(100):
        # Record request
        status = "success" if random.random() > 0.05 else "error"
        metrics.record_request(status)

        # Record latency (varied)
        base_latency = random.uniform(100, 500)
        latency = base_latency * (3 if random.random() > 0.95 else 1)  # Some slow ones
        metrics.record_latency(latency)

        # Record tokens
        model = random.choice(["claude-3-haiku", "claude-3-sonnet"])
        metrics.record_tokens(
            random.randint(50, 200),
            random.randint(100, 400),
            model
        )

        # Record cost
        metrics.record_cost(random.uniform(0.001, 0.05), model)

        # Record tool calls (sometimes)
        if random.random() > 0.7:
            tool = random.choice(["search", "calculator", "datetime"])
            metrics.record_tool_call(tool, success=random.random() > 0.1)

    # Get summary
    stats = metrics.get_stats()

    print("   Counter: agent_requests_total")
    for labels, value in stats["counters"].get("agent_requests_total", {}).items():
        print(f"      {labels}: {value:.0f}")

    print("\n   Counter: llm_tokens_total")
    for labels, value in stats["counters"].get("llm_tokens_total", {}).items():
        print(f"      {labels}: {value:.0f}")

    print("\n   Histogram: agent_request_latency_ms")
    latency_stats = stats["histograms"].get("agent_request_latency_ms", {})
    if latency_stats:
        print(f"      count: {latency_stats.get('count', 0):.0f}")
        print(f"      mean: {latency_stats.get('mean', 0):.1f}ms")
        print(f"      median: {latency_stats.get('median', 0):.1f}ms")
        print(f"      p95: {latency_stats.get('p95', 0):.1f}ms")
        print(f"      p99: {latency_stats.get('p99', 0):.1f}ms")

    print("\n✅ Metrics collection demo complete")


def demo3_cost_tracking():
    """Demo 3: Cost Tracking"""
    print("\n" + "=" * 70)
    print("DEMO 3: Cost Tracking")
    print("=" * 70)

    tracker = CostTracker()

    print("\n📝 Cost tracking shows:")
    print("   - Total spending")
    print("   - Breakdown by model")
    print("   - Breakdown by user")
    print("   - Token usage patterns")

    print("\n⚙️  Model pricing (per 1K tokens):")
    for model, rates in tracker.MODEL_COSTS.items():
        print(f"   {model}: ${rates['input']:.4f} input, ${rates['output']:.4f} output")

    # Simulate usage
    print("\n📊 Simulating 50 requests across users and models...\n")

    users = ["user_a", "user_b", "user_c"]
    models = ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]

    for i in range(50):
        user = random.choice(users)
        # Simulate model routing (haiku for simple, opus for complex)
        complexity = random.random()
        if complexity < 0.6:
            model = "claude-3-haiku"
            tokens = (random.randint(20, 100), random.randint(50, 150))
        elif complexity < 0.9:
            model = "claude-3-sonnet"
            tokens = (random.randint(100, 300), random.randint(200, 500))
        else:
            model = "claude-3-opus"
            tokens = (random.randint(200, 500), random.randint(300, 800))

        tracker.record(
            f"req_{i}",
            user,
            model,
            tokens[0],
            tokens[1]
        )

    # Get summary
    summary = tracker.get_summary()

    print(f"   Total cost: ${summary['total_cost_usd']:.4f}")
    print(f"   Total requests: {summary['total_records']}")
    print(f"   Average per request: ${summary['average_cost']:.6f}")

    print(f"\n   Cost by model:")
    for model, cost in sorted(summary['by_model'].items(), key=lambda x: -x[1]):
        pct = (cost / summary['total_cost_usd']) * 100 if summary['total_cost_usd'] > 0 else 0
        print(f"      {model}: ${cost:.4f} ({pct:.1f}%)")

    print(f"\n   Cost by user:")
    for user, cost in sorted(summary['by_user'].items(), key=lambda x: -x[1]):
        pct = (cost / summary['total_cost_usd']) * 100 if summary['total_cost_usd'] > 0 else 0
        print(f"      {user}: ${cost:.4f} ({pct:.1f}%)")

    print(f"\n   Token usage:")
    print(f"      Input: {summary['total_tokens']['input']:,}")
    print(f"      Output: {summary['total_tokens']['output']:,}")
    print(f"      Total: {summary['total_tokens']['input'] + summary['total_tokens']['output']:,}")

    print("\n✅ Cost tracking demo complete")


def demo4_performance_analysis():
    """Demo 4: Performance Analysis"""
    print("\n" + "=" * 70)
    print("DEMO 4: Performance Analysis")
    print("=" * 70)

    agent = ObservableAgent("performance_test")

    print("\n📝 Performance analysis provides:")
    print("   - Latency distributions")
    print("   - Success rates")
    print("   - Operation breakdowns")

    # Run simulated requests
    print("\n📊 Processing 30 simulated requests...\n")

    for i in range(30):
        request_id = f"req_{i:03d}"
        user_id = f"user_{i % 5}"
        message = f"Test message {i} with some content to process"

        try:
            agent.process(request_id, user_id, message)
        except Exception:
            pass  # Some might fail

    # Get performance summary
    perf = agent.performance_tracker.get_summary()

    print(f"   Total requests: {perf['total_requests']}")
    print(f"   Success rate: {perf['success_rate'] * 100:.1f}%")

    print(f"\n   Latency statistics:")
    lat = perf['latency']
    print(f"      Min: {lat['min']:.1f}ms")
    print(f"      Mean: {lat['mean']:.1f}ms")
    print(f"      Median: {lat['median']:.1f}ms")
    print(f"      P90: {lat['p90']:.1f}ms")
    print(f"      P95: {lat['p95']:.1f}ms")
    print(f"      Max: {lat['max']:.1f}ms")

    print(f"\n   Operation averages:")
    avgs = perf['averages']
    print(f"      LLM calls per request: {avgs['llm_calls']:.1f}")
    print(f"      Tool calls per request: {avgs['tool_calls']:.1f}")
    print(f"      Memory lookups per request: {avgs['memory_lookups']:.1f}")

    # Cost summary
    cost = agent.cost_tracker.get_summary()
    print(f"\n   Cost analysis:")
    print(f"      Total cost: ${cost['total_cost_usd']:.4f}")
    print(f"      Cost per request: ${cost['average_cost']:.6f}")

    # Log analysis
    logs = agent.logger.logs
    print(f"\n   Log analysis:")
    print(f"      Total log entries: {len(logs)}")
    print(f"      LLM calls logged: {len([l for l in logs if l.event == 'llm_call'])}")
    print(f"      Tool calls logged: {len([l for l in logs if l.event == 'tool_call'])}")

    print("\n✅ Performance analysis demo complete")


def show_help():
    """Show help information."""
    print("\n" + "=" * 70)
    print("MONITORING AND OBSERVABILITY - Module 21 Example 03")
    print("=" * 70)

    print("""
Demonstrates monitoring and observability for production AI agents:

DEMOS:
  demo1  - Structured logging with JSON output
  demo2  - Metrics collection (counters, gauges, histograms)
  demo3  - Cost tracking and analysis
  demo4  - Performance analysis with observable agent

USAGE:
  python 03_monitoring_observability.py demo1
  python 03_monitoring_observability.py demo2
  python 03_monitoring_observability.py demo3
  python 03_monitoring_observability.py demo4
  python 03_monitoring_observability.py all

OBSERVABILITY PILLARS:
  Logs     - What happened? (request IDs, events, errors)
  Metrics  - How much? (counters, latencies, costs)
  Traces   - How did it flow? (request spans, tool calls)

Author: Neural Dojo
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo1_structured_logging()
    elif command == "demo2":
        demo2_metrics_collection()
    elif command == "demo3":
        demo3_cost_tracking()
    elif command == "demo4":
        demo4_performance_analysis()
    elif command == "help":
        show_help()
    elif command == "all":
        demo1_structured_logging()
        demo2_metrics_collection()
        demo3_cost_tracking()
        demo4_performance_analysis()
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run 'python 03_monitoring_observability.py help' for usage")


if __name__ == "__main__":
    main()
