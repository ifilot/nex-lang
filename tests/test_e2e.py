from pathlib import Path

import pytest

from nex.cli import main

INPUT_DIR = Path(__file__).resolve().parent / "input"
EXPECTED_OUTPUTS = {
    "fibo.nex": "1\n2\n3\n5\n8\n13\n21\n34\n55\n89\n",
    "fizzbuzz.nex": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n",
    "for.nex": "0\n1\n2\n0\n1\n2\n0\n1\n2\n",
    "grid.nex": "11\n12\n21\n22\n31\n32\n",
    "hello.nex": "Hello World\n",
    "math.nex": "13\n11\n21\n2\n",
    "scope.nex": "outer\ninner\nnested\ninner\nouter\n",
    "strings.nex": "Hello, NEX!\nordered\nexact match\ncustom target\n",
    "while.nex": "0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n",
}
EXPECTED_ERRORS = {
    "comparison.nex": (
        "6\n",
        "runtime error: line 7, column 13: operator `<` expects matching int or str operands, got bool and int\n",
    ),
}


def test_all_inputs_are_covered():
    input_filenames = {path.name for path in INPUT_DIR.glob("*.nex")}
    assert input_filenames == set(EXPECTED_OUTPUTS) | set(EXPECTED_ERRORS)


@pytest.mark.parametrize(
    ("filename", "expected_output"),
    sorted(EXPECTED_OUTPUTS.items()),
)
def test_inputs_produce_expected_output(filename, expected_output, capsys):
    main([str(INPUT_DIR / filename)])

    captured = capsys.readouterr()
    assert captured.out == expected_output
    assert captured.err == ""


@pytest.mark.parametrize(
    ("filename", "expected_output", "expected_error"),
    sorted((name, out, err) for name, (out, err) in EXPECTED_ERRORS.items()),
)
def test_inputs_produce_expected_error(
    filename, expected_output, expected_error, capsys
):
    exit_code = main([str(INPUT_DIR / filename)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == expected_output
    assert captured.err == expected_error
