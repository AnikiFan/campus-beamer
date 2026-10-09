---
name: campus-beamer-authoring
description: Create or revise a Campus Beamer talk from an outline and supplied materials, including requests such as 根据大纲制作 PPT.
---

# Campus Beamer authoring

Use this workflow for a user's talk, including content-bearing revisions.
Theme implementation and repository maintenance follow the root AGENTS.md routes.
Resolve the links below relative to this file; run commands from the repository
root containing Makefile.

## Start from the user's inputs

Read the [authoring guide](../../../docs/agent-authoring.md),
[STYLE.md](../../../STYLE.md), and the root [outline.md](../../../outline.md)
or explicitly supplied brief. STYLE.md contains editable preferences; the
current brief's explicit requirements take precedence. Inspect the authorized
materials and relevant template examples as needed.

## Choose the content stage

- **New talk or content revision:** inventory the supplied materials, including
  ignored files and referenced assets. Read documents and view relevant images.
  Develop substantive section/subsection content, evidence, notes allocation,
  time budget, material coverage and open questions in
  `build/outline-normalized.md`. Preserve the user's original draft. Present
  this detailed outline for confirmation before writing slide source or notes.
- **Confirmed outline:** use confirmation for that specific revision; do not
  request it again. Create or revise the local talk source and notes from the
  approved content. Focus on page boundaries, concise wording, layouts and the
  split between visible content and speaker notes.
- **Layout-only revision:** proceed within approved content. Splitting a crowded
  frame is a layout decision; new claims or substantive explanations return to
  outline review before entering either slides or notes.

Develop explanations within the supplied purpose and materials. Keep unsupported
claims open; obtain authorization for external research or changes to supplied
facts. Keep the public demo separate from the user's talk.

## Finish the approved talk

Apply the authoring guide and current STYLE.md to body headers, figures, citations,
code, semantic boxes and notes. Follow the relevant checks in the
[validation guide](../../../docs/agent-validation.md): build the final draft,
inspect every rendered page, then export PDF/PPTX and verify notes, links,
sections and metadata. Fix failures caused by the work and report unresolved
placeholders, warnings or external blockers. Keep private inputs and generated
outputs out of public commits and source packages.
