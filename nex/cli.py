import sys

from nex import Interpreter, Lexer, Parser, __version__
from nex.common import NexLexError, NexParseError, NexRuntimeError


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(prog="nex", description="Run my language")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("file", help="Source file")

    args = parser.parse_args(argv)

    with open(args.file) as f:
        source = f.read()

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except NexLexError as exc:
        print(f"lex error: {exc}", file=sys.stderr)
        return 1

    try:
        parser_ = Parser(tokens)
        program = parser_.parse()
    except NexParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 1

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


if __name__ == "__main__":
    raise SystemExit(main())
