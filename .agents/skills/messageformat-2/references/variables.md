# Variables and declarations

## Contents

- Variables
- `.local`
- `.input`
- Shadowing and redeclaration

## Variables

Reference data supplied at runtime. Always prefixed with `$`. The name may contain almost any non-space, non-punctuation characters and cannot start with a digit.

```
Your name is {$name}.
You have {42 :number style=currency currency=$currency}.   // variable as an option value
```

## `.local`

Binds a new variable to an expression within the message.

```
.local $count = {42}
{{The count is: {$count}}}

.local $score = {0.42}
.local $score_percent = {$score :number style=percent}
{{Your score was {$score_percent}.}}
```

-> `The count is: 42`, `Your score was 42%.`

The right-hand side may contain literals, functions, and other variables (local or external), but only ones declared **before** it. It cannot reference itself.

Also usable to name a formatted value: `.local $date1 = {$date :datetime weekday=long}` then `{{Today is {$date1}.}}`.

## `.input`

Explicitly names an external value; the operand must be a variable, which is both the input and the declared name.

```
.input {$count :number}
{{The count is: {$count}}}
```

Uses:

- **Documentation**: `.input {$count}` tells the developer the message expects `count` and tells the translator it is supplied.
- **Annotation / coercion**: `.input {$amount :number style=currency currency=USD}` always formats it that way. Functions here are coercions (they return a new value of the type, or signal an error), not type assertions. A non-numeric value under `:number` gives "Input is not numeric", surfacing bad input early.
- **Selection options travel with the variable**: options in `.input` apply to any `.match` using it.
  ```
  .input {$rank :number select=ordinal}
  .match $rank
  one {{This is the {$rank}st most expensive item}}
  two {{This is the {$rank}nd most expensive item}}
  few {{This is the {$rank}rd most expensive item}}
  *   {{This is the {$rank}th most expensive item}}
  ```
  (rank 32 -> "32nd")

Equivalent forms: `.local $d = {$date :datetime weekday=long}` + `{$d}` vs `.input {$date :datetime weekday=long}` + `{$date}`.

## Shadowing and redeclaration

- A `.local` with the same name as an external input **shadows** it: later references use the local value.
  ```
  .local $count = {42}
  {{The count is: {$count}}}      // with external count=32 -> "The count is: 42"
  ```
- A variable can be declared only **once**. These are all errors (duplicate declaration):
  ```
  .local $count = {42}
  .local $count = {32}

  .input {$count :number}
  .local $count = {32}

  .local $count = {32}
  .input {$count :number}
  ```
- Using an external variable creates an **implicit declaration**, so this is also an error:
  ```
  .local $count1 = {$count}
  .local $count = {32}
  ```
- Fix: give each variable a unique name.
