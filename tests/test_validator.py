import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from engine import load_story  # type: ignore  # noqa: E402
from validator import validate  # type: ignore  # noqa: E402


def test_validator_clean_sample():
    scenes = load_story(str(ROOT / 'stories' / 'sample_story.json'))
    issues = validate(scenes, 'intro')
    assert issues == []
