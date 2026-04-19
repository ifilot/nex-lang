# Types And Values

NEX currently has three first-class value types:

- `int`
- `str`
- `bool`

Variables are declared with an explicit type and keep that type for their
lifetime.

## Integers

`int` values are whole numbers.

```nex
int a = 10;
int b = -3;
print(a + b);
```

Arithmetic operators only accept integers, except for `+`, which also supports
string concatenation.

## Strings

`str` values are double-quoted text literals.

```nex
str left = "he";
str right = "llo";
print(left + right);
```

Strings can be compared with the ordering operators and with equality
operators.

## Booleans

`bool` values are either `true` or `false`.

```nex
bool ready = true;
print(!ready);
```

Conditions in `if`, `while`, and `for` must evaluate to `bool`. NEX does not
use implicit truthiness.

## Variable declarations

Variables are introduced with an explicit type, a name, and an initializer.

```nex
int count = 0;
str name = "nex";
bool ok = true;
```

The initializer expression must evaluate to a value that matches the declared
type.

## Assignment

Assignment updates an existing variable.

```nex
int x = 1;
x = x + 2;
```

Assignments must preserve the declared variable type. Assigning a `str` to an
`int` variable, for example, is a runtime error.

