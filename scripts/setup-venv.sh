#!/usr/bin/env bash
set -euo pipefail
VENV_DIR=.venv
python -m venv "$VENV_DIR"
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install -e .[dev]
cat <<'EOF'
Done. Activate with:
source .venv/bin/activate
EOF
