# Lexical Structure

## Source files

A NEX program begins life as plain text. Before the parser can understand
statements and expressions, the lexer first breaks that text into tokens such
as identifiers, keywords, literals, operators, and punctuation. This chapter
describes the raw textual shape of the language: what counts as a comment, what
counts as a name, and which symbols the lexer recognizes.

Whitespace is mostly insignificant in NEX. It is used to separate tokens when
needed, but it does not change the meaning of the program by itself. Newlines
do not terminate statements; semicolons do. This gives the language a simple,
statement-oriented feel that is easy to tokenize and parse.

## Comments

NEX supports line comments introduced by `#`. Anything from `#` to the end of
the current line is ignored by the lexer, which means comments are part of the
source text but not part of the program's meaning.

```nex
int x = 1; # trailing comment

# whole-line comment
print(x);
```

## Identifiers

Identifiers are used for variable names. In the current core, they are the
names by which values are introduced into the environment and later looked up
again in expressions and assignments.

An identifier may start with a letter or `_`. After the first character, it
may contain letters, digits, and `_`.

Identifiers and keywords are case-sensitive. For example, `count`, `Count`,
and `COUNT` are different names, and only lowercase `print` is the `print`
keyword.

Examples:

- `x`
- `counter`
- `message`
- `_name`
- `with_internal_underscore`

Keywords such as `fn`, `return`, `void`, `int`, `bool`, `str`, `array`, `if`,
`else`, `while`, `for`, `true`, and `false` are reserved. They have fixed
meaning in the grammar and therefore cannot be used as identifiers.

## Literals

The current core supports three literal kinds. Literals are source forms that
directly produce values without first looking them up from a variable:

- integer literals such as `0` and `42`
- string literals such as `"hello"`
- boolean literals `true` and `false`

```nex
print(42);
print("hello");
print(true);
```

## Punctuation and operators

The lexer recognizes the following punctuation and operators. Together, they
define the basic shape of NEX expressions, declarations, blocks, and control
flow:

- `(` `)` `{` `}` `;`
- `=` `+` `-` `*` `/` `%` `^`
- `&&` `||`
- `<` `>` `<=` `>=` `==` `!=`
- `!`

Example:

```nex
int score = 10;

if (score >= 10 && score != 15) {
    print("good");
}
```
