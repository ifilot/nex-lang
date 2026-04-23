from dataclasses import dataclass
from typing import Callable, Tuple

from .stmt import Block


@dataclass(frozen=True)
class Function:
    callee: str  # function name (callee)
    params: Tuple[Tuple[str, str], ...]
    return_type: str

    @property
    def param_types(self) -> Tuple[str, ...]:
        return tuple(param_type for param_type, _ in self.params)


@dataclass(frozen=True)
class BuiltinFunction(Function):
    handler: Callable[..., object]

    def call(self, argvalues: list[object]):
        """
        Call mechanism for builtin functions
        """
        return self.handler(*argvalues)


@dataclass(frozen=True)
class UserFunction(Function):
    body: Block
