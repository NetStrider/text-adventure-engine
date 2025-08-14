import sys
import subprocess
import os

PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(__file__))

proc = subprocess.run([PY, '-m', 'src.cli', 'stories/timed_demo.json', 'timed_intro'], input='wait 600\nquit\n', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
print('RC:', proc.returncode)
print('OUT:\n', proc.stdout)
