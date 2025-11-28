# Neural Dojo: Master Curriculum

**From Zero to AI Guru: Master AI, ML, LLMs, and AI-Driven Development**

**Last Updated**: 2025-11-28
**Version**: 4.7.0 - COMPLETE AI GURU CURRICULUM (56 modules, 13 phases)
**Status**: Phase 8 Progress! Module 38 (Time Series) Complete!
**Total Duration**: 56 modules, 50-60 weeks (220-300 hours)

---

## 🎯 Mission

Transform you from AI novice to **AI Guru** capable of:
- Building production RAG systems with advanced patterns (GraphRAG, HyDE)
- Creating sophisticated AI agents with memory, planning, and multi-agent coordination
- Using AI to accelerate development (AI-driven coding)
- Training and deploying deep learning models
- Understanding RLHF and how modern LLMs are actually trained
- Building multimodal AI (text, audio, vision, video)
- Mastering classical ML (XGBoost, time series) - still 80% of production ML!
- Deploying AI/ML with modern DevOps & MLOps practices
- Implementing AI Safety, red teaming, and responsible AI
- Evaluating and benchmarking LLMs systematically
- Applying AI to real-world problems

---

## 🧭 Curriculum Philosophy

Following the **jamesblonde pattern**:
- **Theory-first**: Deep understanding before coding
- **Hands-on**: Every concept has working code examples
- **Production-ready**: Build real systems, not toys
- **Progressive**: Each module builds on previous knowledge
- **Practical-first**: Get productive quickly, then go deep

### 💡 Heureka Moments

Throughout this curriculum, you'll encounter transformative insights marked with 🔮:
1. **Prompt Engineering** (Module 2) - Already discovered! ✅
2. **Embeddings as Semantic Space** (Module 10) - Already discovered! ✅
3. **RAG vs Fine-tuning Trade-offs** (Module 13) - Already discovered! ✅
4. **Chain-of-Thought Reasoning** (Module 17) - 🔮
5. **Agentic Memory & Planning** (Module 20) - 🔮
6. **RLHF: How ChatGPT Was Trained** (Module 35) - 🔮
7. **Backpropagation Intuition** (Module 30) - 🔮
8. **AI Safety: The Alignment Problem** (Module 43) - 🔮

---

## 📊 Progress Tracking

| Phase | Modules | Status | Completion |
|-------|---------|--------|------------|
| Module 0: Prerequisites | 0 | 🟢 Complete | 1/1 (100%) |
| Phase 1: AI-Native Development | 1.1-1.3, 2-5 | 🟢 Complete | 7/7 (100%) |
| Phase 2: Generative AI Fundamentals | 6-10 | 🟢 Complete | 5/5 (100%) |
| Phase 3: Vector Search & RAG | 11-14 | 🟢 Complete | 4/4 (100%) |
| Phase 4: Frameworks & Agents | 15-21 | 🟢 Complete | 7/7 |
| Phase 5: Multimodal AI | 22-24 | 🟢 Complete | 3/3 |
| Phase 6: Deep Learning Foundations | 25-31 | 🟢 Complete | 7/7 |
| Phase 7: Advanced Generative AI | 32-36 | 🟢 Complete | 5/5 |
| Phase 8: Classical ML | 37-39 | 🟡 In Progress | 2/3 |
| Phase 9: AI Safety & Evaluation | 40-42 | ⚪ Not Started | 0/3 |
| Phase 10: DevOps & MLOps | 43-52 | ⚪ Not Started | 0/10 |
| Phase 11: AI for Infrastructure | 53-54 | ⚪ Not Started | 0/2 |
| Phase 12: Capstone Projects | 55-57 | ⚪ Not Started | 0/3 |
| Phase 13: History of AI (Optional) | 58-60 | ⚪ Not Started | 0/3 |
| **TOTAL** | **56 core + 3 optional** | **64% Complete** | **36/56** |

**Legend**: ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

---

## 📚 Curriculum Structure

---

## Module 0: Prerequisites & Environment Setup

**Goal**: Prepare your development environment before starting

### Module 0: Prerequisites & Environment Setup
- **Duration**: 2-3 hours
- **Prerequisites**: None - this is where you start!
- **Status**: 🟢 Complete

**Learning Objectives**:
- Verify prerequisites (Python 3.10+, command line basics)
- Set up development environment (venv, pip, IDE)
- Configure API keys for Claude and/or OpenAI
- Make your first LLM API call

**Deliverables**:
- ✅ Python 3.10+ environment verified
- ✅ Virtual environment created and activated
- ✅ `.env` file with API key(s) configured
- ✅ All test scripts passing

**Files**: `docs/curriculum/notes/module_00_prerequisites.md`, `examples/module_00/`

---

## Phase 1: AI-Native Development (Weeks 1-5)

**Goal**: Master using AI as your development partner

### Module 1.1: AI Coding Tools Landscape
- **Duration**: 4-5 hours
- **Prerequisites**: None (start here!)
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand the AI development landscape (2024-2025)
- Set up AI coding assistants (Claude Code, Cursor, GitHub Copilot)
- Learn the mental model of AI pair programming
- Master subscriptions vs API access distinction

**Deliverables**:
- ✅ Configured development environment with Claude Code
- ✅ 5 AI coding pattern demonstrations
- ✅ AI tools comparison template (13 tools evaluated)

**Files**: `docs/curriculum/notes/module_01.1_ai_coding_tools.md`, `examples/module_01/`

---

### Module 1.2: Local Models for AI Coding
- **Duration**: 3-4 hours
- **Prerequisites**: Module 1.1
- **Status**: 🟢 Complete

**Learning Objectives**:
- Install and run Ollama (local model management)
- Use local models with Aider and Continue.dev
- Implement hybrid approach (80% local, 20% API)
- Optimize costs ($0-5/month vs $50-150/month)

**Deliverables**:
- ✅ Ollama installation and setup
- ✅ Aider + local models configuration
- ✅ Continue.dev + local models setup

**Files**: `docs/curriculum/notes/module_01.2_local_models.md`, `examples/module_01.2/`

---

### Module 1.3: Claude Code & CLI Deep Dive
- **Duration**: 4-5 hours
- **Prerequisites**: Module 1.1
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master Claude Code's multi-modal operation
- Configure settings.json and CLAUDE.md
- Build custom slash commands and skills
- Implement hooks for automation

**Deliverables**:
- ✅ Optimized settings.local.json
- ✅ Custom slash commands
- ✅ Project CLAUDE.md template

**Files**: `docs/curriculum/notes/module_01.3_claude_code_deep_dive.md`

---

### Module 2: Prompt Engineering Fundamentals 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Module 1
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master the art of prompt engineering
- Understand prompt structure (system, user, assistant)
- Learn few-shot learning and chain-of-thought
- Handle edge cases and failure modes

**Deliverables**:
- ✅ Prompt engineering toolkit
- ✅ 8 working code examples
- ✅ **DELIVERABLE**: Prompt Library & Testing Framework

**💡 Heureka Moment**: Prompts are the new programming interface!

**Files**: `docs/curriculum/notes/module_02_prompt_engineering.md`, `examples/module_02/`

---

### Module 3: AI-Powered Code Generation
- **Duration**: 4-5 hours
- **Prerequisites**: Module 2
- **Status**: 🟢 Complete

**Learning Objectives**:
- Generate code from natural language
- Refactor and debug with AI
- Write tests using AI

**Deliverables**:
- ✅ AI-generated package template
- ✅ **DELIVERABLE**: Code Generation Workflow Toolkit

**Files**: `docs/curriculum/notes/module_03_code_generation.md`, `examples/module_03/`

---

### Module 4: AI-Assisted Debugging & Optimization
- **Duration**: 4-5 hours
- **Prerequisites**: Module 3
- **Status**: 🟢 Complete

**Learning Objectives**:
- Use AI to find and fix bugs
- Optimize performance with AI
- Understand AI's debugging strategies

**Deliverables**:
- ✅ AI debugging workflow
- ✅ **DELIVERABLE**: AI Debugging Assistant

**Files**: `docs/curriculum/notes/module_04_debugging.md`, `examples/module_04/`

---

### Module 5: Building with AI Coding Assistants
- **Duration**: 5-6 hours
- **Prerequisites**: Module 4
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master Claude Code, Copilot, Cursor workflows
- Build a complete project with AI assistance
- Develop your personal AI workflow

**Deliverables**:
- ✅ Tool-specific workflows
- ✅ **DELIVERABLE**: AI Tools Comparison Suite
- ✅ **Phase 1 Complete!**

**Files**: `docs/curriculum/notes/module_05_ai_tools.md`, `examples/module_05/`

---

## Phase 2: Generative AI Fundamentals (Weeks 6-10)

**Goal**: Understand how LLMs and generative AI work under the hood

### Module 6: Introduction to Large Language Models
- **Duration**: 5-6 hours
- **Prerequisites**: Phase 1 complete
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand transformer architecture at a high level
- Learn about GPT, Claude, Llama, and other LLMs
- Compare open-source vs proprietary models
- Make your first direct API integration

**Deliverables**:
- ✅ LLM landscape analysis
- ✅ **DELIVERABLE**: Model Comparison Benchmark

**Files**: `docs/curriculum/notes/module_06_intro_to_llms.md`, `examples/module_06/`

---

### Module 7: Tokenization & Text Processing
- **Duration**: 4-5 hours
- **Prerequisites**: Module 6
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand how text becomes tokens
- Learn about BPE, WordPiece, SentencePiece
- Master token counting and optimization

**Deliverables**:
- ✅ Token counter tool
- ✅ **DELIVERABLE**: Token Optimization Analyzer

**Files**: `docs/curriculum/notes/module_07_tokenization.md`, `examples/module_07/`

---

### Module 8: Text Generation & Sampling Strategies
- **Duration**: 5-6 hours
- **Prerequisites**: Module 7
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand autoregressive generation
- Master temperature, top-p, top-k sampling
- Control generation quality and creativity

**Deliverables**:
- ✅ Text generation playground
- ✅ **DELIVERABLE**: Sampling Strategy Tuner

**Files**: `docs/curriculum/notes/module_08_text_generation.md`, `examples/module_08/`

---

### Module 9: Embeddings & Semantic Similarity
- **Duration**: 2-3 hours
- **Prerequisites**: Module 8
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand embeddings as dense vectors
- Learn cosine similarity and distance metrics
- Build semantic search applications

**Deliverables**:
- ✅ Embedding generation examples
- ✅ **DELIVERABLE**: Semantic Search Engine

**Files**: `docs/curriculum/notes/module_09_embeddings.md`, `examples/module_09/`

---

### Module 10: Vector Spaces & Semantic Search 🔮
- **Duration**: 2-3 hours
- **Prerequisites**: Module 9
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master vector arithmetic (king - man + woman ≈ queen)
- Visualize semantic spaces in 2D/3D
- Build production search with FAISS

**Deliverables**:
- ✅ Vector arithmetic demonstrations
- ✅ **DELIVERABLE**: Vector Space Explorer

**💡 Heureka Moment**: Math works on meaning! Vector operations transform concepts!

**Files**: `docs/curriculum/notes/module_10_vector_spaces.md`, `examples/module_10/`

---

## Phase 3: Vector Search & RAG (Weeks 11-14)

**Goal**: Master retrieval-augmented generation systems

### Module 11: Introduction to Vector Databases
- **Duration**: 5-6 hours
- **Prerequisites**: Module 10
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand vector database architectures
- Compare Qdrant, Pinecone, Weaviate, Chroma
- Master indexing strategies and metadata filtering

**Deliverables**:
- ✅ Qdrant installation and setup
- ✅ **DELIVERABLE**: Multi-Tenant Vector Store

**Files**: `docs/curriculum/notes/module_11_vector_databases.md`, `examples/module_11/`

---

### Module 12: Building Your First RAG System
- **Duration**: 6-7 hours
- **Prerequisites**: Module 11
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand RAG architecture
- Build a simple RAG pipeline
- Implement document chunking strategies
- Measure RAG performance

**Deliverables**:
- ✅ Working RAG system
- ✅ **DELIVERABLE**: Production RAG Pipeline

**Files**: `docs/curriculum/notes/module_12_rag_systems.md`, `examples/module_12/`

---

### Module 13: RAG vs Fine-tuning Trade-offs 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Module 12
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand when to use RAG vs fine-tuning
- Master cost-benefit analysis
- Learn LoRA/QLoRA basics
- Design hybrid architectures

**Deliverables**:
- ✅ Decision framework with scoring
- ✅ **DELIVERABLE**: RAG vs Fine-tuning Decision Engine

**💡 Heureka Moment**: RAG = Dynamic Knowledge, Fine-tuning = Behavior Modification!

**Files**: `docs/curriculum/notes/module_13_rag_vs_finetuning.md`, `examples/module_13/`

---

### Module 14: Advanced RAG Patterns 🆕
- **Duration**: 6-7 hours
- **Prerequisites**: Module 13
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master GraphRAG (knowledge graph + RAG)
- Implement HyDE (Hypothetical Document Embeddings)
- Build Self-RAG (self-reflective retrieval)
- Learn Parent Document Retriever patterns
- Implement hybrid search (BM25 + semantic)
- Master reranking with cross-encoders

**Deliverables**:
- ✅ HyDE query expansion system
- ✅ Hybrid search (BM25 + Semantic)
- ✅ Cross-encoder reranking
- ✅ **DELIVERABLE**: Advanced RAG Toolkit (700+ lines)

**Key Concepts**:
- GraphRAG: Knowledge graphs for better context
- HyDE: Generate hypothetical answers, then retrieve
- Self-RAG: Reflect on retrieval quality
- Hybrid Search: BM25 (lexical) + embeddings (semantic)
- Reranking: Cross-encoders for precision
- Parent Document Retrieval: Retrieve parents, use children

**Files**: `docs/curriculum/notes/module_14_advanced_rag_patterns.md`, `examples/module_14/`

**Real-World Application**: Enhance kaizen's RAG with these advanced patterns!

---

## Phase 4: Frameworks & Agents (Weeks 15-21)

**Goal**: Master AI frameworks and build sophisticated agents

### Module 15: LangChain Fundamentals
- **Duration**: 6-7 hours
- **Prerequisites**: Module 14
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master LangChain core concepts
- Build chains and sequences
- Use LangChain memory (RunnableWithMessageHistory)
- Integrate multiple LLMs (Gemini, Claude)

**Deliverables**:
- ✅ LangChain-powered chatbot with memory
- ✅ Multi-step LCEL pipelines
- ✅ Memory-enabled conversation system
- ✅ Multi-model router

**Key Concepts**:
- Chains, prompts, models, memory
- Sequential and parallel chains
- LangChain Expression Language (LCEL)
- RunnableWithMessageHistory for stateful conversations
- Multi-provider support (Gemini, Claude)

**Files**: `docs/curriculum/notes/module_15_langchain_fundamentals.md`, `examples/module_15/`

---

### Module 16: LangChain Tools & Function Calling
- **Duration**: 6-7 hours
- **Prerequisites**: Module 15
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand function calling / tool use
- Build custom LangChain tools
- Create tool-calling agents
- Handle tool execution errors

**Deliverables**:
- ✅ Custom tool library (5 built-in tools)
- ✅ Function-calling agent (AgentExecutor)
- ✅ Tool orchestration system (deliverable)

**Key Concepts**:
- Function/tool schemas
- Tool calling protocols
- Error handling
- Tool selection strategies

**Files**: `docs/curriculum/notes/module_16_langchain_tools_function_calling.md`, `examples/module_16/`

---

### Module 17: Chain-of-Thought & Reasoning 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Module 16
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master chain-of-thought (CoT) prompting
- Implement ReAct pattern
- Build multi-step reasoning systems
- Understand reasoning limitations

**Deliverables**:
- ✅ CoT reasoning system (Zero-shot, Few-shot, Structured)
- ✅ ReAct agent implementation (with tools)
- ✅ Reasoning Engine (deliverable with benchmarks)

**Key Concepts**:
- Zero-shot CoT ("Let's think step by step")
- Few-shot CoT
- ReAct (Reason + Act)
- Self-consistency

**💡 Heureka Moment**: Making AI "think out loud" dramatically improves reasoning!

**Files**: `docs/curriculum/notes/module_17_chain_of_thought_reasoning.md`, `examples/module_17/`

---

### Module 18: LangGraph & Stateful Workflows
- **Duration**: 7-8 hours
- **Prerequisites**: Module 17
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master LangGraph for stateful workflows
- Build complex multi-agent systems
- Implement cyclic workflows
- Use StateGraph effectively

**Deliverables**:
- ✅ LangGraph-based workflow system
- ✅ Multi-agent orchestrator
- ✅ State persistence implementation
- ✅ **DELIVERABLE**: Stateful Workflow Engine (650+ lines)

**Key Concepts**:
- StateGraph architecture and compilation
- State reducers (accumulation vs replacement)
- Cyclic workflows for iterative refinement
- Conditional routing and branching
- Multi-agent patterns (supervisor, parallel, hierarchical)
- Human-in-the-loop with interrupts
- Checkpointing for persistence

**Files**: `docs/curriculum/notes/module_18_langgraph_stateful_workflows.md`, `examples/module_18/`

---

### Module 19: LlamaIndex & Alternative Frameworks
- **Duration**: 5-6 hours
- **Prerequisites**: Module 18
- **Status**: 🟢 Complete

**Learning Objectives**:
- Learn LlamaIndex for data indexing
- Compare LangChain vs LlamaIndex
- Explore AutoGen, CrewAI, others
- Choose the right framework

**Deliverables**:
- ✅ LlamaIndex fundamentals (documents, indexes, queries)
- ✅ Framework comparison (LangChain vs LlamaIndex)
- ✅ Multi-agent frameworks overview (CrewAI, AutoGen)
- ✅ **DELIVERABLE**: Framework Selector Toolkit (550+ lines)

**Key Concepts**:
- Data connectors and loaders
- Index types (Vector, Summary, Keyword, Tree)
- Query engines and chat engines
- CrewAI role-based agents
- AutoGen conversational agents
- Framework selection criteria

**Files**: `docs/curriculum/notes/module_19_llamaindex_alternative_frameworks.md`, `examples/module_19/`

---

### Module 20: Advanced Agentic AI 🆕 🔮
- **Duration**: 8-9 hours
- **Prerequisites**: Module 19
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master agent memory systems (short-term, long-term, episodic)
- Implement planning algorithms (ReWOO, Plan-and-Execute)
- Build multi-agent collaborative systems
- Design agent architectures (supervisor, swarm, hierarchical)
- Implement tool creation by agents
- Master reflection and self-correction patterns

**Deliverables**:
- ✅ Agent with persistent memory (vector + summary)
- ✅ Plan-and-execute agent
- ✅ Multi-agent team (researcher + writer + critic)
- ✅ **DELIVERABLE**: Autonomous Agent Framework (750+ lines)

**Files**: `docs/curriculum/notes/module_20_advanced_agentic_ai.md`, `examples/module_20/`

**Key Concepts**:
- **Memory Systems**:
  - Short-term: Conversation buffer
  - Long-term: Vector store for past experiences
  - Episodic: Specific interaction memories
  - Summary: Compressed conversation history
- **Planning Patterns**:
  - ReWOO: Reason Without Observation
  - Plan-and-Execute: Create plan, then execute steps
  - Tree of Thought: Explore multiple reasoning paths
- **Multi-Agent Architectures**:
  - Supervisor: One agent manages others
  - Swarm: Agents collaborate as peers
  - Hierarchical: Nested agent teams
  - Debate: Agents argue to find truth
- **Self-Improvement**:
  - Reflection: Agents evaluate their own outputs
  - Self-correction: Fix mistakes iteratively
  - Tool creation: Agents build new tools

**💡 Heureka Moment**: Agents with memory and planning can solve problems they couldn't before!

**Real-World Application**: Build autonomous agents for kaizen that remember past issues and plan solutions!

---

### Module 21: AI Agents in Production
- **Duration**: 6-7 hours
- **Prerequisites**: Module 20
- **Status**: 🟢 Complete

**Learning Objectives**:
- Deploy agents to production
- Implement guardrails and safety
- Monitor agent behavior
- Handle failures gracefully

**Deliverables**:
- ✅ Production agent patterns (stateless, stateful, circuit breaker)
- ✅ Guardrails system (input/output validation, PII, injection)
- ✅ Observability pipeline (logging, metrics, cost tracking)
- ✅ **DELIVERABLE**: Production Agent Toolkit (600+ lines)

**Key Concepts**:
- **Production Patterns**:
  - Stateless vs Stateful agent design
  - Circuit breaker (CLOSED → OPEN → HALF_OPEN)
  - Graceful degradation levels
  - Retry with exponential backoff
- **Guardrails**:
  - Input validation (prompt injection, content filtering)
  - Output guardrails (PII redaction, forbidden patterns)
  - Rate limiting (token bucket algorithm)
  - Budget controls (per-request, per-user, global)
- **Observability**:
  - Structured logging with correlation IDs
  - Metrics collection (latency, cost, success rate)
  - Cost tracking per model/user
  - Performance percentiles (P50, P95, P99)

**Files**: `docs/curriculum/notes/module_21_ai_agents_in_production.md`, `examples/module_21/`

**Real-World Application**: Deploy robust agents to kaizen with full production guardrails!

---

## Phase 5: Multimodal AI (Weeks 22-24) 🆕

**Goal**: Master AI across text, audio, vision, and video

### Module 22: Speech AI 🆕
- **Duration**: 6-7 hours
- **Prerequisites**: Phase 4 complete
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master Whisper for speech-to-text (STT)
- Build text-to-speech (TTS) systems (ElevenLabs, OpenAI TTS)
- Understand voice cloning and voice synthesis
- Implement real-time transcription
- Build voice-enabled AI assistants

**Deliverables**:
- ✅ Whisper transcription pipeline (01_speech_to_text.py)
- ✅ TTS integration (02_text_to_speech.py)
- ✅ Voice assistant (03_voice_assistant.py)
- ✅ **DELIVERABLE**: Voice AI Toolkit (deliverable_voice_ai_toolkit.py)

**Key Concepts**:
- **Speech-to-Text (STT)**:
  - Whisper architecture and models
  - Real-time vs batch transcription
  - Speaker diarization
  - Multi-language support
- **Text-to-Speech (TTS)**:
  - Neural TTS models
  - Voice cloning (ElevenLabs, Coqui)
  - Emotional expression
  - SSML for control
- **Voice AI Applications**:
  - Voice assistants
  - Meeting transcription
  - Podcast generation
  - Audiobook creation

**Real-World Application**: Add voice capabilities to vibe's teaching platform!

**Files**: `docs/curriculum/notes/module_22_speech_ai.md`, `examples/module_22/`

---

### Module 23: Vision AI & Vision-Language Models
- **Duration**: 7-8 hours
- **Prerequisites**: Module 22
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand multimodal architectures
- Master CLIP for image-text embeddings
- Use GPT-4V, Claude Vision, LLaVA
- Build image-text applications
- Implement vision-language reasoning

**Deliverables**:
- ✅ CLIP embeddings (01_clip_embeddings.py)
- ✅ Vision-Language Models (02_vision_language_models.py)
- ✅ Visual QA (03_visual_qa.py)
- ✅ **DELIVERABLE**: Vision AI Toolkit (deliverable_vision_ai_toolkit.py)

**Key Concepts**:
- CLIP architecture (image + text encoders)
- Vision encoders (ViT, SigLIP)
- Vision-language models (GPT-4V, Claude 3, LLaVA)
- Cross-modal alignment
- Multimodal prompting

**Real-World Application**: Build image search for kaizen!

**Files**: `docs/curriculum/notes/module_23_vision_ai.md`, `examples/module_23/`

---

### Module 24: Video AI & Generation 🆕
- **Duration**: 6-7 hours
- **Prerequisites**: Module 23
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand video AI architectures
- Implement video understanding (captioning, Q&A)
- Explore video generation (Sora, Runway, Pika)
- Build video analysis pipelines
- Master video summarization

**Deliverables**:
- ✅ Video understanding (01_video_understanding.py)
- ✅ Video generation concepts (02_video_generation.py)
- ✅ Video summarization (03_video_summarization.py)
- ✅ **DELIVERABLE**: Video AI Toolkit (deliverable_video_ai_toolkit.py)

**Key Concepts**:
- **Video Understanding**:
  - Frame extraction and sampling (uniform, keyframe, scene-based)
  - Scene detection (histogram correlation)
  - Video captioning with vision LLMs
  - Video Q&A (multi-frame analysis)
- **Video Generation**:
  - Sora architecture (DiT, spacetime patches)
  - Runway ML, Pika Labs, Luma
  - Text-to-video, Image-to-video
  - Prompt engineering for video
- **Video Analysis**:
  - Quality scoring (sharpness, color, brightness)
  - Chapter generation
  - Highlight extraction
  - Thumbnail selection

**Files**: `docs/curriculum/notes/module_24_video_ai.md`, `examples/module_24/`

**Real-World Application**: Build video content analysis for vibe's courses!

---

## Phase 6: Deep Learning Foundations (Weeks 25-31)

**Goal**: Master PyTorch and deep learning fundamentals

### Module 25: Python for Machine Learning
- **Duration**: 5-6 hours
- **Prerequisites**: Phase 5 complete
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master NumPy for numerical computing
- Learn pandas for data manipulation
- Understand matplotlib/seaborn for visualization

**Deliverables**:
- ✅ NumPy performance benchmarks (demo4)
- ✅ Data analysis pipeline (demo5)
- ✅ ML Data Toolkit (900+ lines)

**Files**: `docs/curriculum/notes/module_25_python_for_ml.md`, `examples/module_25/`

---

### Module 26: Neural Networks from Scratch
- **Duration**: 7-8 hours
- **Prerequisites**: Module 25
- **Status**: 🟢 Complete

**Learning Objectives**:
- Build a neural network without frameworks
- Understand forward propagation
- Implement backpropagation by hand
- Train on MNIST dataset

**Deliverables**:
- ✅ Pure Python neural network (800+ lines)
- ✅ MNIST classifier (>95% accuracy)
- ✅ Training visualizations

**Files**: `docs/curriculum/notes/module_26_neural_networks_from_scratch.md`, `examples/module_26/`

---

### Module 27: PyTorch Fundamentals
- **Duration**: 6-7 hours
- **Prerequisites**: Module 26
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master PyTorch tensors and operations
- Understand autograd (automatic differentiation)
- Build models with nn.Module
- Train neural networks with PyTorch

**Deliverables**:
- ✅ PyTorch Lab toolkit (700+ lines)
- ✅ Tensor benchmarks (PyTorch vs NumPy)
- ✅ Autograd visualization
- ✅ Training experiments

**Files**: `docs/curriculum/notes/module_27_pytorch_fundamentals.md`, `examples/module_27/`

---

### Module 28: Training Deep Networks
- **Duration**: 7-8 hours
- **Prerequisites**: Module 27
- **Status**: 🟢 Complete

**Files**: `docs/curriculum/notes/module_28_training_deep_networks.md`, `examples/module_28/`

**Learning Objectives**:
- Master training techniques (BatchNorm, LayerNorm, Dropout)
- Understand optimization algorithms (SGD, Adam, AdamW)
- Implement learning rate scheduling (warmup, cosine, 1cycle)
- Handle overfitting with early stopping and regularization
- Apply proper weight initialization (Xavier, He)
- Use gradient clipping for stable training

**Deliverables**:
- ✅ Theory document with origin stories (BatchNorm, Dropout, initialization history)
- ✅ Normalization comparison example
- ✅ Initialization comparison example
- ✅ Learning rate schedule comparison example
- ✅ Complete production training pipeline
- ✅ Training Toolkit deliverable (LR finder, init comparison, best practices)

---

### Module 29: Convolutional Neural Networks (CNNs)
- **Duration**: 6-7 hours
- **Prerequisites**: Module 28
- **Status**: 🟢 Complete

**Files**: `docs/curriculum/notes/module_29_cnns.md`, `examples/module_29/`

**Learning Objectives**:
- Understand convolutional layers
- Learn CNN architectures (ResNet, EfficientNet)
- Build image classifiers
- Apply transfer learning

**Deliverables**:
- ✅ Custom CNN architecture
- ✅ Transfer learning implementation
- ✅ CNN Vision Toolkit deliverable (architecture analysis, training, reports)

---

### Module 30: Transformers & Attention Mechanisms 🔮
- **Duration**: 8-9 hours
- **Prerequisites**: Module 29
- **Status**: 🟢 Complete

**Files**: `docs/curriculum/notes/module_30_transformers.md`, `examples/module_30/`

**Learning Objectives**:
- Master the transformer architecture
- Understand self-attention
- Implement multi-head attention
- Build a transformer from scratch

**Deliverables**:
- ✅ Transformer implementation from scratch
- ✅ Attention visualization tools
- ✅ Mini language model training
- ✅ Transformer Lab deliverable (attention analysis, training, reports)

**💡 Heureka Moment**: Attention is all you need - and now you understand why!

---

### Module 31: Backpropagation Deep Dive
- **Duration**: 6-7 hours
- **Prerequisites**: Module 30
- **Status**: 🟢 Complete

**Learning Objectives**:
- Truly understand backpropagation
- Master the chain rule
- Implement custom autograd
- Debug gradient issues

**Deliverables**:
- ✅ Custom autograd engine (Value class with full operations)
- ✅ Gradient checking utilities (numerical vs analytical verification)
- ✅ Neural network training (XOR problem with pure autograd)
- ✅ Autograd Engine deliverable (600+ lines)

**Files**: `docs/curriculum/notes/module_31_backpropagation.md`, `examples/module_31/`

---

## Phase 7: Advanced Generative AI (Weeks 32-36)

**Goal**: Master modern generative AI techniques

### Module 32: Fine-tuning Large Language Models
- **Duration**: 7-8 hours
- **Prerequisites**: Phase 6 complete
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand fine-tuning techniques
- Master LoRA and QLoRA
- Fine-tune open-source models (Llama, Mistral)
- Deploy fine-tuned models

**Deliverables**:
- ✅ Fine-tuning theory document (~700 lines)
- ✅ LoRA configuration analysis
- ✅ Dataset preparation pipeline
- ✅ Cost and memory estimator
- ✅ **DELIVERABLE**: Fine-tuning Toolkit (700+ lines)

**Files**: `docs/curriculum/notes/module_32_finetuning_llms.md`, `examples/module_32/`

---

### Module 33: Diffusion Models & Image Generation
- **Duration**: 7-8 hours
- **Prerequisites**: Module 32
- **Status**: 🟢 Complete

**Files**: `docs/curriculum/notes/module_33_diffusion_models.md`, `examples/module_33/`

**Learning Objectives**:
- Understand diffusion model theory
- Learn Stable Diffusion architecture
- Generate images with AI
- Fine-tune diffusion models

**Deliverables**:
- ✅ Comprehensive theory document (~800 lines)
- ✅ Forward/reverse diffusion visualization
- ✅ Noise schedule comparison (linear, cosine, quadratic)
- ✅ Minimal diffusion model training on 2D data
- ✅ DDPM vs DDIM sampling comparison
- ✅ **DELIVERABLE**: Diffusion Lab (600+ lines)

---

### Module 34: Code Generation Models
- **Duration**: 6-7 hours
- **Prerequisites**: Module 33
- **Status**: 🟢 Complete

**Files**: `docs/curriculum/notes/module_34_code_generation_models.md`, `examples/module_34/`

**Learning Objectives**:
- Understand code-specific LLMs (Codex, CodeLlama, StarCoder, DeepSeek)
- Master Fill-in-the-Middle (FIM) training
- Evaluate with HumanEval, MBPP, SWE-bench
- Build code completion and search systems

**Deliverables**:
- ✅ Comprehensive theory document (~700 lines)
- ✅ FIM transformation demos (PSM, SPM, model formats)
- ✅ Completion strategy comparison (greedy, sampling, beam)
- ✅ Pass@k evaluation implementation
- ✅ Code search and indexing system
- ✅ **DELIVERABLE**: Code Generation Toolkit (900+ lines)

---

### Module 35: RLHF & How LLMs Are Trained 🆕 🔮
- **Duration**: 8-9 hours
- **Prerequisites**: Module 34
- **Status**: 🟢 Complete

**Files**: `docs/curriculum/notes/module_35_rlhf.md`, `examples/module_35/`

**Learning Objectives**:
- Understand Reinforcement Learning from Human Feedback (RLHF)
- Learn how ChatGPT was actually trained
- Master the three stages: Pretraining → SFT → RLHF
- Implement reward modeling with Bradley-Terry loss
- Explore alternatives: DPO, ORPO, KTO

**Deliverables**:
- ✅ Comprehensive theory document (~780 lines)
- ✅ Reward model training with Bradley-Terry loss
- ✅ DPO (Direct Preference Optimization) implementation
- ✅ KTO (Kahneman-Tversky Optimization) for unpaired feedback
- ✅ Full RLHF pipeline simulation
- ✅ **DELIVERABLE**: RLHF Training Toolkit (900+ lines)

**Key Concepts**:
- **Three-Stage Training**:
  1. Pretraining: Next-token prediction on internet text
  2. SFT (Supervised Fine-Tuning): Train on human demonstrations
  3. RLHF: Optimize for human preferences
- **RLHF Components**:
  - Reward Model: Predicts human preferences
  - PPO: Proximal Policy Optimization
  - KL Divergence: Prevent reward hacking
- **Modern Alternatives**:
  - DPO (Direct Preference Optimization): Simpler, no reward model
  - ORPO (Odds Ratio Preference Optimization)
  - KTO (Kahneman-Tversky Optimization)
  - Constitutional AI (Anthropic's approach)

**💡 Heureka Moment**: THIS is how ChatGPT became ChatGPT! RLHF aligns models to human preferences!

**Why This Matters**:
- Understanding RLHF explains why LLMs behave the way they do
- You'll understand why "jailbreaks" work
- You'll know how to fine-tune for specific behaviors

---

### Module 36: Constitutional AI & Alignment
- **Duration**: 6-7 hours
- **Prerequisites**: Module 35
- **Status**: 🟢 Complete
**Files**: `docs/curriculum/notes/module_36_constitutional_ai.md`, `examples/module_36/`

**Learning Objectives**:
- Understand Constitutional AI (Anthropic's approach)
- Learn AI alignment principles
- Implement self-critique mechanisms
- Explore harmlessness training

**Deliverables**:
- ✅ Constitutional AI theory document (587 lines)
- ✅ CAI toolkit with constitution design, critique-revise, RLAIF (900+ lines)
- ✅ Alignment evaluation and scoring system

---

## Phase 8: Classical ML (Weeks 37-39) 🆕

**Goal**: Master traditional ML that still powers 80% of production systems

### Module 37: Tabular ML & Gradient Boosting 🆕
- **Duration**: 6-7 hours
- **Prerequisites**: Phase 7 complete
- **Status**: 🟢 Complete
**Files**: `docs/curriculum/notes/module_37_tabular_ml.md`, `examples/module_37/`

**Learning Objectives**:
- Master XGBoost, LightGBM, CatBoost
- Understand gradient boosting algorithms
- Learn feature engineering for tabular data
- Compare deep learning vs gradient boosting for tabular data
- Implement ensemble methods

**Deliverables**:
- ✅ Theory document on tabular ML (932 lines)
- ✅ Gradient Boosting toolkit from scratch (1256 lines)
- ✅ Decision tree and boosting implementation

**Key Concepts**:
- **Gradient Boosting**:
  - XGBoost: eXtreme Gradient Boosting
  - LightGBM: Light Gradient Boosting Machine
  - CatBoost: Categorical Boosting
- **Feature Engineering**:
  - Categorical encoding (one-hot, target, etc.)
  - Numerical transformations
  - Feature interactions
  - Missing value handling
- **Why Still Relevant**:
  - 80% of Kaggle competitions won by GBMs
  - Faster training than deep learning
  - Better interpretability
  - Works well with small data

**Real-World Application**: Build contrarian's stock prediction models!

---

### Module 38: Time Series & Forecasting 🆕
- **Duration**: 7-8 hours
- **Prerequisites**: Module 37
- **Status**: 🟢 Complete
**Files**: `docs/curriculum/notes/module_38_time_series.md`, `examples/module_38/`

**Learning Objectives**:
- Master time series fundamentals
- Implement classical methods (ARIMA, Prophet)
- Build deep learning time series models
- Learn temporal feature engineering
- Implement anomaly detection

**Deliverables**:
- ✅ Theory document on time series forecasting (1178 lines)
- ✅ Time Series Forecasting Toolkit from scratch (1802 lines)
- ✅ ARIMA, Prophet-style forecasting, anomaly detection

**Key Concepts**:
- **Classical Methods**:
  - ARIMA, SARIMA
  - Prophet (Facebook)
  - Exponential smoothing
- **Deep Learning**:
  - LSTM, GRU
  - Temporal Convolutional Networks
  - Transformers for time series
- **Feature Engineering**:
  - Lag features
  - Rolling statistics
  - Seasonal decomposition
- **Evaluation**:
  - MAE, RMSE, MAPE
  - Backtesting
  - Cross-validation for time series

**Real-World Application**: Build forecasting for contrarian stock analysis!

---

### Module 39: AutoML & Feature Stores
- **Duration**: 5-6 hours
- **Prerequisites**: Module 38
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand AutoML (auto-sklearn, AutoGluon)
- Learn feature store concepts (Feast)
- Implement automated feature engineering
- Build ML pipelines with AutoML

**Deliverables**:
- AutoGluon pipeline
- Feast feature store setup
- Automated feature engineering

---

## Phase 9: AI Safety & Evaluation (Weeks 40-42) 🆕

**Goal**: Build responsible, safe, and well-evaluated AI systems

### Module 40: AI Safety & Alignment 🆕 🔮
- **Duration**: 7-8 hours
- **Prerequisites**: Phase 8 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand the AI alignment problem
- Learn about AI safety risks (misuse, accidents, misalignment)
- Implement safety guardrails
- Master responsible AI development
- Explore interpretability and explainability

**Deliverables**:
- Safety guardrails system
- Content moderation pipeline
- AI ethics checklist
- **DELIVERABLE**: AI Safety Toolkit

**Key Concepts**:
- **AI Safety Risks**:
  - Misuse: Bad actors using AI for harm
  - Accidents: Unintended harmful behaviors
  - Misalignment: AI optimizing for wrong objectives
- **Safety Techniques**:
  - Input/output filtering
  - Constitutional AI principles
  - Guardrails (NeMo Guardrails, Guardrails AI)
  - Content moderation
- **Responsible AI**:
  - Bias detection and mitigation
  - Fairness metrics
  - Transparency and explainability
  - Privacy preservation

**💡 Heureka Moment**: Safety isn't optional - it's what separates responsible AI from reckless AI!

---

### Module 41: Red Teaming & Adversarial AI 🆕
- **Duration**: 6-7 hours
- **Prerequisites**: Module 40
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master red teaming techniques for AI
- Understand prompt injection attacks
- Learn jailbreaking and defenses
- Implement adversarial testing
- Build robust AI systems

**Deliverables**:
- Red teaming playbook
- Prompt injection defense system
- Adversarial test suite
- **DELIVERABLE**: AI Red Team Toolkit

**Key Concepts**:
- **Attack Types**:
  - Prompt injection (direct, indirect)
  - Jailbreaking techniques
  - Data poisoning
  - Model extraction
  - Adversarial examples
- **Defense Strategies**:
  - Input sanitization
  - Output filtering
  - Canary tokens
  - Rate limiting
  - Monitoring and detection
- **Red Teaming Process**:
  - Threat modeling
  - Attack simulation
  - Vulnerability assessment
  - Remediation planning

**Real-World Application**: Secure your AI systems before deploying to production!

---

### Module 42: LLM Evaluation & Benchmarking 🆕
- **Duration**: 6-7 hours
- **Prerequisites**: Module 41
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand LLM evaluation frameworks
- Master standard benchmarks (MMLU, HumanEval, etc.)
- Implement custom evaluation metrics
- Build evaluation pipelines
- Learn human evaluation best practices

**Deliverables**:
- Evaluation pipeline for LLMs
- Custom benchmark suite
- Human evaluation framework
- **DELIVERABLE**: LLM Evaluation Toolkit

**Key Concepts**:
- **Standard Benchmarks**:
  - MMLU: Multitask Language Understanding
  - HumanEval: Code generation
  - TruthfulQA: Factual accuracy
  - HellaSwag: Common sense
  - GSM8K: Math reasoning
- **Evaluation Frameworks**:
  - lm-eval-harness
  - HELM
  - BIG-bench
- **Custom Evaluation**:
  - Task-specific metrics
  - Rubric-based evaluation
  - LLM-as-judge
- **Human Evaluation**:
  - A/B testing
  - Preference ranking
  - Quality rubrics

**Real-World Application**: Evaluate your models before deploying!

---

## Phase 10: DevOps & MLOps (Weeks 43-52)

**Goal**: Master production deployment and operations for AI/ML

### Module 43: DevOps Fundamentals for ML Engineers
- **Duration**: 5-6 hours
- **Prerequisites**: Phase 9 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Git workflows for ML projects
- Understand version control for code + data + models
- Learn testing strategies for ML code
- Implement code review practices

**Deliverables**:
- Git workflow guide for ML projects
- ML testing framework
- Pre-commit hooks for ML code quality

---

### Module 44: Docker & Containerization for ML
- **Duration**: 6-7 hours
- **Prerequisites**: Module 43
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Docker for ML applications
- Build optimized Docker images (multi-stage builds)
- Handle large ML artifacts in containers
- Use Docker Compose for local development

**Deliverables**:
- Dockerized ML application
- Multi-stage Dockerfile for ML
- Docker Compose stack

---

### Module 45: CI/CD for AI/ML Development
- **Duration**: 7-8 hours
- **Prerequisites**: Module 44
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand CI/CD for ML workflows
- Master Dagger (portable CI/CD pipelines)
- Implement GitHub Actions for ML
- Build continuous training pipelines
- Use Dagger AI Agent for autonomous development

**Deliverables**:
- Dagger pipeline for ML project
- GitHub Actions workflow
- Automated model validation pipeline
- Dagger AI Agent integration (LLM-powered autonomous coding)

**Key Concepts**:
- Dagger modules and functions
- Containerized, portable CI/CD pipelines
- **Dagger AI Agent**: Connect to LLM (Claude/GPT) for autonomous feature development
- Agent workflow: GitHub Issue → Analyze codebase → Code changes → Run tests → Open PR
- Workspace tools: read-file, write-file, list-files, test

**Real-World Application**: Set up Dagger Agent for kaizen to auto-implement features from GitHub issues!

**Reference**: [Dagger AI Agent Quickstart](https://docs.dagger.io/getting-started/quickstarts/agent-in-project)

---

### Module 46: Kubernetes Fundamentals for ML
- **Duration**: 7-8 hours
- **Prerequisites**: Module 45
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Kubernetes architecture
- Deploy ML workloads on Kubernetes
- Understand GPU scheduling (NVIDIA GPU Operator)
- Manage resources (CPU, memory, GPU allocation)

**Deliverables**:
- ML inference deployment on K8s
- GPU-enabled training job
- Persistent volume setup

---

### Module 47: Advanced Kubernetes for AI/ML
- **Duration**: 8-9 hours
- **Prerequisites**: Module 46
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Kubeflow for ML workflows
- Implement KServe for model serving
- Deploy Ray on Kubernetes
- Use NVIDIA Triton Inference Server

**Deliverables**:
- Kubeflow Pipelines workflow
- KServe deployment
- Ray cluster on Kubernetes

---

### Module 48: MLOps & Experiment Tracking
- **Duration**: 6-7 hours
- **Prerequisites**: Module 47
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master MLflow for experiment tracking
- Learn Weights & Biases (W&B)
- Implement model versioning and registry

**Deliverables**:
- MLflow setup and integration
- Experiment tracking dashboard
- Model registry implementation

---

### Module 49: Data Versioning & Feature Stores
- **Duration**: 6-7 hours
- **Prerequisites**: Module 48
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master DVC for datasets and models
- Learn feature stores (Feast)
- Implement data validation (Great Expectations)

**Deliverables**:
- DVC setup for dataset versioning
- Feast feature store deployment
- Data validation suite

---

### Module 50: ML Pipeline Orchestration
- **Duration**: 7-8 hours
- **Prerequisites**: Module 49
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Airflow for ML pipelines
- Build Kubeflow Pipelines
- Compare orchestration tools

**Deliverables**:
- Airflow DAG for ML pipeline
- Kubeflow Pipeline for training
- Pipeline comparison matrix

---

### Module 51: Model Deployment & Serving Patterns
- **Duration**: 7-8 hours
- **Prerequisites**: Module 50
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Deploy models as REST APIs (FastAPI)
- Implement gRPC for high-performance serving
- Master deployment patterns (canary, blue-green, A/B)
- Optimize models for serving (ONNX, TensorRT)

**Deliverables**:
- FastAPI model server
- Canary deployment on Kubernetes
- A/B testing framework for models

---

### Module 52: Monitoring, Governance & Production Best Practices
- **Duration**: 7-8 hours
- **Prerequisites**: Module 51
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Monitor model performance in production
- Detect data drift and concept drift
- Implement model explainability (SHAP, LIME)
- Build model governance frameworks

**Deliverables**:
- Model monitoring dashboard
- Data drift detection system
- Model explainability reports

---

## Phase 11: AI for Infrastructure (Weeks 53-54)

**Goal**: Apply AI to infrastructure management and AIOps

### Module 53: AI for Proactive Cloud Management
- **Duration**: 7-8 hours
- **Prerequisites**: Phase 10 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Build anomaly detection systems
- Implement predictive scaling
- Use AI for capacity planning

**Deliverables**:
- Anomaly detection system
- Predictive scaling model
- Capacity planning tool

---

### Module 54: AIOps & Log Analysis
- **Duration**: 6-7 hours
- **Prerequisites**: Module 53
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Use LLMs for log analysis
- Build root cause analysis systems
- Implement intelligent incident response

**Deliverables**:
- Log analysis system with LLMs
- Root cause analysis tool
- Incident response automation

---

## Phase 12: Capstone Projects (Weeks 55-60)

**Goal**: Apply everything to real-world projects

### Module 55: Kaizen Enhancement - Advanced AI Features
- **Duration**: 8-10 hours
- **Prerequisites**: Phases 1-11 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Implement hybrid search and GraphRAG
- Build multi-agent workflows
- Add autonomous debugging capabilities

**Deliverables**:
- Enhanced kaizen RAG with 90%+ accuracy
- Multi-agent system for issue resolution
- Code review bot

---

### Module 56: Vibe AI Features - Generative Content Platform
- **Duration**: 8-10 hours
- **Prerequisites**: Phases 1-11 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Implement generative AI for content creation
- Add multimodal capabilities (text + audio + video)
- Build RAG for course knowledge management

**Deliverables**:
- AI content generation API
- Multimodal lesson builder
- RAG-powered Q&A system

---

### Module 57: Contrarian AI Analytics - Stock Intelligence System
- **Duration**: 8-10 hours
- **Prerequisites**: Phases 1-11 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Build LLM-powered sentiment analysis
- Implement time series forecasting
- Create anomaly detection for market data

**Deliverables**:
- Sentiment analysis pipeline
- Time series forecasting model
- AI-generated investment reports

---

## Phase 13: History of AI (Optional Enrichment) 🕰️

**Goal**: Understand how we got here

### Module 58: The Foundations (1950s-1980s)
- **Duration**: 3-4 hours
- **Status**: ⚪ Not Started

The birth of AI, perceptrons, AI winters, expert systems, and backpropagation.

---

### Module 59: The Deep Learning Revolution (2000s-2010s)
- **Duration**: 3-4 hours
- **Status**: ⚪ Not Started

ImageNet, AlexNet, Word2Vec, GPU revolution, and the bitter lesson.

---

### Module 60: The Transformer Era (2017-Present)
- **Duration**: 4-5 hours
- **Status**: ⚪ Not Started

"Attention Is All You Need", BERT, GPT series, ChatGPT moment, and the future.

---

## 📊 Summary: New vs Old Curriculum

| Metric | Old (v3.0) | New (v4.0) | Change |
|--------|------------|------------|--------|
| Core Modules | 45 | 57 | +12 |
| Optional Modules | 3 | 3 | - |
| Total Phases | 9 | 13 | +4 |
| New Topics Added | - | 8 major areas | - |
| Estimated Duration | 44-52 weeks | 50-60 weeks | +6-8 weeks |
| Heureka Moments | 8 | 8 | - |

### New Modules Added (8 total):
1. **Module 14**: Advanced RAG Patterns (GraphRAG, HyDE, Self-RAG)
2. **Module 20**: Advanced Agentic AI (Memory, Planning, Multi-Agent)
3. **Module 22**: Speech AI (Whisper, TTS, Voice)
4. **Module 24**: Video AI & Generation
5. **Module 35**: RLHF & How LLMs Are Trained
6. **Module 37**: Tabular ML & Gradient Boosting
7. **Module 38**: Time Series & Forecasting
8. **Module 40**: AI Safety & Alignment
9. **Module 41**: Red Teaming & Adversarial AI
10. **Module 42**: LLM Evaluation & Benchmarking

### New Phases Added (4 total):
1. **Phase 5**: Multimodal AI (Audio, Vision, Video)
2. **Phase 8**: Classical ML (Tabular, Time Series)
3. **Phase 9**: AI Safety & Evaluation
4. Expanded **Phase 4** with Advanced Agentic AI

---

## 🎓 The AI Guru Checklist

After completing Neural Dojo v4.0, you will be able to:

### Foundation ✅
- [x] Use AI for development (prompt engineering, AI coding)
- [x] Understand LLMs (transformers, tokenization, sampling)
- [x] Build semantic search and embeddings

### Building ✅
- [ ] Build production RAG systems (basic + advanced patterns)
- [ ] Create sophisticated agents (memory, planning, multi-agent)
- [ ] Use LangChain, LangGraph, LlamaIndex

### Multimodal ✅
- [ ] Build speech-to-text and text-to-speech systems
- [ ] Create vision AI applications
- [ ] Work with video understanding and generation

### Deep Learning ✅
- [ ] Train neural networks from scratch
- [ ] Build and train transformers
- [ ] Fine-tune LLMs with LoRA/QLoRA
- [ ] Understand RLHF (how ChatGPT was trained!)

### Classical ML ✅
- [ ] Master gradient boosting (XGBoost, LightGBM)
- [ ] Build time series forecasting models
- [ ] Implement AutoML pipelines

### Safety & Evaluation ✅
- [ ] Implement AI safety guardrails
- [ ] Red team AI systems
- [ ] Evaluate and benchmark LLMs

### Production ✅
- [ ] Deploy ML on Kubernetes with GPUs
- [ ] Implement MLOps best practices
- [ ] Monitor models in production

### Applied ✅
- [ ] Build AIOps systems
- [ ] Complete real-world capstone projects

---

## 🚀 You're Building Towards AI Guru Status!

**Current Progress**: 25/56 modules (45%)

**What You've Mastered**:
- ✅ AI-Native Development (Phase 1)
- ✅ Generative AI Fundamentals (Phase 2)
- ✅ Vector Search & RAG (Phase 3)
- ✅ Frameworks & Agents (Phase 4)
- ✅ **Multimodal AI (Phase 5)** - COMPLETE! 🎉
  - Speech AI (Module 22) - Whisper, TTS, Voice Assistant
  - Vision AI (Module 23) - CLIP, VLMs, Visual QA
  - Video AI (Module 24) - Frame extraction, scene detection, summarization

**What's Next**:
- Begin Phase 6: Deep Learning Foundations
- Next: Module 25 - Python for Machine Learning (NumPy, pandas)

---

_Last updated: 2025-11-26_
_Version: 4.1.0 - COMPLETE AI GURU CURRICULUM_
_56 core modules + 3 optional history modules_
_Estimated duration: 50-60 weeks (220-300 hours)_

**🥋🧠⚡ Let's build an AI Guru!**
