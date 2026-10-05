# Accessibility / 无障碍说明

Campus Beamer produces presentation PDFs and image-based PowerPoint files. The
template keeps the visual layout stable, but the exported PPTX deliberately
uses one rendered image per slide, so its visible text is not available as
native PowerPoint text to screen readers or text editing tools. The PDF may also
have limited semantic structure depending on the TeX engine and viewer.

## Author checklist

- Put the main claim, essential numbers and necessary caveats on the slide;
  keep additional spoken explanation in speaker notes.
- Do not communicate meaning by color alone. Check text and callout contrast
  after changing the school profile or adding campus images.
- Use readable text and uncluttered frames. Run `make draft` and inspect every
  page at the intended presentation size, including section pages and overlays.
- Give every meaningful figure, equation and video a short spoken description in
  `build/main.notes.json`. Explain trends and conclusions, not just the file
  name or a visual label.
- For video, provide captions or a transcript when available, describe the
  important visual information in the notes, and keep the poster frame useful.
  The local-video build step adds a first-frame preview and preserves the link
  that opens the video.
- Keep navigation usable: retain section headings, meaningful frame titles and
  the generated PDF bookmarks/PPTX sections.

## Known limits

The PDF-to-PPTX converter preserves the rendered appearance, links, native
sections and speaker notes. It does not turn rendered glyphs into editable or
screen-reader-readable slide text. If an accessible handout is required, export
the source content separately as structured HTML, Markdown or a tagged document,
and provide a text transcript or outline alongside the PDF/PPTX.

Accessibility feedback and reproducible template issues can be reported through
the [contribution guide](CONTRIBUTING.md) or a public issue. Do not include
private presentation material in an issue; use the [security policy](SECURITY.md)
for confidential reports.
