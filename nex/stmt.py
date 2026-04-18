from dataclasses import dataclass
from .expr import Expr

class Stmt: 
    """
    Base class for statements. Statements are constructs that perform an action
    that potentially change the state of the program, without necessarily producing
    a value.
    """
    pass

@dataclass
class VarDecl(Stmt):
    """
    A statement that declares a new variable in the current scope and
    initializes it with the value of the given expression.
    """
    name: str
    initializer: Expr

@dataclass
class Assign(Stmt):
    """
    A statement that updates the value of an existing variable by assigning it
    the result of evaluating the given expression.
    """
    name: str
    expr: Expr

@dataclass
class Print(Stmt):
    """
    Built-in function for printing expressions
    """
    expr: Expr