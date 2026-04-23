import pytest

from nex import Interpreter, Lexer, Parser, __version__
from nex.common import NexIndexError, NexParseError, NexRuntimeError
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


def test_executes_compound_scalar_assignments(capsys):
    run_source(
        """
        int x = 2;
        x += 1;
        x *= 15;
        x /= 3;
        x -= 10;
        x ^= 2;
        print(x);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "25\n"


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
    assert xs.storage == []

    assert isinstance(ys, NexArray)
    assert ys.declared_type == "array<str>"
    assert ys.length() == 0
    assert ys.storage == []


def test_reads_array_element_with_negative_index(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = [10, 20, 30]

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


def test_executes_compound_index_assignment(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = [10, 20, 30]

    interpreter.run(parse_source("xs[-1] += 5; print(xs[-1]);"))

    captured = capsys.readouterr()
    assert captured.out == "35\n"
    assert xs.storage == [10, 20, 35]


def test_compound_index_assignment_evaluates_target_once(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = [10, 20]

    interpreter.run(parse_source("int i = 0; xs[i++] += 5; print(xs[0]); print(i);"))

    captured = capsys.readouterr()
    assert captured.out == "15\n1\n"
    assert xs.storage == [15, 20]


def test_explicit_index_self_assignment_preserves_double_evaluation(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = [10, 20]

    interpreter.run(
        parse_source("int i = 0; xs[i++] = xs[i++] + 1; print(xs[0]); print(i);")
    )

    captured = capsys.readouterr()
    assert captured.out == "21\n2\n"
    assert xs.storage == [21, 20]


def test_rejects_out_of_bounds_array_access():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))

    with pytest.raises(NexIndexError) as excinfo:
        interpreter.run(parse_source("print(xs[0]);"))

    assert excinfo.value.message == "array index 0 out of bounds for length 0"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 10


def test_rejects_out_of_bounds_array_assignment():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))

    with pytest.raises(NexIndexError) as excinfo:
        interpreter.run(parse_source("xs[-1] = 1;"))

    assert excinfo.value.message == "array index -1 out of bounds for length 0"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 4


def test_rejects_array_assignment_of_wrong_element_type():
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = [1]

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
    xs.storage = [10, 20, 30]

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
    xs.storage = [10, 20, 30]
    names.storage = ["Ada", "Grace"]

    interpreter.run(
        parse_source(
            "reset(xs); names.reset(); print(xs[0]); print(xs[-1]); print(names[0]); print(names[-1]);"
        )
    )

    captured = capsys.readouterr()
    assert captured.out == "0\n0\n\n\n"
    assert xs.storage == [0, 0, 0]
    assert names.storage == ["", ""]


def test_power_operator_supports_integer_exponentiation(capsys):
    run_source(
        """
        print(2 ^ 5);
        print(2 * 3 ^ 2);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "32\n18\n"


def test_power_operator_is_right_associative(capsys):
    run_source("print(2 ^ 3 ^ 2);")

    captured = capsys.readouterr()
    assert captured.out == "512\n"


def test_power_operator_rejects_negative_exponents():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source("print(2 ^ -1);")

    assert excinfo.value.message == "operator `^` does not support negative exponents"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 9


def test_power_operator_preserves_arbitrary_precision_integers(capsys):
    run_source("print(2 ^ 100);")

    captured = capsys.readouterr()
    assert captured.out == "1267650600228229401496703205376\n"


def test_integer_division_preserves_arbitrary_precision(capsys):
    big = 10**400

    run_source(f"print({big} / 3);")

    captured = capsys.readouterr()
    assert captured.out == f"{big // 3}\n"


def test_integer_division_truncates_toward_zero(capsys):
    run_source("print(-8 / 3); print(8 / -3); print(-8 / -3);")

    captured = capsys.readouterr()
    assert captured.out == "-2\n-2\n2\n"


def test_indexed_int_value_round_trips_as_plain_nex_int(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))
    xs = interpreter.env.lookup("xs")
    xs.storage = [5]

    interpreter.run(parse_source("int y = xs[0]; print(y + 2);"))

    captured = capsys.readouterr()
    assert captured.out == "7\n"


def test_array_equality_is_structural_for_both_array_kinds(capsys):
    interpreter = Interpreter()
    interpreter.run(
        parse_source("array<int> xs; array<int> ys; array<str> a; array<str> b;")
    )

    xs = interpreter.env.lookup("xs")
    ys = interpreter.env.lookup("ys")
    a = interpreter.env.lookup("a")
    b = interpreter.env.lookup("b")

    xs.storage = [1, 2, 3]
    ys.storage = [1, 2, 3]
    a.storage = ["Ada", "Grace"]
    b.storage = ["Ada", "Linus"]

    interpreter.run(
        parse_source("print(xs == ys); print(xs != ys); print(a == b); print(a != b);")
    )

    captured = capsys.readouterr()
    assert captured.out == "true\nfalse\nfalse\ntrue\n"


def test_rejects_equality_between_different_array_types():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            array<int> xs;
            array<str> ys;
            print(xs == ys);
            """
        )

    assert (
        excinfo.value.message
        == "operator `==` expects operands of the same type, got array<int> and array<str>"
    )
    assert excinfo.value.line == 4
    assert excinfo.value.column == 22


def test_array_int_supports_arbitrary_precision_values(capsys):
    big = 10**30
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs;"))

    interpreter.run(parse_source(f"resize(xs, 1); xs[0] = {big}; print(xs[0]);"))

    captured = capsys.readouterr()
    assert captured.out == f"{big}\n"


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


def test_standalone_block_creates_scope(capsys):
    run_source(
        """
        int x = 1;
        {
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


def test_builtin_intstr_converts_int_to_string(capsys):
    run_source("print(intstr(42)); print(intstr(2 ^ 10));")

    captured = capsys.readouterr()
    assert captured.out == "42\n1024\n"


def test_builtin_strint_converts_string_to_int_with_zero_fallback(capsys):
    run_source('print(strint("123")); print(strint("-7")); print(strint("nope"));')

    captured = capsys.readouterr()
    assert captured.out == "123\n-7\n0\n"


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


def test_rejects_user_function_that_conflicts_with_builtin():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn print(int x) -> void {
                return;
            }
            """
        )

    assert (
        excinfo.value.message
        == "cannot declare function `print` because it conflicts with a built-in function"
    )
    assert excinfo.value.line == 2
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


def test_function_reads_live_global_value_at_call_time(capsys):
    run_source(
        """
        int y = 2;

        fn show() -> void {
            print(y);
        }

        show();
        y = 3;
        show();
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "2\n3\n"


def test_function_can_update_global_variable(capsys):
    run_source(
        """
        int y = 2;

        fn bump() -> void {
            y = y + 1;
        }

        bump();
        print(y);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "3\n"


def test_function_local_shadow_does_not_leak_to_global(capsys):
    run_source(
        """
        int y = 2;

        fn show() -> void {
            int y = 10;
            print(y);
        }

        show();
        print(y);
        """
    )

    captured = capsys.readouterr()
    assert captured.out == "10\n2\n"


def test_function_cannot_read_callers_block_local():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn show() -> void {
                print(y);
            }

            if (true) {
                int y = 2;
                show();
            }
            """
        )

    assert excinfo.value.message == "undefined variable `y`"
    assert excinfo.value.line == 3
    assert excinfo.value.column == 23


def test_function_cannot_read_callers_function_local():
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source(
            """
            fn show() -> void {
                print(x);
            }

            fn caller() -> void {
                int x = 2;
                show();
            }

            caller();
            """
        )

    assert excinfo.value.message == "undefined variable `x`"
    assert excinfo.value.line == 3
    assert excinfo.value.column == 23


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
    assert captured.out == "1\nhello\ntrue\n"


def test_builtin_print_formats_arrays_with_nex_value_rendering(capsys):
    interpreter = Interpreter()
    interpreter.run(parse_source("array<int> xs; array<str> names;"))
    xs = interpreter.env.lookup("xs")
    names = interpreter.env.lookup("names")
    xs.storage = [1, 2, 3]
    names.storage = ["Ada", "Grace"]

    interpreter.run(parse_source("print(xs); print(names);"))

    captured = capsys.readouterr()
    assert captured.out == '[1, 2, 3]\n["Ada", "Grace"]\n'


def test_rejects_void_as_print_argument(capsys):
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source('print(print("inner"));')

    captured = capsys.readouterr()
    assert captured.out == "inner\n"
    assert (
        excinfo.value.message
        == "no overload of function `print` matches argument types (void)"
    )
    assert excinfo.value.line == 1
    assert excinfo.value.column == 1


def test_rejects_void_equality(capsys):
    with pytest.raises(NexRuntimeError) as excinfo:
        run_source('bool b = print("a") == print("b");')

    captured = capsys.readouterr()
    assert captured.out == "a\nb\n"
    assert excinfo.value.message == "operator `==` does not support void operands"
    assert excinfo.value.line == 1
    assert excinfo.value.column == 21


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
