#!/usr/bin/env python3
"""
Module 9 Deliverable: Production-Ready Semantic Search Engine

This is a complete semantic search system for Neural Dojo documentation.
It demonstrates all key concepts from Module 9 in a real-world application.

Features:
- Document ingestion and chunking
- Embedding generation with caching
- Semantic similarity search
- Performance metrics (latency, recall@k)
- Production-ready code (error handling, logging)

Usage:
    # Index documentation
    python deliverable_semantic_search.py --index

    # Search
    python deliverable_semantic_search.py --query "How do I use embeddings?"

    # Interactive mode
    python deliverable_semantic_search.py --interactive

Author: Neural Dojo Student
Date: 2025-11-23
"""

import argparse
import json
import logging
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document chunk with metadata."""
    id: str
    text: str
    source_file: str
    chunk_index: int
    metadata: Dict[str, any]

    def __repr__(self) -> str:
        return f"Document(id={self.id}, source={self.source_file}, chunk={self.chunk_index})"


@dataclass
class SearchResult:
    """Represents a search result with score."""
    document: Document
    score: float
    rank: int

    def __repr__(self) -> str:
        return f"SearchResult(rank={self.rank}, score={self.score:.3f}, doc={self.document.id})"


class DocumentLoader:
    """Load and chunk markdown documents from the curriculum."""

    def __init__(self, docs_dir: Path, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document loader.

        Args:
            docs_dir: Path to documentation directory
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Overlap between chunks to preserve context
        """
        self.docs_dir = docs_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Initialized DocumentLoader: {docs_dir}")

    def load_all(self) -> List[Document]:
        """
        Load all markdown files from docs directory.

        Returns:
            List of Document objects
        """
        logger.info("Loading documents...")
        documents = []

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            try:
                docs = self._load_file(md_file)
                documents.extend(docs)
                logger.debug(f"Loaded {len(docs)} chunks from {md_file.name}")
            except Exception as e:
                logger.error(f"Error loading {md_file}: {e}")
                continue

        logger.info(f"Loaded {len(documents)} document chunks total")
        return documents

    def _load_file(self, file_path: Path) -> List[Document]:
        """
        Load and chunk a single markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            List of Document chunks
        """
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata from frontmatter (if present)
        metadata = self._extract_metadata(content)

        # Remove frontmatter
        content = self._remove_frontmatter(content)

        # Chunk the content
        chunks = self._chunk_text(content)

        # Create Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            doc_id = f"{file_path.stem}_{i}"
            documents.append(Document(
                id=doc_id,
                text=chunk,
                source_file=str(file_path.relative_to(self.docs_dir)),
                chunk_index=i,
                metadata=metadata
            ))

        return documents

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Strategy:
        - Split by paragraph first (preserve semantic units)
        - Combine paragraphs until chunk_size is reached
        - Add overlap to preserve context across chunks

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # Split by paragraphs (double newline)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            # If adding this paragraph exceeds chunk_size, save current chunk
            if current_size + para_size > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap (last paragraph from previous chunk)
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], para]
                    current_size = len(current_chunk[-1]) + para_size
                else:
                    current_chunk = [para]
                    current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        # Add final chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def _extract_metadata(self, content: str) -> Dict[str, any]:
        """Extract metadata from markdown frontmatter."""
        # Simple frontmatter extraction (YAML between --- markers)
        if not content.startswith('---'):
            return {}

        try:
            end_idx = content.index('---', 3)
            frontmatter = content[3:end_idx].strip()
            # Simple key: value parsing
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            return metadata
        except ValueError:
            return {}

    def _remove_frontmatter(self, content: str) -> str:
        """Remove frontmatter from content."""
        if not content.startswith('---'):
            return content

        try:
            end_idx = content.index('---', 3)
            return content[end_idx + 3:].strip()
        except ValueError:
            return content


class SemanticSearchEngine:
    """Production-ready semantic search engine."""

    def __init__(
        self,
        model_name: str = 'all-MiniLM-L6-v2',
        cache_dir: Path = Path('.cache')
    ):
        """
        Initialize semantic search engine.

        Args:
            model_name: Sentence Transformer model name
            cache_dir: Directory for caching embeddings
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)

        self.documents: List[Document] = []
        self.embeddings: Optional[np.ndarray] = None

        logger.info("SemanticSearchEngine initialized")

    def index_documents(self, documents: List[Document], force_reindex: bool = False):
        """
        Index documents (generate and cache embeddings).

        Args:
            documents: List of Document objects
            force_reindex: Force re-generation of embeddings even if cached
        """
        self.documents = documents
        cache_file = self.cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"

        # Try to load from cache
        if cache_file.exists() and not force_reindex:
            logger.info(f"Loading embeddings from cache: {cache_file}")
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    # Verify cache matches current documents
                    if len(cached_data['embeddings']) == len(documents):
                        self.embeddings = cached_data['embeddings']
                        logger.info("✅ Loaded embeddings from cache")
                        return
            except Exception as e:
                logger.warning(f"Cache load failed: {e}, regenerating...")

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        start_time = time.time()

        # Batch encode all documents
        texts = [doc.text for doc in documents]
        self.embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        elapsed = time.time() - start_time
        logger.info(f"✅ Generated {len(self.embeddings)} embeddings in {elapsed:.2f}s")
        logger.info(f"   ({elapsed/len(documents)*1000:.2f}ms per document)")

        # Cache embeddings
        logger.info(f"Caching embeddings to {cache_file}")
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'model': self.model_name,
                'document_count': len(documents)
            }, f)
        logger.info("✅ Embeddings cached")

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for documents semantically similar to query.

        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of SearchResult objects, sorted by score (descending)
        """
        if self.embeddings is None:
            raise ValueError("No documents indexed. Call index_documents() first.")

        # Encode query
        start_time = time.time()
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Create results
        results = []
        for idx, score in enumerate(similarities):
            if score >= min_score:
                results.append(SearchResult(
                    document=self.documents[idx],
                    score=float(score),
                    rank=0  # Will be set after sorting
                ))

        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)

        # Assign ranks
        for rank, result in enumerate(results[:top_k], start=1):
            result.rank = rank

        elapsed = time.time() - start_time
        logger.debug(f"Search completed in {elapsed*1000:.2f}ms")

        return results[:top_k]

    def get_stats(self) -> Dict[str, any]:
        """Get search engine statistics."""
        return {
            'model': self.model_name,
            'document_count': len(self.documents),
            'embedding_dimensions': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'cache_dir': str(self.cache_dir)
        }


def format_search_results(results: List[SearchResult], show_full_text: bool = False) -> str:
    """
    Format search results for display.

    Args:
        results: List of SearchResult objects
        show_full_text: Whether to show full document text

    Returns:
        Formatted string
    """
    if not results:
        return "No results found."

    output = []
    output.append(f"\n{'='*80}")
    output.append(f"Found {len(results)} results")
    output.append(f"{'='*80}\n")

    for result in results:
        # Header
        output.append(f"{result.rank}. Score: {result.score:.3f} {'█' * int(result.score * 40)}")
        output.append(f"   Source: {result.document.source_file}")
        output.append(f"   Chunk: {result.document.chunk_index}")

        # Preview (first 200 chars)
        text_preview = result.document.text[:200].replace('\n', ' ')
        if len(result.document.text) > 200:
            text_preview += "..."
        output.append(f"   Preview: {text_preview}")

        # Full text (if requested)
        if show_full_text:
            output.append("\n   Full text:")
            for line in result.document.text.split('\n'):
                output.append(f"   {line}")

        output.append("")

    return '\n'.join(output)


def interactive_mode(engine: SemanticSearchEngine):
    """Run interactive search mode."""
    print("\n" + "="*80)
    print("🔍 Neural Dojo Semantic Search - Interactive Mode")
    print("="*80)
    print("\nCommands:")
    print("  - Type your query to search")
    print("  - 'stats' to show engine statistics")
    print("  - 'quit' or 'exit' to exit")
    print("")

    while True:
        try:
            query = input("\n🔍 Query: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if query.lower() == 'stats':
                stats = engine.get_stats()
                print("\n📊 Engine Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue

            # Search
            start_time = time.time()
            results = engine.search(query, top_k=5)
            elapsed = time.time() - start_time

            # Display results
            print(format_search_results(results))
            print(f"⏱️  Search completed in {elapsed*1000:.2f}ms")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            continue


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Semantic Search Engine for Neural Dojo Documentation"
    )
    parser.add_argument(
        '--index',
        action='store_true',
        help='Index documentation (generate embeddings)'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Search query'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to return (default: 5)'
    )
    parser.add_argument(
        '--docs-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'docs' / 'curriculum',
        help='Path to documentation directory'
    )
    parser.add_argument(
        '--force-reindex',
        action='store_true',
        help='Force re-indexing even if cache exists'
    )
    parser.add_argument(
        '--full-text',
        action='store_true',
        help='Show full document text in results'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Sentence Transformer model name (default: all-MiniLM-L6-v2)'
    )

    args = parser.parse_args()

    # Validate docs directory
    if not args.docs_dir.exists():
        logger.error(f"Documentation directory not found: {args.docs_dir}")
        return

    # Initialize search engine
    engine = SemanticSearchEngine(model_name=args.model)

    # Load documents
    loader = DocumentLoader(args.docs_dir)
    documents = loader.load_all()

    if not documents:
        logger.error("No documents loaded!")
        return

    # Index documents
    if args.index or args.force_reindex:
        engine.index_documents(documents, force_reindex=args.force_reindex)
        print(f"\n✅ Indexed {len(documents)} document chunks")
        stats = engine.get_stats()
        print(f"📊 Model: {stats['model']}")
        print(f"📊 Embedding dimensions: {stats['embedding_dimensions']}")
        print(f"📊 Cache: {stats['cache_dir']}")
        return

    # Load existing embeddings
    engine.index_documents(documents, force_reindex=False)

    # Interactive mode
    if args.interactive:
        interactive_mode(engine)
        return

    # Single query mode
    if args.query:
        results = engine.search(args.query, top_k=args.top_k)
        print(format_search_results(results, show_full_text=args.full_text))
        return

    # No action specified
    parser.print_help()


if __name__ == '__main__':
    main()
