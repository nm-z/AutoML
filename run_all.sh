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

# Activate the default pyenv environment used by the project
if [[ "$(pyenv version-name)" != "automl-py311" ]]; then
    pyenv activate automl-py311
fi

# Basic dependency check so the orchestrator doesn't fail on import errors
if ! python - <<'EOF' >/dev/null 2>&1
import pandas, sklearn, tpot
EOF
then
    echo "Installing required Python packages..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

# Set the PYTHON_PATH to include the current directory so Python can find orchestrator.py
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the orchestrator script
python orchestrator.py --all

