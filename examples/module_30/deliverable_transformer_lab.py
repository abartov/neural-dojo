#!/usr/bin/env python3
"""
Module 30 Deliverable: Transformer Lab

A comprehensive lab for building, training, and analyzing transformer architectures.
Implements attention mechanisms from scratch with visualization and analysis tools.

Features:
- Self-attention implementation with visualization
- Multi-head attention from scratch
- Positional encoding (sinusoidal and learned)
- Complete transformer encoder
- Mini language model training
- Attention pattern analysis
- JSON result persistence

Usage:
    python deliverable_transformer_lab.py demo1  # Self-attention visualization
    python deliverable_transformer_lab.py demo2  # Train mini language model
    python deliverable_transformer_lab.py demo3  # Attention pattern analysis
    python deliverable_transformer_lab.py demo4  # Generate transformer report

Author: Neural Dojo
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import math
import os
import sys
import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Any


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TransformerConfig:
    """Configuration for transformer architecture."""
    vocab_size: int = 1000
    d_model: int = 256
    num_heads: int = 8
    num_layers: int = 4
    d_ff: int = 1024
    max_len: int = 512
    dropout: float = 0.1


@dataclass
class AttentionAnalysis:
    """Analysis of attention patterns."""
    layer: int
    head: int
    entropy: float
    sparsity: float
    diagonal_strength: float
    description: str


@dataclass
class TrainingResult:
    """Results from training run."""
    model_name: str
    config: Dict[str, Any]
    train_losses: List[float]
    val_losses: List[float]
    final_loss: float
    total_epochs: int
    training_time_seconds: float
    samples_seen: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# ATTENTION MECHANISMS
# ============================================================================

class ScaledDotProductAttention(nn.Module):
    """
    Scaled dot-product attention mechanism.

    Attention(Q, K, V) = softmax(Q @ K.T / sqrt(d_k)) @ V

    This is the core building block of transformers.
    """

    def __init__(self, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query: [batch, seq_len, d_k]
            key: [batch, seq_len, d_k]
            value: [batch, seq_len, d_v]
            mask: Optional mask [batch, seq_len, seq_len]

        Returns:
            output: Attended values [batch, seq_len, d_v]
            attention_weights: Attention patterns [batch, seq_len, seq_len]
        """
        d_k = query.size(-1)

        # Compute attention scores
        scores = torch.bmm(query, key.transpose(-2, -1)) / math.sqrt(d_k)

        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        # Softmax to get attention weights
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention to values
        output = torch.bmm(attention_weights, value)

        return output, attention_weights


class MultiHeadAttention(nn.Module):
    """
    Multi-head attention mechanism.

    Runs multiple attention operations in parallel, each learning
    different relationship patterns.
    """

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # Linear projections for Q, K, V
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

        self.attention = ScaledDotProductAttention(dropout)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query, key, value: [batch, seq_len, d_model]
            mask: Optional [batch, 1, seq_len, seq_len]

        Returns:
            output: [batch, seq_len, d_model]
            attention_weights: [batch, num_heads, seq_len, seq_len]
        """
        batch_size, seq_len, _ = query.shape

        # Linear projections
        Q = self.W_q(query)
        K = self.W_k(key)
        V = self.W_v(value)

        # Reshape for multi-head attention
        # [batch, seq_len, d_model] -> [batch, seq_len, num_heads, d_k]
        # -> [batch, num_heads, seq_len, d_k]
        Q = Q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)

        # Reshape for batch processing of all heads
        # [batch, num_heads, seq_len, d_k] -> [batch * num_heads, seq_len, d_k]
        Q = Q.reshape(batch_size * self.num_heads, seq_len, self.d_k)
        K = K.reshape(batch_size * self.num_heads, seq_len, self.d_k)
        V = V.reshape(batch_size * self.num_heads, seq_len, self.d_k)

        # Apply attention
        if mask is not None:
            # Expand mask for all heads: need [batch * num_heads, seq_len, seq_len]
            # mask comes in as [1, seq_len, seq_len] or [batch, seq_len, seq_len]
            if mask.size(0) == 1:
                # Broadcast to all batches and heads
                mask = mask.expand(batch_size, -1, -1)
            # Now mask is [batch, seq_len, seq_len]
            # Expand to [batch, num_heads, seq_len, seq_len] then flatten
            mask = mask.unsqueeze(1).expand(-1, self.num_heads, -1, -1)
            mask = mask.reshape(batch_size * self.num_heads, seq_len, seq_len)

        attended, attention_weights = self.attention(Q, K, V, mask)

        # Reshape back
        attended = attended.view(batch_size, self.num_heads, seq_len, self.d_k)
        attention_weights = attention_weights.view(
            batch_size, self.num_heads, seq_len, seq_len
        )

        # Concatenate heads
        attended = attended.transpose(1, 2).contiguous()
        attended = attended.view(batch_size, seq_len, self.d_model)

        # Final projection
        output = self.W_o(attended)

        return output, attention_weights


# ============================================================================
# POSITIONAL ENCODING
# ============================================================================

class SinusoidalPositionalEncoding(nn.Module):
    """
    Sinusoidal positional encoding from "Attention Is All You Need."

    PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()

        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() *
            (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0)  # [1, max_len, d_model]
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input embeddings."""
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


class LearnedPositionalEncoding(nn.Module):
    """Learned positional embeddings (like BERT/GPT)."""

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        self.position_embeddings = nn.Embedding(max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device)
        position_embeddings = self.position_embeddings(positions)
        return self.dropout(x + position_embeddings)


# ============================================================================
# TRANSFORMER COMPONENTS
# ============================================================================

class FeedForward(nn.Module):
    """
    Position-wise feed-forward network.

    FFN(x) = GELU(xW1 + b1)W2 + b2
    """

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TransformerEncoderBlock(nn.Module):
    """
    Single transformer encoder block.

    Contains multi-head self-attention and feed-forward network,
    each with residual connections and layer normalization.
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1
    ):
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.ff = FeedForward(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # Self-attention with residual
        attended, attention_weights = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attended))

        # Feed-forward with residual
        ff_out = self.ff(x)
        x = self.norm2(x + ff_out)

        return x, attention_weights


class TransformerEncoder(nn.Module):
    """
    Complete transformer encoder.

    Stacks multiple encoder blocks with token and positional embeddings.
    """

    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        self.d_model = config.d_model

        # Embeddings
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.positional_encoding = SinusoidalPositionalEncoding(
            config.d_model, config.max_len, config.dropout
        )

        # Encoder blocks
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(
                config.d_model, config.num_heads,
                config.d_ff, config.dropout
            )
            for _ in range(config.num_layers)
        ])

        self.norm = nn.LayerNorm(config.d_model)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Args:
            x: Token IDs [batch, seq_len]
            mask: Optional attention mask

        Returns:
            output: Encoded representations [batch, seq_len, d_model]
            attention_weights: List of attention matrices per layer
        """
        # Embed tokens
        x = self.token_embedding(x) * math.sqrt(self.d_model)
        x = self.positional_encoding(x)

        # Pass through encoder blocks
        attention_weights = []
        for layer in self.layers:
            x, attn = layer(x, mask)
            attention_weights.append(attn)

        x = self.norm(x)

        return x, attention_weights


class MiniLanguageModel(nn.Module):
    """
    A minimal language model using transformer decoder.

    Predicts next token given previous tokens.
    """

    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config

        self.transformer = TransformerEncoder(config)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        # Tie weights between embedding and output
        self.lm_head.weight = self.transformer.token_embedding.weight

    def forward(
        self,
        x: torch.Tensor,
        targets: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], List[torch.Tensor]]:
        """
        Args:
            x: Input token IDs [batch, seq_len]
            targets: Target token IDs [batch, seq_len] (optional)

        Returns:
            logits: [batch, seq_len, vocab_size]
            loss: Cross-entropy loss if targets provided
            attention_weights: Attention patterns from all layers
        """
        # Create causal mask
        seq_len = x.size(1)
        causal_mask = torch.tril(torch.ones(seq_len, seq_len, device=x.device))
        causal_mask = causal_mask.unsqueeze(0)  # [1, seq_len, seq_len]

        # Forward through transformer
        hidden, attention_weights = self.transformer(x, causal_mask)

        # Project to vocabulary
        logits = self.lm_head(hidden)

        # Compute loss if targets provided
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, self.config.vocab_size),
                targets.view(-1),
                ignore_index=-1  # Ignore padding
            )

        return logits, loss, attention_weights

    @torch.no_grad()
    def generate(
        self,
        start_tokens: torch.Tensor,
        max_new_tokens: int = 50,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        Generate tokens autoregressively.

        Args:
            start_tokens: Starting sequence [batch, seq_len]
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature (higher = more random)

        Returns:
            Generated sequence [batch, seq_len + max_new_tokens]
        """
        self.eval()
        generated = start_tokens

        for _ in range(max_new_tokens):
            # Truncate if necessary
            if generated.size(1) > self.config.max_len:
                context = generated[:, -self.config.max_len:]
            else:
                context = generated

            # Get predictions
            logits, _, _ = self(context)
            logits = logits[:, -1, :] / temperature

            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            generated = torch.cat([generated, next_token], dim=1)

        return generated


# ============================================================================
# DATASET
# ============================================================================

class CharacterDataset(Dataset):
    """
    Simple character-level dataset for language modeling.
    """

    def __init__(self, text: str, seq_len: int = 64):
        self.seq_len = seq_len

        # Build vocabulary
        chars = sorted(list(set(text)))
        self.char_to_idx = {ch: i for i, ch in enumerate(chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(chars)}
        self.vocab_size = len(chars)

        # Encode text
        self.data = torch.tensor(
            [self.char_to_idx[ch] for ch in text],
            dtype=torch.long
        )

    def __len__(self):
        return max(0, len(self.data) - self.seq_len)

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.seq_len]
        y = self.data[idx + 1:idx + self.seq_len + 1]
        return x, y

    def decode(self, indices: torch.Tensor) -> str:
        return ''.join([self.idx_to_char[i.item()] for i in indices])


# ============================================================================
# ANALYSIS UTILITIES
# ============================================================================

def analyze_attention_head(
    attention_weights: torch.Tensor,
    layer: int,
    head: int
) -> AttentionAnalysis:
    """
    Analyze attention patterns for a specific head.

    Args:
        attention_weights: [batch, num_heads, seq_len, seq_len]
        layer: Layer index
        head: Head index

    Returns:
        AttentionAnalysis with metrics
    """
    # Get attention for this head (average over batch)
    attn = attention_weights[:, head].mean(0)  # [seq_len, seq_len]

    # Entropy (higher = more distributed attention)
    entropy = -(attn * (attn + 1e-10).log()).sum(-1).mean().item()

    # Sparsity (how concentrated is attention)
    max_attn = attn.max(-1).values.mean().item()
    sparsity = max_attn

    # Diagonal strength (attention to adjacent positions)
    seq_len = attn.size(0)
    if seq_len > 1:
        diagonal = torch.diagonal(attn, offset=1).mean().item()
        diagonal += torch.diagonal(attn, offset=-1).mean().item()
        diagonal_strength = diagonal / 2
    else:
        diagonal_strength = 0.0

    # Generate description
    if entropy < 1.0:
        description = "Sparse/focused attention"
    elif diagonal_strength > 0.3:
        description = "Local/positional attention"
    elif sparsity > 0.5:
        description = "Key-focused attention"
    else:
        description = "Distributed attention"

    return AttentionAnalysis(
        layer=layer,
        head=head,
        entropy=entropy,
        sparsity=sparsity,
        diagonal_strength=diagonal_strength,
        description=description
    )


def create_attention_map_ascii(
    attention_weights: torch.Tensor,
    tokens: List[str],
    max_display: int = 10
) -> str:
    """
    Create ASCII visualization of attention weights.
    """
    # Average over batch and heads
    attn = attention_weights.mean(dim=(0, 1))  # [seq_len, seq_len]

    # Limit size
    n = min(attn.size(0), max_display)
    attn = attn[:n, :n]
    tokens = tokens[:n]

    # Create ASCII art
    lines = []

    # Header
    header = "     " + " ".join(f"{t[:4]:>4}" for t in tokens)
    lines.append(header)
    lines.append("-" * len(header))

    # Rows
    for i, token in enumerate(tokens):
        row = f"{token[:4]:>4} "
        for j in range(n):
            val = attn[i, j].item()
            if val > 0.5:
                char = "##"
            elif val > 0.2:
                char = "++"
            elif val > 0.1:
                char = ".."
            else:
                char = "  "
            row += f"{char:>4} "
        lines.append(row)

    return "\n".join(lines)


# ============================================================================
# STORAGE
# ============================================================================

class Storage:
    """Handle saving and loading results."""

    def __init__(self, storage_dir: str = ".transformer_lab"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_result(self, result: Any, filename: str) -> str:
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        return filepath

    def load_result(self, filename: str) -> Dict:
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def save_attention_analysis(
        self,
        analyses: List[AttentionAnalysis],
        filename: str
    ) -> str:
        filepath = os.path.join(self.storage_dir, filename)
        data = {
            "analyses": [asdict(a) for a in analyses],
            "timestamp": datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return filepath


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_1_attention_visualization():
    """
    Demo 1: Self-Attention Visualization

    Shows how self-attention works on a simple sequence,
    visualizing the attention patterns.
    """
    print("=" * 60)
    print("DEMO 1: Self-Attention Visualization")
    print("=" * 60)
    print()

    # Create simple attention module
    d_model = 64
    num_heads = 4

    print("Creating multi-head attention (d_model=64, num_heads=4)...")
    mha = MultiHeadAttention(d_model, num_heads)
    print()

    # Create a simple sequence
    seq_len = 6
    batch_size = 1

    # Random embeddings (in practice, these come from token embeddings)
    x = torch.randn(batch_size, seq_len, d_model)

    # Labels for visualization
    tokens = ["The", "cat", "sat", "on", "the", "mat"]

    print(f"Input sequence: {tokens}")
    print(f"Input shape: {x.shape}")
    print()

    # Forward pass
    output, attention_weights = mha(x, x, x)

    print(f"Output shape: {output.shape}")
    print(f"Attention weights shape: {attention_weights.shape}")
    print()

    # Visualize attention for each head
    print("Attention patterns by head:")
    print("-" * 40)

    for head in range(num_heads):
        print(f"\nHead {head}:")
        head_attn = attention_weights[0, head]  # [seq_len, seq_len]

        # Simple ASCII visualization
        print("     " + "  ".join(f"{t[:3]:>3}" for t in tokens))
        for i, token in enumerate(tokens):
            row = f"{token[:3]:>3}  "
            for j in range(seq_len):
                val = head_attn[i, j].item()
                if val > 0.3:
                    row += " ## "
                elif val > 0.15:
                    row += " ++ "
                else:
                    row += " .  "
            print(row)

    print()
    print("Legend: ## = high attention, ++ = medium, . = low")
    print()

    # Analyze patterns
    print("Attention Analysis:")
    print("-" * 40)
    for head in range(num_heads):
        analysis = analyze_attention_head(attention_weights, 0, head)
        print(f"Head {head}: {analysis.description}")
        print(f"  Entropy: {analysis.entropy:.2f}, Sparsity: {analysis.sparsity:.2f}")

    print()
    print("Key Insight: Each head learns different attention patterns!")
    print("Some focus on adjacent words, others on specific relationships.")

    return attention_weights


def demo_2_train_mini_lm():
    """
    Demo 2: Train Mini Language Model

    Trains a small transformer language model on a text sample.
    Demonstrates the complete training loop.
    """
    print("=" * 60)
    print("DEMO 2: Train Mini Language Model")
    print("=" * 60)
    print()

    storage = Storage()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print()

    # Sample text for training
    sample_text = """
    The transformer architecture has revolutionized natural language processing.
    Attention mechanisms allow models to focus on relevant parts of the input.
    Self-attention computes relationships between all positions in a sequence.
    Multi-head attention runs multiple attention operations in parallel.
    Positional encoding adds information about token positions.
    The original transformer paper introduced the encoder-decoder architecture.
    Modern language models like GPT use decoder-only transformers.
    BERT uses encoder-only transformers for bidirectional understanding.
    Transformers have also been applied to computer vision with great success.
    The scaling laws show that larger transformers perform better with more data.
    """ * 20  # Repeat for more training data

    print("Creating character-level dataset...")
    dataset = CharacterDataset(sample_text, seq_len=64)
    print(f"  Vocabulary size: {dataset.vocab_size}")
    print(f"  Dataset size: {len(dataset)} samples")
    print()

    # Create data loader
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Model configuration
    config = TransformerConfig(
        vocab_size=dataset.vocab_size,
        d_model=128,
        num_heads=4,
        num_layers=3,
        d_ff=512,
        max_len=128,
        dropout=0.1
    )

    print("Creating Mini Language Model...")
    print(f"  d_model: {config.d_model}")
    print(f"  num_heads: {config.num_heads}")
    print(f"  num_layers: {config.num_layers}")

    model = MiniLanguageModel(config).to(device)
    num_params = sum(p.numel() for p in model.parameters())
    print(f"  Total parameters: {num_params:,}")
    print()

    # Training setup
    optimizer = optim.AdamW(model.parameters(), lr=3e-4)
    num_epochs = 10

    print("Training...")
    print("-" * 50)

    train_losses = []
    start_time = time.time()
    samples_seen = 0

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0
        num_batches = 0

        for x, y in dataloader:
            x, y = x.to(device), y.to(device)

            optimizer.zero_grad()
            logits, loss, _ = model(x, y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1
            samples_seen += x.size(0)

        avg_loss = epoch_loss / num_batches
        train_losses.append(avg_loss)
        print(f"  Epoch {epoch+1:2d}: Loss = {avg_loss:.4f}")

    training_time = time.time() - start_time
    print("-" * 50)
    print()

    # Generate sample
    print("Generating sample text...")
    model.eval()

    start_text = "The transformer"
    start_tokens = torch.tensor(
        [[dataset.char_to_idx.get(ch, 0) for ch in start_text]],
        device=device
    )

    generated = model.generate(start_tokens, max_new_tokens=100, temperature=0.8)
    generated_text = dataset.decode(generated[0])

    print(f"Prompt: '{start_text}'")
    print(f"Generated: '{generated_text}'")
    print()

    # Save results
    result = TrainingResult(
        model_name="MiniLanguageModel",
        config=asdict(config),
        train_losses=train_losses,
        val_losses=[],
        final_loss=train_losses[-1],
        total_epochs=num_epochs,
        training_time_seconds=training_time,
        samples_seen=samples_seen
    )

    filepath = storage.save_result(result, "mini_lm_result.json")
    print(f"Results saved to: {filepath}")
    print()

    print("Summary:")
    print(f"  Final loss: {train_losses[-1]:.4f}")
    print(f"  Training time: {training_time:.1f}s")
    print(f"  Samples processed: {samples_seen:,}")

    return result


def demo_3_attention_analysis():
    """
    Demo 3: Attention Pattern Analysis

    Analyzes attention patterns across layers and heads
    to understand what the model has learned.
    """
    print("=" * 60)
    print("DEMO 3: Attention Pattern Analysis")
    print("=" * 60)
    print()

    storage = Storage()

    # Create model
    config = TransformerConfig(
        vocab_size=100,
        d_model=128,
        num_heads=8,
        num_layers=4,
        d_ff=512
    )

    print("Creating transformer encoder...")
    print(f"  Layers: {config.num_layers}, Heads: {config.num_heads}")
    model = TransformerEncoder(config)
    model.eval()
    print()

    # Create sample input
    seq_len = 20
    batch_size = 4
    x = torch.randint(0, config.vocab_size, (batch_size, seq_len))

    print(f"Processing batch of {batch_size} sequences, length {seq_len}...")
    with torch.no_grad():
        output, attention_weights_list = model(x)
    print()

    # Analyze each layer and head
    print("Attention Pattern Analysis:")
    print("=" * 50)

    all_analyses = []

    for layer_idx, layer_attn in enumerate(attention_weights_list):
        print(f"\nLayer {layer_idx}:")
        print("-" * 40)

        for head_idx in range(config.num_heads):
            analysis = analyze_attention_head(layer_attn, layer_idx, head_idx)
            all_analyses.append(analysis)

            print(f"  Head {head_idx}: {analysis.description}")
            print(f"    Entropy: {analysis.entropy:.2f} | "
                  f"Sparsity: {analysis.sparsity:.2f} | "
                  f"Diagonal: {analysis.diagonal_strength:.2f}")

    print()

    # Summary statistics
    print("Summary Statistics:")
    print("-" * 40)

    avg_entropy = sum(a.entropy for a in all_analyses) / len(all_analyses)
    avg_sparsity = sum(a.sparsity for a in all_analyses) / len(all_analyses)
    avg_diagonal = sum(a.diagonal_strength for a in all_analyses) / len(all_analyses)

    print(f"Average entropy: {avg_entropy:.2f}")
    print(f"Average sparsity: {avg_sparsity:.2f}")
    print(f"Average diagonal strength: {avg_diagonal:.2f}")
    print()

    # Count pattern types
    pattern_counts = {}
    for a in all_analyses:
        pattern_counts[a.description] = pattern_counts.get(a.description, 0) + 1

    print("Pattern distribution:")
    for pattern, count in sorted(pattern_counts.items()):
        pct = 100 * count / len(all_analyses)
        print(f"  {pattern}: {count} ({pct:.0f}%)")

    # Save analysis
    filepath = storage.save_attention_analysis(all_analyses, "attention_analysis.json")
    print()
    print(f"Analysis saved to: {filepath}")

    return all_analyses


def demo_4_generate_report():
    """
    Demo 4: Generate Transformer Report

    Generates a comprehensive markdown report from saved results.
    """
    print("=" * 60)
    print("DEMO 4: Generate Transformer Report")
    print("=" * 60)
    print()

    storage = Storage()

    # Load results
    lm_result = storage.load_result("mini_lm_result.json")
    attn_analysis = storage.load_result("attention_analysis.json")

    # Generate report
    lines = [
        "# Transformer Lab Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Key Concepts Demonstrated",
        "",
        "1. **Self-Attention**: Q, K, V projections with scaled dot-product",
        "2. **Multi-Head Attention**: Multiple attention patterns in parallel",
        "3. **Positional Encoding**: Adding sequence order information",
        "4. **Transformer Architecture**: Attention + FFN + residuals + layer norm",
        "",
    ]

    # LM training results
    if lm_result:
        lines.extend([
            "## Language Model Training",
            "",
            f"- **Model**: {lm_result.get('model_name', 'Unknown')}",
            f"- **Final Loss**: {lm_result.get('final_loss', 0):.4f}",
            f"- **Epochs**: {lm_result.get('total_epochs', 0)}",
            f"- **Training Time**: {lm_result.get('training_time_seconds', 0):.1f}s",
            "",
        ])

        if lm_result.get('config'):
            config = lm_result['config']
            lines.extend([
                "### Model Configuration",
                "",
                f"| Parameter | Value |",
                f"|-----------|-------|",
                f"| d_model | {config.get('d_model', 'N/A')} |",
                f"| num_heads | {config.get('num_heads', 'N/A')} |",
                f"| num_layers | {config.get('num_layers', 'N/A')} |",
                f"| d_ff | {config.get('d_ff', 'N/A')} |",
                "",
            ])

    # Attention analysis
    if attn_analysis and attn_analysis.get('analyses'):
        lines.extend([
            "## Attention Pattern Analysis",
            "",
            "| Layer | Head | Pattern | Entropy | Sparsity |",
            "|-------|------|---------|---------|----------|",
        ])

        for a in attn_analysis['analyses'][:16]:  # First 16
            lines.append(
                f"| {a['layer']} | {a['head']} | "
                f"{a['description']} | {a['entropy']:.2f} | {a['sparsity']:.2f} |"
            )

        lines.append("")

    # Key takeaways
    lines.extend([
        "## Key Takeaways",
        "",
        "1. **Attention is interpretable**: We can visualize what the model focuses on",
        "2. **Heads specialize**: Different heads learn different relationship types",
        "3. **Layers build abstraction**: Early layers capture local patterns, later layers capture global",
        "4. **Scaling works**: Larger models with more data perform better",
        "",
        "---",
        "",
        "*Generated by Neural Dojo Transformer Lab*",
    ])

    report = "\n".join(lines)

    # Save report
    report_path = os.path.join(storage.storage_dir, "transformer_report.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print("Report generated successfully!")
    print()
    print(f"Report saved to: {report_path}")
    print()
    print("Preview:")
    print("-" * 50)
    for line in lines[:35]:
        print(line)
    if len(lines) > 35:
        print("...")
    print("-" * 50)

    return report_path


# ============================================================================
# MAIN
# ============================================================================

def print_help():
    """Print usage information."""
    print("""
Transformer Lab - Module 30 Deliverable
========================================

A comprehensive lab for understanding and building transformers.

Usage:
    python deliverable_transformer_lab.py <command>

Commands:
    demo1   Visualize self-attention patterns
    demo2   Train a mini language model
    demo3   Analyze attention patterns across layers/heads
    demo4   Generate a comprehensive report
    help    Show this help message

Examples:
    python deliverable_transformer_lab.py demo1
    python deliverable_transformer_lab.py demo2
    python deliverable_transformer_lab.py demo3
    python deliverable_transformer_lab.py demo4

Results are saved to .transformer_lab/

This is the HEUREKA MOMENT module - understand why "Attention Is All You Need"!
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_attention_visualization()
    elif command == "demo2":
        demo_2_train_mini_lm()
    elif command == "demo3":
        demo_3_attention_analysis()
    elif command == "demo4":
        demo_4_generate_report()
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
