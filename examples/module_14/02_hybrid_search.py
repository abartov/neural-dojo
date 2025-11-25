#!/usr/bin/env python3
"""
Module 14 Example 2: Hybrid Search (BM25 + Semantic)

Demonstrates how combining lexical (BM25) and semantic search
provides better results than either method alone.

Key Insight:
- Semantic search understands meaning but misses exact matches
- BM25 finds exact matches but misses semantic similarity
- Hybrid combines the best of both!
"""

import os
import json
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import numpy as np

# Try to import dependencies
try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    print("⚠️  rank_bm25 not installed. Run: pip install rank-bm25")

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("⚠️  sentence-transformers not installed.")


@dataclass
class HybridResult:
    """A hybrid search result with component scores."""
    document: str
    doc_id: int
    bm25_score: float
    semantic_score: float
    hybrid_score: float
    bm25_rank: int
    semantic_rank: int


class HybridSearch:
    """
    Hybrid Search: BM25 + Semantic

    Combines:
    1. BM25 (lexical): Term frequency-based matching
    2. Semantic: Embedding similarity

    Methods:
    - Weighted combination: alpha * semantic + (1-alpha) * bm25
    - Reciprocal Rank Fusion (RRF): Combines rankings, not scores
    """

    def __init__(self, documents: List[str], model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize hybrid search.

        Args:
            documents: List of documents to search
            model_name: Sentence transformer model
        """
        self.documents = documents
        self.doc_ids = list(range(len(documents)))

        # Initialize BM25
        if HAS_BM25:
            tokenized_docs = [self._tokenize(doc) for doc in documents]
            self.bm25 = BM25Okapi(tokenized_docs)
            print("✅ BM25 index created")
        else:
            self.bm25 = None

        # Initialize semantic search
        if HAS_SENTENCE_TRANSFORMERS:
            self.model = SentenceTransformer(model_name)
            self.doc_embeddings = self.model.encode(documents, show_progress_bar=True)
            print(f"✅ Semantic index created with {model_name}")
        else:
            self.model = None
            self.doc_embeddings = None

        print(f"✅ Indexed {len(documents)} documents")

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        # Lowercase and split on non-alphanumeric
        import re
        tokens = re.findall(r'\w+', text.lower())
        return tokens

    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        """Min-max normalize scores to [0, 1]."""
        min_s, max_s = scores.min(), scores.max()
        if max_s == min_s:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)

    def bm25_search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """
        BM25 lexical search.

        Returns list of (doc_id, score) tuples.
        """
        if not self.bm25:
            return [(i, 0.0) for i in range(min(k, len(self.documents)))]

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k
        top_indices = np.argsort(scores)[::-1][:k]
        return [(int(i), float(scores[i])) for i in top_indices]

    def semantic_search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """
        Semantic embedding search.

        Returns list of (doc_id, score) tuples.
        """
        if self.model is None or self.doc_embeddings is None:
            return [(i, 0.0) for i in range(min(k, len(self.documents)))]

        query_embedding = self.model.encode([query])[0]

        # Cosine similarity
        similarities = np.dot(self.doc_embeddings, query_embedding) / (
            np.linalg.norm(self.doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:k]
        return [(int(i), float(similarities[i])) for i in top_indices]

    def hybrid_weighted(self, query: str, k: int = 5, alpha: float = 0.5) -> List[HybridResult]:
        """
        Hybrid search with weighted score combination.

        Args:
            query: Search query
            k: Number of results
            alpha: Weight for semantic (1-alpha for BM25)
                   alpha=1.0: Pure semantic
                   alpha=0.0: Pure BM25
                   alpha=0.5: Balanced

        Returns:
            List of hybrid results with all scores
        """
        # Get all scores
        bm25_results = self.bm25_search(query, k=len(self.documents))
        semantic_results = self.semantic_search(query, k=len(self.documents))

        # Create score arrays
        bm25_scores = np.zeros(len(self.documents))
        semantic_scores = np.zeros(len(self.documents))

        for doc_id, score in bm25_results:
            bm25_scores[doc_id] = score
        for doc_id, score in semantic_results:
            semantic_scores[doc_id] = score

        # Normalize scores
        bm25_norm = self._normalize(bm25_scores)
        semantic_norm = self._normalize(semantic_scores)

        # Compute hybrid scores
        hybrid_scores = alpha * semantic_norm + (1 - alpha) * bm25_norm

        # Get rankings for each method
        bm25_ranking = np.argsort(bm25_scores)[::-1]
        semantic_ranking = np.argsort(semantic_scores)[::-1]

        bm25_rank_map = {doc_id: rank for rank, doc_id in enumerate(bm25_ranking)}
        semantic_rank_map = {doc_id: rank for rank, doc_id in enumerate(semantic_ranking)}

        # Get top-k hybrid
        top_indices = np.argsort(hybrid_scores)[::-1][:k]

        return [
            HybridResult(
                document=self.documents[i],
                doc_id=i,
                bm25_score=float(bm25_scores[i]),
                semantic_score=float(semantic_scores[i]),
                hybrid_score=float(hybrid_scores[i]),
                bm25_rank=bm25_rank_map[i],
                semantic_rank=semantic_rank_map[i]
            )
            for i in top_indices
        ]

    def hybrid_rrf(self, query: str, k: int = 5, rrf_k: int = 60) -> List[HybridResult]:
        """
        Hybrid search with Reciprocal Rank Fusion (RRF).

        RRF combines rankings rather than scores:
        RRF_score = sum(1 / (k + rank)) for each ranking

        Args:
            query: Search query
            k: Number of results
            rrf_k: RRF constant (default 60)

        Returns:
            List of hybrid results
        """
        # Get rankings
        bm25_results = self.bm25_search(query, k=len(self.documents))
        semantic_results = self.semantic_search(query, k=len(self.documents))

        # Build score arrays for reference
        bm25_scores = {doc_id: score for doc_id, score in bm25_results}
        semantic_scores = {doc_id: score for doc_id, score in semantic_results}

        # Compute RRF scores
        rrf_scores = {}
        for rank, (doc_id, _) in enumerate(bm25_results):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (rrf_k + rank + 1)

        for rank, (doc_id, _) in enumerate(semantic_results):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (rrf_k + rank + 1)

        # Sort by RRF score
        sorted_docs = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        # Get rankings
        bm25_rank_map = {doc_id: rank for rank, (doc_id, _) in enumerate(bm25_results)}
        semantic_rank_map = {doc_id: rank for rank, (doc_id, _) in enumerate(semantic_results)}

        return [
            HybridResult(
                document=self.documents[doc_id],
                doc_id=doc_id,
                bm25_score=bm25_scores.get(doc_id, 0),
                semantic_score=semantic_scores.get(doc_id, 0),
                hybrid_score=rrf_scores[doc_id],
                bm25_rank=bm25_rank_map.get(doc_id, len(self.documents)),
                semantic_rank=semantic_rank_map.get(doc_id, len(self.documents))
            )
            for doc_id in sorted_docs[:k]
        ]

    def compare_methods(self, query: str, k: int = 5) -> Dict:
        """
        Compare all search methods.

        Args:
            query: Search query
            k: Number of results

        Returns:
            Comparison dictionary
        """
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")

        # BM25 only
        print("\n📊 BM25 (Lexical) Results:")
        bm25_results = self.bm25_search(query, k)
        for rank, (doc_id, score) in enumerate(bm25_results, 1):
            print(f"  {rank}. [Score: {score:.4f}] {self.documents[doc_id][:80]}...")

        # Semantic only
        print("\n📊 Semantic Results:")
        semantic_results = self.semantic_search(query, k)
        for rank, (doc_id, score) in enumerate(semantic_results, 1):
            print(f"  {rank}. [Score: {score:.4f}] {self.documents[doc_id][:80]}...")

        # Hybrid weighted
        print("\n📊 Hybrid (Weighted, alpha=0.5) Results:")
        hybrid_results = self.hybrid_weighted(query, k, alpha=0.5)
        for rank, result in enumerate(hybrid_results, 1):
            print(f"  {rank}. [Hybrid: {result.hybrid_score:.4f}] "
                  f"(BM25 rank: {result.bm25_rank+1}, Semantic rank: {result.semantic_rank+1})")
            print(f"     {result.document[:80]}...")

        # Hybrid RRF
        print("\n📊 Hybrid (RRF) Results:")
        rrf_results = self.hybrid_rrf(query, k)
        for rank, result in enumerate(rrf_results, 1):
            print(f"  {rank}. [RRF: {result.hybrid_score:.4f}] "
                  f"(BM25 rank: {result.bm25_rank+1}, Semantic rank: {result.semantic_rank+1})")
            print(f"     {result.document[:80]}...")

        return {
            "query": query,
            "bm25": bm25_results,
            "semantic": semantic_results,
            "hybrid_weighted": [(r.doc_id, r.hybrid_score) for r in hybrid_results],
            "hybrid_rrf": [(r.doc_id, r.hybrid_score) for r in rrf_results]
        }


# Sample documents with mix of technical terms and concepts
SAMPLE_DOCUMENTS = [
    "Error code 0x80070005 indicates an access denied error in Windows. "
    "This typically occurs when a process lacks the necessary permissions to access a resource.",

    "Permission denied errors in operating systems occur when the current user or process "
    "doesn't have the required access rights to perform an operation on a file or resource.",

    "The HTTP 403 Forbidden status code indicates the server understood the request "
    "but refuses to authorize it. This is different from 401 Unauthorized.",

    "Python's PermissionError is raised when trying to run an operation without "
    "adequate access rights. Common causes include file system permissions and elevation requirements.",

    "Access control mechanisms in modern systems include role-based access control (RBAC), "
    "discretionary access control (DAC), and mandatory access control (MAC).",

    "The sudo command in Unix-like systems allows users to run programs with elevated privileges. "
    "Always use sudo cautiously to avoid security risks.",

    "Machine learning model performance depends on data quality, feature engineering, "
    "hyperparameter tuning, and proper validation strategies.",

    "Neural networks learn through backpropagation, adjusting weights based on "
    "the gradient of the loss function with respect to each parameter.",

    "The transformer architecture uses self-attention mechanisms to process "
    "sequential data without the limitations of recurrent neural networks.",

    "Large language models like GPT and Claude are trained on massive text corpora "
    "and can perform a wide range of natural language tasks.",

    "API rate limiting with Redis can be implemented using the token bucket algorithm. "
    "INCR and EXPIRE commands provide atomic operations for rate tracking.",

    "Redis cache eviction policies include LRU (least recently used), LFU (least frequently used), "
    "and TTL-based expiration. Choose based on your access patterns.",

    "Elasticsearch provides full-text search capabilities with BM25 scoring by default. "
    "It supports fuzzy matching, phrase queries, and complex aggregations.",

    "Vector databases like Pinecone, Qdrant, and Weaviate are optimized for "
    "storing and querying high-dimensional embeddings for semantic search."
]


def demo_exact_match():
    """Show how BM25 excels at exact matches."""
    print("\n" + "="*70)
    print("DEMO 1: Exact Match Query (BM25 Advantage)")
    print("="*70)
    print("""
When queries contain specific codes, IDs, or terms,
BM25 (lexical) search often outperforms semantic search.
    """)

    searcher = HybridSearch(SAMPLE_DOCUMENTS)

    # Query with exact code
    query = "error code 0x80070005"
    searcher.compare_methods(query, k=3)


def demo_semantic_query():
    """Show how semantic search handles natural language."""
    print("\n" + "="*70)
    print("DEMO 2: Natural Language Query (Semantic Advantage)")
    print("="*70)
    print("""
When queries describe concepts without exact term matches,
semantic search finds relevant documents by meaning.
    """)

    searcher = HybridSearch(SAMPLE_DOCUMENTS)

    # Conceptual query
    query = "how do neural networks learn from data?"
    searcher.compare_methods(query, k=3)


def demo_hybrid_benefits():
    """Show how hybrid combines best of both."""
    print("\n" + "="*70)
    print("DEMO 3: Mixed Query (Hybrid Advantage)")
    print("="*70)
    print("""
Many real queries mix specific terms with natural language.
Hybrid search handles both aspects effectively.
    """)

    searcher = HybridSearch(SAMPLE_DOCUMENTS)

    # Mixed query
    query = "how to implement rate limiting with Redis"
    searcher.compare_methods(query, k=3)


def demo_alpha_tuning():
    """Demonstrate effect of alpha parameter."""
    print("\n" + "="*70)
    print("DEMO 4: Alpha Tuning Effect")
    print("="*70)
    print("""
The alpha parameter controls the balance:
- alpha = 1.0: Pure semantic search
- alpha = 0.5: Balanced (default)
- alpha = 0.0: Pure BM25 search

Tune based on your query distribution!
    """)

    searcher = HybridSearch(SAMPLE_DOCUMENTS)

    query = "permission denied access error"

    for alpha in [0.0, 0.3, 0.5, 0.7, 1.0]:
        print(f"\n📊 Alpha = {alpha}")
        results = searcher.hybrid_weighted(query, k=3, alpha=alpha)
        for rank, result in enumerate(results, 1):
            print(f"  {rank}. {result.document[:60]}...")


def main():
    """Run all demos."""
    print("="*70)
    print("Hybrid Search: BM25 + Semantic")
    print("="*70)
    print("""
Hybrid search combines lexical (BM25) and semantic search:

BM25 (Lexical):
  ✅ Great for exact term matching (codes, IDs, names)
  ❌ Misses semantic similarity

Semantic:
  ✅ Understands meaning and synonyms
  ❌ Can miss exact term matches

Hybrid:
  ✅ Best of both worlds!
  ✅ Two combination methods: Weighted and RRF
    """)

    if not HAS_BM25:
        print("\n⚠️  Install rank-bm25: pip install rank-bm25")
        return

    if not HAS_SENTENCE_TRANSFORMERS:
        print("\n⚠️  Install sentence-transformers: pip install sentence-transformers")
        return

    # Run demos
    demo_exact_match()
    demo_semantic_query()
    demo_hybrid_benefits()
    demo_alpha_tuning()

    print("\n" + "="*70)
    print("✅ Hybrid Search Demo Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
