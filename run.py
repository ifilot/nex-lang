from nex import *

program = [
    VarDecl("x", Literal(5)),
    Assign("x", Binary(Variable("x"), "+", Literal(1))),
    Print(Variable("x"))
]

inptr = Interpreter()
inptr.run(program)