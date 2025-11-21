# Neural Dojo: Gap TODO Tracker

**Last Updated**: 2025-11-21
**Version**: 1.0.0
**Status**: Active Tracking

---

## 🎯 Purpose

Living document tracking all identified gaps and their resolution status. Updated after each gap analysis iteration.

**Usage**:
- Run gap analysis periodically (after completing phases, when blockers encountered)
- Update this file with new gaps or status changes
- Reference when planning module development
- Track completion over time

---

## 📊 Gap Status Summary

| Priority | Total | ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked |
|----------|-------|----------------|----------------|-------------|------------|
| CRITICAL | 4     | 3              | 1              | 0           | 0          |
| HIGH     | 5     | 5              | 0              | 0           | 0          |
| MEDIUM   | 7     | 7              | 0              | 0           | 0          |
| LOW      | 4     | 4              | 0              | 0           | 0          |
| DOCS     | 6     | 5              | 1              | 0           | 0          |
| STRUCT   | 3     | 3              | 0              | 0           | 0          |
| PRACTICAL| 3     | 3              | 0              | 0           | 0          |
| **TOTAL**| **32**| **31**         | **2**          | **0**       | **0**      |

---

## 🚨 CRITICAL PRIORITY GAPS

### GAP-C01: No Module 0 (Prerequisites & Environment Setup)
- **Status**: 🟡 In Progress
- **Priority**: CRITICAL
- **Impact**: HIGH - Blocks all learning
- **Affects**: All students, Module 1
- **Apply When**: Before Module 1 content
- **Estimated Effort**: 4-6 hours (theory + examples)
- **Dependencies**: None
- **Notes**: Creating now as part of Option 1

**Solution**:
- Create Module 0 theory document (2k-5k words)
- Create setup examples (API keys, venv, first LLM call)
- Verify on clean machine
- Add to MASTER_CURRICULUM.md

**Deliverables**:
- [ ] `docs/curriculum/notes/module_00_prerequisites.md`
- [ ] `examples/module_00/` with setup scripts
- [ ] Prerequisites checklist
- [ ] Troubleshooting common setup issues

---

### GAP-C02: Missing Math Prerequisites
- **Status**: ⚪ Not Started
- **Priority**: CRITICAL
- **Impact**: HIGH - Blocks Phase 4 (Deep Learning)
- **Affects**: Modules 20-25
- **Apply When**: Before Module 20, or just-in-time in modules
- **Estimated Effort**: 2-3 hours per module (math sections)
- **Dependencies**: User math background assessment
- **Notes**: Prefer just-in-time explanations over separate module

**Solution Options**:
- **Option A**: Separate "Math for ML" module (8-10 hours)
- **Option B**: Math appendix referenced from modules
- **Option C**: Just-in-time math sections in each module (PREFERRED)

**Math Topics Needed**:
- Linear algebra (vectors, matrices, dot products)
- Calculus (derivatives, chain rule, gradients)
- Probability (distributions, expectation, Bayes' theorem)
- Statistics (mean, variance, correlation)

**Apply To Modules**:
- Module 20: Calculus (gradients, derivatives)
- Module 21: Linear algebra (tensors, matrix ops)
- Module 22: Optimization (gradient descent math)
- Module 25: Chain rule deep dive

---

### GAP-C03: No Data Engineering Coverage
- **Status**: ⚪ Not Started
- **Priority**: CRITICAL
- **Impact**: MEDIUM-HIGH - Missing production skill
- **Affects**: Phase 4+, real-world applications
- **Apply When**: After Module 19, before Module 20
- **Estimated Effort**: 8-10 hours (full module)
- **Dependencies**: Module 19 complete
- **Notes**: Essential for real ML work

**Solution**:
- Create **Module 19.5: Data Engineering for ML**
- Duration: 5-6 hours
- Insert between Modules 19 and 20

**Topics**:
- Data collection strategies (APIs, scraping, datasets)
- Data cleaning and validation (missing values, outliers)
- Dataset creation and curation
- Data versioning (DVC)
- ETL pipelines for ML
- Data quality metrics
- Train/val/test splits
- Data augmentation

**Deliverables**:
- [ ] Data collection pipeline
- [ ] Data cleaning toolkit
- [ ] DVC setup and workflow
- [ ] Dataset versioning example

---

### GAP-C04: No Evaluation & Metrics Module
- **Status**: ⚪ Not Started
- **Priority**: CRITICAL
- **Impact**: HIGH - Can't improve without measuring
- **Affects**: Module 12 (RAG), all AI systems
- **Apply When**: After Module 12
- **Estimated Effort**: 8-10 hours (full module)
- **Dependencies**: Module 12 complete
- **Notes**: Critical for production systems

**Solution**:
- Create **Module 12.5: Evaluating AI Systems**
- Duration: 5-6 hours
- Insert after Module 12

**Topics**:
- RAG evaluation metrics (precision, recall, MRR, NDCG)
- LLM evaluation (perplexity, BLEU, ROUGE, METEOR)
- Human evaluation design
- Creating evaluation datasets
- A/B testing AI systems
- Automated vs human evaluation trade-offs
- Eval dataset biases
- Continuous evaluation

**Deliverables**:
- [ ] RAG evaluation framework
- [ ] LLM evaluation toolkit
- [ ] Evaluation dataset creation guide
- [ ] A/B testing infrastructure

---

## 🟡 HIGH PRIORITY GAPS

### GAP-H01: Security & Safety
- **Status**: ⚪ Not Started
- **Priority**: HIGH
- **Impact**: MEDIUM-HIGH - Critical for production
- **Affects**: Modules 2, 15, 31
- **Apply When**: Module 2 (prompt injection), Module 31 (deployment security)
- **Estimated Effort**: 2-3 hours per module (add sections)
- **Dependencies**: None
- **Notes**: Add sections throughout, not separate module

**Topics**:
- Prompt injection attacks and defenses (Module 2)
- PII handling and data privacy (Modules 12, 31)
- Jailbreaking and guardrails (Module 15)
- Model output validation (Module 15)
- Safe AI deployment (Module 31)
- Security monitoring (Module 32)

**Action Items**:
- [ ] Add security section to Module 2 theory
- [ ] Add PII handling to Module 12
- [ ] Add guardrails to Module 15
- [ ] Add security checklist to Module 31
- [ ] Create security appendix

---

### GAP-H02: Cost Optimization Strategies
- **Status**: ⚪ Not Started
- **Priority**: HIGH
- **Impact**: MEDIUM - Make or break production deployments
- **Affects**: Modules 7, 12, 32
- **Apply When**: Throughout, especially Phase 6
- **Estimated Effort**: 2-3 hours (expand Module 32)
- **Dependencies**: Modules 7, 12 complete
- **Notes**: Expand Module 32 or add dedicated section

**Topics**:
- Caching strategies (semantic caching, exact match)
- Prompt optimization for cost (shorter prompts, batch)
- Batch processing vs streaming trade-offs
- Model selection for cost (GPT-4 vs 3.5 vs local)
- When to cache embeddings vs recompute
- Cost monitoring and alerting
- Token usage optimization
- Streaming for better UX + cost

**Action Items**:
- [ ] Add cost awareness to Module 7 (tokenization)
- [ ] Add caching to Module 12 (RAG)
- [ ] Expand Module 32 with cost optimization
- [ ] Create cost estimation spreadsheet

---

### GAP-H03: Testing AI Systems
- **Status**: ⚪ Not Started
- **Priority**: HIGH
- **Impact**: MEDIUM-HIGH - Essential for production reliability
- **Affects**: Phase 6 (Production ML)
- **Apply When**: After Module 31
- **Estimated Effort**: 8-10 hours (full module)
- **Dependencies**: Module 31 complete
- **Notes**: AI-specific testing is different from standard testing

**Solution**:
- Create **Module 31.5: Testing AI Systems**
- Duration: 5-6 hours
- Insert after Module 31

**Topics**:
- Testing non-deterministic systems
- Testing RAG systems (retrieval + generation)
- Regression testing for ML models
- Property-based testing for AI
- Fuzzing LLM inputs
- Test dataset creation
- Golden dataset approach
- Evaluation-driven development

**Deliverables**:
- [ ] AI testing framework
- [ ] RAG test suite
- [ ] Golden dataset creation guide
- [ ] Regression test automation

---

### GAP-H04: Failure Modes & Robustness
- **Status**: ⚪ Not Started
- **Priority**: HIGH
- **Impact**: MEDIUM - Essential for production systems
- **Affects**: Modules 31-32
- **Apply When**: Phase 6 (Production)
- **Estimated Effort**: 2-3 hours (add sections)
- **Dependencies**: Modules 31-32
- **Notes**: Add to deployment/monitoring modules

**Topics**:
- LLM hallucinations and detection
- When models fail (edge cases, adversarial inputs)
- Error recovery strategies
- Graceful degradation patterns
- Circuit breakers for AI services
- Retry logic and exponential backoff
- Fallback strategies
- Health checks for AI systems

**Action Items**:
- [ ] Add failure modes section to Module 31
- [ ] Add robustness patterns to Module 31
- [ ] Add monitoring for failures in Module 32
- [ ] Create failure mode catalog

---

### GAP-H05: Context Management Deep Dive
- **Status**: ⚪ Not Started
- **Priority**: HIGH
- **Impact**: MEDIUM - Critical for long conversations
- **Affects**: Module 14 (LangChain memory)
- **Apply When**: Module 14
- **Estimated Effort**: 2-3 hours (expand module)
- **Dependencies**: Module 14
- **Notes**: Expand existing module, don't create new one

**Topics**:
- Long conversation management strategies
- Context summarization techniques
- Context compression (selective retention)
- Memory management in agents
- When to truncate vs summarize vs ignore
- Rolling window strategies
- Semantic memory vs episodic memory

**Action Items**:
- [ ] Expand Module 14 theory with context management
- [ ] Add long conversation examples
- [ ] Add summarization strategies
- [ ] Add context window optimization guide

---

## 🟢 MEDIUM PRIORITY GAPS

### GAP-M01: Traditional ML (scikit-learn)
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Often better for tabular data
- **Affects**: Phase 4
- **Apply When**: Optional - create appendix or skip
- **Estimated Effort**: 6-8 hours (full module) OR 1-2 hours (appendix)
- **Dependencies**: Module 19
- **Notes**: Focus is AI/LLMs, traditional ML is secondary

**Solution Options**:
- **Option A**: Full module on scikit-learn (6-8 hours)
- **Option B**: Appendix "When Traditional ML Beats Deep Learning" (PREFERRED)

**Topics (if pursued)**:
- scikit-learn basics
- Decision trees, random forests
- Gradient boosting (XGBoost, LightGBM)
- When to use traditional ML vs deep learning
- Feature engineering

**Decision**: Create appendix, not full module

---

### GAP-M02: Structured Output & Validation
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Important for production reliability
- **Affects**: Module 15 (LangChain Tools)
- **Apply When**: Module 15
- **Estimated Effort**: 2-3 hours (add to module)
- **Dependencies**: Module 15
- **Notes**: Add to existing module

**Topics**:
- Pydantic models for output validation
- JSON schema enforcement
- Retry logic for invalid outputs
- Type-safe AI integrations
- Constrained generation

**Action Items**:
- [ ] Add Pydantic section to Module 15
- [ ] Add JSON schema examples
- [ ] Add retry logic patterns
- [ ] Add validation examples

---

### GAP-M03: Streaming & Real-time Systems
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Better UX for user-facing apps
- **Affects**: Module 31 (Deployment)
- **Apply When**: Module 31
- **Estimated Effort**: 2-3 hours (add to module)
- **Dependencies**: Module 31
- **Notes**: Add to deployment module

**Topics**:
- Streaming LLM responses (token by token)
- WebSocket integrations
- Server-Sent Events (SSE)
- Real-time inference optimization
- Async/await patterns

**Action Items**:
- [ ] Add streaming section to Module 31
- [ ] Add WebSocket example
- [ ] Add SSE example
- [ ] Add async inference patterns

---

### GAP-M04: Hardware & Infrastructure
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Affects deployment decisions
- **Affects**: Modules 19, 26, 31
- **Apply When**: Throughout Phase 4-6
- **Estimated Effort**: 2-3 hours (add sections)
- **Dependencies**: Various
- **Notes**: Add to relevant modules

**Topics**:
- GPU vs CPU trade-offs
- Quantization deep dive (int8, int4, GPTQ, AWQ)
- Model optimization (ONNX, TensorRT)
- Hardware requirements for different models
- Memory optimization techniques
- Compute resource estimation

**Action Items**:
- [ ] Add GPU section to Module 19
- [ ] Expand quantization in Module 26
- [ ] Add hardware considerations to Module 31
- [ ] Create hardware requirements matrix

---

### GAP-M05: Local Model Management
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Important for cost savings, privacy
- **Affects**: Module 6 or new module
- **Apply When**: Module 6 or after
- **Estimated Effort**: 4-6 hours (full module) OR 2-3 hours (expand Module 6)
- **Dependencies**: Module 6
- **Notes**: Ollama mentioned but not covered

**Topics**:
- Ollama deep dive and usage
- llama.cpp for inference
- vLLM for serving
- text-generation-webui
- Running models on consumer hardware
- Quantization for local models
- Local model selection

**Decision**: Expand Module 6 with local models section

---

### GAP-M06: Knowledge Graphs & GraphRAG
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Emerging important technique
- **Affects**: Module 18 or new module
- **Apply When**: Module 18 or after
- **Estimated Effort**: 4-6 hours (full coverage)
- **Dependencies**: Module 18
- **Notes**: Mentioned in Module 18 but not covered

**Topics**:
- Knowledge graph basics
- GraphRAG architecture
- Entity extraction
- Relationship mapping
- Graph-based retrieval
- Hybrid RAG + Graph

**Decision**: Add to Module 18, consider expansion based on interest

---

### GAP-M07: RNNs/LSTMs
- **Status**: ⚪ Not Started (may skip)
- **Priority**: MEDIUM (low if skipping)
- **Impact**: LOW-MEDIUM - Transformers dominate
- **Affects**: Module 24 (Transformers)
- **Apply When**: Module 24 (historical context only)
- **Estimated Effort**: 1-2 hours (historical context) OR 6-8 hours (full module)
- **Dependencies**: Module 23
- **Notes**: Probably skip full coverage, add historical context

**Decision**: Add historical context section to Module 24, skip full module

---

## 🔵 LOW PRIORITY GAPS

### GAP-L01: Ethical AI & Bias
- **Status**: ⚪ Not Started
- **Priority**: LOW-MEDIUM
- **Impact**: LOW-MEDIUM - Important but not core learning
- **Affects**: Throughout
- **Apply When**: Add sections where relevant
- **Estimated Effort**: 1-2 hours (sections)
- **Notes**: Add to relevant modules, create appendix

**Topics**:
- Bias in ML models
- Fairness metrics
- Transparency and explainability
- Responsible AI practices

**Decision**: Add sections throughout, create appendix if needed

---

### GAP-L02: Legal & Compliance
- **Status**: ⚪ Not Started
- **Priority**: LOW-MEDIUM
- **Impact**: LOW-MEDIUM - Important for production
- **Affects**: Production deployment
- **Apply When**: Create appendix
- **Estimated Effort**: 2-3 hours (appendix)
- **Notes**: Not core learning, but good reference

**Topics**:
- Data privacy (GDPR, CCPA)
- Model licensing (open source licenses)
- Using AI output (copyright, attribution)
- Terms of service for AI APIs

**Decision**: Create appendix "Legal Considerations for AI"

---

### GAP-L03: Collaboration & Team ML
- **Status**: ⚪ Not Started (may skip)
- **Priority**: LOW
- **Impact**: LOW - Personal curriculum
- **Affects**: None (personal project)
- **Apply When**: Skip for personal project
- **Estimated Effort**: N/A
- **Notes**: Not needed for personal learning

**Decision**: Skip - not relevant for personal curriculum

---

### GAP-L04: Model Interpretability
- **Status**: ⚪ Not Started
- **Priority**: LOW-MEDIUM
- **Impact**: LOW-MEDIUM - Important for some domains
- **Affects**: Advanced topics
- **Apply When**: Create appendix or advanced module
- **Estimated Effort**: 4-6 hours (full coverage)
- **Notes**: SHAP, LIME, attention visualization

**Decision**: Consider for advanced topics or appendix

---

## 📚 DOCUMENTATION GAPS

### GAP-D01: MODULE_INDEX.md
- **Status**: 🟡 In Progress
- **Priority**: CRITICAL (for usability)
- **Impact**: MEDIUM - Affects navigation
- **Apply When**: Before Module 1
- **Estimated Effort**: 1-2 hours
- **Notes**: Quick reference guide

**Contents**:
- Module listing with one-line descriptions
- Quick navigation
- Search/filter by topic
- Prerequisites at a glance

---

### GAP-D02: session_log.md
- **Status**: 🟡 In Progress
- **Priority**: HIGH (for tracking)
- **Impact**: MEDIUM - Affects session management
- **Apply When**: Before Module 1
- **Estimated Effort**: 30 minutes (template)
- **Notes**: Session tracking protocol

**Contents**:
- Session template
- Chronological log
- Progress tracking
- Decisions made

---

### GAP-D03: GLOSSARY.md
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM (for reference)
- **Impact**: MEDIUM - Helps with terminology
- **Apply When**: Before Module 1, expand throughout
- **Estimated Effort**: 2-3 hours (initial), ongoing
- **Notes**: Living document

**Contents**:
- AI/ML terms with definitions
- Acronyms
- Common abbreviations
- Cross-references

---

### GAP-D04: TROUBLESHOOTING.md
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM (for support)
- **Impact**: MEDIUM - Reduces blockers
- **Apply When**: As issues encountered
- **Estimated Effort**: 1-2 hours (initial), ongoing
- **Notes**: Build up over time

**Contents**:
- Common setup issues
- Environment problems
- API errors
- Installation failures
- Platform-specific issues

---

### GAP-D05: FAQ.md
- **Status**: ⚪ Not Started
- **Priority**: LOW-MEDIUM
- **Impact**: LOW-MEDIUM - Convenient reference
- **Apply When**: As questions arise
- **Estimated Effort**: 1-2 hours (initial), ongoing
- **Notes**: Build up over time

**Contents**:
- Frequently asked questions
- Common misconceptions
- Quick answers
- Links to detailed explanations

---

### GAP-D06: RESOURCES.md
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM (for learning)
- **Impact**: MEDIUM - Curated learning paths
- **Apply When**: Before Module 1
- **Estimated Effort**: 2-3 hours (curated list)
- **Notes**: Papers, tutorials, tools

**Contents**:
- Must-read papers
- Recommended tutorials
- Tools and frameworks
- Communities and forums
- Blogs and newsletters
- Video courses

---

## 🏗️ STRUCTURAL GAPS

### GAP-S01: Steep Phase Transitions
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - May lose learners
- **Affects**: Phase 3 → Phase 4 transition
- **Apply When**: Before Phase 4
- **Estimated Effort**: 2-3 hours (bridge content)
- **Notes**: Phase 3 (LangChain) → Phase 4 (PyTorch) is steep

**Solution**:
- Strengthen Module 19 (Python for ML)
- Add "bridge" content at end of Phase 3
- Explain why we're switching gears
- Preview what's coming

---

### GAP-S02: No Mid-Phase Checkpoints
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Hard to gauge progress
- **Affects**: All phases
- **Apply When**: End of each phase
- **Estimated Effort**: 2-3 hours per checkpoint
- **Notes**: Add mini-projects to validate learning

**Solution**:
- Phase 1: Build AI-powered CLI tool
- Phase 2: Build custom chatbot
- Phase 3: Build production RAG system (already implicit)
- Phase 4: Train and deploy custom model
- Phase 5: Build multimodal application
- Phase 6: Deploy ML system to production (already implicit)
- Phase 7: Build AIOps tool

**Action**: Formalize these as deliverables

---

### GAP-S03: No "Choose Your Path" Options
- **Status**: ⚪ Not Started
- **Priority**: LOW
- **Impact**: LOW - Personal curriculum, but flexibility good
- **Affects**: Overall structure
- **Apply When**: After Phase 1 complete
- **Estimated Effort**: 1-2 hours (documentation)
- **Notes**: Linear curriculum assumes everyone needs everything

**Solution**: Add "Learning Paths" section to MASTER_CURRICULUM.md
- **Path A: AI User** - Phases 1-3, skip deep learning (faster)
- **Path B: AI Builder** - All phases (comprehensive)
- **Path C: ML Engineer** - Phases 1-2, 4-6, lighter on LangChain

**Decision**: Document optional paths, keep linear default

---

## 🛠️ PRACTICAL GAPS

### GAP-P01: Compute Resources Not Addressed
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Blocks Phase 4-5 without GPU
- **Affects**: Module 19, Phase 4-5
- **Apply When**: Module 19
- **Estimated Effort**: 1-2 hours (add section)
- **Notes**: Where to get GPUs, how to use them

**Topics**:
- Free GPU options (Colab, Kaggle, Lightning AI)
- Cloud GPU setup (AWS, GCP, Azure)
- Cost estimation for training
- When you need GPU vs CPU is fine
- Local GPU setup (CUDA)

**Action**: Add compute resources section to Module 19

---

### GAP-P02: No Benchmarking/Profiling
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Can't optimize without measuring
- **Affects**: Modules 22, 31
- **Apply When**: Modules 22, 31
- **Estimated Effort**: 2-3 hours (add sections)
- **Notes**: Performance and memory profiling

**Topics**:
- Performance profiling (cProfile, line_profiler)
- Memory profiling (memory_profiler)
- GPU profiling (nvidia-smi, torch.profiler)
- Benchmark creation
- Comparing model performance

**Action**: Add profiling sections to Modules 22 and 31

---

### GAP-P03: Docker Not Systematically Covered
- **Status**: ⚪ Not Started
- **Priority**: MEDIUM
- **Impact**: MEDIUM - Essential for production deployment
- **Affects**: Modules 11, 30, 31
- **Apply When**: Module 30 or 31
- **Estimated Effort**: 2-3 hours (add section)
- **Notes**: Docker mentioned but not taught

**Topics**:
- Docker basics (images, containers, Dockerfile)
- Docker Compose for multi-container
- Containerizing ML applications
- GPU in Docker
- Docker best practices

**Action**: Add Docker basics to Module 30 or 31

---

## 📈 Gap Analysis History

### Analysis #1: 2025-11-21 (Initial)
- **Gaps Identified**: 32 total
  - 4 Critical
  - 5 High Priority
  - 7 Medium Priority
  - 4 Low Priority
  - 6 Documentation
  - 3 Structural
  - 3 Practical
- **Action Taken**: Created GAP_TODO.md, starting Option 1 (fix critical gaps)
- **Next Analysis**: After Phase 1 complete

---

## 🎯 Prioritization Rules

1. **CRITICAL**: Must fix before affected content
2. **HIGH**: Should fix before affected phase
3. **MEDIUM**: Can fix during or after phase
4. **LOW**: Can defer or skip entirely
5. **DOCS**: Fix before or as needed
6. **STRUCT**: Fix when pattern emerges
7. **PRACTICAL**: Fix when blocked

---

## 📝 Update Protocol

**When to Update**:
- After completing a phase
- When encountering new gaps
- When priorities change
- After user feedback
- During periodic gap analysis

**How to Update**:
1. Run gap analysis (review curriculum, code, docs)
2. Add new gaps to this document
3. Update status of existing gaps
4. Adjust priorities if needed
5. Update summary table
6. Commit changes

---

## ✅ Quick Actions

**Before Module 1** (Critical):
- [x] GAP-D01: MODULE_INDEX.md (in progress)
- [x] GAP-D02: session_log.md (in progress)
- [ ] GAP-D03: GLOSSARY.md
- [ ] GAP-D06: RESOURCES.md
- [ ] GAP-C01: Module 0 (in progress)

**Before Phase 4** (High Priority):
- [ ] GAP-C02: Math prerequisites (just-in-time)
- [ ] GAP-C03: Module 19.5 (Data Engineering)
- [ ] GAP-P01: Compute resources (Module 19)

**Before Phase 6** (High Priority):
- [ ] GAP-C04: Module 12.5 (Evaluation)
- [ ] GAP-H03: Module 31.5 (Testing)
- [ ] GAP-H02: Cost optimization (expand Module 32)

---

**This is a living document. Update after each gap analysis iteration!**

---

_Created: 2025-11-21_
_Last Updated: 2025-11-21_
_Next Review: After Phase 1 complete_
