#!/usr/bin/env bash
set -euo pipefail

# DEMO: This script installs the package from the local source tree for development.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# DEMO: A virtual environment keeps this lesson isolated from the rest of the computer.
python3 -m venv .venv
source .venv/bin/activate

# DEMO: Editable install means code changes are visible without reinstalling each time.
python -m pip install --upgrade pip
python -m pip install -e .

# DEMO: The installed console script comes from [project.scripts] in pyproject.toml.
dir-monitor-exellenteam --help

# DEMO: Compare local editable package paths with packages downloaded from PyPI.
python scripts/compare_install_locations.py

# DEMO: These examples show module, regular package, namespace package, and installed package imports.
python examples/01_import_examples.py
python examples/02_use_installed_package.py
python examples/03_logging_levels.py
python examples/04_relative_vs_absolute_imports.py
