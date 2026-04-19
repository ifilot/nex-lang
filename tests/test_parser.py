import pytest

from nex import Interpreter
from nex.interpreter.expr import Binary, Literal, Variable
from nex.interpreter.stmt import Assign, Block, ExprStmt, For, If, Print, VarDecl, While
from nex.lexer import Lexer
from nex.parser import Parser


def parse(source: str):
    """
    Helper function to lex and parse a source string into an AST.
    """
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def test_parses_variable_declaration():
    program = parse("var x = 1 + 2;")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.initializer, Binary)
    assert stmt.initializer.op == "+"
    assert stmt.initializer.left == Literal(1)
    assert stmt.initializer.right == Literal(2)


def test_parses_expression_statement():
    program = parse("1 + 2;")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == Binary(Literal(1), "+", Literal(2))


def test_parses_if_else_statement():
    program = parse('if (x < 10) { print("ok"); } else { print("no"); }')

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, If)
    assert isinstance(stmt.condition, Binary)
    assert stmt.condition.op == "<"
    assert stmt.condition.left == Variable("x")
    assert stmt.condition.right == Literal(10)
    assert isinstance(stmt.then_branch, Block)
    assert isinstance(stmt.else_branch, Block)
    assert len(stmt.then_branch.statements) == 1
    assert len(stmt.else_branch.statements) == 1
    assert isinstance(stmt.then_branch.statements[0], Print)
    assert isinstance(stmt.else_branch.statements[0], Print)


def test_parses_while_statement():
    program = parse("while (x < 3) { print(x); }")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, While)
    assert isinstance(stmt.condition, Binary)
    assert stmt.condition.left == Variable("x")
    assert stmt.condition.op == "<"
    assert stmt.condition.right == Literal(3)
    assert isinstance(stmt.body, Block)
    assert len(stmt.body.statements) == 1
    assert isinstance(stmt.body.statements[0], Print)


def test_parses_for_statement_with_var_initializer():
    program = parse("for (var i = 0; i < 3; i = i + 1) { print(i); }")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init == VarDecl("i", Literal(0))
    assert isinstance(stmt.condition, Binary)
    assert stmt.condition.left == Variable("i")
    assert stmt.condition.op == "<"
    assert stmt.condition.right == Literal(3)
    assert stmt.iter == Assign("i", Binary(Variable("i"), "+", Literal(1)))
    assert isinstance(stmt.body, Block)
    assert len(stmt.body.statements) == 1
    assert isinstance(stmt.body.statements[0], Print)


def test_parses_for_statement_with_assignment_initializer():
    program = parse("for (i = 0; i < 3; i = i + 1) { print(i); }")

    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init == Assign("i", Literal(0))
    assert stmt.iter == Assign("i", Binary(Variable("i"), "+", Literal(1)))


def test_parses_for_statement_with_empty_initializer_and_iteration():
    program = parse("for (; i < 3; ) { print(i); }")

    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init is None
    assert isinstance(stmt.condition, Binary)
    assert stmt.condition.left == Variable("i")
    assert stmt.condition.op == "<"
    assert stmt.condition.right == Literal(3)
    assert stmt.iter is None


def test_rejects_invalid_for_initializer_clause():
    with pytest.raises(RuntimeError, match="Invalid initializer clause."):
        parse("for (print(1); i < 3; i = i + 1) { print(i); }")


def test_executes_expression_statement_without_output(capsys):
    program = parse("1 + 2;")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == ""
