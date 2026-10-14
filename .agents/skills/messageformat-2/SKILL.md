---
name: messageformat-2
description: Write, review, translate, and debug MessageFormat 2 (MF2) message syntax - placeholders, .input/.local declarations, .match plural/gender/ordinal variants, markup, built-in functions (:number, :string, :datetime, ...), escaping, and error diagnosis. Use when the user shows or asks for an MF2 message string, `.match`, `{{...}}` quoted patterns, or an MF2 error, even if they do not say "MessageFormat 2".
metadata:
  version: '1.0'
---

# MessageFormat 2 (MF2) syntax

## Core rules (always apply)

1. `{ }` separates code from translatable text. Outside single braces = text; inside = code.
2. **Simple message** = a bare pattern: `Hello, {$name}!`. **Complex message** = has declarations (`.input`/`.local`) and/or a matcher (`.match`); all patterns in it must be quoted `{{...}}`.
3. A bare pattern cannot start with `.` or `{{`, because the parser would read it as a declaration/matcher or a quoted pattern.
4. In text, escape `\`, `{`, `}` as `\\`, `\{`, `\}`. Whitespace in patterns is preserved.
5. Variables are `$name`; functions are `:name`; options are `name=value` (literal or `$var`); markup is `{#tag}` `{/tag}` `{#tag/}`.
6. Quote literals containing anything other than letters/digits/`_` (and not a plain number): `|2-digit|`.
7. Every `.match` selector needs a selector function (`:number`, `:integer`, `:string`, custom) via `.input`/`.local`; every variant needs the same key count as selectors; an all-`*` variant is mandatory.
8. Each variable may be declared once; a `.local` may only use earlier variables.

## Which reference to load

| Task                                                         | Read                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------ |
| Patterns, text, escapes, literals, markup                    | [references/syntax.md](references/syntax.md)           |
| `$variables`, `.input`, `.local`, shadowing, redeclaration   | [references/variables.md](references/variables.md)     |
| `.match`, plural/ordinal/exact selection, multiple selectors | [references/matchers.md](references/matchers.md)       |
| Function names, options, allowed values, custom functions    | [references/functions.md](references/functions.md)     |
| Diagnosing or fixing an error message                        | [references/errors.md](references/errors.md)           |
| Translating an MF2 message to another language               | [references/translators.md](references/translators.md) |

Load only the files the task needs.

## Workflow: write, fix, or review a message

Progress:

- [ ] Decide simple vs complex (declarations or `.match` -> complex, quote every pattern)
- [ ] Declare each selector value: `.input {$x :number}` (or `:string`)
- [ ] Write variants; add the all-`*` fallback; key count equals selector count
- [ ] Quote special literals; escape stray `{`, `}`, `\`
- [ ] Run the checklist below; fix and re-check until all items pass

Checklist:

1. Braces and `{{ }}` balanced; all patterns quoted in complex messages.
2. No variable declared twice, used before declaration, or self-referencing.
3. Every selector has a selector annotation; only selectable functions (not `:date`/`:time`/`:datetime`).
4. Same key count in all variants; no duplicate key lists; fallback variant present.
5. Known function names; no repeated options; valid option values.
6. Date field options not mixed with `dateStyle`/`timeStyle`.

## Example

Input: "Show how many photos a user added, singular/plural."

```
.input {$count :number}
.match $count
one {{You added {$count} photo.}}
*   {{You added {$count} photos.}}
```

Return the final message in a code block, then one line on which variants were added and why.

## Gotchas

- Forgetting `{{ }}` after a declaration is a syntax error.
- `.match $x` with no annotation on `$x` -> `missing-selector-annotation`. Add `.input {$x :number}`.
- `.input {$x}` without a function only documents the variable.
- Referencing `$count` anywhere creates an implicit declaration; a later `.local $count` is then a duplicate.
- A `.local` with an input's name shadows or duplicates it; use a new name.
- Option values like `2-digit` need `|...|`.
- Markup is not a function (no colon) and is never interpreted by the formatter.
- Output wording (date/number formatting) varies by locale and implementation; show sample results as illustrative, never as guaranteed.
