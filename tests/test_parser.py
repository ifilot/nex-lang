import pytest

from nex import Interpreter
from nex.common import NexParseError, NexRuntimeError
from nex.interpreter.expr import Binary, FuncCall, Literal, Postfix, Unary, Variable
from nex.interpreter.stmt import (
    Assign,
    Block,
    ExprStmt,
    For,
    FuncDecl,
    If,
    Return,
    VarDecl,
    While,
)
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


def test_parses_logical_operator_expression_statements_with_precedence():
    program = parse("a || b && c == d;")

    assert len(program) == 1
    assert program[0] == ExprStmt(
        Binary(
            Variable("a"),
            "||",
            Binary(
                Variable("b"),
                "&&",
                Binary(Variable("c"), "==", Variable("d")),
            ),
        )
    )


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
    assert stmt.then_branch.statements[0] == ExprStmt(
        FuncCall("print", 1, (Literal("ok"),))
    )
    assert stmt.else_branch.statements[0] == ExprStmt(
        FuncCall("print", 1, (Literal("no"),))
    )


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
    assert stmt.body.statements[0] == ExprStmt(FuncCall("print", 1, (Variable("x"),)))


def test_parses_function_declaration_without_parameters():
    program = parse('fn hello() -> void { print("hi"); }')

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, FuncDecl)
    assert stmt.callee == "hello"
    assert stmt.arity == 0
    assert stmt.arguments == ()
    assert stmt.return_type == "void"
    assert isinstance(stmt.body, Block)
    assert len(stmt.body.statements) == 1
    assert stmt.body.statements[0] == ExprStmt(FuncCall("print", 1, (Literal("hi"),)))


def test_parses_function_declaration_with_parameters_and_return():
    program = parse("fn add(int a, int b) -> int { return a + b; }")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, FuncDecl)
    assert stmt.callee == "add"
    assert stmt.arity == 2
    assert stmt.arguments == (("int", "a"), ("int", "b"))
    assert stmt.return_type == "int"
    assert isinstance(stmt.body, Block)
    assert len(stmt.body.statements) == 1
    assert stmt.body.statements[0] == Return(Binary(Variable("a"), "+", Variable("b")))


def test_parses_return_without_expression():
    program = parse("fn noop() -> void { return; }")

    stmt = program[0]
    assert isinstance(stmt, FuncDecl)
    assert stmt.body.statements == (Return(None),)


def test_parses_return_inside_nested_block_within_function():
    program = parse(
        """
        fn classify(int x) -> int {
            if (x == 0) {
                return 1;
            }
            return 2;
        }
        """
    )

    stmt = program[0]
    assert isinstance(stmt, FuncDecl)
    assert isinstance(stmt.body.statements[0], If)
    assert stmt.body.statements[0].then_branch.statements == (Return(Literal(1)),)
    assert stmt.body.statements[1] == Return(Literal(2))


def test_rejects_duplicate_parameter_names_with_structured_parse_error():
    with pytest.raises(NexParseError) as excinfo:
        parse("fn f(int a, int a) -> int { return a; }")

    assert excinfo.value.message == "duplicate parameter `a` encountered"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 17


def test_rejects_return_outside_function_with_structured_parse_error():
    with pytest.raises(NexParseError) as excinfo:
        parse("return 1;")

    assert (
        excinfo.value.message
        == "return statement are not allowed outside of function declarations"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_parses_function_call_as_expression_statement():
    program = parse("hello();")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == FuncCall("hello", 0, ())


def test_parses_postfix_increment_as_expression_statement():
    program = parse("i++;")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == Postfix(Variable("i"), "++")


def test_parses_postfix_decrement_inside_expression():
    program = parse("print(i--);")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == FuncCall("print", 1, (Postfix(Variable("i"), "--"),))


def test_rejects_postfix_update_on_non_variable_operand():
    with pytest.raises(NexParseError) as excinfo:
        parse("(1 + 2)++;")

    assert excinfo.value.message == "postfix operators require a variable operand"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 8


def test_parses_function_call_inside_print_expression():
    program = parse("print(add(1, 2));")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == FuncCall(
        "print", 1, (FuncCall("add", 2, (Literal(1), Literal(2))),)
    )


def test_parses_nested_function_call_arguments():
    program = parse("outer(inner(1), 2 + 3);")

    stmt = program[0]
    assert isinstance(stmt, ExprStmt)
    assert stmt.expr == FuncCall(
        "outer",
        2,
        (
            FuncCall("inner", 1, (Literal(1),)),
            Binary(Literal(2), "+", Literal(3)),
        ),
    )


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
    assert stmt.body.statements[0] == ExprStmt(FuncCall("print", 1, (Variable("i"),)))


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


def test_parses_for_statement_with_expression_initializer():
    program = parse("for (1 + 2; i < 3; i = i + 1) { print(i); }")

    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init == ExprStmt(Binary(Literal(1), "+", Literal(2)))
    assert stmt.iter == Assign("i", Binary(Variable("i"), "+", Literal(1)))


def test_parses_for_statement_with_expression_iteration():
    program = parse("for (int i = 0; i < 3; i + 1) { print(i); }")

    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init == VarDecl("i", Literal(0), "int")
    assert stmt.iter == ExprStmt(Binary(Variable("i"), "+", Literal(1)))


def test_parses_function_call_in_for_initializer_clause():
    program = parse("for (print(1); i < 3; i = i + 1) { print(i); }")

    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, For)
    assert stmt.init == ExprStmt(FuncCall("print", 1, (Literal(1),)))
    assert stmt.body.statements[0] == ExprStmt(FuncCall("print", 1, (Variable("i"),)))


def test_rejects_missing_semicolon_with_structured_parse_error():
    with pytest.raises(NexParseError) as excinfo:
        parse("int x = 1")

    assert excinfo.value.message == "expect ';'"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 9


def test_rejects_missing_closing_paren_with_structured_parse_error():
    with pytest.raises(NexParseError) as excinfo:
        parse("print((1 + 2);")

    assert excinfo.value.message == "expected expression"
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


def test_executes_postfix_increment_and_returns_original_value(capsys):
    program = parse("int i = 1; print(i++); print(i);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "1\n2\n"


def test_executes_postfix_decrement_and_returns_original_value(capsys):
    program = parse("int i = 2; print(i--); print(i);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "2\n1\n"


def test_rejects_unary_not_on_non_boolean():
    program = parse("!0;")

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "cannot apply unary operator `!` to type int; expected bool"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_rejects_postfix_increment_on_non_integer():
    program = parse('str s = "x"; s++;')

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "cannot apply postfix operator `++` to type str; expected int"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 15


def test_rejects_unary_minus_on_non_integer():
    program = parse("-true;")

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "cannot apply unary operator `-` to type bool; expected int"
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


def test_executes_logical_operators(capsys):
    program = parse(
        "print(true && true); print(true && false); print(false || true); print(false || false);"
    )

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "True\nFalse\nTrue\nFalse\n"


def test_short_circuits_logical_operators():
    program = parse("false && missing(); true || missing();")

    Interpreter().run(program)


def test_rejects_non_boolean_logical_and_operand():
    program = parse("1 && true;")

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "operator `&&` expects bool operands, got int and <unevaluated>"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 3


def test_rejects_non_boolean_logical_or_rhs_operand():
    program = parse("false || 1;")

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message == "operator `||` expects bool operands, got bool and int"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 7


def test_executes_modulus_expression(capsys):
    program = parse("print(5 % 2); print(8 % 3);")

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "1\n2\n"


def test_executes_for_loop_with_expression_initializer(capsys):
    program = parse(
        """
        int i = 0;
        for (1 + 2; i < 3; i = i + 1) {
            print(i);
        }
        """
    )

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "0\n1\n2\n"


def test_executes_for_loop_with_expression_iteration(capsys):
    program = parse(
        """
        int i = 0;
        for (; i < 3; i + 1) {
            print(i);
            i = i + 1;
        }
        """
    )

    Interpreter().run(program)

    captured = capsys.readouterr()
    assert captured.out == "0\n1\n2\n"


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
        == "operator `==` expects operands of the same type, got int and str"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 3


def test_rejects_mixed_type_ordering():
    program = parse('1 < "2";')

    with pytest.raises(NexRuntimeError) as excinfo:
        Interpreter().run(program)

    assert (
        excinfo.value.message
        == "operator `<` expects matching int or str operands, got int and str"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 3
