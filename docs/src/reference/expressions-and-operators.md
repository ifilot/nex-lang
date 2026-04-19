# Expressions And Operators

## Overview

Expressions produce values. The current core includes:

- literals
- variable references
- parenthesized expressions
- unary expressions
- binary expressions

Expressions are the computational side of the language. They are the parts of a
program that answer questions such as "what value does this literal have?",
"what value is stored in this variable?", or "what is the result of combining
these two operands with an operator?" In the interpreter, expressions are
evaluated recursively, which is why precedence and grouping rules matter so
much.

## Operator precedence

From highest precedence to lowest:

1. primary expressions: literals, variables, parenthesized expressions
2. unary operators: `-`, `!`
3. multiplicative operators: `*`, `/`, `%`
4. additive operators: `+`, `-`
5. comparison and equality operators: `<`, `>`, `<=`, `>=`, `==`, `!=`

Binary operators at the same precedence level associate from left to right.
This precedence structure is a compact way of saying which expression trees the
parser is supposed to build when several operators appear together.

For comparison and equality operators, this left-to-right rule also applies to
chains. For example, `1 < 2 < 3` is parsed as `(1 < 2) < 3`, not as a special
"between" form. Since `1 < 2` produces a `bool`, the second `<` then attempts
to compare `bool` with `int`, which is a runtime error.

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
