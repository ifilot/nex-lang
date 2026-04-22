# Built-in Functions

Built-in functions are names provided directly by the language runtime. They do
not need to be declared before use.

Built-in functions behave like ordinary function calls:

- they are called by name with parentheses
- their arguments are evaluated before the call
- they may return a value
- they may also have side effects such as printing or reading input

Unlike user-defined functions, their implementation lives in the interpreter
rather than in a NEX function body.

At the moment, NEX provides these built-in functions:

- `print(any msg) -> void`
- `print_inline(any msg) -> void`
- `version() -> str`
- `input() -> str`

## List

### `print(any msg) -> void`

`print(...)` evaluates its argument and writes the resulting value followed by a
newline.

```nex
print("hello");
print(1 + 2);
```

This is the main output function in NEX.

### `print_inline(any msg) -> void`

`print_inline(...)` writes its argument without appending a newline.

```nex
print_inline("name: ");
print("Ada");
```

This is useful for prompts and inline output.

### `version() -> str`

`version()` returns the interpreter version as a string.

```nex
print(version());
```

### `input() -> str`

`input()` reads one line of user input and returns it as a string.

```nex
print_inline("What is your name? > ");
str name = input();
print("Hello, " + name);
```

If input cannot be read, execution stops with a runtime error.

## Notes

- Built-in functions are part of the runtime namespace, not special statement
  forms.
- Because function calls are expressions, a built-in function can appear in a
  variable initializer, inside another call, or as a plain expression
  statement.
