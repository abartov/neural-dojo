# Module 24 Deliverable: Video AI Toolkit

**Comprehensive toolkit for video understanding, analysis, and summarization with LLM integration.**

## Features

- **Frame Extraction**: Multiple sampling strategies (uniform, keyframe, scene-based)
- **Scene Detection**: Histogram-based boundary detection with quality scoring
- **Video Analysis**: Caption and Q&A with vision LLMs (GPT-4V, Claude Vision)
- **Summarization**: Chapter generation, key moments, overview synthesis
- **Highlights**: Automatic highlight reel extraction based on visual interest
- **Thumbnail Selection**: Quality-based best frame identification
- **Multi-Provider**: OpenAI, Anthropic, and simulated modes
- **JSON Persistence**: Cache analysis results for reuse

## Quick Start

```bash
# Run demos
python deliverable_video_ai_toolkit.py demo1    # Frame extraction strategies
python deliverable_video_ai_toolkit.py demo2    # Scene detection pipeline
python deliverable_video_ai_toolkit.py demo3    # LLM video analysis
python deliverable_video_ai_toolkit.py demo4    # Summarization & highlights

# Analyze a video
python deliverable_video_ai_toolkit.py analyze video.mp4

# Generate summary
python deliverable_video_ai_toolkit.py summary video.mp4
```

## Architecture

```
VideoAIToolkit
├── Frame Extraction
│   ├── extract_frames(strategy, n_frames)
│   ├── _extract_uniform()
│   ├── _extract_keyframes()
│   └── _extract_scene_based()
├── Scene Detection
│   ├── detect_scenes(threshold)
│   └── _find_best_frame_in_range()
├── LLM Analysis
│   ├── caption_video()
│   ├── ask_video()
│   └── _call_vision_llm()
├── Summarization
│   ├── summarize()
│   └── extract_highlights()
├── Quality Metrics
│   ├── _calculate_quality()
│   └── _calculate_motion()
└── Persistence
    ├── save_analysis()
    └── load_analysis()
```

## Frame Sampling Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| UNIFORM | Evenly spaced frames | General overview |
| KEYFRAME | Significant visual changes | Transitions, action |
| SCENE_BASED | Best frame per scene | Thumbnails, summaries |
| MOTION_BASED | High-activity regions | Sports, action videos |

## Quality Metrics

The toolkit uses multiple metrics to evaluate frame quality:

```python
quality = 0.5 * sharpness + 0.3 * color_variance + 0.2 * brightness_score

# Where:
# - Sharpness: Laplacian variance (higher = sharper)
# - Color variance: Pixel intensity variance (higher = more interesting)
# - Brightness: Distance from optimal (40-60% brightness)
```

## Provider Configuration

```python
from deliverable_video_ai_toolkit import VideoAIToolkit, Provider

# OpenAI (requires OPENAI_API_KEY)
toolkit = VideoAIToolkit(provider=Provider.OPENAI)

# Anthropic (requires ANTHROPIC_API_KEY)
toolkit = VideoAIToolkit(provider=Provider.ANTHROPIC)

# Simulated (no API required - demo mode)
toolkit = VideoAIToolkit(provider=Provider.SIMULATED)
```

## Example Usage

```python
# Initialize toolkit
toolkit = VideoAIToolkit()

# Get video metadata
metadata = toolkit.get_metadata("video.mp4")
print(f"Duration: {metadata.duration}s, Resolution: {metadata.width}x{metadata.height}")

# Extract frames
frames = toolkit.extract_frames("video.mp4", strategy=SamplingStrategy.KEYFRAME, n_frames=10)

# Detect scenes
scenes = toolkit.detect_scenes("video.mp4")
for scene in scenes:
    print(f"Scene {scene.index}: {scene.start_time:.1f}s - {scene.end_time:.1f}s")

# Generate caption
caption = toolkit.caption_video("video.mp4", n_frames=5)
print(caption)

# Ask questions
answer = toolkit.ask_video("video.mp4", "How many people appear in this video?")
print(answer)

# Full summarization
summary = toolkit.summarize("video.mp4")
print(f"Title: {summary.title}")
print(f"Chapters: {len(summary.chapters)}")

# Extract highlights
highlights = toolkit.extract_highlights("video.mp4", target_duration=30)
for h in highlights:
    print(f"Highlight: {h.start_time:.1f}s - {h.end_time:.1f}s (score: {h.score:.2f})")

# Select best thumbnail
frame_num, score = toolkit.select_thumbnail("video.mp4", save_path="thumb.jpg")
```

## Data Structures

```python
@dataclass
class VideoMetadata:
    path: str
    filename: str
    duration: float
    fps: float
    frame_count: int
    width: int
    height: int
    size_bytes: int
    codec: str
    hash: str

@dataclass
class Scene:
    index: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    thumbnail_frame: int
    description: str

@dataclass
class VideoSummary:
    video_path: str
    title: str
    overview: str
    duration: float
    chapters: List[Dict]
    key_moments: List[Dict]
    topics: List[str]
    thumbnail_timestamp: float
    generated_at: str
```

## Storage Structure

```
.video_ai_toolkit/
├── frames/           # Extracted frame images
├── results/          # JSON analysis results
└── thumbnails/       # Selected thumbnails
```

## Dependencies

- `opencv-python` - Video processing
- `numpy` - Numerical operations
- `Pillow` - Image handling
- `openai` - GPT-4V integration (optional)
- `anthropic` - Claude Vision integration (optional)

## Performance Notes

- Scene detection: ~1-2 seconds per minute of video
- Frame extraction: ~100-500ms per frame
- LLM analysis: ~2-5 seconds per API call
- Full analysis cached to JSON for reuse

**Time**: ~4 hours | **Lines**: 900+ | **Author**: Neural Dojo
