#!/usr/bin/env python3
"""
AIOps Toolkit - Module 54 Deliverable

A comprehensive toolkit for AI-powered IT operations:
- Intelligent log parsing and template extraction
- Log anomaly detection (frequency, sequence, content)
- AI-assisted root cause analysis
- Automated incident response
- Full AIOps pipeline integration

Usage:
    python deliverable_aiops_toolkit.py demo1  # Log parsing
    python deliverable_aiops_toolkit.py demo2  # Anomaly detection
    python deliverable_aiops_toolkit.py demo3  # Root cause analysis
    python deliverable_aiops_toolkit.py demo4  # Incident response
    python deliverable_aiops_toolkit.py demo5  # Full AIOps pipeline

Author: Neural Dojo
Module: 54 - AIOps & Log Analysis

Note: This is an EDUCATIONAL implementation demonstrating AIOps concepts.
For production use, consider:
- Drain3 or Spell for log parsing
- scikit-learn or PyOD for anomaly detection
- Production AIOps platforms (Splunk ITSI, Datadog, Moogsoft)
- LLMs (Claude, GPT-4) for semantic log analysis and RCA
"""

import json
import math
import random
import re
import sys
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from collections import defaultdict, Counter


# =============================================================================
# Configuration
# =============================================================================

STORAGE_DIR = Path(".aiops_toolkit")
STORAGE_DIR.mkdir(exist_ok=True)


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AnomalyType(Enum):
    """Types of log anomalies."""
    FREQUENCY = "frequency"
    SEQUENCE = "sequence"
    CONTENT = "content"
    NEW_PATTERN = "new_pattern"
    TIMING = "timing"


class IncidentSeverity(Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RemediationLevel(Enum):
    """Auto-remediation trust levels."""
    ALERT_ONLY = 0
    SUGGEST = 1
    APPROVE = 2
    AUTO_LOW_RISK = 3
    AUTO_HIGH_RISK = 4


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LogEntry:
    """A parsed log entry."""
    timestamp: str
    level: str
    source: str
    message: str
    raw: str
    template: Optional[str] = None
    variables: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LogTemplate:
    """A log template with statistics."""
    template_id: str
    pattern: str
    count: int
    first_seen: str
    last_seen: str
    example: str
    variable_positions: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LogAnomaly:
    """A detected log anomaly."""
    anomaly_id: str
    timestamp: str
    anomaly_type: str
    severity: str
    description: str
    evidence: List[str]
    confidence: float
    affected_logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RootCauseResult:
    """Result of root cause analysis."""
    incident_id: str
    root_cause: str
    causal_chain: List[str]
    contributing_factors: List[str]
    confidence: float
    evidence: Dict[str, Any]
    recommended_fix: str
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RemediationAction:
    """An automated remediation action."""
    action_id: str
    action_type: str
    description: str
    command: str
    risk_level: str
    requires_approval: bool
    estimated_impact: str
    rollback_command: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Incident:
    """An incident record."""
    incident_id: str
    title: str
    severity: str
    status: str
    created_at: str
    updated_at: str
    root_cause: Optional[str] = None
    remediation_applied: Optional[str] = None
    resolved_at: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# Log Generator (Simulates Real Logs)
# =============================================================================

class LogGenerator:
    """
    Generates realistic log data with:
    - Multiple services and components
    - Normal patterns with occasional anomalies
    - Various log formats and levels
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.services = ["api-gateway", "auth-service", "user-service",
                        "payment-service", "notification-service", "database"]
        self.normal_templates = [
            ("INFO", "{service}", "Request processed successfully in {latency}ms"),
            ("INFO", "{service}", "User {user_id} logged in from {ip}"),
            ("INFO", "{service}", "Cache hit for key {cache_key}"),
            ("DEBUG", "{service}", "Processing request {request_id}"),
            ("INFO", "{service}", "Health check passed"),
            ("WARN", "{service}", "Slow query detected: {query_time}ms"),
            ("INFO", "{service}", "Connection established to {host}:{port}"),
        ]
        self.error_templates = [
            ("ERROR", "{service}", "Failed to connect to database: timeout after {timeout}s"),
            ("ERROR", "{service}", "Authentication failed for user {user_id}"),
            ("CRITICAL", "{service}", "Out of memory: {memory_used}MB / {memory_total}MB"),
            ("ERROR", "{service}", "Request failed with status {status_code}"),
            ("WARN", "{service}", "Rate limit exceeded for client {client_id}"),
            ("ERROR", "{service}", "Connection refused to {host}:{port}"),
        ]

    def _generate_value(self, var_type: str) -> str:
        """Generate realistic values for template variables."""
        generators = {
            "service": lambda: random.choice(self.services),
            "latency": lambda: str(random.randint(10, 500)),
            "user_id": lambda: f"user_{random.randint(1000, 9999)}",
            "ip": lambda: f"{random.randint(1,255)}.{random.randint(0,255)}."
                          f"{random.randint(0,255)}.{random.randint(1,254)}",
            "cache_key": lambda: f"cache:{random.choice(['user', 'session', 'product'])}:"
                                  f"{random.randint(1, 1000)}",
            "request_id": lambda: hashlib.md5(str(random.random()).encode()).hexdigest()[:8],
            "query_time": lambda: str(random.randint(100, 5000)),
            "host": lambda: random.choice(["db-primary", "db-replica", "redis-1", "kafka-1"]),
            "port": lambda: str(random.choice([5432, 6379, 9092, 3306])),
            "timeout": lambda: str(random.randint(5, 30)),
            "status_code": lambda: str(random.choice([400, 401, 403, 404, 500, 502, 503])),
            "client_id": lambda: f"client_{random.randint(100, 999)}",
            "memory_used": lambda: str(random.randint(7000, 8000)),
            "memory_total": lambda: "8192",
        }
        return generators.get(var_type, lambda: "unknown")()

    def _fill_template(self, template: str) -> Tuple[str, Dict[str, str]]:
        """Fill template variables with generated values."""
        variables = {}
        result = template

        # Find all {var} patterns
        var_pattern = r'\{(\w+)\}'
        matches = re.findall(var_pattern, template)

        for var_name in matches:
            value = self._generate_value(var_name)
            variables[var_name] = value
            result = result.replace(f"{{{var_name}}}", value, 1)

        return result, variables

    def generate_logs(
        self,
        count: int = 1000,
        error_rate: float = 0.05,
        anomaly_rate: float = 0.02,
        time_span_hours: int = 24
    ) -> List[LogEntry]:
        """Generate realistic log entries."""
        logs = []
        start_time = datetime.now() - timedelta(hours=time_span_hours)

        for i in range(count):
            # Determine log type
            if random.random() < anomaly_rate:
                # Anomaly: unusual pattern
                level = random.choice(["ERROR", "CRITICAL"])
                source = random.choice(self.services)
                message = f"ANOMALY_{random.randint(1000, 9999)}: Unexpected state detected"
                variables = {}
            elif random.random() < error_rate:
                # Error log
                level, source_tmpl, msg_tmpl = random.choice(self.error_templates)
                source, _ = self._fill_template(source_tmpl)
                message, variables = self._fill_template(msg_tmpl)
            else:
                # Normal log
                level, source_tmpl, msg_tmpl = random.choice(self.normal_templates)
                source, _ = self._fill_template(source_tmpl)
                message, variables = self._fill_template(msg_tmpl)

            # Generate timestamp with some clustering
            time_offset = timedelta(
                seconds=random.randint(0, time_span_hours * 3600)
            )
            timestamp = start_time + time_offset

            raw = f"[{timestamp.isoformat()}] [{level}] [{source}] {message}"

            logs.append(LogEntry(
                timestamp=timestamp.isoformat(),
                level=level,
                source=source,
                message=message,
                raw=raw,
                variables=variables
            ))

        # Sort by timestamp
        logs.sort(key=lambda x: x.timestamp)
        return logs


# =============================================================================
# Log Parser
# =============================================================================

class LogParser:
    """
    Intelligent log parser using pattern matching and template extraction.
    Based on the Drain algorithm concept.
    """

    def __init__(self, similarity_threshold: float = 0.5):
        self.similarity_threshold = similarity_threshold
        self.templates: Dict[str, LogTemplate] = {}
        self.parsed_count = 0

        # Common log patterns
        self.patterns = [
            # ISO timestamp
            (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '<TIMESTAMP>'),
            # IP addresses
            (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>'),
            # UUIDs
            (r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '<UUID>'),
            # Hex strings (8+ chars)
            (r'\b[a-f0-9]{8,}\b', '<HEX>'),
            # Numbers
            (r'\b\d+\b', '<NUM>'),
            # User IDs
            (r'user_\d+', '<USER_ID>'),
            # Client IDs
            (r'client_\d+', '<CLIENT_ID>'),
        ]

    def _normalize_message(self, message: str) -> str:
        """Normalize message by replacing variables with placeholders."""
        normalized = message
        for pattern, placeholder in self.patterns:
            normalized = re.sub(pattern, placeholder, normalized)
        return normalized

    def _calculate_similarity(self, template: str, normalized: str) -> float:
        """Calculate similarity between template and normalized message."""
        template_tokens = template.split()
        message_tokens = normalized.split()

        if len(template_tokens) != len(message_tokens):
            return 0.0

        matches = sum(1 for t, m in zip(template_tokens, message_tokens)
                     if t == m or t.startswith('<'))
        return matches / len(template_tokens)

    def _generate_template_id(self, template: str) -> str:
        """Generate unique template ID."""
        return hashlib.md5(template.encode()).hexdigest()[:12]

    def parse(self, log_entry: LogEntry) -> LogEntry:
        """Parse a log entry and extract/match template."""
        normalized = self._normalize_message(log_entry.message)

        # Try to match existing template
        best_match = None
        best_similarity = 0.0

        for template_id, template in self.templates.items():
            similarity = self._calculate_similarity(template.pattern, normalized)
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = template

        if best_match:
            # Update existing template
            best_match.count += 1
            best_match.last_seen = log_entry.timestamp
            log_entry.template = best_match.template_id
        else:
            # Create new template
            template_id = self._generate_template_id(normalized)
            new_template = LogTemplate(
                template_id=template_id,
                pattern=normalized,
                count=1,
                first_seen=log_entry.timestamp,
                last_seen=log_entry.timestamp,
                example=log_entry.message
            )
            self.templates[template_id] = new_template
            log_entry.template = template_id

        self.parsed_count += 1
        return log_entry

    def parse_batch(self, logs: List[LogEntry]) -> List[LogEntry]:
        """Parse a batch of log entries."""
        return [self.parse(log) for log in logs]

    def get_template_stats(self) -> Dict[str, Any]:
        """Get template statistics."""
        if not self.templates:
            return {"status": "no_templates"}

        counts = [t.count for t in self.templates.values()]
        return {
            "total_templates": len(self.templates),
            "total_logs_parsed": self.parsed_count,
            "avg_logs_per_template": round(sum(counts) / len(counts), 2),
            "max_template_count": max(counts),
            "min_template_count": min(counts),
            "top_templates": sorted(
                [(t.template_id, t.count, t.pattern[:50])
                 for t in self.templates.values()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


# =============================================================================
# Log Anomaly Detector
# =============================================================================

class LogAnomalyDetector:
    """
    Detects anomalies in log streams using multiple methods:
    - Frequency analysis
    - Sequence analysis
    - Content analysis
    - New pattern detection
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.template_counts: Dict[str, List[int]] = defaultdict(list)
        self.recent_templates: List[str] = []
        self.known_sequences: Set[Tuple[str, ...]] = set()
        self.sequence_length = 3
        self.anomalies: List[LogAnomaly] = []

    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID."""
        return f"ANM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    def _detect_frequency_anomaly(
        self,
        template_id: str,
        count: int,
        threshold_std: float = 3.0
    ) -> Optional[LogAnomaly]:
        """Detect if template frequency is anomalous."""
        history = self.template_counts.get(template_id, [])

        if len(history) < 10:
            return None

        mean = sum(history) / len(history)
        if mean == 0:
            return None

        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std = math.sqrt(variance) if variance > 0 else 1

        z_score = (count - mean) / std if std > 0 else 0

        if abs(z_score) > threshold_std:
            direction = "spike" if z_score > 0 else "drop"
            return LogAnomaly(
                anomaly_id=self._generate_anomaly_id(),
                timestamp=datetime.now().isoformat(),
                anomaly_type=AnomalyType.FREQUENCY.value,
                severity="high" if abs(z_score) > 5 else "medium",
                description=f"Frequency {direction} for template {template_id[:8]}",
                evidence=[
                    f"Current count: {count}",
                    f"Historical mean: {mean:.1f}",
                    f"Z-score: {z_score:.2f}"
                ],
                confidence=min(0.99, 0.5 + abs(z_score) / 10)
            )
        return None

    def _detect_sequence_anomaly(
        self,
        template_ids: List[str]
    ) -> Optional[LogAnomaly]:
        """Detect if log sequence is anomalous."""
        if len(template_ids) < self.sequence_length:
            return None

        current_sequence = tuple(template_ids[-self.sequence_length:])

        # Check if sequence is known
        if current_sequence not in self.known_sequences:
            if len(self.known_sequences) > 100:  # Have enough history
                return LogAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    timestamp=datetime.now().isoformat(),
                    anomaly_type=AnomalyType.SEQUENCE.value,
                    severity="medium",
                    description="Unusual log sequence detected",
                    evidence=[
                        f"Sequence: {' -> '.join(s[:8] for s in current_sequence)}",
                        f"Known sequences: {len(self.known_sequences)}"
                    ],
                    confidence=0.7
                )

        # Learn sequence
        self.known_sequences.add(current_sequence)
        return None

    def _detect_new_pattern(
        self,
        log: LogEntry,
        parser: LogParser
    ) -> Optional[LogAnomaly]:
        """Detect if this is a never-before-seen pattern."""
        if log.template and log.template in parser.templates:
            template = parser.templates[log.template]
            if template.count == 1:  # First occurrence
                return LogAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    timestamp=log.timestamp,
                    anomaly_type=AnomalyType.NEW_PATTERN.value,
                    severity="low",
                    description="New log pattern detected",
                    evidence=[
                        f"Pattern: {template.pattern[:60]}",
                        f"Example: {log.message[:60]}"
                    ],
                    confidence=0.6,
                    affected_logs=[log.raw[:100]]
                )
        return None

    def analyze(
        self,
        logs: List[LogEntry],
        parser: LogParser
    ) -> List[LogAnomaly]:
        """Analyze logs for anomalies."""
        anomalies = []

        # Count templates in this batch
        batch_counts: Dict[str, int] = Counter()
        template_sequence = []

        for log in logs:
            if log.template:
                batch_counts[log.template] += 1
                template_sequence.append(log.template)

                # Check for new pattern
                new_pattern = self._detect_new_pattern(log, parser)
                if new_pattern:
                    anomalies.append(new_pattern)

        # Check frequency anomalies
        for template_id, count in batch_counts.items():
            freq_anomaly = self._detect_frequency_anomaly(template_id, count)
            if freq_anomaly:
                anomalies.append(freq_anomaly)

            # Update history
            self.template_counts[template_id].append(count)
            if len(self.template_counts[template_id]) > self.window_size:
                self.template_counts[template_id] = \
                    self.template_counts[template_id][-self.window_size:]

        # Check sequence anomalies (sample every 10 logs)
        # Only check if we have enough logs for a valid sequence
        if len(template_sequence) >= self.sequence_length:
            for i in range(0, len(template_sequence) - self.sequence_length + 1, 10):
                end_idx = min(i + self.sequence_length, len(template_sequence))
                seq_anomaly = self._detect_sequence_anomaly(
                    template_sequence[i:end_idx]
                )
                if seq_anomaly:
                    anomalies.append(seq_anomaly)

        self.anomalies.extend(anomalies)
        return anomalies

    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get summary of detected anomalies."""
        if not self.anomalies:
            return {"status": "no_anomalies"}

        by_type = Counter(a.anomaly_type for a in self.anomalies)
        by_severity = Counter(a.severity for a in self.anomalies)

        return {
            "total_anomalies": len(self.anomalies),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "known_sequences": len(self.known_sequences),
            "recent": [a.to_dict() for a in self.anomalies[-5:]]
        }


# =============================================================================
# Root Cause Analyzer
# =============================================================================

class RootCauseAnalyzer:
    """
    AI-powered root cause analysis for incidents.
    Correlates logs, metrics, and events to identify root causes.
    """

    def __init__(self):
        self.incident_patterns = {
            "database_timeout": {
                "symptoms": ["timeout", "connection refused", "database"],
                "root_causes": ["Database overload", "Network issues", "Connection pool exhausted"],
                "fixes": ["Scale database", "Check network", "Increase connection pool"]
            },
            "memory_pressure": {
                "symptoms": ["out of memory", "oom", "memory"],
                "root_causes": ["Memory leak", "Traffic spike", "Undersized instances"],
                "fixes": ["Restart service", "Scale horizontally", "Increase memory limits"]
            },
            "auth_failure": {
                "symptoms": ["authentication failed", "unauthorized", "401"],
                "root_causes": ["Invalid credentials", "Token expired", "Service misconfiguration"],
                "fixes": ["Refresh credentials", "Check auth service", "Verify configuration"]
            },
            "rate_limiting": {
                "symptoms": ["rate limit", "429", "throttle"],
                "root_causes": ["Traffic spike", "Client misconfiguration", "DDoS attack"],
                "fixes": ["Increase rate limits", "Enable caching", "Block suspicious IPs"]
            },
            "service_unavailable": {
                "symptoms": ["503", "service unavailable", "connection refused"],
                "root_causes": ["Service crashed", "Deployment issue", "Dependency failure"],
                "fixes": ["Restart service", "Rollback deployment", "Check dependencies"]
            }
        }

    def _match_pattern(self, logs: List[LogEntry]) -> Tuple[str, float]:
        """Match logs to known incident patterns."""
        if not logs:
            return (None, 0.0)

        all_text = " ".join(log.message.lower() for log in logs)

        best_match = None
        best_score = 0.0

        for pattern_name, pattern in self.incident_patterns.items():
            symptoms = pattern.get("symptoms", [])
            if not symptoms:
                continue
            score = sum(1 for symptom in symptoms if symptom in all_text)
            score = score / len(symptoms)

            if score > best_score:
                best_score = score
                best_match = pattern_name

        return best_match, best_score

    def _build_causal_chain(
        self,
        pattern_name: str,
        logs: List[LogEntry]
    ) -> List[str]:
        """Build causal chain from logs."""
        chain = []

        # Sort logs by timestamp
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)

        # Extract key events
        error_logs = [l for l in sorted_logs if l.level in ["ERROR", "CRITICAL"]]
        warn_logs = [l for l in sorted_logs if l.level == "WARN"]

        if warn_logs:
            chain.append(f"Warning signs: {warn_logs[0].message[:50]}")

        if error_logs:
            chain.append(f"Error occurred: {error_logs[0].message[:50]}")

        if len(error_logs) > 1:
            chain.append(f"Error propagated: {len(error_logs)} errors in cascade")

        chain.append(f"Pattern identified: {pattern_name.replace('_', ' ').title()}")

        return chain

    def analyze(
        self,
        incident: Incident,
        logs: List[LogEntry],
        metrics: Optional[Dict[str, List[float]]] = None
    ) -> RootCauseResult:
        """Perform root cause analysis on an incident."""
        # Match to known pattern
        pattern_name, confidence = self._match_pattern(logs)

        if pattern_name and confidence > 0.3:
            pattern = self.incident_patterns[pattern_name]
            root_cause = pattern["root_causes"][0]
            contributing = pattern["root_causes"][1:] if len(pattern["root_causes"]) > 1 else []
            fix = pattern["fixes"][0]
        else:
            root_cause = "Unknown - requires manual investigation"
            contributing = []
            fix = "Escalate to engineering team"
            confidence = 0.3

        # Build causal chain
        causal_chain = self._build_causal_chain(pattern_name or "unknown", logs)

        # Gather evidence
        def safe_timestamp(ts: str) -> str:
            """Extract datetime portion safely from various timestamp formats."""
            # Remove timezone suffix if present
            clean = ts.replace("Z", "").split("+")[0].split("-05")[0].split("-04")[0]
            return clean[:19] if len(clean) >= 19 else clean

        evidence = {
            "error_count": sum(1 for l in logs if l.level in ["ERROR", "CRITICAL"]),
            "services_affected": list(set(l.source for l in logs)),
            "time_range": f"{safe_timestamp(logs[0].timestamp)} to {safe_timestamp(logs[-1].timestamp)}" if logs else "N/A",
            "pattern_match": pattern_name or "none"
        }

        if metrics:
            for metric_name, values in metrics.items():
                if values:
                    evidence[f"{metric_name}_avg"] = round(sum(values) / len(values), 2)

        return RootCauseResult(
            incident_id=incident.incident_id,
            root_cause=root_cause,
            causal_chain=causal_chain,
            contributing_factors=contributing,
            confidence=round(confidence, 2),
            evidence=evidence,
            recommended_fix=fix,
            timestamp=datetime.now().isoformat()
        )


# =============================================================================
# Incident Response Automator
# =============================================================================

class IncidentResponder:
    """
    Automated incident response with configurable trust levels.
    """

    def __init__(self, trust_level: RemediationLevel = RemediationLevel.SUGGEST):
        self.trust_level = trust_level
        self.remediation_history: List[Dict] = []
        self.runbooks = {
            "restart_service": RemediationAction(
                action_id="restart_001",
                action_type="restart",
                description="Restart the affected service",
                command="kubectl rollout restart deployment/{service}",
                risk_level="low",
                requires_approval=False,
                estimated_impact="30s downtime",
                rollback_command=None
            ),
            "scale_up": RemediationAction(
                action_id="scale_001",
                action_type="scale",
                description="Scale up service replicas",
                command="kubectl scale deployment/{service} --replicas={replicas}",
                risk_level="low",
                requires_approval=False,
                estimated_impact="2-3 min for new pods",
                rollback_command="kubectl scale deployment/{service} --replicas={original}"
            ),
            "rollback": RemediationAction(
                action_id="rollback_001",
                action_type="rollback",
                description="Rollback to previous deployment",
                command="kubectl rollout undo deployment/{service}",
                risk_level="medium",
                requires_approval=True,
                estimated_impact="1-2 min, potential data issues",
                rollback_command="kubectl rollout undo deployment/{service}"
            ),
            "clear_cache": RemediationAction(
                action_id="cache_001",
                action_type="cache",
                description="Clear application cache",
                command="redis-cli FLUSHDB",
                risk_level="low",
                requires_approval=False,
                estimated_impact="Temporary latency increase",
                rollback_command=None
            ),
            "increase_resources": RemediationAction(
                action_id="resource_001",
                action_type="resource",
                description="Increase memory/CPU limits",
                command="kubectl set resources deployment/{service} --limits=memory={memory}",
                risk_level="low",
                requires_approval=False,
                estimated_impact="Pod restart required",
                rollback_command="kubectl set resources deployment/{service} --limits=memory={original}"
            )
        }

    def _select_remediation(
        self,
        rca_result: RootCauseResult
    ) -> Optional[RemediationAction]:
        """Select appropriate remediation based on root cause."""
        root_cause_lower = rca_result.root_cause.lower()

        if "memory" in root_cause_lower or "oom" in root_cause_lower:
            return self.runbooks["increase_resources"]
        elif "overload" in root_cause_lower or "spike" in root_cause_lower:
            return self.runbooks["scale_up"]
        elif "crash" in root_cause_lower:
            return self.runbooks["restart_service"]
        elif "deployment" in root_cause_lower:
            return self.runbooks["rollback"]
        elif "cache" in root_cause_lower:
            return self.runbooks["clear_cache"]

        return None

    def respond(
        self,
        incident: Incident,
        rca_result: RootCauseResult
    ) -> Dict[str, Any]:
        """Generate incident response based on RCA and trust level."""
        remediation = self._select_remediation(rca_result)

        response = {
            "incident_id": incident.incident_id,
            "timestamp": datetime.now().isoformat(),
            "trust_level": self.trust_level.name,
            "rca_confidence": rca_result.confidence,
            "recommended_action": None,
            "action_taken": None,
            "requires_approval": True,
            "status": "pending"
        }

        if not remediation:
            response["status"] = "no_automated_remediation"
            response["message"] = "No automated remediation available. Escalating to human."
            return response

        response["recommended_action"] = remediation.to_dict()

        # Determine action based on trust level
        if self.trust_level == RemediationLevel.ALERT_ONLY:
            response["status"] = "alert_sent"
            response["message"] = "Alert sent. Manual intervention required."

        elif self.trust_level == RemediationLevel.SUGGEST:
            response["status"] = "suggestion_ready"
            response["message"] = f"Suggested action: {remediation.description}"

        elif self.trust_level == RemediationLevel.APPROVE:
            response["status"] = "awaiting_approval"
            response["message"] = "Remediation prepared. Awaiting human approval."
            response["approval_command"] = f"approve {incident.incident_id}"

        elif self.trust_level.value >= RemediationLevel.AUTO_LOW_RISK.value:
            if remediation.risk_level == "low" or \
               self.trust_level == RemediationLevel.AUTO_HIGH_RISK:

                if rca_result.confidence >= 0.7:
                    response["status"] = "auto_remediated"
                    response["action_taken"] = remediation.to_dict()
                    response["message"] = f"Auto-remediation executed: {remediation.description}"
                    response["requires_approval"] = False

                    # Record remediation
                    self.remediation_history.append({
                        "incident_id": incident.incident_id,
                        "action": remediation.action_type,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    })
                else:
                    response["status"] = "confidence_too_low"
                    response["message"] = f"RCA confidence {rca_result.confidence} below threshold"
            else:
                response["status"] = "risk_too_high"
                response["message"] = f"Action risk '{remediation.risk_level}' exceeds trust level"

        return response

    def get_response_stats(self) -> Dict[str, Any]:
        """Get incident response statistics."""
        if not self.remediation_history:
            return {"status": "no_remediations"}

        successful = sum(1 for r in self.remediation_history if r["success"])

        return {
            "total_remediations": len(self.remediation_history),
            "successful": successful,
            "success_rate": f"{successful / len(self.remediation_history) * 100:.1f}%",
            "trust_level": self.trust_level.name,
            "recent": self.remediation_history[-5:]
        }


# =============================================================================
# Full AIOps Pipeline
# =============================================================================

class AIOPsPipeline:
    """
    Complete AIOps pipeline integrating all components.
    """

    def __init__(self, trust_level: RemediationLevel = RemediationLevel.SUGGEST):
        self.parser = LogParser()
        self.anomaly_detector = LogAnomalyDetector()
        self.rca_analyzer = RootCauseAnalyzer()
        self.responder = IncidentResponder(trust_level)

        self.incidents: List[Incident] = []
        self.processed_logs = 0

    def _create_incident(
        self,
        anomalies: List[LogAnomaly],
        logs: List[LogEntry]
    ) -> Optional[Incident]:
        """Create incident from anomalies."""
        if not anomalies:
            return None

        # Determine severity based on anomalies
        severities = [a.severity for a in anomalies]
        if "critical" in severities or "high" in severities:
            severity = IncidentSeverity.HIGH.value
        elif "medium" in severities:
            severity = IncidentSeverity.MEDIUM.value
        else:
            severity = IncidentSeverity.LOW.value

        incident = Incident(
            incident_id=f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            title=f"Multiple anomalies detected: {anomalies[0].description[:50]}",
            severity=severity,
            status="open",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            logs=[l.raw[:100] for l in logs[:10]]
        )

        self.incidents.append(incident)
        return incident

    def process(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Process logs through the full AIOps pipeline."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "logs_processed": len(logs),
            "parsing": {},
            "anomalies": {},
            "incidents": [],
            "responses": []
        }

        # Step 1: Parse logs
        parsed_logs = self.parser.parse_batch(logs)
        results["parsing"] = self.parser.get_template_stats()

        # Step 2: Detect anomalies
        anomalies = self.anomaly_detector.analyze(parsed_logs, self.parser)
        results["anomalies"] = self.anomaly_detector.get_anomaly_summary()

        # Step 3: Create incidents if needed
        if anomalies:
            incident = self._create_incident(anomalies, parsed_logs)
            if incident:
                results["incidents"].append(incident.to_dict())

                # Step 4: Root cause analysis
                error_logs = [l for l in parsed_logs
                             if l.level in ["ERROR", "CRITICAL", "WARN"]]
                rca = self.rca_analyzer.analyze(incident, error_logs)
                incident.root_cause = rca.root_cause

                results["rca"] = rca.to_dict()

                # Step 5: Automated response
                response = self.responder.respond(incident, rca)
                results["responses"].append(response)

        self.processed_logs += len(logs)
        return results

    def get_dashboard(self) -> Dict[str, Any]:
        """Get AIOps dashboard summary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "pipeline_stats": {
                "total_logs_processed": self.processed_logs,
                "total_incidents": len(self.incidents),
                "open_incidents": sum(1 for i in self.incidents if i.status == "open")
            },
            "parser_stats": self.parser.get_template_stats(),
            "anomaly_stats": self.anomaly_detector.get_anomaly_summary(),
            "response_stats": self.responder.get_response_stats()
        }


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_log_parsing():
    """
    Demo 1: Log Parsing and Template Extraction

    Demonstrates intelligent log parsing using pattern matching.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: Intelligent Log Parsing")
    print("=" * 70)

    parser = LogParser()
    generator = LogGenerator(seed=42)

    # Generate sample logs
    print("\n📝 Generating 500 sample logs...")
    logs = generator.generate_logs(count=500, error_rate=0.1)
    print(f"  Generated {len(logs)} logs")

    # Parse logs
    print("\n🔍 Parsing logs and extracting templates...")
    parsed = parser.parse_batch(logs)

    # Show template statistics
    print("\n" + "-" * 40)
    print("📊 Template Statistics")
    print("-" * 40)

    stats = parser.get_template_stats()
    print(f"\n  Total Templates Extracted: {stats['total_templates']}")
    print(f"  Total Logs Parsed: {stats['total_logs_parsed']}")
    print(f"  Avg Logs per Template: {stats['avg_logs_per_template']}")

    # Show top templates
    print("\n" + "-" * 40)
    print("📋 Top 5 Log Templates")
    print("-" * 40)

    for template_id, count, pattern in stats["top_templates"]:
        print(f"\n  Template: {template_id}")
        print(f"  Count: {count}")
        print(f"  Pattern: {pattern}...")

    # Show sample parsed logs
    print("\n" + "-" * 40)
    print("📝 Sample Parsed Logs")
    print("-" * 40)

    for log in parsed[:5]:
        print(f"\n  Raw: {log.raw[:60]}...")
        print(f"  Level: {log.level}")
        print(f"  Source: {log.source}")
        print(f"  Template: {log.template}")

    print("\n✅ Demo 1 Complete: Log parsing with template extraction")


def demo_2_anomaly_detection():
    """
    Demo 2: Log Anomaly Detection

    Demonstrates multi-method anomaly detection in log streams.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Log Anomaly Detection")
    print("=" * 70)

    parser = LogParser()
    detector = LogAnomalyDetector()
    generator = LogGenerator(seed=123)

    # Generate logs with anomalies
    print("\n📝 Generating logs with embedded anomalies...")
    logs = generator.generate_logs(
        count=1000,
        error_rate=0.05,
        anomaly_rate=0.03
    )
    print(f"  Generated {len(logs)} logs")

    # Parse and analyze in batches
    print("\n🔍 Analyzing logs for anomalies...")
    batch_size = 100
    all_anomalies = []

    for i in range(0, len(logs), batch_size):
        batch = logs[i:i + batch_size]
        parsed = parser.parse_batch(batch)
        anomalies = detector.analyze(parsed, parser)
        all_anomalies.extend(anomalies)

    # Show anomaly summary
    print("\n" + "-" * 40)
    print("📊 Anomaly Detection Summary")
    print("-" * 40)

    summary = detector.get_anomaly_summary()
    print(f"\n  Total Anomalies Detected: {summary['total_anomalies']}")

    if "by_type" in summary:
        print("\n  By Type:")
        for atype, count in summary["by_type"].items():
            print(f"    {atype}: {count}")

    if "by_severity" in summary:
        print("\n  By Severity:")
        for severity, count in summary["by_severity"].items():
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            print(f"    {icon} {severity}: {count}")

    # Show sample anomalies
    print("\n" + "-" * 40)
    print("🚨 Sample Anomalies")
    print("-" * 40)

    for anomaly in all_anomalies[:5]:
        print(f"\n  [{anomaly.severity.upper()}] {anomaly.anomaly_type}")
        print(f"  Description: {anomaly.description}")
        print(f"  Confidence: {anomaly.confidence:.1%}")
        print(f"  Evidence: {anomaly.evidence[0] if anomaly.evidence else 'N/A'}")

    print("\n✅ Demo 2 Complete: Multi-method anomaly detection")


def demo_3_root_cause_analysis():
    """
    Demo 3: AI-Powered Root Cause Analysis

    Demonstrates automated root cause analysis for incidents.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Root Cause Analysis")
    print("=" * 70)

    analyzer = RootCauseAnalyzer()
    generator = LogGenerator(seed=456)

    # Simulate different incident scenarios
    scenarios = [
        {
            "name": "Database Timeout",
            "error_templates": [
                ("ERROR", "db-service", "Connection timeout after 30s"),
                ("ERROR", "api-gateway", "Request failed: database unavailable"),
                ("WARN", "db-service", "Connection pool exhausted"),
            ]
        },
        {
            "name": "Memory Pressure",
            "error_templates": [
                ("CRITICAL", "user-service", "Out of memory: 7800MB / 8192MB"),
                ("ERROR", "user-service", "Request processing failed: OOM"),
                ("WARN", "user-service", "Memory usage at 95%"),
            ]
        },
        {
            "name": "Service Crash",
            "error_templates": [
                ("CRITICAL", "payment-service", "Service unavailable"),
                ("ERROR", "api-gateway", "Connection refused to payment-service:8080"),
                ("WARN", "payment-service", "Health check failed"),
            ]
        }
    ]

    for scenario in scenarios:
        print(f"\n" + "-" * 40)
        print(f"🔬 Scenario: {scenario['name']}")
        print("-" * 40)

        # Generate incident logs
        logs = []
        base_time = datetime.now() - timedelta(minutes=30)

        for i, (level, source, message) in enumerate(scenario["error_templates"]):
            timestamp = base_time + timedelta(minutes=i * 5)
            logs.append(LogEntry(
                timestamp=timestamp.isoformat(),
                level=level,
                source=source,
                message=message,
                raw=f"[{timestamp.isoformat()}] [{level}] [{source}] {message}"
            ))

        # Create incident
        incident = Incident(
            incident_id=f"INC-{random.randint(1000, 9999)}",
            title=scenario["name"],
            severity="high",
            status="open",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Run RCA
        rca = analyzer.analyze(incident, logs)

        print(f"\n  🎯 Root Cause: {rca.root_cause}")
        print(f"  📊 Confidence: {rca.confidence:.0%}")

        print(f"\n  📋 Causal Chain:")
        for i, step in enumerate(rca.causal_chain, 1):
            print(f"    {i}. {step}")

        if rca.contributing_factors:
            print(f"\n  ⚠️ Contributing Factors:")
            for factor in rca.contributing_factors:
                print(f"    • {factor}")

        print(f"\n  🔧 Recommended Fix: {rca.recommended_fix}")

    print("\n✅ Demo 3 Complete: AI-powered root cause analysis")


def demo_4_incident_response():
    """
    Demo 4: Automated Incident Response

    Demonstrates intelligent incident response at different trust levels.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Automated Incident Response")
    print("=" * 70)

    analyzer = RootCauseAnalyzer()

    # Test different trust levels
    trust_levels = [
        (RemediationLevel.ALERT_ONLY, "Alert Only"),
        (RemediationLevel.SUGGEST, "Suggest"),
        (RemediationLevel.APPROVE, "Approve Required"),
        (RemediationLevel.AUTO_LOW_RISK, "Auto (Low Risk)"),
    ]

    # Create a sample incident
    incident = Incident(
        incident_id="INC-2024-001",
        title="API Service Memory Pressure",
        severity="high",
        status="open",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )

    logs = [
        LogEntry(
            timestamp=datetime.now().isoformat(),
            level="CRITICAL",
            source="api-service",
            message="Out of memory: 7500MB / 8192MB",
            raw="[...] [CRITICAL] Out of memory"
        ),
        LogEntry(
            timestamp=datetime.now().isoformat(),
            level="ERROR",
            source="api-service",
            message="Request processing failed due to memory pressure",
            raw="[...] [ERROR] Request failed"
        )
    ]

    rca = analyzer.analyze(incident, logs)

    print(f"\n📋 Incident: {incident.title}")
    print(f"🎯 Root Cause: {rca.root_cause}")
    print(f"📊 RCA Confidence: {rca.confidence:.0%}")

    print("\n" + "-" * 40)
    print("Testing Different Trust Levels")
    print("-" * 40)

    for level, level_name in trust_levels:
        print(f"\n  {'='*30}")
        print(f"  Trust Level: {level_name}")
        print(f"  {'='*30}")

        responder = IncidentResponder(trust_level=level)
        response = responder.respond(incident, rca)

        status_icon = {
            "alert_sent": "📢",
            "suggestion_ready": "💡",
            "awaiting_approval": "⏳",
            "auto_remediated": "✅",
            "confidence_too_low": "❌",
            "risk_too_high": "⚠️"
        }.get(response["status"], "❓")

        print(f"\n  {status_icon} Status: {response['status']}")
        print(f"  📝 Message: {response['message']}")

        if response.get("recommended_action"):
            action = response["recommended_action"]
            print(f"  🔧 Action: {action['description']}")
            print(f"  ⚡ Command: {action['command']}")

    print("\n" + "-" * 40)
    print("💡 Trust Level Progression")
    print("-" * 40)
    print("""
  Level 0 (Alert Only):     Just notify, human does everything
  Level 1 (Suggest):        Analyze and suggest, human executes
  Level 2 (Approve):        Prepare fix, human approves, system executes
  Level 3 (Auto Low Risk):  Auto-execute low-risk fixes
  Level 4 (Auto High Risk): Auto-execute any fix (use carefully!)

  Recommendation: Start at Level 1, progress as trust builds.
    """)

    print("\n✅ Demo 4 Complete: Intelligent incident response")


def demo_5_full_pipeline():
    """
    Demo 5: Full AIOps Pipeline

    Demonstrates the complete integrated AIOps system.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Full AIOps Pipeline")
    print("=" * 70)

    pipeline = AIOPsPipeline(trust_level=RemediationLevel.AUTO_LOW_RISK)
    generator = LogGenerator(seed=789)

    print("\n🔧 Initializing AIOps Pipeline...")
    print("  Components:")
    print("    ✓ Log Parser (template extraction)")
    print("    ✓ Anomaly Detector (multi-method)")
    print("    ✓ Root Cause Analyzer (pattern matching)")
    print("    ✓ Incident Responder (auto-remediation)")

    # Process multiple batches
    print("\n📊 Processing log batches...")

    total_incidents = 0
    total_anomalies = 0

    for batch_num in range(3):
        print(f"\n  Batch {batch_num + 1}:")

        logs = generator.generate_logs(
            count=200,
            error_rate=0.1,
            anomaly_rate=0.05
        )

        result = pipeline.process(logs)

        anomaly_count = result["anomalies"].get("total_anomalies", 0)
        incident_count = len(result["incidents"])

        total_anomalies += anomaly_count
        total_incidents += incident_count

        print(f"    Logs: {result['logs_processed']}")
        print(f"    Templates: {result['parsing'].get('total_templates', 0)}")
        print(f"    Anomalies: {anomaly_count}")
        print(f"    Incidents: {incident_count}")

        if result.get("rca"):
            rca = result["rca"]
            print(f"    RCA: {rca['root_cause'][:40]}... ({rca['confidence']:.0%})")

        if result.get("responses"):
            for response in result["responses"]:
                print(f"    Response: {response['status']}")

    # Show dashboard
    print("\n" + "-" * 40)
    print("📊 AIOps Dashboard")
    print("-" * 40)

    dashboard = pipeline.get_dashboard()

    print(f"\n  Pipeline Stats:")
    print(f"    Total Logs Processed: {dashboard['pipeline_stats']['total_logs_processed']}")
    print(f"    Total Incidents: {dashboard['pipeline_stats']['total_incidents']}")
    print(f"    Open Incidents: {dashboard['pipeline_stats']['open_incidents']}")

    print(f"\n  Parser Stats:")
    print(f"    Templates: {dashboard['parser_stats'].get('total_templates', 0)}")

    print(f"\n  Anomaly Stats:")
    anomaly_stats = dashboard["anomaly_stats"]
    if "by_type" in anomaly_stats:
        for atype, count in anomaly_stats["by_type"].items():
            print(f"    {atype}: {count}")

    # Summary
    print("\n" + "-" * 40)
    print("💡 AIOps Pipeline Benefits")
    print("-" * 40)
    print(f"""
  Traditional Operations:
    • Manual log review
    • Slow incident detection
    • Time-consuming RCA
    • Reactive response

  AIOps Pipeline:
    • Automatic template extraction ({dashboard['parser_stats'].get('total_templates', 0)} templates)
    • Real-time anomaly detection ({total_anomalies} detected)
    • AI-powered root cause analysis
    • Automated incident response

  Result: Faster detection, faster resolution, less toil!
    """)

    print("\n✅ Demo 5 Complete: Full AIOps pipeline")


def print_usage():
    """Print usage information."""
    print("""
AIOps Toolkit - Module 54 Deliverable
=====================================

Usage:
    python deliverable_aiops_toolkit.py <demo>

Available Demos:
    demo1    Log parsing and template extraction
    demo2    Log anomaly detection
    demo3    Root cause analysis
    demo4    Automated incident response
    demo5    Full AIOps pipeline

Examples:
    python deliverable_aiops_toolkit.py demo1
    python deliverable_aiops_toolkit.py demo2
    python deliverable_aiops_toolkit.py demo3
    python deliverable_aiops_toolkit.py demo4
    python deliverable_aiops_toolkit.py demo5

Each demo demonstrates key AIOps concepts.
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo_1_log_parsing,
        "demo2": demo_2_anomaly_detection,
        "demo3": demo_3_root_cause_analysis,
        "demo4": demo_4_incident_response,
        "demo5": demo_5_full_pipeline,
    }

    if command in demos:
        print("\n🤖 AIOps Toolkit - Module 54")
        print("=" * 70)
        demos[command]()
        print("\n" + "=" * 70)
        print("🎉 Demo completed successfully!")
    elif command == "help":
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
