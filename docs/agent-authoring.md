# Agent guide: authoring a talk

Read this guide for a new or revised `main.tex` talk. It is intentionally
separate from the root `AGENTS.md` so maintenance tasks do not load deck-writing
details.

## Before writing

Read [STYLE.md](../STYLE.md) for the user's editable presentation preferences.
Explicit instructions in the current brief take precedence over those defaults.

Read the user's draft directly from the root `outline.md` (or another explicitly
supplied brief) and inspect only the supplied paths under `materials/`. A short
request such as “根据大纲制作 PPT” is sufficient to start this workflow.
If the outline contains only unfilled fields and no brief was supplied, ask for
the intended talk. An archive may be unpacked into a working copy while the
original is retained. For a paper project, follow its entry file, inputs,
captions, figures, and bibliography; read the relevant paper text before making
substantive claims. Prefer its original figures. If a figure exists only in a
PDF, extract or crop it without changing its meaning and record its source in
the notes.

Ask one bundled question before dependent authoring when the audience, purpose,
language, duration, slide count, evidence, external research, private material,
or requested visual treatment is materially unclear. An explicit request for
DBLP/BibTeX/citation lookup authorizes that read-only lookup within scope;
availability of a tool alone does not. Local paper sources authorize reading
their text, figures, captions, and bibliography. Do not substitute demo claims
for missing evidence.

Use routine judgment for the rest: keep the 16:9 layout, source language,
concise slide wording, local assets, primary-color section pages, and a slide
count derived from the brief. State a consequential but non-blocking assumption
and continue.

## Two-stage outline workflow

The user supplies basic information and a free-form draft in `outline.md`.
Read the draft for its purpose, priorities, facts, and material paths. Use
[STYLE.md](../STYLE.md) to guide the eventual presentation.

### Inventory the supplied materials

Before outline confirmation, enumerate each user-specified materials directory
with `rg --files -uuu <directory>` so Git ignore rules cannot hide inputs.
Limit enumeration to the authorized directories. Inspect actual file types,
read relevant documents, view relevant images directly, and check local assets
referenced by Markdown or TeX. If enumeration is empty, verify the directory
and the explicit referenced paths before reporting a missing asset.

Add a material-coverage section to the detailed outline. For each relevant file,
record its relative path and type, read/view status, extracted topic/evidence
or visual role, intended section/subsection, and usage: full, partial,
notes/source only, or excluded with a reason. Record unreadable, inaccessible,
damaged or uncertain-version inputs and their effect on the argument. Exclude
`.gitkeep` from the content inventory. Coverage means inspected inputs with
reviewable choices; unrelated, duplicate or out-of-scope material can be omitted.
Preserve explicit scope limits. A screenshot is evidence of its captured content,
not proof of the website's current state. Local use does not authorize public
redistribution. Content-bearing omissions found after confirmation return to
outline review before entering slides or notes.

### Stage 1: develop the detailed outline

Expand and organize the draft into substantive `section` and `subsection`
content in `build/outline-normalized.md`. This is the content-development stage:
explain the ideas, build the argument, fill in supported definitions or steps,
select evidence and examples from the authorized material, and plan transitions
and limitations. Do this work before creating slide source or speaker notes.
Do not limit the result to a list of headings or repeat the draft verbatim.

The reviewable outline must contain:

- the supplied metadata, audience, goal, and speaking-time budget;
- each section's title, purpose, order, and approximate speaking time;
- each subsection's topic, developed content and key points, supporting
  figures/data/code/citations, and explanations to cover in the talk;
- source paths or references for factual claims, required visible evidence,
  speaker-note material, transitions, and necessary limitations;
- the material inventory, coverage mapping, and explained exclusions;
- proposed content changes and unresolved facts or material gaps.

Within the supplied purpose and materials, use judgment to develop explanations
and restructure the narrative. Present proposed additions with their evidence
in the outline for review. External research, proprietary assets, or changes to
user-provided facts require prior authorization. Label unsupported items as
questions; never invent results, examples presented as facts, or citations.
Keep the user's original draft intact and record which outline revision the
user actually confirmed. While awaiting confirmation, continue inspection and
outline work. Confirmation authorizes the reviewed content for production.

### Stage 2: compose and lay out the slides

After confirmation, create `main.tex`, `sections/talk/`, verified citation
resources when needed, and native `\note` commands alongside the frames from the approved outline.
Map sections and subsections to the Beamer hierarchy, choose frame boundaries,
condense visible text, distribute approved explanations between slides and
notes, and select layouts for the figures, equations, code, and links.
Compile, inspect the actual pages, and validate PDF/PPTX output.

Frame count and boundaries are layout decisions. Split crowded frames, combine
sparse ones, shorten titles, or move approved detail into notes as needed while
preserving the argument, evidence, necessary conditions, and time budget.
A layout split does not require another content approval. Keep notes aligned
with the final PDF pages.

New claims, examples, recommendations, or substantive explanations discovered
necessary during production return to the detailed outline for review before
entering slides or notes. Later content-bearing revisions follow the same loop;
layout, spelling, and formatting fixes can proceed within the approved content.
Public-template commits must exclude filled private outlines. Source packaging
uses `tools/templates/outline.md` for the distributed starter outline.

## Source layout

Start a new deck with the class interface, for example:

```tex
\documentclass[
  language=chinese, cjk=auto, bibstyle=ieee, bibsorting=none,
  mathfont=serif, navigation=true, cornerwidth=4.8cm,
  layoutguides=false
]{campusbeamer}
```

Keep metadata in `sections/talk/metadata.tex`, class/build settings in
`main.tex`, and one section per file under `sections/talk/`. Select those files
explicitly with `\input`. Do not put a class or document environment in a
chapter. Use `\campusbibresource{bibliography/main.bib}` only when the talk has
verified citations; leave `bibliography/refs.bib` unchanged for the demo.

The class already loads the theme, Chinese support when requested, math setup,
and biblatex. English decks containing Chinese text need `cjk=true`; do not
duplicate package loads or add a biblatex class option. New covers use the
fixed primary-color split automatically. Use `\sectioncoverpage[primary]{...}`
for section openings unless the user confirms another treatment. Select talk
images in the talk source, not through school-profile image aliases.

For a Chinese talk, format a supplied complete ISO date as `\date{2026年10月14日}`,
preserving its value. Do not substitute `\today` for a specified event date.
Keep empty/custom dates and English formatting as requested. The existing
`\date` interface does not parse ISO dates: PDF date metadata and PPTX
`PresentationDate` contain the same resolved text as the display, so a Chinese
formatted date is also a Chinese metadata string (not a separate ISO value).

## Content and notes

### Two-line body headers

Organize body content as `section → subsection → frametitle`. Every ordinary
body frame, including `paperframe` and `rightimageframe`, needs a non-empty
current subsection and its own title. The theme displays the subsection on the
upper line and the frame title on the lower line. After each new `\section`,
declare a meaningful `\subsection` before the first body frame; the previous
section's subsection does not carry over. A short section can have one
subsection shared by several frames. Choose a topic for the subsection and a
specific message for each frame, rather than repeating the same text twice.

```tex
\section{实验结果}
\sectioncoverpage[primary]{本节介绍实验设置与结果分析。}
\subsection{性能对比}
\begin{frame}{主要结果}
  % Upper line: 性能对比; lower line: 主要结果.
  本页的核心证据。
\end{frame}
```

Generated TOC and references pages (including continuations) retain single-line
headers; cover, section-opening, and closing pages retain their dedicated
layouts. The no-subsection single-line fallback exists for compatibility, not
as an authoring choice for ordinary body pages. Do not use `plain`, clear the
header, or manually add line breaks or `\framesubtitle` to bypass this structure.

### Progressive reveals

Use Beamer overlays when approved content has a meaningful explanation order:
derivations, process steps, dependencies, or before/after states. Simple claims
and comparisons needing simultaneous inspection can stay fully visible. Choose
reveals during layout; no new content approval is needed merely to stage the
approved argument. New claims still return to outline review.

Prefer cumulative `\item<1->`, `\uncover` or `\onslide` to reserve layout space.
For replacement states, use `\only` inside a fixed `overlayarea`; select the
final state explicitly for handouts, e.g. `\only<2|handout:1>{...}` and exclude
earlier states with `handout:0`. Keep both header lines, captions, source URLs
and retained evidence stable across stages. Necessary conditions must be visible
whenever the associated conclusion is visible. Do not use overlays to disguise
an overcrowded final page.

Each overlay becomes a PDF page and a PPTX slide. For a useful smooth reveal,
use `\transfade<2-|handout:0>[duration=0.2]` on subsequent stages; the converter
preserves Fade and Dissolve as native slide transitions. Whole-slide rendering
does not recover editable object animations. Do not add effects to every frame
or infer overlay groups from similar page images. Keep manual advancement unless
timed playback is requested. See the [overlay example](usage.md#逐步显示与换页效果).

Write notes for each final rendered stage: explain what becomes visible and how
to advance, without repeating the entire frame's script at every step. Recheck
page counts, order, links and final-state coverage after adding overlays.

### Semantic boxes and description labels

Keep the main comparison, table or diagram as the page's primary structure.
Organize necessary related conditions or constraints with a specific heading
or one compact titled box: `tipbox` for operational advice, `notebox` for
conditions or context, `alertbox` for critical restrictions, and the matching
definition/example environments. Use descriptive titles. Select by meaning;
avoid mechanical boxing or repeated summaries. Condense or split when a box
makes the page crowded.

The optional argument to `description` is a width sample; Beamer does not scan
labels for the widest one. Select the actual widest label at the current font
and size, then check right edges and the explanation column in the PDF. For
example, use `[Host / HostName]` for a list containing `Host / HostName`, `User`,
`IdentityFile` and `IdentitiesOnly`. Check each column separately; keep wrapping
natural without spaces or negative-spacing fixes.

### Slide text and speaker notes

Apply the density and notes criteria in [STYLE.md](../STYLE.md). For each frame,
identify its one message, select the evidence/actions that must be visible,
move remaining authorized explanation to notes, then remove the duplication
from the body. Keep a brief page-by-page record of message, visible content,
and moved explanation under `build/` when reviewing a deck. Recheck time budget
after splitting. Do not equate merely creating a notes file with reducing density.

Give each frame one message. Use short scan-friendly text, figures, equations,
and existing layout environments; put transitions, definitions, derivation
details, caveats, and source reminders in speaker notes when they do not belong
on the slide. Essential evidence and limiting conditions must remain visible.
Write visible text for the audience, not for the authoring process. Remove
phrases such as “作者提供”“本次材料”“作者截图”“本页来自草稿” and
“素材来源”; replace them with audience-facing labels such as “课后学习资源”、
“课程规则来源” or “相关文档”. Keep detailed provenance, source paths and
editing instructions in speaker notes. Preserve necessary visible scientific
citations, attribution, and evidence labels.
Use `\cornercite{key}` for slide citations, and create a references summary before
the closing page when citations are present. For code, use a `fragile` frame.
For paper walkthroughs, use `paperframe`; for a full-height right image, use
`rightimageframe`; use `fitgraphic`/`fitfigure` for fitted graphics.

For code, keep the content type, file/path, and language marker in the code
window's upper bar. Put a shared explanation below the window with
`caption={...}` or its `description={...}` alias. Use `Terminal` for command
transcripts; use a file/config icon and a label such as `Config` for SSH or
other configuration files; use the source-file name for program code. Keep
`language` for highlighting and `label`/`icon` for the visible category.

Keep literature citations at the default top-right position, including `paperframe`.
Use `\campusdoccite{title}{URL}` for web sources and `campusdoccites` for a
shared block of multiple sources. The default prints both source name and the
clickable full URL in the standard corner style; keep BibTeX files read-only
for web-source additions. Use `\campusdoccite*{title}{URL}` only when a long
address cannot fit readably beside both header lines, and show the same named
full URL in the body on that page. Preserve fragments and required query
parameters. A configuration document being taught is an audience reference,
not speaker-only provenance.
Use bottom-corner arguments only when the user requests or approves them;
report the pages and reason. Check long two-line headers and multiple citations
for collisions; shorten titles or verified citation short forms first rather
than silently moving citations. Position examples in the public demo document
the available API and do not override these talk-authoring defaults.

Keep both body-header lines short and specific. Use noun phrases or compact topic
labels such as `SSH 配置示例`, `规则搜索路径`, or `Agent 职责与边界`; do not turn
a frame title into a complete causal sentence or a chain of actions. The body
carries the conclusion and conditions, while notes carry the spoken explanation.
Do not impose an unrequested character limit; check the rendered width at the
normal font size.

When a slide expresses multiple nodes, steps, branches, device boundaries, or
spatial relationships, draw a node-based diagram with TikZ or a separately
generated Mermaid/PDF/SVG source. Use profile-derived colors and theme-matched
fonts and size; preserve editable source and generation metadata. Place each
content diagram, image or screenshot in `figure` with `\caption`, or use an
existing caption-bearing image helper. The nearby caption below the graphic
explains its objects and relationships, using the theme caption style. Node
labels and page titles do not replace this explanation. Decorative graphics,
logos, theme backgrounds, plain prose and a single mathematical arrow do not
need content-figure captions.

For resources the audience must visit, show the resource name and visible URL
on the same page and keep the hyperlink target identical. Web citations use
the corner URL by default; a long-address fallback uses a named full body URL. Use `\url` or `\href` with
the URL as visible text, let long addresses wrap or split across pages, and
retain meaningful query parameters such as video `watch?v=...`. Short labels
remain appropriate only for auxiliary speaker-only provenance, not formal
references or learning resources being discussed on the page. Show local inputs as relative
paths such as `materials/AGENTS.md`, never as machine-specific absolute paths.

Write notes in the TeX source with native `\note{...}`, preferably inside each
frame. Use `\note<1>{...}` and `\note<2>{...}` for overlay-specific explanations;
a note after a frame belongs to that frame. Cover title, section, overview,
reference continuation and closing pages as needed. Leave an intentional blank
when no explanation is needed. Do not author a separate JSON note list for new
talks or edit generated `build/<MAIN>.notes.pdf`.

Keep `shownotes=false` for the default audience PDF. Use `shownotes=true` when
the user requests a PDF with a right-hand presenter note screen. `make` renders
native notes separately for PPTX in either mode; PowerPoint receives plain text
extracted from typeset notes, while rich graphical content remains in the notes
PDF. Use visible URLs for detailed sources that the speaker needs to access.
Inspect each overlay and generated note page after rearranging frames. When
migrating an existing JSON-only talk, move all approved notes to corresponding
native commands before switching sources. An explicit empty `\note{}` also
makes TeX authoritative; the exporter does not blend two note sources.

## Citation facts

When lookup is authorized, use `make literature`, then `make bibtex`; inspect
the candidate rather than assuming the first result. Merge a verified entry
into `bibliography/main.bib` after checking key, DOI, title, authors, year, and
publication version. Use `make citations DOI=...` only for an exact DOI. A
missing or rate-limited count is unavailable, not zero. BibTeX and citation
counts do not establish research findings; read the source paper first.

## Authoring finish line

Run `make draft`, inspect the report and every rendered page, and revise density,
overflow, or collisions. Then run `make` to produce the final PDF/PPTX. Verify
page count, notes coverage, links, section boundaries, and document metadata.
Use `docs/agent-validation.md` for the detailed checks and report placeholders
or unresolved evidence.
