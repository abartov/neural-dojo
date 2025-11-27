# Module 35 Deliverable: RLHF Training Toolkit

**Understand how ChatGPT and Claude were actually trained!**

## Features

- **Reward Model Training**: Bradley-Terry loss on preference pairs
- **DPO Implementation**: Direct Preference Optimization explained
- **KTO Training**: Works with thumbs up/down feedback
- **Pipeline Simulation**: Full Pretraining → SFT → RLHF flow
- **Method Comparison**: PPO vs DPO vs ORPO vs KTO

## Quick Start

```bash
# Navigate to module directory
cd examples/module_35

# Run demos
python deliverable_rlhf_toolkit.py demo1  # Reward model training
python deliverable_rlhf_toolkit.py demo2  # DPO vs PPO comparison
python deliverable_rlhf_toolkit.py demo3  # KTO with unpaired feedback
python deliverable_rlhf_toolkit.py demo4  # Full RLHF pipeline
python deliverable_rlhf_toolkit.py demo5  # Generate analysis report
```

## The Heureka Moment 🔮

**How did GPT-3 become ChatGPT?**

GPT-3 was impressive but frustrating:
- Wouldn't answer questions (just continued them)
- Generated harmful content without hesitation
- Made up facts confidently

Then OpenAI added RLHF, and everything changed:
- Helpful (actually answers questions)
- Harmless (refuses dangerous requests)
- Honest (admits uncertainty)

**The key insight**: You can't just train on "predict the next word."
You need to train on "be helpful to humans." RLHF bridges that gap!

## The Three Stages

```
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: PRETRAINING                                          │
│  └─ Next-token prediction on internet text                     │
│  └─ Result: Base model that completes text                     │
│                                                                │
│                    ↓                                           │
│                                                                │
│  STAGE 2: SFT (Supervised Fine-Tuning)                        │
│  └─ Train on human demonstrations                             │
│  └─ Result: Model understands Q&A format                      │
│                                                                │
│                    ↓                                           │
│                                                                │
│  STAGE 3: RLHF / DPO / KTO                                    │
│  └─ Optimize for human preferences                            │
│  └─ Result: Aligned assistant (ChatGPT, Claude)               │
└─────────────────────────────────────────────────────────────────┘
```

## Method Comparison

| Method | Models | Data | Speed | Best For |
|--------|--------|------|-------|----------|
| PPO | 4 | Pairs | 1x | Research |
| DPO | 2 | Pairs | 10x | Production |
| ORPO | 1 | Pairs | 15x | Efficiency |
| KTO | 2 | Single | 10x | Implicit feedback |

## Key Equations

**Bradley-Terry (Reward Model)**:
```
P(A > B) = sigmoid(R(A) - R(B))
Loss = -log(sigmoid(R_chosen - R_rejected))
```

**DPO Loss**:
```
L = -log(sigmoid(β * ((π_w - ref_w) - (π_l - ref_l))))
```

**PPO Objective**:
```
max E[R(x,y)] - β * KL(π || π_ref)
```

## Demo Descriptions

### Demo 1: Reward Model Training
Shows how to train a reward model from preference pairs using Bradley-Terry loss.

### Demo 2: DPO vs PPO
Compares Direct Preference Optimization with traditional PPO-based RLHF.
DPO is 10x faster and doesn't need a separate reward model!

### Demo 3: KTO
Kahneman-Tversky Optimization works with unpaired feedback (thumbs up/down).
No need for expensive A vs B comparisons!

### Demo 4: Full Pipeline
Simulates the complete RLHF training pipeline from SFT to alignment.

### Demo 5: Analysis Report
Generates a comprehensive report with all metrics and recommendations.

## Output Files

```
.rlhf_toolkit/
├── rlhf_report.md         # Analysis report
├── preferences.json       # Generated preference data
└── model_state.json       # Saved model states
```

## No API Keys Required

All demos work without external APIs using simulations of:
- Preference data generation
- Reward model training
- Policy optimization
- Pipeline execution

**Time**: ~6 hours | **Lines**: 900+ | **Author**: Neural Dojo
