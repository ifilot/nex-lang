import pytest

from nex import Interpreter
from nex.interpreter.expr import Binary, Literal, Unary, Variable
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


def test_parses_unary_not_expression_statement():
    program = parse("!0;")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == Unary("!", Literal(0))


def test_parses_modulus_expression_statement():
    program = parse("5 % 2;")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == Binary(Literal(5), "%", Literal(2))


def test_parses_two_character_comparison_expression_statements():
    program = parse("x <= 3; y >= 4; z == 5; w != 6;")

    assert len(program) == 4
    assert program[0] == ExprStmt(Binary(Variable("x"), "<=", Literal(3)))
    assert program[1] == ExprStmt(Binary(Variable("y"), ">=", Literal(4)))
    assert program[2] == ExprStmt(Binary(Variable("z"), "==", Literal(5)))
    assert program[3] == ExprStmt(Binary(Variable("w"), "!=", Literal(6)))


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


def test_executes_unary_not_expression(capsys):
    program = parse("print(!0); print(!1);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "True\nFalse\n"


def test_executes_two_character_comparisons(capsys):
    program = parse(
        "print(2 <= 2); print(5 >= 3); print(1 >= 4); print(4 == 4); print(4 != 5);"
    )

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "True\nTrue\nFalse\nTrue\nTrue\n"


def test_executes_modulus_expression(capsys):
    program = parse("print(5 % 2); print(8 % 3);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "1\n2\n"
