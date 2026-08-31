# Front-end Writing Rules

These apply to the Angular application in `front/`. They mirror the
spirit of [`code-writing.md`](code-writing.md), which governs the Python
side, adapted to TypeScript and Angular.

- **Language:** All code — identifiers, doc comments, comments, and
  user-facing UI copy — MUST be written in **en-US**, matching the rest
  of the repository.

- **Angular idioms:** Standalone components only (no NgModules), signals
  for state (`signal`, `computed`, `input`, `output`, `model`), the
  built-in control flow (`@if`, `@for` with a `track` expression), and
  `ChangeDetectionStrategy.OnPush`. The app runs zoneless; never reach
  for `NgZone` or manual `detectChanges` to force an update.

- **Doc comments:** Every service, every public method with behaviour
  worth explaining, and every non-obvious module gets a TSDoc comment
  (`/** ... */`) with `@param`/`@returns` where they add information.
  Comments explain *why*, not *what* the next line already says.

- **Type hints:** Annotate public members and function signatures.
  `strict` is on in `tsconfig.json` — keep it that way, and never
  silence the compiler with `any` or a non-null assertion where a real
  narrowing works.

- **Immutability:** Model types are `readonly`; update signals by
  producing new values (spread, `map`, `filter`) rather than mutating in
  place, so change detection sees the change.

- **Separation:** HTTP lives only in `core/services`; components read
  state from a store and emit intent through outputs. A component should
  never call `HttpClient` directly.

- **Files:** One component per directory, as `<name>.ts` / `<name>.html`
  / `<name>.scss`, following the CLI's own naming (no `.component`
  suffix). Templates and styles stay in their own files, not inline,
  once they grow past a couple of lines.

- **Styling:** Colors, spacing and radii come from the CSS custom
  properties in `src/styles.scss` — never hard-code a hex value in a
  component. Every component must read correctly in both the light and
  dark palettes.

- **Untrusted content:** The agent's answers are model-generated text.
  Render them only through the `Markdown` service, which sanitizes with
  DOMPurify before the HTML is bound.

- **Tests:** Services carry unit tests (`*.spec.ts`) covering their
  state transitions and error paths, not just the happy path. Code MUST
  pass `npm --prefix front run build` and `npm --prefix front test`
  cleanly before being considered done.
