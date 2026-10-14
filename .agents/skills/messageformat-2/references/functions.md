# MF2 built-in functions reference

Load this when you need exact option names, values, or defaults.

## Contents

- `:number` and `:integer`
- `:string`
- `:datetime`, `:date`, `:time`
- Custom functions

## `:number` and `:integer`

`:integer` treats its operand as an integer (e.g. `{3.14 :integer}` -> `3`); otherwise `:number` and `:integer` behave similarly. `:integer` accepts the same options except where noted in the last column.

| Option                     | Allowed values                                                               | Default          | `:integer`? |
| -------------------------- | ---------------------------------------------------------------------------- | ---------------- | ----------- |
| `select`                   | `plural`, `ordinal`, `exact`                                                 | `plural`         | yes         |
| `compactDisplay`           | `short`, `long`                                                              | `short`          | no          |
| `notation`                 | `standard`, `scientific`, `engineering`, `compact`                           | `standard`       | no          |
| `numberingSystem`          | a valid Unicode Number System Identifier (docs show `roman`, `arab`, `thai`) | locale-dependent | yes         |
| `signDisplay`              | `auto`, `always`, `exceptZero`, `negative`, `never`                          | `auto`           | yes         |
| `style`                    | `decimal`, `percent`                                                         | `decimal`        | yes         |
| `useGrouping`              | `auto`, `always`, `never`, `min2`                                            | `auto`           | yes         |
| `minimumIntegerDigits`     | digit size                                                                   | `1`              | yes         |
| `minimumFractionDigits`    | digit size                                                                   | none             | no          |
| `maximumFractionDigits`    | digit size                                                                   | none             | no          |
| `minimumSignificantDigits` | digit size                                                                   | none             | no          |
| `maximumSignificantDigits` | digit size                                                                   | none             | yes         |

Digit size = integer >= 0 (or a string parseable as one).

Examples (en-US, `$num` = 3.1415927 unless noted):

- `{$num :number notation=scientific minimumSignificantDigits=5}` -> `3.1415927E0`
- `{$num :number style=percent}` -> `314%`
- `{$num :number minimumIntegerDigits=4 minimumFractionDigits=4}` -> `0,003.1416`
- `{$num :number maximumSignificantDigits=6}` -> `3.14159`
- `{3.14 :integer}` -> `3`
- `{$n :number compactDisplay=long notation=compact}` with 10001 -> `10 thousand` (short -> `10K`)
- `{42 :number style=currency currency=$currency}` with `currency=USD` -> `$42.00`
- `signDisplay` with `-0`: `auto`/`always` -> `-0`; `exceptZero`/`negative`/`never` -> `0`

### Selection

See [matchers.md](matchers.md) for `select=plural|ordinal|exact` with examples.

## `:string`

- Formatter: stringifies operand (details implementation-dependent).
- Selector: exact match against keys.
- No options.
- Use it to express intent to match a value exactly; example in [matchers.md](matchers.md).

## `:datetime`, `:date`, `:time`

Operand: ISO 8601 string with optional offset (e.g. `2006-01-02T15:04:06`); implementations may accept other date types. Not selectable.

`:date` = `:datetime` ignoring time; `:time` = `:datetime` ignoring date. They have a single option `style` (`full`, `long`, `medium`, `short`); default `medium` for `:date`, `short` for `:time`.

`:datetime` options:

| Option                   | Allowed values                                                              | Default         |
| ------------------------ | --------------------------------------------------------------------------- | --------------- |
| `dateStyle`              | `full`, `long`, `medium`, `short`                                           | `medium`        |
| `timeStyle`              | `full`, `long`, `medium`, `short`                                           | `short`         |
| `weekday`                | `long`, `short`, `narrow`                                                   | none            |
| `era`                    | `long`, `short`, `narrow`                                                   | none            |
| `year`                   | `numeric`, `2-digit`                                                        | none            |
| `month`                  | `numeric`, `2-digit`, `long`, `short`, `narrow`                             | none            |
| `day`                    | `numeric`, `2-digit`                                                        | none            |
| `hour`                   | `numeric`, `2-digit`                                                        | none            |
| `minute`                 | `numeric`, `2-digit`                                                        | none            |
| `second`                 | `numeric`, `2-digit`                                                        | none            |
| `fractionalSecondDigits` | `1`, `2`, `3`                                                               | none            |
| `hourCycle`              | `h11`, `h12`, `h23`, `h24`                                                  | locale-specific |
| `timeZoneName`           | `long`, `short`, `shortOffset`, `longOffset`, `shortGeneric`, `longGeneric` | none            |

Rules:

- Everything except `dateStyle`/`timeStyle` is a _field option_. Field options **cannot** be combined with `dateStyle` or `timeStyle`.
- When field options are used, only the named fields appear: `{$date :datetime weekday=long year=|2-digit|}` -> `24 Friday`.
- `hourCycle`: `h12` 1-12 (midnight 12:00 AM); `h23` 0-23 (midnight 0:00); `h11` 0-11 (midnight 0:00 AM); `h24` 0-24 (midnight 24:00).
- Exact output wording is locale- and implementation-dependent.

Examples:

```
Today is {$date :datetime weekday=long}.
The time is {$date :time style=full}.
The date is {$date :date style=short}.
Today is {$date :datetime dateStyle=full timeStyle=long}.
```

## Custom functions (syntax patterns only)

Names and semantics are defined by whoever registers them; they are used like built-ins.

Custom formatters:

```
Check out {MessageFormat :uppercase}.
I know how to program in {$languages :list type=AND}
```

Custom selectors (declare via `.local`/`.input` first):

```
.local $pronoun = {$person :pronoun}
.match $pronoun
he   {{{$person :name} won his game}}
she  {{{$person :name} won her game}}
they {{{$person :name} won their game}}
*    {{{$person :name} won the game}}
```

```
.local $range = {$name :range}
.match $range
|A-J| {{{$name} is in the first group}}
|J-P| {{{$name} is in the second group}}
|Q-Z| {{{$name} is in the third group}}
*     {{Should be unreachable}}
```

Keys containing special characters (like `-`) must be quoted with `|...|`.

A function can be a formatter, a selector, or both (like `:number`). Using a function that is not registered gives an "Unknown function" error.
