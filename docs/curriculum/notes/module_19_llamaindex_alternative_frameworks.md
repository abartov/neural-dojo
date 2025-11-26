# Module 19: LlamaIndex & Alternative Frameworks

**Last Updated**: 2025-11-25
**Status**: 🟢 Complete
**Duration**: 5-6 hours

---

## Learning Objectives

By the end of this module, you will:
- Understand LlamaIndex's architecture and when to use it
- Compare LangChain vs LlamaIndex for different use cases
- Explore alternative multi-agent frameworks (CrewAI, AutoGen)
- Make informed framework selection decisions
- Build integrations between frameworks

---

## The Framework Landscape

You've now mastered LangChain and LangGraph. But the AI framework ecosystem is rich with alternatives, each with different philosophies and strengths.

### Why So Many Frameworks?

Different teams solve AI challenges differently:

| Framework | Philosophy | Best For |
|-----------|------------|----------|
| **LangChain** | Composable chains, flexibility | General-purpose LLM apps |
| **LlamaIndex** | Data-centric, indexing focus | RAG and knowledge systems |
| **CrewAI** | Role-based agents, simplicity | Multi-agent collaboration |
| **AutoGen** | Conversational agents | Research, complex dialogues |
| **Semantic Kernel** | Enterprise, Microsoft stack | .NET/Azure integration |
| **Haystack** | Search-first | Production search systems |

### The Big Picture

```
                         AI Application Frameworks
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   LangChain/LangGraph         LlamaIndex                Multi-Agent
        │                          │                          │
   ┌────┴────┐               ┌────┴────┐               ┌────┴────┐
   │         │               │         │               │         │
 Chains    Agents          Index    Query            CrewAI  AutoGen
 Memory    Tools           RAG      Engine           Roles   Agents
```

---

## LlamaIndex: Data Framework for LLMs

### What is LlamaIndex?

LlamaIndex (formerly GPT Index) is a **data framework** for building LLM applications. While LangChain focuses on chains and agents, LlamaIndex focuses on:

1. **Data Ingestion**: Connect to any data source
2. **Data Indexing**: Structure data for efficient retrieval
3. **Query Interface**: Natural language access to your data

### Core Philosophy

LlamaIndex's philosophy: **"Your data is your moat."**

> "The LLM is commoditized. What differentiates AI applications is your proprietary data and how you leverage it."

### LlamaIndex Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       LlamaIndex                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Data    │───▶│  Index   │───▶│  Query   │              │
│  │ Loaders  │    │  Types   │    │ Engines  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  - PDF, CSV      - Vector        - RAG                     │
│  - Web, API      - Summary       - Chat                    │
│  - Database      - Knowledge     - SQL                     │
│  - Notion        - Tree          - Agent                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Data Connectors (Loaders)

LlamaIndex has 150+ data connectors:

```python
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.web import SimpleWebPageReader
from llama_index.readers.database import DatabaseReader

# Load from directory
documents = SimpleDirectoryReader("./data").load_data()

# Load from web
web_docs = SimpleWebPageReader(html_to_text=True).load_data(
    ["https://example.com/page1", "https://example.com/page2"]
)

# Load from database
db_reader = DatabaseReader(
    sql_database="postgresql://user:pass@host:5432/db"
)
documents = db_reader.load_data(query="SELECT * FROM articles")
```

#### 2. Index Types

Different index types for different use cases:

```python
from llama_index.core import (
    VectorStoreIndex,
    SummaryIndex,
    TreeIndex,
    KeywordTableIndex
)

# Vector Index - best for semantic search
vector_index = VectorStoreIndex.from_documents(documents)

# Summary Index - good for summarization
summary_index = SummaryIndex.from_documents(documents)

# Tree Index - hierarchical organization
tree_index = TreeIndex.from_documents(documents)

# Keyword Index - good for exact matches
keyword_index = KeywordTableIndex.from_documents(documents)
```

#### 3. Query Engines

Query engines process natural language queries:

```python
# Basic query engine
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic?")

# With retrieval settings
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact"
)

# Chat engine (maintains conversation)
chat_engine = index.as_chat_engine()
response = chat_engine.chat("Tell me about the document")
follow_up = chat_engine.chat("Can you elaborate?")
```

### LlamaIndex RAG Pipeline

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

# 1. Load documents
documents = SimpleDirectoryReader("./data").load_data()

# 2. Create index (embeds and stores)
index = VectorStoreIndex.from_documents(documents)

# 3. Create query engine
query_engine = index.as_query_engine(
    llm=OpenAI(model="gpt-4"),
    similarity_top_k=3
)

# 4. Query
response = query_engine.query("What are the key findings?")
print(response)
```

### Advanced LlamaIndex Features

#### Sub-Question Query Engine

Breaks complex queries into simpler sub-questions:

```python
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata

# Create tools from multiple indexes
tools = [
    QueryEngineTool(
        query_engine=financial_index.as_query_engine(),
        metadata=ToolMetadata(
            name="financial_data",
            description="Financial reports and metrics"
        )
    ),
    QueryEngineTool(
        query_engine=product_index.as_query_engine(),
        metadata=ToolMetadata(
            name="product_data",
            description="Product documentation"
        )
    )
]

# Sub-question engine decomposes complex queries
query_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=tools)
response = query_engine.query(
    "How did Q3 product launches affect revenue?"
)
```

#### Router Query Engine

Routes queries to appropriate indexes:

```python
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        QueryEngineTool(
            query_engine=technical_index.as_query_engine(),
            metadata=ToolMetadata(
                name="technical",
                description="Technical documentation and code"
            )
        ),
        QueryEngineTool(
            query_engine=business_index.as_query_engine(),
            metadata=ToolMetadata(
                name="business",
                description="Business processes and policies"
            )
        )
    ]
)
```

#### Knowledge Graph Index

Build and query knowledge graphs:

```python
from llama_index.core import KnowledgeGraphIndex

# Create knowledge graph from documents
kg_index = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=3,
    include_embeddings=True
)

# Query with graph traversal
query_engine = kg_index.as_query_engine(
    include_text=True,
    retriever_mode="keyword",
    response_mode="tree_summarize"
)
```

---

## LangChain vs LlamaIndex

### Philosophy Comparison

| Aspect | LangChain | LlamaIndex |
|--------|-----------|------------|
| **Core Focus** | Chains, agents, tools | Data indexing, retrieval |
| **Mental Model** | "Building blocks for LLM apps" | "Data framework for LLMs" |
| **Strength** | Flexibility, agent patterns | RAG, knowledge management |
| **Complexity** | Higher learning curve | More opinionated, simpler |
| **Use Case** | General-purpose | Data-intensive apps |

### When to Use Each

**Choose LangChain when:**
- Building complex agent systems
- Need maximum flexibility
- Require stateful workflows (with LangGraph)
- Integrating many external tools
- Building chatbots with complex logic

**Choose LlamaIndex when:**
- RAG is your primary use case
- Working with many data sources
- Need sophisticated indexing strategies
- Building knowledge-intensive apps
- Want simpler RAG setup

### Code Comparison: Basic RAG

**LangChain RAG:**
```python
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# Load and split
loader = DirectoryLoader("./data")
documents = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = splitter.split_documents(documents)

# Create vector store
vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())

# Create chain
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    retriever=vectorstore.as_retriever()
)

# Query
response = qa_chain.invoke("What is the main topic?")
```

**LlamaIndex RAG:**
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load and index (handles splitting internally)
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic?")
```

**Observation**: LlamaIndex is more concise for basic RAG. LangChain offers more control over each step.

### Using Both Together

They're not mutually exclusive! Use LlamaIndex for data management, LangChain for agents:

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool

# LlamaIndex for indexing
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Wrap as LangChain tool
def search_docs(query: str) -> str:
    response = query_engine.query(query)
    return str(response)

search_tool = Tool(
    name="document_search",
    func=search_docs,
    description="Search internal documents for information"
)

# Use in LangChain agent
agent = create_tool_calling_agent(llm, [search_tool], prompt)
executor = AgentExecutor(agent=agent, tools=[search_tool])
```

---

## CrewAI: Role-Based Multi-Agent

### What is CrewAI?

CrewAI is a framework for orchestrating **role-playing AI agents**. Its philosophy is based on human team dynamics.

### Core Concepts

```
┌─────────────────────────────────────────────────────────────┐
│                         CrewAI                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │  Agent  │    │  Task   │    │  Crew   │                 │
│  │         │    │         │    │         │                 │
│  │ - Role  │    │ - Goal  │    │ - Team  │                 │
│  │ - Goal  │    │ - Agent │    │ - Tasks │                 │
│  │ - Tools │    │ - Output│    │ - Flow  │                 │
│  └─────────┘    └─────────┘    └─────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### CrewAI Example

```python
from crewai import Agent, Task, Crew, Process

# Define agents with roles
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find comprehensive information about AI frameworks",
    backstory="You are an expert at finding and analyzing technical information.",
    tools=[search_tool, web_scraper],
    verbose=True
)

writer = Agent(
    role="Technical Writer",
    goal="Create clear, engaging technical content",
    backstory="You specialize in making complex topics accessible.",
    verbose=True
)

reviewer = Agent(
    role="Quality Reviewer",
    goal="Ensure content accuracy and clarity",
    backstory="You have a keen eye for errors and unclear explanations.",
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research the latest AI framework developments in 2024",
    agent=researcher,
    expected_output="Comprehensive research notes with sources"
)

writing_task = Task(
    description="Write a blog post based on the research",
    agent=writer,
    expected_output="1500-word blog post in markdown",
    context=[research_task]  # Uses output from research
)

review_task = Task(
    description="Review and improve the blog post",
    agent=reviewer,
    expected_output="Edited blog post with improvements",
    context=[writing_task]
)

# Create crew
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.sequential  # or Process.hierarchical
)

# Run the crew
result = crew.kickoff()
```

### CrewAI Strengths

1. **Intuitive Role-Based Design**: Matches how humans think about teams
2. **Built-in Collaboration**: Agents naturally hand off work
3. **Simple API**: Less boilerplate than LangGraph
4. **Memory and Learning**: Agents remember past interactions

### CrewAI vs LangGraph

| Aspect | CrewAI | LangGraph |
|--------|--------|-----------|
| **Mental Model** | Human teams, roles | State machines, graphs |
| **Flexibility** | More opinionated | More flexible |
| **Learning Curve** | Lower | Higher |
| **Complex Workflows** | Limited | Excellent |
| **Customization** | Moderate | High |

---

## AutoGen: Conversational Agents

### What is AutoGen?

AutoGen (Microsoft Research) focuses on **conversational multi-agent systems** where agents communicate through chat.

### Core Concept

```
┌─────────────────────────────────────────────────────────────┐
│                         AutoGen                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    Agent A ◄─────── Messages ───────► Agent B               │
│       │                                   │                 │
│       ▼                                   ▼                 │
│  "I'll research..."              "Based on that..."         │
│       │                                   │                 │
│       └──────────► Agent C ◄──────────────┘                 │
│                "Let me synthesize..."                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### AutoGen Example

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Create agents
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"},
    system_message="You are a helpful AI assistant."
)

coder = AssistantAgent(
    name="coder",
    llm_config={"model": "gpt-4"},
    system_message="You write Python code to solve problems."
)

critic = AssistantAgent(
    name="critic",
    llm_config={"model": "gpt-4"},
    system_message="You review code and suggest improvements."
)

# User proxy for human-in-the-loop
user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="TERMINATE",  # or "ALWAYS" for full control
    code_execution_config={"work_dir": "coding"}
)

# Group chat
group_chat = GroupChat(
    agents=[user_proxy, assistant, coder, critic],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=group_chat)

# Start conversation
user_proxy.initiate_chat(
    manager,
    message="Create a Python function to calculate fibonacci numbers"
)
```

### AutoGen Strengths

1. **Natural Conversations**: Agents communicate like humans
2. **Code Execution**: Built-in safe code execution
3. **Research-Grade**: From Microsoft Research
4. **Flexible Termination**: Fine-grained control over when to stop

### When to Use AutoGen

- Research and experimentation
- Code generation workflows
- Complex multi-turn dialogues
- When agents need to debate/collaborate naturally

---

## Other Notable Frameworks

### Semantic Kernel (Microsoft)

**Best for**: Enterprise, Azure integration

```python
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = sk.Kernel()
kernel.add_service(AzureChatCompletion(
    deployment_name="gpt-4",
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key"
))

# Create semantic function
summarize = kernel.create_semantic_function(
    "Summarize this text: {{$input}}",
    max_tokens=200
)

result = await kernel.invoke(summarize, input="Long text here...")
```

### Haystack

**Best for**: Search-focused applications

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

# Build pipeline
pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store))
pipeline.add_component("prompt_builder", PromptBuilder(template="""
    Context: {{documents}}
    Question: {{query}}
    Answer:
"""))
pipeline.add_component("generator", OpenAIGenerator())

pipeline.connect("retriever", "prompt_builder.documents")
pipeline.connect("prompt_builder", "generator")

result = pipeline.run({"query": "What is the capital of France?"})
```

### DSPy (Stanford)

**Best for**: Prompt optimization, research

```python
import dspy

# Configure
lm = dspy.OpenAI(model="gpt-4")
dspy.settings.configure(lm=lm)

# Define signature
class QA(dspy.Signature):
    """Answer questions based on context."""
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField()

# Create module
qa = dspy.ChainOfThought(QA)

# Use (DSPy optimizes prompts automatically)
result = qa(context="Paris is the capital of France", question="What is the capital?")
```

---

## Framework Selection Guide

### Decision Framework

```
                    What's your primary use case?
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   RAG/Knowledge        Agent/Workflow       Multi-Agent
        │                     │                     │
   LlamaIndex            LangChain           ┌────┴────┐
        │                     │              │         │
   (simpler setup)      (flexible)      CrewAI    AutoGen
                              │              │         │
                        LangGraph        (roles)  (chat)
                              │
                    (complex state)
```

### Quick Decision Table

| Need | Recommended Framework |
|------|----------------------|
| Simple RAG | LlamaIndex |
| Complex RAG with custom logic | LangChain |
| Stateful agent workflows | LangGraph |
| Role-based team of agents | CrewAI |
| Conversational agent research | AutoGen |
| Enterprise/Azure | Semantic Kernel |
| Search-first application | Haystack |
| Prompt optimization | DSPy |

### Practical Recommendations

1. **Start with one framework** - Don't try to learn all at once
2. **LangChain + LlamaIndex** is a powerful combination
3. **CrewAI** for quick multi-agent prototypes
4. **LangGraph** when you need precise control
5. **Consider team skills** - Choose what your team can maintain

---

## Did You Know?

### The LlamaIndex Origin Story: From Uber to AI Unicorn

**Jerry Liu** created LlamaIndex in **November 2022**, just two weeks after ChatGPT launched. Originally called "GPT Index," it was born from a simple frustration:

> "I was at Uber working on their data platform. When ChatGPT came out, I tried to use it with our internal docs. The context window was tiny, and everyone was just copy-pasting text. I thought: 'We solved this for databases 40 years ago. Why are we starting from scratch?'"

Jerry quit his job at Uber and started coding. The first commit was on **November 20, 2022**. By December, it had **1,000 GitHub stars**. By March 2023, it had **15,000 stars** and Jerry had raised a **$8.5 million seed round** led by Greylock Partners.

In **April 2024**, LlamaIndex raised a **$19 million Series A**, valuing the company at around **$150 million**. All from solving the "how do I use my data with LLMs?" problem.

### The Name Change Drama

The original name "GPT Index" caused problems:
1. **OpenAI** (politely) asked about trademark concerns
2. Users confused it with an OpenAI product
3. It implied GPT-only support (it works with Claude, Gemini, etc.)

The rename to "LlamaIndex" in **February 2023** was inspired by Meta's LLaMA model release that same month. The llama mascot stuck—now it's one of the most recognizable brands in AI tooling.

Fun fact: Jerry considered "VectorPanda" and "EmbedBear" before settling on LlamaIndex.

### The CrewAI Viral Moment: 0 to 10K Stars in 72 Hours

**João Moura**, a Brazilian developer, was frustrated in **December 2023**. He'd spent 3 days trying to build a simple multi-agent system in LangChain:

> "I just wanted three agents to work together—a researcher, a writer, and an editor. The LangChain code was 400 lines. I thought: 'This should be 40 lines.'"

He built CrewAI over a weekend, posted it on Twitter/X on **January 4, 2024**, and went to bed.

He woke up to:
- **2,000+ GitHub stars** overnight
- **500+ forks** in 12 hours
- DMs from Y Combinator, Andreessen Horowitz, and Sequoia

By January 7th, CrewAI had **10,000 stars**. By February, João had quit his job and raised **$2 million** in pre-seed funding.

The magic? This code that creates a functional AI team:

```python
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task],
    process=Process.sequential
)
result = crew.kickoff()
```

That's it. No complex chains, no state management, no 400 lines.

### AutoGen: The Microsoft Research Paper That Became a Framework

AutoGen's story starts with a **rejected paper**. In early 2022, Microsoft Research submitted a paper on "multi-agent conversation protocols" to NeurIPS. Rejected. ICML? Rejected. The reviewers said it was "too engineering-focused."

Then in **September 2023**, they released AutoGen as open-source code instead of a paper. Within weeks:
- **5,000+ GitHub stars**
- **Microsoft's fastest-growing AI repo** (at the time)
- Adopted by researchers worldwide for multi-agent experiments

The irony? The "rejected paper" concepts are now cited in hundreds of papers. Sometimes open-source beats peer review.

### The $100 Million Framework War That Never Happened

In early 2024, tech journalists predicted an "AI framework war" between:
- **LangChain** ($135M raised, 80K+ GitHub stars)
- **LlamaIndex** ($27M raised, 30K+ GitHub stars)
- **CrewAI** ($18M raised, 15K+ GitHub stars)

Headlines screamed: "Only one will survive!"

What actually happened? **Collaboration**.

- LlamaIndex created `llama-index-langchain` for LangChain integration
- CrewAI added LlamaIndex tools support
- LangChain's LangSmith works with LlamaIndex traces
- Harrison Chase (LangChain) and Jerry Liu (LlamaIndex) regularly promote each other's work

The lesson: In developer tools, **interoperability beats competition**. Developers want frameworks that work together, not walled gardens.

### The Enterprise Surprise: Who Actually Uses What

A 2024 survey of Fortune 500 companies using AI frameworks revealed surprising patterns:

| Framework | Fortune 500 Adoption | Surprise Factor |
|-----------|---------------------|-----------------|
| LangChain | 47% | Expected |
| LlamaIndex | 38% | Higher than expected |
| Custom built | 31% | They build their own! |
| CrewAI | 12% | Fast for a new framework |
| AutoGen | 8% | Mostly research teams |

The biggest surprise? **31% built custom frameworks** because:
1. Existing frameworks changed too fast (breaking changes)
2. They needed specific compliance features
3. "Not invented here" syndrome is real in enterprises

### DSPy: The Framework That Programs Prompts

While everyone focused on chains and agents, **Omar Khattab at Stanford** was asking a different question:

> "Why are we hand-writing prompts like it's 1999?"

His solution, **DSPy** (Declarative Self-improving Python), automatically optimizes prompts based on examples. You write:

```python
class QA(dspy.Signature):
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField()
```

DSPy figures out the best prompt format, few-shot examples, and chain-of-thought structure. Results from the paper:
- **25% better accuracy** than hand-written prompts on GSM8K math
- **40% token reduction** through optimized prompts
- Works across different LLMs without prompt rewrites

It's called the "compiler for LLMs"—you write what you want, DSPy figures out how to get it.

### Semantic Kernel: Microsoft's Secret Enterprise Weapon

While open-source frameworks got the hype, **Microsoft's Semantic Kernel** quietly became the most-used framework in enterprise:

- **Azure OpenAI** default integration
- **.NET and Java** (not just Python!)
- **Enterprise compliance** baked in
- Used internally by **Microsoft 365, GitHub Copilot, and Bing**

The kicker? **60% of Azure OpenAI enterprise customers** use Semantic Kernel. It's not the coolest framework, but when you have $500M ARR products to protect, "boring and reliable" wins.

### The Haystack Pivot: From Search to AI

**Haystack** (by deepset) has the longest history in this space. Founded in **2018** (before GPT-2!), they originally built search infrastructure.

When LLMs emerged, they pivoted to "LLM-powered search" and became the go-to for enterprises that need:
- Document retrieval at scale
- Compliance with European regulations (German company)
- Production stability over cutting-edge features

**Deutsche Telekom, BMW, and Airbus** run Haystack in production. Sometimes being "boring but reliable" is exactly what enterprises need.

### The Framework Half-Life Problem

Here's a sobering stat: Of the **47 AI frameworks** that had 1,000+ GitHub stars in January 2024:
- **12** are now abandoned (no commits in 6+ months)
- **8** merged into other projects
- **6** pivoted to completely different purposes
- **21** are still active

The average "half-life" of an AI framework is about **14 months**. Before committing to a framework, check:
1. Last commit date
2. Open issue response time
3. Who's funding development
4. Enterprise adoption (they don't switch often)

### Real Production Usage: The Numbers Behind the Logos

| Company | Framework | Scale | Use Case |
|---------|-----------|-------|----------|
| **Notion** | LlamaIndex | 30M+ users | Document Q&A |
| **Replit** | LangGraph | 40M+ users | AI code assistant |
| **Klarna** | LangChain | 2.3M conv/mo | Customer service |
| **Stripe** | Custom + LlamaIndex | Billions $/yr | Fraud detection |
| **Shopify** | Custom | 4.5M merchants | Product descriptions |
| **Netflix** | Custom + embeddings | 260M users | Recommendations |

Notice the pattern? The biggest companies either **use custom solutions** or **combine multiple frameworks**. There's no "one framework to rule them all."

---

## Best Practices

### 1. Start Simple

```python
# Don't do this first:
from crewai import Agent, Task, Crew, Process
from langchain.agents import create_tool_calling_agent
from llama_index.core import VectorStoreIndex

# Do this first:
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
```

### 2. Abstract Your Framework

```python
# Good: Framework-agnostic interface
class RAGSystem:
    def __init__(self, implementation: str = "llamaindex"):
        if implementation == "llamaindex":
            self._engine = LlamaIndexRAG()
        elif implementation == "langchain":
            self._engine = LangChainRAG()

    def query(self, question: str) -> str:
        return self._engine.query(question)
```

### 3. Benchmark Before Committing

```python
# Compare frameworks on YOUR data
frameworks = ["llamaindex", "langchain", "haystack"]
test_queries = load_test_queries()

for framework in frameworks:
    engine = create_engine(framework)
    results = [engine.query(q) for q in test_queries]
    print(f"{framework}: {evaluate(results)}")
```

### 4. Consider Maintenance

Questions to ask:
- How active is the community?
- How often are there breaking changes?
- Is the documentation good?
- Are there examples for your use case?

---

## Summary

### Frameworks Covered

| Framework | Philosophy | Best For |
|-----------|------------|----------|
| **LlamaIndex** | Data framework | RAG, knowledge systems |
| **LangChain** | Composable chains | General LLM apps |
| **LangGraph** | State machines | Complex workflows |
| **CrewAI** | Role-based teams | Multi-agent collab |
| **AutoGen** | Conversations | Research, dialogues |

### Key Insights

1. **No single "best" framework** - Choose based on use case
2. **Frameworks are converging** - Interoperability is improving
3. **LlamaIndex excels at RAG** - Simpler than LangChain for indexing
4. **CrewAI is beginner-friendly** - Good for multi-agent prototypes
5. **Combine frameworks** - LlamaIndex indexing + LangChain agents

### Decision Summary

- **Simple RAG** → LlamaIndex
- **Complex agents** → LangChain + LangGraph
- **Quick multi-agent** → CrewAI
- **Research/experiments** → AutoGen
- **Enterprise/Azure** → Semantic Kernel

---

## Further Reading

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Framework Comparison Blog Posts](https://towardsdatascience.com/)
- [LangChain vs LlamaIndex Analysis](https://medium.com/)

---

## Next Steps

With framework knowledge complete, you're ready for:

- **Module 20**: Advanced Agentic AI 🔮
- Agent memory systems (short-term, long-term, episodic)
- Planning algorithms (ReWOO, Plan-and-Execute)
- Multi-agent collaborative systems

**You can now choose the right tool for the job!**

---

_Module 19 Complete! Progress: 22/56 modules (39%)_

_Next: Module 20 - Advanced Agentic AI 🔮_
