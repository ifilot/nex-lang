from pathlib import Path

import pytest

from nex.cli import main

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
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


def test_all_examples_are_covered():
    example_filenames = {path.name for path in EXAMPLES_DIR.glob("*.nex")}
    assert example_filenames == set(EXPECTED_OUTPUTS)


@pytest.mark.parametrize(
    ("filename", "expected_output"),
    sorted(EXPECTED_OUTPUTS.items()),
)
def test_examples_produce_expected_output(filename, expected_output, capsys):
    main([str(EXAMPLES_DIR / filename)])

    captured = capsys.readouterr()
    assert captured.out == expected_output
    assert captured.err == ""
