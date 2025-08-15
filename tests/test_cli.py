import sys
import subprocess
import os

PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(__file__))


def run_cli_with_input(args, input_text, timeout=5):
    proc = subprocess.run(
        [PY, '-m', 'src.cli'] + args,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=ROOT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout


def test_cli_wait_triggers_timed_choice():
    # Run timed demo and wait so the timed choice auto-selects
    rc, out = run_cli_with_input(['stories/timed_demo.json', 'timed_intro'], 'wait 600\nquit\n', timeout=10)
    assert rc == 0
    # The CLI prints the timed auto selection line when it occurs
    assert '[Timed auto]' in out or 'TIMED_END' in out


def test_cli_validate_reports_ok_or_issues():
    rc, out = run_cli_with_input(['stories/relic_node_slice.json', 'docking_breach'], 'validate\nquit\n')
    assert rc == 0
    assert 'Validation' in out


def test_cli_save_load_roundtrip(tmp_path):
    savefile = tmp_path / 'savegame.json'
    # Start CLI, make no moves, save and exit
    rc, out = run_cli_with_input(
        ['stories/relic_node_slice.json', 'docking_breach'],
        f'save {str(savefile)}\nquit\n',
    )
    assert rc == 0
    assert 'Saved to' in out

    # Start a fresh CLI and load the save
    rc2, out2 = run_cli_with_input(
        ['stories/relic_node_slice.json', 'docking_breach'],
        f'load {str(savefile)}\nquit\n',
    )
    assert rc2 == 0
    assert 'Loaded from' in out2
