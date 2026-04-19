import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.repo_checks
def test_ascii_check_script_passes_for_repository():
    root = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        [sys.executable, "scripts/check_ascii.py"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
