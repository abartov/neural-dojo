#!/usr/bin/env python3
"""
Module 24 Example 01: Video Understanding

Demonstrates video understanding capabilities:
- Frame extraction and sampling
- Video captioning with LLMs
- Video Q&A
- Scene detection
- Action recognition concepts

Requirements:
    pip install opencv-python numpy pillow

Author: Neural Dojo
"""

import os
import sys
import time
import base64
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path

# Check for required packages
try:
    import cv2
    import numpy as np
except ImportError:
    print("Installing required packages...")
    os.system("pip install opencv-python numpy")
    import cv2
    import numpy as np


@dataclass
class VideoMetadata:
    """Metadata about a video file."""
    path: str
    duration_seconds: float
    fps: float
    frame_count: int
    width: int
    height: int
    codec: str


@dataclass
class FrameSample:
    """A sampled frame from a video."""
    frame: np.ndarray
    frame_number: int
    timestamp: float


@dataclass
class SceneSegment:
    """A detected scene segment."""
    start_time: float
    end_time: float
    start_frame: int
    end_frame: int


class VideoExtractor:
    """
    Extract and sample frames from videos.

    Supports multiple sampling strategies for different use cases.
    """

    def __init__(self, video_path: str):
        """
        Initialize video extractor.

        Args:
            video_path: Path to video file
        """
        self.video_path = video_path
        self.cap = None
        self._metadata = None

    @property
    def metadata(self) -> VideoMetadata:
        """Get video metadata (lazy loaded)."""
        if self._metadata is None:
            self._metadata = self._extract_metadata()
        return self._metadata

    def _extract_metadata(self) -> VideoMetadata:
        """Extract video metadata."""
        cap = cv2.VideoCapture(self.video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec_str = "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])

        duration = frame_count / fps if fps > 0 else 0

        cap.release()

        return VideoMetadata(
            path=self.video_path,
            duration_seconds=duration,
            fps=fps,
            frame_count=frame_count,
            width=width,
            height=height,
            codec=codec_str
        )

    def extract_frames(
        self,
        fps: float = 1.0,
        max_frames: int = 100,
        start_time: float = 0,
        end_time: Optional[float] = None
    ) -> List[FrameSample]:
        """
        Extract frames at specified fps.

        Args:
            fps: Frames per second to extract
            max_frames: Maximum frames to return
            start_time: Start time in seconds
            end_time: End time in seconds (None = video end)

        Returns:
            List of FrameSample objects
        """
        cap = cv2.VideoCapture(self.video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        if video_fps <= 0:
            cap.release()
            return []

        frame_interval = max(1, int(video_fps / fps))

        # Seek to start time
        start_frame = int(start_time * video_fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Calculate end frame
        end_frame = int((end_time or self.metadata.duration_seconds) * video_fps)

        frames = []
        frame_idx = start_frame

        while cap.isOpened() and len(frames) < max_frames:
            if frame_idx >= end_frame:
                break

            ret, frame = cap.read()
            if not ret:
                break

            if (frame_idx - start_frame) % frame_interval == 0:
                timestamp = frame_idx / video_fps
                frames.append(FrameSample(
                    frame=frame,
                    frame_number=frame_idx,
                    timestamp=timestamp
                ))

            frame_idx += 1

        cap.release()
        return frames

    def sample_uniform(self, n_frames: int) -> List[FrameSample]:
        """Sample n frames uniformly across the video."""
        all_frames = self.extract_frames(fps=self.metadata.fps, max_frames=10000)

        if len(all_frames) <= n_frames:
            return all_frames

        indices = np.linspace(0, len(all_frames) - 1, n_frames, dtype=int)
        return [all_frames[i] for i in indices]

    def detect_keyframes(self, threshold: float = 0.5) -> List[FrameSample]:
        """
        Detect keyframes (scene changes) in the video.

        Args:
            threshold: Correlation threshold for scene change

        Returns:
            List of keyframe samples
        """
        cap = cv2.VideoCapture(self.video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        keyframes = []
        prev_hist = None
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate grayscale histogram
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is None or cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL) < threshold:
                keyframes.append(FrameSample(
                    frame=frame,
                    frame_number=frame_idx,
                    timestamp=frame_idx / video_fps
                ))

            prev_hist = hist
            frame_idx += 1

        cap.release()
        return keyframes


class SceneDetector:
    """Detect scene boundaries in videos."""

    def __init__(self, threshold: float = 0.5):
        """
        Initialize scene detector.

        Args:
            threshold: Correlation threshold for scene change
        """
        self.threshold = threshold

    def detect_scenes(self, video_path: str) -> List[SceneSegment]:
        """
        Detect scenes in a video.

        Returns:
            List of SceneSegment objects
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        scenes = []
        prev_hist = None
        scene_start_frame = 0
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is not None:
                correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)

                if correlation < self.threshold:
                    # Scene change detected
                    scenes.append(SceneSegment(
                        start_time=scene_start_frame / fps,
                        end_time=frame_idx / fps,
                        start_frame=scene_start_frame,
                        end_frame=frame_idx
                    ))
                    scene_start_frame = frame_idx

            prev_hist = hist
            frame_idx += 1

        # Add final scene
        if frame_idx > scene_start_frame:
            scenes.append(SceneSegment(
                start_time=scene_start_frame / fps,
                end_time=frame_idx / fps,
                start_frame=scene_start_frame,
                end_frame=frame_idx
            ))

        cap.release()
        return scenes


class VideoAnalyzer:
    """Analyze videos using vision LLMs."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize video analyzer."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print("✅ Video Analyzer initialized with OpenAI")
            except ImportError:
                print("⚠️ openai not installed")
        else:
            print("⚠️ No API key - using simulated mode")

    def encode_frame(self, frame: np.ndarray, quality: int = 80) -> str:
        """Encode frame to base64."""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return base64.b64encode(buffer).decode('utf-8')

    def caption(self, frames: List[FrameSample]) -> str:
        """Generate a caption for the video."""
        if not self.client:
            return "[Simulated caption] The video shows various scenes and activities."

        content = [{"type": "text", "text": "Describe what happens in this video. These are sampled frames."}]

        for sample in frames[:10]:  # Limit to 10 frames
            encoded = self.encode_frame(sample.frame)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}
            })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=300
        )

        return response.choices[0].message.content

    def ask(self, frames: List[FrameSample], question: str) -> str:
        """Ask a question about the video."""
        if not self.client:
            return f"[Simulated answer to: {question}]"

        content = [{"type": "text", "text": f"Based on these video frames, answer: {question}"}]

        for sample in frames[:10]:
            encoded = self.encode_frame(sample.frame)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}
            })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=300
        )

        return response.choices[0].message.content


def demo_frame_extraction():
    """Demo 1: Frame extraction and sampling."""
    print("=" * 60)
    print("DEMO 1: Frame Extraction & Sampling")
    print("=" * 60)

    print("\n📹 Video Frame Extraction Pipeline:\n")
    print("   Video File (.mp4, .avi, .mov)")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │       OpenCV VideoCapture       │")
    print("   │   • Read frames sequentially    │")
    print("   │   • Access metadata             │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │      Sampling Strategy          │")
    print("   │   • Uniform (every Nth frame)   │")
    print("   │   • Keyframe (scene changes)    │")
    print("   │   • Dense (high fps)            │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   [Frame1, Frame2, Frame3, ...]")
    print()

    print("📊 Sampling Strategies:\n")

    strategies = [
        ("Uniform", "Equal intervals", "General analysis, summarization"),
        ("Keyframe", "Scene changes", "Video summarization, highlights"),
        ("Dense", "High fps", "Action recognition, motion analysis"),
        ("Sparse", "Low fps", "Long video understanding"),
        ("Adaptive", "Based on motion", "Efficient processing"),
    ]

    print(f"   {'Strategy':<12} {'Method':<20} {'Use Case'}")
    print("   " + "-" * 55)
    for strategy, method, use_case in strategies:
        print(f"   {strategy:<12} {method:<20} {use_case}")
    print()


def demo_scene_detection():
    """Demo 2: Scene detection."""
    print("=" * 60)
    print("DEMO 2: Scene Detection")
    print("=" * 60)

    print("\n🎬 Scene Detection Pipeline:\n")
    print("   Video Frames")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │   Calculate Frame Histogram     │")
    print("   │   (grayscale distribution)      │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │   Compare Adjacent Frames       │")
    print("   │   correlation(hist[i], hist[i+1])│")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │   Detect Scene Changes          │")
    print("   │   if correlation < threshold    │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   [Scene1: 0:00-0:30, Scene2: 0:30-1:15, ...]")
    print()

    print("📊 Example Output:\n")
    print("   Scene    Start      End        Duration")
    print("   " + "-" * 45)
    print("   1        0:00.0     0:28.5     28.5s")
    print("   2        0:28.5     1:15.2     46.7s")
    print("   3        1:15.2     2:03.8     48.6s")
    print("   4        2:03.8     2:45.0     41.2s")
    print()

    print("💡 Applications:")
    print("   • Video chapter markers")
    print("   • Automatic thumbnails")
    print("   • Content indexing")
    print("   • Highlight reels")
    print()


def demo_video_qa():
    """Demo 3: Video Q&A with LLMs."""
    print("=" * 60)
    print("DEMO 3: Video Q&A with Vision LLMs")
    print("=" * 60)

    print("\n🤖 Video Q&A Pipeline:\n")
    print("   Video + Question")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │      Extract Key Frames         │")
    print("   │   (uniform sampling, ~10 fps)   │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │      Encode to Base64           │")
    print("   │   (JPEG compression)            │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │      Vision LLM (GPT-4V)        │")
    print("   │   [Question] + [Frame1, F2, ...]│")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   Answer: \"The video shows...\"")
    print()

    print("📝 Example Questions:\n")

    questions = [
        ("What is happening in this video?", "Scene description"),
        ("How many people are visible?", "Counting"),
        ("What actions are being performed?", "Action recognition"),
        ("Where was this video filmed?", "Location inference"),
        ("What is the mood or tone?", "Sentiment analysis"),
        ("Summarize this video in 3 sentences.", "Summarization"),
    ]

    for question, task in questions:
        print(f"   Q: {question}")
        print(f"      Task: {task}")
        print()


def demo_video_analysis():
    """Demo 4: Complete video analysis."""
    print("=" * 60)
    print("DEMO 4: Complete Video Analysis")
    print("=" * 60)

    print("\n📊 Full Video Analysis Pipeline:\n")

    print("   Input: video.mp4")
    print("   ┌────────────────────────────────────────┐")
    print("   │                                        │")
    print("   │   1. Extract Metadata                  │")
    print("   │      └─ Duration, FPS, Resolution      │")
    print("   │                                        │")
    print("   │   2. Scene Detection                   │")
    print("   │      └─ Identify scene boundaries      │")
    print("   │                                        │")
    print("   │   3. Keyframe Extraction               │")
    print("   │      └─ Sample representative frames   │")
    print("   │                                        │")
    print("   │   4. Visual Analysis (LLM)             │")
    print("   │      └─ Caption, Q&A, summarize        │")
    print("   │                                        │")
    print("   │   5. Generate Report                   │")
    print("   │      └─ Structured output              │")
    print("   │                                        │")
    print("   └────────────────────────────────────────┘")
    print()

    print("   Output:")
    print("   ┌────────────────────────────────────────┐")
    print("   │ {                                      │")
    print("   │   \"duration\": \"2:45\",                 │")
    print('   │   "scenes": 4,                        │')
    print('   │   "summary": "A tutorial video...",   │')
    print('   │   "key_events": ["intro", "demo"],    │')
    print('   │   "objects": ["laptop", "person"]     │')
    print("   │ }                                      │")
    print("   └────────────────────────────────────────┘")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 24: VIDEO UNDERSTANDING")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "1":
            demo_frame_extraction()
        elif demo == "2":
            demo_scene_detection()
        elif demo == "3":
            demo_video_qa()
        elif demo == "4":
            demo_video_analysis()
        else:
            print(f"Unknown demo: {demo}")
            print("Usage: python 01_video_understanding.py [1|2|3|4]")
    else:
        demo_frame_extraction()
        demo_scene_detection()
        demo_video_qa()
        demo_video_analysis()

    print("=" * 60)
    print("✅ Video Understanding demos completed!")
    print("=" * 60)
    print("\n💡 To use with real videos:")
    print("   extractor = VideoExtractor('video.mp4')")
    print("   frames = extractor.sample_uniform(10)")
    print()


if __name__ == "__main__":
    main()
