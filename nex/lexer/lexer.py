from .tokentype import TokenType
from .token import Token
from .keywords import KEYWORDS

class Lexer:
    def __init__(self, source: str):
        """
        Assign a string to the object for tokenization
        """
        self.source = source
        self.pos = 0
        self.tokens = []
        self.line = 1
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
        return ch

    def _peek(self):
        """
        Peek ahead
        """
        if self._is_at_end():
            return '\0'
        return self.source[self.pos]
    
    def _scan_token(self):
        """
        Scan the token
        """
        c = self._advance()

        if c == '+':
            self._add_token(TokenType.PLUS, c)
        elif c == '-':
            self._add_token(TokenType.MINUS, c)
        elif c == '*':
            self._add_token(TokenType.STAR, c)
        elif c == '/':
            self._add_token(TokenType.SLASH, c)
        elif c == '<':
            self._add_token(TokenType.LT, c)
        elif c == '>':
            self._add_token(TokenType.GT, c)
        elif c == '=':
            self._add_token(TokenType.EQ, c)
        elif c == ';':
            self._add_token(TokenType.SEMICOLON, c)
        elif c == '(':
            self._add_token(TokenType.LPAREN, c)
        elif c == ')':
            self._add_token(TokenType.RPAREN, c)
        elif c == '{':
            self._add_token(TokenType.LBRACE, c)
        elif c == '}':
            self._add_token(TokenType.RBRACE, c)
        elif c == '"':
            self._string()
        elif c == '#':
            self._comment()
        elif c.isspace():
            if c == '\n':
                self.line += 1
                self.column = 0
        elif c.isdigit():
            self._number(c)
        elif c.isalpha():
            self._identifier(c)
        else:
            raise RuntimeError(f"Unexpected character: '{c}' at Line {self.line}, Column {self.column}")
    
    def _add_token(self, type: TokenType, lexeme:str, literal = None):
        """
        Helper function to add a token to the tokenlist. Automatically assigns
        line and column.
        """
        self.tokens.append(Token(type, lexeme, literal, self.line, self.column))

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
            raise RuntimeError("Unterminated string")
        
        self._advance()  # closing quote

        self._add_token(TokenType.STRING, value, value)

    def _identifier(self, first):
        """
        Capture identifier / keyword
        """
        ident = first
        while self._peek().isalnum():
            ident += self._advance()

        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        self._add_token(token_type, ident)
    
    def _comment(self):
        while self._peek() != '\n' and not self._is_at_end():
            self._advance()

        if not self._is_at_end():
            self._advance()  # newline character