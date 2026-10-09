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

For a new talk or a content-bearing revision, first normalize the supplied
outline before writing presentation source. Save a reviewable
`build/outline-normalized.md` containing the goal, audience, duration budget,
section order, per-page core message, visible evidence, notes content, sources
and metadata, planned deletions/merges/splits/reordering/rewrites, and items
requiring external lookup or new assets. Include any change that could affect
facts, claims, examples, page count, or duration as a pending question with its
source and expected impact.

Wait for the user's confirmation before creating or expanding `main.tex`,
`chapters/talk/`, `bibliography/main.bib`, or speaker notes. Do not put guesses
into the deck while confirmation is pending; continue source inspection and
keep optional additions outside the deck. After confirmation, implement only
the confirmed outline, then compile and validate the final PDF/PPTX. For later
content changes, update and re-confirm the normalized outline before syncing
the presentation. Purely mechanical checks or an explicitly requested typo and
layout fix may proceed without inventing content.

Within a confirmed outline, rewriting, condensing, date formatting, and moving
authorized explanations into notes are routine authoring. Preserve the root
`outline.md` as user input and write the normalized review copy under `build/`.
Keep the original draft intact. Public-template commits must exclude filled
private outlines. Source packaging uses `tools/templates/outline.md` for the
distributed starter outline. Record which outline revision the user actually
confirmed. Before adding facts, opinions, recommendations, examples, tutorial
steps, demos, or conclusions not
provided or authorized for expansion, bundle the proposed additions, sources,
and impact on slide count/duration for approval. This applies to notes as well
as visible slides. While the outline awaits confirmation, continue inspection
and planning only; keep optional additions outside the deck. Silence is not
approval. An explicit expansion request authorizes planning within that scope
without asking again about scope, but the resulting outline still needs review.
Reading supplied material
or verifying a fact does not authorize an unrelated expansion of the talk.

## Source layout

Start a new deck with the class interface, for example:

```tex
\documentclass[
  language=chinese, cjk=auto, bibstyle=ieee, bibsorting=none,
  mathfont=serif, navigation=true, cornerwidth=4.8cm,
  layoutguides=false
]{campusbeamer}
```

Keep metadata in `chapters/talk/metadata.tex`, class/build settings in
`main.tex`, and one section per file under `chapters/talk/`. Select those files
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

Keep citations at the default top-right position, including `paperframe`.
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
fonts and size; preserve editable source and generation metadata. Plain prose
and a single mathematical arrow do not need a diagram.

For resources the audience must visit, show the resource name and visible URL
in the body and keep the hyperlink target identical. Use `\url` or `\href` with
the URL as visible text, let long addresses wrap or split across pages, and
retain meaningful query parameters such as video `watch?v=...`. Short labels
remain appropriate for speaker-only provenance. Show local inputs as relative
paths such as `materials/AGENTS.md`, never as machine-specific absolute paths.

Create `build/<MAIN>.notes.json` with exactly one entry per final PDF page,
including title, section, overview, reference continuation, and closing pages.
Use `""` for an intentional blank. Recheck order after adding, deleting, or
rearranging frames; equal page counts do not prove alignment.

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
