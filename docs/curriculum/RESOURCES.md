# Neural Dojo: Curated Resources

**Last Updated**: 2025-11-21
**Purpose**: Papers, tutorials, tools, and learning resources

---

## 📚 Must-Read Papers

### Foundational

1. **"Attention Is All You Need"** (Vaswani et al., 2017)
   - The transformer paper
   - https://arxiv.org/abs/1706.03762
   - *Relevant to*: Module 24

2. **"BERT: Pre-training of Deep Bidirectional Transformers"** (Devlin et al., 2018)
   - Bidirectional pre-training
   - https://arxiv.org/abs/1810.04805
   - *Relevant to*: Module 9

3. **"Language Models are Few-Shot Learners"** (GPT-3 paper) (Brown et al., 2020)
   - Few-shot learning, in-context learning
   - https://arxiv.org/abs/2005.14165
   - *Relevant to*: Module 2, 6

### RAG & Retrieval

4. **"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"** (Lewis et al., 2020)
   - Original RAG paper
   - https://arxiv.org/abs/2005.11401
   - *Relevant to*: Module 12-13

5. **"Dense Passage Retrieval for Open-Domain Question Answering"** (Karpukhin et al., 2020)
   - Dense retrieval with embeddings
   - https://arxiv.org/abs/2004.04906
   - *Relevant to*: Module 10-11

### Fine-Tuning & Adaptation

6. **"LoRA: Low-Rank Adaptation of Large Language Models"** (Hu et al., 2021)
   - Parameter-efficient fine-tuning
   - https://arxiv.org/abs/2106.09685
   - *Relevant to*: Module 13, 26

7. **"QLoRA: Efficient Finetuning of Quantized LLMs"** (Dettmers et al., 2023)
   - Quantized LoRA
   - https://arxiv.org/abs/2305.14314
   - *Relevant to*: Module 26

### Prompting & Reasoning

8. **"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"** (Wei et al., 2022)
   - Chain-of-thought technique
   - https://arxiv.org/abs/2201.11903
   - *Relevant to*: Module 16

9. **"ReAct: Synergizing Reasoning and Acting in Language Models"** (Yao et al., 2022)
   - Reasoning + acting for agents
   - https://arxiv.org/abs/2210.03629
   - *Relevant to*: Module 16

### Multimodal

10. **"Learning Transferable Visual Models From Natural Language Supervision"** (CLIP) (Radford et al., 2021)
    - Text-image contrastive learning
    - https://arxiv.org/abs/2103.00020
    - *Relevant to*: Module 27

### Image Generation

11. **"Denoising Diffusion Probabilistic Models"** (Ho et al., 2020)
    - Foundational diffusion paper
    - https://arxiv.org/abs/2006.11239
    - *Relevant to*: Module 28

12. **"High-Resolution Image Synthesis with Latent Diffusion Models"** (Stable Diffusion) (Rombach et al., 2021)
    - Latent diffusion
    - https://arxiv.org/abs/2112.10752
    - *Relevant to*: Module 28

---

## 🎓 Online Courses & Tutorials

### Beginner-Friendly

1. **Fast.ai - Practical Deep Learning for Coders**
   - https://www.fast.ai/
   - Free, top-down approach
   - *Relevant to*: Phase 4

2. **Hugging Face Course**
   - https://huggingface.co/course
   - Free, comprehensive transformers course
   - *Relevant to*: Module 24, Phase 5

3. **Andrew Ng's Machine Learning Specialization** (Coursera)
   - https://www.coursera.org/specializations/machine-learning-introduction
   - Classic ML foundations
   - *Relevant to*: Phase 4

### Advanced

4. **Andrej Karpathy - Neural Networks: Zero to Hero**
   - https://karpathy.ai/zero-to-hero.html
   - YouTube series building neural nets from scratch
   - *Relevant to*: Module 20-21

5. **Stanford CS224N: Natural Language Processing with Deep Learning**
   - https://web.stanford.edu/class/cs224n/
   - Free lecture videos
   - *Relevant to*: Phase 2, 4

6. **Berkeley CS 182: Deep Learning**
   - https://cs182sp21.github.io/
   - Comprehensive deep learning course
   - *Relevant to*: Phase 4

---

## 📖 Books

### AI/ML Fundamentals

1. **"Deep Learning"** by Goodfellow, Bengio, and Courville
   - The deep learning bible
   - Free online: https://www.deeplearningbook.org/
   - *Relevant to*: Phase 4

2. **"Speech and Language Processing"** by Jurafsky and Martin
   - NLP fundamentals
   - Free draft: https://web.stanford.edu/~jurafsky/slp3/
   - *Relevant to*: Phase 2

3. **"Dive into Deep Learning"** by Zhang et al.
   - Interactive, code-focused
   - Free online: https://d2l.ai/
   - *Relevant to*: Phase 4

### Practical AI

4. **"Designing Machine Learning Systems"** by Chip Huyen
   - Production ML best practices
   - *Relevant to*: Phase 6

5. **"Building Machine Learning Powered Applications"** by Emmanuel Ameisen
   - End-to-end ML product development
   - *Relevant to*: Phase 6

---

## 🛠️ Tools & Frameworks

### LLM APIs

1. **Anthropic Claude**
   - https://console.anthropic.com/
   - State-of-the-art LLM
   - *Used throughout curriculum*

2. **OpenAI API**
   - https://platform.openai.com/
   - GPT models
   - *Alternative to Claude*

3. **Ollama**
   - https://ollama.ai/
   - Run LLMs locally
   - *Module 6*

### AI Frameworks

4. **LangChain**
   - https://www.langchain.com/
   - https://python.langchain.com/docs/
   - Framework for building with LLMs
   - *Modules 14-17*

5. **LangGraph**
   - https://langchain-ai.github.io/langgraph/
   - Stateful workflows
   - *Module 17*

6. **LlamaIndex**
   - https://www.llamaindex.ai/
   - Data framework for LLM applications
   - *Module 18*

### Vector Databases

7. **Qdrant**
   - https://qdrant.tech/
   - Vector database (used in kaizen!)
   - *Modules 11-12*

8. **Pinecone**
   - https://www.pinecone.io/
   - Managed vector database
   - *Module 11*

9. **ChromaDB**
   - https://www.trychroma.com/
   - Embedded vector database
   - *Module 11*

### Deep Learning

10. **PyTorch**
    - https://pytorch.org/
    - https://pytorch.org/tutorials/
    - Primary deep learning framework
    - *Phase 4*

11. **TensorFlow**
    - https://www.tensorflow.org/
    - Alternative deep learning framework
    - *Module 21*

12. **Hugging Face Transformers**
    - https://huggingface.co/docs/transformers/
    - Pre-trained models library
    - *Phase 5*

### MLOps

13. **MLflow**
    - https://mlflow.org/
    - Experiment tracking, model registry
    - *Module 30*

14. **Weights & Biases**
    - https://wandb.ai/
    - ML experiment tracking and visualization
    - *Module 30*

15. **DVC (Data Version Control)**
    - https://dvc.org/
    - Version control for data and models
    - *Module 19.5*

### Deployment

16. **FastAPI**
    - https://fastapi.tiangolo.com/
    - Modern API framework for Python
    - *Module 31*

17. **Docker**
    - https://www.docker.com/
    - Containerization for deployment
    - *Module 31*

---

## 💻 Development Tools

### Editors & IDEs

1. **VS Code**
   - https://code.visualstudio.com/
   - Popular, extensible editor
   - *Module 0*

2. **Cursor**
   - https://cursor.sh/
   - AI-native IDE (VS Code fork)
   - *Module 1, 5*

3. **PyCharm**
   - https://www.jetbrains.com/pycharm/
   - Professional Python IDE
   - *Module 0*

### AI Coding Assistants

4. **Claude Code**
   - Part of Claude
   - AI coding assistant
   - *Module 1, 5*

5. **GitHub Copilot**
   - https://github.com/features/copilot
   - AI pair programmer
   - *Module 1, 5*

---

## 📰 Blogs & Newsletters

### Must-Follow Blogs

1. **Anthropic Blog**
   - https://www.anthropic.com/news
   - Claude updates and research

2. **OpenAI Blog**
   - https://openai.com/blog/
   - GPT updates and research

3. **Hugging Face Blog**
   - https://huggingface.co/blog
   - ML models and techniques

4. **Chip Huyen's Blog**
   - https://huyenchip.com/blog/
   - ML engineering and systems

5. **Eugene Yan**
   - https://eugeneyan.com/
   - Applied ML and systems

6. **Sebastian Raschka**
   - https://sebastianraschka.com/blog/
   - Deep learning and PyTorch

### Newsletters

7. **The Batch** (Andrew Ng)
   - https://www.deeplearning.ai/the-batch/
   - Weekly AI news

8. **Import AI** (Jack Clark)
   - https://jack-clark.net/
   - Weekly AI research digest

9. **TLDR AI**
   - https://tldr.tech/ai
   - Daily AI news

---

## 🎥 YouTube Channels

1. **Andrej Karpathy**
   - https://www.youtube.com/@AndrejKarpathy
   - Neural networks from scratch

2. **3Blue1Brown**
   - https://www.youtube.com/@3blue1brown
   - Visual math explanations (neural networks series excellent)

3. **StatQuest with Josh Starmer**
   - https://www.youtube.com/@statquest
   - ML concepts explained clearly

4. **Yannic Kilcher**
   - https://www.youtube.com/@YannicKilcher
   - Paper explanations and discussions

---

## 🌐 Communities

### Forums & Discussion

1. **Hugging Face Forums**
   - https://discuss.huggingface.co/
   - Help with transformers, models

2. **r/MachineLearning** (Reddit)
   - https://www.reddit.com/r/MachineLearning/
   - Research discussions

3. **r/LocalLLaMA** (Reddit)
   - https://www.reddit.com/r/LocalLLaMA/
   - Running LLMs locally

4. **LangChain Discord**
   - https://discord.gg/langchain
   - LangChain community

### Competitions & Practice

5. **Kaggle**
   - https://www.kaggle.com/
   - ML competitions and datasets

6. **Papers with Code**
   - https://paperswithcode.com/
   - Research papers + implementations

---

## 🔬 Research Resources

### Preprint Servers

1. **arXiv**
   - https://arxiv.org/list/cs.AI/recent
   - AI/ML research papers

2. **arXiv Sanity**
   - http://www.arxiv-sanity.com/
   - Better arXiv navigation

### Paper Reading

3. **Papers with Code**
   - https://paperswithcode.com/
   - Papers + code implementations

4. **Connected Papers**
   - https://www.connectedpapers.com/
   - Visualize paper connections

---

## 🆓 Free Compute Resources

### GPU Access

1. **Google Colab**
   - https://colab.research.google.com/
   - Free GPU (limited)
   - *Module 19, Phase 4*

2. **Kaggle Notebooks**
   - https://www.kaggle.com/code
   - Free GPU/TPU
   - *Module 19, Phase 4*

3. **Lightning AI**
   - https://lightning.ai/
   - Free GPU studios
   - *Module 19, Phase 4*

---

## 📊 Datasets

1. **Hugging Face Datasets**
   - https://huggingface.co/datasets
   - Thousands of datasets

2. **Kaggle Datasets**
   - https://www.kaggle.com/datasets
   - Curated datasets

3. **Common Crawl**
   - https://commoncrawl.org/
   - Web crawl data

---

## 🔖 Quick Reference Cards

1. **NumPy Cheat Sheet**
   - https://numpy.org/doc/stable/user/absolute_beginners.html

2. **pandas Cheat Sheet**
   - https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf

3. **PyTorch Cheat Sheet**
   - https://pytorch.org/tutorials/beginner/ptcheat.html

---

## 🗺️ Learning Paths from Other Sources

1. **Full Stack Deep Learning**
   - https://fullstackdeeplearning.com/
   - Production ML

2. **MLOps.community**
   - https://mlops.community/
   - MLOps best practices

3. **Made With ML**
   - https://madewithml.com/
   - Applied ML

---

_This resource list will be expanded throughout the curriculum_
_Suggest additions via issues or PRs!_
