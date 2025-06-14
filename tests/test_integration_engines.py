import importlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "DataSets" / "1"

PREDICTORS = DATA_DIR / "D1-Predictors.csv"
TARGETS = DATA_DIR / "D1-Targets.csv"

pytestmark = pytest.mark.integration


def test_run_all_engines():
    pytest.importorskip("autosklearn")
    pytest.importorskip("tpot")
    pytest.importorskip("autogluon.tabular")

    cmd = [
        sys.executable,
        str(REPO_ROOT / "orchestrator.py"),
        "--all",
        "--data",
        str(PREDICTORS),
        "--target",
        str(TARGETS),
        "--time",
        "5",
        "--no-ensemble",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
