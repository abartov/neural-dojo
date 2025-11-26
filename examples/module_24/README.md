# Module 24 Examples: Video AI

This directory contains working examples for Module 24 (Video AI).

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Video Understanding
**File**: `01_video_understanding.py`
**Description**: Frame extraction, scene detection, and video Q&A with LLMs.

```bash
python 01_video_understanding.py        # Run all demos
python 01_video_understanding.py 1      # Frame extraction
python 01_video_understanding.py 2      # Scene detection
python 01_video_understanding.py 3      # Video captioning
python 01_video_understanding.py 4      # Video Q&A
```

### Example 2: Video Generation
**File**: `02_video_generation.py`
**Description**: Video generation concepts, architectures, and prompt engineering.

```bash
python 02_video_generation.py           # Run all demos
python 02_video_generation.py 1         # Generation concepts
python 02_video_generation.py 2         # Architecture (Sora-style)
python 02_video_generation.py 3         # Prompt engineering
python 02_video_generation.py 4         # Provider comparison
```

### Example 3: Video Summarization
**File**: `03_video_summarization.py`
**Description**: Video summarization, chapter generation, and highlight extraction.

```bash
python 03_video_summarization.py        # Run all demos
python 03_video_summarization.py 1      # Summarization pipeline
python 03_video_summarization.py 2      # Chapter generation
python 03_video_summarization.py 3      # Highlight extraction
python 03_video_summarization.py 4      # Thumbnail selection
```

## Deliverable

### Video AI Toolkit
**File**: `deliverable_video_ai_toolkit.py`
**Description**: Comprehensive toolkit for video understanding, analysis, and summarization.

```bash
python deliverable_video_ai_toolkit.py demo1     # Frame extraction strategies
python deliverable_video_ai_toolkit.py demo2     # Scene detection
python deliverable_video_ai_toolkit.py demo3     # LLM video analysis
python deliverable_video_ai_toolkit.py demo4     # Summarization & highlights
python deliverable_video_ai_toolkit.py analyze video.mp4  # Analyze a video
python deliverable_video_ai_toolkit.py summary video.mp4  # Generate summary
```

## Key Concepts

### Frame Sampling Strategies
- **Uniform**: Evenly distributed frames
- **Keyframe**: Frames with significant visual changes
- **Scene-based**: Best frame from each detected scene
- **Motion-based**: High-activity regions

### Scene Detection
- Histogram-based correlation analysis
- Configurable threshold and minimum duration
- Automatic thumbnail selection per scene

### Video Analysis with LLMs
- Multi-provider support (OpenAI, Anthropic)
- Frame-to-base64 encoding
- Video captioning and Q&A

### Video Summarization
- Automatic chapter generation
- Key moment extraction
- Highlight reel creation
- Quality-based thumbnail selection

## Notes

- OpenCV required for video processing
- Vision LLM access (GPT-4V, Claude Vision) for AI analysis
- Works in simulated mode without API keys
- JSON persistence for caching results
