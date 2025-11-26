# Module 22: Speech AI Examples

This directory contains working code examples for Module 22: Speech AI.

## Prerequisites

```bash
pip install -r requirements.txt
```

**Optional** (for full functionality):
- OpenAI API key for API-based STT/TTS
- `openai-whisper` for local transcription
- Audio input device for live recording

## Examples

### Example 1: Speech-to-Text with Whisper
**File**: `01_speech_to_text.py`
**Description**: Transcription using OpenAI's Whisper model with multiple size options
**Run**: `python 01_speech_to_text.py [audio_file.mp3]`

Features:
- Basic transcription
- Word-level timestamps
- Language detection
- Model size comparison

### Example 2: Text-to-Speech
**File**: `02_text_to_speech.py`
**Description**: Speech synthesis using OpenAI TTS with multiple voices
**Run**: `python 02_text_to_speech.py [1|2|3|4]`

Features:
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- TTS caching for efficiency
- Voice comparison
- Use case recommendations

### Example 3: Voice Assistant
**File**: `03_voice_assistant.py`
**Description**: Complete voice-in, voice-out AI assistant
**Run**: `python 03_voice_assistant.py [1|2|3|4]`

Features:
- Full STT → LLM → TTS pipeline
- Conversation memory
- Interactive text mode
- Latency tracking

## Deliverable

### Voice AI Toolkit
**File**: `deliverable_voice_ai_toolkit.py`
**Description**: Production-ready toolkit for building voice-enabled AI applications
**Run**: `python deliverable_voice_ai_toolkit.py [demo1|demo2|demo3|demo4]`

See `DELIVERABLE_README.md` for detailed documentation.

## Expected Output

### Example 1 (STT)
```
📝 Transcription:
   Hello! This is a test of the Whisper speech recognition system.

📊 Metadata:
   Language: en (99.2% confidence)
   Duration: 5.2s
   Processing time: 1.24s
   Speed: 4.2x real-time
```

### Example 2 (TTS)
```
🎙️ Available OpenAI TTS Voices:

   alloy      Neutral, balanced
   echo       Warm, conversational
   fable      British, narrative
   onyx       Deep, authoritative
   nova       Energetic, young
   shimmer    Soft, gentle
```

### Example 3 (Voice Assistant)
```
📋 Voice Assistant Pipeline:

   Microphone → Whisper (STT) → GPT-4 (LLM) → OpenAI TTS → Speaker

⏱️ Target Latencies:
   STT (Whisper):  100-500ms
   LLM (GPT-4):    200-500ms
   TTS (OpenAI):   200-400ms
   Total:          500-1400ms
```

## Notes

### API Keys
- Set `OPENAI_API_KEY` for OpenAI services (STT API, TTS, LLM)
- Examples work in simulated mode without API keys

### Whisper Models
| Model | Params | VRAM | Speed | Use Case |
|-------|--------|------|-------|----------|
| tiny | 39M | ~1GB | ~32x | Real-time, low accuracy |
| base | 74M | ~1GB | ~16x | Development, good accuracy |
| small | 244M | ~2GB | ~6x | Production, better accuracy |
| medium | 769M | ~5GB | ~2x | High accuracy |
| large-v3 | 1.5B | ~10GB | 1x | Best accuracy |

### TTS Voices
- **nova**: Best for voice assistants (energetic, clear)
- **onyx**: Best for announcements (deep, authoritative)
- **shimmer**: Best for meditation/relaxation (soft, gentle)
- **fable**: Best for storytelling (British, narrative)

## Related Theory

See `docs/curriculum/notes/module_22_speech_ai.md` for comprehensive theory on:
- Whisper architecture and training
- TTS technologies and providers
- Voice assistant design patterns
- Real-time streaming considerations
- Production deployment strategies
