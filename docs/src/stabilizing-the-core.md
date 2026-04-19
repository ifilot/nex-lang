# Stabilizing The Core

The current NEX milestone is about finishing the first coherent slice of the
language before adding larger features such as functions and arrays. In a
teaching language, a stable core matters even more than a broad feature set. A
small language becomes genuinely useful when its rules are predictable, its
examples match its implementation, and its failures teach something instead of
feeling arbitrary.

For NEX, stabilizing the core means defining the semantics clearly, making
parser and runtime errors consistent, strengthening tests around edge cases and
failure modes, and keeping the documentation aligned with the implementation.
The core should feel boring in the best possible way: predictable,
understandable, and easy to extend.

## What "stable core" means

NEX will consider this phase wrapped up when every supported construct is
documented in this book, operator behavior is specified rather than implied,
scope rules are clear and tested, CLI failures return useful diagnostics, and
the examples cover the supported language surface.

The project now has structured lex, parse, and runtime errors with source
locations, which is an important part of making the core feel stable instead of
fragile.

## Non-goals for this phase

The following are intentionally out of scope while the core is being wrapped
up: user-defined functions, arrays or indexed collections, advanced standard-
library features, and optimization work beyond basic correctness and clarity.
The point of this phase is not to make NEX bigger. It is to make the current
language small, clear, and trustworthy.

## Why this matters

New features are much easier to add once the language underneath them is
well-defined. A stable core also makes it possible to answer design questions
with confidence: Is a behavior intentional? Is a parser rejection correct? Is a
runtime error part of the language contract? That is exactly what this book is
meant to support.
