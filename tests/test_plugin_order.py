from src.engine import load_default_engine


class OrderRecorder:
    def __init__(self):
        self.calls = []

    def on_choice_selected(self, engine, choice):
        self.calls.append('on_choice_selected')

    def on_choice_effects_applied(self, engine, choice, state):
        self.calls.append('on_choice_effects_applied')

    def on_state_change(self, engine, state):
        self.calls.append('on_state_change')

    def on_choice_transition(self, engine, choice, old_scene, new_scene):
        self.calls.append('on_choice_transition')


def test_plugin_hook_order(tmp_path):
    # timed_demo has a choice that transitions scenes
    story = 'stories/timed_demo.json'
    recorder = OrderRecorder()
    eng = load_default_engine(story, 'timed_intro', plugins=[recorder])

    choices = eng.list_choices()
    assert choices, 'expected at least one choice'
    choice = choices[0]

    # choose and assert ordering of hooks
    eng.choose(choice.id)

    # expected order:
    # on_choice_selected -> on_choice_effects_applied
    # -> on_state_change -> on_choice_transition
    assert recorder.calls[0] == 'on_choice_selected'
    assert recorder.calls[1] == 'on_choice_effects_applied'
    assert recorder.calls[2] == 'on_state_change'
    assert recorder.calls[3] == 'on_choice_transition'
