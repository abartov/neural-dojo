# Module 50: ML Pipeline & Workflow Orchestration

**Duration**: 8-10 hours
**Prerequisites**: Module 49 (Data Versioning & Feature Stores)
**Status**: 🟢 Complete

---

## The 3 AM Wake-Up Call That Spawned an Industry

**San Francisco. October 3, 2014. 3:17 AM.**

Maxime Beauchemin's phone buzzed with yet another alert. Airbnb's data pipeline had failed again. This time it was a cascade: the pricing model hadn't retrained because the feature pipeline died, which happened because the data validation job timed out, which happened because... nobody could tell anymore.

Beauchemin dragged himself to his laptop and started digging through logs. Four hours later, he'd traced the failure to a single upstream task that had silently failed two days ago. The cron job hadn't reported the error. No one knew until everything downstream collapsed.

"This is insane," he muttered. "We're running a billion-dollar company on bash scripts and hope."

Over the next few months, Beauchemin built something different: a system where tasks declared their dependencies, where failures triggered immediate alerts, where you could see the entire pipeline at a glance. He called it "Airflow."

> "I wrote Airflow out of frustration. Every data team was solving the same problem badly—orchestrating complex workflows with cron and prayer. I thought: what if we could make pipelines first-class citizens, with proper scheduling, monitoring, and visualization?"
> — Maxime Beauchemin, Creator of Apache Airflow

Airbnb open-sourced Airflow in 2015. Today, it orchestrates ML pipelines at Uber, Spotify, and thousands of other companies. That 3 AM wake-up call spawned an entire industry.

---

## Learning Objectives

By the end of this module, you will:
- Master Apache Airflow for ML pipeline orchestration
- Build Kubeflow Pipelines for Kubernetes-native ML
- Create visual AI workflows with n8n
- Compare modern orchestration tools (Prefect, Dagster, Temporal)
- Design production-ready ML pipelines
- Implement retry, monitoring, and alerting patterns

---

## Why Pipeline Orchestration Matters

Every ML system in production needs orchestration. Training a model once is easy. Training it daily, with data validation, feature engineering, model evaluation, and deployment - that's where orchestration becomes essential.

Think of ML orchestration like an airport control tower. Individual planes (ML tasks) know how to fly, but without coordination, you'd have chaos—planes taking off into each other, landing on occupied runways, fuel trucks colliding with baggage carts. The control tower (orchestrator) ensures everything happens in the right order, at the right time, with the right resources, and knows immediately when something goes wrong.

**The Reality of ML in Production**:
```
WITHOUT ORCHESTRATION              WITH ORCHESTRATION
====================              ==================

Manual cron jobs                  Declarative DAGs
"It worked on my machine"         Reproducible pipelines
No visibility                     Full observability
Failures go unnoticed             Automatic retries + alerts
No dependency management          Clear task dependencies
Ad-hoc scheduling                 Intelligent scheduling
```

**Did You Know?** Airbnb created Apache Airflow in 2014 when Maxime Beauchemin needed to orchestrate their complex data pipelines. They open-sourced it in 2015, and it became an Apache top-level project in 2019. Today, Airflow powers ML pipelines at Uber, Spotify, Twitter, and thousands of other companies.

---

## The Orchestration Landscape

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ML ORCHESTRATION TOOLS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CODE-FIRST                          VISUAL/LOW-CODE                     │
│  ──────────                          ──────────────                      │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐   ┌─────────────┐  ┌─────────────┐   │
│  │   AIRFLOW   │  │   PREFECT   │   │     n8n     │  │  LANGFLOW   │   │
│  │  (Apache)   │  │  (Modern)   │   │  (Visual)   │  │ (LangChain) │   │
│  │             │  │             │   │             │  │             │   │
│  │ Python DAGs │  │ Python-     │   │ Drag-drop   │  │ AI chains   │   │
│  │ Scheduling  │  │ native      │   │ 400+ nodes  │  │ Visual      │   │
│  │ Battle-     │  │ Dynamic     │   │ AI nodes    │  │ builder     │   │
│  │ tested      │  │ Hybrid      │   │ Self-host   │  │             │   │
│  └─────────────┘  └─────────────┘   └─────────────┘  └─────────────┘   │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐   ┌─────────────┐  ┌─────────────┐   │
│  │   DAGSTER   │  │  KUBEFLOW   │   │  WINDMILL   │  │   FLOWISE   │   │
│  │  (Asset)    │  │  (K8s ML)   │   │  (Scripts)  │  │  (LLM)      │   │
│  │             │  │             │   │             │  │             │   │
│  │ Data-aware  │  │ K8s-native  │   │ Any lang    │  │ Drag-drop   │   │
│  │ Typed       │  │ ML-focused  │   │ Visual +    │  │ LLM flows   │   │
│  │ Software-   │  │ Pipelines   │   │ code        │  │             │   │
│  │ defined     │  │             │   │             │  │             │   │
│  └─────────────┘  └─────────────┘   └─────────────┘  └─────────────┘   │
│                                                                          │
│  ┌─────────────┐                                                        │
│  │  TEMPORAL   │  WHEN TO USE WHAT:                                     │
│  │  (Durable)  │  ───────────────────                                   │
│  │             │  Complex ML Pipelines → Airflow, Kubeflow              │
│  │ Long-       │  Data Engineering    → Dagster, Airflow                │
│  │ running     │  Quick AI Prototypes → n8n, LangFlow                   │
│  │ Reliable    │  Production Agents   → n8n, Temporal                   │
│  │ workflows   │  Long-running Jobs   → Temporal                        │
│  └─────────────┘  K8s-native ML       → Kubeflow                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Apache Airflow Deep Dive

### What is Airflow?

Airflow is the industry standard for workflow orchestration. It lets you define workflows as code (DAGs - Directed Acyclic Graphs), schedule them, and monitor their execution.

```
AIRFLOW ARCHITECTURE
====================

┌─────────────────────────────────────────────────────────────────┐
│                         AIRFLOW                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  SCHEDULER  │───▶│   EXECUTOR  │───▶│   WORKERS   │        │
│   │             │    │             │    │             │        │
│   │ Triggers    │    │ Celery/K8s/ │    │ Run tasks   │        │
│   │ DAG runs    │    │ Local       │    │             │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│          │                                     │                │
│          ▼                                     ▼                │
│   ┌─────────────┐                      ┌─────────────┐        │
│   │  METADATA   │                      │  WEB UI     │        │
│   │  DATABASE   │◀────────────────────▶│             │        │
│   │  (Postgres) │                      │ Monitoring  │        │
│   └─────────────┘                      └─────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### DAG Basics

A DAG (Directed Acyclic Graph) defines the workflow structure. Think of a DAG like a recipe with dependencies: you can chop vegetables and boil water in parallel (no dependencies), but you can't add the vegetables until the water is boiling (dependency). The "acyclic" part means you can't create circular dependencies—the vegetables can't require the soup to be done before being chopped.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# DAG definition
default_args = {
    'owner': 'ml_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['ml-team@company.com'],
}

with DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='Daily ML model training pipeline',
    schedule_interval='@daily',  # or '0 6 * * *' for 6 AM
    catchup=False,
    tags=['ml', 'training'],
) as dag:

    # Task 1: Extract data
    extract_data = PythonOperator(
        task_id='extract_data',
        python_callable=extract_from_database,
    )

    # Task 2: Validate data
    validate_data = PythonOperator(
        task_id='validate_data',
        python_callable=run_data_validation,
    )

    # Task 3: Feature engineering
    feature_engineering = PythonOperator(
        task_id='feature_engineering',
        python_callable=engineer_features,
    )

    # Task 4: Train model
    train_model = PythonOperator(
        task_id='train_model',
        python_callable=train_ml_model,
    )

    # Task 5: Evaluate model
    evaluate_model = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model_performance,
    )

    # Task 6: Deploy if good
    deploy_model = PythonOperator(
        task_id='deploy_model',
        python_callable=deploy_to_production,
    )

    # Define dependencies (the DAG structure)
    extract_data >> validate_data >> feature_engineering
    feature_engineering >> train_model >> evaluate_model >> deploy_model
```

### ML-Specific Patterns in Airflow

```python
from airflow.decorators import dag, task
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

@dag(
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def ml_pipeline_with_branching():
    """
    ML pipeline with conditional deployment based on metrics.
    """

    @task
    def extract_data():
        """Extract training data from source."""
        # Extract logic
        return {'rows': 10000, 'features': 50}

    @task
    def validate_data(data_info: dict):
        """Validate data quality."""
        if data_info['rows'] < 1000:
            raise ValueError("Insufficient data!")
        return {'valid': True, 'rows': data_info['rows']}

    @task
    def train_model(data_info: dict):
        """Train the ML model."""
        # Training logic
        return {
            'accuracy': 0.92,
            'f1_score': 0.89,
            'model_path': '/models/v1.0'
        }

    @task
    def evaluate_model(metrics: dict):
        """Evaluate model and decide deployment."""
        return {
            'deploy': metrics['accuracy'] > 0.90,
            'metrics': metrics
        }

    def choose_deployment_path(**context):
        """Branch based on model quality."""
        ti = context['ti']
        evaluation = ti.xcom_pull(task_ids='evaluate_model')

        if evaluation['deploy']:
            return 'deploy_to_production'
        else:
            return 'notify_failure'

    branch = BranchPythonOperator(
        task_id='branch_on_quality',
        python_callable=choose_deployment_path,
    )

    @task
    def deploy_to_production(evaluation: dict):
        """Deploy model to production."""
        print(f"Deploying model with accuracy: {evaluation['metrics']['accuracy']}")
        return {'deployed': True}

    @task
    def notify_failure(evaluation: dict):
        """Send notification about failed quality check."""
        print(f"Model did not meet threshold: {evaluation['metrics']['accuracy']}")
        return {'notified': True}

    @task(trigger_rule=TriggerRule.ONE_SUCCESS)
    def cleanup():
        """Cleanup temporary files."""
        print("Cleaning up...")

    # Build the DAG
    data = extract_data()
    validated = validate_data(data)
    model = train_model(validated)
    evaluation = evaluate_model(model)

    branch >> [deploy_to_production(evaluation), notify_failure(evaluation)]
    [deploy_to_production(evaluation), notify_failure(evaluation)] >> cleanup()

# Instantiate the DAG
ml_pipeline = ml_pipeline_with_branching()
```

**Did You Know?** The TaskFlow API (using `@task` decorators) was introduced in Airflow 2.0 (December 2020). It was created by Kaxil Naik and the community to make DAGs more Pythonic and reduce boilerplate. Before TaskFlow, passing data between tasks required explicit XCom pulls, which was verbose and error-prone.

---

## Kubeflow Pipelines

### Why Kubeflow?

Kubeflow Pipelines is designed specifically for ML on Kubernetes. Think of Kubeflow like a factory assembly line where each station (container) has specialized equipment. The data processing station has different tools than the GPU training station, but they all connect smoothly. And because each station is independent, you can upgrade or replace one without disrupting the others.

Kubeflow is perfect for:
- GPU-intensive training jobs
- Reproducible experiments
- Multi-team ML platforms

```
KUBEFLOW PIPELINES ARCHITECTURE
===============================

┌─────────────────────────────────────────────────────────────────┐
│                    KUBEFLOW PIPELINES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   PIPELINE DEFINITION (Python SDK)                               │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  @component → @pipeline → compile() → upload()          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 KUBERNETES CLUSTER                       │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│   │  │  Step 1 │─▶│  Step 2 │─▶│  Step 3 │─▶│  Step 4 │    │   │
│   │  │  (Pod)  │  │  (Pod)  │  │  (Pod)  │  │  (Pod)  │    │   │
│   │  │         │  │  +GPU   │  │         │  │         │    │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  METADATA STORE  │  ARTIFACT STORE  │  UI DASHBOARD     │   │
│   │  (MySQL)         │  (MinIO/GCS)     │  (Runs, Metrics)  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Kubeflow Pipeline Definition

```python
from kfp import dsl
from kfp import compiler
from kfp.dsl import Dataset, Model, Metrics, Input, Output

# Define a component
@dsl.component(
    base_image='python:3.10',
    packages_to_install=['pandas', 'scikit-learn']
)
def preprocess_data(
    input_data: Input[Dataset],
    output_data: Output[Dataset],
    test_size: float = 0.2
):
    """Preprocess and split data."""
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(input_data.path)

    # Preprocessing
    df = df.dropna()
    df = df[df['value'] > 0]

    # Split
    train, test = train_test_split(df, test_size=test_size)

    # Save
    train.to_csv(output_data.path, index=False)


@dsl.component(
    base_image='python:3.10',
    packages_to_install=['pandas', 'scikit-learn', 'xgboost']
)
def train_model(
    training_data: Input[Dataset],
    model_output: Output[Model],
    metrics_output: Output[Metrics],
    n_estimators: int = 100,
    max_depth: int = 6
):
    """Train XGBoost model."""
    import pandas as pd
    import xgboost as xgb
    from sklearn.metrics import accuracy_score, f1_score
    import json

    df = pd.read_csv(training_data.path)
    X = df.drop('target', axis=1)
    y = df['target']

    # Train
    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    model.fit(X, y)

    # Evaluate
    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)
    f1 = f1_score(y, predictions, average='weighted')

    # Save model
    model.save_model(model_output.path)

    # Log metrics
    metrics_output.log_metric('accuracy', accuracy)
    metrics_output.log_metric('f1_score', f1)


@dsl.component(base_image='python:3.10')
def deploy_model(
    model: Input[Model],
    metrics: Input[Metrics],
    endpoint: str
) -> str:
    """Deploy model if metrics pass threshold."""
    # Check metrics
    if metrics.metadata.get('accuracy', 0) < 0.85:
        return "Model did not meet accuracy threshold"

    # Deploy logic
    print(f"Deploying to {endpoint}")
    return f"Deployed to {endpoint}"


# Define the pipeline
@dsl.pipeline(
    name='ML Training Pipeline',
    description='End-to-end ML training with Kubeflow'
)
def ml_training_pipeline(
    input_data_path: str,
    test_size: float = 0.2,
    n_estimators: int = 100,
    max_depth: int = 6,
    deploy_endpoint: str = 'production'
):
    # Step 1: Preprocess
    preprocess_task = preprocess_data(
        input_data=dsl.importer(
            artifact_uri=input_data_path,
            artifact_class=Dataset
        ),
        test_size=test_size
    )

    # Step 2: Train (request GPU)
    train_task = train_model(
        training_data=preprocess_task.outputs['output_data'],
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    train_task.set_gpu_limit(1)
    train_task.set_memory_limit('8G')

    # Step 3: Deploy
    deploy_task = deploy_model(
        model=train_task.outputs['model_output'],
        metrics=train_task.outputs['metrics_output'],
        endpoint=deploy_endpoint
    )


# Compile the pipeline
compiler.Compiler().compile(
    ml_training_pipeline,
    'ml_pipeline.yaml'
)
```

**Did You Know?** Kubeflow started as an internal Google project in 2017 to simplify ML on Kubernetes. The name comes from "Kubernetes" + "TensorFlow" (though it now supports all frameworks). Google's David Aronchick led the project, which became one of the fastest-growing Kubernetes projects, reaching 10,000+ GitHub stars within two years.

---

## n8n: Visual AI Workflows

### Why n8n?

n8n is a visual workflow automation tool that's particularly powerful for AI applications. Think of n8n like building with LEGO blocks—each block (node) does one thing, and you snap them together visually to create complex AI workflows. Non-programmers can build RAG pipelines, chatbot backends, and document processors by dragging and connecting nodes, while programmers can add custom code blocks when needed.

```
n8n FOR AI WORKFLOWS
====================

┌─────────────────────────────────────────────────────────────────┐
│                        n8n WORKFLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ TRIGGER │───▶│  FETCH  │───▶│   LLM   │───▶│  STORE  │      │
│  │         │    │  DATA   │    │ PROCESS │    │ RESULT  │      │
│  │ Webhook │    │  HTTP   │    │ OpenAI  │    │ Postgres│      │
│  │ Cron    │    │ DB      │    │ Claude  │    │ Vector  │      │
│  │ Email   │    │ S3      │    │ Ollama  │    │ Notion  │      │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│                                                                  │
│  AI-SPECIFIC NODES:                                              │
│  ─────────────────                                               │
│  • OpenAI (GPT-4, embeddings)                                    │
│  • Anthropic (Claude)                                            │
│  • Ollama (local models)                                         │
│  • Vector Stores (Pinecone, Qdrant, Supabase)                   │
│  • Document Loaders (PDF, web, etc.)                            │
│  • Text Splitters (chunk documents)                              │
│  • LangChain nodes                                               │
│                                                                  │
│  EXAMPLE RAG WORKFLOW:                                           │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐          │
│  │Webhook│─▶│Embed │─▶│Vector│─▶│ LLM  │─▶│Return│          │
│  │Query │   │Query │   │Search│   │Answer│   │Response│          │
│  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### n8n Workflow Example (JSON)

```json
{
  "name": "AI Document Q&A",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "ask",
        "method": "POST"
      }
    },
    {
      "name": "Embed Question",
      "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
      "parameters": {
        "model": "text-embedding-3-small"
      }
    },
    {
      "name": "Vector Store Search",
      "type": "@n8n/n8n-nodes-langchain.vectorStoreQdrant",
      "parameters": {
        "operation": "search",
        "topK": 5
      }
    },
    {
      "name": "Generate Answer",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "parameters": {
        "model": "gpt-4",
        "prompt": "Based on the following context, answer the question.\n\nContext: {{$node['Vector Store Search'].json.results}}\n\nQuestion: {{$node['Webhook'].json.question}}"
      }
    },
    {
      "name": "Return Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "responseBody": "={{$node['Generate Answer'].json.text}}"
      }
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Embed Question" }]] },
    "Embed Question": { "main": [[{ "node": "Vector Store Search" }]] },
    "Vector Store Search": { "main": [[{ "node": "Generate Answer" }]] },
    "Generate Answer": { "main": [[{ "node": "Return Response" }]] }
  }
}
```

**Did You Know?** n8n was created by Jan Oberhauser in Berlin in 2019. The name "n8n" is a numeronym for "nodemation" (n-8 letters-n). It raised $12M in Series A funding in 2022 and has become the go-to tool for self-hosted workflow automation, with over 400 integrations and a thriving community of AI workflow builders.

---

## Modern Alternatives: Prefect & Dagster

### Prefect: Python-Native Workflows

Prefect is a modern alternative to Airflow, designed to be more Pythonic and developer-friendly.

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(
    retries=3,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def extract_data(source: str) -> dict:
    """Extract data from source."""
    print(f"Extracting from {source}")
    return {"rows": 10000, "source": source}

@task
def transform_data(data: dict) -> dict:
    """Transform the data."""
    return {"rows": data["rows"], "transformed": True}

@task
def train_model(data: dict) -> dict:
    """Train ML model."""
    return {"accuracy": 0.95, "rows_used": data["rows"]}

@task
def deploy_if_good(metrics: dict) -> str:
    """Deploy model if metrics are good."""
    if metrics["accuracy"] > 0.90:
        return "Deployed to production!"
    return "Model not good enough"

@flow(name="ML Training Pipeline")
def ml_pipeline(source: str = "s3://data/training"):
    """Complete ML training pipeline."""
    # Extract
    raw_data = extract_data(source)

    # Transform
    clean_data = transform_data(raw_data)

    # Train
    metrics = train_model(clean_data)

    # Deploy
    result = deploy_if_good(metrics)

    return result

# Run the flow
if __name__ == "__main__":
    ml_pipeline()
```

**Prefect vs Airflow**:
```
PREFECT                              AIRFLOW
───────                              ───────
Python-native                        DAG files in specific folder
Dynamic workflows                    Static DAG structure
Local-first                          Server-first
Hybrid execution                     Centralized execution
Built-in caching                     Manual caching
Modern UI                            Classic UI
```

### Dagster: Asset-Based Pipelines

Dagster takes a different approach: instead of defining tasks, you define assets (the data you produce). Think of the difference like cooking: Airflow is like a recipe that says "chop vegetables, then sauté, then serve"—it focuses on the steps. Dagster is like describing the meal itself—"we need chopped vegetables, we need sautéed vegetables, we need a served dish"—and the system figures out the steps to make each thing.

```python
from dagster import asset, AssetExecutionContext, Definitions
from dagster import MaterializeResult, MetadataValue
import pandas as pd

@asset(
    description="Raw user data from database",
    group_name="bronze"
)
def raw_users(context: AssetExecutionContext) -> pd.DataFrame:
    """Extract raw user data."""
    context.log.info("Extracting raw users...")
    return pd.DataFrame({
        'user_id': range(1000),
        'name': [f'User {i}' for i in range(1000)],
        'signup_date': pd.date_range('2024-01-01', periods=1000)
    })

@asset(
    description="Cleaned and validated user data",
    group_name="silver",
    deps=[raw_users]
)
def clean_users(context: AssetExecutionContext, raw_users: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate user data."""
    # Remove duplicates
    df = raw_users.drop_duplicates()

    # Add derived columns
    df['days_since_signup'] = (pd.Timestamp.now() - df['signup_date']).dt.days

    context.log.info(f"Cleaned {len(df)} users")
    return df

@asset(
    description="User features for ML",
    group_name="gold",
    deps=[clean_users]
)
def user_features(context: AssetExecutionContext, clean_users: pd.DataFrame) -> MaterializeResult:
    """Engineer features for ML."""
    df = clean_users.copy()

    # Feature engineering
    df['is_new_user'] = df['days_since_signup'] < 30
    df['user_segment'] = pd.cut(
        df['days_since_signup'],
        bins=[0, 30, 90, 365, float('inf')],
        labels=['new', 'active', 'mature', 'veteran']
    )

    # Save
    df.to_parquet('/data/features/user_features.parquet')

    return MaterializeResult(
        metadata={
            'num_rows': MetadataValue.int(len(df)),
            'num_features': MetadataValue.int(len(df.columns)),
            'schema': MetadataValue.md(df.dtypes.to_markdown())
        }
    )

@asset(
    description="Trained churn prediction model",
    group_name="ml",
    deps=[user_features]
)
def churn_model(context: AssetExecutionContext) -> MaterializeResult:
    """Train churn prediction model."""
    # Load features
    features = pd.read_parquet('/data/features/user_features.parquet')

    # Train model (simplified)
    accuracy = 0.92

    return MaterializeResult(
        metadata={
            'accuracy': MetadataValue.float(accuracy),
            'training_rows': MetadataValue.int(len(features))
        }
    )

# Define the Dagster job
defs = Definitions(
    assets=[raw_users, clean_users, user_features, churn_model]
)
```

**Dagster's Asset Graph**:
```
┌─────────────┐
│  raw_users  │ (Bronze)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ clean_users │ (Silver)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│user_features│ (Gold)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ churn_model │ (ML)
└─────────────┘
```

**Did You Know?** Dagster was created by Nick Schrock, who previously created GraphQL at Facebook. He founded Elementl in 2018 with the insight that data pipelines should be treated like software: with types, tests, and clear interfaces. The asset-based approach mirrors how data teams actually think about their work.

---

## Temporal: Durable Execution

Temporal is different from other tools - it's designed for long-running, reliable workflows that need to survive failures. Think of Temporal like a notary that records every step of a complex business process. If the power goes out mid-signature, when it comes back, the notary knows exactly which documents were signed and which weren't—nothing is lost, and you resume from exactly where you stopped. This "durable execution" is why Temporal is used for critical ML workflows that can't afford to restart from scratch.

```python
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class TrainingConfig:
    dataset_path: str
    model_type: str
    hyperparameters: dict

@dataclass
class TrainingResult:
    model_path: str
    metrics: dict

# Activities (the actual work)
@activity.defn
async def download_dataset(path: str) -> str:
    """Download dataset (can take hours for large datasets)."""
    # Temporal handles retries, timeouts, heartbeats
    print(f"Downloading from {path}...")
    return "/local/data/training.parquet"

@activity.defn
async def train_model(local_path: str, config: TrainingConfig) -> dict:
    """Train model (can take hours/days)."""
    # Long-running training
    print(f"Training {config.model_type}...")
    return {"accuracy": 0.95, "path": "/models/v1"}

@activity.defn
async def deploy_model(model_path: str) -> str:
    """Deploy to production."""
    print(f"Deploying {model_path}...")
    return "https://api.company.com/model/v1"

# Workflow (the orchestration)
@workflow.defn
class MLTrainingWorkflow:
    """
    Durable ML training workflow.

    If this crashes mid-training, Temporal will resume
    from exactly where it left off!
    """

    @workflow.run
    async def run(self, config: TrainingConfig) -> TrainingResult:
        # Step 1: Download (with timeout and retries)
        local_path = await workflow.execute_activity(
            download_dataset,
            config.dataset_path,
            start_to_close_timeout=timedelta(hours=2),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

        # Step 2: Train (long-running, with heartbeat)
        training_result = await workflow.execute_activity(
            train_model,
            local_path,
            config,
            start_to_close_timeout=timedelta(days=7),
            heartbeat_timeout=timedelta(minutes=10),
        )

        # Step 3: Human approval (workflow waits!)
        approved = await workflow.execute_activity(
            wait_for_human_approval,
            training_result,
            start_to_close_timeout=timedelta(days=30),
        )

        if approved:
            # Step 4: Deploy
            endpoint = await workflow.execute_activity(
                deploy_model,
                training_result["path"],
                start_to_close_timeout=timedelta(minutes=30),
            )

            return TrainingResult(
                model_path=training_result["path"],
                metrics=training_result
            )
        else:
            raise Exception("Human rejected the model")

# Run the workflow
async def main():
    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        MLTrainingWorkflow.run,
        TrainingConfig(
            dataset_path="s3://data/training",
            model_type="xgboost",
            hyperparameters={"n_estimators": 100}
        ),
        id="ml-training-2024-01-15",
        task_queue="ml-training",
    )

    print(f"Training complete: {result}")
```

**When to Use Temporal**:
```
USE TEMPORAL WHEN:
──────────────────
• Workflows can take hours/days/weeks
• Human approval steps are needed
• Workflows must survive infrastructure failures
• You need exactly-once execution guarantees
• Complex compensation/rollback logic

DON'T USE TEMPORAL WHEN:
────────────────────────
• Simple scheduled jobs (use Airflow)
• Quick data transformations (use Dagster)
• Real-time streaming (use Kafka/Flink)
```

---

## Comparison Matrix

```
┌────────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│    Feature     │   AIRFLOW   │   PREFECT   │   DAGSTER   │  KUBEFLOW   │   TEMPORAL  │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Paradigm       │ Task-based  │ Task-based  │ Asset-based │ Container   │ Durable     │
│                │ DAGs        │ Flows       │ Assets      │ Pipelines   │ Workflows   │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Learning Curve │ Medium      │ Low         │ Medium      │ High        │ High        │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Best For       │ Data/ML     │ Modern      │ Data        │ K8s ML      │ Long-       │
│                │ Pipelines   │ Pipelines   │ Products    │ Training    │ running     │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Scheduling     │ ✅ Built-in │ ✅ Built-in │ ✅ Built-in │ ✅ Built-in │ ⚠️ External │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Dynamic DAGs   │ ⚠️ Limited  │ ✅ Native   │ ✅ Native   │ ⚠️ Limited  │ ✅ Native   │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ GPU Support    │ ⚠️ Manual   │ ⚠️ Manual   │ ⚠️ Manual   │ ✅ Native   │ ⚠️ Manual   │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Self-hosted    │ ✅ Yes      │ ✅ Yes      │ ✅ Yes      │ ✅ Yes      │ ✅ Yes      │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Managed Cloud  │ ✅ MWAA     │ ✅ Prefect  │ ✅ Dagster  │ ✅ Vertex   │ ✅ Temporal │
│                │   GCP       │   Cloud     │   Cloud     │   AI        │   Cloud     │
├────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Community      │ ⭐⭐⭐⭐⭐  │ ⭐⭐⭐⭐    │ ⭐⭐⭐⭐    │ ⭐⭐⭐⭐    │ ⭐⭐⭐      │
└────────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Production Patterns

### Pattern 1: Retry with Exponential Backoff

```python
# Airflow
from airflow.decorators import task

@task(
    retries=5,
    retry_delay=timedelta(minutes=1),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(hours=1)
)
def flaky_api_call():
    """Call external API with retries."""
    pass

# Prefect
from prefect import task

@task(
    retries=5,
    retry_delay_seconds=[60, 120, 240, 480, 960]  # Custom backoff
)
def flaky_api_call():
    pass
```

### Pattern 2: Conditional Branching

```python
# Airflow
from airflow.operators.python import BranchPythonOperator

def choose_path(**context):
    metrics = context['ti'].xcom_pull(task_ids='evaluate')
    if metrics['accuracy'] > 0.9:
        return 'deploy_production'
    elif metrics['accuracy'] > 0.8:
        return 'deploy_staging'
    else:
        return 'retrain'

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_path
)
```

### Pattern 3: Parallel Execution

```python
# Airflow - Dynamic Task Mapping
@task
def process_partition(partition_id: int):
    return f"Processed {partition_id}"

@dag
def parallel_processing():
    partitions = list(range(10))

    # This creates 10 parallel tasks!
    results = process_partition.expand(partition_id=partitions)

    aggregate_results(results)

# Prefect - Concurrent Execution
from prefect import flow, task
from prefect.futures import wait

@task
def process_item(item):
    return item * 2

@flow
def parallel_flow():
    items = range(100)
    futures = [process_item.submit(item) for item in items]
    results = [f.result() for f in futures]
    return results
```

### Pattern 4: Sensors and Triggers

```python
# Airflow - Wait for file
from airflow.sensors.filesystem import FileSensor

wait_for_data = FileSensor(
    task_id='wait_for_data',
    filepath='/data/daily/{{ ds }}/data.parquet',
    poke_interval=300,  # Check every 5 minutes
    timeout=3600 * 6,   # Timeout after 6 hours
    mode='reschedule'   # Don't block worker
)

# Airflow - Wait for external DAG
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='data_ingestion',
    external_task_id='load_complete',
    timeout=3600
)
```

---

## Decision Framework

```
CHOOSING AN ORCHESTRATION TOOL
==============================

START HERE
    │
    ▼
┌─────────────────────────────────────┐
│ Do you need Kubernetes-native ML?   │
└─────────────────────────────────────┘
    │                    │
   YES                  NO
    │                    │
    ▼                    ▼
┌─────────┐    ┌─────────────────────────────┐
│KUBEFLOW │    │ Do workflows run for        │
│PIPELINES│    │ hours/days with human       │
└─────────┘    │ approval steps?             │
               └─────────────────────────────┘
                   │                    │
                  YES                  NO
                   │                    │
                   ▼                    ▼
              ┌─────────┐    ┌─────────────────────────────┐
              │TEMPORAL │    │ Is your team data-centric   │
              └─────────┘    │ (thinking in assets)?       │
                             └─────────────────────────────┘
                                 │                    │
                                YES                  NO
                                 │                    │
                                 ▼                    ▼
                            ┌─────────┐    ┌─────────────────────────────┐
                            │ DAGSTER │    │ Need battle-tested,         │
                            └─────────┘    │ enterprise-grade?           │
                                           └─────────────────────────────┘
                                               │                    │
                                              YES                  NO
                                               │                    │
                                               ▼                    ▼
                                          ┌─────────┐         ┌─────────┐
                                          │ AIRFLOW │         │ PREFECT │
                                          └─────────┘         └─────────┘

VISUAL/LOW-CODE NEEDS:
──────────────────────
• Quick AI prototypes      → n8n
• LangChain flows          → LangFlow
• LLM chat flows           → Flowise
• Multi-language scripts   → Windmill
```

---

## Hands-On Exercises

### Exercise 1: Build an Airflow ML DAG

Create a DAG that:
1. Extracts data from a CSV
2. Validates data quality
3. Trains a model
4. Evaluates and branches
5. Deploys or notifies

### Exercise 2: Create a Prefect Flow

Build a Prefect flow that:
1. Fetches data from an API
2. Processes in parallel
3. Aggregates results
4. Caches intermediate results

### Exercise 3: Design a Dagster Asset Graph

Create assets for:
1. Raw data (bronze)
2. Clean data (silver)
3. Feature data (gold)
4. ML model

---

## Further Reading

### Documentation
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Prefect Docs](https://docs.prefect.io/)
- [Dagster Docs](https://docs.dagster.io/)
- [Kubeflow Pipelines Docs](https://www.kubeflow.org/docs/components/pipelines/)
- [Temporal Docs](https://docs.temporal.io/)
- [n8n Docs](https://docs.n8n.io/)

### Articles
- "Why We Moved from Airflow to Prefect" (Netflix)
- "Building ML Pipelines at Scale with Kubeflow" (Google)
- "Asset-Based Data Pipelines with Dagster" (Elementl)

---

## Summary

```
ORCHESTRATION TOOLS SUMMARY
===========================

AIRFLOW:   Industry standard, battle-tested, large community
PREFECT:   Modern, Python-native, better developer experience
DAGSTER:   Asset-based, data-centric, great for analytics
KUBEFLOW:  Kubernetes-native, ML-focused, GPU support
TEMPORAL:  Durable execution, long-running, reliable
n8n:       Visual, low-code, AI-native nodes

WHEN TO USE:
────────────
Data Engineering     → Airflow, Dagster
ML Training          → Kubeflow, Airflow
Quick Prototypes     → n8n, Prefect
Long-running Jobs    → Temporal
Modern Teams         → Prefect, Dagster
```

---

## Next Steps

Module 51 will cover Model Deployment & Serving Patterns, including FastAPI, gRPC, canary deployments, and A/B testing.

---

_Module 50 Complete!_
_"The best pipeline is one that runs without you thinking about it."_
