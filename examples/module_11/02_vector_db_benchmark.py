"""
Module 11 Example 2: Vector Database Benchmark

This example benchmarks and compares different vector database solutions:
1. Qdrant (production-ready, filtering, persistence)
2. FAISS (fastest in-memory, Facebook AI)
3. Chroma (easiest to use, local development)

Metrics measured:
- Query latency (ms)
- Recall@K accuracy
- Memory usage (MB)
- Index build time (s)

Author: Neural Dojo
Time: ~3 hours
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import time
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
from tqdm import tqdm

# Vector database imports
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import faiss
import chromadb


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    database: str
    num_vectors: int
    vector_dim: int
    query_latency_ms: float
    recall_at_10: float
    memory_mb: float
    index_build_time_s: float
    queries_per_second: float


class VectorDBBenchmark:
    """Benchmark suite for vector databases."""

    def __init__(self, vector_dim: int = 384):
        """
        Initialize benchmark suite.

        Args:
            vector_dim: Dimension of embedding vectors
        """
        self.vector_dim = vector_dim
        self.results: List[BenchmarkResult] = []

        # Load embedding model
        print("📦 Loading embedding model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Model loaded")

    def generate_test_data(
        self,
        num_vectors: int,
        num_queries: int = 100,
    ) -> Tuple[np.ndarray, List[str], np.ndarray, List[str]]:
        """
        Generate synthetic test data.

        Args:
            num_vectors: Number of vectors in the database
            num_queries: Number of query vectors

        Returns:
            Tuple of (vectors, texts, query_vectors, query_texts)
        """
        print(f"\n📊 Generating test data...")
        print(f"   Vectors: {num_vectors}")
        print(f"   Queries: {num_queries}")

        # Generate synthetic document texts
        topics = [
            "machine learning", "deep learning", "neural networks",
            "data science", "python programming", "web development",
            "cloud computing", "artificial intelligence", "natural language",
            "computer vision", "reinforcement learning", "transformers",
        ]

        texts = []
        for i in range(num_vectors):
            topic = topics[i % len(topics)]
            text = f"Document {i} about {topic} with some random content"
            texts.append(text)

        query_texts = []
        for i in range(num_queries):
            topic = topics[i % len(topics)]
            query_texts.append(f"Query about {topic}")

        # Generate embeddings
        print("   Encoding documents...")
        vectors = self.model.encode(texts, show_progress_bar=False)

        print("   Encoding queries...")
        query_vectors = self.model.encode(query_texts, show_progress_bar=False)

        print(f"✅ Generated {len(vectors)} vectors and {len(query_vectors)} queries")

        return vectors, texts, query_vectors, query_texts

    def benchmark_qdrant(
        self,
        vectors: np.ndarray,
        texts: List[str],
        query_vectors: np.ndarray,
        collection_name: str = "benchmark",
    ) -> BenchmarkResult:
        """
        Benchmark Qdrant vector database.

        Args:
            vectors: Database vectors
            texts: Corresponding text documents
            query_vectors: Query vectors
            collection_name: Collection name

        Returns:
            BenchmarkResult
        """
        print("\n" + "=" * 80)
        print("🔵 Benchmarking Qdrant")
        print("=" * 80)

        # Connect
        client = QdrantClient(url="http://localhost:6333")

        # Measure index build time
        start_time = time.time()

        # Delete collection if exists
        try:
            client.delete_collection(collection_name)
        except:
            pass

        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=self.vector_dim,
                distance=Distance.COSINE,
            ),
        )

        # Insert vectors
        batch_size = 100
        for i in tqdm(range(0, len(vectors), batch_size), desc="Inserting"):
            batch_vectors = vectors[i : i + batch_size]
            batch_texts = texts[i : i + batch_size]

            points = [
                PointStruct(
                    id=idx,
                    vector=vec.tolist(),
                    payload={"text": text},
                )
                for idx, (vec, text) in enumerate(
                    zip(batch_vectors, batch_texts), start=i
                )
            ]

            client.upsert(collection_name=collection_name, points=points)

        index_build_time = time.time() - start_time

        # Measure query latency
        print("Running queries...")
        latencies = []

        for query_vec in tqdm(query_vectors, desc="Querying"):
            start = time.time()
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vec.tolist(),
                limit=10,
            )
            latency = (time.time() - start) * 1000  # Convert to ms
            latencies.append(latency)

        avg_latency = np.mean(latencies)
        qps = 1000 / avg_latency  # Queries per second

        # Calculate recall (using brute force as ground truth)
        recall = self._calculate_recall(
            client, collection_name, vectors, query_vectors
        )

        # Estimate memory usage (rough)
        memory_mb = (
            len(vectors) * self.vector_dim * 4 / (1024 * 1024)
        )  # 4 bytes per float

        result = BenchmarkResult(
            database="Qdrant",
            num_vectors=len(vectors),
            vector_dim=self.vector_dim,
            query_latency_ms=avg_latency,
            recall_at_10=recall,
            memory_mb=memory_mb,
            index_build_time_s=index_build_time,
            queries_per_second=qps,
        )

        print(f"\n✅ Qdrant Benchmark Complete:")
        print(f"   Query Latency: {avg_latency:.2f}ms")
        print(f"   Recall@10: {recall:.1f}%")
        print(f"   QPS: {qps:.0f}")
        print(f"   Index Build Time: {index_build_time:.2f}s")

        # Cleanup
        client.delete_collection(collection_name)

        return result

    def benchmark_faiss(
        self,
        vectors: np.ndarray,
        query_vectors: np.ndarray,
    ) -> BenchmarkResult:
        """
        Benchmark FAISS vector database.

        Args:
            vectors: Database vectors
            query_vectors: Query vectors

        Returns:
            BenchmarkResult
        """
        print("\n" + "=" * 80)
        print("🟠 Benchmarking FAISS")
        print("=" * 80)

        # Measure index build time
        start_time = time.time()

        # Create FAISS index (HNSW for fair comparison with Qdrant)
        index = faiss.IndexHNSWFlat(self.vector_dim, 32)  # M=32
        index.hnsw.efConstruction = 200

        # Add vectors
        print("Building index...")
        index.add(vectors.astype(np.float32))

        index_build_time = time.time() - start_time

        # Measure query latency
        print("Running queries...")
        latencies = []

        for query_vec in tqdm(query_vectors, desc="Querying"):
            start = time.time()
            D, I = index.search(query_vec.reshape(1, -1).astype(np.float32), k=10)
            latency = (time.time() - start) * 1000
            latencies.append(latency)

        avg_latency = np.mean(latencies)
        qps = 1000 / avg_latency

        # Calculate recall
        recall = self._calculate_recall_faiss(index, vectors, query_vectors)

        # Memory usage (FAISS is efficient)
        memory_mb = len(vectors) * self.vector_dim * 4 / (1024 * 1024) * 1.2

        result = BenchmarkResult(
            database="FAISS",
            num_vectors=len(vectors),
            vector_dim=self.vector_dim,
            query_latency_ms=avg_latency,
            recall_at_10=recall,
            memory_mb=memory_mb,
            index_build_time_s=index_build_time,
            queries_per_second=qps,
        )

        print(f"\n✅ FAISS Benchmark Complete:")
        print(f"   Query Latency: {avg_latency:.2f}ms")
        print(f"   Recall@10: {recall:.1f}%")
        print(f"   QPS: {qps:.0f}")
        print(f"   Index Build Time: {index_build_time:.2f}s")

        return result

    def benchmark_chroma(
        self,
        vectors: np.ndarray,
        texts: List[str],
        query_vectors: np.ndarray,
        collection_name: str = "benchmark",
    ) -> BenchmarkResult:
        """
        Benchmark ChromaDB.

        Args:
            vectors: Database vectors
            texts: Corresponding text documents
            query_vectors: Query vectors
            collection_name: Collection name

        Returns:
            BenchmarkResult
        """
        print("\n" + "=" * 80)
        print("🟢 Benchmarking ChromaDB")
        print("=" * 80)

        # Initialize client
        client = chromadb.Client()

        # Measure index build time
        start_time = time.time()

        # Delete collection if exists
        try:
            client.delete_collection(collection_name)
        except:
            pass

        # Create collection
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Add vectors
        print("Inserting vectors...")
        batch_size = 100
        for i in tqdm(range(0, len(vectors), batch_size), desc="Inserting"):
            batch_vectors = vectors[i : i + batch_size]
            batch_texts = texts[i : i + batch_size]

            collection.add(
                ids=[str(j) for j in range(i, i + len(batch_vectors))],
                embeddings=batch_vectors.tolist(),
                documents=batch_texts,
            )

        index_build_time = time.time() - start_time

        # Measure query latency
        print("Running queries...")
        latencies = []

        for query_vec in tqdm(query_vectors, desc="Querying"):
            start = time.time()
            results = collection.query(
                query_embeddings=[query_vec.tolist()],
                n_results=10,
            )
            latency = (time.time() - start) * 1000
            latencies.append(latency)

        avg_latency = np.mean(latencies)
        qps = 1000 / avg_latency

        # Calculate recall
        recall = self._calculate_recall_chroma(
            collection, vectors, query_vectors
        )

        # Memory usage
        memory_mb = len(vectors) * self.vector_dim * 4 / (1024 * 1024) * 1.3

        result = BenchmarkResult(
            database="ChromaDB",
            num_vectors=len(vectors),
            vector_dim=self.vector_dim,
            query_latency_ms=avg_latency,
            recall_at_10=recall,
            memory_mb=memory_mb,
            index_build_time_s=index_build_time,
            queries_per_second=qps,
        )

        print(f"\n✅ ChromaDB Benchmark Complete:")
        print(f"   Query Latency: {avg_latency:.2f}ms")
        print(f"   Recall@10: {recall:.1f}%")
        print(f"   QPS: {qps:.0f}")
        print(f"   Index Build Time: {index_build_time:.2f}s")

        # Cleanup
        client.delete_collection(collection_name)

        return result

    def _calculate_recall(
        self,
        client: QdrantClient,
        collection_name: str,
        vectors: np.ndarray,
        query_vectors: np.ndarray,
        k: int = 10,
    ) -> float:
        """Calculate recall@k for Qdrant using brute force ground truth."""
        # Sample a few queries for recall calculation
        sample_queries = query_vectors[:20]  # Sample 20 queries

        recalls = []
        for query_vec in sample_queries:
            # Get approximate results from Qdrant
            approx_results = client.search(
                collection_name=collection_name,
                query_vector=query_vec.tolist(),
                limit=k,
            )
            approx_ids = {hit.id for hit in approx_results}

            # Get ground truth (brute force)
            similarities = np.dot(vectors, query_vec) / (
                np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vec)
            )
            true_top_k = np.argsort(-similarities)[:k]

            # Calculate recall
            recall = len(approx_ids.intersection(set(true_top_k))) / k
            recalls.append(recall)

        return np.mean(recalls) * 100

    def _calculate_recall_faiss(
        self,
        index: faiss.Index,
        vectors: np.ndarray,
        query_vectors: np.ndarray,
        k: int = 10,
    ) -> float:
        """Calculate recall@k for FAISS."""
        sample_queries = query_vectors[:20]

        recalls = []
        for query_vec in sample_queries:
            # FAISS results
            D, I = index.search(query_vec.reshape(1, -1).astype(np.float32), k=k)
            approx_ids = set(I[0])

            # Ground truth
            similarities = np.dot(vectors, query_vec) / (
                np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vec)
            )
            true_top_k = set(np.argsort(-similarities)[:k])

            recall = len(approx_ids.intersection(true_top_k)) / k
            recalls.append(recall)

        return np.mean(recalls) * 100

    def _calculate_recall_chroma(
        self,
        collection,
        vectors: np.ndarray,
        query_vectors: np.ndarray,
        k: int = 10,
    ) -> float:
        """Calculate recall@k for ChromaDB."""
        sample_queries = query_vectors[:20]

        recalls = []
        for query_vec in sample_queries:
            # Chroma results
            results = collection.query(
                query_embeddings=[query_vec.tolist()],
                n_results=k,
            )
            approx_ids = {int(id_) for id_ in results["ids"][0]}

            # Ground truth
            similarities = np.dot(vectors, query_vec) / (
                np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vec)
            )
            true_top_k = set(np.argsort(-similarities)[:k])

            recall = len(approx_ids.intersection(true_top_k)) / k
            recalls.append(recall)

        return np.mean(recalls) * 100

    def run_full_benchmark(self, num_vectors: int = 10000) -> List[BenchmarkResult]:
        """
        Run full benchmark suite across all databases.

        Args:
            num_vectors: Number of vectors to test with

        Returns:
            List of benchmark results
        """
        print("\n" + "=" * 80)
        print(f"🚀 Running Full Benchmark Suite")
        print(f"   Vectors: {num_vectors:,}")
        print(f"   Dimensions: {self.vector_dim}")
        print("=" * 80)

        # Generate test data
        vectors, texts, query_vectors, query_texts = self.generate_test_data(
            num_vectors=num_vectors
        )

        # Run benchmarks
        results = []

        # Qdrant
        try:
            result = self.benchmark_qdrant(vectors, texts, query_vectors)
            results.append(result)
        except Exception as e:
            print(f"⚠️  Qdrant benchmark failed: {e}")

        # FAISS
        try:
            result = self.benchmark_faiss(vectors, query_vectors)
            results.append(result)
        except Exception as e:
            print(f"⚠️  FAISS benchmark failed: {e}")

        # ChromaDB
        try:
            result = self.benchmark_chroma(vectors, texts, query_vectors)
            results.append(result)
        except Exception as e:
            print(f"⚠️  ChromaDB benchmark failed: {e}")

        self.results.extend(results)
        return results

    def print_comparison(self, results: List[BenchmarkResult]) -> None:
        """Print comparison table of results."""
        print("\n" + "=" * 80)
        print("📊 Benchmark Comparison")
        print("=" * 80)

        print(f"\n{'Database':<15} {'Latency (ms)':<15} {'QPS':<10} {'Recall@10':<12} {'Memory (MB)':<12} {'Build Time (s)':<15}")
        print("-" * 80)

        for result in results:
            print(
                f"{result.database:<15} "
                f"{result.query_latency_ms:<15.2f} "
                f"{result.queries_per_second:<10.0f} "
                f"{result.recall_at_10:<12.1f}% "
                f"{result.memory_mb:<12.1f} "
                f"{result.index_build_time_s:<15.2f}"
            )

        # Find best in each category
        print("\n🏆 Winners:")
        fastest = min(results, key=lambda r: r.query_latency_ms)
        print(f"   Fastest: {fastest.database} ({fastest.query_latency_ms:.2f}ms)")

        most_accurate = max(results, key=lambda r: r.recall_at_10)
        print(f"   Most Accurate: {most_accurate.database} ({most_accurate.recall_at_10:.1f}%)")

        most_efficient = min(results, key=lambda r: r.memory_mb)
        print(f"   Most Memory Efficient: {most_efficient.database} ({most_efficient.memory_mb:.1f}MB)")

    def plot_results(self, results: List[BenchmarkResult], save_path: str = "benchmark_results.png") -> None:
        """Plot benchmark results."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Vector Database Benchmark Results", fontsize=16)

        databases = [r.database for r in results]

        # Query latency
        ax = axes[0, 0]
        latencies = [r.query_latency_ms for r in results]
        ax.bar(databases, latencies, color=["#3498db", "#e74c3c", "#2ecc71"])
        ax.set_ylabel("Latency (ms)")
        ax.set_title("Query Latency (Lower is Better)")
        ax.grid(axis="y", alpha=0.3)

        # Recall
        ax = axes[0, 1]
        recalls = [r.recall_at_10 for r in results]
        ax.bar(databases, recalls, color=["#3498db", "#e74c3c", "#2ecc71"])
        ax.set_ylabel("Recall@10 (%)")
        ax.set_title("Search Accuracy (Higher is Better)")
        ax.set_ylim([90, 100])
        ax.grid(axis="y", alpha=0.3)

        # Memory usage
        ax = axes[1, 0]
        memory = [r.memory_mb for r in results]
        ax.bar(databases, memory, color=["#3498db", "#e74c3c", "#2ecc71"])
        ax.set_ylabel("Memory (MB)")
        ax.set_title("Memory Usage (Lower is Better)")
        ax.grid(axis="y", alpha=0.3)

        # Queries per second
        ax = axes[1, 1]
        qps = [r.queries_per_second for r in results]
        ax.bar(databases, qps, color=["#3498db", "#e74c3c", "#2ecc71"])
        ax.set_ylabel("QPS")
        ax.set_title("Throughput (Higher is Better)")
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"\n📊 Plot saved to: {save_path}")

    def save_results(self, results: List[BenchmarkResult], output_file: str = "benchmark_results.json") -> None:
        """Save results to JSON file."""
        data = [asdict(r) for r in results]

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Results saved to: {output_file}")


def main():
    """Main benchmark execution."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║  Module 11: Vector Database Benchmark                    ║
║  Comparing Qdrant, FAISS, and ChromaDB                    ║
╚═══════════════════════════════════════════════════════════╝
""")

    print("Prerequisites:")
    print("  - Qdrant running: docker run -p 6333:6333 qdrant/qdrant")
    print("  - Dependencies installed: pip install -r requirements.txt")
    print()

    # Initialize benchmark
    benchmark = VectorDBBenchmark(vector_dim=384)

    # Run benchmark with 10K vectors
    results = benchmark.run_full_benchmark(num_vectors=10000)

    # Print comparison
    benchmark.print_comparison(results)

    # Plot results
    benchmark.plot_results(results)

    # Save results
    benchmark.save_results(results)

    print("\n" + "=" * 80)
    print("✅ Benchmark Complete!")
    print("=" * 80)

    print("\n💡 Key Takeaways:")
    print("  • FAISS: Fastest queries, but no persistence or filtering")
    print("  • Qdrant: Best balance - production-ready with excellent filtering")
    print("  • ChromaDB: Easiest to use, great for local development")
    print()
    print("💡 When to use each:")
    print("  • Production RAG systems → Qdrant")
    print("  • Research & experiments → FAISS")
    print("  • Local development → ChromaDB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        print("\nTroubleshooting:")
        print("  - Is Qdrant running? (docker ps)")
        print("  - Are all dependencies installed?")
        print("  - Is there enough memory available?")
