"""
Module 9 Example 2: Semantic Applications

This example demonstrates practical applications of embeddings:
1. Semantic Search - Find relevant documents using meaning
2. Clustering - Group similar items automatically
3. Recommendation System - Recommend similar items
4. Zero-Shot Classification - Classify without training
5. Duplicate Detection - Find near-duplicate content

Prerequisites:
- sentence-transformers library
- scikit-learn library

This example uses local models (FREE, no API calls needed!)
"""

import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from collections import Counter

# Try to import required libraries
try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
    # Load model once
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"✅ Loaded model: all-MiniLM-L6-v2 ({model.get_sentence_embedding_dimension()} dims)")
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠️  Install sentence-transformers: pip install sentence-transformers")

try:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Install scikit-learn: pip install scikit-learn")


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@dataclass
class SearchResult:
    """Container for search result."""
    text: str
    score: float
    rank: int


# =============================================================================
# APPLICATION 1: Semantic Search
# =============================================================================

def demo_semantic_search():
    """Demonstrate semantic search that understands meaning, not just keywords."""
    print("\n" + "="*80)
    print("APPLICATION 1: Semantic Search")
    print("="*80)
    print("\nFind relevant documents even when keywords don't match!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required")
        return

    # Knowledge base (documentation)
    documents = [
        "How to restart a Linux service using systemctl",
        "Service recovery and troubleshooting procedures",
        "Debugging crashed daemon processes",
        "Kubernetes pod restart policies",
        "Database backup and restore procedures",
        "Monitoring service health with Prometheus",
        "Configuring automatic service restarts",
        "Python recipe for chocolate cake",
        "Italian cooking pasta recipes",
        "Network troubleshooting guide",
    ]

    print(f"\nKnowledge base: {len(documents)} documents")

    # Precompute document embeddings (do this once in production)
    print("\n📊 Indexing documents...")
    doc_embeddings = model.encode(documents)
    print(f"✅ Indexed {len(documents)} documents")

    # User queries
    queries = [
        "fix a crashed service",
        "reboot a failed daemon",
        "cooking recipes",
    ]

    for query in queries:
        print(f"\n{'='*80}")
        print(f"🔍 Query: '{query}'")
        print(f"{'='*80}")

        # Generate query embedding
        query_embedding = model.encode(query)

        # Calculate similarities to all documents
        similarities = [
            cosine_similarity(query_embedding, doc_emb)
            for doc_emb in doc_embeddings
        ]

        # Rank results
        results = [
            SearchResult(text=doc, score=sim, rank=i+1)
            for i, (doc, sim) in enumerate(sorted(
                zip(documents, similarities),
                key=lambda x: x[1],
                reverse=True
            ))
        ]

        # Show top 3 results
        print("\nTop 3 results:")
        print("-" * 80)
        for i, result in enumerate(results[:3], 1):
            bar = "█" * int(result.score * 50)
            print(f"\n{i}. Score: {result.score:.3f} {bar}")
            print(f"   {result.text}")

        # Show why semantic search works
        if "crashed" in query or "failed" in query:
            print("\n💡 Why this works:")
            print("   The model understands:")
            print("   - 'fix' ≈ 'restart' ≈ 'recovery'")
            print("   - 'crashed' ≈ 'failed' ≈ 'debugging'")
            print("   - 'service' ≈ 'daemon' ≈ 'process'")
            print("   → No exact keyword matches needed!")


# =============================================================================
# APPLICATION 2: Clustering
# =============================================================================

def demo_clustering():
    """Automatically group similar documents."""
    print("\n" + "="*80)
    print("APPLICATION 2: Document Clustering")
    print("="*80)
    print("\nAutomatically group similar documents by topic!")

    if not SBERT_AVAILABLE or not SKLEARN_AVAILABLE:
        print("⚠️  Requires sentence-transformers and scikit-learn")
        return

    # Mixed collection of documents
    documents = [
        # Cluster 1: Programming/Development
        "Python programming tutorial for beginners",
        "JavaScript web development guide",
        "React frontend framework documentation",
        "TypeScript type system overview",
        "Node.js backend development",

        # Cluster 2: Machine Learning/AI
        "Machine learning fundamentals",
        "Deep learning with PyTorch",
        "Neural networks introduction",
        "AI and artificial intelligence basics",
        "Training transformers for NLP",

        # Cluster 3: DevOps/Infrastructure
        "Kubernetes container orchestration",
        "Docker containerization guide",
        "CI/CD pipeline setup with GitHub Actions",
        "Infrastructure as code with Terraform",
        "Cloud deployment on AWS",

        # Cluster 4: Food/Cooking
        "Italian pasta cooking recipes",
        "Baking chocolate cake tutorial",
        "Healthy meal prep ideas",
        "Vegetarian cooking guide",
    ]

    print(f"\nDocuments: {len(documents)}")

    # Generate embeddings
    print("\n📊 Generating embeddings...")
    embeddings = model.encode(documents)
    print(f"✅ Generated {len(embeddings)} embeddings")

    # Cluster into 4 groups
    n_clusters = 4
    print(f"\n🎯 Clustering into {n_clusters} groups...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)

    # Display clusters
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)

    cluster_names = [
        "Programming/Development",
        "Machine Learning/AI",
        "DevOps/Infrastructure",
        "Food/Cooking"
    ]

    for cluster_id in range(n_clusters):
        # Get documents in this cluster
        cluster_docs = [
            doc for doc, label in zip(documents, cluster_labels)
            if label == cluster_id
        ]

        print(f"\n📁 Cluster {cluster_id + 1}: {len(cluster_docs)} documents")
        print("-" * 80)

        for doc in cluster_docs:
            print(f"  • {doc}")

    print("\n💡 Observations:")
    print("   - Programming docs grouped together")
    print("   - ML/AI docs grouped together")
    print("   - DevOps docs grouped together")
    print("   - Cooking docs grouped together")
    print("   → Clustering works without manual labels!")


# =============================================================================
# APPLICATION 3: Recommendation System
# =============================================================================

def demo_recommendations():
    """Recommend similar items based on user preferences."""
    print("\n" + "="*80)
    print("APPLICATION 3: Recommendation System")
    print("="*80)
    print("\nRecommend items similar to what the user likes!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required")
        return

    # Catalog of articles
    all_articles = [
        "Introduction to neural networks and deep learning",
        "Advanced transformer architectures explained",
        "Cooking perfect risotto at home",
        "Python programming best practices",
        "Machine learning for time series forecasting",
        "Gardening tips for beginners",
        "Natural language processing with BERT",
        "Italian cuisine: authentic pasta recipes",
        "Understanding attention mechanisms in transformers",
        "Baking sourdough bread tutorial",
        "Reinforcement learning fundamentals",
    ]

    # User's reading history (what they liked)
    user_favorites = [
        "Introduction to neural networks and deep learning",
        "Natural language processing with BERT",
    ]

    print(f"\nUser has read and liked:")
    for fav in user_favorites:
        print(f"  ❤️  {fav}")

    # Generate embeddings for all articles
    print("\n📊 Generating embeddings...")
    all_embeddings = model.encode(all_articles)
    favorite_embeddings = model.encode(user_favorites)

    # Create user profile (average of favorites)
    user_profile = np.mean(favorite_embeddings, axis=0)

    # Score all articles (exclude already read)
    scores = []
    for article, embedding in zip(all_articles, all_embeddings):
        if article in user_favorites:
            continue  # Skip already read

        similarity = cosine_similarity(user_profile, embedding)
        scores.append((article, similarity))

    # Rank recommendations
    recommendations = sorted(scores, key=lambda x: x[1], reverse=True)

    print("\n" + "="*80)
    print("RECOMMENDED FOR YOU:")
    print("="*80)

    for i, (article, score) in enumerate(recommendations[:5], 1):
        bar = "█" * int(score * 50)
        print(f"\n{i}. Score: {score:.3f} {bar}")
        print(f"   {article}")

    print("\n💡 Notice:")
    print("   - ML/AI articles ranked high (similar to user's interests)")
    print("   - Cooking/gardening articles ranked low (different topics)")
    print("   → Recommendations match user preferences!")


# =============================================================================
# APPLICATION 4: Zero-Shot Classification
# =============================================================================

def demo_classification():
    """Classify text without training a classifier!"""
    print("\n" + "="*80)
    print("APPLICATION 4: Zero-Shot Classification")
    print("="*80)
    print("\nClassify text by comparing to category descriptions!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required")
        return

    # Define categories with descriptions
    categories = {
        "Technology": "Software, hardware, programming, computers, AI, tech startups",
        "Sports": "Football, basketball, athletics, competitions, teams, players",
        "Politics": "Government, elections, policy, legislation, politicians",
        "Entertainment": "Movies, music, celebrities, TV shows, arts, culture",
        "Business": "Finance, companies, stocks, economy, markets, entrepreneurship",
    }

    # Texts to classify
    texts_to_classify = [
        "Apple releases new iPhone with advanced AI features",
        "Lakers win championship after intense playoff series",
        "New climate legislation passed by Congress",
        "Taylor Swift announces world tour dates",
        "Tesla stock surges after quarterly earnings report",
        "Python 3.12 introduces new syntax features",
    ]

    print("\nCategories defined:")
    for category, description in categories.items():
        print(f"  📁 {category}: {description}")

    # Generate category embeddings
    category_embeddings = {
        name: model.encode(description)
        for name, description in categories.items()
    }

    print("\n" + "="*80)
    print("CLASSIFICATION RESULTS:")
    print("="*80)

    # Classify each text
    for text in texts_to_classify:
        print(f"\n📄 Text: '{text}'")
        print("-" * 80)

        # Generate text embedding
        text_embedding = model.encode(text)

        # Calculate similarity to each category
        scores = {
            category: cosine_similarity(text_embedding, cat_emb)
            for category, cat_emb in category_embeddings.items()
        }

        # Predict category (highest score)
        predicted = max(scores, key=scores.get)

        print(f"✅ Predicted: {predicted} (score: {scores[predicted]:.3f})")
        print(f"\nAll scores:")
        for category in sorted(scores, key=scores.get, reverse=True):
            bar = "█" * int(scores[category] * 40)
            print(f"  {category:15} {scores[category]:.3f} {bar}")

    print("\n💡 Zero-shot means:")
    print("   - No training data needed")
    print("   - No model fine-tuning required")
    print("   - Just compare text to category descriptions")
    print("   → Works out of the box!")


# =============================================================================
# APPLICATION 5: Duplicate Detection
# =============================================================================

def demo_duplicate_detection():
    """Find duplicate or near-duplicate documents."""
    print("\n" + "="*80)
    print("APPLICATION 5: Duplicate Detection")
    print("="*80)
    print("\nFind near-duplicate content automatically!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required")
        return

    # Documents (some are duplicates/paraphrases)
    documents = [
        "How to restart a Linux service",
        "Restarting a service in Linux",          # Duplicate of #1
        "Linux service restart tutorial",         # Duplicate of #1
        "Python programming for beginners",
        "Introduction to Python programming",     # Duplicate of #4
        "Cooking pasta recipes",
        "How to cook perfect pasta",             # Duplicate of #6
        "Machine learning fundamentals",
        "Kubernetes deployment guide",
    ]

    print(f"\nDocuments: {len(documents)}")

    # Generate embeddings
    embeddings = model.encode(documents)

    # Find duplicates (similarity > threshold)
    threshold = 0.75
    duplicates = []

    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim > threshold:
                duplicates.append((i, j, sim, documents[i], documents[j]))

    # Display duplicates
    print(f"\n🔍 Found {len(duplicates)} duplicate pairs (threshold={threshold}):")
    print("="*80)

    for i, j, sim, doc_i, doc_j in sorted(duplicates, key=lambda x: x[2], reverse=True):
        print(f"\n📎 Similarity: {sim:.3f}")
        print(f"   Doc {i+1}: {doc_i}")
        print(f"   Doc {j+1}: {doc_j}")

    if duplicates:
        print("\n💡 Actions you could take:")
        print("   - Merge duplicate content")
        print("   - Remove redundant documents")
        print("   - Add canonical links")
        print("   - Flag for human review")
    else:
        print("\n✅ No duplicates found!")


# =============================================================================
# BONUS: Semantic Search with Ranking
# =============================================================================

def demo_advanced_search():
    """Advanced semantic search with multiple ranking factors."""
    print("\n" + "="*80)
    print("BONUS: Advanced Semantic Search")
    print("="*80)
    print("\nCombine semantic similarity with other ranking signals!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required")
        return

    # Documents with metadata
    documents_with_meta = [
        {"text": "How to restart a Linux service", "views": 1000, "date": "2024-01"},
        {"text": "Service recovery procedures", "views": 500, "date": "2024-02"},
        {"text": "Debugging crashed services", "views": 2000, "date": "2024-03"},
        {"text": "Kubernetes pod restart", "views": 800, "date": "2024-01"},
        {"text": "Python tutorial", "views": 300, "date": "2024-02"},
    ]

    query = "fix a failed service"

    print(f"\n🔍 Query: '{query}'")

    # Generate embeddings
    query_embedding = model.encode(query)
    doc_embeddings = [model.encode(doc["text"]) for doc in documents_with_meta]

    # Calculate semantic similarity
    similarities = [
        cosine_similarity(query_embedding, doc_emb)
        for doc_emb in doc_embeddings
    ]

    # Calculate popularity score (normalized views)
    max_views = max(doc["views"] for doc in documents_with_meta)
    popularity_scores = [doc["views"] / max_views for doc in documents_with_meta]

    # Calculate recency score (newer = better)
    dates = [doc["date"] for doc in documents_with_meta]
    recency_scores = [1.0 if date == "2024-03" else 0.7 if date == "2024-02" else 0.5 for date in dates]

    # Combine scores (weighted)
    final_scores = [
        0.7 * sim + 0.2 * pop + 0.1 * rec
        for sim, pop, rec in zip(similarities, popularity_scores, recency_scores)
    ]

    # Rank results
    results = sorted(
        zip(documents_with_meta, similarities, popularity_scores, recency_scores, final_scores),
        key=lambda x: x[4],  # Sort by final score
        reverse=True
    )

    print("\n" + "="*80)
    print("RANKED RESULTS (semantic + popularity + recency):")
    print("="*80)

    for i, (doc, sem, pop, rec, final) in enumerate(results, 1):
        print(f"\n{i}. Final Score: {final:.3f}")
        print(f"   {doc['text']}")
        print(f"   Semantic: {sem:.2f} | Popularity: {pop:.2f} | Recency: {rec:.2f}")
        print(f"   Views: {doc['views']} | Date: {doc['date']}")

    print("\n💡 Production search systems combine:")
    print("   - Semantic similarity (meaning match)")
    print("   - Popularity (user engagement)")
    print("   - Recency (freshness)")
    print("   - Click-through rate")
    print("   - User preferences")
    print("   → Multi-signal ranking!")


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Run all application demonstrations."""
    print("="*80)
    print("MODULE 9: SEMANTIC APPLICATIONS")
    print("="*80)
    print("\nPractical applications of embeddings in real-world scenarios.")

    if not SBERT_AVAILABLE:
        print("\n⚠️  sentence-transformers required!")
        print("    Install: pip install sentence-transformers")
        return

    # Run all applications
    demo_semantic_search()
    demo_clustering()
    demo_recommendations()
    demo_classification()
    demo_duplicate_detection()
    demo_advanced_search()

    print("\n" + "="*80)
    print("✅ All applications demonstrated!")
    print("="*80)
    print("\nKey takeaways:")
    print("  1. Semantic search finds meaning, not just keywords")
    print("  2. Clustering groups similar items automatically")
    print("  3. Recommendations match user preferences")
    print("  4. Zero-shot classification needs no training")
    print("  5. Duplicate detection prevents redundancy")
    print("\nThese patterns work for:")
    print("  - Documentation search (kaizen)")
    print("  - Content recommendations (vibe)")
    print("  - News clustering (contrarian)")
    print("  - Infrastructure docs search (work)")
    print("\n🎯 Next: Module 10 - Vector Spaces & the Heureka Moment!")
    print("="*80)


if __name__ == "__main__":
    main()
