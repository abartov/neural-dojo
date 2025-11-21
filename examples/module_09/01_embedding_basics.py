"""
Module 9 Example 1: Embedding Basics & Similarity Calculation

This example demonstrates:
1. Generating embeddings using OpenAI API
2. Generating embeddings using open-source models (Sentence Transformers)
3. Calculating cosine similarity
4. Comparing semantic similarity between different text pairs
5. Performance comparison between models

Prerequisites:
- OpenAI API key (set in .env as ANTHROPIC_API_KEY)
- sentence-transformers library

Cost warning: This example makes ~10-15 API calls to OpenAI (~$0.01)
"""

import os
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import OpenAI (optional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except (ImportError, Exception):
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available. Install with: pip install openai")
    print("    Set OPENAI_API_KEY in .env file")

# Try to import Sentence Transformers (optional)
try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
    # Load a small, fast model
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"✅ Loaded Sentence Transformer model: all-MiniLM-L6-v2 ({sbert_model.get_sentence_embedding_dimension()} dimensions)")
except (ImportError, Exception) as e:
    SBERT_AVAILABLE = False
    print("⚠️  Sentence Transformers not available. Install with: pip install sentence-transformers")


@dataclass
class EmbeddingResult:
    """Container for embedding and metadata."""
    text: str
    embedding: List[float]
    model: str
    dimensions: int


# =============================================================================
# Embedding Generation Functions
# =============================================================================

def get_openai_embedding(text: str, model: str = "text-embedding-3-small") -> EmbeddingResult:
    """
    Generate embedding using OpenAI API.

    Args:
        text: Text to embed
        model: OpenAI model to use

    Returns:
        EmbeddingResult with embedding and metadata
    """
    if not OPENAI_AVAILABLE:
        raise RuntimeError("OpenAI is not available")

    # Normalize text (recommended by OpenAI)
    text = text.replace("\n", " ")

    # Generate embedding
    response = openai_client.embeddings.create(
        input=text,
        model=model
    )

    embedding = response.data[0].embedding

    return EmbeddingResult(
        text=text,
        embedding=embedding,
        model=model,
        dimensions=len(embedding)
    )


def get_sbert_embedding(text: str) -> EmbeddingResult:
    """
    Generate embedding using Sentence Transformers (local, free).

    Args:
        text: Text to embed

    Returns:
        EmbeddingResult with embedding and metadata
    """
    if not SBERT_AVAILABLE:
        raise RuntimeError("Sentence Transformers is not available")

    # Generate embedding (runs locally)
    embedding = sbert_model.encode(text)

    return EmbeddingResult(
        text=text,
        embedding=embedding.tolist(),
        model="all-MiniLM-L6-v2",
        dimensions=len(embedding)
    )


# =============================================================================
# Similarity Calculation
# =============================================================================

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Formula: cosine_similarity(A, B) = (A · B) / (|A| × |B|)

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Similarity score between -1 and 1 (typically 0 to 1 for text)
    """
    # Convert to numpy arrays
    a = np.array(vec_a)
    b = np.array(vec_b)

    # Compute dot product
    dot_product = np.dot(a, b)

    # Compute magnitudes (L2 norm)
    magnitude_a = np.linalg.norm(a)
    magnitude_b = np.linalg.norm(b)

    # Compute cosine similarity
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    similarity = dot_product / (magnitude_a * magnitude_b)

    return float(similarity)


def euclidean_distance(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate Euclidean distance between two vectors.

    Note: For text embeddings, cosine similarity is usually better!

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Distance (0 = identical, larger = more different)
    """
    a = np.array(vec_a)
    b = np.array(vec_b)

    return float(np.linalg.norm(a - b))


# =============================================================================
# Demonstration Functions
# =============================================================================

def demo_basic_similarity():
    """Demonstrate basic similarity calculation between text pairs."""
    print("\n" + "="*80)
    print("DEMO 1: Basic Semantic Similarity")
    print("="*80)

    # Test pairs with expected similarity
    test_pairs = [
        ("The cat sat on the mat", "A cat is sitting on a mat", "High (paraphrases)"),
        ("Machine learning is powerful", "AI and ML are transformative", "High (related topics)"),
        ("Python is a programming language", "Java is a programming language", "Medium (similar but different)"),
        ("I love pizza", "The weather is sunny today", "Low (unrelated)"),
        ("How do I restart a service?", "Restarting a crashed daemon", "High (synonyms)"),
    ]

    if SBERT_AVAILABLE:
        print("\nUsing Sentence Transformers (local, free):")
        print("-" * 80)

        for text_1, text_2, expected in test_pairs:
            # Generate embeddings
            emb_1 = get_sbert_embedding(text_1)
            emb_2 = get_sbert_embedding(text_2)

            # Calculate similarity
            sim = cosine_similarity(emb_1.embedding, emb_2.embedding)

            print(f"\nText 1: {text_1}")
            print(f"Text 2: {text_2}")
            print(f"Expected: {expected}")
            print(f"Similarity: {sim:.3f} {interpret_similarity(sim)}")

    if OPENAI_AVAILABLE:
        print("\n\nUsing OpenAI (API, paid):")
        print("-" * 80)

        # Just demonstrate with one pair to save API calls
        text_1, text_2, expected = test_pairs[0]

        emb_1 = get_openai_embedding(text_1)
        emb_2 = get_openai_embedding(text_2)

        sim = cosine_similarity(emb_1.embedding, emb_2.embedding)

        print(f"\nText 1: {text_1}")
        print(f"Text 2: {text_2}")
        print(f"Expected: {expected}")
        print(f"Similarity: {sim:.3f} {interpret_similarity(sim)}")
        print(f"Model: {emb_1.model} ({emb_1.dimensions} dimensions)")


def interpret_similarity(score: float) -> str:
    """Convert similarity score to human-readable interpretation."""
    if score >= 0.9:
        return "✅ Nearly identical"
    elif score >= 0.7:
        return "✅ Very similar"
    elif score >= 0.5:
        return "🟡 Somewhat similar"
    elif score >= 0.3:
        return "🟠 Slightly similar"
    else:
        return "❌ Not similar"


def demo_synonym_understanding():
    """Demonstrate that embeddings understand synonyms."""
    print("\n" + "="*80)
    print("DEMO 2: Synonym Understanding")
    print("="*80)
    print("\nEmbeddings understand that different words can have similar meanings!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required for this demo")
        return

    synonym_pairs = [
        ("car", "automobile"),
        ("happy", "joyful"),
        ("big", "large"),
        ("fast", "quick"),
        ("intelligent", "smart"),
    ]

    print("\nSynonym pairs:")
    print("-" * 80)

    for word_1, word_2 in synonym_pairs:
        emb_1 = get_sbert_embedding(word_1)
        emb_2 = get_sbert_embedding(word_2)

        sim = cosine_similarity(emb_1.embedding, emb_2.embedding)

        print(f"{word_1:15} ↔ {word_2:15} = {sim:.3f} {interpret_similarity(sim)}")

    # Compare to non-synonyms
    print("\nNon-synonym pairs (for comparison):")
    print("-" * 80)

    non_synonym_pairs = [
        ("car", "pizza"),
        ("happy", "computer"),
        ("big", "green"),
    ]

    for word_1, word_2 in non_synonym_pairs:
        emb_1 = get_sbert_embedding(word_1)
        emb_2 = get_sbert_embedding(word_2)

        sim = cosine_similarity(emb_1.embedding, emb_2.embedding)

        print(f"{word_1:15} ↔ {word_2:15} = {sim:.3f} {interpret_similarity(sim)}")


def demo_semantic_relationships():
    """Demonstrate semantic relationships captured by embeddings."""
    print("\n" + "="*80)
    print("DEMO 3: Semantic Relationships")
    print("="*80)
    print("\nEmbeddings capture conceptual relationships between terms!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required for this demo")
        return

    # Query and related terms
    query = "Python programming"

    candidates = [
        "JavaScript web development",     # Related (programming)
        "Machine learning with PyTorch",  # Related (Python + ML)
        "Cooking Italian cuisine",        # Unrelated
        "Ruby on Rails framework",        # Related (programming)
        "Data science tutorials",         # Related (often uses Python)
        "Gardening tips and tricks",      # Unrelated
    ]

    print(f"\nQuery: '{query}'")
    print("\nRanking candidates by semantic similarity:")
    print("-" * 80)

    # Generate query embedding
    query_emb = get_sbert_embedding(query)

    # Calculate similarities
    results = []
    for candidate in candidates:
        cand_emb = get_sbert_embedding(candidate)
        sim = cosine_similarity(query_emb.embedding, cand_emb.embedding)
        results.append((candidate, sim))

    # Sort by similarity (descending)
    results.sort(key=lambda x: x[1], reverse=True)

    # Display ranked results
    for i, (candidate, sim) in enumerate(results, 1):
        bar = "█" * int(sim * 50)
        print(f"{i}. {sim:.3f} {bar}")
        print(f"   {candidate}")


def demo_context_sensitivity():
    """Demonstrate that embeddings are context-sensitive."""
    print("\n" + "="*80)
    print("DEMO 4: Context Sensitivity")
    print("="*80)
    print("\nSame word in different contexts → different meanings!")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required for this demo")
        return

    # Word "bank" in different contexts
    contexts = [
        "I deposited money in the bank",           # Financial institution
        "We sat by the river bank",                # Edge of river
        "The plane made a steep bank to the left", # Aviation maneuver
    ]

    print("\nWord 'bank' in different contexts:")
    print("-" * 80)

    embeddings = [get_sbert_embedding(ctx) for ctx in contexts]

    # Compare similarities
    for i in range(len(contexts)):
        for j in range(i + 1, len(contexts)):
            sim = cosine_similarity(embeddings[i].embedding, embeddings[j].embedding)
            print(f"\nContext {i+1} vs Context {j+1}: {sim:.3f}")
            print(f"  '{contexts[i]}'")
            print(f"  '{contexts[j]}'")
            print(f"  → {interpret_similarity(sim)}")


def demo_cosine_vs_euclidean():
    """Compare cosine similarity vs Euclidean distance."""
    print("\n" + "="*80)
    print("DEMO 5: Cosine Similarity vs Euclidean Distance")
    print("="*80)
    print("\nWhy we use cosine similarity for text embeddings:")

    if not SBERT_AVAILABLE:
        print("⚠️  Sentence Transformers required for this demo")
        return

    # Two very similar texts (one is just longer/more detailed)
    text_1 = "Python is great"
    text_2 = "Python is a great programming language with excellent libraries"
    text_3 = "I love cooking pasta"

    emb_1 = get_sbert_embedding(text_1)
    emb_2 = get_sbert_embedding(text_2)
    emb_3 = get_sbert_embedding(text_3)

    print(f"\nText 1: '{text_1}'")
    print(f"Text 2: '{text_2}'")
    print(f"Text 3: '{text_3}'")

    print("\nText 1 vs Text 2 (similar topic, different length):")
    print("-" * 80)
    cos_sim_12 = cosine_similarity(emb_1.embedding, emb_2.embedding)
    euc_dist_12 = euclidean_distance(emb_1.embedding, emb_2.embedding)
    print(f"Cosine similarity: {cos_sim_12:.3f} {interpret_similarity(cos_sim_12)}")
    print(f"Euclidean distance: {euc_dist_12:.3f}")

    print("\nText 1 vs Text 3 (different topic):")
    print("-" * 80)
    cos_sim_13 = cosine_similarity(emb_1.embedding, emb_3.embedding)
    euc_dist_13 = euclidean_distance(emb_1.embedding, emb_3.embedding)
    print(f"Cosine similarity: {cos_sim_13:.3f} {interpret_similarity(cos_sim_13)}")
    print(f"Euclidean distance: {euc_dist_13:.3f}")

    print("\n💡 Key insight:")
    print("   Cosine similarity focuses on DIRECTION (meaning)")
    print("   Euclidean distance focuses on MAGNITUDE (length)")
    print("   → For text, direction matters more!")


def demo_model_comparison():
    """Compare different embedding models."""
    print("\n" + "="*80)
    print("DEMO 6: Model Comparison")
    print("="*80)

    test_text = "Machine learning transforms data into insights"

    print(f"\nText: '{test_text}'")
    print("\nModel comparison:")
    print("-" * 80)

    if SBERT_AVAILABLE:
        emb_sbert = get_sbert_embedding(test_text)
        print(f"\n✅ Sentence-BERT (all-MiniLM-L6-v2):")
        print(f"   Dimensions: {emb_sbert.dimensions}")
        print(f"   First 5 values: {emb_sbert.embedding[:5]}")
        print(f"   Cost: FREE (runs locally)")
        print(f"   Speed: Fast")

    if OPENAI_AVAILABLE:
        emb_openai = get_openai_embedding(test_text)
        print(f"\n✅ OpenAI (text-embedding-3-small):")
        print(f"   Dimensions: {emb_openai.dimensions}")
        print(f"   First 5 values: {emb_openai.embedding[:5]}")
        print(f"   Cost: $0.02 / 1M tokens")
        print(f"   Speed: API latency (~100-300ms)")

    if SBERT_AVAILABLE and OPENAI_AVAILABLE:
        # Compare similarity on a test pair
        text_a = "The cat sat on the mat"
        text_b = "A cat is sitting on a mat"

        # SBERT
        emb_a_sbert = get_sbert_embedding(text_a)
        emb_b_sbert = get_sbert_embedding(text_b)
        sim_sbert = cosine_similarity(emb_a_sbert.embedding, emb_b_sbert.embedding)

        # OpenAI
        emb_a_openai = get_openai_embedding(text_a)
        emb_b_openai = get_openai_embedding(text_b)
        sim_openai = cosine_similarity(emb_a_openai.embedding, emb_b_openai.embedding)

        print(f"\n\nSimilarity comparison on paraphrase:")
        print(f"  Text A: '{text_a}'")
        print(f"  Text B: '{text_b}'")
        print("-" * 80)
        print(f"  SBERT:  {sim_sbert:.3f} {interpret_similarity(sim_sbert)}")
        print(f"  OpenAI: {sim_openai:.3f} {interpret_similarity(sim_openai)}")
        print(f"\n💡 Both models recognize these as paraphrases!")


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*80)
    print("MODULE 9: EMBEDDING BASICS & SIMILARITY CALCULATION")
    print("="*80)
    print("\nThis example demonstrates embedding generation and similarity calculation.")
    print(f"\nAvailable models:")
    print(f"  - OpenAI: {'✅' if OPENAI_AVAILABLE else '❌'}")
    print(f"  - Sentence Transformers: {'✅' if SBERT_AVAILABLE else '❌'}")

    if not SBERT_AVAILABLE and not OPENAI_AVAILABLE:
        print("\n⚠️  No embedding models available!")
        print("    Install at least one:")
        print("    - pip install sentence-transformers  (free, local)")
        print("    - pip install openai  (requires API key)")
        return

    # Run demonstrations
    demo_basic_similarity()
    demo_synonym_understanding()
    demo_semantic_relationships()
    demo_context_sensitivity()
    demo_cosine_vs_euclidean()
    demo_model_comparison()

    print("\n" + "="*80)
    print("✅ All demonstrations complete!")
    print("="*80)
    print("\nKey takeaways:")
    print("  1. Embeddings capture semantic meaning as vectors")
    print("  2. Cosine similarity measures how 'close' meanings are")
    print("  3. Models understand synonyms, context, and relationships")
    print("  4. Different models have different dimensions and quality")
    print("  5. Cosine similarity > Euclidean distance for text")
    print("\nNext: Example 2 - Semantic Search & Applications")
    print("="*80)


if __name__ == "__main__":
    main()
