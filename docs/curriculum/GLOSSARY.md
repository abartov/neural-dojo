# Neural Dojo: Glossary

**Last Updated**: 2025-11-21
**Purpose**: AI/ML terms and definitions

---

## How to Use This Glossary

- **Alphabetical**: Terms sorted A-Z
- **Cross-references**: Related terms linked
- **Module references**: Where terms are introduced
- **Living document**: Updated as curriculum progresses

---

## A

**Activation Function**: Non-linear function applied to neuron outputs (e.g., ReLU, sigmoid, tanh). Introduces non-linearity into neural networks. *Module 20*

**Agent**: AI system that can take actions, use tools, and make decisions autonomously. *Module 15-17*

**ANN (Approximate Nearest Neighbor)**: Algorithm for finding similar vectors efficiently without checking all vectors. Used in vector search. *Module 10*

**API (Application Programming Interface)**: Interface for programmatic access to services (e.g., Claude API, OpenAI API). *Module 0, 1*

**Attention Mechanism**: Core component of transformers that allows models to focus on relevant parts of input. *Module 24*

**Autograd**: Automatic differentiation - automatically computing gradients for backpropagation. *Module 21*

**Autoregressive Generation**: Generating text one token at a time, where each token depends on previous tokens. *Module 8*

---

## B

**Backpropagation**: Algorithm for computing gradients in neural networks using chain rule. Fundamental to training deep learning models. *Module 20, 25* 🔮

**Batch**: Group of training examples processed together. Balances speed and memory usage. *Module 22*

**BPE (Byte-Pair Encoding)**: Tokenization algorithm that breaks text into subword units. Used by GPT and many LLMs. *Module 7*

**BERT**: Bidirectional Encoder Representations from Transformers. Influential pre-trained language model. *Module 9*

---

## C

**Chain-of-Thought (CoT)**: Prompting technique where AI "shows its work" by reasoning step-by-step. *Module 16* 🔮

**Chunking**: Breaking documents into smaller pieces for RAG systems. Strategy affects retrieval quality. *Module 12*

**CLIP**: Contrastive Language-Image Pre-training. Multimodal model linking text and images. *Module 27*

**CNN (Convolutional Neural Network)**: Neural network architecture for processing images using convolutional layers. *Module 23*

**Context Window**: Maximum number of tokens an LLM can process at once. Varies by model (e.g., 200K for Claude). *Module 6, 32* 🔮

**Cosine Similarity**: Measure of similarity between vectors based on angle between them. Common in embeddings. *Module 9*

---

## D

**DDPM (Denoising Diffusion Probabilistic Model)**: Type of diffusion model for generating images by iteratively denoising. *Module 28*

**Deep Learning**: Machine learning using neural networks with many layers. *Phase 4*

**Deployment**: Process of making ML models available for production use. *Module 31*

**Diffusion Model**: Generative model that creates images by gradually denoising random noise. Powers Stable Diffusion. *Module 28*

**Dropout**: Regularization technique that randomly drops neurons during training to prevent overfitting. *Module 22*

---

## E

**Embedding**: Dense vector representation of text, images, or other data capturing semantic meaning. *Module 9-10* 🔮

**Encoder-Decoder**: Transformer architecture with separate encoder (input processing) and decoder (output generation). *Module 24*

**Epoch**: One complete pass through the training dataset. *Module 22*

**ETL (Extract, Transform, Load)**: Data pipeline pattern for preparing data for ML. *Module 19.5*

**Evaluation**: Measuring how well an AI system performs. Critical for improvement. *Module 12.5*

---

## F

**Few-Shot Learning**: Learning from a few examples provided in the prompt. *Module 2*

**FIM (Fill-in-the-Middle)**: Code generation technique where model fills in missing code. *Module 29*

**Fine-Tuning**: Adapting a pre-trained model to specific task by continuing training on domain-specific data. *Module 13, 26* 🔮

**Function Calling**: LLM capability to invoke external tools/functions. Also called "tool use". *Module 15*

---

## G

**Generative AI**: AI that creates new content (text, images, code). *Phase 2, 5*

**GPU (Graphics Processing Unit)**: Specialized processor for parallel computation. Essential for training deep learning models. *Module 19*

**Gradient**: Direction and magnitude of change in loss function. Used to update model weights. *Module 20, 25*

**Gradient Descent**: Optimization algorithm that adjusts weights to minimize loss. *Module 20, 22*

**GraphRAG**: RAG system using knowledge graphs for structured retrieval. *Module 18*

---

## H

**Hallucination**: When LLM generates plausible but incorrect information. Major challenge in production systems. *Module 31*

**HNSW (Hierarchical Navigable Small World)**: Efficient ANN algorithm used in vector databases. *Module 10, 11*

**Hugging Face**: Platform for sharing ML models and datasets. Hub for transformers and LLMs. *Phase 4-5*

**Hyperparameter**: Configuration value set before training (e.g., learning rate, batch size). *Module 22*

---

## I

**Inference**: Using a trained model to make predictions. Distinct from training. *Module 31*

**Instruction Tuning**: Fine-tuning LLMs to follow instructions better. *Module 26*

---

## J

**JSON**: Data format commonly used for LLM outputs and function calling. *Module 15*

---

## K

**Knowledge Graph**: Structured representation of entities and relationships. Used in GraphRAG. *Module 18*

---

## L

**LangChain**: Framework for building applications with LLMs. Provides chains, agents, memory, tools. *Module 14-17*

**LangGraph**: Extension of LangChain for stateful, cyclic workflows. Used in kaizen! *Module 17* 🔮

**Latent Diffusion**: Diffusion model operating in latent space. More efficient than pixel-space diffusion. *Module 28*

**LCEL (LangChain Expression Language)**: Declarative way to compose LangChain chains. *Module 14*

**Learning Rate**: Step size for gradient descent. Critical hyperparameter. *Module 22*

**LLM (Large Language Model)**: Neural network trained on massive text data. Examples: GPT, Claude, Llama. *Module 6*

**LoRA (Low-Rank Adaptation)**: Parameter-efficient fine-tuning method. Adds small trainable matrices. *Module 13, 26*

**Loss Function**: Metric measuring how wrong model predictions are. Minimized during training. *Module 20*

---

## M

**MLflow**: Open-source platform for MLOps - experiment tracking, model registry. *Module 30*

**MLOps**: Practices for deploying and maintaining ML systems in production. *Phase 6*

**Model**: Neural network with learned parameters. Can be pre-trained, fine-tuned, or trained from scratch. *Throughout*

**Multimodal**: AI handling multiple types of data (text + images, audio, etc.). *Module 27*

---

## N

**Neural Network**: Computing system inspired by biological brains. Consists of interconnected neurons in layers. *Module 20*

**Neuron**: Basic unit in neural network. Computes weighted sum of inputs + bias, applies activation function. *Module 20*

**NumPy**: Python library for numerical computing. Foundation for ML in Python. *Module 19*

---

## O

**Ollama**: Tool for running LLMs locally. Alternative to API-based models. *Module 6*

**Optimizer**: Algorithm for updating model weights (e.g., Adam, SGD). *Module 21, 22*

**Overfitting**: When model memorizes training data but fails to generalize. Prevented by regularization. *Module 22*

---

## P

**pandas**: Python library for data manipulation and analysis. Essential for ML. *Module 19*

**Parameter**: Learned weight in neural network. Modern LLMs have billions of parameters. *Module 6*

**PEFT (Parameter-Efficient Fine-Tuning)**: Methods for fine-tuning using fewer parameters (e.g., LoRA). *Module 13, 26*

**Positional Encoding**: Adding position information to transformer inputs. Transformers have no inherent notion of order. *Module 24*

**Pre-training**: Initial training of model on large dataset. Creates foundation for fine-tuning. *Module 6*

**Prompt**: Input text given to LLM. Quality of prompt dramatically affects output quality. *Module 2* 🔮

**Prompt Engineering**: Art and science of crafting effective prompts. First heureka moment! *Module 2* 🔮

**PyTorch**: Popular deep learning framework. Primary framework for this curriculum. *Module 21-25*

---

## Q

**QLoRA (Quantized LoRA)**: LoRA combined with quantization for even more efficient fine-tuning. *Module 13, 26*

**Quantization**: Reducing numerical precision of weights (e.g., float32 → int8) to save memory and speed inference. *Module 26*

**Qdrant**: Vector database for semantic search. Used in kaizen! *Module 11-12*

---

## R

**RAG (Retrieval-Augmented Generation)**: Architecture combining retrieval (vector search) with generation (LLM). Injects dynamic knowledge. *Module 12-13* 🔮

**ReAct**: Reasoning + Acting pattern for agents. Combines chain-of-thought with tool use. *Module 16*

**Regularization**: Techniques to prevent overfitting (dropout, L2, early stopping). *Module 22*

**ReLU (Rectified Linear Unit)**: Common activation function: f(x) = max(0, x). *Module 20*

---

## S

**Sampling**: Choosing next token during generation based on probability distribution. *Module 8*

**Self-Attention**: Attention mechanism where input attends to itself. Core of transformers. *Module 24*

**Semantic Search**: Search based on meaning rather than keywords. Powered by embeddings. *Module 10*

**sentence-transformers**: Library for computing sentence embeddings. *Module 9, 11*

**SGD (Stochastic Gradient Descent)**: Optimizer that updates weights using individual or small batches. *Module 22*

**StateGraph**: LangGraph construct for managing stateful workflows. *Module 17*

**Streaming**: Sending LLM responses token-by-token as generated. Better UX. *Module 31*

**System Prompt**: Initial instructions that set LLM behavior for entire conversation. *Module 2*

---

## T

**Temperature**: Sampling parameter controlling randomness (low = focused, high = creative). *Module 8, 17* 🔮

**Tensor**: Multi-dimensional array. Fundamental data structure in PyTorch. *Module 21*

**TensorFlow**: Deep learning framework by Google. Alternative to PyTorch. *Module 21 (secondary)*

**Token**: Unit of text LLMs process (roughly 0.75 words). Affects cost and context limits. *Module 7*

**Tokenization**: Process of splitting text into tokens. Different LLMs use different tokenizers. *Module 7*

**Tool Use**: See "Function Calling". *Module 15*

**Top-k Sampling**: Sampling from k most likely next tokens. *Module 8*

**Top-p (Nucleus) Sampling**: Sampling from smallest set of tokens with cumulative probability ≥ p. *Module 8*

**Transfer Learning**: Using pre-trained model as starting point. Common in computer vision. *Module 23*

**Transformer**: Neural network architecture using attention. Foundation of modern LLMs. *Module 24*

---

## U

**U-Net**: CNN architecture for image generation, used in diffusion models. *Module 28*

---

## V

**Vector**: Array of numbers representing something (text, image, etc.) in embedding space. *Module 9-10*

**Vector Database**: Specialized database for storing and searching vectors. Examples: Qdrant, Pinecone. *Module 11*

**venv**: Python virtual environment for isolated dependencies. *Module 0*

**Vision-Language Model**: Multimodal model processing both images and text (e.g., CLIP, GPT-4V). *Module 27*

---

## W

**Weights**: Learned parameters in neural network. Adjusted during training. *Module 20*

**Weight Decay**: Regularization technique adding penalty for large weights. *Module 22*

---

## Z

**Zero-Shot Learning**: Performing task without examples, relying on pre-training. *Module 2*

---

## Acronyms Quick Reference

- **AI**: Artificial Intelligence
- **ANN**: Approximate Nearest Neighbor
- **API**: Application Programming Interface
- **BERT**: Bidirectional Encoder Representations from Transformers
- **BPE**: Byte-Pair Encoding
- **CLIP**: Contrastive Language-Image Pre-training
- **CNN**: Convolutional Neural Network
- **CoT**: Chain-of-Thought
- **DDPM**: Denoising Diffusion Probabilistic Model
- **DVC**: Data Version Control
- **ETL**: Extract, Transform, Load
- **FIM**: Fill-in-the-Middle
- **GPU**: Graphics Processing Unit
- **HNSW**: Hierarchical Navigable Small World
- **LCEL**: LangChain Expression Language
- **LLM**: Large Language Model
- **LoRA**: Low-Rank Adaptation
- **ML**: Machine Learning
- **MLOps**: Machine Learning Operations
- **PEFT**: Parameter-Efficient Fine-Tuning
- **QLoRA**: Quantized LoRA
- **RAG**: Retrieval-Augmented Generation
- **ReLU**: Rectified Linear Unit
- **SGD**: Stochastic Gradient Descent

---

## 🔮 Heureka Moment Terms

These terms mark transformative insights:
- **Prompt Engineering** (Module 2)
- **Embeddings** (Module 10)
- **RAG vs Fine-tuning** (Module 13)
- **Chain-of-Thought** (Module 16)
- **Temperature** (Module 17)
- **LangGraph StateGraph** (Module 17)
- **Backpropagation** (Module 25)
- **Context Window Economics** (Module 32)

---

_This glossary will be expanded as curriculum progresses_
_Definitions kept concise - see modules for detailed explanations_
