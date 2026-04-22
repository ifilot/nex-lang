# Grammar

This chapter gives a compact view of the current NEX surface grammar. It is
meant as a structural summary for readers who want to see how the language fits
together after reading the surrounding reference chapters.

Like most practical parsers, NEX also has a few rules that are checked outside
the grammar itself. For example, `return` is only valid inside a function body,
and nested function declarations are rejected even though both are statement
forms in the general grammar.

## Surface grammar

```text
<program>           ::= <statement>* EOF

<statement>         ::= <typed-decl>
                      | <function-decl>
                      | <return-stmt>
                      | <if-stmt>
                      | <while-stmt>
                      | <for-stmt>
                      | <assignment-stmt>
                      | <expr-stmt>

<typed-decl>        ::= <typed-decl-core> ";"

<typed-decl-core>   ::= <type> <identifier> "=" <expression>

<type>              ::= "int" | "str" | "bool"

<function-decl>     ::= "fn" <identifier> "(" [ <parameters> ] ")" "->" <return-type> <block>

<parameters>        ::= <parameter> ("," <parameter>)*

<parameter>         ::= <type> <identifier>

<return-type>       ::= <type> | "void"

<return-stmt>       ::= "return" [ <expression> ] ";"

<if-stmt>           ::= "if" "(" <expression> ")" <block> [ "else" <block> ]

<while-stmt>        ::= "while" "(" <expression> ")" <block>

<for-stmt>          ::= "for" "(" <for-init> ";" <expression> ";" <for-iter> ")" <block>

<for-init>          ::= empty
                      | <typed-decl-core>
                      | <assignment-core>
                      | <expression>

<for-iter>          ::= empty
                      | <assignment-core>
                      | <expression>

<block>             ::= "{" <statement>* "}"

<assignment-stmt>   ::= <assignment-core> ";"

<assignment-core>   ::= <identifier> "=" <expression>

<expr-stmt>         ::= <expression> ";"

<expression>        ::= <logical-or>

<logical-or>        ::= <logical-and> ( "||" <logical-and> )*

<logical-and>       ::= <comparison> ( "&&" <comparison> )*

<comparison>        ::= <term> (( "<" | ">" | "<=" | ">=" | "==" | "!=" ) <term>)*

<term>              ::= <factor> (("+" | "-") <factor>)*

<factor>            ::= <unary> (("*" | "/" | "%") <unary>)*

<unary>             ::= ("-" | "!") <unary>
                      | <primary>

<primary>           ::= <number>
                      | <string>
                      | "true"
                      | "false"
                      | <function-call>
                      | <identifier>
                      | "(" <expression> ")"

<function-call>     ::= <identifier> "(" [ <arguments> ] ")"

<arguments>         ::= <expression> ("," <expression>)*
```

## Notes

- Function calls are expressions, not statements in their own right. That is
  why built-in functions such as `print(...)` and `input()` can appear in an
  initializer, inside another call, or as a plain expression statement.
- `for` reuses declaration, assignment, and expression forms in its header, but
  without extra trailing semicolons inside those clauses.
- The grammar allows repeated comparison operators syntactically. Runtime type
  rules still determine whether a particular chained comparison is meaningful.
- Logical operators are part of the expression grammar, with `&&` binding more
  tightly than `||`.

For the meaning of each construct, the surrounding reference chapters remain
the authoritative explanation. This chapter is mainly a compact syntax map.
