#!/usr/bin/env python3
"""
Module 22 Example 01: Speech-to-Text with Whisper

Demonstrates various STT capabilities:
- Basic transcription with Whisper
- Word-level timestamps
- Language detection and translation
- Audio preprocessing for better accuracy

Requirements:
    pip install openai-whisper faster-whisper librosa numpy

Author: Neural Dojo
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List
import numpy as np

# Check for required packages
try:
    import whisper
except ImportError:
    print("Installing openai-whisper...")
    os.system("pip install openai-whisper")
    import whisper


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio."""
    start: float
    end: float
    text: str
    words: Optional[List[dict]] = None


@dataclass
class TranscriptionResult:
    """Complete transcription result."""
    text: str
    language: str
    language_probability: float
    duration: float
    segments: List[TranscriptionSegment]
    processing_time: float


class WhisperTranscriber:
    """
    Speech-to-text transcription using OpenAI's Whisper.

    Supports multiple model sizes for different speed/accuracy tradeoffs:
    - tiny: Fastest, lowest accuracy (39M params)
    - base: Fast, good accuracy (74M params)
    - small: Balanced (244M params)
    - medium: High accuracy (769M params)
    - large-v3: Best accuracy (1.5B params)
    """

    # Model information
    MODELS = {
        "tiny": {"params": "39M", "vram": "~1GB", "speed": "~32x"},
        "base": {"params": "74M", "vram": "~1GB", "speed": "~16x"},
        "small": {"params": "244M", "vram": "~2GB", "speed": "~6x"},
        "medium": {"params": "769M", "vram": "~5GB", "speed": "~2x"},
        "large": {"params": "1.5B", "vram": "~10GB", "speed": "1x"},
        "large-v2": {"params": "1.5B", "vram": "~10GB", "speed": "1x"},
        "large-v3": {"params": "1.5B", "vram": "~10GB", "speed": "1x"},
    }

    def __init__(self, model_size: str = "base"):
        """
        Initialize transcriber with specified model size.

        Args:
            model_size: One of tiny, base, small, medium, large, large-v2, large-v3
        """
        if model_size not in self.MODELS:
            raise ValueError(f"Unknown model size: {model_size}. Choose from: {list(self.MODELS.keys())}")

        self.model_size = model_size
        print(f"Loading Whisper {model_size} model...")
        print(f"  Parameters: {self.MODELS[model_size]['params']}")
        print(f"  VRAM: {self.MODELS[model_size]['vram']}")

        start = time.time()
        self.model = whisper.load_model(model_size)
        load_time = time.time() - start
        print(f"  Model loaded in {load_time:.1f}s")
        print()

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        word_timestamps: bool = False
    ) -> TranscriptionResult:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Language code (e.g., 'en', 'es', 'fr') or None for auto-detect
            task: 'transcribe' or 'translate' (translates to English)
            word_timestamps: Include word-level timestamps

        Returns:
            TranscriptionResult with text, segments, and metadata
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Transcribing: {audio_path}")
        print(f"  Task: {task}")
        print(f"  Language: {language or 'auto-detect'}")

        start = time.time()
        result = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            word_timestamps=word_timestamps
        )
        processing_time = time.time() - start

        # Parse segments
        segments = []
        for seg in result["segments"]:
            segment = TranscriptionSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
                words=seg.get("words")
            )
            segments.append(segment)

        # Calculate duration from last segment
        duration = segments[-1].end if segments else 0

        return TranscriptionResult(
            text=result["text"].strip(),
            language=result["language"],
            language_probability=result.get("language_probability", 1.0),
            duration=duration,
            segments=segments,
            processing_time=processing_time
        )

    def transcribe_with_timestamps(self, audio_path: str) -> TranscriptionResult:
        """Transcribe with word-level timestamps."""
        return self.transcribe(audio_path, word_timestamps=True)

    def translate_to_english(self, audio_path: str) -> TranscriptionResult:
        """Transcribe non-English audio and translate to English."""
        return self.transcribe(audio_path, task="translate")

    def detect_language(self, audio_path: str) -> tuple:
        """
        Detect language of audio file.

        Returns:
            Tuple of (language_code, probability)
        """
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)

        return detected_lang, probs[detected_lang]


def generate_sample_audio():
    """Generate a sample audio file for testing (requires TTS)."""
    try:
        from gtts import gTTS

        text = "Hello! This is a test of the Whisper speech recognition system. It can transcribe audio in many languages with remarkable accuracy."

        tts = gTTS(text=text, lang='en')

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            return f.name

    except ImportError:
        print("Note: Install gTTS for automatic sample generation: pip install gTTS")
        return None


def demo_basic_transcription(transcriber: WhisperTranscriber, audio_path: str):
    """Demo 1: Basic transcription."""
    print("=" * 60)
    print("DEMO 1: Basic Transcription")
    print("=" * 60)

    result = transcriber.transcribe(audio_path)

    print(f"\n📝 Transcription:")
    print(f"   {result.text}")
    print(f"\n📊 Metadata:")
    print(f"   Language: {result.language} ({result.language_probability:.1%} confidence)")
    print(f"   Duration: {result.duration:.1f}s")
    print(f"   Processing time: {result.processing_time:.2f}s")
    print(f"   Speed: {result.duration / result.processing_time:.1f}x real-time")
    print()


def demo_timestamps(transcriber: WhisperTranscriber, audio_path: str):
    """Demo 2: Transcription with timestamps."""
    print("=" * 60)
    print("DEMO 2: Transcription with Timestamps")
    print("=" * 60)

    result = transcriber.transcribe_with_timestamps(audio_path)

    print(f"\n⏱️ Timestamped segments:")
    for segment in result.segments:
        print(f"   [{segment.start:6.2f}s - {segment.end:6.2f}s] {segment.text}")

        # Show word timestamps if available
        if segment.words:
            for word in segment.words[:3]:  # Show first 3 words
                print(f"      [{word['start']:.2f}s] {word['word']}")
            if len(segment.words) > 3:
                print(f"      ... and {len(segment.words) - 3} more words")
    print()


def demo_language_detection(transcriber: WhisperTranscriber, audio_path: str):
    """Demo 3: Language detection."""
    print("=" * 60)
    print("DEMO 3: Language Detection")
    print("=" * 60)

    lang, prob = transcriber.detect_language(audio_path)

    print(f"\n🌍 Detected language: {lang}")
    print(f"   Confidence: {prob:.1%}")

    # Language name mapping (subset)
    lang_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ja": "Japanese",
        "ko": "Korean", "zh": "Chinese", "ru": "Russian", "ar": "Arabic"
    }

    if lang in lang_names:
        print(f"   Language name: {lang_names[lang]}")
    print()


def demo_model_comparison():
    """Demo 4: Compare different model sizes."""
    print("=" * 60)
    print("DEMO 4: Model Size Comparison")
    print("=" * 60)

    print("\n📊 Whisper Model Sizes:\n")
    print(f"{'Model':<12} {'Parameters':<12} {'VRAM':<10} {'Relative Speed':<15}")
    print("-" * 50)

    for model, info in WhisperTranscriber.MODELS.items():
        print(f"{model:<12} {info['params']:<12} {info['vram']:<10} {info['speed']:<15}")

    print("\n💡 Recommendations:")
    print("   - Development/Testing: 'base' (fast iteration)")
    print("   - Production (English): 'medium' or 'large-v3'")
    print("   - Production (Multilingual): 'large-v3'")
    print("   - Real-time: 'tiny' or 'base' (low latency)")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 22: SPEECH-TO-TEXT WITH WHISPER")
    print("=" * 60 + "\n")

    # Demo 4: Model comparison (no audio needed)
    demo_model_comparison()

    # Try to get or generate sample audio
    audio_path = None

    # Check for command line argument
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        if not os.path.exists(audio_path):
            print(f"❌ Audio file not found: {audio_path}")
            sys.exit(1)
    else:
        # Try to generate sample
        print("No audio file provided. Generating sample...")
        audio_path = generate_sample_audio()

        if not audio_path:
            print("\n⚠️ No audio file available for demos.")
            print("   Usage: python 01_speech_to_text.py <audio_file.mp3>")
            print("\n   Or install gTTS for auto-generated samples:")
            print("   pip install gTTS")
            return

    print(f"\n🎵 Using audio file: {audio_path}\n")

    # Initialize transcriber
    transcriber = WhisperTranscriber(model_size="base")

    # Run demos
    demo_basic_transcription(transcriber, audio_path)
    demo_timestamps(transcriber, audio_path)
    demo_language_detection(transcriber, audio_path)

    # Cleanup temp file if we generated it
    if "tmp" in audio_path.lower():
        os.unlink(audio_path)
        print("🧹 Cleaned up temporary audio file")

    print("\n" + "=" * 60)
    print("✅ All demos completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
