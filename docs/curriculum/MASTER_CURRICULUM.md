# Neural Dojo: Master Curriculum

**From Zero to Hero: Master AI, ML, LLMs, and AI-Driven Development**

**Last Updated**: 2025-11-21
**Version**: 1.3.0
**Status**: Modules 1-2 Complete - Phase 1 In Progress
**Total Duration**: 36 modules, 35-40 weeks (142-203 hours)

---

## 🎯 Mission

Transform you from AI novice to AI-fluent developer capable of:
- Building production RAG systems
- Creating AI agents and multi-agent orchestrations
- Using AI to accelerate development (AI-driven coding)
- Training and deploying deep learning models
- Mastering prompt engineering and LLM integration
- Building generative AI applications
- Applying AI to real-world problems (cloud management, stock analysis, devops)

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
| Module 0: Prerequisites | 0 | ⚪ Not Started | 0/1 |
| Phase 1: AI-Native Development | 1-5 | 🟡 In Progress | 2/5 (40%) |
| Phase 2: Generative AI Fundamentals | 6-10 | ⚪ Not Started | 0/5 |
| Phase 3: Building with AI Toolkits | 11-18 | ⚪ Not Started | 0/8 |
| Phase 4: Deep Learning Foundations | 19-25 | ⚪ Not Started | 0/7 |
| Phase 5: Advanced Generative AI | 26-29 | ⚪ Not Started | 0/4 |
| Phase 6: Production ML Systems | 30-32 | ⚪ Not Started | 0/3 |
| Phase 7: AI for Infrastructure | 33-34 | ⚪ Not Started | 0/2 |
| Phase 8: Capstone Projects | 35 | ⚪ Not Started | 0/1 |
| **TOTAL** | **36 modules** | **6% Complete** | **2/36** |

**Legend**: ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

---

## 📚 Curriculum Structure

---

## Module 0: Prerequisites & Environment Setup (Pre-Phase 1)

**Goal**: Prepare your development environment before starting Module 1

### Module 0: Prerequisites & Environment Setup
- **Duration**: 2-3 hours
- **Prerequisites**: None - this is where you start!
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Verify you have the required prerequisites (Python 3.10+, command line basics)
- Set up your development environment (venv, pip, IDE/editor)
- Configure API keys for Claude and/or OpenAI
- Make your first LLM API call
- Verify everything works before diving into Module 1

**Deliverables**:
- Python 3.10+ environment verified
- Virtual environment created and activated
- `.env` file with API key(s) configured
- All test scripts passing (test_environment.py, test_claude_api.py)
- Development tools ready (text editor/IDE)

**Key Concepts**:
- Virtual environments for Python
- Environment variables and API keys
- Testing API connections
- Basic Python package management

**Files**:
- Theory: `docs/curriculum/notes/module_00_prerequisites.md`
- Examples: `examples/module_00/`

---

## Phase 1: AI-Native Development (Weeks 1-5)

**Goal**: Master using AI as your development partner

### Module 1: Foundations of AI-Driven Development
- **Duration**: 4-5 hours
- **Prerequisites**: None (start here!)
- **Status**: 🟢 Complete

**Learning Objectives**:
- Understand the AI development landscape (2024-2025)
- Set up AI coding assistants (Claude Code, Cursor, GitHub Copilot)
- Learn the mental model of AI pair programming
- Understand when to use AI vs traditional coding

**Deliverables**:
- ✅ Configured development environment with Claude Code
- ✅ 5 AI coding pattern demonstrations (200+ lines each)
- ✅ Python File Analyzer CLI tool (250+ lines, full test coverage)
- ✅ AI tools comparison template
- ✅ Reflection document template

**Key Concepts**:
- AI as a tool, not a replacement
- The human-in-the-loop principle
- AI strengths and limitations
- 5 AI coding patterns (Specification, Iteration, Example, Explanation, Debugging)

**Files Created**:
- Theory: `docs/curriculum/notes/module_01_ai_driven_development.md` (8,000+ words)
- Examples: `examples/module_01/patterns/` (5 pattern demonstrations)
- Project: `examples/module_01/project/pyanalyzer.py` (CLI tool with tests)
- Deliverables: `docs/deliverables/module_01_*.md` (2 templates)

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
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Generate code from natural language
- Refactor existing code with AI
- Debug with AI assistance
- Write tests using AI

**Deliverables**:
- AI-generated Python package
- Automated test suite (AI-written)
- Refactored legacy codebase example

**Key Concepts**:
- Code generation patterns
- AI for documentation
- AI for code review
- Limitations of AI-generated code

---

### Module 4: AI-Assisted Debugging & Optimization
- **Duration**: 4-5 hours
- **Prerequisites**: Modules 1-3
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Use AI to find and fix bugs
- Optimize code performance with AI
- Understand AI's debugging strategies
- Learn when AI fails at debugging

**Deliverables**:
- Debugged complex codebase with AI
- Performance optimization report
- AI debugging workflow document

**Key Concepts**:
- Error analysis with LLMs
- Code optimization patterns
- AI limitations in debugging
- Combining AI + traditional debugging

---

### Module 5: Building with AI Coding Assistants
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 1-4
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master Claude Code workflows
- Understand GitHub Copilot patterns
- Learn Cursor IDE advanced features
- Build a complete project with AI assistance

**Deliverables**:
- Complete CLI tool built with AI
- AI coding assistant comparison matrix
- Personal AI workflow documentation

**Key Concepts**:
- Tool-specific best practices
- Context management
- When to override AI suggestions
- Productivity metrics

---

## Phase 2: Generative AI Fundamentals (Weeks 6-10)

**Goal**: Understand how LLMs and generative AI work under the hood

### Module 6: Introduction to Large Language Models
- **Duration**: 5-6 hours
- **Prerequisites**: Phase 1 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand transformer architecture at a high level
- Learn about GPT, Claude, Llama, and other LLMs
- Understand model sizes and capabilities
- Compare open-source vs proprietary models

**Deliverables**:
- LLM landscape analysis document
- Model comparison matrix
- Your first API integration (Claude/OpenAI)

**Key Concepts**:
- Transformer basics
- Pre-training vs fine-tuning
- Context windows
- Model families (GPT, Llama, Claude)

---

### Module 7: Tokenization & Text Processing
- **Duration**: 4-5 hours
- **Prerequisites**: Module 6
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand how text becomes tokens
- Learn about different tokenizers (BPE, WordPiece, SentencePiece)
- Master token counting and optimization
- Handle multilingual text

**Deliverables**:
- Tokenization analysis tool
- Token optimization examples
- Multilingual tokenization comparison

**Key Concepts**:
- Byte-pair encoding (BPE)
- Token limits and costs
- Subword tokenization
- Special tokens

---

### Module 8: Text Generation & Sampling Strategies
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 6-7
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand how LLMs generate text
- Master temperature, top-p, top-k sampling
- Learn about repetition penalties
- Control generation quality

**Deliverables**:
- Text generation playground
- Sampling strategy comparison
- Generation quality metrics

**Key Concepts**:
- Autoregressive generation
- Temperature scaling
- Nucleus sampling (top-p)
- Top-k sampling

**💡 Heureka Moment** (Module 17 preview): Temperature isn't just "creativity" - it's probability distribution control!

---

### Module 9: Embeddings & Semantic Similarity
- **Duration**: 5-6 hours
- **Prerequisites**: Modules 6-8
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Understand what embeddings are
- Learn about embedding models (BERT, sentence-transformers)
- Calculate semantic similarity
- Visualize embedding spaces

**Deliverables**:
- Embedding visualization tool
- Semantic search prototype
- Embedding model comparison

**Key Concepts**:
- Word embeddings vs sentence embeddings
- Cosine similarity
- Embedding dimensions
- Embedding model selection

---

### Module 10: Vector Spaces & Semantic Search 🔮
- **Duration**: 5-6 hours
- **Prerequisites**: Module 9
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master vector space concepts
- Implement semantic search from scratch
- Understand approximate nearest neighbor (ANN)
- Learn about vector indexing

**Deliverables**:
- Semantic search engine
- Vector space visualization
- ANN algorithm comparison

**Key Concepts**:
- Vector spaces as semantic coordinates
- Nearest neighbor search
- HNSW, IVF, LSH algorithms
- Vector quantization

**💡 Heureka Moment**: Embeddings create a semantic coordinate system where "meaning" has geometry!

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

## Phase 6: Production ML Systems (Weeks 30-32)

**Goal**: Deploy and operate ML systems in production

### Module 30: MLOps & Experiment Tracking
- **Duration**: 6-7 hours
- **Prerequisites**: Phase 5 complete
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Master MLflow for experiment tracking
- Learn Weights & Biases (W&B)
- Implement model versioning
- Track metrics and artifacts

**Deliverables**:
- MLflow setup and integration
- Experiment tracking dashboard
- Model registry implementation

**Key Concepts**:
- Experiment tracking
- Model versioning
- Hyperparameter logging
- Artifact management

---

### Module 31: Model Deployment & Serving
- **Duration**: 7-8 hours
- **Prerequisites**: Module 30
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Deploy models as REST APIs
- Use FastAPI for model serving
- Implement batch inference
- Handle model updates

**Deliverables**:
- FastAPI model server
- Batch inference pipeline
- Model deployment automation

**Key Concepts**:
- REST API design
- Model serialization
- Inference optimization
- A/B testing

---

### Module 32: Monitoring & Observability 🔮
- **Duration**: 6-7 hours
- **Prerequisites**: Module 31
- **Status**: ⚪ Not Started

**Learning Objectives**:
- Monitor model performance
- Detect data drift
- Track token usage and costs
- Implement alerting

**Deliverables**:
- Monitoring dashboard
- Drift detection system
- Cost tracking tool

**Key Concepts**:
- Model performance metrics
- Data drift vs concept drift
- Token economics
- Observability best practices

**💡 Heureka Moment**: Context window economics - understanding token costs changes how you architect AI systems!

---

## Phase 7: AI for Infrastructure (Weeks 33-34)

**Goal**: Apply AI to infrastructure management and AIOps

### Module 33: AI for Proactive Cloud Management
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

### Module 34: AIOps & Log Analysis
- **Duration**: 6-7 hours
- **Prerequisites**: Module 33
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

## Phase 8: Capstone Projects (Weeks 35-40)

**Goal**: Apply everything to real-world projects

### Module 35: Applied AI Projects
- **Duration**: 20-30 hours (flexible)
- **Prerequisites**: All previous phases
- **Status**: ⚪ Not Started

**Choose 2-3 projects to build**:

**Project 1: Enhance Kaizen with Advanced AI**
- Improve RAG system with hybrid search
- Add multi-agent workflows
- Implement autonomous debugging
- Build AI-powered code review
- **Duration**: 8-10 hours

**Project 2: Build AI Features for Vibe**
- Generative AI for content creation
- Multimodal capabilities
- RAG for knowledge management
- **Duration**: 8-10 hours

**Project 3: AI for Contrarian Stock Analysis**
- Sentiment analysis with LLMs
- Time series forecasting
- Anomaly detection in market data
- Generate investment insights
- **Duration**: 8-10 hours

**Project 4: Your Own AI Tool**
- Build something uniquely yours
- Combine multiple techniques
- Deploy to production
- **Duration**: 8-10 hours

**Deliverables**:
- 2-3 complete, production-ready projects
- Documentation and deployment guides
- Lessons learned document

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
- **MLOps**: MLflow, Weights & Biases, DVC
- **Deployment**: FastAPI, Docker, AWS/GCP

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
- ✅ Implement MLOps best practices
- ✅ Apply AI to real infrastructure problems
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
- **kaizen**: RAG, LangChain, vector DBs, agents (Phases 3-6)
- **vibe**: Generative AI, multimodal (Phase 5)
- **contrarian**: ML for time series, forecasting (Phase 4 + capstone)
- **Work (geospatial + cloud)**: AIOps, infrastructure (Phase 7)

---

**Remember**: The goal isn't to memorize everything - it's to become fluent in using and building with AI. You're learning a new way of thinking, not just new tools.

**Let's build! 🥋🧠⚡**

---

_Last updated: 2025-11-21_
_Version: 1.3.0 - Modules 1-2 complete, Phase 1 40% done_
_Next session: Start Module 3 - AI-Powered Code Generation_
