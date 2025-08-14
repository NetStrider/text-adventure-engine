import os
import sys

# Ensure the project's src directory is on sys.path so tests can import engine
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.engine import load_default_engine


def test_timed_auto_selects_default():
    # Use a fake time function we can control
    t = {'now': 1.0}

    def time_func():
        return t['now']

    eng = load_default_engine(
        'stories/timed_demo.json', 'timed_intro', time_func=time_func
    )
    # initial timers set; nothing expired
    assert eng.process_timeouts() is None
    # advance time beyond timeout
    t['now'] += 1.0
    choice_id = eng.process_timeouts()
    assert choice_id == 'wait_it_out'
    # After auto-selection, engine should be in timed_result and ended
    assert eng.state.scene_id == 'timed_result'
    assert eng.state.ended is True
    assert eng.state.ending_code == 'TIMED_END'


def test_timed_manual_choice_before_timeout():
    t = {'now': 1.0}

    def time_func():
        return t['now']

    eng = load_default_engine(
        'stories/timed_demo.json', 'timed_intro', time_func=time_func
    )
    # Player chooses dash before timeout
    eng.choose('dash_for_it')
    assert eng.state.scene_id == 'timed_result'
    assert eng.state.ending_code == 'TIMED_END'
