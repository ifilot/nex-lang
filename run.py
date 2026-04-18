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
       Block([
           VarDecl("x", Literal(0)),
           Print(Variable("x")),
        ]),
       Block([Print(Literal("x < 10"))]),
    ),
    Print(Variable("x")),
))

pp = PrettyPrinter()
print(pp.print_program(program))

inptr = Interpreter()
inptr.run(program)