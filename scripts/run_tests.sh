#!/usr/bin/env bash
set -euo pipefail

# DEMO: This script installs test dependencies and runs every test layer.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# DEMO: A separate test virtualenv keeps pytest out of normal user installs.
python3 -m venv .venv-test
source .venv-test/bin/activate

# DEMO: The [dev] extra comes from pyproject.toml and installs pytest.
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# DEMO: Pytest markers let students run unit, integration, or system tests separately.
python -m pytest "$@"
