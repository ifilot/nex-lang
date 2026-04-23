from dataclasses import dataclass, field

import numpy as np


@dataclass
class NexArray:
    """
    Runtime representation of a NEX array value.
    """

    element_type: str
    storage: object = field(init=False)

    def __post_init__(self):
        if self.element_type == "int":
            self.storage = np.array([], dtype=np.int64)
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
        if self.element_type == "int":
            if size <= current:
                self.storage = self.storage[:size].copy()
                return
            padding = np.zeros(size - current, dtype=np.int64)
            self.storage = np.concatenate((self.storage, padding))
            return

        if size <= current:
            del self.storage[size:]
            return
        self.storage.extend([""] * (size - current))

    def reset(self) -> None:
        """
        Replace every existing element with that type's default value.
        """
        if self.element_type == "int":
            self.storage.fill(0)
            return

        for i in range(self.length()):
            self.storage[i] = ""

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
        if self.element_type == "int":
            return repr(self.storage.tolist())
        return repr(self.storage)
