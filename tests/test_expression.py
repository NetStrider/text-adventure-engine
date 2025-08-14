import os
import sys

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.expression import safe_eval, make_local_map
from src.engine import GameState


def make_state():
    s = GameState()
    s.flags = {}
    s.stats = {}
    s.reputation = {}
    s.inventory = {}
    return s


def test_boolean_logic_and_not():
    s = make_state()
    s.flags['a'] = True
    s.flags['b'] = False
    local = make_local_map(s)
    assert safe_eval('flag.a and not flag.b', local) is True


def test_comparison_and_stats():
    s = make_state()
    s.stats['oxygen'] = 3
    local = make_local_map(s)
    assert safe_eval('stat.oxygen >= 2', local) is True
    assert safe_eval('stat.oxygen < 1', local) is False


def test_inv_has_and_inventory_attr():
    s = make_state()
    s.inventory['key'] = 1
    local = make_local_map(s)
    # direct inv_has call
    assert safe_eval('inv_has("key")', local) is True
    # engine normally rewrites inventory.has(...) to inv_has(...)
    expr = 'inventory.has("key")'.replace('inventory.has', 'inv_has')
    assert safe_eval(expr, local) is True


def test_attribute_missing_returns_false():
    s = make_state()
    local = make_local_map(s)
    assert safe_eval('flag.nope', local) is False


def test_arithmetic_and_comparison():
    s = make_state()
    s.stats['a'] = 3
    local = make_local_map(s)
    assert safe_eval('stat.a + 2 == 5', local) is True


def test_reject_unsafe_calls_and_imports():
    s = make_state()
    local = make_local_map(s)
    assert safe_eval("__import__('os').system('echo hi')", local) is False
    assert safe_eval('open("x")', local) is False

