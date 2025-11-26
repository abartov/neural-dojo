#!/usr/bin/env python3
"""
Module 19, Example 2: Framework Comparison

This example demonstrates:
1. Building the same RAG pipeline in LangChain vs LlamaIndex
2. Comparing code complexity and features
3. Benchmarking retrieval quality
4. Integration between frameworks
5. Framework selection decision making

Side-by-side comparison helps you choose the right tool.

Usage:
    python 02_framework_comparison.py

Requires:
    pip install langchain langchain-google-genai llama-index llama-index-llms-google
"""

import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# =============================================================================
# Check Available Frameworks
# =============================================================================

# LlamaIndex
try:
    from llama_index.core import VectorStoreIndex, Document as LIDocument, Settings
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False

# LangChain
try:
    from langchain_core.documents import Document as LCDocument
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# LLM
try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    LLM_AVAILABLE = bool(os.getenv("GOOGLE_API_KEY"))
except ImportError:
    LLM_AVAILABLE = False


# =============================================================================
# Sample Data (Same for Both Frameworks)
# =============================================================================

SAMPLE_DOCUMENTS = [
    {
        "title": "AI Framework Overview",
        "content": """
The AI framework landscape in 2024 is diverse and rapidly evolving.
LangChain provides composable building blocks for LLM applications,
including chains, agents, and memory systems. LlamaIndex focuses on
data indexing and retrieval, excelling at RAG implementations.

Both frameworks support multiple LLM providers including OpenAI,
Anthropic, Google, and open-source models via Ollama or HuggingFace.
The choice between them often depends on your primary use case.
        """
    },
    {
        "title": "RAG Architecture",
        "content": """
Retrieval-Augmented Generation (RAG) combines retrieval with generation.
The basic RAG pipeline consists of:
1. Document ingestion and chunking
2. Embedding generation
3. Vector storage
4. Query embedding
5. Similarity search
6. Context augmentation
7. LLM response generation

Both LangChain and LlamaIndex support this architecture, but with
different levels of abstraction and customization options.
        """
    },
    {
        "title": "Choosing a Framework",
        "content": """
When selecting an AI framework, consider:
- Primary use case (RAG vs agents vs general)
- Team expertise and learning curve
- Customization requirements
- Community and documentation
- Integration needs

LlamaIndex is often recommended for RAG-focused applications due to
its simpler API and built-in optimizations. LangChain is preferred
for complex agent workflows and tool integration scenarios.
        """
    }
]


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class BenchmarkResult:
    """Result from a benchmark run."""
    framework: str
    operation: str
    duration_ms: float
    success: bool
    details: Dict[str, Any]


@dataclass
class ComparisonResult:
    """Result from framework comparison."""
    query: str
    langchain_response: Optional[str]
    llamaindex_response: Optional[str]
    langchain_time_ms: float
    llamaindex_time_ms: float


# =============================================================================
# Part 1: LlamaIndex RAG Implementation
# =============================================================================

class LlamaIndexRAG:
    """RAG implementation using LlamaIndex."""

    def __init__(self):
        """Initialize LlamaIndex RAG."""
        self.index = None
        self.query_engine = None

    def ingest(self, documents: List[Dict]) -> BenchmarkResult:
        """Ingest documents into LlamaIndex."""
        start = time.time()

        if not LLAMAINDEX_AVAILABLE:
            return BenchmarkResult(
                framework="LlamaIndex",
                operation="ingest",
                duration_ms=0,
                success=False,
                details={"error": "LlamaIndex not installed"}
            )

        try:
            # Convert to LlamaIndex documents
            li_docs = [
                LIDocument(
                    text=doc["content"],
                    metadata={"title": doc["title"]}
                )
                for doc in documents
            ]

            # Create index (handles chunking and embedding internally)
            self.index = VectorStoreIndex.from_documents(li_docs)
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=2
            )

            duration = (time.time() - start) * 1000

            return BenchmarkResult(
                framework="LlamaIndex",
                operation="ingest",
                duration_ms=duration,
                success=True,
                details={
                    "num_documents": len(documents),
                    "index_type": "VectorStoreIndex"
                }
            )

        except Exception as e:
            return BenchmarkResult(
                framework="LlamaIndex",
                operation="ingest",
                duration_ms=(time.time() - start) * 1000,
                success=False,
                details={"error": str(e)}
            )

    def query(self, question: str) -> tuple:
        """Query the index."""
        start = time.time()

        if self.query_engine is None:
            return None, 0

        try:
            response = self.query_engine.query(question)
            duration = (time.time() - start) * 1000
            return str(response), duration
        except Exception as e:
            return f"Error: {e}", (time.time() - start) * 1000


# =============================================================================
# Part 2: LangChain RAG Implementation
# =============================================================================

class LangChainRAG:
    """RAG implementation using LangChain."""

    def __init__(self):
        """Initialize LangChain RAG."""
        self.documents = []
        self.chunks = []
        self.embeddings = None
        self.vectors = None

    def ingest(self, documents: List[Dict]) -> BenchmarkResult:
        """Ingest documents into LangChain."""
        start = time.time()

        if not LANGCHAIN_AVAILABLE:
            return BenchmarkResult(
                framework="LangChain",
                operation="ingest",
                duration_ms=0,
                success=False,
                details={"error": "LangChain not installed"}
            )

        try:
            # Convert to LangChain documents
            lc_docs = [
                LCDocument(
                    page_content=doc["content"],
                    metadata={"title": doc["title"]}
                )
                for doc in documents
            ]

            # Manual chunking (LangChain requires explicit splitting)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            self.chunks = splitter.split_documents(lc_docs)

            # Store for later querying
            self.documents = lc_docs

            duration = (time.time() - start) * 1000

            return BenchmarkResult(
                framework="LangChain",
                operation="ingest",
                duration_ms=duration,
                success=True,
                details={
                    "num_documents": len(documents),
                    "num_chunks": len(self.chunks)
                }
            )

        except Exception as e:
            return BenchmarkResult(
                framework="LangChain",
                operation="ingest",
                duration_ms=(time.time() - start) * 1000,
                success=False,
                details={"error": str(e)}
            )

    def query(self, question: str) -> tuple:
        """Query using simple keyword matching (without vector store)."""
        start = time.time()

        if not self.chunks:
            return None, 0

        try:
            # Simple retrieval (keyword matching for demo without embeddings)
            question_lower = question.lower()
            relevant_chunks = []

            for chunk in self.chunks:
                # Score based on word overlap
                chunk_words = set(chunk.page_content.lower().split())
                question_words = set(question_lower.split())
                overlap = len(chunk_words & question_words)
                if overlap > 0:
                    relevant_chunks.append((overlap, chunk))

            # Get top 2 chunks
            relevant_chunks.sort(reverse=True, key=lambda x: x[0])
            top_chunks = [c[1] for c in relevant_chunks[:2]]

            # Simple response (without LLM for demo)
            if top_chunks:
                context = "\n".join([c.page_content[:200] for c in top_chunks])
                response = f"Based on the documents:\n{context[:300]}..."
            else:
                response = "No relevant information found."

            duration = (time.time() - start) * 1000
            return response, duration

        except Exception as e:
            return f"Error: {e}", (time.time() - start) * 1000


# =============================================================================
# Part 3: Side-by-Side Comparison
# =============================================================================

def demo_code_comparison():
    """Show code complexity comparison."""
    print("\n" + "="*60)
    print("Part 1: Code Complexity Comparison")
    print("="*60)

    print("""
    LlamaIndex RAG (Minimal):
    ─────────────────────────
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    response = index.as_query_engine().query("What is X?")

    Lines of code: 4


    LangChain RAG (Minimal):
    ────────────────────────
    from langchain_community.document_loaders import DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.chains import RetrievalQA

    loader = DirectoryLoader("./data")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
    chunks = splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        retriever=vectorstore.as_retriever()
    )
    response = qa_chain.invoke("What is X?")

    Lines of code: 12


    Observation: LlamaIndex requires ~70% less code for basic RAG.
                 LangChain offers more explicit control over each step.
    """)


def demo_benchmark():
    """Benchmark both frameworks."""
    print("\n" + "="*60)
    print("Part 2: Performance Benchmark")
    print("="*60)

    # Initialize frameworks
    li_rag = LlamaIndexRAG()
    lc_rag = LangChainRAG()

    # Ingest
    print("\n  Ingestion Benchmark:")
    print("-" * 40)

    li_result = li_rag.ingest(SAMPLE_DOCUMENTS)
    print(f"    LlamaIndex: {li_result.duration_ms:.1f}ms - {'Success' if li_result.success else li_result.details}")

    lc_result = lc_rag.ingest(SAMPLE_DOCUMENTS)
    print(f"    LangChain:  {lc_result.duration_ms:.1f}ms - {'Success' if lc_result.success else lc_result.details}")

    # Query
    print("\n  Query Benchmark:")
    print("-" * 40)

    test_queries = [
        "What are the main AI frameworks?",
        "How does RAG work?",
        "How to choose between frameworks?"
    ]

    for query in test_queries:
        print(f"\n    Q: {query[:40]}...")

        li_response, li_time = li_rag.query(query)
        lc_response, lc_time = lc_rag.query(query)

        print(f"      LlamaIndex: {li_time:.1f}ms")
        print(f"      LangChain:  {lc_time:.1f}ms")


# =============================================================================
# Part 4: Feature Comparison
# =============================================================================

def demo_feature_comparison():
    """Compare features between frameworks."""
    print("\n" + "="*60)
    print("Part 3: Feature Comparison")
    print("="*60)

    print("""
    ┌─────────────────────────┬───────────────┬───────────────┐
    │ Feature                 │ LlamaIndex    │ LangChain     │
    ├─────────────────────────┼───────────────┼───────────────┤
    │ Basic RAG               │ ✅ Excellent  │ ✅ Good       │
    │ Data Connectors         │ ✅ 150+       │ ✅ 100+       │
    │ Index Types             │ ✅ Many       │ ⚠️ Vector only│
    │ Query Optimization      │ ✅ Built-in   │ ⚠️ Manual     │
    │ Agent Support           │ ⚠️ Basic     │ ✅ Excellent  │
    │ Tool Integration        │ ⚠️ Limited   │ ✅ Extensive  │
    │ Memory Systems          │ ⚠️ Basic     │ ✅ Advanced   │
    │ Chains/Workflows        │ ⚠️ Limited   │ ✅ Excellent  │
    │ Learning Curve          │ ✅ Lower      │ ⚠️ Steeper   │
    │ Documentation           │ ✅ Good       │ ✅ Good       │
    │ Community Size          │ ⚠️ Growing   │ ✅ Large      │
    │ Breaking Changes        │ ⚠️ Frequent  │ ⚠️ Frequent  │
    └─────────────────────────┴───────────────┴───────────────┘

    Summary:
    • LlamaIndex: Best for RAG-focused applications
    • LangChain: Best for complex agents and workflows
    • Both: Can be used together effectively
    """)


# =============================================================================
# Part 5: Integration Example
# =============================================================================

def demo_integration():
    """Show how to use both frameworks together."""
    print("\n" + "="*60)
    print("Part 4: Framework Integration")
    print("="*60)

    print("""
    Using LlamaIndex + LangChain Together:
    ─────────────────────────────────────

    # LlamaIndex for indexing
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    # Wrap as LangChain tool
    from langchain.tools import Tool

    def search_docs(query: str) -> str:
        response = query_engine.query(query)
        return str(response)

    search_tool = Tool(
        name="document_search",
        func=search_docs,
        description="Search internal documents for information"
    )

    # Use in LangChain agent
    from langchain.agents import create_tool_calling_agent, AgentExecutor

    agent = create_tool_calling_agent(llm, [search_tool], prompt)
    executor = AgentExecutor(agent=agent, tools=[search_tool])

    result = executor.invoke({
        "input": "What do our documents say about RAG?"
    })


    Benefits of Integration:
    ─────────────────────────
    1. LlamaIndex handles sophisticated data indexing
    2. LangChain provides agent orchestration
    3. Best of both worlds for complex applications
    4. Clear separation of concerns
    """)


# =============================================================================
# Part 6: Decision Framework
# =============================================================================

def demo_decision_framework():
    """Present a decision framework for choosing frameworks."""
    print("\n" + "="*60)
    print("Part 5: Decision Framework")
    print("="*60)

    print("""
    Use This Decision Tree:
    ───────────────────────

                    What's your primary use case?
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    RAG/Search           Agents/Tools          Both/Complex
        │                     │                     │
        ▼                     ▼                     ▼
    LlamaIndex           LangChain           Integration
        │                     │                     │
        ▼                     ▼                     ▼
    Simple setup         Flexible            LlamaIndex +
    Fast iteration       Customizable        LangChain


    Quick Decision Guide:
    ─────────────────────

    Choose LlamaIndex if:
    • RAG is your primary use case
    • You want the simplest possible setup
    • You're working with many data sources
    • Query optimization is important
    • You prefer opinionated defaults

    Choose LangChain if:
    • Building complex agent systems
    • Need extensive tool integration
    • Require custom chains/workflows
    • Want maximum flexibility
    • Building stateful applications (with LangGraph)

    Choose Both if:
    • Complex application with heavy data + agents
    • Want best indexing + best orchestration
    • Team has capacity to maintain both
    • Different parts of app have different needs
    """)


# =============================================================================
# Part 7: Code Lines Comparison
# =============================================================================

def count_lines_comparison():
    """Count and compare lines of code for various operations."""
    print("\n" + "="*60)
    print("Part 6: Lines of Code Comparison")
    print("="*60)

    comparisons = [
        {
            "operation": "Basic RAG Pipeline",
            "llamaindex": 4,
            "langchain": 12
        },
        {
            "operation": "Document Loading",
            "llamaindex": 1,
            "langchain": 3
        },
        {
            "operation": "Chunking",
            "llamaindex": 0,  # Automatic
            "langchain": 4
        },
        {
            "operation": "Index Creation",
            "llamaindex": 1,
            "langchain": 3
        },
        {
            "operation": "Query Interface",
            "llamaindex": 2,
            "langchain": 8
        },
        {
            "operation": "Agent with Tools",
            "llamaindex": 15,
            "langchain": 12
        },
        {
            "operation": "Custom Memory",
            "llamaindex": 10,
            "langchain": 6
        }
    ]

    print("\n  Lines of Code by Operation:")
    print("-" * 50)
    print(f"  {'Operation':<25} {'LlamaIndex':>10} {'LangChain':>10}")
    print("-" * 50)

    li_total = 0
    lc_total = 0

    for comp in comparisons:
        print(f"  {comp['operation']:<25} {comp['llamaindex']:>10} {comp['langchain']:>10}")
        li_total += comp['llamaindex']
        lc_total += comp['langchain']

    print("-" * 50)
    print(f"  {'Total':<25} {li_total:>10} {lc_total:>10}")
    print()

    print(f"  LlamaIndex requires ~{((lc_total - li_total) / lc_total * 100):.0f}% less code for RAG tasks")
    print(f"  LangChain requires less code for agents/memory tasks")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*60)
    print("Module 19, Example 2: Framework Comparison")
    print("="*60)

    status = []
    if LLAMAINDEX_AVAILABLE:
        status.append("LlamaIndex: Available")
    else:
        status.append("LlamaIndex: Not installed")

    if LANGCHAIN_AVAILABLE:
        status.append("LangChain: Available")
    else:
        status.append("LangChain: Not installed")

    print(f"\nFramework Status: {', '.join(status)}")

    # Run all demos
    demo_code_comparison()
    demo_benchmark()
    demo_feature_comparison()
    demo_integration()
    demo_decision_framework()
    count_lines_comparison()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    Key Takeaways:

    1. LLAMAINDEX excels at RAG
       - Simpler API, fewer lines of code
       - Built-in chunking and optimization
       - Many index types

    2. LANGCHAIN excels at agents
       - More flexible and customizable
       - Better tool integration
       - Superior memory systems

    3. THEY COMPLEMENT EACH OTHER
       - Use LlamaIndex for data layer
       - Use LangChain for orchestration
       - Integrate via tool wrapping

    4. CHOOSE BASED ON USE CASE
       - RAG-focused → LlamaIndex
       - Agent-focused → LangChain
       - Complex apps → Both

    Next: Explore multi-agent frameworks (CrewAI, AutoGen)!
    """)


if __name__ == "__main__":
    main()
