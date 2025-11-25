# Module 14: Advanced RAG Patterns

This directory contains examples for advanced retrieval-augmented generation patterns that improve upon basic RAG systems.

## Overview

Basic RAG (Module 12) works, but has limitations:
- Semantic gaps between queries and documents
- Missing context from surrounding text
- "Close but not best" retrieval results
- No self-evaluation of retrieval quality

**Advanced patterns solve these problems!**

## Examples

### 1. HyDE Search (`01_hyde_search.py`)

**Hypothetical Document Embeddings** - Bridge the query-document language gap.

```bash
python 01_hyde_search.py
```

**Key Concept**: Generate a hypothetical answer, then search for similar real documents.

```
Query: "Why is my code slow?"
↓
Generate hypothetical: "Performance issues commonly stem from..."
↓
Search for docs similar to the hypothetical (not the query!)
```

### 2. Hybrid Search (`02_hybrid_search.py`)

**BM25 + Semantic** - Best of lexical and semantic search.

```bash
python 02_hybrid_search.py
```

**Key Concept**: Combine exact term matching (BM25) with meaning-based search (embeddings).

```
Query: "error code 0x80070005"
↓
BM25: Finds exact code matches ✓
Semantic: Finds related error docs ✓
Hybrid: Gets both! ✓✓
```

### 3. Cross-Encoder Reranking (`03_reranking.py`)

**Two-stage retrieval** - Fast recall, precise reranking.

```bash
python 03_reranking.py
```

**Key Concept**: Use fast bi-encoder for candidates, accurate cross-encoder for final ranking.

```
Stage 1 (Bi-encoder): 1000 docs → 50 candidates (fast)
Stage 2 (Cross-encoder): 50 → 5 final results (accurate)
```

### 4. Advanced RAG Toolkit (Deliverable)

**Full pipeline** combining all patterns.

```bash
python deliverable_advanced_rag.py demo1  # Compare all methods
python deliverable_advanced_rag.py demo2  # HyDE deep dive
python deliverable_advanced_rag.py demo3  # Production pipeline
python deliverable_advanced_rag.py benchmark  # Performance comparison
```

## Prerequisites

```bash
pip install -r requirements.txt
```

Required:
- `anthropic` - For HyDE generation
- `sentence-transformers` - For embeddings and cross-encoders
- `rank-bm25` - For BM25 lexical search
- `numpy` - Numerical operations

## Pattern Selection Guide

| Pattern | When to Use | Latency Impact |
|---------|-------------|----------------|
| **HyDE** | Q&A with question/answer mismatch | +200-500ms |
| **Hybrid** | Mixed keyword/semantic queries | +10-50ms |
| **Reranking** | When precision matters | +50-200ms |
| **GraphRAG** | Connected knowledge domains | +100-300ms |

## Key Takeaways

1. **HyDE**: Bridges query-document language gap via hypothetical generation
2. **Hybrid Search**: Combines BM25 (exact) + semantic (meaning)
3. **Reranking**: Two-stage retrieval balances speed and accuracy
4. **Combine Patterns**: Production RAG often uses multiple patterns together

## Further Reading

- [HyDE Paper](https://arxiv.org/abs/2212.10496)
- [Self-RAG Paper](https://arxiv.org/abs/2310.11511)
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
- [MTEB Embedding Benchmarks](https://huggingface.co/spaces/mteb/leaderboard)

---

**Time**: 6-7 hours | **Module**: 14 of 56 | **Phase**: 3 - Vector Search & RAG
