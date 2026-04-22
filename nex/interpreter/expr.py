from dataclasses import dataclass, field
from typing import Tuple

# Design choice: AST nodes (including expressions) are immutable.
#
# Expressions represent the syntactic structure of the program and are
# treated as read-only data. This prevents accidental mutation during
# interpretation and enforces a clear separation between:
#   - program structure (AST, immutable)
#   - program state (environment, mutable)
#
# Any transformation of the AST should produce new nodes rather than
# modifying existing ones.


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
    line: int | None = field(default=None, compare=False)
    column: int | None = field(default=None, compare=False)

    def __repr__(self):
        return f"{self.value}"


@dataclass(frozen=True)
class Unary(Expr):
    """
    An expression that applies a single operator to one sub-expression to
    produce a new value.
    """

    op: str
    expr: Expr
    line: int | None = field(default=None, compare=False)
    column: int | None = field(default=None, compare=False)

    def __repr__(self):
        return f"({self.op}{self.expr})"


@dataclass(frozen=True)
class Binary(Expr):
    """
    An expression that applies a binary operator to two sub-expressions to
    produce a new value.
    """

    left: Expr
    op: str
    right: Expr
    line: int | None = field(default=None, compare=False)
    column: int | None = field(default=None, compare=False)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


@dataclass(frozen=True)
class Variable(Expr):
    """
    An expression that refers to a variable by name and evaluates to the value
    currently bound to that name in the environment.
    """

    name: str
    line: int | None = field(default=None, compare=False)
    column: int | None = field(default=None, compare=False)

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class FuncCall(Expr):
    """
    A call to a function
    """

    callee: str
    arity: int
    arguments: Tuple[Expr, ...]
    line: int | None = field(default=None, compare=False)
    column: int | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Postfix(Expr):
    """
    An expression that applies a postfix operator to a sub-expression.
    """

    expr: Expr
    op: str
    line: int | None = field(default=None, compare=False)
    column: int | None = field(default=None, compare=False)

    def __repr__(self):
        return f"({self.expr}{self.op})"
