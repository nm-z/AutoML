#!/usr/bin/env bash
# Run orchestrator with all engines for a 60-second smoke test on all datasets
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

# Prefer automl-py311 but fall back to automl-py310
if pyenv versions --bare | grep -q "automl-py311"; then
    pyenv activate automl-py311
elif pyenv versions --bare | grep -q "automl-py310"; then
    echo "automl-py311 not found; falling back to automl-py310" >&2
    pyenv activate automl-py310
else
    echo "No suitable pyenv environment found" >&2
    exit 1
fi

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the environment
# Replace with the appropriate environment for your project
# source "${SCRIPT_DIR}/env-tpa/bin/activate" # Example for a virtual environment

# Set the PYTHON_PATH to include the current directory so Python can find orchestrator.py
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the orchestrator script for each dataset found in DataSets/
for ds_dir in "$SCRIPT_DIR"/DataSets/*; do
    [ -d "$ds_dir" ] || continue
    preds=$(find "$ds_dir" -maxdepth 1 -name '*Predictors.csv')
    target=$(find "$ds_dir" -maxdepth 1 -name '*Targets.csv')
    if [[ -f "$preds" && -f "$target" ]]; then
        echo "Running smoke test on $(basename "$ds_dir")"
        python orchestrator.py --all --data "$preds" --target "$target" --time "${TIME_LIMIT:-60}" --no-ensemble || {
            echo "Dataset $(basename "$ds_dir") failed" >&2
        }
    else
        echo "Skipping $(basename "$ds_dir") - predictors/targets not found" >&2
    fi
done

pyenv deactivate

