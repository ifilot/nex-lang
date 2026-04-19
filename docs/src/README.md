# The NEX Book

NEX is a small experimental programming language implemented in Python. It is
deliberately modest in size: the goal is not to compete with production
languages, but to make the core ideas of language design easy to see. If you
are curious about how a programming language works internally, NEX is intended
to be small enough to understand and large enough to feel real.

This book is the home for the current NEX language definition. At this stage,
the project is focused less on adding many new features and more on making the
existing core explicit, consistent, and pleasant to learn from. In practice,
that means the language is being treated as a carefully documented teaching
language: every feature should have a clear purpose, a clear rule, and a clear
error when used incorrectly.

The current NEX core has several defining traits. It uses explicit variable
declarations with strong runtime type checks, so programs must make their
intent visible and type mismatches are reported instead of being silently
coerced. It has first-class values of type `int`, `str`, and `bool`, block-
based lexical scoping, expression evaluation with operator precedence, and a
small set of control-flow constructs built around boolean conditions. In other
words, it is a compact, C-like language core designed to show how values,
variables, scopes, and statements fit together.

Here is a small complete program:

```nex
int x = 0;

while (x < 5) {
    print(x);
    x = x + 1;
}
```

The reference chapters describe the language as it exists today. They focus on
source-level behavior rather than interpreter internals, but they are written
with implementation-minded readers in mind. When the implementation and the
book disagree, that is a bug to fix rather than a reason to guess.

The current implementation also provides structured diagnostics for lexing,
parsing, and runtime failures. These diagnostics report the phase together with
source line and column information when available, which makes NEX a better
tool both for writing small programs and for studying how a language reports
errors in a disciplined way.
