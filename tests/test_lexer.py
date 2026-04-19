import pytest

from nex.lexer import Lexer
from nex.lexer.tokentype import TokenType


def lex(source: str):
    """
    Helper function to read string and tokenize it
    """
    return Lexer(source).tokenize()


def token_types(source: str):
    """
    Helper function to extract the token types from a list of tokens
    """
    return [token.type for token in lex(source)]


def test_lexes_keywords_and_punctuation():
    """
    Test that the lexer correctly identifies keywords and punctuation symbols.
    """
    source = (
        'int x = 1; bool flag = true; str msg = "ok"; if (x < 10) { print(msg); } false'
    )

    assert token_types(source) == [
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.BOOL,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.TRUE,
        TokenType.SEMICOLON,
        TokenType.STR,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.STRING,
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
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.FALSE,
        TokenType.EOF,
    ]


def test_lexes_number_and_string_literals():
    """
    Test that the lexer correctly identifies numbers (non-negative integers) and
    strings.
    """
    tokens = lex('print("hello"); int n = 42;')

    assert tokens[2].literal == "hello"
    assert tokens[8].literal == 42


def test_lexes_arithmetic_operators():
    """
    Test that the lexer correctly identifies arithmetic operators.
    """
    assert token_types("x = 1 + 2 * 3 / 4 % 5 - 6;") == [
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.STAR,
        TokenType.NUMBER,
        TokenType.SLASH,
        TokenType.NUMBER,
        TokenType.PERCENT,
        TokenType.NUMBER,
        TokenType.MINUS,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_lexes_two_character_comparison_operators():
    """
    Test that the lexer correctly identifies two-character comparison operators.
    """
    assert token_types("a <= b; c >= d; e == f; g != h;") == [
        TokenType.IDENTIFIER,
        TokenType.LTE,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.GTE,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQQ,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.NEQ,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_tracks_line_and_column_numbers():
    """
    Test that the lexer correctly keeps track of line and column numbers.
    """
    tokens = lex('int x = 1;\nprint("hi");\nfoo = 42;')

    assert [(token.type, token.line, token.column) for token in tokens] == [
        (TokenType.INT, 1, 3),
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


def test_skips_full_line_comments():
    """
    Test that the lexer ignores lines that start with '#'.
    """
    assert token_types('# full line comment\nprint("ok");') == [
        TokenType.PRINT,
        TokenType.LPAREN,
        TokenType.STRING,
        TokenType.RPAREN,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_skips_trailing_comments():
    """
    Test that the lexer ignores comments after valid code on the same line.
    """
    assert token_types("int x = 1; # trailing comment\nprint(x);") == [
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.PRINT,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_skips_comment_at_end_of_file():
    """
    Test that a final '#'-style comment without a trailing newline is ignored.
    """
    assert token_types("int x = 1; # trailing comment") == [
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_raises_on_unexpected_character():
    """
    Test that the lexer throws an error when finding unexpected characters.
    """
    with pytest.raises(
        RuntimeError, match="Unexpected character: '@' at Line 1, Column 1"
    ):
        lex("@")

    with pytest.raises(
        RuntimeError, match="Unexpected character: '@' at Line 2, Column 1"
    ):
        lex("int x = 5;\n@")
