"""Formatting helpers that demonstrate third-party dependencies."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Optional

# DEMO: colorama is a third-party dependency listed in pyproject.toml.
from colorama import Fore, Style, just_fix_windows_console

# DEMO: humanize is another third-party dependency listed in pyproject.toml.
import humanize


LOG_LEVEL_COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED + Style.BRIGHT,
}


def human_duration(seconds: Optional[float]) -> str:
    """Return a friendly duration string for logs."""

    if seconds is None:
        return "forever"

    if seconds == 0:
        return "0 seconds"

    return humanize.precisedelta(timedelta(seconds=seconds), minimum_unit="seconds")


def color_log_level(level_name: str) -> str:
    """Return a colored log level name for console output."""

    color = LOG_LEVEL_COLORS.get(level_name, "")
    if not color:
        return level_name

    return f"{color}{level_name}{Style.RESET_ALL}"


class ColorfulLogFormatter(logging.Formatter):
    """A logging formatter that colors only the level name."""

    def __init__(self, fmt: str, *, use_color: bool = True) -> None:
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        original_level_name = record.levelname
        if self.use_color:
            record.levelname = color_log_level(record.levelname)
        try:
            return super().format(record)
        finally:
            record.levelname = original_level_name


def prepare_console_colors() -> None:
    """Prepare console coloring on platforms that need it."""

    just_fix_windows_console()
