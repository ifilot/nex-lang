# Scopes And Bindings

## Lexical scope

NEX uses lexical scoping with nested block environments.

Each block creates a new scope. Variables declared in an inner scope can shadow
variables from an outer scope.

```nex
int x = 1;

if (true) {
    int x = 2;
    print(x);
}

print(x);
```

This prints:

```text
2
1
```

## Redeclaration

Redeclaring a variable in the same scope is an error.

Shadowing a variable in a nested scope is allowed.

## Assignment lookup

Assignments search outward through enclosing scopes and update the nearest
matching binding.

Assigning to an undefined variable is an error.

## For-loop scope

The current interpreter gives each `for` loop its own scope.

That means a variable declared in the initializer is available in the
condition, iteration clause, and loop body, but does not leak outside the loop.

```nex
for (int i = 0; i < 2; i = i + 1) {
    print(i);
}
```

After the loop finishes, `i` is no longer defined.

