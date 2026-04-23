class NexError(RuntimeError):
    def __init__(
        self, message: str, *, line: int | None = None, column: int | None = None
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"line {self.line}, column {self.column}: {self.message}"
        return self.message


class NexLexError(NexError):
    pass


class NexParseError(NexError):
    pass


class NexRuntimeError(NexError):
    pass


class NexIndexError(NexRuntimeError):
    pass
