"""System tests that run the package like an outside user."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Optional
from unittest.mock import patch

import pytest

SRC_DIR = Path(__file__).resolve().parents[2] / "src"


def package_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)
    return env


def run_cli(args: list[str], *, cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "dir_monitor_exellenteam", *args],
        cwd=cwd,
        env=package_env(),
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.system
def test_python_m_package_help_runs_successfully() -> None:
    # DEMO: A system test crosses the process boundary with subprocess.
    result = subprocess.run(
        [sys.executable, "-m", "dir_monitor_exellenteam", "--help"],
        env=package_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "dir-monitor-exellenteam" in result.stdout
    assert "--log-level" in result.stdout


@pytest.mark.system
def test_python_m_package_version_runs_successfully() -> None:
    result = run_cli(["--version"])

    assert result.returncode == 0
    assert "dir-monitor-exellenteam 0.1.0" in result.stdout


@pytest.mark.system
def test_cli_monitor_prints_warning_when_no_changes(tmp_path: Path) -> None:
    with patch.dict(os.environ, package_env()):
        # DEMO: patch.dict is a small mock that gives the subprocess a controlled environment.
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "dir_monitor_exellenteam",
                str(tmp_path),
                "--timeout",
                "0.15",
                "--interval",
                "0.05",
                "--log-level",
                "WARNING",
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    assert result.returncode == 0
    assert "No changes detected" in result.stderr
    assert "Watching" not in result.stderr


@pytest.mark.system
def test_cli_writes_warning_log_file_when_no_changes(tmp_path: Path) -> None:
    log_file = tmp_path / "system-warning.log"

    result = run_cli(
        [
            str(tmp_path),
            "--timeout",
            "0.15",
            "--interval",
            "0.05",
            "--log-level",
            "WARNING",
            "--log-file",
            str(log_file),
        ]
    )

    log_text = log_file.read_text(encoding="utf-8")
    # DEMO: This system test verifies logs are written by the real CLI process.
    assert result.returncode == 0
    assert "No changes detected before monitor stopped." in result.stderr
    assert "WARNING No changes detected before monitor stopped." in log_text
    assert "INFO Watching" not in log_text


@pytest.mark.system
def test_cli_writes_event_log_file_for_created_file(tmp_path: Path) -> None:
    log_file = tmp_path / "system-created.log"
    watched_dir = tmp_path / "watched"
    watched_dir.mkdir()

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "dir_monitor_exellenteam",
            str(watched_dir),
            "--timeout",
            "1.0",
            "--interval",
            "0.05",
            "--log-level",
            "INFO",
            "--log-file",
            str(log_file),
        ],
        env=package_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(0.2)
    (watched_dir / "created-by-system-test.txt").write_text("hello", encoding="utf-8")
    stdout, stderr = process.communicate(timeout=3)

    log_text = log_file.read_text(encoding="utf-8")
    # DEMO: This exercises the real subprocess, real filesystem, and real log file.
    assert process.returncode == 0
    assert stdout == ""
    assert "CREATED" in stderr
    assert "INFO Watching" in log_text
    assert "CREATED" in log_text
    assert "INFO Stopped monitoring after logging" in log_text


@pytest.mark.system
def test_cli_returns_error_for_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dir_monitor_exellenteam",
            str(missing),
            "--timeout",
            "0.1",
        ],
        env=package_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Directory does not exist" in result.stderr


@pytest.mark.system
def test_cli_rejects_invalid_log_level(tmp_path: Path) -> None:
    result = run_cli([str(tmp_path), "--log-level", "LOUD"])

    assert result.returncode == 2
    assert "invalid choice" in result.stderr
