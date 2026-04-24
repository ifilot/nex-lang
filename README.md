# NEX

[![PyPI Version](https://img.shields.io/pypi/v/nex-lang)](https://pypi.org/project/nex-lang/)
[![Python Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fifilot%2Fnex-lang%2Fmaster%2Fpyproject.toml&query=%24.project.requires-python&label=python)](https://github.com/ifilot/nex-lang/blob/master/pyproject.toml)
[![Unit Tests](https://github.com/ifilot/nex-lang/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/ifilot/nex-lang/actions/workflows/unit-tests.yml)
[![Docs](https://github.com/ifilot/nex-lang/actions/workflows/docs.yml/badge.svg)](https://github.com/ifilot/nex-lang/actions/workflows/docs.yml)
![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue)

`NEX` is a small experimental programming language implemented in Python.

![Nex logo](img/nex-lang-logo-256.png)

The project currently includes:

- a lexer
- a recursive-descent parser
- a tree-walking interpreter
- a small CLI runner
- an `mdBook` documentation site under `docs/`

## Example

```nex
int x = 0;
while(x < 10) {
    print(x);
    x = x + 1;
}
```

## Installation

Install the package in editable mode:

```bash
python -m pip install -e .
```

Once published, the package can be installed from PyPI with:

```bash
python -m pip install nex-lang
```

Install development dependencies as well:

```bash
python -m pip install -e ".[dev]"
```

Enable the local pre-commit hook to block commits when formatting, linting, or
ASCII-only checks fail:

```bash
pre-commit install
```

## Running Programs

The package exposes a `nexlang` command:

```bash
nexlang examples/hello.nex
```

You can check the installed CLI version with:

```bash
nexlang --version
```

You can also run the CLI module directly:

```bash
python -m nex.cli examples/hello.nex
```

The CLI also supports a few inspection and reporting options:

```bash
nexlang tokens examples/hello.nex
nexlang ast examples/hello.nex
nexlang --times examples/hello.nex
nexlang run --times --color examples/hello.nex
```

- `tokens` prints the token stream and stops after lexing.
- `ast` prints the parsed syntax tree and stops after parsing.
- `--times` shows a formatted timing summary for the lexer, parser,
  interpreter, and total runtime after the program finishes.
- `--color` (or `-c`) colorizes the timing summary. It is intended to be used
  together with `--times`.

## Documentation

The language reference lives in the `mdBook` project under `docs/`.

Build it locally with:

```bash
python scripts/generate_grammar_diagrams.py
~/.cargo/bin/mdbook build docs
```

The grammar page diagrams are generated from the fenced grammar block in
`docs/src/reference/grammar.md`, so rerun the generator whenever that grammar
changes.

Once GitHub Pages is enabled for this repository, the published book will be
available at:

```text
https://ifilot.github.io/nex-lang/
```

## VS Code Syntax Highlighting

A lightweight VS Code syntax-highlighting extension for `.nex` files lives at:

```text
editors/vscode/nex-syntax
```

If you are using VS Code through WSL, you can expose that extension to the WSL
server with:

```bash
cd editors/vscode/nex-syntax
mkdir -p ~/.vscode-server/extensions && ln -s "$(pwd)" ~/.vscode-server/extensions/local.nex-syntax
```

After that, reload the VS Code window.

## Releases

PyPI releases are published from Git tags that start with `v`. The published
package name is `nex-lang`. The installed CLI command remains `nexlang`.

Before publishing, the release workflow checks that the tag matches
`nex.__version__` exactly, for example `v0.3.0`, and that the package version
does not already exist on PyPI.

For local releases, create the tag through the guarded helper:

```bash
python scripts/create_release_tag.py
```

The helper creates `v<nex.__version__>` only after checking that the local Git
tag does not already exist and that the package version is still available on
PyPI.

## Testing

Run the test suite with:

```bash
python -m pytest -q tests
```

Using `python -m pytest` is the most reliable form across environments and editors.

## Linting

Check linting, formatting, and ASCII-only text files with:

```bash
python -m ruff check .
python -m ruff format --check .
python scripts/check_ascii.py
```

## Project Structure

```text
nex/
  lexer/         Tokenization
  parser/        Recursive-descent parser
  interpreter/   AST nodes, environment, and interpreter
  cli.py         Command-line entry point
tests/           Unit tests
examples/        Example programs
```
