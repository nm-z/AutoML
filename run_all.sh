#!/usr/bin/env bash
# Run orchestrator with all engines for a 60-second smoke test
set -euo pipefail

# Load pyenv so that `pyenv activate` works even when the script is executed
# non-interactively.
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
if command -v pyenv >/dev/null; then
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
else
    echo "pyenv not found; aborting" >&2
    exit 1
fi

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure required Python packages are installed
python - <<'EOF'
import importlib
import sys
required = ['pandas', 'numpy', 'sklearn', 'rich', 'joblib']
missing = [m for m in required if importlib.util.find_spec(m) is None]
sys.exit(len(missing))
EOF
if [ $? -ne 0 ]; then
    echo "Installing Python dependencies from requirements.txt"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Activate the environment if desired
# Replace with the appropriate environment for your project
# source "${SCRIPT_DIR}/env-tpa/bin/activate" # Example for a virtual environment

# Set the PYTHON_PATH to include the current directory so Python can find orchestrator.py
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the orchestrator script
python orchestrator.py --all

