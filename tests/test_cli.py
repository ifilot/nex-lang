from pathlib import Path

import pytest

from nex import __version__
from nex.cli import main


def run_cli_on_source(tmp_path: Path, source: str, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text(source, encoding="utf-8")

    exit_code = main([str(source_file)])
    captured = capsys.readouterr()
    return exit_code, captured


def test_version_flag_prints_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"nex {__version__}"


def test_cli_reports_lexer_errors_to_stderr_and_returns_nonzero(tmp_path, capsys):
    exit_code, captured = run_cli_on_source(tmp_path, "@", capsys)

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "lex error: line 1, column 1: unexpected character '@'\n"


def test_cli_reports_missing_semicolon_to_stderr_and_returns_nonzero(tmp_path, capsys):
    exit_code, captured = run_cli_on_source(tmp_path, "int x = 1", capsys)

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "parse error: line 1, column 9: expect ';'\n"


def test_cli_reports_missing_closing_paren_to_stderr_and_returns_nonzero(
    tmp_path, capsys
):
    exit_code, captured = run_cli_on_source(tmp_path, "print((1 + 2);", capsys)

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "parse error: line 1, column 14: expect ')'\n"


def test_cli_reports_undefined_variable_as_runtime_error(tmp_path, capsys):
    exit_code, captured = run_cli_on_source(tmp_path, "print(x);", capsys)

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "runtime error: line 1, column 7: undefined variable 'x'\n"


def test_cli_reports_type_mismatch_assignment_as_runtime_error(tmp_path, capsys):
    exit_code, captured = run_cli_on_source(
        tmp_path,
        """
        int x = 1;
        x = "hello";
        """,
        capsys,
    )

    assert exit_code == 1
    assert captured.out == ""
    assert (
        captured.err
        == "runtime error: line 3, column 13: cannot assign value of type str to variable 'x' of type int\n"
    )
