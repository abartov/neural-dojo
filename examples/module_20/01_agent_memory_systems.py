#!/usr/bin/env python3
"""
Module 20 Example 01: Agent Memory Systems

This example demonstrates different memory types for AI agents:
1. Short-term memory (conversation buffer)
2. Long-term memory (vector store)
3. Episodic memory (specific experiences)
4. Summary memory (compressed history)
5. Hybrid memory (combining all types)

Each memory type solves different problems and has different trade-offs.
The best agents combine multiple memory types for optimal performance.

Usage:
    python 01_agent_memory_systems.py demo1  # Short-term memory
    python 01_agent_memory_systems.py demo2  # Long-term vector memory
    python 01_agent_memory_systems.py demo3  # Summary memory
    python 01_agent_memory_systems.py demo4  # Hybrid memory system
"""

import json
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# Storage directory
STORAGE_DIR = Path(".agent_memory_demo")


# =============================================================================
# MEMORY DATA STRUCTURES
# =============================================================================

@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


@dataclass
class MemoryEntry:
    """A memory entry with embedding for vector search."""
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    importance: float = 1.0

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "importance": self.importance
        }


# =============================================================================
# SIMPLE EMBEDDING MODEL (NO API REQUIRED)
# =============================================================================

class SimpleEmbeddingModel:
    """
    A simple word-frequency based embedding model.

    This is NOT production quality - it's for demonstration purposes.
    In production, you'd use:
    - Google's text-embedding-004
    - OpenAI's text-embedding-ada-002
    - Sentence Transformers
    """

    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = vocab_size
        self.vocab: Dict[str, int] = {}
        self.word_count = 0

    def _tokenize(self, text: str) -> List[str]:
        """Simple word tokenization."""
        # Lowercase and split on non-alphanumeric
        import re
        return re.findall(r'\b\w+\b', text.lower())

    def _get_word_index(self, word: str) -> int:
        """Get or create index for a word."""
        if word not in self.vocab:
            self.vocab[word] = self.word_count % self.vocab_size
            self.word_count += 1
        return self.vocab[word]

    def embed(self, text: str) -> List[float]:
        """Create a simple embedding from text."""
        tokens = self._tokenize(text)

        # Initialize embedding vector
        embedding = [0.0] * self.vocab_size

        # Count word frequencies
        for token in tokens:
            idx = self._get_word_index(token)
            embedding[idx] += 1.0

        # Normalize (L2 norm)
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# =============================================================================
# MEMORY TYPE 1: SHORT-TERM (CONVERSATION BUFFER)
# =============================================================================

class ConversationBuffer:
    """
    Short-term memory: keeps recent conversation history.

    Like human working memory - limited capacity, fast access.
    Good for: maintaining conversation context
    Limited by: fixed window size, loses old information
    """

    def __init__(self, max_messages: int = 20):
        self.messages: List[Message] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        """Add a message to the buffer."""
        self.messages.append(Message(role=role, content=content))

        # Trim to max size (FIFO)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> str:
        """Format messages for LLM context."""
        return "\n".join([
            f"{m.role}: {m.content}"
            for m in self.messages
        ])

    def get_recent(self, n: int = 5) -> List[Message]:
        """Get the n most recent messages."""
        return self.messages[-n:]

    def clear(self):
        """Clear all messages."""
        self.messages = []

    def __len__(self) -> int:
        return len(self.messages)


# =============================================================================
# MEMORY TYPE 2: LONG-TERM (VECTOR STORE)
# =============================================================================

class VectorMemory:
    """
    Long-term memory using vector similarity.

    Like human long-term memory - large capacity, semantic retrieval.
    Good for: finding relevant past information
    Requires: embedding model for semantic search
    """

    def __init__(self, embedding_model: SimpleEmbeddingModel):
        self.embedding_model = embedding_model
        self.memories: List[MemoryEntry] = []

    def store(self, content: str, metadata: Dict[str, Any] = None):
        """Store a new memory."""
        embedding = self.embedding_model.embed(content)
        importance = self._calculate_importance(content)

        memory = MemoryEntry(
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
            importance=importance
        )
        self.memories.append(memory)

    def retrieve(self, query: str, k: int = 5) -> List[MemoryEntry]:
        """Retrieve k most relevant memories."""
        if not self.memories:
            return []

        query_embedding = self.embedding_model.embed(query)

        # Score all memories
        scored = []
        for memory in self.memories:
            similarity = cosine_similarity(query_embedding, memory.embedding)
            # Weight by importance
            score = similarity * memory.importance
            scored.append((score, memory))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [m for _, m in scored[:k]]

    def _calculate_importance(self, content: str) -> float:
        """Estimate importance of content (heuristic)."""
        importance = 1.0
        content_lower = content.lower()

        # Personal information is important
        personal_keywords = ["my name", "i am", "i work", "i live", "my email", "my phone"]
        for kw in personal_keywords:
            if kw in content_lower:
                importance += 0.3

        # Explicit importance markers
        if any(w in content_lower for w in ["remember", "don't forget", "important"]):
            importance += 0.4

        # Questions might be important
        if "?" in content:
            importance += 0.1

        # Preferences
        if any(w in content_lower for w in ["prefer", "want", "like", "hate", "always", "never"]):
            importance += 0.2

        return min(importance, 2.0)  # Cap at 2x

    def __len__(self) -> int:
        return len(self.memories)


# =============================================================================
# MEMORY TYPE 3: SUMMARY MEMORY
# =============================================================================

class SummaryMemory:
    """
    Summary memory: progressively summarizes conversation.

    Like human episodic memory compression - detailed recent, compressed old.
    Good for: maintaining context over very long conversations
    Requires: LLM for summarization (simulated here)
    """

    def __init__(self, summary_interval: int = 5):
        self.summary_interval = summary_interval
        self.summaries: List[str] = []
        self.current_buffer: List[Message] = []

    def add_message(self, message: Message):
        """Add message, summarize if needed."""
        self.current_buffer.append(message)

        if len(self.current_buffer) >= self.summary_interval:
            self._summarize_buffer()

    def _summarize_buffer(self):
        """Create summary from buffer (simulated - would use LLM)."""
        # In production, you'd use an LLM here
        # We'll simulate with a simple extraction

        key_points = []
        for msg in self.current_buffer:
            content = msg.content.lower()

            # Extract what seems important
            if "my name is" in content:
                key_points.append(f"User introduced themselves: {msg.content}")
            elif "i work" in content or "i live" in content:
                key_points.append(f"User shared: {msg.content}")
            elif "?" in msg.content and msg.role == "user":
                key_points.append(f"User asked: {msg.content[:50]}...")
            elif msg.role == "assistant" and len(msg.content) > 100:
                key_points.append(f"Assistant provided detailed response about: {msg.content[:30]}...")

        if key_points:
            summary = "Summary: " + "; ".join(key_points)
        else:
            summary = f"Conversation segment ({len(self.current_buffer)} messages)"

        self.summaries.append(summary)
        self.current_buffer = []

    def get_context(self) -> str:
        """Get full context: summaries + current buffer."""
        parts = []

        if self.summaries:
            parts.append("Previous conversation:")
            parts.extend(self.summaries)
            parts.append("\nRecent messages:")

        for msg in self.current_buffer:
            parts.append(f"{msg.role}: {msg.content}")

        return "\n".join(parts)

    def __len__(self) -> int:
        return len(self.summaries) + len(self.current_buffer)


# =============================================================================
# MEMORY TYPE 4: HYBRID MEMORY
# =============================================================================

class HybridMemory:
    """
    Hybrid memory: combines all memory types.

    The most capable agents use hybrid memory:
    - Short-term for immediate context
    - Long-term for semantic retrieval
    - Summary for compressed history
    """

    def __init__(self, embedding_model: SimpleEmbeddingModel):
        self.short_term = ConversationBuffer(max_messages=10)
        self.long_term = VectorMemory(embedding_model)
        self.summary = SummaryMemory(summary_interval=5)

    def add_interaction(self, role: str, content: str):
        """Record an interaction across all memory systems."""
        message = Message(role=role, content=content)

        # Short-term: always add
        self.short_term.add(role, content)

        # Summary: track for periodic summarization
        self.summary.add_message(message)

        # Long-term: store if important
        if self._is_important(content):
            self.long_term.store(content, metadata={"role": role})

    def get_relevant_context(self, query: str) -> str:
        """Build context from all memory systems."""
        parts = []

        # 1. Summary of older conversations
        summary_context = self.summary.get_context()
        if summary_context:
            parts.append(f"=== History ===\n{summary_context}")

        # 2. Relevant long-term memories
        memories = self.long_term.retrieve(query, k=3)
        if memories:
            memory_text = "\n".join([f"- {m.content}" for m in memories])
            parts.append(f"\n=== Relevant Memories ===\n{memory_text}")

        # 3. Recent conversation
        recent = self.short_term.get_context()
        if recent:
            parts.append(f"\n=== Recent Messages ===\n{recent}")

        return "\n".join(parts)

    def _is_important(self, content: str) -> bool:
        """Determine if content should go to long-term memory."""
        important_patterns = [
            "my name", "i am", "i work", "i live",
            "remember", "don't forget", "important",
            "always", "never", "prefer"
        ]
        content_lower = content.lower()
        return any(p in content_lower for p in important_patterns)

    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics."""
        return {
            "short_term_messages": len(self.short_term),
            "long_term_memories": len(self.long_term),
            "summaries": len(self.summary.summaries),
            "summary_buffer": len(self.summary.current_buffer)
        }


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================

def demo_1_short_term_memory():
    """Demo 1: Short-term conversation buffer."""
    print("\n" + "="*60)
    print("DEMO 1: SHORT-TERM MEMORY (CONVERSATION BUFFER)")
    print("="*60)

    buffer = ConversationBuffer(max_messages=5)

    # Simulate a conversation
    conversation = [
        ("user", "Hi, my name is Alex."),
        ("assistant", "Hello Alex! Nice to meet you. How can I help?"),
        ("user", "I work at TechCorp as a software engineer."),
        ("assistant", "That's great! Software engineering at TechCorp sounds exciting."),
        ("user", "I'm interested in learning about AI agents."),
        ("assistant", "AI agents are fascinating! They can plan, remember, and act autonomously."),
        ("user", "What's my name again?"),
    ]

    print("\n--- Simulating conversation ---")
    for role, content in conversation:
        buffer.add(role, content)
        print(f"{role}: {content}")

    print(f"\n--- Buffer state (max={buffer.max_messages}) ---")
    print(f"Messages stored: {len(buffer)}")

    print("\n--- Current context ---")
    print(buffer.get_context())

    print("\n--- Analysis ---")
    print("Notice: The first message ('Hi, my name is Alex') was lost")
    print("when the buffer exceeded max_messages!")
    print("This is the limitation of short-term memory.")

    print("\n✅ Short-term memory is fast but forgets old information!")


def demo_2_long_term_memory():
    """Demo 2: Long-term vector memory."""
    print("\n" + "="*60)
    print("DEMO 2: LONG-TERM MEMORY (VECTOR STORE)")
    print("="*60)

    embedding_model = SimpleEmbeddingModel(vocab_size=500)
    memory = VectorMemory(embedding_model)

    # Store some memories
    memories_to_store = [
        "My name is Alex and I'm a software engineer.",
        "I work at TechCorp in the AI division.",
        "My favorite programming language is Python.",
        "I prefer working from home on Fridays.",
        "Remember to always use type hints in Python.",
        "The project deadline is next month.",
        "I have a meeting with Sarah tomorrow at 3pm.",
    ]

    print("\n--- Storing memories ---")
    for content in memories_to_store:
        memory.store(content)
        importance = memory.memories[-1].importance
        print(f"  [{importance:.2f}] {content}")

    print(f"\n--- Memory statistics ---")
    print(f"Total memories stored: {len(memory)}")

    # Query the memory
    queries = [
        "What is my name?",
        "Where do I work?",
        "What's my favorite language?",
        "Any upcoming deadlines?",
    ]

    print("\n--- Querying memories ---")
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = memory.retrieve(query, k=2)
        for i, mem in enumerate(results, 1):
            similarity = cosine_similarity(
                embedding_model.embed(query),
                mem.embedding
            )
            print(f"  {i}. [{similarity:.3f}] {mem.content}")

    print("\n✅ Long-term memory retrieves semantically relevant information!")


def demo_3_summary_memory():
    """Demo 3: Summary memory with compression."""
    print("\n" + "="*60)
    print("DEMO 3: SUMMARY MEMORY (COMPRESSED HISTORY)")
    print("="*60)

    memory = SummaryMemory(summary_interval=3)

    # Simulate a longer conversation
    conversation = [
        ("user", "Hello! My name is Jordan."),
        ("assistant", "Hi Jordan! Welcome! How can I help you today?"),
        ("user", "I'm learning about machine learning."),
        # -- First summary created here --
        ("assistant", "That's exciting! ML has many subfields. What interests you most?"),
        ("user", "I want to build chatbots for customer service."),
        ("assistant", "Great choice! You'll want to learn about NLP and transformer models."),
        # -- Second summary created here --
        ("user", "What resources do you recommend?"),
        ("assistant", "Start with the Hugging Face course and then try LangChain."),
        ("user", "Thanks! I work at a fintech startup."),
        # -- Third summary created here --
        ("user", "What's the best model for our use case?"),
    ]

    print("\n--- Processing conversation ---")
    for role, content in conversation:
        message = Message(role=role, content=content)
        memory.add_message(message)
        print(f"{role}: {content}")

        if len(memory.summaries) > 0:
            if len(memory.current_buffer) == 0:
                print(f"  [Summary {len(memory.summaries)} created!]")

    print(f"\n--- Memory statistics ---")
    print(f"Summaries created: {len(memory.summaries)}")
    print(f"Current buffer size: {len(memory.current_buffer)}")

    print("\n--- Full context ---")
    print(memory.get_context())

    print("\n✅ Summary memory compresses old conversations while keeping recent detail!")


def demo_4_hybrid_memory():
    """Demo 4: Hybrid memory combining all types."""
    print("\n" + "="*60)
    print("DEMO 4: HYBRID MEMORY (COMBINED SYSTEM)")
    print("="*60)

    embedding_model = SimpleEmbeddingModel(vocab_size=500)
    memory = HybridMemory(embedding_model)

    # Simulate an extended interaction
    conversation = [
        ("user", "Hi! My name is Sam and I work at DataCorp."),
        ("assistant", "Hello Sam from DataCorp! Great to meet you."),
        ("user", "I'm building a RAG system for our documentation."),
        ("assistant", "RAG is excellent for documentation search. What stack are you using?"),
        ("user", "We use Python with LangChain. Remember that for later."),
        ("assistant", "Noted! Python + LangChain is a solid choice for RAG."),
        ("user", "I prefer chunking documents at 500 tokens."),
        ("assistant", "500 tokens is a good balance. Some prefer 1000 for more context."),
        ("user", "Can you help me with vector databases?"),
        ("assistant", "Of course! Popular options include Qdrant, Pinecone, and Chroma."),
        ("user", "What's my preferred chunk size again?"),
    ]

    print("\n--- Processing conversation ---")
    for role, content in conversation:
        memory.add_interaction(role, content)
        print(f"{role}: {content}")

    print(f"\n--- Memory statistics ---")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Query the hybrid memory
    query = "What is Sam's chunk size preference?"
    print(f"\n--- Querying: '{query}' ---")
    context = memory.get_relevant_context(query)
    print(context)

    print("\n--- Analysis ---")
    print("The hybrid memory system:")
    print("  1. Keeps recent messages in short-term buffer")
    print("  2. Stores important info (name, preferences) in long-term")
    print("  3. Compresses older conversation into summaries")
    print("  4. Retrieves relevant context for any query")

    print("\n✅ Hybrid memory gives the best of all memory types!")


def show_usage():
    """Show usage information."""
    print(__doc__)
    print("\nAvailable demos:")
    print("  demo1 - Short-term memory (conversation buffer)")
    print("  demo2 - Long-term memory (vector store)")
    print("  demo3 - Summary memory (compressed history)")
    print("  demo4 - Hybrid memory (combined system)")


def main():
    """Main entry point."""
    # Ensure storage directory exists
    STORAGE_DIR.mkdir(exist_ok=True)

    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_short_term_memory()
    elif command == "demo2":
        demo_2_long_term_memory()
    elif command == "demo3":
        demo_3_summary_memory()
    elif command == "demo4":
        demo_4_hybrid_memory()
    elif command == "all":
        demo_1_short_term_memory()
        demo_2_long_term_memory()
        demo_3_summary_memory()
        demo_4_hybrid_memory()
    else:
        print(f"Unknown command: {command}")
        show_usage()


if __name__ == "__main__":
    main()
