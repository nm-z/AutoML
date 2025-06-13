#!/bin/bash
# Run orchestrator on sample dataset using all engines

# Exit if any command fails
set -e

# Activate TPOT + AutoGluon environment
source ./activate-tpa.sh

# Execute orchestrator with all engines for a short run
python orchestrator.py --all --time 60 \
  --data DataSets/1/D1-Predictors.csv \
  --target DataSets/1/D1-Targets.csv

# Deactivate environment
deactivate

