# Diagnostics and errors

NEX reports failures in three main phases:

- lexing
- parsing
- runtime evaluation

The command-line runner reports these as:

- `lex error: ...`
- `parse error: ...`
- `runtime error: ...`

This separation matters for learners. A lexing error means the raw text could
not even be tokenized correctly. A parse error means the tokens were valid, but
they did not form a sentence that matches the grammar. A runtime error means
the program was syntactically valid, but something about its execution violated
the language rules.

## Source locations

When a source location is available, diagnostics include the line and column:

```text
parse error: line 1, column 9: expect ';'
```

The current implementation reports source positions using the start of the
relevant token or expression.
That choice makes diagnostics easier to relate back to the program text, since
the reported position points to where the problematic construct begins.

## Message style

Diagnostic messages in the current core follow a simple convention:

- lowercase wording
- no trailing period
- source position handled separately from the message text

This convention keeps diagnostics short and regular. The exception object
contains the message and the source location, while the CLI decides how to add
the phase prefix.

Examples:

```text
lex error: line 1, column 1: unexpected character '@'
parse error: line 1, column 14: expect ')'
runtime error: line 3, column 17: cannot assign value of type str to variable 'x' of type int
```

## Parse errors

Parse errors describe violations of the grammar, such as:

- missing semicolons
- missing closing parentheses
- invalid `for` initializer clauses
- missing expressions

These are errors in the *shape* of the program. They tell you that the parser
cannot build a meaningful abstract syntax tree from the given tokens.

For example, this program is missing a semicolon after the declaration:

```nex
int x = 1
print(x);
```

## Runtime errors

Runtime errors describe programs that are syntactically valid but semantically
invalid at execution time, such as:

- using an undefined variable
- assigning a value of the wrong type
- calling a function with the wrong number of arguments
- calling a function with arguments of the wrong type
- returning a value of the wrong type from a function
- using a non-boolean condition in `if`, `while`, or `for`
- applying an operator to unsupported operand types
- writing a chained comparison such as `1 < 2 < 3`, which becomes `(1 < 2) < 3`

These are errors in the *meaning* of the program as it runs. They are
especially valuable in a small interpreter because they show how a language can
stay simple while still enforcing strong semantic rules.

For example, this program is syntactically valid but tries to assign a string
to an integer variable:

```nex
int count = 3;
count = "three";
```

## Stability note

The exact wording of diagnostics may still evolve, but line/column reporting
and phase-specific CLI errors are now part of the intended user experience of
the current NEX core.
