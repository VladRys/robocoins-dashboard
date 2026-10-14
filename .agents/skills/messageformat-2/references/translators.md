# Translating MF2 messages

MF2 syntax makes clear which parts are text and which are code.

## Translate vs. keep

| Translate                                                           | Do NOT translate                                                                                                                                 |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Plain text outside `{ }` (simple message)                           | Anything inside single `{ }`: placeholders `{$name}`, functions `:datetime`, options `dateStyle=long`                                            |
| Plain text inside `{{ }}` (complex message), excluding placeholders | Markup (`{#bold}`, `{/bold}`, `{#icon/}`) - tags start with `#` or `/`                                                                           |
| Text between markup tags (`{#bold}bold text{/bold}`)                | Declaration lines (`.local`, `.input`) - these are code                                                                                          |
|                                                                     | Code-like literals (e.g. `\|2-digit\|` in options) - usually code; but a literal like `{\|John Doe\|}` in text depends on the developer's intent |

Example: `It is the {$today :datetime dateStyle=long timeStyle=long} today.` -> only "It is the" and "today" are translated.

## Rules

- You may **move placeholders** to produce correct grammar: `Hello, {$name}!` -> `{$name}, hello!`. Move the braces with them.
- Keep curly braces balanced.
- In a complex message (with declarations), only text inside the double braces `{{ }}` is translatable.
- To write a literal brace in text, escape it: `\{`, `\}` (and `\\` for a backslash).

## Matchers

Translating a matcher might involve adding new variants: translate the existing variants and add any new ones the target language needs. When looking at a matcher, ask whether more (or fewer) variants are needed in the target language; the CLDR Plural Rules page lists plural categories per language. The `*` key matches anything.

English -> Czech:

```
.input {$numDays :number}
.match $numDays
one  {{{$numDays} den}}
few  {{{$numDays} dny}}
many {{{$numDays} dne}}
*    {{{$numDays} dní}}
```

New `few` and `many` variants were added.

## Declarations

Lines beginning `.local`/`.input` are code, not translatable; the pattern after them in `{{ }}` is.

```
.local $x = {|This is an expression|}
.input {$now :datetime dateStyle=long}
{{{$x} from {$now}}}
```

## Before finishing

- Braces balanced, `{{ }}` intact.
- Every variant keeps its keys and a `*` fallback exists.
- No function, option, or markup name was altered.
- Added/removed variants match the target language's plural categories.
