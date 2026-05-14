"""System-level tests for the external installer picker script."""

from __future__ import annotations

import subprocess
import sys
from typing import Union
from unittest.mock import patch

import pytest

from scripts import install_picker_and_show_paths


@pytest.mark.system
def test_install_picker_local_dev_mode_runs_commands_in_order() -> None:
    calls: list[list[str]] = []

    def fake_run(command: Union[list[str], str], **_: object) -> None:
        if isinstance(command, list):
            calls.append(command)

    argv = ["install_picker_and_show_paths.py", "--mode", "local-dev"]
    with patch.object(install_picker_and_show_paths, "prepare_venv") as prepare_venv:
        with patch.object(sys, "argv", argv):
            with patch.object(subprocess, "run", side_effect=fake_run) as run:
                # DEMO: This mock prevents a system helper from creating virtualenvs during the test.
                exit_code = install_picker_and_show_paths.main()

    assert exit_code == 0
    assert prepare_venv.called
    assert run.called
    assert any(command[1:4] == ["-m", "pip", "install"] for command in calls)
    assert any("-e" in command for command in calls)


@pytest.mark.system
def test_install_picker_help_runs_as_external_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/install_picker_and_show_paths.py", "--help"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "local-dev" in result.stdout
