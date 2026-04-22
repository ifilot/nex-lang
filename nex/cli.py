import sys
from pathlib import Path

from nex import Interpreter, Lexer, Parser, __version__
from nex.common import NexLexError, NexParseError, NexRuntimeError
from nex.pretty_printer import PrettyPrinter


def main(argv=None):
    from_sys_argv = argv is None
    argv = sys.argv[1:] if argv is None else argv
    prog_name = _detect_prog_name(from_sys_argv)
    commands = {"run", "tokens", "ast"}

    if argv and argv[0] in commands:
        cli_parser = _build_parser(prog_name)
        args = cli_parser.parse_args(argv)
        command = args.command
        file = args.file
    else:
        cli_parser = _build_run_parser(prog_name)
        args = cli_parser.parse_args(argv)
        command = "run"
        file = args.file

    source = _read_source(file)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except NexLexError as exc:
        print(f"lex error: {exc}", file=sys.stderr)
        return 1

    if command == "tokens":
        print(_format_tokens(tokens))
        return 0

    try:
        parser = Parser(tokens)
        program = parser.parse()
    except NexParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 1

    if command == "ast":
        print(PrettyPrinter().print_program(program))
        return 0

    try:
        interpreter = Interpreter()
        interpreter.run(program)
    except NexRuntimeError as exc:
        print(f"runtime error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


def _build_parser(prog_name):
    import argparse

    cli_parser = argparse.ArgumentParser(
        prog=prog_name, description="Run Nex programs or inspect tokens and AST"
    )
    cli_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = cli_parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a Nex program")
    run_parser.add_argument("file", help="Source file")

    tokens_parser = subparsers.add_parser(
        "tokens", help="Print the token stream and stop after lexing"
    )
    tokens_parser.add_argument("file", help="Source file")

    ast_parser = subparsers.add_parser(
        "ast", help="Print the parsed AST and stop after parsing"
    )
    ast_parser.add_argument("file", help="Source file")

    return cli_parser


def _build_run_parser(prog_name):
    import argparse

    cli_parser = argparse.ArgumentParser(
        prog=prog_name, description="Run a Nex program"
    )
    cli_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    cli_parser.add_argument("file", help="Source file")
    return cli_parser


def _read_source(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _detect_prog_name(from_sys_argv):
    if from_sys_argv:
        candidate = Path(sys.argv[0]).name
        if candidate:
            return candidate
    return "nexlang"


def _format_tokens(tokens):
    location_width = max(
        len("LOCATION"), *(len(f"{token.line}:{token.column}") for token in tokens)
    )
    type_width = max(len("TYPE"), *(len(token.type.name) for token in tokens))
    lexeme_width = max(len("LEXEME"), *(len(repr(token.lexeme)) for token in tokens))
    literal_width = max(len("LITERAL"), *(len(repr(token.literal)) for token in tokens))
    header = (
        f"{'LOCATION':<{location_width}}  "
        f"{'TYPE':<{type_width}}  "
        f"{'LEXEME':<{lexeme_width}}  "
        f"{'LITERAL':<{literal_width}}"
    )
    lines = [
        header,
        f"{'-' * location_width}  "
        f"{'-' * type_width}  "
        f"{'-' * lexeme_width}  "
        f"{'-' * literal_width}",
    ]

    for token in tokens:
        location = f"{token.line}:{token.column}"
        lexeme = repr(token.lexeme)
        literal = repr(token.literal)
        lines.append(
            f"{location:<{location_width}}  "
            f"{token.type.name:<{type_width}}  "
            f"{lexeme:<{lexeme_width}}  "
            f"{literal:<{literal_width}}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
