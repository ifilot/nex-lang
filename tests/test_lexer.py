import pytest

from nex.lexer import Lexer
from nex.lexer.tokentype import TokenType


def lex(source: str):
    return Lexer(source).tokenize()


def token_types(source: str):
    return [token.type for token in lex(source)]


def test_lexes_keywords_and_punctuation():
    source = 'var x = 1; if (x < 10) { print("ok"); }'

    assert token_types(source) == [
        TokenType.VAR,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IF,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.LT,
        TokenType.NUMBER,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.PRINT,
        TokenType.LPAREN,
        TokenType.STRING,
        TokenType.RPAREN,
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.EOF,
    ]


def test_lexes_number_and_string_literals():
    tokens = lex('print("hello"); var n = 42;')

    assert tokens[2].literal == "hello"
    assert tokens[8].literal == 42


def test_lexes_arithmetic_operators():
    assert token_types("x = 1 + 2 * 3 / 4 - 5;") == [
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.STAR,
        TokenType.NUMBER,
        TokenType.SLASH,
        TokenType.NUMBER,
        TokenType.MINUS,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_tracks_line_and_column_numbers():
    tokens = lex('var x = 1;\nprint("hi");\nfoo = 42;')

    assert [(token.type, token.line, token.column) for token in tokens] == [
        (TokenType.VAR, 1, 3),
        (TokenType.IDENTIFIER, 1, 5),
        (TokenType.EQ, 1, 7),
        (TokenType.NUMBER, 1, 9),
        (TokenType.SEMICOLON, 1, 10),
        (TokenType.PRINT, 2, 5),
        (TokenType.LPAREN, 2, 6),
        (TokenType.STRING, 2, 10),
        (TokenType.RPAREN, 2, 11),
        (TokenType.SEMICOLON, 2, 12),
        (TokenType.IDENTIFIER, 3, 3),
        (TokenType.EQ, 3, 5),
        (TokenType.NUMBER, 3, 8),
        (TokenType.SEMICOLON, 3, 9),
        (TokenType.EOF, 3, 9),
    ]


def test_raises_on_unexpected_character():
    with pytest.raises(RuntimeError, match="Unexpected character: '@' at Line 1, Column 1"):
        lex("@")

    with pytest.raises(RuntimeError, match="Unexpected character: '@' at Line 2, Column 1"):
        lex("var x = 5;\n@")
