from dataclasses import dataclass

class Expr:
    """
    Base class for expressions. Expressions are constructs that eventually evaluate
    to a value.
    """
    pass

@dataclass(frozen=True)
class Literal(Expr):
    """
    An expression that directly represents a fixed value in the source code.
    """
    value: object

    def __repr__(self):
        return f"{self.value}"

@dataclass
class Unary(Expr):
    """
    An expression that applies a single operator to one sub-expression to
    produce a new value.
    """
    op: str
    expr: Expr

    def __repr__(self):
        return f"({self.op}{self.expr})"
    
@dataclass
class Binary(Expr):
    """
    An expression that applies a binary operator to two sub-expressions to
    produce a new value.
    """
    left: Expr
    op: str
    right: Expr

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

@dataclass
class Variable(Expr):
    """
    An expression that refers to a variable by name and evaluates to the value
    currently bound to that name in the environment.
    """
    name: str