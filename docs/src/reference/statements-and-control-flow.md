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

Every simple statement ends with a semicolon.

## Print

`print(...)` evaluates an expression and writes the resulting value.

```nex
print("hello");
print(1 + 2);
```

## Blocks

A block is a sequence of statements enclosed in braces.

```nex
{
    int x = 1;
    print(x);
}
```

Blocks introduce a new lexical scope.

## If statements

An `if` statement requires a boolean condition.

```nex
if (x < 10) {
    print("small");
} else {
    print("large");
}
```

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

