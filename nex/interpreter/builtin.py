from nex import __version__


def nex_print(msg: str) -> None:
    print(msg)


def nex_print_inline(msg: str) -> None:
    print(msg, end="")


def nex_version() -> str:
    return str(__version__)


def nex_input() -> str:
    return input()
