from .builtin import nex_input, nex_print, nex_print_inline, nex_version
from .function import BuiltinFunction, Function


class NexFunctionStoreError(Exception):
    def __init__(self, message: str):
        self.message = message


class FunctionStore:
    """
    Keeps track of all the functions that have been defined
    """

    def __init__(self):
        """
        Default initializer
        """
        self.functions = {}
        self._load_builtin_functions()

    def declare_function(self, func: Function):
        overloads = self.functions.setdefault(func.callee, [])
        if any(existing.param_types == func.param_types for existing in overloads):
            signature = ", ".join(func.param_types)
            raise NexFunctionStoreError(
                f"function `{func.callee}` with signature ({signature}) is already defined"
            )
        overloads.append(func)

    def lookup_function(self, callee: str):
        if callee in self.functions:
            return self.functions[callee]
        else:
            raise NexFunctionStoreError(f"undefined function `{callee}`")

    def _load(self, func):
        self.declare_function(func)

    def _load_builtin_functions(self):
        # print function
        self._load(
            BuiltinFunction(
                "print",
                (("any", "msg"),),  # never forget the trailing comma!
                "void",
                nex_print,
            )
        )

        # print without newline function
        self._load(
            BuiltinFunction(
                "print_inline",
                (("any", "msg"),),  # never forget the trailing comma!
                "void",
                nex_print_inline,
            )
        )

        # version function
        self._load(
            BuiltinFunction(
                "version",
                (),  # empty tuple
                "str",
                nex_version,
            )
        )

        # version function
        self._load(
            BuiltinFunction(
                "input",
                (),  # empty tuple
                "str",
                nex_input,
            )
        )
