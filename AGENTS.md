## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical roles, recorded as the `Status:` line in issue files. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `GLOSSARY.md` plus `docs/adr/`. See `docs/agents/domain.md`.

## Style Guide

1. Never use ternary operators in JSX, instead use `&&` twice. e.g. `isError && <>...</>`, `!isError && <>...</>`. The same applies to choosing a class or a handler: `cn('base', isActive && ACTIVE, !isActive && INACTIVE)`.
2. Dont check for array `length` like `arr.length === 0`, do `!arr.length` or `arr.length`.
3. Characters are free. Do not shortcut `event`, `value`, `number` and others. But `char`, `i`, `j` are allowed.
4. Event handlers created in hooks are named `handleX`. Props are named `onX`.
5. Never use comments.
6. Don't destructure hooks. `model` hooks are exempt - identified by their return shape (`state`, `queries`, `mutations`, `functions`, `features`). Don't do for values too, like `{ ... } = event` and etc.

## Structure

1. **Page**: Define page component inline in `index.tsx`. Consumes `model hook` and only renders JSX. Never extract the full page to `-components/`.
2. **Slices**: `-constants`, `-utils`, `-types`, `-actions`, `-components`, `-hooks`, `-schemas`, `-lib` must be directories with `index.ts`.
3. **Fractal**: `components` slice can nest however deep and contain other slices too.

## Page Model Hooks

`use<Feature>Page` (e.g. `useUsersPage`) lives in `-hooks/use-<feature>-page.ts` and returns:

- `state?`: reactive state, computed values.
- `queries?`: TanStack Query queries.
- `mutations?`: TanStack Query mutations.
- `functions?`: handlers (`handleX`) or helpers.
- `features?`: result of other hooks, e.g. `form` or `clipboard` (useCopy).

Component-local hooks may deliberately return a bare object of their state and handlers instead of this shape. A hook that does so is not a model hook, and its return value must not be destructured.

## Verification

After each change run scoped `vp check ...` (e.g. `vp check ./src/main.tsx`) and `vp exec stylelint ...` (e.g. `vp exec stylelint ./src/assets/styles/global.css`) if `css` is changed.
