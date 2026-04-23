# Functions and return

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

Function declarations are top-level declarations. They cannot be written inside
an `if`, `while`, `for`, plain block, or another function body.

```nex
fn top_level() -> void {
    print("ok");
}
```

This is invalid:

```nex
if (true) {
    fn nested() -> void {
        print("not allowed");
    }
}
```

The special `any` type is not part of the ordinary user-facing function type
system. It is reserved for selected built-in functions such as `print(...)`,
where the runtime intentionally accepts values of different concrete types.

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

Because function calls are expressions, they can also participate in impure
evaluation. For example, a call such as `print("hello")` both produces a value
(`void`) and performs an observable side effect by writing output.

## Function scope

User-defined functions are top-level declarations. NEX does not have closures,
so a function call does not capture or borrow local variables from the block or
function that called it.

When a function runs, it can access:

- its own parameters and local variables
- global variables that exist when the function body is executed
- globally declared functions that exist when the call is executed

This means a function can observe the current value of a global variable:

```nex
int y = 2;

fn show() -> void {
    print(y);
}

show(); # 2
y = 3;
show(); # 3
```

A function can also update a global variable:

```nex
int count = 0;

fn bump() -> void {
    count += 1;
}

bump();
print(count); # 1
```

But a function cannot see a caller's local block variables:

```nex
fn show() -> void {
    print(y); # runtime error: y is not global or local to show
}

if (true) {
    int y = 2;
    show();
}
```

The same rule applies when one function calls another. The called function
does not see the caller's local variables:

```nex
fn show() -> void {
    print(x); # runtime error
}

fn caller() -> void {
    int x = 2;
    show();
}

caller();
```

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
- `array<int>`
- `array<str>`
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

- functions may share a name if their parameter-type signatures differ
- parameter names must be unique within one function
- functions must be declared at the top level; nested function declarations are
  not allowed
- a function must be declared before it is called
- functions do not capture caller locals; they can access only their own locals
  and the live global scope
- calls must provide the correct number of arguments for some matching overload
- each argument must match the declared parameter type of the selected overload
- non-void functions must return a value of the declared type
- `return` is only allowed inside a function body

These rules keep function behavior explicit. That makes the language easier to
teach and easier to reason about, because the interpreter never has to guess
what a call or return statement was supposed to mean.

When several overloads share the same name, NEX resolves the call using the
argument count and argument types.

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
