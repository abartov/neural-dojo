# Module 23: Vision AI Examples

This directory contains working code examples for Module 23: Vision AI & Vision-Language Models.

## Prerequisites

```bash
pip install -r requirements.txt
```

**Optional** (for full functionality):
- OpenAI API key for GPT-4V
- Anthropic API key for Claude Vision
- `transformers` for local CLIP

## Examples

### Example 1: CLIP Embeddings
**File**: `01_clip_embeddings.py`
**Description**: CLIP image-text embeddings, zero-shot classification, semantic search
**Run**: `python 01_clip_embeddings.py [1|2|3|4]`

Features:
- Image encoding to embeddings
- Text encoding to embeddings
- Zero-shot image classification
- Semantic image search

### Example 2: Vision-Language Models
**File**: `02_vision_language_models.py`
**Description**: Multi-provider VLM comparison (GPT-4V, Claude, Gemini)
**Run**: `python 02_vision_language_models.py [1|2|3|4]`

Features:
- Provider comparison
- VLM architecture overview
- Prompting techniques
- Use case recommendations

### Example 3: Visual Question Answering
**File**: `03_visual_qa.py`
**Description**: Visual QA, document extraction, diagram understanding
**Run**: `python 03_visual_qa.py [1|2|3|4]`

Features:
- Single-turn visual questions
- Document data extraction
- Diagram understanding
- Multi-image comparison

## Deliverable

### Vision AI Toolkit
**File**: `deliverable_vision_ai_toolkit.py`
**Description**: Production-ready toolkit for vision-enabled AI applications
**Run**: `python deliverable_vision_ai_toolkit.py [demo1|demo2|demo3|demo4]`

See `DELIVERABLE_README.md` for detailed documentation.

## Expected Output

### Example 1 (CLIP)
```
📊 Available CLIP Models:
   base     openai/clip-vit-base-patch32
   large    openai/clip-vit-large-patch14
   huge     laion/CLIP-ViT-H-14-laion2B-s32B-b79K
```

### Example 2 (VLMs)
```
📋 Vision Language Model Comparison:

   🔹 GPT-4V / GPT-4o (OpenAI)
      Models: gpt-4o, gpt-4o-mini, gpt-4-turbo
      Strengths: General reasoning, OCR, Multi-image
```

### Example 3 (Visual QA)
```
📊 Visual QA Pipeline:

   Input Image → User Question → Vision-Language Model → Answer
```

## Notes

### API Keys
- Set `OPENAI_API_KEY` for GPT-4V
- Set `ANTHROPIC_API_KEY` for Claude Vision
- Set `GOOGLE_API_KEY` for Gemini Vision
- Examples work in simulated mode without API keys

### CLIP Models
| Model | Params | Use Case |
|-------|--------|----------|
| base (ViT-B/32) | 151M | Development, fast |
| large (ViT-L/14) | 428M | Production, balanced |
| huge (ViT-H/14) | 986M | Maximum accuracy |

### VLM Capabilities
- **GPT-4V**: Best general purpose, fast
- **Claude 3**: Best for detailed analysis, safest
- **Gemini**: Best for video, longest context
- **LLaVA**: Best for local deployment

## Related Theory

See `docs/curriculum/notes/module_23_vision_ai.md` for comprehensive theory on:
- Vision Transformer (ViT) architecture
- CLIP contrastive learning
- Vision-Language Model architectures
- Multimodal prompting techniques
- Production considerations
