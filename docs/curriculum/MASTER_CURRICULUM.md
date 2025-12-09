# Neural Dojo: Master Curriculum

**From Zero to AI Guru: Master AI, ML, LLMs, and AI-Driven Development**

**Last Updated**: 2025-12-09
**Version**: 2.0.0
**Status**: 58/60 modules complete (96%)
**Total Duration**: 60 modules, 52-62 weeks (230-310 hours)

---

## 📊 Progress Tracking

| Phase | Name | Modules | Status |
|-------|------|---------|--------|
| 0 | Prerequisites & Environment Setup | 1 | 🟢 1/1 (100%) |
| 1 | AI-Native Development | 9 | 🟡 7/9 (77%) |
| 2 | Generative AI Fundamentals | 5 | 🟢 5/5 (100%) |
| 3 | Vector Search & RAG | 4 | 🟢 4/4 (100%) |
| 4 | Frameworks & Agents | 7 | 🟢 7/7 (100%) |
| 5 | Multimodal AI | 3 | 🟢 3/3 (100%) |
| 6 | Deep Learning Foundations | 7 | 🟢 7/7 (100%) |
| 7 | Advanced Generative AI | 5 | 🟢 5/5 (100%) |
| 8 | Classical ML | 3 | 🟢 3/3 (100%) |
| 9 | AI Safety & Evaluation | 3 | 🟢 3/3 (100%) |
| 10 | DevOps & MLOps | 10 | 🟢 10/10 (100%) |
| 11 | AI for Infrastructure | 2 | 🟢 2/2 (100%) |
| 12 | History of AI/ML | 1 | 🟢 1/1 (100%) |
| **Total** | | **60** | **96%** |

---

## Phase 0: Prerequisites & Environment Setup

**Prepare your development environment before starting**

**Weeks**: 0

### Module 0.0: Prerequisites & Environment Setup

- **Duration**: 2-3 hours
- **Status**: 🟢 Complete
- **Theory**: [module_00_prerequisites.md](notes/module_00_prerequisites.md)
- **Examples**: [module_00/](examples/module_00/)

**Learning Objectives**:
- Verify prerequisites (Python 3.10+, command line basics)
- Set up development environment (venv, pip, IDE)
- Configure API keys for Claude and/or OpenAI
- Make your first LLM API call

**Deliverables**:
- ✅ Python 3.10+ environment verified
- ✅ Virtual environment created and activated
- ✅ .env file with API key(s) configured
- ✅ All test scripts passing

---

## Phase 1: AI-Native Development

**Master using AI as your development partner**

**Weeks**: 1-5

### Module 1.1: AI Coding Tools Landscape

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Theory**: [module_01.1_ai_coding_tools.md](notes/module_01.1_ai_coding_tools.md)
- **Examples**: [module_01/](examples/module_01/)

**Learning Objectives**:
- Understand the AI development landscape (2024-2025)
- Set up AI coding assistants (Claude Code, Cursor, GitHub Copilot)
- Learn the mental model of AI pair programming
- Master subscriptions vs API access distinction

---

### Module 1.2: Local Models for AI Coding

- **Duration**: 3-4 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 1.1
- **Theory**: [module_01.2_local_models.md](notes/module_01.2_local_models.md)
- **Examples**: [module_01.2/](examples/module_01.2/)

**Learning Objectives**:
- Install and run Ollama (local model management)
- Use local models with Aider and Continue.dev
- Implement hybrid approach (80% local, 20% API)
- Optimize costs ($0-5/month vs $50-150/month)

---

### Module 1.3: Claude Code & CLI Deep Dive

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 1.1
- **Theory**: [module_01.3_claude_code_deep_dive.md](notes/module_01.3_claude_code_deep_dive.md)
- **Examples**: [module_01/](examples/module_01/)

**Learning Objectives**:
- Master Claude Code's multi-modal operation
- Configure settings.json and CLAUDE.md
- Build custom slash commands and skills
- Implement hooks for automation

---

### Module 1.4: Agent-First IDEs

- **Duration**: 4-6 hours
- **Status**: 🟡 In Progress
- **Prerequisites**: 1.1
- **Theory**: [module_01.4_agent_first_ides.md](notes/module_01.4_agent_first_ides.md)
- **Examples**: [module_01.4/](examples/module_01.4/)

**Learning Objectives**:
- Understand the evolution from autocomplete to agentic IDEs
- Master Google Antigravity's multi-agent architecture
- Use Windsurf's Cascade system with memory and Flows
- Configure Cline's open-source agent capabilities
- *... and 1 more*

---

### Module 1.5: CLI AI Coding Agents

- **Duration**: 4-6 hours
- **Status**: 🟡 In Progress
- **Prerequisites**: 1.3, 1.4
- **Theory**: [module_01.5_cli_ai_coding_agents.md](notes/module_01.5_cli_ai_coding_agents.md)
- **Examples**: [module_01.5/](examples/module_01.5/)

**Learning Objectives**:
- Master Claude Code's hooks, MCP servers, and slash commands
- Use Aider for git-native AI pair programming
- Explore Goose and other CLI agents
- Build automated CLI workflows and pipelines
- *... and 1 more*

---

### Module 1.6: Prompt Engineering Fundamentals 🔮

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 1.1
- **Theory**: [module_02_prompt_engineering.md](notes/module_02_prompt_engineering.md)
- **Examples**: [module_02/](examples/module_02/)

**Learning Objectives**:
- Master the art of prompt engineering
- Understand prompt structure (system, user, assistant)
- Learn few-shot learning and chain-of-thought
- Handle edge cases and failure modes

---

### Module 1.7: AI-Powered Code Generation

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 1.6
- **Theory**: [module_03_code_generation.md](notes/module_03_code_generation.md)
- **Examples**: [module_03/](examples/module_03/)

**Learning Objectives**:
- Generate code from natural language
- Refactor and debug with AI
- Write tests using AI

---

### Module 1.8: AI-Assisted Debugging & Optimization

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 1.7
- **Theory**: [module_04_debugging.md](notes/module_04_debugging.md)
- **Examples**: [module_04/](examples/module_04/)

**Learning Objectives**:
- Use AI to find and fix bugs
- Optimize performance with AI
- Understand AI's debugging strategies

---

### Module 1.9: Building with AI Coding Assistants

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 1.8
- **Theory**: [module_05_ai_tools.md](notes/module_05_ai_tools.md)
- **Examples**: [module_05/](examples/module_05/)

**Learning Objectives**:
- Master Claude Code, Copilot, Cursor workflows
- Build a complete project with AI assistance
- Develop your personal AI workflow

---

## Phase 2: Generative AI Fundamentals

**Deep understanding of LLMs and how they work**

**Weeks**: 6-10

### Module 2.1: Introduction to Large Language Models

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 1
- **Theory**: [module_06_intro_to_llms.md](notes/module_06_intro_to_llms.md)
- **Examples**: [module_06/](examples/module_06/)

**Learning Objectives**:
- Understand transformer architecture at a high level
- Learn about GPT, Claude, Llama, and other LLMs
- Compare open-source vs proprietary models
- Understand context windows and limitations

---

### Module 2.2: Tokenization & Text Processing

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 2.1
- **Theory**: [module_07_tokenization.md](notes/module_07_tokenization.md)
- **Examples**: [module_07/](examples/module_07/)

**Learning Objectives**:
- Understand how text becomes tokens
- Learn about BPE, WordPiece, SentencePiece
- Master token counting and optimization

---

### Module 2.3: Text Generation & Sampling Strategies

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 2.2
- **Theory**: [module_08_text_generation.md](notes/module_08_text_generation.md)
- **Examples**: [module_08/](examples/module_08/)

**Learning Objectives**:
- Understand autoregressive generation
- Master temperature, top-p, top-k sampling
- Learn about beam search and nucleus sampling

---

### Module 2.4: Embeddings & Semantic Search

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 2.3
- **Theory**: [module_09_embeddings.md](notes/module_09_embeddings.md)
- **Examples**: [module_09/](examples/module_09/)

**Learning Objectives**:
- Understand embedding vectors
- Learn similarity measures (cosine, dot product)
- Build basic semantic search

---

### Module 2.5: Vector Space Visualization 🔮

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 2.4
- **Theory**: [module_10_vector_spaces.md](notes/module_10_vector_spaces.md)
- **Examples**: [module_10/](examples/module_10/)

**Learning Objectives**:
- Visualize embeddings in 2D/3D
- Understand dimensionality reduction (PCA, t-SNE, UMAP)
- Explore semantic relationships in vector space

---

## Phase 3: Vector Search & RAG

**Build production-ready retrieval-augmented generation systems**

**Weeks**: 11-14

### Module 3.1: Vector Databases Deep Dive

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 2.5
- **Theory**: [module_11_vector_databases.md](notes/module_11_vector_databases.md)
- **Examples**: [module_11/](examples/module_11/)

**Learning Objectives**:
- Understand vector database architectures
- Master Qdrant, Pinecone, Weaviate, ChromaDB
- Learn indexing strategies (HNSW, IVF)

---

### Module 3.2: Building RAG Systems

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 3.1
- **Theory**: [module_12_rag_systems.md](notes/module_12_rag_systems.md)
- **Examples**: [module_12/](examples/module_12/)

**Learning Objectives**:
- Design end-to-end RAG pipelines
- Implement chunking strategies
- Handle document preprocessing

---

### Module 3.3: Advanced RAG Patterns 🔮

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 3.2
- **Theory**: [module_13_rag_vs_finetuning.md](notes/module_13_rag_vs_finetuning.md)
- **Examples**: [module_13/](examples/module_13/)

**Learning Objectives**:
- Implement HyDE, query decomposition
- Build multi-hop retrieval
- Master reranking and filtering

---

### Module 3.4: RAG Evaluation & Optimization

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 3.3
- **Theory**: [module_14_advanced_rag_patterns.md](notes/module_14_advanced_rag_patterns.md)
- **Examples**: [module_14/](examples/module_14/)

**Learning Objectives**:
- Evaluate RAG with RAGAS metrics
- Optimize retrieval and generation
- Handle hallucination and accuracy

---

## Phase 4: Frameworks & Agents

**Master LLM frameworks and build autonomous agents**

**Weeks**: 15-21

### Module 4.1: LangChain Fundamentals

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 3
- **Theory**: [module_15_langchain_fundamentals.md](notes/module_15_langchain_fundamentals.md)
- **Examples**: [module_15/](examples/module_15/)

---

### Module 4.2: LangChain Advanced

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 4.1
- **Theory**: [module_16_langchain_tools_function_calling.md](notes/module_16_langchain_tools_function_calling.md)
- **Examples**: [module_16/](examples/module_16/)

---

### Module 4.3: LangGraph for Agents 🔮

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 4.2
- **Theory**: [module_17_chain_of_thought_reasoning.md](notes/module_17_chain_of_thought_reasoning.md)
- **Examples**: [module_17/](examples/module_17/)

---

### Module 4.4: LlamaIndex

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 4.2
- **Theory**: [module_18_langgraph_stateful_workflows.md](notes/module_18_langgraph_stateful_workflows.md)
- **Examples**: [module_18/](examples/module_18/)

---

### Module 4.5: Building AI Agents

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 4.3
- **Theory**: [module_19_llamaindex_alternative_frameworks.md](notes/module_19_llamaindex_alternative_frameworks.md)
- **Examples**: [module_19/](examples/module_19/)

---

### Module 4.6: Agent Memory & Planning 🔮

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 4.5
- **Theory**: [module_20_advanced_agentic_ai.md](notes/module_20_advanced_agentic_ai.md)
- **Examples**: [module_20/](examples/module_20/)

---

### Module 4.7: Multi-Agent Systems

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 4.6
- **Theory**: [module_21_ai_agents_in_production.md](notes/module_21_ai_agents_in_production.md)
- **Examples**: [module_21/](examples/module_21/)

---

## Phase 5: Multimodal AI

**Work with audio, vision, and video AI**

**Weeks**: 22-24

### Module 5.1: Voice & Audio AI

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 4
- **Theory**: [module_22_speech_ai.md](notes/module_22_speech_ai.md)
- **Examples**: [module_22/](examples/module_22/)

---

### Module 5.2: Vision AI

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 5.1
- **Theory**: [module_23_vision_ai.md](notes/module_23_vision_ai.md)
- **Examples**: [module_23/](examples/module_23/)

---

### Module 5.3: Video AI

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 5.2
- **Theory**: [module_24_video_ai.md](notes/module_24_video_ai.md)
- **Examples**: [module_24/](examples/module_24/)

---

## Phase 6: Deep Learning Foundations

**Understand the math and code behind neural networks**

**Weeks**: 25-31

### Module 6.1: Neural Network Fundamentals

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 5
- **Theory**: [module_25_python_for_ml.md](notes/module_25_python_for_ml.md)
- **Examples**: [module_25/](examples/module_25/)

---

### Module 6.2: PyTorch Fundamentals

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 6.1
- **Theory**: [module_26_neural_networks_from_scratch.md](notes/module_26_neural_networks_from_scratch.md)
- **Examples**: [module_26/](examples/module_26/)

---

### Module 6.3: Training Neural Networks

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 6.2
- **Theory**: [module_27_pytorch_fundamentals.md](notes/module_27_pytorch_fundamentals.md)
- **Examples**: [module_27/](examples/module_27/)

---

### Module 6.4: CNNs & Computer Vision

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 6.3
- **Theory**: [module_28_training_deep_networks.md](notes/module_28_training_deep_networks.md)
- **Examples**: [module_28/](examples/module_28/)

---

### Module 6.5: RNNs & Sequence Models

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 6.4
- **Theory**: [module_29_cnns.md](notes/module_29_cnns.md)
- **Examples**: [module_29/](examples/module_29/)

---

### Module 6.6: Backpropagation Deep Dive 🔮

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 6.5
- **Theory**: [module_30_transformers.md](notes/module_30_transformers.md)
- **Examples**: [module_30/](examples/module_30/)

---

### Module 6.7: Transformers from Scratch

- **Duration**: 8-10 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 6.6
- **Theory**: [module_31_backpropagation.md](notes/module_31_backpropagation.md)
- **Examples**: [module_31/](examples/module_31/)

---

## Phase 7: Advanced Generative AI

**Fine-tuning, diffusion models, and RLHF**

**Weeks**: 32-36

### Module 7.1: Fine-tuning LLMs

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 6
- **Theory**: [module_32_finetuning_llms.md](notes/module_32_finetuning_llms.md)
- **Examples**: [module_32/](examples/module_32/)

---

### Module 7.2: LoRA & Parameter-Efficient Fine-tuning

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 7.1
- **Theory**: [module_33_diffusion_models.md](notes/module_33_diffusion_models.md)
- **Examples**: [module_33/](examples/module_33/)

---

### Module 7.3: Diffusion Models

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 7.2
- **Theory**: [module_34_code_generation_models.md](notes/module_34_code_generation_models.md)
- **Examples**: [module_34/](examples/module_34/)

---

### Module 7.4: RLHF & Alignment 🔮

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 7.3
- **Theory**: [module_35_rlhf.md](notes/module_35_rlhf.md)
- **Examples**: [module_35/](examples/module_35/)

---

### Module 7.5: Advanced Generation Techniques

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 7.4
- **Theory**: [module_36_constitutional_ai.md](notes/module_36_constitutional_ai.md)
- **Examples**: [module_36/](examples/module_36/)

---

## Phase 8: Classical ML

**Master the ML techniques that still power 80% of production systems**

**Weeks**: 37-39

### Module 8.1: Scikit-learn & Classical ML

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 7
- **Theory**: [module_37_tabular_ml.md](notes/module_37_tabular_ml.md)
- **Examples**: [module_37/](examples/module_37/)

---

### Module 8.2: XGBoost & Gradient Boosting

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 8.1
- **Theory**: [module_38_time_series.md](notes/module_38_time_series.md)
- **Examples**: [module_38/](examples/module_38/)

---

### Module 8.3: Time Series Forecasting

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 8.2
- **Theory**: [module_39_automl_feature_stores.md](notes/module_39_automl_feature_stores.md)
- **Examples**: [module_39/](examples/module_39/)

---

## Phase 9: AI Safety & Evaluation

**Responsible AI development and systematic evaluation**

**Weeks**: 40-42

### Module 9.1: LLM Evaluation

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 8
- **Theory**: [module_40_ai_safety_alignment.md](notes/module_40_ai_safety_alignment.md)
- **Examples**: [module_40/](examples/module_40/)

---

### Module 9.2: AI Red Teaming

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 9.1
- **Theory**: [module_41_red_teaming.md](notes/module_41_red_teaming.md)
- **Examples**: [module_41/](examples/module_41/)

---

### Module 9.3: AI Safety & Alignment 🔮

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 9.2
- **Theory**: [module_42_llm_evaluation.md](notes/module_42_llm_evaluation.md)
- **Examples**: [module_42/](examples/module_42/)

---

## Phase 10: DevOps & MLOps

**Deploy and operate ML systems in production**

**Weeks**: 43-52

### Module 10.1: ML DevOps Foundations

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 9
- **Theory**: [module_43_devops_fundamentals.md](notes/module_43_devops_fundamentals.md)
- **Examples**: [module_43/](examples/module_43/)

---

### Module 10.2: Docker for ML

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.1
- **Theory**: [module_44_docker_containerization.md](notes/module_44_docker_containerization.md)
- **Examples**: [module_44/](examples/module_44/)

---

### Module 10.3: CI/CD for ML

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.2
- **Theory**: [module_45_cicd_for_ml.md](notes/module_45_cicd_for_ml.md)
- **Examples**: [module_45/](examples/module_45/)

---

### Module 10.4: Kubernetes for ML

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.3
- **Theory**: [module_46_kubernetes_for_ml.md](notes/module_46_kubernetes_for_ml.md)
- **Examples**: [module_46/](examples/module_46/)

---

### Module 10.5: Advanced Kubernetes

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.4
- **Theory**: [module_47_advanced_kubernetes_ml.md](notes/module_47_advanced_kubernetes_ml.md)
- **Examples**: [module_47/](examples/module_47/)

---

### Module 10.6: Experiment Tracking

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.5
- **Theory**: [module_48_mlops_experiment_tracking.md](notes/module_48_mlops_experiment_tracking.md)
- **Examples**: [module_48/](examples/module_48/)

---

### Module 10.7: Data Pipelines

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.6
- **Theory**: [module_49_data_versioning_feature_stores.md](notes/module_49_data_versioning_feature_stores.md)
- **Examples**: [module_49/](examples/module_49/)

---

### Module 10.8: ML Pipelines

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.7
- **Theory**: [module_50_ml_pipeline_orchestration.md](notes/module_50_ml_pipeline_orchestration.md)
- **Examples**: [module_50/](examples/module_50/)

---

### Module 10.9: Model Serving

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.8
- **Theory**: [module_51_model_deployment_patterns.md](notes/module_51_model_deployment_patterns.md)
- **Examples**: [module_51/](examples/module_51/)

---

### Module 10.10: ML Monitoring

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 10.9
- **Theory**: [module_52_monitoring_observability.md](notes/module_52_monitoring_observability.md)
- **Examples**: [module_52/](examples/module_52/)

---

## Phase 11: AI for Infrastructure

**Apply AI to real-world infrastructure problems**

**Weeks**: 53-54

### Module 11.1: Cloud AI Services

- **Duration**: 5-6 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 10
- **Theory**: [module_53_ai_cloud_management.md](notes/module_53_ai_cloud_management.md)
- **Examples**: [module_53/](examples/module_53/)

---

### Module 11.2: AIOps

- **Duration**: 6-8 hours
- **Status**: 🟢 Complete
- **Prerequisites**: 11.1
- **Theory**: [module_54_aiops_log_analysis.md](notes/module_54_aiops_log_analysis.md)
- **Examples**: [module_54/](examples/module_54/)

---

## Phase 12: History of AI/ML

**Understand where we came from to know where we're going**

**Weeks**: 55

### Module 12.1: History of AI & Machine Learning

- **Duration**: 4-5 hours
- **Status**: 🟢 Complete
- **Prerequisites**: Phase 11
- **Theory**: [module_55_history_of_ai_ml.md](notes/module_55_history_of_ai_ml.md)
- **Examples**: [module_55/](examples/module_55/)

---


---

*Generated from curriculum.yaml*