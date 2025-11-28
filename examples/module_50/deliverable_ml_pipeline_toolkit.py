#!/usr/bin/env python3
"""
ML Pipeline Orchestration Toolkit

A comprehensive toolkit demonstrating ML pipeline orchestration concepts
including DAGs, task execution, scheduling, retries, branching, and
parallel execution - simulating Airflow, Prefect, Dagster patterns.

Features:
- DAG (Directed Acyclic Graph) definition and execution
- Task dependencies and topological sorting
- Retry logic with exponential backoff
- Conditional branching based on results
- Parallel task execution
- Pipeline scheduling and triggers
- Execution history and logging

Author: Neural Dojo
Module: 50 - ML Pipeline & Workflow Orchestration
"""

import json
import time
import random
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Storage directory
PIPELINE_DIR = Path(".ml_pipeline_toolkit")
PIPELINE_DIR.mkdir(exist_ok=True)
(PIPELINE_DIR / "runs").mkdir(exist_ok=True)
(PIPELINE_DIR / "logs").mkdir(exist_ok=True)
(PIPELINE_DIR / "dags").mkdir(exist_ok=True)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"
    RETRYING = "retrying"


class TriggerRule(Enum):
    """When to trigger a task based on upstream status."""
    ALL_SUCCESS = "all_success"      # All upstream tasks succeeded
    ALL_FAILED = "all_failed"        # All upstream tasks failed
    ALL_DONE = "all_done"            # All upstream tasks completed (any status)
    ONE_SUCCESS = "one_success"      # At least one upstream succeeded
    ONE_FAILED = "one_failed"        # At least one upstream failed
    NONE_FAILED = "none_failed"      # No upstream tasks failed


@dataclass
class RetryPolicy:
    """Retry configuration for tasks."""
    max_retries: int = 3
    retry_delay_seconds: float = 60.0
    exponential_backoff: bool = True
    max_delay_seconds: float = 3600.0

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        if self.exponential_backoff:
            delay = self.retry_delay_seconds * (2 ** (attempt - 1))
            return min(delay, self.max_delay_seconds)
        return self.retry_delay_seconds


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    attempt: int = 1

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "attempt": self.attempt
        }


@dataclass
class Task:
    """
    A task in the pipeline.

    Similar to Airflow's BaseOperator or Prefect's @task.
    """
    task_id: str
    callable: Callable
    description: str = ""
    upstream: List[str] = field(default_factory=list)
    downstream: List[str] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    trigger_rule: TriggerRule = TriggerRule.ALL_SUCCESS
    timeout_seconds: float = 3600.0
    params: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.task_id)


@dataclass
class DAGRun:
    """A single execution of a DAG."""
    run_id: str
    dag_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "dag_id": self.dag_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "task_results": {k: v.to_dict() for k, v in self.task_results.items()},
            "config": self.config
        }


class DAG:
    """
    Directed Acyclic Graph for pipeline orchestration.

    Similar to Airflow's DAG class.
    """

    def __init__(
        self,
        dag_id: str,
        description: str = "",
        schedule_interval: Optional[str] = None,
        default_retry_policy: Optional[RetryPolicy] = None,
        max_parallel_tasks: int = 4,
        catchup: bool = False
    ):
        self.dag_id = dag_id
        self.description = description
        self.schedule_interval = schedule_interval
        self.default_retry_policy = default_retry_policy or RetryPolicy()
        self.max_parallel_tasks = max_parallel_tasks
        self.catchup = catchup
        self.tasks: Dict[str, Task] = {}
        self.runs: List[DAGRun] = []

    def add_task(self, task: Task) -> "DAG":
        """Add a task to the DAG."""
        self.tasks[task.task_id] = task
        return self

    def set_dependencies(self, upstream_id: str, downstream_id: str) -> "DAG":
        """Set dependency between tasks."""
        if upstream_id in self.tasks and downstream_id in self.tasks:
            self.tasks[upstream_id].downstream.append(downstream_id)
            self.tasks[downstream_id].upstream.append(upstream_id)
        return self

    def get_execution_order(self) -> List[List[str]]:
        """
        Get topologically sorted execution order.

        Returns list of task groups that can run in parallel.
        """
        # Calculate in-degrees
        in_degree = {task_id: len(task.upstream) for task_id, task in self.tasks.items()}

        # Start with tasks that have no dependencies
        ready = [task_id for task_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while ready:
            # All ready tasks can run in parallel
            execution_order.append(sorted(ready))

            next_ready = []
            for task_id in ready:
                for downstream_id in self.tasks[task_id].downstream:
                    in_degree[downstream_id] -= 1
                    if in_degree[downstream_id] == 0:
                        next_ready.append(downstream_id)

            ready = next_ready

        return execution_order

    def validate(self) -> List[str]:
        """Validate the DAG structure."""
        errors = []

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            for downstream_id in self.tasks[task_id].downstream:
                if downstream_id not in visited:
                    if has_cycle(downstream_id):
                        return True
                elif downstream_id in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    errors.append(f"Cycle detected in DAG starting from task '{task_id}'")

        # Check for missing dependencies
        for task_id, task in self.tasks.items():
            for upstream_id in task.upstream:
                if upstream_id not in self.tasks:
                    errors.append(f"Task '{task_id}' depends on missing task '{upstream_id}'")

        return errors

    def visualize(self) -> str:
        """Generate ASCII visualization of the DAG."""
        execution_order = self.get_execution_order()

        lines = [
            f"DAG: {self.dag_id}",
            f"Description: {self.description}",
            f"Schedule: {self.schedule_interval or 'Manual'}",
            f"Tasks: {len(self.tasks)}",
            "",
            "Execution Order:",
            "=" * 50
        ]

        for level, task_ids in enumerate(execution_order):
            lines.append(f"\nLevel {level}:")
            for task_id in task_ids:
                task = self.tasks[task_id]
                upstream = ", ".join(task.upstream) if task.upstream else "None"
                lines.append(f"  [{task_id}]")
                lines.append(f"    ↑ Depends on: {upstream}")
                if task.downstream:
                    downstream = ", ".join(task.downstream)
                    lines.append(f"    ↓ Triggers: {downstream}")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Convert DAG to dictionary for serialization."""
        return {
            "dag_id": self.dag_id,
            "description": self.description,
            "schedule_interval": self.schedule_interval,
            "max_parallel_tasks": self.max_parallel_tasks,
            "tasks": {
                task_id: {
                    "task_id": task.task_id,
                    "description": task.description,
                    "upstream": task.upstream,
                    "downstream": task.downstream,
                    "trigger_rule": task.trigger_rule.value,
                    "timeout_seconds": task.timeout_seconds
                }
                for task_id, task in self.tasks.items()
            }
        }


class PipelineExecutor:
    """
    Execute DAGs with proper dependency resolution.

    Handles retries, parallel execution, and result tracking.
    """

    def __init__(self, dag: DAG):
        self.dag = dag
        self.results: Dict[str, TaskResult] = {}
        self.lock = threading.Lock()

    def should_run_task(self, task: Task) -> bool:
        """Check if task should run based on upstream status and trigger rule."""
        if not task.upstream:
            return True

        upstream_statuses = [
            self.results.get(upstream_id, TaskResult(upstream_id, TaskStatus.PENDING)).status
            for upstream_id in task.upstream
        ]

        if task.trigger_rule == TriggerRule.ALL_SUCCESS:
            return all(s == TaskStatus.SUCCESS for s in upstream_statuses)
        elif task.trigger_rule == TriggerRule.ALL_FAILED:
            return all(s == TaskStatus.FAILED for s in upstream_statuses)
        elif task.trigger_rule == TriggerRule.ALL_DONE:
            return all(s in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.SKIPPED]
                      for s in upstream_statuses)
        elif task.trigger_rule == TriggerRule.ONE_SUCCESS:
            return any(s == TaskStatus.SUCCESS for s in upstream_statuses)
        elif task.trigger_rule == TriggerRule.ONE_FAILED:
            return any(s == TaskStatus.FAILED for s in upstream_statuses)
        elif task.trigger_rule == TriggerRule.NONE_FAILED:
            return not any(s == TaskStatus.FAILED for s in upstream_statuses)

        return False

    def execute_task(
        self,
        task: Task,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute a single task with retry logic."""
        result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now()
        )

        # Check if we should run based on trigger rule
        if not self.should_run_task(task):
            result.status = TaskStatus.SKIPPED
            result.end_time = datetime.now()
            return result

        attempt = 0
        last_error = None

        while attempt <= task.retry_policy.max_retries:
            attempt += 1
            result.attempt = attempt

            try:
                # Build task context
                task_context = {
                    **context,
                    "task_id": task.task_id,
                    "attempt": attempt,
                    "upstream_results": {
                        upstream_id: self.results.get(upstream_id)
                        for upstream_id in task.upstream
                    },
                    "params": task.params
                }

                # Execute the callable
                output = task.callable(task_context)

                result.status = TaskStatus.SUCCESS
                result.output = output
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - result.start_time).total_seconds()

                return result

            except Exception as e:
                last_error = str(e)

                if attempt <= task.retry_policy.max_retries:
                    delay = task.retry_policy.get_delay(attempt)
                    result.status = TaskStatus.RETRYING
                    print(f"    ⚠️ Task {task.task_id} failed (attempt {attempt}), retrying in {delay:.1f}s...")
                    time.sleep(min(delay, 2))  # Cap actual sleep for demo

        # All retries exhausted
        result.status = TaskStatus.FAILED
        result.error = last_error
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - result.start_time).total_seconds()

        return result

    def execute(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> DAGRun:
        """Execute the entire DAG."""
        run_id = f"{self.dag.dag_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        dag_run = DAGRun(
            run_id=run_id,
            dag_id=self.dag.dag_id,
            start_time=datetime.now(),
            config=config or {}
        )

        context = {
            "run_id": run_id,
            "dag_id": self.dag.dag_id,
            "execution_date": datetime.now(),
            "config": config or {}
        }

        execution_order = self.dag.get_execution_order()

        print(f"\n{'='*60}")
        print(f"Executing DAG: {self.dag.dag_id}")
        print(f"Run ID: {run_id}")
        print(f"{'='*60}")

        for level, task_ids in enumerate(execution_order):
            print(f"\n📊 Level {level}: {task_ids}")

            # Execute tasks at this level in parallel
            with ThreadPoolExecutor(max_workers=self.dag.max_parallel_tasks) as executor:
                future_to_task = {
                    executor.submit(
                        self.execute_task,
                        self.dag.tasks[task_id],
                        context
                    ): task_id
                    for task_id in task_ids
                }

                for future in as_completed(future_to_task):
                    task_id = future_to_task[future]
                    result = future.result()

                    with self.lock:
                        self.results[task_id] = result
                        dag_run.task_results[task_id] = result

                    status_icon = {
                        TaskStatus.SUCCESS: "✅",
                        TaskStatus.FAILED: "❌",
                        TaskStatus.SKIPPED: "⏭️",
                        TaskStatus.RETRYING: "🔄"
                    }.get(result.status, "❓")

                    print(f"  {status_icon} {task_id}: {result.status.value} "
                          f"({result.duration_seconds:.2f}s)")

                    if result.error:
                        print(f"      Error: {result.error}")

        # Determine overall DAG status
        failed_tasks = [
            task_id for task_id, result in dag_run.task_results.items()
            if result.status == TaskStatus.FAILED
        ]

        dag_run.end_time = datetime.now()
        dag_run.status = "failed" if failed_tasks else "success"

        # Save run to disk
        run_path = PIPELINE_DIR / "runs" / f"{run_id}.json"
        with open(run_path, "w") as f:
            json.dump(dag_run.to_dict(), f, indent=2, default=str)

        return dag_run


class PipelineScheduler:
    """
    Schedule and manage DAG executions.

    Simulates Airflow's scheduler functionality.
    """

    def __init__(self):
        self.dags: Dict[str, DAG] = {}
        self.schedules: Dict[str, Dict] = {}

    def register_dag(self, dag: DAG) -> None:
        """Register a DAG with the scheduler."""
        self.dags[dag.dag_id] = dag

        if dag.schedule_interval:
            self.schedules[dag.dag_id] = {
                "interval": dag.schedule_interval,
                "last_run": None,
                "next_run": self._calculate_next_run(dag.schedule_interval)
            }

        # Save DAG definition
        dag_path = PIPELINE_DIR / "dags" / f"{dag.dag_id}.json"
        with open(dag_path, "w") as f:
            json.dump(dag.to_dict(), f, indent=2)

    def _calculate_next_run(self, interval: str) -> datetime:
        """Calculate next run time based on interval."""
        now = datetime.now()

        if interval == "@daily":
            return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        elif interval == "@hourly":
            return (now + timedelta(hours=1)).replace(minute=0, second=0)
        elif interval == "@weekly":
            days_until_monday = (7 - now.weekday()) % 7 or 7
            return (now + timedelta(days=days_until_monday)).replace(hour=0, minute=0, second=0)
        else:
            # Default to next hour
            return now + timedelta(hours=1)

    def get_pending_runs(self) -> List[str]:
        """Get DAGs that are due to run."""
        now = datetime.now()
        pending = []

        for dag_id, schedule in self.schedules.items():
            if schedule["next_run"] and schedule["next_run"] <= now:
                pending.append(dag_id)

        return pending

    def trigger_dag(self, dag_id: str, config: Optional[Dict] = None) -> Optional[DAGRun]:
        """Manually trigger a DAG run."""
        if dag_id not in self.dags:
            print(f"❌ DAG '{dag_id}' not found")
            return None

        dag = self.dags[dag_id]
        executor = PipelineExecutor(dag)
        run = executor.execute(config)

        # Update schedule if applicable
        if dag_id in self.schedules:
            self.schedules[dag_id]["last_run"] = datetime.now()
            self.schedules[dag_id]["next_run"] = self._calculate_next_run(
                self.schedules[dag_id]["interval"]
            )

        return run

    def list_dags(self) -> None:
        """List all registered DAGs."""
        print("\n📋 Registered DAGs:")
        print("-" * 60)

        for dag_id, dag in self.dags.items():
            schedule = self.schedules.get(dag_id, {})
            interval = schedule.get("interval", "Manual")
            next_run = schedule.get("next_run", "N/A")

            print(f"\n  {dag_id}:")
            print(f"    Description: {dag.description}")
            print(f"    Tasks: {len(dag.tasks)}")
            print(f"    Schedule: {interval}")
            if isinstance(next_run, datetime):
                print(f"    Next Run: {next_run.strftime('%Y-%m-%d %H:%M')}")

    def get_run_history(self, dag_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get run history for DAGs."""
        runs_dir = PIPELINE_DIR / "runs"
        run_files = sorted(runs_dir.glob("*.json"), reverse=True)

        history = []
        for run_file in run_files[:limit]:
            with open(run_file) as f:
                run_data = json.load(f)

            if dag_id is None or run_data["dag_id"] == dag_id:
                history.append(run_data)

        return history


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo1_basic_dag():
    """
    Demo 1: Basic DAG with task dependencies.

    Shows how to create a simple ML pipeline DAG.
    """
    print("=" * 70)
    print("DEMO 1: BASIC DAG WITH TASK DEPENDENCIES")
    print("=" * 70)

    print("\n📋 DAG Concepts:")
    print("-" * 40)
    print("  • DAG = Directed Acyclic Graph")
    print("  • Tasks are nodes, dependencies are edges")
    print("  • No cycles allowed (acyclic)")
    print("  • Tasks run when all upstream tasks complete")

    # Define task functions
    def extract_data(context):
        """Extract data from source."""
        time.sleep(0.2)  # Simulate work
        return {"rows": 10000, "columns": 50}

    def validate_data(context):
        """Validate extracted data."""
        upstream = context["upstream_results"]["extract"].output
        time.sleep(0.1)
        if upstream["rows"] < 100:
            raise ValueError("Insufficient data!")
        return {"valid": True, "rows": upstream["rows"]}

    def feature_engineering(context):
        """Engineer features."""
        time.sleep(0.2)
        return {"features": 100, "method": "automatic"}

    def train_model(context):
        """Train ML model."""
        time.sleep(0.3)
        return {"accuracy": 0.92, "model_type": "xgboost"}

    def evaluate_model(context):
        """Evaluate model performance."""
        upstream = context["upstream_results"]["train"].output
        time.sleep(0.1)
        return {
            "accuracy": upstream["accuracy"],
            "passed_threshold": upstream["accuracy"] > 0.85
        }

    # Create DAG
    dag = DAG(
        dag_id="ml_training_pipeline",
        description="Daily ML model training pipeline",
        schedule_interval="@daily",
        max_parallel_tasks=2
    )

    # Add tasks
    dag.add_task(Task("extract", extract_data, "Extract data from database"))
    dag.add_task(Task("validate", validate_data, "Validate data quality"))
    dag.add_task(Task("features", feature_engineering, "Engineer features"))
    dag.add_task(Task("train", train_model, "Train ML model"))
    dag.add_task(Task("evaluate", evaluate_model, "Evaluate model"))

    # Set dependencies
    dag.set_dependencies("extract", "validate")
    dag.set_dependencies("validate", "features")
    dag.set_dependencies("features", "train")
    dag.set_dependencies("train", "evaluate")

    # Visualize
    print(f"\n{dag.visualize()}")

    # Validate
    errors = dag.validate()
    if errors:
        print(f"\n❌ Validation errors: {errors}")
    else:
        print("\n✅ DAG validation passed!")

    # Execute
    executor = PipelineExecutor(dag)
    run = executor.execute()

    # Summary
    print(f"\n{'='*60}")
    print("📊 Execution Summary:")
    print(f"  Status: {run.status.upper()}")
    print(f"  Duration: {(run.end_time - run.start_time).total_seconds():.2f}s")
    print(f"  Tasks: {len(run.task_results)}")

    successful = sum(1 for r in run.task_results.values() if r.status == TaskStatus.SUCCESS)
    print(f"  Successful: {successful}/{len(run.task_results)}")

    print("\n✅ Demo 1 complete!")


def demo2_parallel_execution():
    """
    Demo 2: Parallel task execution.

    Shows how independent tasks run in parallel.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: PARALLEL TASK EXECUTION")
    print("=" * 70)

    print("\n📋 Parallel Execution Concepts:")
    print("-" * 40)
    print("  • Independent tasks run concurrently")
    print("  • Reduces total pipeline duration")
    print("  • Controlled by max_parallel_tasks")

    def fetch_source_a(context):
        """Fetch from source A."""
        time.sleep(0.5)
        return {"source": "A", "rows": 5000}

    def fetch_source_b(context):
        """Fetch from source B."""
        time.sleep(0.5)
        return {"source": "B", "rows": 3000}

    def fetch_source_c(context):
        """Fetch from source C."""
        time.sleep(0.5)
        return {"source": "C", "rows": 2000}

    def merge_data(context):
        """Merge all sources."""
        upstream = context["upstream_results"]
        total_rows = sum(
            r.output["rows"]
            for r in upstream.values()
            if r and r.output
        )
        time.sleep(0.2)
        return {"total_rows": total_rows, "sources": 3}

    def process_data(context):
        """Process merged data."""
        upstream = context["upstream_results"]["merge"].output
        time.sleep(0.3)
        return {"processed_rows": upstream["total_rows"], "status": "complete"}

    # Create DAG with parallel branches
    dag = DAG(
        dag_id="parallel_data_pipeline",
        description="Pipeline with parallel data fetching",
        max_parallel_tasks=3  # Allow 3 parallel tasks
    )

    # Add tasks
    dag.add_task(Task("fetch_a", fetch_source_a, "Fetch from source A"))
    dag.add_task(Task("fetch_b", fetch_source_b, "Fetch from source B"))
    dag.add_task(Task("fetch_c", fetch_source_c, "Fetch from source C"))
    dag.add_task(Task(
        "merge",
        merge_data,
        "Merge all sources",
        trigger_rule=TriggerRule.ALL_SUCCESS
    ))
    dag.add_task(Task("process", process_data, "Process merged data"))

    # Set dependencies - fetch tasks run in parallel, then merge
    dag.set_dependencies("fetch_a", "merge")
    dag.set_dependencies("fetch_b", "merge")
    dag.set_dependencies("fetch_c", "merge")
    dag.set_dependencies("merge", "process")

    print(f"\n{dag.visualize()}")

    print("\n📊 Expected Behavior:")
    print("  Level 0: fetch_a, fetch_b, fetch_c run in PARALLEL")
    print("  Level 1: merge waits for all fetches")
    print("  Level 2: process runs after merge")

    # Execute
    executor = PipelineExecutor(dag)
    run = executor.execute()

    # Summary
    total_duration = (run.end_time - run.start_time).total_seconds()
    sequential_duration = 0.5 * 3 + 0.2 + 0.3  # If run sequentially

    print(f"\n{'='*60}")
    print("📊 Parallel Execution Results:")
    print(f"  Actual duration: {total_duration:.2f}s")
    print(f"  Sequential would be: ~{sequential_duration:.2f}s")
    print(f"  Speedup: ~{sequential_duration/total_duration:.1f}x")

    print("\n✅ Demo 2 complete!")


def demo3_retry_and_failure():
    """
    Demo 3: Retry logic and failure handling.

    Shows exponential backoff retries and failure propagation.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: RETRY LOGIC AND FAILURE HANDLING")
    print("=" * 70)

    print("\n📋 Retry Concepts:")
    print("-" * 40)
    print("  • Automatic retries on failure")
    print("  • Exponential backoff between retries")
    print("  • Max retries limit")
    print("  • Failure propagation to downstream tasks")

    # Track attempts for flaky task
    attempt_counter = {"count": 0}

    def reliable_task(context):
        """Always succeeds."""
        time.sleep(0.1)
        return {"status": "success"}

    def flaky_task(context):
        """Fails first 2 attempts, succeeds on 3rd."""
        attempt_counter["count"] += 1
        attempt = attempt_counter["count"]

        if attempt < 3:
            raise Exception(f"Simulated failure (attempt {attempt})")

        time.sleep(0.1)
        return {"status": "recovered", "attempts": attempt}

    def downstream_task(context):
        """Runs after flaky task."""
        upstream = context["upstream_results"]["flaky"].output
        time.sleep(0.1)
        return {"upstream_status": upstream["status"]}

    # Create DAG
    dag = DAG(
        dag_id="retry_demo_pipeline",
        description="Pipeline demonstrating retry logic"
    )

    # Custom retry policy
    retry_policy = RetryPolicy(
        max_retries=3,
        retry_delay_seconds=1.0,
        exponential_backoff=True
    )

    dag.add_task(Task("reliable", reliable_task, "Always succeeds"))
    dag.add_task(Task(
        "flaky",
        flaky_task,
        "Fails then succeeds",
        retry_policy=retry_policy
    ))
    dag.add_task(Task("downstream", downstream_task, "Depends on flaky task"))

    dag.set_dependencies("reliable", "flaky")
    dag.set_dependencies("flaky", "downstream")

    print("\n📊 Retry Policy:")
    print(f"  Max retries: {retry_policy.max_retries}")
    print(f"  Initial delay: {retry_policy.retry_delay_seconds}s")
    print(f"  Exponential backoff: {retry_policy.exponential_backoff}")
    print("\n  Expected delays: 1s → 2s → 4s")

    # Execute
    executor = PipelineExecutor(dag)
    run = executor.execute()

    # Summary
    flaky_result = run.task_results["flaky"]
    print(f"\n{'='*60}")
    print("📊 Retry Results:")
    print(f"  Flaky task status: {flaky_result.status.value}")
    print(f"  Total attempts: {flaky_result.attempt}")
    print(f"  Downstream task: {run.task_results['downstream'].status.value}")

    print("\n✅ Demo 3 complete!")


def demo4_branching():
    """
    Demo 4: Conditional branching.

    Shows how to branch based on task results.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: CONDITIONAL BRANCHING")
    print("=" * 70)

    print("\n📋 Branching Concepts:")
    print("-" * 40)
    print("  • Branch based on upstream results")
    print("  • Different trigger rules for different paths")
    print("  • ONE_SUCCESS: Run if any upstream succeeds")
    print("  • ALL_SUCCESS: Run only if all upstream succeed")

    def train_model(context):
        """Train model and return metrics."""
        time.sleep(0.2)
        # Simulate good model
        accuracy = random.uniform(0.85, 0.98)
        return {"accuracy": accuracy, "model_path": "/models/v1"}

    def evaluate_model(context):
        """Evaluate and decide deployment path."""
        upstream = context["upstream_results"]["train"].output
        accuracy = upstream["accuracy"]
        time.sleep(0.1)
        return {
            "accuracy": accuracy,
            "deploy_production": accuracy > 0.92,
            "deploy_staging": 0.85 <= accuracy <= 0.92
        }

    def deploy_production(context):
        """Deploy to production."""
        upstream = context["upstream_results"]["evaluate"].output
        if not upstream["deploy_production"]:
            raise Exception("Accuracy too low for production")
        time.sleep(0.1)
        return {"deployed_to": "production"}

    def deploy_staging(context):
        """Deploy to staging."""
        upstream = context["upstream_results"]["evaluate"].output
        if not upstream["deploy_staging"]:
            raise Exception("Not suitable for staging")
        time.sleep(0.1)
        return {"deployed_to": "staging"}

    def notify_failure(context):
        """Send failure notification."""
        time.sleep(0.1)
        return {"notified": True, "message": "Model did not meet threshold"}

    def cleanup(context):
        """Cleanup after deployment."""
        time.sleep(0.1)
        return {"cleaned": True}

    # Create DAG
    dag = DAG(
        dag_id="branching_pipeline",
        description="Pipeline with conditional branching"
    )

    dag.add_task(Task("train", train_model, "Train ML model"))
    dag.add_task(Task("evaluate", evaluate_model, "Evaluate model"))
    dag.add_task(Task(
        "deploy_prod",
        deploy_production,
        "Deploy to production",
        trigger_rule=TriggerRule.ALL_SUCCESS
    ))
    dag.add_task(Task(
        "deploy_staging",
        deploy_staging,
        "Deploy to staging",
        trigger_rule=TriggerRule.ALL_SUCCESS
    ))
    dag.add_task(Task(
        "notify_failure",
        notify_failure,
        "Notify on failure",
        trigger_rule=TriggerRule.ONE_FAILED
    ))
    dag.add_task(Task(
        "cleanup",
        cleanup,
        "Cleanup resources",
        trigger_rule=TriggerRule.ALL_DONE
    ))

    # Set dependencies
    dag.set_dependencies("train", "evaluate")
    dag.set_dependencies("evaluate", "deploy_prod")
    dag.set_dependencies("evaluate", "deploy_staging")
    dag.set_dependencies("evaluate", "notify_failure")
    dag.set_dependencies("deploy_prod", "cleanup")
    dag.set_dependencies("deploy_staging", "cleanup")
    dag.set_dependencies("notify_failure", "cleanup")

    print(f"\n{dag.visualize()}")

    print("\n📊 Branching Logic:")
    print("  accuracy > 0.92  → deploy_production")
    print("  0.85 ≤ acc ≤ 0.92 → deploy_staging")
    print("  accuracy < 0.85  → notify_failure")
    print("  Always           → cleanup (trigger: ALL_DONE)")

    # Execute
    executor = PipelineExecutor(dag)
    run = executor.execute()

    # Summary
    eval_result = run.task_results["evaluate"].output
    print(f"\n{'='*60}")
    print("📊 Branching Results:")
    print(f"  Model accuracy: {eval_result['accuracy']:.2%}")

    for task_id in ["deploy_prod", "deploy_staging", "notify_failure", "cleanup"]:
        result = run.task_results[task_id]
        print(f"  {task_id}: {result.status.value}")

    print("\n✅ Demo 4 complete!")


def demo5_scheduler():
    """
    Demo 5: Pipeline scheduler and run history.

    Shows scheduling, triggering, and history tracking.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: PIPELINE SCHEDULER AND HISTORY")
    print("=" * 70)

    print("\n📋 Scheduler Concepts:")
    print("-" * 40)
    print("  • Register DAGs with scheduler")
    print("  • Schedule intervals (@daily, @hourly, etc.)")
    print("  • Manual triggers")
    print("  • Run history tracking")

    # Create scheduler
    scheduler = PipelineScheduler()

    # Define simple tasks
    def step1(context):
        return {"step": 1, "config": context.get("config", {})}

    def step2(context):
        return {"step": 2}

    def step3(context):
        return {"step": 3}

    # Create multiple DAGs
    dag1 = DAG(
        dag_id="daily_training",
        description="Daily model training",
        schedule_interval="@daily"
    )
    dag1.add_task(Task("step1", step1))
    dag1.add_task(Task("step2", step2))
    dag1.add_task(Task("step3", step3))
    dag1.set_dependencies("step1", "step2")
    dag1.set_dependencies("step2", "step3")

    dag2 = DAG(
        dag_id="hourly_inference",
        description="Hourly batch inference",
        schedule_interval="@hourly"
    )
    dag2.add_task(Task("infer", lambda ctx: {"predictions": 1000}))

    dag3 = DAG(
        dag_id="manual_retrain",
        description="Manual retraining pipeline"
    )
    dag3.add_task(Task("retrain", lambda ctx: {"retrained": True}))

    # Register DAGs
    scheduler.register_dag(dag1)
    scheduler.register_dag(dag2)
    scheduler.register_dag(dag3)

    # List registered DAGs
    scheduler.list_dags()

    # Trigger some runs
    print("\n📊 Triggering DAG Runs:")
    print("-" * 40)

    run1 = scheduler.trigger_dag("daily_training", {"param1": "value1"})
    run2 = scheduler.trigger_dag("hourly_inference")
    run3 = scheduler.trigger_dag("manual_retrain")

    # Get run history
    print("\n📜 Run History:")
    print("-" * 40)

    history = scheduler.get_run_history(limit=5)
    for run in history:
        status_icon = "✅" if run["status"] == "success" else "❌"
        print(f"  {status_icon} {run['run_id']}")
        print(f"      Status: {run['status']}")
        print(f"      Started: {run['start_time']}")
        tasks_success = sum(
            1 for t in run["task_results"].values()
            if t["status"] == "success"
        )
        print(f"      Tasks: {tasks_success}/{len(run['task_results'])} succeeded")

    # Show pending runs
    print("\n⏰ Pending Runs (scheduled):")
    print("-" * 40)
    for dag_id, schedule in scheduler.schedules.items():
        if schedule.get("next_run"):
            print(f"  {dag_id}: {schedule['next_run'].strftime('%Y-%m-%d %H:%M')}")

    print("\n✅ Demo 5 complete!")
    print(f"📂 Pipeline data saved to: {PIPELINE_DIR}")


def show_help():
    """Show help information."""
    help_text = """
ML Pipeline Orchestration Toolkit
=================================

A comprehensive toolkit demonstrating ML pipeline orchestration concepts.

Usage:
    python deliverable_ml_pipeline_toolkit.py <demo>

Available Demos:
    demo1   Basic DAG with task dependencies
    demo2   Parallel task execution
    demo3   Retry logic and failure handling
    demo4   Conditional branching
    demo5   Pipeline scheduler and history

Examples:
    python deliverable_ml_pipeline_toolkit.py demo1
    python deliverable_ml_pipeline_toolkit.py demo2
    python deliverable_ml_pipeline_toolkit.py demo5

Key Concepts:
    DAG             Directed Acyclic Graph defining workflow
    Task            Individual unit of work
    Dependency      Relationship between tasks
    Trigger Rule    When to run based on upstream status
    Retry Policy    How to handle failures
    Scheduler       Manage and trigger DAG runs

Simulated Tools:
    Airflow         Industry-standard orchestrator
    Prefect         Modern Python-native workflows
    Dagster         Asset-based pipelines
    Kubeflow        Kubernetes-native ML pipelines
    """
    print(help_text)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    demos = {
        "demo1": demo1_basic_dag,
        "demo2": demo2_parallel_execution,
        "demo3": demo3_retry_and_failure,
        "demo4": demo4_branching,
        "demo5": demo5_scheduler,
        "help": show_help,
        "--help": show_help,
        "-h": show_help
    }

    if command in demos:
        demos[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
