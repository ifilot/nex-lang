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

    def tokenize(self):
        """
        Tokenize a string
        """
        while not self._is_at_end():
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, ""))
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
            self.tokens.append(Token(TokenType.PLUS, c))
        elif c == '-':
            self.tokens.append(Token(TokenType.MINUS, c))
        elif c == '<':
            self.tokens.append(Token(TokenType.LT, c))
        elif c == '=':
            self.tokens.append(Token(TokenType.EQ, c))
        elif c == ';':
            self.tokens.append(Token(TokenType.SEMICOLON, c))
        elif c == '(':
            self.tokens.append(Token(TokenType.LPAREN, c))
        elif c == ')':
            self.tokens.append(Token(TokenType.RPAREN, c))
        elif c == '{':
            self.tokens.append(Token(TokenType.LBRACE, c))
        elif c == '}':
            self.tokens.append(Token(TokenType.RBRACE, c))
        elif c == '"':
            self._string()
        elif c.isspace():
            pass  # ignore whitespace
        elif c.isdigit():
            self._number(c)
        elif c.isalpha():
            self._identifier(c)
        else:
            raise RuntimeError(f"Unexpected character: {c}")
    
    def _number(self, first):
        """
        Capture number literal
        """
        num = first
        while self._peek().isdigit():
            num += self._advance()

        self.tokens.append(Token(TokenType.NUMBER, num, int(num)))
    
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

        self.tokens.append(Token(TokenType.STRING, value, value))

    def _identifier(self, first):
        """
        Capture identifier / keyword
        """
        ident = first
        while self._peek().isalnum():
            ident += self._advance()

        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, ident))