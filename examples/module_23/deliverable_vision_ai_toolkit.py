#!/usr/bin/env python3
"""
Module 23 Deliverable: Vision AI Toolkit

A comprehensive toolkit for building vision-enabled AI applications:
- Multi-provider VLM support (OpenAI, Anthropic, simulated)
- CLIP-based image embeddings and search
- Visual Question Answering
- Document understanding and extraction
- Image comparison and analysis
- Caching and metrics tracking

Requirements:
    pip install openai anthropic pillow numpy

Author: Neural Dojo
"""

import os
import sys
import json
import time
import base64
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

# Check for required packages
try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Installing required packages...")
    os.system("pip install pillow numpy")
    from PIL import Image
    import numpy as np


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class VisionConfig:
    """Configuration for vision operations."""
    provider: str = "simulated"  # openai, anthropic, simulated
    model: str = "gpt-4o"
    max_tokens: int = 1000
    temperature: float = 0.0
    detail: str = "auto"  # auto, low, high (for OpenAI)


@dataclass
class VisionResult:
    """Result from a vision operation."""
    text: str
    provider: str
    model: str
    latency_ms: float
    tokens_used: int = 0
    cached: bool = False
    image_path: str = ""
    prompt: str = ""


@dataclass
class ImageEmbedding:
    """Image embedding result."""
    path: str
    embedding: np.ndarray
    model: str
    created_at: float = field(default_factory=time.time)


@dataclass
class SearchResult:
    """Image search result."""
    path: str
    score: float
    rank: int


@dataclass
class DocumentField:
    """Extracted document field."""
    name: str
    value: Any
    confidence: float


@dataclass
class DocumentExtract:
    """Document extraction result."""
    fields: List[DocumentField]
    raw_text: str
    document_type: str
    extraction_time_ms: float


@dataclass
class ComparisonResult:
    """Image comparison result."""
    similarities: List[str]
    differences: List[str]
    overall_similarity: str  # "high", "medium", "low"
    analysis: str


@dataclass
class MetricsSummary:
    """Metrics tracking."""
    total_analyses: int = 0
    total_extractions: int = 0
    total_searches: int = 0
    total_comparisons: int = 0
    avg_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0


# =============================================================================
# Vision Providers
# =============================================================================

class VisionProvider(ABC):
    """Abstract base class for vision providers."""

    @abstractmethod
    def analyze(self, image_path: str, prompt: str, config: VisionConfig) -> VisionResult:
        """Analyze an image with a prompt."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass


class SimulatedVisionProvider(VisionProvider):
    """Simulated vision provider for testing."""

    def analyze(self, image_path: str, prompt: str, config: VisionConfig) -> VisionResult:
        """Return simulated analysis."""
        time.sleep(0.1)  # Simulate latency

        # Generate contextual response based on prompt
        prompt_lower = prompt.lower()

        if "describe" in prompt_lower or "what" in prompt_lower:
            response = (
                f"[Simulated Analysis]\n"
                f"The image appears to show visual content. "
                f"Without actual vision capabilities, I can describe that this is an image file "
                f"located at: {image_path}"
            )
        elif "count" in prompt_lower:
            response = "[Simulated] I can see multiple elements in this image, but exact counting requires real vision."
        elif "extract" in prompt_lower or "text" in prompt_lower:
            response = '{"simulated": true, "message": "Text extraction requires real vision API"}'
        elif "compare" in prompt_lower:
            response = "[Simulated] Images appear to have both similarities and differences."
        else:
            response = f"[Simulated response to: {prompt[:50]}...]"

        return VisionResult(
            text=response,
            provider="simulated",
            model="simulated-v1",
            latency_ms=100,
            image_path=image_path,
            prompt=prompt
        )

    def get_name(self) -> str:
        return "simulated"


class OpenAIVisionProvider(VisionProvider):
    """OpenAI GPT-4V / GPT-4o vision provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass

    def encode_image(self, image_path: str) -> Tuple[str, str]:
        """Encode image to base64 and determine media type."""
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = Path(image_path).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type = media_types.get(ext, "image/jpeg")

        return data, media_type

    def analyze(self, image_path: str, prompt: str, config: VisionConfig) -> VisionResult:
        """Analyze image with GPT-4V."""
        if not self.client:
            return SimulatedVisionProvider().analyze(image_path, prompt, config)

        start_time = time.time()

        image_data, media_type = self.encode_image(image_path)

        response = self.client.chat.completions.create(
            model=config.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}",
                                "detail": config.detail
                            }
                        }
                    ]
                }
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        latency = (time.time() - start_time) * 1000

        return VisionResult(
            text=response.choices[0].message.content,
            provider="openai",
            model=config.model,
            latency_ms=latency,
            tokens_used=response.usage.total_tokens if response.usage else 0,
            image_path=image_path,
            prompt=prompt
        )

    def get_name(self) -> str:
        return "openai"


class AnthropicVisionProvider(VisionProvider):
    """Anthropic Claude 3 vision provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                pass

    def encode_image(self, image_path: str) -> Tuple[str, str]:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = Path(image_path).suffix.lower()
        media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif"}
        media_type = media_types.get(ext, "image/jpeg")

        return data, media_type

    def analyze(self, image_path: str, prompt: str, config: VisionConfig) -> VisionResult:
        """Analyze image with Claude Vision."""
        if not self.client:
            return SimulatedVisionProvider().analyze(image_path, prompt, config)

        start_time = time.time()

        image_data, media_type = self.encode_image(image_path)

        response = self.client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        )

        latency = (time.time() - start_time) * 1000

        return VisionResult(
            text=response.content[0].text,
            provider="anthropic",
            model=config.model,
            latency_ms=latency,
            tokens_used=(response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0,
            image_path=image_path,
            prompt=prompt
        )

    def get_name(self) -> str:
        return "anthropic"


# =============================================================================
# Vision Cache
# =============================================================================

class VisionCache:
    """Cache for vision results."""

    def __init__(self, cache_dir: str = ".vision_toolkit"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.index_path = self.cache_dir / "cache_index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load cache index."""
        if self.index_path.exists():
            with open(self.index_path) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        """Save cache index."""
        with open(self.index_path, "w") as f:
            json.dump(self.index, f, indent=2)

    def _cache_key(self, image_path: str, prompt: str, provider: str) -> str:
        """Generate cache key."""
        # Include image hash for same path but different content
        try:
            with open(image_path, "rb") as f:
                image_hash = hashlib.md5(f.read()).hexdigest()[:8]
        except:
            image_hash = "unknown"

        content = f"{image_path}:{image_hash}:{prompt}:{provider}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, image_path: str, prompt: str, provider: str) -> Optional[VisionResult]:
        """Get cached result."""
        key = self._cache_key(image_path, prompt, provider)

        if key in self.index:
            entry = self.index[key]
            return VisionResult(
                text=entry["text"],
                provider=entry["provider"],
                model=entry["model"],
                latency_ms=0,
                tokens_used=entry.get("tokens_used", 0),
                cached=True,
                image_path=image_path,
                prompt=prompt
            )
        return None

    def put(self, result: VisionResult):
        """Cache a result."""
        key = self._cache_key(result.image_path, result.prompt, result.provider)

        self.index[key] = {
            "text": result.text,
            "provider": result.provider,
            "model": result.model,
            "tokens_used": result.tokens_used,
            "cached_at": time.time()
        }
        self._save_index()

    def clear(self):
        """Clear cache."""
        self.index = {}
        self._save_index()


# =============================================================================
# Image Search (CLIP-based)
# =============================================================================

class ImageSearch:
    """CLIP-based semantic image search."""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self._model = None
        self._processor = None
        self.index: List[ImageEmbedding] = []

    @property
    def model(self):
        """Lazy load CLIP model."""
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
        """Load CLIP model."""
        try:
            from transformers import CLIPProcessor, CLIPModel
            import torch

            self._model = CLIPModel.from_pretrained(self.model_name)
            self._processor = CLIPProcessor.from_pretrained(self.model_name)
            print(f"✅ CLIP model loaded: {self.model_name}")
        except ImportError:
            print("⚠️ transformers not available. Using simulated embeddings.")
            self._model = "simulated"
            self._processor = "simulated"

    def add_image(self, image_path: str) -> ImageEmbedding:
        """Add image to search index."""
        if self._model == "simulated" or self._processor == "simulated":
            # Generate random embedding for simulation
            embedding = np.random.randn(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
        else:
            import torch

            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")

            with torch.no_grad():
                features = self.model.get_image_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
                embedding = features.numpy()[0]

        img_embedding = ImageEmbedding(
            path=image_path,
            embedding=embedding,
            model=self.model_name
        )
        self.index.append(img_embedding)
        return img_embedding

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search images with text query."""
        if not self.index:
            return []

        if self._model == "simulated" or self._processor == "simulated":
            # Simulated search
            results = []
            for i, img_emb in enumerate(self.index[:top_k]):
                results.append(SearchResult(
                    path=img_emb.path,
                    score=0.9 - (i * 0.1),
                    rank=i + 1
                ))
            return results

        import torch

        inputs = self.processor(text=[query], return_tensors="pt", padding=True)

        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            query_embedding = text_features.numpy()[0]

        # Compute similarities
        results = []
        for img_emb in self.index:
            score = float(np.dot(query_embedding, img_emb.embedding))
            results.append((img_emb.path, score))

        # Sort and rank
        results.sort(key=lambda x: x[1], reverse=True)

        return [
            SearchResult(path=path, score=score, rank=i+1)
            for i, (path, score) in enumerate(results[:top_k])
        ]

    def clear(self):
        """Clear search index."""
        self.index = []


# =============================================================================
# Vision AI Toolkit
# =============================================================================

class VisionAIToolkit:
    """
    Comprehensive Vision AI Toolkit.

    Features:
    - Multi-provider VLM support
    - Image analysis and description
    - Visual Question Answering
    - Document extraction
    - Image comparison
    - CLIP-based image search
    - Caching and metrics
    """

    def __init__(
        self,
        provider: str = "simulated",
        enable_cache: bool = True,
        cache_dir: str = ".vision_toolkit"
    ):
        """
        Initialize Vision AI Toolkit.

        Args:
            provider: Vision provider ("openai", "anthropic", "simulated")
            enable_cache: Enable response caching
            cache_dir: Cache directory path
        """
        self.provider_name = provider
        self.enable_cache = enable_cache
        self.cache_dir = cache_dir

        # Initialize provider
        self.provider = self._create_provider(provider)

        # Initialize cache
        self.cache = VisionCache(cache_dir) if enable_cache else None

        # Initialize image search (lazy loaded)
        self._image_search = None

        # Initialize metrics
        self.metrics = MetricsSummary()
        self._latencies: List[float] = []

        # Storage path
        self.storage_path = Path(cache_dir)
        self.storage_path.mkdir(exist_ok=True)

        print(f"🔍 Vision AI Toolkit initialized")
        print(f"   Provider: {provider}")
        print(f"   Cache: {'enabled' if enable_cache else 'disabled'}")
        print()

    def _create_provider(self, name: str) -> VisionProvider:
        """Create vision provider."""
        providers = {
            "openai": OpenAIVisionProvider,
            "anthropic": AnthropicVisionProvider,
            "simulated": SimulatedVisionProvider
        }

        provider_class = providers.get(name, SimulatedVisionProvider)
        return provider_class()

    @property
    def image_search(self) -> ImageSearch:
        """Get image search (lazy loaded)."""
        if self._image_search is None:
            self._image_search = ImageSearch()
        return self._image_search

    def _track_latency(self, latency_ms: float):
        """Track latency for metrics."""
        self._latencies.append(latency_ms)
        self.metrics.avg_latency_ms = sum(self._latencies) / len(self._latencies)

    # -------------------------------------------------------------------------
    # Core Vision Operations
    # -------------------------------------------------------------------------

    def analyze(
        self,
        image_path: str,
        prompt: str,
        config: Optional[VisionConfig] = None
    ) -> VisionResult:
        """
        Analyze an image with a prompt.

        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            config: Optional vision config

        Returns:
            VisionResult with analysis
        """
        config = config or VisionConfig(provider=self.provider_name)

        # Check cache
        if self.cache:
            cached = self.cache.get(image_path, prompt, self.provider_name)
            if cached:
                self.metrics.cache_hits += 1
                return cached
            self.metrics.cache_misses += 1

        # Analyze
        try:
            result = self.provider.analyze(image_path, prompt, config)
            self.metrics.total_analyses += 1
            self._track_latency(result.latency_ms)

            # Cache result
            if self.cache:
                self.cache.put(result)

            return result

        except Exception as e:
            self.metrics.errors += 1
            raise

    def describe(self, image_path: str) -> VisionResult:
        """Get a detailed description of an image."""
        prompt = "Describe this image in detail. Include objects, colors, composition, and any notable elements."
        return self.analyze(image_path, prompt)

    def ask(self, image_path: str, question: str) -> VisionResult:
        """Ask a question about an image (Visual QA)."""
        prompt = f"Look at this image carefully and answer the following question:\n{question}"
        return self.analyze(image_path, prompt)

    # -------------------------------------------------------------------------
    # Document Understanding
    # -------------------------------------------------------------------------

    def extract_text(self, image_path: str) -> str:
        """Extract all text from an image (OCR)."""
        prompt = "Extract all visible text from this image. Return only the text, preserving layout."
        result = self.analyze(image_path, prompt)
        return result.text

    def extract_document(
        self,
        image_path: str,
        document_type: str = "invoice"
    ) -> DocumentExtract:
        """
        Extract structured data from a document.

        Args:
            image_path: Path to document image
            document_type: Type of document ("invoice", "receipt", "form", "business_card")

        Returns:
            DocumentExtract with structured fields
        """
        start_time = time.time()

        prompts = {
            "invoice": """Extract from this invoice and return as JSON:
                {"invoice_number": str, "date": str, "vendor": str, "items": [{"description": str, "quantity": num, "price": num}], "subtotal": num, "tax": num, "total": num}
                Return ONLY valid JSON.""",
            "receipt": """Extract from this receipt and return as JSON:
                {"store": str, "date": str, "items": [{"name": str, "price": num}], "subtotal": num, "tax": num, "total": num}
                Return ONLY valid JSON.""",
            "form": """Extract all filled fields from this form as JSON:
                {"fields": [{"label": str, "value": str}]}
                Return ONLY valid JSON.""",
            "business_card": """Extract from this business card as JSON:
                {"name": str, "title": str, "company": str, "email": str, "phone": str, "address": str}
                Return ONLY valid JSON."""
        }

        prompt = prompts.get(document_type, prompts["invoice"])
        result = self.analyze(image_path, prompt)

        # Parse response
        fields = []
        text = result.text

        try:
            # Clean JSON from markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())

            # Convert to DocumentField list
            for key, value in data.items():
                if value is not None:
                    fields.append(DocumentField(
                        name=key,
                        value=value,
                        confidence=0.9
                    ))
        except json.JSONDecodeError:
            fields.append(DocumentField(
                name="raw_text",
                value=text,
                confidence=0.5
            ))

        self.metrics.total_extractions += 1
        extraction_time = (time.time() - start_time) * 1000

        return DocumentExtract(
            fields=fields,
            raw_text=result.text,
            document_type=document_type,
            extraction_time_ms=extraction_time
        )

    # -------------------------------------------------------------------------
    # Image Comparison
    # -------------------------------------------------------------------------

    def compare_images(
        self,
        image_path1: str,
        image_path2: str,
        aspect: str = "general"
    ) -> ComparisonResult:
        """
        Compare two images.

        Args:
            image_path1: First image path
            image_path2: Second image path
            aspect: Comparison aspect ("general", "quality", "content", "differences")

        Returns:
            ComparisonResult with analysis
        """
        self.metrics.total_comparisons += 1

        # For providers that don't support multi-image, analyze separately
        if self.provider_name == "simulated":
            return ComparisonResult(
                similarities=["Both are images", "Similar format"],
                differences=["Content may vary", "Details differ"],
                overall_similarity="medium",
                analysis="[Simulated comparison] Images appear to have some similarities and differences."
            )

        # Build comparison prompt
        prompts = {
            "general": "Compare these two images. List 3 similarities and 3 differences.",
            "quality": "Compare the quality of these images (resolution, clarity, lighting).",
            "content": "Compare what's shown in these images - subjects, objects, scenes.",
            "differences": "List every difference you can find between these images."
        }

        prompt = prompts.get(aspect, prompts["general"]) + "\nFormat: SIMILARITIES: [...], DIFFERENCES: [...], OVERALL: [high/medium/low similarity]"

        # For OpenAI, can send multiple images
        if self.provider_name == "openai" and hasattr(self.provider, 'client') and self.provider.client:
            from openai import OpenAI

            img1_data, media1 = self.provider.encode_image(image_path1)
            img2_data, media2 = self.provider.encode_image(image_path2)

            response = self.provider.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{media1};base64,{img1_data}"}},
                            {"type": "image_url", "image_url": {"url": f"data:{media2};base64,{img2_data}"}}
                        ]
                    }
                ],
                max_tokens=500
            )

            analysis = response.choices[0].message.content
        else:
            # Fallback: analyze each separately
            result1 = self.describe(image_path1)
            result2 = self.describe(image_path2)
            analysis = f"Image 1: {result1.text[:200]}...\n\nImage 2: {result2.text[:200]}..."

        return ComparisonResult(
            similarities=["Extracted from analysis"],
            differences=["Extracted from analysis"],
            overall_similarity="medium",
            analysis=analysis
        )

    # -------------------------------------------------------------------------
    # Image Search
    # -------------------------------------------------------------------------

    def index_image(self, image_path: str) -> ImageEmbedding:
        """Add image to search index."""
        return self.image_search.add_image(image_path)

    def index_images(self, image_paths: List[str]) -> List[ImageEmbedding]:
        """Add multiple images to search index."""
        print(f"Indexing {len(image_paths)} images...")
        embeddings = []
        for path in image_paths:
            emb = self.image_search.add_image(path)
            embeddings.append(emb)
            print(f"  ✅ {path}")
        return embeddings

    def search_images(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search indexed images with text query."""
        self.metrics.total_searches += 1
        return self.image_search.search(query, top_k)

    # -------------------------------------------------------------------------
    # Metrics and State
    # -------------------------------------------------------------------------

    def get_metrics_summary(self) -> str:
        """Get formatted metrics summary."""
        cache_total = self.metrics.cache_hits + self.metrics.cache_misses
        hit_rate = (self.metrics.cache_hits / cache_total * 100) if cache_total > 0 else 0

        return f"""
Vision AI Toolkit Metrics
{'=' * 40}

Analyses:
   Total: {self.metrics.total_analyses}
   Avg Latency: {self.metrics.avg_latency_ms:.1f}ms

Document Extractions: {self.metrics.total_extractions}
Image Searches: {self.metrics.total_searches}
Image Comparisons: {self.metrics.total_comparisons}

Cache:
   Hits: {self.metrics.cache_hits}
   Misses: {self.metrics.cache_misses}
   Hit Rate: {hit_rate:.1f}%

Errors: {self.metrics.errors}
"""

    def save_state(self):
        """Save toolkit state."""
        state = {
            "metrics": asdict(self.metrics),
            "provider": self.provider_name,
            "indexed_images": [e.path for e in self.image_search.index] if self._image_search else [],
            "saved_at": datetime.now().isoformat()
        }

        state_path = self.storage_path / "state.json"
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        print(f"💾 State saved to {state_path}")

    def clear_cache(self):
        """Clear vision cache."""
        if self.cache:
            self.cache.clear()
            print("🧹 Cache cleared")


# =============================================================================
# Demo Functions
# =============================================================================

def demo_image_analysis():
    """Demo 1: Image analysis and description."""
    print("=" * 60)
    print("DEMO 1: Image Analysis")
    print("=" * 60)

    toolkit = VisionAIToolkit(provider="simulated")

    print("\n📋 Vision Analysis Pipeline:\n")
    print("   ┌─────────────────────────────────────┐")
    print("   │           Input Image               │")
    print("   └───────────────┬─────────────────────┘")
    print("                   │")
    print("                   ▼")
    print("   ┌─────────────────────────────────────┐")
    print("   │       Vision AI Toolkit            │")
    print("   │  • OpenAI GPT-4V                    │")
    print("   │  • Anthropic Claude Vision          │")
    print("   │  • Simulated (testing)              │")
    print("   └───────────────┬─────────────────────┘")
    print("                   │")
    print("                   ▼")
    print("   ┌─────────────────────────────────────┐")
    print("   │       Analysis Result               │")
    print("   │  • Description                      │")
    print("   │  • Objects detected                 │")
    print("   │  • Text extracted                   │")
    print("   └─────────────────────────────────────┘")
    print()

    print("🔧 Available Methods:")
    print("   toolkit.analyze(image, prompt)  - Custom analysis")
    print("   toolkit.describe(image)         - Get description")
    print("   toolkit.ask(image, question)    - Visual QA")
    print("   toolkit.extract_text(image)     - OCR")
    print()


def demo_document_extraction():
    """Demo 2: Document understanding."""
    print("=" * 60)
    print("DEMO 2: Document Extraction")
    print("=" * 60)

    toolkit = VisionAIToolkit(provider="simulated")

    print("\n📄 Supported Document Types:\n")

    doc_types = [
        ("invoice", ["invoice_number", "date", "vendor", "items", "total"]),
        ("receipt", ["store", "date", "items", "total"]),
        ("form", ["field labels", "field values", "checkboxes"]),
        ("business_card", ["name", "title", "company", "email", "phone"])
    ]

    for doc_type, fields in doc_types:
        print(f"   📑 {doc_type.title()}")
        print(f"      Fields: {', '.join(fields)}")
        print()

    print("📝 Example Usage:")
    print('   result = toolkit.extract_document("invoice.jpg", "invoice")')
    print('   for field in result.fields:')
    print('       print(f"{field.name}: {field.value}")')
    print()


def demo_image_search():
    """Demo 3: CLIP-based image search."""
    print("=" * 60)
    print("DEMO 3: Semantic Image Search")
    print("=" * 60)

    toolkit = VisionAIToolkit(provider="simulated")

    print("\n🔍 CLIP Image Search Pipeline:\n")
    print("   Indexing:")
    print("   ┌─────────────────────────────────────┐")
    print("   │  Images → CLIP Encoder → Embeddings │")
    print("   │                                      │")
    print("   │  [img1] → [0.12, 0.34, ...]         │")
    print("   │  [img2] → [0.56, 0.78, ...]         │")
    print("   │  [img3] → [0.91, 0.23, ...]         │")
    print("   └─────────────────────────────────────┘")
    print()
    print("   Searching:")
    print("   ┌─────────────────────────────────────┐")
    print('   │  Query: "sunset over mountains"     │')
    print("   │            ↓                        │")
    print("   │  CLIP Text Encoder                  │")
    print("   │            ↓                        │")
    print("   │  Compare with indexed images        │")
    print("   │            ↓                        │")
    print("   │  Return ranked results              │")
    print("   └─────────────────────────────────────┘")
    print()

    print("📝 Example Usage:")
    print('   toolkit.index_images(["img1.jpg", "img2.jpg", "img3.jpg"])')
    print('   results = toolkit.search_images("cute animals playing")')
    print('   for r in results:')
    print('       print(f"{r.rank}. {r.path} (score: {r.score:.2f})")')
    print()


def demo_metrics():
    """Demo 4: Metrics and monitoring."""
    print("=" * 60)
    print("DEMO 4: Metrics Dashboard")
    print("=" * 60)

    toolkit = VisionAIToolkit(provider="simulated")

    # Simulate some activity
    print("\n⏳ Simulating toolkit activity...")

    # Fake some metrics
    toolkit.metrics.total_analyses = 15
    toolkit.metrics.total_extractions = 5
    toolkit.metrics.total_searches = 8
    toolkit.metrics.total_comparisons = 3
    toolkit.metrics.cache_hits = 7
    toolkit.metrics.cache_misses = 8
    toolkit.metrics.avg_latency_ms = 234.5

    print(toolkit.get_metrics_summary())

    # Save state
    toolkit.save_state()


def main():
    """Run demos."""
    print("\n" + "=" * 60)
    print("MODULE 23 DELIVERABLE: VISION AI TOOLKIT")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "demo1":
            demo_image_analysis()
        elif demo == "demo2":
            demo_document_extraction()
        elif demo == "demo3":
            demo_image_search()
        elif demo == "demo4":
            demo_metrics()
        else:
            print(f"Unknown demo: {demo}")
            print("Available: demo1, demo2, demo3, demo4")
    else:
        print("Usage: python deliverable_vision_ai_toolkit.py <demo>\n")
        print("Demos:")
        print("  demo1  - Image analysis")
        print("  demo2  - Document extraction")
        print("  demo3  - Semantic image search")
        print("  demo4  - Metrics dashboard")
        print("\nRunning all demos...\n")

        demo_image_analysis()
        demo_document_extraction()
        demo_image_search()
        demo_metrics()

    print("=" * 60)
    print("✅ Vision AI Toolkit demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
