from nex import __version__, Interpreter, Lexer, Parser

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

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser_ = Parser(tokens)
    program = parser_.parse()

    interpreter = Interpreter()
    interpreter.run(program)


if __name__ == "__main__":
    main()
