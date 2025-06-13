import subprocess
import sys


def test_orchestrator_help():
    result = subprocess.run([sys.executable, "orchestrator.py", "--help"], capture_output=True)
    assert result.returncode == 0
    assert b"AutoML Orchestrator" in result.stdout
