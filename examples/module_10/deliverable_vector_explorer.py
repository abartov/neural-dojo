#!/usr/bin/env python3
"""
Module 10 Deliverable: Vector Space Explorer

An interactive tool for exploring the geometry of semantic vector spaces.
Experience the "Heureka Moment" - see how math works on meaning!

Features:
- Generate embeddings for custom word lists
- Visualize in 2D using PCA or t-SNE
- Interactive vector arithmetic (king - man + woman = queen!)
- Nearest neighbor search
- Automatic cluster discovery
- Beautiful visualizations

Usage:
    # Run interactive explorer
    python deliverable_vector_explorer.py --interactive

    # Run demonstrations
    python deliverable_vector_explorer.py --demo analogies
    python deliverable_vector_explorer.py --demo relationships
    python deliverable_vector_explorer.py --demo clustering

    # Custom word list
    python deliverable_vector_explorer.py --words "king,queen,man,woman,prince,princess"

Author: Neural Dojo Student
Date: 2025-11-23
Module: 10 (Vector Spaces & Semantic Search)
"""

import argparse
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VectorResult:
    """Result of a vector operation."""
    word: str
    similarity: float
    vector: np.ndarray


class VectorSpaceExplorer:
    """
    Interactive tool for exploring semantic vector spaces.

    This class demonstrates the "Heureka Moment" of Module 10:
    Math works on meaning! Vector arithmetic transforms concepts.
    """

    def __init__(
        self,
        model_name: str = 'all-MiniLM-L6-v2',
        cache_dir: Path = Path('.cache')
    ):
        """
        Initialize Vector Space Explorer.

        Args:
            model_name: Sentence Transformer model name
            cache_dir: Directory for caching embeddings
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Storage
        self.words: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self.embeddings_2d: Optional[np.ndarray] = None
        self.reduction_method: Optional[str] = None

        logger.info("VectorSpaceExplorer initialized")

    def load_words(self, words: List[str], force_reload: bool = False):
        """
        Load word list and generate embeddings.

        Args:
            words: List of words/phrases to embed
            force_reload: Force re-generation of embeddings
        """
        self.words = words
        cache_file = self.cache_dir / f"words_cache_{hash(tuple(sorted(words)))}.pkl"

        # Try to load from cache
        if cache_file.exists() and not force_reload:
            logger.info(f"Loading embeddings from cache: {cache_file}")
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.embeddings = cached_data['embeddings']
                    logger.info(f"✅ Loaded {len(self.words)} embeddings from cache")
                    return
            except Exception as e:
                logger.warning(f"Cache load failed: {e}, regenerating...")

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(words)} words...")
        self.embeddings = self.model.encode(
            words,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        logger.info(f"✅ Generated {len(self.embeddings)} embeddings")

        # Cache embeddings
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'words': words,
                'model': self.model_name
            }, f)
        logger.info(f"✅ Cached embeddings to {cache_file}")

    def reduce_dimensions(self, method: str = 'pca', n_components: int = 2):
        """
        Reduce embeddings to 2D for visualization.

        Args:
            method: 'pca' or 'tsne'
            n_components: Number of dimensions (typically 2)
        """
        if self.embeddings is None:
            raise ValueError("No embeddings loaded. Call load_words() first.")

        logger.info(f"Reducing dimensions using {method.upper()}...")

        if method == 'pca':
            reducer = PCA(n_components=n_components, random_state=42)
            self.embeddings_2d = reducer.fit_transform(self.embeddings)
            variance = sum(reducer.explained_variance_ratio_) * 100
            logger.info(f"✅ PCA complete ({variance:.1f}% variance explained)")
        elif method == 'tsne':
            reducer = TSNE(n_components=n_components, random_state=42, perplexity=min(30, len(self.words)-1))
            self.embeddings_2d = reducer.fit_transform(self.embeddings)
            logger.info(f"✅ t-SNE complete")
        else:
            raise ValueError(f"Unknown method: {method}. Use 'pca' or 'tsne'")

        self.reduction_method = method

    def vector_arithmetic(
        self,
        positive: List[str],
        negative: List[str],
        top_k: int = 5
    ) -> List[VectorResult]:
        """
        Perform vector arithmetic: (positive words) - (negative words).

        Classic example: king - man + woman ≈ queen
        positive = ['king', 'woman']
        negative = ['man']

        Args:
            positive: Words to add
            negative: Words to subtract
            top_k: Number of results to return

        Returns:
            List of VectorResult objects, sorted by similarity
        """
        if self.embeddings is None:
            raise ValueError("No embeddings loaded. Call load_words() first.")

        # Get embeddings for positive and negative words
        positive_vecs = []
        for word in positive:
            if word not in self.words:
                raise ValueError(f"Word '{word}' not in vocabulary. Load it first.")
            idx = self.words.index(word)
            positive_vecs.append(self.embeddings[idx])

        negative_vecs = []
        for word in negative:
            if word not in self.words:
                raise ValueError(f"Word '{word}' not in vocabulary. Load it first.")
            idx = self.words.index(word)
            negative_vecs.append(self.embeddings[idx])

        # Perform vector arithmetic
        result_vec = np.mean(positive_vecs, axis=0) - np.mean(negative_vecs, axis=0)

        # Find nearest neighbors
        similarities = cosine_similarity([result_vec], self.embeddings)[0]

        # Create results (exclude input words)
        results = []
        exclude_words = set(positive + negative)
        for idx, sim in enumerate(similarities):
            if self.words[idx] not in exclude_words:
                results.append(VectorResult(
                    word=self.words[idx],
                    similarity=float(sim),
                    vector=self.embeddings[idx]
                ))

        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)

        return results[:top_k]

    def nearest_neighbors(self, word: str, top_k: int = 5) -> List[VectorResult]:
        """
        Find nearest neighbors of a word in vector space.

        Args:
            word: Query word
            top_k: Number of neighbors to return

        Returns:
            List of VectorResult objects, sorted by similarity
        """
        if self.embeddings is None:
            raise ValueError("No embeddings loaded. Call load_words() first.")

        if word not in self.words:
            raise ValueError(f"Word '{word}' not in vocabulary.")

        # Get word embedding
        idx = self.words.index(word)
        word_vec = self.embeddings[idx]

        # Calculate similarities
        similarities = cosine_similarity([word_vec], self.embeddings)[0]

        # Create results (exclude query word)
        results = []
        for i, sim in enumerate(similarities):
            if i != idx:  # Exclude the word itself
                results.append(VectorResult(
                    word=self.words[i],
                    similarity=float(sim),
                    vector=self.embeddings[i]
                ))

        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)

        return results[:top_k]

    def cluster_words(self, n_clusters: int = 3) -> Dict[int, List[str]]:
        """
        Automatically discover semantic clusters using K-means.

        Args:
            n_clusters: Number of clusters

        Returns:
            Dictionary mapping cluster_id to list of words
        """
        if self.embeddings is None:
            raise ValueError("No embeddings loaded. Call load_words() first.")

        logger.info(f"Clustering {len(self.words)} words into {n_clusters} clusters...")

        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(self.embeddings)

        # Group by cluster
        clusters = {}
        for cluster_id in range(n_clusters):
            cluster_words = [self.words[i] for i, label in enumerate(labels) if label == cluster_id]
            clusters[cluster_id] = cluster_words

        logger.info(f"✅ Clustered into {n_clusters} groups")

        return clusters

    def visualize(
        self,
        title: str = "Semantic Vector Space",
        highlight_words: Optional[List[str]] = None,
        show_clusters: bool = False,
        n_clusters: int = 3,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[Path] = None
    ):
        """
        Visualize embeddings in 2D space.

        Args:
            title: Plot title
            highlight_words: Words to highlight with different color/size
            show_clusters: Show cluster boundaries
            n_clusters: Number of clusters if show_clusters=True
            figsize: Figure size
            save_path: Path to save figure (optional)
        """
        if self.embeddings_2d is None:
            raise ValueError("No 2D embeddings. Call reduce_dimensions() first.")

        fig, ax = plt.subplots(figsize=figsize)

        # Cluster if requested
        cluster_labels = None
        if show_clusters:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(self.embeddings)

        # Plot points
        if cluster_labels is not None:
            # Color by cluster
            scatter = ax.scatter(
                self.embeddings_2d[:, 0],
                self.embeddings_2d[:, 1],
                c=cluster_labels,
                cmap='tab10',
                s=100,
                alpha=0.6,
                edgecolors='black',
                linewidth=1
            )
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Cluster ID', rotation=270, labelpad=20)
        else:
            # Single color
            ax.scatter(
                self.embeddings_2d[:, 0],
                self.embeddings_2d[:, 1],
                s=100,
                alpha=0.6,
                c='steelblue',
                edgecolors='black',
                linewidth=1
            )

        # Highlight specific words
        if highlight_words:
            highlight_indices = [i for i, word in enumerate(self.words) if word in highlight_words]
            if highlight_indices:
                ax.scatter(
                    self.embeddings_2d[highlight_indices, 0],
                    self.embeddings_2d[highlight_indices, 1],
                    s=300,
                    alpha=0.8,
                    c='red',
                    edgecolors='darkred',
                    linewidth=2,
                    marker='*',
                    zorder=10
                )

        # Add labels
        for i, word in enumerate(self.words):
            fontsize = 12 if (highlight_words and word in highlight_words) else 9
            fontweight = 'bold' if (highlight_words and word in highlight_words) else 'normal'
            ax.annotate(
                word,
                (self.embeddings_2d[i, 0], self.embeddings_2d[i, 1]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=fontsize,
                fontweight=fontweight,
                alpha=0.9
            )

        # Styling
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(f'Dimension 1 ({self.reduction_method.upper()})', fontsize=12)
        ax.set_ylabel(f'Dimension 2 ({self.reduction_method.upper()})', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Saved visualization to {save_path}")

        plt.show()

    def visualize_vector_arithmetic(
        self,
        positive: List[str],
        negative: List[str],
        result_word: str,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[Path] = None
    ):
        """
        Visualize vector arithmetic operation with arrows.

        Shows: positive - negative = result

        Args:
            positive: Words to add
            negative: Words to subtract
            result_word: Expected result word
            figsize: Figure size
            save_path: Path to save figure (optional)
        """
        if self.embeddings_2d is None:
            raise ValueError("No 2D embeddings. Call reduce_dimensions() first.")

        fig, ax = plt.subplots(figsize=figsize)

        # Plot all points (faded)
        ax.scatter(
            self.embeddings_2d[:, 0],
            self.embeddings_2d[:, 1],
            s=50,
            alpha=0.2,
            c='gray'
        )

        # Get 2D positions
        def get_2d_pos(word):
            idx = self.words.index(word)
            return self.embeddings_2d[idx]

        # Plot operation words
        colors = {'positive': 'green', 'negative': 'red', 'result': 'blue'}

        for word in positive:
            pos = get_2d_pos(word)
            ax.scatter(pos[0], pos[1], s=300, c=colors['positive'], marker='o', edgecolors='darkgreen', linewidth=2, zorder=10)
            ax.annotate(word, pos, xytext=(5, 5), textcoords='offset points', fontsize=12, fontweight='bold')

        for word in negative:
            pos = get_2d_pos(word)
            ax.scatter(pos[0], pos[1], s=300, c=colors['negative'], marker='o', edgecolors='darkred', linewidth=2, zorder=10)
            ax.annotate(word, pos, xytext=(5, 5), textcoords='offset points', fontsize=12, fontweight='bold')

        result_pos = get_2d_pos(result_word)
        ax.scatter(result_pos[0], result_pos[1], s=400, c=colors['result'], marker='*', edgecolors='darkblue', linewidth=2, zorder=10)
        ax.annotate(result_word, result_pos, xytext=(5, 5), textcoords='offset points', fontsize=14, fontweight='bold', color='darkblue')

        # Draw arrows showing the operation
        # This is simplified - in 2D projection, the arithmetic doesn't perfectly match
        origin = np.mean([get_2d_pos(w) for w in positive], axis=0)
        for word in negative:
            pos = get_2d_pos(word)
            ax.arrow(origin[0], origin[1], pos[0]-origin[0], pos[1]-origin[1],
                    head_width=0.05, head_length=0.05, fc='red', ec='red', alpha=0.5, linestyle='--')

        # Title
        operation = " + ".join(positive) + " - " + " - ".join(negative) + " ≈ " + result_word
        ax.set_title(f"Vector Arithmetic: {operation}", fontsize=14, fontweight='bold', pad=20)

        ax.set_xlabel(f'Dimension 1 ({self.reduction_method.upper()})', fontsize=12)
        ax.set_ylabel(f'Dimension 2 ({self.reduction_method.upper()})', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Positive (add)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Negative (subtract)'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='blue', markersize=15, label='Result')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Saved visualization to {save_path}")

        plt.show()


def print_vector_results(results: List[VectorResult], title: str = "Results"):
    """Pretty print vector arithmetic results."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")

    for i, result in enumerate(results, 1):
        bar = '█' * int(result.similarity * 40)
        print(f"{i}. {result.word:20s} | Similarity: {result.similarity:.3f} {bar}")

    print()


# Demonstration datasets
def get_analogy_words() -> List[str]:
    """Get words for analogy demonstrations."""
    return [
        # Royalty
        'king', 'queen', 'prince', 'princess',
        # Gender pairs
        'man', 'woman', 'boy', 'girl', 'father', 'mother', 'brother', 'sister',
        # Geography
        'Paris', 'France', 'Rome', 'Italy', 'London', 'England', 'Berlin', 'Germany',
        'Tokyo', 'Japan', 'Beijing', 'China',
        # Verb forms
        'walking', 'walked', 'running', 'run', 'swimming', 'swim',
        # Comparative/Superlative
        'good', 'better', 'best', 'bad', 'worse', 'worst',
    ]


def get_relationship_words() -> List[str]:
    """Get words for semantic relationship demonstrations."""
    return [
        # Opposites
        'hot', 'cold', 'big', 'small', 'fast', 'slow', 'happy', 'sad',
        'light', 'dark', 'day', 'night', 'up', 'down', 'left', 'right',
        # Synonyms
        'happy', 'joyful', 'cheerful', 'glad',
        'sad', 'unhappy', 'miserable', 'sorrowful',
        'big', 'large', 'huge', 'enormous',
        'small', 'tiny', 'little', 'miniature',
    ]


def get_topic_words() -> List[str]:
    """Get words for topic clustering demonstration."""
    return [
        # Animals
        'dog', 'cat', 'lion', 'tiger', 'elephant', 'giraffe',
        # Food
        'pizza', 'burger', 'sushi', 'pasta', 'bread', 'cheese',
        # Technology
        'computer', 'phone', 'internet', 'software', 'code', 'algorithm',
        # Sports
        'football', 'basketball', 'tennis', 'soccer', 'baseball', 'hockey',
        # Nature
        'tree', 'flower', 'mountain', 'river', 'ocean', 'forest',
        # Music
        'piano', 'guitar', 'violin', 'drums', 'music', 'song',
    ]


def demo_analogies(explorer: VectorSpaceExplorer):
    """Demonstrate classic word analogies."""
    print("\n" + "🔮"*40)
    print("🔮  DEMO 1: ANALOGIES - Math Works on Meaning!  🔮")
    print("🔮"*40 + "\n")

    words = get_analogy_words()
    explorer.load_words(words)
    explorer.reduce_dimensions(method='pca')

    # Demo 1: king - man + woman ≈ queen
    print("\n" + "─"*80)
    print("ANALOGY 1: Gender Transformation")
    print("─"*80)
    print("\n🤔 Question: If 'king' is to 'man', what is to 'woman'?")
    print("📐 Vector Math: king - man + woman = ?")
    print()

    results = explorer.vector_arithmetic(
        positive=['king', 'woman'],
        negative=['man'],
        top_k=5
    )
    print_vector_results(results, "Top 5 Results")

    if results and results[0].word == 'queen':
        print("✅ SUCCESS! The top result is 'queen'! Math works on meaning! 🔮\n")
    else:
        print(f"🎯 Top result: '{results[0].word}' (expected 'queen')\n")

    # Demo 2: Paris - France + Italy ≈ Rome
    print("\n" + "─"*80)
    print("ANALOGY 2: Geographic Relationship")
    print("─"*80)
    print("\n🤔 Question: If 'Paris' is to 'France', what is to 'Italy'?")
    print("📐 Vector Math: Paris - France + Italy = ?")
    print()

    results = explorer.vector_arithmetic(
        positive=['Paris', 'Italy'],
        negative=['France'],
        top_k=5
    )
    print_vector_results(results, "Top 5 Results")

    if results and results[0].word == 'Rome':
        print("✅ SUCCESS! The top result is 'Rome'! Geography encoded in vectors! 🗺️\n")

    # Demo 3: Grammar transformation
    print("\n" + "─"*80)
    print("ANALOGY 3: Grammar Transformation")
    print("─"*80)
    print("\n🤔 Question: If 'walking' is to 'walk', what is to 'run'?")
    print("📐 Vector Math: walking - walk + run = ?")
    print()

    # Check if we have these words
    if all(w in words for w in ['walking', 'walk', 'run']):
        results = explorer.vector_arithmetic(
            positive=['walking', 'run'],
            negative=['walk'],
            top_k=5
        )
        print_vector_results(results, "Top 5 Results")

    # Visualize
    print("\n📊 Visualizing semantic space...")
    explorer.visualize(
        title="🔮 Analogy Demonstration: King, Queen, Man, Woman",
        highlight_words=['king', 'queen', 'man', 'woman'],
        figsize=(14, 10)
    )


def demo_relationships(explorer: VectorSpaceExplorer):
    """Demonstrate semantic relationships."""
    print("\n" + "🔗"*40)
    print("🔗  DEMO 2: SEMANTIC RELATIONSHIPS  🔗")
    print("🔗"*40 + "\n")

    words = get_relationship_words()
    explorer.load_words(words)
    explorer.reduce_dimensions(method='tsne')

    # Find opposites
    print("\n" + "─"*80)
    print("FINDING OPPOSITES")
    print("─"*80)

    opposite_pairs = [
        ('hot', 'cold'),
        ('big', 'small'),
        ('happy', 'sad'),
        ('day', 'night')
    ]

    for word1, word2 in opposite_pairs:
        if word1 in words and word2 in words:
            idx1 = explorer.words.index(word1)
            idx2 = explorer.words.index(word2)
            vec1 = explorer.embeddings[idx1]
            vec2 = explorer.embeddings[idx2]
            similarity = cosine_similarity([vec1], [vec2])[0][0]
            print(f"  '{word1}' ↔️ '{word2}': similarity = {similarity:.3f}")

    # Find synonyms
    print("\n" + "─"*80)
    print("FINDING SYNONYMS")
    print("─"*80)

    synonym_groups = [
        ['happy', 'joyful', 'cheerful'],
        ['big', 'large', 'huge'],
        ['small', 'tiny', 'little']
    ]

    for group in synonym_groups:
        if all(w in words for w in group):
            print(f"\n  Synonym group: {', '.join(group)}")
            # Calculate pairwise similarities
            for i, word1 in enumerate(group):
                for word2 in group[i+1:]:
                    idx1 = explorer.words.index(word1)
                    idx2 = explorer.words.index(word2)
                    vec1 = explorer.embeddings[idx1]
                    vec2 = explorer.embeddings[idx2]
                    similarity = cosine_similarity([vec1], [vec2])[0][0]
                    print(f"    '{word1}' ↔️ '{word2}': {similarity:.3f}")

    # Nearest neighbors
    print("\n" + "─"*80)
    print("NEAREST NEIGHBORS")
    print("─"*80)

    test_words = ['happy', 'big', 'fast']
    for word in test_words:
        if word in words:
            print(f"\n🔍 Nearest neighbors of '{word}':")
            neighbors = explorer.nearest_neighbors(word, top_k=5)
            for i, neighbor in enumerate(neighbors, 1):
                bar = '█' * int(neighbor.similarity * 30)
                print(f"  {i}. {neighbor.word:15s} {neighbor.similarity:.3f} {bar}")

    # Visualize
    print("\n📊 Visualizing semantic relationships...")
    explorer.visualize(
        title="🔗 Semantic Relationships: Opposites and Synonyms",
        highlight_words=['happy', 'sad', 'big', 'small'],
        figsize=(14, 10)
    )


def demo_clustering(explorer: VectorSpaceExplorer):
    """Demonstrate automatic topic discovery."""
    print("\n" + "📊"*40)
    print("📊  DEMO 3: AUTOMATIC TOPIC CLUSTERING  📊")
    print("📊"*40 + "\n")

    words = get_topic_words()
    explorer.load_words(words)
    explorer.reduce_dimensions(method='pca')

    # Cluster into topics
    n_clusters = 6  # Animals, Food, Tech, Sports, Nature, Music
    clusters = explorer.cluster_words(n_clusters=n_clusters)

    print("\n" + "─"*80)
    print(f"DISCOVERED {n_clusters} SEMANTIC CLUSTERS")
    print("─"*80 + "\n")

    for cluster_id, cluster_words in clusters.items():
        print(f"📁 Cluster {cluster_id + 1}:")
        print(f"   Words: {', '.join(cluster_words)}")
        print()

    # Visualize with clusters
    print("📊 Visualizing clusters...")
    explorer.visualize(
        title="📊 Automatic Topic Discovery: K-means Clustering",
        show_clusters=True,
        n_clusters=n_clusters,
        figsize=(14, 10)
    )

    print("\n💡 Notice how words group by semantic meaning automatically!")
    print("   The model has never seen 'topic labels', but discovers them from geometry!\n")


def interactive_mode(explorer: VectorSpaceExplorer):
    """Run interactive exploration mode."""
    print("\n" + "="*80)
    print("🔮 VECTOR SPACE EXPLORER - Interactive Mode")
    print("="*80)
    print("\nExplore the geometry of semantic meaning!")
    print("\nCommands:")
    print("  1. Load words - Enter custom word list")
    print("  2. Visualize - See words in 2D semantic space")
    print("  3. Arithmetic - Perform vector arithmetic (A - B + C)")
    print("  4. Neighbors - Find nearest neighbors")
    print("  5. Cluster - Discover semantic clusters")
    print("  quit - Exit")
    print()

    words_loaded = False

    while True:
        try:
            cmd = input("\n🔮 Command (1-5 or quit): ").strip().lower()

            if cmd in ['quit', 'q', 'exit']:
                print("👋 Goodbye!")
                break

            if cmd == '1':
                # Load words
                words_input = input("Enter words (comma-separated): ").strip()
                words = [w.strip() for w in words_input.split(',') if w.strip()]
                if len(words) < 3:
                    print("❌ Please enter at least 3 words")
                    continue
                explorer.load_words(words)
                explorer.reduce_dimensions(method='pca')
                words_loaded = True
                print(f"✅ Loaded {len(words)} words")

            elif cmd == '2':
                # Visualize
                if not words_loaded:
                    print("❌ Load words first (command 1)")
                    continue
                clusters = input("Show clusters? (y/n): ").strip().lower() == 'y'
                if clusters:
                    n = int(input("Number of clusters (2-10): ").strip())
                    explorer.visualize(show_clusters=True, n_clusters=n)
                else:
                    explorer.visualize()

            elif cmd == '3':
                # Vector arithmetic
                if not words_loaded:
                    print("❌ Load words first (command 1)")
                    continue
                print("\nVector arithmetic: (positive words) - (negative words)")
                print(f"Available words: {', '.join(explorer.words)}")
                pos_input = input("Positive words (comma-separated): ").strip()
                neg_input = input("Negative words (comma-separated): ").strip()
                positive = [w.strip() for w in pos_input.split(',') if w.strip()]
                negative = [w.strip() for w in neg_input.split(',') if w.strip()]

                results = explorer.vector_arithmetic(positive, negative, top_k=5)
                operation = " + ".join(positive) + " - " + " - ".join(negative)
                print_vector_results(results, f"Results: {operation} = ?")

            elif cmd == '4':
                # Nearest neighbors
                if not words_loaded:
                    print("❌ Load words first (command 1)")
                    continue
                print(f"Available words: {', '.join(explorer.words)}")
                word = input("Enter word: ").strip()
                if word not in explorer.words:
                    print(f"❌ Word '{word}' not found")
                    continue
                results = explorer.nearest_neighbors(word, top_k=5)
                print_vector_results(results, f"Nearest neighbors of '{word}'")

            elif cmd == '5':
                # Clustering
                if not words_loaded:
                    print("❌ Load words first (command 1)")
                    continue
                n = int(input("Number of clusters (2-10): ").strip())
                clusters = explorer.cluster_words(n_clusters=n)
                print(f"\n{'='*80}")
                print(f"Discovered {n} Clusters")
                print(f"{'='*80}\n")
                for cluster_id, cluster_words in clusters.items():
                    print(f"Cluster {cluster_id + 1}: {', '.join(cluster_words)}")

            else:
                print("❌ Unknown command. Use 1-5 or 'quit'")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            continue


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Vector Space Explorer - Explore the geometry of semantic meaning!"
    )
    parser.add_argument(
        '--demo',
        choices=['analogies', 'relationships', 'clustering', 'all'],
        help='Run demonstration'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--words',
        type=str,
        help='Comma-separated list of words to explore'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Sentence Transformer model (default: all-MiniLM-L6-v2)'
    )

    args = parser.parse_args()

    # Initialize explorer
    explorer = VectorSpaceExplorer(model_name=args.model)

    # Run demo
    if args.demo:
        if args.demo in ['analogies', 'all']:
            demo_analogies(explorer)
        if args.demo in ['relationships', 'all']:
            demo_relationships(explorer)
        if args.demo in ['clustering', 'all']:
            demo_clustering(explorer)
        return

    # Interactive mode
    if args.interactive:
        interactive_mode(explorer)
        return

    # Custom words
    if args.words:
        words = [w.strip() for w in args.words.split(',')]
        explorer.load_words(words)
        explorer.reduce_dimensions(method='pca')
        explorer.visualize(title=f"Exploring {len(words)} Words")
        return

    # No arguments - show help
    parser.print_help()
    print("\n💡 Try:")
    print("  python deliverable_vector_explorer.py --demo all")
    print("  python deliverable_vector_explorer.py --interactive")


if __name__ == '__main__':
    main()
