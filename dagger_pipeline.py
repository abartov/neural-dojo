#!/usr/bin/env python3
"""
Dagger pipeline for Neural Dojo CI

Runs (in order):
1) Curriculum validation (theory-first sanity)
2) MkDocs nav sync from curriculum.yaml
3) Deliverable smoke tests via pytest
4) MkDocs build

Usage:
  dagger run python dagger_pipeline.py            # run full pipeline
  dagger run python dagger_pipeline.py test       # run pytest only
"""

import sys

import anyio
import dagger

PYTHON_IMAGE = "python:3.11-slim"
EXCLUDES = [
    ".git",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "venv",
    ".venv",
    "site",
    "htmlcov",
    "docs/_site",
]


async def prepare_environment(client: dagger.Client) -> dagger.Container:
    """Base container with dependencies installed and project mounted."""
    src = client.host().directory(".", exclude=EXCLUDES)

    container = (
        client.container()
        .from_(PYTHON_IMAGE)
        .with_mounted_cache("/root/.cache/pip", client.cache_volume("pip-cache"))
        .with_env_variable("PIP_DISABLE_PIP_VERSION_CHECK", "1")
        .with_mounted_directory("/src", src)
        .with_workdir("/src")
    )

    container = container.with_exec(["python", "-m", "pip", "install", "--upgrade", "pip"])
    container = container.with_exec(["python", "-m", "pip", "install", "-r", "requirements.txt"])
    return container


async def run_step(container: dagger.Container, args: list[str], label: str):
    """Run a command inside the prepared container and print output."""
    print(f"\n▶ {label}")
    output = await container.with_exec(args).stdout()
    if output:
        print(output.strip())


async def run_ci(target: str):
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        container = await prepare_environment(client)

        if target in ("ci", "all"):
            await run_step(
                container,
                ["python", "scripts/generate_curriculum.py", "validate"],
                "Validate curriculum",
            )
            await run_step(
                container,
                ["python", "scripts/generate_curriculum.py", "nav"],
                "Sync MkDocs navigation",
            )
            await run_step(
                container,
                ["python", "scripts/lint_modules.py"],
                "Lint module deliverables and READMEs",
            )
            await run_step(
                container,
                ["pytest", "tests/test_deliverables.py", "-v", "-x", "--tb=short"],
                "Run deliverable smoke tests",
            )
            await run_step(container, ["mkdocs", "build", "--strict"], "Build MkDocs site")
        elif target == "test":
            await run_step(
                container,
                ["pytest", "tests/test_deliverables.py", "-v", "-x", "--tb=short"],
                "Run deliverable smoke tests",
            )
        else:
            raise SystemExit(f"Unknown target: {target}")


async def amain():
    target = sys.argv[1] if len(sys.argv) > 1 else "ci"
    await run_ci(target)


if __name__ == "__main__":
    anyio.run(amain)
