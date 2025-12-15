# Reproducibility Playbook

Use this checklist before moving from theory to hands-on for any module.

## Minimal Repro Contract
- **Seeds**: set and log all seeds (Python, NumPy, torch/TF, random libs) in your entrypoint.
- **Dependencies**: pin versions; prefer `pip freeze > deps.lock` for ad-hoc runs and keep `requirements.txt` updated.
- **Configs**: capture knobs in a single config (YAML/JSON). Save the resolved config with the run artifacts.
- **Data**: store dataset hash/manifest (file count + checksums). Note preprocessing steps and filters.
- **Models**: log model artifact path/hash and commit SHA used to train.
- **Hardware/runtime**: record accelerator type, driver/runtime versions, and OS image.

## `repro.yaml` Template (fill per run)
See `docs/repro.template.yaml` for a ready-to-copy skeleton.
- `run`: id, module, purpose, commit.
- `data`: source URI, version/hash, preprocessing notes.
- `model`: artifact URI/hash, hyperparameters, metrics.
- `env`: python version, pip lock hash, hardware, seeds.
- `notes`: anomalies, follow-ups, safety checks performed.

## Phase Checkpoints
- **Phase intro**: short quiz (concept recall) + tiny run with seeds + log output.
- **Mid-phase**: run a single end-to-end example with `repro.yaml` filled; share artifact + lock file.
- **Phase capstone**: publish a brief report linking config, metrics, and safety checks; include rollback/kill switch notes for deployable work.

## Safety & Cost Guards
- Red-team prompts or eval suites when using LLMs (toxicity, hallucination, prompt-injection basics).
- Track token/latency budgets for agent/tooling examples; record observed costs and limits.
- Keep secrets out of `repro.yaml`; load via environment variables only.

## Quick Commands
- Lock deps: `pip freeze | sort > deps.lock`
- Verify curriculum consistency: `python scripts/generate_curriculum.py validate`
- Sync nav before docs: `python scripts/generate_curriculum.py nav`
- Smoke tests: `pytest tests/test_deliverables.py -v -x --tb=short`
