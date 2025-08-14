# Text Based Adventure Game

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

This text based adventure game is a fun and interactive way to explore different scenarios and make choices that affect the outcome of the story. Players immerse themselves in a rich narrative, encountering challenges and puzzles. With each decision the story unfolds uniquely, providing a personalized experience and replay value.

## Vision

Multiple endings and branching storylines encourage exploration. Every decision has consequences that alter available future choices, state, and endings.

Interface goals:

- User-friendly and intuitive.
- Support typed commands AND dynamic buttons (web / GUI layer later) for quick selection.
- Highlight (bold/colour) important or interactive tokens inside narrative text. Tokens are denoted as `[[token]]` and can be extracted programmatically (see `src/tokens.py`).

## Current Status (Phase 1 Prototype)

Implemented a foundational Python engine plus an initial themed slice (Relic Node) with:

- JSON story loading (`stories/sample_story.json`, `stories/relic_node_slice.json`).
- Scene + Choice data model.
- Conditional, hidden, and gated choices.
- Effects system for flags, stats, inventory, reputation, endings.
- Simple CLI loop (`src/cli.py`).
- Basic tests (`tests/test_engine.py`).

## Quick Start

Install (editable) and run the prototype CLI.

```bash
pip install -e .[dev]
python -m src.cli
```

### Recommended: use a virtual environment

It's best to use a Python virtual environment to keep dependencies isolated.

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest -q
```

POSIX (macOS / Linux):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

Commands in CLI:

- Enter number or choice id to pick.
- inv - show inventory
- state - show flags/stats/reputation
- validate [maxChoices] - run validation (default maxChoices=12)
- quit - exit game

## Quick demo: timed choice

You can run the CLI against the timed-demo story to see auto-selection of a default timed choice.

```powershell
# From the project root
python -m src.cli stories/timed_demo.json timed_intro
# In the CLI, you can use `wait <ms>` to pause for a number of milliseconds, e.g.
# wait 600  -> waits 600ms so the timed choice expires
```

## Story JSON Schema (Incremental)

Top-level object:

```json
{
 "scenes": [ /* SCENE objects */ ]
}
```

Scene fields:

- id (string, unique)
- text (string) - May contain token markers like [[torch]] (future clickable/highlight target)
- choices (array of Choice objects)
- tags (array<string>) optional
- endings (array<{ code, category }>) optional; presence marks scene as terminal.

Choice fields:

- id (string, unique within scene)
- label (string) - displayed to player
- target (string|null) - next scene id (omit for staying in same scene)
- conditions (array<string>) - expressions (e.g. `flag.hasTorch`, `not flag.hasTorch`)
- effects (array<string>) - mini DSL commands:

  - flag.someFlag = true|false
  - stat.health = 10 | stat.health += 2 | stat.health -= 3
  - inv.add("item") / inv.remove("item")
  - reputation.guild += 2 | reputation.guild = 5
  - end("ENDING_CODE") - immediate ending

- type: normal | hidden | gated | timed (timed placeholder for future)
- timeout_ms (int) - reserved for timed choices
- default (bool) - reserved for timed choices
- requirement_text (string) - message when gated not yet available (future UI usage)

## Expression Mini-Language

Used in `conditions` list. Supported:

- Boolean logic: `and`, `or`, `not` (Python style: `and`, `or`, `not`)
- References: `flag.someFlag`, `stat.health`, `reputation.guild`
- Inventory presence via: `inventory.has("torch")`
- Comparisons: `== != > < >= <=`

If an expression errors, it safely returns False.

## Effect Commands Summary

| Pattern | Meaning |
|---------|---------|
| flag.x = true | Set boolean flag |
| stat.energy = 5 | Set stat to value |
| stat.energy += 2 / -= 1 | Increment / decrement stat |
| inv.add("rope") | Add one rope |
| inv.remove("rope") | Remove one rope if present |
| reputation.guild += 3 | Adjust faction reputation |
| end("CODE") | Mark game ended with CODE |

## Engine Core Objects

- GameState: flags, stats, inventory, reputation, current scene, history, ending.
- Scene: text + choices.
- Choice: decision metadata + conditions + effects.
- Engine:

  - `list_choices()` - returns visible (and gated) choices.

  - `choose(choice_id)` - applies effects, transitions, sets endings.

## Roadmap (Summary)

Full detailed roadmap: see `docs/ROADMAP.md`.
Phases: Core MVP ✅ → Authoring Tools → UX Enhancements → Extensibility → Narrative Depth → UI Packaging → Analytics → Ecosystem.

## Additional Documentation

- Architecture: `docs/ARCHITECTURE.md`
- Story Schema: `docs/STORY_SCHEMA.md`
- Plugin System: `docs/PLUGINS.md`
- Contribution Guide: `CONTRIBUTING.md`
- Style Guide: `docs/STYLE_GUIDE.md`

## Contributing Content

1. Add scenes to a new or existing JSON story file under `stories/`.
2. Keep ids concise (snake_case) and stable.
3. Test with `pytest -q` and manual CLI playthrough.

## Testing

Run tests:

```bash
pytest -q
```

## Validation Utility

CLI command `validate` (optionally pass max choices). Reports:

- Unreachable scenes
- Missing choice targets
- Scenes exceeding max choices (default 12)
- Duplicate choice ids (per scene)
- Dangling scenes (no choices & no endings)
- Scenes mixing endings and choices
- Unreachable scenes
- Missing choice targets
- Scenes exceeding max choices (default 12)
- Duplicate choice ids (per scene)
- Dangling scenes (no choices & no endings)
- Scenes mixing endings and choices

## License

MIT (see `pyproject.toml`).

## Next Steps (Implementation Targets)

- Timed choice handling + default selection
- Token highlighting / formatting pipeline
- Additional plugin hooks (choice_selected, state_change, format_output)
- Save schema version + migration system
- Oxygen resource UI polish (display & warning thresholds)

---
Feel free to propose additional narrative mechanics or request a feature from the roadmap.

## Developer workflow

Quick helper commands (from project root):

- Create venv and install dev deps:

```bash
make install
```

- Run tests:

```bash
make test
```

- Run markdown lint:

```bash
make docs-lint
```

- Install git pre-commit hooks:

```bash
make precommit-install
```

The repository includes `scripts/setup-venv.ps1` and `scripts/setup-venv.sh` for convenient environment setup on Windows and POSIX systems.
