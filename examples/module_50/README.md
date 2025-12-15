# Module 50 Deliverable: ML Pipeline Orchestration Toolkit

**Comprehensive pipeline orchestration demonstrating DAGs, task execution, and workflow management.**

## Features

- **DAG Definition**: Create directed acyclic graphs for workflows
- **Task Dependencies**: Define and resolve task dependencies
- **Parallel Execution**: Run independent tasks concurrently
- **Retry Logic**: Exponential backoff and automatic retries
- **Conditional Branching**: Different paths based on results
- **Scheduling**: Schedule and trigger DAG runs
- **History Tracking**: Track execution history and metrics

## Quick Start

```bash
# Basic DAG with dependencies
python deliverable_ml_pipeline_toolkit.py demo1

# Parallel task execution
python deliverable_ml_pipeline_toolkit.py demo2

# Retry and failure handling
python deliverable_ml_pipeline_toolkit.py demo3

# Conditional branching
python deliverable_ml_pipeline_toolkit.py demo4

# Scheduler and history
python deliverable_ml_pipeline_toolkit.py demo5
```

## Core Concepts

### DAG (Directed Acyclic Graph)

```
┌─────────┐
│ extract │ Level 0
└────┬────┘
     │
     ▼
┌─────────┐
│validate │ Level 1
└────┬────┘
     │
     ▼
┌─────────┐
│features │ Level 2
└────┬────┘
     │
     ▼
┌─────────┐
│  train  │ Level 3
└────┬────┘
     │
     ▼
┌─────────┐
│evaluate │ Level 4
└─────────┘
```

### Parallel Execution (Demo 2)

```
┌─────────┐ ┌─────────┐ ┌─────────┐
│ fetch_a │ │ fetch_b │ │ fetch_c │  Level 0 (parallel)
└────┬────┘ └────┬────┘ └────┬────┘
     │          │          │
     └──────────┼──────────┘
                │
                ▼
          ┌─────────┐
          │  merge  │  Level 1
          └────┬────┘
               │
               ▼
          ┌─────────┐
          │ process │  Level 2
          └─────────┘

Speedup: ~2x with 3 parallel tasks
```

### Trigger Rules

| Rule | Description |
|------|-------------|
| ALL_SUCCESS | All upstream tasks succeeded |
| ALL_FAILED | All upstream tasks failed |
| ALL_DONE | All upstream tasks completed |
| ONE_SUCCESS | At least one succeeded |
| ONE_FAILED | At least one failed |
| NONE_FAILED | No upstream failed |

### Retry Policy

```python
RetryPolicy(
    max_retries=3,
    retry_delay_seconds=60.0,
    exponential_backoff=True,
    max_delay_seconds=3600.0
)

# Delays: 60s → 120s → 240s → 480s → ...
```

## Tools Simulated

| Tool | Paradigm | Best For |
|------|----------|----------|
| Airflow | Task-based DAGs | Data/ML pipelines |
| Prefect | Python-native | Modern workflows |
| Dagster | Asset-based | Data products |
| Kubeflow | Container-based | K8s ML training |
| Temporal | Durable execution | Long-running jobs |

## Demo Outputs

### Demo 1: Basic DAG
- DAG validation
- Execution order (topological sort)
- Sequential task execution

### Demo 2: Parallel Execution
- 3 parallel fetch tasks
- Merge after all complete
- ~2x speedup demonstrated

### Demo 3: Retry Logic
- Flaky task (fails first 2 attempts)
- Exponential backoff delays
- Successful retry on attempt 3

### Demo 4: Conditional Branching
- Model training with random accuracy
- Branch to production/staging/notify
- Cleanup runs regardless (ALL_DONE)

### Demo 5: Scheduler
- Register multiple DAGs
- Schedule intervals (@daily, @hourly)
- Run history tracking
- Manual triggers

## Production Deployment

```python
# Real Airflow DAG
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG('ml_pipeline', schedule_interval='@daily') as dag:
    extract = PythonOperator(task_id='extract', ...)
    train = PythonOperator(task_id='train', ...)
    deploy = PythonOperator(task_id='deploy', ...)

    extract >> train >> deploy

# Real Prefect Flow
from prefect import flow, task

@task(retries=3)
def extract_data():
    ...

@flow
def ml_pipeline():
    data = extract_data()
    model = train_model(data)
    deploy(model)
```

**Time**: ~4 hours | **Lines**: 1,000+ | **Author**: Neural Dojo
