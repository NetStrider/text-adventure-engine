# Style Guide

## Code
* Keep functions focused; prefer <80 LOC.
* Avoid adding new dependencies lightly; core stays stdlib.
* Public API changes require doc + test updates.
* Hooks: never raise unhandled exceptions (wrap internally if complex).

## Naming
* Scene ids / choice ids: snake_case, descriptive (`airlock_triage`, `seal_leak`).
* Flags: boolean, prefixed by domain if helpful (`intel_shard1`, `airlock_sealed`).
* Stats: quantifiable resources (`oxygen`, `integrity`).

## Narrative Style (Relic Node Slice)
* Second-person present tense.
* Evoke biotech + cathedral imagery (bone, hymnal static, lumen glands).
* Keep choice labels imperative verbs first: "Seal the breach", "Divert flow".

## Scene Composition Checklist
| Element | Target |
|---------|--------|
| Choices count | 2–5 (avoid overload) |
| Hidden/gated | ≥1 in slice to demo conditional content |
| Resource effect | At least one oxygen delta |
| Branch to ending | Early failure OR success path |

## Story JSON
* Order keys: id, text, choices, tags, endings (consistent diffs).
* Keep lines ≤ 120 chars for readability.

## Commit Messages
`engine: add on_before_choices hook` / `story: add data_core scene` / `tests: cover oxygen depletion`.

Clarity and author happiness over cleverness.
