#!/usr/bin/env python
"""Baseline runner for Dataset 2.

This utility launches the orchestrator with Dataset 2 to establish
baseline performance across all AutoML engines once Goal 1 is achieved.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    orchestrator = repo_root / "orchestrator.py"
    data = repo_root / "DataSets" / "2" / "D2-Predictors.csv"
    target = repo_root / "DataSets" / "2" / "D2-Targets.csv"
    cmd = [
        sys.executable,
        str(orchestrator),
        "--all",
        "--data",
        str(data),
        "--target",
        str(target),
        "--time",
        "3600",
        "--tree",
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
