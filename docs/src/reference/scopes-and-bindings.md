# Scopes And Bindings

## Lexical scope

NEX uses lexical scoping with nested block environments. In a lexically scoped
language, the meaning of a variable name depends on where that name appears in
the source program, not on some dynamic history of how execution arrived
there.

Each block creates a new scope. Variables declared in an inner scope can shadow
variables from an outer scope, which means the inner binding temporarily hides
the outer one while execution remains inside the block.

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

Redeclaring a variable in the same scope is an error, because one scope should
not contain two competing bindings for the same name. Shadowing a variable in a
nested scope is allowed, because the nested block is a distinct environment
with its own lifetime.

For example, this is invalid because both declarations live in the same block:

```nex
int score = 10;
int score = 20;
```

## Assignment lookup

Assignments search outward through enclosing scopes and update the nearest
matching binding. Variable reads also search outward through enclosing scopes.
This is a simple but important rule: lookup starts locally and only falls back
to outer scopes if the current one has no matching name.

```nex
int total = 1;

{
    total = total + 2;
    print(total);
}

print(total);
```

This prints:

```text
3
3
```

Assigning to an undefined variable is an error, and reading an undefined
variable is a runtime error. These checks keep the environment disciplined and
prevent names from appearing "by accident" during execution.
## For-loop scope

The current interpreter gives each `for` loop its own scope.

That means a variable declared in the initializer is available in the
condition, iteration clause, and loop body, but does not leak outside the loop.

```nex
for (int i = 0; i < 2; i = i + 1) {
    print(i);
}
```

After the loop finishes, `i` is no longer defined. This makes `for` loops a
useful example of how a language can give a syntactic construct its own local
environment.
