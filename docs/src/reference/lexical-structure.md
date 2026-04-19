# Lexical Structure

## Source files

A NEX program is plain text source code composed of statements.

Whitespace is ignored except where it separates tokens. Newlines do not end
statements by themselves; semicolons do.

## Comments

NEX supports line comments introduced by `#`.

Anything from `#` to the end of the current line is ignored by the lexer.

```nex
int x = 1; # trailing comment

# whole-line comment
print(x);
```

## Identifiers

Identifiers are used for variable names.

Examples:

- `x`
- `counter`
- `message`

Keywords such as `int`, `bool`, `str`, `if`, `else`, `while`, `for`, `print`,
`true`, and `false` are reserved and cannot be used as identifiers.

## Literals

The current core supports three literal kinds:

- integer literals such as `0` and `42`
- string literals such as `"hello"`
- boolean literals `true` and `false`

## Punctuation and operators

The lexer recognizes the following punctuation and operators:

- `(` `)` `{` `}` `;`
- `=` `+` `-` `*` `/` `%`
- `<` `>` `<=` `>=` `==` `!=`
- `!`

