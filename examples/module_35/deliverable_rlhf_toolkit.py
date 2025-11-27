#!/usr/bin/env python3
"""
Module 35 Deliverable: RLHF Training Toolkit

A comprehensive toolkit for understanding Reinforcement Learning from Human
Feedback (RLHF) including reward modeling, DPO, KTO, and training pipelines.

This toolkit demonstrates:
- Bradley-Terry reward model training
- Direct Preference Optimization (DPO)
- Kahneman-Tversky Optimization (KTO)
- Preference data simulation and analysis
- RLHF training pipeline visualization

Usage:
    python deliverable_rlhf_toolkit.py demo1  # Reward model training
    python deliverable_rlhf_toolkit.py demo2  # DPO vs PPO comparison
    python deliverable_rlhf_toolkit.py demo3  # KTO with unpaired feedback
    python deliverable_rlhf_toolkit.py demo4  # Full RLHF pipeline simulation
    python deliverable_rlhf_toolkit.py demo5  # Generate analysis report

Author: Neural Dojo
Module: 35 - RLHF & How LLMs Are Trained
"""

import json
import math
import os
import random
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PreferencePair:
    """A human preference comparison."""
    prompt: str
    chosen: str
    rejected: str
    margin: float = 1.0  # How much better chosen is (1.0 = slightly, 5.0 = much)


@dataclass
class SingleFeedback:
    """Single-label feedback (for KTO)."""
    prompt: str
    response: str
    is_good: bool
    score: float = 0.0  # Optional continuous score


@dataclass
class RewardModelState:
    """State of a reward model."""
    weights: Dict[str, float]
    bias: float
    training_steps: int
    loss_history: List[float]


@dataclass
class PolicyState:
    """State of a policy model."""
    name: str
    base_quality: float
    alignment_score: float
    kl_from_base: float
    training_steps: int
    reward_history: List[float]


@dataclass
class TrainingConfig:
    """Configuration for RLHF training."""
    method: str  # "ppo", "dpo", "orpo", "kto"
    learning_rate: float = 1e-5
    kl_coef: float = 0.1
    beta: float = 0.1  # For DPO/KTO
    epochs: int = 3
    batch_size: int = 8


@dataclass
class RLHFReport:
    """Comprehensive RLHF analysis report."""
    timestamp: str
    reward_model_stats: Dict
    dpo_results: Dict
    kto_results: Dict
    pipeline_results: Dict
    method_comparison: Dict
    recommendations: List[str]


# =============================================================================
# Storage Configuration
# =============================================================================

STORAGE_DIR = Path(".rlhf_toolkit")
STORAGE_DIR.mkdir(exist_ok=True)

REPORT_FILE = STORAGE_DIR / "rlhf_report.md"
PREFERENCES_FILE = STORAGE_DIR / "preferences.json"
MODEL_STATE_FILE = STORAGE_DIR / "model_state.json"


# =============================================================================
# Preference Data Generation
# =============================================================================

SAMPLE_PROMPTS = [
    "Explain quantum computing to a beginner",
    "Write a poem about artificial intelligence",
    "How do I make a good cup of coffee?",
    "What causes climate change?",
    "Explain the theory of relativity",
    "How do neural networks learn?",
    "What is the meaning of life?",
    "Describe the water cycle",
    "How does machine learning differ from traditional programming?",
    "What are the benefits of exercise?",
]

RESPONSE_QUALITIES = {
    "excellent": {
        "helpfulness": 0.9,
        "accuracy": 0.95,
        "clarity": 0.9,
        "safety": 1.0,
        "description": "Detailed, accurate, well-structured"
    },
    "good": {
        "helpfulness": 0.7,
        "accuracy": 0.8,
        "clarity": 0.75,
        "safety": 0.95,
        "description": "Helpful but could be more detailed"
    },
    "mediocre": {
        "helpfulness": 0.5,
        "accuracy": 0.6,
        "clarity": 0.5,
        "safety": 0.9,
        "description": "Basic answer, some inaccuracies"
    },
    "poor": {
        "helpfulness": 0.3,
        "accuracy": 0.4,
        "clarity": 0.3,
        "safety": 0.7,
        "description": "Unhelpful, confusing, potentially wrong"
    },
    "harmful": {
        "helpfulness": 0.1,
        "accuracy": 0.2,
        "clarity": 0.2,
        "safety": 0.1,
        "description": "Dangerous, misleading, or offensive"
    }
}


def generate_response(prompt: str, quality: str) -> str:
    """Generate a simulated response of given quality."""
    quality_info = RESPONSE_QUALITIES[quality]

    # Simulate response based on quality
    if quality == "excellent":
        return f"[Excellent response to '{prompt[:30]}...': Well-structured, comprehensive explanation with examples and nuance.]"
    elif quality == "good":
        return f"[Good response to '{prompt[:30]}...': Helpful answer covering main points.]"
    elif quality == "mediocre":
        return f"[Mediocre response to '{prompt[:30]}...': Brief, missing key details.]"
    elif quality == "poor":
        return f"[Poor response to '{prompt[:30]}...': Confusing, partially incorrect.]"
    else:
        return f"[Harmful response to '{prompt[:30]}...': Contains dangerous misinformation.]"


def generate_preference_pairs(n_pairs: int = 50) -> List[PreferencePair]:
    """Generate simulated preference pairs for training."""
    pairs = []
    quality_levels = list(RESPONSE_QUALITIES.keys())

    for _ in range(n_pairs):
        prompt = random.choice(SAMPLE_PROMPTS)

        # Choose two different quality levels
        q1, q2 = random.sample(quality_levels, 2)
        q1_info = RESPONSE_QUALITIES[q1]
        q2_info = RESPONSE_QUALITIES[q2]
        score1 = (q1_info["helpfulness"] + q1_info["accuracy"] +
                  q1_info["clarity"] + q1_info["safety"]) / 4
        score2 = (q2_info["helpfulness"] + q2_info["accuracy"] +
                  q2_info["clarity"] + q2_info["safety"]) / 4

        response1 = generate_response(prompt, q1)
        response2 = generate_response(prompt, q2)

        # Chosen is the higher quality response
        if score1 > score2:
            chosen, rejected = response1, response2
            margin = score1 - score2
        else:
            chosen, rejected = response2, response1
            margin = score2 - score1

        pairs.append(PreferencePair(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected,
            margin=margin * 5  # Scale to 0-5
        ))

    return pairs


def generate_single_feedback(n_samples: int = 100) -> List[SingleFeedback]:
    """Generate simulated single-label feedback for KTO."""
    feedback = []
    quality_levels = list(RESPONSE_QUALITIES.keys())

    for _ in range(n_samples):
        prompt = random.choice(SAMPLE_PROMPTS)
        quality = random.choice(quality_levels)
        response = generate_response(prompt, quality)

        quality_info = RESPONSE_QUALITIES[quality]
        score = sum([
            quality_info["helpfulness"],
            quality_info["accuracy"],
            quality_info["clarity"],
            quality_info["safety"]
        ]) / 4

        # Good if above threshold
        is_good = score > 0.6

        feedback.append(SingleFeedback(
            prompt=prompt,
            response=response,
            is_good=is_good,
            score=score
        ))

    return feedback


# =============================================================================
# Reward Model
# =============================================================================

class SimpleRewardModel:
    """
    Simple reward model using feature-based scoring.
    In practice, this would be a neural network.
    """

    def __init__(self):
        self.weights = {
            "length": 0.1,
            "structure": 0.2,
            "keywords": 0.3,
            "quality_indicator": 0.4
        }
        self.bias = 0.0
        self.training_steps = 0
        self.loss_history = []

    def extract_features(self, prompt: str, response: str) -> Dict[str, float]:
        """Extract features from prompt-response pair."""
        features = {}

        # Length feature (normalized)
        features["length"] = min(len(response) / 500, 1.0)

        # Structure indicators
        has_structure = "[" in response and "]" in response
        features["structure"] = 1.0 if has_structure else 0.5

        # Quality keywords
        quality_words = ["excellent", "comprehensive", "detailed", "well"]
        bad_words = ["poor", "confusing", "harmful", "wrong"]

        quality_score = sum(1 for w in quality_words if w.lower() in response.lower())
        bad_score = sum(1 for w in bad_words if w.lower() in response.lower())
        features["keywords"] = (quality_score - bad_score + 2) / 4

        # Quality indicator from response format
        if "Excellent" in response:
            features["quality_indicator"] = 0.9
        elif "Good" in response:
            features["quality_indicator"] = 0.7
        elif "Mediocre" in response:
            features["quality_indicator"] = 0.5
        elif "Poor" in response:
            features["quality_indicator"] = 0.3
        else:
            features["quality_indicator"] = 0.1

        return features

    def predict(self, prompt: str, response: str) -> float:
        """Predict reward for a prompt-response pair."""
        features = self.extract_features(prompt, response)
        reward = self.bias
        for name, value in features.items():
            reward += self.weights.get(name, 0) * value
        return reward

    def train_step(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        learning_rate: float = 0.01
    ) -> float:
        """
        One training step using Bradley-Terry loss.
        Loss = -log(sigmoid(r_chosen - r_rejected))
        """
        r_chosen = self.predict(prompt, chosen)
        r_rejected = self.predict(prompt, rejected)

        # Bradley-Terry loss
        diff = r_chosen - r_rejected
        sigmoid_diff = 1 / (1 + math.exp(-diff))
        loss = -math.log(sigmoid_diff + 1e-10)

        # Gradient update (simplified)
        features_chosen = self.extract_features(prompt, chosen)
        features_rejected = self.extract_features(prompt, rejected)

        gradient_scale = learning_rate * (1 - sigmoid_diff)

        for name in self.weights:
            grad = features_chosen.get(name, 0) - features_rejected.get(name, 0)
            self.weights[name] += gradient_scale * grad

        self.bias += gradient_scale * 0.1

        self.training_steps += 1
        self.loss_history.append(loss)

        return loss

    def train(
        self,
        preferences: List[PreferencePair],
        epochs: int = 3,
        learning_rate: float = 0.01
    ) -> Dict:
        """Train on preference dataset."""
        all_losses = []

        for epoch in range(epochs):
            epoch_losses = []
            random.shuffle(preferences)

            for pref in preferences:
                loss = self.train_step(
                    pref.prompt,
                    pref.chosen,
                    pref.rejected,
                    learning_rate
                )
                epoch_losses.append(loss)

            avg_loss = sum(epoch_losses) / len(epoch_losses)
            all_losses.append(avg_loss)
            print(f"  Epoch {epoch + 1}/{epochs}: Loss = {avg_loss:.4f}")

        return {
            "final_loss": all_losses[-1],
            "loss_history": all_losses,
            "training_steps": self.training_steps
        }

    def evaluate(self, preferences: List[PreferencePair]) -> Dict:
        """Evaluate reward model accuracy."""
        correct = 0
        total = 0
        margins = []

        for pref in preferences:
            r_chosen = self.predict(pref.prompt, pref.chosen)
            r_rejected = self.predict(pref.prompt, pref.rejected)

            if r_chosen > r_rejected:
                correct += 1
            total += 1
            margins.append(r_chosen - r_rejected)

        return {
            "accuracy": correct / total,
            "avg_margin": sum(margins) / len(margins),
            "correct": correct,
            "total": total
        }

    def get_state(self) -> RewardModelState:
        return RewardModelState(
            weights=self.weights.copy(),
            bias=self.bias,
            training_steps=self.training_steps,
            loss_history=self.loss_history.copy()
        )


# =============================================================================
# DPO Implementation
# =============================================================================

class DPOTrainer:
    """
    Direct Preference Optimization trainer.
    Trains directly on preferences without explicit reward model.
    """

    def __init__(self, beta: float = 0.1):
        self.beta = beta
        self.policy_logprobs = {}  # Simulated log probabilities
        self.ref_logprobs = {}
        self.training_steps = 0
        self.loss_history = []

    def _get_logprob(
        self,
        prompt: str,
        response: str,
        policy: str = "current"
    ) -> float:
        """
        Simulate log probability of response given prompt.
        In practice, this would be the actual model log prob.
        """
        # Use hash for deterministic simulation
        key = hash((prompt, response)) % 1000
        base_prob = -2.0 - (key / 500)  # Range: -2 to -4

        # Adjust based on quality indicators
        if "Excellent" in response:
            base_prob += 0.5
        elif "Poor" in response or "Harmful" in response:
            base_prob -= 0.5

        # Current policy gets slight boost from training
        if policy == "current":
            base_prob += 0.1 * min(self.training_steps / 100, 1.0)

        return base_prob

    def compute_dpo_loss(
        self,
        prompt: str,
        chosen: str,
        rejected: str
    ) -> float:
        """
        Compute DPO loss for a preference pair.

        Loss = -log(sigmoid(beta * (
            (pi_chosen - ref_chosen) - (pi_rejected - ref_rejected)
        )))
        """
        # Get log probs
        pi_chosen = self._get_logprob(prompt, chosen, "current")
        pi_rejected = self._get_logprob(prompt, rejected, "current")
        ref_chosen = self._get_logprob(prompt, chosen, "reference")
        ref_rejected = self._get_logprob(prompt, rejected, "reference")

        # DPO objective
        logits = self.beta * (
            (pi_chosen - ref_chosen) -
            (pi_rejected - ref_rejected)
        )

        # Loss
        loss = -math.log(1 / (1 + math.exp(-logits)) + 1e-10)

        return loss

    def train_step(self, prompt: str, chosen: str, rejected: str) -> float:
        """One DPO training step."""
        loss = self.compute_dpo_loss(prompt, chosen, rejected)
        self.training_steps += 1
        self.loss_history.append(loss)
        return loss

    def train(
        self,
        preferences: List[PreferencePair],
        epochs: int = 3
    ) -> Dict:
        """Train using DPO."""
        all_losses = []

        for epoch in range(epochs):
            epoch_losses = []
            random.shuffle(preferences)

            for pref in preferences:
                loss = self.train_step(pref.prompt, pref.chosen, pref.rejected)
                epoch_losses.append(loss)

            avg_loss = sum(epoch_losses) / len(epoch_losses)
            all_losses.append(avg_loss)
            print(f"  Epoch {epoch + 1}/{epochs}: DPO Loss = {avg_loss:.4f}")

        return {
            "final_loss": all_losses[-1],
            "loss_history": all_losses,
            "training_steps": self.training_steps,
            "method": "DPO"
        }


# =============================================================================
# KTO Implementation
# =============================================================================

class KTOTrainer:
    """
    Kahneman-Tversky Optimization trainer.
    Works with unpaired good/bad feedback instead of comparisons.
    """

    def __init__(self, beta: float = 0.1):
        self.beta = beta
        self.training_steps = 0
        self.loss_history = []
        self.good_count = 0
        self.bad_count = 0

    def _get_logprob(
        self,
        prompt: str,
        response: str,
        policy: str = "current"
    ) -> float:
        """Simulate log probability."""
        key = hash((prompt, response)) % 1000
        base_prob = -2.0 - (key / 500)

        if "Excellent" in response or "Good" in response:
            base_prob += 0.3
        elif "Poor" in response or "Harmful" in response:
            base_prob -= 0.3

        if policy == "current":
            base_prob += 0.1 * min(self.training_steps / 100, 1.0)

        return base_prob

    def compute_kto_loss(
        self,
        prompt: str,
        response: str,
        is_good: bool
    ) -> float:
        """
        Compute KTO loss for single feedback.

        For good responses: loss = 1 - sigmoid(beta * ratio)
        For bad responses: loss = sigmoid(beta * ratio)
        """
        pi_logprob = self._get_logprob(prompt, response, "current")
        ref_logprob = self._get_logprob(prompt, response, "reference")

        ratio = pi_logprob - ref_logprob

        if is_good:
            # Maximize probability of good responses
            sigmoid_val = 1 / (1 + math.exp(-self.beta * ratio))
            loss = 1 - sigmoid_val
            self.good_count += 1
        else:
            # Minimize probability of bad responses
            sigmoid_val = 1 / (1 + math.exp(-self.beta * ratio))
            loss = sigmoid_val
            self.bad_count += 1

        return loss

    def train_step(
        self,
        prompt: str,
        response: str,
        is_good: bool
    ) -> float:
        """One KTO training step."""
        loss = self.compute_kto_loss(prompt, response, is_good)
        self.training_steps += 1
        self.loss_history.append(loss)
        return loss

    def train(
        self,
        feedback: List[SingleFeedback],
        epochs: int = 3
    ) -> Dict:
        """Train using KTO."""
        all_losses = []

        for epoch in range(epochs):
            epoch_losses = []
            random.shuffle(feedback)

            for fb in feedback:
                loss = self.train_step(fb.prompt, fb.response, fb.is_good)
                epoch_losses.append(loss)

            avg_loss = sum(epoch_losses) / len(epoch_losses)
            all_losses.append(avg_loss)
            print(f"  Epoch {epoch + 1}/{epochs}: KTO Loss = {avg_loss:.4f}")

        return {
            "final_loss": all_losses[-1],
            "loss_history": all_losses,
            "training_steps": self.training_steps,
            "good_samples": self.good_count,
            "bad_samples": self.bad_count,
            "method": "KTO"
        }


# =============================================================================
# RLHF Pipeline Simulation
# =============================================================================

class RLHFPipeline:
    """
    Simulate full RLHF training pipeline.
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.policy_state = PolicyState(
            name="policy",
            base_quality=0.5,
            alignment_score=0.3,
            kl_from_base=0.0,
            training_steps=0,
            reward_history=[]
        )
        self.metrics = defaultdict(list)

    def simulate_ppo_step(
        self,
        reward_model: SimpleRewardModel,
        prompt: str
    ) -> Dict:
        """Simulate one PPO training step."""
        # Generate response (simulated)
        quality_prob = self.policy_state.alignment_score
        if random.random() < quality_prob:
            quality = random.choice(["excellent", "good"])
        else:
            quality = random.choice(["mediocre", "poor"])

        response = generate_response(prompt, quality)

        # Get reward
        reward = reward_model.predict(prompt, response)

        # Compute KL (simulated)
        kl = 0.01 * (1 + self.policy_state.training_steps / 100)
        self.policy_state.kl_from_base = kl

        # Final reward with KL penalty
        final_reward = reward - self.config.kl_coef * kl

        # Update policy (simulated improvement)
        if final_reward > 0.5:
            self.policy_state.alignment_score = min(
                0.95,
                self.policy_state.alignment_score + 0.005
            )

        self.policy_state.training_steps += 1
        self.policy_state.reward_history.append(reward)

        return {
            "reward": reward,
            "kl": kl,
            "final_reward": final_reward,
            "alignment": self.policy_state.alignment_score
        }

    def run_ppo_training(
        self,
        reward_model: SimpleRewardModel,
        prompts: List[str],
        steps: int = 100
    ) -> Dict:
        """Run PPO training simulation."""
        print("\n  Running PPO Training Simulation...")

        for step in range(steps):
            prompt = random.choice(prompts)
            metrics = self.simulate_ppo_step(reward_model, prompt)

            self.metrics["reward"].append(metrics["reward"])
            self.metrics["kl"].append(metrics["kl"])
            self.metrics["alignment"].append(metrics["alignment"])

            if (step + 1) % 20 == 0:
                avg_reward = sum(self.metrics["reward"][-20:]) / 20
                print(f"    Step {step + 1}: Avg Reward = {avg_reward:.4f}, "
                      f"Alignment = {metrics['alignment']:.3f}")

        return {
            "final_alignment": self.policy_state.alignment_score,
            "final_kl": self.policy_state.kl_from_base,
            "avg_reward": sum(self.metrics["reward"]) / len(self.metrics["reward"]),
            "total_steps": self.policy_state.training_steps
        }


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_reward_model():
    """Demo 1: Reward Model Training."""
    print("=" * 70)
    print("Demo 1: Bradley-Terry Reward Model Training")
    print("=" * 70)
    print()

    print("What is a Reward Model?")
    print("-" * 40)
    print("A reward model predicts human preferences:")
    print("  Input: (prompt, response)")
    print("  Output: Scalar reward (higher = better)")
    print()
    print("Training: Learn to predict which response humans prefer")
    print("  Given: Response A vs Response B")
    print("  Loss: -log(sigmoid(R(A) - R(B))) when A is preferred")
    print()

    # Generate preference data
    print("Generating preference pairs...")
    preferences = generate_preference_pairs(50)
    print(f"  Generated {len(preferences)} preference pairs")
    print()

    # Show some examples
    print("Sample Preference Pairs:")
    print("-" * 40)
    for i, pref in enumerate(preferences[:3]):
        print(f"\n  Pair {i + 1}:")
        print(f"    Prompt: {pref.prompt[:40]}...")
        print(f"    Chosen: {pref.chosen[:50]}...")
        print(f"    Rejected: {pref.rejected[:50]}...")
        print(f"    Margin: {pref.margin:.2f}")
    print()

    # Train reward model
    print("Training Reward Model:")
    print("-" * 40)
    reward_model = SimpleRewardModel()

    # Split data
    train_prefs = preferences[:40]
    test_prefs = preferences[40:]

    train_results = reward_model.train(train_prefs, epochs=3)
    print()

    # Evaluate
    print("Evaluation:")
    print("-" * 40)
    eval_results = reward_model.evaluate(test_prefs)
    print(f"  Test Accuracy: {eval_results['accuracy']:.1%}")
    print(f"  Avg Margin: {eval_results['avg_margin']:.3f}")
    print(f"  Correct: {eval_results['correct']}/{eval_results['total']}")
    print()

    # Show learned weights
    print("Learned Reward Model Weights:")
    print("-" * 40)
    for name, weight in reward_model.weights.items():
        print(f"  {name}: {weight:.4f}")
    print(f"  bias: {reward_model.bias:.4f}")
    print()

    print("✅ Reward model trained successfully!")
    print("   Key insight: Comparisons are easier than absolute scores")
    print()


def demo_2_dpo_comparison():
    """Demo 2: DPO vs PPO Comparison."""
    print("=" * 70)
    print("Demo 2: DPO vs PPO-based RLHF")
    print("=" * 70)
    print()

    print("The PPO Problem:")
    print("-" * 40)
    print("PPO-based RLHF requires 4 models:")
    print("  1. Policy model (being trained)")
    print("  2. Reference model (frozen SFT)")
    print("  3. Reward model (trained separately)")
    print("  4. Value model (for PPO)")
    print()
    print("This is expensive, slow, and unstable!")
    print()

    print("DPO Solution:")
    print("-" * 40)
    print("Direct Preference Optimization needs only 2 models:")
    print("  1. Policy model (being trained)")
    print("  2. Reference model (frozen SFT)")
    print()
    print("Key insight: The RLHF objective has a closed-form solution!")
    print("We can train directly on preferences without explicit reward.")
    print()

    # Generate preferences
    preferences = generate_preference_pairs(50)

    # Train with DPO
    print("Training with DPO:")
    print("-" * 40)
    dpo_trainer = DPOTrainer(beta=0.1)
    dpo_results = dpo_trainer.train(preferences, epochs=3)
    print()

    # Compare methods
    print("Method Comparison:")
    print("-" * 40)
    print(f"\n{'Aspect':<25} {'PPO':<20} {'DPO':<20}")
    print("-" * 65)
    print(f"{'Models Required':<25} {'4':<20} {'2':<20}")
    print(f"{'Reward Model':<25} {'Required':<20} {'Not needed':<20}")
    print(f"{'Generation During Train':<25} {'Yes (slow)':<20} {'No (fast)':<20}")
    print(f"{'Stability':<25} {'Unstable':<20} {'Stable':<20}")
    print(f"{'Hyperparameters':<25} {'Many':<20} {'Few (just beta)':<20}")
    print(f"{'Training Speed':<25} {'1x':<20} {'~10x faster':<20}")
    print()

    print("DPO Loss Function:")
    print("-" * 40)
    print("  L = -log(sigmoid(beta * ((pi_w - ref_w) - (pi_l - ref_l))))")
    print()
    print("  where:")
    print("    pi_w = log P(chosen | prompt) under policy")
    print("    pi_l = log P(rejected | prompt) under policy")
    print("    ref_* = same under reference model")
    print("    beta = temperature (typically 0.1)")
    print()

    print("✅ DPO: Simpler, faster, more stable than PPO!")
    print("   Most new models (Llama 3, etc.) use DPO")
    print()


def demo_3_kto():
    """Demo 3: KTO with Unpaired Feedback."""
    print("=" * 70)
    print("Demo 3: KTO - Kahneman-Tversky Optimization")
    print("=" * 70)
    print()

    print("The Pairing Problem:")
    print("-" * 40)
    print("Both PPO and DPO require paired comparisons:")
    print("  - Need: 'Response A is better than B for prompt X'")
    print("  - Problem: Pairing is expensive to collect")
    print()
    print("Real feedback is often unpaired:")
    print("  - Thumbs up/down on a single response")
    print("  - Star ratings (1-5)")
    print("  - 'This was helpful' / 'This was not helpful'")
    print()

    print("KTO Solution:")
    print("-" * 40)
    print("KTO works with single-label feedback:")
    print("  - Good responses: Maximize probability")
    print("  - Bad responses: Minimize probability")
    print()
    print("Based on Kahneman-Tversky prospect theory:")
    print("  - Losses hurt more than gains help")
    print("  - KTO weights bad feedback more heavily")
    print()

    # Generate single feedback
    feedback = generate_single_feedback(100)
    good_count = sum(1 for f in feedback if f.is_good)
    bad_count = len(feedback) - good_count

    print(f"Generated {len(feedback)} feedback samples:")
    print(f"  Good (thumbs up): {good_count}")
    print(f"  Bad (thumbs down): {bad_count}")
    print()

    # Show examples
    print("Sample Feedback:")
    print("-" * 40)
    for i, fb in enumerate(feedback[:4]):
        label = "👍 Good" if fb.is_good else "👎 Bad"
        print(f"  {i + 1}. {label}: {fb.response[:50]}...")
    print()

    # Train with KTO
    print("Training with KTO:")
    print("-" * 40)
    kto_trainer = KTOTrainer(beta=0.1)
    kto_results = kto_trainer.train(feedback, epochs=3)
    print()

    print("KTO Loss Function:")
    print("-" * 40)
    print("  For good responses: L = 1 - sigmoid(beta * ratio)")
    print("  For bad responses:  L = sigmoid(beta * ratio)")
    print()
    print("  where ratio = log P_policy(y|x) - log P_ref(y|x)")
    print()

    print("KTO vs DPO:")
    print("-" * 40)
    print(f"\n{'Aspect':<25} {'DPO':<20} {'KTO':<20}")
    print("-" * 65)
    print(f"{'Data Required':<25} {'Paired comparisons':<20} {'Single labels':<20}")
    print(f"{'Collection Cost':<25} {'Higher':<20} {'Lower':<20}")
    print(f"{'Models':<25} {'2':<20} {'2':<20}")
    print(f"{'Real-world data':<25} {'Hard to get':<20} {'Easy to get':<20}")
    print()

    print("✅ KTO: Works with thumbs up/down feedback!")
    print("   Great for real-world deployment with implicit feedback")
    print()


def demo_4_pipeline():
    """Demo 4: Full RLHF Pipeline Simulation."""
    print("=" * 70)
    print("Demo 4: Full RLHF Pipeline Simulation")
    print("=" * 70)
    print()

    print("The Three-Stage Pipeline:")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │  STAGE 1: PRETRAINING                                          │
    │  └─ Next-token prediction on internet text                     │
    │  └─ Creates base model (GPT-3, LLaMA, etc.)                   │
    │  └─ Cost: $10M+, months of training                           │
    │                                                                │
    │                    ↓                                           │
    │                                                                │
    │  STAGE 2: SFT (Supervised Fine-Tuning)                        │
    │  └─ Train on human demonstrations                             │
    │  └─ Teaches instruction-following format                      │
    │  └─ Cost: $10K-100K, days of training                        │
    │                                                                │
    │                    ↓                                           │
    │                                                                │
    │  STAGE 3: RLHF / DPO / KTO                                    │
    │  └─ Optimize for human preferences                            │
    │  └─ Creates aligned model (ChatGPT, Claude)                  │
    │  └─ Cost: $100K-1M, weeks of training                        │
    └─────────────────────────────────────────────────────────────────┘
    """)

    # Simulate Stage 2: SFT (reward model as proxy)
    print("Simulating Stage 2: SFT...")
    print("-" * 40)
    preferences = generate_preference_pairs(50)
    reward_model = SimpleRewardModel()
    reward_model.train(preferences, epochs=2)
    print()

    # Simulate Stage 3: RLHF
    print("Simulating Stage 3: RLHF with PPO...")
    print("-" * 40)
    config = TrainingConfig(
        method="ppo",
        kl_coef=0.1,
        epochs=3
    )
    pipeline = RLHFPipeline(config)

    results = pipeline.run_ppo_training(
        reward_model,
        SAMPLE_PROMPTS,
        steps=100
    )
    print()

    print("Training Results:")
    print("-" * 40)
    print(f"  Initial Alignment: 0.30")
    print(f"  Final Alignment: {results['final_alignment']:.3f}")
    print(f"  Improvement: {(results['final_alignment'] - 0.3) / 0.3 * 100:.1f}%")
    print(f"  Final KL: {results['final_kl']:.4f}")
    print(f"  Avg Reward: {results['avg_reward']:.3f}")
    print()

    print("Why KL Penalty Matters:")
    print("-" * 40)
    print("  Without KL penalty → Reward hacking!")
    print("  Model finds degenerate patterns that score high")
    print("  but are clearly wrong (e.g., repeating 'good' 1000x)")
    print()
    print("  KL penalty keeps model close to SFT baseline")
    print("  Prevents straying too far from sensible behavior")
    print()

    print("✅ Full RLHF pipeline simulated!")
    print("   Key: Pretraining → SFT → RLHF = ChatGPT")
    print()


def demo_5_report():
    """Demo 5: Generate Comprehensive Report."""
    print("=" * 70)
    print("Demo 5: RLHF Analysis Report")
    print("=" * 70)
    print()

    print("Generating comprehensive report...")

    # Run all analyses
    preferences = generate_preference_pairs(50)
    feedback = generate_single_feedback(100)

    # Reward model
    reward_model = SimpleRewardModel()
    rm_train = reward_model.train(preferences[:40], epochs=2)
    rm_eval = reward_model.evaluate(preferences[40:])

    # DPO
    dpo = DPOTrainer(beta=0.1)
    dpo_results = dpo.train(preferences, epochs=2)

    # KTO
    kto = KTOTrainer(beta=0.1)
    kto_results = kto.train(feedback, epochs=2)

    # Generate report
    report = f"""# RLHF Training Toolkit Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overview

This report analyzes RLHF (Reinforcement Learning from Human Feedback)
concepts demonstrated in the toolkit.

## The Three-Stage Pipeline

| Stage | Data | Objective | Result |
|-------|------|-----------|--------|
| Pretraining | Internet text | Next-token prediction | Base model |
| SFT | Demonstrations | Instruction following | Helpful format |
| RLHF | Preferences | Human alignment | ChatGPT/Claude |

## 1. Reward Model Training

**Bradley-Terry Loss**: -log(sigmoid(R_chosen - R_rejected))

| Metric | Value |
|--------|-------|
| Training Loss | {rm_train['final_loss']:.4f} |
| Test Accuracy | {rm_eval['accuracy']:.1%} |
| Avg Margin | {rm_eval['avg_margin']:.3f} |

**Key Insight**: Comparisons are easier than absolute judgments!
Humans can quickly say "A is better than B" but struggle with
"Rate A from 1-10."

## 2. DPO (Direct Preference Optimization)

**Loss**: -log(sigmoid(beta * ((pi_w - ref_w) - (pi_l - ref_l))))

| Metric | Value |
|--------|-------|
| Final Loss | {dpo_results['final_loss']:.4f} |
| Training Steps | {dpo_results['training_steps']} |
| Beta | 0.1 |

**Advantages over PPO**:
- 2 models instead of 4
- No reward model needed
- No generation during training
- 10x faster
- More stable

## 3. KTO (Kahneman-Tversky Optimization)

| Metric | Value |
|--------|-------|
| Final Loss | {kto_results['final_loss']:.4f} |
| Good Samples | {kto_results['good_samples']} |
| Bad Samples | {kto_results['bad_samples']} |

**Advantage**: Works with unpaired thumbs up/down feedback!

## Method Comparison

| Method | Models | Data | Speed | Stability | Real-world |
|--------|--------|------|-------|-----------|------------|
| PPO | 4 | Pairs | 1x | Unstable | Hard |
| DPO | 2 | Pairs | 10x | Stable | Moderate |
| ORPO | 1 | Pairs | 15x | Stable | Moderate |
| KTO | 2 | Single | 10x | Stable | Easy |

## Recommendations

1. **For new projects**: Start with DPO (simpler, faster)
2. **For implicit feedback**: Use KTO (thumbs up/down)
3. **For research**: PPO gives more control
4. **For production**: DPO or ORPO for efficiency

## Key Equations

**Bradley-Terry (Reward Model)**:
```
P(A > B) = sigmoid(R(A) - R(B))
```

**DPO Loss**:
```
L = -log(sigmoid(β * ((π_w - ref_w) - (π_l - ref_l))))
```

**KTO Loss**:
```
Good: L = 1 - sigmoid(β * ratio)
Bad:  L = sigmoid(β * ratio)
```

**PPO Objective**:
```
max E[R(x,y)] - β * KL(π || π_ref)
```

---

## The Heureka Moment

**How did GPT-3 become ChatGPT?**

GPT-3 could complete text but wouldn't answer questions.
Adding RLHF taught it:
- To be helpful (answer questions)
- To be harmless (refuse dangerous requests)
- To be honest (admit uncertainty)

**The key insight**: You can't just train on "predict next word."
You need to train on "be helpful to humans."
RLHF bridges that gap!

---

*Generated by Neural Dojo RLHF Toolkit*
"""

    with open(REPORT_FILE, 'w') as f:
        f.write(report)

    print(f"✅ Report saved to {REPORT_FILE}")
    print()

    print("Report Summary:")
    print("-" * 40)
    print(f"  Reward Model Accuracy: {rm_eval['accuracy']:.1%}")
    print(f"  DPO Final Loss: {dpo_results['final_loss']:.4f}")
    print(f"  KTO Final Loss: {kto_results['final_loss']:.4f}")
    print()

    print("Key Takeaways:")
    print("-" * 40)
    print("  1. RLHF transforms base models into helpful assistants")
    print("  2. DPO is simpler and faster than PPO")
    print("  3. KTO works with implicit feedback (thumbs up/down)")
    print("  4. KL penalty prevents reward hacking")
    print("  5. The secret: Pretraining → SFT → RLHF = ChatGPT")
    print()


def show_help():
    """Show help information."""
    print("=" * 70)
    print("Module 35 Deliverable: RLHF Training Toolkit")
    print("=" * 70)
    print()
    print("Understand how ChatGPT and Claude were trained!")
    print()
    print("Usage:")
    print("  python deliverable_rlhf_toolkit.py <command>")
    print()
    print("Commands:")
    print("  demo1    Bradley-Terry reward model training")
    print("  demo2    DPO vs PPO comparison")
    print("  demo3    KTO with unpaired feedback")
    print("  demo4    Full RLHF pipeline simulation")
    print("  demo5    Generate comprehensive report")
    print("  help     Show this help message")
    print()
    print("Examples:")
    print("  python deliverable_rlhf_toolkit.py demo1  # Reward model")
    print("  python deliverable_rlhf_toolkit.py demo2  # DPO explained")
    print("  python deliverable_rlhf_toolkit.py demo5  # Full analysis")
    print()
    print("Storage: Results saved to .rlhf_toolkit/")
    print()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        'demo1': demo_1_reward_model,
        'demo2': demo_2_dpo_comparison,
        'demo3': demo_3_kto,
        'demo4': demo_4_pipeline,
        'demo5': demo_5_report,
        'help': show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python deliverable_rlhf_toolkit.py help' for usage.")


if __name__ == "__main__":
    main()
