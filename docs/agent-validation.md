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
Speaker notes are authored in the source with native `\note`; generated note
PDFs are working output, not editable authoring documents.
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
confirmed this content before production. Check the material inventory against
the actual authorized directories (including ignored inputs and referenced
assets); every relevant input has a read/view status and a documented use or
exclusion. Check unexplained omissions, unread images, and broken paths. Respect
the approved scope rather than requiring all material to appear in slides. Review the final slides and notes
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
single-line headers; explicitly selected `campusfocus` frames also use one title
and only the bottom footer row. Check that the next ordinary frame restores both
header lines and navigation. Image backgrounds must cover the page without aspect
distortion, stay centered and respect opacity; inspect wide and tall sources and
text contrast. Both TOC modes retain section links; overview entries have uniform
color and emphasis. Cover, section-opening, and closing pages have dedicated
layouts. Check rendered output as well as declarations in the source.

Review body-header text as short, specific topic phrases. Keep conclusions,
causal explanations, and conditions in the body or notes rather than turning the
lower header into a sentence. For code pages, confirm the upper bar contains the
type marker and file/path, while an optional global description is below the code
area in the figure-caption style; check Terminal, configuration-file, source-file,
line-number, fragile, and column cases. For node-based diagrams, inspect node/arrow anchors, profile-derived
colors, final font size, wrapping, clipping, and editable source/generation
metadata. Check compliance with the shared figure-layout rules in
[AGENTS.md](../AGENTS.md#non-negotiable-boundaries). For Mermaid, also check the
actual fonts and text size in the render report.
Where semantics permit, check symmetry, equal peer-node dimensions,
aligned centers and regular gaps. Check edge anchors, routing and visible shafts
longer than arrowheads at the final insertion size. A plain sentence or single
mathematical arrow does not need a diagram.

For audience-facing resources, verify the visible URL is the actual PDF link
target, including required query parameters. Check long URLs for natural wrapping,
readable size, and page-edge clearance; local resources should use relative paths.

Check necessary conditions or restrictions for recognizable headings. A titled
auxiliary box can organize related conditions beside a main table/diagram;
confirm its semantic type, readable height and absence of repeated summaries.
For description lists, confirm that the width sample is the actual widest label
at the selected font/size, and inspect aligned right edges, explanation starts,
column boundaries and wrapped text.

For tables, verify that labels shared by multiple detail rows occupy merged
cells and are vertically centered across the complete row group, including
wrapped text. Partial rules must not cross those cells; check group boundaries
and consistent text/numeric alignment across columns.

Every content diagram/image/screenshot has a nearby caption below it describing
objects or relationships; check the visible text, spacing and clearance from
body/footer. Exempt logos, decorative backgrounds and theme overlay TikZ.
Source scanning is a supporting check, not a general detector for uncaptained
content figures.

Code and video captions use the localized theme-colored label followed by
normal caption text, matching figures and tables. Check both `caption` and
`description` code options, `\campusvideocaption`, and empty captions; do not
color the entire description or leave a label when the caption is absent.
Image and video titles/captions must describe their content. Original paper
figure numbers belong in citations or source notes; file sizes and durations
are visible only when they serve as evidence in the talk.

Web sources use the standard gray top-right citation style. Verify both the
source name and actual URL are visible and clickable, including fragments and
query parameters. For the long-address fallback, match the corner label to the
named full URL on that page. Keep the configured citation font readable;
shorten a title, relocate the full URL or split rather than shrink text.

Check rendered academic citations for verified paper affiliations, publication
dates and citation counts with provider and snapshot date. Do not treat populated
BibTeX fields as proof that these details are visible. Report unavailable fields
to the user; never render metadata placeholders or invent a zero count.

For bibliography summaries, verify the fitting sequence in STYLE.md: existing
font and single column when one page suffices; progressively smaller fonts down
to tiny; then tiny two-column; then multiple pages retaining that format. Check
actual rendered font sizes, column layout, complete entry coverage and footer
clearance. Do not accept hidden frame scaling below tiny or prematurely reduced
fonts. This is an authoring policy, not an automatic `\referencespage` feature.

If the talk's corner-citation width was increased to reduce wrapping, inspect
all affected pages, especially the longest frame and subsection titles and the
longest citation blocks. Require a visible safe horizontal gap and body
clearance, without additional title wrapping or smaller citation text.

Search rendered body text and speaker notes for authoring-process phrases such
as “作者提供”, “本次材料”, “作者截图”, “本页来自草稿”, “待完成”, “待补充”,
“TODO” and “请替换图片”. Use audience-facing resource labels, keep detailed
provenance in speaker notes, and move editing tasks to user messages. Review
matches in context: scientific open questions, limitations and future work may
be legitimate talk content. An unresolved gap that prevents the intended talk
from being delivered must block a readiness claim, even if no placeholder remains.

Inspect section lists for phantom blank rows as well as genuine wrapped titles.
Verify top-right citation placement and clearance from both header lines;
report any user-approved position exceptions. Check the specified date on the
cover and closing page, plus PDF/PPTX metadata; `\date` exports its display text.

Before delivery, run a full unfiltered `make draft`, then `make`. If the final
compile changes page order or count, repeat the visual review and regenerate
notes.

## Overlay and transition review

Inspect every rendered stage, including the final complete state. Check reveal
order, retained evidence/conditions, stable headers/captions/URLs and geometry;
replacement states must not overlap. Count physical PDF/PPTX pages separately
from logical frames and align notes with each stage. Verify jumps to the intended
stage rather than accepting only the slide count.

The converter maps explicit PDF Fade/Dissolve transitions and page durations to
native PPTX settings. Check the per-slide transition type/duration and absence
of automatic advance unless it was requested; effects must not leak into the next
ordinary frame. Unsupported effects warn and use a plain slide change. For a
static export use `--no-transitions`; this also disables automatic page durations.
If delivering a handout, inspect its separate final-state output and notes count.
PPTX XML evidence does not establish playback in a PowerPoint client.

## PDF/PPTX contract

The converter defaults to 600 DPI and keeps the rendered slide as an image,
internal/external links, speaker notes, PDF bookmarks, native PowerPoint
sections, and talk metadata. Make renders native TeX notes into
`build/<MAIN>.notes.pdf` and extracts its right-hand text screen for PowerPoint.
The generated PDF is tied to the slide PDF by a fingerprint and must have the
same physical stage count. Direct converter calls can use `--notes-pdf`,
`--notes-dir`, `--no-notes`, and `--verbose`; `--notes` retains legacy JSON import.

Check `shownotes=false` for a clean audience PDF and `shownotes=true` for a
paired slide/notes PDF. In both cases the PPTX must contain ordinary 16:9 slide
images with notes only in the speaker-note field. Inspect empty stages,
overlay-specific notes, outside-frame notes and reference continuations. A
paired PDF passed directly to the converter is rejected; use Make, which renders
a clean slide variant when needed. Count/fingerprint mismatches must stop export
without replacing a previous PPTX. Do not silently discard existing JSON-only
talk notes; once native commands exist, TeX becomes authoritative for all stages.

Verify:

- PDF and PPTX page counts match and notes cover every final PDF page exactly;
- internal jumps and external links survive, including local video links;
- overlay order and explicit transition/timing settings match the final PDF;
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
