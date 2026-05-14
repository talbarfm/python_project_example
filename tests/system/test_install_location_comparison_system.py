"""System tests for the install-location comparison helper."""

from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.system
def test_compare_install_locations_script_shows_local_and_pypi_paths() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/compare_install_locations.py"],
        text=True,
        capture_output=True,
        check=False,
    )

    # DEMO: This verifies the classroom script compares local editable and PyPI dependency paths.
    assert result.returncode == 0
    assert "Local editable package: dir-monitor-exellenteam" in result.stdout
    assert "External PyPI dependency: humanize" in result.stdout
    assert "External PyPI dependency: colorama" in result.stdout
    assert "src/dir_monitor_exellenteam" in result.stdout
    assert "site-packages" in result.stdout
