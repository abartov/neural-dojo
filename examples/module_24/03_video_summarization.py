#!/usr/bin/env python3
"""
Module 24 Example 03: Video Summarization

Demonstrates video summarization techniques:
- Hierarchical summarization
- Chapter/segment generation
- Key moment extraction
- Thumbnail selection
- Video highlights

Requirements:
    pip install opencv-python numpy

Author: Neural Dojo
"""

import os
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:
    print("Installing required packages...")
    os.system("pip install opencv-python numpy")
    import cv2
    import numpy as np


@dataclass
class VideoChapter:
    """A chapter/segment of a video."""
    title: str
    start_time: float
    end_time: float
    summary: str
    thumbnail_frame: int


@dataclass
class KeyMoment:
    """A key moment in a video."""
    timestamp: float
    description: str
    importance: float  # 0-1 score
    frame_number: int


@dataclass
class VideoSummary:
    """Complete video summary."""
    title: str
    overview: str
    duration: float
    chapters: List[VideoChapter]
    key_moments: List[KeyMoment]
    topics: List[str]
    generated_at: float = field(default_factory=time.time)


class VideoSummarizer:
    """
    Summarize videos into chapters and key moments.

    Uses a combination of scene detection and LLM analysis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize summarizer."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print("✅ Video Summarizer initialized")
            except ImportError:
                print("⚠️ openai not installed")
        else:
            print("⚠️ No API key - using simulated mode")

    def detect_scenes(self, video_path: str, threshold: float = 0.5) -> List[tuple]:
        """
        Detect scene boundaries.

        Returns list of (start_time, end_time) tuples.
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        scenes = []
        prev_hist = None
        scene_start = 0
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
                if corr < threshold:
                    scenes.append((scene_start, frame_idx / fps))
                    scene_start = frame_idx / fps

            prev_hist = hist
            frame_idx += 1

        # Add final scene
        scenes.append((scene_start, frame_idx / fps))

        cap.release()
        return scenes

    def extract_thumbnail(
        self,
        video_path: str,
        timestamp: float,
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """Extract a frame at timestamp as thumbnail."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_num = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

        ret, frame = cap.read()
        cap.release()

        if ret and output_path:
            cv2.imwrite(output_path, frame)

        return frame if ret else None

    def find_best_thumbnail(
        self,
        video_path: str,
        start_time: float,
        end_time: float
    ) -> int:
        """
        Find the best thumbnail frame in a segment.

        Uses sharpness and color variance as quality metrics.
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        best_frame = start_frame
        best_score = 0

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        for frame_idx in range(start_frame, min(end_frame, start_frame + 100), 5):
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate sharpness (Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Calculate color variance
            color_var = np.var(frame)

            # Combined score
            score = sharpness * 0.7 + color_var * 0.3

            if score > best_score:
                best_score = score
                best_frame = frame_idx

        cap.release()
        return best_frame

    def summarize(self, video_path: str) -> VideoSummary:
        """
        Generate a complete video summary.

        Returns VideoSummary with chapters, key moments, and overview.
        """
        # Get video metadata
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()

        # Detect scenes
        scenes = self.detect_scenes(video_path)

        # Generate chapters from scenes
        chapters = []
        for i, (start, end) in enumerate(scenes[:10]):  # Limit to 10 chapters
            thumbnail_frame = self.find_best_thumbnail(video_path, start, end)

            chapter = VideoChapter(
                title=f"Chapter {i + 1}",
                start_time=start,
                end_time=end,
                summary=f"Scene from {start:.1f}s to {end:.1f}s",
                thumbnail_frame=thumbnail_frame
            )
            chapters.append(chapter)

        # Generate simulated key moments
        key_moments = []
        moment_times = np.linspace(0, duration, min(5, len(scenes) + 1))[1:-1]

        for i, t in enumerate(moment_times):
            key_moments.append(KeyMoment(
                timestamp=t,
                description=f"Key moment at {t:.1f}s",
                importance=0.8 - (i * 0.1),
                frame_number=int(t * fps)
            ))

        return VideoSummary(
            title=Path(video_path).stem,
            overview=f"Video with {len(scenes)} scenes, duration {duration:.1f}s",
            duration=duration,
            chapters=chapters,
            key_moments=key_moments,
            topics=["scene1", "scene2", "scene3"]
        )


class HighlightGenerator:
    """Generate video highlights/clips."""

    def __init__(self):
        pass

    def extract_highlights(
        self,
        video_path: str,
        duration: int = 30,
        n_segments: int = 5
    ) -> List[tuple]:
        """
        Extract highlight segments.

        Returns list of (start_time, end_time) for highlight clips.
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / fps
        cap.release()

        # Calculate segment length
        segment_length = duration / n_segments

        # Select segments with highest activity (motion)
        # For demo, use uniform distribution
        highlights = []
        step = video_duration / (n_segments + 1)

        for i in range(n_segments):
            start = step * (i + 0.5)
            end = min(start + segment_length, video_duration)
            highlights.append((start, end))

        return highlights

    def create_highlight_reel(
        self,
        video_path: str,
        highlights: List[tuple],
        output_path: str
    ) -> bool:
        """
        Create a highlight reel from segments.

        Note: Actual implementation would use MoviePy or FFmpeg.
        """
        print(f"Would create highlight reel:")
        print(f"  Source: {video_path}")
        print(f"  Output: {output_path}")
        print(f"  Segments: {len(highlights)}")
        for i, (start, end) in enumerate(highlights):
            print(f"    {i+1}. {start:.1f}s - {end:.1f}s")

        return True


def demo_summarization():
    """Demo 1: Video summarization."""
    print("=" * 60)
    print("DEMO 1: Video Summarization")
    print("=" * 60)

    print("\n📝 Video Summarization Pipeline:\n")
    print("   Input Video")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │       Scene Detection           │")
    print("   │   Identify visual boundaries    │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │      Frame Sampling             │")
    print("   │   Extract key frames per scene  │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │      LLM Analysis               │")
    print("   │   Caption and summarize         │")
    print("   └─────────────────────────────────┘")
    print("        │")
    print("        ▼")
    print("   Video Summary:")
    print("   • Overview")
    print("   • Chapters with timestamps")
    print("   • Key moments")
    print("   • Topics/tags")
    print()


def demo_chapters():
    """Demo 2: Chapter generation."""
    print("=" * 60)
    print("DEMO 2: Chapter Generation")
    print("=" * 60)

    print("\n📖 Automatic Chapter Generation:\n")

    print("   Example Output:")
    print("   ┌────────────────────────────────────────────┐")
    print("   │ VIDEO: \"Product Demo Tutorial\"             │")
    print("   │                                            │")
    print("   │ CHAPTERS:                                  │")
    print("   │                                            │")
    print("   │ 1. Introduction         0:00 - 0:45        │")
    print("   │    Overview of the product                 │")
    print("   │                                            │")
    print("   │ 2. Setup Guide          0:45 - 2:30        │")
    print("   │    Installation and configuration          │")
    print("   │                                            │")
    print("   │ 3. Basic Features       2:30 - 5:15        │")
    print("   │    Core functionality walkthrough          │")
    print("   │                                            │")
    print("   │ 4. Advanced Features    5:15 - 8:00        │")
    print("   │    Power user capabilities                 │")
    print("   │                                            │")
    print("   │ 5. Tips & Tricks        8:00 - 9:30        │")
    print("   │    Expert recommendations                  │")
    print("   │                                            │")
    print("   │ 6. Conclusion           9:30 - 10:00       │")
    print("   │    Summary and next steps                  │")
    print("   └────────────────────────────────────────────┘")
    print()

    print("💡 Applications:")
    print("   • YouTube chapter markers")
    print("   • Educational video navigation")
    print("   • Meeting recordings")
    print("   • Podcast episodes")
    print()


def demo_highlights():
    """Demo 3: Highlight extraction."""
    print("=" * 60)
    print("DEMO 3: Highlight Extraction")
    print("=" * 60)

    print("\n🎬 Highlight Reel Generation:\n")

    print("   Original Video (10 minutes)")
    print("   ┌──────────────────────────────────────────┐")
    print("   │████░░░░████░░░████░░░░░████░░░░░░░░████  │")
    print("   │ H1     H2    H3       H4            H5   │")
    print("   └──────────────────────────────────────────┘")
    print("         │")
    print("         ▼ Extract & Concatenate")
    print()
    print("   Highlight Reel (30 seconds)")
    print("   ┌────────────────────┐")
    print("   │ H1 │ H2 │ H3 │ H4 │ H5 │")
    print("   └────────────────────┘")
    print()

    print("   Selection Criteria:")
    print("   • Motion/action peaks")
    print("   • Audio peaks (applause, reactions)")
    print("   • Face detection moments")
    print("   • Scene transitions")
    print()


def demo_thumbnail():
    """Demo 4: Thumbnail selection."""
    print("=" * 60)
    print("DEMO 4: Automatic Thumbnail Selection")
    print("=" * 60)

    print("\n🖼️ Smart Thumbnail Selection:\n")

    print("   Video Frames → Quality Analysis → Best Thumbnail")
    print()
    print("   Quality Metrics:")
    print("   ┌─────────────────────────────────────────┐")
    print("   │                                         │")
    print("   │   📊 Sharpness (Laplacian variance)     │")
    print("   │      Higher = clearer image             │")
    print("   │                                         │")
    print("   │   🎨 Color Variance                     │")
    print("   │      Higher = more visual interest      │")
    print("   │                                         │")
    print("   │   👤 Face Detection                     │")
    print("   │      Presence and position of faces     │")
    print("   │                                         │")
    print("   │   🎯 Rule of Thirds                     │")
    print("   │      Subject placement                  │")
    print("   │                                         │")
    print("   │   💡 Brightness                         │")
    print("   │      Not too dark or overexposed        │")
    print("   │                                         │")
    print("   └─────────────────────────────────────────┘")
    print()

    print("   Example Score Calculation:")
    print("   Frame 150:  Sharpness=0.72  Color=0.65  Score=0.70")
    print("   Frame 230:  Sharpness=0.88  Color=0.78  Score=0.85 ← Best")
    print("   Frame 310:  Sharpness=0.45  Color=0.82  Score=0.58")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 24: VIDEO SUMMARIZATION")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "1":
            demo_summarization()
        elif demo == "2":
            demo_chapters()
        elif demo == "3":
            demo_highlights()
        elif demo == "4":
            demo_thumbnail()
        else:
            print(f"Unknown demo: {demo}")
            print("Usage: python 03_video_summarization.py [1|2|3|4]")
    else:
        demo_summarization()
        demo_chapters()
        demo_highlights()
        demo_thumbnail()

    print("=" * 60)
    print("✅ Video Summarization demos completed!")
    print("=" * 60)
    print("\n💡 To summarize real videos:")
    print("   summarizer = VideoSummarizer()")
    print("   summary = summarizer.summarize('video.mp4')")
    print()


if __name__ == "__main__":
    main()
