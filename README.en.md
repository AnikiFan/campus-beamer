<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/campus-beamer-logo-white.svg">
    <img src="assets/campus-beamer-logo.svg" alt="Campus Beamer" width="480">
  </picture>
</h1>

**Give an agent your ideas and prepared materials; get a complete PDF and PowerPoint with speaker notes.**

[中文](README.md) · [User guide (Chinese)](docs/usage.md) · [Contributing](CONTRIBUTING.md) · [Releases](docs/releases.md) · [Acknowledgements](#acknowledgements)

![Cover rendered with the default school profile](docs/images/cover.png)

Tsinghua is the default school profile. Colors, emblems and wordmarks
live in `theme/campuscolor.sty`; the theme and its identifiers use the neutral `campus` name.
`example.tex` demonstrates the layouts and features; the agent creates your presentation from your brief.
This is not an official university template.

## Recommended workflow: ideas and local materials

1. Copy this folder and open it with an agent that can read/write local files and run commands.
2. Put prepared materials in `materials/`: for example an arXiv LaTeX source archive, a paper PDF, figures or your own results.
3. Use [`prompt.md`](prompt.md) as a sample and give the agent your ideas, audience and priorities. A rough outline or a paragraph is enough; no LaTeX authoring is required.
4. Ask the agent to follow [`AGENTS.md`](AGENTS.md) and complete the presentation. It asks for clarification when missing information would materially change the content.

For example:

> Read AGENTS.md and make a 20-minute English group-meeting presentation.
> materials/paper/ contains the paper's LaTeX project downloaded and unpacked from arXiv.
> Explain the problem first, illustrate the method's intuition, then discuss whether the experiments support the claims and what the limitations are.
> The audience knows machine learning but has not read the paper. Put derivation details in speaker notes.
> Complete the narrative, figures, citations, layout review and PDF/PPTX export. Ask me about missing key facts.

`prompt.md` is a sample, not a required form. You can send your own brief and file paths directly.
The agent unpacks source archives and reads the paper's text, captions, figures and bibliography; you do not need to turn the paper into slide content first.
External research or new assets require confirmation; supplied local materials can be used directly.

The agent creates `main.tex`, content under `chapters/talk/` and, when needed,
`bibliography/main.bib`. It runs `make draft`, inspects the actual pages, revises
crowded slides, writes `build/main.notes.json` in final page order, then runs `make`.
The deliverables are `build/main.pdf` and `build/main.pptx`. For revisions, give
the agent your feedback; it updates both slides and notes and rebuilds them.

PPTX exports automatically include native sections and document properties: title,
author, subtitle, group, advisor and presentation date. No extra configuration is needed.

**PPTX slides are rendered images, not editable native PowerPoint text.**
Give edits to the agent or edit the generated `.tex` source.
Make compiles and converts existing content; the agent performs the writing.

## Environment and reference example

The build environment needs GNU Make, uv, XeLaTeX, latexmk, biber and the template's TeX packages/fonts.
Use TeX Live / MacTeX or the [Docker environment](docs/docker.md).
See [installation instructions](docs/installation.md). Set up the environment once;
the agent can check the existing tools. `uv run --frozen` creates `.venv` from
`uv.lock`; the initial dependency download needs network access.

```bash
make doctor              # Check tools, TeX packages and fonts
make draft MAIN=example  # Inspect reference-example pages and layout report
make MAIN=example        # build/example.pdf and build/example.pptx
make                     # Build main.tex if present; otherwise example.tex
```

[`example.tex`](example.tex) is a reference for people and agents. Its content
under `chapters/` demonstrates section pages, figures, equations, citations,
code windows, navigation and video. The agent chooses useful layouts and creates
your content separately. The example also lists all public class options and
defaults; see [class options](docs/class-options.md).

- Fixed 16:9 layout with Chinese and English support; full primary-color section pages by default (purple in the Tsinghua profile).
- Fitted figures, equations, paper walkthroughs and [terminal-style code windows](docs/usage.md#代码与终端窗口).
- `biblatex` / `biber`, corner citations and cited references; optional [DBLP and citation-count tools](docs/literature.md).
- PDF-to-PPTX export preserving navigation, external links, embedded local video and per-page notes. Video export needs FFmpeg.
- `make draft` page previews and diagnostics for density, alignment and overflow review.

<details>
<summary>See corner citations and navigation</summary>

![Corner citations and section navigation from the full demo](docs/images/citations.png)

</details>

The repository and source ZIP include `materials/.gitkeep`, so the folder is ready after cloning or unpacking. Files you add under `materials/`, generated `main.tex`, `chapters/talk/`, `bibliography/main.bib`, and output in `build/` stay local: Git ignores them and source ZIPs omit them. `prompt.md` is a generic sample; send your own brief to the agent.
See [environment workflows](docs/workflows.md) for VS Code, Overleaf and the command line.

## Another university

Edit **`theme/campuscolor.sty`** to change functional colors (`maincolor`, `tipcolor`,
`notecolor`, `alertcolor`, `examplecolor`, `definitioncolor`), transparent
emblems/wordmarks. Pass campus photo and illustration
paths directly in your chapter files. Section backgrounds can also be `primary`,
`white`, or empty. Demo metadata lives in `chapters/metadata.tex`; the agent writes
your metadata in `chapters/talk/metadata.tex`.
Layout geometry stays in the theme implementation.
The footer always uses `maincolor` with white text; no separate footer-color setting is needed.
The cover always uses the primary-color diagonal layout. No setup is required;
the only explicit setting is `\titlebackground{primary}`, and its color follows `maincolor`.

## Development

```bash
make test          # Python regression tests
make check-theme   # Compile theme fixtures in isolation
make dist          # Standalone source ZIP, without generated output
make version       # Project version from pyproject.toml
make release       # Test, build the public demo and bundle checksummed release artifacts
make clean         # Manually remove intermediates after a failed build
make help
```

Document-class, theme and school-profile files live in `theme/`. Keep this directory
and `.latexmkrc` when copying the template: latexmk configures the TeX search path,
so `\documentclass{campusbeamer}` and the Make commands remain unchanged.
Presentation sections, metadata and reusable demo fragments live together in
`chapters/`, documentation in `docs/`, and test sources in `tools/fixtures/`.
Local output lives in ignored `build/` directories.
GitHub Actions reads `.github/workflows/` from the repository root.
See [CONTRIBUTING.md](CONTRIBUTING.md) for bug reports and pull requests.

Track public changes in [CHANGELOG.md](CHANGELOG.md). Source ZIPs include only
the individually reviewed files in `tools/package_source.py`; new files are
excluded by default. `make release` creates
`build/releases/campus-beamer-v<version>-release.zip` containing the source ZIP,
public example PDF/PPTX, bilingual release notes and SHA-256 checksums. It always
builds `example.tex`. The **Release Please** GitHub workflow maintains release
PRs, creates releases and uploads bundles after merging, with a manual build
entry point as well. See the [release guide](docs/releases.md) for setup and publishing.

## License and assets

Source code uses **GPL-3.0-or-later**; see [LICENSE](LICENSE). The bundled Tsinghua emblem, wordmark, combined marks
and campus images come from the [Tsinghua visual identity system](https://vi.tsinghua.edu.cn/)
and the
[Tsinghua SIGS official photo gallery](https://www.sigs.tsinghua.edu.cn/en/7453/list.htm);
some images have been cropped. The emblem, university name and related marks
involve Tsinghua University's registered trademarks and other rights. Do not use
these marks outside this template's presentation purposes. These images are not
covered by the code's GPL license; this notice grants no university authorization
and implies no university endorsement.
The original procedural demo video, `assets/presentation_demo.mp4`, is separately
dedicated under CC0-1.0; its geometric source and dedication are documented in
[assets/README.md](assets/README.md#原创演示视频).
We are currently unable to reach the relevant rights holders or photographers;
explicit asset permissions and individual photographer credits have not been obtained or verified.
If you believe an asset infringes your rights, or find missing credits or incorrect
attribution, please contact [xiaofan140@gmail.com](mailto:xiaofan140@gmail.com)
or open a repository Issue. We will promptly review the report and add credits,
correct attribution, replace or remove the affected assets and derived previews as appropriate.
This contact notice does not replace permission from the rights holder.
The previews contain these assets and are subject to the same notice.
See [assets/README.md](assets/README.md) for the full notice and file list.

## Acknowledgements

Thanks to the authors and contributors of these projects:

- **Engineering practices**: [TongjiThesis](https://github.com/TJ-CSCCG/TongjiThesis).
  Its document-class options, bibliography interface, chapter organization, Make workflow,
  environment checks and guidance for the command line, VS Code, Overleaf and GitHub Actions
  informed this project's independent implementation for Beamer presentations.
- **Visual style**: [THU-beamer-template](https://github.com/FangWHao/THU-beamer-template)
  and [TongjiBeamer](https://github.com/Kian-Chen/TongjiBeamer). This template's style builds
  on both projects, with further adjustments for its layout and presentation features.
- **Early template origins**: [college-beamer](https://github.com/liu-qilong/college-beamer)
  and Federico Zenith's [SINTEF Presentation](https://www.overleaf.com/latex/templates/sintef-presentation/jhbhdffczpnx).
  This template's early foundations trace back to these projects; college-beamer also explicitly
  credits SINTEF Presentation as its basis.
