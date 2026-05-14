"""Integration tests that use the real filesystem."""

from __future__ import annotations

import logging
from pathlib import Path
import threading
import time
from unittest.mock import patch

import pytest

from dir_monitor_exellenteam import iter_directory_changes, monitor_directory


@pytest.mark.integration
def test_iter_directory_changes_detects_file_lifecycle(tmp_path: Path) -> None:
    def mutate_directory() -> None:
        original = tmp_path / "lesson.txt"
        moved = tmp_path / "lesson-renamed.txt"

        time.sleep(0.15)
        original.write_text("first", encoding="utf-8")
        time.sleep(0.2)
        original.write_text("second", encoding="utf-8")
        time.sleep(0.2)
        original.rename(moved)
        time.sleep(0.2)
        moved.unlink()

    worker = threading.Thread(target=mutate_directory)
    worker.start()

    # DEMO: This integration test combines real pathlib, stat calls, polling, and diffing.
    events = list(iter_directory_changes(tmp_path, interval=0.05, timeout=1.5))
    worker.join()

    event_types = [event.event_type for event in events]
    assert "created" in event_types
    assert "modified" in event_types
    assert "moved" in event_types
    assert "deleted" in event_types


@pytest.mark.integration
def test_monitor_directory_writes_to_log_file_and_mock_logger(tmp_path: Path) -> None:
    log_file = tmp_path / "changes.log"
    logger = logging.getLogger(f"test-monitor-{id(tmp_path)}")
    logger.handlers.clear()
    target = tmp_path / "created-during-monitor.txt"

    def create_file() -> None:
        time.sleep(0.15)
        target.write_text("hello", encoding="utf-8")

    worker = threading.Thread(target=create_file)
    worker.start()

    # DEMO: A spy mock records logger calls while the real logger still writes to the log file.
    with patch.object(logger, "info", wraps=logger.info) as info_spy:
        count = monitor_directory(
            tmp_path,
            interval=0.05,
            timeout=0.6,
            log_file=log_file,
            log_level="INFO",
            logger=logger,
        )
    worker.join()

    assert count >= 1
    log_text = log_file.read_text(encoding="utf-8")
    # DEMO: This asserts the log file contains start, event, and stop records.
    assert "INFO Watching" in log_text
    assert "CREATED" in log_text
    assert "INFO Stopped monitoring after logging" in log_text
    info_spy.assert_any_call("Watching %s", tmp_path.resolve())
    assert any("CREATED" in call.args[0] for call in info_spy.call_args_list if call.args)
    logger.handlers.clear()


@pytest.mark.integration
def test_monitor_directory_writes_warning_to_log_file_when_no_changes(tmp_path: Path) -> None:
    log_file = tmp_path / "no-changes.log"

    count = monitor_directory(
        tmp_path,
        interval=0.05,
        timeout=0.15,
        log_file=log_file,
        log_level="WARNING",
    )

    log_text = log_file.read_text(encoding="utf-8")
    # DEMO: Log level WARNING filters out INFO records but still writes warnings.
    assert count == 0
    assert "WARNING No changes detected before monitor stopped." in log_text
    assert "INFO Watching" not in log_text
