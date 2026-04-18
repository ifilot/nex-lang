from nex import *

with open("examples/hello.nex") as f:
    source = f.read()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token.type)
    
    parser = Parser(tokens)
    program = parser.parse()

    inptr = Interpreter()
    inptr.run(program)