#!/usr/bin/env python3
"""
Module 22 Example 02: Text-to-Speech (TTS)

Demonstrates various TTS providers and capabilities:
- OpenAI TTS (high quality, easy to use)
- Multiple voices and models
- Streaming TTS for low latency
- Audio caching for efficiency

Requirements:
    pip install openai pydub

Optional (for audio playback):
    pip install simpleaudio  # or use system player

Author: Neural Dojo
"""

import os
import sys
import time
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from abc import ABC, abstractmethod

# Check for OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system("pip install openai")
    from openai import OpenAI


@dataclass
class TTSResult:
    """Result from TTS generation."""
    audio_path: str
    text: str
    voice: str
    model: str
    duration_ms: float
    generation_time_ms: float
    cached: bool = False


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def generate(self, text: str, voice: str, output_path: str) -> TTSResult:
        """Generate speech from text."""
        pass

    @abstractmethod
    def list_voices(self) -> List[str]:
        """List available voices."""
        pass


class OpenAITTS(TTSProvider):
    """
    OpenAI Text-to-Speech provider.

    Models:
    - tts-1: Optimized for speed (~300ms latency)
    - tts-1-hd: Higher quality, slower (~500ms)

    Voices:
    - alloy: Neutral, balanced
    - echo: Warm, conversational
    - fable: British, narrative
    - onyx: Deep, authoritative
    - nova: Energetic, young
    - shimmer: Soft, gentle
    """

    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    MODELS = ["tts-1", "tts-1-hd"]

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key (or use OPENAI_API_KEY env var)."""
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = "tts-1"

    def generate(
        self,
        text: str,
        voice: str = "nova",
        output_path: str = "output.mp3",
        model: Optional[str] = None,
        speed: float = 1.0
    ) -> TTSResult:
        """
        Generate speech from text.

        Args:
            text: Text to synthesize
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            output_path: Path to save audio file
            model: Model name (tts-1 or tts-1-hd)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            TTSResult with audio path and metadata
        """
        if voice not in self.VOICES:
            raise ValueError(f"Unknown voice: {voice}. Choose from: {self.VOICES}")

        model = model or self.model
        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Choose from: {self.MODELS}")

        print(f"Generating speech with OpenAI TTS...")
        print(f"  Voice: {voice}")
        print(f"  Model: {model}")
        print(f"  Text length: {len(text)} chars")

        start = time.time()

        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed
        )

        # Save to file
        response.stream_to_file(output_path)

        generation_time = (time.time() - start) * 1000

        # Estimate duration (rough: ~150 words per minute)
        word_count = len(text.split())
        estimated_duration = (word_count / 150) * 60 * 1000 / speed

        print(f"  Generated in {generation_time:.0f}ms")
        print(f"  Saved to: {output_path}")

        return TTSResult(
            audio_path=output_path,
            text=text,
            voice=voice,
            model=model,
            duration_ms=estimated_duration,
            generation_time_ms=generation_time
        )

    def generate_streaming(
        self,
        text: str,
        voice: str = "nova",
        output_path: str = "output.mp3",
        chunk_callback=None
    ) -> TTSResult:
        """
        Generate speech with streaming (for lower time-to-first-byte).

        Args:
            text: Text to synthesize
            voice: Voice name
            output_path: Path to save audio file
            chunk_callback: Optional callback for each chunk (for real-time playback)

        Returns:
            TTSResult with audio path and metadata
        """
        print(f"Streaming TTS generation...")

        start = time.time()

        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        # Stream to file and optionally call callback
        with open(output_path, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=1024):
                f.write(chunk)
                if chunk_callback:
                    chunk_callback(chunk)

        generation_time = (time.time() - start) * 1000

        word_count = len(text.split())
        estimated_duration = (word_count / 150) * 60 * 1000

        return TTSResult(
            audio_path=output_path,
            text=text,
            voice=voice,
            model="tts-1",
            duration_ms=estimated_duration,
            generation_time_ms=generation_time
        )

    def list_voices(self) -> List[str]:
        """List available voices."""
        return self.VOICES.copy()


class CachedTTS:
    """
    TTS wrapper with caching to avoid regenerating repeated content.

    Useful for:
    - Repeated phrases (greetings, error messages)
    - Development/testing
    - Cost optimization
    """

    def __init__(self, provider: TTSProvider, cache_dir: str = ".tts_cache"):
        self.provider = provider
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_path = self.cache_dir / "index.json"
        self.cache_index = self._load_index()

    def _load_index(self) -> dict:
        """Load cache index from disk."""
        if self.cache_index_path.exists():
            with open(self.cache_index_path) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        """Save cache index to disk."""
        with open(self.cache_index_path, "w") as f:
            json.dump(self.cache_index, f, indent=2)

    def _cache_key(self, text: str, voice: str, model: str) -> str:
        """Generate cache key from parameters."""
        content = f"{text}:{voice}:{model}"
        return hashlib.md5(content.encode()).hexdigest()

    def generate(
        self,
        text: str,
        voice: str = "nova",
        model: str = "tts-1",
        force_regenerate: bool = False
    ) -> TTSResult:
        """
        Generate speech with caching.

        Args:
            text: Text to synthesize
            voice: Voice name
            model: Model name
            force_regenerate: Skip cache and regenerate

        Returns:
            TTSResult (with cached=True if from cache)
        """
        cache_key = self._cache_key(text, voice, model)

        # Check cache
        if not force_regenerate and cache_key in self.cache_index:
            cached_path = self.cache_dir / f"{cache_key}.mp3"
            if cached_path.exists():
                print(f"✨ Using cached audio: {cached_path}")
                entry = self.cache_index[cache_key]
                return TTSResult(
                    audio_path=str(cached_path),
                    text=text,
                    voice=voice,
                    model=model,
                    duration_ms=entry.get("duration_ms", 0),
                    generation_time_ms=0,
                    cached=True
                )

        # Generate new
        output_path = str(self.cache_dir / f"{cache_key}.mp3")
        result = self.provider.generate(text, voice, output_path, model=model)

        # Update cache index
        self.cache_index[cache_key] = {
            "text": text,
            "voice": voice,
            "model": model,
            "duration_ms": result.duration_ms,
            "created_at": time.time()
        }
        self._save_index()

        return result

    def clear_cache(self):
        """Clear all cached audio files."""
        import shutil
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index = {}
        print("🧹 Cache cleared")


def play_audio(audio_path: str):
    """Play audio file using available method."""
    import platform

    system = platform.system()

    if system == "Darwin":  # macOS
        os.system(f"afplay '{audio_path}'")
    elif system == "Linux":
        # Try various players
        players = ["aplay", "paplay", "mpv", "ffplay"]
        for player in players:
            if os.system(f"which {player} > /dev/null 2>&1") == 0:
                os.system(f"{player} '{audio_path}' 2>/dev/null")
                break
    elif system == "Windows":
        os.system(f'start "" "{audio_path}"')
    else:
        print(f"⚠️ Cannot auto-play audio. File saved at: {audio_path}")


def demo_basic_tts():
    """Demo 1: Basic TTS generation."""
    print("=" * 60)
    print("DEMO 1: Basic Text-to-Speech")
    print("=" * 60)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️ OPENAI_API_KEY not set. Showing simulated output.")
        print("\n📝 Sample text: 'Hello! This is a test of OpenAI's text to speech system.'")
        print("🎙️ Voice: nova")
        print("⏱️ Generated in ~300ms (simulated)")
        print()
        return

    tts = OpenAITTS()

    text = "Hello! This is a test of OpenAI's text to speech system. It can generate natural sounding speech from any text."

    result = tts.generate(
        text=text,
        voice="nova",
        output_path="demo_basic.mp3"
    )

    print(f"\n✅ Audio generated!")
    print(f"   Duration: ~{result.duration_ms / 1000:.1f}s")
    print(f"   Generation time: {result.generation_time_ms:.0f}ms")
    print()

    # Offer to play
    response = input("Play audio? (y/n): ").strip().lower()
    if response == "y":
        play_audio(result.audio_path)


def demo_voice_comparison():
    """Demo 2: Compare different voices."""
    print("=" * 60)
    print("DEMO 2: Voice Comparison")
    print("=" * 60)

    print("\n🎙️ Available OpenAI TTS Voices:\n")

    voices = {
        "alloy": "Neutral, balanced - good for general use",
        "echo": "Warm, conversational - good for chat interfaces",
        "fable": "British accent, narrative - good for storytelling",
        "onyx": "Deep, authoritative - good for announcements",
        "nova": "Energetic, young - good for dynamic content",
        "shimmer": "Soft, gentle - good for meditation/relaxation"
    }

    for voice, description in voices.items():
        print(f"   {voice:<10} {description}")

    print("\n📊 Model Options:")
    print("   tts-1     Fast (~300ms), good quality")
    print("   tts-1-hd  Slower (~500ms), higher quality")

    # Generate samples if API key is available
    if os.getenv("OPENAI_API_KEY"):
        print("\n📣 Generating voice samples...")
        tts = OpenAITTS()

        text = "Welcome to the Neural Dojo. Let's learn about speech synthesis."

        for voice in ["nova", "onyx", "shimmer"]:
            print(f"\n   Generating {voice}...")
            result = tts.generate(
                text=text,
                voice=voice,
                output_path=f"demo_voice_{voice}.mp3"
            )
            print(f"   ✅ Saved to demo_voice_{voice}.mp3")
    else:
        print("\n⚠️ Set OPENAI_API_KEY to generate voice samples.")
    print()


def demo_caching():
    """Demo 3: TTS caching for efficiency."""
    print("=" * 60)
    print("DEMO 3: TTS Caching")
    print("=" * 60)

    print("\n💡 Caching avoids regenerating repeated content.")
    print("   Useful for: greetings, error messages, common phrases\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Set OPENAI_API_KEY to demo caching.")
        print("\n📋 How caching works:")
        print("   1. First request: Generate and cache")
        print("   2. Same request: Return cached file instantly")
        print("   3. Cache key: hash(text + voice + model)")
        print()
        return

    tts = OpenAITTS()
    cached_tts = CachedTTS(tts, cache_dir=".tts_cache_demo")

    text = "This is a cached message that won't be regenerated."

    # First generation
    print("📣 First generation (will create cache)...")
    result1 = cached_tts.generate(text, voice="nova")
    print(f"   Time: {result1.generation_time_ms:.0f}ms")
    print(f"   Cached: {result1.cached}")

    # Second generation (from cache)
    print("\n📣 Second generation (from cache)...")
    result2 = cached_tts.generate(text, voice="nova")
    print(f"   Time: {result2.generation_time_ms:.0f}ms")
    print(f"   Cached: {result2.cached}")

    # Cleanup
    cached_tts.clear_cache()
    print()


def demo_use_cases():
    """Demo 4: Real-world use cases."""
    print("=" * 60)
    print("DEMO 4: TTS Use Cases")
    print("=" * 60)

    use_cases = [
        {
            "name": "Voice Assistant",
            "voice": "nova",
            "model": "tts-1",
            "speed": 1.0,
            "reason": "Fast response, natural conversation"
        },
        {
            "name": "Audiobook Narration",
            "voice": "fable",
            "model": "tts-1-hd",
            "speed": 0.9,
            "reason": "High quality, slower pace for comprehension"
        },
        {
            "name": "News Reading",
            "voice": "onyx",
            "model": "tts-1",
            "speed": 1.1,
            "reason": "Authoritative, slightly faster"
        },
        {
            "name": "Meditation Guide",
            "voice": "shimmer",
            "model": "tts-1-hd",
            "speed": 0.85,
            "reason": "Soft, slow, calming"
        },
        {
            "name": "Notification/Alert",
            "voice": "alloy",
            "model": "tts-1",
            "speed": 1.2,
            "reason": "Neutral, fast, clear"
        }
    ]

    print("\n📋 Recommended settings by use case:\n")
    print(f"{'Use Case':<20} {'Voice':<10} {'Model':<12} {'Speed':<6} Reason")
    print("-" * 80)

    for uc in use_cases:
        print(f"{uc['name']:<20} {uc['voice']:<10} {uc['model']:<12} {uc['speed']:<6} {uc['reason']}")

    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MODULE 22: TEXT-TO-SPEECH (TTS)")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo_num = sys.argv[1]
        if demo_num == "1":
            demo_basic_tts()
        elif demo_num == "2":
            demo_voice_comparison()
        elif demo_num == "3":
            demo_caching()
        elif demo_num == "4":
            demo_use_cases()
        else:
            print(f"Unknown demo: {demo_num}")
            print("Usage: python 02_text_to_speech.py [1|2|3|4]")
    else:
        # Run all demos
        demo_use_cases()
        demo_voice_comparison()
        demo_caching()
        demo_basic_tts()

    print("\n" + "=" * 60)
    print("✅ TTS demos completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
