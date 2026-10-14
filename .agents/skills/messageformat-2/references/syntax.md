# Syntax: patterns, text, literals, markup

## Contents

- Patterns and quoted patterns
- Text and escapes
- Expressions and annotations
- Literals
- Markup

## Patterns

A pattern is a sequence of text and placeholders formatted as a unit. Formatting a message (without errors) always yields the result of exactly one pattern: the simple message's pattern or the matching variant's pattern.

- **Unquoted pattern** = a simple message. Almost anything not beginning with `.` or `{{` works.
  `This is a pattern. It can include expressions like {$v} and {#bold}markup{/bold}.`
- **Quoted pattern** `{{...}}`: required when the message has declarations or `.match`; required for every variant pattern.
  ```
  .local $y = {1}
  {{This pattern must be quoted.}}
  ```
- Some characters cannot appear in an unquoted pattern; quoting avoids this.

## Text

Translatable content. Any Unicode code point is allowed except surrogates U+D800-U+DFFF. `\`, `{`, `}` must be escaped. Whitespace (spaces, tabs, newlines) is significant and preserved:

```
.input {$num :number}
{{   This is the {$num} pattern   }}
```

-> `   This is the 5 pattern   ` (surrounding spaces kept inside `{{ }}`)

Escapes:

```
Backslash: \\, left curly brace \{, right curly brace \}
```

-> `Backslash: \, left curly brace {, right curly brace }`

## Expressions (placeholders)

An expression is in `{ }` and holds an operand with an optional annotation (function + options):

```
{$date :datetime weekday=long}   // operand, function, option
{42 :number style=percent}       // literal operand
{|Some text|}                    // literal expression
{$name}                          // variable, no function
```

Read `{$date :datetime weekday=long}` as: "take `$date` and format it as a date, using the long weekday." Expressions appear in patterns, in declarations, and in variants.

## Literals

A literal is literal text in code, not data from a variable. Contexts: variant keys, expression operands, option values (an option value is a literal if it doesn't start with `$`).

**Unquoted literal**: a number, or a string of alphanumerics starting with a letter or `_`.

```
.local $x = {42}
.local $y = {number42}
.local $z = {_number}
{{{$x} {$y} {$z}}}
```

-> `42 number42 _number`. The braces belong to the expression, not the literal.

**Quoted literal** `|...|`: almost any character; required when the text has non-alphanumerics, spaces, etc.

```
.local $x = {|@literal|}
.local $y = {|white space|}
.local $z = {|{{curly braces}}|}
{{{$x} {$y} {$z} {|and \\, a backslash|}}}
```

-> `@literal white space {{curly braces}} and \, a backslash`
A literal used as pattern content still has to sit inside an expression `{...}`. Backslash is written `\\` inside quoted literals.

Examples needing quotes: `|image.png|` (has `.`), `year=|2-digit|` (has `-`).

MF2 is untyped: number literals are strings to the formatter; the number/other distinction is purely syntactic. Functions parse numbers from strings. Exact allowed characters are in the formal grammar (`name`, `number-literal`, `quoted-char` productions).

## Markup

A kind of placeholder: **open** `{#name}`, **close** `{/name}`, **standalone** `{#name/}`.

```
Click {#link}here{/link}. {#bold}{$count}{/bold} {#star-icon/}
```

- Names are not built into MF2 (`link`, `bold`, `star-icon` are playground-provided).
- Not tied to HTML or any markup language; the formatter does not interpret it, it passes markup through in the formatted result (representation is implementation-specific).
- Markup names are code; do not translate them. Text between tags is translatable.
