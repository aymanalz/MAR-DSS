"""
Entry script for PyInstaller: starts the Dash dashboard (no dev reloader).
"""
from __future__ import annotations

import multiprocessing
import sys


def _main() -> None:
    from mar_dss.dashboard import launch_dashboard

    launch_dashboard(debug=False, port=8050)


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        multiprocessing.freeze_support()
    _main()
