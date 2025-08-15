import sys
from pathlib import Path

# Ensure repo root is on sys.path so tests can import top-level 'src' during
# pre-commit's isolated pytest runs.
ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)
