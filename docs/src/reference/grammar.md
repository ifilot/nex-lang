# Grammar

> Note for new readers:
> This chapter is included mainly to give a complete structural view of the
> language. You do not need to read the full grammar to start using or
> understanding NEX. If the notation feels unfamiliar, it is perfectly fine to
> skim this page and return to it later as a reference.

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

<typed-decl-core>   ::= <scalar-typed-decl-core>
                      | <array-decl-core>

<scalar-typed-decl-core> ::= <scalar-type> <identifier> "=" <expression>

<array-decl-core>   ::= <array-type> <identifier>

<type>              ::= <scalar-type> | <array-type>

<scalar-type>       ::= "int" | "str" | "bool"

<array-type>        ::= "array" "<" ( "int" | "str" ) ">"

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

<assignment-core>   ::= <assignment-target> "=" <expression>

<assignment-target> ::= <identifier> | <index-expr>

<expr-stmt>         ::= <expression> ";"

<expression>        ::= <logical-or>

<logical-or>        ::= <logical-and> ( "||" <logical-and> )*

<logical-and>       ::= <comparison> ( "&&" <comparison> )*

<comparison>        ::= <term> (( "<" | ">" | "<=" | ">=" | "==" | "!=" ) <term>)*

<term>              ::= <factor> (("+" | "-") <factor>)*

<factor>            ::= <unary> (("*" | "/" | "%") <unary>)*

<unary>             ::= ("-" | "!") <unary>
                      | <postfix>

<postfix>           ::= <primary> ( <call-suffix> | <index-suffix> | <method-suffix> | <postfix-update> )*

<call-suffix>       ::= "(" [ <arguments> ] ")"

<index-suffix>      ::= "[" <expression> "]"

<method-suffix>     ::= "." <identifier> "(" [ <arguments> ] ")"

<postfix-update>    ::= "++" | "--"

<index-expr>        ::= <postfix> <index-suffix>

<primary>           ::= <number>
                      | <string>
                      | "true"
                      | "false"
                      | <identifier>
                      | "(" <expression> ")"

<arguments>         ::= <expression> ("," <expression>)*
```

<!-- GENERATED GRAMMAR DIAGRAMS START -->

## Syntax diagrams

### `<program>`

![Syntax diagram for <program>](grammar-diagrams/program.svg)

### `<statement>`

![Syntax diagram for <statement>](grammar-diagrams/statement.svg)

### `<typed-decl>`

![Syntax diagram for <typed-decl>](grammar-diagrams/typed_decl.svg)

### `<typed-decl-core>`

![Syntax diagram for <typed-decl-core>](grammar-diagrams/typed_decl_core.svg)

### `<scalar-typed-decl-core>`

![Syntax diagram for <scalar-typed-decl-core>](grammar-diagrams/scalar_typed_decl_core.svg)

### `<array-decl-core>`

![Syntax diagram for <array-decl-core>](grammar-diagrams/array_decl_core.svg)

### `<type>`

![Syntax diagram for <type>](grammar-diagrams/type.svg)

### `<scalar-type>`

![Syntax diagram for <scalar-type>](grammar-diagrams/scalar_type.svg)

### `<array-type>`

![Syntax diagram for <array-type>](grammar-diagrams/array_type.svg)

### `<function-decl>`

![Syntax diagram for <function-decl>](grammar-diagrams/function_decl.svg)

### `<parameters>`

![Syntax diagram for <parameters>](grammar-diagrams/parameters.svg)

### `<parameter>`

![Syntax diagram for <parameter>](grammar-diagrams/parameter.svg)

### `<return-type>`

![Syntax diagram for <return-type>](grammar-diagrams/return_type.svg)

### `<return-stmt>`

![Syntax diagram for <return-stmt>](grammar-diagrams/return_stmt.svg)

### `<if-stmt>`

![Syntax diagram for <if-stmt>](grammar-diagrams/if_stmt.svg)

### `<while-stmt>`

![Syntax diagram for <while-stmt>](grammar-diagrams/while_stmt.svg)

### `<for-stmt>`

![Syntax diagram for <for-stmt>](grammar-diagrams/for_stmt.svg)

### `<for-init>`

![Syntax diagram for <for-init>](grammar-diagrams/for_init.svg)

### `<for-iter>`

![Syntax diagram for <for-iter>](grammar-diagrams/for_iter.svg)

### `<block>`

![Syntax diagram for <block>](grammar-diagrams/block.svg)

### `<assignment-stmt>`

![Syntax diagram for <assignment-stmt>](grammar-diagrams/assignment_stmt.svg)

### `<assignment-core>`

![Syntax diagram for <assignment-core>](grammar-diagrams/assignment_core.svg)

### `<assignment-target>`

![Syntax diagram for <assignment-target>](grammar-diagrams/assignment_target.svg)

### `<expr-stmt>`

![Syntax diagram for <expr-stmt>](grammar-diagrams/expr_stmt.svg)

### `<expression>`

![Syntax diagram for <expression>](grammar-diagrams/expression.svg)

### `<logical-or>`

![Syntax diagram for <logical-or>](grammar-diagrams/logical_or.svg)

### `<logical-and>`

![Syntax diagram for <logical-and>](grammar-diagrams/logical_and.svg)

### `<comparison>`

![Syntax diagram for <comparison>](grammar-diagrams/comparison.svg)

### `<term>`

![Syntax diagram for <term>](grammar-diagrams/term.svg)

### `<factor>`

![Syntax diagram for <factor>](grammar-diagrams/factor.svg)

### `<unary>`

![Syntax diagram for <unary>](grammar-diagrams/unary.svg)

### `<postfix>`

![Syntax diagram for <postfix>](grammar-diagrams/postfix.svg)

### `<call-suffix>`

![Syntax diagram for <call-suffix>](grammar-diagrams/call_suffix.svg)

### `<index-suffix>`

![Syntax diagram for <index-suffix>](grammar-diagrams/index_suffix.svg)

### `<method-suffix>`

![Syntax diagram for <method-suffix>](grammar-diagrams/method_suffix.svg)

### `<postfix-update>`

![Syntax diagram for <postfix-update>](grammar-diagrams/postfix_update.svg)

### `<index-expr>`

![Syntax diagram for <index-expr>](grammar-diagrams/index_expr.svg)

### `<primary>`

![Syntax diagram for <primary>](grammar-diagrams/primary.svg)

### `<arguments>`

![Syntax diagram for <arguments>](grammar-diagrams/arguments.svg)

<!-- GENERATED GRAMMAR DIAGRAMS END -->

## Notes

- Function calls are postfix expressions, not statements in their own right.
  That is why built-in functions such as `print(...)` and `input()` can appear
  in an initializer, inside another call, or as a plain expression statement.
- Array declarations are syntactically distinct from scalar declarations:
  `array<int> arr;` is valid, while array declarations with initializers are
  currently rejected.
- Postfix `++` and `--` are also part of the expression grammar. In the current
  implementation they are restricted to variable operands.
- Postfix expressions now also include array indexing such as `arr[-1]` and
  method-style calls such as `arr.length()`, `arr.resize(3)`, or `arr.reset()`.
- `for` reuses declaration, assignment, and expression forms in its header, but
  without extra trailing semicolons inside those clauses.
- The grammar allows repeated comparison operators syntactically. Runtime type
  rules still determine whether a particular chained comparison is meaningful.
- Logical operators are part of the expression grammar, with `&&` binding more
  tightly than `||`.

For the meaning of each construct, the surrounding reference chapters remain
the authoritative explanation. This chapter is mainly a compact syntax map.
