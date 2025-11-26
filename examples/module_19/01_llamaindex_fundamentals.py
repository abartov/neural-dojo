#!/usr/bin/env python3
"""
Module 19, Example 1: LlamaIndex Fundamentals

This example demonstrates:
1. Document loading and ingestion
2. Index creation (Vector, Summary, Keyword)
3. Query engines and chat engines
4. Response modes and retrieval settings
5. Node parsing and transformations

LlamaIndex is a data framework for LLM applications,
optimized for RAG and knowledge management.

Usage:
    python 01_llamaindex_fundamentals.py

Requires:
    pip install llama-index llama-index-llms-google
"""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Check for LlamaIndex
try:
    from llama_index.core import (
        VectorStoreIndex,
        SummaryIndex,
        SimpleDirectoryReader,
        Document,
        Settings,
        StorageContext,
        load_index_from_storage
    )
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.schema import TextNode
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    print("LlamaIndex not installed. Install with: pip install llama-index")

# Check for LLM
try:
    from llama_index.llms.google import GoogleGenerativeAI
    from llama_index.embeddings.google import GoogleGenerativeAIEmbedding
    LLM_AVAILABLE = bool(os.getenv("GOOGLE_API_KEY"))
except ImportError:
    LLM_AVAILABLE = False


# =============================================================================
# Sample Documents
# =============================================================================

SAMPLE_DOCUMENTS = [
    {
        "title": "Introduction to LlamaIndex",
        "content": """
LlamaIndex is a data framework for building LLM applications.
It provides tools for data ingestion, indexing, and querying.
The framework excels at RAG (Retrieval-Augmented Generation) applications.

Key features include:
- 150+ data connectors for various sources
- Multiple index types (Vector, Summary, Tree, Keyword)
- Flexible query engines
- Built-in response synthesis
- Easy integration with vector databases

LlamaIndex was created by Jerry Liu in 2022, originally called GPT Index.
The philosophy is that your data is your competitive advantage.
        """
    },
    {
        "title": "LlamaIndex vs LangChain",
        "content": """
LlamaIndex and LangChain serve different purposes in the LLM ecosystem.

LlamaIndex focuses on:
- Data ingestion and indexing
- RAG pipelines
- Knowledge management
- Query optimization

LangChain focuses on:
- Chains and agents
- Tool integration
- Memory management
- Complex workflows

Many developers use both: LlamaIndex for data management and
LangChain for agent orchestration. They complement each other well.
        """
    },
    {
        "title": "Building RAG with LlamaIndex",
        "content": """
RAG (Retrieval-Augmented Generation) is a technique that enhances
LLM responses by providing relevant context from a knowledge base.

Steps to build RAG with LlamaIndex:
1. Load documents using data connectors
2. Parse documents into nodes (chunks)
3. Create embeddings for each node
4. Store in a vector index
5. Query with natural language
6. Retrieve relevant nodes
7. Synthesize response using LLM

LlamaIndex handles most of this automatically with just a few lines of code.
The VectorStoreIndex is the most common choice for RAG applications.
        """
    }
]


# =============================================================================
# Helper Functions
# =============================================================================

def create_sample_documents() -> List:
    """Create LlamaIndex Document objects from sample data."""
    if not LLAMAINDEX_AVAILABLE:
        return []

    documents = []
    for doc in SAMPLE_DOCUMENTS:
        documents.append(Document(
            text=doc["content"],
            metadata={"title": doc["title"]}
        ))
    return documents


def setup_llm():
    """Configure LlamaIndex to use Google Gemini."""
    if not LLAMAINDEX_AVAILABLE:
        return

    if LLM_AVAILABLE:
        # Use Google Gemini
        llm = GoogleGenerativeAI(model="gemini-2.0-flash-exp")
        embed_model = GoogleGenerativeAIEmbedding(model_name="models/embedding-001")
        Settings.llm = llm
        Settings.embed_model = embed_model
        print("  Using Google Gemini for LLM and embeddings")
    else:
        # Will use default mock embeddings for demo
        print("  No API key - using mock embeddings (set GOOGLE_API_KEY for real)")


# =============================================================================
# Part 1: Document Loading
# =============================================================================

def demo_document_loading():
    """Demonstrate document loading in LlamaIndex."""
    print("\n" + "="*60)
    print("Part 1: Document Loading")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE:
        print("Skipping - LlamaIndex not available")
        return []

    print("""
    LlamaIndex provides multiple ways to load documents:

    1. SimpleDirectoryReader - Load from files
    2. Custom Document objects - Programmatic creation
    3. Data connectors - 150+ integrations (web, DB, APIs)
    """)

    # Create documents from sample data
    documents = create_sample_documents()
    print(f"\n  Created {len(documents)} documents:")
    for doc in documents:
        title = doc.metadata.get("title", "Untitled")
        print(f"    - {title}: {len(doc.text)} characters")

    # Show document structure
    print("\n  Document structure:")
    print(f"    - text: The document content")
    print(f"    - metadata: Dictionary of metadata (title, source, etc.)")
    print(f"    - doc_id: Unique identifier")

    return documents


# =============================================================================
# Part 2: Node Parsing
# =============================================================================

def demo_node_parsing(documents: List):
    """Demonstrate node parsing (chunking) in LlamaIndex."""
    print("\n" + "="*60)
    print("Part 2: Node Parsing (Chunking)")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE or not documents:
        print("Skipping - LlamaIndex not available or no documents")
        return []

    print("""
    Documents are split into "nodes" for indexing:

    - Nodes are chunks of text with metadata
    - SentenceSplitter maintains sentence boundaries
    - Each node tracks its parent document
    - Overlapping chunks improve retrieval
    """)

    # Create node parser
    parser = SentenceSplitter(
        chunk_size=256,      # Target chunk size in tokens
        chunk_overlap=50     # Overlap between chunks
    )

    # Parse documents into nodes
    nodes = parser.get_nodes_from_documents(documents)

    print(f"\n  Parsed {len(documents)} documents into {len(nodes)} nodes:")
    for i, node in enumerate(nodes[:5], 1):  # Show first 5
        preview = node.text[:60].replace("\n", " ")
        print(f"    Node {i}: '{preview}...'")

    if len(nodes) > 5:
        print(f"    ... and {len(nodes) - 5} more nodes")

    return nodes


# =============================================================================
# Part 3: Index Creation
# =============================================================================

def demo_index_creation(documents: List):
    """Demonstrate different index types in LlamaIndex."""
    print("\n" + "="*60)
    print("Part 3: Index Creation")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE or not documents:
        print("Skipping - LlamaIndex not available or no documents")
        return None

    setup_llm()

    print("""
    LlamaIndex supports multiple index types:

    1. VectorStoreIndex - Semantic similarity search
       Best for: General RAG, semantic queries

    2. SummaryIndex - Summarizes all documents
       Best for: Overview queries, "tell me everything"

    3. KeywordTableIndex - Keyword extraction
       Best for: Exact match queries

    4. TreeIndex - Hierarchical summarization
       Best for: Large document collections
    """)

    # Create Vector Index
    print("\n  Creating VectorStoreIndex...")
    try:
        vector_index = VectorStoreIndex.from_documents(
            documents,
            show_progress=True
        )
        print("    VectorStoreIndex created")
    except Exception as e:
        print(f"    Error creating VectorStoreIndex: {e}")
        vector_index = None

    # Create Summary Index
    print("\n  Creating SummaryIndex...")
    try:
        summary_index = SummaryIndex.from_documents(documents)
        print("    SummaryIndex created")
    except Exception as e:
        print(f"    Error creating SummaryIndex: {e}")
        summary_index = None

    return vector_index


# =============================================================================
# Part 4: Query Engines
# =============================================================================

def demo_query_engines(index):
    """Demonstrate query engine functionality."""
    print("\n" + "="*60)
    print("Part 4: Query Engines")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE or index is None:
        print("Skipping - LlamaIndex not available or no index")
        return

    print("""
    Query engines process natural language queries:

    Parameters:
    - similarity_top_k: Number of nodes to retrieve
    - response_mode: How to synthesize response
      - "compact": Concatenate and summarize
      - "refine": Iteratively refine answer
      - "tree_summarize": Hierarchical summary
      - "no_text": Return nodes only
    """)

    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=2,
        response_mode="compact"
    )

    # Test queries
    test_queries = [
        "What is LlamaIndex?",
        "How does LlamaIndex compare to LangChain?",
        "What are the steps to build RAG?"
    ]

    print("\n  Testing queries:")
    print("-" * 40)

    for query in test_queries:
        print(f"\n  Q: {query}")
        try:
            response = query_engine.query(query)
            # Truncate long responses for display
            answer = str(response)[:200]
            if len(str(response)) > 200:
                answer += "..."
            print(f"  A: {answer}")
        except Exception as e:
            print(f"  Error: {e}")


# =============================================================================
# Part 5: Chat Engines
# =============================================================================

def demo_chat_engines(index):
    """Demonstrate chat engine with conversation memory."""
    print("\n" + "="*60)
    print("Part 5: Chat Engines")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE or index is None:
        print("Skipping - LlamaIndex not available or no index")
        return

    print("""
    Chat engines maintain conversation history:

    - Tracks previous messages
    - Context-aware responses
    - Can reference earlier in conversation
    - Multiple chat modes available
    """)

    # Create chat engine
    chat_engine = index.as_chat_engine(
        chat_mode="context",  # or "condense_question", "react"
        verbose=False
    )

    # Simulated conversation
    conversation = [
        "What is LlamaIndex used for?",
        "How does it handle data?",
        "Can you give me more details on indexing?"
    ]

    print("\n  Simulated conversation:")
    print("-" * 40)

    for message in conversation:
        print(f"\n  User: {message}")
        try:
            response = chat_engine.chat(message)
            answer = str(response)[:200]
            if len(str(response)) > 200:
                answer += "..."
            print(f"  Assistant: {answer}")
        except Exception as e:
            print(f"  Error: {e}")

    # Reset chat
    chat_engine.reset()
    print("\n  Chat history reset")


# =============================================================================
# Part 6: Index Persistence
# =============================================================================

def demo_persistence(index):
    """Demonstrate saving and loading indexes."""
    print("\n" + "="*60)
    print("Part 6: Index Persistence")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE or index is None:
        print("Skipping - LlamaIndex not available or no index")
        return

    print("""
    Indexes can be saved and loaded:

    - Avoid re-indexing on every run
    - Save embeddings to disk
    - Use with vector databases
    - Storage contexts for management
    """)

    storage_dir = "./.llamaindex_demo"

    # Save index
    print(f"\n  Saving index to {storage_dir}...")
    try:
        index.storage_context.persist(persist_dir=storage_dir)
        print("    Index saved!")

        # Show saved files
        if Path(storage_dir).exists():
            files = list(Path(storage_dir).glob("*"))
            print(f"\n  Saved files:")
            for f in files:
                print(f"    - {f.name}")
    except Exception as e:
        print(f"    Error saving: {e}")

    # Load index
    print(f"\n  Loading index from {storage_dir}...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        loaded_index = load_index_from_storage(storage_context)
        print("    Index loaded!")

        # Quick test
        query_engine = loaded_index.as_query_engine()
        response = query_engine.query("What is LlamaIndex?")
        print(f"\n  Test query on loaded index:")
        print(f"    Q: What is LlamaIndex?")
        print(f"    A: {str(response)[:100]}...")
    except Exception as e:
        print(f"    Error loading: {e}")


# =============================================================================
# Part 7: Response Synthesis Modes
# =============================================================================

def demo_response_modes(documents: List):
    """Demonstrate different response synthesis modes."""
    print("\n" + "="*60)
    print("Part 7: Response Synthesis Modes")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE or not documents:
        print("Skipping - LlamaIndex not available or no documents")
        return

    print("""
    LlamaIndex offers different response synthesis strategies:

    1. compact: Stuff all context into one prompt
       - Fast, good for small contexts
       - May truncate with large results

    2. refine: Iteratively improve answer
       - Better quality, slower
       - Good for complex questions

    3. tree_summarize: Hierarchical summarization
       - Best for large contexts
       - Builds summary tree

    4. no_text: Return raw nodes
       - For custom processing
       - Debugging retrieval
    """)

    # Create index
    try:
        index = VectorStoreIndex.from_documents(documents)

        modes = ["compact", "tree_summarize"]
        query = "Summarize the key points about LlamaIndex"

        print(f"\n  Query: '{query}'")
        print("-" * 40)

        for mode in modes:
            print(f"\n  Mode: {mode}")
            try:
                engine = index.as_query_engine(response_mode=mode)
                response = engine.query(query)
                print(f"    Response: {str(response)[:150]}...")
            except Exception as e:
                print(f"    Error: {e}")

    except Exception as e:
        print(f"  Error: {e}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*60)
    print("Module 19, Example 1: LlamaIndex Fundamentals")
    print("="*60)

    if not LLAMAINDEX_AVAILABLE:
        print("\n*** LlamaIndex is not installed ***")
        print("Install with: pip install llama-index llama-index-llms-google")
        print("\nShowing concepts without running code...")
        return

    # Run demos
    documents = demo_document_loading()
    nodes = demo_node_parsing(documents)
    index = demo_index_creation(documents)
    demo_query_engines(index)
    demo_chat_engines(index)
    demo_persistence(index)
    demo_response_modes(documents)

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    Key LlamaIndex concepts:

    1. DOCUMENTS: Raw text with metadata
       - Load from files, web, databases
       - Or create programmatically

    2. NODES: Chunks of documents
       - SentenceSplitter maintains boundaries
       - Configurable size and overlap

    3. INDEXES: Data structures for retrieval
       - VectorStoreIndex for semantic search
       - SummaryIndex for summarization
       - KeywordTableIndex for exact match

    4. QUERY ENGINES: Natural language interface
       - Configurable retrieval (top_k)
       - Multiple response modes

    5. CHAT ENGINES: Conversational interface
       - Maintains history
       - Context-aware responses

    6. PERSISTENCE: Save and load indexes
       - Avoid re-indexing
       - Production-ready

    Next: Compare LlamaIndex with LangChain!
    """)


if __name__ == "__main__":
    main()
