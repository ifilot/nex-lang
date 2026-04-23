from .tokentype import TokenType

KEYWORDS = {
    "int": TokenType.INT,
    "bool": TokenType.BOOL,
    "str": TokenType.STR,
    "array": TokenType.ARRAY,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "void": TokenType.VOID,
    "fn": TokenType.FUNCTION,
    "return": TokenType.RETURN,
}
