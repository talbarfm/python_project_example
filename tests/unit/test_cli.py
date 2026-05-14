"""Unit tests for the command-line interface."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from dir_monitor_exellenteam import cli


@pytest.mark.unit
def test_main_passes_parsed_arguments_to_library_api(tmp_path: Path) -> None:
    log_file = tmp_path / "changes.log"

    with patch("dir_monitor_exellenteam.cli.monitor_directory", return_value=0) as monitor:
        # DEMO: Mocking the library API keeps this CLI unit test focused on argument parsing.
        exit_code = cli.main(
            [
                str(tmp_path),
                "--timeout",
                "2",
                "--interval",
                "0.25",
                "--log-file",
                str(log_file),
                "--log-level",
                "DEBUG",
                "--non-recursive",
            ]
        )

    assert exit_code == 0
    monitor.assert_called_once_with(
        str(tmp_path),
        timeout=2.0,
        interval=0.25,
        log_file=log_file,
        log_level="DEBUG",
        recursive=False,
    )


@pytest.mark.unit
def test_main_returns_130_for_keyboard_interrupt(tmp_path: Path) -> None:
    with patch("dir_monitor_exellenteam.cli.monitor_directory", side_effect=KeyboardInterrupt):
        with patch("dir_monitor_exellenteam.cli.logging.getLogger") as get_logger:
            # DEMO: The CLI uses logging for user-visible status, even when interrupted.
            logger = get_logger.return_value
            exit_code = cli.main([str(tmp_path)])

    assert exit_code == 130
    logger.warning.assert_called_once_with("Stopped by user.")


@pytest.mark.unit
def test_main_returns_2_for_monitoring_error(tmp_path: Path) -> None:
    with patch("dir_monitor_exellenteam.cli.monitor_directory", side_effect=FileNotFoundError("missing")):
        # DEMO: argparse reports CLI errors by raising SystemExit with exit code 2.
        with pytest.raises(SystemExit) as error:
            cli.main([str(tmp_path)])

    assert error.value.code == 2
