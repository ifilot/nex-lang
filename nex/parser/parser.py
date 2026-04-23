from typing import Tuple

from ..common import NexParseError
from ..interpreter.expr import (
    Binary,
    FuncCall,
    Index,
    Literal,
    MethodCall,
    Postfix,
    Unary,
    Variable,
)
from ..interpreter.stmt import (
    ArrayDecl,
    Assign,
    Block,
    ExprStmt,
    For,
    FuncDecl,
    If,
    IndexAssign,
    Return,
    VarDecl,
    While,
)
from ..lexer.token import Token
from ..lexer.tokentype import TokenType

# -----------------------------------------------------------------------------
# Grammar (BNF-like)
# -----------------------------------------------------------------------------
# This grammar describes the parser's surface syntax. Some language rules are
# enforced separately as context-sensitive checks, such as:
# - `return` is only allowed inside function bodies
# - nested function declarations are rejected
#
# <program>           ::= <statement>* EOF
#
# <statement>         ::= <typed-decl>
#                       | <function-decl>
#                       | <return-stmt>
#                       | <if-stmt>
#                       | <while-stmt>
#                       | <for-stmt>
#                       | <block>
#                       | <assignment-stmt>
#                       | <expr-stmt>
#
# <typed-decl>        ::= <typed-decl-core> ";"
#
# <typed-decl-core>   ::= <scalar-typed-decl-core> | <array-decl-core>
#
# <scalar-typed-decl-core> ::= <scalar-type> <identifier> "=" <expression>
#
# <array-decl-core>   ::= <array-type> <identifier>
#
# <type>              ::= <scalar-type> | <array-type>
#
# <scalar-type>       ::= "int" | "str" | "bool"
#
# <array-type>        ::= "array" "<" ( "int" | "str" ) ">"
#
# <function-decl>     ::= "fn" <identifier> "(" [ <parameters> ] ")" "->" <return-type> <block>
#
# <parameters>        ::= <parameter> ("," <parameter>)*
#
# <parameter>         ::= <type> <identifier>
#
# <return-type>       ::= <type> | "void"
#
# <return-stmt>       ::= "return" [ <expression> ] ";"
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
# <assignment-core>   ::= <assignment-target> <assignment-op> <expression>
#
# <assignment-op>     ::= "=" | "+=" | "-=" | "*=" | "/=" | "^="
#
# <assignment-target> ::= <identifier> | <index-expr>
#
# <expr-stmt>         ::= <expression> ";"
#
# <expression>        ::= <logical-or>
#
# <logical-or>        ::= <logical-and> ( "||" <logical-and> )*
#
# <logical-and>       ::= <comparison> ( "&&" <comparison> )*
#
# <comparison>        ::= <term> (( "<" | ">" | "<=" | ">=" | "==" | "!=" ) <term>)*
#
# <term>              ::= <factor> (("+" | "-") <factor>)*
#
# <factor>            ::= <power> (("*" | "/" | "%") <power>)*
#
# <power>             ::= <unary> ["^" <power>]
#
# <unary>             ::= ("-" | "!") <unary>
#                       | <postfix>
#
# <postfix>           ::= <primary> ( <call-suffix> | <index-suffix> | <method-suffix> | <postfix-update> )*
#
# <call-suffix>       ::= "(" [ <arguments> ] ")"
# <index-suffix>      ::= "[" <expression> "]"
# <method-suffix>     ::= "." <identifier> "(" [ <arguments> ] ")"
# <postfix-update>    ::= "++" | "--"
#
# <primary>           ::= <number>
#                       | <string>
#                       | "true"
#                       | "false"
#                       | <identifier>
#                       | "(" <expression> ")"
#
# <arguments>         ::= <expression> ("," <expression>)*


class Parser:
    """
    Converts the list of Tokens into an Abstract Syntax Tree (AST), the latter
    being represented by a list of statements.
    """

    def __init__(self, tokens: Tuple[Token, ...]):
        self.tokens = tokens
        self.pos = 0
        self.function_depth = 0  # keep track whether we are parsing a function
        self.block_depth = 0  # keep track whether we are inside any block

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
        if self._starts_type():
            return self._typed_decl(self._parse_type())
        elif self._match(TokenType.FUNCTION):
            return self._function_decl()
        elif self._match(TokenType.RETURN):
            return self._return_stmt()
        elif self._match(TokenType.IF):
            return self._if_stmt()
        elif self._match(TokenType.WHILE):
            return self._while_stmt()
        elif self._match(TokenType.FOR):
            return self._for_stmt()
        elif self._check(TokenType.LBRACE):
            return self._block_stmt()
        else:
            assign_stmt = self._try_assign_stmt()
            if assign_stmt is not None:
                return assign_stmt
        return self._expr_stmt()

    def _typed_decl(self, declared_type, require_semicolon=True):
        """
        Parse a typed variable declaration after the type keyword was consumed.
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        if self._is_array_type(declared_type):
            if self._check(TokenType.EQ):
                raise NexParseError(
                    "array declarations must not have an initializer",
                    line=self._peek().line,
                    column=self._peek().column,
                )
            if require_semicolon:
                self._consume(TokenType.SEMICOLON, "Expect ';'.")
            return ArrayDecl(
                name.lexeme,
                declared_type,
                line=name.line,
                column=name.column,
            )

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
        """
        Parse a function declaration.
        """
        fn_token = self._previous()
        if self.function_depth > 0 or self.block_depth > 0:
            raise NexParseError(
                "nested functions are not allowed",
                line=fn_token.line,
                column=fn_token.column,
            )

        # increment function depth (can in principle never exceed 1, because
        # nested functions are not allowed)
        self.function_depth += 1

        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.LPAREN, "Expect '(")

        # consume parameters, check for duplicates
        param_types = []
        param_names = []
        while self._starts_type():
            paramtype = self._parse_type()
            paramname = self._consume(
                TokenType.IDENTIFIER, "Expect variable name"
            ).lexeme
            if paramname in param_names:
                raise NexParseError(
                    f"duplicate parameter `{paramname}` encountered",
                    line=self._previous().line,
                    column=self._previous().column,
                )

            param_types.append(paramtype)
            param_names.append(paramname)

            if not self._check(TokenType.COMMA):
                break
            self._advance()

        self._consume(TokenType.RPAREN, "Expect ')'")
        self._consume(TokenType.RETTYPE, "Expect '->'")

        try:
            # grab return type
            return_type = self._parse_type(allow_void=True)

            # grab function body
            body = self._block_stmt()
        finally:
            # decrement function depth even if parsing the body fails
            self.function_depth -= 1

        # assemble parameters
        params = [
            (paramtype, paramname)
            for paramtype, paramname in zip(param_types, param_names)
        ]

        return FuncDecl(
            name.lexeme,
            len(params),
            tuple(params),
            body,
            return_type,
            line=fn_token.line,
            column=fn_token.column,
        )

    def _return_stmt(self):
        """
        Parse a return statement
        """
        # return statements are not allowed at the global level
        if self.function_depth < 1:
            raise NexParseError(
                "return statement are not allowed outside of function declarations",
                line=self._previous().line,
                column=self._previous().column,
            )

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

        if self._starts_type():
            return self._typed_decl(self._parse_type(), require_semicolon=False)
        assign_stmt = self._try_assign_stmt(require_semicolon=False)
        if assign_stmt is not None:
            return assign_stmt
        return self._expr_stmt(require_semicolon=False)

    def _for_iter_clause(self):
        """
        Parse the iteration clause of a for statement.
        """
        if self._check(TokenType.RPAREN):
            return None

        assign_stmt = self._try_assign_stmt(require_semicolon=False)
        if assign_stmt is not None:
            return assign_stmt
        return self._expr_stmt(require_semicolon=False)

    def _block_stmt(self):
        """
        Parse a block statement
        """
        statements = []
        self._consume(TokenType.LBRACE, "Expect '{'.")
        self.block_depth += 1
        try:
            while not self._check(TokenType.RBRACE) and not self._is_at_end():
                statements.append(self._statement())
            self._consume(TokenType.RBRACE, "Expect '}'.")
        finally:
            self.block_depth -= 1
        return Block(tuple(statements))

    def _assign_stmt(self, require_semicolon=True):
        """
        Parse an assignment statement (set a value to variable), optionally
        check that it ends with a semicolon.
        """
        target = self._assignment_target()
        operator = self._assignment_operator()
        expr = self._expression()
        if require_semicolon:
            self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return self._build_assignment_stmt(target, operator, expr)

    def _expr_stmt(self, require_semicolon=True):
        """
        Parse an expression statement, optionally check that it ends with a
        semicolon.
        """
        expr = self._expression()
        if require_semicolon:
            self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return ExprStmt(expr, line=expr.line, column=expr.column)

    def _expression(self):
        """
        Parse an expression
        """
        return self._logical_or()

    def _logical_or(self):
        """
        Parse logical OR expressions.
        """
        expr = self._logical_and()

        while self._match(TokenType.OR):
            operator = self._previous()
            op = operator.lexeme
            right = self._logical_and()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

    def _logical_and(self):
        """
        Parse logical AND expressions.
        """
        expr = self._comparison()

        while self._match(TokenType.AND):
            operator = self._previous()
            op = operator.lexeme
            right = self._comparison()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

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
        expr = self._power()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            op = operator.lexeme
            right = self._power()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

    def _power(self):
        """
        Parse exponentiation. This operator binds more tightly than
        multiplication and associates to the right.
        """
        expr = self._unary()

        if self._match(TokenType.CARET):
            operator = self._previous()
            op = operator.lexeme
            right = self._power()
            expr = Binary(expr, op, right, line=operator.line, column=operator.column)

        return expr

    def _unary(self):
        """
        Parse unary
        """
        while self._match(TokenType.MINUS, TokenType.EXCLAMATION):
            operator = self._previous()
            op = operator.lexeme
            right = self._unary()
            return Unary(op, right, line=operator.line, column=operator.column)

        return self._postfix()

    def _postfix(self):
        """
        Parse postfix expressions. NEX currently supports function-call postfixes
        and postfix increment/decrement operators.
        """
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_function_call(expr)
                continue

            if self._match(TokenType.LBRACKET):
                expr = self._finish_index(expr)
                continue

            if self._match(TokenType.DOT):
                expr = self._finish_method_call(expr)
                continue

            if self._match(TokenType.INC, TokenType.DEC):
                expr = self._finish_postfix_update(expr)
                continue

            break

        return expr

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

    def _starts_type(self, allow_void=False):
        """
        Check whether the current token begins a type annotation.
        """
        type_tokens = (TokenType.INT, TokenType.STR, TokenType.BOOL, TokenType.ARRAY)
        if allow_void:
            type_tokens += (TokenType.VOID,)
        return self._peek().type in type_tokens if not self._is_at_end() else False

    def _parse_type(self, allow_void=False):
        """
        Parse a type annotation and return its canonical string representation.
        """
        if self._match(TokenType.INT, TokenType.STR, TokenType.BOOL):
            return self._previous().lexeme

        if allow_void and self._match(TokenType.VOID):
            return self._previous().lexeme

        if self._match(TokenType.ARRAY):
            self._consume(TokenType.LT, "Expect '<' after 'array'.")

            if self._match(TokenType.INT, TokenType.STR):
                element_type = self._previous().lexeme
            elif self._match(TokenType.BOOL, TokenType.ARRAY, TokenType.VOID):
                raise NexParseError(
                    f"unsupported array element type `{self._previous().lexeme}`; expected int or str",
                    line=self._previous().line,
                    column=self._previous().column,
                )
            else:
                raise NexParseError(
                    "expect array element type",
                    line=self._peek().line,
                    column=self._peek().column,
                )

            self._consume(TokenType.GT, "Expect '>' after array element type.")
            return f"array<{element_type}>"

        if allow_void:
            message = "unexpected return type"
        else:
            message = "expect type"

        raise NexParseError(
            message,
            line=self._peek().line,
            column=self._peek().column,
        )

    def _is_array_type(self, declared_type: str) -> bool:
        return declared_type.startswith("array<")

    def _try_assign_stmt(self, require_semicolon=True):
        """
        Attempt to parse an assignment statement without committing on failure.
        """
        if not self._check(TokenType.IDENTIFIER):
            return None

        start = self.pos
        target = self._assignment_target()
        if not self._check_assignment_operator():
            self.pos = start
            return None
        operator = self._assignment_operator()
        expr = self._expression()
        if require_semicolon:
            self._consume(TokenType.SEMICOLON, "Expect ';'.")
        return self._build_assignment_stmt(target, operator, expr)

    def _assignment_target(self):
        """
        Parse the left-hand side of an assignment.
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        target = Variable(name.lexeme, line=name.line, column=name.column)

        while self._match(TokenType.LBRACKET):
            target = self._finish_index(target)

        return target

    def _check_assignment_operator(self):
        return any(
            self._check(token_type)
            for token_type in (
                TokenType.EQ,
                TokenType.PLUSEQ,
                TokenType.MINUSEQ,
                TokenType.STAREQ,
                TokenType.CARETEQ,
                TokenType.SLASHEQ,
            )
        )

    def _assignment_operator(self):
        if self._match(
            TokenType.EQ,
            TokenType.PLUSEQ,
            TokenType.MINUSEQ,
            TokenType.STAREQ,
            TokenType.CARETEQ,
            TokenType.SLASHEQ,
        ):
            return self._previous()

        raise NexParseError(
            "Expect assignment operator.",
            line=self._peek().line,
            column=self._peek().column,
        )

    def _build_assignment_stmt(self, target, operator, expr):
        if operator.type != TokenType.EQ:
            expr = Binary(
                target,
                operator.lexeme[0],
                expr,
                line=operator.line,
                column=operator.column,
            )

        if isinstance(target, Variable):
            return Assign(
                target.name,
                expr,
                operator.lexeme,
                line=target.line,
                column=target.column,
            )
        return IndexAssign(
            target,
            expr,
            operator.lexeme,
            line=target.line,
            column=target.column,
        )

    def _finish_function_call(self, callee):
        """
        Parse a function call suffix after the opening '(' was already
        consumed.
        """
        if not isinstance(callee, Variable):
            raise NexParseError(
                "only named functions can be called",
                line=self._previous().line,
                column=self._previous().column,
            )

        # consume function values
        arguments = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Expect ')'")

        return FuncCall(
            callee.name,  # callee name
            len(arguments),  # arity
            tuple(arguments),  # argument expressions
            line=callee.line,
            column=callee.column,
        )

    def _finish_index(self, receiver):
        """
        Parse an indexing postfix after the opening '[' was already consumed.
        """
        bracket = self._previous()
        index = self._expression()
        self._consume(TokenType.RBRACKET, "Expect ']'.")
        return Index(receiver, index, line=bracket.line, column=bracket.column)

    def _finish_method_call(self, receiver):
        """
        Parse a method-style call after the '.' token was already consumed.
        """
        dot = self._previous()
        method = self._consume(TokenType.IDENTIFIER, "Expect method name.")
        self._consume(TokenType.LPAREN, "Expect '(' after method name.")

        arguments = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Expect ')'")

        return MethodCall(
            receiver,
            method.lexeme,
            len(arguments),
            tuple(arguments),
            line=dot.line,
            column=dot.column,
        )

    def _finish_postfix_update(self, expr):
        """
        Parse a postfix increment/decrement suffix after the operator token was
        already consumed. These operators are restricted to variables.
        """
        operator = self._previous()

        if not isinstance(expr, Variable):
            raise NexParseError(
                "postfix operators require a variable operand",
                line=operator.line,
                column=operator.column,
            )

        return Postfix(
            expr, operator.lexeme, line=operator.line, column=operator.column
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
