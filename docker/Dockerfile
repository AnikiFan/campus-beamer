# Campus Beamer: container image with TeX, uv and the PDF-to-PPTX tools.
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

# Build an environment image; mount the presentation source at /workspace.
# Keep the uv version explicit rather than pulling a changing latest tag.
FROM ghcr.io/astral-sh/uv:0.12.3 AS uv
# Full TeX Live 2025, including XeLaTeX, latexmk, biber and the CJK packages.
# Pin the multi-platform index so amd64 and arm64 use the same release.
FROM ghcr.io/xu-cheng/texlive-historic-debian:2025@sha256:d3e42adc0c8d84bc913bfc33571feaf7037616260a771bb6f027504661568bf6

# Keep TeX and biber from the upstream image; apt only supplies system tools/fonts.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        ffmpeg \
        fontconfig \
        fonts-crosextra-caladea \
        fonts-crosextra-carlito \
        git \
        make \
        python3 \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f

COPY --from=uv /uv /usr/local/bin/uv

# This environment stays outside the mounted project's .venv.
ENV UV_PROJECT_ENVIRONMENT=/opt/campus-venv \
    UV_PYTHON=/usr/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/campus-uv-cache \
    XDG_CACHE_HOME=/tmp/campus-cache \
    TEXMFHOME=/tmp/campus-texmf-home \
    TEXMFVAR=/tmp/campus-texmf-var \
    TEXMFCONFIG=/tmp/campus-texmf-config

WORKDIR /opt/campus-dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-config --no-cache \
        --default-index https://pypi.org/simple \
    && sha256sum pyproject.toml uv.lock > dependencies.sha256

# An arbitrary host UID can use the prebuilt environment without modifying it.
# The entrypoint rejects changed dependency files; rebuild the image to update.
ENV PATH="/opt/campus-venv/bin:${PATH}" \
    UV_NO_SYNC=1 \
    UV_NO_CONFIG=1 \
    UV_OFFLINE=1

COPY tools/doctor.py /tmp/campus-doctor.py
RUN python /tmp/campus-doctor.py \
    && git --version \
    && python -c "import pymupdf, pptx" \
    && rm /tmp/campus-doctor.py

COPY docker/entrypoint.sh /usr/local/bin/campus-entrypoint
RUN chmod 755 /usr/local/bin/campus-entrypoint

WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/campus-entrypoint"]
CMD ["make"]
