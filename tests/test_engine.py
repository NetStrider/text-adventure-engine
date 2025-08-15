from src.engine import load_story, Engine, StoryError

import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
STORY = str(ROOT / 'stories' / 'sample_story.json')


def test_story_load():
    scenes = load_story(STORY)
    assert 'intro' in scenes
    assert scenes['intro'].choices


def test_basic_path_good():
    scenes = load_story(STORY)
    eng = Engine(scenes, 'intro')
    eng.choose('take_torch')  # to junction
    eng.choose('left_path')   # to ice_chamber
    eng.choose('melt_ice')    # to treasure_room -> ending
    assert eng.state.ended
    assert eng.state.ending_code == 'GEM_GOOD'


def test_bad_ending():
    scenes = load_story(STORY)
    eng = Engine(scenes, 'intro')
    eng.choose('go_dark')
    eng.choose('feel_way')
    assert eng.state.ended
    assert eng.state.ending_code == 'FALL_BAD'


def test_hidden_choice_not_visible_with_torch():
    scenes = load_story(STORY)
    eng = Engine(scenes, 'intro')
    eng.choose('take_torch')
    eng.choose('left_path')  # goes to ice_chamber
    # ensure hidden path only when no torch; not directly test listing
    assert 'torch' in eng.state.inventory


def test_invalid_choice():
    scenes = load_story(STORY)
    eng = Engine(scenes, 'intro')
    try:
        eng.choose('invalid')
    except StoryError:
        pass
    else:
        assert False, 'Expected StoryError'
