from src.engine import load_default_engine


class DeltaRecorder:
    def __init__(self):
        self.delta = None

    def on_state_delta(self, engine, delta: dict):
        self.delta = delta


def test_state_delta_reports_stats_and_history():
    story = 'stories/timed_demo.json'
    recorder = DeltaRecorder()
    eng = load_default_engine(story, 'timed_intro', plugins=[recorder])

    choices = eng.list_choices()
    assert choices
    choice = choices[0]

    eng.choose(choice.id)

    assert recorder.delta is not None
    # timed_demo reduces stat.oxygen by 1 or 2 depending on choice
    assert 'stats' in recorder.delta or 'history_added' in recorder.delta
    if 'stats' in recorder.delta:
        assert 'oxygen' in recorder.delta['stats']
    if 'history_added' in recorder.delta:
        assert isinstance(recorder.delta['history_added'], list)
