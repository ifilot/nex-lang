from .program import Program


class PrettyPrinter:
    """
    Printer class that outputs the AST as a visual tree.
    """

    def print_program(self, program: Program):
        lines = ["Program"]
        statements = list(program)
        for index, stmt in enumerate(statements):
            lines.extend(self.print(stmt, "", index == len(statements) - 1))
        return "\n".join(lines)

    def print(self, node, prefix="", is_last=True):
        method = getattr(self, f"print_{type(node).__name__}", self._default)
        return method(node, prefix, is_last)

    def _default(self, node, prefix="", is_last=True):
        raise NotImplementedError(f"No printer for {type(node).__name__}")

    def _branch(self, prefix, is_last, label):
        connector = "`-" if is_last else "|-"
        return f"{prefix}{connector} {label}"

    def _child_prefix(self, prefix, is_last):
        return prefix + ("   " if is_last else "|  ")

    def _render_children(self, children, prefix):
        lines = []
        for index, child in enumerate(children):
            lines.extend(self.print(child, prefix, index == len(children) - 1))
        return lines

    def _render_labeled_child(self, label, child, prefix, is_last):
        lines = [self._branch(prefix, is_last, label)]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self.print(child, child_prefix, True))
        return lines

    def print_Literal(self, node, prefix="", is_last=True):
        return [self._branch(prefix, is_last, f"Literal({node!r})")]

    def print_Unary(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, f"Unary({node.op})")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self.print(node.expr, child_prefix, True))
        return lines

    def print_Binary(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, f"Binary({node.op})")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self._render_children([node.left, node.right], child_prefix))
        return lines

    def print_Variable(self, node, prefix="", is_last=True):
        return [self._branch(prefix, is_last, f"Variable({node!r})")]

    def print_VarDecl(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, f"VarDecl({node.name})")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self.print(node.initializer, child_prefix, True))
        return lines

    def print_Assign(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, f"Assign({node.name})")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self.print(node.expr, child_prefix, True))
        return lines

    def print_Print(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, "Print")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self.print(node.expr, child_prefix, True))
        return lines

    def print_Block(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, "Block")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self._render_children(list(node), child_prefix))
        return lines

    def print_If(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, "If")]
        child_prefix = self._child_prefix(prefix, is_last)
        children = [
            ("Condition", node.condition),
            ("Then", node.then_branch),
        ]

        if node.else_branch is not None:
            children.append(("Else", node.else_branch))

        for index, (label, child) in enumerate(children):
            lines.extend(
                self._render_labeled_child(
                    label, child, child_prefix, index == len(children) - 1
                )
            )
        return lines

    def print_While(self, node, prefix="", is_last=True):
        lines = [self._branch(prefix, is_last, "While")]
        child_prefix = self._child_prefix(prefix, is_last)
        lines.extend(self._render_labeled_child("Condition", node.condition, child_prefix, False))
        lines.extend(self._render_labeled_child("Body", node.body, child_prefix, True))
        return lines
