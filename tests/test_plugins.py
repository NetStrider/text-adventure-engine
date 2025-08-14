import pytest

from src.engine import load_default_engine


class RecorderPlugin:
    def __init__(self):
        self.calls = []

    def on_game_start(self, engine, scene):
        self.calls.append(('start', scene.id))

    def on_scene_enter(self, engine, scene):
        self.calls.append(('enter', scene.id))

    def on_before_choices(self, engine, scene, choices):
        self.calls.append(('before_choices', scene.id, [c.id for c in choices]))

    def on_choice_selected(self, engine, choice):
        self.calls.append(('choice', choice.id))

    def on_state_change(self, engine, state):
        # record a shallow snapshot of scene_id to keep assertions simple
        self.calls.append(('state', state.scene_id))


def test_plugin_hooks_called(tmp_path):
    story = 'stories/relic_node_slice.json'
    plugin = RecorderPlugin()
    eng = load_default_engine(story, 'docking_breach', plugins=[plugin])

    # initial hooks should have fired during Engine init
    assert any(c[0] == 'start' for c in plugin.calls)
    assert any(c[0] == 'enter' for c in plugin.calls)

    plugin.calls.clear()
    # pick a visible choice from the starting scene
    choices = eng.list_choices()
    assert choices, 'expected at least one choice'
    first = choices[0]

    eng.choose(first.id)

    # after choosing, both choice and state hooks should have been recorded
    types = [c[0] for c in plugin.calls]
    assert 'choice' in types
    assert 'state' in types
