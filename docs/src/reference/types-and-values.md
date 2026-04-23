# Types And Values

NEX currently has three first-class value types:

- `int`
- `str`
- `bool`

Variables are declared with an explicit type and keep that type for their
lifetime. That makes NEX an explicitly typed language core with strong runtime
type checks. A variable is not just a name; it is a name bound to a value of a
particular type, and later assignments must respect that binding.

This design keeps the language small while still illustrating an important
concept in language implementation: values have kinds, and the interpreter must
enforce the rules that say which operations are valid for which kinds of
values.

## Integers

`int` values are whole numbers.

```nex
int a = 10;
int b = -3;
print(a + b);
```

Integers support the usual arithmetic operators. In the current core, `-`, `*`,
`/`, and `%` are integer-only operators, while `+` also has a second meaning
for string concatenation. That split is intentional: it keeps the operator set
small while showing that the same surface symbol can have different meanings
depending on operand types.

## Strings

`str` values are double-quoted text literals.

```nex
str left = "he";
str right = "llo";
print(left + right);
```

Strings can be concatenated with `+`, compared for equality, and also compared
with the ordering operators. This is a useful teaching choice because it shows
that not all comparisons are numeric: some values can be ordered
lexicographically.

## Booleans

`bool` values are either `true` or `false`.

```nex
bool ready = true;

if (!ready) {
    print("wait");
} else {
    print("go");
}
```

Conditions in `if`, `while`, and `for` must evaluate to `bool`. NEX does not
use implicit truthiness. In other words, NEX does not silently treat integers
or strings as conditions. A condition must really be boolean, which keeps the
rules easy to explain and easy to check.

## Variable declarations

Variables are introduced with an explicit type, a name, and an initializer.

```nex
int count = 0;
str name = "nex";
bool ok = true;
```

The initializer expression must evaluate to a value that matches the declared
type. Redeclaring a variable in the same scope is a runtime error. Together,
these rules make declarations do two things at once: they create a new binding
and they immediately give it a valid initial value.

## Assignment

Assignment updates an existing variable.

```nex
int x = 1;
x = x + 2;
print(x);
```

Assignments must preserve the declared variable type. Assigning a `str` to an
`int` variable, for example, is a runtime error. Assigning to a variable name
that has not been declared is also a runtime error. This means NEX does not
allow assignment to invent new bindings implicitly; declarations and
assignments have separate roles.
