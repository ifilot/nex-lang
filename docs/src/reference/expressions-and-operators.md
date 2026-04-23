# Expressions And Operators

## Overview

Expressions produce values. The current core includes:

- literals
- variable references
- parenthesized expressions
- unary expressions
- postfix expressions
- binary expressions

Expressions are the computational side of the language. They are the parts of a
program that answer questions such as "what value does this literal have?",
"what value is stored in this variable?", or "what is the result of combining
these two operands with an operator?" In the interpreter, expressions are
evaluated recursively, which is why precedence and grouping rules matter so
much.

That said, "expression" in NEX does not mean "pure computation only". An
expression always produces a value, but some expressions may also have side
effects while they are being evaluated. Function calls are the clearest example:
`print("hi")` is an expression even though evaluating it writes output. Postfix
`++` and `--` behave the same way: they produce a value and update a variable
as part of that evaluation. In other words, NEX currently allows impure
expressions.

## Operator precedence

From highest precedence to lowest:

1. primary expressions: literals, variables, parenthesized expressions
2. postfix operators: function call `(...)`, index access `[...]`, method call `.name(...)`, postfix increment `++`, postfix decrement `--`
3. unary operators: `-`, `!`
4. multiplicative operators: `*`, `/`, `%`
5. additive operators: `+`, `-`
6. comparison and equality operators: `<`, `>`, `<=`, `>=`, `==`, `!=`
7. logical AND: `&&`
8. logical OR: `||`

Binary operators at the same precedence level associate from left to right.
This precedence structure is a compact way of saying which expression trees the
parser is supposed to build when several operators appear together.

For example:

```nex
print(2 + 3 * 4);
print((2 + 3) * 4);
```

For comparison and equality operators, this left-to-right rule also applies to
chains. For example, `1 < 2 < 3` is parsed as `(1 < 2) < 3`, not as a special
"between" form. Since `1 < 2` produces a `bool`, the second `<` then attempts
to compare `bool` with `int`, which is a runtime error.

Postfix operators bind more tightly than unary operators. For example, `-f()`
is parsed as `-(f())`, not as `(-f)()`.

## Postfix operators

The current postfix operators are:

- function call: `name(...)`
- index access: `arr[i]`
- method call: `arr.name(...)`
- postfix increment: `x++`
- postfix decrement: `x--`

Function calls are described in more detail in
[Functions And Return](functions-and-return.md). The key idea here is that
postfix operators attach to an already-parsed primary expression and therefore
have the highest operator precedence in the language core.

### Index access

Index access reads a value from an indexed receiver expression.

```nex
int first = arr[0];
int last = arr[-1];
```

Negative indices count from the back. This means `arr[-1]` refers to the last
element, `arr[-2]` to the second-to-last element, and so on.

### Method calls

Method-style calls are postfix expressions attached to a receiver:

```nex
arr.resize(100);
arr.reset();
int size = arr.length();
```

This syntax is currently used for array operations such as resizing, resetting,
and length queries.

Method calls in NEX use a uniform function call style. That means the receiver
expression becomes the first argument of an ordinary function call. For
example, `arr.length()` behaves like `length(arr)`, and `arr.resize(100)`
behaves like `resize(arr, 100)`. In the same way, `arr.reset()` behaves like
`reset(arr)`.

### Postfix increment and decrement

`++` and `--` currently require a variable operand of type `int`.

Examples:

```nex
int i = 1;
print(i++);
print(i);
```

The first `print` outputs the original value. After that evaluation finishes,
the variable has been updated by one. `--` works the same way but subtracts one.

Because these operators update program state while also producing a value, they
are impure expressions rather than pure arithmetic.

## Unary operators

### Numeric negation

Unary `-` requires an `int` operand.

```nex
print(-3);
```

### Boolean negation

Unary `!` requires a `bool` operand.

```nex
print(!false);
```

Using unary operators with the wrong type is a runtime error.

## Arithmetic operators

`-`, `*`, `/`, and `%` require `int` operands on both sides.

```nex
print(8 - 3);
print(8 / 3);
print(8 % 3);
```

The current interpreter performs integer division for `/`.
More precisely, division truncates the result toward zero.

## Addition

Binary `+` supports:

- `int + int`
- `str + str`

Mixed-type addition is not allowed.
The interpreter does not try to guess what you meant by combining unrelated
types. Instead, it reports a runtime error.

Examples:

```nex
print(3 + 4);
print("Hello, " + "NEX");
```

## Comparisons

The operators `<`, `>`, `<=`, and `>=` support:

- `int` compared with `int`
- `str` compared with `str`

Mixed-type ordering comparisons are runtime errors.

Because comparisons associate from left to right, chained comparisons do not
have a special combined meaning.

```nex
print(1 < 2 < 3);
```

The example above is parsed as `(1 < 2) < 3`. The first comparison evaluates
to `true`, and the second comparison then fails because ordering comparisons do
not support `bool` operands.

## Equality

The operators `==` and `!=` require both operands to have the same runtime
type.

Examples:

```nex
print(4 == 4);
print("a" != "b");
print(true == false);
```

Mixed-type equality is a runtime error rather than automatically evaluating to
`false`. This keeps equality semantically strict and avoids surprising implicit
conversions.

## Logical operators

The operators `&&` and `||` require `bool` operands.

Examples:

```nex
print(true && false);
print(false || true);
print(true && (1 < 2));
```

Logical operators use short-circuit evaluation:

- `a && b` evaluates `b` only if `a` evaluates to `true`
- `a || b` evaluates `b` only if `a` evaluates to `false`

This matters both for efficiency and for behavior. For example, `false &&
missing()` does not attempt to evaluate `missing()`, because the left-hand side
already determines the result.
