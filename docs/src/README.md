# The NEX Book

NEX is a small experimental programming language implemented in Python.

This book is the home for the language definition of the current NEX core.
For now, the focus is not on expanding the language surface, but on making the
existing core explicit, testable, and stable.

At the moment, the implemented language includes:

- typed variable declarations for `int`, `str`, and `bool`
- arithmetic and comparison expressions
- boolean literals and unary operators
- block statements with lexical scoping
- `if`, `while`, and `for`
- a built-in `print(...)` statement

Here is a small complete program:

```nex
int x = 0;

while (x < 5) {
    print(x);
    x = x + 1;
}
```

The reference chapters describe the language as it exists today. When the
implementation and the book disagree, that is a bug to fix rather than a reason
to guess.

