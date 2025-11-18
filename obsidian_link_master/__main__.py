"""Module entrypoint for ``python -m obsidian_link_master``.

This mirrors the installed console script to keep a single canonical
entrypoint while preserving legacy wrappers (``run.py`` and
``run_with_dashboard.py``) for compatibility.
"""

from __future__ import annotations

from .cli import main


if __name__ == "__main__":  # pragma: no cover
    main()
