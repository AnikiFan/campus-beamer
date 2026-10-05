# Campus Beamer: build the PDF, draft previews and PowerPoint export.
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

# Run from the copied template directory. latexmk tracks TeX/BibTeX/assets;
# PPTX is regenerated on each invocation so notes and DPI changes are honored.
.DEFAULT_GOAL := all

# Agent-authored main.tex takes precedence; a fresh copy builds the reference demo.
MAIN ?= $(if $(wildcard main.tex),main,example)
# Shared with .latexmkrc and the editor: all generated files stay under build/.
BUILD_DIR := build
DPI ?= 600
DRAFT_DPI ?= 96
PAGES ?= all
UV ?= uv
LATEXMK ?= latexmk
PYTHON ?= python3

DBLP_HOST ?= dblp.org
CITATION_SOURCE ?= openalex
BIB_OUTPUT ?= build/literature/paper.bib
BIB_REPORT ?= build/literature/paper.json
# Treat input as literal text, including dollar signs and Make expressions.
override QUERY := $(value QUERY)
override DBLP_KEY := $(value DBLP_KEY)
override DOI := $(value DOI)
override CITE_KEY := $(value CITE_KEY)
override DBLP_HOST := $(value DBLP_HOST)
override CITATION_SOURCE := $(value CITATION_SOURCE)
override BIB_OUTPUT := $(value BIB_OUTPUT)
override BIB_REPORT := $(value BIB_REPORT)
override INPUT_BIB := $(value INPUT_BIB)
# Pass text through the environment, so titles/keys are not shell fragments.
export QUERY DBLP_KEY DOI CITE_KEY DBLP_HOST CITATION_SOURCE BIB_OUTPUT BIB_REPORT INPUT_BIB

.PHONY: all pptx pdf pdf-build draft doctor test literature bibtex citations check-theme logo dist version release clean help

all: pptx

pptx: pdf-build
	$(UV) run --frozen python tools/images_to_ppt.py "$(BUILD_DIR)/$(MAIN).pdf" "$(BUILD_DIR)/$(MAIN).pptx" --dpi "$(DPI)" --strict-links --strict-notes
	$(LATEXMK) -c "$(MAIN).tex"

pdf: pdf-build
	$(LATEXMK) -c "$(MAIN).tex"

pdf-build:
	$(LATEXMK) -xelatex -interaction=nonstopmode -halt-on-error -file-line-error "$(MAIN).tex"
	$(UV) run --frozen python tools/add_video_posters.py "$(BUILD_DIR)/$(MAIN).pdf"

# Use the final layout, but skip high-DPI PPTX conversion and notes validation.
draft: pdf-build
	$(UV) run --frozen python tools/draft_preview.py "$(BUILD_DIR)/$(MAIN).pdf" --log "$(BUILD_DIR)/$(MAIN).log" --output "$(BUILD_DIR)/draft/$(MAIN)" --dpi "$(DRAFT_DPI)" --pages "$(PAGES)"
	$(LATEXMK) -c "$(MAIN).tex"

doctor:
	$(PYTHON) tools/doctor.py

test:
	$(UV) run --frozen python -m unittest discover -s tools/tests -v

# Read-only network queries. Bibliography output is staged under build/;
# reviewing/merging into bibliography/refs.bib remains an explicit authoring step.
literature:
	@$(PYTHON) tools/literature.py --make-target search

bibtex:
	@$(PYTHON) tools/literature.py --make-target fetch

citations:
	@$(PYTHON) tools/literature.py --make-target citations

check-theme:
	$(UV) run --frozen python tools/check_theme.py

logo:
	$(UV) run --frozen python tools/generate_logo.py

dist:
	$(UV) run --frozen python tools/package_source.py

version:
	@$(UV) version --short

# Keep these steps sequential: successful builds clean shared intermediates.
# Always release the public demo, even when a private main.tex exists locally.
release:
	$(UV) lock --check --offline
	$(MAKE) test
	$(MAKE) draft MAIN=example
	$(MAKE) MAIN=example DPI="$(DPI)"
	$(MAKE) dist
	$(UV) run --frozen python tools/package_release.py --version "$$($(UV) version --short)"

# Retain PDF, PPTX, notes, sources and assets. Successful public build targets
# clean LaTeX intermediates; this explicit target is also available after a
# failed build, once its logs have been inspected.
clean:
	$(LATEXMK) -c "$(MAIN).tex"

help:
	@printf '%s\n' \
	  'make                 Build main.tex when present, otherwise example.tex (PDF + PPTX, 600 DPI)' \
	  'make MAIN=example    Build the bundled reference demo explicitly' \
	  'make DPI=200         Build a smaller preview' \
	  'make draft           Compile PDF and render 96-DPI page previews + layout report' \
	  'make draft PAGES=2,5-8  Preview selected PDF pages (1-based); no PPTX export' \
	  'make MAIN=talk       Build talk.tex -> build/talk.pdf -> build/talk.pptx; read build/talk.notes.json' \
	  'make pdf             Build PDF, then remove LaTeX intermediates on success' \
	  'make doctor          Check default tools, TeX packages and fonts without building' \
	  'make test            Run Python regression tests via uv (offline)' \
	  'make literature QUERY="paper title"  Search DBLP; return JSON candidates' \
	  'make bibtex DBLP_KEY=conf/... CITE_KEY=MyPaper  Stage BibTeX + citation snapshot in build/literature/' \
	  'make citations DOI=10.../...  Query DOI-matched citation count + source/date' \
	  '  CITATION_SOURCE=openalex (default), semantic-scholar, or none (BibTeX only)' \
	  'make check-theme     Compile theme fixtures without changing main output' \
	  'make logo            Rebuild project logo SVGs and PDF/PNG previews' \
	  'make dist            Create a standalone source ZIP in build/dist/' \
	  'make version         Show the project version from pyproject.toml' \
	  'make release         Test, build the demo and package versioned release artifacts (600 DPI)' \
	  'make clean           Remove LaTeX intermediates; retain PDF/PPTX and sources' \
	  'PDF/PPTX, generated notes and TeX intermediates go in build/; previews go in build/draft/' \
	  'Style files live in theme/; .latexmkrc configures the TeX search path' \
	  'Bibliography databases live in bibliography/; Docker files live in docker/' \
	  'Prerequisites: GNU Make, uv, XeLaTeX, latexmk, biber and the template TeX packages' \
	  'Local video export also needs FFmpeg (included in the Docker image)'
