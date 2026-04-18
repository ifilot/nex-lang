from dataclasses import dataclass
from .stmt import Stmt

@dataclass(frozen=True)
class Program:
    """
    Program is essentially a list of statements
    """
    statements: tuple[Stmt, ...]

    def __iter__(self):
        return iter(self.statements)