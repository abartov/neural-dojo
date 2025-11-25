# Module 14 Deliverable: Advanced RAG Toolkit

**Transform basic RAG into production-grade retrieval with HyDE, Hybrid Search, and Reranking.**

## Features

- **HyDE Search**: Generate hypothetical documents to bridge query-document gap
- **Hybrid Search**: Combine BM25 lexical + semantic embedding search
- **Cross-Encoder Reranking**: Two-stage retrieval for precision
- **Self-RAG Critique**: Filter irrelevant results with LLM
- **Production Pipeline**: Combine all patterns with timing analysis
- **Benchmarking**: Compare methods performance

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (for HyDE and generation features)
export ANTHROPIC_API_KEY="your-key"

# Run demos
python deliverable_advanced_rag.py demo1      # Compare all methods
python deliverable_advanced_rag.py demo2      # HyDE deep dive
python deliverable_advanced_rag.py demo3      # Production pipeline
python deliverable_advanced_rag.py benchmark  # Performance comparison
```

## Advanced RAG Patterns Explained

### 1. HyDE (Hypothetical Document Embeddings)

**Problem**: User queries use different language than documents.
```
Query: "Why is my code slow?"
Docs:  "Performance optimization techniques include..."
```

**Solution**: Generate a hypothetical answer, search for similar docs.
```
Query → Generate Hypothetical → Embed → Search
```

**Best for**: Q&A where queries are questions, docs are statements.

### 2. Hybrid Search (BM25 + Semantic)

**Problem**: Semantic misses exact matches, BM25 misses meaning.
```
Query: "error 0x80070005"
Semantic: Returns docs about "error handling" ❌
BM25: Finds exact code matches ✓
```

**Solution**: Combine both with weighted scoring.
```
Hybrid Score = α × Semantic + (1-α) × BM25
```

**Best for**: Mixed keyword/natural language queries.

### 3. Cross-Encoder Reranking

**Problem**: Bi-encoders are fast but less accurate.
```
Bi-encoder: Query and doc encoded separately
Cross-encoder: Query+doc encoded together (more accurate!)
```

**Solution**: Two-stage retrieval.
```
Stage 1: Bi-encoder → 50 candidates (fast)
Stage 2: Cross-encoder → 5 final (accurate)
```

**Best for**: When precision matters more than latency.

### 4. Self-RAG Critique

**Problem**: Basic RAG blindly uses whatever is retrieved.

**Solution**: LLM evaluates relevance before generation.
```
Retrieve → Critique ("Is this relevant?") → Generate
```

**Best for**: High-stakes applications (legal, medical, financial).

## Production Pipeline

The toolkit combines all patterns:

```python
from deliverable_advanced_rag import AdvancedRAGToolkit

toolkit = AdvancedRAGToolkit(documents)

result = toolkit.production_pipeline(
    query="How do I optimize database queries?",
    k=5,
    use_hyde=True,
    use_hybrid=True,
    use_rerank=True,
    use_self_critique=False
)

print(result.answer)
print(f"Time: {result.total_time_ms}ms")
```

## Benchmark Results

| Method | Avg Time | Quality |
|--------|----------|---------|
| BM25 | ~5ms | ⭐⭐ |
| Semantic | ~20ms | ⭐⭐⭐ |
| Hybrid | ~25ms | ⭐⭐⭐⭐ |
| +Rerank | ~80ms | ⭐⭐⭐⭐⭐ |
| HyDE | ~500ms | ⭐⭐⭐⭐⭐ |

## Pattern Selection Guide

| Scenario | Recommended Pattern |
|----------|-------------------|
| Fast Q&A with keywords | Hybrid Search |
| Technical documentation | HyDE + Rerank |
| High-stakes applications | Full pipeline + Self-RAG |
| Real-time autocomplete | BM25 or Semantic only |
| Product search | Hybrid (exact + semantic) |

## Files Structure

```
examples/module_14/
├── 01_hyde_search.py           # HyDE implementation
├── 02_hybrid_search.py         # BM25 + Semantic hybrid
├── 03_reranking.py             # Cross-encoder reranking
├── deliverable_advanced_rag.py # Full toolkit (700+ lines)
├── DELIVERABLE_README.md       # This file
├── README.md                   # Module overview
├── requirements.txt            # Dependencies
└── .gitignore                  # Exclude cache
```

## Key Insights

1. **HyDE improves recall 20-40%** for Q&A tasks
2. **Hybrid search is almost always better** than either method alone
3. **Reranking improves precision 30-50%** with minimal latency cost
4. **Combine patterns** for production-grade RAG
5. **Tune alpha** based on your query distribution

## Real-World Applications

Apply to your projects:
- **kaizen**: Enhance RAG with hybrid search + reranking
- **vibe**: Q&A system with HyDE for better course search
- **contrarian**: Financial document search with precision reranking

---

**Time**: ~4 hours | **Lines**: 700+ | **Author**: Neural Dojo
