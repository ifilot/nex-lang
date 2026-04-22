# NEX

[![Unit Tests](https://github.com/ifilot/nex-lang/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/ifilot/nex-lang/actions/workflows/unit-tests.yml)
[![Docs](https://github.com/ifilot/nex-lang/actions/workflows/docs.yml/badge.svg)](https://github.com/ifilot/nex-lang/actions/workflows/docs.yml)

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

## Documentation

The language reference lives in the `mdBook` project under `docs/`.

Build it locally with:

```bash
~/.cargo/bin/mdbook build docs
```

Once GitHub Pages is enabled for this repository, the published book will be
available at:

```text
https://ifilot.github.io/nex-lang/
```

## Releases

PyPI releases are published from Git tags that start with `v`, for example:

```text
v0.2.0
```

The published package name is `nex-lang`. The installed CLI command remains
`nexlang`.

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

## Current Status

This is an early interpreter project and the language is still evolving. The
syntax is intentionally simple and currently leans toward a small C-like
language.
