from dataclasses import dataclass, field


@dataclass
class NexArray:
    """
    Runtime representation of a NEX array value.
    """

    element_type: str
    storage: object = field(init=False)

    def __post_init__(self):
        if self.element_type == "int":
            self.storage = []
            return
        if self.element_type == "str":
            self.storage = []
            return
        raise RuntimeError(f"unsupported array element type: {self.element_type}")

    @property
    def declared_type(self) -> str:
        return f"array<{self.element_type}>"

    def length(self) -> int:
        return len(self.storage)

    def resize(self, size: int) -> None:
        if size < 0:
            raise ValueError("size must be non-negative")

        current = self.length()
        if size <= current:
            del self.storage[size:]
            return

        default = 0 if self.element_type == "int" else ""
        self.storage.extend([default] * (size - current))

    def reset(self) -> None:
        """
        Replace every existing element with that type's default value.
        """
        default = 0 if self.element_type == "int" else ""
        for i in range(self.length()):
            self.storage[i] = default

    def get(self, index: int):
        return self.storage[self._normalize_index(index)]

    def set(self, index: int, value: object) -> None:
        self.storage[self._normalize_index(index)] = value

    def _normalize_index(self, index: int) -> int:
        if index < 0:
            index += self.length()
        if index < 0 or index >= self.length():
            raise IndexError(index)
        return index

    def __repr__(self) -> str:
        return repr(self.storage)

    def __eq__(self, other) -> bool:
        if not isinstance(other, NexArray):
            return NotImplemented
        return self.element_type == other.element_type and self.storage == other.storage
