#!/usr/bin/env bash
# Download all wheels for offline installation

set -euo pipefail

WHEEL_DIR=${1:-wheels}

mkdir -p "$WHEEL_DIR"

# Determine which requirement files exist
REQUIREMENT_FILES=(requirements.txt)
if [ -f requirements-py311.txt ]; then
    REQUIREMENT_FILES+=(requirements-py311.txt)
fi
if [ -f requirements-py310.txt ]; then
    REQUIREMENT_FILES+=(requirements-py310.txt)
fi

for req in "${REQUIREMENT_FILES[@]}"; do
    echo "Downloading wheels for $req..."
    pip download --only-binary=:all: -r "$req" -d "$WHEEL_DIR"
    echo "Done downloading wheels for $req"
    echo ""
done

echo "All wheels downloaded to $WHEEL_DIR"
