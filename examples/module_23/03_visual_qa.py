#!/usr/bin/env python3
"""
Module 23 Example 03: Visual Question Answering

Demonstrates Visual QA and Document Understanding:
- Single-turn visual questions
- Multi-turn conversations with images
- Document data extraction
- Diagram understanding
- Image comparison

Requirements:
    pip install openai pillow

Author: Neural Dojo
"""

import os
import sys
import base64
import time
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path

# Check for required packages
try:
    from PIL import Image
except ImportError:
    print("Installing pillow...")
    os.system("pip install pillow")
    from PIL import Image


@dataclass
class VQAResult:
    """Result from Visual QA."""
    question: str
    answer: str
    confidence: Optional[str] = None
    latency_ms: float = 0


@dataclass
class DocumentExtraction:
    """Structured data extracted from a document."""
    raw_text: str
    structured_data: Dict[str, Any]
    confidence: float
    fields_found: List[str]


@dataclass
class ConversationTurn:
    """A turn in a visual conversation."""
    role: str  # "user" or "assistant"
    content: str
    has_image: bool = False


class VisualQA:
    """
    Visual Question Answering system.

    Answers questions about images using vision-language models.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Visual QA."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print("✅ Visual QA initialized with OpenAI")
            except ImportError:
                print("⚠️ openai package not installed")
        else:
            print("⚠️ No API key - using simulated mode")

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def ask(self, image_path: str, question: str) -> VQAResult:
        """
        Ask a question about an image.

        Args:
            image_path: Path to image file
            question: Question to ask about the image

        Returns:
            VQAResult with answer
        """
        start_time = time.time()

        if not self.client:
            # Simulated response
            return VQAResult(
                question=question,
                answer=f"[Simulated answer for: {question}]\n"
                       f"The image contains visual elements relevant to your question.",
                latency_ms=100
            )

        image_data = self.encode_image(image_path)
        media_type = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Look at this image carefully and answer the following question:\n{question}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        latency = (time.time() - start_time) * 1000

        return VQAResult(
            question=question,
            answer=response.choices[0].message.content,
            latency_ms=latency
        )

    def ask_with_confidence(self, image_path: str, question: str) -> VQAResult:
        """Ask a question and get confidence rating."""
        enhanced_question = (
            f"{question}\n\n"
            f"After answering, rate your confidence as HIGH, MEDIUM, or LOW "
            f"based on how clearly the image supports your answer."
        )
        result = self.ask(image_path, enhanced_question)

        # Try to extract confidence from answer
        answer_lower = result.answer.lower()
        if "high" in answer_lower:
            result.confidence = "HIGH"
        elif "medium" in answer_lower:
            result.confidence = "MEDIUM"
        elif "low" in answer_lower:
            result.confidence = "LOW"

        return result


class DocumentUnderstanding:
    """
    Document understanding and data extraction.

    Extracts structured information from documents, receipts, invoices.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Document Understanding."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print("✅ Document Understanding initialized")
            except ImportError:
                print("⚠️ openai package not installed")
        else:
            print("⚠️ No API key - using simulated mode")

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def extract_text(self, image_path: str) -> str:
        """Extract all text from an image (OCR)."""
        if not self.client:
            return "[Simulated OCR: Sample extracted text from document]"

        image_data = self.encode_image(image_path)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all visible text from this image. Return only the text, preserving the general layout."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                }
            ]
        )

        return response.choices[0].message.content

    def extract_invoice(self, image_path: str) -> DocumentExtraction:
        """Extract structured data from an invoice."""
        if not self.client:
            return DocumentExtraction(
                raw_text="[Simulated invoice text]",
                structured_data={
                    "invoice_number": "INV-001",
                    "date": "2024-01-15",
                    "vendor": "Sample Vendor",
                    "items": [{"description": "Item 1", "quantity": 1, "price": 100.00}],
                    "subtotal": 100.00,
                    "tax": 10.00,
                    "total": 110.00
                },
                confidence=0.95,
                fields_found=["invoice_number", "date", "vendor", "items", "total"]
            )

        image_data = self.encode_image(image_path)

        prompt = """Extract all information from this invoice and return as JSON with these fields:
        {
            "invoice_number": string,
            "date": string (YYYY-MM-DD format),
            "vendor": string,
            "vendor_address": string,
            "items": [{"description": string, "quantity": number, "unit_price": number, "total": number}],
            "subtotal": number,
            "tax": number,
            "total": number,
            "payment_terms": string,
            "notes": string
        }
        Use null for any fields you cannot find. Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        )

        text = response.choices[0].message.content

        # Try to parse JSON
        try:
            # Clean up potential markdown formatting
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())
            fields_found = [k for k, v in data.items() if v is not None]
            confidence = len(fields_found) / 10  # Simple confidence metric
        except json.JSONDecodeError:
            data = {"raw": text}
            fields_found = []
            confidence = 0.5

        return DocumentExtraction(
            raw_text=text,
            structured_data=data,
            confidence=confidence,
            fields_found=fields_found
        )

    def extract_receipt(self, image_path: str) -> DocumentExtraction:
        """Extract structured data from a receipt."""
        if not self.client:
            return DocumentExtraction(
                raw_text="[Simulated receipt text]",
                structured_data={
                    "store_name": "Sample Store",
                    "date": "2024-01-15",
                    "items": [{"name": "Coffee", "price": 4.50}],
                    "total": 4.50
                },
                confidence=0.90,
                fields_found=["store_name", "date", "items", "total"]
            )

        image_data = self.encode_image(image_path)

        prompt = """Extract all information from this receipt and return as JSON:
        {
            "store_name": string,
            "store_address": string,
            "date": string,
            "time": string,
            "items": [{"name": string, "quantity": number, "price": number}],
            "subtotal": number,
            "tax": number,
            "total": number,
            "payment_method": string
        }
        Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        )

        text = response.choices[0].message.content

        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            data = json.loads(text.strip())
            fields_found = [k for k, v in data.items() if v is not None]
            confidence = len(fields_found) / 8
        except json.JSONDecodeError:
            data = {"raw": text}
            fields_found = []
            confidence = 0.5

        return DocumentExtraction(
            raw_text=text,
            structured_data=data,
            confidence=confidence,
            fields_found=fields_found
        )


class ImageComparator:
    """Compare multiple images."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Image Comparator."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def compare(self, image_path1: str, image_path2: str, aspect: str = "general") -> str:
        """
        Compare two images.

        Args:
            image_path1: Path to first image
            image_path2: Path to second image
            aspect: What to compare ("general", "quality", "content", "differences")

        Returns:
            Comparison description
        """
        if not self.client:
            return f"[Simulated comparison ({aspect})]\n" \
                   f"Image 1 and Image 2 show different content with some similarities."

        prompts = {
            "general": "Compare these two images. Describe similarities and differences.",
            "quality": "Compare the quality of these two images (resolution, clarity, composition).",
            "content": "Compare what's shown in these images. What subjects or objects are in each?",
            "differences": "List every difference you can find between these two images."
        }

        image1_data = self.encode_image(image_path1)
        image2_data = self.encode_image(image_path2)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompts.get(aspect, prompts["general"])},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image1_data}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image2_data}"}}
                    ]
                }
            ]
        )

        return response.choices[0].message.content


def demo_basic_vqa():
    """Demo 1: Basic Visual QA."""
    print("=" * 60)
    print("DEMO 1: Basic Visual Question Answering")
    print("=" * 60)

    print("\n📊 Visual QA Pipeline:\n")
    print("   ┌──────────────────────────────────┐")
    print("   │           Input Image            │")
    print("   └───────────────┬──────────────────┘")
    print("                   │")
    print("                   ▼")
    print("   ┌──────────────────────────────────┐")
    print("   │   \"What color is the car?\"       │")
    print("   │        (User Question)           │")
    print("   └───────────────┬──────────────────┘")
    print("                   │")
    print("                   ▼")
    print("   ┌──────────────────────────────────┐")
    print("   │     Vision-Language Model        │")
    print("   │   • Process image + question     │")
    print("   │   • Reason about content         │")
    print("   │   • Generate answer              │")
    print("   └───────────────┬──────────────────┘")
    print("                   │")
    print("                   ▼")
    print("   ┌──────────────────────────────────┐")
    print("   │   \"The car in the image is       │")
    print("   │    red with silver accents.\"     │")
    print("   └──────────────────────────────────┘")
    print()

    print("📝 Example Questions:\n")

    examples = [
        ("What objects are visible?", "Object detection"),
        ("How many people are in this image?", "Counting"),
        ("What is the mood of this scene?", "Sentiment/emotion"),
        ("What text is visible?", "OCR"),
        ("What time of day does this appear to be?", "Context inference"),
        ("Is this image suitable for children?", "Content moderation"),
    ]

    for question, task_type in examples:
        print(f"   Q: {question}")
        print(f"      Task type: {task_type}")
        print()


def demo_document_extraction():
    """Demo 2: Document data extraction."""
    print("=" * 60)
    print("DEMO 2: Document Understanding")
    print("=" * 60)

    print("\n📄 Document Extraction Pipeline:\n")

    print("   Input: Invoice/Receipt Image")
    print("   ┌────────────────────────────────────┐")
    print("   │  ┌────────────────────────────┐   │")
    print("   │  │  INVOICE #INV-2024-001     │   │")
    print("   │  │  Date: 2024-01-15          │   │")
    print("   │  │  ──────────────────────    │   │")
    print("   │  │  Widget A    x2   $50.00   │   │")
    print("   │  │  Service B   x1   $100.00  │   │")
    print("   │  │  ──────────────────────    │   │")
    print("   │  │  Total:          $150.00   │   │")
    print("   │  └────────────────────────────┘   │")
    print("   └────────────────────────────────────┘")
    print()
    print("   Output: Structured JSON")
    print("   ┌────────────────────────────────────┐")
    print('   │ {                                  │')
    print('   │   "invoice_number": "INV-2024-001",│')
    print('   │   "date": "2024-01-15",            │')
    print('   │   "items": [                       │')
    print('   │     {"desc": "Widget A", ...},    │')
    print('   │     {"desc": "Service B", ...}    │')
    print('   │   ],                               │')
    print('   │   "total": 150.00                  │')
    print('   │ }                                  │')
    print("   └────────────────────────────────────┘")
    print()

    print("📋 Supported Document Types:\n")

    doc_types = [
        ("Invoices", "Invoice number, dates, line items, totals"),
        ("Receipts", "Store info, items, prices, payment method"),
        ("Forms", "Field labels and values, checkboxes"),
        ("Business Cards", "Name, title, company, contact info"),
        ("ID Documents", "Name, DOB, ID number (with privacy care)"),
        ("Tables", "Rows, columns, headers, cell values"),
    ]

    for doc, fields in doc_types:
        print(f"   📑 {doc}")
        print(f"      Fields: {fields}")
        print()


def demo_diagram_understanding():
    """Demo 3: Diagram and chart understanding."""
    print("=" * 60)
    print("DEMO 3: Diagram Understanding")
    print("=" * 60)

    print("\n📊 Diagram Types VLMs Can Understand:\n")

    diagram_types = [
        {
            "type": "Architecture Diagrams",
            "capabilities": ["Identify components", "Trace data flow", "Find bottlenecks"],
            "prompt": "Explain the architecture shown in this diagram. List all components and their connections."
        },
        {
            "type": "Flowcharts",
            "capabilities": ["Follow logic paths", "Identify decision points", "Describe process"],
            "prompt": "Walk me through this flowchart step by step. What happens at each decision point?"
        },
        {
            "type": "Charts & Graphs",
            "capabilities": ["Read values", "Identify trends", "Compare data points"],
            "prompt": "Analyze this chart. What are the key trends and notable data points?"
        },
        {
            "type": "UML Diagrams",
            "capabilities": ["Parse class relationships", "Identify methods", "Describe inheritance"],
            "prompt": "Explain the class structure shown in this UML diagram."
        },
        {
            "type": "Network Diagrams",
            "capabilities": ["Identify nodes", "Trace connections", "Find critical paths"],
            "prompt": "Describe the network topology shown. What are the main nodes and connections?"
        }
    ]

    for d in diagram_types:
        print(f"   🔹 {d['type']}")
        print(f"      Capabilities: {', '.join(d['capabilities'])}")
        print(f"      Sample prompt: \"{d['prompt'][:50]}...\"")
        print()

    print("💡 Best Practices for Diagrams:")
    print("   • Use high-resolution images")
    print("   • Ask for step-by-step explanations")
    print("   • Request specific information (\"List all services\")")
    print("   • Ask follow-up questions about specific components")
    print()


def demo_multi_image():
    """Demo 4: Multi-image comparison."""
    print("=" * 60)
    print("DEMO 4: Multi-Image Comparison")
    print("=" * 60)

    print("\n🔄 Multi-Image Analysis:\n")

    print("   Image 1                 Image 2")
    print("   ┌──────────┐            ┌──────────┐")
    print("   │ Product  │            │ Product  │")
    print("   │ Listing  │     vs     │ Received │")
    print("   │  Photo   │            │   Photo  │")
    print("   └──────────┘            └──────────┘")
    print("        │                       │")
    print("        └───────────┬───────────┘")
    print("                    │")
    print("                    ▼")
    print("        ┌─────────────────────┐")
    print("        │   VLM Comparison    │")
    print("        │  • Same product?    │")
    print("        │  • Quality match?   │")
    print("        │  • Any differences? │")
    print("        └─────────────────────┘")
    print()

    print("📋 Comparison Use Cases:\n")

    use_cases = [
        ("Product Verification", "Compare listing vs received product"),
        ("Before/After", "Document changes over time"),
        ("Quality Control", "Compare to reference standard"),
        ("Change Detection", "Find differences in satellite/security images"),
        ("A/B Testing", "Compare UI designs"),
        ("Authentication", "Compare documents for fraud detection"),
    ]

    for name, desc in use_cases:
        print(f"   • {name}")
        print(f"     {desc}")
        print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 23: VISUAL QUESTION ANSWERING")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "1":
            demo_basic_vqa()
        elif demo == "2":
            demo_document_extraction()
        elif demo == "3":
            demo_diagram_understanding()
        elif demo == "4":
            demo_multi_image()
        else:
            print(f"Unknown demo: {demo}")
            print("Usage: python 03_visual_qa.py [1|2|3|4]")
    else:
        demo_basic_vqa()
        demo_document_extraction()
        demo_diagram_understanding()
        demo_multi_image()

    print("=" * 60)
    print("✅ Visual QA demos completed!")
    print("=" * 60)
    print("\n💡 To use with real images:")
    print("   Set OPENAI_API_KEY environment variable")
    print('   vqa = VisualQA()')
    print('   result = vqa.ask("photo.jpg", "What is this?")')
    print()


if __name__ == "__main__":
    main()
