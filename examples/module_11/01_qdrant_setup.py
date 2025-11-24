"""
Module 11 Example 1: Qdrant Setup and Basic Operations

This example demonstrates:
1. Connecting to Qdrant (local Docker instance)
2. Creating vector collections
3. Inserting documents with embeddings
4. Performing similarity searches
5. Using metadata filtering

Author: Neural Dojo
Time: ~2 hours
"""

from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
from sentence_transformers import SentenceTransformer


def connect_to_qdrant(url: str = "http://localhost:6333") -> QdrantClient:
    """
    Connect to Qdrant instance.

    Args:
        url: Qdrant server URL (default: local Docker instance)

    Returns:
        QdrantClient instance
    """
    try:
        client = QdrantClient(url=url)
        # Test connection
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant at {url}")
        print(f"📊 Existing collections: {len(collections.collections)}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        print("\n💡 Make sure Qdrant is running:")
        print("   docker run -p 6333:6333 qdrant/qdrant")
        raise


def create_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int = 384,
    distance: Distance = Distance.COSINE,
    recreate: bool = True,
) -> None:
    """
    Create a vector collection in Qdrant.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection to create
        vector_size: Dimension of vectors (default: 384 for all-MiniLM-L6-v2)
        distance: Distance metric (COSINE, DOT, EUCLID)
        recreate: If True, delete existing collection with same name
    """
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)

        if exists and recreate:
            print(f"⚠️  Collection '{collection_name}' exists, deleting...")
            client.delete_collection(collection_name)
        elif exists and not recreate:
            print(f"✅ Collection '{collection_name}' already exists")
            return

        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance,
            ),
        )
        print(f"✅ Collection '{collection_name}' created")
        print(f"   Vector size: {vector_size}")
        print(f"   Distance metric: {distance}")

    except Exception as e:
        print(f"❌ Failed to create collection: {e}")
        raise


def insert_documents(
    client: QdrantClient,
    collection_name: str,
    documents: List[Dict[str, Any]],
    embedding_model: SentenceTransformer,
) -> None:
    """
    Insert documents with embeddings into Qdrant collection.

    Args:
        client: Qdrant client instance
        collection_name: Target collection name
        documents: List of documents with 'id', 'text', and metadata fields
        embedding_model: Model to generate embeddings
    """
    print(f"\n📝 Inserting {len(documents)} documents...")

    try:
        # Generate embeddings for all documents
        texts = [doc["text"] for doc in documents]
        embeddings = embedding_model.encode(texts, show_progress_bar=True)

        # Create points for Qdrant
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Extract metadata (everything except 'text')
            payload = {k: v for k, v in doc.items() if k != "text"}
            payload["text"] = doc["text"]  # Include text in payload too

            points.append(
                PointStruct(
                    id=doc["id"],
                    vector=embedding.tolist(),
                    payload=payload,
                )
            )

        # Upload to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points,
        )

        print(f"✅ Inserted {len(points)} documents")

    except Exception as e:
        print(f"❌ Failed to insert documents: {e}")
        raise


def search_similar(
    client: QdrantClient,
    collection_name: str,
    query: str,
    embedding_model: SentenceTransformer,
    top_k: int = 5,
    score_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar documents using semantic similarity.

    Args:
        client: Qdrant client instance
        collection_name: Collection to search
        query: Search query text
        embedding_model: Model to encode query
        top_k: Number of results to return
        score_threshold: Minimum similarity score (0-1)

    Returns:
        List of results with score and payload
    """
    print(f"\n🔍 Searching for: \"{query}\"")

    try:
        # Encode query
        query_vector = embedding_model.encode(query).tolist()

        # Search
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # Format results
        formatted_results = []
        for hit in results:
            formatted_results.append({
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
            })

        print(f"✅ Found {len(formatted_results)} results")
        return formatted_results

    except Exception as e:
        print(f"❌ Search failed: {e}")
        raise


def search_with_filter(
    client: QdrantClient,
    collection_name: str,
    query: str,
    embedding_model: SentenceTransformer,
    filters: Dict[str, Any],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Search with metadata filtering (hybrid search).

    Args:
        client: Qdrant client instance
        collection_name: Collection to search
        query: Search query text
        embedding_model: Model to encode query
        filters: Dictionary of field filters
        top_k: Number of results to return

    Returns:
        List of filtered results
    """
    print(f"\n🔍 Filtered search for: \"{query}\"")
    print(f"📋 Filters: {filters}")

    try:
        # Encode query
        query_vector = embedding_model.encode(query).tolist()

        # Build filter conditions
        conditions = []
        for field, value in filters.items():
            if isinstance(value, (int, float)):
                # Numeric range filter
                conditions.append(
                    FieldCondition(
                        key=field,
                        range=Range(gte=value),
                    )
                )
            else:
                # Exact match filter
                conditions.append(
                    FieldCondition(
                        key=field,
                        match=MatchValue(value=value),
                    )
                )

        # Search with filters
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=Filter(must=conditions) if conditions else None,
            limit=top_k,
        )

        # Format results
        formatted_results = []
        for hit in results:
            formatted_results.append({
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
            })

        print(f"✅ Found {len(formatted_results)} filtered results")
        return formatted_results

    except Exception as e:
        print(f"❌ Filtered search failed: {e}")
        raise


def print_results(results: List[Dict[str, Any]]) -> None:
    """Pretty print search results."""
    if not results:
        print("❌ No results found")
        return

    print(f"\n📊 Top {len(results)} Results:")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. [Score: {result['score']:.3f}] (ID: {result['id']})")
        print(f"   Text: {result['text'][:100]}...")
        if result['metadata']:
            print(f"   Metadata: {result['metadata']}")


def demo_basic_operations():
    """Demo: Basic Qdrant operations."""
    print("\n" + "=" * 80)
    print("DEMO: Basic Qdrant Operations")
    print("=" * 80)

    # 1. Connect to Qdrant
    client = connect_to_qdrant()

    # 2. Load embedding model
    print("\n📦 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")

    # 3. Create collection
    collection_name = "documents"
    create_collection(client, collection_name, vector_size=384)

    # 4. Prepare sample documents
    documents = [
        {
            "id": 1,
            "text": "Introduction to Machine Learning: supervised and unsupervised learning",
            "category": "AI",
            "year": 2023,
        },
        {
            "id": 2,
            "text": "Deep Learning with Neural Networks: CNNs, RNNs, and Transformers",
            "category": "AI",
            "year": 2024,
        },
        {
            "id": 3,
            "text": "Python Programming Best Practices: PEP 8, type hints, and testing",
            "category": "Programming",
            "year": 2023,
        },
        {
            "id": 4,
            "text": "Data Science Fundamentals: statistics, visualization, and pandas",
            "category": "Data Science",
            "year": 2023,
        },
        {
            "id": 5,
            "text": "Natural Language Processing with Transformers: BERT, GPT, and T5",
            "category": "AI",
            "year": 2024,
        },
        {
            "id": 6,
            "text": "Web Development with FastAPI: building REST APIs in Python",
            "category": "Programming",
            "year": 2024,
        },
        {
            "id": 7,
            "text": "Reinforcement Learning: Q-learning, policy gradients, and PPO",
            "category": "AI",
            "year": 2024,
        },
        {
            "id": 8,
            "text": "Vector Databases: HNSW indexing and similarity search",
            "category": "Data Science",
            "year": 2024,
        },
    ]

    # 5. Insert documents
    insert_documents(client, collection_name, documents, model)

    # 6. Basic similarity search
    results = search_similar(
        client,
        collection_name,
        query="machine learning algorithms",
        embedding_model=model,
        top_k=3,
    )
    print_results(results)

    # 7. Search with score threshold
    results = search_similar(
        client,
        collection_name,
        query="python programming",
        embedding_model=model,
        top_k=3,
        score_threshold=0.5,
    )
    print_results(results)


def demo_metadata_filtering():
    """Demo: Metadata filtering (hybrid search)."""
    print("\n" + "=" * 80)
    print("DEMO: Metadata Filtering")
    print("=" * 80)

    # Connect and get model
    client = connect_to_qdrant()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    collection_name = "documents"

    # Search only AI category
    results = search_with_filter(
        client,
        collection_name,
        query="neural networks",
        embedding_model=model,
        filters={"category": "AI"},
        top_k=3,
    )
    print_results(results)

    # Search only recent documents (2024)
    results = search_with_filter(
        client,
        collection_name,
        query="machine learning",
        embedding_model=model,
        filters={"year": 2024},
        top_k=3,
    )
    print_results(results)


def demo_collection_stats():
    """Demo: Collection statistics and info."""
    print("\n" + "=" * 80)
    print("DEMO: Collection Statistics")
    print("=" * 80)

    client = connect_to_qdrant()
    collection_name = "documents"

    try:
        # Get collection info
        info = client.get_collection(collection_name)

        print(f"\n📊 Collection: {collection_name}")
        print(f"   Points count: {info.points_count}")
        print(f"   Vector size: {info.config.params.vectors.size}")
        print(f"   Distance: {info.config.params.vectors.distance}")
        print(f"   Status: {info.status}")

        # Get a sample point
        points = client.scroll(
            collection_name=collection_name,
            limit=1,
        )

        if points[0]:
            sample = points[0][0]
            print(f"\n📝 Sample Point:")
            print(f"   ID: {sample.id}")
            print(f"   Payload keys: {list(sample.payload.keys())}")
            print(f"   Text: {sample.payload.get('text', '')[:100]}...")

    except Exception as e:
        print(f"❌ Failed to get collection stats: {e}")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║  Module 11: Qdrant Setup and Basic Operations            ║
║  Vector Databases & Semantic Search                       ║
╚═══════════════════════════════════════════════════════════╝
""")

    print("Make sure Qdrant is running:")
    print("  docker run -p 6333:6333 qdrant/qdrant")
    print()

    try:
        # Run all demos
        demo_basic_operations()
        demo_metadata_filtering()
        demo_collection_stats()

        print("\n" + "=" * 80)
        print("✅ All demos completed successfully!")
        print("=" * 80)

        print("\n💡 Next Steps:")
        print("  1. Try different queries and see how semantic search works")
        print("  2. Experiment with different embedding models")
        print("  3. Add more documents with diverse metadata")
        print("  4. Run example 02 to benchmark different vector databases")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("  - Is Qdrant running? (docker ps)")
        print("  - Is port 6333 available? (lsof -i :6333)")
        print("  - Are dependencies installed? (pip install -r requirements.txt)")
