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
    PLUSEQ = auto()
    INC = auto()
    MINUS = auto()
    MINUSEQ = auto()
    DEC = auto()
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
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    DOT = auto()

    # keywords
    INT = auto()
    BOOL = auto()
    STR = auto()
    ARRAY = auto()
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
