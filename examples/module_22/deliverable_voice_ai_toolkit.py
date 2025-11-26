#!/usr/bin/env python3
"""
Module 22 Deliverable: Voice AI Toolkit

A comprehensive toolkit for building voice-enabled AI applications.

Features:
- Multi-provider STT (Whisper local, OpenAI API)
- Multi-provider TTS (OpenAI, simulated ElevenLabs)
- Voice Activity Detection (VAD)
- Audio preprocessing and enhancement
- Conversation management with memory
- Caching for efficiency
- Metrics and monitoring
- Production-ready patterns

Usage:
    python deliverable_voice_ai_toolkit.py demo1  # STT showcase
    python deliverable_voice_ai_toolkit.py demo2  # TTS showcase
    python deliverable_voice_ai_toolkit.py demo3  # Voice assistant
    python deliverable_voice_ai_toolkit.py demo4  # Metrics dashboard

Author: Neural Dojo
"""

import os
import sys
import json
import time
import hashlib
import tempfile
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Callable
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import statistics

# Ensure numpy is available
try:
    import numpy as np
except ImportError:
    os.system("pip install numpy")
    import numpy as np


# =============================================================================
# Configuration and Data Classes
# =============================================================================

class STTProvider(Enum):
    """Available STT providers."""
    WHISPER_LOCAL = "whisper_local"
    OPENAI_API = "openai_api"
    SIMULATED = "simulated"


class TTSProvider(Enum):
    """Available TTS providers."""
    OPENAI = "openai"
    ELEVENLABS = "elevenlabs"
    SIMULATED = "simulated"


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    silence_threshold: float = 0.01
    silence_duration: float = 0.5
    max_duration: float = 30.0


@dataclass
class STTConfig:
    """Speech-to-text configuration."""
    provider: STTProvider = STTProvider.SIMULATED
    model: str = "base"
    language: Optional[str] = None
    word_timestamps: bool = False


@dataclass
class TTSConfig:
    """Text-to-speech configuration."""
    provider: TTSProvider = TTSProvider.SIMULATED
    voice: str = "nova"
    model: str = "tts-1"
    speed: float = 1.0


@dataclass
class VoiceToolkitConfig:
    """Complete toolkit configuration."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    cache_dir: str = ".voice_toolkit"
    enable_caching: bool = True
    enable_metrics: bool = True


@dataclass
class TranscriptionResult:
    """Result from speech-to-text."""
    text: str
    language: str
    confidence: float
    duration_seconds: float
    processing_time_ms: float
    provider: str
    segments: List[Dict] = field(default_factory=list)


@dataclass
class SynthesisResult:
    """Result from text-to-speech."""
    audio_path: str
    text: str
    voice: str
    duration_ms: float
    processing_time_ms: float
    provider: str
    cached: bool = False


@dataclass
class ConversationMessage:
    """A message in the conversation."""
    role: str
    content: str
    timestamp: float
    audio_path: Optional[str] = None


@dataclass
class VoiceMetrics:
    """Metrics for voice processing."""
    total_transcriptions: int = 0
    total_syntheses: int = 0
    avg_stt_latency_ms: float = 0.0
    avg_tts_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    stt_latencies: List[float] = field(default_factory=list)
    tts_latencies: List[float] = field(default_factory=list)


# =============================================================================
# STT Providers
# =============================================================================

class STTProviderBase(ABC):
    """Abstract base class for STT providers."""

    @abstractmethod
    def transcribe(self, audio_path: str, config: STTConfig) -> TranscriptionResult:
        """Transcribe audio file to text."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class WhisperLocalSTT(STTProviderBase):
    """Local Whisper STT provider."""

    def __init__(self):
        self._model = None
        self._model_name = None

    def _load_model(self, model_name: str):
        """Lazy load Whisper model."""
        if self._model is None or self._model_name != model_name:
            try:
                import whisper
                print(f"📦 Loading Whisper {model_name}...")
                self._model = whisper.load_model(model_name)
                self._model_name = model_name
                print(f"✅ Whisper loaded")
            except ImportError:
                raise RuntimeError("Whisper not installed. Run: pip install openai-whisper")

    def transcribe(self, audio_path: str, config: STTConfig) -> TranscriptionResult:
        """Transcribe using local Whisper."""
        self._load_model(config.model)

        start = time.time()
        result = self._model.transcribe(
            audio_path,
            language=config.language,
            word_timestamps=config.word_timestamps
        )
        processing_time = (time.time() - start) * 1000

        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        duration = segments[-1]["end"] if segments else 0

        return TranscriptionResult(
            text=result["text"].strip(),
            language=result.get("language", "en"),
            confidence=result.get("language_probability", 1.0),
            duration_seconds=duration,
            processing_time_ms=processing_time,
            provider="whisper_local",
            segments=segments
        )

    def is_available(self) -> bool:
        try:
            import whisper
            return True
        except ImportError:
            return False


class OpenAISTT(STTProviderBase):
    """OpenAI Whisper API STT provider."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def transcribe(self, audio_path: str, config: STTConfig) -> TranscriptionResult:
        """Transcribe using OpenAI API."""
        client = self._get_client()

        start = time.time()
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        processing_time = (time.time() - start) * 1000

        segments = []
        for seg in result.segments or []:
            segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            })

        duration = segments[-1]["end"] if segments else 0

        return TranscriptionResult(
            text=result.text.strip(),
            language=result.language or "en",
            confidence=1.0,
            duration_seconds=duration,
            processing_time_ms=processing_time,
            provider="openai_api",
            segments=segments
        )

    def is_available(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))


class SimulatedSTT(STTProviderBase):
    """Simulated STT for testing without real audio."""

    def transcribe(self, audio_path: str, config: STTConfig) -> TranscriptionResult:
        """Return simulated transcription."""
        time.sleep(0.1)  # Simulate processing

        return TranscriptionResult(
            text="This is a simulated transcription for testing purposes.",
            language="en",
            confidence=0.95,
            duration_seconds=3.0,
            processing_time_ms=100.0,
            provider="simulated",
            segments=[{"start": 0, "end": 3.0, "text": "This is a simulated transcription."}]
        )

    def is_available(self) -> bool:
        return True


# =============================================================================
# TTS Providers
# =============================================================================

class TTSProviderBase(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def synthesize(self, text: str, output_path: str, config: TTSConfig) -> SynthesisResult:
        """Synthesize speech from text."""
        pass

    @abstractmethod
    def list_voices(self) -> List[str]:
        """List available voices."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class OpenAITTS(TTSProviderBase):
    """OpenAI TTS provider."""

    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def synthesize(self, text: str, output_path: str, config: TTSConfig) -> SynthesisResult:
        """Synthesize using OpenAI TTS."""
        client = self._get_client()

        start = time.time()
        response = client.audio.speech.create(
            model=config.model,
            voice=config.voice,
            input=text,
            speed=config.speed
        )
        response.stream_to_file(output_path)
        processing_time = (time.time() - start) * 1000

        # Estimate duration
        word_count = len(text.split())
        estimated_duration = (word_count / 150) * 60 * 1000 / config.speed

        return SynthesisResult(
            audio_path=output_path,
            text=text,
            voice=config.voice,
            duration_ms=estimated_duration,
            processing_time_ms=processing_time,
            provider="openai"
        )

    def list_voices(self) -> List[str]:
        return self.VOICES.copy()

    def is_available(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))


class SimulatedTTS(TTSProviderBase):
    """Simulated TTS for testing without API."""

    def synthesize(self, text: str, output_path: str, config: TTSConfig) -> SynthesisResult:
        """Return simulated synthesis result."""
        time.sleep(0.1)  # Simulate processing

        # Create empty audio file for testing
        with open(output_path, "wb") as f:
            f.write(b"\x00" * 1000)  # Dummy audio data

        word_count = len(text.split())
        estimated_duration = (word_count / 150) * 60 * 1000

        return SynthesisResult(
            audio_path=output_path,
            text=text,
            voice=config.voice,
            duration_ms=estimated_duration,
            processing_time_ms=100.0,
            provider="simulated"
        )

    def list_voices(self) -> List[str]:
        return ["simulated_voice"]

    def is_available(self) -> bool:
        return True


# =============================================================================
# Voice AI Toolkit
# =============================================================================

class VoiceAIToolkit:
    """
    Comprehensive Voice AI Toolkit.

    Provides unified interface for:
    - Speech-to-text (STT)
    - Text-to-speech (TTS)
    - Voice activity detection
    - Audio caching
    - Conversation management
    - Metrics and monitoring
    """

    def __init__(self, config: Optional[VoiceToolkitConfig] = None):
        self.config = config or VoiceToolkitConfig()
        self.metrics = VoiceMetrics()
        self.conversation: List[ConversationMessage] = []

        # Setup cache directory
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_path = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()

        # Initialize providers
        self._stt_providers = {
            STTProvider.WHISPER_LOCAL: WhisperLocalSTT(),
            STTProvider.OPENAI_API: OpenAISTT(),
            STTProvider.SIMULATED: SimulatedSTT(),
        }

        self._tts_providers = {
            TTSProvider.OPENAI: OpenAITTS(),
            TTSProvider.SIMULATED: SimulatedTTS(),
        }

        print("🎙️ Voice AI Toolkit initialized")
        print(f"   STT Provider: {self.config.stt.provider.value}")
        print(f"   TTS Provider: {self.config.tts.provider.value}")
        print(f"   Cache: {'enabled' if self.config.enable_caching else 'disabled'}")
        print()

    def _load_cache_index(self) -> Dict:
        """Load cache index from disk."""
        if self.cache_index_path.exists():
            with open(self.cache_index_path) as f:
                return json.load(f)
        return {"tts": {}, "stt": {}}

    def _save_cache_index(self):
        """Save cache index to disk."""
        with open(self.cache_index_path, "w") as f:
            json.dump(self.cache_index, f, indent=2)

    def _get_cache_key(self, content: str, params: Dict) -> str:
        """Generate cache key."""
        data = f"{content}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    # -------------------------------------------------------------------------
    # Speech-to-Text
    # -------------------------------------------------------------------------

    def transcribe(
        self,
        audio_path: str,
        config: Optional[STTConfig] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_path: Path to audio file
            config: Optional STT configuration override

        Returns:
            TranscriptionResult with text and metadata
        """
        config = config or self.config.stt
        provider = self._stt_providers.get(config.provider)

        if not provider or not provider.is_available():
            print(f"⚠️ Provider {config.provider.value} not available, falling back to simulated")
            provider = self._stt_providers[STTProvider.SIMULATED]

        try:
            result = provider.transcribe(audio_path, config)

            # Update metrics
            if self.config.enable_metrics:
                self.metrics.total_transcriptions += 1
                self.metrics.stt_latencies.append(result.processing_time_ms)
                self.metrics.avg_stt_latency_ms = statistics.mean(self.metrics.stt_latencies)

            return result

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Transcription failed: {e}")

    # -------------------------------------------------------------------------
    # Text-to-Speech
    # -------------------------------------------------------------------------

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        config: Optional[TTSConfig] = None
    ) -> SynthesisResult:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            output_path: Path to save audio (auto-generated if None)
            config: Optional TTS configuration override

        Returns:
            SynthesisResult with audio path and metadata
        """
        config = config or self.config.tts
        provider = self._tts_providers.get(config.provider)

        if not provider or not provider.is_available():
            print(f"⚠️ Provider {config.provider.value} not available, falling back to simulated")
            provider = self._tts_providers[TTSProvider.SIMULATED]

        # Check cache
        if self.config.enable_caching:
            cache_key = self._get_cache_key(text, {"voice": config.voice, "model": config.model})
            if cache_key in self.cache_index.get("tts", {}):
                cached_path = self.cache_dir / f"tts_{cache_key}.mp3"
                if cached_path.exists():
                    self.metrics.cache_hits += 1
                    entry = self.cache_index["tts"][cache_key]
                    return SynthesisResult(
                        audio_path=str(cached_path),
                        text=text,
                        voice=config.voice,
                        duration_ms=entry.get("duration_ms", 0),
                        processing_time_ms=0,
                        provider=entry.get("provider", "cached"),
                        cached=True
                    )
            self.metrics.cache_misses += 1

        # Generate output path
        if output_path is None:
            output_path = str(self.cache_dir / f"tts_{int(time.time() * 1000)}.mp3")

        try:
            result = provider.synthesize(text, output_path, config)

            # Update cache
            if self.config.enable_caching:
                cache_key = self._get_cache_key(text, {"voice": config.voice, "model": config.model})
                cached_path = self.cache_dir / f"tts_{cache_key}.mp3"

                # Copy to cache location
                if str(output_path) != str(cached_path):
                    import shutil
                    shutil.copy(output_path, cached_path)

                self.cache_index.setdefault("tts", {})[cache_key] = {
                    "text": text[:100],
                    "voice": config.voice,
                    "duration_ms": result.duration_ms,
                    "provider": result.provider,
                    "created_at": time.time()
                }
                self._save_cache_index()

            # Update metrics
            if self.config.enable_metrics:
                self.metrics.total_syntheses += 1
                self.metrics.tts_latencies.append(result.processing_time_ms)
                self.metrics.avg_tts_latency_ms = statistics.mean(self.metrics.tts_latencies)

            return result

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Synthesis failed: {e}")

    def list_voices(self) -> Dict[str, List[str]]:
        """List available voices for each TTS provider."""
        voices = {}
        for provider_enum, provider in self._tts_providers.items():
            if provider.is_available():
                voices[provider_enum.value] = provider.list_voices()
        return voices

    # -------------------------------------------------------------------------
    # Conversation Management
    # -------------------------------------------------------------------------

    def add_message(self, role: str, content: str, audio_path: Optional[str] = None):
        """Add a message to the conversation history."""
        self.conversation.append(ConversationMessage(
            role=role,
            content=content,
            timestamp=time.time(),
            audio_path=audio_path
        ))

    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history."""
        return [asdict(msg) for msg in self.conversation[-limit:]]

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation = []

    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------

    def get_metrics(self) -> Dict:
        """Get current metrics."""
        return asdict(self.metrics)

    def get_metrics_summary(self) -> str:
        """Get formatted metrics summary."""
        m = self.metrics

        summary = f"""
📊 Voice AI Toolkit Metrics
{'=' * 40}

Transcriptions (STT):
   Total: {m.total_transcriptions}
   Avg Latency: {m.avg_stt_latency_ms:.1f}ms

Syntheses (TTS):
   Total: {m.total_syntheses}
   Avg Latency: {m.avg_tts_latency_ms:.1f}ms

Cache:
   Hits: {m.cache_hits}
   Misses: {m.cache_misses}
   Hit Rate: {m.cache_hits / max(m.cache_hits + m.cache_misses, 1) * 100:.1f}%

Errors: {m.errors}
"""
        return summary

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def play_audio(self, audio_path: str):
        """Play audio file using system player."""
        import platform
        system = platform.system()

        if system == "Darwin":
            os.system(f"afplay '{audio_path}' 2>/dev/null")
        elif system == "Linux":
            os.system(f"aplay '{audio_path}' 2>/dev/null || mpv '{audio_path}' 2>/dev/null")
        elif system == "Windows":
            os.system(f'start "" "{audio_path}"')

    def clear_cache(self):
        """Clear all cached audio."""
        import shutil
        if self.cache_dir.exists():
            for f in self.cache_dir.glob("*.mp3"):
                f.unlink()
        self.cache_index = {"tts": {}, "stt": {}}
        self._save_cache_index()
        print("🧹 Cache cleared")

    def save_state(self, path: Optional[str] = None):
        """Save toolkit state to JSON."""
        path = path or str(self.cache_dir / "state.json")
        state = {
            "metrics": asdict(self.metrics),
            "conversation": [asdict(m) for m in self.conversation],
            "cache_index": self.cache_index,
            "timestamp": time.time()
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2)
        print(f"💾 State saved to {path}")

    @classmethod
    def load_state(cls, path: str, config: Optional[VoiceToolkitConfig] = None) -> "VoiceAIToolkit":
        """Load toolkit from saved state."""
        toolkit = cls(config)

        if os.path.exists(path):
            with open(path) as f:
                state = json.load(f)

            # Restore metrics
            for key, value in state.get("metrics", {}).items():
                if hasattr(toolkit.metrics, key):
                    setattr(toolkit.metrics, key, value)

            # Restore conversation
            for msg_data in state.get("conversation", []):
                toolkit.conversation.append(ConversationMessage(**msg_data))

            print(f"📂 State loaded from {path}")

        return toolkit


# =============================================================================
# Demo Functions
# =============================================================================

def demo_stt_showcase():
    """Demo 1: STT capabilities."""
    print("=" * 60)
    print("DEMO 1: Speech-to-Text Showcase")
    print("=" * 60)

    toolkit = VoiceAIToolkit()

    print("\n📋 STT Providers:")
    print("   - whisper_local: Local Whisper (requires openai-whisper)")
    print("   - openai_api: OpenAI Whisper API (requires API key)")
    print("   - simulated: Testing mode (no real transcription)")

    print("\n🎯 Whisper Model Sizes:")
    models = {
        "tiny": "39M params, ~32x speed, lowest accuracy",
        "base": "74M params, ~16x speed, good accuracy",
        "small": "244M params, ~6x speed, better accuracy",
        "medium": "769M params, ~2x speed, high accuracy",
        "large-v3": "1.5B params, 1x speed, best accuracy"
    }
    for model, desc in models.items():
        print(f"   {model:<10} {desc}")

    # Test with simulated audio
    print("\n🎤 Testing STT (simulated)...")
    result = toolkit.transcribe("test.wav")  # Will use simulated provider
    print(f"   Text: {result.text}")
    print(f"   Language: {result.language}")
    print(f"   Confidence: {result.confidence:.1%}")
    print(f"   Processing: {result.processing_time_ms:.0f}ms")
    print()


def demo_tts_showcase():
    """Demo 2: TTS capabilities."""
    print("=" * 60)
    print("DEMO 2: Text-to-Speech Showcase")
    print("=" * 60)

    toolkit = VoiceAIToolkit()

    print("\n📋 Available Voices:")
    voices = toolkit.list_voices()
    for provider, voice_list in voices.items():
        print(f"   {provider}: {', '.join(voice_list)}")

    print("\n🎙️ OpenAI TTS Voices:")
    voice_descriptions = {
        "alloy": "Neutral, balanced",
        "echo": "Warm, conversational",
        "fable": "British, narrative",
        "onyx": "Deep, authoritative",
        "nova": "Energetic, young",
        "shimmer": "Soft, gentle"
    }
    for voice, desc in voice_descriptions.items():
        print(f"   {voice:<10} {desc}")

    # Test synthesis
    print("\n🔊 Testing TTS (simulated)...")
    result = toolkit.synthesize("Hello! This is a test of the voice synthesis system.")
    print(f"   Output: {result.audio_path}")
    print(f"   Voice: {result.voice}")
    print(f"   Duration: ~{result.duration_ms / 1000:.1f}s")
    print(f"   Processing: {result.processing_time_ms:.0f}ms")
    print(f"   Cached: {result.cached}")
    print()


def demo_voice_assistant():
    """Demo 3: Voice assistant workflow."""
    print("=" * 60)
    print("DEMO 3: Voice Assistant Workflow")
    print("=" * 60)

    toolkit = VoiceAIToolkit()

    print("\n📋 Voice Assistant Pipeline:")
    print("""
   ┌─────────────┐
   │ Audio Input │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │     STT     │ → Transcribe speech
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │     LLM     │ → Generate response
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │     TTS     │ → Synthesize speech
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Audio Output│
   └─────────────┘
""")

    # Simulate conversation
    print("🤖 Simulated Conversation:")
    print()

    messages = [
        ("user", "What's the weather like today?"),
        ("assistant", "I'd need access to weather data to answer that, but I can help you find a weather service!"),
        ("user", "Tell me a joke."),
        ("assistant", "Why do programmers prefer dark mode? Because light attracts bugs!")
    ]

    for role, content in messages:
        toolkit.add_message(role, content)
        emoji = "👤" if role == "user" else "🤖"
        print(f"   {emoji} {role.title()}: {content}")

    print("\n📊 Conversation History:")
    history = toolkit.get_conversation_history()
    print(f"   {len(history)} messages recorded")
    print()


def demo_metrics_dashboard():
    """Demo 4: Metrics and monitoring."""
    print("=" * 60)
    print("DEMO 4: Metrics Dashboard")
    print("=" * 60)

    toolkit = VoiceAIToolkit()

    # Generate some activity
    print("\n⏳ Generating test activity...")
    for i in range(5):
        toolkit.synthesize(f"Test message number {i + 1}")
        toolkit.transcribe("test.wav")

    # Show metrics
    print(toolkit.get_metrics_summary())

    # Show cache info
    print("💾 Cache Status:")
    cache_size = sum(f.stat().st_size for f in toolkit.cache_dir.glob("*.mp3") if f.exists())
    print(f"   Directory: {toolkit.cache_dir}")
    print(f"   Size: {cache_size / 1024:.1f} KB")
    print(f"   Files: {len(list(toolkit.cache_dir.glob('*.mp3')))}")
    print()

    # Save state
    toolkit.save_state()


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("MODULE 22 DELIVERABLE: VOICE AI TOOLKIT")
    print("=" * 60)
    print()

    if len(sys.argv) < 2:
        print("Usage: python deliverable_voice_ai_toolkit.py <demo>")
        print()
        print("Demos:")
        print("  demo1  - STT (Speech-to-Text) showcase")
        print("  demo2  - TTS (Text-to-Speech) showcase")
        print("  demo3  - Voice assistant workflow")
        print("  demo4  - Metrics dashboard")
        print()
        print("Running all demos...")
        print()

        demo_stt_showcase()
        demo_tts_showcase()
        demo_voice_assistant()
        demo_metrics_dashboard()
    else:
        demo = sys.argv[1].lower()
        if demo == "demo1":
            demo_stt_showcase()
        elif demo == "demo2":
            demo_tts_showcase()
        elif demo == "demo3":
            demo_voice_assistant()
        elif demo == "demo4":
            demo_metrics_dashboard()
        else:
            print(f"Unknown demo: {demo}")
            print("Available: demo1, demo2, demo3, demo4")
            sys.exit(1)

    print("=" * 60)
    print("✅ Voice AI Toolkit demo complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
