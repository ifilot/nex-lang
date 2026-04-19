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
    GT = auto()
    LTE = auto()
    GTE = auto()
    EQ = auto()
    EQQ = auto()
    NEQ = auto()
    PERCENT = auto()
    EXCLAMATION = auto()

    # punctuation
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    STRING = auto()

    # keywords
    INT = auto()
    BOOL = auto()
    STR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    PRINT = auto()
    TRUE = auto()
    FALSE = auto()

    EOF = auto()
