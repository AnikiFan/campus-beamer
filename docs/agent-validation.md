# Agent guide: build, export, and validation

Read this guide when compiling, exporting, inspecting, or diagnosing a talk or
the public demo. Use the narrowest target that answers the current question.

## Commands

```bash
make doctor                 # tools, packages, and fonts
make test                   # Python regression tests
make draft                  # final layout + previews + report
make draft PAGES=3,8-10     # focused visual iteration
make                         # PDF, notes-aware PPTX, then cleanup
make pdf                    # PDF only, then cleanup
make check-theme            # isolated theme fixtures
make dist                   # reviewed standalone source ZIP
```

`make` chooses `main.tex` when present and `example.tex` otherwise; explicit
`MAIN` overrides it. `make draft` uses the final layout but skips PPTX export and
notes-count validation. Failed builds retain logs/intermediates; do not present
an older output as a newly built result. Successful targets clean TeX
intermediates while retaining final outputs and notes.

## Visual review

Use [STYLE.md](../STYLE.md) to review the communication, not just geometry.
For every page record its one message, retained visible evidence/actions, and
explanations moved to notes. Review density (usually 3–4 main points), duplicate
summaries, font size, notes usefulness and total speaking time. Essential
conditions, grading/submission requirements, and evidence remain visible.
Confirm all additions in both slides and notes are within the user's authorized
scope; pending suggestions stay outside the deck.

Keep the user's original draft in the root `outline.md` and the normalized review
copy in `build/outline-normalized.md`.

For a new or content-bearing revision, confirm that `build/outline-normalized.md`
contains developed section/subsection content, metadata, audience, goal, time
budget, explanations, evidence, sources, and open questions. Verify that the user
confirmed this content before production. Review the final slides and notes
against that revision: substantive additions belong in outline review. Frame
splits, concise wording, and redistribution of approved detail into notes are
layout decisions; check their coverage and time budget without treating page
count as a fixed outline requirement.

After the first successful draft, read `build/draft/<MAIN>/report.txt` (or
`report.json`), inspect every contact sheet, and open every rendered page at a
readable size. Review title, section, overview, ordinary, citation, reference
continuation, and closing pages; inspect all overlays. Fix condensation and
splitting before changing geometry. Review every overfull warning in context;
underfull warnings are spacing hints, not proof of quality.

Check every ordinary body page for two visible header lines: subsection above,
frame title below. If one is missing, fix the source structure/title, including
the first body frame after each new section. Generated TOC/references pages use
single-line headers; cover, section-opening, and closing pages have dedicated
layouts. Check rendered output as well as declarations in the source.

Review body-header text as short, specific topic phrases. Keep conclusions,
causal explanations, and conditions in the body or notes rather than turning the
lower header into a sentence. For code pages, confirm the upper bar contains the
type marker and file/path, while an optional global description is below the code
area in the figure-caption style; check Terminal, configuration-file, source-file,
line-number, fragile, and column cases. For node-based diagrams, inspect node/arrow anchors, profile-derived
colors, final font size, wrapping, clipping, and editable source/generation
metadata. A plain sentence or single mathematical arrow does not need a diagram.

For audience-facing resources, verify the visible URL is the actual PDF link
target, including required query parameters. Check long URLs for natural wrapping,
readable size, and page-edge clearance; local resources should use relative paths.

Search rendered body text for authoring-process phrases such as “作者提供”、
“本次材料”、“作者截图”、“本页来自草稿” and “素材来源”. Replace them with
audience-facing resource labels; keep provenance and editing notes in speaker notes.

Inspect section lists for phantom blank rows as well as genuine wrapped titles.
Verify top-right citation placement and clearance from both header lines;
report any user-approved position exceptions. Check the specified date on the
cover and closing page, plus PDF/PPTX metadata; `\date` exports its display text.

Before delivery, run a full unfiltered `make draft`, then `make`. If the final
compile changes page order or count, repeat the visual review and regenerate
notes.

## PDF/PPTX contract

The converter defaults to 600 DPI and keeps the rendered slide as an image,
internal/external links, speaker notes, PDF bookmarks, native PowerPoint
sections, and talk metadata. Notes are loaded from `build/<MAIN>.notes.json`;
direct converter calls can use `--notes`, `--notes-dir`, `--no-notes`, and
`--verbose`.

Verify:

- PDF and PPTX page counts match and notes cover every final PDF page exactly;
- internal jumps and external links survive, including local video links;
- level-one bookmarks map to the expected PowerPoint section names/boundaries;
- title/author and supplied custom properties (`Subtitle`, `Group`, `Advisor`,
  `PresentationDate`, `Contact`) match the source;
- citations and reference pages contain only verified entries.

Local-video export needs FFmpeg and must fail without replacing a previous PPTX
when the decoder is missing or the video is undecodable. The PDF source remains
unchanged. Use `UV_CACHE_DIR=/tmp/<task-cache>` when a restricted environment
cannot write the default uv cache.

## Packaging and release

`make dist` packages only the explicit `FILES` allowlist in
`tools/package_source.py`. New public files, including agent guides, must be
listed deliberately; user materials, private talks, build output, notes, and
`.venv` stay out. The archive uses `tools/templates/outline.md` as its starter outline; packaging
must leave the user's root draft unchanged. Use `CONTRIBUTING.md` and `docs/releases.md` for release
workflow and CI details.
