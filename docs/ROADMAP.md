# Roadmap

High-level phased plan to evolve the engine from prototype to a sustainable, extensible platform.

## Principles

- Data‑driven first: story JSON (later optional YAML) stays declarative.
- Backwards compatibility: bump a `story_version` only when incompatible.
- Minimal core, rich plugin surface. Core stays small and audited.
- Deterministic resolution: same inputs -> same outputs (unless an explicit randomness feature is enabled and seeded).
- Author ergonomics: quick validation + good error messages > micro‑optimizations.

## Phase 0 (Done)

Foundations: scene/choice model, conditions, effects DSL, endings, CLI loop, save/load, validation, token extractor, basic tests, plugin start/scene/end hooks.

## Phase 1 – Authoring & Quality Tooling

Deliverables:

- Story validator (extended) – unreachable, dead targets, duplicate ids (DONE baseline; extend with: unused tokens, unused flags/stats, cycles to terminal ratio stats).
- Linter / formatter for JSON ordering and style.
- Schema version field & migration hook stub.
- Story pack loader (folder glob, merge collisions warnings).
- Coverage report: % of choices leading to each ending in sample Monte Carlo runs.

## Phase 2 – UX & Narrative Depth

- Timed choices (timeout_ms + default fallback execution).
- Inline conditional text segments (e.g. `You see [[torch|a lit torch|if=flag.hasTorch]]`).
- Rich output formatting abstraction (tokens -> colored spans / HTML for web UI).
- Multi-select / holding choices (inventory management prompts).
- Weighted random event injection (encounters) with seed for reproducibility.

## Phase 3 – Extensibility Expansion

- Additional plugin hooks: `on_before_choices`, `on_choice_selected`, `on_state_change`, `format_output`.
- Plugin manifest & safe mode (disable untrusted plugins).
- Event bus with typed events objects.
- Sandbox expression parser (remove `eval`).

## Phase 4 – Persistence & Meta

- Save schema migrations.
- Multiple save slots with metadata (playtime, ending reached?).
- Meta progression: persistent unlock flags across runs.
- Minimal analytics (counts of endings reached, average depth) – opt‑in.

## Phase 5 – Tooling & Distribution

- Web authoring UI (schema aware, live validation, graph visualization).
- CLI export to static site (HTML) and to packaged GUI.
- Story packaging spec (.tadv zip: manifest + assets + story.json files + checksum).

## Phase 6 – Ecosystem & Polish

- Localization layer (string tables, token interpolation, fallback locale).
- Accessibility: text speed, high contrast tokens, screen reader friendly output.
- Performance profiling & large story benchmarks (>10k choices) – ensure <50ms choice listing.

## Nice‑To‑Have (Future / Stretch)

- Multiplayer / shared state experiments.
- Procedural scene generation plugins.
- Branch pruning heuristics suggestion tool for authors.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Expression `eval` security | Replace with custom safe parser (Phase 3) |
| Story bloat vs perf | Bench harness + complexity metrics (Phase 6) |
| Plugin instability | Clear hook contracts + exception isolation (done) |
| Schema churn | Version field + migration registry |
| Author confusion | Rich validation & docs + examples |

## Anti‑Goals (For Now)

- 3D rendering / heavy graphics.
- Real‑time combat or physics simulation.
- Deep AI narrative generation inside core (can live in plugins later).

## Status Tags Legend

`DONE`, `PLANNED`, `IN PROGRESS`, `DEFERRED`, `STRETCH`.

---
This file evolves; keep it concise—detailed technical design belongs in the Architecture doc.
