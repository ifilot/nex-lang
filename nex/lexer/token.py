from dataclasses import dataclass

from .tokentype import TokenType


@dataclass(frozen=True)
class Token:
    """
    A token is a sequence of characters in the source code that the lexer groups
    together as a single, meaningful unit according to the language's lexical
    rules.
    """

    type: TokenType  # type of token
    lexeme: str  # the actual character sequence
    literal: object  # value associated with the token in case of a literal
    line: int  # which line number in the source code
    column: int  # which column number in the source code
