# Architecture

## Overview

The engine is a deterministic state machine over a directed graph of Scenes. Each Scene contains Choices that (optionally) mutate `GameState` and transition to another Scene. Terminal Scenes (or an explicit `end()` effect) close the run.

```text
Player Input -> Engine.choose -> Effects Applied -> State Mutated -> Next Scene -> Plugins Notified -> Present Choices
```

## Core Modules

- `engine.py`
  - Data classes: `Choice`, `Scene`, `GameState`.
  - `load_story` builds in‑memory graph from JSON.
  - `ExpressionContext` evaluates boolean gate expressions.
  - `apply_effects` interprets DSL commands.
  - `Engine` orchestrates listing choices, applying effects, transitions, plugin hooks, and persistence.
- `validator.py` – static structural checks.
- `tokens.py` – narrative token extraction for future highlighting.

## Data Flow

1. Story JSON -> `load_story` -> `dict[id, Scene]`.
2. Engine init sets `GameState.scene_id` to start.
3. Rendering layer calls `list_choices()` -> filtered list based on conditions & choice types.
4. User selection -> `choose(id)` -> effects -> state mutation -> potential ending -> plugin notifications.
5. Save -> serialize `GameState` snapshot (versioned wrapper) to JSON.

## Choice Visibility Rules

| Type | Condition Fails | Condition Passes |
|------|-----------------|------------------|
| normal | Hidden (if any conditions) | Shown enabled |
| hidden | Hidden | Shown enabled |
| gated | Shown LOCKED | Shown enabled |
| timed (future) | Pending / countdown | Active until timeout |

## Effects DSL (Current)

| Prefix | Operation |
|--------|----------|
| `flag.` | boolean set |
| `stat.` | set / += / -= |
| `inv.add/remove(` | inventory delta |
| `reputation.` | numeric adjustments |
| `end(` | terminate run |

Future: `meta.` (persistent), `var.` (scoped variables), `emit(` (event bus).

## Plugin Lifecycle (current hooks)

- `on_game_start(engine, scene)` – after initial load.
- `on_scene_enter(engine, scene)` – after each transition.
- `on_game_end(engine, scene)` – once after reaching an ending.

Planned hooks:

- `on_before_choices(engine, scene, choices)` – mutate / reorder / annotate.
- `on_choice_selected(engine, scene, choice)` – analytics, logging.
- `on_state_change(engine, delta)` – state diff introspection.
- `format_output(engine, scene_text)` – customize text (e.g., token coloring).

## Persistence

Current save payload: `{ "state": GameState-as-dict, "version": 1 }`.
Planned: add `schema_version` for story, plus migration registry: `migrations[ (from,to) ] = callable`.

## Expression Evaluation

Currently Python `eval` with stripped builtins + attribute proxies. Risks: user expressions limited but still need full sandbox eventually. Replacement plan: parse simple grammar: IDENT ('.' IDENT)* comparisons, bool ops, parentheses, unary NOT, numeric literals, string literals, membership tests (inventory has). Build small AST interpreter—safe and faster.

## Performance Considerations

- Choice listing: O(#choices in scene) – usually small.
- Validation BFS: O(#scenes + #choices) done offline.
- Memory footprint minimal (dataclasses only).

Scaling tactic: lazy load large story shards (future) through indirection layer.

## Extensibility Strategy

Keep `Engine` thin; push experiment features into plugins (analytics, dynamic events, formatting). Provide typed event objects & stable hook names.

## Anti Corruption Layer (future)

When adding a GUI or web transport, isolate I/O adapters (e.g., `adapters/web.py`) so core logic remains framework agnostic.

## Security / Integrity

- Short term: restrict eval builtins (done).
- Medium: custom parser; optional checksum of story file(s) to detect tampering.
- Optional signing: manifest with hash list + signature.

## Testing Strategy

- Unit: engine transitions, effect parsing, expression evaluation edge cases.
- Story fixtures: sample micro stories for each feature type.
- Property-based (future): random sequences of choices should not raise exceptions (except expected gating errors).

## Observability (future)

- Plugin publishes events to allow logging to file / JSON.
- Aggregator plugin to compute ending distribution.

---
Architecture evolves; keep this doc updated when adding new public hooks or persistence changes.
