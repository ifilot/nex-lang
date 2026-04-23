# Statements And Control Flow

## Statements

The current NEX core supports these statement forms:

- variable declarations
- array declarations
- assignment statements
- expression statements
- function declarations
- `return`
- block statements
- `if` and `if ... else`
- `while`
- `for`

Statements are the parts of a NEX program that do work at the top level of a
block. While expressions compute values, statements use those values to declare
variables, update state, print results, or choose which block of code to
execute next. Every simple statement ends with a semicolon.

With arrays, NEX now distinguishes between:

- scalar declarations, which require an initializer
- array declarations, which create an empty array value

## Blocks

A block is a sequence of statements enclosed in braces.

```nex
{
    int x = 1;
    array<int> arr;
    print(x);
}
```

Blocks introduce a new lexical scope. This means they are not just a way to
group statements visually; they also define where local variable bindings begin
and end.

## If statements

An `if` statement requires a boolean condition.

```nex
int temperature = 18;

if (temperature < 20) {
    print("cool");
} else {
    print("warm");
}
```

Using a non-boolean condition is a runtime error. NEX treats control-flow
conditions strictly, which keeps the language behavior explicit and easy to
reason about.

## While loops

A `while` loop repeatedly executes its body while its condition evaluates to
`true`.

```nex
int i = 0;

while (i < 3) {
    print(i);
    i = i + 1;
}
```

Using a non-boolean condition is a runtime error. A `while` loop therefore
combines two important ideas at once: repeated execution and repeated
evaluation of a boolean expression.

## For loops

The supported `for` form is:

```nex
for (initializer; condition; iteration) {
    /* body */
}
```

The initializer may be:

- empty
- a typed variable declaration
- an empty array declaration
- an assignment
- an expression statement form such as `1 + 2`

The iteration clause may be:

- empty
- an assignment
- an expression statement form such as `i + 1`

The condition is mandatory and must evaluate to `bool`.

Example:

```nex
for (int i = 0; i < 3; i = i + 1) {
    print(i);
}
```

The initializer and iteration clauses reuse statement-like forms, but they do
not carry their own trailing semicolons. The semicolons inside the `for (...)`
header already separate the three clauses.

These clauses may also use expression forms, though that is usually most useful
when the expression has a side effect. For example:

```nex
int i = 0;

for (print_inline("start "); i < 3; print_inline(".")) {
    print(i);
    i = i + 1;
}
```

Using a non-boolean `for` condition is a runtime error. The current `for`
design is intentionally narrow, but it already shows the classic three-part
loop structure: setup, test, and update.

## Functions

Function declarations and `return` statements are also part of the current
statement system. They are described in more detail in
[Functions And Return](functions-and-return.md), but the short version is:

- `fn ... { ... }` introduces a named function
- function calls are expressions
- `return` stops the current function and optionally returns a value

That split is useful to keep in mind. Declaring a function is a statement, but
calling one is an expression.

Built-in functions such as `print(...)` are described separately in
[Built-in Functions](built-in-functions.md).

## Array operations in statements

Array syntax appears in both statements and expressions:

```nex
array<int> arr;
arr.resize(3);
arr[0] = 10;
int last = arr[-1];
```

Here:

- `array<int> arr;` is a declaration statement
- `arr.resize(3);` is an expression statement
- `arr[0] = 10;` is an assignment statement
- `arr[-1]` is an expression used inside an initializer
