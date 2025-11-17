#!/usr/bin/env python3
"""Compatibility wrapper delegating to the unified runner in ``run.py``.

This project previously shipped two entry points: ``run.py`` (interactive) and
``run_with_dashboard.py`` (dashboard-focused). To avoid duplicated logic, this
wrapper now forwards to the shared runner while forcing the dashboard to be
enabled and auto-confirming default answers. Existing workflows that call
``python3 run_with_dashboard.py`` continue to work unchanged.
"""

import sys

from run import main


def _delegate():
    """Invoke the unified runner with dashboard defaults."""
    argv = ["--dashboard", "--non-interactive", *sys.argv[1:]]
    main(argv)


if __name__ == "__main__":
    _delegate()
