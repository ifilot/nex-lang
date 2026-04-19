from dataclasses import dataclass

from .expr import Expr

# Design choice: Statement nodes are immutable.
#
# Statements represent actions in the program (e.g. variable declaration,
# assignment, control flow) but are part of the program's static structure. Like
# expressions, they are treated as read-only data.
#
# Execution of a statement may modify the runtime environment, but never the AST
# itself. This enforces a clear separation between:
#   - program structure (AST, immutable)
#   - program state (environment, mutable)
#
# Any transformation of the program should create new nodes rather than mutating
# existing ones.


class Stmt:
    """
    Base class for statements. Statements are constructs that perform an action
    that potentially change the state of the program, without necessarily producing
    a value.
    """

    pass


@dataclass(frozen=True)
class VarDecl(Stmt):
    """
    A statement that declares a new variable in the current scope and
    initializes it with the value of the given expression.
    """

    name: str
    initializer: Expr


@dataclass(frozen=True)
class Assign(Stmt):
    """
    A statement that updates the value of an existing variable by assigning it
    the result of evaluating the given expression.
    """

    name: str
    expr: Expr


@dataclass(frozen=True)
class Print(Stmt):
    """
    Built-in function for printing expressions
    """

    expr: Expr


@dataclass(frozen=True)
class Block(Stmt):
    """
    Block statement, contains a set of statements.
    """

    statements: tuple[Stmt, ...]

    def __iter__(self):
        return iter(self.statements)


@dataclass(frozen=True)
class If(Stmt):
    """
    If statement. If the condition is true, execute then_branch, else execute
    the else_branch.
    """

    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None


@dataclass(frozen=True)
class For(Stmt):
    """
    For statement, keep looping over the body while condition is valid. Allow
    for initialization and iteration instructions.
    """

    init: Stmt | None
    condition: Expr
    iter: Stmt | None
    body: Stmt


@dataclass(frozen=True)
class While(Stmt):
    """
    While statement. While the condition evaluates to true, keep on executing
    the body statement.
    """

    condition: Expr
    body: Stmt


@dataclass(frozen=True)
class ExprStmt(Stmt):
    """
    Expression Statement. Evaluates the expression as if it is a statement.
    Effectively does nothing except consuming CPU cycles.
    """

    expr: Expr
