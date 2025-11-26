#!/usr/bin/env python3
"""
Module 21 Example 01: Production Agent Patterns

Demonstrates production-ready patterns for deploying AI agents:
- Stateless vs Stateful agent design
- Request lifecycle management
- Error handling and retry strategies
- Circuit breaker pattern
- Graceful degradation

Usage:
    python 01_production_patterns.py demo1  # Stateless agent
    python 01_production_patterns.py demo2  # Stateful with external store
    python 01_production_patterns.py demo3  # Circuit breaker
    python 01_production_patterns.py demo4  # Graceful degradation

Author: Neural Dojo
"""

import sys
import json
import hashlib
import time
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import deque
import threading


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AgentRequest:
    """Incoming agent request."""
    request_id: str
    user_id: str
    session_id: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent response with metadata."""
    request_id: str
    content: str
    success: bool = True
    degraded: bool = False
    reason: Optional[str] = None
    latency_ms: float = 0.0
    tokens_used: int = 0
    cost_usd: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionState:
    """Session state for stateful agents."""
    session_id: str
    user_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl_seconds: int = 3600


# =============================================================================
# SIMULATED SERVICES
# =============================================================================

class SimulatedLLM:
    """Simulated LLM with configurable failure rate."""

    def __init__(self, failure_rate: float = 0.0, latency_ms: float = 100):
        self.failure_rate = failure_rate
        self.latency_ms = latency_ms
        self.call_count = 0

    def generate(self, prompt: str, context: str = "") -> str:
        """Generate response with simulated behavior."""
        self.call_count += 1

        # Simulate latency
        time.sleep(self.latency_ms / 1000)

        # Simulate failures
        if random.random() < self.failure_rate:
            raise ServiceUnavailableError("LLM service temporarily unavailable")

        # Generate response based on prompt
        if "hello" in prompt.lower():
            return "Hello! How can I help you today?"
        elif "weather" in prompt.lower():
            return "I don't have real-time weather data, but I can help with other questions!"
        elif "help" in prompt.lower():
            return "I'm here to assist you. What would you like to know?"
        else:
            return f"I understand you're asking about '{prompt[:50]}...'. Let me help with that."


class SimulatedStateStore:
    """In-memory state store (simulates Redis)."""

    def __init__(self):
        self.store: Dict[str, Dict] = {}
        self.expiry: Dict[str, datetime] = {}

    def get(self, key: str) -> Optional[Dict]:
        """Get state by key."""
        if key in self.expiry:
            if datetime.now() > self.expiry[key]:
                del self.store[key]
                del self.expiry[key]
                return None

        return self.store.get(key)

    def set(self, key: str, value: Dict, ttl_seconds: int = 3600):
        """Set state with TTL."""
        self.store[key] = value
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)

    def delete(self, key: str):
        """Delete state."""
        self.store.pop(key, None)
        self.expiry.pop(key, None)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class ServiceUnavailableError(Exception):
    """Service temporarily unavailable."""
    pass


class RateLimitError(Exception):
    """Rate limit exceeded."""
    pass


class CircuitOpenError(Exception):
    """Circuit breaker is open."""
    pass


class BudgetExceededError(Exception):
    """Budget limit exceeded."""
    pass


# =============================================================================
# PRODUCTION PATTERNS
# =============================================================================

class StatelessAgent:
    """
    Stateless agent - no memory between requests.
    Easy to scale horizontally.
    """

    def __init__(self, llm: Optional[SimulatedLLM] = None):
        self.llm = llm or SimulatedLLM()
        self.system_prompt = "You are a helpful assistant."

    def process(self, request: AgentRequest) -> AgentResponse:
        """Process a single request with no state."""
        start_time = time.time()

        try:
            # Build prompt (no history)
            prompt = f"{self.system_prompt}\n\nUser: {request.message}"

            # Generate response
            response_text = self.llm.generate(prompt)

            latency = (time.time() - start_time) * 1000

            return AgentResponse(
                request_id=request.request_id,
                content=response_text,
                success=True,
                latency_ms=latency,
                tokens_used=len(prompt.split()) + len(response_text.split())
            )

        except Exception as e:
            return AgentResponse(
                request_id=request.request_id,
                content=f"Error processing request: {str(e)}",
                success=False,
                reason=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )


class StatefulAgent:
    """
    Stateful agent with externalized state storage.
    Maintains conversation history across requests.
    """

    def __init__(self, state_store: SimulatedStateStore,
                 llm: Optional[SimulatedLLM] = None):
        self.state_store = state_store
        self.llm = llm or SimulatedLLM()
        self.system_prompt = "You are a helpful assistant with memory of our conversation."

    def _get_session_key(self, session_id: str) -> str:
        """Generate state store key for session."""
        return f"session:{session_id}"

    def _load_state(self, session_id: str, user_id: str) -> SessionState:
        """Load or create session state."""
        key = self._get_session_key(session_id)
        data = self.state_store.get(key)

        if data:
            return SessionState(**data)

        # Create new session
        return SessionState(session_id=session_id, user_id=user_id)

    def _save_state(self, state: SessionState):
        """Save session state."""
        state.updated_at = datetime.now().isoformat()
        key = self._get_session_key(state.session_id)
        self.state_store.set(key, asdict(state), state.ttl_seconds)

    def process(self, request: AgentRequest) -> AgentResponse:
        """Process request with session state."""
        start_time = time.time()

        try:
            # Load state
            state = self._load_state(request.session_id, request.user_id)

            # Add user message to history
            state.messages.append({
                "role": "user",
                "content": request.message,
                "timestamp": request.timestamp
            })

            # Build prompt with history
            history = "\n".join([
                f"{m['role'].capitalize()}: {m['content']}"
                for m in state.messages[-10:]  # Last 10 messages
            ])
            prompt = f"{self.system_prompt}\n\nConversation:\n{history}"

            # Generate response
            response_text = self.llm.generate(prompt)

            # Add assistant response to history
            state.messages.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })

            # Save state
            self._save_state(state)

            latency = (time.time() - start_time) * 1000

            return AgentResponse(
                request_id=request.request_id,
                content=response_text,
                success=True,
                latency_ms=latency,
                tokens_used=len(prompt.split()) + len(response_text.split())
            )

        except Exception as e:
            return AgentResponse(
                request_id=request.request_id,
                content=f"Error: {str(e)}",
                success=False,
                reason=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascade failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests rejected immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        """Check if request should be allowed."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout passed
                if self.last_failure_time:
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
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.half_open_calls += 1
                if self.success_count >= self.half_open_max_calls:
                    # Recovered!
                    self._reset()
            else:
                self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record failed execution."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            if self.state == CircuitState.HALF_OPEN:
                # Failed during recovery
                self.state = CircuitState.OPEN
                self.half_open_calls = 0

    def _reset(self):
        """Reset circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": self.recovery_timeout.total_seconds()
        }


class CircuitBreakerAgent:
    """Agent wrapped with circuit breaker."""

    def __init__(self, agent: StatelessAgent, circuit_breaker: CircuitBreaker):
        self.agent = agent
        self.circuit_breaker = circuit_breaker

    def process(self, request: AgentRequest) -> AgentResponse:
        """Process with circuit breaker protection."""
        if not self.circuit_breaker.can_execute():
            return AgentResponse(
                request_id=request.request_id,
                content="Service temporarily unavailable. Please try again later.",
                success=False,
                degraded=True,
                reason="circuit_open"
            )

        try:
            response = self.agent.process(request)

            if response.success:
                self.circuit_breaker.record_success()
            else:
                self.circuit_breaker.record_failure()

            return response

        except Exception as e:
            self.circuit_breaker.record_failure()
            return AgentResponse(
                request_id=request.request_id,
                content=f"Service error: {str(e)}",
                success=False,
                reason=str(e)
            )


# =============================================================================
# GRACEFUL DEGRADATION
# =============================================================================

class FallbackResponses:
    """Pre-defined fallback responses for common scenarios."""

    RESPONSES = {
        "greeting": "Hello! I'm currently operating in limited mode. How can I help?",
        "help": "I can help with general questions. What would you like to know?",
        "weather": "I'm sorry, I don't have access to weather data right now.",
        "unknown": "I'm experiencing some difficulties. Please try again later or contact support.",
        "rate_limited": "You've reached the request limit. Please wait a moment before trying again.",
        "budget_exceeded": "I've reached my usage limit for now. Please try again later.",
    }

    @classmethod
    def get(cls, intent: str) -> str:
        return cls.RESPONSES.get(intent, cls.RESPONSES["unknown"])

    @classmethod
    def classify_intent(cls, message: str) -> str:
        """Simple intent classification."""
        message_lower = message.lower()

        if any(w in message_lower for w in ["hello", "hi", "hey"]):
            return "greeting"
        if any(w in message_lower for w in ["help", "assist", "support"]):
            return "help"
        if "weather" in message_lower:
            return "weather"
        return "unknown"


class GracefulDegradationAgent:
    """
    Agent with multiple fallback levels:
    1. Full agent processing
    2. Simpler/cheaper model
    3. Cached responses
    4. Fallback templates
    """

    def __init__(
        self,
        primary_agent: StatelessAgent,
        fallback_agent: Optional[StatelessAgent] = None
    ):
        self.primary_agent = primary_agent
        self.fallback_agent = fallback_agent or StatelessAgent(
            SimulatedLLM(failure_rate=0.1, latency_ms=50)  # Faster, more reliable
        )
        self.response_cache: Dict[str, str] = {}
        self.fallback = FallbackResponses()

    def _cache_key(self, message: str) -> str:
        """Generate cache key for message."""
        normalized = message.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def process(self, request: AgentRequest) -> AgentResponse:
        """Process with graceful degradation."""

        # Level 1: Try primary agent
        try:
            response = self.primary_agent.process(request)
            if response.success:
                # Cache successful response
                cache_key = self._cache_key(request.message)
                self.response_cache[cache_key] = response.content
                return response
        except Exception:
            pass

        # Level 2: Try fallback agent
        try:
            response = self.fallback_agent.process(request)
            if response.success:
                response.degraded = True
                response.reason = "using_fallback_model"
                return response
        except Exception:
            pass

        # Level 3: Try cache
        cache_key = self._cache_key(request.message)
        if cache_key in self.response_cache:
            return AgentResponse(
                request_id=request.request_id,
                content=self.response_cache[cache_key],
                success=True,
                degraded=True,
                reason="cached_response"
            )

        # Level 4: Use fallback templates
        intent = self.fallback.classify_intent(request.message)
        fallback_response = self.fallback.get(intent)

        return AgentResponse(
            request_id=request.request_id,
            content=fallback_response,
            success=True,
            degraded=True,
            reason="template_fallback"
        )


# =============================================================================
# RETRY STRATEGY
# =============================================================================

class RetryStrategy:
    """Configurable retry strategy with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt number."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        # Add jitter
        jitter = random.uniform(0, 0.1 * delay)
        return min(delay + jitter, self.max_delay)

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        retryable_exceptions: tuple = (ServiceUnavailableError,),
        **kwargs
    ) -> Any:
        """Execute function with retry on failure."""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except retryable_exceptions as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = self.get_delay(attempt)
                    print(f"   Attempt {attempt + 1} failed, retrying in {delay:.1f}s...")
                    time.sleep(delay)

        raise last_exception


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo1_stateless_agent():
    """Demo 1: Stateless Agent Pattern"""
    print("\n" + "=" * 70)
    print("DEMO 1: Stateless Agent Pattern")
    print("=" * 70)

    agent = StatelessAgent()

    print("\n📝 Stateless agents have no memory between requests")
    print("   Each request is processed independently")
    print("   Easy to scale horizontally (any instance handles any request)")

    # Send multiple requests
    requests = [
        AgentRequest(
            request_id=f"req_{i}",
            user_id="user_123",
            session_id="session_abc",
            message=msg
        )
        for i, msg in enumerate([
            "Hello, how are you?",
            "What's the weather like?",
            "Can you help me with something?"
        ])
    ]

    print("\n📨 Processing requests:")
    for req in requests:
        response = agent.process(req)
        print(f"\n   Request: {req.message}")
        print(f"   Response: {response.content}")
        print(f"   Latency: {response.latency_ms:.1f}ms")

    print("\n✅ Stateless processing complete")
    print("   Note: Agent doesn't remember previous messages in same session")


def demo2_stateful_agent():
    """Demo 2: Stateful Agent with External Store"""
    print("\n" + "=" * 70)
    print("DEMO 2: Stateful Agent with External State Store")
    print("=" * 70)

    state_store = SimulatedStateStore()
    agent = StatefulAgent(state_store)

    print("\n📝 Stateful agents maintain conversation history")
    print("   State is externalized (Redis, PostgreSQL, etc.)")
    print("   Still scalable - any instance can load session state")

    session_id = "session_xyz"
    user_id = "user_456"

    messages = [
        "Hi, my name is Alice",
        "What did I just tell you?",
        "Can you remember my name?"
    ]

    print(f"\n📨 Conversation in session {session_id}:")
    for i, msg in enumerate(messages):
        request = AgentRequest(
            request_id=f"req_{i}",
            user_id=user_id,
            session_id=session_id,
            message=msg
        )
        response = agent.process(request)
        print(f"\n   [{i+1}] User: {msg}")
        print(f"       Agent: {response.content}")

    # Show stored state
    state_key = agent._get_session_key(session_id)
    stored_state = state_store.get(state_key)
    print(f"\n📦 State stored with {len(stored_state['messages'])} messages")
    print(f"   Session TTL: {stored_state['ttl_seconds']} seconds")

    print("\n✅ Stateful processing complete")


def demo3_circuit_breaker():
    """Demo 3: Circuit Breaker Pattern"""
    print("\n" + "=" * 70)
    print("DEMO 3: Circuit Breaker Pattern")
    print("=" * 70)

    # Create agent with high failure rate
    failing_llm = SimulatedLLM(failure_rate=0.7, latency_ms=50)
    base_agent = StatelessAgent(failing_llm)

    circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout_seconds=5.0,
        half_open_max_calls=2
    )

    protected_agent = CircuitBreakerAgent(base_agent, circuit_breaker)

    print("\n📝 Circuit Breaker prevents cascade failures:")
    print("   - CLOSED: Normal operation")
    print("   - OPEN: Too many failures, reject immediately")
    print("   - HALF_OPEN: Testing if service recovered")

    print(f"\n⚙️  Configuration:")
    print(f"   Failure threshold: {circuit_breaker.failure_threshold}")
    print(f"   Recovery timeout: {circuit_breaker.recovery_timeout.total_seconds()}s")
    print(f"   LLM failure rate: 70% (for demo)")

    print("\n📨 Sending requests (some will fail):")

    for i in range(10):
        request = AgentRequest(
            request_id=f"req_{i}",
            user_id="user_789",
            session_id="session_test",
            message="Test message"
        )

        response = protected_agent.process(request)
        status = circuit_breaker.get_status()

        symbol = "✅" if response.success else "❌"
        circuit_state = status["state"].upper()

        print(f"   [{i+1:2d}] {symbol} Circuit: {circuit_state:10s} | "
              f"Failures: {status['failure_count']}/{status['failure_threshold']} | "
              f"Response: {response.content[:40]}...")

        # Small delay
        time.sleep(0.1)

    print("\n⏳ Waiting for recovery timeout...")
    time.sleep(5)

    print("\n📨 Sending request after recovery timeout:")
    request = AgentRequest(
        request_id="req_recovery",
        user_id="user_789",
        session_id="session_test",
        message="Recovery test"
    )
    response = protected_agent.process(request)
    status = circuit_breaker.get_status()
    print(f"   Circuit: {status['state'].upper()} | Response success: {response.success}")

    print("\n✅ Circuit breaker demo complete")


def demo4_graceful_degradation():
    """Demo 4: Graceful Degradation Pattern"""
    print("\n" + "=" * 70)
    print("DEMO 4: Graceful Degradation Pattern")
    print("=" * 70)

    # Primary agent that always fails
    failing_llm = SimulatedLLM(failure_rate=1.0, latency_ms=100)
    primary_agent = StatelessAgent(failing_llm)

    # Fallback agent that sometimes fails
    fallback_llm = SimulatedLLM(failure_rate=0.5, latency_ms=50)
    fallback_agent = StatelessAgent(fallback_llm)

    graceful_agent = GracefulDegradationAgent(primary_agent, fallback_agent)

    print("\n📝 Graceful Degradation provides multiple fallback levels:")
    print("   1. Primary agent (full functionality)")
    print("   2. Fallback agent (simpler/cheaper)")
    print("   3. Cached responses")
    print("   4. Template fallbacks")

    print("\n📨 Testing degradation levels:")

    # Pre-populate cache
    graceful_agent.response_cache[
        graceful_agent._cache_key("what is 2+2")
    ] = "The answer is 4."

    test_cases = [
        ("Hello there!", "greeting"),
        ("Help me please", "help"),
        ("What's the weather?", "weather"),
        ("what is 2+2", "cached"),
        ("Random question", "unknown"),
    ]

    for message, expected_type in test_cases:
        request = AgentRequest(
            request_id=f"req_{expected_type}",
            user_id="user_test",
            session_id="session_test",
            message=message
        )

        response = graceful_agent.process(request)

        degradation = "FULL" if not response.degraded else response.reason or "DEGRADED"
        print(f"\n   Message: '{message}'")
        print(f"   Mode: {degradation}")
        print(f"   Response: {response.content}")

    print("\n✅ Graceful degradation demo complete")
    print("   Note: System never fully fails - always provides some response")


def show_help():
    """Show help information."""
    print("\n" + "=" * 70)
    print("PRODUCTION AGENT PATTERNS - Module 21 Example 01")
    print("=" * 70)

    print("""
Demonstrates production-ready patterns for AI agents:

DEMOS:
  demo1  - Stateless Agent (no memory, easy to scale)
  demo2  - Stateful Agent (external state store)
  demo3  - Circuit Breaker (prevent cascade failures)
  demo4  - Graceful Degradation (multiple fallback levels)

USAGE:
  python 01_production_patterns.py demo1
  python 01_production_patterns.py demo2
  python 01_production_patterns.py demo3
  python 01_production_patterns.py demo4
  python 01_production_patterns.py all

KEY PATTERNS:
  Stateless   - Each request independent, easy horizontal scaling
  Stateful    - Externalized state (Redis), session affinity optional
  Circuit     - Open when failing, close when recovered
  Degradation - Multiple fallback levels ensure availability

Author: Neural Dojo
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo1_stateless_agent()
    elif command == "demo2":
        demo2_stateful_agent()
    elif command == "demo3":
        demo3_circuit_breaker()
    elif command == "demo4":
        demo4_graceful_degradation()
    elif command == "help":
        show_help()
    elif command == "all":
        demo1_stateless_agent()
        demo2_stateful_agent()
        demo3_circuit_breaker()
        demo4_graceful_degradation()
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run 'python 01_production_patterns.py help' for usage")


if __name__ == "__main__":
    main()
