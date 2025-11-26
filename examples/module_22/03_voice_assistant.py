#!/usr/bin/env python3
"""
Module 22 Example 03: Voice AI Assistant

Demonstrates a complete voice-in, voice-out AI assistant:
- Real-time speech recognition with Whisper
- Conversation with LLM (GPT-4/Claude)
- Natural speech synthesis
- Conversation memory

Requirements:
    pip install openai-whisper openai pyaudio numpy

Note: Requires microphone access and audio output capability.

Author: Neural Dojo
"""

import os
import sys
import time
import tempfile
import threading
import queue
from dataclasses import dataclass
from typing import Optional, List, Callable
from pathlib import Path

# Audio handling
try:
    import numpy as np
except ImportError:
    os.system("pip install numpy")
    import numpy as np

# Check for OpenAI
try:
    from openai import OpenAI
except ImportError:
    os.system("pip install openai")
    from openai import OpenAI


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float


@dataclass
class VoiceAssistantConfig:
    """Configuration for the voice assistant."""
    whisper_model: str = "base"
    tts_voice: str = "nova"
    tts_model: str = "tts-1"
    llm_model: str = "gpt-4o-mini"
    system_prompt: str = "You are a helpful voice assistant. Keep responses concise (1-2 sentences) for natural conversation."
    max_history: int = 10
    silence_threshold: float = 0.01
    silence_duration: float = 0.8
    sample_rate: int = 16000


class SimpleAudioRecorder:
    """
    Simple audio recorder using numpy (no pyaudio required for demo).

    In production, use pyaudio for proper microphone access.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def record_simulated(self, duration: float = 3.0) -> np.ndarray:
        """
        Simulate recording (for demo without microphone).

        Returns silence - in production, replace with actual mic input.
        """
        samples = int(duration * self.sample_rate)
        return np.zeros(samples, dtype=np.float32)

    def record_from_file(self, audio_path: str) -> np.ndarray:
        """Load audio from file for testing."""
        try:
            import librosa
            audio, _ = librosa.load(audio_path, sr=self.sample_rate)
            return audio.astype(np.float32)
        except ImportError:
            print("Install librosa for audio file support: pip install librosa")
            return np.zeros(self.sample_rate * 3, dtype=np.float32)


class VoiceAssistant:
    """
    Complete voice-in, voice-out AI assistant.

    Pipeline:
    1. Record audio from microphone
    2. Transcribe with Whisper (STT)
    3. Process with LLM (generate response)
    4. Synthesize speech (TTS)
    5. Play audio response
    """

    def __init__(self, config: Optional[VoiceAssistantConfig] = None):
        self.config = config or VoiceAssistantConfig()
        self.client = OpenAI()
        self.conversation_history: List[ConversationTurn] = []
        self.recorder = SimpleAudioRecorder(self.config.sample_rate)

        # Load Whisper model
        self._whisper_model = None

        print(f"🤖 Voice Assistant initialized")
        print(f"   Whisper model: {self.config.whisper_model}")
        print(f"   TTS voice: {self.config.tts_voice}")
        print(f"   LLM: {self.config.llm_model}")
        print()

    @property
    def whisper_model(self):
        """Lazy load Whisper model."""
        if self._whisper_model is None:
            try:
                import whisper
                print(f"Loading Whisper {self.config.whisper_model}...")
                self._whisper_model = whisper.load_model(self.config.whisper_model)
                print("✅ Whisper loaded")
            except ImportError:
                print("⚠️ Whisper not available. Install with: pip install openai-whisper")
                return None
        return self._whisper_model

    def transcribe(self, audio: np.ndarray) -> str:
        """Convert speech to text using Whisper."""
        if self.whisper_model is None:
            return ""

        # Save to temp file (Whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            # Convert to int16 for WAV
            audio_int16 = (audio * 32767).astype(np.int16)

            # Write simple WAV header
            import struct
            num_samples = len(audio_int16)
            num_channels = 1
            sample_width = 2
            byte_rate = self.config.sample_rate * num_channels * sample_width
            block_align = num_channels * sample_width
            data_size = num_samples * sample_width

            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + data_size))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(struct.pack('<IHHIIHH', 16, 1, num_channels, self.config.sample_rate, byte_rate, block_align, sample_width * 8))
            f.write(b'data')
            f.write(struct.pack('<I', data_size))
            f.write(audio_int16.tobytes())

            temp_path = f.name

        try:
            result = self.whisper_model.transcribe(temp_path, language="en")
            return result["text"].strip()
        finally:
            os.unlink(temp_path)

    def get_llm_response(self, user_message: str) -> str:
        """Get response from LLM with conversation history."""
        # Add user message to history
        self.conversation_history.append(ConversationTurn(
            role="user",
            content=user_message,
            timestamp=time.time()
        ))

        # Build messages for API
        messages = [{"role": "system", "content": self.config.system_prompt}]

        # Add conversation history (limited to max_history)
        for turn in self.conversation_history[-self.config.max_history:]:
            messages.append({"role": turn.role, "content": turn.content})

        # Get response
        response = self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=messages,
            max_tokens=150  # Keep responses short for voice
        )

        assistant_message = response.choices[0].message.content

        # Add to history
        self.conversation_history.append(ConversationTurn(
            role="assistant",
            content=assistant_message,
            timestamp=time.time()
        ))

        return assistant_message

    def synthesize_speech(self, text: str, output_path: str = "response.mp3") -> str:
        """Convert text to speech using OpenAI TTS."""
        response = self.client.audio.speech.create(
            model=self.config.tts_model,
            voice=self.config.tts_voice,
            input=text
        )

        response.stream_to_file(output_path)
        return output_path

    def play_audio(self, audio_path: str):
        """Play audio file."""
        import platform
        system = platform.system()

        if system == "Darwin":
            os.system(f"afplay '{audio_path}' 2>/dev/null")
        elif system == "Linux":
            os.system(f"aplay '{audio_path}' 2>/dev/null || mpv '{audio_path}' 2>/dev/null")
        elif system == "Windows":
            os.system(f'start "" "{audio_path}"')

    def process_turn(self, audio: np.ndarray) -> Optional[str]:
        """
        Process a complete conversation turn.

        Args:
            audio: Audio input as numpy array

        Returns:
            Assistant's response text
        """
        # Step 1: Transcribe
        print("🎤 Transcribing...")
        start = time.time()
        user_text = self.transcribe(audio)
        transcribe_time = time.time() - start

        if not user_text.strip():
            print("   (No speech detected)")
            return None

        print(f"   You: {user_text}")
        print(f"   ⏱️ Transcription: {transcribe_time:.2f}s")

        # Step 2: Get LLM response
        print("🧠 Thinking...")
        start = time.time()
        response = self.get_llm_response(user_text)
        llm_time = time.time() - start
        print(f"   Assistant: {response}")
        print(f"   ⏱️ LLM: {llm_time:.2f}s")

        # Step 3: Synthesize speech
        print("🔊 Synthesizing...")
        start = time.time()
        audio_path = self.synthesize_speech(response)
        tts_time = time.time() - start
        print(f"   ⏱️ TTS: {tts_time:.2f}s")

        # Step 4: Play audio
        print("▶️ Playing response...")
        self.play_audio(audio_path)

        # Cleanup
        os.unlink(audio_path)

        total_time = transcribe_time + llm_time + tts_time
        print(f"   ⏱️ Total latency: {total_time:.2f}s")

        return response

    def process_text(self, text: str) -> str:
        """Process text input (bypass STT for testing)."""
        print(f"📝 You: {text}")

        # Get LLM response
        print("🧠 Thinking...")
        response = self.get_llm_response(text)
        print(f"🤖 Assistant: {response}")

        return response

    def interactive_text_mode(self):
        """
        Interactive text-based conversation (for testing without audio).
        """
        print("\n" + "=" * 50)
        print("TEXT MODE - Type your messages (Ctrl+C to exit)")
        print("=" * 50 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("Assistant: Goodbye!")
                    break

                response = self.process_text(user_input)

                # Optionally speak the response
                if os.getenv("OPENAI_API_KEY"):
                    speak = input("Speak response? (y/n): ").strip().lower()
                    if speak == "y":
                        audio_path = self.synthesize_speech(response)
                        self.play_audio(audio_path)
                        os.unlink(audio_path)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.conversation_history:
            return "No conversation yet."

        summary = f"Conversation ({len(self.conversation_history)} turns):\n"
        for turn in self.conversation_history[-5:]:  # Last 5 turns
            role = "You" if turn.role == "user" else "AI"
            summary += f"  {role}: {turn.content[:50]}...\n" if len(turn.content) > 50 else f"  {role}: {turn.content}\n"

        return summary


def demo_text_conversation():
    """Demo 1: Text-based conversation."""
    print("=" * 60)
    print("DEMO 1: Text-Based Conversation")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️ OPENAI_API_KEY not set. Showing simulated conversation.\n")

        print("You: What's the capital of France?")
        print("Assistant: The capital of France is Paris.\n")

        print("You: What's the population?")
        print("Assistant: Paris has a population of about 2.1 million in the city proper, or 12 million in the metropolitan area.\n")
        return

    assistant = VoiceAssistant()

    # Test conversation
    test_messages = [
        "Hello! How are you today?",
        "What can you help me with?",
        "Tell me a fun fact about AI."
    ]

    for message in test_messages:
        print()
        assistant.process_text(message)
        print()

    print("\n📊 Conversation Summary:")
    print(assistant.get_conversation_summary())


def demo_voice_pipeline():
    """Demo 2: Full voice pipeline (simulated)."""
    print("=" * 60)
    print("DEMO 2: Voice Pipeline (Simulated)")
    print("=" * 60)

    print("\n📋 Voice Assistant Pipeline:")
    print()
    print("   ┌─────────────┐")
    print("   │ Microphone  │")
    print("   └──────┬──────┘")
    print("          │")
    print("          ▼")
    print("   ┌─────────────┐")
    print("   │   Whisper   │ ← Speech-to-Text")
    print("   │    (STT)    │")
    print("   └──────┬──────┘")
    print("          │")
    print("          ▼")
    print("   ┌─────────────┐")
    print("   │  GPT-4 /    │ ← Language Model")
    print("   │   Claude    │")
    print("   └──────┬──────┘")
    print("          │")
    print("          ▼")
    print("   ┌─────────────┐")
    print("   │ OpenAI TTS  │ ← Text-to-Speech")
    print("   └──────┬──────┘")
    print("          │")
    print("          ▼")
    print("   ┌─────────────┐")
    print("   │   Speaker   │")
    print("   └─────────────┘")
    print()

    print("⏱️ Target Latencies:")
    print("   STT (Whisper):  100-500ms")
    print("   LLM (GPT-4):    200-500ms")
    print("   TTS (OpenAI):   200-400ms")
    print("   ─────────────────────────")
    print("   Total:          500-1400ms")
    print()


def demo_configurations():
    """Demo 3: Different assistant configurations."""
    print("=" * 60)
    print("DEMO 3: Assistant Configurations")
    print("=" * 60)

    configs = [
        {
            "name": "Quick Assistant",
            "whisper_model": "tiny",
            "tts_voice": "nova",
            "tts_model": "tts-1",
            "llm_model": "gpt-4o-mini",
            "use_case": "Fast responses, simple queries"
        },
        {
            "name": "Quality Assistant",
            "whisper_model": "medium",
            "tts_voice": "onyx",
            "tts_model": "tts-1-hd",
            "llm_model": "gpt-4o",
            "use_case": "High quality, complex conversations"
        },
        {
            "name": "Storyteller",
            "whisper_model": "base",
            "tts_voice": "fable",
            "tts_model": "tts-1-hd",
            "llm_model": "gpt-4o",
            "use_case": "Narration, storytelling"
        },
        {
            "name": "Customer Service",
            "whisper_model": "small",
            "tts_voice": "shimmer",
            "tts_model": "tts-1",
            "llm_model": "gpt-4o-mini",
            "use_case": "Friendly, helpful support"
        }
    ]

    print("\n📋 Recommended Configurations:\n")
    print(f"{'Config':<20} {'Whisper':<10} {'Voice':<10} {'TTS Model':<12} {'LLM':<15} Use Case")
    print("-" * 100)

    for c in configs:
        print(f"{c['name']:<20} {c['whisper_model']:<10} {c['tts_voice']:<10} {c['tts_model']:<12} {c['llm_model']:<15} {c['use_case']}")

    print()


def demo_interactive():
    """Demo 4: Interactive text mode."""
    print("=" * 60)
    print("DEMO 4: Interactive Mode")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️ OPENAI_API_KEY not set.")
        print("   Set it to enable interactive mode:")
        print("   export OPENAI_API_KEY=your-key-here")
        print()
        return

    assistant = VoiceAssistant()
    assistant.interactive_text_mode()


def main():
    """Run demos."""
    print("\n" + "=" * 60)
    print("MODULE 22: VOICE AI ASSISTANT")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "1":
            demo_text_conversation()
        elif demo == "2":
            demo_voice_pipeline()
        elif demo == "3":
            demo_configurations()
        elif demo == "4":
            demo_interactive()
        else:
            print(f"Unknown demo: {demo}")
            print("Usage: python 03_voice_assistant.py [1|2|3|4]")
    else:
        demo_voice_pipeline()
        demo_configurations()
        demo_text_conversation()

    print("\n" + "=" * 60)
    print("✅ Voice Assistant demos completed!")
    print("=" * 60)
    print("\n💡 Try interactive mode: python 03_voice_assistant.py 4\n")


if __name__ == "__main__":
    main()
