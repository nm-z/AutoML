#!/usr/bin/env bash
# Run orchestrator with all engines for a 60-second smoke test
set -euo pipefail

# Load pyenv so that `pyenv activate` works even when the script is executed
# non-interactively.
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
if command -v pyenv >/dev/null; then
    eval "$(pyenv init -)"
    if command -v pyenv-virtualenv-init >/dev/null 2>&1 || pyenv commands | grep -q virtualenv-init; then
        eval "$(pyenv virtualenv-init -)"
    fi
else
    echo "pyenv not found; aborting" >&2
    exit 1
fi

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the environment
# Replace with the appropriate environment for your project
# source "${SCRIPT_DIR}/env-tpa/bin/activate" # Example for a virtual environment

# Set the PYTHON_PATH to include the current directory so Python can find orchestrator.py
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Run the orchestrator script
if ! python orchestrator.py --all; then
    echo "Smoke test failed. Check that dependencies are installed." >&2
    exit 1
fi

