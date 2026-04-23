from .builtin import (
    nex_input,
    nex_intstr,
    nex_length,
    nex_print,
    nex_print_inline,
    nex_reset,
    nex_resize,
    nex_strint,
    nex_version,
)
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
        Initialize the function registry and preload builtin functions.
        """
        self.functions = {}
        self._load_builtin_functions()

    def declare_function(self, func: Function):
        """
        Register one function overload under its callee name.

        Overloads may share the same name as long as their parameter-type
        signatures differ. Redeclaring an identical signature is rejected.
        """
        overloads = self.functions.setdefault(func.callee, [])
        if not isinstance(func, BuiltinFunction) and any(
            isinstance(existing, BuiltinFunction) for existing in overloads
        ):
            raise NexFunctionStoreError(
                f"cannot declare function `{func.callee}` because it conflicts with a built-in function"
            )
        if any(existing.param_types == func.param_types for existing in overloads):
            signature = ", ".join(func.param_types)
            raise NexFunctionStoreError(
                f"function `{func.callee}` with signature ({signature}) is already defined"
            )
        overloads.append(func)

    def lookup_function(self, callee: str):
        """
        Return all overloads registered for the given function name.
        """
        if callee in self.functions:
            return self.functions[callee]
        else:
            raise NexFunctionStoreError(f"undefined function `{callee}`")

    def _load(self, func):
        """
        Insert one builtin function through the normal declaration path.
        """
        self.declare_function(func)

    def _load_from_specs(self, specs):
        """
        Build builtin function objects from a compact sequence of specs.
        """
        for spec in specs:
            self._load(
                BuiltinFunction(
                    spec["callee"],
                    spec["params"],
                    spec["return_type"],
                    spec["handler"],
                )
            )

    def _load_builtin_functions(self):
        """
        Register the builtin function overload set available in every program.
        """
        self._load_from_specs(
            [
                {
                    "callee": "print",
                    "params": (("any", "msg"),),
                    "return_type": "void",
                    "handler": nex_print,
                },
                {
                    "callee": "print_inline",
                    "params": (("any", "msg"),),
                    "return_type": "void",
                    "handler": nex_print_inline,
                },
                {
                    "callee": "version",
                    "params": (),
                    "return_type": "str",
                    "handler": nex_version,
                },
                {
                    "callee": "input",
                    "params": (),
                    "return_type": "str",
                    "handler": nex_input,
                },
                {
                    "callee": "intstr",
                    "params": (("int", "value"),),
                    "return_type": "str",
                    "handler": nex_intstr,
                },
                {
                    "callee": "strint",
                    "params": (("str", "value"),),
                    "return_type": "int",
                    "handler": nex_strint,
                },
                {
                    "callee": "resize",
                    "params": (("array<int>", "arr"), ("int", "size")),
                    "return_type": "void",
                    "handler": nex_resize,
                },
                {
                    "callee": "resize",
                    "params": (("array<str>", "arr"), ("int", "size")),
                    "return_type": "void",
                    "handler": nex_resize,
                },
                {
                    "callee": "length",
                    "params": (("array<int>", "arr"),),
                    "return_type": "int",
                    "handler": nex_length,
                },
                {
                    "callee": "length",
                    "params": (("array<str>", "arr"),),
                    "return_type": "int",
                    "handler": nex_length,
                },
                {
                    "callee": "reset",
                    "params": (("array<int>", "arr"),),
                    "return_type": "void",
                    "handler": nex_reset,
                },
                {
                    "callee": "reset",
                    "params": (("array<str>", "arr"),),
                    "return_type": "void",
                    "handler": nex_reset,
                },
            ]
        )
