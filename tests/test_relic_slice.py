
import os
import sys

# Ensure the project's src directory is importable as a package during tests
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.engine import load_default_engine


def test_relic_full_success():
    e = load_default_engine('stories/relic_node_slice.json', 'docking_breach')
    e.state.stats['oxygen'] = 5
    e.state.stats['stability'] = 0
    e.choose('seal_with_foam')
    assert e.state.stats['oxygen'] == 4
    e.choose('stabilize')
    assert e.state.stats['oxygen'] == 3
    assert e.state.stats['stability'] == 1
    assert 'inspect_creche' in [c.id for c in e.list_choices()]
    e.choose('inspect_creche')
    e.choose('decode_chant')
    assert e.state.stats['oxygen'] == 2
    e.choose('slot_shard')
    assert e.state.ended
    assert e.state.ending_code == 'FULL_RELAY'


def test_relic_abort():
    e = load_default_engine('stories/relic_node_slice.json', 'docking_breach')
    e.state.stats['oxygen'] = 3
    e.choose('rush_inside')
    assert e.state.stats['oxygen'] == 1
    e.choose('skip_protocol')
    e.choose('abort_here')
    assert e.state.ended
    assert e.state.ending_code in {'ABORT_EARLY', 'PARTIAL_DUMP'}
