from nex.interpreter.expr import Binary, FuncCall, Literal, Postfix, Variable
from nex.interpreter.stmt import Block, ExprStmt, FuncDecl, Return
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
