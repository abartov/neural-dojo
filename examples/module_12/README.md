# Module 12 Deliverable: Production RAG Pipeline

**Build AI systems that actually know your data - not just hallucinate about it.**

## Features

- 🔄 **4 Chunking Strategies**: Fixed, Sentence, Semantic, Recursive
- 🔍 **Vector Search**: In-memory store (production: Qdrant/Pinecone)
- 📊 **Evaluation Metrics**: Recall@K, MRR, query analysis
- 💾 **JSON Persistence**: Save/load pipeline state
- 🏗️ **Production Architecture**: Swap components for production use

## Quick Start

```bash
# Basic RAG demonstration
python deliverable_rag_pipeline.py demo1

# Compare chunking strategies
python deliverable_rag_pipeline.py demo2

# Evaluation metrics
python deliverable_rag_pipeline.py demo3

# Full production pipeline
python deliverable_rag_pipeline.py demo4

# Run all demos
python deliverable_rag_pipeline.py all
```

## Demo Overview

### Demo 1: Basic RAG Pipeline
Shows the core RAG loop:
1. Ingest documents → Chunk → Embed → Store
2. Query → Embed → Search → Retrieve
3. Generate answer with sources

```
📥 Ingesting 4 documents...
  📄 docs/authentication.md: 4 chunks
  📄 docs/deployment.md: 3 chunks
  📄 docs/api-reference.md: 4 chunks
  📄 docs/troubleshooting.md: 5 chunks
✅ Ingested 16 total chunks
```

### Demo 2: Chunking Comparison
Compares chunking strategies on the same text:

| Strategy | Chunks | Avg Size | Coherence |
|----------|--------|----------|-----------|
| Fixed (300) | 8 | 280 | ❌ Breaks mid-sentence |
| Sentence (3) | 5 | 350 | ✅ Respects sentences |
| Semantic (300) | 4 | 380 | ✅ Keeps paragraphs |
| Recursive (300) | 5 | 320 | ✅ Best of all worlds |

### Demo 3: Evaluation Metrics
Measures retrieval quality:

```
📊 Overall Metrics:
  Queries evaluated: 4
  Average Recall@1: 75.00%
  Average Recall@3: 87.50%
  Average Recall@5: 100.00%
  Average MRR: 0.833
```

### Demo 4: Full Pipeline
Production-ready RAG with:
- Recursive chunking (optimal size)
- Query processing with timing
- Source attribution
- Performance statistics

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RAG Pipeline                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Indexing (Offline)                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐ │
│  │Documents│→ │ Chunker │→ │Embedder │→ │VectorStore│ │
│  └─────────┘  └─────────┘  └─────────┘  └───────────┘ │
│                                                         │
│  Retrieval (Online)                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐ │
│  │  Query  │→ │Embedder │→ │ Search  │→ │  Top-K    │ │
│  └─────────┘  └─────────┘  └─────────┘  └───────────┘ │
│                                                         │
│  Generation (Online)                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ Context │→ │  LLM    │→ │ Answer  │                │
│  └─────────┘  └─────────┘  └─────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Chunking Strategies

### Fixed Chunking
```python
chunker = FixedChunker(chunk_size=500, overlap=50)
```
- Simple, predictable sizes
- May break mid-sentence
- Good for uniform content

### Sentence Chunking
```python
chunker = SentenceChunker(sentences_per_chunk=5)
```
- Respects sentence boundaries
- Variable sizes
- Good for prose

### Semantic Chunking
```python
chunker = SemanticChunker(max_chunk_size=500)
```
- Splits on paragraphs
- Preserves semantic units
- Good for documentation

### Recursive Chunking
```python
chunker = RecursiveChunker(chunk_size=500)
```
- Tries multiple separators
- Best balance of size and coherence
- Good for mixed content

## Evaluation Metrics

### Recall@K
"Of the relevant documents, how many did we retrieve in top K?"

```python
recall = evaluator.recall_at_k(query, relevant_doc_ids, k_values=[1, 3, 5])
# recall = {1: 0.5, 3: 1.0, 5: 1.0}
```

### Mean Reciprocal Rank (MRR)
"How high is the first relevant document ranked?"

```python
mrr = evaluator.mrr(query, relevant_doc_ids)
# mrr = 0.5 (first relevant at position 2)
```

## Production Upgrade Path

Replace demo components with production-ready alternatives:

```python
# Demo (current)
pipeline = RAGPipeline(
    chunker=SemanticChunker(),
    embedder=SimpleEmbedder(),      # Pseudo-embeddings
    vector_store=SimpleVectorStore() # In-memory
)

# Production
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

pipeline = RAGPipeline(
    chunker=RecursiveChunker(chunk_size=400),
    embedder=SentenceTransformer('all-MiniLM-L6-v2'),
    vector_store=QdrantVectorStore(
        client=QdrantClient("localhost", port=6333)
    )
)
```

## Sample Output

```
🔍 Query: How do I configure JWT authentication?
──────────────────────────────────────────────────
📚 Retrieved sources:
   [1] docs/authentication.md
       Relevance: ████████████████████ 95.2%
   [2] docs/api-reference.md
       Relevance: ████████████████ 82.1%
   [3] docs/troubleshooting.md
       Relevance: ████████████ 61.3%

⏱️  Total time: 2.3ms
```

## File Structure

```
examples/module_12/
├── deliverable_rag_pipeline.py   # Main deliverable (700+ lines)
├── DELIVERABLE_README.md         # This file
├── requirements.txt              # Dependencies
└── .gitignore                    # Excludes .rag_pipeline/
```

## Storage

Results are persisted in `.rag_pipeline/`:
- `vector_store.json` - Indexed chunks with embeddings
- `evaluation_results.json` - Evaluation metrics

---

**Time**: ~3-4 hours | **Lines**: 700+ | **Author**: Neural Dojo
