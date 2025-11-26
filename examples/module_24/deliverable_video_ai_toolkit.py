#!/usr/bin/env python3
"""
Module 24 Deliverable: Video AI Toolkit

A comprehensive toolkit for video understanding, analysis, and summarization.
Combines frame extraction, scene detection, LLM-based captioning, and
highlight generation into a unified pipeline.

Features:
- Intelligent frame sampling (uniform, keyframe, scene-based)
- Scene boundary detection using histogram analysis
- Video captioning and Q&A with vision LLMs
- Automatic chapter generation
- Thumbnail selection (quality-based)
- Highlight reel extraction
- JSON persistence for results

Requirements:
    pip install opencv-python numpy openai anthropic Pillow

Author: Neural Dojo
"""

import os
import sys
import json
import time
import base64
import hashlib
from io import BytesIO
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from enum import Enum
from datetime import datetime

try:
    import cv2
    import numpy as np
except ImportError:
    print("Installing required packages...")
    os.system("pip install opencv-python numpy")
    import cv2
    import numpy as np

try:
    from PIL import Image
except ImportError:
    os.system("pip install Pillow")
    from PIL import Image


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class SamplingStrategy(Enum):
    """Frame sampling strategies."""
    UNIFORM = "uniform"
    KEYFRAME = "keyframe"
    SCENE_BASED = "scene_based"
    MOTION_BASED = "motion_based"


class Provider(Enum):
    """LLM providers for video analysis."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    SIMULATED = "simulated"


@dataclass
class VideoMetadata:
    """Metadata about a video file."""
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
class Frame:
    """A single video frame."""
    number: int
    timestamp: float
    image: Optional[np.ndarray] = None
    quality_score: float = 0.0
    motion_score: float = 0.0
    is_keyframe: bool = False


@dataclass
class Scene:
    """A detected scene in a video."""
    index: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    thumbnail_frame: int
    description: str = ""


@dataclass
class Chapter:
    """A chapter in a video."""
    number: int
    title: str
    start_time: float
    end_time: float
    summary: str
    thumbnail_frame: int
    topics: List[str] = field(default_factory=list)


@dataclass
class Highlight:
    """A highlight segment."""
    start_time: float
    end_time: float
    score: float
    reason: str


@dataclass
class VideoSummary:
    """Complete video summary."""
    video_path: str
    title: str
    overview: str
    duration: float
    chapters: List[Dict]
    key_moments: List[Dict]
    topics: List[str]
    thumbnail_timestamp: float
    generated_at: str


@dataclass
class AnalysisResult:
    """Result of video analysis."""
    video_hash: str
    video_path: str
    metadata: Dict
    frames_analyzed: int
    captions: List[Dict]
    scenes: List[Dict]
    chapters: List[Dict]
    summary: Optional[Dict]
    qa_history: List[Dict]
    analysis_time: float
    provider: str
    created_at: str


# =============================================================================
# VIDEO TOOLKIT
# =============================================================================

class VideoAIToolkit:
    """
    Comprehensive video AI toolkit.

    Combines frame extraction, scene detection, LLM analysis,
    and summarization into a unified interface.
    """

    STORAGE_DIR = ".video_ai_toolkit"

    def __init__(
        self,
        provider: Provider = Provider.SIMULATED,
        api_key: Optional[str] = None
    ):
        """
        Initialize the toolkit.

        Args:
            provider: LLM provider for analysis
            api_key: API key (auto-detected from env if not provided)
        """
        self.provider = provider
        self.api_key = api_key
        self.client = None

        # Setup storage
        self._setup_storage()

        # Initialize LLM client
        self._init_client()

        # Cache for video metadata
        self._metadata_cache: Dict[str, VideoMetadata] = {}

        print(f"✅ Video AI Toolkit initialized")
        print(f"   Provider: {self.provider.value}")

    def _setup_storage(self):
        """Create storage directory."""
        os.makedirs(self.STORAGE_DIR, exist_ok=True)
        os.makedirs(f"{self.STORAGE_DIR}/frames", exist_ok=True)
        os.makedirs(f"{self.STORAGE_DIR}/results", exist_ok=True)
        os.makedirs(f"{self.STORAGE_DIR}/thumbnails", exist_ok=True)

    def _init_client(self):
        """Initialize LLM client based on provider."""
        if self.provider == Provider.OPENAI:
            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=api_key)
                    print("   OpenAI client ready")
                except ImportError:
                    print("   ⚠️ openai package not installed")
                    self.provider = Provider.SIMULATED
            else:
                print("   ⚠️ No OpenAI API key - using simulated mode")
                self.provider = Provider.SIMULATED

        elif self.provider == Provider.ANTHROPIC:
            api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    import anthropic
                    self.client = anthropic.Anthropic(api_key=api_key)
                    print("   Anthropic client ready")
                except ImportError:
                    print("   ⚠️ anthropic package not installed")
                    self.provider = Provider.SIMULATED
            else:
                print("   ⚠️ No Anthropic API key - using simulated mode")
                self.provider = Provider.SIMULATED

    # -------------------------------------------------------------------------
    # Video Metadata
    # -------------------------------------------------------------------------

    def get_metadata(self, video_path: str) -> VideoMetadata:
        """
        Get video metadata.

        Args:
            video_path: Path to video file

        Returns:
            VideoMetadata object
        """
        # Check cache
        if video_path in self._metadata_cache:
            return self._metadata_cache[video_path]

        cap = cv2.VideoCapture(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        cap.release()

        # Calculate hash
        video_hash = self._hash_file(video_path)

        metadata = VideoMetadata(
            path=video_path,
            filename=Path(video_path).name,
            duration=frame_count / fps if fps > 0 else 0,
            fps=fps,
            frame_count=frame_count,
            width=width,
            height=height,
            size_bytes=os.path.getsize(video_path),
            codec=codec,
            hash=video_hash
        )

        self._metadata_cache[video_path] = metadata
        return metadata

    def _hash_file(self, path: str) -> str:
        """Calculate file hash."""
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            # Read first 10MB for hashing
            hasher.update(f.read(10 * 1024 * 1024))
        return hasher.hexdigest()[:12]

    # -------------------------------------------------------------------------
    # Frame Extraction
    # -------------------------------------------------------------------------

    def extract_frames(
        self,
        video_path: str,
        strategy: SamplingStrategy = SamplingStrategy.UNIFORM,
        n_frames: int = 10,
        save_frames: bool = False
    ) -> List[Frame]:
        """
        Extract frames from video.

        Args:
            video_path: Path to video
            strategy: Sampling strategy
            n_frames: Number of frames to extract
            save_frames: Whether to save frames to disk

        Returns:
            List of Frame objects
        """
        metadata = self.get_metadata(video_path)

        if strategy == SamplingStrategy.UNIFORM:
            frames = self._extract_uniform(video_path, n_frames)
        elif strategy == SamplingStrategy.KEYFRAME:
            frames = self._extract_keyframes(video_path, n_frames)
        elif strategy == SamplingStrategy.SCENE_BASED:
            frames = self._extract_scene_based(video_path, n_frames)
        else:
            frames = self._extract_uniform(video_path, n_frames)

        # Calculate quality scores
        for frame in frames:
            if frame.image is not None:
                frame.quality_score = self._calculate_quality(frame.image)

        # Optionally save frames
        if save_frames:
            for frame in frames:
                if frame.image is not None:
                    path = f"{self.STORAGE_DIR}/frames/{metadata.hash}_f{frame.number}.jpg"
                    cv2.imwrite(path, frame.image)

        return frames

    def _extract_uniform(self, video_path: str, n_frames: int) -> List[Frame]:
        """Extract frames uniformly distributed across video."""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        indices = np.linspace(0, total_frames - 1, n_frames, dtype=int)
        frames = []

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, image = cap.read()

            if ret:
                frames.append(Frame(
                    number=idx,
                    timestamp=idx / fps,
                    image=image
                ))

        cap.release()
        return frames

    def _extract_keyframes(
        self,
        video_path: str,
        n_frames: int,
        threshold: float = 0.5
    ) -> List[Frame]:
        """Extract keyframes based on histogram changes."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        keyframes = []
        prev_hist = None
        frame_idx = 0

        while cap.isOpened() and len(keyframes) < n_frames * 3:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is not None:
                corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                if corr < threshold:
                    keyframes.append(Frame(
                        number=frame_idx,
                        timestamp=frame_idx / fps,
                        image=frame.copy(),
                        is_keyframe=True
                    ))
            else:
                # First frame is always a keyframe
                keyframes.append(Frame(
                    number=frame_idx,
                    timestamp=frame_idx / fps,
                    image=frame.copy(),
                    is_keyframe=True
                ))

            prev_hist = hist
            frame_idx += 1

        cap.release()

        # Select best n_frames based on quality
        if len(keyframes) > n_frames:
            for kf in keyframes:
                kf.quality_score = self._calculate_quality(kf.image)
            keyframes.sort(key=lambda x: x.quality_score, reverse=True)
            keyframes = keyframes[:n_frames]
            keyframes.sort(key=lambda x: x.number)

        return keyframes

    def _extract_scene_based(self, video_path: str, n_frames: int) -> List[Frame]:
        """Extract one representative frame per scene."""
        scenes = self.detect_scenes(video_path)

        frames = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get best frame from each scene
        for scene in scenes[:n_frames]:
            best_frame = self._find_best_frame_in_range(
                cap, scene.start_frame, scene.end_frame
            )
            if best_frame is not None:
                frames.append(Frame(
                    number=best_frame[0],
                    timestamp=best_frame[0] / fps,
                    image=best_frame[1]
                ))

        cap.release()
        return frames

    def _find_best_frame_in_range(
        self,
        cap: cv2.VideoCapture,
        start: int,
        end: int,
        sample_count: int = 10
    ) -> Optional[Tuple[int, np.ndarray]]:
        """Find best quality frame in a range."""
        step = max(1, (end - start) // sample_count)
        best_frame = None
        best_score = 0

        for idx in range(start, min(end, start + sample_count * step), step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()

            if ret:
                score = self._calculate_quality(frame)
                if score > best_score:
                    best_score = score
                    best_frame = (idx, frame)

        return best_frame

    def _calculate_quality(self, image: np.ndarray) -> float:
        """Calculate frame quality score (0-1)."""
        # Sharpness via Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = min(1.0, laplacian.var() / 1000)

        # Color variance
        color_var = min(1.0, np.var(image) / 5000)

        # Brightness (penalize too dark/bright)
        brightness = np.mean(gray) / 255
        brightness_score = 1 - abs(brightness - 0.5) * 2

        # Combined score
        return sharpness * 0.5 + color_var * 0.3 + brightness_score * 0.2

    # -------------------------------------------------------------------------
    # Scene Detection
    # -------------------------------------------------------------------------

    def detect_scenes(
        self,
        video_path: str,
        threshold: float = 0.5,
        min_scene_duration: float = 1.0
    ) -> List[Scene]:
        """
        Detect scene boundaries.

        Args:
            video_path: Path to video
            threshold: Histogram correlation threshold
            min_scene_duration: Minimum scene length in seconds

        Returns:
            List of Scene objects
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        min_frames = int(min_scene_duration * fps)

        boundaries = [0]
        prev_hist = None
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is not None:
                corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)

                # Check for scene change
                if corr < threshold:
                    # Ensure minimum scene duration
                    if frame_idx - boundaries[-1] >= min_frames:
                        boundaries.append(frame_idx)

            prev_hist = hist
            frame_idx += 1

        boundaries.append(total_frames)
        cap.release()

        # Create Scene objects
        scenes = []
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]

            # Find best thumbnail frame
            cap = cv2.VideoCapture(video_path)
            best = self._find_best_frame_in_range(cap, start, end)
            cap.release()
            thumbnail_frame = best[0] if best else start

            scenes.append(Scene(
                index=i,
                start_frame=start,
                end_frame=end,
                start_time=start / fps,
                end_time=end / fps,
                duration=(end - start) / fps,
                thumbnail_frame=thumbnail_frame
            ))

        return scenes

    # -------------------------------------------------------------------------
    # LLM Analysis
    # -------------------------------------------------------------------------

    def caption_video(
        self,
        video_path: str,
        n_frames: int = 5,
        detailed: bool = False
    ) -> str:
        """
        Generate caption for video.

        Args:
            video_path: Path to video
            n_frames: Number of frames to analyze
            detailed: Whether to generate detailed caption

        Returns:
            Caption string
        """
        frames = self.extract_frames(
            video_path,
            strategy=SamplingStrategy.SCENE_BASED,
            n_frames=n_frames
        )

        if self.provider == Provider.SIMULATED:
            return self._simulated_caption(video_path, len(frames))

        # Convert frames to base64
        frame_images = self._frames_to_base64(frames)

        prompt = (
            "Describe what's happening in this video based on these frames. "
            f"{'Provide a detailed description.' if detailed else 'Be concise.'}"
        )

        return self._call_vision_llm(frame_images, prompt)

    def ask_video(
        self,
        video_path: str,
        question: str,
        n_frames: int = 8
    ) -> str:
        """
        Ask a question about a video.

        Args:
            video_path: Path to video
            question: Question to ask
            n_frames: Number of frames to analyze

        Returns:
            Answer string
        """
        frames = self.extract_frames(
            video_path,
            strategy=SamplingStrategy.UNIFORM,
            n_frames=n_frames
        )

        if self.provider == Provider.SIMULATED:
            return f"[Simulated] Analysis of {n_frames} frames suggests: {question[:50]}..."

        frame_images = self._frames_to_base64(frames)

        prompt = (
            f"Based on these video frames, answer: {question}\n"
            "Provide a clear, direct answer based on what you observe."
        )

        return self._call_vision_llm(frame_images, prompt)

    def _frames_to_base64(self, frames: List[Frame]) -> List[str]:
        """Convert frames to base64 strings."""
        encoded = []
        for frame in frames:
            if frame.image is not None:
                # Resize for efficiency
                h, w = frame.image.shape[:2]
                if max(h, w) > 512:
                    scale = 512 / max(h, w)
                    resized = cv2.resize(frame.image, None, fx=scale, fy=scale)
                else:
                    resized = frame.image

                _, buffer = cv2.imencode('.jpg', resized)
                b64 = base64.b64encode(buffer).decode('utf-8')
                encoded.append(b64)

        return encoded

    def _call_vision_llm(self, images: List[str], prompt: str) -> str:
        """Call vision LLM with images."""
        if self.provider == Provider.OPENAI and self.client:
            content = [{"type": "text", "text": prompt}]
            for img in images[:4]:  # Limit to 4 images
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                })

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": content}],
                max_tokens=500
            )
            return response.choices[0].message.content

        elif self.provider == Provider.ANTHROPIC and self.client:
            content = [{"type": "text", "text": prompt}]
            for img in images[:4]:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img
                    }
                })

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": content}]
            )
            return response.content[0].text

        return "[No LLM available]"

    def _simulated_caption(self, video_path: str, n_frames: int) -> str:
        """Generate simulated caption."""
        metadata = self.get_metadata(video_path)
        return (
            f"Video '{metadata.filename}' ({metadata.duration:.1f}s, "
            f"{metadata.width}x{metadata.height}). "
            f"Analyzed {n_frames} frames across {len(self.detect_scenes(video_path))} scenes."
        )

    # -------------------------------------------------------------------------
    # Summarization
    # -------------------------------------------------------------------------

    def summarize(
        self,
        video_path: str,
        generate_chapters: bool = True,
        n_frames_per_chapter: int = 3
    ) -> VideoSummary:
        """
        Generate complete video summary.

        Args:
            video_path: Path to video
            generate_chapters: Whether to generate chapters
            n_frames_per_chapter: Frames to analyze per chapter

        Returns:
            VideoSummary object
        """
        metadata = self.get_metadata(video_path)
        scenes = self.detect_scenes(video_path)

        # Generate chapters from scenes
        chapters = []
        if generate_chapters:
            for i, scene in enumerate(scenes[:10]):  # Max 10 chapters
                chapter = {
                    "number": i + 1,
                    "title": f"Chapter {i + 1}",
                    "start_time": scene.start_time,
                    "end_time": scene.end_time,
                    "summary": f"Scene from {scene.start_time:.1f}s to {scene.end_time:.1f}s",
                    "thumbnail_frame": scene.thumbnail_frame
                }
                chapters.append(chapter)

        # Generate key moments
        key_moments = []
        moment_times = np.linspace(0, metadata.duration, min(5, len(scenes) + 1))[1:-1]
        for i, t in enumerate(moment_times):
            key_moments.append({
                "timestamp": float(t),
                "description": f"Key moment at {t:.1f}s",
                "importance": 0.9 - (i * 0.1),
                "frame_number": int(t * metadata.fps)
            })

        # Generate overall caption
        if self.provider != Provider.SIMULATED:
            overview = self.caption_video(video_path, n_frames=5, detailed=True)
        else:
            overview = (
                f"Video with {len(scenes)} scenes, duration {metadata.duration:.1f}s. "
                f"Resolution: {metadata.width}x{metadata.height} @ {metadata.fps:.1f} fps."
            )

        # Find best thumbnail
        all_quality = []
        for scene in scenes:
            all_quality.append((scene.thumbnail_frame, self._get_frame_quality(
                video_path, scene.thumbnail_frame
            )))
        best_thumbnail = max(all_quality, key=lambda x: x[1])[0] if all_quality else 0

        return VideoSummary(
            video_path=video_path,
            title=Path(video_path).stem,
            overview=overview,
            duration=metadata.duration,
            chapters=chapters,
            key_moments=key_moments,
            topics=self._extract_topics(scenes),
            thumbnail_timestamp=best_thumbnail / metadata.fps,
            generated_at=datetime.now().isoformat()
        )

    def _get_frame_quality(self, video_path: str, frame_num: int) -> float:
        """Get quality score for a specific frame."""
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()

        if ret:
            return self._calculate_quality(frame)
        return 0.0

    def _extract_topics(self, scenes: List[Scene]) -> List[str]:
        """Extract topic tags from scenes."""
        # Simple topic extraction based on scene characteristics
        topics = []
        if len(scenes) > 5:
            topics.append("multi-scene")
        if any(s.duration > 30 for s in scenes):
            topics.append("long-takes")
        if any(s.duration < 2 for s in scenes):
            topics.append("fast-paced")
        return topics or ["general"]

    # -------------------------------------------------------------------------
    # Highlights
    # -------------------------------------------------------------------------

    def extract_highlights(
        self,
        video_path: str,
        target_duration: int = 30,
        n_segments: int = 5
    ) -> List[Highlight]:
        """
        Extract highlight segments.

        Args:
            video_path: Path to video
            target_duration: Target highlight reel duration
            n_segments: Number of segments to extract

        Returns:
            List of Highlight objects
        """
        metadata = self.get_metadata(video_path)
        scenes = self.detect_scenes(video_path)

        segment_length = target_duration / n_segments

        # Score scenes by visual interest
        scored_scenes = []
        for scene in scenes:
            score = self._score_scene_interest(video_path, scene)
            scored_scenes.append((scene, score))

        # Sort by score and select top segments
        scored_scenes.sort(key=lambda x: x[1], reverse=True)

        highlights = []
        for scene, score in scored_scenes[:n_segments]:
            # Extract segment from scene
            start = scene.start_time
            end = min(start + segment_length, scene.end_time)

            highlights.append(Highlight(
                start_time=start,
                end_time=end,
                score=score,
                reason=f"High visual interest (score: {score:.2f})"
            ))

        # Sort by timestamp
        highlights.sort(key=lambda x: x.start_time)

        return highlights

    def _score_scene_interest(self, video_path: str, scene: Scene) -> float:
        """Score a scene's visual interest."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Sample frames from scene
        n_samples = 5
        step = max(1, (scene.end_frame - scene.start_frame) // n_samples)

        scores = []
        prev_frame = None

        for i in range(n_samples):
            frame_idx = scene.start_frame + i * step
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if ret:
                # Quality score
                quality = self._calculate_quality(frame)
                scores.append(quality)

                # Motion score
                if prev_frame is not None:
                    motion = self._calculate_motion(prev_frame, frame)
                    scores.append(motion * 0.5)

                prev_frame = frame

        cap.release()
        return np.mean(scores) if scores else 0.0

    def _calculate_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate motion between two frames."""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray1, gray2)
        motion = np.mean(diff) / 255.0

        return min(1.0, motion * 5)  # Scale up

    # -------------------------------------------------------------------------
    # Thumbnail Selection
    # -------------------------------------------------------------------------

    def select_thumbnail(
        self,
        video_path: str,
        save_path: Optional[str] = None
    ) -> Tuple[int, float]:
        """
        Select best thumbnail frame.

        Args:
            video_path: Path to video
            save_path: Optional path to save thumbnail

        Returns:
            Tuple of (frame_number, quality_score)
        """
        frames = self.extract_frames(
            video_path,
            strategy=SamplingStrategy.KEYFRAME,
            n_frames=20
        )

        # Find best quality frame
        best_frame = max(frames, key=lambda f: f.quality_score)

        if save_path and best_frame.image is not None:
            cv2.imwrite(save_path, best_frame.image)
            print(f"   Thumbnail saved: {save_path}")

        return best_frame.number, best_frame.quality_score

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def save_analysis(self, result: AnalysisResult) -> str:
        """Save analysis result to JSON."""
        path = f"{self.STORAGE_DIR}/results/{result.video_hash}_analysis.json"

        with open(path, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)

        return path

    def load_analysis(self, video_path: str) -> Optional[AnalysisResult]:
        """Load cached analysis result."""
        video_hash = self._hash_file(video_path)
        path = f"{self.STORAGE_DIR}/results/{video_hash}_analysis.json"

        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return AnalysisResult(**data)

        return None

    def analyze_full(self, video_path: str) -> AnalysisResult:
        """
        Perform full video analysis.

        Args:
            video_path: Path to video

        Returns:
            Complete AnalysisResult
        """
        start_time = time.time()

        metadata = self.get_metadata(video_path)
        scenes = self.detect_scenes(video_path)
        summary = self.summarize(video_path)

        # Generate captions for key frames
        frames = self.extract_frames(video_path, n_frames=5)
        captions = []
        for i, frame in enumerate(frames):
            captions.append({
                "frame": frame.number,
                "timestamp": frame.timestamp,
                "caption": f"Frame at {frame.timestamp:.1f}s"
            })

        result = AnalysisResult(
            video_hash=metadata.hash,
            video_path=video_path,
            metadata=asdict(metadata),
            frames_analyzed=len(frames),
            captions=captions,
            scenes=[asdict(s) for s in scenes],
            chapters=summary.chapters,
            summary=asdict(summary),
            qa_history=[],
            analysis_time=time.time() - start_time,
            provider=self.provider.value,
            created_at=datetime.now().isoformat()
        )

        # Save result
        self.save_analysis(result)

        return result


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_frame_extraction():
    """Demo 1: Frame extraction strategies."""
    print("=" * 60)
    print("DEMO 1: Frame Extraction Strategies")
    print("=" * 60)

    print("\n📽️ Video Frame Sampling Strategies:\n")

    strategies = [
        {
            "name": "Uniform Sampling",
            "description": "Evenly spaced frames across video",
            "use_case": "General overview, consistent coverage",
            "method": "np.linspace(0, total_frames, n)"
        },
        {
            "name": "Keyframe Detection",
            "description": "Frames with significant visual changes",
            "use_case": "Scene transitions, action moments",
            "method": "Histogram correlation < threshold"
        },
        {
            "name": "Scene-Based",
            "description": "Best frame from each scene",
            "use_case": "Chapter thumbnails, summaries",
            "method": "Scene detection + quality scoring"
        },
        {
            "name": "Motion-Based",
            "description": "High-activity regions",
            "use_case": "Action highlights, sports",
            "method": "Frame differencing"
        }
    ]

    for s in strategies:
        print(f"   📸 {s['name']}")
        print(f"      {s['description']}")
        print(f"      Use: {s['use_case']}")
        print(f"      Method: {s['method']}")
        print()

    print("💡 Quality Metrics for Frame Selection:")
    print("   • Sharpness: Laplacian variance (higher = sharper)")
    print("   • Color: Variance across channels (higher = more interesting)")
    print("   • Brightness: Optimal range 40-60% (not too dark/bright)")
    print("   • Combined: 0.5*sharpness + 0.3*color + 0.2*brightness")
    print()

    # Simulate toolkit usage
    print("📋 Example Code:")
    print("   toolkit = VideoAIToolkit()")
    print("   frames = toolkit.extract_frames(")
    print("       'video.mp4',")
    print("       strategy=SamplingStrategy.KEYFRAME,")
    print("       n_frames=10")
    print("   )")
    print()


def demo_2_scene_detection():
    """Demo 2: Scene detection."""
    print("=" * 60)
    print("DEMO 2: Scene Detection")
    print("=" * 60)

    print("\n🎬 Scene Detection Pipeline:\n")

    print("   Video Stream")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │    For each frame:              │")
    print("   │    1. Convert to grayscale      │")
    print("   │    2. Calculate histogram       │")
    print("   │    3. Normalize histogram       │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │    Compare consecutive frames:  │")
    print("   │    correlation = compareHist()  │")
    print("   │    if correlation < threshold:  │")
    print("   │        → Scene boundary!        │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   Scene List: [(0-120), (121-340), (341-500), ...]")
    print()

    print("📊 Example Scene Detection Results:")
    print("   ┌────────────────────────────────────────────┐")
    print("   │ Scene 1: 0:00 - 0:15   (Introduction)      │")
    print("   │ Scene 2: 0:15 - 0:45   (Main content)      │")
    print("   │ Scene 3: 0:45 - 1:20   (Demo section)      │")
    print("   │ Scene 4: 1:20 - 1:35   (Closing)           │")
    print("   └────────────────────────────────────────────┘")
    print()

    print("⚙️ Tuning Parameters:")
    print("   • threshold: 0.5 (lower = more sensitive)")
    print("   • min_scene_duration: 1.0s (avoid micro-scenes)")
    print()


def demo_3_video_analysis():
    """Demo 3: Video analysis with LLMs."""
    print("=" * 60)
    print("DEMO 3: Video Analysis with Vision LLMs")
    print("=" * 60)

    print("\n🤖 Multi-Modal Video Analysis:\n")

    print("   Video → Frame Sampling → Vision LLM → Understanding")
    print()

    print("   Supported Providers:")
    print("   ┌─────────────────────────────────────────────────┐")
    print("   │ Provider      │ Model         │ Max Images     │")
    print("   │───────────────│───────────────│────────────────│")
    print("   │ OpenAI        │ gpt-4o-mini   │ 4              │")
    print("   │ Anthropic     │ claude-3-haiku│ 5              │")
    print("   │ Simulated     │ (demo mode)   │ unlimited      │")
    print("   └─────────────────────────────────────────────────┘")
    print()

    print("   Capabilities:")
    print("   • caption_video() - Describe video content")
    print("   • ask_video() - Answer questions about video")
    print()

    print("📝 Example Q&A:")
    print("   Q: 'How many people are in this video?'")
    print("   A: 'Based on the frames analyzed, there appear to be")
    print("       3 people visible throughout the video...'")
    print()
    print("   Q: 'What activity is being performed?'")
    print("   A: 'The video shows a cooking demonstration...")
    print("       The person is preparing a salad...'")
    print()

    # Show provider selection
    print("⚙️ Provider Configuration:")
    print("   # OpenAI (requires OPENAI_API_KEY)")
    print("   toolkit = VideoAIToolkit(provider=Provider.OPENAI)")
    print()
    print("   # Anthropic (requires ANTHROPIC_API_KEY)")
    print("   toolkit = VideoAIToolkit(provider=Provider.ANTHROPIC)")
    print()
    print("   # Simulated (no API key needed)")
    print("   toolkit = VideoAIToolkit(provider=Provider.SIMULATED)")
    print()


def demo_4_summarization():
    """Demo 4: Video summarization and highlights."""
    print("=" * 60)
    print("DEMO 4: Video Summarization & Highlights")
    print("=" * 60)

    print("\n📋 Video Summary Generation:\n")

    print("   ┌──────────────────────────────────────────────────┐")
    print("   │           VIDEO SUMMARY REPORT                   │")
    print("   │──────────────────────────────────────────────────│")
    print("   │                                                  │")
    print("   │ Title: Product Demo Tutorial                     │")
    print("   │ Duration: 10:30                                  │")
    print("   │ Scenes: 6                                        │")
    print("   │                                                  │")
    print("   │ Overview:                                        │")
    print("   │ A comprehensive product demonstration covering   │")
    print("   │ setup, features, and best practices...           │")
    print("   │                                                  │")
    print("   │ Chapters:                                        │")
    print("   │ 1. Introduction (0:00-0:45)                      │")
    print("   │ 2. Setup Guide (0:45-2:30)                       │")
    print("   │ 3. Core Features (2:30-5:15)                     │")
    print("   │ 4. Advanced Tips (5:15-8:00)                     │")
    print("   │ 5. Q&A Section (8:00-9:30)                       │")
    print("   │ 6. Conclusion (9:30-10:30)                       │")
    print("   │                                                  │")
    print("   │ Topics: tutorial, demo, product                  │")
    print("   └──────────────────────────────────────────────────┘")
    print()

    print("🎬 Highlight Extraction:")
    print()
    print("   Original Video (10 minutes):")
    print("   ├─────────────────────────────────────────────────┤")
    print("   ███░░░░░░░░███░░░░░░███░░░░░░░░░███░░░░░░░░░░░███")
    print("    H1          H2       H3          H4             H5")
    print()
    print("   Highlight Reel (30 seconds):")
    print("   ├─────────────────────┤")
    print("   ███ ███ ███ ███ ███")
    print("    H1  H2  H3  H4  H5")
    print()

    print("   Selection Criteria:")
    print("   • Visual interest score (quality + color)")
    print("   • Motion/activity level")
    print("   • Scene importance ranking")
    print("   • Temporal distribution")
    print()

    print("📋 Example Code:")
    print("   toolkit = VideoAIToolkit()")
    print("   summary = toolkit.summarize('video.mp4')")
    print("   highlights = toolkit.extract_highlights(")
    print("       'video.mp4', target_duration=30, n_segments=5")
    print("   )")
    print()


def main():
    """Run demos or process video."""
    print("\n" + "=" * 60)
    print("MODULE 24 DELIVERABLE: VIDEO AI TOOLKIT")
    print("=" * 60 + "\n")

    if len(sys.argv) < 2:
        print("Usage: python deliverable_video_ai_toolkit.py <command> [options]")
        print()
        print("Commands:")
        print("  demo1      - Frame extraction strategies")
        print("  demo2      - Scene detection")
        print("  demo3      - Video analysis with LLMs")
        print("  demo4      - Summarization and highlights")
        print("  analyze    - Analyze a video file")
        print("  summary    - Generate video summary")
        print()
        print("Examples:")
        print("  python deliverable_video_ai_toolkit.py demo1")
        print("  python deliverable_video_ai_toolkit.py analyze video.mp4")
        print("  python deliverable_video_ai_toolkit.py summary video.mp4")
        print()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_frame_extraction()
    elif command == "demo2":
        demo_2_scene_detection()
    elif command == "demo3":
        demo_3_video_analysis()
    elif command == "demo4":
        demo_4_summarization()
    elif command == "analyze" and len(sys.argv) > 2:
        video_path = sys.argv[2]
        if os.path.exists(video_path):
            toolkit = VideoAIToolkit()
            print(f"\n📹 Analyzing: {video_path}")

            # Get metadata
            metadata = toolkit.get_metadata(video_path)
            print(f"\nMetadata:")
            print(f"  Duration: {metadata.duration:.1f}s")
            print(f"  Resolution: {metadata.width}x{metadata.height}")
            print(f"  FPS: {metadata.fps:.1f}")
            print(f"  Frames: {metadata.frame_count}")

            # Detect scenes
            scenes = toolkit.detect_scenes(video_path)
            print(f"\nScenes detected: {len(scenes)}")
            for scene in scenes[:5]:
                print(f"  Scene {scene.index + 1}: {scene.start_time:.1f}s - {scene.end_time:.1f}s")

            # Select thumbnail
            thumb_frame, thumb_score = toolkit.select_thumbnail(video_path)
            print(f"\nBest thumbnail: frame {thumb_frame} (score: {thumb_score:.2f})")

            print("\n✅ Analysis complete!")
        else:
            print(f"❌ Video not found: {video_path}")
    elif command == "summary" and len(sys.argv) > 2:
        video_path = sys.argv[2]
        if os.path.exists(video_path):
            toolkit = VideoAIToolkit()
            print(f"\n📹 Summarizing: {video_path}")

            summary = toolkit.summarize(video_path)
            print(f"\n{'='*50}")
            print(f"SUMMARY: {summary.title}")
            print(f"{'='*50}")
            print(f"Duration: {summary.duration:.1f}s")
            print(f"Chapters: {len(summary.chapters)}")
            print(f"\nOverview:\n{summary.overview}")
            print(f"\nChapters:")
            for ch in summary.chapters:
                print(f"  {ch['number']}. {ch['title']} ({ch['start_time']:.1f}s - {ch['end_time']:.1f}s)")
            print("\n✅ Summary complete!")
        else:
            print(f"❌ Video not found: {video_path}")
    else:
        print(f"Unknown command: {command}")
        print("Use 'demo1', 'demo2', 'demo3', 'demo4', 'analyze', or 'summary'")

    print("\n" + "=" * 60)
    print("✅ Video AI Toolkit - Module 24 Complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
