#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create a private outline from the public starter without overwriting a draft."""
from pathlib import Path


def initialize(root: Path) -> bool:
    """Return whether a new outline was created; existing paths stay untouched."""
    content = (root / 'tools/templates/outline.md').read_bytes()
    try:
        with (root / 'outline.md').open('xb') as stream:
            stream.write(content)
    except FileExistsError:
        return False
    return True


if __name__ == '__main__':
    created = initialize(Path(__file__).resolve().parents[1])
    print('Created outline.md; fill in your brief.' if created else
          'Keeping existing outline.md unchanged.')
