#!/usr/bin/env bash
# Run orchestrator with all engines for a 60-second smoke test on the
# bundled sample dataset.
set -euo pipefail

# Load pyenv so that `pyenv activate` works even when the script is executed
# non-interactively.
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
if command -v pyenv >/dev/null; then
    eval "$(pyenv init -)"
    if command -v pyenv-virtualenv-init >/dev/null; then
        eval "$(pyenv virtualenv-init -)"
    elif pyenv commands | grep -q virtualenv-init; then
        eval "$(pyenv virtualenv-init -)"
    else
        echo "pyenv-virtualenv plugin not found" >&2
    fi
else
    echo "pyenv not found; aborting" >&2
    exit 1
fi

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure the default environment exists and activate it
if pyenv versions --bare | grep -q "automl-py311"; then
    pyenv activate automl-py311
else
    echo "automl-py311 environment missing. Run ./setup.sh first." >&2
    exit 1
fi

# Activate the environment
# Replace with the appropriate environment for your project
# source "${SCRIPT_DIR}/env-tpa/bin/activate" # Example for a virtual environment

# Set the PYTHON_PATH to include the current directory so Python can find orchestrator.py
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Verify key packages are installed; install from requirements if missing
if ! python - <<'EOF'
import pandas, joblib, sklearn, rich
EOF
then
    echo "Installing missing Python packages..." >&2
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Run the orchestrator script on the sample dataset for 60 seconds
python orchestrator.py --all --time 60 \
  --data "$SCRIPT_DIR/DataSets/1/D1-Predictors.csv" \
  --target "$SCRIPT_DIR/DataSets/1/D1-Targets.csv" \
  --no-ensemble

pyenv deactivate

