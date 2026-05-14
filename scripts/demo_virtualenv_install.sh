#!/usr/bin/env bash
set -euo pipefail

# DEMO: This script shows Python-package isolation with a virtualenv.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# DEMO: A virtualenv isolates Python packages, but it still uses the host operating system.
rm -rf .venv-compare
python3 -m venv .venv-compare
source .venv-compare/bin/activate

# DEMO: pip installs the local package into the virtualenv's site-packages directory.
python -m pip install --upgrade pip setuptools
python -m pip install .

# DEMO: These commands prove the package and its dependencies were installed in the virtualenv.
python -m pip show dir-monitor-exellenteam
python -m pip show colorama humanize
python -c "import sys, dir_monitor_exellenteam; print('Python:', sys.executable); print('Package:', dir_monitor_exellenteam.__file__)"
dir-monitor-exellenteam --version
