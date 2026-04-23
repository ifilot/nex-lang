# Built-in Functions

Built-in functions are names provided directly by the language runtime. They do
not need to be declared before use.

Built-in functions behave like ordinary function calls:

- they are called by name with parentheses
- their arguments are evaluated before the call
- they may return a value
- they may also have side effects such as printing or reading input

Unlike user-defined functions, their implementation lives in the interpreter
rather than in a NEX function body.

The <code class="language-nex">any</code> type shown above is not a general
source-level wildcard type. It is reserved for selected built-in functions such
as <code class="language-nex">print(...)</code> and
<code class="language-nex">print_inline(...)</code>. User programs currently
declare parameters, variables, and return types with the ordinary concrete
types of the language.

## General Built-ins

### `print`

<code class="language-nex">print(any msg) -> void</code>

<code class="language-nex">print(...)</code> evaluates its argument and writes
the resulting value followed by a newline.

```nex
print("hello");
print(1 + 2);
```

This is the main output function in NEX.

### `print_inline`

<code class="language-nex">print_inline(any msg) -> void</code>

<code class="language-nex">print_inline(...)</code> writes its argument without
appending a newline.

```nex
print_inline("name: ");
print("Ada");
```

This is useful for prompts and inline output.

### `version`

<code class="language-nex">version() -> str</code>

<code class="language-nex">version()</code> returns the interpreter version as
a string.

```nex
print(version());
```

### `input`

<code class="language-nex">input() -> str</code>

<code class="language-nex">input()</code> reads one line of user input and
returns it as a string.

```nex
print_inline("What is your name? > ");
str name = input();
print("Hello, " + name);
```

If input cannot be read, execution stops with a runtime error.

## Array Built-ins

### `resize`

<code class="language-nex">resize(array&lt;int&gt; arr, int size) -> void</code>

<code class="language-nex">resize(array&lt;str&gt; arr, int size) -> void</code>

<code class="language-nex">resize(...)</code> changes the logical length of an
array in place.

```nex
array<int> nums;
resize(nums, 3);
```

When an array grows, new slots are filled with the default value for the array
element type. For `array<int>`, that value is `0`. For `array<str>`, that
value is `""`.

This builtin can also be called with method syntax:

```nex
nums.resize(3);
```

### `length`

<code class="language-nex">length(array&lt;int&gt; arr) -> int</code>

<code class="language-nex">length(array&lt;str&gt; arr) -> int</code>

<code class="language-nex">length(...)</code> returns the current logical
length of an array.

```nex
array<int> nums;
nums.resize(3);
print(length(nums));
print(nums.length());
```

The method-style and function-style forms are equivalent.

### `reset`

<code class="language-nex">reset(array&lt;int&gt; arr) -> void</code>

<code class="language-nex">reset(array&lt;str&gt; arr) -> void</code>

<code class="language-nex">reset(...)</code> replaces every existing element
with the default value for the array element type.

```nex
array<int> nums;
resize(nums, 3);
nums[0] = 7;
nums[1] = 9;
reset(nums);
print(nums[0]);
```

For <code class="language-nex">array&lt;int&gt;</code>, the default value is
<code class="language-nex">0</code>. For
<code class="language-nex">array&lt;str&gt;</code>, the default value is
<code class="language-nex">""</code>.

This builtin can also be called with method syntax:

```nex
nums.reset();
```

## Notes

- Built-in functions are part of the runtime namespace, not special statement
  forms.
- Because function calls are expressions, a built-in function can appear in a
  variable initializer, inside another call, or as a plain expression
  statement.
- Method-style calls such as `arr.length()`, `arr.resize(3)`, and
  `arr.reset()` are alternative surface syntax for ordinary built-in function
  calls.
