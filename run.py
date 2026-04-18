from nex import *

program = Program((
    VarDecl("x", Unary('-', Literal(5))),
    Assign("x", Binary(Variable("x"), "+", Literal(1))),
    Print(Variable("x")),
    While(Binary(Variable("x"), "<", Literal(10)), 
          Block([
              Print(Variable("x")),
              Assign("x", Binary(Variable("x"), "+", Literal(1)))
          ])),
    Print(Variable("x")),
    If(Binary(Variable("x"), "<", Literal(5)),
       Block([Print(Literal("x < 5"))]),
       Block([Print(Literal("x >= 5"))]),
    ),
    Print(Variable("x")),
    If(Binary(Variable("x"), ">=", Literal(10)),
       Block([Print(Literal("x >= 10"))]),
       Block([Print(Literal("x < 10"))]),
    ),
))

pp = PrettyPrinter()
print(pp.print_program(program))

inptr = Interpreter()
inptr.run(program)