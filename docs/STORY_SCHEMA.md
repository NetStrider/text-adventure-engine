# Story Schema

Formal specification of the story JSON consumed by `load_story`.

## Top-Level

```json
{
 "story_version": 1,            // optional, for future migrations
 "scenes": [ Scene, ... ]
}
```

`story_version` defaults to 1 if omitted.

## Scene Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Unique across all scenes |
| text | string | yes | Narrative body; may include tokens `[[token]]` |
| choices | Choice[] | yes (can be empty if endings present) | Order given displayed |
| tags | string[] | no | Arbitrary categorization |
| endings | Ending[] | no | Presence marks scene as terminal if non-empty |

Constraints:

- A scene must have either choices or endings (or both – but flagged as ambiguous by validator).
- Ids should be snake_case.

## Choice Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Unique within the parent scene |
| label | string | yes | Display text |
| target | string|null | no | Scene id to transition; null/omit = remain |
| conditions | string[] | no | Boolean expressions gating visibility/locking |
| effects | string[] | no | Effects DSL commands executed on selection |
| type | enum | no | normal (default) | hidden | gated | timed |
| timeout_ms | int | no | Timed choices only |
| default | bool | no | If true & timed, auto-picked on timeout |
| requirement_text | string | no | UI message when gated and locked |

## Ending Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| code | string | yes | Identifier returned in `GameState.ending_code` |
| category | string | no | e.g., good, bad, neutral |

## Expressions (Conditions)

Grammar (informal):

```text
EXPR := OR
OR   := AND ('or' AND)*
AND  := NOT ('and' NOT)*
NOT  := 'not' NOT | ATOM
ATOM := IDENT ('.' IDENT)*
 | 'inventory.has'(STRING)
 | NUMBER | STRING | '(' EXPR ')'
 | ATOM ( '==' | '!=' | '>' | '<' | '>=' | '<=' ) ATOM
```

Identifiers resolve through attribute proxy into `flags`, `stats`, `reputation` dicts.

## Effects DSL

See Architecture doc; each string parsed by prefix.

## Reserved / Future Fields

| Location | Field | Purpose |
|----------|-------|---------|
| scene | meta | arbitrary metadata blob |
| choice | weight | random selection weighting |
| choice | cooldown_ms | re-display delay after use (looping scenes) |

## Example Scene

```json
{
 "id": "junction",
 "text": "The passage splits. Left air is cold. Right smells of moss.",
 "choices": [
  {"id": "left_path", "label": "Go left (cold)", "target": "ice_chamber", "conditions": ["flag.hasTorch"]},
  {"id": "right_path", "label": "Go right (moss)", "target": "moss_room"},
  {"id": "feel_way", "label": "Feel your way left in darkness", "target": "pit_fall", "conditions": ["not flag.hasTorch"], "type": "hidden"}
 ]
}
```

---
Update this doc when introducing new fields; add them as optional with defaults first.

### Timed Choices

When `type` is `timed` a choice may specify:

- `timeout_ms` (milliseconds until expiration)
- `default` (auto-select when it expires)
Expired non-default timed choices vanish; timers reset on each scene enter.
