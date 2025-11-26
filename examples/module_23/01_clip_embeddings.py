#!/usr/bin/env python3
"""
Module 23 Example 01: CLIP Embeddings

Demonstrates CLIP (Contrastive Language-Image Pre-training):
- Image encoding to embeddings
- Text encoding to embeddings
- Zero-shot image classification
- Image-text similarity matching
- Semantic image search

Requirements:
    pip install transformers torch pillow numpy

Author: Neural Dojo
"""

import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

# Check for required packages
try:
    import torch
    from PIL import Image
except ImportError:
    print("Installing required packages...")
    os.system("pip install torch pillow")
    import torch
    from PIL import Image


@dataclass
class CLIPEmbedding:
    """Result from CLIP encoding."""
    embedding: np.ndarray
    source: str  # "image" or "text"
    input_data: str  # path or text


@dataclass
class SimilarityResult:
    """Result from similarity computation."""
    score: float
    label: str
    rank: int


class CLIPEncoder:
    """
    CLIP encoder for images and text.

    Uses HuggingFace transformers for easy model loading.
    Supports both local images and text encoding.
    """

    MODELS = {
        "base": "openai/clip-vit-base-patch32",      # 151M params
        "large": "openai/clip-vit-large-patch14",    # 428M params
        "huge": "laion/CLIP-ViT-H-14-laion2B-s32B-b79K",  # 986M params
    }

    def __init__(self, model_size: str = "base"):
        """
        Initialize CLIP encoder.

        Args:
            model_size: One of "base", "large", "huge"
        """
        if model_size not in self.MODELS:
            raise ValueError(f"Unknown model: {model_size}. Choose from: {list(self.MODELS.keys())}")

        self.model_name = self.MODELS[model_size]
        self.model_size = model_size
        self._model = None
        self._processor = None

        print(f"CLIP Encoder initialized (model: {model_size})")
        print(f"  Model: {self.model_name}")

    @property
    def model(self):
        """Lazy load model."""
        if self._model is None:
            self._load_model()
        return self._model

    @property
    def processor(self):
        """Lazy load processor."""
        if self._processor is None:
            self._load_model()
        return self._processor

    def _load_model(self):
        """Load CLIP model and processor."""
        try:
            from transformers import CLIPProcessor, CLIPModel

            print(f"Loading CLIP model: {self.model_name}...")
            self._model = CLIPModel.from_pretrained(self.model_name)
            self._processor = CLIPProcessor.from_pretrained(self.model_name)
            print("✅ Model loaded")

        except ImportError:
            print("⚠️ transformers not installed. Install with: pip install transformers")
            raise

    def encode_image(self, image_path: str) -> CLIPEmbedding:
        """
        Encode an image to CLIP embedding.

        Args:
            image_path: Path to image file

        Returns:
            CLIPEmbedding with normalized embedding vector
        """
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")

        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            # Normalize embedding
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return CLIPEmbedding(
            embedding=image_features.numpy()[0],
            source="image",
            input_data=image_path
        )

    def encode_text(self, text: str) -> CLIPEmbedding:
        """
        Encode text to CLIP embedding.

        Args:
            text: Text to encode

        Returns:
            CLIPEmbedding with normalized embedding vector
        """
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)

        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            # Normalize embedding
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return CLIPEmbedding(
            embedding=text_features.numpy()[0],
            source="text",
            input_data=text
        )

    def encode_texts(self, texts: List[str]) -> List[CLIPEmbedding]:
        """Encode multiple texts."""
        inputs = self.processor(text=texts, return_tensors="pt", padding=True)

        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        embeddings = []
        for i, text in enumerate(texts):
            embeddings.append(CLIPEmbedding(
                embedding=text_features.numpy()[i],
                source="text",
                input_data=text
            ))

        return embeddings

    def similarity(self, embedding1: CLIPEmbedding, embedding2: CLIPEmbedding) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0-1, higher = more similar)
        """
        # Dot product of normalized vectors = cosine similarity
        return float(np.dot(embedding1.embedding, embedding2.embedding))

    def zero_shot_classify(
        self,
        image_path: str,
        class_names: List[str],
        prompt_template: str = "a photo of a {}"
    ) -> List[SimilarityResult]:
        """
        Zero-shot image classification.

        Args:
            image_path: Path to image
            class_names: List of possible class names
            prompt_template: Template for class prompts (use {} for class name)

        Returns:
            List of SimilarityResult sorted by score (highest first)
        """
        # Encode image
        image_embedding = self.encode_image(image_path)

        # Create prompts for each class
        prompts = [prompt_template.format(name) for name in class_names]

        # Encode all prompts
        text_embeddings = self.encode_texts(prompts)

        # Compute similarities
        results = []
        for i, (name, text_emb) in enumerate(zip(class_names, text_embeddings)):
            score = self.similarity(image_embedding, text_emb)
            results.append(SimilarityResult(
                score=score,
                label=name,
                rank=0  # Will be set after sorting
            ))

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)

        # Set ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        return results


class CLIPImageSearch:
    """
    Semantic image search using CLIP embeddings.

    Index images and search using natural language queries.
    """

    def __init__(self, encoder: Optional[CLIPEncoder] = None):
        """
        Initialize image search.

        Args:
            encoder: CLIPEncoder instance (creates new if None)
        """
        self.encoder = encoder or CLIPEncoder()
        self.index: List[CLIPEmbedding] = []

    def add_image(self, image_path: str):
        """Add an image to the search index."""
        embedding = self.encoder.encode_image(image_path)
        self.index.append(embedding)
        print(f"  Indexed: {image_path}")

    def add_images(self, image_paths: List[str]):
        """Add multiple images to the index."""
        print(f"Indexing {len(image_paths)} images...")
        for path in image_paths:
            self.add_image(path)
        print(f"✅ Indexed {len(self.index)} images")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search images using natural language query.

        Args:
            query: Natural language search query
            top_k: Number of results to return

        Returns:
            List of (image_path, similarity_score) tuples
        """
        if not self.index:
            return []

        # Encode query
        query_embedding = self.encoder.encode_text(query)

        # Compute similarities
        results = []
        for img_embedding in self.index:
            score = self.encoder.similarity(query_embedding, img_embedding)
            results.append((img_embedding.input_data, score))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def clear(self):
        """Clear the search index."""
        self.index = []


def create_sample_images():
    """Create simple sample images for testing."""
    import numpy as np
    from PIL import Image
    import os

    os.makedirs("sample_images", exist_ok=True)

    samples = [
        ("sample_images/red_square.png", (255, 0, 0)),
        ("sample_images/green_circle.png", (0, 255, 0)),
        ("sample_images/blue_triangle.png", (0, 0, 255)),
        ("sample_images/yellow_star.png", (255, 255, 0)),
    ]

    for path, color in samples:
        img = Image.new("RGB", (224, 224), color)
        img.save(path)

    print(f"✅ Created {len(samples)} sample images in sample_images/")
    return [s[0] for s in samples]


def demo_basic_encoding():
    """Demo 1: Basic CLIP encoding."""
    print("=" * 60)
    print("DEMO 1: Basic CLIP Encoding")
    print("=" * 60)

    print("\n📋 CLIP Architecture:")
    print("   ┌─────────────┐    ┌─────────────┐")
    print("   │   Image     │    │    Text     │")
    print("   │  Encoder    │    │  Encoder    │")
    print("   │  (ViT)      │    │ (Transformer)│")
    print("   └──────┬──────┘    └──────┬──────┘")
    print("          │                  │")
    print("          ▼                  ▼")
    print("    Image Embedding    Text Embedding")
    print("       [512-dim]         [512-dim]")
    print("          │                  │")
    print("          └──────────────────┘")
    print("                   │")
    print("          Cosine Similarity")
    print()

    print("📊 Available CLIP Models:")
    for name, path in CLIPEncoder.MODELS.items():
        print(f"   {name:<8} {path}")
    print()

    # Simulated output (actual encoding requires model download)
    print("🔢 Embedding Properties:")
    print("   Dimension: 512 (base) / 768 (large)")
    print("   Normalized: L2 norm = 1.0")
    print("   Similarity: Dot product = Cosine similarity")
    print()


def demo_zero_shot():
    """Demo 2: Zero-shot classification."""
    print("=" * 60)
    print("DEMO 2: Zero-Shot Classification")
    print("=" * 60)

    print("\n🎯 How Zero-Shot Works:")
    print()
    print("   1. Create text prompts for each class:")
    print('      "a photo of a cat"')
    print('      "a photo of a dog"')
    print('      "a photo of a bird"')
    print()
    print("   2. Encode image and all prompts")
    print()
    print("   3. Find highest similarity:")
    print("      Image ← cosine_sim → Each prompt")
    print()
    print("   4. Predicted class = prompt with max similarity")
    print()

    # Simulated classification
    print("📊 Example Classification:")
    print()
    print("   Image: dog_photo.jpg")
    print("   Classes: [cat, dog, bird, fish]")
    print()
    print("   Results:")
    print("   ┌────────┬────────┬──────┐")
    print("   │ Rank   │ Class  │ Score│")
    print("   ├────────┼────────┼──────┤")
    print("   │   1    │ dog    │ 0.89 │")
    print("   │   2    │ cat    │ 0.42 │")
    print("   │   3    │ bird   │ 0.21 │")
    print("   │   4    │ fish   │ 0.08 │")
    print("   └────────┴────────┴──────┘")
    print()

    print("💡 Prompt Engineering Tips:")
    print('   - "a photo of a {}" - general images')
    print('   - "a satellite image of {}" - remote sensing')
    print('   - "a medical image of {}" - healthcare')
    print('   - "a {} in the style of anime" - styled content')
    print()


def demo_image_search():
    """Demo 3: Semantic image search."""
    print("=" * 60)
    print("DEMO 3: Semantic Image Search")
    print("=" * 60)

    print("\n🔍 How CLIP Search Works:")
    print()
    print("   Indexing Phase:")
    print("   ┌────────────────────────────────┐")
    print("   │  Images → CLIP → Embeddings   │")
    print("   │                                │")
    print("   │  img1.jpg → [0.12, 0.34, ...] │")
    print("   │  img2.jpg → [0.56, 0.78, ...] │")
    print("   │  img3.jpg → [0.91, 0.23, ...] │")
    print("   └────────────────────────────────┘")
    print()
    print("   Search Phase:")
    print("   ┌────────────────────────────────┐")
    print('   │  Query: "a sunset over ocean" │')
    print("   │           ↓                    │")
    print("   │      CLIP Text Encoder        │")
    print("   │           ↓                    │")
    print("   │   [0.45, 0.67, 0.12, ...]     │")
    print("   │           ↓                    │")
    print("   │   Compare with all images     │")
    print("   │           ↓                    │")
    print("   │   Return top-K matches        │")
    print("   └────────────────────────────────┘")
    print()

    print("📊 Example Search Results:")
    print()
    print('   Query: "cute pets playing"')
    print()
    print("   Results:")
    print("   ┌──────┬──────────────────┬───────┐")
    print("   │ Rank │ Image            │ Score │")
    print("   ├──────┼──────────────────┼───────┤")
    print("   │  1   │ puppies_park.jpg │ 0.87  │")
    print("   │  2   │ kittens_yarn.jpg │ 0.82  │")
    print("   │  3   │ dog_beach.jpg    │ 0.76  │")
    print("   │  4   │ cat_window.jpg   │ 0.71  │")
    print("   │  5   │ hamster.jpg      │ 0.65  │")
    print("   └──────┴──────────────────┴───────┘")
    print()


def demo_applications():
    """Demo 4: CLIP Applications."""
    print("=" * 60)
    print("DEMO 4: CLIP Applications")
    print("=" * 60)

    applications = [
        {
            "name": "Image Search Engines",
            "description": "Search millions of images with natural language",
            "examples": ["Unsplash", "Shutterstock", "Pinterest"]
        },
        {
            "name": "Content Moderation",
            "description": "Detect inappropriate content without explicit training",
            "examples": ["NSFW detection", "Violence detection", "Brand safety"]
        },
        {
            "name": "E-commerce",
            "description": "Search products by description or similar images",
            "examples": ["Visual search", "Product tagging", "Recommendations"]
        },
        {
            "name": "Image Generation",
            "description": "Guide generative models (DALL-E, Stable Diffusion)",
            "examples": ["CLIP-guided generation", "Style transfer", "Editing"]
        },
        {
            "name": "Medical Imaging",
            "description": "Zero-shot disease detection in medical scans",
            "examples": ["X-ray analysis", "Pathology", "Radiology"]
        },
        {
            "name": "Autonomous Systems",
            "description": "Robot vision and scene understanding",
            "examples": ["Object detection", "Scene classification", "Navigation"]
        }
    ]

    print("\n📋 CLIP Use Cases:\n")

    for app in applications:
        print(f"   🎯 {app['name']}")
        print(f"      {app['description']}")
        print(f"      Examples: {', '.join(app['examples'])}")
        print()

    print("💡 Why CLIP is Revolutionary:")
    print("   ✅ No task-specific training needed")
    print("   ✅ Works on any visual concept")
    print("   ✅ 400M image-text pairs training")
    print("   ✅ Unified vision-language embedding")
    print("   ✅ Powers DALL-E, Stable Diffusion, Midjourney")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 23: CLIP EMBEDDINGS")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "1":
            demo_basic_encoding()
        elif demo == "2":
            demo_zero_shot()
        elif demo == "3":
            demo_image_search()
        elif demo == "4":
            demo_applications()
        else:
            print(f"Unknown demo: {demo}")
            print("Usage: python 01_clip_embeddings.py [1|2|3|4]")
    else:
        demo_basic_encoding()
        demo_zero_shot()
        demo_image_search()
        demo_applications()

    print("=" * 60)
    print("✅ CLIP demos completed!")
    print("=" * 60)
    print("\n💡 To use with real images:")
    print("   pip install transformers torch")
    print("   encoder = CLIPEncoder()")
    print('   embedding = encoder.encode_image("photo.jpg")')
    print()


if __name__ == "__main__":
    main()
