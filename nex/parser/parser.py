from typing import Tuple
from ..lexer.token import Token
from ..lexer.tokentype import TokenType
from ..interpreter.expr import *
from ..interpreter.stmt import *

# -----------------------------------------------------------------------------
# Grammar (BNF)
# -----------------------------------------------------------------------------
# <program>           ::= <statement>* EOF
#
# <statement>         ::= <var-decl>
#                       | <if-stmt>
#                       | <while-stmt>
#                       | <print-stmt>
#                       | <assignment-stmt>
#                       | <expr-stmt>
#
# <var-decl>          ::= "var" <identifier> "=" <expression> ";"
#
# <if-stmt>           ::= "if" "(" <expression> ")" <block> [ "else" <block> ]
#
# <while-stmt>        ::= "while" "(" <expression> ")" <block>
#
# <block>             ::= "{" <statement>* "}"
#
# <assignment-stmt>   ::= <identifier> "=" <expression> ";"
#
# <print-stmt>        ::= "print" "(" <expression> ")" ";"
#
# <expr-stmt>         ::= <expression> ";"
#
# <expression>        ::= <comparison>
#
# <comparison>        ::= <term> [ "<" <term> ]
#
# <term>              ::= <factor> (("+" | "-") <factor>)*
#
# <factor>            ::= <unary> (("*" | "/") <unary>)*
#
# <unary>             ::= "-" <unary>
#                       | <primary>
#
# <primary>           ::= <number>
#                       | <string>
#                       | <identifier>
#                       | "(" <expression> ")"


class Parser:
    def __init__(self, tokens: Tuple[Token, ...]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self):
        """
        Parse a list of tokens to create a program
        """
        statements = []
        while not self._is_at_end():
            statements.append(self._statement())
        return statements
    
    # --------------------------------------------------------------------------
    # PARSER FUNCTIONS
    # --------------------------------------------------------------------------

    def _statement(self):
        """
        Parse a statement
        """
        if self._match(TokenType.VAR):
            return self._var_decl()
        elif self._match(TokenType.IF):
            return self._if_stmt()
        elif self._match(TokenType.WHILE):
            return self._while_stmt()
        elif self._match(TokenType.PRINT):
            return self._print_stmt()
        elif self._check(TokenType.IDENTIFIER) and self.tokens[self.pos + 1].type == TokenType.EQ:
            return self._assignment_stmt()
        return self._expr_stmt()
    
    def _var_decl(self):
        """
        Parse a variable declaration
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQ, "Expect '=' after name.")
        initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return VarDecl(name.lexeme, initializer)

    def _if_stmt(self):
        """
        Parse an if statement.
        """
        self._consume(TokenType.LPAREN, "Expect '('.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        then_branch = self._block_stmt()
        if self._peek().type == TokenType.ELSE:
            self._advance()
            else_branch = self._block_stmt()
        else:
            else_branch = None
        return If(condition, then_branch, else_branch)
    
    def _while_stmt(self):
        """
        Parse a while statement
        """
        self._consume(TokenType.LPAREN, "Expect '('.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        body = self._block_stmt()
        return While(condition, body)
    
    def _block_stmt(self):
        statements = []
        self._consume(TokenType.LBRACE, "Expect '{'.")
        while self._peek().type != TokenType.RBRACE:
            statements.append(self._statement())
        self._consume(TokenType.RBRACE, "Expect '}'.")
        return Block(tuple(statements))

    def _assignment_stmt(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQ, "Expect '='.")
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return Assign(name.lexeme, expr)

    def _expr_stmt(self):
        """
        Parse an expression statement, check that it ends with a semicolon
        """
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return ExprStmt(expr)
    
    def _print_stmt(self):
        """
        Parse a print statement
        """
        self._consume(TokenType.LPAREN, "Expect '('.")
        value = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return Print(value)

    def _expression(self):
        """
        Parse an expression
        """
        return self._comparison()

    def _comparison(self):
        """
        Parse comparison
        """
        expr = self._term()

        if self._match(TokenType.LT):
            op = self._previous().lexeme
            right = self._term()
            expr = Binary(expr, op, right)

        return expr

    def _term(self):
        """
        Parse +/- terms
        """
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().lexeme
            right = self._factor()
            expr = Binary(expr, op, right)

        return expr
    
    def _factor(self):
        """
        Parse factors
        """
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous().lexeme
            right = self._unary()
            expr = Binary(expr, op, right)

        return expr
    
    def _unary(self):
        """
        Parse unary
        """
        if self._match(TokenType.MINUS):
            op = self._previous().lexeme
            right = self._unary()
            return Unary(op, right)

        return self._primary()
    
    def _primary(self):
        """
        Parse primary
        """
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
    
    # --------------------------------------------------------------------------
    # HELPER FUNCTIONS
    # --------------------------------------------------------------------------

    def _peek(self):
        """
        Look ahead at next token without consuming it
        """
        return self.tokens[self.pos]

    def _previous(self):
        """
        Look at previous token
        """
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