import importlib.util
from importlib import metadata
from pathlib import Path

import pytest

from nex import __version__


def load_release_check_module():
    root = Path(__file__).resolve().parent.parent
    path = root / "scripts" / "check_release_version.py"
    spec = importlib.util.spec_from_file_location("check_release_version", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_release_check_reads_project_name_and_version():
    check_release_version = load_release_check_module()
    root = Path(__file__).resolve().parent.parent

    assert check_release_version.read_project_name(root) == "nex-lang"
    assert check_release_version.read_package_version(root) == "0.3.0"


def test_pyproject_has_pypi_display_metadata():
    check_release_version = load_release_check_module()
    root = Path(__file__).resolve().parent.parent
    pyproject = check_release_version.tomllib.loads(
        (root / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = pyproject["project"]

    assert project["description"]
    assert project["readme"] == "README.md"
    assert project["license"] == {"file": "LICENSE"}
    assert "Repository" in project["urls"]


def test_distribution_metadata_version_matches_runtime_version():
    try:
        distribution_version = metadata.version("nex-lang")
    except metadata.PackageNotFoundError:
        pytest.skip("nex-lang is not installed in this environment")

    assert distribution_version == __version__


def test_release_check_accepts_matching_tag():
    check_release_version = load_release_check_module()

    assert check_release_version.check_tag_matches_version("v0.3.0", "0.3.0") == []


def test_release_check_rejects_mismatched_tag():
    check_release_version = load_release_check_module()

    assert check_release_version.check_tag_matches_version("v0.2.0", "0.3.0") == [
        "Release tag must be v0.3.0, got v0.2.0."
    ]


def test_release_check_rejects_existing_local_tag(tmp_path, monkeypatch):
    check_release_version = load_release_check_module()

    monkeypatch.setattr(check_release_version, "local_tag_exists", lambda *args: True)

    assert check_release_version.check_local_tag_available(tmp_path, "v0.3.0") == [
        "Local Git tag v0.3.0 already exists."
    ]


def test_release_check_accepts_missing_local_tag(tmp_path, monkeypatch):
    check_release_version = load_release_check_module()

    monkeypatch.setattr(check_release_version, "local_tag_exists", lambda *args: False)

    assert check_release_version.check_local_tag_available(tmp_path, "v0.3.0") == []


def test_release_check_rejects_existing_repository_version(monkeypatch):
    check_release_version = load_release_check_module()

    monkeypatch.setattr(check_release_version, "version_exists", lambda *args: True)

    assert check_release_version.check_repository_version_available(
        "https://pypi.org/pypi",
        "nex-lang",
        "0.3.0",
    ) == ["nex-lang 0.3.0 already exists at https://pypi.org/pypi."]


def test_release_check_accepts_missing_repository_version(monkeypatch):
    check_release_version = load_release_check_module()

    monkeypatch.setattr(check_release_version, "version_exists", lambda *args: False)

    assert (
        check_release_version.check_repository_version_available(
            "https://pypi.org/pypi/",
            "nex-lang",
            "0.3.0",
        )
        == []
    )
