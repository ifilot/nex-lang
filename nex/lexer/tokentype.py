from enum import Enum, auto

class TokenType(Enum):
    # literals
    NUMBER = auto()
    IDENTIFIER = auto()

    # operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LT = auto()
    EQ = auto()

    # punctuation
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    STRING = auto()

    # keywords
    VAR = auto()
    IF = auto()
    WHILE = auto()
    PRINT = auto()

    EOF = auto()