# Expressions And Operators

## Overview

Expressions produce values. The current core includes:

- literals
- variable references
- parenthesized expressions
- unary expressions
- binary expressions

## Operator precedence

From highest precedence to lowest:

1. primary expressions: literals, variables, parenthesized expressions
2. unary operators: `-`, `!`
3. multiplicative operators: `*`, `/`, `%`
4. additive operators: `+`, `-`
5. comparison and equality operators: `<`, `>`, `<=`, `>=`, `==`, `!=`

Binary operators at the same precedence level associate from left to right.

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

## Addition

Binary `+` supports:

- `int + int`
- `str + str`

Mixed-type addition is not allowed.

## Comparisons

The operators `<`, `>`, `<=`, and `>=` support:

- `int` compared with `int`
- `str` compared with `str`

Mixed-type ordering comparisons are runtime errors.

## Equality

The operators `==` and `!=` require both operands to have the same runtime
type.

Examples:

```nex
print(4 == 4);
print("a" != "b");
print(true == false);
```

