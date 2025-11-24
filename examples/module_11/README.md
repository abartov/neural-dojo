# Module 11 Examples: Vector Databases & Embeddings

This directory contains working code examples for Module 11: Introduction to Vector Databases.

## Prerequisites

```bash
pip install -r requirements.txt
```

You'll also need Docker installed to run Qdrant locally:
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 qdrant/qdrant
```

## Examples

### Example 1: Qdrant Setup and Basic Operations
**File**: `01_qdrant_setup.py`
**Description**: Learn how to set up Qdrant, create collections, insert vectors, and perform basic similarity searches
**Run**: `python 01_qdrant_setup.py`

**What it covers**:
- Installing and connecting to Qdrant
- Creating vector collections
- Inserting documents with embeddings
- Basic similarity search
- Metadata filtering

### Example 2: Vector Database Benchmark
**File**: `02_vector_db_benchmark.py`
**Description**: Comprehensive benchmark comparing different vector database approaches (Qdrant, FAISS, Chroma)
**Run**: `python 02_vector_db_benchmark.py`

**What it covers**:
- Performance comparison across databases
- Query latency measurement
- Accuracy (recall) evaluation
- Memory usage analysis
- Scalability testing

### Deliverable: Multi-Tenant Vector Store
**File**: `deliverable_multi_tenant_store.py`
**Description**: Production-ready multi-tenant vector store with isolation, metadata filtering, and comprehensive CLI
**Run**: `python deliverable_multi_tenant_store.py demo1`

**What it covers**:
- Multi-tenant collection management
- User-specific vector isolation
- Advanced metadata filtering
- Production-ready error handling
- Comprehensive CLI interface

## Expected Output

### Example 1 Output:
```
✅ Connected to Qdrant at http://localhost:6333
✅ Collection 'documents' created
✅ Inserted 5 documents
🔍 Searching for: "machine learning"
Top 3 Results:
1. [Score: 0.95] "Introduction to Machine Learning"
2. [Score: 0.87] "Deep Learning Fundamentals"
3. [Score: 0.72] "Data Science Best Practices"
```

### Example 2 Output:
```
📊 Vector Database Benchmark Report
================================================
Dataset: 10,000 vectors (384 dimensions)
Query set: 100 queries

Qdrant:
  Query latency: 1.2ms (avg)
  Recall@10: 98.5%
  Memory: 45 MB

FAISS:
  Query latency: 0.8ms (avg)
  Recall@10: 97.2%
  Memory: 38 MB

Chroma:
  Query latency: 2.5ms (avg)
  Recall@10: 96.8%
  Memory: 52 MB
```

## Notes

### Qdrant vs FAISS vs Chroma

**Qdrant**:
- Best for production deployments
- Excellent filtering support
- Built-in persistence and replication
- Great for multi-tenant scenarios

**FAISS**:
- Fastest in-memory search
- No persistence (save to disk manually)
- Best for research and experimentation
- No filtering support

**Chroma**:
- Easiest to get started
- Good for local development
- Built-in embeddings generation
- Growing ecosystem

### Production Considerations

1. **Persistence**: Always enable persistence in production
2. **Replication**: Use replication for high availability
3. **Sharding**: Shard collections for datasets > 10M vectors
4. **Monitoring**: Track query latency and recall metrics
5. **Indexing**: Balance between HNSW parameters (m, ef_construct)

### Troubleshooting

**Qdrant not connecting?**
- Ensure Docker container is running: `docker ps`
- Check port 6333 is available: `lsof -i :6333`

**Slow queries?**
- Increase `ef` parameter for HNSW
- Check if collection is properly indexed
- Consider sharding for large datasets

**Low recall?**
- Increase HNSW `m` and `ef_construct` during creation
- Use better embedding models (e.g., OpenAI text-embedding-3-large)
- Check if metadata filtering is too restrictive

## Further Reading

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [HNSW Algorithm Paper](https://arxiv.org/abs/1603.09320)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [Chroma Documentation](https://docs.trychroma.com/)

---

**Time**: ~6-8 hours | **Difficulty**: Intermediate | **Status**: Complete
