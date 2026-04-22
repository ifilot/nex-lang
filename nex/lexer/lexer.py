from ..common import NexLexError
from .keywords import KEYWORDS
from .token import Token
from .tokentype import TokenType


class Lexer:
    """
    Reads source code as a stream of characters and converts it into a sequence
    of tokens.
    """

    def __init__(self, source: str):
        """
        Assign a string to the object for tokenization
        """
        self.source = source
        self.pos = 0
        self.tokens = []
        self.line = 1
        self.start_line = -1
        self.start_column = -1
        self.column = 0

    def tokenize(self):
        """
        Tokenize a string
        """
        while not self._is_at_end():
            self._scan_token()
        self._add_token(TokenType.EOF, "")
        return self.tokens

    def _is_at_end(self):
        """
        Assess whether we are at the end of string
        """
        return self.pos >= len(self.source)

    def _advance(self):
        """
        Return the current character and advance the pointer
        """
        ch = self.source[self.pos]
        self.pos += 1
        self.column += 1

        if ch == "\n":
            self.line += 1
            self.column = 0

        return ch

    def _peek(self):
        """
        Peek ahead
        """
        if self._is_at_end():
            return "\0"
        return self.source[self.pos]

    def _scan_token(self):
        """
        Scan the token
        """
        self.start_line = self.line
        self.start_column = self.column + 1
        c = self._advance()

        if c == "+":
            if self._peek() == "=":
                self._advance()
                self._add_token(TokenType.PLUSEQ, "+=")
            elif self._peek() == "+":
                self._advance()
                self._add_token(TokenType.INC, "++")
            else:
                self._add_token(TokenType.PLUS, c)
        elif c == "-":
            if self._peek() == ">":
                self._advance()
                self._add_token(TokenType.RETTYPE, "->")
            elif self._peek() == "=":
                self._advance()
                self._add_token(TokenType.MINUSEQ, "-=")
            elif self._peek() == "-":
                self._advance()
                self._add_token(TokenType.DEC, "--")
            else:
                self._add_token(TokenType.MINUS, c)
        elif c == "*":
            self._add_token(TokenType.STAR, c)
        elif c == "/":
            self._add_token(TokenType.SLASH, c)
        elif c == "%":
            self._add_token(TokenType.PERCENT, c)
        elif c == "|" and self._peek() == "|":
            self._advance()
            self._add_token(TokenType.OR, "||")
        elif c == "&" and self._peek() == "&":
            self._advance()
            self._add_token(TokenType.AND, "&&")
        elif c == "<":
            if self._peek() == "=":
                self._advance()
                self._add_token(TokenType.LTE, "<=")
            else:
                self._add_token(TokenType.LT, c)
        elif c == ">":
            if self._peek() == "=":
                self._advance()
                self._add_token(TokenType.GTE, ">=")
            else:
                self._add_token(TokenType.GT, c)
        elif c == "!":
            if self._peek() == "=":
                self._advance()
                self._add_token(TokenType.NEQ, "!=")
            else:
                self._add_token(TokenType.EXCLAMATION, c)
        elif c == "=":
            if self._peek() == "=":
                self._advance()
                self._add_token(TokenType.EQQ, "==")
            else:
                self._add_token(TokenType.EQ, c)
        elif c == ";":
            self._add_token(TokenType.SEMICOLON, c)
        elif c == "(":
            self._add_token(TokenType.LPAREN, c)
        elif c == ")":
            self._add_token(TokenType.RPAREN, c)
        elif c == "{":
            self._add_token(TokenType.LBRACE, c)
        elif c == "}":
            self._add_token(TokenType.RBRACE, c)
        elif c == ",":
            self._add_token(TokenType.COMMA, c)
        elif c == '"':
            self._string()
        elif c == "#":
            self._comment()
        elif c.isspace():
            pass
        elif c.isdigit():
            self._number(c)
        elif c.isalpha() or c == "_":
            self._identifier(c)
        else:
            raise NexLexError(
                f"unexpected character '{c}'",
                line=self.line,
                column=self.column,
            )

    def _add_token(self, type: TokenType, lexeme: str, literal=None):
        """
        Helper function to add a token to the tokenlist. Automatically assigns
        line and column.
        """
        self.tokens.append(
            Token(type, lexeme, literal, self.start_line, self.start_column)
        )

    def _number(self, first):
        """
        Capture number literal
        """
        num = first
        while self._peek().isdigit():
            num += self._advance()

        self._add_token(TokenType.NUMBER, num, int(num))

    def _string(self):
        """
        Capture string literal
        """
        value = ""
        while self._peek() != '"' and not self._is_at_end():
            value += self._advance()

        if self._is_at_end():
            raise NexLexError(
                "unterminated string",
                line=self.line,
                column=self.column,
            )

        self._advance()  # closing quote

        self._add_token(TokenType.STRING, value, value)

    def _identifier(self, first):
        """
        Capture identifier (sequence of characters used to name a variable,
        function, or other entity in a program) / keyword (reserved word in a
        programming language that has a predefined meaning and cannot be used as
        an identifier)

        Because true / false are reserved keywords, these are captured here as
        well and eventually become literals in the parser.
        """
        ident = first
        while self._peek().isalnum() or self._peek() == "_":
            ident += self._advance()

        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        self._add_token(token_type, ident)

    def _comment(self):
        """
        Capture a comment
        """
        while self._peek() != "\n" and not self._is_at_end():
            self._advance()

        if not self._is_at_end():
            self._advance()  # newline character
