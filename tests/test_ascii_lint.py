import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def load_check_ascii_module():
    root = Path(__file__).resolve().parent.parent
    path = root / "scripts" / "check_ascii.py"
    spec = importlib.util.spec_from_file_location("check_ascii", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def test_python_ascii_scan_detects_non_ascii_and_ignores_excluded_dirs(tmp_path):
    check_ascii = load_check_ascii_module()

    (tmp_path / "ok.py").write_text("print('ok')\n", encoding="ascii")
    (tmp_path / "bad.md").write_text("caf\u00e9\n", encoding="utf-8")
    ignored = tmp_path / "__pycache__"
    ignored.mkdir()
    (ignored / "ignored.py").write_text("pi = '\u03c0'\n", encoding="utf-8")

    assert check_ascii.find_non_ascii_files_python(tmp_path) == [Path("bad.md")]


def test_ascii_scan_falls_back_to_python_when_rg_is_unavailable(tmp_path, monkeypatch):
    check_ascii = load_check_ascii_module()

    (tmp_path / "bad.py").write_text("name = '\u00f1'\n", encoding="utf-8")

    monkeypatch.setattr(check_ascii.shutil, "which", lambda name: None)

    assert check_ascii.find_non_ascii_files(tmp_path) == [Path("bad.py")]


def test_rg_ascii_scan_detects_non_ascii_when_available(tmp_path):
    check_ascii = load_check_ascii_module()
    rg_executable = check_ascii.shutil.which("rg")

    if rg_executable is None:
        pytest.skip("rg is not available in this environment")

    (tmp_path / "ok.py").write_text("print('ok')\n", encoding="ascii")
    (tmp_path / "bad.nex").write_text('print("ol\u00e1");\n', encoding="utf-8")

    assert check_ascii.find_non_ascii_files_rg(tmp_path, rg_executable) == [
        Path("bad.nex")
    ]
