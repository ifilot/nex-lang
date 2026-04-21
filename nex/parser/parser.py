from typing import Tuple

from ..common import NexParseError
from ..interpreter.expr import Binary, Literal, Unary, Variable
from ..interpreter.stmt import (
    Assign,
    Block,
    ExprStmt,
    For,
    FuncCall,
    FuncDecl,
    If,
    Print,
    Return,
    VarDecl,
    While,
)
from ..lexer.token import Token
from ..lexer.tokentype import TokenType

# -----------------------------------------------------------------------------
# Grammar (BNF)
# -----------------------------------------------------------------------------
# <program>           ::= <statement>* EOF
#
# <statement>         ::= <typed-decl>
#                       | <if-stmt>
#                       | <while-stmt>
#                       | <for-stmt>
#                       | <print-stmt>
#                       | <assignment-stmt>
#                       | <expr-stmt>
#
# <typed-decl>        ::= <typed-decl-core> ";"
#
# <typed-decl-core>   ::= <type> <identifier> "=" <expression>
#
# <type>              ::= "int" | "str" | "bool"
#
# <if-stmt>           ::= "if" "(" <expression> ")" <block> [ "else" <block> ]
#
# <while-stmt>        ::= "while" "(" <expression> ")" <block>
#
# <for-stmt>          ::= "for" "(" <for-init> ";" <expression> ";" <for-iter> ")" <block>
#
# <for-init>          ::= empty
#                       | <typed-decl-core>
#                       | <assignment-core>
#                       | <expression>
#
# <for-iter>          ::= empty
#                       | <assignment-core>
#                       | <expression>
#
# <block>             ::= "{" <statement>* "}"
#
# <assignment-stmt>   ::= <assignment-core> ";"
#
# <assignment-core>   ::= <identifier> "=" <expression>
#
# <print-stmt>        ::= "print" "(" <expression> ")" ";"
#
# <expr-stmt>         ::= <expression> ";"
#
# <expression>        ::= <comparison>
#
# <comparison>        ::= <term> [( "<" | ">" | "<=" | ">=" | "==" | "!=" ) <term>]
#
# <term>              ::= <factor> (("+" | "-") <factor>)*
#
# <factor>            ::= <unary> (("*" | "/" | "%") <unary>)*
#
# <unary>             ::= ("-" | "!") <unary>
#                       | <primary>
#
# <primary>           ::= <number>
#                       | <string>
#                       | "true"
#                       | "false"
#                       | <identifier>
#                       | "(" <expression> ")"


class Parser:
    """
    Converts the list of Tokens into an Abstract Syntax Tree (AST), the latter
    being represented by a list of statements.
    """

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
        if self._match(TokenType.INT):
            return self._int_decl()
        elif self._match(TokenType.STR):
            return self._str_decl()
        elif self._match(TokenType.BOOL):
            return self._bool_decl()
        elif self._match(TokenType.RETURN):
            return self._return_stmt()
        elif self._match(TokenType.IF):
            return self._if_stmt()
        elif self._match(TokenType.WHILE):
            return self._while_stmt()
        elif self._match(TokenType.FOR):
            return self._for_stmt()
        elif self._match(TokenType.FUNCTION):
            return self._function_decl()
        elif self._match(TokenType.PRINT):
            return self._print_stmt()
        elif self._check(TokenType.IDENTIFIER):
            if self.tokens[self.pos + 1].type == TokenType.EQ:
                return self._assign_stmt()
        return self._expr_stmt()

    def _int_decl(self):
        """
        Parse an integer declaration.
        """
        return self._typed_decl("int")

    def _str_decl(self):
        """
        Parse a string declaration.
        """
        return self._typed_decl("str")

    def _bool_decl(self):
        """
        Parse a boolean declaration.
        """
        return self._typed_decl("bool")

    def _return_stmt(self):
        """
        Parse a return statement
        """
        ret = self._previous()
        expr = None
        if not self._check(TokenType.SEMICOLON):
            expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return Return(
            expr,
            line=ret.line,
            column=ret.column,
        )

    def _typed_decl(self, declared_type, require_semicolon=True):
        """
        Parse a typed variable declaration after the type keyword was consumed.
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQ, "Expect '=' after name.")
        initializer = self._expression()
        if require_semicolon:
            self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return VarDecl(
            name.lexeme,
            initializer,
            declared_type,
            line=name.line,
            column=name.column,
        )

    def _function_decl(self):
        fn_token = self._previous()
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.LPAREN, "Expect '(")

        # consume parameters
        params = []
        while self._match(TokenType.INT, TokenType.STR, TokenType.BOOL):
            params.append(
                (
                    self._previous().lexeme,
                    self._consume(TokenType.IDENTIFIER, "Expect variable name").lexeme,
                )
            )
            if not self._check(TokenType.COMMA):
                break
            self._advance()

        self._consume(TokenType.RPAREN, "Expect ')'")
        self._consume(TokenType.RETTYPE, "Expect '->'")

        # grab return type
        if self._match(TokenType.INT, TokenType.STR, TokenType.BOOL, TokenType.VOID):
            return_type = self._previous()
        else:
            raise NexParseError(
                "Expected return type",
                line=self._peek().line,
                column=self._peek().column,
            )

        # grab function body
        body = self._block_stmt()

        return FuncDecl(
            name.lexeme,
            len(params),
            params,
            body,
            return_type,
            line=fn_token.line,
            column=fn_token.column,
        )

    def _function_call(self):
        callee = self._consume(TokenType.IDENTIFIER, "Expect function name.")
        self._consume(TokenType.LPAREN, "Expect '('")

        # consume function values
        arguments = []
        while not self._check(TokenType.RPAREN):
            arguments.append(self._expression())
            if self._check(TokenType.COMMA):
                self._advance()

        self._consume(TokenType.RPAREN, "Expect ')'")

        return FuncCall(
            callee.lexeme,  # callee name
            len(arguments),  # arity
            arguments,  # argument expressions
            line=callee.line,
            column=callee.column,
        )

    def _if_stmt(self):
        """
        Parse an if statement.
        """
        if_token = self._previous()
        self._consume(TokenType.LPAREN, "Expect '('.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        then_branch = self._block_stmt()
        if self._check(TokenType.ELSE):
            self._advance()
            else_branch = self._block_stmt()
        else:
            else_branch = None
        return If(
            condition,
            then_branch,
            else_branch,
            line=if_token.line,
            column=if_token.column,
        )

    def _while_stmt(self):
        """
        Parse a while statement
        """
        while_token = self._previous()
        self._consume(TokenType.LPAREN, "Expect '('.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        body = self._block_stmt()
        return While(condition, body, line=while_token.line, column=while_token.column)

    def _for_stmt(self):
        """
        Parse a for statement
        """
        for_token = self._previous()
        self._consume(TokenType.LPAREN, "Expect '('.")

        init = self._for_init_clause()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")

        # condition clause is mandatory
        condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';'.")

        iterclause = self._for_iter_clause()

        self._consume(TokenType.RPAREN, "Expect ')'.")

        # consume body
        body = self._block_stmt()
        return For(
            init,
            condition,
            iterclause,
            body,
            line=for_token.line,
            column=for_token.column,
        )

    def _for_init_clause(self):
        """
        Parse the initializer clause of a for statement.
        """
        if self._check(TokenType.SEMICOLON):
            return None

        if self._match(TokenType.INT):
            return self._typed_decl("int", require_semicolon=False)
        if self._match(TokenType.STR):
            return self._typed_decl("str", require_semicolon=False)
        if self._match(TokenType.BOOL):
            return self._typed_decl("bool", require_semicolon=False)
        if (
            self._check(TokenType.IDENTIFIER)
            and self.tokens[self.pos + 1].type == TokenType.EQ
        ):
            return self._assign_stmt(require_semicolon=False)
        return self._expr_stmt(require_semicolon=False)

    def _for_iter_clause(self):
        """
        Parse the iteration clause of a for statement.
        """
        if self._check(TokenType.RPAREN):
            return None

        if (
            self._check(TokenType.IDENTIFIER)
            and self.tokens[self.pos + 1].type == TokenType.EQ
        ):
            return self._assign_stmt(require_semicolon=False)
        return self._expr_stmt(require_semicolon=False)

    def _block_stmt(self):
        """
        Parse a block statement
        """
        statements = []
        self._consume(TokenType.LBRACE, "Expect '{'.")
        while not self._check(TokenType.RBRACE):
            statements.append(self._statement())
        self._consume(TokenType.RBRACE, "Expect '}'.")
        return Block(tuple(statements))

    def _assign_stmt(self, require_semicolon=True):
        """
        Parse an assignment statement (set a value to variable), optionally
        check that it ends with a semicolon.
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQ, "Expect '='.")
        expr = self._expression()
        if require_semicolon:
            self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return Assign(name.lexeme, expr, line=name.line, column=name.column)

    def _expr_stmt(self, require_semicolon=True):
        """
        Parse an expression statement, optionally check that it ends with a
        semicolon.
        """
        expr = self._expression()
        if require_semicolon:
            self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return ExprStmt(expr, line=expr.line, column=expr.column)

    def _print_stmt(self):
        """
        Parse a print statement
        """
        print_token = self._previous()
        self._consume(TokenType.LPAREN, "Expect '('.")
        value = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')'.")
        self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return Print(value, line=print_token.line, column=print_token.column)

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

        while self._match(
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
            TokenType.EQQ,
            TokenType.NEQ,
        ):
            operator = self._previous()
            op = operator.lexeme
            right = self._term()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

    def _term(self):
        """
        Parse +/- terms
        """
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            op = operator.lexeme
            right = self._factor()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

    def _factor(self):
        """
        Parse factors
        """
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            op = operator.lexeme
            right = self._unary()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

    def _unary(self):
        """
        Parse unary
        """
        if (
            self._check(TokenType.IDENTIFIER)
            and self.tokens[self.pos + 1].type == TokenType.LPAREN
        ):
            return self._function_call()

        while self._match(TokenType.MINUS, TokenType.EXCLAMATION):
            operator = self._previous()
            op = operator.lexeme
            right = self._unary()
            return Unary(op, right, line=operator.line, column=operator.column)

        return self._primary()

    def _primary(self):
        """
        Parse primary
        """
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return Literal(token.literal, line=token.line, column=token.column)

        if self._match(TokenType.STRING):
            token = self._previous()
            return Literal(token.literal, line=token.line, column=token.column)

        if self._match(TokenType.TRUE, TokenType.FALSE):
            token = self._previous()
            return Literal(
                True if token.type == TokenType.TRUE else False,
                line=token.line,
                column=token.column,
            )

        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return Variable(token.lexeme, line=token.line, column=token.column)

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expect ')'.")
            return expr

        raise NexParseError(
            "expected expression",
            line=self._peek().line,
            column=self._peek().column,
        )

    # --------------------------------------------------------------------------
    # HELPER FUNCTIONS
    # --------------------------------------------------------------------------

    def _peek(self):
        """
        Look ahead at next token without consuming it.
        """
        return self.tokens[self.pos]

    def _previous(self):
        """
        Look at previous token.
        """
        return self.tokens[self.pos - 1]

    def _is_at_end(self):
        """
        Check whether we are at the end of the list of Tokens.
        """
        return self._peek().type.name == "EOF"

    def _advance(self):
        """
        Consume the next Token and move the position forward.
        """
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _check(self, type_):
        """
        Compare the current Token to the expected type and return the result.
        """
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _match(self, *types):
        """
        Check if the upcoming Token matches one of the types given by *types. If
        so, consume it and return True.
        """
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, type_, message):
        """
        Consume a Token of the given type. If the Token is not of that type,
        raise a NexParseError.
        """
        if self._check(type_):
            return self._advance()
        raise NexParseError(
            message.lower().rstrip("."),
            line=self._peek().line,
            column=self._peek().column,
        )
