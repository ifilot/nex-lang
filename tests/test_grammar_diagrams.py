import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def load_diagram_module():
    root = Path(__file__).resolve().parent.parent
    path = root / "scripts" / "generate_grammar_diagrams.py"
    spec = importlib.util.spec_from_file_location("generate_grammar_diagrams", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.repo_checks
def test_grammar_diagram_script_is_in_sync():
    root = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        [sys.executable, "scripts/generate_grammar_diagrams.py", "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_parse_rules_supports_multi_line_and_nested_productions():
    diagrams = load_diagram_module()

    rules = diagrams.parse_rules(
        """
        <statement> ::= <typed-decl>
                      | <expr-stmt>

        <postfix>   ::= <primary> ( <call-suffix> | <postfix-update> )*
        """.strip()
    )

    assert [rule.name for rule in rules] == ["<statement>", "<postfix>"]
    assert rules[0].expression == diagrams.Choice(
        (
            diagrams.Symbol("<typed-decl>"),
            diagrams.Symbol("<expr-stmt>"),
        )
    )
    assert rules[1].expression == diagrams.Sequence(
        (
            diagrams.Symbol("<primary>"),
            diagrams.Repeat(
                diagrams.Choice(
                    (
                        diagrams.Symbol("<call-suffix>"),
                        diagrams.Symbol("<postfix-update>"),
                    )
                )
            ),
        )
    )


def test_parse_expression_builds_nested_choice_and_optional_nodes():
    diagrams = load_diagram_module()

    expression = diagrams.parse_expression('"(" [ <parameters> ] ")" | "void"')

    assert expression == diagrams.Choice(
        (
            diagrams.Sequence(
                (
                    diagrams.Symbol('"("'),
                    diagrams.Optional(diagrams.Symbol("<parameters>")),
                    diagrams.Symbol('")"'),
                )
            ),
            diagrams.Symbol('"void"'),
        )
    )


def test_render_svg_uses_nested_choice_layout_for_inline_alternation():
    diagrams = load_diagram_module()
    rule = diagrams.Rule(
        "<type>",
        diagrams.Choice(
            (
                diagrams.Symbol('"int"'),
                diagrams.Symbol('"str"'),
                diagrams.Symbol('"bool"'),
            )
        ),
    )

    svg = diagrams.render_svg(rule)

    assert svg.count("<circle") == 2
    assert svg.count("<path") >= 4
    assert ">int</text>" in svg
    assert ">str</text>" in svg
    assert ">bool</text>" in svg
    assert ">|</text>" not in svg


def test_render_svg_uses_nested_choice_layout_inside_repetition_group():
    diagrams = load_diagram_module()
    rule = diagrams.Rule(
        "<comparison>",
        diagrams.Sequence(
            (
                diagrams.Symbol("<term>"),
                diagrams.Repeat(
                    diagrams.Sequence(
                        (
                            diagrams.Choice(
                                (
                                    diagrams.Symbol('"<"'),
                                    diagrams.Symbol('">"'),
                                    diagrams.Symbol('"<="'),
                                    diagrams.Symbol('">="'),
                                    diagrams.Symbol('"=="'),
                                    diagrams.Symbol('"!="'),
                                )
                            ),
                            diagrams.Symbol("<term>"),
                        )
                    )
                ),
            )
        ),
    )

    svg = diagrams.render_svg(rule)

    assert svg.count("<path") >= 6
    assert "&lt;term&gt;" in svg
    assert "&lt;=" in svg
    assert "&gt;=" in svg
    assert "==" in svg
    assert "!=" in svg


def test_render_svg_expands_small_diagrams_to_fit_long_titles():
    diagrams = load_diagram_module()
    rule = diagrams.Rule(
        "<postfix-update>",
        diagrams.Choice(
            (
                diagrams.Symbol('"++"'),
                diagrams.Symbol('"--"'),
            )
        ),
    )

    svg = diagrams.render_svg(rule)
    expected_width = max(
        diagrams.LEFT_MARGIN
        + diagrams.TRACK_GAP
        + diagrams.layout_node(rule.expression).width
        + diagrams.TRACK_GAP
        + diagrams.RIGHT_MARGIN,
        diagrams.LEFT_MARGIN + diagrams.title_width(rule) + diagrams.RIGHT_MARGIN,
    )

    assert f'width="{expected_width}"' in svg
    assert "&lt;postfix-update&gt;" in svg


def test_update_markdown_inserts_generated_section_before_notes():
    diagrams = load_diagram_module()
    markdown = "# Grammar\n\n```text\n<program> ::= EOF\n```\n\n## Notes\n"
    generated = (
        f"{diagrams.MARKER_START}\n\n## Syntax diagrams\n\n{diagrams.MARKER_END}\n"
    )

    updated = diagrams.update_markdown(markdown, generated)

    assert "## Syntax diagrams" in updated
    assert updated.index(diagrams.MARKER_START) < updated.index("## Notes")
