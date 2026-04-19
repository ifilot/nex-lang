# Stabilizing The Core

The current NEX milestone is about finishing the first coherent slice of the
language before adding larger features such as functions and arrays.

That means the short-term goal is:

- define the current semantics clearly
- make parser and runtime errors consistent
- strengthen tests around edge cases and failure modes
- keep examples and docs aligned with the implementation

The core should feel boring in the best possible way: predictable,
understandable, and easy to extend.

## What "stable core" means

NEX will consider this phase wrapped up when:

- every supported construct is documented in this book
- operator behavior is specified, not implied
- scope rules are clear and tested
- CLI failures return useful diagnostics
- examples cover the supported language surface

## Non-goals for this phase

The following are intentionally out of scope while the core is being wrapped up:

- user-defined functions
- arrays or indexed collections
- advanced standard-library features
- optimization work beyond basic correctness and clarity

## Why this matters

New features are much easier to add once the small language underneath them is
well-defined. A stable core also makes it possible to answer design questions
with confidence:

- Is a behavior intentional?
- Is a parser rejection correct?
- Is a runtime error part of the language contract?

That is exactly what this book is meant to support.

