#!/usr/bin/env python3
# Campus Beamer: pack a standalone source archive.
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Create a standalone source ZIP, using an explicit public-project manifest."""
from pathlib import Path
import argparse
import zipfile

FILES = (
    'examples/example-eva.tex', 'examples/example-eva-43.tex',
    'theme/eva/profile.tex', 'theme/eva/section-art.tex', 'theme/eva/sample.tex',
    'theme/eva/emblem.tex', 'theme/eva/wordmark.tex', 'theme/eva/backdrop.tex', 'theme/eva/README.md',
    'tools/fixtures/profile-eva.tex', 'tools/fixtures/profile-eva-english.tex',
    'docs/images/preview-eva-cover.png', 'docs/images/preview-eva-section.png',
    'docs/images/preview-eva-body.png', 'docs/images/preview-eva-closing.png',
    'tools/package_overleaf.py', 'tools/tests/test_package_overleaf.py',
    'tools/templates/overleaf-latexmkrc', 'tools/templates/overleaf-README.md',
    'examples/example-43.tex',
    'examples/example-en-43.tex',
    'examples/example-tsinghua-43.tex',
    'examples/example-pcl-43.tex',
    'examples/example-tokyo-night-43.tex',
    'examples/example-undefined-43.tex',
    'tools/fixtures/aspect-ratio-43.tex',
    'tools/fixtures/aspect-ratio-169.tex',
    'tools/fixtures/aspect-ratio-notes.tex',
    'theme/undefined/profile.tex',
    'theme/undefined/sample.tex',
    'theme/undefined/README.md',
    'theme/undefined/emblem.tex',
    'theme/undefined/wordmark.tex',
    'theme/undefined/GENERATION.md',
    'examples/example-undefined.tex',
    'tools/fixtures/profile-undefined.tex',
    'docs/images/preview-undefined-cover.png',
    'docs/images/preview-undefined-section.png',
    'docs/images/preview-undefined-body.png',
    'docs/images/preview-undefined-closing.png',
    'theme/tokyo-night/profile.tex',
    'theme/tokyo-night/sample.tex',
    'theme/tokyo-night/README.md',
    'theme/tokyo-night/Tokyo-Night.LICENSE.txt',
    'theme/tokyo-night/emblem.tex',
    'theme/tokyo-night/wordmark.tex',
    'theme/tokyo-night/backdrop.tex',
    'docs/images/preview-tokyo-night-cover.png',
    'docs/images/preview-tokyo-night-section.png',
    'docs/images/preview-tokyo-night-body.png',
    'docs/images/preview-tokyo-night-closing.png',
    'tools/fixtures/profile-tokyo-night.tex',
    'README.md', 'README.en.md', 'LICENSE', 'SECURITY.md', 'ACCESSIBILITY.md', 'CHANGELOG.md',
    'release-please-config.json', '.release-please-manifest.json',
    'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'AGENTS.md', '.editorconfig', '.gitattributes', '.gitignore', '.latexmkrc', 'Makefile',
    '.agents/skills/campus-beamer-authoring/SKILL.md',
    '.agents/skills/campus-beamer-validation/SKILL.md',
    '.agents/skills/campus-mermaid/SKILL.md',
    '.agents/skills/campus-mermaid/agents/openai.yaml',
    '.agents/skills/campus-mermaid/references/diagram-selection.md',
    '.agents/skills/campus-mermaid/references/rendering.md',
    '.agents/skills/campus-mermaid/assets/config.json',
    '.agents/skills/campus-mermaid/scripts/render.mjs',
    'docker/Dockerfile', 'docker/Dockerfile.dockerignore', 'docker/entrypoint.sh',
    'examples/example.tex', 'examples/example-en.tex', 'examples/example-tokyo-night.tex', 'examples/example-tsinghua.tex', 'examples/example-pcl.tex', 'outline.md', 'STYLE.md', 'materials/.gitkeep',
    'examples/english/metadata.tex', 'examples/english/refs.bib',
    'examples/english/01_basics.tex', 'examples/english/02_papers.tex',
    'examples/english/03_callouts.tex', 'examples/english/04_navigation.tex',
    'examples/english/05_media.tex', 'examples/english/layout-guide.tex',
    'examples/english/font-guide.tex',
    'examples/theme-images.tex', 'tools/templates/outline.md', 'sections/.gitkeep', 'bibliography/.gitkeep',
    'theme/campusbeamer.cls', 'theme/beamerthemecampus.sty',
    'theme/campuscolor.sty', 'theme/README.md',
    'theme/tsinghua/profile.tex', 'theme/tsinghua/README.md', 'theme/tsinghua/sample.tex',
    'theme/pcl/profile.tex',
    'theme/general/profile.tex', 'theme/general/README.md',
    'theme/general/emblem.tex', 'theme/general/wordmark.tex', 'theme/general/backdrop.tex',
    'theme/general/assets/emblem_on_dark.pdf', 'theme/general/assets/emblem_on_light.pdf',
    'theme/general/assets/wordmark_on_dark.pdf', 'theme/general/assets/wordmark_on_light.pdf',
    'theme/general/assets/backdrop.pdf',
    'tools/generate_general_assets.py',
    'tools/fixtures/profile-general.tex', 'tools/fixtures/profile-general-legacy.tex',
    'theme/pcl/README.md', 'theme/pcl/sample.tex',
    'theme/pcl/wordmark.tex',
    'tools/fixtures/profile-pcl.tex',
    'theme/pcl/emblem.tex',
    'theme/campuscode.sty',
    'examples/bibliography/refs.bib', 'pyproject.toml', 'uv.lock',
    '.github/ISSUE_TEMPLATE/bug_report.yml', '.github/PULL_REQUEST_TEMPLATE.md',
    '.github/workflows/ci.yml', '.github/workflows/release.yml',
    '.vscode/extensions.json', '.vscode/settings.json', '.vscode/tasks.json',
    'assets/Latin-Modern.LICENSE.txt', 'assets/README.md',
    'assets/campus-beamer-logo-white.svg', 'assets/campus-beamer-logo.svg',
    'assets/campus-beamer-logo.tex', 'assets/presentation_demo.LICENSE.txt',
    'assets/presentation_demo.mp4',
    'examples/sections/01_basics.tex', 'examples/sections/02_papers.tex', 'examples/sections/03_callouts.tex',
    'examples/sections/04_navigation.tex', 'examples/sections/05_media.tex',
    'examples/sections/bibliography-guide.tex', 'examples/sections/code-guide.tex',
    'examples/sections/code/normalize.py', 'examples/sections/font-guide.tex',
    'examples/sections/harness-guide.tex', 'examples/sections/callout-layout.tex', 'examples/sections/layout-guide.tex',
    'examples/sections/overlay-layout.tex',
    'examples/sections/native-notes-layout.tex',
    'examples/sections/notes-guide.tex',
    'examples/sections/page-styles.tex',
    'examples/sections/math-examples.tex', 'examples/sections/metadata.tex',
    'docs/class-options.md', 'docs/docker.md',
    'docs/images/preview-general-cover.png',
    'docs/images/preview-general-section.png',
    'docs/images/preview-general-body.png',
    'docs/images/preview-general-closing.png',
    'docs/images/preview-general-flow.png',
    'docs/images/preview-general-layout.png',
    'docs/images/preview-general-code.png',
    'docs/images/preview-general-fullheight.png',
    'docs/images/preview-general-citations.png',
    'docs/images/preview-general-callouts.png',
    'docs/images/preview-general-en-cover.png',
    'docs/images/preview-general-en-section.png',
    'docs/images/preview-general-en-body.png',
    'docs/images/preview-general-en-closing.png',
    'docs/images/preview-general-en-flow.png',
    'docs/images/preview-general-en-layout.png',
    'docs/images/preview-general-en-code.png',
    'docs/images/preview-general-en-fullheight.png',
    'docs/images/preview-general-en-citations.png',
    'docs/images/preview-general-en-callouts.png',
    'docs/images/preview-tsinghua-cover.png',
    'docs/images/preview-tsinghua-section.png',
    'docs/images/preview-tsinghua-body.png',
    'docs/images/preview-tsinghua-closing.png',
    'docs/images/preview-pcl-cover.png',
    'docs/images/preview-pcl-section.png',
    'docs/images/preview-pcl-body.png',
    'docs/images/preview-pcl-closing.png',
    'docs/installation.md', 'docs/literature.md',
    'docs/agent-authoring.md', 'docs/agent-theme.md', 'docs/agent-validation.md',
    'docs/notes.example.json', 'docs/releases.md', 'docs/usage.md',
    'docs/workflows.md',
    'tools/add_video_posters.py', 'tools/check_theme.py', 'tools/compare_pdf.py', 'tools/doctor.py',
    'tools/draft_preview.py', 'tools/generate_demo_video.py',
    'tools/generate_logo.py', 'tools/render_wordmarks.py', 'tools/recolor_pcl_wordmark.py',
    'tools/images_to_ppt.py', 'tools/export_presentation.py', 'tools/literature.py',
    'tools/theme_assets.py', 'tools/tests/test_theme_assets.py',
    '.github/workflows/theme-assets.yml',
    'tools/package_release.py', 'tools/package_source.py', 'tools/render_theme_previews.py',
    'tools/fixtures/profile-selection.tex', 'tools/fixtures/profile-selection-legacy.tex',
    'tools/fixtures/brand-variants.tex', 'tools/fixtures/class-handout.tex',
    'tools/fixtures/class-metadata.tex', 'tools/fixtures/class-mixed-language.tex',
    'tools/fixtures/class-options.bib', 'tools/fixtures/class-options.tex',
    'tools/fixtures/code-windows.tex', 'tools/fixtures/demo-without-guides.tex',
    'tools/fixtures/language-layout.tex', 'tools/fixtures/name-layout.tex', 'tools/fixtures/layout-guides-off.tex',
    'tools/fixtures/layout-guides.tex', 'tools/fixtures/single-header.tex',
    'tools/fixtures/toc-overview.tex', 'tools/fixtures/page-styles.tex',
    'tools/fixtures/section-toc-spacing.tex', 'tools/fixtures/date-display.tex',
    'tools/fixtures/citation-top-right.tex', 'tools/fixtures/citation-top-right.bib',
    'tools/fixtures/flow-layout.tex', 'tools/fixtures/url-layout.tex',
    'tools/fixtures/doc-citations.tex', 'tools/fixtures/description-alignment.tex',
    'tools/fixtures/callout-layout.tex',
    'tools/fixtures/titleless-box.tex', 'tools/fixtures/titleless-box-dark.tex',
    'tools/fixtures/overlays.tex', 'tools/fixtures/overlays-handout.tex',
    'tools/fixtures/native-notes.tex', 'tools/fixtures/native-notes-screen.tex',
    'tools/tests/test_compare_pdf.py', 'tools/tests/test_doctor.py',
    'tools/tests/test_draft_preview.py', 'tools/tests/test_images_to_ppt.py',
    'tools/tests/test_literature.py', 'tools/tests/test_make_entry.py',
    'tools/tests/test_mermaid.py',
    'tools/tests/test_package_release.py', 'tools/tests/test_package_source.py',
    'tools/tests/test_theme_inspection.py', 'tools/tests/test_theme_previews.py',
    'tools/tests/test_transitions.py',
    'tools/tests/test_native_notes.py',
)


def source_files(root):
    """Only distribute reviewed files; new files are private by default."""
    paths = [root / name for name in FILES]
    for path in paths:
        # A regular file inside a symlinked directory can also read outside root.
        if any(part.is_symlink() for part in (path, *path.parents) if part != root
               and part.is_relative_to(root)):
            raise ValueError(f'Source distribution must not contain symlinks: {path}')
        if not path.is_file():
            raise FileNotFoundError(f'Missing source-distribution file: {path}')
    return sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())


def package(root, output):
    root = root.resolve()
    paths = source_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.zip.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                # The archive is unpacked directly into the project root.
                name = path.relative_to(root).as_posix()
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                # Distribute the starter template instead of the user's draft.
                source = root / 'tools/templates/outline.md' if name == 'outline.md' else path
                archive.writestr(info, source.read_bytes())
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return len(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('build/dist/campus-beamer.zip'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    count = package(root, args.output)
    print(f'Source ZIP: {args.output} ({count} files; '
          'asset sources and rights-holder contact notice: assets/README.md)')


if __name__ == '__main__':
    main()
