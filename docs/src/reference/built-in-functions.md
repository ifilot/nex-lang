# Built-in Functions

Built-in functions are names provided directly by the language runtime. They do
not need to be declared before use.

At the moment, NEX has one built-in function: `print(...)`.

## Print

`print(...)` evaluates an expression and writes the resulting value.

```nex
print("hello");
print(1 + 2);
```

It is useful both practically and pedagogically: it lets small programs show
their results without needing a larger standard library.

Function calls in general are expressions, and `print(...)` is no exception.
What makes it special is simply that the name is provided by the language
itself rather than by a user-written function declaration.
