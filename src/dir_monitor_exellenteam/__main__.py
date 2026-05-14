"""Run the package with: python -m dir_monitor_exellenteam"""

from .cli import main


# DEMO: __main__.py lets a package run as a module with python -m package_name.
if __name__ == "__main__":
    raise SystemExit(main())
