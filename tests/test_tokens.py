import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tokens import extract_tokens  # type: ignore  # noqa: E402

def test_extract_tokens_order_and_uniqueness():
    text = 'You see a [[torch]] then a [[door]] and another [[torch]] later.'
    toks = extract_tokens(text)
    assert toks == ['torch', 'door']
