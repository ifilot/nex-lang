from nex.interpreter.expr import (
    Binary,
    FuncCall,
    Index,
    Literal,
    MethodCall,
    Postfix,
    Variable,
)
from nex.interpreter.stmt import (
    ArrayDecl,
    Block,
    ExprStmt,
    FuncDecl,
    IndexAssign,
    Return,
)
from nex.pretty_printer import PrettyPrinter


def test_pretty_prints_function_declaration_signature_and_body():
    program = [
        FuncDecl(
            "add",
            2,
            (("int", "a"), ("int", "b")),
            Block((Return(Binary(Variable("a"), "+", Variable("b"))),)),
            "int",
        )
    ]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "`- FuncDecl [add(int a, int b) -> int]",
            "   |- Arity: 2",
            "   `- Body",
            "      `- Block",
            "         `- Return",
            "            `- Expr",
            "               `- Binary(+)",
            "                  |- Variable(a)",
            "                  `- Variable(b)",
        ]
    )


def test_pretty_prints_function_call_arguments_in_order():
    program = [
        ExprStmt(
            FuncCall(
                "outer",
                2,
                (
                    FuncCall("inner", 1, (Literal(1),)),
                    Binary(Literal(2), "+", Literal(3)),
                ),
            )
        )
    ]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "`- ExprStmt",
            "   `- FuncCall [outer]",
            "      |- Argument 1",
            "      |  `- FuncCall [inner]",
            "      |     `- Argument 1",
            "      |        `- Literal(1)",
            "      `- Argument 2",
            "         `- Binary(+)",
            "            |- Literal(2)",
            "            `- Literal(3)",
        ]
    )


def test_pretty_prints_return_without_expression():
    program = [FuncDecl("noop", 0, (), Block((Return(None),)), "void")]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "`- FuncDecl [noop() -> void]",
            "   |- Arity: 0",
            "   `- Body",
            "      `- Block",
            "         `- Return",
            "            `- Expr: None",
        ]
    )


def test_pretty_prints_postfix_expression():
    program = [ExprStmt(Postfix(Variable("i"), "++"))]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "`- ExprStmt",
            "   `- Postfix(++)",
            "      `- Variable(i)",
        ]
    )


def test_pretty_prints_array_types_in_function_signature():
    program = [
        FuncDecl(
            "clone",
            2,
            (("array<int>", "xs"), ("array<str>", "ys")),
            Block((Return(Variable("ys")),)),
            "array<str>",
        )
    ]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "`- FuncDecl [clone(array<int> xs, array<str> ys) -> array<str>]",
            "   |- Arity: 2",
            "   `- Body",
            "      `- Block",
            "         `- Return",
            "            `- Expr",
            "               `- Variable(ys)",
        ]
    )


def test_pretty_prints_array_declaration():
    program = [ArrayDecl("arr", "array<int>")]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "`- ArrayDecl(array<int> arr)",
        ]
    )


def test_pretty_prints_method_call_and_index_assignment():
    program = [
        ExprStmt(MethodCall(Variable("arr"), "resize", 1, (Literal(100),))),
        IndexAssign(Index(Variable("arr"), Literal(0)), Literal(42)),
    ]

    rendered = PrettyPrinter().print_program(program)

    assert rendered == "\n".join(
        [
            "Program",
            "|- ExprStmt",
            "|  `- MethodCall [resize]",
            "|     |- Receiver",
            "|     |  `- Variable(arr)",
            "|     `- Argument 1",
            "|        `- Literal(100)",
            "`- IndexAssign",
            "   |- Target",
            "   |  `- Index",
            "   |     |- Receiver",
            "   |     |  `- Variable(arr)",
            "   |     `- Offset",
            "   |        `- Literal(0)",
            "   `- Expr",
            "      `- Literal(42)",
        ]
    )
