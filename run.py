from nex import *

program = Program((
    VarDecl("x", Literal(5)),
    Assign("x", Binary(Variable("x"), "+", Literal(1))),
    Print(Variable("x"))
))

pp = PrettyPrinter()
print(pp.print_program(program))

inptr = Interpreter()
inptr.run(program)