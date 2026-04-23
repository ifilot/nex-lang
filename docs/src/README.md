# The NEX Book

NEX is a small interpreted programming language for learning the foundations of
programming. It emphasizes explicit types, clear control flow, and predictable
rules, so new programmers can focus on how values, variables, functions, and
scope work together.

NEX is deliberately compact. It includes the core building blocks of
programming such as integers, strings, booleans, variables, expressions,
functions, and loops, but leaves out larger abstraction systems such as
classes and first-class functions. That keeps attention on the basic patterns
of programming and on how simple constructs can be combined to solve larger
problems.

This book explains NEX as a language for learning. It aims to show not only
what programs can be written, but also why they behave the way they do.

Here is a small complete program:

```nex
int x = 0;

while (x < 5) {
    print(x);
    x++;
}
```

## Installation

Install NEX locally in editable mode:

```bash
python -m pip install -e .
```

Once published, NEX can also be installed from PyPI:

```bash
python -m pip install nex-lang
```

This installs the `nexlang` command-line runner. For example:

```bash
nexlang examples/hello.nex
```

The runner can also show intermediate views and execution timings:

```bash
nexlang tokens examples/hello.nex
nexlang ast examples/hello.nex
nexlang --times examples/hello.nex
nexlang run --times --color examples/hello.nex
```

Use `--times` to print a timing summary for lexing, parsing, interpretation,
and total execution. Add `--color` or `-c` if you want that timing table
highlighted with colors.

The reference chapters describe the language as it exists today. They focus on
source-level behavior rather than interpreter internals, but they are written
with implementation-minded readers in mind. When the implementation and the
book disagree, that is a bug to fix rather than a reason to guess.

When writing documentation, fenced <code class="language-nex">```nex</code>
blocks are highlighted automatically. Inline snippets can also be highlighted,
but inline Markdown backticks do not carry language information. For inline NEX
syntax, use raw HTML such as
<code class="language-nex">&lt;code class="language-nex"&gt;arr.length()&lt;/code&gt;</code>.

The current implementation also provides structured diagnostics for lexing,
parsing, and runtime failures. These diagnostics report the phase together with
source line and column information when available, which makes NEX a better
tool both for writing small programs and for studying how a language reports
errors in a disciplined way.
