from nex.common import NexRuntimeError

from .environment import Environment
from .function import BuiltinFunction, UserFunction
from .function_store import FunctionStore, NexFunctionStoreError


class NexReturnSignal(Exception):
    """
    Custom return signal to unroll to the call site
    """

    def __init__(self, value):
        self.value = value


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
        self.function_store = FunctionStore()

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

    def exec_Return(self, node):
        """
        Raise a NexReturnSignal with the result of the expression evaluation
        """
        # assess that we are
        raise NexReturnSignal(self.eval(node.expr) if node.expr is not None else None)

    def exec_FuncDecl(self, node):
        """
        Declare a new function
        """
        func = UserFunction(node.callee, node.arguments, node.return_type, node.body)
        try:
            self.function_store.declare_function(func)
        except NexFunctionStoreError as e:
            raise NexRuntimeError(e.message, line=node.line, column=node.column)

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
        raise NotImplementedError(f"no eval for `{type(node).__name__}`")

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
                    f"cannot apply unary operator `{node.op}` to type "
                    f"{self._runtime_type_name(val)}; expected bool",
                    line=node.line,
                    column=node.column,
                )
            return not val

        if node.op == "-":
            if type(val) is not int:
                raise NexRuntimeError(
                    f"cannot apply unary operator `{node.op}` to type "
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

        if node.op == "&&":
            if type(left) is not bool:
                raise NexRuntimeError(
                    f"operator `&&` expects bool operands, got "
                    f"{self._runtime_type_name(left)} and <unevaluated>",
                    line=node.line,
                    column=node.column,
                )
            if not left:
                return False

            right = self.eval(node.right)
            if type(right) is not bool:
                raise NexRuntimeError(
                    f"operator `&&` expects bool operands, got "
                    f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
                    line=node.line,
                    column=node.column,
                )
            return left and right

        if node.op == "||":
            if type(left) is not bool:
                raise NexRuntimeError(
                    f"operator `||` expects bool operands, got "
                    f"{self._runtime_type_name(left)} and <unevaluated>",
                    line=node.line,
                    column=node.column,
                )
            if left:
                return True

            right = self.eval(node.right)
            if type(right) is not bool:
                raise NexRuntimeError(
                    f"operator `||` expects bool operands, got "
                    f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
                    line=node.line,
                    column=node.column,
                )
            return left or right

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
                f"operator `{node.op}` expects matching int or str operands, got "
                f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
                line=node.line,
                column=node.column,
            )

        if node.op in ("==", "!="):
            if type(left) is not type(right):
                raise NexRuntimeError(
                    f"operator `{node.op}` expects operands of the same type, got "
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

    def eval_FuncCall(self, node):
        """
        Evaluates a function call
        """
        # try to grab the function definition from the function store
        try:
            func = self.function_store.lookup_function(node.callee)
        except NexFunctionStoreError as e:
            raise NexRuntimeError(e.message, line=node.line, column=node.column)

        # check whether all variables match
        nrargs = len(node.arguments)
        nrparams = len(func.params)
        if nrargs != nrparams:
            raise NexRuntimeError(
                f"incorrect number of arguments provided {nrargs} != {nrparams}",
                line=node.line,
                column=node.column,
            )

        # evaluate all argument expressions
        argvalues = []
        for arg in node.arguments:
            argvalues.append(self.eval(arg))

        # check all parameter types
        for param, arg in zip(func.params, argvalues):
            if param[0] != "any" and not self._matches_type(param[0], arg):
                argtype = self._runtime_type_name(arg)
                raise NexRuntimeError(
                    f"param `{param[1]}` has the wrong type, encountered `{argtype}` while expected `{param[0]}`",
                    line=node.line,
                    column=node.column,
                )

        # call a user-defined function
        if isinstance(func, UserFunction):
            self.env.push()
            for param, arg in zip(func.params, argvalues):
                self.env.declare(param[1], param[0], arg)

            try:
                for stmt in func.body:
                    self.exec(stmt)
            except NexReturnSignal as ret:
                if not self._matches_type(func.return_type, ret.value):
                    argtype = self._runtime_type_name(ret.value)
                    raise NexRuntimeError(
                        f"return value has wrong type, expected `{func.return_type}` while got `{argtype}`",
                        line=node.line,
                        column=node.column,
                    )
                return ret.value
            finally:
                self.env.pop()

            # if no return value was encountered, the return value is "void" and it
            # should be explicitly checked then that the function returns this
            if not self._matches_type(func.return_type, None):
                raise NexRuntimeError(
                    f"non-void function `{func.callee}` returned void",
                    line=node.line,
                    column=node.column,
                )

            return None

        # call a builtin function
        if isinstance(func, BuiltinFunction):
            try:
                ret = func.call(argvalues)
            except NexRuntimeError:
                raise
            except Exception as exc:
                raise NexRuntimeError(
                    f"builtin function `{func.callee}` failed: {exc}",
                    line=node.line,
                    column=node.column,
                ) from exc
            if not self._matches_type(func.return_type, ret):
                argtype = self._runtime_type_name(ret)
                raise NexRuntimeError(
                    f"return value has wrong type, expected `{func.return_type}` while got `{argtype}`",
                    line=node.line,
                    column=node.column,
                )
            return ret

        raise RuntimeError("unknown function subtype")

    def eval_Postfix(self, node):
        """
        Evaluate a postfix increment/decrement expression. The expression
        returns the original value and updates the variable as a side effect.
        """
        if not hasattr(node.expr, "name"):
            raise NexRuntimeError(
                f"postfix operator `{node.op}` expects a variable operand",
                line=node.line,
                column=node.column,
            )

        current = self.eval(node.expr)
        if type(current) is not int:
            raise NexRuntimeError(
                f"cannot apply postfix operator `{node.op}` to type "
                f"{self._runtime_type_name(current)}; expected int",
                line=node.line,
                column=node.column,
            )

        delta = 1 if node.op == "++" else -1
        self.env.assign(
            node.expr.name,
            current + delta,
            line=node.line,
            column=node.column,
        )
        return current

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
        if declared_type == "void":
            return val is None

        raise NexRuntimeError(f"unknown type: `{declared_type}`")

    def _runtime_type_name(self, val: object):
        if type(val) is int:
            return "int"
        if type(val) is str:
            return "str"
        if type(val) is bool:
            return "bool"
        if val is None:
            return "void"

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
            f"operator `{op}` expects {expectation}, got "
            f"{self._runtime_type_name(left)} and {self._runtime_type_name(right)}",
            line=node.line,
            column=node.column,
        )
