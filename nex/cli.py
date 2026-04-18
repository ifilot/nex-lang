from nex import Lexer, Parser, Interpreter

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run my language")
    parser.add_argument("file", help="Source file")

    args = parser.parse_args()

    with open(args.file) as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser_ = Parser(tokens)
    program = parser_.parse()

    interpreter = Interpreter()
    interpreter.run(program)