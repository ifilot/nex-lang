import numpy as np
import pytest

from nex import Interpreter, Lexer, Parser, __version__
from nex.common import NexParseError, NexRuntimeError
from nex.interpreter.nex_array import NexArray


def run_source(source: str) -> None:
    """
    Lex, parse, and execute a source string.
    """
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    Interpreter().run(program)


def parse_source(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


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


def test_array_declaration_creates_empty_backend_values():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs; array<str> ys;"))

    xs = interpreter.env.lookup("xs")
    ys = interpreter.env.lookup("ys")

    assert isinstance(xs, NexArray)
    assert xs.declared_type == "array<int>"
    assert xs.length() == 0
    assert isinstance(xs.storage, np.ndarray)

    assert isinstance(ys, NexArray)
    assert ys.declared_type == "array<str>"
    assert ys.length() == 0
    assert ys.storage == []


def test_reads_array_element_with_negative_index(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = np.array([10, 20, 30], dtype=np.int64)

    interpreter.run(parse_source("print(xs[-1]);"))

    captured = capsys.readouterr()
    assert captured.out == "30\n"


def test_assigns_array_element_with_negative_index(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<str> names;"))
    names = interpreter.env.lookup("names")
    names.storage = ["Ada", "Grace"]

    interpreter.run(parse_source('names[-1] = "Linus"; print(names[-1]);'))

    captured = capsys.readouterr()
    assert captured.out == "Linus\n"
    assert names.storage == ["Ada", "Linus"]


def test_rejects_out_of_bounds_array_access():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))

    with pytest.raises(NexRuntimeError) as excinfo:
        interpreter.run(parse_source("print(xs[0]);"))

    assert excinfo.value.message == "array index 0 out of bounds for length 0"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 10


def test_rejects_out_of_bounds_array_assignment():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))

    with pytest.raises(NexRuntimeError) as excinfo:
        interpreter.run(parse_source("xs[-1] = 1;"))

    assert excinfo.value.message == "array index -1 out of bounds for length 0"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 4


def test_rejects_array_assignment_of_wrong_element_type():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = np.array([1], dtype=np.int64)

    with pytest.raises(NexRuntimeError) as excinfo:
        interpreter.run(parse_source('xs[0] = "hello";'))

    assert (
        excinfo.value.message == "cannot assign value of type str to array<int> element"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 9


def test_builtin_length_supports_direct_and_method_style_calls(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = np.array([10, 20, 30], dtype=np.int64)

    interpreter.run(parse_source("print(length(xs)); print(xs.length());"))

    captured = capsys.readouterr()
    assert captured.out == "3\n3\n"


def test_builtin_resize_supports_direct_and_method_style_calls(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<str> names;"))
    names = interpreter.env.lookup("names")
    names.storage = ["Ada"]

    interpreter.run(
        parse_source(
            "resize(names, 3); print(names[1]); names.resize(4); print(names.length());"
        )
    )

    captured = capsys.readouterr()
    assert captured.out == "\n4\n"
    assert names.storage == ["Ada", "", "", ""]


def test_builtin_resize_rejects_negative_sizes():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))

    with pytest.raises(NexRuntimeError) as excinfo:
        interpreter.run(parse_source("resize(xs, -1);"))

    assert (
        excinfo.value.message
        == "builtin function `resize` failed: size must be non-negative"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_builtin_reset_supports_direct_and_method_style_calls(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs; array<str> names;"))
    xs = interpreter.env.lookup("xs")
    names = interpreter.env.lookup("names")
    xs.storage = np.array([10, 20, 30], dtype=np.int64)
    names.storage = ["Ada", "Grace"]

    interpreter.run(
        parse_source(
            "reset(xs); names.reset(); print(xs[0]); print(xs[-1]); print(names[0]); print(names[-1]);"
        )
    )

    captured = capsys.readouterr()
    assert captured.out == "0\n0\n\n\n"
    assert xs.storage.tolist() == [0, 0, 0]
    assert names.storage == ["", ""]


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


def test_builtin_version_returns_interpreter_version(capsys):
    run_source("print(version());")

    captured = capsys.readouterr()
    assert captured.out == f"{__version__}\n"


def test_builtin_print_inline_omits_trailing_newline(capsys):
    run_source(
        """
        print_inline("Hello");
        print(" World");
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"


def test_builtin_input_reads_string(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda: "Ada")

    run_source(
        """
        str name = input();
        print(name);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "Ada\n"


def test_builtin_input_wraps_host_errors_as_runtime_errors(monkeypatch):
    def raise_eof():
        raise EOFError("EOF when reading a line")

    monkeypatch.setattr("builtins.input", raise_eof)

    with pytest.raises(NexRuntimeError) as excinfo:
        run_source("input();")

    assert (
        excinfo.value.message
        == "builtin function `input` failed: EOF when reading a line"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


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

    assert (
        excinfo.value.message == "function `ping` with signature () is already defined"
    )
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

    assert excinfo.value.message == "no overload of function `add` accepts 0 arguments"
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
        == "no overload of function `add` matches argument types (str)"
    )
    assert excinfo.value.line == 6
    assert excinfo.value.column == 13


def test_dispatches_overloaded_functions_by_argument_type(capsys):
    run_source(
        """
        fn show(int x) -> void {
            print("int");
        }

        fn show(str x) -> void {
            print("str");
        }

        show(1);
        show("hello");
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "int\nstr\n"


def test_allows_overloads_with_same_name_and_different_arity(capsys):
    run_source(
        """
        fn show() -> void {
            print("zero");
        }

        fn show(int x) -> void {
            print("one");
        }

        show();
        show(1);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "zero\none\n"


def test_builtin_print_still_accepts_any_supported_value_type(capsys):
    run_source(
        """
        print(1);
        print("hello");
        print(true);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "1\nhello\nTrue\n"


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
