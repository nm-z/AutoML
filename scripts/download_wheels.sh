#!/bin/bash
# Download all required wheels for offline installation
# Usage: ./scripts/download_wheels.sh [wheel_dir]

set -e

WHEEL_DIR=${1:-wheels}
mkdir -p "$WHEEL_DIR"

pip download -d "$WHEEL_DIR" -r requirements.txt
if [ -f requirements-py311.txt ]; then
    pip download -d "$WHEEL_DIR" -r requirements-py311.txt
fi
if [ -f requirements-py310.txt ]; then
    pip download -d "$WHEEL_DIR" -r requirements-py310.txt || true
fi
