from nex import __version__

from .nex_array import NexArray


def nex_print(msg: str) -> None:
    print(msg)


def nex_print_inline(msg: str) -> None:
    print(msg, end="")


def nex_version() -> str:
    return str(__version__)


def nex_input() -> str:
    return input()


def nex_intstr(value: int) -> str:
    """
    Convert an integer value to its string representation.
    """
    return str(value)


def nex_strint(value: str) -> int:
    """
    Convert a string to an integer, falling back to 0 on invalid input.
    """
    try:
        return int(value)
    except ValueError:
        return 0


def nex_resize(arr: NexArray, size: int) -> None:
    """
    Resize an array in place to the requested logical length.
    """
    arr.resize(size)


def nex_length(arr: NexArray) -> int:
    """
    Return the current logical length of an array.
    """
    return arr.length()


def nex_reset(arr: NexArray) -> None:
    """
    Reset every array element to the default value for its element type.
    """
    arr.reset()
