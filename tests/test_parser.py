import pytest

from nex import Interpreter
from nex.common import NexParseError, NexRuntimeError
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
    program = parse("int x = 1 + 2;")

    assert len(program) == 1
    stmt = program[0]
    assert stmt == VarDecl("x", Binary(Literal(1), "+", Literal(2)), "int")


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


def test_parses_boolean_literal_expression_statements():
    program = parse("true; false;")

    assert len(program) == 2
    assert program[0] == ExprStmt(Literal(True))
    assert program[1] == ExprStmt(Literal(False))


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


def test_parses_for_statement_with_typed_initializer():
    program = parse("for (int i = 0; i < 3; i = i + 1) { print(i); }")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init == VarDecl("i", Literal(0), "int")
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
    with pytest.raises(NexParseError) as excinfo:
        parse("for (print(1); i < 3; i = i + 1) { print(i); }")

    assert excinfo.value.message == "invalid initializer clause"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 6


def test_rejects_missing_semicolon_with_structured_parse_error():
    with pytest.raises(NexParseError) as excinfo:
        parse("int x = 1")

    assert excinfo.value.message == "expect ';'"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 9


def test_rejects_missing_closing_paren_with_structured_parse_error():
    with pytest.raises(NexParseError) as excinfo:
        parse("print((1 + 2);")

    assert excinfo.value.message == "expect ')'"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 14


def test_executes_expression_statement_without_output(capsys):
    program = parse("1 + 2;")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == ""


def test_executes_unary_not_expression(capsys):
    program = parse("print(!true); print(!false);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "False\nTrue\n"


def test_rejects_unary_not_on_non_boolean():
    program = parse("!0;")

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "cannot apply unary operator '!' to type int; expected bool"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_rejects_unary_minus_on_non_integer():
    program = parse("-true;")

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "cannot apply unary operator '-' to type bool; expected int"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_executes_boolean_literals(capsys):
    program = parse("print(true); print(false);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "True\nFalse\n"


def test_executes_string_concatenation_and_comparison(capsys):
    program = parse('print("he" + "llo"); print("apple" < "banana");')

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "hello\nTrue\n"


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


def test_rejects_mixed_type_addition():
    program = parse('1 + "x";')

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "operator '+' expects int+int or str+str, got int and str"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 3


def test_rejects_mixed_type_equality():
    program = parse('1 == "1";')

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "operator '==' expects operands of the same type, got int and str"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 3


def test_rejects_mixed_type_ordering():
    program = parse('1 < "2";')

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "operator '<' expects matching int or str operands, got int and str"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 3
