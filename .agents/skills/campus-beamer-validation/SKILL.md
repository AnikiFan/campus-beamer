---
name: campus-beamer-validation
description: Build, inspect, or diagnose Campus Beamer PDF/PPTX output, including rendering, speaker notes, links and export failures.
---

# Campus Beamer validation

Read the [validation guide](../../../docs/agent-validation.md) for the checks
relevant to the requested output. Use [STYLE.md](../../../STYLE.md) for visual
review. Resolve these links relative to this file; run commands from the root
containing Makefile.

## Select the entry and scope

Use the entry requested by the user. Otherwise Make selects main.tex when present
and example.tex when absent; an explicit MAIN wins. Distinguish a build request,
an output review, a diagnosis, and full delivery. Check the actual source and
output timestamps; a stale artifact does not establish a successful build.

- **Build or export:** use the narrowest appropriate Make target. Use doctor when
  prerequisites are uncertain; do not reinstall a working environment.
- **Visual review:** inspect the draft report, contact sheets and readable pages.
  Check density, both body-header lines, captions, semantic headings, description
  alignment, visible source URLs, clipping and footer clearance. Compilation and
  link annotations alone do not establish readable output.
- **Full delivery:** validate the final PDF/PPTX page counts, aligned notes,
  actual internal/external targets, sections and supplied metadata. Inspect the
  final layout before reporting the deck ready.
- **Diagnosis:** reproduce the relevant failure, inspect its logs and artifacts,
  and verify the affected behavior after fixing it. Run code tests or theme
  fixtures when the change affects those components, rather than for every talk.

Use the guide's commands and output contract without duplicating converter or
inspection code. Keep source/materials intact and editable notes separate from
compiler intermediates. Respect an existing content approval; new substantive
content returns to outline review. Theme changes follow the
[theme guide](../../../docs/agent-theme.md).

Report what was checked, the resulting artifacts or diagnosis, and any unresolved
warning, placeholder or external dependency. Distinguish package-level evidence
from actual PowerPoint client playback. Fix failures caused by the requested work;
do not claim unrun checks passed.
