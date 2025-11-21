# Module 10 Examples: Vector Spaces & Semantic Search 🔮

**This is a Heureka Moment module!**

## Overview

These examples demonstrate the transformative insight: **Math works on meaning!** You'll see how embeddings create semantic space where vector arithmetic transforms concepts.

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

**All examples run locally (FREE, no API calls)**

## Examples

### Example 1: Vector Arithmetic & Visualization (`01_vector_arithmetic.py`) 🔮

**What it does**: The Heureka Moment - demonstrates that math works on meaning!

**Run**:
```bash
python 01_vector_arithmetic.py
```

**Demonstrations**:
1. **Classic Analogies** - `king - man + woman ≈ queen`
2. **Geographic Relationships** - `Paris - France + Italy ≈ Rome`
3. **Grammar Transformations** - `walking - walk + run ≈ running`
4. **2D Visualization** - See semantic space with your eyes!
5. **Topic Clusters** - Words group by meaning automatically

**You'll learn**:
- How vector arithmetic transforms meaning
- Why embeddings create semantic space
- Visualizing high-dimensional embeddings in 2D
- The geometry of meaning

**Sample output**:
```
🔮 HEUREKA MOMENT: Vector Arithmetic on Meaning!
================================================================================

Example 1: Gender Transformation
================================================================================

Question: If 'king' is to 'man', what is to 'woman'?
Formula: king - man + woman ≈ ?

Results:
1. 0.921 ██████████████████████████████████████████████ queen
2. 0.847 ██████████████████████████████████████████ monarch
3. 0.812 ████████████████████████████████████████ princess

💡 Explanation:
   king   = [royalty + male + power + ...]
   - man  = [male + human + adult]
   + woman = [female + human + adult]
   ≈ [royalty + female + power + ...] = QUEEN!
```

**Generated visualizations**:
- `semantic_space_2d.png` - 2D projection showing relationships
- `topic_clusters.png` - Words clustered by topic

**Cost**: FREE (uses local Sentence Transformers)

---

### Example 2: Production Semantic Search (`02_production_search.py`)

**What it does**: Build production-grade semantic search with FAISS.

**Run**:
```bash
python 02_production_search.py
```

**Features**:
1. **Naive Search** - Brute force baseline (O(N))
2. **FAISS Search** - Fast ANN with HNSW (O(log N))
3. **Hybrid Search** - Combine semantic + metadata filtering
4. **Performance Benchmarks** - Compare speed at different scales
5. **Scalability Demo** - Test on 100, 500, 1000+ documents

**You'll learn**:
- Why brute force doesn't scale
- How FAISS accelerates search (100-1000x faster!)
- HNSW algorithm for approximate nearest neighbors
- Hybrid search patterns for production
- Performance benchmarking techniques

**Sample output**:
```
BENCHMARK: Search Performance Comparison
================================================================================

Naive:
  Average latency: 45.23 ms
  Std deviation: 3.12 ms

FAISS:
  Average latency: 1.87 ms
  Std deviation: 0.42 ms

================================================================================
⚡ FAISS Speedup: 24.2x faster than naive search!
================================================================================
```

**Cost**: FREE (uses local models)

---

## Quick Start

**Run both examples**:
```bash
python 01_vector_arithmetic.py  # See the Heureka Moment!
python 02_production_search.py   # Build production search
```

---

## Key Takeaways

### The Heureka Moment 🔮

**Before**: Embeddings are "magic black boxes" that somehow represent meaning.

**After**: Embeddings are **coordinates in semantic space** - a real geometry where:
- Distance = semantic similarity
- Direction = relationships
- Arithmetic = meaning transformations

**This changes everything!**

### Vector Arithmetic

**Math literally works on concepts:**

```python
king - man + woman ≈ queen
Paris - France + Italy ≈ Rome
good - bad + terrible ≈ excellent
```

**How it works**:
```
king = [royalty + male + power + ...]
- man = [male + human + adult]
+ woman = [female + human + adult]
= [royalty + female + power + ...]
≈ queen!
```

### Semantic Space Geometry

**Three key properties**:

1. **Distance measures similarity**
   ```
   distance(embedding("cat"), embedding("kitten")) → SMALL
   distance(embedding("cat"), embedding("pizza")) → LARGE
   ```

2. **Direction encodes relationships**
   ```
   king → queen  (same direction as)  man → woman
   Paris → France  (same direction as)  Rome → Italy
   ```

3. **Clusters reveal topics**
   ```
   Programming cluster: [Python, JavaScript, coding, ...]
   Food cluster: [pizza, pasta, cooking, ...]
   ```

### Production Search

**Naive search doesn't scale**:
- 1,000 docs → 10ms ✅
- 100,000 docs → 1,000ms ⚠️
- 1,000,000 docs → 10,000ms ❌

**FAISS makes it fast**:
- Uses HNSW (Hierarchical Navigable Small World)
- O(log N) instead of O(N)
- 100-1000x speedup!
- Can handle billions of vectors

---

## Algorithms Explained

### HNSW (Hierarchical Navigable Small World)

**Idea**: Multi-layer graph where each layer skips more nodes:

```
Layer 2: •────────────────•  (sparse, long jumps)
          \              /
Layer 1:  •────•────•────•    (medium density)
            \   \  /   /
Layer 0:  •─•─•─•─•─•─•  (dense, all nodes)
```

**Search process**:
1. Start at top layer
2. Jump quickly to approximate region
3. Descend to lower layers for precision
4. Find exact nearest neighbors

**Performance**: O(log N) - exponentially faster!

### Why Cosine Similarity?

**Cosine measures direction, not magnitude**:

```python
vec_1 = [1, 2, 3]
vec_2 = [2, 4, 6]  # Same direction, 2x magnitude

cosine_similarity(vec_1, vec_2) = 1.0  # Identical!
```

For text, **direction** (meaning) matters more than **magnitude** (length).

---

## Visualizations

Both examples generate visualizations:

### `semantic_space_2d.png`

Shows embeddings projected to 2D using PCA:
- Related words cluster together
- Arrows show relationships
- Parallel arrows = analogous relationships

### `topic_clusters.png`

Shows words clustered by topic using t-SNE:
- Color-coded by topic
- Clear separation between clusters
- Distance ≈ semantic distance

---

## Practical Applications

### 1. Semantic Search

**Replace keyword search with meaning-based search:**

```python
# Index documents (once)
embeddings = [model.encode(doc) for doc in documents]
index = faiss.IndexHNSWFlat(dimension, 32)
index.add(embeddings)

# Search (fast!)
query_emb = model.encode(query)
distances, indices = index.search(query_emb, k=5)
```

**Use cases**:
- Documentation search (kaizen)
- FAQ matching
- Code search
- Customer support

### 2. Recommendation System

**Find similar items:**

```python
item_emb = embeddings[item_id]
distances, indices = index.search(item_emb.reshape(1, -1), k=10)
recommendations = [items[i] for i in indices[0][1:]]  # Skip self
```

**Use cases**:
- Content recommendations (vibe)
- Product recommendations
- "You might also like..."
- Similar article suggestions

### 3. Hybrid Search

**Combine semantic + metadata:**

```python
# 1. Semantic search (get top 100)
semantic_results = faiss_search(query, k=100)

# 2. Filter by metadata
filtered = [r for r in semantic_results if r.category == "Technology"]

# 3. Rerank by popularity
final_results = sorted(filtered, key=lambda r: r.score * r.popularity)[:5]
```

**Use cases**:
- E-commerce search (filter + rank)
- News search (category + recency)
- Job search (location + salary + match)

---

## Performance Tips

### 1. Batch Encoding

```python
# Faster: Batch encoding
embeddings = model.encode(texts, batch_size=32)

# Slower: Sequential
embeddings = [model.encode(text) for text in texts]

# Speedup: 10-50x
```

### 2. Use GPU (if available)

```python
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
# → 10-100x faster encoding!
```

### 3. Dimensionality Reduction

```python
# Reduce 384 → 128 dimensions
from sklearn.decomposition import PCA
pca = PCA(n_components=128)
reduced_embeddings = pca.fit_transform(embeddings)

# Storage: 66% reduction
# Search: 3x faster
# Accuracy: ~5% loss
```

### 4. Quantization

```python
# Float32 (4 bytes/dim) → Int8 (1 byte/dim)
embeddings_i8 = (embeddings * 127).astype('int8')

# Storage: 75% reduction
# Accuracy: <1% loss
```

---

## Common Issues and Solutions

### Issue: "FAISS not found"
**Solution**: Install with `pip install faiss-cpu` (or `faiss-gpu` for GPU)

### Issue: "Visualizations not showing"
**Solution**:
- Install matplotlib: `pip install matplotlib`
- Check saved PNG files in examples directory

### Issue: "Out of memory"
**Solution**:
- Process in batches
- Use dimensionality reduction
- Use quantization (int8)

### Issue: "Search is still slow"
**Solution**:
- Check you're using FAISS, not naive search
- Use GPU for encoding
- Reduce embedding dimensions

---

## Real-World Applications

### kaizen (Lean DevOps Platform)

**Enhancement**: Semantic RAG retrieval

```python
# Index kaizen docs with FAISS
doc_embeddings = model.encode(kaizen_docs)
index = build_faiss_index(doc_embeddings)

# User query
query_emb = model.encode("How do I optimize deployments?")
distances, indices = index.search(query_emb, k=5)

# Use top docs as RAG context
context = [kaizen_docs[i] for i in indices[0]]
answer = llm_query(context + query)
```

### vibe (Teaching Platform)

**Feature**: Lesson recommendations

```python
# Student completes a lesson
completed_emb = lesson_embeddings[lesson_id]

# Find similar lessons
distances, indices = index.search(completed_emb.reshape(1, -1), k=6)

# Recommend (skip the completed lesson itself)
recommendations = [lessons[i] for i in indices[0][1:]]
```

### contrarian (Stock Analysis)

**Feature**: News clustering

```python
# Embed news articles
news_embeddings = model.encode(news_articles)

# Cluster by topic
from sklearn.cluster import KMeans
clusters = KMeans(n_clusters=5).fit_predict(news_embeddings)

# Group articles by cluster
for cluster_id in range(5):
    articles = [news_articles[i] for i, c in enumerate(clusters) if c == cluster_id]
    print(f"Topic {cluster_id}: {articles}")
```

---

## Further Reading

### Papers
- [Word2Vec (2013)](https://arxiv.org/abs/1301.3781) - Vector arithmetic on words
- [HNSW (2016)](https://arxiv.org/abs/1603.09320) - Fast ANN algorithm
- [FAISS Paper (2017)](https://arxiv.org/abs/1702.08734) - Facebook's similarity search

### Tools
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [Qdrant](https://qdrant.tech/) - Vector database (Module 14!)
- [Annoy](https://github.com/spotify/annoy) - Spotify's ANN library

### Benchmarks
- [ANN-Benchmarks](http://ann-benchmarks.com/) - Compare ANN algorithms

---

## Next Steps

After experiencing the Heureka Moment:
- **Module 11**: Introduction to RAG (Retrieval-Augmented Generation)
  - Combine semantic search (Module 10) with LLM generation (Module 8)
  - Build production RAG pipelines
  - RAG for kaizen, vibe, contrarian

**Phase 2 Complete!** 🎉

You now understand:
- ✅ How LLMs work (Module 6)
- ✅ Tokenization and optimization (Module 7)
- ✅ Text generation strategies (Module 8)
- ✅ Embeddings and similarity (Module 9)
- ✅ Vector spaces and semantic search (Module 10) 🔮

**Ready for Phase 3**: Building with AI Toolkits!

---

**🥋 Neural Dojo - Math works on meaning! 🧠⚡🔮**
