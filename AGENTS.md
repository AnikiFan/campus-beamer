# AGENTS.md

This is the single canonical instruction file for this directory.
Read `README.md` for the project overview, `docs/usage.md` for detailed template
usage, `docs/class-options.md` for document-class options, and `make help` for
build commands. For development, read `CONTRIBUTING.md`.

## Harness Role

This directory is a reusable presentation harness. The primary user workflow is
to give the agent a brief and locally prepared materials, not to edit a demo deck.
`prompt.md` is a sample brief, not a required form. Users may instead send their
ideas in chat. `materials/` is the default local input folder, for example an
unpacked arXiv LaTeX project, a paper PDF, figures or experiment results.
When the user supplies an outline, rough notes, a paper, or an idea, turn it into a complete Beamer
presentation and a matching PowerPoint export. The expected deliverables are:

- a newly authored `main.tex` entry and `chapters/talk/` content with a clear narrative and one message per frame;
- `build/main.notes.json`, generated speaker notes for the final PDF pages;
- a compiled `build/main.pdf`; and
- `build/main.pptx`, generated from that PDF with internal and external links kept,
  native PowerPoint sections and document metadata matching the talk.

The model should do the work through the existing template rather than merely
returning a proposed outline or asking the user to write LaTeX. Read `example.tex`
and its demo chapters as layout and command references; create the user's talk
separately, preserving those examples. A fresh source copy contains no user deck.
Make selects `main.tex` when present, otherwise `example.tex`; an explicit `MAIN`
always takes precedence. Make compiles existing sources, while the agent writes
the presentation. Preserve the user's facts and intent. Do not
invent experimental results, citations, quotations, dates, affiliations, or
images. Mark a missing fact as a placeholder or ask the user, depending on
whether the omission changes the argument.

### Confirmation gate

Ask the user before writing the final deck when a decision could materially
change its meaning or require information the user has not supplied. Bundle the
blocking questions into one short message. Typical confirmation cases are:

- the audience, purpose, language, duration, or approximate slide count is
  unclear and different choices would produce different content;
- the outline supports several incompatible narratives or a key claim needs
  evidence that is not available;
- the deck would need images, data, web research, proprietary files or citations
  beyond the supplied local materials and the active deck's bibliography;
- the request includes personal, confidential, sensitive, or potentially
  misleading material whose inclusion or wording is uncertain; or
- the requested visual treatment cannot be implemented without changing the
  theme or introducing a new asset.

An explicit request to find papers, download DBLP BibTeX, or query citation
counts authorizes those read-only lookups within the requested scope. Do not
ask again for each paper. The availability of a lookup tool alone is not
authorization to add external research to a different deck.
Supplying a local paper project authorizes reading its text, figures, captions
and bibliography for the requested talk. Verified citations and figures in that
project may be reused without another confirmation. Missing evidence remains a
confirmation case; do not substitute demo claims or citations for the user's sources.

Do not pause for routine authoring choices: use the existing 16:9 layout,
source language, concise slide wording, local assets, the default primary-color
section page (purple in the supplied profile), and a reasonable slide count derived from the outline. If a
non-blocking assumption matters, state it briefly in the progress update and
continue. If confirmation is required, prepare any independent file inspection
first, then wait before generating the dependent slides or claims.

### Authoring workflow

1. Read the user's brief in chat or `prompt.md` and inspect the supplied material
   paths (default `materials/`). Sample placeholders in `prompt.md` are not user
   facts. Inspect `example.tex`, its demo chapters, `theme/campusbeamer.cls`,
   `theme/beamerthemecampus.sty`, `theme/campuscolor.sty` and `assets/` for the
   available layouts; inspect an existing `main.tex` and its inputs when revising
   a user talk. If the supplied source is archived, unpack a working copy under
   `materials/` while retaining the original archive. For an arXiv LaTeX project,
   find its entry and follow its inputs,
   captions, figure paths and bibliography to understand the paper. Keep the
   original project intact. Prefer its original figure files; if a useful figure
   exists only in the PDF, extract or crop it without changing its meaning and
   retain its source in notes. Read the actual paper before writing its claims.
   Identify the intended audience, central message,
   evidence, and likely slide sequence.
   Start new decks with `\documentclass[language=chinese]{campusbeamer}` or
   `language=english`. The class loads the theme, Chinese support when needed,
   the math font setup and biblatex; do not duplicate these package loads in
   the talk preamble. Store verified talk entries in `bibliography/main.bib` and
   use `\campusbibresource{bibliography/main.bib}`. Keep the demo's `bibliography/refs.bib`
   unchanged unless maintaining the demo itself.
   English decks containing Chinese text need `cjk=true`. Bibliography support
   is always enabled; do not add a biblatex document-class option. Talks without
   citations can omit bibliography resources and references pages. The cover
   uses the primary-color split layout automatically; omit `\titlebackground`
   from new presentation entries.
2. Convert the outline into sections, subsections, and frames. Use section
  files such as `chapters/talk/01_intro.tex`, selected explicitly with `\input` in
  `main.tex`. Keep title/author/advisor/date in `chapters/talk/metadata.tex` and
  class/build/layout settings in the root entry. Each section file owns its
  section declaration, opening page, subsections and frames. Do not copy the
  demo's personal metadata, unrelated feature-tour frames or sample citations
  into the user's talk. Use confirmed metadata or explicit placeholders.
  Do not add a document class or
  document environment to chapter files, or compile them independently.
  Graphic and nested input paths are relative to the project root. Local PDF
  file/video hyperlinks are relative to the PDF in `build/`: use
  `\href{run:../assets/file.mp4}{...}` for a root asset. Use section
  opening pages explicitly after each `\section`; their default is always the
  full primary-color (purple by default) page: `\sectioncoverpage[primary]{...}`. Use an image, white
  split, or another visual variant only after the user requests it or confirms
  the choice.
  The bundled demo passes the user-selected campus image paths directly to
  `\sectioncoverpage`; preserve these examples when maintaining the demo.
  Select talk images in the talk source, not through numbered image aliases
  in the school profile. New decks still default to the configured primary color.
  Image backgrounds default to the original image's right edge aligned with
  the page's right edge, with proportional scaling and vertical centering.
  Finish proportional scaling before calculating alignment: measure the final
  image box width, then set its left position to page width minus that width.
  Keep the demo's image options empty so users can adjust the visible region
  by editing the original asset; enable trimming or horizontal centering only
  when the user explicitly requests it.
3. Write slide text for scanning and speaking. Put the explanation, transitions,
   definitions, caveats, and source reminders in `build/main.notes.json` instead of
   crowding the slide. Never use notes to hide a claim that should be visible
   on the slide.
4. Run `make draft`, inspect the actual page images and layout report, and
   revise overloaded pages using the layout rules below. Repeat until readable.
   Inspect the generated page count and keep the notes
   list aligned with the final PDF page order. Generated section pages,
   overview pages, reference continuation pages, and the closing page each need
   their own notes entry, even when the entry is an empty string.
5. Convert the PDF with the bundled converter, then validate slide count,
   speaker notes, native section boundaries, document metadata, navigation
   links, citations, and the visual checkpoints below.
   Deliver links to `build/main.pdf` and `build/main.pptx` with a concise account
   of any placeholders or unresolved facts. For later user feedback, update the
   authored talk and notes, repeat the draft review and rebuild. Do not ask the
   user to perform routine authoring or build steps that the agent can complete.

Input material stays under `materials/`; derived talk figures may go under
`materials/derived/`. Preserve `materials/.gitkeep`: it is tracked and packaged
so fresh clones and source ZIPs include the input folder. All other material
contents, `main.tex`, `chapters/talk/`,
`bibliography/main.bib` and `build/` are ignored by Git and excluded from source
ZIPs. Do not put private talk figures into the distributed `assets/` folder.
`prompt.md` is included in source packages: keep its distributed copy generic
and do not publish a user-filled private brief.

### Speaker-note contract

Speaker notes are generated artifacts, stored beside PDF/PPTX outputs in
`build/`: `build/main.notes.json`, or `build/<MAIN>.notes.json` for another entry.
Create the directory when needed and write/update the notes there after inspecting
the final page order. Do not create per-deck notes in the project root or commit
them to source control. Make and direct converter calls both auto-load notes
beside the input PDF; `--notes-dir` can select a different directory explicitly.
The source ZIP excludes generated notes. A fresh source copy can build the demo
with empty notes; agent-authored decks must generate their own complete notes.
The file must contain one entry per final PDF page. The preferred format is:

```json
{
  "slides": [
    {"notes": "开场：说明本页要回答的问题，并给出讲解顺序。"},
    {"notes": "解释图中趋势；停顿后强调右侧结论。"},
    {"notes": ""}
  ]
}
```

An entry may also be a plain string. Notes should be useful spoken guidance:
what to emphasize, how to transition, what a number means, which caveat to
mention, and which citation supports it. They should not simply duplicate the
visible bullets. Extra entries are an error because they would shift notes onto
the wrong slides. The default `make` build rejects both extra and missing
entries when a notes file exists. Use an empty string for intentional blanks.
No page-count check detects same-length reorderings: recheck the notes after
adding, deleting, or rearranging frames. When generating a new deck, always
create its notes file; a build without one is allowed for the template demo
and clearly reports empty notes.

Use this command for the final export:

```bash
make
```

When invoking `tools/images_to_ppt.py` directly, use
`--notes path/to/notes.json` for a different notes file, `--notes-dir path/to/output` to
select a different notes directory, `--no-notes` to
disable auto-loading, and `--verbose` to inspect every link. The default export resolution is 600 DPI. The PPTX keeps the
rendered slide as an image and writes the notes into PowerPoint speaker notes;
the slide text is therefore intentionally not editable as native PowerPoint
text.

The converter automatically maps level-one PDF bookmarks (`\section`) to native
PowerPoint sections; subsections and overlays remain within their parent section.
Pages before the first section form a cover/introduction section. Keep Beamer's
section bookmarks enabled. The class embeds cover metadata in PDF Info fields,
so no metadata sidecar or extra export flag is needed. Title and author become
standard PPTX properties; subtitle, group, advisor, talk date and contact become
the custom properties `Subtitle`, `Group`, `Advisor`, `PresentationDate` and
`Contact` when supplied. Do not invent missing properties or confuse the talk
date with file timestamps. Before delivery, verify section names, boundaries,
complete slide coverage, and these properties against the final source.

## School profile boundary

Use the institution-neutral `campus` theme and `\campus…` identifiers. All
school-specific functional palette values and logo/wordmark paths belong in
`theme/campuscolor.sty`. Keep demo titles, groups and personal metadata as
literal demo content in `chapters/metadata.tex`; user talk metadata belongs in
`chapters/talk/metadata.tex`. Do not add schooldemotitle or
schooldemogroup profile commands. Do not hard-code a school's
brand colors, emblem or wordmark in the theme or in `main.tex`. The supplied profile defaults to
Tsinghua and must retain the existing visual output when maintained.
`primary` means the configured main color; `purple` is an alias of `primary`
for section pages only. Covers use the fixed primary-color split
layout by default, with `\titlebackground{primary}` as the only explicit setting.
A starred `\titlebackground*{primary}` has the same effect; the star
does not select a layout. Do not offer full-color, white, image or purple cover modes.
School changes are made in the profile; talk content belongs in
`main.tex` and `chapters/talk/`, demo content in `example.tex` and its chapters.
Keep layout geometry in the theme. Name profile colors by purpose:
`maincolor`, `tipcolor`, `notecolor`, `alertcolor`, `examplecolor` and
`definitioncolor`. The supplied definition box uses amber (`B36B16`) to remain
distinct from notes, whose color follows `maincolor`. Do not add unused hue-named palette entries.
The footline background always uses `maincolor` with white text. Change the
profile's `maincolor` to change it; do not add a separate footline-color option
or call `\footlinecolor` in presentation sources.
Campus photographs, section backgrounds and demonstration graphics are talk
content: pass their asset paths directly in chapter or fixture files.
Do not create `imageone`/`demographic` registries in the school profile.

## Scope
This repository is a Beamer template for weekly group-meeting slides.
When assisting the user, prioritize:
- keeping the template visually stable,
- keeping slides easy to edit,
- keeping all outputs compilable with XeLaTeX + biblatex/biber.

## Repository organization

Keep `example.tex` and `prompt.md` at the root, the agent-authored `main.tex` at
the root locally, and document-class, theme, color and school-profile
files in `theme/`. Keep `.latexmkrc` with the project: it adds `theme/` to TeX's
search path, so document sources keep using `\documentclass{campusbeamer}`.
Always build from the project root. Keep metadata, presentation sections and
reusable demonstration fragments together in `chapters/`, with demo code sources
in `chapters/code/`. Keep generated user content separately in `chapters/talk/`.
Keep bibliography databases in `bibliography/`, and Docker
build files and the container entrypoint in `docker/`. Do not add a root
`refs.bib`, `Dockerfile` or `.dockerignore`. Do not create a separate examples directory. Keep detailed
documentation in `docs/`, test source in `tools/fixtures/`, and generated output
in ignored `build/`. Do not commit historical logs, virtual environments or
private presentations. Record confirmed outside inspirations in the final
Acknowledgements section of `README.md` and keep `README.en.md` in sync.
Credit engineering practices, visual influences and early template origins
accurately; do not add unrelated research or recreate a separate credits file.
The original procedural `assets/presentation_demo.mp4` is documented as CC0-1.0
in `assets/README.md`, with its generator and a separate dedication file. Use
this small local video for media demonstrations. Do not add another demo video.
User-facing documentation describes the current template; do not mention removed
files, commands, or private revision history. The maintainer has confirmed that the Tsinghua marks
and campus images come from https://vi.tsinghua.edu.cn/ and
https://www.sigs.tsinghua.edu.cn/en/7453/list.htm; some images have been cropped.
Preserve the source, trademark and use notices in `assets/README.md`, including
their application to the derived preview images. Do not label these confirmed
sources as unknown, assert that cropping was the only modification, or extend
the code's GPL or video's CC0 license to the Tsinghua images. The maintainer is
currently unable to reach the rights holders or photographers and has chosen
to retain the documented assets with a rights-holder contact and correction/
removal notice. Preserve that notice and its existing public contact address;
do not repeatedly ask the user to contact these parties during routine template
maintenance. Explicit asset permissions and individual photographer credits
remain unavailable; do not invent an authorization or university endorsement,
or describe the contact notice as a license. Update the records if the user
later supplies permissions, credits or a request to remove an asset.

## Source Of Truth
- `prompt.md`: sample natural-language request; the user's chat or filled brief defines the talk.
- `materials/`: pre-created input folder; only `.gitkeep` is distributed,
  user-provided papers, source projects, figures and data remain local.
- `example.tex`: bundled feature/layout reference, class options and explicit demo chapter order.
- `main.tex`: agent-authored user entry, class settings, bibliography resources and chapter order; not distributed.
- `chapters/talk/`: agent-authored user metadata and section content; not distributed.
- `chapters/metadata.tex`: demo title, group, presenter, advisor and date.
- `chapters/01_*.tex` through `05_*.tex`: section content, backgrounds, frames and demo closing pages.
- `chapters/*-guide.tex` and `chapters/math-examples.tex`: demonstration fragments
  included by their owning section; `chapters/harness-guide.tex` introduces the
  brief/materials workflow after the demo cover; `chapters/code/`: demo code.
- `theme/campusbeamer.cls`: public document-class options, package setup and bibliography-resource command;
  layout geometry stays in the theme and school identity stays in the profile.
- `theme/beamerthemecampus.sty`: theme internals (headline, footline, title page,
  backmatter, fitted figures, paper frames, right-image frames, corner citations).
- `theme/campuscolor.sty`: the single school profile (functional colors and emblem/wordmark paths);
  loads xcolor before defining colors. Preserve its default rendering.
  Talk metadata and images stay in talk sources; do not recreate school-config.tex.
- `bibliography/refs.bib`: demo bibliography entries.
- `bibliography/main.bib`: verified user-talk bibliography; not distributed.
- `assets/`: logos and backgrounds.
- `tools/images_to_ppt.py`: PDF-to-PPTX export with clickable link and notes support.
- `tools/draft_preview.py`: low-resolution page previews and layout diagnostics.
- `tools/literature.py`: DBLP search/BibTeX and DOI-matched citation snapshots;
  Python standard library only. See `docs/literature.md` for the retrieval workflow.
- `build/main.notes.json`: generated speaker notes aligned to the final PDF page order;
  retained by `make clean`, ignored by Git and excluded from source packages.
- `docs/notes.example.json`: a source-controlled format example, not a deck's notes.
- `pyproject.toml` and `uv.lock`: the minimal `uv` environment for the converter.
- `Makefile`: the shared build entry point for agents and humans.
- `.latexmkrc`: local `theme/` search path, XeLaTeX output and intermediate directory (`build/`) and cleanup rules.
- `docker/Dockerfile` and `docker/Dockerfile.dockerignore`: the container build
  environment. Build from the root with `docker build -f docker/Dockerfile -t campus-beamer:local .`,
  mount the project at `/workspace` and run the same Make targets. See `docs/docker.md`.
- `docker/entrypoint.sh`: validate dependency files before using the
  image's prebuilt Python environment; rebuild the image after dependency changes.

Do not manually edit compiler-generated files in `build/`, such as `main.aux`, `main.log`, `main.bbl`, `main.bcf`, `main.nav`, `main.snm`, `main.toc`, `main.fls`, `main.fdb_latexmk`.
Agent-generated `build/*.notes.json` files are editable deliverables: create and
revise them to follow the final page order.

## Build Commands

Run from the template root:

```bash
make                 # main.tex if present, otherwise example.tex -> PDF -> PPTX, 600 DPI
make MAIN=example    # Explicitly build the bundled reference demo
make draft           # Fast layout iteration: PDF + 96-DPI PNGs/contact sheets/report
make draft PAGES=3,8-10  # Only render these PDF pages for a local revision
make DPI=200         # Faster preview
make MAIN=talk       # talk.tex -> build/talk.pdf -> build/talk.pptx, build/talk.notes.json
make pdf             # Compile PDF, then remove LaTeX intermediates on success
make test            # Converter tests, no extra test dependencies
make literature QUERY="paper title" # DBLP candidates as JSON
make bibtex DBLP_KEY=conf/... CITE_KEY=MyPaper # Stage BibTeX + citation snapshot
make citations DOI=10.../... # Citation count, source, date and usere/userf fields
make clean           # Clean intermediates, retain final outputs and notes
```

Prerequisites: GNU Make, uv, XeLaTeX, latexmk, biber and the template's TeX
packages/fonts. Local-video PPTX export additionally needs FFmpeg (included in
the Docker image); PDF-only and non-video exports do not. The converter extracts
a first-frame poster, scales proportionally and centers within the PDF video
placeholder, and removes the placeholder border/text from the PPT background.
Use `\XeTeXLinkBox{\fbox{...}}` inside the local-video `\href` so the PDF link
covers the complete placeholder. Keep the source PDF intact. A missing decoder
or undecodable video must fail without replacing the previous PPTX.
`uv run --frozen` creates/syncs `.venv` automatically; do not
copy `.venv` between machines. Keep `pyproject.toml` and `uv.lock` with the
folder. After editing dependencies in `pyproject.toml`, explicitly run `uv lock`
before building; `--frozen` deliberately does not update the lock. Missing system tools must be reported, not silently skipped.

Keep the shared lockfile on official PyPI. Regenerate it with
`uv lock --no-config --default-index https://pypi.org/simple`, with any extra
index environment settings unset. Check versions and hashes before committing;
do not hand-edit artifact URLs or commit a personal mirror's lockfile.

`latexmk` tracks TeX inputs, bibliography and assets and reruns as needed.
PPTX conversion runs only after successful compilation and always reruns so
notes edits and DPI changes take effect. Link loss and notes-count mismatch
fail the build before replacing the previous PPTX. A previous output may still
exist after failure; never present it as the newly built result.
All PDF/PPTX outputs and TeX intermediates are written to `build/`, as configured
in `.latexmkrc`; the editor uses the same directory. `make`, `make pdf`, and
`make draft` remove LaTeX intermediates after their
final step; failed builds retain intermediates and logs for diagnostics. Use
`make clean` after inspecting a failed build. Do not run clean and build
targets together with `make -j`.

## Per-page layout and draft iteration (Required)

A successful compilation is not evidence that a slide is readable. Inspect
**every final PDF page**, including each overlay, section page and references
continuation. No content may be cut off, overflow the body area, collide with
the headline/footline/navigation/citations, or become too small to read.
Check title wrapping, whitespace, alignment, tables, equations, captions and
image labels as well as bullet text. More than 5–6 bullets or several unrelated
ideas is a signal to review density, not a hard quota.

When a page is crowded or overflows, fix it in this order as appropriate:

1. Condense wording and remove repetition while retaining the main claim,
   evidence, units, assumptions and qualifications needed to interpret it.
2. Move derivation details, examples, background and speaking transitions to
   the corresponding speaker notes. Do not move essential evidence or limiting
   conditions out of sight if doing so would make the visible claim misleading.
3. Split the frame into coherent pages, each with one message. Update titles,
   narrative transitions, navigation and **all affected notes indices**.
4. Adjust column proportions, image sizes and spacing within the theme's
   existing geometry. Do not use tiny fonts, blanket `shrink`, negative spacing,
   clipping or suppressed warnings to conceal excessive content. Preserve the
   fixed theme margins and footer. References may use the existing reference
   layout options, but still must be readable.

Routine condensation and splitting are authorized authoring work. Ask only
when the fix would change meaning or violate an explicit time/page constraint.

Use this feedback loop during drafting:

- Run `make draft` after the first pass. It compiles the same layout as the
  final build and skips PPTX rendering and notes-count validation, so incomplete
  notes do not block early layout work. It does not enable TeX's `draft` option
  or remove images/overlays, which would change what you need to inspect. After
  a successful preview report, LaTeX intermediates in `build/` are removed automatically.
- Read `build/draft/main/report.txt` (or `report.json`), inspect every
  `contact-*.png` for overall balance, then open the relevant `page-XXXX.png`
  images at readable size. A human can open `index.html` in a browser.
- Review every Overfull warning and inspect the corresponding source/log
  context. The report's log line number is **not** a PDF page or source-file
  location. Underfull is a spacing hint. Warnings may arise from the theme;
  do not silently suppress them or equate zero warnings with good layout.
  Note any remaining benign warning and the visual evidence for that judgment.
- Edit, run `make draft PAGES=...` to inspect changed pages and neighbours, and
  repeat. `DRAFT_DPI=144` gives sharper text when needed. `MAIN=talk` uses
  `build/draft/talk/`. Check the exit code and report timestamp/hash: failed
  builds leave old files behind. A subset run replaces the previous previews
  with that subset, and the report still covers the whole compilation log.
- Before delivery, run a full `make draft` with no PAGES filter and review every
  page again; align notes to the final order and run `make` for the final PPTX.
  If final compilation changes pages, repeat the visual review. Never claim
  visual validation if previews could not actually be inspected.

## Visual Invariants (Must Keep)
These are confirmed user preferences and should not regress:
- Footline text must be vertically centered in the primary-color bar (not stuck to top/bottom).
- Footline colors are fixed to white text on `maincolor`; no independent color setting.
- Footline horizontal layout must remain: left `frame/total`, right `author | title`, with side margins preserved.
- Title-page top-left logo block must be flush with the page top (no white gap above it).
- Use the `\schoolemblemondark` and `\schoolemblemonlight` assets from
  `theme/campuscolor.sty` for the emblem. Draw the background
  block in the theme: primary color on white pages, white on primary-color pages. Its width
  is one `\Huge` baseline; its height follows the existing three-row header grid.
  The emblem's bounding rectangle must be inset from the block's left, right
  and bottom edges by `3pt`; scale proportionally and keep its
  horizontal center aligned with the block. Top padding follows from these dimensions.
  Keep the block geometry independent of later emblem-size adjustments.
- The cover always uses the current white-left, primary-color-right split layout.
  Its lower-right university wordmark uses `\schoolwordmarkondark` on the primary color,
  as configured in `theme/campuscolor.sty`. Draw the cover
  panels in the theme rather than using an opaque bitmap backdrop. Keep the
  original right/bottom anchors independent of the panel geometry: each margin
  is one `\large` baseline. Fit the wordmark's width between the diagonal
  midpoint's vertical line at 61.8% of page width and that fixed right anchor;
  scale proportionally and derive its height from the asset ratio. Its left
  edge must align by scaling, without moving the right edge. Diagnostic labels
  must show the actual dimensions, left alignment and margin font basis.
- Split-panel diagonals cross the page's half-height at 61.8% of its width.
  The line makes a 72-degree angle with the horizontal, with its top end to the
  right of its bottom end. Measure counterclockwise from horizontal-right
  towards the upper-right end in Cartesian coordinates. Derive
  both endpoints from these parameters and use the same geometry for the solid
  cover panel, section split images and white section panels. Keep the default
  full primary-color (purple by default) section pages. Red guides must show the midpoint and angle convention.
- Cover and closing-page subtitles use `\Large`; course/group, presenter,
  advisor and date use `\normalsize`. On the cover, the course/group line uses
  the same black color as the presenter. All closing-page content text is white.
  Place the information block directly below the title
  with no extra gap. Both closing thank-you lines
  use `\LARGE`. Keep the existing title anchors and metadata alignment.
- Corner citations must be plain text (no border box, no filled rectangle), left-aligned, compact line spacing, gray tone.
- Main slide text margins must remain symmetric; the body left edge aligns with
  the left edge of the top-left logo block. Header titles and subtitles start
  one `\normalsize` baseline after the logo block's right edge.
- Description labels are right-aligned within each environment; the widest label starts at the body left edge, and the description body begins at one shared column.
- Ordinary frame headers show the current subsection in the upper frametitle-style
  line and the frame title in the lower framesubtitle-style line. The lower line
  uses `\normalsize`, with its grid row based on that font's baseline; its lower
  edge aligns with the bottom of the logo block. Both lines use the shared
  horizontal gap `\campusheadertextgap` (one `\normalsize` baseline).
  Examples use section → subsection → frametitle without per-frame subtitles.
- Single-line headers (table of contents, references including continuations,
  and ordinary frames without a subsection header) use `\LARGE`. Their text
  box bottom sits one `\tiny` baseline above the logo block bottom
  (`\campusheaderemptybaseline`); retain the shared horizontal
  title position and reserve the same header height as two-line frames.
- Section opening pages list all current subsections with section.subsection numbers; one to three entries use one column, while four or more use alternating left/right rows.
- Section opening titles share the title-page title's vertical position; the subsection list and introduction extend downward from that fixed title anchor.
- Section opening label-to-title spacing uses one `\Large` baseline;
  title-to-subsection-list and list-to-introduction spacing each use one
  `\normalsize` baseline. Diagnostic arrows must use these same font bases.
- Backmatter (thank-you slide) vertical placement remains fixed and visually centered/lower-centered as requested.

If a change targets only vertical alignment, do not unintentionally modify horizontal positions.

## Document Class And Layout Options (Edit In `main.tex`)
Configure new decks through the document class; keep theme geometry fixed.
Keep all public Campus class options explicitly listed with their defaults and
brief value comments in the bundled `example.tex`. Generate the user's entry
from these class options, selecting values appropriate to the brief:

```tex
\documentclass[
  language=chinese,   % chinese / english
  cjk=auto,           % auto / true / false
  bibstyle=ieee,      % bibliography style, e.g. authoryear
  bibsorting=none,    % citation order; e.g. nyt for name/year/title
  mathfont=serif,     % serif / sans
  navigation=true,   % true / false
  cornerwidth=4.8cm,  % default corner citation width
  layoutguides=false % true / false, class option only
]{campusbeamer}
\campusbibresource{bibliography/main.bib}
```

Use `language=chinese` (default) or `english` for theme-generated text:
TOC and references titles, section labels, advisor label, callout defaults,
figure/table labels, and closing text. User content is not translated.
Chinese mode automatically loads xeCJK; English mode does not unless
`cjk=true` is supplied for mixed-language content. The low-level
`\campussetlayout{template language=...}` changes labels only, not package loading.
`\sectiontocpage` has no arguments; its title is generated from the language setting.

Use `navigation=false` to hide both footer navigation rows. Inside a frame,
`\setcornercitewidth{6cm}` changes subsequent corner citations for that frame only;
the next frame restores the default. This also applies to automatic paperframe citations.
References font size is set locally with `\referencespage[shrink][\small]` or
`\referencespage[break][\footnotesize]`; append `[twocolumn]` for a two-column
references page (the default is `onecolumn`).

Other options include `mathfont=sans`, `bibstyle=...`, `bibsorting=...`, and
`layoutguides=true`; see `docs/class-options.md`. Configure diagnostic overlays
only through the document-class option `layoutguides=true/false`; do not add
commands to enable or disable them. The dedicated alignment-check demo frame
always includes its own reference lines. Existing Beamer documents
with `\usetheme{campus}` and low-level `\campussetlayout` overrides remain
supported, but new decks should use the class interface.

## Citation Workflow For Slides
Use `\cornercite` as the only public slide-citation command.

### Retrieve and verify literature

When literature lookup is authorized, use the bundled tool rather than typing
invented bibliography entries or counts. These targets use `python3` and need
no extra Python packages, TeX installation, or changes to `uv.lock`:

1. Run `make literature QUERY="title or author keywords"`. Inspect the JSON
   candidates and match title, authors, year, venue and publication version.
   Never assume the first result is the intended paper. If ambiguity changes
   which work supports a claim, ask the user; routine exact matches need no
   additional confirmation.
2. Run `make bibtex DBLP_KEY=conf/... CITE_KEY=MyPaper`. This saves a single
   self-contained DBLP entry to `build/literature/paper.bib` and provenance to
   `build/literature/paper.json`. Use distinct `BIB_OUTPUT` and `BIB_REPORT`
   paths when collecting several papers. The default count provider is
   OpenAlex; use `CITATION_SOURCE=semantic-scholar` to choose Semantic Scholar
   or `CITATION_SOURCE=none` for BibTeX alone. Providers are never silently
   switched, and counts are not obtained from DBLP's bibliographic search API.
3. Review the downloaded entry, then merge it into the active deck's bibliography (`bibliography/main.bib` for agent-authored talks), checking existing
   keys, DOI and title for duplicates. Preserve existing keys used by slides,
   custom `usera`/`userb`/`userc`, and other verified fields when enriching an
   existing entry. Do not use the active bibliography as `BIB_OUTPUT`: output replaces a file,
   rather than appending a database. The tool does not modify the active bibliography itself.
4. Citation lookup must match the exact DOI. For an existing entry, run
   `make citations DOI=10.../...` and copy the returned `bibtex_fields` into
   that entry. `usere` is the count; `userf` includes the provider and UTC
   retrieval date. Also retain the JSON snapshot under `build/literature/`
   or the source URL/date in speaker notes when needed for the talk.
   Do not compare counts from different providers as though their coverage
   were identical. A citation count is not evidence for a paper's claims.
5. Missing DOI, missing record, rate limits, HTML verification pages, and
   network errors mean the count is unavailable, not zero. On failure do not
   present an older staged file as fresh output. Fetch BibTeX with source
   `none` if needed; hide/omit unavailable count fields. For DBLP verification
   pages, try its official mirror with `DBLP_HOST=dblp.uni-trier.de`, or use a
   browser-downloaded single standard entry with `INPUT_BIB=path/to/paper.bib`.
   Never manufacture metadata or silently use a fuzzy title match for counts.

Check required metadata before citing: title, authors, year, proceedings or
journal and, when applicable, DOI, pages, volume and issue. Resolve missing
fields from authorized primary sources, or explicitly document an unavailable
field; do not invent it. BibTeX and citation counts do not establish the
paper's findings. Read user-supplied or authorized paper content before writing
substantive claims about the work. Missing paper content is a confirmation
case when it changes the argument.

### Cite verified entries

1. Add a verified entry in the active bibliography (`bibliography/main.bib` for user talks; `bibliography/refs.bib` for the demo).
2. Optionally add `usera` for the compact slide form. Legacy `shorthand`
   values are migrated automatically so they do not replace numeric labels.
3. Put one or more comma-separated citations in the upper-right corner:

```tex
\cornercite{Zadeh2017TensorFN,Liu2018EfficientLM}
```

4. Select a lower position with the optional argument:

```tex
\cornercite[bottom-left]{Zadeh2017TensorFN}
\cornercite[bottom-right]{Liu2018EfficientLM}
```

Supported positions are `top-right` (default), `bottom-left`, and
`bottom-right`. Each key is rendered on its own line using the default
slide-citation format.

5. Generate one summary frame for all cited entries before the thank-you page:

```tex
\referencespage                         % shrink to one frame (default, one column)
\referencespage[break]                  % add continuation frames when needed
\referencespage[shrink][\small][twocolumn] % compact two-column summary
```

The summary contains cited entries only and numbers them in citation order when
`sorting=none` is active. The default stays on one frame; `break` favors
readability by adding continuation frames when needed.

## Content Authoring Rules
- One frame, one message; avoid dense paragraphs.
- Prefer short bullets and figures over paper-style prose.
- Start each section with `\sectioncoverpage[primary]{...}` by default. A section
  page is full primary-color (purple by default) unless the user explicitly chooses another treatment.
- Prefer `\fitgraphic[width=...,height=...]{file}` for images and PDF pages.
  Its width and height are fractions of `\paperwidth` and `\paperheight`; use
  `page=...` to select a page from a multi-page PDF.
- Prefer `\fitfigure[width=...,height=...]{file}{caption}` when a fitted graphic
  also needs a caption; pass an empty caption argument to suppress it.
- For repeated paper walkthrough slides, use
  `\begin{paperframe}{title}{keys} ... \end{paperframe}` so the current
  subsection header and comma-separated corner citations stay consistent.
  Append `[bottom-left]` or `[bottom-right]` after `{keys}` to move the
  automatic citation; the default is `[top-right]`. Append another optional
  length such as `[6cm]` to set this paper frame's citation width.
  Optional `userb`, `userc`, `usere`, and `userf` BibTeX fields append
  institution, venue/status (use `arXiv` for a preprint), citation count,
  and its snapshot date in the same compact citation style.
- Use `\begin{rightimageframe}[image width=.40,page=...]{title}{file}` for a
  normal frame with a full-height right image that stops above the footline;
  put the remaining content in the environment body.
- If verbatim/code is present, use `[fragile]` frame.
- Keep wording concise for speaking, not manuscript writing.
- For every generated final PDF page, add one corresponding `build/main.notes.json`
  entry. Include notes for title, section, overview, references, and closing
  pages; use `""` when no spoken note is needed.

## Change Checklist Before Finishing
After substantial content/layout edits, use the draft loop above and visually
check every final page, with particular attention to:
- title page,
- one normal content frame with footline,
- one frame with corner citations,
- references summary page,
- backmatter/thank-you page.
- at least one PowerPoint speaker-note entry and one internal jump in the PPTX.
- native PowerPoint section names/boundaries and document properties against the source.

Only finish after successful compilation, per-page visual inspection, and
resolution of visible overflow, overlap and unreadable density. Report any
unresolved issue accurately; do not mark an uninspected deck as ready.
