import subprocess
import sys
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "quickstart.py"


def test_quickstart_example_runs_and_prints_expected():
    result = subprocess.run(
        [sys.executable, str(EXAMPLE)],
        capture_output=True,
        text=True,
        check=True,
    )
    out = result.stdout
    assert "code: A8F3-K2P9" in out
    assert "link domain: example.com" in out
    assert "link path: /auth/magic" in out
    assert "token: real-token-123" in out
