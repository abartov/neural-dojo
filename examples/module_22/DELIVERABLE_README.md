# Module 22 Deliverable: Voice AI Toolkit

**A comprehensive toolkit for building voice-enabled AI applications with speech-to-text, text-to-speech, and voice assistant capabilities.**

## Features

- **Multi-provider STT**: Local Whisper, OpenAI API, or simulated mode
- **Multi-provider TTS**: OpenAI TTS with 6 voices, extensible for ElevenLabs
- **Smart caching**: Hash-based TTS caching to avoid regenerating repeated content
- **Metrics tracking**: Latency, cache hit rates, error monitoring
- **Conversation management**: Multi-turn dialogue with history
- **Graceful degradation**: Works in simulated mode without API keys

## Quick Start

```bash
# Run all demos
python deliverable_voice_ai_toolkit.py

# Individual demos
python deliverable_voice_ai_toolkit.py demo1  # STT showcase
python deliverable_voice_ai_toolkit.py demo2  # TTS showcase
python deliverable_voice_ai_toolkit.py demo3  # Voice assistant workflow
python deliverable_voice_ai_toolkit.py demo4  # Metrics dashboard
```

## STT Providers

| Provider | Requirements | Best For |
|----------|-------------|----------|
| `whisper_local` | `openai-whisper` | Offline processing, privacy |
| `openai_api` | `OPENAI_API_KEY` | Fast, production use |
| `simulated` | None | Testing, development |

### Whisper Model Selection

```
Model      Params    Speed    Accuracy    Use Case
-------    ------    -----    --------    --------
tiny       39M       ~32x     Low         Real-time, edge devices
base       74M       ~16x     Good        Development, testing
small      244M      ~6x      Better      Production (balanced)
medium     769M      ~2x      High        Quality-critical apps
large-v3   1.5B      1x       Best        Maximum accuracy
```

## TTS Voices

| Voice | Character | Best For |
|-------|-----------|----------|
| `alloy` | Neutral, balanced | General purpose |
| `echo` | Warm, conversational | Chat interfaces |
| `fable` | British, narrative | Storytelling, audiobooks |
| `onyx` | Deep, authoritative | Announcements, news |
| `nova` | Energetic, young | Voice assistants |
| `shimmer` | Soft, gentle | Meditation, ASMR |

## Usage Examples

### Basic STT
```python
from deliverable_voice_ai_toolkit import VoiceAIToolkit, STTConfig

toolkit = VoiceAIToolkit(stt_provider="openai_api")
result = toolkit.transcribe("audio.mp3")
print(f"Text: {result.text}")
print(f"Language: {result.language}")
```

### Basic TTS
```python
from deliverable_voice_ai_toolkit import VoiceAIToolkit, TTSConfig

toolkit = VoiceAIToolkit(tts_provider="openai")
config = TTSConfig(voice="nova", model="tts-1")
result = toolkit.synthesize("Hello, how can I help you?", config=config)
print(f"Audio saved to: {result.audio_path}")
```

### Voice Conversation
```python
from deliverable_voice_ai_toolkit import VoiceAIToolkit

toolkit = VoiceAIToolkit()

# Add conversation turns
toolkit.add_conversation_turn("user", "What's the weather?")
toolkit.add_conversation_turn("assistant", "I can help you check the weather.")

# Get conversation history
history = toolkit.get_conversation_history()
```

## Metrics & Monitoring

```python
# Get performance metrics
print(toolkit.get_metrics_summary())

# Output:
# Transcriptions (STT): 15, Avg Latency: 245ms
# Syntheses (TTS): 12, Avg Latency: 312ms
# Cache: Hit Rate 67.3%
# Errors: 0
```

## Caching

TTS responses are automatically cached based on:
- Text content
- Voice selection
- Model selection

Cache location: `.voice_toolkit/tts_*.mp3`

Clear cache:
```python
toolkit.cache.clear_cache()
```

## Architecture

```
VoiceAIToolkit
├── STTProvider (abstract)
│   ├── WhisperLocalSTT (local inference)
│   ├── OpenAISTT (API-based)
│   └── SimulatedSTT (testing)
├── TTSProvider (abstract)
│   ├── OpenAITTS (6 voices)
│   └── SimulatedTTS (testing)
├── TTSCache (hash-based caching)
├── ConversationManager (dialogue history)
└── MetricsTracker (latency, errors)
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI STT/TTS

### Dataclasses
```python
@dataclass
class STTConfig:
    model: str = "base"        # Whisper model size
    language: str = None       # Auto-detect if None
    task: str = "transcribe"   # or "translate"

@dataclass
class TTSConfig:
    voice: str = "nova"        # OpenAI voice
    model: str = "tts-1"       # or "tts-1-hd"
    speed: float = 1.0         # 0.25 to 4.0
```

## Performance Benchmarks

| Operation | Provider | Typical Latency |
|-----------|----------|-----------------|
| STT | Whisper base (local) | 200-500ms |
| STT | OpenAI API | 100-300ms |
| TTS | OpenAI tts-1 | 200-400ms |
| TTS | OpenAI tts-1-hd | 400-600ms |
| TTS | Cached | <10ms |

## Error Handling

```python
try:
    result = toolkit.transcribe("audio.mp3")
except FileNotFoundError:
    print("Audio file not found")
except Exception as e:
    print(f"Transcription failed: {e}")
```

## Dependencies

```
openai>=1.0.0           # OpenAI API client
numpy>=1.24.0           # Audio processing
# Optional:
openai-whisper>=20231117  # Local Whisper
librosa>=0.10.0          # Audio loading
```

## Files

```
module_22/
├── deliverable_voice_ai_toolkit.py  # Main deliverable (700+ lines)
├── DELIVERABLE_README.md            # This file
├── requirements.txt                 # Dependencies
├── .gitignore                       # Excludes .voice_toolkit/
├── 01_speech_to_text.py            # STT example
├── 02_text_to_speech.py            # TTS example
└── 03_voice_assistant.py           # Voice assistant example
```

---

**Time**: ~4 hours | **Lines**: 700+ | **Author**: Neural Dojo
