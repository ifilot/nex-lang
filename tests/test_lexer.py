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


def test_raises_on_unexpected_character():
    with pytest.raises(RuntimeError, match="Unexpected character"):
        lex("@")
