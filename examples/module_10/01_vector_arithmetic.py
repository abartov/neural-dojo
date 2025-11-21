"""
Module 10 Example 1: Vector Arithmetic & Visualization

This example demonstrates the HEUREKA MOMENT: Math works on meaning!

Demonstrations:
1. Vector arithmetic: king - man + woman ≈ queen
2. Analogies: Paris - France + Italy ≈ Rome
3. Visualizing semantic space in 2D/3D
4. Understanding the geometry of meaning

Prerequisites:
- sentence-transformers
- scikit-learn
- matplotlib (for visualization)
- numpy

Cost: FREE (uses local models)
"""

import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass

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
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SK_AVAILABLE = True
except ImportError:
    SK_AVAILABLE = False
    print("⚠️  Install: pip install scikit-learn")

try:
    import matplotlib.pyplot as plt
    PLT_AVAILABLE = True
except ImportError:
    PLT_AVAILABLE = False
    print("⚠️  Install: pip install matplotlib")


def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# =============================================================================
# Vector Arithmetic Functions
# =============================================================================

def vector_arithmetic(
    positive: List[str],
    negative: List[str],
    vocabulary: List[str],
    topn: int = 5
) -> List[Tuple[str, float]]:
    """
    Perform vector arithmetic on words and find closest results.

    Args:
        positive: Words to add
        negative: Words to subtract
        vocabulary: All available words to search
        topn: Number of results to return

    Returns:
        List of (word, similarity_score) tuples
    """
    if not SBERT_AVAILABLE:
        raise RuntimeError("sentence-transformers required")

    # Generate embeddings
    positive_embs = [model.encode(word) for word in positive]
    negative_embs = [model.encode(word) for word in negative]

    # Vector arithmetic
    result_vector = np.sum(positive_embs, axis=0) - np.sum(negative_embs, axis=0)

    # Find closest words
    similarities = []
    for word in vocabulary:
        # Skip input words
        if word in positive or word in negative:
            continue

        word_emb = model.encode(word)
        sim = cosine_similarity(result_vector, word_emb)
        similarities.append((word, sim))

    # Sort and return top-n
    return sorted(similarities, key=lambda x: x[1], reverse=True)[:topn]


# =============================================================================
# Demonstration 1: Classic Examples
# =============================================================================

def demo_classic_analogies():
    """Demonstrate the famous king-man+woman=queen example and others."""
    print("\n" + "="*80)
    print("🔮 HEUREKA MOMENT: Vector Arithmetic on Meaning!")
    print("="*80)
    print("\nMath works on concepts! Watch:")

    if not SBERT_AVAILABLE:
        print("⚠️  sentence-transformers required")
        return

    # Vocabulary for search
    vocabulary = [
        # Royalty
        "queen", "king", "prince", "princess", "monarch", "empress", "duke", "duchess",
        # People
        "man", "woman", "boy", "girl", "male", "female", "gentleman", "lady",
        # Other
        "person", "child", "adult", "human", "people"
    ]

    # Example 1: king - man + woman ≈ queen
    print("\n" + "="*80)
    print("Example 1: Gender Transformation")
    print("="*80)
    print("\nQuestion: If 'king' is to 'man', what is to 'woman'?")
    print("Formula: king - man + woman ≈ ?")

    results = vector_arithmetic(
        positive=["king", "woman"],
        negative=["man"],
        vocabulary=vocabulary,
        topn=5
    )

    print("\nResults:")
    for i, (word, score) in enumerate(results, 1):
        bar = "█" * int(score * 50)
        print(f"{i}. {score:.3f} {bar} {word}")

    print("\n💡 Explanation:")
    print("   king   = [royalty + male + power + ...]")
    print("   - man  = [male + human + adult]")
    print("   + woman = [female + human + adult]")
    print("   ≈ [royalty + female + power + ...] = QUEEN!")

    # Example 2: Opposite gender pairs
    print("\n" + "="*80)
    print("Example 2: More Gender Transformations")
    print("="*80)

    pairs = [
        (["prince", "woman"], ["man"]),
        (["boy", "woman"], ["man"]),
        (["gentleman", "woman"], ["man"]),
    ]

    for positive, negative in pairs:
        results = vector_arithmetic(positive, negative, vocabulary, topn=3)
        print(f"\n{positive[0]} - {negative[0]} + {positive[1]} ≈ {results[0][0]}")
        print(f"  Confidence: {results[0][1]:.3f}")


def demo_geography_analogies():
    """Demonstrate geographic analogies: Paris-France+Italy≈Rome."""
    print("\n" + "="*80)
    print("Example 3: Geographic Relationships")
    print("="*80)
    print("\nCapitals and countries have consistent relationships!")

    if not SBERT_AVAILABLE:
        return

    # Geographic vocabulary
    vocabulary = [
        # European cities
        "Paris", "London", "Berlin", "Rome", "Madrid", "Vienna", "Athens", "Lisbon",
        "Amsterdam", "Brussels", "Dublin", "Prague",
        # Countries
        "France", "England", "Germany", "Italy", "Spain", "Austria", "Greece",
        "Portugal", "Netherlands", "Belgium", "Ireland", "Czech",
        # Asian cities
        "Tokyo", "Beijing", "Seoul", "Bangkok",
        # Asian countries
        "Japan", "China", "Korea", "Thailand"
    ]

    examples = [
        (["Paris", "Italy"], ["France"], "Rome"),
        (["London", "Germany"], ["England"], "Berlin"),
        (["Tokyo", "China"], ["Japan"], "Beijing"),
    ]

    for positive, negative, expected in examples:
        print(f"\n{positive[0]} - {negative[0]} + {positive[1]} ≈ ?")
        print(f"Expected: {expected}")

        results = vector_arithmetic(positive, negative, vocabulary, topn=3)

        print(f"Results:")
        for i, (word, score) in enumerate(results, 1):
            marker = "✅" if word == expected else "  "
            print(f"  {marker} {i}. {score:.3f} - {word}")


def demo_grammar_analogies():
    """Demonstrate grammatical transformations."""
    print("\n" + "="*80)
    print("Example 4: Grammar Transformations")
    print("="*80)
    print("\nGrammar rules are captured as vector relationships!")

    if not SBERT_AVAILABLE:
        return

    vocabulary = [
        # Present/past tense
        "walk", "walking", "walked",
        "run", "running", "ran",
        "eat", "eating", "ate",
        "swim", "swimming", "swam",
        # Comparative/superlative
        "good", "better", "best",
        "bad", "worse", "worst",
        "fast", "faster", "fastest",
    ]

    examples = [
        (["walking", "run"], ["walk"], "running"),
        (["walked", "eat"], ["walk"], "ate"),
        (["better", "bad"], ["good"], "worse"),
    ]

    for positive, negative, expected in examples:
        print(f"\n{positive[0]} - {negative[0]} + {positive[1]} ≈ ?")
        print(f"Expected: {expected}")

        results = vector_arithmetic(positive, negative, vocabulary, topn=3)

        print(f"Results:")
        for i, (word, score) in enumerate(results, 1):
            marker = "✅" if word == expected else "  "
            print(f"  {marker} {i}. {score:.3f} - {word}")


# =============================================================================
# Demonstration 2: Visualization
# =============================================================================

def visualize_semantic_space_2d():
    """Visualize embeddings in 2D using PCA."""
    print("\n" + "="*80)
    print("Visualization: Semantic Space in 2D")
    print("="*80)

    if not all([SBERT_AVAILABLE, SK_AVAILABLE, PLT_AVAILABLE]):
        print("⚠️  Requires sentence-transformers, scikit-learn, matplotlib")
        return

    # Words to visualize
    words = [
        # Royalty
        "king", "queen", "prince", "princess",
        # Commoners
        "man", "woman", "boy", "girl",
        # Concepts
        "power", "gentle", "strong", "kind"
    ]

    print(f"\nVisualizing {len(words)} words in 2D space...")

    # Generate embeddings
    embeddings = [model.encode(word) for word in words]

    # Reduce to 2D using PCA
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)

    # Create plot
    plt.figure(figsize=(12, 8))

    # Plot points
    for word, (x, y) in zip(words, embeddings_2d):
        plt.scatter(x, y, s=200, alpha=0.6)
        plt.annotate(word, (x, y), fontsize=12, ha='center', va='bottom')

    # Draw some relationship arrows
    def draw_arrow(word1, word2, color='blue', style='-'):
        idx1 = words.index(word1)
        idx2 = words.index(word2)
        x1, y1 = embeddings_2d[idx1]
        x2, y2 = embeddings_2d[idx2]
        plt.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color=color, linestyle=style, lw=2))

    # Male→Female transformation
    draw_arrow("king", "queen", color='red')
    draw_arrow("man", "woman", color='red')

    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)")
    plt.title("Semantic Space Visualization (2D Projection)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    print("✅ Plot created!")
    print("   → Notice: Related words cluster together")
    print("   → Red arrows show gender transformations")
    print("   → Parallel arrows = analogous relationships!")

    plt.savefig('/Users/krisztiankoos/projects/neural-dojo/examples/module_10/semantic_space_2d.png', dpi=150)
    print("\n📊 Saved: semantic_space_2d.png")


def visualize_clusters():
    """Visualize topical clusters."""
    print("\n" + "="*80)
    print("Visualization: Topic Clusters")
    print("="*80)

    if not all([SBERT_AVAILABLE, SK_AVAILABLE, PLT_AVAILABLE]):
        print("⚠️  Requires sentence-transformers, scikit-learn, matplotlib")
        return

    # Words from different topics
    topics = {
        "Programming": ["Python", "JavaScript", "coding", "software", "programming"],
        "Food": ["pizza", "pasta", "cooking", "recipe", "cuisine"],
        "Sports": ["football", "basketball", "soccer", "athlete", "competition"],
        "Science": ["physics", "chemistry", "experiment", "research", "laboratory"]
    }

    all_words = []
    labels = []
    for topic, words in topics.items():
        all_words.extend(words)
        labels.extend([topic] * len(words))

    print(f"\nVisualizing {len(all_words)} words from {len(topics)} topics...")

    # Generate embeddings
    embeddings = [model.encode(word) for word in all_words]

    # Reduce to 2D
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(all_words)-1))
    embeddings_2d = tsne.fit_transform(embeddings)

    # Create plot
    plt.figure(figsize=(12, 8))

    # Color map
    colors = {'Programming': 'blue', 'Food': 'green', 'Sports': 'red', 'Science': 'purple'}

    for topic in topics:
        # Get indices for this topic
        indices = [i for i, label in enumerate(labels) if label == topic]
        x = [embeddings_2d[i, 0] for i in indices]
        y = [embeddings_2d[i, 1] for i in indices]

        plt.scatter(x, y, c=colors[topic], label=topic, s=200, alpha=0.6)

        # Annotate
        for i in indices:
            plt.annotate(all_words[i], (embeddings_2d[i, 0], embeddings_2d[i, 1]),
                         fontsize=10, ha='center', va='bottom')

    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    plt.title("Topic Clusters in Semantic Space")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    print("✅ Plot created!")
    print("   → Notice: Words cluster by topic")
    print("   → Distance in space ≈ semantic distance")

    plt.savefig('/Users/krisztiankoos/projects/neural-dojo/examples/module_10/topic_clusters.png', dpi=150)
    print("\n📊 Saved: topic_clusters.png")


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*80)
    print("MODULE 10: VECTOR ARITHMETIC & VISUALIZATION")
    print("="*80)
    print("\n🔮 This is the HEUREKA MOMENT!")
    print("\nYou're about to see that MATH WORKS ON MEANING.")
    print("Vector arithmetic literally transforms concepts!")

    if not SBERT_AVAILABLE:
        print("\n⚠️  sentence-transformers required")
        print("    Install: pip install sentence-transformers")
        return

    # Run demonstrations
    demo_classic_analogies()
    demo_geography_analogies()
    demo_grammar_analogies()

    if SK_AVAILABLE and PLT_AVAILABLE:
        visualize_semantic_space_2d()
        visualize_clusters()
    else:
        print("\n⚠️  Install scikit-learn and matplotlib for visualizations")

    print("\n" + "="*80)
    print("✅ HEUREKA MOMENT COMPLETE! 🔮")
    print("="*80)
    print("\nKey insights:")
    print("  1. Embeddings create semantic space")
    print("  2. Similar words cluster together")
    print("  3. Relationships are preserved as directions")
    print("  4. Vector arithmetic transforms meaning")
    print("  5. king - man + woman = queen (really works!)")
    print("\nThis is why embeddings are so powerful:")
    print("  → We can do algebra on CONCEPTS")
    print("  → Math operations correspond to meaning transformations")
    print("  → Semantic understanding is geometric!")
    print("\n🎯 Next: Example 2 - Production Semantic Search")
    print("="*80)


if __name__ == "__main__":
    main()
