# Neural Dojo: Module Index

**Last Updated**: 2025-11-22 (Session #8 - Quality Enhanced)
**Quick Reference**: All 40 modules at a glance

---

## 🔍 How to Use This Index

- **Jump to module**: Click module links to view theory/examples
- **Check status**: 🟢 Complete | 🟡 In Progress | ⚪ Not Started
- **Find prerequisites**: See what to complete first
- **Search by topic**: Use keywords to find relevant modules

---

## 📊 Quick Stats

- **Total Modules**: 40 (Module 0 + Phases 1-9)
- **Total Duration**: 150-214 hours
- **Completed**: 11/40 (28%) 🎉
- **Foundation**: Module 0 + Phases 1-2 Complete!
- **Next Up**: Phase 3 - Building with AI Toolkits
- **New**: Phase 9 (Modules 38-40) - History of AI/ML (Optional)

---

## Module 0: Prerequisites & Environment Setup

**Duration**: 2-3 hours | **Prerequisites**: None - start here! | **Status**: 🟢 Complete
**Topics**: Python 3.10+ setup, venv, API keys (Claude/OpenAI), environment verification
**📖 Theory**: [module_00_prerequisites.md](notes/module_00_prerequisites.md)
**💻 Examples**: [module_00/](../../examples/module_00/) (test_environment.py, test_claude_api.py, test_openai_api.py)

---

## Phase 1: AI-Native Development (Modules 1-5) ✅

**Status**: 🟢 Complete (5/5 modules)

### Module 1: Foundations of AI-Driven Development
**Duration**: 4-5 hours | **Prerequisites**: Module 0 | **Status**: 🟢 Complete
**Topics**: AI development landscape, AI coding assistants, pair programming, when to use AI
**📖 Theory**: [module_01_ai_driven_development.md](notes/module_01_ai_driven_development.md)
**💻 Examples**: [module_01/](../../examples/module_01/) (patterns/, project/pyanalyzer.py)

### Module 2: Prompt Engineering Fundamentals 🔮
**Duration**: 5-6 hours | **Prerequisites**: Module 1 | **Status**: 🟢 Complete
**Topics**: Prompt structure, few-shot learning, chain-of-thought, prompt security
**📖 Theory**: [module_02_prompt_engineering.md](notes/module_02_prompt_engineering.md)
**💻 Examples**: [module_02/](../../examples/module_02/) (8 prompt examples)
**🔮 Heureka**: Prompts are the new programming interface!

### Module 3: AI-Powered Code Generation
**Duration**: 4-5 hours | **Prerequisites**: Modules 1-2 | **Status**: 🟢 Complete
**Topics**: Code from natural language, refactoring, debugging, test generation
**📖 Theory**: [module_03_code_generation.md](notes/module_03_code_generation.md)
**💻 Examples**: [module_03/](../../examples/module_03/) (basic_generation.py)

### Module 4: AI-Assisted Debugging & Optimization
**Duration**: 4-5 hours | **Prerequisites**: Modules 1-3 | **Status**: 🟢 Complete
**Topics**: Bug finding, performance optimization, AI debugging strategies
**📖 Theory**: [module_04_debugging.md](notes/module_04_debugging.md)
**📋 Deliverable**: [module_04_debugging_log.md](../deliverables/module_04_debugging_log.md)

### Module 5: Building with AI Coding Assistants
**Duration**: 5-6 hours | **Prerequisites**: Modules 1-4 | **Status**: 🟢 Complete
**Topics**: Claude Code workflows, GitHub Copilot, Cursor IDE, complete project
**📖 Theory**: [module_05_ai_tools.md](notes/module_05_ai_tools.md)
**📋 Deliverable**: [module_05_ai_workflow.md](../deliverables/module_05_ai_workflow.md)

---

## Phase 2: Generative AI Fundamentals (Modules 6-10) ✅

**Status**: 🟢 Complete (5/5 modules)

### Module 6: Introduction to Large Language Models
**Duration**: 5-6 hours | **Prerequisites**: Phase 1 complete | **Status**: 🟢 Complete
**Topics**: Transformer architecture, GPT/Claude/Llama, model sizes, open vs proprietary
**📖 Theory**: [module_06_intro_to_llms.md](notes/module_06_intro_to_llms.md)
**💻 Examples**: [module_06/](../../examples/module_06/) (01_model_comparison.py)

### Module 7: Tokenization & Text Processing
**Duration**: 4-5 hours | **Prerequisites**: Module 6 | **Status**: 🟢 Complete
**Topics**: BPE, WordPiece, SentencePiece, token counting, multilingual tokenization
**📖 Theory**: [module_07_tokenization.md](notes/module_07_tokenization.md)
**💻 Examples**: [module_07/](../../examples/module_07/) (token_counter.py, optimization.py, multilingual.py)

### Module 8: Text Generation & Sampling Strategies
**Duration**: 5-6 hours | **Prerequisites**: Modules 6-7 | **Status**: 🟢 Complete
**Topics**: Autoregressive generation, temperature, top-p, top-k, repetition penalties
**📖 Theory**: [module_08_text_generation.md](notes/module_08_text_generation.md)
**💻 Examples**: [module_08/](../../examples/module_08/) (sampling_playground.py, temperature_explorer.py)

### Module 9: Embeddings & Semantic Similarity
**Duration**: 2-3 hours | **Prerequisites**: Modules 6-8 | **Status**: 🟢 Complete
**Topics**: Dense vectors, cosine similarity, semantic applications, OpenAI/Sentence-BERT
**📖 Theory**: [module_09_embeddings.md](notes/module_09_embeddings.md)
**💻 Examples**: [module_09/](../../examples/module_09/) (embedding_basics.py, semantic_applications.py)

### Module 10: Vector Spaces & Semantic Search 🔮
**Duration**: 2-3 hours | **Prerequisites**: Module 9 | **Status**: 🟢 Complete
**Topics**: Vector arithmetic, semantic space geometry, FAISS, ANN, HNSW
**📖 Theory**: [module_10_vector_spaces.md](notes/module_10_vector_spaces.md)
**💻 Examples**: [module_10/](../../examples/module_10/) (vector_arithmetic.py, production_search.py)
**🔮 Heureka**: Math works on meaning! `king - man + woman ≈ queen`

---

## Phase 3: Building with AI Toolkits (Modules 11-18) ⏭️

**Status**: ⚪ Not Started (0/8 modules) - **NEXT UP!**

### Module 11: Introduction to Vector Databases
**Duration**: 5-6 hours | **Prerequisites**: Modules 9-10 | **Status**: ⚪ Not Started
**Topics**: Qdrant, Pinecone, Weaviate, Chroma, indexing, metadata filtering
**Heureka**: None

### Module 12: Building Your First RAG System
**Duration**: 6-7 hours | **Prerequisites**: Modules 10-11 | **Status**: ⚪
**Topics**: RAG architecture, document chunking, retrieval scoring, evaluation
**Heureka**: None

### Module 12.5: Evaluating AI Systems ⚠️ NEW
**Duration**: 5-6 hours | **Prerequisites**: Module 12 | **Status**: ⚪
**Topics**: RAG metrics, LLM evaluation, eval datasets, A/B testing
**Heureka**: None
**Note**: Added from gap analysis

### Module 13: RAG vs Fine-tuning Trade-offs 🔮
**Duration**: 5-6 hours | **Prerequisites**: Module 12 | **Status**: ⚪
**Topics**: When to use RAG vs fine-tuning, PEFT, LoRA, QLoRA, cost-benefit
**Heureka**: RAG = dynamic knowledge, Fine-tuning = behavior/style

### Module 14: LangChain Fundamentals
**Duration**: 6-7 hours | **Prerequisites**: Modules 11-13 | **Status**: ⚪
**Topics**: Chains, prompts, models, memory, LCEL, model abstraction
**Heureka**: None

### Module 15: LangChain Tools & Function Calling
**Duration**: 6-7 hours | **Prerequisites**: Module 14 | **Status**: ⚪
**Topics**: Function calling, custom tools, tool-calling agents, error handling
**Heureka**: None

### Module 16: Chain-of-Thought & Reasoning 🔮
**Duration**: 5-6 hours | **Prerequisites**: Modules 14-15 | **Status**: ⚪
**Topics**: CoT prompting, ReAct pattern, multi-step reasoning, limitations
**Heureka**: Making AI "think out loud" improves reasoning dramatically!

### Module 17: Advanced LangChain: LangGraph 🔮
**Duration**: 7-8 hours | **Prerequisites**: Modules 14-16 | **Status**: ⚪
**Topics**: StateGraph, cyclic workflows, multi-agent systems, state persistence
**Heureka**: Temperature controls probability distribution, not just "creativity"!

### Module 18: LlamaIndex & Alternative Frameworks
**Duration**: 5-6 hours | **Prerequisites**: Modules 14-17 | **Status**: ⚪
**Topics**: LlamaIndex, AutoGen, CrewAI, framework comparison, trade-offs
**Heureka**: None

---

## Phase 4: Deep Learning Foundations (Modules 19-25)

### Module 19: Python for Machine Learning
**Duration**: 5-6 hours | **Prerequisites**: Phase 3 complete | **Status**: ⚪
**Topics**: NumPy, pandas, matplotlib, seaborn, ML environment setup
**Heureka**: None

### Module 19.5: Data Engineering for ML ⚠️ NEW
**Duration**: 5-6 hours | **Prerequisites**: Module 19 | **Status**: ⚪
**Topics**: Data collection, cleaning, versioning (DVC), ETL pipelines, augmentation
**Heureka**: None
**Note**: Added from gap analysis

### Module 20: Neural Networks from Scratch
**Duration**: 7-8 hours | **Prerequisites**: Module 19 | **Status**: ⚪
**Topics**: Forward propagation, backpropagation by hand, gradient descent, MNIST
**Heureka**: None

### Module 21: PyTorch Fundamentals
**Duration**: 6-7 hours | **Prerequisites**: Module 20 | **Status**: ⚪
**Topics**: Tensors, autograd, nn.Module, optimizers, training loops
**Heureka**: None

### Module 22: Training Deep Networks
**Duration**: 7-8 hours | **Prerequisites**: Module 21 | **Status**: ⚪
**Topics**: SGD/Adam/AdamW, learning rate scheduling, overfitting, regularization
**Heureka**: None

### Module 23: Convolutional Neural Networks (CNNs)
**Duration**: 6-7 hours | **Prerequisites**: Module 22 | **Status**: ⚪
**Topics**: Convolutional layers, ResNet, EfficientNet, transfer learning
**Heureka**: None

### Module 24: Transformers & Attention Mechanisms
**Duration**: 8-9 hours | **Prerequisites**: Module 23 | **Status**: ⚪
**Topics**: Self-attention, multi-head attention, positional encoding, encoder-decoder
**Heureka**: None

### Module 25: Backpropagation Deep Dive 🔮
**Duration**: 6-7 hours | **Prerequisites**: Modules 20-24 | **Status**: ⚪
**Topics**: Chain rule, computational graphs, gradient flow, vanishing/exploding gradients
**Heureka**: Backprop is just the chain rule on graphs - elegant and simple!

---

## Phase 5: Advanced Generative AI (Modules 26-29)

### Module 26: Fine-tuning Large Language Models
**Duration**: 7-8 hours | **Prerequisites**: Phase 4 complete | **Status**: ⚪
**Topics**: Full fine-tuning vs PEFT, LoRA, QLoRA, instruction tuning
**Heureka**: None

### Module 27: Multimodal AI & Vision-Language Models
**Duration**: 7-8 hours | **Prerequisites**: Module 26 | **Status**: ⚪
**Topics**: CLIP, LLaVA, GPT-4V, cross-modal alignment, multimodal prompting
**Heureka**: None

### Module 28: Diffusion Models & Image Generation
**Duration**: 7-8 hours | **Prerequisites**: Module 27 | **Status**: ⚪
**Topics**: DDPM, U-Net, Stable Diffusion, ControlNet, LoRA for diffusion
**Heureka**: None

### Module 29: Code Generation Models
**Duration**: 6-7 hours | **Prerequisites**: Module 28 | **Status**: ⚪
**Topics**: Codex, StarCoder, CodeLlama, FIM, execution feedback loops
**Heureka**: None

---

## Phase 6: Production ML Systems (Modules 30-32)

### Module 30: MLOps & Experiment Tracking
**Duration**: 6-7 hours | **Prerequisites**: Phase 5 complete | **Status**: ⚪
**Topics**: MLflow, Weights & Biases, model versioning, artifact management
**Heureka**: None

### Module 31: Model Deployment & Serving
**Duration**: 7-8 hours | **Prerequisites**: Module 30 | **Status**: ⚪
**Topics**: FastAPI, batch inference, model updates, A/B testing
**Heureka**: None

### Module 31.5: Testing AI Systems ⚠️ NEW
**Duration**: 5-6 hours | **Prerequisites**: Module 31 | **Status**: ⚪
**Topics**: Testing non-deterministic systems, RAG testing, golden datasets
**Heureka**: None
**Note**: Added from gap analysis

### Module 32: Monitoring & Observability 🔮
**Duration**: 6-7 hours | **Prerequisites**: Module 31 | **Status**: ⚪
**Topics**: Performance metrics, data drift, token usage, cost tracking, alerting
**Heureka**: Context window economics - token costs shape architecture!

---

## Phase 7: AI for Infrastructure (Modules 33-34)

### Module 33: AI for Proactive Cloud Management
**Duration**: 7-8 hours | **Prerequisites**: Phase 6 complete | **Status**: ⚪
**Topics**: Anomaly detection, predictive scaling, capacity planning, intelligent alerting
**Heureka**: None
**Application**: Your on-prem private cloud management!

### Module 34: AIOps & Log Analysis
**Duration**: 6-7 hours | **Prerequisites**: Module 33 | **Status**: ⚪
**Topics**: LLMs for log analysis, root cause analysis, incident response, runbooks
**Heureka**: None
**Application**: Proactive vs reactive infrastructure management!

---

## Phase 8: Capstone Projects (Module 35)

### Module 35: Applied AI Projects
**Duration**: 20-30 hours (flexible) | **Prerequisites**: All phases | **Status**: ⚪
**Topics**: Choose 2-3 projects - enhance kaizen, build vibe features, contrarian AI, your own tool
**Heureka**: None
**Application**: Everything combined!

---

## 🔍 Search by Topic

### AI Development
- Module 0: Environment setup
- Module 1: AI-driven development
- Module 2: Prompt engineering 🔮
- Module 3: Code generation
- Module 4: Debugging
- Module 5: AI coding assistants

### LLMs & Text
- Module 6: LLMs intro
- Module 7: Tokenization
- Module 8: Text generation
- Module 14-18: LangChain ecosystem

### Embeddings & Search
- Module 9: Embeddings
- Module 10: Vector spaces 🔮
- Module 11: Vector databases
- Module 12: RAG systems
- Module 12.5: Evaluation ⚠️ NEW

### Deep Learning
- Module 19: Python for ML
- Module 19.5: Data engineering ⚠️ NEW
- Module 20: Neural networks from scratch
- Module 21: PyTorch
- Module 22: Training
- Module 23: CNNs
- Module 24: Transformers
- Module 25: Backpropagation 🔮

### Advanced AI
- Module 13: RAG vs fine-tuning 🔮
- Module 26: Fine-tuning LLMs
- Module 27: Multimodal AI
- Module 28: Diffusion models
- Module 29: Code generation

### Production & Ops
- Module 30: MLOps
- Module 31: Deployment
- Module 31.5: Testing ⚠️ NEW
- Module 32: Monitoring 🔮
- Module 33-34: AIOps

### Reasoning & Agents
- Module 15: Function calling
- Module 16: Chain-of-thought 🔮
- Module 17: LangGraph 🔮
- Module 18: Alternative frameworks

---

## Phase 8: Capstone Projects (Modules 35-37)

### Module 35: Kaizen Enhancement - Advanced AI Features
**Duration**: 8-10 hours | **Prerequisites**: Phases 1-7 | **Status**: ⚪
**Topics**: Hybrid search RAG, multi-agent workflows, autonomous debugging, AI code review
**Project**: Enhance kaizen with production-grade AI features

### Module 36: Vibe AI Features - Generative Content Platform
**Duration**: 8-10 hours | **Prerequisites**: Phases 1-7 | **Status**: ⚪
**Topics**: AI content generation, multimodal learning, RAG knowledge management, personalization
**Project**: Build AI-powered features for teaching platform

### Module 37: Contrarian AI Analytics - Stock Intelligence System
**Duration**: 8-10 hours | **Prerequisites**: Phases 1-7 | **Status**: ⚪
**Topics**: Financial NLP, sentiment analysis, time series forecasting, anomaly detection
**Project**: AI-driven stock analysis and insights

---

## Phase 9: History of AI/ML - Optional Enrichment 🕰️

**Note**: Optional phase for historical context. Best taken AFTER Phase 2+ for deeper appreciation.

### Module 38: The Foundations (1950s-1980s) - The Dark Ages Before Deep Learning 🕰️
**Duration**: 3-4 hours | **Prerequisites**: None (best after Phase 2+) | **Status**: ⚪
**Topics**: Birth of AI (1956), perceptron, AI winters, expert systems, backpropagation (1986)
**Stories**: Perceptron controversy, ELIZA chatbot, AI winter causes, Hinton's persistence
**💡 Fascinating Facts**: Why XOR broke the perceptron, LISP machine collapse, backpropagation discovered 3 times

### Module 39: The Deep Learning Revolution (2000s-2010s) - How Cat Pictures Saved AI 🔥
**Duration**: 3-4 hours | **Prerequisites**: None (best after Phase 2+) | **Status**: ⚪
**Topics**: ImageNet/AlexNet (2012), Word2Vec (2013), CNN/RNN/LSTM evolution, GPU revolution
**Stories**: Fei-Fei Li's ImageNet, AlexNet's 10% leap, "king - man + woman = queen" moment
**💡 Fascinating Facts**: Why GPUs beat CPUs 50×, Hinton almost quit academia, the "bitter lesson"

### Module 40: The Transformer Era (2017-Present) - Eight Researchers Changed Everything 🚀
**Duration**: 4-5 hours | **Prerequisites**: None (best after Phase 4+) | **Status**: ⚪
**Topics**: "Attention Is All You Need" (2017), BERT/GPT evolution, scaling laws, ChatGPT moment
**Stories**: Paper almost rejected, GPT-2 "too dangerous", ChatGPT's 100M users in 2 months
**💡 Fascinating Facts**: Transformer had 8 authors, GPT-4 cost $100M to train, fastest app growth ever
**Future**: Multimodal models, reasoning systems, AI agents, where we're headed (2025+)

---

## 🔮 Heureka Moments

Transformative insights that change how you think about AI:

1. **Module 2**: Prompt Engineering - Prompts as programming interface ✅ (discovered!)
2. **Module 10**: Embeddings as Semantic Space - Meaning has geometry ✅ (discovered!)
3. **Module 13**: RAG vs Fine-tuning - Different problems, different solutions
4. **Module 16**: Chain-of-Thought - Making AI show its work
5. **Module 17**: Temperature - Probability distribution control
6. **Module 25**: Backpropagation - Chain rule elegance
7. **Module 32**: Context Window Economics - Token costs shape architecture

---

## ⚠️ New Modules (From Gap Analysis)

- **Module 12.5**: Evaluating AI Systems (5-6 hours)
- **Module 19.5**: Data Engineering for ML (5-6 hours)
- **Module 31.5**: Testing AI Systems (5-6 hours)

**Total New**: 15-18 hours added

---

## 📊 Module Status Legend

- ⚪ Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔴 Blocked
- 🔮 Heureka Moment
- ⚠️ New (from gap analysis)

---

## 🔗 Quick Links

- [MASTER_CURRICULUM.md](MASTER_CURRICULUM.md) - Full curriculum details
- [START_HERE_TOMORROW.md](START_HERE_TOMORROW.md) - Session handoff
- [GAP_ANALYSIS.md](GAP_ANALYSIS.md) - Identified gaps
- [GAP_TODO.md](GAP_TODO.md) - Gap tracking
- [GLOSSARY.md](GLOSSARY.md) - AI/ML terms
- [RESOURCES.md](RESOURCES.md) - Curated learning resources

---

_Last updated: 2025-11-22 (Session #8 - Quality Enhanced)_
_Total modules: 40 (Module 0 + Phases 1-9, includes 3 optional history modules)_
_Total duration: 150-214 hours_
_Progress: 11/40 modules complete (28%)_
