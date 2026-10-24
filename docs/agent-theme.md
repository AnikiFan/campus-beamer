# Agent guide: theme and visual maintenance

Read this guide when changing `theme/`, class options, layout geometry, visual
fixtures, or school configuration. Content changes should stay in the talk
sources and do not need this guide.

## Boundaries

Keep the implementation institution-neutral and use `campus…` identifiers.
School colors, emblem/wordmark paths, and functional palette values belong only
in `theme/<name>/profile.tex`; its assets and provenance belong in that school
directory. `theme/campuscolor.sty` selects and validates the profile; layout geometry belongs in
`theme/beamerthemecampus.sty`. The default profile is institution-neutral `general`. Explicit `tsinghua` and
`pcl` profiles retain their existing institutional identities. The `tokyo-night` profile provides
a dark, institution-neutral palette through the optional surface/text colors in `theme/README.md`. Do not hard-code another school's brand
or create `imageone`/`demographic` registries. Keep demo metadata literal in
`examples/sections/metadata.tex`; keep user metadata in `sections/metadata.tex`.

The public class is the configuration surface for new decks. Preserve legacy
`\usetheme{campus}` and low-level layout compatibility unless the change is
deliberate. Keep all public options and defaults documented in `example.tex`
and `docs/class-options.md`; use `layoutguides=true/false` only as the class
option.

## Visual invariants

Preserve these unless the user explicitly requests a design change:

- fixed 16:9 geometry and symmetric body margins;
- profile `campusonprimary` text (white by default) on a `maincolor` footline,
  with the existing centered baseline and
  `frame/total` plus `author | title` arrangement;
- the top-left emblem block flush with the page top and using the configured
  dark/light emblem assets;
- the profile-body-color-left, primary-color-right cover split (white left for the
  original light profiles), its documented diagonal and
  wordmark anchors, and full primary-color section pages by default;
- ordinary two-line headers (subsection over frame title), single-line header
  baselines, and shared header gaps; explicitly selected `campusfocus` frames use
  a single header and only the bottom footer row; their optional backgrounds use
  centered cover scaling, cropping and per-frame opacity;
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

Asset source, trademark, and rights-holder notices in `assets/README.md` and
`theme/<name>/README.md` are
part of the public contract. Preserve them and do not turn a contact/removal
notice into a license or invent permissions.
