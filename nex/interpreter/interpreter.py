from nex.common import NexRuntimeError

from .environment import Environment


class Interpreter:
    """
    Tree-walking interpreter that evaluates AST nodes and produces values.
    """

    def __init__(self):
        """
        Default constructor: builds the environment associated with the
        interpeter.
        """
        self.env = Environment()

    def run(self, program):
        """
        Run a program by evaluating the list of statements
        """
        for node in program:
            self.exec(node)

    # -------------------------------------------------------------------------
    # STATEMENT EXECUTION
    # -------------------------------------------------------------------------

    def exec(self, node):
        """
        Execute a statement, dispatch to the appropriate exec_* method based on
        the runtime type of the node.
        """
        method = getattr(self, f"exec_{type(node).__name__}", self._exec_default)
        return method(node)

    def _exec_default(self, node):
        """
        Default execution; automatically raises a NotImplementedError to inform
        the user that there is no support (yet) for this type of node.
        """
        raise NotImplementedError(f"No exec for {type(node).__name__}")

    def exec_VarDecl(self, node):
        """
        Variable declaration
        """
        val = self.eval(node.initializer)

        if self._matches_type(node.type, val):
            return self.env.declare(
                node.name,
                node.type,
                val,
                line=node.line,
                column=node.column,
            )

        raise NexRuntimeError(
            f"cannot assign expression {node.initializer} "
            f"of type {self._runtime_type_name(val)} to type {node.type}",
            line=node.initializer.line,
            column=node.initializer.column,
        )

    def exec_Assign(self, node):
        """
        Assigns a value to variable or declares and initializes a new variable
        """
        val = self.eval(node.expr)
        self.env.assign(
            node.name,
            val,
            line=node.line,
            column=node.column,
            value_line=node.expr.line,
            value_column=node.expr.column,
        )

    def exec_Print(self, node):
        """
        Built-in print function that outputs the result of an expression to the
        screen
        """
        val = self.eval(node.expr)
        print(val)

    def exec_Block(self, node):
        """
        Execute a block statement. Blocks result in scoping and variables
        declared inside a block statement shadow variables defined in a higher
        scope.
        """
        self.env.push()
        try:
            for stmt in node:
                self.exec(stmt)
        finally:
            self.env.pop()

    def exec_If(self, node):
        """
        Execute If statement.
        """
        if self._checked_condition(node.condition):
            self.exec(node.then_branch)
        elif node.else_branch is not None:
            self.exec(node.else_branch)

    def exec_While(self, node):
        """
        Execute While statements.
        """
        while self._checked_condition(node.condition):
            self.exec(node.body)

    def exec_For(self, node):
        """
        Execute For statements.
        """
        self.env.push()
        try:
            if node.init is not None:
                self.exec(node.init)
            while self._checked_condition(node.condition):
                self.exec(node.body)
                if node.iter is not None:
                    self.exec(node.iter)
        finally:
            self.env.pop()

    def exec_ExprStmt(self, node):
        """
        Execute expression; effectively does nothing.
        """
        self.eval(node.expr)

    # -------------------------------------------------------------------------
    # EXPRESSION EVALUATION
    # -------------------------------------------------------------------------

    def eval(self, node):
        """
        Dispatch to the appropriate eval_* method based on the runtime type of
        the node.
        """
        method = getattr(self, f"eval_{type(node).__name__}", self._eval_default)
        return method(node)

    def _eval_default(self, node):
        """
        Default evaluation; automatically raises a NotImplementedError to inform
        the user that there is no support (yet) for this type of node.
        """
        raise NotImplementedError(f"No eval for {type(node).__name__}")

    def eval_Literal(self, node):
        """
        Return the literal value directly.
        """
        return node.value

    def eval_Unary(self, node):
        """
        Evaluate a unary expression by first evaluating its operand, then
        applying the operator.
        """
        val = self.eval(node.expr)
        if node.op == "!":
            if type(val) is not bool:
                raise NexRuntimeError(
                    f"cannot apply unary operator '{node.op}' to type "
                    f"{self._runtime_type_name(val)}; expected bool",
                    line=node.line,
                    column=node.column,
                )
            return not val

        if node.op == "-":
            if type(val) is not int:
                raise NexRuntimeError(
                    f"cannot apply unary operator '{node.op}' to type "
                    f"{self._runtime_type_name(val)}; expected int",
                    line=node.line,
                    column=node.column,
                )
            return -val

        raise NotImplementedError(f"Unsupported operator: {node.op}")

    def eval_Binary(self, node):
        """
        Evaluate a binary expression by evaluating both operands and applying
        the operator to their values.
        """
        left = self.eval(node.left)
        right = self.eval(node.right)
        if node.op == "+":
            if self._both_of_type(left, right, int) or self._both_of_type(
                left, right, str
            ):
                return left + right
            raise NexRuntimeError(
                f"operator '+' expects int+int or str+str, got "
                f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
                line=node.line,
                column=node.column,
            )

        if node.op in ("-", "*", "/", "%"):
            self._require_matching_types(
                node, node.op, left, right, int, "int operands"
            )
            if node.op == "-":
                return left - right
            if node.op == "*":
                return left * right
            if node.op == "/":
                if right == 0:
                    raise NexRuntimeError(
                        "division by zero", line=node.line, column=node.column
                    )
                return int(left / right)
            if node.op == "%":
                if right == 0:
                    raise NexRuntimeError(
                        "division by zero", line=node.line, column=node.column
                    )
                return left % right
            return NexRuntimeError("invalid operation detected.")

        if node.op in ("<", ">", "<=", ">="):
            if self._both_of_type(left, right, int) or self._both_of_type(
                left, right, str
            ):
                if node.op == "<":
                    return left < right
                if node.op == ">":
                    return left > right
                if node.op == "<=":
                    return left <= right
                return left >= right
            raise NexRuntimeError(
                f"operator '{node.op}' expects matching int or str operands, got "
                f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
                line=node.line,
                column=node.column,
            )

        if node.op in ("==", "!="):
            if type(left) is not type(right):
                raise NexRuntimeError(
                    f"operator '{node.op}' expects operands of the same type, got "
                    f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
                    line=node.line,
                    column=node.column,
                )
            return left == right if node.op == "==" else left != right

        raise NotImplementedError(f"Unsupported operator: {node.op}")

    def eval_Variable(self, node):
        """
        Evaluates a variable and returns the value bound to it.
        """
        return self.env.lookup(node.name, line=node.line, column=node.column)

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _matches_type(self, declared_type: str, val: object):
        if declared_type == "int":
            return type(val) is int
        if declared_type == "str":
            return type(val) is str
        if declared_type == "bool":
            return type(val) is bool

        raise RuntimeError(f"Unknown type: {declared_type}")

    def _runtime_type_name(self, val: object):
        if type(val) is int:
            return "int"
        if type(val) is str:
            return "str"
        if type(val) is bool:
            return "bool"

        return type(val).__name__

    def _checked_condition(self, expr):
        val = self.eval(expr)

        if type(val) is not bool:
            t = self._runtime_type_name(val)
            raise NexRuntimeError(
                f"condition must evaluate to a bool, got {t}",
                line=expr.line,
                column=expr.column,
            )

        return val

    def _both_of_type(self, left: object, right: object, expected_type: type) -> bool:
        return type(left) is expected_type and type(right) is expected_type

    def _require_matching_types(
        self,
        node,
        op: str,
        left: object,
        right: object,
        expected_type: type,
        expectation: str,
    ) -> None:
        if self._both_of_type(left, right, expected_type):
            return

        raise NexRuntimeError(
            f"operator '{op}' expects {expectation}, got "
            f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
            line=node.line,
            column=node.column,
        )
