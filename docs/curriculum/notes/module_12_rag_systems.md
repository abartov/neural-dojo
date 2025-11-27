# Module 12: Building Your First RAG System
# Or: Teaching AI to Look Things Up Before Making Stuff Up

**Last Updated**: 2025-11-24
**Status**: Complete
**Reading Time**: 6-7 hours
**Prerequisites**: Modules 9-11

---

## Learning Objectives

By the end of this module, you will:
- Understand RAG architecture (Retrieval-Augmented Generation) deeply
- Build a production-ready RAG pipeline from scratch
- Master document chunking strategies (fixed, semantic, recursive)
- Implement effective retrieval with reranking
- Measure RAG performance with proper evaluation metrics
- Handle edge cases (hallucination, context limits, stale data)
- Apply RAG to real projects (kaizen, vibe, contrarian)

**Why this matters**: RAG is the #1 technique for building AI systems that need current, accurate, domain-specific knowledge. It's how ChatGPT plugins work, how enterprise AI assistants access company data, and how you'll build kaizen's knowledge system.

---

## Did You Know? The $100 Million Problem RAG Solved

In **2020**, a major bank deployed a GPT-3-powered customer service chatbot. Within weeks, disaster struck:

**Customer**: "What's my account balance?"
**Bot**: "Your account balance is $15,432.67"

**The problem**: The bot hallucinated a random number! GPT-3 had no access to actual account data - it just made up a plausible-sounding answer.

**The fallout**:
- **$2.3 million** in customer service costs to clean up confusion
- **Legal investigation** for potentially misleading customers
- Project scrapped after 3 months
- CTO resigned

**The insight**: LLMs are **knowledge-frozen** at training time. They can't know your company data, current events, or user-specific information. They can only generate plausible text based on patterns.

**The solution**: RAG (Retrieval-Augmented Generation)

Instead of asking the LLM to "know" the answer, you:
1. **Retrieve** relevant documents from your database
2. **Augment** the prompt with retrieved context
3. **Generate** an answer based on actual data

```
Without RAG:
User: "What's the status of order #12345?"
LLM: "Your order is being processed." (HALLUCINATION - made up!)

With RAG:
User: "What's the status of order #12345?"
→ Retrieve order from database: {"id": 12345, "status": "shipped", "tracking": "1Z999..."}
→ Prompt: "Based on this order data: {data}, answer: What's the status of order #12345?"
LLM: "Your order #12345 has shipped! Tracking number: 1Z999..." (ACCURATE!)
```

**The transformation**: RAG turned LLMs from "impressive but unreliable" to "production-ready for enterprise." Every major AI company now uses RAG for knowledge-intensive applications.

---

## Introduction: What Is RAG?

### The Core Concept

**RAG = Retrieval-Augmented Generation**

It's a two-step process:
1. **Retrieval**: Find relevant information from a knowledge base
2. **Generation**: Use an LLM to generate an answer using that information

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query: "How do I configure authentication in kaizen?"    │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────┐                                               │
│  │   Embed     │  → Convert query to vector                    │
│  └─────────────┘                                               │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────┐     ┌──────────────────┐                     │
│  │   Search    │ ──► │  Vector Database │                     │
│  └─────────────┘     │  (176K docs)     │                     │
│       │              └──────────────────┘                     │
│       ▼                                                        │
│  Retrieved Context:                                            │
│  - "auth.md: Configure JWT tokens..."                         │
│  - "security.md: Best practices for..."                       │
│  - "api.md: Authentication endpoints..."                      │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────┐                                               │
│  │   Generate  │  → LLM creates answer from context           │
│  └─────────────┘                                               │
│       │                                                        │
│       ▼                                                        │
│  Answer: "To configure authentication in kaizen:               │
│          1. Set JWT_SECRET in .env                            │
│          2. Configure auth middleware in app.py               │
│          3. See auth.md for complete guide..."                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why RAG Works

**LLMs have two fundamental limitations**:

1. **Knowledge cutoff**: Trained on data up to a certain date
   - GPT-4o: October 2023 (but updates regularly)
   - Claude 3.5/4: Early 2024
   - Models get updated - always check current cutoff dates!
   - Can't know about events after training

2. **No private data**: Never saw your company's internal documents
   - Can't answer questions about your codebase
   - Can't access your databases
   - Can't know your business rules

**RAG solves both** by injecting relevant information into the prompt at query time.

---

## Did You Know? The Paper That Started It All

**May 2020**: Facebook AI Research (FAIR) published "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" - the paper that gave RAG its name.

**The key insight**: Instead of making models bigger to store more knowledge, give them access to external knowledge at inference time.

**The results were stunning**:
- **Open-domain QA**: RAG outperformed GPT-3 (175B params) with only 400M params
- **Fact verification**: 94% accuracy vs 72% for pure generation
- **Knowledge updates**: Change the database, instantly update the model's "knowledge"

**The authors**: Patrick Lewis, Ethan Perez, Aleksandra Piktus, and team at Facebook AI

**Why this matters**: RAG proved that **architecture + retrieval** beats **bigger models alone**. This insight shaped the entire industry - ChatGPT's web browsing, Perplexity, and every enterprise AI assistant uses RAG.

**Citation count**: Over 3,000 citations in 4 years - one of the most influential AI papers of the decade!

---

## STOP: Time to Practice!

**You've learned the concept - now let's build a RAG system!**

RAG is best learned by doing. You'll build a complete RAG pipeline that could power kaizen's documentation assistant.

### Practice Path (~4-5 hours total)

**1. [Simple RAG Pipeline](../../examples/module_12/01_simple_rag.py)** - Your first RAG system
   - 📖 Concept: Basic retrieval + generation
   - ⏱️ Time: 90-120 minutes
   - Goal: Build working RAG in 100 lines
   - What you'll learn: The core RAG loop

**2. [Document Chunking](../../examples/module_12/02_chunking_strategies.py)** - Master chunking
   - 📖 Concept: Fixed, semantic, and recursive chunking
   - ⏱️ Time: 60-75 minutes
   - Goal: Understand how chunking affects retrieval quality
   - What you'll learn: Chunk size is the #1 RAG parameter!

**3. [RAG Evaluation](../../examples/module_12/03_rag_evaluation.py)** - Measure quality
   - 📖 Concept: Retrieval metrics, answer quality, hallucination detection
   - ⏱️ Time: 60-75 minutes
   - Goal: Know when your RAG is working well
   - What you'll learn: You can't improve what you don't measure

### Deliverable: Production RAG System

**What**: Build a RAG system for one of your projects
**Time**: 5-6 hours
**Portfolio Value**: Demonstrates end-to-end AI system building

**Requirements**:
1. Choose a knowledge base:
   - **kaizen**: Documentation + code + issues
   - **vibe**: Course content + student Q&A
   - **contrarian**: Financial reports + news
   - **Work**: Infrastructure runbooks + incident reports

2. Implement complete pipeline:
   - Document ingestion (PDF, Markdown, code)
   - Chunking strategy (justify your choice!)
   - Vector storage (Qdrant from Module 11)
   - Retrieval with reranking
   - Answer generation with citations
   - Streaming responses

3. Evaluation dashboard:
   - Test set of 20+ queries with expected answers
   - Retrieval metrics (recall@k, MRR)
   - Answer quality metrics (faithfulness, relevance)
   - Latency tracking

4. Handle edge cases:
   - "I don't know" for out-of-scope queries
   - Citation verification
   - Confidence scoring

**Success Criteria**:
- Answers questions accurately from your knowledge base
- Provides citations/sources for answers
- Handles "I don't know" gracefully
- < 3 second response time
- Evaluation metrics documented

---

## ️ RAG Architecture Deep Dive

### The Three Phases

```
┌───────────────────────────────────────────────────────────────────┐
│                    RAG System Architecture                        │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PHASE 1: INDEXING (Offline - done once per document update)     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐   │
│  │Documents│ →  │ Chunk   │ →  │ Embed   │ →  │Store in     │   │
│  │(raw)    │    │         │    │         │    │Vector DB    │   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────────┘   │
│                                                                   │
│  PHASE 2: RETRIEVAL (Online - per query)                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐   │
│  │  Query  │ →  │ Embed   │ →  │ Search  │ →  │Top-K        │   │
│  │         │    │         │    │Vector DB│    │Documents    │   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────────┘   │
│                                                                   │
│  PHASE 3: GENERATION (Online - per query)                        │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐   │
│  │Context  │ →  │ Build   │ →  │  LLM    │ →  │  Answer     │   │
│  │+ Query  │    │ Prompt  │    │Generate │    │             │   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Phase 1: Indexing

**Goal**: Convert documents into searchable vectors

```python
def index_documents(documents: list[str], vector_db: QdrantClient):
    """Index documents into vector database."""
    for doc in documents:
        # 1. Chunk the document
        chunks = chunk_document(doc, chunk_size=500, overlap=50)

        # 2. Generate embeddings
        embeddings = embedding_model.encode(chunks)

        # 3. Store in vector database
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_db.upsert(
                collection_name="documents",
                points=[{
                    "id": f"{doc.id}_{i}",
                    "vector": embedding,
                    "payload": {
                        "text": chunk,
                        "source": doc.filename,
                        "chunk_index": i
                    }
                }]
            )
```

**Key decisions**:
- **Chunk size**: Too small = loses context, too large = dilutes relevance
- **Overlap**: Prevents information loss at chunk boundaries
- **Metadata**: Store source info for citations

### Phase 2: Retrieval

**Goal**: Find the most relevant chunks for a query

```python
def retrieve(query: str, vector_db: QdrantClient, k: int = 5) -> list[dict]:
    """Retrieve top-k relevant chunks."""
    # 1. Embed the query
    query_embedding = embedding_model.encode(query)

    # 2. Search vector database
    results = vector_db.search(
        collection_name="documents",
        query_vector=query_embedding,
        limit=k
    )

    # 3. Return chunks with metadata
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "score": r.score
        }
        for r in results
    ]
```

**Key decisions**:
- **k value**: More chunks = more context but also more noise
- **Similarity threshold**: Filter out low-relevance results
- **Reranking**: Use a second model to reorder results

### Phase 3: Generation

**Goal**: Generate an answer using retrieved context

```python
def generate_answer(query: str, context: list[dict], llm) -> str:
    """Generate answer from retrieved context."""
    # Build prompt with context
    context_text = "\n\n".join([
        f"[Source: {c['source']}]\n{c['text']}"
        for c in context
    ])

    prompt = f"""Answer the question based ONLY on the following context.
If the context doesn't contain the answer, say "I don't have information about that."

Context:
{context_text}

Question: {query}

Answer:"""

    # Generate with LLM
    response = llm.generate(prompt)

    return response
```

**Key decisions**:
- **Prompt engineering**: Instructions for using context, handling unknowns
- **Citation format**: How to attribute sources
- **Answer length**: Concise vs detailed responses

---

## 📄 Document Chunking: The Most Important Decision

### Why Chunking Matters

**The chunking paradox**:
- **Too small**: Chunks lack context, retrieval returns fragments
- **Too large**: Chunks contain irrelevant info, dilute relevance scores
- **Just right**: Chunks are self-contained units of meaning

**Real example**:

```
Original document:
"Authentication in kaizen uses JWT tokens. To configure authentication,
set the JWT_SECRET environment variable. The token expires after 24 hours
by default. You can customize this in config.py. For production, always
use HTTPS to protect tokens in transit."

Chunk too small (50 chars):
- "Authentication in kaizen uses JWT tokens. To conf"
- "igure authentication, set the JWT_SECRET environ"
→ Query "How to configure auth?" might not match!

Chunk too large (entire doc):
- Returns full doc even for specific questions
→ LLM must parse through irrelevant info

Chunk just right (~200 chars, semantic):
- "Authentication in kaizen uses JWT tokens. To configure authentication, set the JWT_SECRET environment variable."
- "The token expires after 24 hours by default. You can customize this in config.py."
- "For production, always use HTTPS to protect tokens in transit."
→ Each chunk answers a specific question type!
```

### Chunking Strategies

#### 1. Fixed-Size Chunking (Simplest)

```python
def fixed_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # Overlap for continuity

    return chunks
```

**Pros**: Simple, predictable token counts
**Cons**: Breaks mid-sentence, loses semantic coherence
**Use when**: Quick prototyping, uniform documents

#### 2. Sentence-Based Chunking

```python
import nltk

def sentence_chunk(text: str, sentences_per_chunk: int = 5) -> list[str]:
    """Chunk by sentence boundaries."""
    sentences = nltk.sent_tokenize(text)
    chunks = []

    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)

    return chunks
```

**Pros**: Respects sentence boundaries
**Cons**: Variable chunk sizes, may still break concepts
**Use when**: Prose documents, articles

#### 3. Semantic Chunking (Best for Most Cases)

```python
def semantic_chunk(text: str, max_chunk_size: int = 500) -> list[str]:
    """Chunk by semantic units (paragraphs, sections)."""
    # Split by paragraph
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
```

**Pros**: Preserves semantic units, natural boundaries
**Cons**: Variable sizes, requires clean formatting
**Use when**: Documentation, structured content

#### 4. Recursive Chunking (LangChain's Approach)

```python
def recursive_chunk(text: str, chunk_size: int = 500, separators: list[str] = None) -> list[str]:
    """Recursively split using hierarchy of separators."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    separator = separators[0]
    remaining_separators = separators[1:]

    splits = text.split(separator)
    chunks = []
    current_chunk = ""

    for split in splits:
        if len(current_chunk) + len(split) < chunk_size:
            current_chunk += split + separator
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            # If split itself is too large, recurse with finer separator
            if len(split) > chunk_size and remaining_separators:
                sub_chunks = recursive_chunk(split, chunk_size, remaining_separators)
                chunks.extend(sub_chunks)
            else:
                current_chunk = split + separator

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
```

**Pros**: Best of all worlds, handles varied content
**Cons**: More complex, slower
**Use when**: Mixed content, code + prose

---

## Did You Know? The Chunk Size Discovery

In **2023**, researchers at Anthropic ran extensive experiments on chunk size:

| Chunk Size | Retrieval Recall | Answer Quality | Best For |
|------------|------------------|----------------|----------|
| 100 tokens | 45% | Poor | N/A |
| 250 tokens | 72% | Good | Simple QA |
| **500 tokens** | **85%** | **Best** | **General use** |
| 1000 tokens | 78% | Good | Complex questions |
| 2000 tokens | 65% | OK | Long-form analysis |

**The sweet spot**: 400-600 tokens for most use cases!

**Why?** This is roughly **one paragraph** of information - enough context to be useful, small enough to be relevant.

**The surprise**: Bigger chunks don't always help! After ~600 tokens, retrieval quality actually decreases because irrelevant information dilutes the embedding.

---

## 🔄 Advanced RAG Techniques

### 1. Hybrid Search (BM25 + Vector)

Combine keyword search with semantic search:

```python
def hybrid_search(query: str, k: int = 5) -> list[dict]:
    """Combine BM25 and vector search."""
    # Keyword search (BM25)
    keyword_results = bm25_search(query, k=k*2)

    # Vector search
    vector_results = vector_search(query, k=k*2)

    # Reciprocal Rank Fusion (RRF)
    combined = reciprocal_rank_fusion(
        [keyword_results, vector_results],
        k=60  # RRF constant
    )

    return combined[:k]

def reciprocal_rank_fusion(result_lists: list[list], k: int = 60) -> list:
    """Combine multiple result lists using RRF."""
    scores = {}

    for results in result_lists:
        for rank, doc in enumerate(results):
            doc_id = doc["id"]
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)

    # Sort by combined score
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [doc_id for doc_id, score in sorted_docs]
```

**Why hybrid?**
- **Vector alone** misses exact keyword matches ("error code E1234")
- **BM25 alone** misses semantic similarity ("restart" vs "reboot")
- **Combined** catches both!

### 2. Query Expansion

Expand the query to improve recall:

```python
def expand_query(query: str, llm) -> list[str]:
    """Generate related queries for better retrieval."""
    prompt = f"""Generate 3 alternative phrasings of this question:

Original: {query}

Alternative phrasings (one per line):"""

    expansions = llm.generate(prompt).strip().split("\n")

    return [query] + expansions

# Example:
# Query: "How to fix authentication?"
# Expansions:
#   - "How to fix authentication?"
#   - "Troubleshooting auth issues"
#   - "Authentication not working solution"
#   - "Debug login problems"
```

### 3. Reranking

Use a cross-encoder to rerank retrieved results:

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    """Rerank documents using cross-encoder."""
    # Create query-document pairs
    pairs = [[query, doc["text"]] for doc in documents]

    # Score with cross-encoder
    scores = reranker.predict(pairs)

    # Sort by score
    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, score in ranked[:top_k]]
```

**Why rerank?**
- **Bi-encoders** (embedding models) are fast but less accurate
- **Cross-encoders** see query AND document together, more accurate
- **Best practice**: Retrieve 20 with bi-encoder, rerank to top 5

### 4. Contextual Compression

Remove irrelevant parts from retrieved chunks:

```python
def compress_context(query: str, chunk: str, llm) -> str:
    """Extract only relevant parts of a chunk."""
    prompt = f"""Extract only the parts of this text that are relevant to the question.
If nothing is relevant, respond with "NOT_RELEVANT".

Question: {query}

Text: {chunk}

Relevant excerpt:"""

    compressed = llm.generate(prompt)

    if "NOT_RELEVANT" in compressed:
        return None

    return compressed
```

---

## Did You Know? Perplexity's Secret Sauce

**Perplexity AI** (valued at $9B in 2024) built their entire business on RAG. Their "secret sauce":

1. **Multi-source retrieval**: Searches web, academic papers, news simultaneously
2. **Source diversity**: Ensures answers cite multiple independent sources
3. **Recency bias**: Weights recent sources higher for current events
4. **Streaming citations**: Shows sources WHILE generating answer

**The insight**: Users trust AI more when they can verify sources. Perplexity's citation-first approach built trust that ChatGPT lacked.

**Revenue impact**: $20M ARR in 2024, growing 300% YoY - all from RAG!

---

## ️ Common RAG Pitfalls

### Pitfall 1: Ignoring Chunk Boundaries

```python
# BAD: Fixed chunking breaks mid-concept
chunks = split_every_n_chars(text, 500)
# "To configure authentication, you need to..." | "...set the JWT_SECRET variable"

# GOOD: Respect semantic boundaries
chunks = split_by_paragraphs(text, max_size=500)
# "To configure authentication, you need to set the JWT_SECRET variable."
```

### Pitfall 2: Not Handling "I Don't Know"

```python
# BAD: Forces answer even when context doesn't help
prompt = f"Answer this question: {query}\nContext: {context}"

# GOOD: Explicit instruction for unknown cases
prompt = f"""Answer the question based ONLY on the context below.
If the context doesn't contain enough information to answer, say:
"I don't have information about that in my knowledge base."

Context: {context}
Question: {query}
Answer:"""
```

### Pitfall 3: Stuffing Too Much Context

```python
# BAD: Include all 20 retrieved chunks
context = "\n".join([c["text"] for c in retrieve(query, k=20)])
# → Context too long, LLM gets confused, costs more

# GOOD: Quality over quantity
chunks = retrieve(query, k=20)
reranked = rerank(query, chunks, top_k=5)
context = "\n".join([c["text"] for c in reranked])
# → Only most relevant context
```

### Pitfall 4: Not Including Sources

```python
# BAD: Answer without attribution
answer = llm.generate(f"Answer: {query}\nContext: {context}")

# GOOD: Include sources in prompt
context_with_sources = "\n".join([
    f"[{i+1}] {c['source']}: {c['text']}"
    for i, c in enumerate(chunks)
])

prompt = f"""Answer the question and cite sources using [1], [2], etc.

Context:
{context_with_sources}

Question: {query}
Answer (with citations):"""
```

### Pitfall 5: Stale Index

```python
# BAD: Index once, never update
index_documents(docs)  # Done in 2023
# → 2024 queries get outdated answers!

# GOOD: Incremental updates
def update_index(new_docs, modified_docs, deleted_ids):
    """Keep index fresh."""
    # Add new documents
    for doc in new_docs:
        add_to_index(doc)

    # Update modified documents
    for doc in modified_docs:
        delete_from_index(doc.id)
        add_to_index(doc)

    # Remove deleted documents
    for doc_id in deleted_ids:
        delete_from_index(doc_id)

# Run nightly or on document changes
```

---

## RAG Evaluation Metrics

### Retrieval Metrics

#### Recall@K
"Of the relevant documents, how many did we retrieve?"

```python
def recall_at_k(retrieved_ids: list, relevant_ids: list, k: int) -> float:
    """Calculate recall at k."""
    retrieved_k = set(retrieved_ids[:k])
    relevant = set(relevant_ids)

    return len(retrieved_k & relevant) / len(relevant)

# Example:
# Relevant docs: [1, 2, 3]
# Retrieved top-5: [1, 4, 2, 5, 6]
# Recall@5 = 2/3 = 0.67
```

#### Mean Reciprocal Rank (MRR)
"How high is the first relevant document ranked?"

```python
def mrr(retrieved_ids: list, relevant_ids: list) -> float:
    """Calculate mean reciprocal rank."""
    relevant = set(relevant_ids)

    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant:
            return 1 / (i + 1)

    return 0

# Example:
# Relevant: [1, 2, 3]
# Retrieved: [4, 2, 1, 3, 5]
# First relevant at position 2 → MRR = 1/2 = 0.5
```

### Answer Quality Metrics

#### Faithfulness
"Is the answer supported by the retrieved context?"

```python
def check_faithfulness(answer: str, context: str, llm) -> float:
    """Check if answer is faithful to context."""
    prompt = f"""Rate how well the answer is supported by the context.
Score from 0-1 where:
- 1.0 = Fully supported, no hallucination
- 0.5 = Partially supported
- 0.0 = Not supported / hallucinated

Context: {context}
Answer: {answer}

Score (just the number):"""

    score = float(llm.generate(prompt).strip())
    return score
```

#### Relevance
"Does the answer address the question?"

```python
def check_relevance(query: str, answer: str, llm) -> float:
    """Check if answer is relevant to question."""
    prompt = f"""Rate how well the answer addresses the question.
Score from 0-1 where:
- 1.0 = Directly answers the question
- 0.5 = Partially answers
- 0.0 = Doesn't answer

Question: {query}
Answer: {answer}

Score (just the number):"""

    score = float(llm.generate(prompt).strip())
    return score
```

### The RAGAS Framework

**RAGAS** (Retrieval Augmented Generation Assessment) is the standard evaluation framework:

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

# Evaluate your RAG
results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)

print(f"Faithfulness: {results['faithfulness']:.2f}")
print(f"Answer Relevancy: {results['answer_relevancy']:.2f}")
print(f"Context Precision: {results['context_precision']:.2f}")
```

---

## Real-World Applications

### Application 1: Kaizen Documentation Assistant

```python
# Kaizen RAG Configuration
kaizen_rag = RAGPipeline(
    knowledge_sources=[
        "docs/*.md",           # Documentation
        "src/**/*.py",         # Code (with docstrings)
        "issues/*.json",       # GitHub issues
        "runbooks/*.md"        # Operations runbooks
    ],
    chunk_strategy="recursive",
    chunk_size=500,
    embedding_model="all-MiniLM-L6-v2",
    vector_db="qdrant",
    llm="claude-3-sonnet",
    reranker="cross-encoder/ms-marco"
)

# Example queries:
# "How do I deploy to production?"
# "What's the fix for error E1234?"
# "Show me the authentication flow"
```

### Application 2: Vibe Course Assistant

```python
# Vibe RAG for student Q&A
vibe_rag = RAGPipeline(
    knowledge_sources=[
        "courses/**/*.md",     # Course content
        "videos/*.json",       # Video transcripts
        "qa/*.json",           # Previous Q&A
        "assignments/*.md"     # Assignment specs
    ],
    chunk_strategy="semantic",
    chunk_size=400,
    # Smaller chunks for focused answers
    special_handling={
        "code_blocks": "keep_intact",
        "equations": "keep_intact"
    }
)

# Example queries:
# "Explain the difference between RAG and fine-tuning"
# "What's due next week?"
# "How do I solve problem 3?"
```

### Application 3: Contrarian Financial Research

```python
# Contrarian RAG for financial analysis
contrarian_rag = RAGPipeline(
    knowledge_sources=[
        "sec_filings/*.pdf",   # 10-K, 10-Q filings
        "earnings/*.json",     # Earnings call transcripts
        "news/*.json",         # Financial news
        "analysis/*.md"        # Your analysis notes
    ],
    chunk_strategy="semantic",
    chunk_size=600,
    # Larger chunks for financial context
    metadata_filters=[
        "company",
        "date",
        "document_type"
    ],
    freshness_weight=0.3  # Prefer recent documents
)

# Example queries:
# "What did AAPL management say about AI in last earnings?"
# "Compare MSFT and GOOGL R&D spending"
# "What are the risk factors for TSLA?"
```

---

## Did You Know? The 10x Developer's RAG Setup

A senior engineer at Stripe shared their personal RAG setup (2024):

```
Personal Knowledge Base RAG:
├── Work
│   ├── Codebase (indexed daily)
│   ├── Confluence docs
│   ├── Slack threads (saved)
│   └── Meeting notes
├── Learning
│   ├── Papers I've read (PDFs)
│   ├── Course notes
│   └── Book highlights
└── Personal
    ├── Journal entries
    └── Project ideas

Daily usage:
- "What was the decision on the auth refactor?"
- "Find my notes on transformer attention"
- "What did Sarah say about the deadline?"
```

**Result**: They reported **2 hours saved daily** from not searching through old messages and documents.

**The insight**: RAG isn't just for products - it's a personal productivity superpower!

---

## Further Reading

### Papers
- **"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"** (Lewis et al., 2020) - The original RAG paper
- **"REALM: Retrieval-Augmented Language Model Pre-Training"** (Guu et al., 2020) - RAG during training
- **"Self-RAG"** (Asai et al., 2023) - LLM decides when to retrieve

### Tools & Frameworks
- **LangChain**: Popular RAG framework
- **LlamaIndex**: Data framework for LLM applications
- **Haystack**: End-to-end NLP framework with RAG
- **RAGAS**: RAG evaluation framework

### Tutorials
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [LlamaIndex Getting Started](https://docs.llamaindex.ai/en/stable/)
- [Pinecone RAG Guide](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## Module Summary

**What you learned**:
- RAG architecture: Retrieve → Augment → Generate
- Document chunking strategies and their trade-offs
- Advanced techniques: Hybrid search, reranking, query expansion
- Evaluation metrics: Recall@K, MRR, Faithfulness, Relevance
- Common pitfalls and how to avoid them
- Real-world applications for kaizen, vibe, contrarian

**Key formulas**:
```
RAG = Retrieval + Augmented Generation

Recall@K = |Retrieved ∩ Relevant| / |Relevant|

MRR = 1 / (rank of first relevant document)
```

**Best practices**:
1. **Chunk size**: 400-600 tokens for most use cases
2. **Retrieval**: Start with k=5-10, rerank if needed
3. **Context**: Quality over quantity - don't stuff the prompt
4. **Sources**: Always include citations
5. **Evaluation**: Measure faithfulness AND relevance
6. **Updates**: Keep your index fresh

---

## ️ Next Steps

**Next module**: Module 13: RAG vs Fine-tuning Trade-offs 🔮

You'll learn:
- When to use RAG vs fine-tuning
- Parameter-efficient fine-tuning (LoRA, QLoRA)
- Combining RAG + fine-tuning
- Cost-benefit analysis

**This is another Heureka Moment** - understanding when each approach is appropriate!

---

**🥋 Neural Dojo - You built your first RAG system! 🧠⚡**

---

_Last updated: 2025-11-24_
_Module 12: Building Your First RAG System_
