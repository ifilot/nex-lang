from nex import *

expr1 = Literal(10)
expr2 = Unary("-", expr1)
expr3 = Unary("-", expr2)
expr4 = Binary(expr3, '+', expr3)
expr5 = Binary(
    Unary("-", Literal(5)),
    "+",
    Literal(3)
)

print(expr5)

inptr = Interpreter()
print(inptr.eval(expr5))