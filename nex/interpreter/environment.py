from nex.common import NexRuntimeError


class Environment:
    """
    Stores the environment of the interpreter
    """

    def __init__(self):
        """
        Default initializer (empty dictionary)
        """
        self.values = [{}]

    def push(self):
        """
        Push a new environment onto the stack
        """
        self.values.append({})

    def pop(self):
        """
        Pop an environment from the stack
        """
        if len(self.values) == 1:
            raise RuntimeError("Cannot pop global environment")
        self.values.pop()

    def declare(self, name, declared_type, value, *, line=None, column=None):
        """
        Declare a new variable
        """
        if name in self.values[-1]:
            raise NexRuntimeError(
                f"redeclaration of variable '{name}' in the current scope",
                line=line,
                column=column,
            )
        self.values[-1][name] = {"type": declared_type, "value": value}

    def assign(
        self,
        name,
        value,
        *,
        line=None,
        column=None,
        value_line=None,
        value_column=None,
    ):
        """
        Assign a value to a variable
        """
        for env in reversed(self.values):
            if name in env:
                binding = env[name]
                if not self._matches_type(binding["type"], value):
                    raise NexRuntimeError(
                        f"cannot assign value of type {self._runtime_type_name(value)} "
                        f"to variable '{name}' of type {binding['type']}",
                        line=value_line if value_line is not None else line,
                        column=value_column if value_column is not None else column,
                    )
                binding["value"] = value
                return
        raise NexRuntimeError(f"undefined variable '{name}'", line=line, column=column)

    def lookup(self, name, *, line=None, column=None):
        """
        Look up the value associated to a variable
        """
        for env in reversed(self.values):
            if name in env:
                return env[name]["value"]
        raise NexRuntimeError(f"undefined variable '{name}'", line=line, column=column)

    def _matches_type(self, declared_type, value):
        if declared_type == "int":
            return type(value) is int
        if declared_type == "str":
            return type(value) is str
        if declared_type == "bool":
            return type(value) is bool

        raise RuntimeError(f"Unknown type: {declared_type}")

    def _runtime_type_name(self, value):
        if type(value) is int:
            return "int"
        if type(value) is str:
            return "str"
        if type(value) is bool:
            return "bool"

        return type(value).__name__
