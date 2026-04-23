#!/usr/bin/env python3
"""
Generate the SVG grammar diagrams used by the NEX reference documentation.

This script treats `docs/src/reference/grammar.md` as the source of truth for
the surface grammar. It parses the fenced `text` grammar block in that file,
renders one SVG railroad-style diagram per grammar rule, writes those SVGs to
`docs/src/reference/grammar-diagrams/`, and refreshes the generated embed
section in the grammar chapter.

Use `--check` in CI to verify that the checked-in Markdown and SVG outputs are
already in sync with the grammar source.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAMMAR_DOC = ROOT / "docs" / "src" / "reference" / "grammar.md"
DIAGRAM_DIR = ROOT / "docs" / "src" / "reference" / "grammar-diagrams"
MARKER_START = "<!-- GENERATED GRAMMAR DIAGRAMS START -->"
MARKER_END = "<!-- GENERATED GRAMMAR DIAGRAMS END -->"

# Match the fenced grammar block that acts as the single source of truth.
# Change this only if the docs switch to a different fence format.
TEXT_BLOCK_PATTERN = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
# Match the first line of a grammar production like `<expr> ::= <term>`.
RULE_PATTERN = re.compile(r"^\s*(<[^>]+>)\s*::=\s*(.+?)\s*$")
# Match continuation lines that begin with `|` and belong to the prior rule.
CONTINUATION_PATTERN = re.compile(r"^\s+\|\s*(.+?)\s*$")
# Tokenize quoted literals, non-terminals, inline groups, and fallback atoms.
TOKEN_PATTERN = re.compile(r'"[^"]*"|<[^>]+>|\[[^\]]+\]|\([^)]+\)\*?|\S+')

# Approximate average character width when sizing label boxes.
# Increase this if labels look cramped; decrease it if boxes feel too wide.
CHAR_WIDTH = 8
# Height of each labeled box on the track.
# Increase for taller boxes and more vertical padding around text.
TOKEN_HEIGHT = 28
# Vertical distance between stacked alternative branches.
# Increase to spread branch rows farther apart and make dense choices airier.
ROW_GAP = 22
# Blank space before the left start marker and first track content.
# Increase to push the whole diagram slightly right.
LEFT_MARGIN = 28
# Blank space after the final track content and right end marker.
# Increase to give the diagram more room at the end.
RIGHT_MARGIN = 28
# Space reserved above the top track for the rule title.
# Increase if titles feel too close to the diagram body.
TOP_MARGIN = 56
# Space reserved below the lowest track element.
# Increase if lower loops or labels feel too tight to the SVG edge.
BOTTOM_MARGIN = 24
# Vertical slot used by the title text itself.
# Increase if the title line needs more breathing room.
TITLE_HEIGHT = 22
# Font size used for the rule title at the top of each diagram.
# Increase for a more prominent title; also increases the minimum width needed
# to avoid clipping long rule names on otherwise small diagrams.
TITLE_FONT_SIZE = 20
# Baseline of the main horizontal track within a token row.
# This normally tracks half the box height; changing it shifts line alignment.
LINE_Y_OFFSET = TOKEN_HEIGHT // 2
# Font stack used for titles and box labels.
# Change this to alter the overall typographic look of the diagrams.
FONT_FAMILY = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
# Radius for rounded line corners and branch turns.
# Increase for softer, wider arcs; decrease for tighter, sharper turns.
ROUND_RADIUS = 6
# Horizontal spacing inserted between consecutive nodes on the same track.
# Increase to open up crowded sequences and long productions.
TRACK_GAP = 18
# Radius of the rounded rectangle corners used for labeled boxes.
# Increase for softer pill-like boxes; decrease for squarer box corners.
BOX_RADIUS = 8


@dataclass(frozen=True)
class Rule:
    """
    Store one grammar rule and its parsed production expression.
    """

    name: str
    expression: "Node"

    @property
    def slug(self) -> str:
        return self.name[1:-1].replace("-", "_")


@dataclass(frozen=True)
class Node:
    """
    Represent one parsed grammar expression node.
    """


@dataclass(frozen=True)
class Symbol(Node):
    """
    Represent one token-like grammar symbol shown as a box in the diagram.
    """

    raw: str


@dataclass(frozen=True)
class Sequence(Node):
    """
    Represent an ordered sequence of grammar nodes on one track.
    """

    items: tuple[Node, ...]


@dataclass(frozen=True)
class Choice(Node):
    """
    Represent a set of alternative grammar branches.
    """

    options: tuple[Node, ...]


@dataclass(frozen=True)
class Repeat(Node):
    """
    Represent a zero-or-more repetition around one child node.
    """

    child: Node


@dataclass(frozen=True)
class Optional(Node):
    """
    Represent an optional child node with a bypass track.
    """

    child: Node


@dataclass(frozen=True)
class Layout:
    """
    Store the size and baseline position for one rendered node.
    """

    width: int
    height: int
    baseline: int


def main() -> int:
    """
    Parse CLI flags and run the grammar diagram generator.
    """
    parser = argparse.ArgumentParser(
        description="Generate SVG syntax diagrams from docs/src/reference/grammar.md."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated diagrams or Markdown embed section are stale",
    )
    args = parser.parse_args()
    return generate(check=args.check)


def extract_grammar_block(markdown: str) -> str:
    """
    Extract the fenced grammar block from the reference Markdown file.
    """
    match = TEXT_BLOCK_PATTERN.search(markdown)
    if match is None:
        raise ValueError(f"could not find a ```text grammar block in {GRAMMAR_DOC}")
    return match.group(1).strip()


def parse_rules(grammar_text: str) -> list[Rule]:
    """
    Parse the BNF-like grammar text into structured rule objects.
    """
    rules: list[Rule] = []
    current_name: str | None = None
    current_alternatives: list[Node] = []

    for raw_line in grammar_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        rule_match = RULE_PATTERN.match(line)
        if rule_match:
            if current_name is not None:
                rules.append(Rule(current_name, combine_choices(current_alternatives)))
            current_name = rule_match.group(1)
            current_alternatives = [parse_expression(rule_match.group(2))]
            continue

        continuation_match = CONTINUATION_PATTERN.match(line)
        if continuation_match and current_name is not None:
            current_alternatives.append(parse_expression(continuation_match.group(1)))
            continue

        raise ValueError(f"unrecognized grammar line: {raw_line!r}")

    if current_name is not None:
        rules.append(Rule(current_name, combine_choices(current_alternatives)))

    if not rules:
        raise ValueError("no grammar rules were parsed")

    return rules


def tokenize(expression: str) -> tuple[str, ...]:
    """
    Split one grammar production into parser tokens.
    """
    tokens: list[str] = []
    i = 0
    while i < len(expression):
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char in "()[]|*":
            tokens.append(char)
            i += 1
            continue
        if char == '"':
            end = i + 1
            while end < len(expression):
                if expression[end] == '"' and expression[end - 1] != "\\":
                    break
                end += 1
            if end >= len(expression):
                raise ValueError(f"unterminated quoted token in {expression!r}")
            tokens.append(expression[i : end + 1])
            i = end + 1
            continue
        if char == "<":
            end = expression.find(">", i)
            if end == -1:
                raise ValueError(f"unterminated nonterminal in {expression!r}")
            tokens.append(expression[i : end + 1])
            i = end + 1
            continue
        end = i
        while (
            end < len(expression)
            and not expression[end].isspace()
            and expression[end] not in "()[]|*"
        ):
            end += 1
        tokens.append(expression[i:end])
        i = end
    return tuple(tokens)


def parse_expression(expression: str) -> Node:
    """
    Parse one grammar expression into a nested node tree.
    """
    tokens = tokenize(expression)
    node, position = parse_choice(tokens, 0, stop_tokens=())
    if position != len(tokens):
        raise ValueError(f"unexpected trailing tokens in {expression!r}")
    return node


def parse_choice(
    tokens: tuple[str, ...], position: int, stop_tokens: tuple[str, ...]
) -> tuple[Node, int]:
    """
    Parse a choice expression separated by `|` tokens.
    """
    options: list[Node] = []
    node, position = parse_sequence(tokens, position, stop_tokens + ("|",))
    options.append(node)

    while position < len(tokens) and tokens[position] == "|":
        node, position = parse_sequence(tokens, position + 1, stop_tokens + ("|",))
        options.append(node)

    return combine_choices(options), position


def parse_sequence(
    tokens: tuple[str, ...], position: int, stop_tokens: tuple[str, ...]
) -> tuple[Node, int]:
    """
    Parse a run of grammar items that appear in sequence.
    """
    items: list[Node] = []
    while position < len(tokens) and tokens[position] not in stop_tokens:
        node, position = parse_item(tokens, position)
        items.append(node)

    return combine_sequence(items), position


def parse_item(tokens: tuple[str, ...], position: int) -> tuple[Node, int]:
    """
    Parse one grammar item and an optional trailing repeat marker.
    """
    node, position = parse_atom(tokens, position)
    if position < len(tokens) and tokens[position] == "*":
        return Repeat(node), position + 1
    return node, position


def parse_atom(tokens: tuple[str, ...], position: int) -> tuple[Node, int]:
    """
    Parse one atomic symbol or grouped sub-expression.
    """
    token = tokens[position]

    if token == "(":
        node, position = parse_choice(tokens, position + 1, stop_tokens=(")",))
        if position >= len(tokens) or tokens[position] != ")":
            raise ValueError("missing closing ')' in grammar expression")
        return node, position + 1

    if token == "[":
        node, position = parse_choice(tokens, position + 1, stop_tokens=("]",))
        if position >= len(tokens) or tokens[position] != "]":
            raise ValueError("missing closing ']' in grammar expression")
        return Optional(node), position + 1

    if token in {")", "]", "|", "*"}:
        raise ValueError(f"unexpected token {token!r} in grammar expression")

    return Symbol(token), position + 1


def combine_sequence(items: list[Node]) -> Node:
    """
    Collapse parsed sequence items into the smallest useful node shape.
    """
    flattened: list[Node] = []
    for item in items:
        if isinstance(item, Sequence):
            flattened.extend(item.items)
        else:
            flattened.append(item)

    if not flattened:
        return Sequence(())
    if len(flattened) == 1:
        return flattened[0]
    return Sequence(tuple(flattened))


def combine_choices(options: list[Node]) -> Node:
    """
    Collapse parsed choice options into the smallest useful node shape.
    """
    flattened: list[Node] = []
    for option in options:
        if isinstance(option, Choice):
            flattened.extend(option.options)
        else:
            flattened.append(option)

    if not flattened:
        raise ValueError("choice cannot be empty")
    if len(flattened) == 1:
        return flattened[0]
    return Choice(tuple(flattened))


def token_kind(symbol: Symbol) -> str:
    """
    Classify a symbol so it can be styled appropriately in the diagram.
    """
    token = symbol.raw
    if token.startswith("<") and token.endswith(">"):
        return "nonterminal"
    if token.startswith('"') and token.endswith('"'):
        return "terminal"
    if token == "empty":
        return "meta"
    return "operator"


def display_token(symbol: Symbol) -> str:
    """
    Convert a symbol into the human-facing label shown inside a box.
    """
    token = symbol.raw
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    return token


def token_width(symbol: Symbol) -> int:
    """
    Estimate the box width needed to render a symbol label clearly.
    """
    label = display_token(symbol)
    return max(40, len(label) * CHAR_WIDTH + 18)


def title_width(rule: Rule) -> int:
    """
    Estimate the horizontal space needed to render the rule title safely.
    """
    return max(0, len(rule.name) * CHAR_WIDTH + TITLE_FONT_SIZE)


# Extra height added above a repeated item for the loop-back bypass path.
# Increase to lift the recursive loop higher above the repeated box.
REPEAT_TOP_PAD = 22
# Extra height reserved below a repeated item.
# Increase only if future repeat shapes need more room underneath.
REPEAT_BOTTOM_PAD = 0
# Vertical gap between the main track and the repeat bypass track.
# Increase to separate the upper loop more clearly from the repeated box.
REPEAT_SKIP_GAP = 12
# Horizontal padding on both sides of a repeated node inside its loop frame.
# Increase to make the loop branch farther before and after the repeated item.
REPEAT_SIDE_PAD = 18
# Horizontal padding used when branches split from or rejoin the main track.
# Increase to make choice diagrams fan out and merge more gradually.
CHOICE_SIDE_PAD = 18


def alt_width(tokens: tuple[Symbol, ...]) -> int:
    """
    Compute the horizontal space needed for one production alternative.
    """
    return layout_sequence(tokens).width


def row_top_pad(tokens: tuple[Symbol, ...]) -> int:
    """
    Return the extra space above a row when repeated items need a bypass track.
    """
    return layout_sequence(tokens).baseline - LINE_Y_OFFSET


def row_bottom_pad(tokens: tuple[Symbol, ...]) -> int:
    """
    Return the extra space below a row for future vertical track needs.
    """
    layout = layout_sequence(tokens)
    return layout.height - layout.baseline - LINE_Y_OFFSET


def row_height(tokens: tuple[Symbol, ...]) -> int:
    """
    Compute the full vertical footprint of one rendered alternative row.
    """
    return layout_sequence(tokens).height


def render_svg(rule: Rule) -> str:
    """
    Dispatch a grammar rule to the appropriate SVG layout strategy.
    """
    layout = layout_node(rule.expression)
    diagram_width = LEFT_MARGIN + TRACK_GAP + layout.width + TRACK_GAP + RIGHT_MARGIN
    minimum_title_width = LEFT_MARGIN + title_width(rule) + RIGHT_MARGIN
    width = max(diagram_width, minimum_title_width)
    height = TOP_MARGIN + TITLE_HEIGHT + layout.height + BOTTOM_MARGIN
    start_x = LEFT_MARGIN
    node_x = LEFT_MARGIN + TRACK_GAP
    track_end_x = node_x + layout.width + TRACK_GAP
    node_y = TOP_MARGIN
    baseline_y = node_y + layout.baseline

    svg = build_svg_header(rule, width, height)
    draw_line(svg, start_x, baseline_y, node_x, baseline_y)
    render_node(svg, rule.expression, node_x, node_y)
    draw_line(svg, node_x + layout.width, baseline_y, track_end_x, baseline_y)
    draw_endcaps(svg, start_x, track_end_x, baseline_y)
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def layout_node(node: Node) -> Layout:
    """
    Compute the layout box and baseline for one grammar node.
    """
    if isinstance(node, Symbol):
        return Layout(token_width(node), TOKEN_HEIGHT, LINE_Y_OFFSET)

    if isinstance(node, Sequence):
        return layout_sequence(node.items)

    if isinstance(node, Choice):
        option_layouts = [layout_node(option) for option in node.options]
        width = (
            CHOICE_SIDE_PAD
            + max(layout.width for layout in option_layouts)
            + CHOICE_SIDE_PAD
        )
        baseline = option_layouts[0].baseline
        total_height = option_layouts[0].height
        for layout in option_layouts[1:]:
            total_height += ROW_GAP + layout.height
        return Layout(width, total_height, baseline)

    if isinstance(node, Repeat):
        child = layout_node(node.child)
        width = REPEAT_SIDE_PAD + child.width + REPEAT_SIDE_PAD
        height = REPEAT_TOP_PAD + child.height + REPEAT_BOTTOM_PAD
        baseline = REPEAT_TOP_PAD + child.baseline
        return Layout(width, height, baseline)

    if isinstance(node, Optional):
        child = layout_node(node.child)
        width = REPEAT_SIDE_PAD + child.width + REPEAT_SIDE_PAD
        height = REPEAT_TOP_PAD + child.height + REPEAT_BOTTOM_PAD
        baseline = REPEAT_TOP_PAD + child.baseline
        return Layout(width, height, baseline)

    raise TypeError(f"unsupported node type: {type(node)!r}")


def layout_sequence(items: tuple[Node, ...]) -> Layout:
    """
    Compute the layout box and baseline for a sequence of nodes.
    """
    if not items:
        return Layout(0, TOKEN_HEIGHT, LINE_Y_OFFSET)

    layouts = [layout_node(item) for item in items]
    baseline = max(layout.baseline for layout in layouts)
    below = max(layout.height - layout.baseline for layout in layouts)
    height = baseline + below
    width = sum(layout.width for layout in layouts) + TRACK_GAP * max(0, len(items) - 1)
    return Layout(width, height, baseline)


def build_svg_header(rule: Rule, width: int, height: int) -> list[str]:
    """
    Build the common SVG header and outer frame for one diagram.
    """
    title_y = 28
    return [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="title-{rule.slug} desc-{rule.slug}">'
        ),
        f'<title id="title-{rule.slug}">{escape(rule.name)} syntax diagram</title>',
        (
            f'<desc id="desc-{rule.slug}">Syntax diagram for {escape(rule.name)} '
            "generated from the grammar reference.</desc>"
        ),
        (
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
            'rx="18" fill="#fbfcfe" stroke="#d6deea"/>'
        ),
        (
            f'<text x="{LEFT_MARGIN}" y="{title_y}" fill="#14324a" '
            f'font-family="{FONT_FAMILY}" font-size="20" font-weight="700">'
            f"{escape(rule.name)}</text>"
        ),
    ]


def render_node(svg: list[str], node: Node, x: int, y: int) -> None:
    """
    Render one grammar node into an existing SVG buffer.
    """
    if isinstance(node, Symbol):
        render_symbol_node(svg, node, x, y)
        return

    if isinstance(node, Sequence):
        render_sequence(svg, node.items, x, y)
        return

    if isinstance(node, Choice):
        render_choice_node(svg, node, x, y)
        return

    if isinstance(node, Repeat):
        render_repeat_node(svg, node, x, y)
        return

    if isinstance(node, Optional):
        render_optional_node(svg, node, x, y)
        return

    raise TypeError(f"unsupported node type: {type(node)!r}")


def render_sequence(svg: list[str], items: tuple[Node, ...], x: int, y: int) -> None:
    """
    Render one sequence of grammar nodes into an existing SVG buffer.
    """
    layout = layout_sequence(items)
    baseline_y = y + layout.baseline
    cursor_x = x

    for index, item in enumerate(items):
        item_layout = layout_node(item)
        item_y = y + layout.baseline - item_layout.baseline
        render_node(svg, item, cursor_x, item_y)
        cursor_x += item_layout.width

        if index != len(items) - 1:
            next_x = cursor_x + TRACK_GAP
            draw_line(svg, cursor_x, baseline_y, next_x, baseline_y)
            cursor_x = next_x


def render_symbol_node(svg: list[str], symbol: Symbol, x: int, y: int) -> None:
    """
    Render one atomic symbol node.
    """
    draw_symbol(svg, x, y, token_width(symbol), y + LINE_Y_OFFSET, symbol)


def render_choice_node(svg: list[str], choice: Choice, x: int, y: int) -> None:
    """
    Render a nested choice node with shared entry and exit spines.
    """
    layout = layout_node(choice)
    option_layouts = [layout_node(option) for option in choice.options]
    branch_left_x = x
    content_x = x + CHOICE_SIDE_PAD
    branch_right_x = x + layout.width
    main_y = y + layout.baseline
    option_y = y

    for index, option in enumerate(choice.options):
        option_layout = option_layouts[index]
        child_y = option_y
        child_baseline_y = child_y + option_layout.baseline
        render_node(svg, option, content_x, child_y)

        if index == 0:
            draw_line(svg, branch_left_x, main_y, content_x, main_y)
            draw_line(
                svg, content_x + option_layout.width, main_y, branch_right_x, main_y
            )
        else:
            draw_down_branch(svg, branch_left_x, main_y, content_x, child_baseline_y)
            draw_up_branch(
                svg,
                content_x + option_layout.width,
                child_baseline_y,
                branch_right_x,
                main_y,
            )

        option_y += option_layout.height + ROW_GAP


def render_repeat_node(svg: list[str], repeat: Repeat, x: int, y: int) -> None:
    """
    Render a zero-or-more repeated node with a bypass track and arrow.
    """
    child_layout = layout_node(repeat.child)
    child_x = x + REPEAT_SIDE_PAD
    child_y = y + REPEAT_TOP_PAD
    baseline_y = child_y + child_layout.baseline
    branch_left_x = x
    branch_right_x = child_x + child_layout.width + REPEAT_SIDE_PAD

    draw_line(svg, branch_left_x, baseline_y, child_x, baseline_y)
    draw_line(svg, child_x + child_layout.width, baseline_y, branch_right_x, baseline_y)
    render_node(svg, repeat.child, child_x, child_y)
    draw_repeat_bypass(
        svg, branch_left_x, baseline_y, branch_right_x, child_y - REPEAT_SKIP_GAP
    )
    arrow_x = branch_left_x + ROUND_RADIUS + 18
    svg.append(
        f'<polygon points="{arrow_x + 10},{child_y - REPEAT_SKIP_GAP - 5} '
        f"{arrow_x},{child_y - REPEAT_SKIP_GAP} "
        f'{arrow_x + 10},{child_y - REPEAT_SKIP_GAP + 5}" fill="#6a7d95"/>'
    )


def render_optional_node(svg: list[str], optional: Optional, x: int, y: int) -> None:
    """
    Render an optional node with a rounded bypass track and no arrow.
    """
    child_layout = layout_node(optional.child)
    child_x = x + REPEAT_SIDE_PAD
    child_y = y + REPEAT_TOP_PAD
    baseline_y = child_y + child_layout.baseline
    branch_left_x = x
    branch_right_x = child_x + child_layout.width + REPEAT_SIDE_PAD

    draw_line(svg, branch_left_x, baseline_y, child_x, baseline_y)
    draw_line(svg, child_x + child_layout.width, baseline_y, branch_right_x, baseline_y)
    render_node(svg, optional.child, child_x, child_y)
    draw_repeat_bypass(
        svg, branch_left_x, baseline_y, branch_right_x, child_y - REPEAT_SKIP_GAP
    )


def draw_symbol(
    svg: list[str], x: int, y: int, width_px: int, center_y: int, symbol: Symbol
) -> None:
    """
    Draw one boxed terminal, nonterminal, or operator symbol.
    """
    kind = token_kind(symbol)
    label = escape(display_token(symbol))
    fill, stroke, text_fill = style_for_token(kind)
    svg.append(
        f'<rect x="{x}" y="{y}" width="{width_px}" height="{TOKEN_HEIGHT}" '
        f'rx="{BOX_RADIUS}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    )
    svg.append(
        f'<text x="{x + width_px / 2}" y="{center_y + 5}" '
        f'text-anchor="middle" fill="{text_fill}" font-family="{FONT_FAMILY}" '
        f'font-size="13">{label}</text>'
    )


def draw_repeat(
    svg: list[str], x: int, y: int, width_px: int, center_y: int, symbol: Symbol
) -> None:
    """
    Draw a zero-or-more bypass track around a repeated symbol.
    """
    branch_left_x = x
    box_x = x + REPEAT_SIDE_PAD
    box_right_x = box_x + width_px
    branch_right_x = box_right_x + REPEAT_SIDE_PAD
    skip_y = y - REPEAT_SKIP_GAP

    draw_line(svg, branch_left_x, center_y, box_x, center_y)
    draw_line(svg, box_right_x, center_y, branch_right_x, center_y)

    draw_symbol(svg, box_x, y, width_px, center_y, Symbol(symbol.raw))
    draw_repeat_bypass(svg, branch_left_x, center_y, branch_right_x, skip_y)
    arrow_x = branch_left_x + ROUND_RADIUS + 18
    svg.append(
        f'<polygon points="{arrow_x + 10},{skip_y - 5} {arrow_x},{skip_y} {arrow_x + 10},{skip_y + 5}" '
        'fill="#6a7d95"/>'
    )


def draw_line(svg: list[str], x1: int, y1: int, x2: int, y2: int) -> None:
    """
    Draw one straight track segment.
    """
    svg.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="#6a7d95" stroke-width="2"/>'
    )


def draw_path(svg: list[str], d: str) -> None:
    """
    Draw one curved SVG path segment for rounded railroad connections.
    """
    svg.append(f'<path d="{d}" fill="none" stroke="#6a7d95" stroke-width="2"/>')


def draw_repeat_bypass(
    svg: list[str], left_x: int, main_y: int, right_x: int, skip_y: int
) -> None:
    """
    Draw the rounded bypass path used for zero-or-more repetition.
    """
    radius = min(ROUND_RADIUS, main_y - skip_y, (right_x - left_x) // 4)
    d = (
        f"M {left_x} {main_y} "
        f"L {left_x} {skip_y + radius} "
        f"A {radius} {radius} 0 0 1 {left_x + radius} {skip_y} "
        f"L {right_x - radius} {skip_y} "
        f"A {radius} {radius} 0 0 1 {right_x} {skip_y + radius} "
        f"L {right_x} {main_y}"
    )
    draw_path(svg, d)


def draw_down_branch(
    svg: list[str], branch_x: int, top_y: int, target_x: int, target_y: int
) -> None:
    """
    Draw the rounded left-side branch that fans a choice downward.
    """
    radius = min(ROUND_RADIUS, target_y - top_y, target_x - branch_x)
    d = (
        f"M {branch_x} {top_y} "
        f"L {branch_x} {target_y - radius} "
        f"A {radius} {radius} 0 0 0 {branch_x + radius} {target_y} "
        f"L {target_x} {target_y}"
    )
    draw_path(svg, d)


def draw_up_branch(
    svg: list[str], start_x: int, start_y: int, branch_x: int, top_y: int
) -> None:
    """
    Draw the rounded right-side branch that merges a choice upward.
    """
    radius = min(ROUND_RADIUS, start_y - top_y, branch_x - start_x)
    d = (
        f"M {start_x} {start_y} "
        f"L {branch_x - radius} {start_y} "
        f"A {radius} {radius} 0 0 0 {branch_x} {start_y - radius} "
        f"L {branch_x} {top_y}"
    )
    draw_path(svg, d)


def draw_endcaps(svg: list[str], start_x: int, end_x: int, y: int) -> None:
    """
    Draw the start and end markers at the ends of the main track.
    """
    svg.append(f'<circle cx="{start_x - 6}" cy="{y}" r="4.5" fill="#6a7d95"/>')
    svg.append(f'<circle cx="{end_x + 6}" cy="{y}" r="4.5" fill="#6a7d95"/>')


def style_for_token(kind: str) -> tuple[str, str, str]:
    """
    Return the fill, stroke, and text colors for one symbol class.
    """
    if kind == "nonterminal":
        return ("#e9f2ff", "#8cb0e8", "#123a6b")
    if kind == "terminal":
        return ("#eef7ea", "#8fbc8f", "#204b24")
    if kind == "meta":
        return ("#fff4df", "#f0c16a", "#7a4d00")
    return ("#f5f7fb", "#c9d2de", "#445468")


def build_generated_markdown(rules: list[Rule]) -> str:
    """
    Build the generated Markdown section that embeds every SVG diagram.
    """
    lines = [
        MARKER_START,
        "",
        "## Syntax diagrams",
        "",
    ]

    for rule in rules:
        lines.extend(
            [
                f"### `{rule.name}`",
                "",
                f"![Syntax diagram for {rule.name}](grammar-diagrams/{rule.slug}.svg)",
                "",
            ]
        )

    lines.append(MARKER_END)
    lines.append("")
    return "\n".join(lines)


def update_markdown(markdown: str, generated_section: str) -> str:
    """
    Insert or replace the generated diagram section in the grammar page.
    """
    pattern = re.compile(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}\n?",
        re.DOTALL,
    )
    if pattern.search(markdown):
        return pattern.sub(generated_section, markdown)

    insertion_point = markdown.find("## Notes")
    if insertion_point == -1:
        raise ValueError(f"could not find an insertion point in {GRAMMAR_DOC}")

    prefix = markdown[:insertion_point].rstrip() + "\n\n"
    suffix = markdown[insertion_point:]
    return prefix + generated_section + "\n" + suffix


def generate(check: bool) -> int:
    """
    Generate diagrams or verify that the checked-in outputs are up to date.
    """
    original_markdown = GRAMMAR_DOC.read_text(encoding="utf-8")
    grammar_text = extract_grammar_block(original_markdown)
    rules = parse_rules(grammar_text)

    rendered_svgs = {rule.slug: render_svg(rule) for rule in rules}
    updated_markdown = update_markdown(
        original_markdown, build_generated_markdown(rules)
    )

    expected_changes: list[str] = []
    if updated_markdown != original_markdown:
        expected_changes.append(str(GRAMMAR_DOC.relative_to(ROOT)))

    for slug, content in rendered_svgs.items():
        target = DIAGRAM_DIR / f"{slug}.svg"
        existing = target.read_text(encoding="utf-8") if target.exists() else None
        if existing != content:
            expected_changes.append(str(target.relative_to(ROOT)))

    if check:
        if expected_changes:
            for path in expected_changes:
                print(path)
            print("generated grammar diagrams are out of date", file=sys.stderr)
            return 1
        return 0

    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    GRAMMAR_DOC.write_text(updated_markdown, encoding="utf-8")

    current_files = {path.name for path in DIAGRAM_DIR.glob("*.svg")}
    wanted_files = {f"{slug}.svg" for slug in rendered_svgs}
    for stale in current_files - wanted_files:
        (DIAGRAM_DIR / stale).unlink()

    for slug, content in rendered_svgs.items():
        (DIAGRAM_DIR / f"{slug}.svg").write_text(content, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
