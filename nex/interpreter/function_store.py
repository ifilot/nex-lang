from dataclasses import dataclass
from typing import Tuple

from .stmt import Block


@dataclass(frozen=True)
class Function:
    callee: str  # function name (callee)
    arity: int
    arguments: Tuple[Tuple[str, str], ...]
    body: Block
    return_type: str


class NexFunctionStoreError(Exception):
    def __init__(self, message: str):
        self.message = message


class FunctionStore:
    """
    Keeps track of all the functions that have been defined
    """

    def __init__(self):
        """
        Default initializer
        """
        self.functions = {}

    def declare_function(self, func: Function):
        if func.callee not in self.functions:
            self.functions[func.callee] = func
        else:
            raise NexFunctionStoreError(f"function `{func.callee}` is already defined")

    def lookup_function(self, callee: str):
        if callee in self.functions:
            return self.functions[callee]
        else:
            raise NexFunctionStoreError(f"undefined function `{callee}`")
