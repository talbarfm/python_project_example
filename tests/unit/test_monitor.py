"""Unit tests for the directory monitor."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union
from unittest.mock import Mock, patch

import pytest

from dir_monitor_exellenteam.monitor import (
    ChangeEvent,
    _FileState,
    _diff_snapshots,
    _normalize_log_level,
    _seconds_until_next_scan,
    monitor_directory,
)


def file_state(path: Path, file_id: tuple[int, int], *, size: int = 10, modified_ns: int = 100) -> _FileState:
    return _FileState(path=path, file_id=file_id, size=size, modified_ns=modified_ns, is_directory=False)


@pytest.mark.unit
def test_change_event_formats_move() -> None:
    # DEMO: A unit test checks one small behavior with no filesystem or clock involved.
    event = ChangeEvent("moved", path=Path("new.txt"), old_path=Path("old.txt"))

    assert event.to_log_line() == "MOVED    file: old.txt -> new.txt"


@pytest.mark.unit
def test_change_event_formats_created_file() -> None:
    # DEMO: This catches the simple formatting mistake students create in the debugging exercise.
    event = ChangeEvent("created", path=Path("created.txt"))

    assert event.to_log_line() == "CREATED  file: created.txt"


@pytest.mark.unit
def test_diff_snapshots_finds_created_modified_moved_and_deleted() -> None:
    before = {
        Path("modified.txt"): file_state(Path("modified.txt"), (1, 1), size=10, modified_ns=100),
        Path("old-name.txt"): file_state(Path("old-name.txt"), (1, 2)),
        Path("deleted.txt"): file_state(Path("deleted.txt"), (1, 3)),
    }
    after = {
        Path("modified.txt"): file_state(Path("modified.txt"), (1, 1), size=11, modified_ns=200),
        Path("new-name.txt"): file_state(Path("new-name.txt"), (1, 2)),
        Path("created.txt"): file_state(Path("created.txt"), (1, 4)),
    }

    events = list(_diff_snapshots(before, after))

    assert [(event.event_type, event.path) for event in events] == [
        ("moved", Path("new-name.txt")),
        ("modified", Path("modified.txt")),
        ("created", Path("created.txt")),
        ("deleted", Path("deleted.txt")),
    ]
    assert events[0].old_path == Path("old-name.txt")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("log_level", "expected"),
    [
        ("debug", logging.DEBUG),
        ("INFO", logging.INFO),
        (logging.WARNING, logging.WARNING),
    ],
)
def test_normalize_log_level_accepts_strings_and_ints(log_level: Union[str, int], expected: int) -> None:
    assert _normalize_log_level(log_level) == expected


@pytest.mark.unit
def test_normalize_log_level_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Unknown log level"):
        _normalize_log_level("LOUD")


@pytest.mark.unit
def test_seconds_until_next_scan_returns_none_after_timeout() -> None:
    with patch("dir_monitor_exellenteam.monitor.time.monotonic", return_value=15.0):
        # DEMO: Mocking time makes timeout behavior deterministic and fast.
        assert _seconds_until_next_scan(started_at=10.0, interval=1.0, timeout=5.0) is None


@pytest.mark.unit
def test_monitor_directory_logs_events_from_mocked_iterator(tmp_path: Path) -> None:
    logger = Mock()
    logger.handlers = []
    event = ChangeEvent("created", tmp_path / "created.txt")

    with patch("dir_monitor_exellenteam.monitor.iter_directory_changes", return_value=iter([event])) as changes:
        # DEMO: This mock isolates monitor_directory from the real filesystem polling loop.
        count = monitor_directory(tmp_path, timeout=1, interval=0.5, logger=logger, log_level="DEBUG")

    assert count == 1
    changes.assert_called_once_with(tmp_path.resolve(), interval=0.5, timeout=1, recursive=True)
    logger.info.assert_any_call("Watching %s", tmp_path.resolve())
    logger.info.assert_any_call(event.to_log_line())
    logger.info.assert_any_call("Stopped monitoring after logging %s event(s).", 1)
    logger.debug.assert_called_once()
    logger.warning.assert_not_called()
    logger.exception.assert_not_called()


@pytest.mark.unit
def test_monitor_directory_warns_when_no_changes_are_detected(tmp_path: Path) -> None:
    logger = Mock()
    logger.handlers = []

    with patch("dir_monitor_exellenteam.monitor.iter_directory_changes", return_value=iter([])):
        # DEMO: WARNING is used for unusual but non-fatal outcomes.
        count = monitor_directory(tmp_path, logger=logger)

    assert count == 0
    logger.warning.assert_called_once_with("No changes detected before monitor stopped.")


@pytest.mark.unit
def test_monitor_directory_logs_exception_from_mocked_iterator(tmp_path: Path) -> None:
    logger = Mock()
    logger.handlers = []

    with patch("dir_monitor_exellenteam.monitor.iter_directory_changes", side_effect=FileNotFoundError("missing")):
        # DEMO: The mock makes the error path easy to test without deleting real folders mid-test.
        with pytest.raises(FileNotFoundError):
            monitor_directory(tmp_path, logger=logger)

    logger.exception.assert_called_once_with("Monitoring failed")
