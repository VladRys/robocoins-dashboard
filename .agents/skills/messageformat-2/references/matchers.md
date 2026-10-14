# Matchers (`.match`)

## Contents

- Anatomy and evaluation
- Selection with `:number`
- Selection with `:string`
- Multiple selectors
- Languages with more plural categories
- Rules summary

## Anatomy

A matcher groups variants of a message; one variant is chosen from runtime data.

```
.input {$count :number}
.match $count
one {{You have {$count} week.}}
*   {{You have {$count} weeks.}}
```

- `.match` is followed by one or more **selector** variables. Selectors must be declared earlier with `.input`/`.local`; the annotation decides how selection works (`:number` -> plural category by default).
- Each variant = **keys** + a **quoted pattern**. `*` is the special catch-all key matching anything.
- Evaluation: the selector function gets the value and the list of keys, determines the best matching key; that key's pattern is chosen; the variable is replaced with its value. `$count`=1 -> "You have 1 week."; 42 -> only `*` fits -> "You have 42 weeks."
- Details of matching depend on the selector function (`:number` is just one example).

## `:number` / `:integer` selection (`select` option)

| `select`           | Keys are matched against               |
| ------------------ | -------------------------------------- |
| `plural` (default) | CLDR plural rules for cardinal numbers |
| `ordinal`          | CLDR plural rules for ordinal numbers  |
| `exact`            | their exact contents                   |

```
.input {$num :number}                    // plural
.match $num
one {{one!}}
*   {{many!}}                            // 2 -> many!

.input {$num :number select=ordinal}
.match $num
one  {{You are {$num}st}}
two  {{You are {$num}nd}}
few  {{You are {$num}rd}}
*    {{You are {$num}th}}                // 2 -> You are 2nd

.input {$num :number select=exact}
.match $num
1 {{one!}}
2 {{two!}}
3 {{three!}}
* {{other!}}                             // 2 -> two!
```

With Czech (`cs-CZ`), `2` has category `few`; with `select=exact` it only matches a key literally `2`, so `*` wins. Numeric keys such as `1` may be written on a `:number` selector (see the "bad variant key" fix in errors.md).

## `:string` selection

Exact string match. Use it to say "match this value exactly" (any selector needs an annotation).

```
.input {$operand :string}
.match $operand
1    {{Number 1}}
one  {{String "one"}}
*    {{Something else}}      // operand "1" -> Number 1
```

## Multiple selectors

One key per selector, in the same order, in every variant.

```
.input {$hostGender :string}
.input {$guestCount :number}
.match $hostGender $guestCount
  female 0 {{{$hostName} does not give a party.}}
  female 1 {{{$hostName} invites {$guestName} to her party.}}
  female 2 {{{$hostName} invites {$guestName} and one other person to her party.}}
  female * {{{$hostName} invites {$guestCount} people, including {$guestName}, to her party.}}
  male   0 {{...}}
  male   1 {{...}}
  male   2 {{...}}
  male   * {{...}}
  *      0 {{...}}
  *      1 {{...}}
  *      2 {{...}}
  *      * {{...}}
```

(`...` stands for the corresponding text, shown here to save space.) With custom selectors an object operand can supply several values:

```
.local $hostGender = {$host :gender}
.local $hostName   = {$host :name}
.match $hostGender $guestCount
```

## Languages with more than two plural categories

Translators add or remove variants per the target language's CLDR plural categories (https://cldr.unicode.org/index/cldr-spec/plural-rules).

```
.input {$count :number}
.match $count
one   {{Masz {$count} tydzień.}}
few   {{Masz {$count} tygodnie.}}
many  {{Masz {$count} tygodni.}}
*     {{Masz {$count} tygodnia.}}
```

The `*` variant is always required and covers the `other` category.

## Rules summary

- Selector needs a selector function (`:number`, `:integer`, `:string`, custom); `:date`/`:time`/`:datetime` are not selectable.
- Key count per variant == selector count.
- No two variants with the same ordered key list (`one *` and `* one` differ).
- At least one variant with all keys `*`.
- Patterns in variants are always quoted.
