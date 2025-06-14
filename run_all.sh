#!/bin/bash
# Run orchestrator with all engines for a 60-second smoke test
set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Execute orchestrator with sample dataset using automl-py311
PYENV_VERSION=automl-py311 pyenv exec python "$SCRIPT_DIR/orchestrator.py" --all --time 60 \
  --data "$SCRIPT_DIR/DataSets/1/D1-Predictors.csv" \
  --target "$SCRIPT_DIR/DataSets/1/D1-Targets.csv" "$@"


