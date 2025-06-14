#!/usr/bin/env bash
# Stress and error tests for the AutoML orchestrator
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the default environment. Fall back to automl-py310 if automl-py311 does not exist.
if pyenv versions --bare | grep -q "automl-py311"; then
    pyenv activate automl-py311
elif pyenv versions --bare | grep -q "automl-py310"; then
    pyenv activate automl-py310
else
    echo "Neither automl-py311 nor automl-py310 environment exists." >&2
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# --------------------------
# Test 7: Multiple Dataset Testing
# --------------------------
for dataset in "$SCRIPT_DIR"/DataSets/*/; do
    echo "Testing dataset: $dataset"
    pred_file=$(find "$dataset" -name "*Predictors.csv" -o -name "*predictors.csv" | head -1)
    target_file=$(find "$dataset" -name "*Targets.csv" -o -name "*targets.csv" | head -1)
    if [[ -f "$pred_file" && -f "$target_file" ]]; then
        python orchestrator.py --data "$pred_file" --target "$target_file" --time 300 --all
    fi
done

# --------------------------
# Test 8: Error Handling Testing
# --------------------------
# Test with non-existent files
if python orchestrator.py --data nonexistent.csv --target nonexistent.csv --time 60 --all; then
    echo "Unexpected success for nonexistent file test" >&2
fi

# Test with a very short runtime on Dataset 1
python orchestrator.py \
    --data DataSets/1/D1-Predictors.csv \
    --target DataSets/1/D1-Targets.csv \
    --time 10 \
    --all

pyenv deactivate
