# Neural Dojo

**From Zero to AI Guru: Master AI, ML, LLMs, and AI-Driven Development**

<!-- GENERATED_BADGES_START -->
[![Progress](https://img.shields.io/badge/Progress-96%25-brightgreen)]()
[![Modules](https://img.shields.io/badge/Modules-58%2F60-blue)]()
[![Status](https://img.shields.io/badge/Status-Active-success)]()
<!-- GENERATED_BADGES_END -->

---

## Mission

Transform from AI novice to **AI Guru** capable of:
- Building production AI systems (RAG, agents, orchestration)
- Using AI for development (prompt engineering, AI coding assistants)
- Understanding deep learning fundamentals (PyTorch, transformers)
- Deploying ML to production (MLOps, monitoring)

---

## Curriculum

**60 modules** across **13 phases** • **96% Complete**

<!-- GENERATED_PROGRESS_START -->
| Phase | Status | Progress |
|-------|--------|----------|
| Phase 0: Prerequisites | 🟢 Complete | 1/1 |
| Phase 1: AI-Native Development | 🟡 In Progress | 5/7 |
| Phase 2: Generative AI Fundamentals | 🟢 Complete | 5/5 |
| Phase 3: Vector Search & RAG | 🟢 Complete | 4/4 |
| Phase 4: Frameworks & Agents | 🟢 Complete | 7/7 |
| Phase 5: Multimodal AI | 🟢 Complete | 3/3 |
| Phase 6: Deep Learning Foundations | 🟢 Complete | 7/7 |
| Phase 7: Advanced Generative AI | 🟢 Complete | 5/5 |
| Phase 8: Classical ML | 🟢 Complete | 3/3 |
| Phase 9: AI Safety & Evaluation | 🟢 Complete | 3/3 |
| Phase 10: DevOps & MLOps | 🟢 Complete | 10/10 |
| Phase 11: AI for Infrastructure | 🟢 Complete | 2/2 |
| Phase 12: History of AI/ML | 🟢 Complete | 3/3 |
| **TOTAL** | **🟡 Active** | **58/60** |
<!-- GENERATED_PROGRESS_END -->

**Full curriculum details**: [MODULE_INDEX.md](docs/curriculum/MODULE_INDEX.md)

---

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- API keys (Claude/OpenAI)

### Setup

```bash
git clone https://github.com/krisztiankoos/neural-dojo.git
cd neural-dojo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start Learning

1. **Begin**: [Module 0 - Prerequisites](docs/curriculum/notes/module_00_prerequisites.md)
2. **Track Progress**: [MODULE_INDEX.md](docs/curriculum/MODULE_INDEX.md)
3. **Session Status**: [START_HERE_TOMORROW.md](docs/curriculum/START_HERE_TOMORROW.md)

---

## Project Structure

```
neural-dojo/
├── curriculum.yaml            # Single source of truth for curriculum
├── docs/curriculum/           # Generated curriculum materials
│   ├── MASTER_CURRICULUM.md   # Generated from curriculum.yaml
│   ├── MODULE_INDEX.md        # Generated navigation index
│   └── notes/                 # Theory documents per module
├── examples/                  # Working code examples per module
│   ├── module_01/
│   ├── module_01.4/
│   ├── module_02/
│   └── ...
├── scripts/
│   ├── generate_curriculum.py # Curriculum generator
│   └── curriculum_manager.py  # Curriculum utilities
├── tools/docs_generator/      # HTML documentation generator
└── README.md                  # This file
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [curriculum.yaml](curriculum.yaml) | Single source of truth (edit this to add modules) |
| [MASTER_CURRICULUM.md](docs/curriculum/MASTER_CURRICULUM.md) | Generated curriculum overview |
| [MODULE_INDEX.md](docs/curriculum/MODULE_INDEX.md) | Module navigation with links |
| [START_HERE_TOMORROW.md](docs/curriculum/START_HERE_TOMORROW.md) | Session handoff |

---

## Curriculum Management

### Regenerate Curriculum Files

```bash
python scripts/generate_curriculum.py generate
```

This generates:
- `MASTER_CURRICULUM.md` from curriculum.yaml
- `MODULE_INDEX.md` with navigation links

### Validate Curriculum

```bash
python scripts/generate_curriculum.py validate
```

Checks for missing theory files, example directories, and deliverables.

### View Status

```bash
python scripts/generate_curriculum.py status
```

### Add a New Module

1. Edit `curriculum.yaml` and add your module to the appropriate phase
2. Run `python scripts/generate_curriculum.py generate` to update index files
3. Create theory doc in `docs/curriculum/notes/`
4. Create examples in `examples/module_X.Y/`

### Generate HTML Documentation

```bash
python -m tools.docs_generator --all
```

Generates HTML documentation in `docs/_site/`

---

## License

Private - for personal learning.

---

## Acknowledgments

- **JamesBlonde** - Proven curriculum pattern
- **Anthropic** - Claude and AI accessibility
- **Open Source Community** - ML/AI tools
