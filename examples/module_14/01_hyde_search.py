#!/usr/bin/env python3
"""
Module 14 Example 1: HyDE (Hypothetical Document Embeddings)

Demonstrates how HyDE improves retrieval by generating hypothetical
documents that match document language better than queries.

Key Insight: Questions and answers use different language!
HyDE bridges this gap by generating document-like text from queries.
"""

import os
import json
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from anthropic import Anthropic

# Try to import sentence-transformers, provide fallback
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("⚠️  sentence-transformers not installed. Using mock embeddings.")


@dataclass
class SearchResult:
    """A search result with document and score."""
    document: str
    score: float
    method: str


class HyDESearch:
    """
    HyDE: Hypothetical Document Embeddings

    Instead of embedding the query directly, we:
    1. Generate a hypothetical document that would answer the query
    2. Embed that hypothetical document
    3. Search for real documents similar to the hypothetical

    This works because generated text uses document-like language!
    """

    def __init__(self, documents: List[str], model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize HyDE search.

        Args:
            documents: List of documents to search
            model_name: Sentence transformer model for embeddings
        """
        self.documents = documents
        self.client = Anthropic()

        # Initialize embedding model
        if HAS_SENTENCE_TRANSFORMERS:
            self.model = SentenceTransformer(model_name)
            print(f"✅ Loaded embedding model: {model_name}")
        else:
            self.model = None

        # Pre-compute document embeddings
        self.doc_embeddings = self._embed_documents()
        print(f"✅ Indexed {len(documents)} documents")

    def _embed_documents(self) -> np.ndarray:
        """Embed all documents."""
        if self.model:
            return self.model.encode(self.documents, show_progress_bar=True)
        else:
            # Mock embeddings for demo
            return np.random.randn(len(self.documents), 384)

    def _embed(self, text: str) -> np.ndarray:
        """Embed a single text."""
        if self.model:
            return self.model.encode([text])[0]
        else:
            # Mock embedding
            np.random.seed(hash(text) % 2**32)
            return np.random.randn(384)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def generate_hypothetical(self, query: str, num_hypotheticals: int = 1) -> List[str]:
        """
        Generate hypothetical documents that would answer the query.

        Args:
            query: The user's question
            num_hypotheticals: Number of hypotheticals to generate

        Returns:
            List of hypothetical documents
        """
        hypotheticals = []

        for i in range(num_hypotheticals):
            angle = ""
            if num_hypotheticals > 1:
                angles = ["technical details", "practical examples", "conceptual explanation"]
                angle = f"\n\nFocus on: {angles[i % len(angles)]}"

            prompt = f"""Write a detailed passage that would perfectly answer this question:

Question: {query}

Requirements:
- Write as if this is from an authoritative technical document
- Include specific details, examples, and terminology
- Use the language style found in documentation and tutorials
- Be comprehensive but focused{angle}

Passage:"""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            hypothetical = response.content[0].text.strip()
            hypotheticals.append(hypothetical)

        return hypotheticals

    def traditional_search(self, query: str, k: int = 5) -> List[SearchResult]:
        """
        Traditional semantic search - embed query directly.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of search results
        """
        query_embedding = self._embed(query)

        # Compute similarities
        similarities = [
            self._cosine_similarity(query_embedding, doc_emb)
            for doc_emb in self.doc_embeddings
        ]

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:k]

        return [
            SearchResult(
                document=self.documents[i],
                score=similarities[i],
                method="traditional"
            )
            for i in top_indices
        ]

    def hyde_search(self, query: str, k: int = 5, num_hypotheticals: int = 1) -> List[SearchResult]:
        """
        HyDE search - generate hypothetical, then search.

        Args:
            query: Search query
            k: Number of results to return
            num_hypotheticals: Number of hypothetical documents to generate

        Returns:
            List of search results
        """
        # Step 1: Generate hypothetical document(s)
        print(f"\n🔮 Generating {num_hypotheticals} hypothetical document(s)...")
        hypotheticals = self.generate_hypothetical(query, num_hypotheticals)

        for i, hyp in enumerate(hypotheticals):
            print(f"\n📄 Hypothetical {i+1}:\n{hyp[:200]}...")

        # Step 2: Embed hypotheticals
        hyde_embeddings = [self._embed(h) for h in hypotheticals]

        # Step 3: Average embeddings if multiple
        if len(hyde_embeddings) > 1:
            hyde_embedding = np.mean(hyde_embeddings, axis=0)
        else:
            hyde_embedding = hyde_embeddings[0]

        # Step 4: Search with HyDE embedding
        similarities = [
            self._cosine_similarity(hyde_embedding, doc_emb)
            for doc_emb in self.doc_embeddings
        ]

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:k]

        return [
            SearchResult(
                document=self.documents[i],
                score=similarities[i],
                method="hyde"
            )
            for i in top_indices
        ]

    def compare_methods(self, query: str, k: int = 3) -> dict:
        """
        Compare traditional vs HyDE search.

        Args:
            query: Search query
            k: Number of results

        Returns:
            Comparison dictionary
        """
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Traditional search
        print("\n📊 Traditional Semantic Search:")
        traditional_results = self.traditional_search(query, k)
        for i, result in enumerate(traditional_results, 1):
            print(f"\n  {i}. Score: {result.score:.4f}")
            print(f"     {result.document[:100]}...")

        # HyDE search
        print("\n📊 HyDE Search:")
        hyde_results = self.hyde_search(query, k)
        for i, result in enumerate(hyde_results, 1):
            print(f"\n  {i}. Score: {result.score:.4f}")
            print(f"     {result.document[:100]}...")

        return {
            "query": query,
            "traditional": [{"doc": r.document, "score": r.score} for r in traditional_results],
            "hyde": [{"doc": r.document, "score": r.score} for r in hyde_results]
        }


# Sample technical documents for demonstration
SAMPLE_DOCUMENTS = [
    """Performance optimization in Python applications requires understanding common bottlenecks.
    The Global Interpreter Lock (GIL) prevents true parallel execution of threads for CPU-bound tasks.
    For CPU-intensive operations, use multiprocessing instead of threading. For I/O-bound tasks,
    asyncio provides efficient concurrency. Profile your code with cProfile to identify hotspots
    before optimizing.""",

    """Memory management in Python is handled automatically through reference counting and garbage
    collection. However, memory leaks can still occur through circular references or holding
    references to large objects. Use the gc module to debug memory issues and objgraph to
    visualize object graphs. Consider using __slots__ for memory-efficient classes.""",

    """Database query optimization starts with proper indexing. Analyze slow queries using EXPLAIN.
    Avoid N+1 query problems by using eager loading (joinedload in SQLAlchemy). Consider query
    caching for frequently accessed data. Use connection pooling to reduce connection overhead.
    Batch operations for bulk inserts and updates.""",

    """API rate limiting protects services from abuse and ensures fair resource allocation.
    Implement using token bucket or sliding window algorithms. Store rate limit state in Redis
    for distributed systems. Return 429 status codes with Retry-After headers. Consider
    different limits for authenticated vs anonymous users.""",

    """Error handling best practices include using specific exception types, logging errors with
    context, and providing meaningful error messages. Use try-except blocks sparingly and only
    catch exceptions you can handle. Implement circuit breakers for external service calls.
    Always clean up resources in finally blocks or use context managers.""",

    """Caching strategies improve application performance by storing computed results. Use
    Redis or Memcached for distributed caching. Implement cache invalidation carefully to
    avoid stale data. Consider cache warming for predictable access patterns. Use cache-aside
    pattern for read-heavy workloads.""",

    """Logging best practices include structured logging with JSON format, consistent log levels,
    and correlation IDs for request tracing. Use logging libraries like structlog or loguru.
    Avoid logging sensitive data. Configure log rotation and retention policies. Ship logs
    to centralized systems like ELK or Datadog.""",

    """Testing strategies for Python include unit tests with pytest, integration tests with
    fixtures, and end-to-end tests with selenium or playwright. Use mocking for external
    dependencies. Aim for high coverage but focus on critical paths. Use property-based
    testing with hypothesis for edge cases.""",

    """Security best practices include input validation, parameterized queries to prevent SQL
    injection, and proper authentication/authorization. Use HTTPS everywhere. Implement CSRF
    protection for web forms. Store passwords with bcrypt. Regularly update dependencies
    and scan for vulnerabilities.""",

    """Microservices communication patterns include synchronous REST/gRPC and asynchronous
    messaging with RabbitMQ or Kafka. Implement service discovery and load balancing.
    Use circuit breakers for resilience. Consider event sourcing for complex domains.
    Design for eventual consistency."""
]


def demo_basic_hyde():
    """Demonstrate basic HyDE search."""
    print("\n" + "="*60)
    print("DEMO 1: Basic HyDE Search")
    print("="*60)

    searcher = HyDESearch(SAMPLE_DOCUMENTS)

    # Query that uses different language than documents
    query = "Why is my Python code running slowly?"

    # This query asks about "slow code" but documents talk about
    # "performance optimization", "bottlenecks", "GIL", etc.

    results = searcher.compare_methods(query, k=3)
    return results


def demo_multi_hyde():
    """Demonstrate multi-hypothetical HyDE."""
    print("\n" + "="*60)
    print("DEMO 2: Multi-Hypothetical HyDE")
    print("="*60)

    searcher = HyDESearch(SAMPLE_DOCUMENTS)

    query = "How do I prevent security vulnerabilities?"

    print(f"\nQuery: {query}")
    print("\n🔮 Generating multiple hypotheticals for better coverage...")

    # Generate 3 hypotheticals from different angles
    results = searcher.hyde_search(query, k=3, num_hypotheticals=3)

    print("\n📊 Multi-HyDE Results:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. Score: {result.score:.4f}")
        print(f"     {result.document[:150]}...")

    return results


def demo_technical_queries():
    """Demonstrate HyDE with various technical queries."""
    print("\n" + "="*60)
    print("DEMO 3: Technical Query Comparison")
    print("="*60)

    searcher = HyDESearch(SAMPLE_DOCUMENTS)

    queries = [
        "How do I make my database queries faster?",
        "What's the best way to handle errors in my API?",
        "How should I structure my tests?",
    ]

    all_results = []
    for query in queries:
        result = searcher.compare_methods(query, k=2)
        all_results.append(result)

    return all_results


def main():
    """Run all demos."""
    print("="*60)
    print("HyDE: Hypothetical Document Embeddings")
    print("="*60)
    print("""
HyDE improves retrieval by generating hypothetical documents
that answer the query, then searching for similar real documents.

Key insight: User queries and document text use different language!
- Query: "Why is my code slow?"
- Document: "Performance optimization techniques include..."

HyDE bridges this gap!
    """)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set. Set it to run demos.")
        return

    # Run demos
    demo_basic_hyde()
    demo_multi_hyde()
    demo_technical_queries()

    print("\n" + "="*60)
    print("✅ HyDE Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
