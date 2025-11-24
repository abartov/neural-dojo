# Neural Dojo: Master Curriculum

**From Zero to Hero: Master AI, ML, LLMs, and AI-Driven Development**

**Last Updated**: 2025-11-24
**Version**: 3.0.0 - EXPANDED DevOps/MLOps (Phase 6: 10 modules!)
**Status**: Module 0 + Phase 1 + Phase 2 Complete! 🎉 Ready for Phase 3
**Total Duration**: 47 modules (including Module 0 + 1.1, 1.2 + 3 optional history modules), 44-52 weeks (178-262 hours)

---

## 🎯 Mission

Transform you from AI novice to AI-fluent developer capable of:
- Building production RAG systems
- Creating AI agents and multi-agent orchestrations
- Using AI to accelerate development (AI-driven coding)
- Training and deploying deep learning models
- Mastering prompt engineering and LLM integration
- Building generative AI applications
- **Deploying AI/ML with modern DevOps & MLOps practices**
- **Orchestrating ML workloads on Kubernetes (with GPU support)**
- Applying AI to real-world problems (cloud management, stock analysis, infrastructure)

---

## 🧭 Curriculum Philosophy

Following the **jamesblonde pattern**:
- **Theory-first**: Deep understanding before coding
- **Hands-on**: Every concept has working code examples
- **Production-ready**: Build real systems, not toys
- **Progressive**: Each module builds on previous knowledge
- **Practical**: Focus on tools and techniques you'll actually use

### 💡 Heureka Moments

Throughout this curriculum, you'll encounter transformative insights marked with 🔮. These are concepts that fundamentally change how you think about AI:
1. **Prompt Engineering** (Module 2) - Already discovered! ✅
2. **Embeddings as Semantic Space** (Module 10) - 🔮
3. **RAG vs Fine-tuning Trade-offs** (Module 13) - 🔮
4. **Chain-of-Thought Reasoning** (Module 16) - 🔮
5. **Temperature & Sampling Strategies** (Module 17) - 🔮
6. **Agent Architectures** (Module 19) - 🔮
7. **Context Window Economics** (Module 22) - 🔮
8. **Backpropagation Intuition** (Module 25) - 🔮

---

## 📊 Progress Tracking

| Phase | Modules | Status | Completion |
|-------|---------|--------|------------|
| Module 0: Prerequisites | 0 | 🟢 Complete | 1/1 (100%) |
| Phase 1: AI-Native Development | 1.1, 1.2, 2-5 | 🟢 Complete | 6/6 (100%) |
| Phase 2: Generative AI Fundamentals | 6-10 | 🟢 Complete | 5/5 (100%) |
| Phase 3: Building with AI Toolkits | 11-18 | ⚪ Not Started | 0/8 |
| Phase 4: Deep Learning Foundations | 19-25 | ⚪ Not Started | 0/7 |
| Phase 5: Advanced Generative AI | 26-29 | ⚪ Not Started | 0/4 |
| **Phase 6: DevOps & MLOps** | **30-39** | ⚪ **Not Started** | **0/10** |
| Phase 7: AI for Infrastructure | 40-41 | ⚪ Not Started | 0/2 |
| Phase 8: Capstone Projects | 42-44 | ⚪ Not Started | 0/3 |
| Phase 9: History of AI/ML (Optional) | 45-47 | ⚪ Not Started | 0/3 |
| **TOTAL** | **47 modules** | **26% Complete** | **12/47** |

**Legend**: ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

---

## 📚 Curriculum Structure

---

## Module 0: Prerequisites & Environment Setup (Pre-Phase 1)

**Goal**: Prepare your development environment before starting Module 1

### Module 0: Prerequisites & Environment Setup
- **Duration**: 2-3 hours
- **Prerequisites**: None - this is where you start!
- **Status**: 🟢 Complete

**Learning Objectives**:
- Verify you have the required prerequisites (Python 3.10+, command line basics)
- Set up your development environment (venv, pip, IDE/editor)
- Configure API keys for Claude and/or OpenAI
- Make your first LLM API call
- Verify everything works before diving into Module 1

**Deliverables**:
- ✅ Python 3.10+ environment verified
- ✅ Virtual environment created and activated
- ✅ `.env` file with API key(s) configured
- ✅ All test scripts passing (test_environment.py, test_claude_api.py)
- ✅ Development tools ready (text editor/IDE)

**Key Concepts**:
- Virtual environments for Python
- Environment variables and API keys
- Testing API connections
- Basic Python package management

**Files Created**:
- Theory: `docs/curriculum/notes/module_00_prerequisites.md` (~600 lines, comprehensive setup guide)
- Examples: `examples/module_00/`
  - `test_environment.py` (Python version, venv, dependencies check)
  - `test_claude_api.py` (Claude API connection test)
  - `test_openai_api.py` (OpenAI API connection test - optional)
  - `README.md` (Module overview and instructions)
  - `requirements.txt` (anthropic, openai, python-dotenv, dev tools)

---

## Phase 1: AI-Native Development (Weeks 1-5)

**Goal**: Master using AI as your development partner

### Module 1.1: AI Coding Tools Landscape
- **Duration**: 4-5 hours
- **Prerequisites**: None (start here!)
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand the AI development landscape (2024-2025)
- Set up AI coding assistants (Claude Code, Cursor, GitHub Copilot, Aider, Continue.dev)
- Learn the mental model of AI pair programming
- Understand when to use AI vs traditional coding
- Master subscriptions vs API access distinction

**Deliverables**:
- ✅ Configured development environment with Claude Code
- ✅ 5 AI coding pattern demonstrations (200+ lines each)
- ✅ Python File Analyzer CLI tool (250+ lines, full test coverage)
- ✅ AI tools comparison template (13 tools evaluated)
- ✅ Reflection document template
- ✅ Subscriptions vs API Access comprehensive guide

**Key Concepts**:
- AI as a tool, not a replacement
- The human-in-the-loop principle
- AI strengths and limitations
- 5 AI coding patterns (Specification, Iteration, Example, Explanation, Debugging)
- Subscription access (web only) vs API access (programmatic)
- Cost optimization strategies

**Files Created**:
- Theory: `docs/curriculum/notes/module_01.1_ai_coding_tools.md` (~2,500 lines, 2025-verified pricing)
- Examples: `examples/module_01/patterns/` (5 pattern demonstrations)
- Project: `examples/module_01/project/pyanalyzer.py` (CLI tool with tests)
- Deliverables: `docs/deliverables/module_01_*.md` (2 templates)

---

### Module 1.2: Local Models for AI Coding
- **Duration**: 3-4 hours
- **Prerequisites**: Module 1.1
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand local AI model landscape (DeepSeek, Qwen, Llama, Mistral, Gemma, Phi)
- Install and run Ollama (local model management)
- Use local models with Aider (terminal AI coding)
- Configure Continue.dev with local models (VS Code extension)
- Implement hybrid approach (80% local, 20% API)
- Optimize costs ($0-5/month vs $50-150/month)

**Deliverables**:
- ✅ Ollama installation and setup (macOS/Linux/Windows)
- ✅ Local model testing suite
- ✅ Aider + local models configuration
- ✅ Continue.dev + local models setup
- ✅ Cost comparison analysis ($600-1,800/year savings potential)
- ✅ Hybrid workflow implementation

**Key Concepts**:
- Local vs API models (cost, privacy, performance)
- Model quantization (Q4, Q8)
- Ollama model management
- Aider terminal workflows
- Continue.dev VS Code integration
- Hybrid cost optimization (local daily work, API for complex tasks)
- Model sizing and hardware requirements

**Files Created**:
- Theory: `docs/curriculum/notes/module_01.2_local_models.md` (~1,100 lines, comprehensive guide)
- Examples: `examples/module_01.2/`
  - `setup_ollama.sh` (automated installation script)
  - `test_local_models.py` (model testing and verification)
  - `aider_with_local.md` (Aider setup guide)
  - `continue_config.json` (Continue.dev configuration)
  - `cost_comparison.md` (detailed cost analysis)
  - `requirements.txt` (dependencies)
  - `README.md` (module overview)

---

### Module 2: Prompt Engineering Fundamentals 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Module 1
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master the art of prompt engineering
- Understand prompt structure (system, user, assistant)
- Learn few-shot learning techniques
- Discover chain-of-thought prompting
- Handle edge cases and failure modes

**Deliverables**:
- ✅ Prompt engineering toolkit (templates, patterns)
- ✅ 8 working code examples demonstrating techniques
- ✅ 3 comprehensive deliverable templates
- ✅ Personal prompt library template

**Key Concepts**:
- Zero-shot vs few-shot vs many-shot
- System prompts for behavior control
- Prompt injection and security
- Iterative prompt refinement

**💡 Heureka Moment**: You already discovered this! Prompts are the new programming interface.

**Files Created**:
- Theory: `docs/curriculum/notes/module_02_prompt_engineering.md` (9,000+ words)
- Examples: `examples/module_02/` (8 complete demonstrations)
  - `01_zero_vs_few_shot.py` - Zero-shot vs few-shot comparison
  - `02_chain_of_thought.py` - Chain-of-thought prompting
  - `03_role_prompting.py` - Role-based prompt variations
  - `04_structured_outputs.py` - JSON, CSV, table formats
  - `05_iterative_refinement.py` - Progressive prompt improvement
  - `06_prompt_library.py` - Reusable prompt templates
  - `07_code_tasks.py` - Code-specific prompts
  - `08_prompt_injection.py` - Security vulnerabilities and defenses
- Deliverables: `docs/deliverables/module_02_*.md` (3 templates)
- Requirements: `examples/module_02/requirements.txt`

---

### Module 3: AI-Powered Code Generation
- **Duration**: 4-5 hours
- **Prerequisites**: Modules 1-2
- **Status**: 🟢 Complete

**Learning Objectives**:
- Generate code from natural language
- Refactor existing code with AI
- Debug with AI assistance
- Write tests using AI

**Deliverables**:
- ✅ AI-generated Python package template
- ✅ Code generation examples with clear specifications
- ✅ Complete deliverable template for building Python packages with AI

**Key Concepts**:
- Specification-driven code generation
- Iterative refinement for code quality
- Test-driven generation
- Security considerations (SQL injection, XSS, input validation)
- Context window management
- When NOT to use AI generation

**Files Created**:
- Theory: `docs/curriculum/notes/module_03_code_generation.md` (~7,000 words)
- Example: `examples/module_03/01_basic_generation.py` (code generation from specifications)
- Deliverable: `docs/deliverables/module_03_generated_package.md` (Python package template)
- `examples/module_03/README.md` and `requirements.txt`

---

### Module 4: AI-Assisted Debugging & Optimization
- **Duration**: 4-5 hours
- **Prerequisites**: Modules 1-3
- **Status**: 🟢 Complete

**Learning Objectives**:
- Use AI to find and fix bugs
- Optimize code performance with AI
- Understand AI's debugging strategies
- Learn when AI fails at debugging

**Deliverables**:
- ✅ AI debugging workflow (gather context → investigate → verify → prevent)
- ✅ Bug categories by AI effectiveness ratings
- ✅ Performance optimization strategies
- ✅ Complete debugging log template

**Key Concepts**:
- AI debugging workflow (4 steps)
- Bug categories by AI effectiveness (syntax ⭐⭐⭐⭐⭐, async ⭐⭐)
- Performance optimization with AI (algorithmic, code-level, database)
- Debugging patterns (binary search, differential, regression)
- Combining AI with profiling tools
- When AI doesn't help (system-level, memory profiling, I/O bottlenecks)

**Files Created**:
- Theory: `docs/curriculum/notes/module_04_debugging.md` (~5,000 words)
- Deliverable: `docs/deliverables/module_04_debugging_log.md` (template to document 5+ debugging sessions)

---

### Module 5: Building with AI Coding Assistants
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 1-4
- **Status**: 🟢 Complete

**Learning Objectives**:
- Master Claude Code workflows
- Understand GitHub Copilot patterns
- Learn Cursor IDE advanced features
- Build a complete project with AI assistance
- Develop your personal AI-assisted development workflow

**Deliverables**:
- ✅ AI coding assistant landscape overview
- ✅ Tool-specific workflows (Claude Code, Copilot, Cursor)
- ✅ Decision matrix for choosing tools
- ✅ Personal AI workflow template
- ✅ **Phase 1 Complete!**

**Key Concepts**:
- Claude Code: long context, sophisticated reasoning, file operations
- GitHub Copilot: fast autocomplete, inline suggestions, boilerplate
- Cursor IDE: full IDE with AI, codebase understanding, Cmd+K edits
- Tool selection decision matrix (task type → best tool)
- Combined workflows using multiple tools
- Productivity patterns (rubber ducking, progressive refinement, style learning)
- When NOT to use AI (autopilot mode, context overload, not testing)
- Real-world project workflow (setup → features → testing → optimization → docs)

**Files Created**:
- Theory: `docs/curriculum/notes/module_05_ai_tools.md` (~6,000 words)
- Deliverable: `docs/deliverables/module_05_ai_workflow.md` (personal workflow design template)

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
- Understand model sizes and capabilities
- Compare open-source vs proprietary models
- Make your first direct API integration
- Choose the right model for your use case

**Deliverables**:
- ✅ LLM landscape analysis template
- ✅ Model comparison and API integration examples
- ✅ Cost and privacy analysis

**Key Concepts**:
- Transformer architecture (attention mechanism, encoder/decoder)
- LLM landscape (GPT-4, Claude 3.5, Gemini, Llama 3, Mistral)
- Pre-training vs fine-tuning vs RAG
- Context windows (4K to 200K to 1M tokens)
- Model families and their strengths
- API integration with Claude/OpenAI
- Cost considerations and optimization
- Privacy and security trade-offs

**Files Created**:
- Theory: `docs/curriculum/notes/module_06_intro_to_llms.md` (~8,000 words)
- Example: `examples/module_06/01_model_comparison.py` (API integration demo)
- Deliverable: `docs/deliverables/module_06_llm_analysis.md` (comprehensive analysis template)
- `examples/module_06/README.md` and `requirements.txt`

---

### Module 7: Tokenization & Text Processing
- **Duration**: 4-5 hours
- **Prerequisites**: Module 6
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand how text becomes tokens
- Learn about different tokenizers (BPE, WordPiece, SentencePiece)
- Master token counting and optimization
- Understand why token limits matter for costs and performance
- Handle multilingual text tokenization
- Optimize prompts for token efficiency

**Deliverables**:
- ✅ Token counter tool with tiktoken (visualizes tokenization)
- ✅ Token optimization examples (6 strategies with cost analysis)
- ✅ Multilingual tokenization comparison (15+ languages)
- ✅ Token analysis and optimization report template

**Key Concepts**:
- Tokens ≠ words: Subword tokenization
- BPE, WordPiece, SentencePiece algorithms
- Token counting for cost optimization
- Code uses 3-4x more tokens than prose
- Multilingual tokenization challenges (non-English = 1.5-3x tokens)
- Token optimization strategies (6 strategies: verbosity, system prompts, formatting, abbreviations, batching, examples)
- RAG and conversation token management
- Emoji tokenization (1-10 tokens depending on complexity)

**Files Created**:
- Theory: `docs/curriculum/notes/module_07_tokenization.md` (~6,000 words)
- Example 1: `examples/module_07/01_token_counter.py` (token counting, visualization, API cost estimation)
- Example 2: `examples/module_07/02_optimization.py` (6 optimization strategies with cost savings)
- Example 3: `examples/module_07/03_multilingual.py` (multilingual tokenization analysis)
- Deliverable: `docs/deliverables/module_07_token_analysis.md` (comprehensive analysis template)
- Supporting: `examples/module_07/README.md` and `requirements.txt`

---

### Module 8: Text Generation & Sampling Strategies
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 6-7
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand how LLMs generate text (autoregressive generation)
- Master temperature, top-p, top-k sampling
- Learn about repetition penalties and length control
- Control generation quality and creativity
- Choose optimal sampling strategies for different use cases

**Deliverables**:
- ✅ Text generation playground (7 real-world demos with Claude API)
- ✅ Temperature explorer (statistical analysis of variation)
- ✅ Sampling strategy analysis template (comprehensive optimization guide)

**Key Concepts**:
- Autoregressive generation (one token at a time)
- Temperature scaling (0.0 = deterministic, 1.0+ = creative)
- Nucleus sampling / top-p (filters unlikely tokens)
- Top-k sampling (fixed number of top tokens)
- Repetition penalty (prevent loops)
- Quality vs creativity trade-off
- Use case-specific configurations

**Files Created**:
- Theory: `docs/curriculum/notes/module_08_text_generation.md` (~10,000 words)
- Example 1: `examples/module_08/01_sampling_playground.py` (comprehensive demos)
- Example 2: `examples/module_08/02_temperature_explorer.py` (statistical analysis)
- Deliverable: `docs/deliverables/module_08_sampling_analysis.md` (optimization template)
- Supporting: `examples/module_08/README.md` and `requirements.txt`

**💡 Heureka Moment**: Temperature isn't just "creativity" - it's probability distribution control! Low temp = sharp distribution (focus on likely tokens), high temp = flat distribution (consider more options).

---

### Module 9: Embeddings & Semantic Similarity
- **Duration**: 2-3 hours
- **Prerequisites**: Module 6 (LLMs), Module 8 (Text Generation)
- **Status**: 🟢 Complete

**Deliverables**:
- ✅ Embedding generation examples (OpenAI, Sentence Transformers)
- ✅ Semantic similarity calculator
- ✅ Practical applications (search, clustering, recommendations, classification)

**Key Concepts**:
- Embeddings as dense vectors representing meaning
- Cosine similarity vs Euclidean distance
- Dense vs sparse embeddings (neural vs TF-IDF)
- Embedding model comparison (OpenAI, Sentence-BERT)
- Applications: semantic search, clustering, recommendations, zero-shot classification, duplicate detection

**Files Created**:
- Theory: `docs/curriculum/notes/module_09_embeddings.md` (~8,000 words)
- Example 1: `examples/module_09/01_embedding_basics.py` (embedding generation, similarity)
- Example 2: `examples/module_09/02_semantic_applications.py` (5 practical applications)
- Deliverable: `docs/deliverables/module_09_embeddings_analysis.md` (implementation guide)
- Supporting: `examples/module_09/README.md` and `requirements.txt`

---

### Module 10: Vector Spaces & Semantic Search 🔮
- **Duration**: 2-3 hours
- **Prerequisites**: Module 9 (Embeddings)
- **Status**: 🟢 Complete

**Deliverables**:
- ✅ Vector arithmetic demonstrations (king - man + woman ≈ queen)
- ✅ 2D/3D visualizations of semantic space
- ✅ Production semantic search with FAISS (100-1000x speedup)
- ✅ Hybrid search (semantic + metadata)

**Key Concepts**:
- 🔮 **Heureka Moment**: Math works on meaning! Vector arithmetic transforms concepts
- Semantic space as geometry (distance = similarity, direction = relationships)
- Vector arithmetic: `king - man + woman ≈ queen`, `Paris - France + Italy ≈ Rome`
- ANN algorithms: HNSW, IVF, LSH (O(log N) vs O(N))
- Production optimization: batching, quantization, dimensionality reduction
- Vector databases: FAISS, Qdrant, Pinecone, Weaviate

**Files Created**:
- Theory: `docs/curriculum/notes/module_10_vector_spaces.md` (~10,000 words, 🔮 Heureka!)
- Example 1: `examples/module_10/01_vector_arithmetic.py` (vector math + visualizations)
- Example 2: `examples/module_10/02_production_search.py` (FAISS, performance benchmarking)
- Deliverable: `docs/deliverables/module_10_production_search.md` (build production search)
- Supporting: `examples/module_10/README.md` and `requirements.txt`
- Visualizations: `semantic_space_2d.png`, `topic_clusters.png`

**💡 Heureka Moment Achieved**: Embeddings create semantic space where mathematical operations correspond to meaning transformations!

---

## Phase 3: Building with AI Toolkits (Weeks 11-18)

**Goal**: Master the tools for building production AI systems

### Module 11: Introduction to Vector Databases
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 9-10
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand vector database architectures
- Compare Qdrant, Pinecone, Weaviate, Chroma
- Learn about indexing strategies
- Master metadata filtering

**Deliverables**:
- Qdrant installation and setup
- Vector database performance benchmark
- Multi-tenant vector store implementation

**Key Concepts**:
- Vector databases vs traditional databases
- HNSW indexing
- Sharding and replication
- Query optimization

---

### Module 12: Building Your First RAG System
- **Duration**: 6-7 hours
- **Prerequisites**: Modules 10-11
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand RAG architecture (Retrieval-Augmented Generation)
- Build a simple RAG pipeline
- Implement document chunking strategies
- Measure RAG performance

**Deliverables**:
- Working RAG system (like kaizen's RAG)
- Document processing pipeline
- RAG evaluation metrics

**Key Concepts**:
- Retrieval vs generation
- Chunking strategies
- Context window management
- Retrieval scoring

---

### Module 13: RAG vs Fine-tuning Trade-offs 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Module 12
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand when to use RAG vs fine-tuning
- Learn about parameter-efficient fine-tuning (PEFT)
- Compare costs and benefits
- Design hybrid approaches

**Deliverables**:
- RAG vs fine-tuning decision matrix
- Cost analysis spreadsheet
- Hybrid approach prototype

**Key Concepts**:
- Knowledge injection methods
- LoRA and QLoRA
- Cost-benefit analysis
- Maintenance overhead

**💡 Heureka Moment**: RAG and fine-tuning solve different problems! RAG = dynamic knowledge, Fine-tuning = behavior/style.

---

### Module 14: LangChain Fundamentals
- **Duration**: 6-7 hours
- **Prerequisites**: Modules 11-13
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master LangChain core concepts
- Build chains and sequences
- Use LangChain memory
- Integrate multiple LLMs

**Deliverables**:
- LangChain-powered chatbot
- Multi-step reasoning chain
- Memory-enabled conversation system

**Key Concepts**:
- Chains, prompts, models, memory
- Sequential chains
- LangChain Expression Language (LCEL)
- Model abstraction

---

### Module 15: LangChain Tools & Function Calling
- **Duration**: 6-7 hours
- **Prerequisites**: Module 14
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand function calling / tool use
- Build custom LangChain tools
- Create tool-calling agents
- Handle tool execution errors

**Deliverables**:
- Custom tool library
- Function-calling agent
- Tool orchestration system

**Key Concepts**:
- Function/tool schemas
- Tool calling protocols
- Error handling
- Tool selection strategies

---

### Module 16: Chain-of-Thought & Reasoning 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 14-15
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master chain-of-thought (CoT) prompting
- Implement ReAct pattern
- Build multi-step reasoning systems
- Understand reasoning limitations

**Deliverables**:
- CoT reasoning system
- ReAct agent implementation
- Reasoning quality benchmark

**Key Concepts**:
- Zero-shot CoT
- Few-shot CoT
- ReAct (Reason + Act)
- Self-consistency

**💡 Heureka Moment**: Making AI "think out loud" dramatically improves reasoning! CoT is like showing your work in math class.

---

### Module 17: Advanced LangChain: LangGraph 🔮
- **Duration**: 7-8 hours
- **Prerequisites**: Modules 14-16
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master LangGraph for stateful workflows
- Build complex multi-agent systems
- Implement cyclic workflows
- Use StateGraph effectively (like kaizen does!)

**Deliverables**:
- LangGraph-based workflow system
- Multi-agent orchestrator
- State persistence implementation

**Key Concepts**:
- StateGraph
- Cyclic workflows
- State management
- Agent coordination

**💡 Heureka Moment**: Temperature controls probability distribution - low temp = focused (argmax), high temp = creative (sampling)!

---

### Module 18: LlamaIndex & Alternative Frameworks
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 14-17
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Learn LlamaIndex for data indexing
- Compare LangChain vs LlamaIndex
- Explore AutoGen, CrewAI, others
- Choose the right framework for your needs

**Deliverables**:
- LlamaIndex data pipeline
- Framework comparison matrix
- Multi-framework integration example

**Key Concepts**:
- Data connectors
- Index types (vector, keyword, knowledge graph)
- Query engines
- Framework trade-offs

---

## Phase 4: Deep Learning Foundations (Weeks 19-25)

**Goal**: Master PyTorch and deep learning fundamentals

### Module 19: Python for Machine Learning
- **Duration**: 5-6 hours
- **Prerequisites**: Phase 3 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master NumPy for numerical computing
- Learn pandas for data manipulation
- Understand matplotlib/seaborn for visualization
- Set up ML development environment

**Deliverables**:
- NumPy performance benchmarks
- Data analysis pipeline
- Visualization toolkit

**Key Concepts**:
- NumPy array operations
- pandas DataFrames
- Vectorization
- Data visualization

---

### Module 20: Neural Networks from Scratch
- **Duration**: 7-8 hours
- **Prerequisites**: Module 19
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Build a neural network without frameworks
- Understand forward propagation
- Implement backpropagation by hand
- Train on MNIST dataset

**Deliverables**:
- Pure Python neural network
- Trained MNIST classifier
- Visualization of learning process

**Key Concepts**:
- Neurons and layers
- Activation functions
- Loss functions
- Gradient descent

---

### Module 21: PyTorch Fundamentals
- **Duration**: 6-7 hours
- **Prerequisites**: Module 20
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master PyTorch tensors
- Understand autograd
- Build models with nn.Module
- Train with PyTorch optimizers

**Deliverables**:
- PyTorch neural network
- Custom Dataset and DataLoader
- Training loop implementation

**Key Concepts**:
- Tensors vs NumPy arrays
- Computational graphs
- Automatic differentiation
- PyTorch training workflow

---

### Module 22: Training Deep Networks
- **Duration**: 7-8 hours
- **Prerequisites**: Module 21
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master training techniques
- Understand optimization algorithms (SGD, Adam, AdamW)
- Implement learning rate scheduling
- Handle overfitting (dropout, regularization)

**Deliverables**:
- Advanced training pipeline
- Hyperparameter tuning framework
- Training visualization dashboard

**Key Concepts**:
- Batch vs mini-batch vs stochastic GD
- Momentum and adaptive learning rates
- Learning rate schedules
- Regularization techniques

---

### Module 23: Convolutional Neural Networks (CNNs)
- **Duration**: 6-7 hours
- **Prerequisites**: Module 22
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand convolutional layers
- Learn CNN architectures (ResNet, EfficientNet)
- Build image classifiers
- Apply transfer learning

**Deliverables**:
- Custom CNN architecture
- Transfer learning implementation
- Image classification system

**Key Concepts**:
- Convolution operations
- Pooling layers
- Batch normalization
- Transfer learning

---

### Module 24: Transformers & Attention Mechanisms
- **Duration**: 8-9 hours
- **Prerequisites**: Module 23
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master the transformer architecture
- Understand self-attention
- Implement multi-head attention
- Build a transformer from scratch

**Deliverables**:
- Transformer implementation
- Attention visualization
- Trained small language model

**Key Concepts**:
- Self-attention mechanism
- Multi-head attention
- Positional encoding
- Encoder-decoder architecture

---

### Module 25: Backpropagation Deep Dive 🔮
- **Duration**: 6-7 hours
- **Prerequisites**: Modules 20-24
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Truly understand backpropagation
- Master the chain rule
- Implement custom autograd
- Debug gradient issues

**Deliverables**:
- Custom autograd engine
- Gradient checking utilities
- Backprop visualization

**Key Concepts**:
- Computational graphs
- Chain rule application
- Gradient flow
- Vanishing/exploding gradients

**💡 Heureka Moment**: Backprop is just the chain rule applied to computational graphs - elegant and simple!

---

## Phase 5: Advanced Generative AI (Weeks 26-29)

**Goal**: Master modern generative AI techniques

### Module 26: Fine-tuning Large Language Models
- **Duration**: 7-8 hours
- **Prerequisites**: Phase 4 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand fine-tuning techniques
- Master LoRA and QLoRA
- Fine-tune open-source models (Llama, Mistral)
- Deploy fine-tuned models

**Deliverables**:
- Fine-tuned Llama model
- LoRA implementation
- Fine-tuning cost analysis

**Key Concepts**:
- Full fine-tuning vs PEFT
- LoRA (Low-Rank Adaptation)
- QLoRA (Quantized LoRA)
- Instruction tuning

---

### Module 27: Multimodal AI & Vision-Language Models
- **Duration**: 7-8 hours
- **Prerequisites**: Module 26
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand multimodal architectures
- Learn about CLIP, LLaVA, GPT-4V
- Build image-text applications
- Implement vision-language reasoning

**Deliverables**:
- CLIP-based image search (like kaizen!)
- Multimodal chatbot
- Vision-language reasoning system

**Key Concepts**:
- CLIP architecture
- Vision encoders + language decoders
- Cross-modal alignment
- Multimodal prompting

---

### Module 28: Diffusion Models & Image Generation
- **Duration**: 7-8 hours
- **Prerequisites**: Module 27
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand diffusion model theory
- Learn Stable Diffusion architecture
- Generate images with AI
- Fine-tune diffusion models

**Deliverables**:
- Image generation pipeline
- Custom LoRA for Stable Diffusion
- Text-to-image application

**Key Concepts**:
- Denoising diffusion probabilistic models (DDPM)
- U-Net architecture
- Latent diffusion
- ControlNet

---

### Module 29: Code Generation Models
- **Duration**: 6-7 hours
- **Prerequisites**: Module 28
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand code-specific LLMs (Codex, StarCoder, CodeLlama)
- Build code generation systems
- Implement code completion
- Create AI coding tools

**Deliverables**:
- Custom code generation tool
- Code completion system
- AI-powered code review bot

**Key Concepts**:
- Code-trained models
- Fill-in-the-middle (FIM)
- Code understanding vs generation
- Execution feedback loops

---

## Phase 6: DevOps & MLOps - Production AI Systems (Weeks 30-39)

**Goal**: Master modern DevOps and MLOps practices for deploying, scaling, and operating AI/ML systems in production

**Why This Phase Matters**:
- AI/ML systems require specialized infrastructure (GPUs, distributed training, model serving)
- Kubernetes has become the de facto standard for ML orchestration (with GPU support!)
- CI/CD for ML is fundamentally different from traditional software
- Modern tools like Dagger enable portable, containerized CI/CD pipelines
- MLOps bridges the gap between research and production

**What You'll Build**:
- Dockerized ML applications with multi-stage builds
- CI/CD pipelines with Dagger (portable pipelines as code)
- Kubernetes deployments with GPU scheduling
- MLOps workflows with experiment tracking and model registry
- Production ML pipelines with orchestration
- Monitoring and governance systems

---

### Module 30: DevOps Fundamentals for ML Engineers
- **Duration**: 5-6 hours
- **Prerequisites**: Phase 5 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Git workflows for ML projects (trunk-based, feature branches)
- Understand version control for code + data + models
- Learn testing strategies for ML code (unit, integration, model validation)
- Implement code review practices for ML teams
- Understand infrastructure as code (IaC) basics

**Deliverables**:
- Git workflow guide for ML projects
- ML testing framework (unit tests, model tests, data tests)
- Pre-commit hooks for ML code quality
- CI/CD readiness checklist

**Key Concepts**:
- Git workflows (trunk-based vs GitFlow)
- Semantic versioning for models
- Testing pyramid for ML (unit → integration → model → system)
- Code review for ML (code quality + model quality)
- Infrastructure as Code (IaC) introduction

**Real-World Application**: Your kaizen, vibe, and contrarian projects need robust DevOps workflows!

---

### Module 31: Docker & Containerization for ML
- **Duration**: 6-7 hours
- **Prerequisites**: Module 30
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Docker for ML applications
- Build optimized Docker images for ML (multi-stage builds, layer caching)
- Handle large ML artifacts (models, datasets) in containers
- Use Docker Compose for local ML development
- Understand container registries (Docker Hub, ECR, GCR, ACR)

**Deliverables**:
- Dockerized ML application (training + inference)
- Multi-stage Dockerfile for ML (builder pattern)
- Docker Compose stack for local development
- Container size optimization guide (10GB → 2GB!)

**Key Concepts**:
- Multi-stage builds (build → runtime separation)
- Layer caching for faster builds
- .dockerignore for ML projects
- Volume mounts for datasets
- GPU support in Docker (nvidia-docker)
- Container registries and image versioning

**Real-World Application**: Containerize your kaizen RAG system for deployment!

**Did You Know?**
- ML Docker images can be 10-20GB! Multi-stage builds can reduce this to 2-3GB
- PyTorch alone is 2GB+, but you can use lighter base images (python:3.10-slim)
- Docker layer caching can speed up builds from 10 minutes to 30 seconds!

---

### Module 32: CI/CD for AI/ML Development 🔮
- **Duration**: 7-8 hours
- **Prerequisites**: Module 31
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand CI/CD for ML workflows (code + data + models)
- **Master Dagger - portable CI/CD pipelines as code (Python SDK)**
- Implement GitHub Actions for ML (linting, testing, model validation)
- Learn GitLab CI/CD for ML projects
- Explore Tekton (Kubernetes-native CI/CD)
- Build continuous training pipelines
- Automate model testing and validation

**Deliverables**:
- **Dagger pipeline for ML project (Python SDK)**
- GitHub Actions workflow (lint → test → train → deploy)
- GitLab CI/CD pipeline for ML
- Automated model validation pipeline
- CI/CD comparison matrix (Dagger vs GitHub Actions vs GitLab vs Tekton)

**Key Concepts**:
- **Dagger fundamentals: Pipelines as code, containerized steps, portability**
- **Dagger Python SDK: Building ML pipelines programmatically**
- CI/CD for ML vs traditional software
- Continuous training (CT) vs continuous deployment (CD)
- Model testing strategies (accuracy, latency, drift)
- Artifact management (models, datasets, experiment logs)
- Pull request workflows for ML code
- Automated retraining triggers

**💡 Heureka Moment**: CI/CD for ML is different! You're testing code + data + models + infrastructure!

**Real-World Application**:
- Dagger enables portable pipelines that run locally and in CI
- Your ML pipelines work the same on your laptop, GitHub Actions, and production!

**Why Dagger?**
- **Portable**: Same pipeline runs locally, CI, and production
- **Programmable**: Python SDK (not YAML!)
- **Containerized**: Built on Docker, guarantees reproducibility
- **Fast**: Intelligent caching, parallel execution
- **Cloud-agnostic**: Works with GitHub Actions, GitLab CI, Jenkins, CircleCI

**Dagger vs Traditional CI/CD**:
```python
# Traditional CI/CD: YAML hell
# .github/workflows/ml-pipeline.yml (100+ lines of YAML)

# Dagger: Pipelines as Python code!
import dagger

async def ml_pipeline():
    async with dagger.Connection() as client:
        # Build container
        python = client.container().from_("python:3.10")

        # Install dependencies
        python = python.with_exec(["pip", "install", "-r", "requirements.txt"])

        # Run tests
        python = python.with_exec(["pytest", "tests/"])

        # Train model
        python = python.with_exec(["python", "train.py"])

        # All steps containerized, cached, and portable!
```

**Covered CI/CD Tools**:
- **Dagger** (deep dive - modern, portable, programmable)
- **GitHub Actions** (most popular, great free tier)
- **GitLab CI/CD** (built-in, powerful, self-hosted option)
- **Tekton** (Kubernetes-native, complex but flexible)
- **Jenkins** (traditional, widely used in enterprises)

---

### Module 33: Kubernetes Fundamentals for ML
- **Duration**: 7-8 hours
- **Prerequisites**: Module 32
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Kubernetes architecture (pods, services, deployments)
- Deploy ML workloads on Kubernetes
- **Understand GPU scheduling in Kubernetes (NVIDIA GPU Operator, device plugins)**
- Manage resources (CPU, memory, GPU allocation)
- Use persistent volumes for datasets
- Configure ConfigMaps and Secrets for ML configs
- Implement StatefulSets for distributed training

**Deliverables**:
- ML inference deployment on K8s
- **GPU-enabled training job on Kubernetes**
- Persistent volume setup for datasets
- K8s resource management guide
- Multi-environment setup (dev, staging, prod)

**Key Concepts**:
- Kubernetes architecture (control plane, nodes, pods)
- Deployments vs StatefulSets vs Jobs
- **GPU scheduling with NVIDIA GPU Operator**
- **Device plugins for GPU sharing**
- **Node selectors and taints/tolerations for GPU nodes**
- Resource requests and limits (CPU, memory, GPU)
- Persistent volumes for ML data
- ConfigMaps for model configs
- Secrets for API keys and credentials
- Horizontal Pod Autoscaling (HPA)

**Real-World Application**:
- **Kubernetes now has first-class GPU support!**
- **NVIDIA GPU Operator automates GPU setup on K8s**
- Schedule ML training jobs with GPU acceleration
- Scale inference services based on load

**Did You Know?**
- Kubernetes 1.8+ supports GPU scheduling natively!
- NVIDIA GPU Operator simplifies GPU setup (drivers, monitoring, device plugins)
- Multi-Instance GPU (MIG) allows sharing a single GPU across multiple pods
- Time-slicing enables GPU sharing for inference workloads
- Major cloud providers (GKE, EKS, AKS) have managed GPU node pools

**GPU Scheduling Example**:
```yaml
# Request 1 GPU for training job
apiVersion: v1
kind: Pod
metadata:
  name: pytorch-training
spec:
  containers:
  - name: trainer
    image: pytorch/pytorch:2.0-cuda11.8
    resources:
      limits:
        nvidia.com/gpu: 1  # Request 1 GPU!
  nodeSelector:
    accelerator: nvidia-tesla-v100  # Target GPU nodes
```

---

### Module 34: Advanced Kubernetes for AI/ML 🔮
- **Duration**: 8-9 hours
- **Prerequisites**: Module 33
- **Status**: ⚪ Not Started

**Learning Objectives**:
- **Master Kubeflow for ML workflows on Kubernetes**
- **Implement KServe for scalable model serving**
- **Deploy Ray on Kubernetes for distributed computing**
- **Use NVIDIA Triton Inference Server for production serving**
- Understand Volcano for batch scheduling
- Implement multi-GPU and multi-node training
- **Master GPU sharing techniques (MIG, time-slicing)**

**Deliverables**:
- **Kubeflow Pipelines for ML workflow**
- **KServe deployment for model inference**
- **Ray cluster on Kubernetes**
- **Triton Inference Server deployment**
- Multi-GPU training job
- GPU sharing configuration

**Key Concepts**:
- **Kubeflow architecture (Pipelines, Katib, Training Operator)**
- **KServe for model serving (autoscaling, canary deployments)**
- **Ray for distributed computing (training, hyperparameter tuning)**
- **Triton Inference Server (multi-model, multi-framework serving)**
- **Volcano for gang scheduling (all-or-nothing GPU allocation)**
- **NVIDIA Multi-Instance GPU (MIG) - partition A100 GPUs**
- **Time-slicing for GPU sharing**
- **GPU topology awareness (NVLink, PCIe)**

**💡 Heureka Moment**: Kubernetes + GPUs = Scalable ML platform! The cloud is now ML-native!

**Real-World Application**:
- Build production ML platform on K8s
- Scale training from 1 GPU to 100 GPUs
- Serve models with autoscaling (0 to N replicas)
- Share expensive GPUs across teams

**Why This Matters**:
- **Kubeflow**: Industry standard for ML on K8s (used by Google, Uber, Spotify)
- **KServe**: Successor to KFServing, supports all major frameworks
- **Ray**: Powers OpenAI's training infrastructure
- **Triton**: NVIDIA's production inference server (used at scale)

**Tool Comparison**:
- **Kubeflow**: Full ML platform (pipelines, experiments, serving)
- **KServe**: Just model serving (simpler than Kubeflow)
- **Ray**: Distributed computing (training + serving + hyperparameter tuning)
- **Triton**: High-performance inference (optimized for NVIDIA GPUs)

---

### Module 35: MLOps & Experiment Tracking
- **Duration**: 6-7 hours
- **Prerequisites**: Module 34
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master MLflow for experiment tracking
- Learn Weights & Biases (W&B)
- Implement model versioning and registry
- Track metrics, hyperparameters, and artifacts
- Compare MLOps platforms (MLflow, W&B, Neptune, Comet)

**Deliverables**:
- MLflow setup and integration
- Experiment tracking dashboard
- Model registry implementation
- MLOps platform comparison

**Key Concepts**:
- Experiment tracking
- Model versioning and registry
- Hyperparameter logging
- Artifact management (models, datasets, plots)
- MLOps platform comparison

**Real-World Application**: Track experiments for your contrarian stock prediction models!

---

### Module 36: Data Versioning & Feature Stores
- **Duration**: 6-7 hours
- **Prerequisites**: Module 35
- **Status**: ⚪ Not Started

**Learning Objectives**:
- **Master DVC (Data Version Control) for datasets and models**
- Understand data pipelines and lineage
- **Learn feature stores (Feast, Tecton)**
- Implement feature engineering workflows
- Use data validation tools (Great Expectations, TFX Data Validation)

**Deliverables**:
- **DVC setup for dataset versioning**
- **Feast feature store deployment**
- Data pipeline with lineage tracking
- Data validation suite

**Key Concepts**:
- **DVC: Git for data (track datasets, models, metrics)**
- **DVC remotes (S3, GCS, Azure Blob)**
- **Feature stores: Centralized feature management**
- **Feast architecture (registry, offline store, online store)**
- Feature engineering workflows
- Data validation and testing
- Data lineage and provenance

**Real-World Application**:
- Version control your datasets (not just code!)
- Share features across ML projects
- Prevent training-serving skew

**Why Feature Stores?**
- **Consistency**: Same features in training and serving
- **Reusability**: Share features across teams
- **Performance**: Pre-computed features for low-latency serving
- **Monitoring**: Track feature drift

**Feature Store Comparison**:
- **Feast**: Open-source, simple, lightweight
- **Tecton**: Enterprise, fully managed, advanced features
- **AWS SageMaker Feature Store**: AWS-native
- **Vertex AI Feature Store**: GCP-native

---

### Module 37: ML Pipeline Orchestration
- **Duration**: 7-8 hours
- **Prerequisites**: Module 36
- **Status**: ⚪ Not Started

**Learning Objectives**:
- **Master Airflow for ML pipelines (DAGs for ETL + training)**
- **Build Kubeflow Pipelines (Kubernetes-native ML workflows)**
- Explore Vertex AI Pipelines (GCP)
- Use MLflow Pipelines (formerly MLflow Recipes)
- Compare orchestration tools (Airflow, Kubeflow, Prefect, Dagster, ZenML, Metaflow)
- Implement pipeline versioning and reproducibility

**Deliverables**:
- **Airflow DAG for end-to-end ML pipeline**
- **Kubeflow Pipeline for distributed training**
- **Pipeline comparison matrix**
- Reusable pipeline templates

**Key Concepts**:
- **Airflow DAGs (Directed Acyclic Graphs)**
- **Kubeflow Pipelines SDK (components, pipelines, experiments)**
- Vertex AI Pipelines (GCP-managed Kubeflow)
- MLflow Pipelines (templates for common ML tasks)
- Pipeline orchestration patterns
- Data → Feature Engineering → Training → Evaluation → Deployment
- Pipeline versioning and lineage

**Real-World Application**:
- Build automated retraining pipelines
- Schedule daily model updates
- Chain ETL → training → deployment

**Orchestration Tool Comparison**:
- **Airflow**: General-purpose, Python-based, most popular
- **Kubeflow Pipelines**: ML-specific, Kubernetes-native
- **Prefect**: Modern Airflow alternative, Python-native
- **Dagster**: Data pipelines, asset-based
- **ZenML**: MLOps pipelines, framework-agnostic
- **Metaflow**: Netflix's framework, production-focused

**When to Use What**:
- **Airflow**: Complex ETL + ML pipelines, many dependencies
- **Kubeflow**: Pure ML workflows on Kubernetes
- **Prefect/Dagster**: Modern Python workflows
- **ZenML/Metaflow**: End-to-end MLOps

---

### Module 38: Model Deployment & Serving Patterns
- **Duration**: 7-8 hours
- **Prerequisites**: Module 37
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Deploy models as REST APIs (FastAPI, Flask)
- Implement gRPC for high-performance serving
- Choose batch vs real-time inference
- Optimize models for serving (ONNX, TensorRT, quantization)
- **Master deployment patterns (canary, blue-green, shadow, A/B testing)**
- Implement model versioning in production
- Handle model rollback and rollforward

**Deliverables**:
- FastAPI model server with versioning
- gRPC inference service
- Model optimization guide (ONNX conversion)
- **Canary deployment on Kubernetes**
- **A/B testing framework for models**
- Batch inference pipeline

**Key Concepts**:
- REST vs gRPC for model serving
- Model serialization formats (pickle, ONNX, SavedModel, TorchScript)
- Model optimization (quantization, pruning, distillation)
- ONNX Runtime for cross-framework inference
- TensorRT for GPU optimization
- **Canary deployments (gradual rollout)**
- **Blue-green deployments (instant switch)**
- **Shadow deployments (dark launch)**
- **A/B testing for models**
- Model versioning strategies

**Real-World Application**:
- Deploy your kaizen RAG system with A/B testing
- Serve vibe content generation models
- Production inference for contrarian stock predictions

**Deployment Patterns**:
```
Canary: 95% traffic → v1, 5% traffic → v2 (test new model)
Blue-Green: All traffic on v1 (blue), deploy v2 (green), switch instantly
Shadow: v2 receives traffic but doesn't serve (log predictions for comparison)
A/B: 50% users → v1, 50% users → v2 (measure business metrics)
```

---

### Module 39: Monitoring, Governance & Production Best Practices 🔮
- **Duration**: 7-8 hours
- **Prerequisites**: Module 38
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Monitor model performance in production (accuracy, latency, throughput)
- **Detect data drift and concept drift**
- Implement model explainability and interpretability (SHAP, LIME)
- Build model governance frameworks (compliance, auditing)
- Track costs and optimize resource usage
- Define SLAs and SLOs for ML systems
- Implement alerting and incident response

**Deliverables**:
- **Model monitoring dashboard (Prometheus + Grafana)**
- **Data drift detection system**
- **Model explainability reports (SHAP values)**
- Model governance documentation
- Cost optimization guide
- SLA/SLO definition for ML services

**Key Concepts**:
- Model performance monitoring (accuracy decay over time)
- **Data drift**: Input distribution changes (detect with KS test, PSI)
- **Concept drift**: True relationship changes (model becomes stale)
- Model explainability (SHAP, LIME, feature importance)
- Model governance (compliance, auditing, versioning)
- Cost tracking (compute, storage, inference costs)
- SLAs for ML (latency < 100ms, uptime > 99.9%)
- Alerting strategies (performance degradation, drift, cost spikes)

**💡 Heureka Moment**: Production ML is 10% training, 90% monitoring! Models degrade over time - you must monitor drift!

**Real-World Application**:
- Monitor your production models for drift
- Explain AI decisions (regulatory compliance)
- Track ML infrastructure costs
- Set up alerts for model degradation

**Monitoring Stack**:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Evidently AI**: ML-specific monitoring (drift, performance)
- **WhyLabs**: Data and ML monitoring
- **Arize AI**: ML observability platform

**Governance & Compliance**:
- Model cards (documentation)
- Datasheets for datasets
- Audit trails (who trained what when)
- Bias detection and mitigation
- Regulatory compliance (GDPR, CCPA, AI Act)

---

## Phase 7: AI for Infrastructure (Weeks 40-41)

**Goal**: Apply AI to infrastructure management and AIOps

### Module 40: AI for Proactive Cloud Management
- **Duration**: 7-8 hours
- **Prerequisites**: Phase 6 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Build anomaly detection systems
- Implement predictive scaling
- Use AI for capacity planning
- Create intelligent alerting

**Deliverables**:
- Anomaly detection system
- Predictive scaling model
- Capacity planning tool

**Key Concepts**:
- Time series forecasting
- Anomaly detection algorithms
- Predictive models for infrastructure
- Alert fatigue reduction

**Real-World Application**: Your on-prem private cloud management!

---

### Module 41: AIOps & Log Analysis
- **Duration**: 6-7 hours
- **Prerequisites**: Module 40
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Use LLMs for log analysis
- Build root cause analysis systems
- Implement intelligent incident response
- Create AI-powered runbooks

**Deliverables**:
- Log analysis system with LLMs
- Root cause analysis tool
- Incident response automation

**Key Concepts**:
- Log parsing with AI
- Pattern recognition
- Incident correlation
- Automated remediation

**Real-World Application**: Proactive vs reactive infrastructure management!

---

## Phase 8: Capstone Projects (Weeks 42-47)

**Goal**: Apply everything to real-world projects

### Module 42: Kaizen Enhancement - Advanced AI Features
- **Duration**: 8-10 hours
- **Prerequisites**: Phases 1-7 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Implement hybrid search (semantic + keyword) for better RAG accuracy
- Build multi-agent workflows for complex tasks
- Add autonomous debugging capabilities
- Create AI-powered code review system

**Deliverables**:
- Enhanced kaizen RAG with 90%+ accuracy
- Multi-agent system for automated issue resolution
- Code review bot with actionable suggestions
- Performance benchmarks and comparison

**Key Concepts**:
- Hybrid search strategies
- Agent collaboration patterns
- Production RAG optimization
- Continuous learning from user feedback

---

### Module 43: Vibe AI Features - Generative Content Platform
- **Duration**: 8-10 hours
- **Prerequisites**: Phases 1-7 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Implement generative AI for educational content creation
- Add multimodal capabilities (text + images + code)
- Build RAG for course knowledge management
- Create personalized learning paths with AI

**Deliverables**:
- AI content generation API
- Multimodal lesson builder
- RAG-powered Q&A system for students
- Personalization engine

**Key Concepts**:
- Content generation at scale
- Multimodal AI integration
- Educational AI best practices
- Quality control for generated content

---

### Module 44: Contrarian AI Analytics - Stock Intelligence System
- **Duration**: 8-10 hours
- **Prerequisites**: Phases 1-7 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Build LLM-powered sentiment analysis for financial news
- Implement time series forecasting with deep learning
- Create anomaly detection for market data
- Generate actionable investment insights with AI

**Deliverables**:
- Sentiment analysis pipeline for news/earnings calls
- Time series forecasting model
- Anomaly detection alerts
- AI-generated investment reports

**Key Concepts**:
- Financial NLP and sentiment analysis
- Time series deep learning
- Anomaly detection at scale
- Responsible AI for finance

---

## Phase 9: The Journey - History of AI/ML (Optional Enrichment) 🕰️

**Goal**: Understand the context, breakthroughs, and stories behind modern AI

**Why optional?** This phase provides historical context and appreciation for how we got here. It's enrichment for curious minds, not a prerequisite for using AI. More meaningful *after* you've built with modern AI and understand "why things are the way they are."

**Style**: Heavy on storytelling, "Did You Know?" sections, real stories about researchers, failed attempts, and accidental breakthroughs. Learn the *human* side of AI development.

---

### Module 45: The Foundations (1950s-1980s) - The Dark Ages Before Deep Learning 🕰️
- **Duration**: 3-4 hours
- **Prerequisites**: None (can be taken anytime, but best after Phase 2+)
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand the birth of AI as a field (Dartmouth Conference 1956)
- Learn about the perceptron and first neural networks
- Discover why AI had TWO "winters" (funding droughts)
- Explore the expert systems era and why it failed
- See how backpropagation (1986) changed everything

**Key Stories You'll Discover**:
- **The Perceptron Controversy**: How Minsky & Papert's book nearly killed neural networks
- **ELIZA the Psychiatrist**: The 1960s chatbot that fooled people
- **The First AI Winter (1974-1980)**: When funding dried up and researchers switched fields
- **Expert Systems Boom & Bust**: Why MYCIN worked but couldn't scale
- **Backpropagation's Breakthrough**: Rumelhart, Hinton, and Williams' 1986 paper

**"Did You Know?" Highlights**:
- The term "Artificial Intelligence" was coined at a summer workshop in 1956
- The perceptron (1958) could learn... but only linearly separable patterns (XOR broke it!)
- ELIZA (1966) was so convincing, Weizenbaum's secretary asked him to leave while she "talked" to it
- The second AI winter (1987-1993) was triggered by the collapse of the LISP machine market
- Backpropagation was actually discovered THREE TIMES before it became widely used

**Deliverables**:
- Timeline of AI history 1950-1990
- "Lessons from failure" document
- Understanding of why modern deep learning took so long

**Real-World Connection**:
- Why we don't use expert systems anymore (but LLMs are kind of bringing them back!)
- Why "AI winter" fears still haunt the industry
- Why Hinton, LeCun, and Bengio are called the "Godfathers of AI"

---

### Module 46: The Deep Learning Revolution (2000s-2010s) - How Cat Pictures Saved AI 🔥
- **Duration**: 3-4 hours
- **Prerequisites**: None (can be taken anytime, but best after Phase 2+)
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand how ImageNet and AlexNet (2012) ignited the deep learning explosion
- Learn the origin story of Word2Vec and the birth of embeddings (2013)
- See how CNNs, RNNs, and LSTMs evolved
- Discover why GPUs changed everything for AI
- Explore the "bitter lesson" - scale beats cleverness

**Key Stories You'll Discover**:
- **ImageNet Challenge**: How Fei-Fei Li's cat-picture dataset became the benchmark
- **AlexNet's Dominance**: 2012's 10% error reduction that shocked the world
- **Word2Vec's Magic**: "king - man + woman = queen" blew everyone's minds
- **GPU Revolution**: Why gaming hardware accidentally became AI infrastructure
- **The Bitter Lesson**: Rich Sutton's observation that compute beats clever algorithms

**"Did You Know?" Highlights**:
- ImageNet has 14 million labeled images - it took 3 years to build using Amazon Mechanical Turk
- AlexNet used 2 GPUs because one couldn't fit the model (GPUs had 3GB memory in 2012!)
- Word2Vec embeddings were trained on Google News articles in just a few hours
- GPUs are 50-100× faster than CPUs for deep learning (parallel matrix operations)
- Geoffrey Hinton almost left academia in 2012 - then AlexNet happened and everyone wanted to hire him

**Deliverables**:
- Understanding of why 2012 was the turning point
- Mental model of CNNs, RNNs, embeddings
- Appreciation for how recent this revolution is

**Real-World Connection**:
- Why every modern AI model uses embeddings (Word2Vec's legacy)
- Why NVIDIA became a trillion-dollar company (GPU demand)
- Why "throw more compute at it" often wins (bitter lesson)

---

### Module 47: The Transformer Era (2017-Present) - Eight Researchers Changed Everything 🚀
- **Duration**: 4-5 hours
- **Prerequisites**: None (can be taken anytime, but best after Phase 4+)
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand the "Attention Is All You Need" paper and its impact
- Learn the evolution from BERT → GPT-1 → GPT-2 → GPT-3 → GPT-4
- See how scaling laws predicted bigger models would work better
- Discover the "ChatGPT moment" (Nov 2022) and AI going mainstream
- Explore what's happening now and where we're headed (2025+)

**Key Stories You'll Discover**:
- **"Attention Is All You Need"**: The 2017 paper that almost wasn't published
- **BERT's Bidirectional Breakthrough**: Google's 2018 language understanding leap
- **GPT-2 "Too Dangerous to Release"**: OpenAI's controversial 2019 decision
- **GPT-3's Emergence**: When scale produced unexpected capabilities (2020)
- **ChatGPT's 100M Users**: The fastest-growing app in history (5 days!)

**"Did You Know?" Highlights**:
- The "Attention Is All You Need" paper has 8 authors - all were at Google
- Reviewers almost rejected it for being "too simple" - now it's the most cited AI paper of the decade
- BERT's name is a Sesame Street reference (like ELMo before it)
- GPT-2 was "too dangerous to release"... then they released it 9 months later
- GPT-3 cost $4.6M to train in 2020 - GPT-4 reportedly cost $100M+
- ChatGPT reached 100M users in 2 months - faster than TikTok, Instagram, or any app in history

**Deliverables**:
- Understanding of transformer architecture's impact
- Timeline of major LLM releases
- Appreciation for how fast things are moving
- Predictions for 2025-2030

**Real-World Connection**:
- Why transformers power everything you use (ChatGPT, Copilot, Claude, Gemini)
- Why "scaling laws" mean bigger models keep getting better
- Why everyone is racing to build AGI (and what that means)
- How to stay current in a fast-moving field

**The Future (2025 and Beyond)**:
- Multimodal models (GPT-4V, Gemini, Claude 3)
- Reasoning models (o1, o3)
- AI agents and autonomous systems
- Specialized models vs. generalists
- Open-source catching up (Llama, Mistral)
- Where you fit in this journey

---

## 📊 Module Structure (Consistent Format)

Each module follows this structure:
```markdown
### Module X: Title [🔮 if Heureka Moment]
- **Duration**: X-Y hours
- **Prerequisites**: Module Z or Phase Y complete
- **Status**: ⚪ / 🟡 / 🟢 / 🔴

**Learning Objectives**:
- [3-5 specific objectives]

**Deliverables**:
- [Concrete outputs you'll build]

**Key Concepts**:
- [Core ideas you'll master]

**[Optional] Heureka Moment**:
- [Transformative insight explanation]

**[Optional] Real-World Application**:
- [Connection to your actual work]
```

---

## 🎓 Learning Resources

### Primary Tools & Frameworks
- **LLM APIs**: Claude (Anthropic), OpenAI, Ollama (local)
- **AI Frameworks**: LangChain, LangGraph, LlamaIndex
- **Vector DBs**: Qdrant, Pinecone, ChromaDB
- **ML Frameworks**: PyTorch, TensorFlow, Hugging Face Transformers
- **MLOps**: MLflow, Weights & Biases, DVC, Feast, Great Expectations
- **DevOps & CI/CD**: Docker, Kubernetes, Dagger, GitHub Actions, GitLab CI/CD
- **ML on K8s**: Kubeflow, KServe, Ray, NVIDIA Triton, NVIDIA GPU Operator
- **Orchestration**: Airflow, Kubeflow Pipelines, Prefect, ZenML
- **Monitoring**: Prometheus, Grafana, Evidently AI, WhyLabs
- **Deployment**: FastAPI, gRPC, ONNX, TensorRT, AWS/GCP/Azure

### Recommended Reading
- "Attention Is All You Need" (Vaswani et al., 2017)
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
- "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., 2021)
- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2022)

### Online Resources
- Hugging Face Course (huggingface.co/course)
- Fast.ai Practical Deep Learning
- Andrej Karpathy's "Neural Networks: Zero to Hero"
- LangChain Documentation
- PyTorch Tutorials

---

## 🚀 Success Criteria

By the end of Neural Dojo, you will:
- ✅ Be fluent in prompt engineering and AI-driven development
- ✅ Build production RAG systems from scratch
- ✅ Create multi-agent AI orchestrations
- ✅ Train and deploy deep learning models
- ✅ Fine-tune LLMs for specific tasks
- ✅ **Master DevOps & MLOps for AI/ML systems**
- ✅ **Deploy ML workloads on Kubernetes with GPU support**
- ✅ **Build CI/CD pipelines for ML (Dagger, GitHub Actions, GitLab CI)**
- ✅ **Implement model monitoring, drift detection, and governance**
- ✅ Apply AI to real infrastructure problems (AIOps)
- ✅ Have a portfolio of production AI projects

**Most Importantly**: You'll think in AI-native patterns and confidently apply AI to any problem!

---

## 📝 Notes for Future Sessions

### Session Tracking
- Use `docs/curriculum/notes/session_log.md` for chronological history
- Update `START_HERE_TOMORROW.md` at end of each session
- Keep `MASTER_CURRICULUM.md` as single source of truth

### Quality Standards (from jamesblonde)
- Every module MUST have working code examples
- Theory documents should be thorough (no handwaving)
- Include real-world examples and applications
- Test all code before marking module complete
- Update progress tracking after each module

### Project Connections
- **kaizen**: RAG, LangChain, vector DBs, agents (Phases 3-6), K8s deployment (Phase 6)
- **vibe**: Generative AI, multimodal (Phase 5), CI/CD pipelines (Phase 6)
- **contrarian**: ML for time series, forecasting (Phase 4), MLOps workflows (Phase 6), capstone (Phase 8)
- **Work (geospatial + cloud)**: K8s GPU scheduling (Phase 6), AIOps (Phase 7)

---

**Remember**: The goal isn't to memorize everything - it's to become fluent in using and building with AI. You're learning a new way of thinking, not just new tools.

**Let's build! 🥋🧠⚡**

---

_Last updated: 2025-11-24_
_Version: 3.0.0 - EXPANDED DevOps/MLOps (Phase 6: 10 modules with Dagger, K8s GPU support)_
_Next session: Continue with Phase 3 (Building with AI Toolkits) or enhance Phase 1-2 modules_

**🎉 Phase 1 Achievement Unlocked! 🎉**
You've mastered AI-Native Development:
- ✅ Module 1.1: AI Coding Tools Landscape (13 tools, subscriptions vs API)
- ✅ Module 1.2: Local Models for AI Coding (Ollama, Aider, Continue.dev)
- ✅ Module 2: Prompt engineering fundamentals
- ✅ Module 3: AI-powered code generation
- ✅ Module 4: AI-assisted debugging and optimization
- ✅ Module 5: AI coding assistants (Claude Code, Copilot, Cursor)

**🎉 Phase 2 Achievement Unlocked! 🎉**
You've mastered Generative AI Fundamentals:
- ✅ Module 6: Introduction to Large Language Models
- ✅ Module 7: Tokenization & Text Processing
- ✅ Module 8: Text Generation & Sampling Strategies
- ✅ Module 9: Embeddings & Semantic Similarity
- ✅ Module 10: Vector Spaces & Semantic Search 🔮
