# Agent guide: theme and visual maintenance

Read this guide when changing `theme/`, class options, layout geometry, visual
fixtures, or school configuration. Content changes should stay in the talk
sources and do not need this guide.

## Boundaries

Keep the implementation institution-neutral and use `campus…` identifiers.
School colors, emblem/wordmark paths, and functional palette values belong only
in `theme/campuscolor.sty`; layout geometry belongs in
`theme/beamerthemecampus.sty`. The default profile is Tsinghua and its existing
rendering is a compatibility baseline. Do not hard-code another school's brand
or create `imageone`/`demographic` registries. Keep demo metadata literal in
`sections/metadata.tex`; keep user metadata in `sections/talk/metadata.tex`.

The public class is the configuration surface for new decks. Preserve legacy
`\usetheme{campus}` and low-level layout compatibility unless the change is
deliberate. Keep all public options and defaults documented in `example.tex`
and `docs/class-options.md`; use `layoutguides=true/false` only as the class
option.

## Visual invariants

Preserve these unless the user explicitly requests a design change:

- fixed 16:9 geometry and symmetric body margins;
- white text on a `maincolor` footline, with the existing centered baseline and
  `frame/total` plus `author | title` arrangement;
- the top-left emblem block flush with the page top and using the configured
  dark/light emblem assets;
- the white-left, primary-color-right cover split, its documented diagonal and
  wordmark anchors, and full primary-color section pages by default;
- ordinary two-line headers (subsection over frame title), single-line header
  baselines, and shared header gaps;
- readable description columns, corner citations as compact plain gray text,
  and fixed closing-page placement.

When a change targets one alignment axis, verify the other axis did not move.
Use the existing theme geometry and fixtures instead of tiny fonts, clipping,
negative spacing, or warning suppression. Diagnostic guides belong in the theme
fixture and must not become a new public layout API.

## Safe maintenance loop

Inspect the affected theme code and the smallest relevant fixture first. Make a
focused change, then run `make check-theme`; if the public demo may change,
also run `make draft MAIN=example` and visually inspect the affected pages. For
a pure refactor, compare PDFs with `tools/compare_pdf.py` as described in
`CONTRIBUTING.md`. Keep warnings visible and explain any benign remaining
warning with visual evidence.

Asset source, trademark, and rights-holder notices in `assets/README.md` are
part of the public contract. Preserve them and do not turn a contact/removal
notice into a license or invent permissions.
