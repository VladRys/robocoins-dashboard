# MF2 errors: failing and corrected examples

## Contents

- Syntax, key-mismatch, fallback, duplicate-variant errors
- Selector errors (annotation, bad selector, bad variant key)
- Declaration errors (duplicate declaration, unresolved variable)
- Function errors (unknown function, bad operand, bad option, duplicate option)

Names in parentheses are the JavaScript implementation's error names; wording varies by implementation.

Categories: syntax errors, data-model errors (found without runtime data), resolution errors (unclear meaning from missing/inconsistent runtime data), message function errors. Syntax and data-model errors are non-recoverable: the formatter provides no fallback output.

## Syntax error (`parse-error`)

Bad: `{|Some text|` (missing closing brace)
Good: `{|Some text|}`

## Variant key mismatch (`key-mismatch`)

Number of keys per variant must equal the number of selectors.

```
// Bad
.local $x = {1 :number}
.match $x
one * {{Too many keys}}
*   * {{Also too many keys}}

// Good
.local $x = {1 :number}
.match $x
one {{Correct number of keys}}
*   {{Also correct number of keys}}
```

## Missing fallback variant (`missing-fallback`)

```
// Bad
.local $x = {1 :number}
.match $x
one {{x is singular}}

// Good
.local $x = {1 :number}
.match $x
one {{x is singular}}
*   {{x is plural}}
```

## Duplicate variant (`duplicate-variant`)

Key lists are ordered: `one *` and `* one` are not duplicates.

```
// Bad
one {{x is singular}}
one {{x is singular.}}
*   {{x is not singular}}

// Good
one {{x is singular}}
*   {{x is not singular}}
```

## Missing selector annotation (`missing-selector-annotation`)

```
// Bad
.match $x
one {{x is singular}}
*   {{x is plural}}

// Good
.input {$x :number}
.match $x
one {{x is singular}}
*   {{x is plural}}
```

Annotations are transitive:

```
.input {$x :number}
.local $y = {$x}
.match $y
one {{x is singular}}
*   {{x is plural}}
```

## Duplicate declaration (`duplicate-declaration`)

```
// Bad
.input {$x :number}
.local $x = {42}

// Bad (implicit declaration by earlier use)
.local $count1 = {$count}
.local $count = {32}

// Good
.input {$x :number}
.local $y = {42}
```

## Duplicate option name (`duplicate-option-name`)

Bad: `.input {$x :number style=percent style=decimal}`
Good: `.input {$x :number style=percent}`

## Unresolved variable ("Variable not available")

An `.input` or `{$x}` reference needs a value supplied at runtime, or a `.local` declaration.

```
.input {$x :number}
{{{$x}}}
```

fails when no value for `$x` is supplied; works when `x` = 5.

## Unknown function

Bad: `.local $x = {1 :num}`
Good: `.local $x = {1 :number}`
Check spelling, or make sure a custom function with that name is registered.

## Bad selector (`bad-selector`)

Bad:

```
.local $day = {|2024-05-01| :datetime}
.match $day
* {{The due date is {$day}}}
```

Good (no matching needed):

```
.local $day = {|2024-05-01| :datetime}
{{The due date is {$day}}}
```

`:number`, `:integer`, `:string` are selectable; `:datetime`, `:date`, `:time` are not.

## Bad operand ("Input is not numeric" / "Input is not a date")

Bad: `.local $horse = {|horse| :number}` and `{|horse| :datetime}`
Good: pass a numeric value for `:number`, an ISO 8601 string for date functions:

```
.input {$numHorses :number}
.match $numHorses
one {{You have a horse.}}
*   {{You have {$numHorses} horses.}}
```

## Bad option ("Value foo is not valid for :number option minimumFractionDigits")

Bad: `{1 :number minimumFractionDigits=foo}`
Good: `{1 :number minimumFractionDigits=2}` -> `1.00`
Check the function's option table in [functions.md](functions.md).

## Bad variant key

Custom selector functions define what kinds of keys they can match against. Just as the operand of `:number` has to be parseable as a number, it can only match against numeric keys.

```
// Bad
.local $answer = {42 :number}
.match $answer
1     {{The value is one.}}
horse {{The value is a horse.}}
*     {{The value is not one.}}

// Good
.local $answer = {42 :number}
.match $answer
1 {{The value is one.}}
* {{The value is not one.}}
```

(Some implementations do not yet raise this error.)
