"""Directory monitoring library code."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import sys
import time
from typing import Dict, Iterator, Optional, TextIO, Tuple, Union

# DEMO: The dot means import formatting from this same package.
from .formatting import ColorfulLogFormatter, human_duration, prepare_console_colors


PathLike = Union[str, Path]


@dataclass(frozen=True)
class ChangeEvent:
    """A single change detected in the watched directory."""

    # DEMO: A dataclass is a compact way to model the event data the library returns.
    event_type: str
    path: Path
    old_path: Optional[Path] = None
    is_directory: bool = False

    def to_log_line(self) -> str:
        """Format this event for humans and log files."""

        item_type = "directory" if self.is_directory else "file"
        if self.event_type == "moved" and self.old_path is not None:
            return f"{self.event_type.upper():8} {item_type}: {self.old_path} -> {self.path}"
        return f"{self.event_type.upper():8} {item_type}: {self.path}"


@dataclass(frozen=True)
class _FileState:
    """Internal snapshot information for one path."""

    path: Path
    file_id: Tuple[int, int]
    size: int
    modified_ns: int
    is_directory: bool


def iter_directory_changes(
    directory: PathLike,
    *,
    interval: float = 1.0,
    timeout: Optional[float] = None,
    recursive: bool = True,
) -> Iterator[ChangeEvent]:
    """Yield directory change events until timeout expires, or forever when timeout is None."""

    watch_path = Path(directory).expanduser().resolve()
    _validate_watch_path(watch_path, interval, timeout)

    # DEMO: The first scan is the baseline; later scans are compared against it.
    previous_snapshot = _scan_directory(watch_path, recursive=recursive)
    started_at = time.monotonic()

    while True:
        sleep_for = _seconds_until_next_scan(started_at, interval, timeout)
        if sleep_for is None:
            return

        time.sleep(sleep_for)
        current_snapshot = _scan_directory(watch_path, recursive=recursive)

        # DEMO: Comparing two snapshots lets us detect created, deleted, modified, and moved paths.
        for event in _diff_snapshots(previous_snapshot, current_snapshot):
            yield event

        previous_snapshot = current_snapshot


def monitor_directory(
    directory: PathLike,
    *,
    interval: float = 1.0,
    timeout: Optional[float] = None,
    log_file: Optional[PathLike] = None,
    log_level: Union[int, str] = logging.INFO,
    recursive: bool = True,
    logger: Optional[logging.Logger] = None,
) -> int:
    """Monitor a directory, log each detected change, and return the number of logged events."""

    active_logger, opened_file, file_handler = _prepare_logger(
        log_file=log_file,
        log_level=log_level,
        logger=logger,
    )
    watch_path = Path(directory).expanduser().resolve()
    count = 0

    try:
        # DEMO: This is the public library API that the CLI and user code both call.
        active_logger.info("Watching %s", watch_path)
        # DEMO: DEBUG logs are useful for details that help developers understand behavior.
        active_logger.debug(
            "Monitor settings: interval=%s (%s) timeout=%s (%s) recursive=%s log_file=%s",
            interval,
            human_duration(interval),
            timeout,
            human_duration(timeout),
            recursive,
            log_file,
        )
        for event in iter_directory_changes(
            watch_path,
            interval=interval,
            timeout=timeout,
            recursive=recursive,
        ):
            active_logger.info(event.to_log_line())
            count += 1
    except Exception:
        # DEMO: ERROR logs describe failures; exception() also includes the traceback.
        active_logger.exception("Monitoring failed")
        raise
    else:
        if count == 0:
            # DEMO: WARNING logs are for unusual but non-fatal situations.
            active_logger.warning("No changes detected before monitor stopped.")
        else:
            active_logger.info("Stopped monitoring after logging %s event(s).", count)
    finally:
        if file_handler is not None:
            active_logger.removeHandler(file_handler)
        if opened_file is not None:
            opened_file.close()

    return count


def _validate_watch_path(path: Path, interval: float, timeout: Optional[float]) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    if interval <= 0:
        raise ValueError("interval must be greater than 0")
    if timeout is not None and timeout < 0:
        raise ValueError("timeout must be 0 or greater")


def _seconds_until_next_scan(started_at: float, interval: float, timeout: Optional[float]) -> Optional[float]:
    if timeout is None:
        return interval

    elapsed = time.monotonic() - started_at
    remaining = timeout - elapsed
    if remaining <= 0:
        return None
    return min(interval, remaining)


def _scan_directory(directory: Path, *, recursive: bool) -> Dict[Path, _FileState]:
    paths = directory.rglob("*") if recursive else directory.iterdir()
    snapshot: Dict[Path, _FileState] = {}

    for path in paths:
        try:
            stats = path.stat()
        except (FileNotFoundError, PermissionError):
            continue

        snapshot[path.resolve()] = _FileState(
            path=path.resolve(),
            file_id=(stats.st_dev, stats.st_ino),
            size=stats.st_size,
            modified_ns=stats.st_mtime_ns,
            is_directory=path.is_dir(),
        )

    return snapshot


def _diff_snapshots(before: Dict[Path, _FileState], after: Dict[Path, _FileState]) -> Iterator[ChangeEvent]:
    before_by_id = {state.file_id: state for state in before.values()}
    after_by_id = {state.file_id: state for state in after.values()}

    moved_from = set()
    moved_to = set()

    for file_id, old_state in before_by_id.items():
        new_state = after_by_id.get(file_id)
        if new_state is not None and old_state.path != new_state.path:
            moved_from.add(old_state.path)
            moved_to.add(new_state.path)
            yield ChangeEvent("moved", path=new_state.path, old_path=old_state.path, is_directory=new_state.is_directory)

    for path, new_state in after.items():
        if path in moved_to:
            continue

        old_state = before.get(path)
        if old_state is None:
            yield ChangeEvent("created", path=path, is_directory=new_state.is_directory)
        elif _is_modified(old_state, new_state):
            yield ChangeEvent("modified", path=path, is_directory=new_state.is_directory)

    for path, old_state in before.items():
        if path in moved_from:
            continue

        if path not in after:
            yield ChangeEvent("deleted", path=path, is_directory=old_state.is_directory)


def _is_modified(old_state: _FileState, new_state: _FileState) -> bool:
    if old_state.is_directory or new_state.is_directory:
        return False

    return old_state.size != new_state.size or old_state.modified_ns != new_state.modified_ns


def _prepare_logger(
    *,
    log_file: Optional[PathLike],
    log_level: Union[int, str],
    logger: Optional[logging.Logger],
) -> Tuple[logging.Logger, Optional[TextIO], Optional[logging.Handler]]:
    active_logger = logger or logging.getLogger("dir_monitor_exellenteam")
    level = _normalize_log_level(log_level)
    active_logger.setLevel(level)
    active_logger.propagate = False

    if not active_logger.handlers:
        prepare_console_colors()
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(ColorfulLogFormatter("%(asctime)s %(levelname)s %(message)s", use_color=sys.stderr.isatty()))
        active_logger.addHandler(stream_handler)
    else:
        for handler in active_logger.handlers:
            handler.setLevel(level)

    opened_file: Optional[TextIO] = None
    file_handler: Optional[logging.Handler] = None
    if log_file is not None:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        opened_file = log_path.open("a", encoding="utf-8")
        file_handler = logging.StreamHandler(opened_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        active_logger.addHandler(file_handler)

    return active_logger, opened_file, file_handler


def _normalize_log_level(log_level: Union[int, str]) -> int:
    if isinstance(log_level, int):
        return log_level

    level = getattr(logging, str(log_level).upper(), None)
    if not isinstance(level, int):
        raise ValueError(f"Unknown log level: {log_level}")

    return level
