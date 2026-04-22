# Functions And Return

Functions let you give a name to a reusable piece of computation. They can
take typed parameters, execute a block of statements, and optionally return a
value.

In a small language like NEX, functions are especially useful because they
show several ideas at once:

- naming behavior
- introducing local parameters
- checking argument and return types
- stopping execution early with `return`

## Function declarations

A function declaration has four parts:

- the `fn` keyword
- the function name
- a parameter list
- a return type followed by a block body

The general form is:

```nex
fn name(type1 arg1, type2 arg2) -> return_type {
    /* body */
}
```

Example:

```nex
fn add(int a, int b) -> int {
    return a + b;
}
```

Parameters are typed, just like variables. That means `a` and `b` are local
names that exist only inside the function body, and each one has a declared
type.

## Calling functions

A function call uses the function name followed by parentheses.

```nex
print(add(2, 3));
```

Arguments are evaluated first, then checked against the declared parameter
types of the function. If the number of arguments is wrong, or if one of the
argument values has the wrong type, execution stops with a runtime error.

Function calls are expressions. That means a call can appear anywhere an
expression is allowed:

```nex
int x = add(2, 3);
print(add(4, 5));
add(1, 2);
```

The last example is valid even though its result is ignored. It is simply an
expression statement whose expression happens to be a function call.

## Return values

Every function declares a return type after `->`.

```nex
fn greet() -> void {
    print("hello");
    return;
}
```

```nex
fn square(int x) -> int {
    return x * x;
}
```

NEX currently supports these return types:

- `int`
- `str`
- `bool`
- `void`

A `void` function does not produce a usable value. It may use plain `return;`
to stop early, or it may reach the end of the body normally.

A non-`void` function must return a value of the declared type. Returning the
wrong kind of value is a runtime error, and falling off the end of a non-void
function is also a runtime error.

## Return statements

A `return` statement stops the current function immediately.

```nex
fn abs(int x) -> int {
    if (x < 0) {
        return -x;
    }
    return x;
}
```

This is an important rule: `return` is allowed anywhere inside a function body,
including inside nested `if`, `while`, `for`, or plain block statements that
belong to that function.

For example:

```nex
fn first_positive(int x, int y) -> int {
    if (x > 0) {
        return x;
    }
    if (y > 0) {
        return y;
    }
    return 0;
}
```

Using `return` outside a function is a parse error.

## Rules

NEX follows these rules for functions:

- function names must be unique
- parameter names must be unique within one function
- nested function declarations are not allowed
- a function must be declared before it is called
- calls must provide the correct number of arguments
- each argument must match the declared parameter type
- non-void functions must return a value of the declared type
- `return` is only allowed inside a function body

These rules keep function behavior explicit. That makes the language easier to
teach and easier to reason about, because the interpreter never has to guess
what a call or return statement was supposed to mean.

That means the following program is invalid:

```nex
hello();

fn hello() -> void {
    print("hello");
}
```

Instead, declare the function first:

```nex
fn hello() -> void {
    print("hello");
}

hello();
```
