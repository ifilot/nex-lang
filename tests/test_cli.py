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
    assert capsys.readouterr().out.strip() == f"nexlang {__version__}"


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
    assert captured.err == "runtime error: line 1, column 7: undefined variable `x`\n"


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
        == "runtime error: line 3, column 13: cannot assign value of type str to variable `x` of type int\n"
    )


def test_cli_reports_builtin_input_failures_as_runtime_errors(
    tmp_path, capsys, monkeypatch
):
    def raise_eof():
        raise EOFError("EOF when reading a line")

    monkeypatch.setattr("builtins.input", raise_eof)

    exit_code, captured = run_cli_on_source(tmp_path, "input();", capsys)

    assert exit_code == 1
    assert captured.out == ""
    assert (
        captured.err
        == "runtime error: line 1, column 1: builtin function `input` failed: EOF when reading a line\n"
    )


def test_cli_tokens_command_prints_tokens_and_stops_before_parser(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text("int x = 1", encoding="utf-8")

    exit_code = main(["tokens", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "INT" in captured.out
    assert "IDENTIFIER" in captured.out
    assert "NUMBER" in captured.out
    assert "EOF" in captured.out
    assert captured.err == ""


def test_cli_tokens_command_formats_output_as_four_aligned_columns(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text('print("hi");', encoding="utf-8")

    exit_code = main(["tokens", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert (
        captured.out == "LOCATION  TYPE        LEXEME   LITERAL\n"
        "--------  ----------  -------  -------\n"
        "1:1       IDENTIFIER  'print'  None   \n"
        "1:6       LPAREN      '('      None   \n"
        "1:7       STRING      'hi'     'hi'   \n"
        "1:11      RPAREN      ')'      None   \n"
        "1:12      SEMICOLON   ';'      None   \n"
        "1:12      EOF         ''       None   \n"
    )


def test_cli_ast_command_prints_ast_and_stops_before_runtime(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text("print(x);", encoding="utf-8")

    exit_code = main(["ast", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert (
        captured.out
        == "Program\n`- ExprStmt\n   `- FuncCall [print]\n      `- Argument 1\n         `- Variable(x)\n"
    )


def test_cli_ast_command_reports_parse_errors(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text("int x = 1", encoding="utf-8")

    exit_code = main(["ast", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "parse error: line 1, column 9: expect ';'\n"


def test_cli_times_flag_prints_stage_timings_after_running_program(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text('print("hi");', encoding="utf-8")

    exit_code = main(["--times", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert captured.out.startswith("hi\n\nExecution Times\n")
    assert "Stage" in captured.out
    assert "Time" in captured.out
    assert "Lexer" in captured.out
    assert "Parser" in captured.out
    assert "Interpreter" in captured.out
    assert "Total" in captured.out


def test_cli_run_times_flag_prints_stage_timings_after_running_program(
    tmp_path, capsys
):
    source_file = tmp_path / "program.nex"
    source_file.write_text("print(1);", encoding="utf-8")

    exit_code = main(["run", "--times", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert captured.out.startswith("1\n\nExecution Times\n")


def test_cli_color_flag_prints_colored_stage_timings(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text("print(1);", encoding="utf-8")

    exit_code = main(["--times", "--color", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "\x1b[" in captured.out
    assert "Execution Times" in captured.out


def test_cli_short_color_flag_prints_colored_stage_timings(tmp_path, capsys):
    source_file = tmp_path / "program.nex"
    source_file.write_text("print(1);", encoding="utf-8")

    exit_code = main(["run", "--times", "-c", str(source_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "\x1b[" in captured.out
