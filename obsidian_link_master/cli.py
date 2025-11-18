"""Command-line entrypoint for Obsidian Link Master."""

from __future__ import annotations

from typing import Iterable, Optional

from run import main as _main


def main(argv: Optional[Iterable[str]] = None) -> None:
    """Entrypoint used by the ``obsidian-link-master`` console script."""

    _main(argv)
