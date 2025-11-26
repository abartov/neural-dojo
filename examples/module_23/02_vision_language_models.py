#!/usr/bin/env python3
"""
Module 23 Example 02: Vision-Language Models (VLMs)

Demonstrates multi-provider vision-language capabilities:
- OpenAI GPT-4V / GPT-4o
- Anthropic Claude 3 Vision
- Google Gemini Vision
- Image analysis and description
- Document understanding

Requirements:
    pip install openai anthropic google-generativeai pillow

Author: Neural Dojo
"""

import os
import sys
import base64
import time
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
from abc import ABC, abstractmethod

# Check for PIL
try:
    from PIL import Image
except ImportError:
    print("Installing pillow...")
    os.system("pip install pillow")
    from PIL import Image


@dataclass
class VisionResponse:
    """Response from a vision model."""
    text: str
    model: str
    provider: str
    latency_ms: float
    tokens_used: int = 0


class VisionProvider(ABC):
    """Abstract base class for vision providers."""

    @abstractmethod
    def analyze(self, image_path: str, prompt: str) -> VisionResponse:
        """Analyze an image with a prompt."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models."""
        pass


class OpenAIVision(VisionProvider):
    """
    OpenAI Vision Provider (GPT-4V, GPT-4o).

    Supports image analysis, OCR, diagram understanding.
    """

    MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize OpenAI Vision."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print(f"✅ OpenAI Vision initialized (model: {model})")
            except ImportError:
                print("⚠️ openai package not installed")
                self.client = None
        else:
            print("⚠️ OPENAI_API_KEY not set - using simulated mode")
            self.client = None

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def analyze(self, image_path: str, prompt: str) -> VisionResponse:
        """Analyze image with GPT-4V."""
        start_time = time.time()

        if not self.client:
            # Simulated response
            return VisionResponse(
                text=f"[Simulated GPT-4V response for: {prompt}]\n"
                     f"This image appears to show various visual elements. "
                     f"Without API access, I cannot provide detailed analysis.",
                model=self.model,
                provider="openai",
                latency_ms=100
            )

        # Encode image
        image_data = self.encode_image(image_path)
        media_type = "image/jpeg" if image_path.lower().endswith(".jpg") else "image/png"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        latency = (time.time() - start_time) * 1000

        return VisionResponse(
            text=response.choices[0].message.content,
            model=self.model,
            provider="openai",
            latency_ms=latency,
            tokens_used=response.usage.total_tokens if response.usage else 0
        )

    def list_models(self) -> List[str]:
        return self.MODELS.copy()


class AnthropicVision(VisionProvider):
    """
    Anthropic Claude Vision Provider.

    Supports detailed analysis, safety, chart interpretation.
    """

    MODELS = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """Initialize Anthropic Vision."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print(f"✅ Claude Vision initialized (model: {model.split('-')[2]})")
            except ImportError:
                print("⚠️ anthropic package not installed")
                self.client = None
        else:
            print("⚠️ ANTHROPIC_API_KEY not set - using simulated mode")
            self.client = None

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def analyze(self, image_path: str, prompt: str) -> VisionResponse:
        """Analyze image with Claude Vision."""
        start_time = time.time()

        if not self.client:
            return VisionResponse(
                text=f"[Simulated Claude response for: {prompt}]\n"
                     f"Based on the image, I can observe several elements. "
                     f"Without API access, detailed analysis is unavailable.",
                model=self.model,
                provider="anthropic",
                latency_ms=100
            )

        image_data = self.encode_image(image_path)
        media_type = "image/jpeg" if image_path.lower().endswith(".jpg") else "image/png"

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
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
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        latency = (time.time() - start_time) * 1000

        return VisionResponse(
            text=response.content[0].text,
            model=self.model,
            provider="anthropic",
            latency_ms=latency,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else 0
        )

    def list_models(self) -> List[str]:
        return self.MODELS.copy()


class GeminiVision(VisionProvider):
    """
    Google Gemini Vision Provider.

    Native multimodal, video support, long context.
    """

    MODELS = ["gemini-pro-vision", "gemini-1.5-pro"]

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro-vision"):
        """Initialize Gemini Vision."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.genai = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                self.client = genai.GenerativeModel(model)
                print(f"✅ Gemini Vision initialized (model: {model})")
            except ImportError:
                print("⚠️ google-generativeai package not installed")
        else:
            print("⚠️ GOOGLE_API_KEY not set - using simulated mode")

    def analyze(self, image_path: str, prompt: str) -> VisionResponse:
        """Analyze image with Gemini Vision."""
        start_time = time.time()

        if not self.genai:
            return VisionResponse(
                text=f"[Simulated Gemini response for: {prompt}]\n"
                     f"The image contains visual content that I would analyze. "
                     f"Without API access, I cannot provide specific details.",
                model=self.model,
                provider="google",
                latency_ms=100
            )

        image = Image.open(image_path)
        response = self.client.generate_content([prompt, image])

        latency = (time.time() - start_time) * 1000

        return VisionResponse(
            text=response.text,
            model=self.model,
            provider="google",
            latency_ms=latency
        )

    def list_models(self) -> List[str]:
        return self.MODELS.copy()


class VisionModelComparator:
    """Compare responses from multiple vision providers."""

    def __init__(self):
        self.providers = {}

    def add_provider(self, name: str, provider: VisionProvider):
        """Add a provider for comparison."""
        self.providers[name] = provider

    def compare(self, image_path: str, prompt: str) -> dict:
        """Get responses from all providers."""
        results = {}

        for name, provider in self.providers.items():
            try:
                response = provider.analyze(image_path, prompt)
                results[name] = {
                    "success": True,
                    "response": response
                }
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": str(e)
                }

        return results


def demo_provider_overview():
    """Demo 1: Vision provider overview."""
    print("=" * 60)
    print("DEMO 1: Vision Language Model Providers")
    print("=" * 60)

    providers = [
        {
            "name": "GPT-4V / GPT-4o",
            "company": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "strengths": ["General reasoning", "OCR", "Multi-image"],
            "context": "128K tokens"
        },
        {
            "name": "Claude 3 Vision",
            "company": "Anthropic",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "strengths": ["Detailed analysis", "Safety", "Charts/graphs"],
            "context": "200K tokens"
        },
        {
            "name": "Gemini Vision",
            "company": "Google",
            "models": ["gemini-pro-vision", "gemini-1.5-pro"],
            "strengths": ["Native multimodal", "Video", "Long context"],
            "context": "1M tokens (1.5 Pro)"
        },
        {
            "name": "LLaVA",
            "company": "Open Source",
            "models": ["llava-7b", "llava-13b", "llava-34b"],
            "strengths": ["Local deployment", "Customizable", "Free"],
            "context": "Varies by base model"
        }
    ]

    print("\n📋 Vision Language Model Comparison:\n")

    for p in providers:
        print(f"   🔹 {p['name']} ({p['company']})")
        print(f"      Models: {', '.join(p['models'])}")
        print(f"      Strengths: {', '.join(p['strengths'])}")
        print(f"      Context: {p['context']}")
        print()

    print("💡 Key Differences:")
    print("   • GPT-4o: Best general purpose, fast")
    print("   • Claude 3: Best for detailed analysis, safest")
    print("   • Gemini: Best for video, longest context")
    print("   • LLaVA: Best for local/private deployment")
    print()


def demo_vlm_architecture():
    """Demo 2: VLM architecture explanation."""
    print("=" * 60)
    print("DEMO 2: VLM Architecture")
    print("=" * 60)

    print("\n📊 Vision-Language Model Architecture:\n")

    print("   ┌─────────────────────────────────────────┐")
    print("   │              Input Image                │")
    print("   └────────────────────┬────────────────────┘")
    print("                        │")
    print("                        ▼")
    print("   ┌─────────────────────────────────────────┐")
    print("   │          Vision Encoder (ViT)          │")
    print("   │    • Splits image into patches         │")
    print("   │    • Creates visual embeddings         │")
    print("   └────────────────────┬────────────────────┘")
    print("                        │")
    print("                        ▼")
    print("   ┌─────────────────────────────────────────┐")
    print("   │        Projection Layer / Adapter       │")
    print("   │    • Maps visual to language space     │")
    print("   │    • Q-Former, Linear, Cross-attention │")
    print("   └────────────────────┬────────────────────┘")
    print("                        │")
    print("                        ▼")
    print("   ┌─────────────────────────────────────────┐")
    print("   │          [Visual Tokens]    [Text]     │")
    print("   │                                         │")
    print("   │        Large Language Model            │")
    print("   │         (GPT-4, Claude, Llama)         │")
    print("   └────────────────────┬────────────────────┘")
    print("                        │")
    print("                        ▼")
    print("   ┌─────────────────────────────────────────┐")
    print("   │           Generated Response           │")
    print("   └─────────────────────────────────────────┘")
    print()

    print("🔑 Key Architectural Choices:\n")

    choices = [
        ("Vision Encoder", "ViT-L/14 (CLIP), SigLIP, EVA-CLIP"),
        ("Connector", "Linear projection, Q-Former, Cross-attention"),
        ("LLM Backbone", "GPT-4, Claude, Llama, Vicuna"),
        ("Training", "Frozen encoders + trained connector, or end-to-end")
    ]

    for component, options in choices:
        print(f"   {component}:")
        print(f"      Options: {options}")
        print()


def demo_prompting_techniques():
    """Demo 3: Vision prompting techniques."""
    print("=" * 60)
    print("DEMO 3: Vision Prompting Techniques")
    print("=" * 60)

    techniques = [
        {
            "name": "Simple Description",
            "prompt": "What's in this image?",
            "use_case": "Quick overview, caption generation"
        },
        {
            "name": "Detailed Analysis",
            "prompt": "Describe this image in detail, including objects, colors, composition, and mood.",
            "use_case": "Thorough documentation"
        },
        {
            "name": "Expert Persona",
            "prompt": "As an art historian, analyze the composition, technique, and historical context of this painting.",
            "use_case": "Domain-specific analysis"
        },
        {
            "name": "Chain-of-Thought",
            "prompt": "Look at this math problem. First identify the type of problem, then list the given information, then solve step by step.",
            "use_case": "Complex reasoning tasks"
        },
        {
            "name": "Structured Output",
            "prompt": "Extract all text from this receipt and return as JSON with fields: store, date, items[], total.",
            "use_case": "Data extraction, OCR"
        },
        {
            "name": "Comparison",
            "prompt": "Compare these two images. List similarities and differences.",
            "use_case": "Product comparison, change detection"
        },
        {
            "name": "Counting",
            "prompt": "Count all the people in this image. Explain your counting method.",
            "use_case": "Quantitative analysis"
        }
    ]

    print("\n📝 Vision Prompting Techniques:\n")

    for i, t in enumerate(techniques, 1):
        print(f"   {i}. {t['name']}")
        print(f"      Prompt: \"{t['prompt']}\"")
        print(f"      Use case: {t['use_case']}")
        print()

    print("💡 Pro Tips:")
    print("   • Be specific about what you want to know")
    print("   • Use structured prompts for structured output")
    print("   • Chain-of-thought improves reasoning accuracy")
    print("   • Ask for confidence when uncertain")
    print("   • Multi-image: \"Compare image 1 with image 2\"")
    print()


def demo_use_cases():
    """Demo 4: Real-world use cases."""
    print("=" * 60)
    print("DEMO 4: VLM Use Cases")
    print("=" * 60)

    use_cases = [
        {
            "category": "Document Understanding",
            "examples": [
                "Invoice/receipt data extraction",
                "Form processing and digitization",
                "Contract analysis",
                "Handwritten note transcription"
            ]
        },
        {
            "category": "Visual QA",
            "examples": [
                "Product identification",
                "Diagram explanation",
                "UI/UX analysis",
                "Medical image interpretation"
            ]
        },
        {
            "category": "Content Creation",
            "examples": [
                "Image captioning for accessibility",
                "Social media post generation",
                "Product description writing",
                "Alt-text generation"
            ]
        },
        {
            "category": "Analysis & Monitoring",
            "examples": [
                "Security camera analysis",
                "Quality control inspection",
                "Environmental monitoring",
                "Traffic analysis"
            ]
        },
        {
            "category": "Creative Applications",
            "examples": [
                "Art analysis and critique",
                "Style identification",
                "Visual storytelling",
                "Meme explanation"
            ]
        }
    ]

    print("\n🎯 VLM Real-World Applications:\n")

    for uc in use_cases:
        print(f"   📂 {uc['category']}")
        for example in uc['examples']:
            print(f"      • {example}")
        print()

    print("📊 Production Considerations:")
    print("   • Cost: Vision calls are 2-10x more expensive than text")
    print("   • Latency: Expect 1-5 seconds per image")
    print("   • Accuracy: Always validate critical extractions")
    print("   • Privacy: Consider local models for sensitive images")
    print("   • Rate limits: Plan for API quotas")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 23: VISION-LANGUAGE MODELS")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "1":
            demo_provider_overview()
        elif demo == "2":
            demo_vlm_architecture()
        elif demo == "3":
            demo_prompting_techniques()
        elif demo == "4":
            demo_use_cases()
        else:
            print(f"Unknown demo: {demo}")
            print("Usage: python 02_vision_language_models.py [1|2|3|4]")
    else:
        demo_provider_overview()
        demo_vlm_architecture()
        demo_prompting_techniques()
        demo_use_cases()

    print("=" * 60)
    print("✅ VLM demos completed!")
    print("=" * 60)
    print("\n💡 To use with real images:")
    print("   Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY")
    print('   provider = OpenAIVision()')
    print('   response = provider.analyze("image.jpg", "Describe this")')
    print()


if __name__ == "__main__":
    main()
