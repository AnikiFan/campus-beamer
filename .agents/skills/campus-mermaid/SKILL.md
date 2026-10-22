---
name: campus-mermaid
description: Draw Mermaid diagrams from supplied content, choose the Mermaid diagram type, apply the active Campus profile's fonts and colors, and render SVG/PDF/PNG while preserving editable sources.
---

# Campus Mermaid

Turn supplied diagram content into Mermaid source and rendered assets.
Run commands from the repository root.

## Select the Mermaid type

Identify the relationship to represent: branching, interaction, hierarchy,
dependency, state transitions, schedule, proportion or quantified flow. Read the
relevant rows in [diagram-selection.md](references/diagram-selection.md) and
choose the Mermaid type whose syntax and semantics match that relationship.
Translate the supplied labels, connections and values into its native structure.

## Configure the drawing style

Read [rendering.md](references/rendering.md) for generation commands. The bundled
renderer reads `maincolor` from `theme/<profile>/profile.tex`, uses Carlito and
FandolHei by default, preloads fonts before measuring labels, and exports
SVG/PDF/PNG plus generation metadata. Reuse its shared configuration rather than
rebuilding a theme for each figure. Use the supplied font and size overrides
when they differ from the defaults.

- Keep typography and palette consistent across drawings. Use white backgrounds,
  primary-color lines, pale derived fills and consistent borders.
- Distinguish series through labels, line styles and related tones. Use profile
  functional colors when needed for the supplied semantics.
- Configure diagram direction, grouping, node spacing, line breaks and edge
  routing within the Mermaid source. Keep labels readable and connections clear.

## Render and check the drawing

Save `.mmd` sources and figure exports under `materials/diagrams/`; put temporary
previews, configs and diagnostics in `build/`. Preserve the generation command,
profile, engine version and deliberate overrides.

Use an existing local runtime and browser. The renderer installs no packages
and makes no network requests. Report missing dependencies or unsupported
syntax as generation issues.

Inspect the rendered files and report: actual fonts, text size, contrast,
wrapping, clipping, node spacing, arrow direction and attachment points. Parsing
success or a CSS declaration does not prove that a setting took effect. Check
for labels clipped inside nodes and overlapping edges as well as SVG bounds.
