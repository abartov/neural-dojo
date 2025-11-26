# Module 23 Deliverable: Vision AI Toolkit

**A comprehensive toolkit for building vision-enabled AI applications with multi-provider VLM support, CLIP-based search, and document understanding.**

## Features

- **Multi-provider VLM**: OpenAI GPT-4V, Anthropic Claude Vision, simulated mode
- **CLIP Image Search**: Semantic search using text queries
- **Document Understanding**: Invoice, receipt, form, business card extraction
- **Image Comparison**: Side-by-side visual analysis
- **Smart Caching**: Hash-based response caching
- **Metrics Tracking**: Latency, cache hits, error monitoring
- **Graceful Degradation**: Works without API keys

## Quick Start

```bash
# Run all demos
python deliverable_vision_ai_toolkit.py

# Individual demos
python deliverable_vision_ai_toolkit.py demo1  # Image analysis
python deliverable_vision_ai_toolkit.py demo2  # Document extraction
python deliverable_vision_ai_toolkit.py demo3  # Semantic image search
python deliverable_vision_ai_toolkit.py demo4  # Metrics dashboard
```

## VLM Providers

| Provider | Requirements | Models |
|----------|-------------|--------|
| `openai` | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini, gpt-4-turbo |
| `anthropic` | `ANTHROPIC_API_KEY` | claude-3-opus, claude-3-sonnet, claude-3-haiku |
| `simulated` | None | Testing mode |

## Usage Examples

### Image Analysis
```python
from deliverable_vision_ai_toolkit import VisionAIToolkit

toolkit = VisionAIToolkit(provider="openai")

# Describe an image
result = toolkit.describe("photo.jpg")
print(result.text)

# Ask a question
result = toolkit.ask("diagram.png", "What architecture is shown?")
print(result.text)
```

### Document Extraction
```python
# Extract invoice data
result = toolkit.extract_document("invoice.jpg", "invoice")
for field in result.fields:
    print(f"{field.name}: {field.value}")

# Output:
# invoice_number: INV-2024-001
# date: 2024-01-15
# total: 150.00
```

### Image Search
```python
# Index images
toolkit.index_images(["cat.jpg", "dog.jpg", "car.jpg"])

# Search with text
results = toolkit.search_images("cute pet playing")
for r in results:
    print(f"{r.rank}. {r.path} (score: {r.score:.2f})")
```

### Image Comparison
```python
# Compare two images
comparison = toolkit.compare_images("before.jpg", "after.jpg")
print(f"Similarities: {comparison.similarities}")
print(f"Differences: {comparison.differences}")
```

## Document Types

| Type | Fields Extracted |
|------|-----------------|
| `invoice` | invoice_number, date, vendor, items, tax, total |
| `receipt` | store, date, items, subtotal, tax, total |
| `form` | field labels, field values |
| `business_card` | name, title, company, email, phone |

## Architecture

```
VisionAIToolkit
├── VisionProvider (abstract)
│   ├── OpenAIVisionProvider (GPT-4V)
│   ├── AnthropicVisionProvider (Claude)
│   └── SimulatedVisionProvider (testing)
├── VisionCache (hash-based caching)
├── ImageSearch (CLIP embeddings)
└── MetricsSummary (tracking)
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: For GPT-4V
- `ANTHROPIC_API_KEY`: For Claude Vision

### VisionConfig
```python
@dataclass
class VisionConfig:
    provider: str = "simulated"
    model: str = "gpt-4o"
    max_tokens: int = 1000
    temperature: float = 0.0
    detail: str = "auto"  # low, high, auto
```

## Metrics

```python
print(toolkit.get_metrics_summary())

# Output:
# Analyses: Total: 15, Avg Latency: 234.5ms
# Document Extractions: 5
# Image Searches: 8
# Cache: Hit Rate: 46.7%
```

## Performance

| Operation | Provider | Typical Latency |
|-----------|----------|-----------------|
| Analysis | GPT-4o | 1-3 seconds |
| Analysis | Claude 3 | 1-3 seconds |
| Analysis | Simulated | 100ms |
| CLIP Embedding | Local | 50-200ms |
| Cached Response | Any | <10ms |

## Files

```
module_23/
├── deliverable_vision_ai_toolkit.py  # Main deliverable (1061 lines)
├── DELIVERABLE_README.md            # This file
├── requirements.txt                 # Dependencies
├── .gitignore                       # Excludes .vision_toolkit/
├── 01_clip_embeddings.py           # CLIP example
├── 02_vision_language_models.py    # VLM example
└── 03_visual_qa.py                 # Visual QA example
```

---

**Time**: ~4 hours | **Lines**: 1061 | **Author**: Neural Dojo
