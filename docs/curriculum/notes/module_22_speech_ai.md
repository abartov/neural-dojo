# Module 22: Speech AI - Voice Interfaces for the AI Era
# Or: Teaching Computers to Listen (Finally)

**Last Updated**: 2025-11-26
**Status**: Complete
**Reading Time**: 6-7 hours
**Prerequisites**: Phase 4 complete

---

## Learning Objectives

By the end of this module, you will:
- Master **Whisper** for speech-to-text (STT) transcription
- Build text-to-speech (TTS) systems with multiple providers
- Understand voice cloning and neural voice synthesis
- Implement real-time transcription pipelines
- Build voice-enabled AI assistants
- Deploy production speech applications
- Understand the architecture behind modern speech models

---

## Introduction: The Voice Revolution

### Why Voice Matters Now

For decades, voice interfaces felt like science fiction—or at best, frustrating. "I'm sorry, I didn't catch that" became a meme. But **2022-2024 changed everything**.

**What happened?**
1. **Whisper** (OpenAI, 2022): First speech model that actually works reliably
2. **ElevenLabs** (2022): Voice cloning that sounds human
3. **GPT-4 + Voice** (2023): Conversational AI that can hear and speak
4. **Real-time APIs** (2024): Sub-second latency for live conversations

**The result**: Voice is no longer a novelty—it's becoming the primary interface for AI.

### The Speech AI Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    SPEECH AI PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Microphone] ──► [STT: Whisper] ──► [Text]                 │
│                                         │                    │
│                                         ▼                    │
│                                    [LLM: Claude/GPT]         │
│                                         │                    │
│                                         ▼                    │
│  [Speaker] ◄── [TTS: ElevenLabs] ◄── [Response Text]        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Components**:
1. **Speech-to-Text (STT)**: Convert audio → text (Whisper, Deepgram, AssemblyAI)
2. **Language Model**: Process text → generate response (Claude, GPT-4)
3. **Text-to-Speech (TTS)**: Convert response → audio (ElevenLabs, OpenAI TTS)

---

## 🎤 Speech-to-Text (STT): Whisper

### What is Whisper?

**Whisper** is OpenAI's speech recognition model, released in **September 2022**. It's trained on 680,000 hours of multilingual audio and achieves human-level accuracy.

**Key features**:
- **99 languages** supported
- **Automatic language detection**
- **Punctuation and capitalization** (unlike old ASR)
- **Robust to noise, accents, and background speech**
- **Open-source** (run locally, no API costs!)

### Whisper Model Sizes

| Model | Parameters | English-Only | VRAM | Relative Speed |
|-------|-----------|--------------|------|----------------|
| `tiny` | 39M | ✅ | ~1 GB | ~32x |
| `base` | 74M | ✅ | ~1 GB | ~16x |
| `small` | 244M | ✅ | ~2 GB | ~6x |
| `medium` | 769M | ✅ | ~5 GB | ~2x |
| `large` | 1550M | ❌ | ~10 GB | 1x |
| `large-v2` | 1550M | ❌ | ~10 GB | 1x |
| `large-v3` | 1550M | ❌ | ~10 GB | 1x |

**Recommendation**:
- **Development**: `base` or `small` (fast iteration)
- **Production (English)**: `medium` or `large-v3`
- **Production (multilingual)**: `large-v3`

### Basic Whisper Usage

```python
import whisper

# Load model (downloads on first run)
model = whisper.load_model("base")

# Transcribe audio file
result = model.transcribe("audio.mp3")

print(result["text"])
# "Hello, this is a test of the Whisper speech recognition system."

# With more details
print(result["language"])  # "en"
print(result["segments"])  # List of timestamped segments
```

### Whisper with Timestamps

```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("podcast.mp3", word_timestamps=True)

# Access word-level timestamps
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")

    # Word-level timestamps (if available)
    if "words" in segment:
        for word in segment["words"]:
            print(f"  [{word['start']:.2f}s] {word['word']}")
```

**Output**:
```
[0.00s - 4.52s] Hello, this is a test of the Whisper system.
  [0.00s] Hello,
  [0.45s] this
  [0.68s] is
  [0.89s] a
  [1.02s] test
  ...
```

### Language Detection and Translation

```python
import whisper

model = whisper.load_model("large-v3")

# Transcribe with auto language detection
result = model.transcribe("french_audio.mp3")
print(f"Detected language: {result['language']}")
print(f"Text: {result['text']}")

# Translate non-English to English
result = model.transcribe(
    "french_audio.mp3",
    task="translate"  # Translate to English
)
print(f"Translation: {result['text']}")
```

### OpenAI Whisper API

For production without GPU infrastructure:

```python
from openai import OpenAI

client = OpenAI()

# Transcribe audio file
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"]
    )

print(transcript.text)
print(transcript.words)  # Word-level timestamps
```

**Pricing** (OpenAI API):
- $0.006 per minute of audio
- 25 MB file size limit
- Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm

### Faster Whisper (Production Optimization)

**faster-whisper** uses CTranslate2 for 4x faster inference:

```python
from faster_whisper import WhisperModel

# Load with optimizations
model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16"  # or "int8" for even faster
)

# Transcribe
segments, info = model.transcribe("audio.mp3", beam_size=5)

print(f"Detected language: {info.language} ({info.language_probability:.2%})")

for segment in segments:
    print(f"[{segment.start:.2f}s → {segment.end:.2f}s] {segment.text}")
```

**Performance comparison** (1-hour audio):
- Whisper (PyTorch): ~25 minutes
- faster-whisper (CTranslate2): ~6 minutes
- **4x speedup!**

---

## Did You Know? The History of Speech Recognition

### The 50-Year Journey to Whisper

Speech recognition has been "almost working" for decades. Here's the journey:

**1952**: Bell Labs builds "Audrey" - recognizes digits 0-9 spoken by its creator (and only its creator).

**1970s**: DARPA funds speech research. CMU builds HARPY - 1,000-word vocabulary, 90% accuracy (controlled conditions).

**1980s**: Hidden Markov Models (HMMs) become dominant. IBM builds "Tangora" - 20,000 words but requires pausing between each word.

**1990s**: Dragon NaturallySpeaking launches (1997). First consumer dictation software. Terrible but revolutionary.

**2000s**: Statistical models improve. Google Voice Search launches (2008). Still frustrating for users.

**2010s**: Deep learning arrives. Google's neural ASR (2012) cuts error rate by 25%. Apple launches Siri (2011) - "I didn't quite catch that" becomes a meme.

**2022**: OpenAI releases Whisper. **Game over.**

**What made Whisper different?**
1. **Scale**: 680,000 hours of training data (vs ~10,000 for previous SOTA)
2. **Multitask**: Trained on transcription, translation, AND language detection simultaneously
3. **Robustness**: Deliberately trained on noisy, real-world audio
4. **Open-source**: Anyone can run it locally

**The numbers**:
- Whisper matches or exceeds commercial APIs on most benchmarks
- 99 languages supported
- Word error rate (WER) < 5% on clean English
- Downloads: 100M+ on Hugging Face

### The Whisper Release Drama

When OpenAI released Whisper in September 2022, it caused controversy:

**The good**:
- Completely open-source (MIT license)
- Model weights freely downloadable
- No API lock-in

**The controversy**:
- Trained on YouTube videos (copyright concerns?)
- No training data release (how was it collected?)
- Immediately obsoleted commercial speech APIs

**Industry reaction**:
- **Deepgram, AssemblyAI**: Scrambled to improve their models
- **Google**: Accelerated USM (Universal Speech Model) development
- **Startups**: Pivoted from "building ASR" to "building on Whisper"

**The lesson**: Open-source AI can disrupt billion-dollar markets overnight.

### The Speaker Who Taught Machines to Listen

**Geoffrey Hinton**, the "godfather of deep learning," wasn't just important for vision—his work enabled modern speech recognition too.

In 2012, Hinton's team (with Navdeep Jaitly and Abdel-rahman Mohamed) showed that deep neural networks could dramatically outperform HMMs for speech recognition. Their paper "Deep Neural Networks for Acoustic Modeling in Speech Recognition" is cited 15,000+ times.

**The irony**: Hinton later left Google and warned about AI dangers. The speech systems his work enabled now power billions of voice assistants worldwide.

---

## 🔊 Text-to-Speech (TTS): Making AI Speak

### The TTS Landscape (2024)

| Provider | Quality | Latency | Price | Voice Cloning |
|----------|---------|---------|-------|---------------|
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | 500ms | $0.30/1K chars | ✅ Best |
| **OpenAI TTS** | ⭐⭐⭐⭐ | 300ms | $0.015/1K chars | ❌ |
| **Amazon Polly** | ⭐⭐⭐ | 200ms | $0.004/1K chars | ❌ |
| **Google TTS** | ⭐⭐⭐ | 250ms | $0.004/1K chars | ❌ |
| **Coqui TTS** | ⭐⭐⭐⭐ | Varies | Free (open-source) | ✅ |
| **Bark** | ⭐⭐⭐⭐ | 2000ms+ | Free (open-source) | ✅ |

**Recommendation**:
- **Production (quality focus)**: ElevenLabs
- **Production (cost focus)**: OpenAI TTS
- **Development/offline**: Coqui TTS or Bark

### OpenAI TTS

The easiest high-quality TTS option:

```python
from openai import OpenAI
from pathlib import Path

client = OpenAI()

# Generate speech
response = client.audio.speech.create(
    model="tts-1",  # or "tts-1-hd" for higher quality
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    input="Hello! This is a test of OpenAI's text-to-speech system.",
    speed=1.0  # 0.25 to 4.0
)

# Save to file
speech_file = Path("output.mp3")
response.stream_to_file(speech_file)
```

**Voices**:
- `alloy`: Neutral, balanced
- `echo`: Warm, conversational
- `fable`: British, narrative
- `onyx`: Deep, authoritative
- `nova`: Energetic, young
- `shimmer`: Soft, gentle

**Models**:
- `tts-1`: Optimized for speed (~300ms latency)
- `tts-1-hd`: Higher quality, slower (~500ms)

### ElevenLabs (Premium Quality)

ElevenLabs offers the most human-like TTS:

```python
from elevenlabs import generate, save, set_api_key

set_api_key("your-api-key")

# Generate with default voice
audio = generate(
    text="Welcome to the future of voice synthesis!",
    voice="Rachel",  # Or custom voice ID
    model="eleven_multilingual_v2"
)

# Save to file
save(audio, "elevenlabs_output.mp3")
```

**Voice cloning** (ElevenLabs' killer feature):

```python
from elevenlabs import clone, generate

# Clone a voice from audio samples
voice = clone(
    name="My Custom Voice",
    files=["sample1.mp3", "sample2.mp3", "sample3.mp3"],
    description="Professional male narrator"
)

# Generate with cloned voice
audio = generate(
    text="This sounds just like the original speaker!",
    voice=voice
)
```

### Streaming TTS for Real-Time

For voice assistants, you need streaming:

```python
from openai import OpenAI

client = OpenAI()

# Stream audio chunks
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="This is a longer text that will be streamed in chunks...",
)

# Write streaming response
with open("streamed_output.mp3", "wb") as f:
    for chunk in response.iter_bytes(chunk_size=1024):
        f.write(chunk)
        # In production: Send chunk to audio player immediately
```

### Open-Source TTS: Coqui

**Coqui TTS** is the best open-source option:

```python
from TTS.api import TTS

# Initialize TTS (downloads model on first run)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

# Generate speech
tts.tts_to_file(
    text="Open source text to speech is amazing!",
    file_path="coqui_output.wav"
)

# With voice cloning
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
tts.tts_to_file(
    text="This uses my cloned voice!",
    speaker_wav="my_voice_sample.wav",
    language="en",
    file_path="cloned_output.wav"
)
```

---

## Did You Know? The Voice Cloning Revolution

### ElevenLabs: From Startup to Industry Disruptor

**ElevenLabs** was founded in **2022** by two former Google engineers: **Piotr Dabkowski** and **Mati Staniszewski**, both from Poland.

**The origin story**: Dabkowski and Staniszewski were frustrated watching poorly dubbed movies. They thought: "What if we could make dubbing sound natural?"

**January 2023**: They launched their voice cloning API and went viral. Within weeks:
- **1 million users** signed up
- **$2M+ revenue** in first month
- Controversy erupted over potential misuse

**The controversy**: Users started cloning celebrity voices without permission. ElevenLabs had to add voice verification and content moderation.

**The funding**:
- 2023 (Series A): $19M
- 2024 (Series B): $80M at **$1B+ valuation**
- Total: $100M+ raised in 2 years

**The technology**: Their secret sauce is "Instant Voice Cloning" - create a convincing clone from just **30 seconds of audio**. Previous tech required hours of samples.

**Famous uses**:
- Dubbing studios cloning actors' voices for foreign releases
- Audiobook narrators scaling their work
- Video game studios creating NPC dialogue at scale
- Podcasters creating "AI co-hosts"

### The Deepfake Dilemma

With great voice cloning comes great responsibility. The technology enables:

**Good uses**:
- Accessibility (voice for people who lost theirs)
- Entertainment (dubbing, games, audiobooks)
- Education (personalized learning)
- Productivity (quick voice content creation)

**Concerning uses**:
- Political deepfakes (fake speeches)
- Fraud (impersonating family members)
- Scams (fake CEO phone calls)
- Misinformation (fake news reports)

**The response**:
- ElevenLabs: Voice verification, content policies, watermarking
- OpenAI: No voice cloning in TTS API (for now)
- Legislation: Several countries exploring AI voice laws

**The numbers**:
- Voice phishing scams increased **300%** from 2022-2024
- $25M+ lost to AI voice fraud in 2023 (FBI estimate)
- Detection tools are ~70-80% accurate (improving)

### The Race for Real-Time Voice AI

**2024 was the year of real-time voice AI**:

**GPT-4o Voice** (May 2024):
- Sub-200ms response time
- Can hear emotion, pace, background noise
- Responds with appropriate tone
- Feels like talking to a human

**Google Gemini Live** (2024):
- Real-time multimodal conversations
- Can see and hear simultaneously
- Integrated with Android

**The technical challenge**: End-to-end latency must be <500ms for natural conversation:
- STT: ~100ms
- LLM inference: ~200ms
- TTS: ~100ms
- Network: ~100ms

**The breakthrough**: OpenAI's GPT-4o uses a single model for audio-to-audio, bypassing the STT→LLM→TTS pipeline entirely. Latency dropped from ~2 seconds to ~200ms.

---

## 🎙️ Real-Time Transcription

### Building a Live Transcription System

For real-time applications (voice assistants, meeting transcription), you need streaming:

```python
import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import threading
import queue

class RealTimeTranscriber:
    """Real-time speech transcription using Whisper."""

    def __init__(self, model_size: str = "base"):
        self.model = WhisperModel(model_size, device="cuda", compute_type="float16")
        self.audio_queue = queue.Queue()
        self.is_running = False

        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1

    def start_recording(self):
        """Start capturing audio from microphone."""
        self.is_running = True

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        print("Listening... (Ctrl+C to stop)")

        try:
            audio_buffer = []
            silence_threshold = 0.01
            silence_duration = 0

            while self.is_running:
                # Read audio chunk
                data = stream.read(self.chunk_size)
                audio_np = np.frombuffer(data, dtype=np.float32)

                # Detect speech vs silence
                volume = np.abs(audio_np).mean()

                if volume > silence_threshold:
                    audio_buffer.append(audio_np)
                    silence_duration = 0
                else:
                    silence_duration += self.chunk_size / self.sample_rate

                    # If silence > 0.5s and we have audio, transcribe
                    if silence_duration > 0.5 and audio_buffer:
                        audio_data = np.concatenate(audio_buffer)
                        self.transcribe_chunk(audio_data)
                        audio_buffer = []

        except KeyboardInterrupt:
            self.is_running = False
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def transcribe_chunk(self, audio_data: np.ndarray):
        """Transcribe a chunk of audio."""
        segments, _ = self.model.transcribe(
            audio_data,
            beam_size=5,
            language="en"
        )

        for segment in segments:
            print(f">>> {segment.text.strip()}")

# Usage
transcriber = RealTimeTranscriber(model_size="base")
transcriber.start_recording()
```

### Voice Activity Detection (VAD)

For better real-time performance, use VAD to detect speech:

```python
import torch
import numpy as np

# Silero VAD (lightweight, accurate)
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)

(get_speech_timestamps, _, read_audio, _, _) = utils

def detect_speech_segments(audio_path: str) -> list:
    """Detect speech segments in audio file."""
    wav = read_audio(audio_path, sampling_rate=16000)

    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        threshold=0.5,
        sampling_rate=16000
    )

    return speech_timestamps

# Example output: [{'start': 0, 'end': 48000}, {'start': 64000, 'end': 96000}]
```

### Speaker Diarization

Identify who's speaking in multi-speaker audio:

```python
from pyannote.audio import Pipeline
import torch

# Initialize pipeline (requires HuggingFace token)
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="YOUR_HF_TOKEN"
)

# Send to GPU if available
if torch.cuda.is_available():
    pipeline = pipeline.to(torch.device("cuda"))

# Diarize audio
diarization = pipeline("meeting.wav")

# Print speaker segments
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"[{turn.start:.1f}s - {turn.end:.1f}s] Speaker {speaker}")
```

**Output**:
```
[0.0s - 4.2s] Speaker SPEAKER_00
[4.5s - 8.1s] Speaker SPEAKER_01
[8.3s - 15.2s] Speaker SPEAKER_00
```

---

## Building Voice AI Assistants

### The Complete Voice Assistant Pipeline

```python
import asyncio
from openai import OpenAI
from faster_whisper import WhisperModel
import pyaudio
import numpy as np
import tempfile
import os

class VoiceAssistant:
    """Complete voice-in, voice-out AI assistant."""

    def __init__(self):
        self.client = OpenAI()
        self.whisper = WhisperModel("base", device="cuda", compute_type="float16")
        self.conversation_history = []

    def record_audio(self, duration: float = 5.0) -> np.ndarray:
        """Record audio from microphone."""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        print("Recording...")
        frames = []
        for _ in range(int(16000 * duration / 1024)):
            data = stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.float32))
        print("Done recording.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        return np.concatenate(frames)

    def transcribe(self, audio: np.ndarray) -> str:
        """Convert speech to text."""
        segments, _ = self.whisper.transcribe(audio, beam_size=5)
        return " ".join([s.text for s in segments]).strip()

    def get_response(self, user_message: str) -> str:
        """Get AI response using Claude/GPT."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise (1-2 sentences) for natural conversation."},
                *self.conversation_history
            ]
        )

        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def speak(self, text: str):
        """Convert text to speech and play."""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )

        # Save to temp file and play
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            response.stream_to_file(f.name)
            os.system(f"afplay {f.name}")  # macOS; use different player for other OS
            os.unlink(f.name)

    def conversation_loop(self):
        """Main conversation loop."""
        print("Voice Assistant ready! Press Ctrl+C to exit.")
        print("Speak after you see 'Recording...'")

        while True:
            try:
                # Listen
                audio = self.record_audio(duration=5.0)

                # Transcribe
                user_text = self.transcribe(audio)
                if not user_text.strip():
                    print("(No speech detected)")
                    continue

                print(f"You: {user_text}")

                # Get AI response
                response = self.get_response(user_text)
                print(f"Assistant: {response}")

                # Speak response
                self.speak(response)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

# Run the assistant
if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.conversation_loop()
```

### Optimizing for Low Latency

For production voice assistants, latency is critical:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedVoiceAssistant:
    """Low-latency voice assistant with parallel processing."""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        # ... initialization

    async def process_turn(self, audio: np.ndarray):
        """Process a conversation turn with optimized latency."""

        # Start transcription immediately
        transcription_future = self.executor.submit(self.transcribe, audio)

        # Wait for transcription
        user_text = transcription_future.result()

        # Start LLM response with streaming
        async def stream_response():
            response_chunks = []
            async for chunk in self.stream_llm_response(user_text):
                response_chunks.append(chunk)

                # Start TTS on first sentence
                if len("".join(response_chunks)) > 50 and "." in chunk:
                    first_sentence = "".join(response_chunks).split(".")[0] + "."
                    self.executor.submit(self.speak, first_sentence)

            return "".join(response_chunks)

        full_response = await stream_response()
        return full_response

# Target latencies:
# - Recording end to transcription complete: <200ms
# - Transcription to first TTS audio: <500ms
# - Total end-to-end: <1000ms
```

---

## Did You Know? Voice AI in Production

### Siri's Rocky Road

**Apple's Siri** launched in 2011 and was revolutionary—but then fell behind:

**2011**: "Siri, set a timer for 10 minutes" blew people's minds.

**2012-2019**: Siri barely improved while Alexa and Google Assistant leaped ahead.

**The problem**: Apple's privacy-first approach limited data collection. Google/Amazon learned from billions of queries; Apple couldn't.

**2024**: Apple Intelligence finally brought modern AI to Siri. The new Siri uses on-device LLMs and can finally have natural conversations.

**The numbers**:
- Siri: 500M+ devices, but lowest satisfaction scores
- Alexa: 100M+ devices, most smart home integrations
- Google Assistant: Best accuracy, least privacy

### The $25 Billion Voice Market

Voice AI is big business:

| Segment | 2023 Revenue | 2028 Projected |
|---------|-------------|----------------|
| Speech Recognition | $12B | $28B |
| Text-to-Speech | $3B | $9B |
| Voice Assistants | $5B | $15B |
| Voice Biometrics | $2B | $6B |
| **Total** | **$22B** | **$58B** |

**Key players**:
- **Nuance** (acquired by Microsoft for $19.7B): Medical transcription
- **Deepgram**: Developer-focused STT API
- **AssemblyAI**: AI-powered transcription
- **Speechmatics**: Enterprise speech recognition

### The Podcast Revolution

**Podcasters discovered AI voice in 2023**, and it changed everything:

**Before AI**:
- Edit 1 hour of podcast = 3-4 hours of work
- Transcripts: Expensive or DIY
- Show notes: Manual writing

**After AI (Whisper + LLMs)**:
- Automatic transcription (free with Whisper)
- AI-generated show notes and summaries
- Auto-detect and remove "um"s and "uh"s
- Auto-generate clips for social media

**Tools that emerged**:
- **Descript**: Edit audio by editing text
- **Podcastle**: AI podcast production
- **Riverside**: AI transcription + editing
- **Opus Clip**: AI clip generator

**The numbers**:
- 80% of top podcasters now use AI transcription
- Average time savings: 60% on post-production
- New accessibility: Deaf audiences can read transcripts

---

## Multilingual Speech AI

### Whisper's Multilingual Magic

Whisper supports **99 languages** with varying quality:

**Tier 1 (Excellent - WER < 5%)**:
English, Spanish, French, German, Italian, Portuguese, Dutch, Polish

**Tier 2 (Good - WER 5-10%)**:
Japanese, Korean, Chinese, Russian, Arabic, Hindi, Turkish

**Tier 3 (Usable - WER 10-20%)**:
Most other languages

### Cross-Language Translation

```python
import whisper

model = whisper.load_model("large-v3")

# Transcribe Japanese audio to Japanese text
result_transcribe = model.transcribe(
    "japanese_speech.mp3",
    language="ja",
    task="transcribe"
)
print(f"Japanese: {result_transcribe['text']}")

# Translate Japanese audio to English text
result_translate = model.transcribe(
    "japanese_speech.mp3",
    task="translate"  # Always translates to English
)
print(f"English: {result_translate['text']}")
```

### Multilingual TTS

```python
from elevenlabs import generate

# ElevenLabs multilingual model
audio = generate(
    text="Bonjour! Comment allez-vous aujourd'hui?",
    voice="Rachel",
    model="eleven_multilingual_v2"
)

# OpenAI TTS also handles multiple languages
from openai import OpenAI
client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="こんにちは、元気ですか?"  # Japanese
)
```

---

## ️ Common Pitfalls

### Pitfall 1: Ignoring Audio Quality

**Problem**: Garbage in, garbage out.

```python
# BAD: Transcribing noisy audio without preprocessing
result = model.transcribe("noisy_audio.mp3")  # Poor results

# GOOD: Preprocess audio first
import librosa
import noisereduce as nr

# Load audio
audio, sr = librosa.load("noisy_audio.mp3", sr=16000)

# Reduce noise
audio_clean = nr.reduce_noise(y=audio, sr=sr)

# Save and transcribe
librosa.output.write_wav("clean_audio.wav", audio_clean, sr)
result = model.transcribe("clean_audio.wav")  # Much better!
```

### Pitfall 2: Not Handling Streaming Properly

**Problem**: Waiting for full audio before transcribing.

```python
# BAD: Transcribe only after recording stops
audio = record_5_seconds()
text = transcribe(audio)  # 5+ second latency!

# GOOD: Continuous transcription with VAD
while True:
    chunk = get_audio_chunk()
    if is_speech(chunk):
        buffer.append(chunk)
    elif buffer:  # End of speech
        text = transcribe(buffer)
        buffer = []
        yield text  # Stream results immediately
```

### Pitfall 3: Wrong Model Size

**Problem**: Using large model when small is enough.

```python
# For real-time (< 500ms latency): Use base or small
model = WhisperModel("base")  # 74M params, fast

# For accuracy (batch processing): Use large-v3
model = WhisperModel("large-v3")  # 1.5B params, accurate

# For English-only: Use .en models
model = WhisperModel("base.en")  # Faster for English
```

### Pitfall 4: Not Caching Voices

**Problem**: Regenerating TTS for repeated content.

```python
import hashlib

def get_cached_audio(text: str, voice: str) -> bytes:
    """Cache TTS results to avoid regeneration."""
    cache_key = hashlib.md5(f"{text}:{voice}".encode()).hexdigest()
    cache_path = f".tts_cache/{cache_key}.mp3"

    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()

    # Generate and cache
    audio = generate_tts(text, voice)
    os.makedirs(".tts_cache", exist_ok=True)
    with open(cache_path, "wb") as f:
        f.write(audio)

    return audio
```

---

## Production Best Practices

### 1. Choose the Right STT Provider

| Use Case | Recommendation |
|----------|----------------|
| Development/Testing | Local Whisper (free) |
| Low volume production | OpenAI Whisper API |
| High volume/real-time | Deepgram or AssemblyAI |
| On-premise required | faster-whisper + GPU |
| Multilingual focus | Whisper large-v3 |

### 2. Optimize TTS for Your Use Case

```python
# For voice assistants (speed matters)
response = client.audio.speech.create(
    model="tts-1",  # Faster, slightly lower quality
    voice="nova",
    input=text,
    speed=1.1  # Slightly faster speech
)

# For audiobooks/podcasts (quality matters)
response = client.audio.speech.create(
    model="tts-1-hd",  # Higher quality
    voice="fable",
    input=text,
    speed=0.95  # Slightly slower, more natural
)
```

### 3. Implement Graceful Degradation

```python
async def transcribe_with_fallback(audio_path: str) -> str:
    """Transcribe with fallback to backup service."""
    try:
        # Primary: Local faster-whisper
        return await transcribe_local(audio_path)
    except Exception as e:
        logger.warning(f"Local transcription failed: {e}")

    try:
        # Fallback: OpenAI API
        return await transcribe_openai(audio_path)
    except Exception as e:
        logger.warning(f"OpenAI transcription failed: {e}")

    try:
        # Last resort: Deepgram
        return await transcribe_deepgram(audio_path)
    except Exception as e:
        logger.error(f"All transcription services failed: {e}")
        return "[Transcription unavailable]"
```

### 4. Monitor Quality Metrics

```python
from dataclasses import dataclass
import time

@dataclass
class SpeechMetrics:
    transcription_latency_ms: float
    tts_latency_ms: float
    word_error_rate: float  # If you have ground truth
    audio_quality_score: float  # From analysis

def track_metrics(func):
    """Decorator to track speech processing metrics."""
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        latency = (time.time() - start) * 1000

        metrics.record(
            name=func.__name__,
            latency_ms=latency,
            timestamp=time.time()
        )

        return result
    return wrapper

@track_metrics
async def transcribe(audio):
    # ... transcription logic
    pass
```

---

## Further Reading

### Papers
- **Whisper** (2022): [Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356)
- **VALL-E** (2023): [Neural Codec Language Models are Zero-Shot Text to Speech Synthesizers](https://arxiv.org/abs/2301.02111)
- **Voicebox** (2023): [Text-Guided Multilingual Universal Speech Generation at Scale](https://arxiv.org/abs/2306.15687)

### Documentation
- [OpenAI Speech-to-Text Guide](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI Text-to-Speech Guide](https://platform.openai.com/docs/guides/text-to-speech)
- [ElevenLabs Documentation](https://docs.elevenlabs.io/)
- [faster-whisper GitHub](https://github.com/guillaumekln/faster-whisper)

### Tools
- **Whisper.cpp**: Whisper in C++ for edge deployment
- **Silero VAD**: Lightweight voice activity detection
- **pyannote.audio**: Speaker diarization toolkit

---

## Module Summary

**What you learned**:
- Whisper for accurate speech-to-text
- OpenAI TTS and ElevenLabs for natural speech synthesis
- Real-time transcription with VAD
- Building complete voice assistants
- Speaker diarization for multi-speaker audio
- Production best practices for speech AI

**Key technologies**:
- **STT**: Whisper, faster-whisper, Deepgram
- **TTS**: OpenAI TTS, ElevenLabs, Coqui
- **VAD**: Silero VAD
- **Diarization**: pyannote.audio

**The voice stack**:
```
Audio In → VAD → Whisper → LLM → TTS → Audio Out
```

---

## ️ Next Steps

**Next module**: Module 23: Vision AI

Now that you can make AI hear and speak, let's make it see! You'll learn:
- CLIP for image-text understanding
- GPT-4V and Claude Vision
- Building multimodal applications
- Image search and analysis

**Phase 5 Progress**: 1/3 modules complete

---

**🥋 Neural Dojo - Give your AI a voice! 🧠⚡🎙️**

---

_Last updated: 2025-11-26_
_Module 22: Speech AI_
