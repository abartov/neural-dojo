"""
Module 10 Example 2: Production Semantic Search

This example demonstrates building production-grade semantic search:
1. Naive brute-force search (baseline)
2. Fast ANN search with FAISS
3. Performance benchmarking
4. Scaling to large datasets
5. Hybrid search (semantic + metadata)

Prerequisites:
- sentence-transformers
- faiss-cpu (or faiss-gpu)
- numpy

Cost: FREE (uses local models)
"""

import time
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict

# Try to import required libraries
try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"✅ Loaded model: all-MiniLM-L6-v2")
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠️  Install: pip install sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
    print(f"✅ FAISS available")
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  Install: pip install faiss-cpu")


@dataclass
class Document:
    """Document with metadata."""
    id: int
    text: str
    category: str
    date: str
    popularity: int


@dataclass
class SearchResult:
    """Search result with score."""
    doc_id: int
    score: float
    text: str
    category: str


def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# =============================================================================
# Sample Dataset
# =============================================================================

def create_sample_dataset(size: int = 1000) -> List[Document]:
    """Create a sample dataset for testing."""
    categories = ["Technology", "Food", "Sports", "Science", "Travel"]

    templates = {
        "Technology": [
            "Introduction to {} programming",
            "{} web development tutorial",
            "Building applications with {}",
            "{} for beginners guide",
            "Advanced {} techniques"
        ],
        "Food": [
            "How to cook perfect {}",
            "{} recipe collection",
            "Traditional {} cooking methods",
            "{} preparation tips",
            "Healthy {} recipes"
        ],
        "Sports": [
            "{} training techniques",
            "Professional {} strategies",
            "{} competition rules",
            "History of {} sports",
            "{} athlete nutrition"
        ],
        "Science": [
            "{} experimental methods",
            "Understanding {} principles",
            "{} research findings",
            "Applications of {} in industry",
            "{} theory explained"
        ],
        "Travel": [
            "Visiting {} travel guide",
            "{} tourist attractions",
            "Best time to visit {}",
            "{} cultural experiences",
            "Budget travel to {}"
        ]
    }

    topics = {
        "Technology": ["Python", "JavaScript", "React", "Docker", "Kubernetes"],
        "Food": ["pasta", "pizza", "sushi", "curry", "tacos"],
        "Sports": ["football", "basketball", "tennis", "swimming", "cycling"],
        "Science": ["physics", "chemistry", "biology", "astronomy", "geology"],
        "Travel": ["Paris", "Tokyo", "New York", "London", "Sydney"]
    }

    documents = []
    for i in range(size):
        category = categories[i % len(categories)]
        template = templates[category][i % len(templates[category])]
        topic = topics[category][i % len(topics[category])]

        doc = Document(
            id=i,
            text=template.format(topic),
            category=category,
            date=f"2024-{(i % 12) + 1:02d}-01",
            popularity=np.random.randint(0, 1000)
        )
        documents.append(doc)

    return documents


# =============================================================================
# Method 1: Naive Brute-Force Search
# =============================================================================

class NaiveSearch:
    """Brute-force search - compare query to ALL documents."""

    def __init__(self, documents: List[Document]):
        """Initialize with documents."""
        if not SBERT_AVAILABLE:
            raise RuntimeError("sentence-transformers required")

        self.documents = {doc.id: doc for doc in documents}

        print(f"\n📊 Indexing {len(documents)} documents (Naive)...")
        start = time.time()

        # Precompute all document embeddings
        self.embeddings = {}
        for doc in documents:
            self.embeddings[doc.id] = model.encode(doc.text)

        elapsed = time.time() - start
        print(f"✅ Indexed in {elapsed:.2f}s")

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using brute force."""
        query_emb = model.encode(query)

        # Compare to ALL documents
        scores = []
        for doc_id, doc_emb in self.embeddings.items():
            score = cosine_similarity(query_emb, doc_emb)
            scores.append((doc_id, score))

        # Sort and return top-k
        top_results = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

        return [
            SearchResult(
                doc_id=doc_id,
                score=score,
                text=self.documents[doc_id].text,
                category=self.documents[doc_id].category
            )
            for doc_id, score in top_results
        ]


# =============================================================================
# Method 2: FAISS ANN Search
# =============================================================================

class FAISSSearch:
    """Fast Approximate Nearest Neighbor search with FAISS."""

    def __init__(self, documents: List[Document]):
        """Initialize with documents."""
        if not SBERT_AVAILABLE or not FAISS_AVAILABLE:
            raise RuntimeError("sentence-transformers and faiss required")

        self.documents = {doc.id: doc for doc in documents}

        print(f"\n📊 Indexing {len(documents)} documents (FAISS)...")
        start = time.time()

        # Batch encode all documents
        texts = [doc.text for doc in documents]
        embeddings = model.encode(texts, show_progress_bar=True)

        # Convert to float32 (FAISS requirement)
        self.embeddings_matrix = embeddings.astype('float32')
        self.dimension = self.embeddings_matrix.shape[1]

        # Build FAISS index (HNSW)
        self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 neighbors
        self.index.add(self.embeddings_matrix)

        # Store document IDs in order
        self.doc_ids = [doc.id for doc in documents]

        elapsed = time.time() - start
        print(f"✅ Indexed in {elapsed:.2f}s")
        print(f"   Dimension: {self.dimension}")
        print(f"   Algorithm: HNSW")

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using FAISS ANN."""
        # Encode query
        query_emb = model.encode(query).astype('float32').reshape(1, -1)

        # FAISS search
        distances, indices = self.index.search(query_emb, top_k)

        # Convert to results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            doc_id = self.doc_ids[idx]
            # Convert L2 distance to similarity (approximate)
            score = 1.0 / (1.0 + dist)

            results.append(SearchResult(
                doc_id=doc_id,
                score=score,
                text=self.documents[doc_id].text,
                category=self.documents[doc_id].category
            ))

        return results


# =============================================================================
# Method 3: Hybrid Search (Semantic + Metadata)
# =============================================================================

class HybridSearch:
    """Combine semantic search with metadata filtering."""

    def __init__(self, documents: List[Document]):
        """Initialize with documents."""
        self.base_search = FAISSSearch(documents) if FAISS_AVAILABLE else NaiveSearch(documents)
        self.documents = {doc.id: doc for doc in documents}

        # Build metadata index
        self.category_index = defaultdict(list)
        for doc in documents:
            self.category_index[doc.category].append(doc.id)

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        boost_popularity: float = 0.2
    ) -> List[SearchResult]:
        """
        Hybrid search with metadata filtering and reranking.

        Args:
            query: Search query
            top_k: Number of results
            category_filter: Filter by category
            boost_popularity: Weight for popularity boost (0-1)
        """
        # Get semantic results (fetch more for reranking)
        semantic_results = self.base_search.search(query, top_k=top_k * 3)

        # Filter by category if specified
        if category_filter:
            semantic_results = [
                r for r in semantic_results
                if self.documents[r.doc_id].category == category_filter
            ]

        # Rerank by combining semantic score + popularity
        if boost_popularity > 0:
            max_pop = max(doc.popularity for doc in self.documents.values())

            reranked = []
            for result in semantic_results:
                doc = self.documents[result.doc_id]
                popularity_score = doc.popularity / max_pop if max_pop > 0 else 0

                # Combine scores
                final_score = (
                    (1 - boost_popularity) * result.score +
                    boost_popularity * popularity_score
                )

                reranked.append(SearchResult(
                    doc_id=result.doc_id,
                    score=final_score,
                    text=result.text,
                    category=result.category
                ))

            semantic_results = sorted(reranked, key=lambda x: x.score, reverse=True)

        return semantic_results[:top_k]


# =============================================================================
# Benchmarking
# =============================================================================

def benchmark_search_methods(documents: List[Document], num_queries: int = 10):
    """Compare performance of different search methods."""
    print("\n" + "="*80)
    print("BENCHMARK: Search Performance Comparison")
    print("="*80)

    test_queries = [
        "Python programming tutorial",
        "How to cook pasta",
        "Football training techniques",
        "Physics experiments",
        "Travel to Paris",
        "Web development with JavaScript",
        "Healthy recipes",
        "Basketball competition",
        "Chemistry research",
        "Tokyo travel guide"
    ][:num_queries]

    methods = {}

    # Naive search
    print("\n--- Method 1: Naive Brute-Force ---")
    naive = NaiveSearch(documents)
    methods["Naive"] = naive

    # FAISS search
    if FAISS_AVAILABLE:
        print("\n--- Method 2: FAISS (HNSW) ---")
        faiss_search = FAISSSearch(documents)
        methods["FAISS"] = faiss_search

    # Benchmark each method
    print("\n" + "="*80)
    print("QUERY LATENCY COMPARISON")
    print("="*80)

    results = {}
    for method_name, search_engine in methods.items():
        latencies = []

        for query in test_queries:
            start = time.time()
            search_engine.search(query, top_k=5)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            latencies.append(elapsed)

        avg_latency = np.mean(latencies)
        std_latency = np.std(latencies)
        results[method_name] = (avg_latency, std_latency)

        print(f"\n{method_name}:")
        print(f"  Average latency: {avg_latency:.2f} ms")
        print(f"  Std deviation: {std_latency:.2f} ms")
        print(f"  Min: {min(latencies):.2f} ms")
        print(f"  Max: {max(latencies):.2f} ms")

    if FAISS_AVAILABLE:
        naive_avg = results["Naive"][0]
        faiss_avg = results["FAISS"][0]
        speedup = naive_avg / faiss_avg

        print(f"\n{'='*80}")
        print(f"⚡ FAISS Speedup: {speedup:.1f}x faster than naive search!")
        print(f"{'='*80}")


# =============================================================================
# Demonstrations
# =============================================================================

def demo_basic_search():
    """Demonstrate basic semantic search."""
    print("\n" + "="*80)
    print("DEMO: Basic Semantic Search")
    print("="*80)

    if not SBERT_AVAILABLE:
        print("⚠️  sentence-transformers required")
        return

    # Create small dataset
    documents = create_sample_dataset(100)

    # Build search index
    if FAISS_AVAILABLE:
        search = FAISSSearch(documents)
    else:
        search = NaiveSearch(documents)

    # Test queries
    queries = [
        "Python programming guide",
        "Cooking Italian food",
        "Sports training"
    ]

    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 80)

        results = search.search(query, top_k=3)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.score:.3f}")
            print(f"   {result.text}")
            print(f"   Category: {result.category}")


def demo_hybrid_search():
    """Demonstrate hybrid search with filtering."""
    print("\n" + "="*80)
    print("DEMO: Hybrid Search (Semantic + Metadata)")
    print("="*80)

    if not SBERT_AVAILABLE:
        print("⚠️  sentence-transformers required")
        return

    documents = create_sample_dataset(200)
    search = HybridSearch(documents)

    query = "programming tutorial"

    # Search 1: No filter
    print(f"\n🔍 Query: '{query}' (no filter)")
    print("-" * 80)
    results = search.search(query, top_k=3)

    for i, result in enumerate(results, 1):
        print(f"{i}. {result.text} [{result.category}]")

    # Search 2: With category filter
    print(f"\n🔍 Query: '{query}' (filter: Technology)")
    print("-" * 80)
    results = search.search(query, top_k=3, category_filter="Technology")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result.text} [{result.category}]")

    # Search 3: With popularity boost
    print(f"\n🔍 Query: '{query}' (boost popular docs)")
    print("-" * 80)
    results = search.search(query, top_k=3, boost_popularity=0.3)

    for i, result in enumerate(results, 1):
        doc = search.documents[result.doc_id]
        print(f"{i}. {result.text} [pop: {doc.popularity}]")


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*80)
    print("MODULE 10: PRODUCTION SEMANTIC SEARCH")
    print("="*80)
    print("\nBuilding fast, scalable semantic search!")

    if not SBERT_AVAILABLE:
        print("\n⚠️  sentence-transformers required")
        print("    Install: pip install sentence-transformers")
        return

    # Run demos
    demo_basic_search()
    demo_hybrid_search()

    # Benchmark
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARKING")
    print("="*80)

    dataset_sizes = [100, 500, 1000]

    for size in dataset_sizes:
        print(f"\n{'='*80}")
        print(f"Dataset size: {size} documents")
        print(f"{'='*80}")

        documents = create_sample_dataset(size)
        benchmark_search_methods(documents, num_queries=5)

    print("\n" + "="*80)
    print("✅ All demonstrations complete!")
    print("="*80)
    print("\nKey takeaways:")
    print("  1. Naive search: O(N) - slow for large datasets")
    print("  2. FAISS ANN: O(log N) - 10-1000x faster!")
    print("  3. HNSW algorithm: Best for most use cases")
    print("  4. Hybrid search: Combine semantic + metadata")
    print("  5. Production ready: FAISS handles millions of docs")
    print("\n🎯 Ready for production semantic search!")
    print("="*80)


if __name__ == "__main__":
    main()
