# Plugin System

Plugins are lightweight Python objects whose optional methods are invoked at defined lifecycle points. They extend behavior (analytics, adaptive text, dynamic events) without modifying core engine code.

## Current Hooks

| Hook | Signature | When |
|------|-----------|------|
| on_game_start | (engine, scene) | After engine initialization; first scene resolved |
| on_scene_enter | (engine, scene) | After any transition (including start & load) |
| on_game_end | (engine, scene) | After entering a terminal scene / end() effect |
| on_before_choices | (engine, scene, choices:list[Choice]) | Just before presenting choices; may mutate list |
| on_choice_effects_applied | (engine, choice, state) | Immediately after choice effects are applied (before state_change) |
| on_choice_transition | (engine, choice, old_scene, new_scene) | After a choice triggers a scene transition |
| on_state_delta | (engine, delta:dict) | Compact delta describing granular state changes (flags/stats/inv/scene/history) |

## Near-Term Planned Hooks

| Hook | Signature | Purpose |
|------|-----------|---------|
| on_choice_selected | (engine, scene, choice) | Analytics, logging, achievements |
| on_state_change | (engine, delta:dict) | Observe granular state diffs |
| format_output | (engine, text:str) -> str | Transform narrative (colors, tokens) |

## Design Guidelines

- Idempotence: Hooks may be called after a load; avoid irreversible side effects without state guards.
- Fail Closed: Exceptions are caught and ignored so gameplay continues.
- Pure Where Possible: side effects (I/O) only when essential.

## Example

```python
class LoggingPlugin:
 def on_scene_enter(self, engine, scene):
  print(f"[SCENE] {scene.id}")

 def on_before_choices(self, engine, scene, choices):
  # Example: sort choices alphabetically by label
  choices.sort(key=lambda c: c.label)

 def on_game_end(self, engine, scene):
  print(f"[END] code={engine.state.ending_code}")
```

Register:

```python
from src.engine import load_default_engine
engine = load_default_engine('stories/relic_node_slice.json', 'docking_breach', plugins=[LoggingPlugin()])
```

## Safety & Future

Update this document when adding/removing hooks.

### Example: format_output plugin

The `format_output` hook lets plugins transform narrative text before it's
printed by the CLI or other front-ends. A common use is to highlight tokens
(`[[token]]`) or apply simple ANSI colorization for terminal output.

```python
from src.tokens import extract_tokens

class TokenHighlighter:
 def format_output(self, engine, text: str) -> str:
  # naive example: wrap known tokens with ** for emphasis
  for tok in extract_tokens(text):
   text = text.replace(f"[[{tok}]]", f"**{tok}**")
  return text

# Register the plugin when creating the engine
engine = load_default_engine(
 'stories/relic_node_slice.json',
 'docking_breach',
 plugins=[TokenHighlighter()],
)

### Example: ANSI token highlighter

For terminal UIs, an ANSI colorizer makes tokens stand out. This plugin
wraps tokens with ANSI escape sequences for bold/green output.

```python
from src.tokens import extract_tokens

class AnsiTokenHighlighter:
 GREEN_BOLD = '\u001b[1;32m'
 RESET = '\u001b[0m'

 def format_output(self, engine, text: str) -> str:
  for tok in extract_tokens(text):
   styled = f"{self.GREEN_BOLD}{tok}{self.RESET}"
   text = text.replace(f"[[{tok}]]", styled)
  return text

# register:
engine = load_default_engine(
 'stories/relic_node_slice.json',
 'docking_breach',
 plugins=[AnsiTokenHighlighter()],
)
```python
