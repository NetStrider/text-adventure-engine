from __future__ import annotations
"""Core engine for the text adventure.

Features: models, story loading, expressions, effects, plugin hooks,
persistence.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Callable
import json
import os
import time


@dataclass
class Choice:
    id: str
    label: str
    target: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    type: str = "normal"  # normal|timed|hidden|gated
    timeout_ms: Optional[int] = None
    default: bool = False
    requirement_text: Optional[str] = None


@dataclass
class Scene:
    id: str
    text: str
    choices: List[Choice] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    # endings: list of objects with keys {code, category}
    endings: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class GameState:
    flags: Dict[str, bool] = field(default_factory=dict)
    stats: Dict[str, int] = field(default_factory=dict)
    inventory: Dict[str, int] = field(default_factory=dict)
    reputation: Dict[str, int] = field(default_factory=dict)
    scene_id: Optional[str] = None
    history: List[str] = field(default_factory=list)
    ended: bool = False
    ending_code: Optional[str] = None


class StoryError(Exception):
    pass


def load_story(path: str) -> Dict[str, Scene]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    scenes: Dict[str, Scene] = {}
    for raw in data.get('scenes', []):
        choices = [Choice(**c) for c in raw.get('choices', [])]
        scene = Scene(
            id=raw['id'],
            text=raw['text'],
            choices=choices,
            tags=raw.get('tags', []),
            endings=raw.get('endings', [])
        )
        if scene.id in scenes:
            raise StoryError(f'Duplicate scene id: {scene.id}')
        scenes[scene.id] = scene
    if not scenes:
        raise StoryError('No scenes loaded')
    return scenes


class ExpressionContext:
    def __init__(self, state: GameState):
        self.state = state

    def resolve(self, expr: str) -> Any:
        try:
            # Import locally to avoid package import timing issues
            # during test collection
            from src.expression import (
                safe_eval,
                make_local_map,
                )

            local = make_local_map(self.state)
            # Support legacy `inventory.has(x)` by rewriting to inv_has(x)
            expr = expr.replace('inventory.has', 'inv_has')
            return safe_eval(expr, local)
        except Exception:
            return False


def apply_effects(effects: List[str], state: GameState):
    for eff in effects:
        eff = eff.strip()
        if not eff:
            continue
        if eff.startswith('flag.'):
            try:
                name, rhs = eff.split('=', 1)
                name = name.strip()[5:]
                rhs = rhs.strip().lower()
                state.flags[name] = rhs in ('true', '1', 'yes')
            except ValueError:
                raise StoryError(f'Malformed flag effect: {eff}')
        elif eff.startswith('stat.'):
            body = eff[len('stat.'):]
            try:
                if '+=' in body:
                    name, num = body.split('+=', 1)
                    key = name.strip()
                    state.stats[key] = (
                        state.stats.get(key, 0) + int(num.strip())
                    )
                elif '-=' in body:
                    name, num = body.split('-=', 1)
                    key = name.strip()
                    state.stats[key] = (
                        state.stats.get(key, 0) - int(num.strip())
                    )
                elif '=' in body:
                    name, num = body.split('=', 1)
                    state.stats[name.strip()] = int(num.strip())
                else:
                    raise StoryError(f'Malformed stat effect: {eff}')
            except Exception as e:
                raise StoryError(f'Malformed stat effect: {eff}: {e}')
        elif eff.startswith('inv.add(') and eff.endswith(')'):
            item = eff[8:-1].strip().strip("'\"")
            state.inventory[item] = state.inventory.get(item, 0) + 1
        elif eff.startswith('inv.remove(') and eff.endswith(')'):
            item = eff[11:-1].strip().strip("'\"")
            if state.inventory.get(item, 0) > 0:
                state.inventory[item] -= 1
                if state.inventory[item] <= 0:
                    del state.inventory[item]
        elif eff.startswith('reputation.'):
            body = eff[len('reputation.'):]
            try:
                if '+=' in body:
                    name, num = body.split('+=', 1)
                    key = name.strip()
                    state.reputation[key] = (
                        state.reputation.get(key, 0) + int(num.strip())
                    )
                elif '-=' in body:
                    name, num = body.split('-=', 1)
                    key = name.strip()
                    state.reputation[key] = (
                        state.reputation.get(key, 0) - int(num.strip())
                    )
                elif '=' in body:
                    name, num = body.split('=', 1)
                    state.reputation[name.strip()] = int(num.strip())
                else:
                    raise StoryError(f'Malformed reputation effect: {eff}')
            except Exception as e:
                raise StoryError(f'Malformed reputation effect: {eff}: {e}')
        elif eff.startswith('end(') and eff.endswith(')'):
            code = eff[4:-1].strip().strip("'\"")
            state.ended = True
            state.ending_code = code
        else:
            raise StoryError(f'Unknown effect: {eff}')


class Engine:
    def __init__(self, scenes: Dict[str, Scene], start_id: str,
                 plugins: Optional[List[Any]] = None,
                 time_func: Optional[Callable[[], float]] = None):
        if start_id not in scenes:
            raise StoryError(f"Start scene '{start_id}' not found")
        self.scenes = scenes
        self.state = GameState(scene_id=start_id)
        self.expr_ctx = ExpressionContext(self.state)
        self.plugins = plugins or []

        # Timed choice machinery
        self._time_func = time_func or time.monotonic
        self._timers: Dict[str, float] = {}
        self._expired: set[str] = set()

        # Emit start + initial scene enter
        self._emit_hook('on_game_start', self.current_scene())
        self._emit_scene_enter(self.current_scene())
        # Initialize timers for the starting scene
        self._init_timers(self.current_scene())

    def current_scene(self) -> Scene:
        return self.scenes[self.state.scene_id]  # type: ignore

    def list_choices(self) -> List[Choice]:
        scene = self.current_scene()
        visible: List[Choice] = []
        for c in scene.choices:
            if c.type == 'timed' and c.id in self._expired:
                continue
            cond_pass = all(
                self.expr_ctx.resolve(expr) for expr in c.conditions
            )
            if c.type == 'hidden' and not cond_pass:
                continue
            if c.type == 'gated' and not cond_pass:
                visible.append(c)
                continue
            if cond_pass or not c.conditions:
                visible.append(c)
        # Plugin mutation hook (planned hook now active)
        for plugin in self.plugins:
            hook = getattr(plugin, 'on_before_choices', None)
            if callable(hook):
                try:
                    hook(self, scene, visible)  # in-place mutation allowed
                except Exception:
                    continue
        return visible

    def choose(self, choice_id: str) -> Scene:
        if self.state.ended:
            raise StoryError('Game already ended')
        scene = self.current_scene()
        choice = next((c for c in scene.choices if c.id == choice_id), None)
        if not choice:
            raise StoryError(f"Choice '{choice_id}' not in scene '{scene.id}'")
        if choice.type == 'gated' and not all(
            self.expr_ctx.resolve(e) for e in choice.conditions
        ):
            raise StoryError('Requirements not met')
        if choice.type == 'hidden' and not all(
            self.expr_ctx.resolve(e) for e in choice.conditions
        ):
            raise StoryError('Hidden choice not available')
        # Plugin hook: choice selected (before effects/state changes)
        self._emit_hook('on_choice_selected', choice)
        # Snapshot state for delta computation
        try:
            old_state = asdict(self.state)
        except Exception:
            old_state = {}
        # Apply effects to the state
        apply_effects(choice.effects, self.state)
        # Plugin hook: after effects applied to the state
        self._emit_hook('on_choice_effects_applied', choice, self.state)
    # Plugin hook: state changed by effects
    # (full state for backward compat)
        self._emit_hook('on_state_change', self.state)
    # Emit a compact delta describing what changed
    # (new hook: on_state_delta)
        try:
            new_state = asdict(self.state)
            delta: Dict[str, Any] = {}
            # keys to compare
            for key in ('flags', 'stats', 'inventory', 'reputation'):
                old_map = old_state.get(key, {}) or {}
                new_map = new_state.get(key, {}) or {}
                changes: Dict[str, Any] = {}
                # keys present in either
                for k in set(list(old_map.keys()) + list(new_map.keys())):
                    o = old_map.get(k)
                    n = new_map.get(k)
                    if o != n:
                        changes[k] = {'old': o, 'new': n}
                if changes:
                    delta[key] = changes
            # scene change
            if old_state.get('scene_id') != new_state.get('scene_id'):
                delta['scene_id'] = {
                    'old': old_state.get('scene_id'),
                    'new': new_state.get('scene_id'),
                }
            # history append (simple heuristic)
            old_hist = old_state.get('history', []) or []
            new_hist = new_state.get('history', []) or []
            if len(new_hist) > len(old_hist):
                delta['history_added'] = new_hist[len(old_hist):]
            # ended/ending_code
            if old_state.get('ended') != new_state.get('ended'):
                delta['ended'] = {
                    'old': old_state.get('ended'),
                    'new': new_state.get('ended'),
                }
            if old_state.get('ending_code') != new_state.get('ending_code'):
                delta['ending_code'] = {
                    'old': old_state.get('ending_code'),
                    'new': new_state.get('ending_code'),
                }
            if delta:
                self._emit_hook('on_state_delta', delta)
        except Exception:
            # don't allow plugin delta emission to break gameplay
            pass
        self.state.history.append(choice.id)
        if choice.target:
            if choice.target not in self.scenes:
                raise StoryError(f"Target scene '{choice.target}' missing")
            old_scene = scene
            self.state.scene_id = choice.target
        new_scene = self.current_scene()
        # Plugin hook: transition from old scene to new scene
        # (if any)
        try:
            _old = locals().get('old_scene')
            self._emit_hook('on_choice_transition', choice, _old, new_scene)
        except UnboundLocalError:
            # old_scene may not be defined if no transition occurred
            pass
        if new_scene.endings and not self.state.ended:
            self.state.ended = True
            self.state.ending_code = new_scene.endings[0].get('code')
        self._emit_scene_enter(new_scene)
        if self.state.ended:
            self._emit_hook('on_game_end', new_scene)
        else:
            self._init_timers(new_scene)
        return new_scene

    def _emit_hook(self, name: str, *args):
        for plugin in self.plugins:
            hook = getattr(plugin, name, None)
            if callable(hook):
                try:
                    hook(self, *args)
                except Exception:
                    continue

    def _emit_scene_enter(self, scene: Scene):
        self._emit_hook('on_scene_enter', scene)
    # Timed choice helpers

    def _init_timers(self, scene: Scene):
        self._timers.clear()
        self._expired.clear()
        now = self._time_func()
        for c in scene.choices:
            if c.type == 'timed' and c.timeout_ms:
                self._timers[c.id] = now + (c.timeout_ms / 1000.0)

    def process_timeouts(self) -> Optional[str]:
        if self.state.ended or not self._timers:
            return None
        now = self._time_func()
        expired = [cid for cid, dl in self._timers.items() if now >= dl]
        if not expired:
            return None
        scene = self.current_scene()
        default_choice: Optional[Choice] = None
        for cid in expired:
            ch = next((c for c in scene.choices if c.id == cid), None)
            if ch and ch.default:
                default_choice = ch
                break
        for cid in expired:
            self._expired.add(cid)
            self._timers.pop(cid, None)
        if default_choice:
            self.choose(default_choice.id)
            return default_choice.id
        return None

    def save(self, path: str):
        data = asdict(self.state)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(
                {'state': data, 'version': 1}, f, ensure_ascii=False, indent=2
            )

    def load(self, path: str):
        if not os.path.exists(path):
            raise StoryError(f'Save file not found: {path}')
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        state_data = payload.get('state')
        if not state_data:
            raise StoryError('Save file missing state')
        self.state = GameState(**state_data)
        self.expr_ctx = ExpressionContext(self.state)
        # Emit hooks similar to initialization
        try:
            self._emit_hook('on_state_change', self.state)
            scene = self.current_scene()
            self._emit_scene_enter(scene)
            if self.state.ended:
                self._emit_hook('on_game_end', scene)
            else:
                self._init_timers(scene)
        except Exception:
            pass

    def format_text(self, text: str) -> str:
        """Run text through format_output hooks (if any)."""
        out = text
        for plugin in self.plugins:
            hook = getattr(plugin, 'format_output', None)
            if callable(hook):
                try:
                    val = hook(self, out)
                    if isinstance(val, str):
                        out = val
                except Exception:
                    continue
        return out


def load_default_engine(
    story_path: str,
    start_id: str,
    plugins: Optional[List[Any]] = None,
    time_func: Optional[Callable[[], float]] = None,
) -> Engine:
    scenes = load_story(story_path)
    return Engine(scenes, start_id, plugins=plugins, time_func=time_func)


__all__ = [
    'Choice',
    'Scene',
    'GameState',
    'Engine',
    'StoryError',
    'load_story',
    'load_default_engine',
]
