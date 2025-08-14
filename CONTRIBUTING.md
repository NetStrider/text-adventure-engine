# Contributing

## Workflow

1. Branch from `main`.
2. Small, focused changes.
3. Add/adjust tests for new behavior.
4. Run `pytest -q` before PR.

## Areas

- Engine core (transitions, effects, expressions)
- Validation tooling
- Story content (JSON in `stories/`)
- Documentation (docs/*.md)

## Adding a Story Slice

1. Create `stories/<name>.json`.
2. Ensure validator passes (CLI `validate`).
3. Provide at least one ending.

## Tests

- Place under `tests/` named `test_*.py`.
- Cover: resource changes, conditional visibility, endings.

## Hooks

When adding a new hook: implement -> document in PLUGINS + ARCHITECTURE -> add tests -> bump minor version.

## Coding Standards

- No unguarded `eval` beyond expression context (future parser will replace it).
- Keep plugin calls exception-safe.

Thank you for contributing.

## Developer setup (venv / pre-commit)

Quick steps to get started locally:

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

POSIX (macOS / Linux):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Install pre-commit and enable hooks:

```bash
make precommit-install
pre-commit install
```

Run pre-commit checks on all files locally:

```bash
pre-commit run --all-files
```
