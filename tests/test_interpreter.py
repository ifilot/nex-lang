import pytest

from nex import Interpreter, Lexer, Parser
from nex.common import NexParseError, NexRuntimeError


def run_source(source: str) -> None:
    """
    Lex, parse, and execute a source string.
    """
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    Interpreter().run(program)


def test_executes_typed_assignment_and_print(capsys):
    run_source(
        """
        int x = 1;
        x = x + 2;
        print(x);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "3\n"


def test_rejects_assignment_of_wrong_type():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            int x = 1;
            x = "hello";
            """
        )

    assert (
        excinfo.value.message
        == "cannot assign value of type str to variable `x` of type int"
    )
    assert excinfo.value.line == 3
    assert excinfo.value.column == 17


def test_rejects_if_condition_that_is_not_bool():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            if (1) {
                print(1);
            }
            """
        )

    assert excinfo.value.message == "condition must evaluate to a bool, got int"
    assert excinfo.value.line == 2
    assert excinfo.value.column == 17


def test_rejects_while_condition_that_is_not_bool():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            while (1) {
                print(1);
            }
            """
        )

    assert excinfo.value.message == "condition must evaluate to a bool, got int"
    assert excinfo.value.line == 2
    assert excinfo.value.column == 20


def test_rejects_for_condition_that_is_not_bool():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            for (int i = 0; 1; i = i + 1) {
                print(i);
            }
            """
        )

    assert excinfo.value.message == "condition must evaluate to a bool, got int"
    assert excinfo.value.line == 2
    assert excinfo.value.column == 29


def test_executes_if_with_nested_logical_condition(capsys):
    run_source(
        """
        if (true && (false || true)) {
            print(1);
        }
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "1\n"


def test_executes_for_loop_accumulation(capsys):
    run_source(
        """
        int total = 0;
        for (int i = 0; i < 4; i = i + 1) {
            total = total + i;
        }
        print(total);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "6\n"


def test_rejects_division_by_zero():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source("print(1 / 0);")

    assert excinfo.value.message == "division by zero"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 9


def test_rejects_modulus_by_zero():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source("print(1 % 0);")

    assert excinfo.value.message == "division by zero"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 9


def test_block_scope_shadows_outer_variable(capsys):
    run_source(
        """
        int x = 1;
        if (true) {
            int x = 2;
            print(x);
        }
        print(x);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "2\n1\n"


def test_for_initializer_scope_does_not_leak():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            for (int i = 0; i < 1; i = i + 1) {
                print(i);
            }
            print(i);
            """
        )

    assert excinfo.value.message == "undefined variable `i`"
    assert excinfo.value.line == 5
    assert excinfo.value.column == 19


def test_rejects_call_to_undefined_function():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source("missing();")

    assert excinfo.value.message == "undefined function `missing`"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_rejects_duplicate_function_declaration():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn ping() -> void {
                return;
            }

            fn ping() -> void {
                return;
            }
            """
        )

    assert excinfo.value.message == "function `ping` is already defined"
    assert excinfo.value.line == 6
    assert excinfo.value.column == 13


def test_rejects_function_call_with_wrong_arity_and_reports_call_site():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn add(int a) -> int {
                return a;
            }

            add();
            """
        )

    assert excinfo.value.message == "incorrect number of arguments provided 0 != 1"
    assert excinfo.value.line == 6
    assert excinfo.value.column == 13


def test_rejects_function_call_with_wrong_argument_type_and_reports_call_site():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn add(int a) -> int {
                return a;
            }

            add("x");
            """
        )

    assert (
        excinfo.value.message
        == "param `a` has the wrong type, encountered `str` while expected `int`"
    )
    assert excinfo.value.line == 6
    assert excinfo.value.column == 13


def test_rejects_nonvoid_function_that_falls_through_in_statement_position():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn bad() -> int {
                int x = 1;
            }

            bad();
            """
        )

    assert excinfo.value.message == "non-void function `bad` returned void"
    assert excinfo.value.line == 6
    assert excinfo.value.column == 13


def test_rejects_nonvoid_function_that_falls_through_in_value_position():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn bad() -> int {
                int x = 1;
            }

            int y = bad();
            """
        )

    assert excinfo.value.message == "non-void function `bad` returned void"
    assert excinfo.value.line == 6
    assert excinfo.value.column == 21


def test_rejects_top_level_return_before_interpretation():
    with pytest.raises(NexParseError) as excinfo:
        run_source("return 1;")

    assert (
        excinfo.value.message
        == "return statement are not allowed outside of function declarations"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1
