from enum import Enum, auto


class TokenType(Enum):
    """
    Defines the role of the Token
    """

    # literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()

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
    VOID = auto()
    FUNCTION = auto()

    EOF = auto()
