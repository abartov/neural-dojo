#!/usr/bin/env python3
"""
Module 14 Deliverable: Advanced RAG Toolkit

A comprehensive toolkit implementing advanced RAG patterns:
1. HyDE (Hypothetical Document Embeddings)
2. Hybrid Search (BM25 + Semantic)
3. Cross-Encoder Reranking
4. Self-RAG Critique
5. Production Pipeline combining all patterns

Usage:
    python deliverable_advanced_rag.py demo1      # Compare all search methods
    python deliverable_advanced_rag.py demo2      # HyDE deep dive
    python deliverable_advanced_rag.py demo3      # Full production pipeline
    python deliverable_advanced_rag.py benchmark  # Performance benchmarks
    python deliverable_advanced_rag.py help       # Show help

Author: Neural Dojo
Version: 1.0.0
"""

import os
import sys
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional, Any
from datetime import datetime
import numpy as np

# Check for API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("⚠️  ANTHROPIC_API_KEY not set. HyDE and Self-RAG features will be disabled.")
    HAS_API_KEY = False
else:
    HAS_API_KEY = True

# Import dependencies with graceful fallbacks
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("⚠️  anthropic not installed. Run: pip install anthropic")

try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    print("⚠️  rank-bm25 not installed. Run: pip install rank-bm25")


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SearchResult:
    """A single search result with metadata."""
    document: str
    doc_id: int
    score: float
    method: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PipelineResult:
    """Result from the full RAG pipeline."""
    query: str
    answer: str
    sources: List[SearchResult]
    pipeline_stages: Dict[str, Any]
    total_time_ms: float
    timestamp: str


@dataclass
class BenchmarkResult:
    """Benchmark results for a search method."""
    method: str
    avg_time_ms: float
    results: List[Tuple[int, float]]


# =============================================================================
# Storage Directory
# =============================================================================

STORAGE_DIR = os.path.join(os.path.dirname(__file__), ".advanced_rag")
os.makedirs(STORAGE_DIR, exist_ok=True)


# =============================================================================
# Advanced RAG Toolkit
# =============================================================================

class AdvancedRAGToolkit:
    """
    Comprehensive Advanced RAG Toolkit

    Implements multiple retrieval patterns:
    - HyDE: Hypothetical Document Embeddings
    - Hybrid: BM25 + Semantic search
    - Reranking: Cross-encoder precision boost
    - Self-RAG: Retrieval critique and reflection

    Combine patterns for production-grade RAG!
    """

    def __init__(
        self,
        documents: List[str],
        bi_encoder_model: str = "all-MiniLM-L6-v2",
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        """
        Initialize the toolkit.

        Args:
            documents: List of documents to search
            bi_encoder_model: Model for embedding search
            cross_encoder_model: Model for reranking
        """
        self.documents = documents
        self.doc_count = len(documents)
        print(f"\n📚 Initializing Advanced RAG Toolkit with {self.doc_count} documents")

        # Initialize LLM client
        if HAS_ANTHROPIC and HAS_API_KEY:
            self.llm = Anthropic()
            print("✅ LLM client ready (Claude)")
        else:
            self.llm = None
            print("⚠️  LLM client not available")

        # Initialize embedding model
        if HAS_TRANSFORMERS:
            print(f"   Loading bi-encoder: {bi_encoder_model}")
            self.bi_encoder = SentenceTransformer(bi_encoder_model)
            self.doc_embeddings = self.bi_encoder.encode(
                documents, show_progress_bar=True, convert_to_numpy=True
            )
            print(f"✅ Bi-encoder ready")

            print(f"   Loading cross-encoder: {cross_encoder_model}")
            self.cross_encoder = CrossEncoder(cross_encoder_model)
            print("✅ Cross-encoder ready")
        else:
            self.bi_encoder = None
            self.cross_encoder = None
            self.doc_embeddings = None

        # Initialize BM25
        if HAS_BM25:
            tokenized = [self._tokenize(doc) for doc in documents]
            self.bm25 = BM25Okapi(tokenized)
            print("✅ BM25 index ready")
        else:
            self.bm25 = None

        print(f"\n🎯 Toolkit initialized!\n")

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        import re
        return re.findall(r'\w+', text.lower())

    def _embed(self, texts: List[str]) -> np.ndarray:
        """Embed texts with bi-encoder."""
        if self.bi_encoder:
            return self.bi_encoder.encode(texts, convert_to_numpy=True)
        return np.random.randn(len(texts), 384)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Compute cosine similarity."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b, axis=1))

    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        """Min-max normalize scores."""
        min_s, max_s = scores.min(), scores.max()
        if max_s == min_s:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)

    # =========================================================================
    # Search Methods
    # =========================================================================

    def semantic_search(self, query: str, k: int = 10) -> List[SearchResult]:
        """Pure semantic search with bi-encoder."""
        if self.bi_encoder is None:
            return [SearchResult(self.documents[i], i, 0.0, "semantic")
                    for i in range(min(k, self.doc_count))]

        query_emb = self._embed([query])[0]
        similarities = self._cosine_similarity(query_emb, self.doc_embeddings)

        top_indices = np.argsort(similarities)[::-1][:k]
        return [
            SearchResult(self.documents[i], i, float(similarities[i]), "semantic")
            for i in top_indices
        ]

    def bm25_search(self, query: str, k: int = 10) -> List[SearchResult]:
        """Pure BM25 lexical search."""
        if self.bm25 is None:
            return [SearchResult(self.documents[i], i, 0.0, "bm25")
                    for i in range(min(k, self.doc_count))]

        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)

        top_indices = np.argsort(scores)[::-1][:k]
        return [
            SearchResult(self.documents[i], i, float(scores[i]), "bm25")
            for i in top_indices
        ]

    def hybrid_search(
        self,
        query: str,
        k: int = 10,
        alpha: float = 0.5
    ) -> List[SearchResult]:
        """
        Hybrid search combining BM25 and semantic.

        Args:
            query: Search query
            k: Number of results
            alpha: Weight for semantic (1-alpha for BM25)
        """
        # Get all scores
        semantic_results = self.semantic_search(query, k=self.doc_count)
        bm25_results = self.bm25_search(query, k=self.doc_count)

        # Build score arrays
        semantic_scores = np.zeros(self.doc_count)
        bm25_scores = np.zeros(self.doc_count)

        for r in semantic_results:
            semantic_scores[r.doc_id] = r.score
        for r in bm25_results:
            bm25_scores[r.doc_id] = r.score

        # Normalize and combine
        semantic_norm = self._normalize(semantic_scores)
        bm25_norm = self._normalize(bm25_scores)
        hybrid_scores = alpha * semantic_norm + (1 - alpha) * bm25_norm

        top_indices = np.argsort(hybrid_scores)[::-1][:k]
        return [
            SearchResult(
                self.documents[i], i, float(hybrid_scores[i]), "hybrid",
                {"semantic_score": float(semantic_scores[i]),
                 "bm25_score": float(bm25_scores[i]),
                 "alpha": alpha}
            )
            for i in top_indices
        ]

    def hyde_search(self, query: str, k: int = 10) -> List[SearchResult]:
        """
        HyDE: Hypothetical Document Embeddings search.

        Generate a hypothetical answer, then search for similar docs.
        """
        if self.llm is None:
            print("⚠️  HyDE requires LLM. Using semantic search fallback.")
            return self.semantic_search(query, k)

        # Generate hypothetical document
        prompt = f"""Write a detailed passage that would perfectly answer this question:

Question: {query}

Requirements:
- Write as if from an authoritative technical document
- Include specific details and terminology
- Be comprehensive but focused

Passage:"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        hypothetical = response.content[0].text.strip()

        # Search with hypothetical embedding
        hyde_emb = self._embed([hypothetical])[0]
        similarities = self._cosine_similarity(hyde_emb, self.doc_embeddings)

        top_indices = np.argsort(similarities)[::-1][:k]
        return [
            SearchResult(
                self.documents[i], i, float(similarities[i]), "hyde",
                {"hypothetical": hypothetical[:200] + "..."}
            )
            for i in top_indices
        ]

    def rerank(
        self,
        query: str,
        candidates: List[SearchResult],
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        Rerank candidates with cross-encoder.

        Args:
            query: Original query
            candidates: Initial search results
            top_k: Number of results after reranking
        """
        if self.cross_encoder is None:
            return candidates[:top_k]

        # Score with cross-encoder
        pairs = [[query, r.document] for r in candidates]
        scores = self.cross_encoder.predict(pairs)

        # Sort and return
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

        return [
            SearchResult(
                r.document, r.doc_id, float(score), f"{r.method}+rerank",
                {"original_score": r.score, "rerank_score": float(score)}
            )
            for r, score in ranked[:top_k]
        ]

    def self_critique(
        self,
        query: str,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """
        Self-RAG: Critique and filter results.

        Uses LLM to evaluate if each result is truly relevant.
        """
        if self.llm is None:
            return results

        relevant = []
        for result in results:
            prompt = f"""Evaluate if this passage is relevant to the query.

Query: {query}

Passage: {result.document}

Is this passage relevant and useful for answering the query?
Answer only: RELEVANT or IRRELEVANT"""

            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}]
            )

            verdict = response.content[0].text.strip().upper()
            if "RELEVANT" in verdict:
                result.metadata = result.metadata or {}
                result.metadata["self_critique"] = "passed"
                relevant.append(result)

        return relevant if relevant else results[:3]  # Fallback if all filtered

    # =========================================================================
    # Production Pipeline
    # =========================================================================

    def production_pipeline(
        self,
        query: str,
        k: int = 5,
        use_hyde: bool = True,
        use_hybrid: bool = True,
        use_rerank: bool = True,
        use_self_critique: bool = False
    ) -> PipelineResult:
        """
        Full production RAG pipeline.

        Combines multiple patterns based on configuration.
        """
        start_time = time.time()
        stages = {}

        # Stage 1: Initial retrieval
        stage_start = time.time()
        if use_hyde and self.llm:
            initial_results = self.hyde_search(query, k=30)
            stages["retrieval"] = {"method": "hyde", "candidates": 30}
        elif use_hybrid:
            initial_results = self.hybrid_search(query, k=30)
            stages["retrieval"] = {"method": "hybrid", "candidates": 30}
        else:
            initial_results = self.semantic_search(query, k=30)
            stages["retrieval"] = {"method": "semantic", "candidates": 30}
        stages["retrieval"]["time_ms"] = (time.time() - stage_start) * 1000

        # Stage 2: Reranking
        if use_rerank and self.cross_encoder:
            stage_start = time.time()
            reranked_results = self.rerank(query, initial_results, top_k=10)
            stages["rerank"] = {
                "enabled": True,
                "input": len(initial_results),
                "output": len(reranked_results),
                "time_ms": (time.time() - stage_start) * 1000
            }
        else:
            reranked_results = initial_results[:10]
            stages["rerank"] = {"enabled": False}

        # Stage 3: Self-critique
        if use_self_critique and self.llm:
            stage_start = time.time()
            final_results = self.self_critique(query, reranked_results[:k])
            stages["self_critique"] = {
                "enabled": True,
                "input": len(reranked_results),
                "output": len(final_results),
                "time_ms": (time.time() - stage_start) * 1000
            }
        else:
            final_results = reranked_results[:k]
            stages["self_critique"] = {"enabled": False}

        # Stage 4: Generate answer
        stage_start = time.time()
        if self.llm:
            context = "\n\n".join([f"[{i+1}] {r.document}" for i, r in enumerate(final_results)])
            prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Provide a comprehensive answer based only on the context provided. Cite sources using [1], [2], etc."""

            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text.strip()
            stages["generation"] = {"time_ms": (time.time() - stage_start) * 1000}
        else:
            answer = "LLM not available for answer generation."
            stages["generation"] = {"time_ms": 0}

        total_time = (time.time() - start_time) * 1000

        return PipelineResult(
            query=query,
            answer=answer,
            sources=final_results,
            pipeline_stages=stages,
            total_time_ms=total_time,
            timestamp=datetime.now().isoformat()
        )

    # =========================================================================
    # Comparison and Benchmarking
    # =========================================================================

    def compare_methods(self, query: str, k: int = 5) -> Dict[str, List[SearchResult]]:
        """Compare all search methods on a query."""
        results = {}

        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")

        methods = [
            ("Semantic", lambda: self.semantic_search(query, k)),
            ("BM25", lambda: self.bm25_search(query, k)),
            ("Hybrid", lambda: self.hybrid_search(query, k)),
        ]

        if self.llm:
            methods.append(("HyDE", lambda: self.hyde_search(query, k)))

        for name, method in methods:
            start = time.time()
            method_results = method()
            elapsed = (time.time() - start) * 1000

            results[name.lower()] = method_results

            print(f"\n📊 {name} Search ({elapsed:.1f}ms):")
            for i, r in enumerate(method_results, 1):
                print(f"   {i}. [Score: {r.score:.4f}] {r.document[:60]}...")

        return results

    def benchmark(self, queries: List[str], k: int = 5) -> Dict[str, BenchmarkResult]:
        """Benchmark all methods on multiple queries."""
        methods = {
            "semantic": self.semantic_search,
            "bm25": self.bm25_search,
            "hybrid": self.hybrid_search,
        }

        if self.llm:
            methods["hyde"] = self.hyde_search

        benchmarks = {}

        for method_name, method in methods.items():
            times = []
            all_results = []

            for query in queries:
                start = time.time()
                results = method(query, k)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                all_results.extend([(r.doc_id, r.score) for r in results])

            benchmarks[method_name] = BenchmarkResult(
                method=method_name,
                avg_time_ms=np.mean(times),
                results=all_results[:10]
            )

        return benchmarks

    def save_results(self, results: Any, filename: str):
        """Save results to JSON."""
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, 'w') as f:
            if hasattr(results, '__dict__'):
                json.dump(asdict(results), f, indent=2, default=str)
            else:
                json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to {filepath}")


# =============================================================================
# Sample Documents
# =============================================================================

SAMPLE_DOCUMENTS = [
    "Python performance optimization requires understanding common bottlenecks. The Global Interpreter Lock (GIL) prevents true parallel execution of threads for CPU-bound tasks. Use multiprocessing for CPU-intensive operations and asyncio for I/O-bound tasks. Profile with cProfile before optimizing.",

    "Memory management in Python uses reference counting with garbage collection. Memory leaks can occur through circular references or holding references to large objects. Use the gc module to debug and objgraph to visualize object graphs.",

    "Database query optimization starts with proper indexing. Use EXPLAIN to analyze slow queries. Avoid N+1 problems with eager loading. Consider query caching for frequently accessed data and batch operations for bulk updates.",

    "API rate limiting protects services from abuse. Implement using token bucket or sliding window algorithms. Store state in Redis for distributed systems. Return 429 status codes with Retry-After headers.",

    "Error handling best practices include using specific exception types, logging errors with context, and providing meaningful messages. Use try-except blocks sparingly. Implement circuit breakers for external services.",

    "Caching strategies improve performance by storing computed results. Use Redis or Memcached for distributed caching. Implement cache invalidation carefully. Use cache-aside pattern for read-heavy workloads.",

    "Testing strategies include unit tests with pytest, integration tests with fixtures, and end-to-end tests. Use mocking for external dependencies. Focus on critical paths. Use property-based testing for edge cases.",

    "Security best practices include input validation, parameterized queries, proper authentication. Use HTTPS everywhere. Implement CSRF protection. Store passwords with bcrypt. Update dependencies regularly.",

    "Microservices communication uses REST/gRPC for synchronous calls and RabbitMQ/Kafka for async. Implement service discovery and load balancing. Use circuit breakers. Design for eventual consistency.",

    "Kubernetes deployments use pods, services, and deployments. Configure resource limits and requests. Use liveness and readiness probes. Implement horizontal pod autoscaling for variable load.",

    "Docker containers package applications with dependencies. Use multi-stage builds for smaller images. Configure health checks. Use docker-compose for local development. Implement proper logging.",

    "CI/CD pipelines automate testing and deployment. Use GitHub Actions or GitLab CI. Implement automated testing gates. Use blue-green or canary deployments. Monitor deployment health.",

    "Monitoring with Prometheus collects metrics. Grafana visualizes dashboards. Set up alerting for critical thresholds. Implement distributed tracing with Jaeger or Zipkin for microservices.",

    "Logging best practices include structured JSON format, consistent log levels, and correlation IDs. Use centralized logging with ELK stack. Configure retention policies. Avoid logging sensitive data.",

    "Vector databases like Qdrant and Pinecone store embeddings for semantic search. They use approximate nearest neighbor algorithms like HNSW. Support metadata filtering and hybrid search."
]


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_compare_methods():
    """Demo 1: Compare all search methods."""
    print("\n" + "="*70)
    print("DEMO 1: Comparing Search Methods")
    print("="*70)
    print("""
This demo compares all search methods on the same queries:
- Semantic: Pure embedding similarity
- BM25: Lexical term matching
- Hybrid: Combined BM25 + Semantic
- HyDE: Hypothetical document search (if LLM available)
    """)

    toolkit = AdvancedRAGToolkit(SAMPLE_DOCUMENTS)

    queries = [
        "How do I make my Python code faster?",
        "error handling best practices",
        "Kubernetes pod configuration",
    ]

    for query in queries:
        toolkit.compare_methods(query, k=3)

    print("\n✅ Demo 1 Complete!")


def demo_2_hyde_deep_dive():
    """Demo 2: HyDE in detail."""
    print("\n" + "="*70)
    print("DEMO 2: HyDE Deep Dive")
    print("="*70)
    print("""
HyDE generates hypothetical documents that would answer the query,
then searches for real documents similar to the hypothetical.

This bridges the query-document language gap!
    """)

    if not HAS_API_KEY:
        print("⚠️  ANTHROPIC_API_KEY required for HyDE demo.")
        return

    toolkit = AdvancedRAGToolkit(SAMPLE_DOCUMENTS)

    queries = [
        "Why is my application slow?",
        "How should I structure my tests?",
        "What's the best way to deploy my app?",
    ]

    for query in queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")

        # Traditional search
        print("\n📊 Traditional Semantic Search:")
        semantic = toolkit.semantic_search(query, k=3)
        for i, r in enumerate(semantic, 1):
            print(f"   {i}. {r.document[:60]}...")

        # HyDE search
        print("\n📊 HyDE Search:")
        hyde = toolkit.hyde_search(query, k=3)
        for i, r in enumerate(hyde, 1):
            print(f"   {i}. {r.document[:60]}...")

        if hyde[0].metadata:
            print(f"\n💡 Generated Hypothetical:\n   {hyde[0].metadata.get('hypothetical', '')}")

    print("\n✅ Demo 2 Complete!")


def demo_3_production_pipeline():
    """Demo 3: Full production pipeline."""
    print("\n" + "="*70)
    print("DEMO 3: Production RAG Pipeline")
    print("="*70)
    print("""
The production pipeline combines:
1. HyDE or Hybrid retrieval
2. Cross-encoder reranking
3. Self-RAG critique (optional)
4. LLM answer generation

Each stage is timed for performance analysis.
    """)

    toolkit = AdvancedRAGToolkit(SAMPLE_DOCUMENTS)

    queries = [
        "How should I implement caching in my Python application?",
        "What are the best practices for API security?",
    ]

    for query in queries:
        print(f"\n{'='*70}")
        result = toolkit.production_pipeline(
            query,
            k=3,
            use_hyde=HAS_API_KEY,
            use_hybrid=True,
            use_rerank=True,
            use_self_critique=False
        )

        print(f"Query: {result.query}")
        print(f"\n📊 Pipeline Stages:")
        for stage, info in result.pipeline_stages.items():
            print(f"   {stage}: {info}")

        print(f"\n📝 Answer:\n{result.answer}")

        print(f"\n📚 Sources:")
        for i, source in enumerate(result.sources, 1):
            print(f"   [{i}] {source.document[:60]}...")

        print(f"\n⏱️  Total Time: {result.total_time_ms:.1f}ms")

        # Save results
        toolkit.save_results(result, f"pipeline_result_{int(time.time())}.json")

    print("\n✅ Demo 3 Complete!")


def benchmark_all():
    """Benchmark all methods."""
    print("\n" + "="*70)
    print("BENCHMARK: Performance Comparison")
    print("="*70)

    toolkit = AdvancedRAGToolkit(SAMPLE_DOCUMENTS)

    queries = [
        "Python performance optimization",
        "database query best practices",
        "Kubernetes deployment configuration",
        "API rate limiting implementation",
        "error handling patterns",
    ]

    print(f"\nRunning benchmark with {len(queries)} queries...")

    results = toolkit.benchmark(queries, k=5)

    print("\n📊 Benchmark Results:")
    print("-" * 50)
    print(f"{'Method':<15} {'Avg Time (ms)':<15}")
    print("-" * 50)

    for name, benchmark in sorted(results.items(), key=lambda x: x[1].avg_time_ms):
        print(f"{name:<15} {benchmark.avg_time_ms:<15.2f}")

    print("-" * 50)

    # Save benchmark
    filepath = os.path.join(STORAGE_DIR, f"benchmark_{int(time.time())}.json")
    with open(filepath, 'w') as f:
        json.dump({k: asdict(v) for k, v in results.items()}, f, indent=2)
    print(f"\n💾 Benchmark saved to {filepath}")

    print("\n✅ Benchmark Complete!")


def show_help():
    """Show help information."""
    print("""
Advanced RAG Toolkit - Module 14 Deliverable
=============================================

Usage:
    python deliverable_advanced_rag.py <command>

Commands:
    demo1      Compare all search methods (semantic, BM25, hybrid, HyDE)
    demo2      HyDE deep dive with hypothetical generation
    demo3      Full production pipeline with answer generation
    benchmark  Performance comparison of all methods
    help       Show this help message

Requirements:
    - ANTHROPIC_API_KEY environment variable (for HyDE and generation)
    - sentence-transformers (pip install sentence-transformers)
    - rank-bm25 (pip install rank-bm25)

Examples:
    python deliverable_advanced_rag.py demo1
    python deliverable_advanced_rag.py benchmark

Output:
    Results are saved to .advanced_rag/ directory as JSON files.
    """)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point."""
    print("="*70)
    print("Advanced RAG Toolkit - Module 14 Deliverable")
    print("="*70)

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_compare_methods()
    elif command == "demo2":
        demo_2_hyde_deep_dive()
    elif command == "demo3":
        demo_3_production_pipeline()
    elif command == "benchmark":
        benchmark_all()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
