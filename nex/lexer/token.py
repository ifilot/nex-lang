from dataclasses import dataclass
from .tokentype import TokenType

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: object = None