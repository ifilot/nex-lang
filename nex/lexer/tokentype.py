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
    OR = auto()
    AND = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    EQ = auto()
    EQQ = auto()
    NEQ = auto()
    PERCENT = auto()
    COMMA = auto()
    EXCLAMATION = auto()
    RETTYPE = auto()

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
    TRUE = auto()
    FALSE = auto()
    VOID = auto()
    FUNCTION = auto()
    RETURN = auto()

    EOF = auto()
