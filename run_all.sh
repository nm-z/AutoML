#!/bin/bash
# Run orchestrator with all engines for a 60-second smoke test
set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate default environment
source "$SCRIPT_DIR/activate-tpa.sh"

# Verify required packages before running
python - <<'EOF'
import importlib, sys
required = ["pandas", "numpy", "sklearn"]
missing = [m for m in required if importlib.util.find_spec(m) is None]
if missing:
    sys.exit(1)
EOF
if [ $? -ne 0 ]; then
  echo "Required Python packages are missing. Run './setup.sh' or 'pip install -r requirements.txt' before executing this script." >&2
  exit 1
fi

# Execute orchestrator with sample dataset
python "$SCRIPT_DIR/orchestrator.py" --all --time 60 \
  --data "$SCRIPT_DIR/DataSets/1/D1-Predictors.csv" \
  --target "$SCRIPT_DIR/DataSets/1/D1-Targets.csv" "$@"

