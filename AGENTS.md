# AGENTS.md

This repository is a reusable, institution-neutral Beamer harness. Keep the
demo stable and let an agent author private talks from a brief and local
materials. This file is the short router for repository work; read the linked
workflow guide only when the task needs it.

## Choose the smallest relevant guide

- **Create or revise a talk:** read [`STYLE.md`](STYLE.md), [`outline.md`](outline.md)
  and [`docs/agent-authoring.md`](docs/agent-authoring.md), then inspect the supplied
  brief/materials and the specific template files you need. `prompt.md` only describes
  the two-stage workflow.
- **Change theme geometry, colors, class options, or visual behavior:** read
  [`docs/agent-theme.md`](docs/agent-theme.md) and the affected files under
  `theme/` or `tools/fixtures/`.
- **Build, export, inspect, or diagnose output:** read
  [`docs/agent-validation.md`](docs/agent-validation.md), then use the narrowest
  relevant `make` target.
- **Look up or update citations:** use [`docs/literature.md`](docs/literature.md)
  and read the paper or other authorized primary source before making claims.
- **Change public documentation, packaging, CI, or releases:** inspect the
  affected document and [`CONTRIBUTING.md`](CONTRIBUTING.md), then run the
  checks that cover the change.

Do not read every guide for every edit. `README.md`, `docs/usage.md`,
`docs/class-options.md`, and `make help` are reference material; consult them
when the task touches their subject.

## Non-negotiable boundaries

- Preserve user-provided facts, intent, metadata, citations, and assets. Never
  invent results, quotations, affiliations, dates, permissions, or images.
- Bundle necessary clarifications when an unknown would change the meaning,
  require external/proprietary material, or cross a privacy or safety boundary.
  Routine condensation, layout choices, local inspection, and safe local tests
  are authorized work. If a missing fact does not change the argument, use a
  clear placeholder and report it.
- New facts, advice, examples, tutorials, demos, or conclusions outside the
  authorized brief/materials need approval before inclusion, in slides or notes.
  Continue within previously approved scope without asking again; verification
  alone is not permission to expand a talk.
- For a new talk or a content-bearing revision, normalize the outline and obtain
  user confirmation before writing or expanding presentation source or notes.
  Keep the normalized outline reviewable under `build/`; routine tool checks may
  proceed before confirmation, but conjectured content may not enter the deck.
- Keep the institution-neutral `campus` API. School identity and functional
  colors belong in `theme/campuscolor.sty`; talk content belongs in `main.tex`,
  `chapters/talk/`, `materials/`, and (when needed) `bibliography/main.bib`.
  Do not alter the demo to make a user talk.
- Ordinary body frames use two header lines: the current `\subsection` above
  the frame title. Give every body frame a meaningful subsection and a title;
  keep single-line headers for generated TOC and references pages.
- Treat compiler output in `build/` as generated. Agent-authored normalized
  outlines and `build/<MAIN>.notes.json` are editable working documents. Do not
  commit private talks, materials, generated outputs, or local environments.
- Build from the repository root. Keep `materials/.gitkeep`; new public source
  files must be added deliberately to `tools/package_source.py`.

## Completion is outcome-based

For a talk, completion means authored source plus aligned speaker notes,
successful PDF and PPTX output, and the checks in the authoring/validation
guides. Do not report a deck as ready without inspecting the rendered pages and
reporting any unresolved placeholder or warning.

For code, theme, or documentation work, completion means the requested change,
the narrowest meaningful tests/checks, and a brief report of what was not run or
could not be verified. Continue through failures caused by the change; stop at
an external dependency or a decision that genuinely needs the user.

## Common entry points

```text
make doctor                 # inspect local prerequisites
make test                   # Python regression tests
make draft                  # compile and render the selected entry
make MAIN=example           # build the public demo
make                       # build main.tex, or example.tex if absent
make check-theme            # compile theme fixtures
make dist                   # create the reviewed standalone source ZIP
```

The default entry is `main.tex` when present, otherwise `example.tex`; an
explicit `MAIN` wins. Use `make help` for the complete command list.

## Repository map

- `outline.md`: public blank content template; `prompt.md`: workflow only.
- `materials/outline.md`, `build/outline-normalized.md`: ignored private outline
  and review copy; keep approval tied to a specific outline revision.
- `example.tex`, `chapters/`, `bibliography/refs.bib`: public reference demo.
- `main.tex`, `chapters/talk/`, `bibliography/main.bib`, `materials/`: local
  agent-authored talk inputs and sources.
- `theme/`: class, theme implementation, school profile, and code-window style.
- `tools/`: converter, preview, literature, packaging, fixtures, and tests.
- `docs/`: user documentation plus the task-specific agent guides linked above.
- `build/`: ignored PDFs, PPTX, notes, previews, logs, and intermediate files.

Keep the existing 16:9 layout, default primary-color section pages, fixed
footline behavior, and documented asset/license boundaries unless the user asks
for a deliberate design change and confirms its meaning.
