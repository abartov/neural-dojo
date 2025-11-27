# Neural Dojo

**From Zero to AI Guru: Master AI, ML, LLMs, and AI-Driven Development**

<!-- GENERATED_BADGES_START -->
[![Progress](https://img.shields.io/badge/Progress-58%25-green)]()
[![Modules](https://img.shields.io/badge/Modules-36%2F62-blue)]()
[![Phase](https://img.shields.io/badge/Current-Phase%207-brightgreen)]()
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

**56 modules** across **12 phases** (~60 weeks, 200+ hours)

<!-- GENERATED_PROGRESS_START -->
| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: AI-Native Development | Complete | 7/7 |
| Phase 2: Generative AI Fundamentals | Complete | 5/5 |
| Phase 3: Vector Search & RAG | Complete | 4/4 |
| Phase 4: Frameworks & Agents | Complete | 7/7 |
| Phase 5: Multimodal AI | Complete | 3/3 |
| Phase 6: Deep Learning Foundations | Complete | 7/7 |
| Phase 7: Advanced Generative AI | In Progress | 3/5 |
| Phase 8: Classical ML | Not Started | 0/3 |
| Phase 9: AI Safety & Evaluation | Not Started | 0/3 |
| Phase 10: DevOps & MLOps | Not Started | 0/10 |
| Phase 11: AI for Infrastructure | Not Started | 0/2 |
| Phase 12: Capstone Projects | Not Started | 0/6 |
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
├── docs/curriculum/           # Curriculum materials
│   ├── MASTER_CURRICULUM.md   # Source of truth
│   ├── MODULE_INDEX.md        # Generated index with navigation
│   └── notes/                 # Theory documents
├── examples/                  # Working code examples per module
│   ├── module_01/
│   ├── module_02/
│   └── ...
├── tools/docs_generator/      # Documentation generator
└── README.md                  # This file (partially generated)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [MASTER_CURRICULUM.md](docs/curriculum/MASTER_CURRICULUM.md) | Complete curriculum (source of truth) |
| [MODULE_INDEX.md](docs/curriculum/MODULE_INDEX.md) | Module navigation with links |
| [START_HERE_TOMORROW.md](docs/curriculum/START_HERE_TOMORROW.md) | Session handoff |

---

## Regenerate Documentation

```bash
python -m tools.docs_generator --all
```

This generates:
- `MODULE_INDEX.md` from MASTER_CURRICULUM.md
- HTML documentation in `docs/_site/`
- Updates README.md progress section

---

## License

Private - for personal learning.

---

## Acknowledgments

- **JamesBlonde** - Proven curriculum pattern
- **Anthropic** - Claude and AI accessibility
- **Open Source Community** - ML/AI tools
