from .tokentype import TokenType

KEYWORDS = {
    "int": TokenType.INT,
    "bool": TokenType.BOOL,
    "str": TokenType.STR,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "print": TokenType.PRINT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "void": TokenType.VOID,
    "fn": TokenType.FUNCTION,
}
