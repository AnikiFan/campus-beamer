#!/bin/sh
# Campus Beamer: verify image dependencies before running a command.
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
set -eu

if [ ! -f pyproject.toml ] || [ ! -f uv.lock ]; then
    printf '%s\n' 'Mount the project root at /workspace before running this image.' >&2
    exit 2
fi

if ! sha256sum --check --status /opt/campus-dependencies/dependencies.sha256; then
    printf '%s\n' 'Dependency files differ from the image. Rebuild with docker build -f docker/Dockerfile -t campus-beamer:local .' >&2
    exit 2
fi

exec "$@"
