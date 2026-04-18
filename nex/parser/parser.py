from typing import Tuple
from ..lexer.token import Token
from ..lexer.tokentype import TokenType
from ..interpreter.expr import *
from ..interpreter.stmt import *

class Parser:
    def __init__(self, tokens: Tuple[Token, ...]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self):
        statements = []
        while not self._is_at_end():
            statements.append(self._statement())
        return statements

    def _peek(self):
        return self.tokens[self.pos]

    def _previous(self):
        return self.tokens[self.pos - 1]

    def _is_at_end(self):
        return self._peek().type.name == "EOF"

    def _advance(self):
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _check(self, type_):
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _match(self, *types):
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, type_, message):
        if self._check(type_):
            return self._advance()
        raise RuntimeError(message)
    
    def _statement(self):
        if self._match(TokenType.VAR):
            return self._var_decl()
        elif self._match(TokenType.PRINT):
            return self._print_stmt()
        return self._expr_stmt()
    
    def _var_decl(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQ, "Expect '=' after name.")
        initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return VarDecl(name.lexeme, initializer)
    
    def _expr_stmt(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return ExprStmt(expr)
    
    def _print_stmt(self):
        self._consume(TokenType.LPAREN, "Expect '('.")
        primary = self._primary()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return Print(primary)

    def _expression(self):
        return self._term()

    def _term(self):
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().lexeme
            right = self._factor()
            expr = Binary(expr, op, right)

        return expr
    
    def _factor(self):
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous().lexeme
            right = self._unary()
            expr = Binary(expr, op, right)

        return expr
    
    def _unary(self):
        if self._match(TokenType.MINUS):
            op = self._previous().lexeme
            right = self._unary()
            return Unary(op, right)

        return self._primary()
    
    def _primary(self):
        if self._match(TokenType.NUMBER):
            return Literal(self._previous().literal)

        if self._match(TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous().lexeme)

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expect ')'.")
            return expr

        raise RuntimeError("Expect expression.")