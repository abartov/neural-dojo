#!/usr/bin/env python3
"""
Module 14 Example 3: Cross-Encoder Reranking

Demonstrates two-stage retrieval with cross-encoder reranking
for improved precision.

Key Insight:
- Bi-encoders (Stage 1): Fast but query/doc encoded separately
- Cross-encoders (Stage 2): Slow but query+doc encoded together = more accurate!

Two-stage approach: Fast recall → Precise reranking
"""

import os
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

# Try to import dependencies
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠️  sentence-transformers not installed.")
    print("   Run: pip install sentence-transformers")


@dataclass
class RankedResult:
    """A reranked search result."""
    document: str
    doc_id: int
    initial_rank: int
    initial_score: float
    reranked_score: float
    final_rank: int


class TwoStageRetriever:
    """
    Two-Stage Retrieval with Reranking

    Stage 1: Fast bi-encoder retrieval (recall-focused)
    Stage 2: Slower cross-encoder reranking (precision-focused)

    Why this works:
    - Bi-encoders encode query and documents separately
      - Fast: Can pre-compute document embeddings
      - Less accurate: Query and doc don't "see" each other

    - Cross-encoders encode [query, document] together
      - Slow: Must compute for each query-doc pair
      - More accurate: Query and doc interact during encoding

    Solution: Use bi-encoder to get candidates, cross-encoder to rerank!
    """

    def __init__(
        self,
        documents: List[str],
        bi_encoder_model: str = "all-MiniLM-L6-v2",
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        """
        Initialize two-stage retriever.

        Args:
            documents: List of documents to search
            bi_encoder_model: Model for initial retrieval
            cross_encoder_model: Model for reranking
        """
        self.documents = documents

        if not HAS_TRANSFORMERS:
            print("⚠️  sentence-transformers required")
            self.bi_encoder = None
            self.cross_encoder = None
            return

        # Initialize bi-encoder for Stage 1
        print(f"Loading bi-encoder: {bi_encoder_model}")
        self.bi_encoder = SentenceTransformer(bi_encoder_model)
        self.doc_embeddings = self.bi_encoder.encode(
            documents,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        print(f"✅ Bi-encoder ready, indexed {len(documents)} documents")

        # Initialize cross-encoder for Stage 2
        print(f"Loading cross-encoder: {cross_encoder_model}")
        self.cross_encoder = CrossEncoder(cross_encoder_model)
        print("✅ Cross-encoder ready")

    def stage1_retrieve(self, query: str, k: int = 50) -> List[Tuple[int, float]]:
        """
        Stage 1: Fast bi-encoder retrieval.

        Returns top-k candidates based on cosine similarity.
        """
        if self.bi_encoder is None:
            return [(i, 0.0) for i in range(min(k, len(self.documents)))]

        # Encode query
        query_embedding = self.bi_encoder.encode([query], convert_to_numpy=True)[0]

        # Compute cosine similarities
        similarities = np.dot(self.doc_embeddings, query_embedding) / (
            np.linalg.norm(self.doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:k]
        return [(int(i), float(similarities[i])) for i in top_indices]

    def stage2_rerank(
        self,
        query: str,
        candidates: List[Tuple[int, float]],
        top_k: int = 10
    ) -> List[Tuple[int, float, int, float]]:
        """
        Stage 2: Cross-encoder reranking.

        Returns reranked results with both initial and reranked scores.
        Format: [(doc_id, reranked_score, initial_rank, initial_score), ...]
        """
        if self.cross_encoder is None:
            return [(doc_id, score, rank, score)
                    for rank, (doc_id, score) in enumerate(candidates[:top_k])]

        # Create query-document pairs
        doc_ids = [doc_id for doc_id, _ in candidates]
        pairs = [[query, self.documents[doc_id]] for doc_id in doc_ids]

        # Score with cross-encoder
        scores = self.cross_encoder.predict(pairs)

        # Combine with original info
        results = [
            (doc_ids[i], float(scores[i]), i, candidates[i][1])
            for i in range(len(candidates))
        ]

        # Sort by reranked score
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def search(
        self,
        query: str,
        k: int = 5,
        candidates: int = 50
    ) -> List[RankedResult]:
        """
        Full two-stage search.

        Args:
            query: Search query
            k: Final number of results
            candidates: Number of candidates for reranking

        Returns:
            List of reranked results
        """
        # Stage 1
        start = time.time()
        initial_results = self.stage1_retrieve(query, k=candidates)
        stage1_time = time.time() - start

        # Stage 2
        start = time.time()
        reranked = self.stage2_rerank(query, initial_results, top_k=k)
        stage2_time = time.time() - start

        print(f"⏱️  Stage 1 (bi-encoder): {stage1_time*1000:.1f}ms")
        print(f"⏱️  Stage 2 (cross-encoder): {stage2_time*1000:.1f}ms")

        return [
            RankedResult(
                document=self.documents[doc_id],
                doc_id=doc_id,
                initial_rank=initial_rank + 1,
                initial_score=initial_score,
                reranked_score=reranked_score,
                final_rank=final_rank + 1
            )
            for final_rank, (doc_id, reranked_score, initial_rank, initial_score)
            in enumerate(reranked)
        ]

    def compare_with_without_reranking(self, query: str, k: int = 5) -> dict:
        """
        Compare results with and without reranking.
        """
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")

        # Without reranking (bi-encoder only)
        print("\n📊 WITHOUT Reranking (Bi-encoder only):")
        initial_results = self.stage1_retrieve(query, k=k)
        for rank, (doc_id, score) in enumerate(initial_results, 1):
            print(f"  {rank}. [Score: {score:.4f}] {self.documents[doc_id][:70]}...")

        # With reranking
        print("\n📊 WITH Reranking (Two-stage):")
        reranked_results = self.search(query, k=k, candidates=20)
        for result in reranked_results:
            rank_change = result.initial_rank - result.final_rank
            change_str = f"↑{rank_change}" if rank_change > 0 else (
                f"↓{-rank_change}" if rank_change < 0 else "="
            )
            print(f"  {result.final_rank}. [Score: {result.reranked_score:.4f}] "
                  f"(was #{result.initial_rank}, {change_str})")
            print(f"     {result.document[:70]}...")

        return {
            "query": query,
            "without_reranking": [(r[0], r[1]) for r in initial_results],
            "with_reranking": [(r.doc_id, r.reranked_score) for r in reranked_results]
        }


# Sample documents for reranking demonstration
SAMPLE_DOCUMENTS = [
    # Highly relevant to "Python performance"
    "Python performance optimization requires understanding the GIL and using appropriate "
    "concurrency patterns. For CPU-bound tasks, use multiprocessing; for I/O-bound, use asyncio.",

    "To speed up Python code, profile with cProfile first, then optimize hot paths. "
    "Consider using NumPy for numerical operations and Cython for critical sections.",

    # Somewhat relevant
    "Python is a popular programming language known for its readability and extensive ecosystem. "
    "It supports multiple paradigms including procedural, object-oriented, and functional programming.",

    "Memory management in Python uses reference counting with a cyclic garbage collector. "
    "Understanding this can help write more memory-efficient code.",

    "The Python standard library includes modules for file I/O, networking, and data processing. "
    "Third-party packages can be installed using pip from PyPI.",

    # Less relevant but contains keywords
    "Python decorators are a powerful feature for modifying function behavior. "
    "Common uses include logging, caching, and access control.",

    "Type hints in Python improve code readability and enable static analysis with mypy. "
    "They don't affect runtime performance but help catch bugs early.",

    # Relevant to different aspect of performance
    "Database query optimization in Python applications often involves using ORM features "
    "like eager loading, query caching, and proper indexing strategies.",

    "Async Python programming with asyncio enables efficient handling of concurrent I/O operations. "
    "It's particularly useful for web scraping, API calls, and database operations.",

    # Not relevant
    "Machine learning with Python typically uses libraries like scikit-learn, TensorFlow, and PyTorch. "
    "These frameworks provide tools for training and deploying models.",

    "Web development in Python commonly uses frameworks like Django, Flask, and FastAPI. "
    "Each has different strengths for building web applications.",

    "Testing Python code is essential for maintainability. pytest is the most popular testing "
    "framework, supporting fixtures, parameterized tests, and plugins.",

    # Tangentially related
    "JIT compilation with PyPy can significantly speed up Python code without modification. "
    "However, compatibility with C extensions may be limited.",

    "Profiling Python memory usage with tools like memory_profiler and objgraph helps "
    "identify memory leaks and optimize memory-intensive operations.",

    "Python packaging has evolved from setup.py to pyproject.toml. Modern tools like Poetry "
    "and PDM simplify dependency management and distribution."
]


def demo_basic_reranking():
    """Demonstrate basic two-stage retrieval."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Two-Stage Reranking")
    print("="*70)
    print("""
The cross-encoder sees query and document TOGETHER,
allowing for more nuanced relevance scoring.
    """)

    retriever = TwoStageRetriever(SAMPLE_DOCUMENTS)

    query = "how to make Python code run faster"
    retriever.compare_with_without_reranking(query, k=5)


def demo_rank_changes():
    """Show dramatic rank changes from reranking."""
    print("\n" + "="*70)
    print("DEMO 2: Observing Rank Changes")
    print("="*70)
    print("""
Watch how documents move up or down after reranking.
Cross-encoders often promote highly relevant documents
that bi-encoders ranked lower.
    """)

    retriever = TwoStageRetriever(SAMPLE_DOCUMENTS)

    queries = [
        "Python async programming for web scraping",
        "how to profile memory usage in Python",
        "Python type hints and static analysis"
    ]

    for query in queries:
        print(f"\n📊 Query: {query}")
        results = retriever.search(query, k=3, candidates=15)

        print("\nRank changes:")
        for result in results:
            change = result.initial_rank - result.final_rank
            if change > 0:
                print(f"  ↑{change} places: #{result.initial_rank} → #{result.final_rank}")
            elif change < 0:
                print(f"  ↓{-change} places: #{result.initial_rank} → #{result.final_rank}")
            else:
                print(f"  = stayed: #{result.final_rank}")
            print(f"      {result.document[:60]}...")


def demo_timing_comparison():
    """Compare timing of different approaches."""
    print("\n" + "="*70)
    print("DEMO 3: Timing Comparison")
    print("="*70)
    print("""
Cross-encoders are slower but more accurate.
Two-stage retrieval balances speed and quality.
    """)

    retriever = TwoStageRetriever(SAMPLE_DOCUMENTS)

    query = "optimizing Python for performance"

    # Time bi-encoder only
    start = time.time()
    for _ in range(10):
        retriever.stage1_retrieve(query, k=5)
    bi_time = (time.time() - start) / 10

    # Time two-stage
    start = time.time()
    for _ in range(10):
        retriever.search(query, k=5, candidates=20)
    two_stage_time = (time.time() - start) / 10

    # Time hypothetical full cross-encoder (all docs)
    if retriever.cross_encoder:
        pairs = [[query, doc] for doc in SAMPLE_DOCUMENTS]
        start = time.time()
        for _ in range(10):
            retriever.cross_encoder.predict(pairs)
        full_cross_time = (time.time() - start) / 10
    else:
        full_cross_time = 0

    print(f"\n⏱️  Timing Results (averaged over 10 runs):")
    print(f"   Bi-encoder only:          {bi_time*1000:.1f}ms")
    print(f"   Two-stage (20 candidates): {two_stage_time*1000:.1f}ms")
    print(f"   Full cross-encoder:        {full_cross_time*1000:.1f}ms")
    print(f"\n   Two-stage is {full_cross_time/two_stage_time:.1f}x faster than full cross-encoder!")
    print(f"   But only {two_stage_time/bi_time:.1f}x slower than bi-encoder only.")


def demo_candidate_count():
    """Show effect of candidate count on quality and speed."""
    print("\n" + "="*70)
    print("DEMO 4: Candidate Count Trade-off")
    print("="*70)
    print("""
More candidates = better quality (higher recall)
                = slower reranking

Find the sweet spot for your use case!
    """)

    retriever = TwoStageRetriever(SAMPLE_DOCUMENTS)
    query = "Python performance profiling"

    for candidates in [5, 10, 20, 50]:
        print(f"\n📊 Candidates: {candidates}")
        start = time.time()
        results = retriever.search(query, k=3, candidates=candidates)
        elapsed = time.time() - start

        print(f"   Time: {elapsed*1000:.1f}ms")
        print(f"   Top result: {results[0].document[:50]}...")


def main():
    """Run all demos."""
    print("="*70)
    print("Two-Stage Retrieval with Cross-Encoder Reranking")
    print("="*70)
    print("""
Two-stage retrieval combines:

Stage 1 - Bi-encoder (Fast, Recall-focused):
  - Query and docs encoded separately
  - Can pre-compute document embeddings
  - Gets many candidates quickly

Stage 2 - Cross-encoder (Slow, Precision-focused):
  - Query and doc encoded TOGETHER
  - Much more accurate relevance scoring
  - Only runs on top candidates

Result: Speed of bi-encoder + Accuracy of cross-encoder!
    """)

    if not HAS_TRANSFORMERS:
        print("\n⚠️  Install sentence-transformers:")
        print("   pip install sentence-transformers")
        return

    # Run demos
    demo_basic_reranking()
    demo_rank_changes()
    demo_timing_comparison()
    demo_candidate_count()

    print("\n" + "="*70)
    print("✅ Reranking Demo Complete!")
    print("="*70)
    print("""
Key Takeaways:
1. Cross-encoders are 5-10x more accurate than bi-encoders
2. But 10-50x slower (can't pre-compute)
3. Two-stage gives best of both worlds
4. Tune candidate count for your latency/quality needs
    """)


if __name__ == "__main__":
    main()
