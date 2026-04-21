# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
make deps           # Install dev dependencies (uv sync --dev --frozen)
make check          # Full check: fmt + lint + test + test-e2e
make check-static   # fmt + lint only
make fmt            # Run ruff formatter
make lint           # Run mypy + ruff + uv lock check
make lint-mypy      # Type check only (args= supported)
make test           # Run unit tests (args= supported)
make test-e2e       # Run e2e tests (requires tool installed)
make docs-watch     # Local docs server
```

Run a single test:
```sh
uv run --frozen pytest tests/path/to/test_file.py::test_name
```

Run CLI during development:
```sh
uv run nava-platform <args>
```

## Architecture

Entry point: `nava/platform/cli/__main__.py` → `cli/main.py` builds a `typer.Typer` with two sub-apps: `infra` and `app`.

**Layer structure:**

- `nava/platform/cli/` — CLI layer (typer commands, context, console, logging, config)
  - `commands/infra/` — `install`, `update`, `add-app`, `info`, `migrate-from-legacy` subcommands
  - `commands/app.py` — app-level subcommands
- `nava/platform/templates/` — core template logic
  - `template.py` — `Template` class wraps copier; handles copy/update against a project
  - `infra_template.py` — infra-specific template operations
  - `state.py` — reads/writes `.nava` answer files that track installed template versions
  - `template_name.py` — parses template name from URI
- `nava/platform/projects/` — project/app abstractions (`Project`, `InfraProject`)
- `nava/platform/copier_worker.py` — `NavaWorker` extends copier's `Worker` to support `src_exclude` filtering _before_ template rendering (upstream only filters after)
- `nava/platform/util/` — git helpers, wrappers, collections

**Key data flow:** CLI command → `CliContext` (log, console, output level) → `Template`/`InfraTemplate` → `NavaWorker` (wraps copier) → writes files to project dir + updates `.nava` state files.

**State tracking:** Installed template versions are stored in `.nava/` answer files within target projects, not in this repo.

**Copier pin:** `copier` is pinned to a specific git commit in `pyproject.toml` because a later commit breaks `NavaWorker`'s `src_exclude` setup.

## Testing

- Unit tests: `tests/` — mirrors `nava/` package structure
- E2e tests: `tests-e2e/` — shell scripts requiring the tool to be installed; `bin/test-e2e` orchestrates them
- `conftest.py` at `tests/` root contains shared fixtures

## Linting

- `ruff` for formatting and linting (line length 100, Google docstring convention)
- `mypy` in strict mode with `local_partial_types = true`; tests exempt from typed def requirements
- In CI, `make fmt` runs with `--check` and `make lint` runs without `--fix`
