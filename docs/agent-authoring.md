# Agent guide: authoring a talk

Read this guide for a new or revised `main.tex` talk. It is intentionally
separate from the root `AGENTS.md` so maintenance tasks do not load deck-writing
details.

## Before writing

Read the user's chat brief (or `prompt.md`) and inspect only the supplied paths
under `materials/`. An archive may be unpacked into a working copy while the
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

## Content and notes

Give each frame one message. Use short scan-friendly text, figures, equations,
and existing layout environments; put transitions, definitions, derivation
details, caveats, and source reminders in speaker notes when they do not belong
on the slide. Essential evidence and limiting conditions must remain visible.
Use `\cornercite` for slide citations, and create a references summary before
the closing page when citations are present. For code, use a `fragile` frame.
For paper walkthroughs, use `paperframe`; for a full-height right image, use
`rightimageframe`; use `fitgraphic`/`fitfigure` for fitted graphics.

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
