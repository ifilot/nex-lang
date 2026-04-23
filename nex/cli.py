import re
import sys
from pathlib import Path
from time import perf_counter

from nex import Interpreter, Lexer, Parser, __version__
from nex.common import NexLexError, NexParseError, NexRuntimeError
from nex.pretty_printer import PrettyPrinter

try:
    from colorama import Fore, Style
    from colorama import init as colorama_init
except ImportError:  # pragma: no cover - exercised only when dependency is absent
    Fore = None
    Style = None
    colorama_init = None


def main(argv=None):
    """
    Run the Nex command-line interface and dispatch to the requested action.
    """
    from_sys_argv = argv is None
    argv = sys.argv[1:] if argv is None else argv
    prog_name = _detect_prog_name(from_sys_argv)
    commands = {"run", "tokens", "ast"}

    # Support both the explicit subcommand form (`nexlang run file.nex`) and the
    # shorthand default form (`nexlang file.nex`) for normal execution.
    if argv and argv[0] in commands:
        cli_parser = _build_parser(prog_name)
        args = cli_parser.parse_args(argv)
        command = args.command
        file = args.file
        show_times = getattr(args, "times", False)
        use_color = getattr(args, "color", False)
    else:
        cli_parser = _build_run_parser(prog_name)
        args = cli_parser.parse_args(argv)
        command = "run"
        file = args.file
        show_times = args.times
        use_color = args.color

    # Read the source once up front so the selected command can reuse it.
    source = _read_source(file)

    try:
        # Lexing is the first shared stage for every command.
        lex_start = perf_counter()
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        lex_duration = perf_counter() - lex_start
    except NexLexError as exc:
        print(f"lex error: {exc}", file=sys.stderr)
        return 1

    # The `tokens` command stops after lexing and prints the token table.
    if command == "tokens":
        print(_format_tokens(tokens))
        return 0

    try:
        # Parsing turns the token stream into the AST used by later stages.
        parse_start = perf_counter()
        parser = Parser(tokens)
        program = parser.parse()
        parse_duration = perf_counter() - parse_start
    except NexParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 1

    # The `ast` command stops after parsing and pretty-prints the AST.
    if command == "ast":
        print(PrettyPrinter().print_program(program))
        return 0

    try:
        # Normal execution continues into the interpreter once the AST is ready.
        interpret_start = perf_counter()
        interpreter = Interpreter()
        interpreter.run(program)
        interpret_duration = perf_counter() - interpret_start
    except NexRuntimeError as exc:
        print(f"runtime error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Timing output is opt-in so normal script output stays uncluttered.
    if show_times:
        print(
            _format_stage_timings(
                lex_duration=lex_duration,
                parse_duration=parse_duration,
                interpret_duration=interpret_duration,
                use_color=use_color,
            )
        )

    return 0


def _build_parser(prog_name):
    """
    Build the full CLI parser that includes the run, tokens, and ast commands.
    """
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
    run_parser.add_argument(
        "--times",
        action="store_true",
        help="Show lexer, parser, interpreter, and total execution times",
    )
    run_parser.add_argument(
        "-c",
        "--color",
        action="store_true",
        help="Colorize the execution timing output",
    )
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
    """
    Build the shorthand parser used when the user omits an explicit subcommand.
    """
    import argparse

    cli_parser = argparse.ArgumentParser(
        prog=prog_name, description="Run a Nex program"
    )
    cli_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    cli_parser.add_argument(
        "--times",
        action="store_true",
        help="Show lexer, parser, interpreter, and total execution times",
    )
    cli_parser.add_argument(
        "-c",
        "--color",
        action="store_true",
        help="Colorize the execution timing output",
    )
    cli_parser.add_argument("file", help="Source file")
    return cli_parser


def _read_source(path):
    """
    Read a source file from disk and return its contents as text.
    """
    with open(path, encoding="utf-8") as f:
        return f.read()


def _detect_prog_name(from_sys_argv):
    """
    Detect the program name shown in help and version output.
    """
    if from_sys_argv:
        candidate = Path(sys.argv[0]).name
        if candidate:
            return candidate
    return "nexlang"


def _format_tokens(tokens):
    """
    Format the token stream as an aligned four-column table.
    """
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


def _format_stage_timings(
    *, lex_duration, parse_duration, interpret_duration, use_color=False
):
    """
    Format the execution timings for the lexer, parser, interpreter, and total.
    """
    total_duration = lex_duration + parse_duration + interpret_duration
    # Keep the timing rows in display order so the summary reads top-to-bottom
    # like the real execution pipeline.
    rows = [
        ("Lexer", _format_duration_ms(lex_duration)),
        ("Parser", _format_duration_ms(parse_duration)),
        ("Interpreter", _format_duration_ms(interpret_duration)),
        ("Total", _format_duration_ms(total_duration)),
    ]
    stage_width = max(len("Stage"), *(len(stage) for stage, _ in rows))
    time_width = max(len("Time"), *(len(duration) for _, duration in rows))
    style = _build_timing_style(use_color)
    lines = [
        "",
        style["title"]("Execution Times"),
        (
            f"{style['header']('Stage'):<{stage_width + _ansi_width(style['header'](''))}}  "
            f"{style['header']('Time'):>{time_width + _ansi_width(style['header'](''))}}"
        ),
        style["rule"](f"{'-' * stage_width}  {'-' * time_width}"),
    ]

    for stage, duration in rows:
        stage_text = style["stage"](stage)
        duration_text = style["time"](duration)
        lines.append(
            f"{stage_text:<{stage_width + _ansi_width(stage_text)}}  "
            f"{duration_text:>{time_width + _ansi_width(duration_text)}}"
        )

    return "\n".join(lines)


def _format_duration_ms(duration_seconds):
    """
    Convert a duration in seconds into a millisecond string for display.
    """
    return f"{duration_seconds * 1000:.3f} ms"


def _build_timing_style(use_color):
    """
    Build the styling functions used by the timing table output.
    """
    if not use_color or colorama_init is None:
        if not use_color:
            return {
                "title": _identity,
                "header": _identity,
                "rule": _identity,
                "stage": _identity,
                "time": _identity,
            }

        return {
            "title": lambda text: _ansi_wrap(text, "1;36"),
            "header": lambda text: _ansi_wrap(text, "1;34"),
            "rule": lambda text: _ansi_wrap(text, "34"),
            "stage": _ansi_color_stage_name,
            "time": lambda text: _ansi_wrap(text, "1;37"),
        }

    colorama_init(strip=False)
    return {
        "title": lambda text: f"{Style.BRIGHT}{Fore.CYAN}{text}{Style.RESET_ALL}",
        "header": lambda text: f"{Style.BRIGHT}{Fore.BLUE}{text}{Style.RESET_ALL}",
        "rule": lambda text: f"{Fore.BLUE}{text}{Style.RESET_ALL}",
        "stage": _color_stage_name,
        "time": lambda text: f"{Style.BRIGHT}{Fore.WHITE}{text}{Style.RESET_ALL}",
    }


def _ansi_color_stage_name(stage):
    """
    Color a timing stage name with ANSI escape codes.
    """
    colors = {
        "Lexer": "1;32",
        "Parser": "1;33",
        "Interpreter": "1;35",
        "Total": "1;36",
    }
    return _ansi_wrap(stage, colors.get(stage, "1;37"))


def _ansi_wrap(text, code):
    """
    Wrap text in a raw ANSI escape sequence.
    """
    return f"\033[{code}m{text}\033[0m"


def _color_stage_name(stage):
    """
    Color a timing stage name with colorama styles.
    """
    colors = {
        "Lexer": Fore.GREEN,
        "Parser": Fore.YELLOW,
        "Interpreter": Fore.MAGENTA,
        "Total": Fore.CYAN,
    }
    return f"{Style.BRIGHT}{colors.get(stage, Fore.WHITE)}{stage}{Style.RESET_ALL}"


def _identity(text):
    """
    Return text unchanged when color styling is disabled.
    """
    return text


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def _ansi_width(text):
    """
    Measure how many characters in a string belong to ANSI escape sequences.
    """
    plain_text = ANSI_ESCAPE_RE.sub("", text)
    return len(text) - len(plain_text)


if __name__ == "__main__":
    raise SystemExit(main())
