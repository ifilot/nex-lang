import pytest

from nex.common import NexLexError
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
        TokenType.IDENTIFIER,
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


def test_lexes_compound_and_increment_operators():
    """
    Test that the lexer correctly identifies compound assignment and
    increment/decrement operators.
    """
    assert token_types("x += 1; y -= 2; i++; j--;") == [
        TokenType.IDENTIFIER,
        TokenType.PLUSEQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.MINUSEQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.INC,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.DEC,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_prefers_longer_plus_and_minus_tokens():
    """
    Test that the lexer prefers the longest valid token for + and - prefixes.
    """
    assert token_types("a+++b; c---d;") == [
        TokenType.IDENTIFIER,
        TokenType.INC,
        TokenType.PLUS,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.DEC,
        TokenType.MINUS,
        TokenType.IDENTIFIER,
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


def test_lexes_logical_operators():
    """
    Test that the lexer correctly identifies logical operators.
    """
    assert token_types("a && b; c || d;") == [
        TokenType.IDENTIFIER,
        TokenType.AND,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.OR,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_lexes_identifiers_with_leading_and_internal_underscores():
    """
    Test that identifiers may start with '_' and may contain '_' internally.
    """
    tokens = lex("int _name = 1; int with_internal_underscore = 2;")

    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "_name"
    assert tokens[6].type == TokenType.IDENTIFIER
    assert tokens[6].lexeme == "with_internal_underscore"


def test_tracks_line_and_column_numbers():
    """
    Test that the lexer correctly keeps track of line and column numbers.
    """
    tokens = lex('int x = 1;\nprint("hi");\nfoo = 42;')

    assert [(token.type, token.line, token.column) for token in tokens] == [
        (TokenType.INT, 1, 1),
        (TokenType.IDENTIFIER, 1, 5),
        (TokenType.EQ, 1, 7),
        (TokenType.NUMBER, 1, 9),
        (TokenType.SEMICOLON, 1, 10),
        (TokenType.IDENTIFIER, 2, 1),
        (TokenType.LPAREN, 2, 6),
        (TokenType.STRING, 2, 7),
        (TokenType.RPAREN, 2, 11),
        (TokenType.SEMICOLON, 2, 12),
        (TokenType.IDENTIFIER, 3, 1),
        (TokenType.EQ, 3, 5),
        (TokenType.NUMBER, 3, 7),
        (TokenType.SEMICOLON, 3, 9),
        (TokenType.EOF, 3, 9),
    ]


def test_tracks_line_and_column_numbers_for_new_two_character_operators():
    """
    Test that the lexer assigns the correct source location to new two-character
    operators.
    """
    tokens = lex("x += 1;\ny--;\nz -= 2;\nw++;")

    assert [(token.type, token.line, token.column) for token in tokens] == [
        (TokenType.IDENTIFIER, 1, 1),
        (TokenType.PLUSEQ, 1, 3),
        (TokenType.NUMBER, 1, 6),
        (TokenType.SEMICOLON, 1, 7),
        (TokenType.IDENTIFIER, 2, 1),
        (TokenType.DEC, 2, 2),
        (TokenType.SEMICOLON, 2, 4),
        (TokenType.IDENTIFIER, 3, 1),
        (TokenType.MINUSEQ, 3, 3),
        (TokenType.NUMBER, 3, 6),
        (TokenType.SEMICOLON, 3, 7),
        (TokenType.IDENTIFIER, 4, 1),
        (TokenType.INC, 4, 2),
        (TokenType.SEMICOLON, 4, 4),
        (TokenType.EOF, 4, 4),
    ]


def test_skips_full_line_comments():
    """
    Test that the lexer ignores lines that start with '#'.
    """
    assert token_types('# full line comment\nprint("ok");') == [
        TokenType.IDENTIFIER,
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
        TokenType.IDENTIFIER,
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
    with pytest.raises(NexLexError) as excinfo:
        lex("@")

    assert excinfo.value.message == "unexpected character '@'"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1

    with pytest.raises(NexLexError) as excinfo:
        lex("int x = 5;\n@")

    assert excinfo.value.message == "unexpected character '@'"
    assert excinfo.value.line == 2
    assert excinfo.value.column == 1


def test_raises_on_unterminated_string():
    """
    Test that the lexer throws a structured error for unterminated strings.
    """
    with pytest.raises(NexLexError) as excinfo:
        lex('print("hello)')

    assert excinfo.value.message == "unterminated string"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 13
