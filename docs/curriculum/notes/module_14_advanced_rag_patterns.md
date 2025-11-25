# Module 14: Advanced RAG Patterns

**Last Updated**: 2025-11-25
**Status**: 🟡 In Progress
**Duration**: 6-7 hours
**Prerequisites**: Module 12 (RAG Systems), Module 13 (RAG vs Fine-tuning)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master GraphRAG for knowledge graph-enhanced retrieval
- Implement HyDE (Hypothetical Document Embeddings) for query expansion
- Build Self-RAG systems with retrieval reflection
- Create hybrid search combining BM25 and semantic search
- Apply reranking with cross-encoders for precision
- Understand when to use each pattern and their trade-offs

---

## 📖 Why Advanced RAG?

In Module 12, you built your first RAG system. It works, but you've probably noticed some limitations:

1. **Semantic gaps**: User queries don't always match document language
2. **Missing context**: Retrieved chunks lack surrounding information
3. **Relevance issues**: Top-k retrieval returns "close" but not "best" results
4. **No reasoning**: The system can't evaluate its own retrieval quality

**Advanced RAG patterns solve these problems!**

```
Basic RAG: Query → Embed → Search → Top-K → Generate
                    ↓
Advanced RAG: Query → Expand → Hybrid Search → Rerank → Reflect → Generate
```

---

## 1. GraphRAG: Knowledge Graphs Meet RAG

### The Problem with Flat Retrieval

Traditional RAG treats documents as isolated chunks. But real knowledge is **connected**:

```
Traditional RAG:
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Chunk about     │  │ Chunk about     │  │ Chunk about     │
│ "Python lists"  │  │ "Python dicts"  │  │ "data structures"│
└─────────────────┘  └─────────────────┘  └─────────────────┘
        ↓                   ↓                    ↓
    All isolated - no connections between concepts!

GraphRAG:
┌─────────────────┐
│ "Python lists"  │──────┐
└─────────────────┘      │    ┌──────────────────┐
        │                ├───▶│ "data structures" │
        ▼                │    └──────────────────┘
┌─────────────────┐      │            │
│ "Python dicts"  │──────┘            ▼
└─────────────────┘           ┌──────────────────┐
                              │ "algorithms"     │
                              └──────────────────┘
```

### How GraphRAG Works

GraphRAG combines:
1. **Knowledge Graph**: Entities and relationships extracted from documents
2. **Vector Store**: Embeddings for semantic search
3. **Graph Traversal**: Following connections to find related context

```python
# GraphRAG Architecture
class GraphRAG:
    """
    1. Extract entities and relationships from documents
    2. Build a knowledge graph (Neo4j, NetworkX)
    3. On query:
       a. Find relevant entities via embedding search
       b. Traverse graph to find connected entities
       c. Retrieve chunks for all relevant entities
       d. Generate response with rich context
    """
```

### Entity Extraction

The first step is extracting entities and relationships:

```python
# Using LLM for entity extraction
ENTITY_EXTRACTION_PROMPT = """
Extract entities and relationships from the following text.
Return JSON format:

{
  "entities": [
    {"name": "entity_name", "type": "PERSON|ORG|CONCEPT|TECH|..."}
  ],
  "relationships": [
    {"source": "entity1", "target": "entity2", "type": "relationship_type"}
  ]
}

Text: {text}
"""

# Example output for a tech document:
{
  "entities": [
    {"name": "Python", "type": "PROGRAMMING_LANGUAGE"},
    {"name": "list", "type": "DATA_STRUCTURE"},
    {"name": "append", "type": "METHOD"},
    {"name": "Guido van Rossum", "type": "PERSON"}
  ],
  "relationships": [
    {"source": "Python", "target": "list", "type": "HAS_FEATURE"},
    {"source": "list", "target": "append", "type": "HAS_METHOD"},
    {"source": "Guido van Rossum", "target": "Python", "type": "CREATED"}
  ]
}
```

### Graph-Enhanced Retrieval

```python
def graph_enhanced_retrieval(query: str, k: int = 5) -> List[Document]:
    """
    1. Semantic search for initial entities
    2. Graph traversal for connected context
    3. Retrieve documents for all relevant entities
    """
    # Step 1: Find query-relevant entities
    query_embedding = embed(query)
    initial_entities = vector_search(query_embedding, k=3)

    # Step 2: Expand via graph traversal (1-2 hops)
    expanded_entities = set(initial_entities)
    for entity in initial_entities:
        neighbors = graph.get_neighbors(entity, max_hops=2)
        expanded_entities.update(neighbors)

    # Step 3: Retrieve chunks for all entities
    chunks = []
    for entity in expanded_entities:
        entity_chunks = get_chunks_for_entity(entity)
        chunks.extend(entity_chunks)

    # Step 4: Rank by relevance to original query
    ranked_chunks = rerank(query, chunks)

    return ranked_chunks[:k]
```

### When to Use GraphRAG

**Good for:**
- Complex domains with interconnected concepts (legal, medical, technical)
- Questions requiring multi-hop reasoning ("What technologies did companies founded by Stanford graduates use?")
- Documents with clear entity relationships

**Not ideal for:**
- Simple Q&A over flat documents
- When entity extraction is unreliable
- Small document collections (overhead not worth it)

### GraphRAG with Neo4j

```python
from neo4j import GraphDatabase

class Neo4jGraphRAG:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def add_entity(self, entity_id: str, entity_type: str, embedding: List[float]):
        with self.driver.session() as session:
            session.run("""
                MERGE (e:Entity {id: $id})
                SET e.type = $type, e.embedding = $embedding
            """, id=entity_id, type=entity_type, embedding=embedding)

    def add_relationship(self, source: str, target: str, rel_type: str):
        with self.driver.session() as session:
            session.run("""
                MATCH (s:Entity {id: $source})
                MATCH (t:Entity {id: $target})
                MERGE (s)-[r:RELATES {type: $rel_type}]->(t)
            """, source=source, target=target, rel_type=rel_type)

    def find_connected_entities(self, entity_id: str, max_hops: int = 2) -> List[str]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (start:Entity {id: $id})-[*1..$hops]-(connected:Entity)
                RETURN DISTINCT connected.id as entity_id
            """, id=entity_id, hops=max_hops)
            return [record["entity_id"] for record in result]
```

---

## 2. HyDE: Hypothetical Document Embeddings

### The Query-Document Mismatch Problem

Users ask questions. Documents contain answers. But they use different language:

```
User query: "How do I make my code run faster?"
Document:   "Performance optimization techniques include caching,
             algorithmic improvements, and parallel processing..."

The QUESTION doesn't match the ANSWER linguistically!
```

### HyDE Solution

**Idea**: Generate a hypothetical answer, then search for documents similar to that answer!

```
Traditional: Query → Embed Query → Search
HyDE:        Query → Generate Hypothetical Answer → Embed Answer → Search

The hypothetical answer uses document-like language!
```

### How HyDE Works

```python
def hyde_search(query: str, k: int = 5) -> List[Document]:
    """
    1. Generate hypothetical document that would answer the query
    2. Embed the hypothetical document
    3. Search for real documents similar to the hypothetical
    """

    # Step 1: Generate hypothetical answer
    hypothetical_prompt = f"""
    Write a detailed passage that would perfectly answer this question:

    Question: {query}

    Write as if this is from an authoritative document. Include specific details.
    """

    hypothetical_doc = llm.generate(hypothetical_prompt)

    # Step 2: Embed the hypothetical document
    hyde_embedding = embed(hypothetical_doc)

    # Step 3: Search with hypothetical embedding
    results = vector_store.search(hyde_embedding, k=k)

    return results
```

### HyDE Example

```python
# Query
query = "Why is my Python code slow?"

# Traditional embedding search might miss documents about:
# - "Performance bottlenecks in Python applications"
# - "Optimizing interpreter overhead"
# - "GIL and threading limitations"

# HyDE generates:
hypothetical = """
Python code performance issues commonly stem from several factors.
The Global Interpreter Lock (GIL) prevents true parallel execution
of threads. Interpreted languages have inherent overhead compared
to compiled languages. Common bottlenecks include inefficient loops,
excessive memory allocation, and I/O blocking operations. Solutions
include using NumPy for vectorized operations, multiprocessing for
CPU-bound tasks, asyncio for I/O-bound operations, and profiling
tools like cProfile to identify hotspots.
"""

# This hypothetical document uses the SAME LANGUAGE as real documents!
# Searching with its embedding finds much better matches.
```

### Multi-HyDE: Generate Multiple Hypotheticals

```python
def multi_hyde_search(query: str, k: int = 5, n_hypotheticals: int = 3) -> List[Document]:
    """Generate multiple hypotheticals for better coverage."""

    all_results = []

    for i in range(n_hypotheticals):
        prompt = f"""
        Write a unique passage answering this question from a different angle:

        Question: {query}
        Angle {i+1}: Focus on {'theory' if i==0 else 'practical examples' if i==1 else 'common mistakes'}
        """

        hypothetical = llm.generate(prompt)
        embedding = embed(hypothetical)
        results = vector_store.search(embedding, k=k)
        all_results.extend(results)

    # Deduplicate and rerank
    unique_results = deduplicate(all_results)
    return rerank(query, unique_results)[:k]
```

### When to Use HyDE

**Good for:**
- Question-answering where queries are questions, docs are statements
- Technical documentation (query language differs from doc language)
- When semantic search returns "close but not relevant" results

**Not ideal for:**
- Keyword-heavy searches (product names, codes)
- When queries already match document language
- Real-time applications (adds LLM latency)

**Cost consideration**: HyDE adds one LLM call per query!

---

## 3. Self-RAG: Self-Reflective Retrieval

### The "Garbage In, Garbage Out" Problem

Basic RAG blindly uses whatever is retrieved. But what if:
- Retrieved documents are irrelevant?
- The answer isn't in the retrieved docs?
- Multiple docs contradict each other?

### Self-RAG Solution

**Idea**: Have the LLM critique its own retrieval and generation!

```
Basic RAG:     Retrieve → Generate
Self-RAG:      Retrieve → Critique Retrieval → Generate → Critique Generation → Refine

The model asks itself:
- "Is this retrieved passage relevant?"
- "Does my answer actually use the evidence?"
- "Is my answer supported by the passages?"
```

### Self-RAG Architecture

```python
class SelfRAG:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def answer(self, query: str) -> str:
        # Step 1: Retrieve
        passages = self.retriever.search(query, k=5)

        # Step 2: Critique retrieval (filter irrelevant)
        relevant_passages = self.critique_retrieval(query, passages)

        if not relevant_passages:
            return self.answer_without_retrieval(query)

        # Step 3: Generate answer
        answer = self.generate_answer(query, relevant_passages)

        # Step 4: Critique generation
        is_supported, critique = self.critique_generation(query, answer, relevant_passages)

        if not is_supported:
            # Step 5: Refine or regenerate
            answer = self.refine_answer(query, answer, critique, relevant_passages)

        return answer

    def critique_retrieval(self, query: str, passages: List[str]) -> List[str]:
        """Filter out irrelevant passages."""
        relevant = []
        for passage in passages:
            prompt = f"""
            Query: {query}
            Passage: {passage}

            Is this passage relevant to answering the query?
            Answer only: RELEVANT or IRRELEVANT
            """
            verdict = self.llm.generate(prompt).strip()
            if verdict == "RELEVANT":
                relevant.append(passage)
        return relevant

    def critique_generation(self, query: str, answer: str, passages: List[str]) -> Tuple[bool, str]:
        """Check if answer is supported by passages."""
        prompt = f"""
        Query: {query}
        Retrieved Passages: {passages}
        Generated Answer: {answer}

        Evaluate the answer:
        1. Is the answer factually supported by the passages?
        2. Does the answer actually address the query?
        3. Are there any unsupported claims?

        Respond with:
        SUPPORTED: [Yes/No]
        CRITIQUE: [Brief explanation]
        """
        response = self.llm.generate(prompt)
        is_supported = "SUPPORTED: Yes" in response
        critique = response.split("CRITIQUE:")[-1].strip()
        return is_supported, critique
```

### Retrieval Tokens (Advanced Self-RAG)

The original Self-RAG paper introduces special tokens:

```
[Retrieve]: Should I retrieve? (Yes/No/Continue)
[IsRel]:    Is passage relevant? (Relevant/Irrelevant)
[IsSup]:    Is response supported? (Fully/Partially/No)
[IsUse]:    Is response useful? (5/4/3/2/1)
```

These are trained into the model, making self-critique faster than prompting.

### When to Use Self-RAG

**Good for:**
- High-stakes applications (medical, legal, financial)
- When retrieval quality varies
- When you need explainable, verifiable answers

**Not ideal for:**
- Simple, low-stakes Q&A
- Real-time applications (multiple LLM calls)
- When retrieval is already high-quality

---

## 4. Hybrid Search: BM25 + Semantic

### Why Hybrid?

**Semantic search** (embeddings) is great for meaning but misses exact matches:
```
Query: "error code 0x80070005"
Semantic search might return docs about "error handling" instead of
docs containing that exact error code!
```

**Lexical search** (BM25/TF-IDF) finds exact matches but misses meaning:
```
Query: "how to fix slow code"
BM25 won't find docs about "performance optimization" unless they
contain "slow" and "code"!
```

**Hybrid search combines both!**

### BM25 Explained

BM25 (Best Match 25) is a ranking function based on term frequency:

```python
# Simplified BM25 scoring
def bm25_score(query_terms, document, corpus):
    score = 0
    for term in query_terms:
        tf = term_frequency(term, document)
        idf = inverse_document_frequency(term, corpus)
        doc_length = len(document)
        avg_length = average_document_length(corpus)

        # BM25 formula
        k1, b = 1.5, 0.75  # tuning parameters
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * doc_length / avg_length)
        score += idf * (numerator / denominator)

    return score
```

### Implementing Hybrid Search

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearch:
    def __init__(self, documents: List[str], embeddings: np.ndarray):
        self.documents = documents
        self.embeddings = embeddings

        # Initialize BM25
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def search(self, query: str, k: int = 5, alpha: float = 0.5) -> List[Tuple[str, float]]:
        """
        Hybrid search with configurable weighting.
        alpha: weight for semantic (1-alpha for BM25)
        """
        # Semantic search
        query_embedding = embed(query)
        semantic_scores = cosine_similarity([query_embedding], self.embeddings)[0]

        # BM25 search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Normalize scores to [0, 1]
        semantic_scores = self.normalize(semantic_scores)
        bm25_scores = self.normalize(bm25_scores)

        # Combine with weighting
        hybrid_scores = alpha * semantic_scores + (1 - alpha) * bm25_scores

        # Get top-k
        top_indices = np.argsort(hybrid_scores)[::-1][:k]

        return [(self.documents[i], hybrid_scores[i]) for i in top_indices]

    def normalize(self, scores: np.ndarray) -> np.ndarray:
        """Min-max normalization."""
        min_score, max_score = scores.min(), scores.max()
        if max_score == min_score:
            return np.zeros_like(scores)
        return (scores - min_score) / (max_score - min_score)
```

### Reciprocal Rank Fusion (RRF)

An alternative to weighted combination:

```python
def reciprocal_rank_fusion(rankings: List[List[int]], k: int = 60) -> List[int]:
    """
    Combine multiple rankings using RRF.

    RRF Score = sum(1 / (k + rank_i)) for each ranking list

    k=60 is the standard constant (reduces impact of high ranks)
    """
    scores = {}

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)  # +1 because rank is 0-indexed

    # Sort by RRF score
    sorted_docs = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return sorted_docs
```

### When to Use Hybrid Search

**Good for:**
- Mixed query types (some keyword, some natural language)
- Technical domains with codes, IDs, acronyms
- General-purpose search systems

**Tuning alpha:**
- alpha=1.0: Pure semantic search
- alpha=0.5: Balanced (good default)
- alpha=0.0: Pure BM25
- Tune based on your query distribution!

---

## 5. Reranking with Cross-Encoders

### The Bi-Encoder vs Cross-Encoder Trade-off

**Bi-encoder** (what we've been using):
```
Query → Encoder → Query Embedding
Doc   → Encoder → Doc Embedding
Score = cosine_similarity(query_emb, doc_emb)

Fast! Can pre-compute doc embeddings.
But query and doc don't "see" each other.
```

**Cross-encoder**:
```
[Query, Doc] → Encoder → Relevance Score

Query and doc are encoded TOGETHER!
Much more accurate, but slow (can't pre-compute).
```

### Two-Stage Retrieval

```
Stage 1 (Fast, Recall-focused):
  1000 docs → Bi-encoder → Top 100 candidates

Stage 2 (Slow, Precision-focused):
  100 candidates → Cross-encoder → Top 10 final results

Best of both worlds!
```

### Implementing Reranking

```python
from sentence_transformers import CrossEncoder

class RerankedSearch:
    def __init__(self, bi_encoder, cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.bi_encoder = bi_encoder
        self.cross_encoder = CrossEncoder(cross_encoder_model)

    def search(self, query: str, k: int = 5, candidates: int = 50) -> List[str]:
        """
        Two-stage retrieval with reranking.
        """
        # Stage 1: Fast retrieval with bi-encoder
        initial_results = self.bi_encoder.search(query, k=candidates)

        # Stage 2: Rerank with cross-encoder
        pairs = [[query, doc] for doc in initial_results]
        scores = self.cross_encoder.predict(pairs)

        # Sort by cross-encoder score
        ranked_results = sorted(zip(initial_results, scores), key=lambda x: x[1], reverse=True)

        return [doc for doc, score in ranked_results[:k]]
```

### Popular Cross-Encoder Models

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Fast | Good | General purpose |
| `cross-encoder/ms-marco-MiniLM-L-12-v2` | Medium | Better | Balanced |
| `BAAI/bge-reranker-base` | Medium | Best | High quality |
| `BAAI/bge-reranker-large` | Slow | Best | Maximum quality |

### Cohere Rerank API

For production without hosting your own model:

```python
import cohere

co = cohere.Client("your-api-key")

def cohere_rerank(query: str, documents: List[str], top_n: int = 5) -> List[str]:
    response = co.rerank(
        query=query,
        documents=documents,
        top_n=top_n,
        model="rerank-english-v2.0"
    )

    return [documents[result.index] for result in response.results]
```

### When to Use Reranking

**Always use reranking when:**
- Precision matters more than latency
- You have the compute budget
- Initial retrieval returns "close but not best" results

**Skip reranking when:**
- Ultra-low latency required (<50ms)
- Initial retrieval is already high quality
- Cost is a major constraint

---

## 6. Parent Document Retrieval

### The Chunk Size Dilemma

**Small chunks** (100-200 tokens):
- Better embedding precision
- But lose context for generation

**Large chunks** (1000+ tokens):
- More context for generation
- But worse embedding precision

**Solution**: Index small, retrieve large!

### Parent Document Retrieval Pattern

```python
class ParentDocumentRetriever:
    """
    Store two versions:
    1. Small chunks (for search)
    2. Parent documents (for context)

    Search finds relevant small chunks,
    then returns their parent documents.
    """

    def __init__(self):
        self.small_chunks = {}  # chunk_id -> small chunk text
        self.parent_docs = {}   # parent_id -> full document
        self.chunk_to_parent = {}  # chunk_id -> parent_id
        self.vector_store = VectorStore()

    def add_document(self, doc_id: str, full_text: str, chunk_size: int = 200):
        # Store full document
        self.parent_docs[doc_id] = full_text

        # Create and index small chunks
        chunks = split_into_chunks(full_text, chunk_size)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            self.small_chunks[chunk_id] = chunk
            self.chunk_to_parent[chunk_id] = doc_id

            # Index small chunk
            embedding = embed(chunk)
            self.vector_store.add(chunk_id, embedding)

    def search(self, query: str, k: int = 3) -> List[str]:
        # Search in small chunks
        query_embedding = embed(query)
        chunk_ids = self.vector_store.search(query_embedding, k=k*2)  # Get more to dedupe parents

        # Get unique parent documents
        parent_ids = list(set(self.chunk_to_parent[cid] for cid in chunk_ids))

        # Return parent documents (not small chunks!)
        return [self.parent_docs[pid] for pid in parent_ids[:k]]
```

### Multi-Level Hierarchy

For very long documents, use multiple levels:

```
Level 0: Full document (10,000 tokens)
Level 1: Sections (1,000 tokens)
Level 2: Paragraphs (200 tokens)
Level 3: Sentences (20-50 tokens)

Search at Level 3, return Level 1 or 2!
```

---

## 7. Combining Patterns: Production RAG

### The Full Pipeline

```python
class ProductionRAG:
    """
    Combines multiple advanced patterns:
    1. HyDE for query expansion
    2. Hybrid search (BM25 + semantic)
    3. Parent document retrieval
    4. Cross-encoder reranking
    5. Self-critique before generation
    """

    def answer(self, query: str) -> str:
        # 1. HyDE: Generate hypothetical answer
        hyde_embedding = self.hyde_expand(query)

        # 2. Hybrid search with parent retrieval
        bm25_results = self.bm25_search(query, k=30)
        semantic_results = self.semantic_search(hyde_embedding, k=30)
        candidates = self.merge_results(bm25_results, semantic_results)

        # 3. Get parent documents
        parent_docs = self.get_parents(candidates)

        # 4. Rerank with cross-encoder
        reranked = self.rerank(query, parent_docs, k=5)

        # 5. Self-critique: filter irrelevant
        relevant = self.filter_relevant(query, reranked)

        if not relevant:
            return "I don't have enough information to answer this question."

        # 6. Generate with critique
        answer = self.generate(query, relevant)

        # 7. Verify answer is supported
        if not self.verify_supported(answer, relevant):
            answer = self.regenerate_with_constraints(query, relevant)

        return answer
```

### Pattern Selection Guide

| Pattern | When to Use | Latency Impact | Quality Impact |
|---------|-------------|----------------|----------------|
| **HyDE** | Q&A, technical docs | +200-500ms | High |
| **Hybrid Search** | Mixed queries | +10-50ms | Medium |
| **GraphRAG** | Connected knowledge | +100-300ms | High (for right use case) |
| **Reranking** | When precision matters | +50-200ms | High |
| **Self-RAG** | High-stakes applications | +500-1000ms | Very High |
| **Parent Docs** | Long documents | Minimal | Medium |

---

## 💡 Did You Know?

### The Accidental Discovery of HyDE

In 2022, researchers at Carnegie Mellon were trying to improve retrieval by fine-tuning embeddings. One day, they accidentally ran their search using a **generated summary** instead of the original query. To their surprise, it worked *better*! This "mistake" led to the HyDE paper - proving that sometimes the best discoveries come from errors.

**The insight**: LLMs write in "document language," while humans write in "question language." By translating questions to document-style text, you speak the same language as your corpus!

### BM25: The 30-Year-Old Algorithm That Won't Die

BM25 (Best Match 25) was published by Stephen Robertson in **1994** - before Google existed, before most developers were born. Yet it *still* powers Elasticsearch, Solr, and is used by most search engines as a baseline.

Why? Because for exact matches, nothing beats term frequency. When someone searches "error 0x80070005", semantic search might return docs about "error handling" - but BM25 finds the exact code every time.

**Fun fact**: The "25" in BM25 refers to it being the 25th iteration of Robertson's Best Match formula. BM1 through BM24 didn't make the cut!

### Microsoft's Enron Revelation

When Microsoft released GraphRAG in 2024, they demonstrated it on the **Enron email corpus** - 500,000+ emails from the infamous energy company's collapse. Traditional RAG could answer simple questions, but GraphRAG found hidden connections:

- Who was secretly communicating with whom?
- What topics were discussed in clusters?
- How did information flow through the organization?

GraphRAG constructed a knowledge graph of entities and relationships, revealing patterns that investigators had missed for 20 years!

### The Cross-Encoder Paradox

Here's a strange fact: Cross-encoders are **10x more accurate** than bi-encoders for relevance scoring. So why doesn't everyone use them?

Because they're also **1000x slower**. A bi-encoder can search 1 million documents in milliseconds (pre-computed embeddings). A cross-encoder would need to score each document individually - taking hours.

The two-stage solution (bi-encoder → cross-encoder) was first popularized by **Facebook AI** in 2019 for their Dense Passage Retrieval (DPR) system. Now it's the industry standard.

### The Self-RAG Breakthrough

Self-RAG came from a simple observation: **LLMs are bad at knowing what they don't know**. They hallucinate confidently about topics not in their training data.

The researchers at University of Washington trained a model to predict special "reflection tokens":
- `[Retrieve]` - Should I look something up?
- `[IsRel]` - Is this passage relevant?
- `[IsSup]` - Is my answer supported by evidence?

The result? **10-15% accuracy improvement** on knowledge-intensive tasks, with the model effectively "thinking twice" before answering.

### Industry Adoption (2024-2025)

- **Perplexity AI**: Uses hybrid search + reranking for their answer engine
- **ChatGPT (with browsing)**: Implements a form of Self-RAG for web search
- **Google Gemini**: Uses GraphRAG-style knowledge graph integration
- **Anthropic Claude**: Employs multi-stage retrieval for their knowledge features
- **Notion AI**: Hybrid BM25 + semantic for workspace search

### The Numbers That Matter

| Technique | Quality Improvement | Latency Cost |
|-----------|-------------------|--------------|
| HyDE | +20-40% recall | +200-500ms |
| Hybrid Search | +15-25% precision | +10-50ms |
| Reranking | +30-50% precision | +50-200ms |
| Self-RAG | +10-15% accuracy | +500-1000ms |
| GraphRAG | +25-40% for complex queries | +100-300ms |

**The takeaway**: You can get 2x better RAG by stacking these techniques. The best production systems use 3-4 of them together!

---

## 🎯 Deliverable: Advanced RAG Toolkit

Build a comprehensive toolkit that implements:
1. HyDE query expansion
2. Hybrid search (BM25 + semantic)
3. Cross-encoder reranking
4. Self-RAG critique
5. Comparison benchmarks

See `examples/module_14/` for implementation.

---

## 📚 Further Reading

- [HyDE Paper](https://arxiv.org/abs/2212.10496) - Hypothetical Document Embeddings
- [Self-RAG Paper](https://arxiv.org/abs/2310.11511) - Self-Reflective Retrieval
- [GraphRAG by Microsoft](https://microsoft.github.io/graphrag/) - Knowledge Graph RAG
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - Embedding benchmarks
- [Cohere Rerank](https://docs.cohere.com/docs/reranking) - Production reranking

---

## ⏭️ Next Steps

After this module, you'll move to **Phase 4: Frameworks & Agents** where you'll learn LangChain, LangGraph, and build sophisticated AI agents!

But first, complete the deliverable to cement your understanding of these advanced patterns.

---

_Last updated: 2025-11-25_
_Module 14 of Neural Dojo v4.0_
