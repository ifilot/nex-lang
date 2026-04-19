# Statements And Control Flow

## Statements

The current NEX core supports these statement forms:

- variable declarations
- assignment statements
- expression statements
- `print(...)`
- block statements
- `if` and `if ... else`
- `while`
- `for`

Statements are the parts of a NEX program that do work at the top level of a
block. While expressions compute values, statements use those values to declare
variables, update state, print results, or choose which block of code to
execute next. Every simple statement ends with a semicolon.

## Print

`print(...)` evaluates an expression and writes the resulting value.

```nex
print("hello");
print(1 + 2);
```

At the moment, `print` is the only built-in operation exposed directly at the
statement level. It is useful both practically and pedagogically: it lets small
programs show their results without needing a larger standard library.

## Blocks

A block is a sequence of statements enclosed in braces.

```nex
{
    int x = 1;
    print(x);
}
```

Blocks introduce a new lexical scope. This means they are not just a way to
group statements visually; they also define where local variable bindings begin
and end.

## If statements

An `if` statement requires a boolean condition.

```nex
if (x < 10) {
    print("small");
} else {
    print("large");
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
- an assignment

The iteration clause may be:

- empty
- an assignment

The condition is mandatory and must evaluate to `bool`.

Example:

```nex
for (int i = 0; i < 3; i = i + 1) {
    print(i);
}
```

Using a non-boolean `for` condition is a runtime error. The current `for`
design is intentionally narrow, but it already shows the classic three-part
loop structure: setup, test, and update.
