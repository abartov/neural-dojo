# Repository Guidelines

## Project Structure & Module Organization
- `src/neural_dojo/`: Library code (minimal today; grows with new modules).
- `curriculum.yaml`: Single source of truth for phases/modules; drive generated docs.
- `docs/`: Published curriculum, deliverables, and site assets (`docs/curriculum`, `docs/_site`).
- `examples/module_XX/`: Hands-on labs and deliverables; each module keeps its own `requirements.txt`.
- `scripts/`: Authoring utilities (e.g., `generate_curriculum.py`).
- `tests/`: Pytest suite focused on deliverable quality (`tests/test_deliverables.py`).

## Build, Test, and Development Commands
- Install: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Regenerate curriculum: `python scripts/generate_curriculum.py generate`.
- Validate curriculum: `python scripts/generate_curriculum.py validate` (checks missing notes/examples).
- Sync MkDocs nav from curriculum: `python scripts/generate_curriculum.py nav` (must be rerun after curriculum edits).
- Docs site (HTML): `python -m tools.docs_generator --all` → outputs to `docs/_site/`.
- Module lint: `python scripts/lint_modules.py` (warns on missing READMEs or deliverable hygiene).
- Tests: `pytest` (full suite) or `pytest tests/test_deliverables.py -v -x --tb=short` for a fast smoke run.

## Coding Style & Naming Conventions
- Python 3.10+; 4-space indent; line length 100 (Black + isort config in `pyproject.toml`).
- Format/lint (if installed): `black . && isort .`; type-check optional but encouraged: `mypy src tests`.
- Deliverables: one per module named `deliverable_<topic>.py` inside `examples/module_XX/`; include a top-level docstring, type hints, and a `main` or `demo` entry point (enforced by tests).
- Tests follow `test_*.py` pattern; keep fixtures near usage in `tests/` or module-specific project folders.

## Testing Guidelines
- Framework: pytest with coverage targets set to `src/neural_dojo` (HTML output in `htmlcov/` via `addopts`).
- Prefer parametrized tests for modules/deliverables; mirror module numbers in test IDs for quick triage.
- When adding deliverables, run `pytest tests/test_deliverables.py -v` to ensure syntax, docstring, and entry-point checks pass.

## Automation (Dagger)
- CI pipeline lives in `dagger_pipeline.py`; run locally with `dagger run python dagger_pipeline.py` (validates curriculum, syncs nav, lints modules, pytest smoke, mkdocs build).
- Keep repo clean before running (no untracked generated files); pipeline excludes `docs/_site`, `venv`, and caches by default.

## Commit & Pull Request Guidelines
- Commit style mirrors repo history: lowercase conventional prefixes (`feat:`, `docs:`, `fix:`, `chore:`).
- Keep commits focused; include the primary module/area in the subject when relevant (e.g., `docs: update module_10 deliverable`).
- PRs should note scope, testing performed (`pytest ...`), and any generated artifacts (curriculum or docs site). Link issues when applicable; include before/after evidence for doc or UX-facing changes.

## Security & Configuration Tips
- Never commit API keys or secrets; load provider credentials via environment variables when running examples.
- After editing `curriculum.yaml`, re-run generation/validation to avoid broken navigation before opening a PR.
- See `docs/repro_playbook.md` and `docs/repro.template.yaml` for run hygiene (seeds, locks, hashes, safety checks); fill one per substantial run or capstone.
